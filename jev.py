"""Minimal async client for TypeSafe's Jev classifier: batching, retries, and an on-disk cache."""

import asyncio
import hashlib
import json
import os
import time
from email.utils import parsedate_to_datetime
from pathlib import Path

import aiohttp

API_URL = "https://api.typesafe.ai/v1/systemone"
MODEL_ALIAS = "jev-latest"  # resolved to a concrete version (e.g. jev-1.13.0) once per run
USD_PER_MTOK = 0.042
REQUEST_TOKEN_BUDGET = 55_000
PER_QUESTION_OVERHEAD = 15  # key + JSON wrapper, in estimated tokens
PER_OPTION_OVERHEAD = 15  # Choice options cost ~1.5x their JSON size (measured: 37 options, +~400 real tokens)
MAX_ATTEMPTS = 8  # for 429s
MAX_5XX_RETRIES = 3


def est_tokens(text: str) -> int:
    return int(len(text) / 3.5) + 1


def cost_usd(tokens: int) -> float:
    return tokens * USD_PER_MTOK / 1e6


def batch_questions(questions: dict, state_tokens: int) -> list[dict]:
    """Split questions (statement texts or full question objects) into batches so state + batch stays
    under REQUEST_TOKEN_BUDGET."""
    batches: list[dict] = [{}]
    used = state_tokens
    for key, text in questions.items():
        cost = est_tokens(text if isinstance(text, str) else json.dumps(text)) + PER_QUESTION_OVERHEAD
        if isinstance(text, dict):
            cost += PER_OPTION_OVERHEAD * len(text.get("criteria", ()))
        if batches[-1] and used + cost > REQUEST_TOKEN_BUDGET:
            batches.append({})
            used = state_tokens
        batches[-1][key] = text
        used += cost
    return batches


def retry_delay(header: str | None, attempt: int) -> float:
    """Seconds to wait from a retry-after header (delta-seconds or HTTP-date), else exponential backoff."""
    if header is None:
        return float(2**attempt)
    if header.strip().isdigit():
        return float(header)
    return max(0.0, parsedate_to_datetime(header).timestamp() - time.time())


class Jev:
    """`async with Jev(cache_dir, concurrency) as jev: p = await jev.ask(state, {key: statement})`. Counts usage in `stats`.

    On entry it resolves `jev-latest` to the concrete model version and pins it for every request and
    cache key, so a Jev upgrade never mixes scores from two models."""

    def __init__(self, cache_dir: Path, concurrency: int) -> None:
        self.stats = {"requests": 0, "cache_hits": 0, "tokens": 0, "billed_tokens": 0}
        self.cache_dir = cache_dir
        self.sem = asyncio.Semaphore(concurrency)

    async def __aenter__(self) -> "Jev":
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        if not os.environ.get("TYPESAFE_API_KEY"):
            raise SystemExit("TYPESAFE_API_KEY is not set: put it in .env (see .env.example) or export it")
        headers = {"Authorization": f"Bearer {os.environ['TYPESAFE_API_KEY']}"}
        self.session = aiohttp.ClientSession(headers=headers, timeout=aiohttp.ClientTimeout(total=120))
        # Never cached, so a warm re-run still makes this one billed request (counted in stats).
        probe = {"q": {"type": "noul", "instructions": "The text in `t` is empty."}}
        payload = await self.post({"model": MODEL_ALIAS, "state": {"t": "x"}, "questions": probe})
        self.model = payload["model"]
        self.stats["requests"] += 1
        self.stats["tokens"] += payload["usage"]["input_tokens"]
        self.stats["billed_tokens"] += payload["usage"]["input_tokens"]
        return self

    async def __aexit__(self, *exc) -> None:
        await self.session.close()

    async def ask(self, state: dict, questions: dict[str, str], usage: dict | None = None) -> dict[str, float]:
        """P(yes) for every statement, sending as many requests as the token budget needs.
        If `usage` is given, the requests and input tokens are added to it."""
        if not questions:
            return {}
        batches = batch_questions(questions, est_tokens(json.dumps(state)))
        answers = await asyncio.gather(*(
            self.request(state, {k: {"type": "noul", "instructions": q} for k, q in b.items()}, usage) for b in batches
        ))
        return {k: v["noul"] for a in answers for k, v in a.items()}

    async def ask_objects(self, state: dict, questions: dict[str, dict]) -> dict[str, dict]:
        """Raw answers for full question objects (any type), batched like `ask`."""
        if not questions:
            return {}
        batches = batch_questions(questions, est_tokens(json.dumps(state)))
        answers = await asyncio.gather(*(self.request(state, b) for b in batches))
        return {k: v for a in answers for k, v in a.items()}

    async def choose(self, state: dict, instructions: str, criteria: dict[str, str]) -> dict:
        """One Choice question; returns Jev's answer ({choice, confidence, probabilities})."""
        answers = await self.request(state, {"kind": {"type": "choice", "instructions": instructions, "criteria": criteria}})
        return answers["kind"]

    async def request(self, state: dict, questions: dict, usage: dict | None = None) -> dict:
        body = {"model": self.model, "state": state, "questions": questions}
        key = hashlib.sha256(json.dumps([self.model, state, questions], sort_keys=True).encode()).hexdigest()
        cache_file = self.cache_dir / f"{key}.json"
        if cache_file.exists():
            payload = json.loads(cache_file.read_text())
            self.stats["cache_hits"] += 1
        else:
            payload = await self.post(body)
            if payload["model"] != self.model:
                raise RuntimeError(f"Jev answered with {payload['model']}, expected {self.model}")
            tmp = cache_file.with_suffix(".tmp")
            tmp.write_text(json.dumps(payload))
            os.replace(tmp, cache_file)
            self.stats["billed_tokens"] += payload["usage"]["input_tokens"]
        self.stats["requests"] += 1
        self.stats["tokens"] += payload["usage"]["input_tokens"]
        if usage is not None:
            usage["requests"] = usage.get("requests", 0) + 1
            usage["tokens"] = usage.get("tokens", 0) + payload["usage"]["input_tokens"]
        return {k: payload["answers"][k] for k in questions}

    async def post(self, body: dict) -> dict:
        server_errors = 0
        async with self.sem:
            for attempt in range(MAX_ATTEMPTS):
                async with self.session.post(API_URL, json=body) as resp:
                    if resp.status >= 500:
                        server_errors += 1
                        if server_errors > MAX_5XX_RETRIES:
                            raise RuntimeError(f"Jev HTTP {resp.status} after {MAX_5XX_RETRIES} retries: "
                                               f"{await resp.text()}")
                    elif resp.status != 429:
                        if resp.status != 200:
                            raise RuntimeError(f"Jev HTTP {resp.status}: {await resp.text()}")
                        return await resp.json()
                    delay = retry_delay(resp.headers.get("retry-after"), attempt)
                if attempt < MAX_ATTEMPTS - 1:
                    await asyncio.sleep(delay)
        raise RuntimeError(f"Jev: still rate-limited after {MAX_ATTEMPTS} attempts")
