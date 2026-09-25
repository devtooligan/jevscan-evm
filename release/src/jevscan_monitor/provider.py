"""Fixed-model classification with validated answers and conservative accounting.

The local dollar ceiling uses a documented price assumption, not a provider-side
billing guarantee. Apply provider account quotas as the ultimate spending limit.
"""

import asyncio
import fcntl
import hashlib
import json
import math
import os
import tempfile
import time
import uuid
from pathlib import Path

import aiohttp

API_URL = "https://api.typesafe.ai/v1/systemone"
USD_PER_MILLION_TOKENS = 0.042
RESERVED_TOKENS = 55_000
MAX_REQUEST_BYTES = 48_000
MAX_RESPONSE_BYTES = 1_000_000


def est_tokens(text: str) -> int:
    """Legacy rendering estimate; never a provider billing measurement."""
    return int(len(text) / 3.5) + 1


def encode(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def score_number(value: object) -> float:
    if type(value) not in (int, float) or not 0 <= value <= 1 or not math.isfinite(value):
        raise ValueError("Provider score must be a finite number between zero and one")
    return float(value)


def validate_response(payload: object, model: str, questions: dict) -> tuple[dict[str, float], int]:
    if not isinstance(payload, dict) or payload.get("model") != model:
        raise ValueError("Provider returned an incompatible model or response")
    usage, answers = payload.get("usage"), payload.get("answers")
    if not isinstance(usage, dict) or type(usage.get("input_tokens")) is not int:
        raise ValueError("Provider returned invalid token accounting")
    tokens = usage["input_tokens"]
    if not 0 <= tokens <= RESERVED_TOKENS:
        raise ValueError("Provider token accounting exceeds the request reservation")
    if not isinstance(answers, dict) or set(answers) != set(questions):
        raise ValueError("Provider answer keys differ from the requested questions")
    scores = {}
    for name, answer in answers.items():
        if not isinstance(answer, dict) or "noul" not in answer:
            raise ValueError("Provider returned an invalid classification answer")
        scores[name] = score_number(answer["noul"])
    return scores, tokens


def atomic_json(path: Path, value: object, *, overwrite: bool = True) -> None:
    """Owner-only temporary file and atomic replacement in the same directory."""
    payload = encode(value)
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, name = tempfile.mkstemp(prefix=".writing-", dir=path.parent)
    temporary = Path(name)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        if overwrite:
            os.replace(temporary, path)
        else:
            os.link(temporary, path)
            temporary.unlink()
        directory = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        temporary.unlink(missing_ok=True)


def ledger_total(rows: list[dict]) -> float:
    reservations = {}
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get("id"), str):
            raise ValueError("Invalid spending ledger; refusing new paid calls")
        identity, kind = row["id"], row.get("kind")
        tokens = row.get("tokens")
        if type(tokens) is not int or not 0 <= tokens <= RESERVED_TOKENS:
            raise ValueError("Invalid spending ledger amount")
        if kind == "reserve" and identity not in reservations and tokens == RESERVED_TOKENS:
            reservations[identity] = (tokens, False)
        elif kind == "settle" and identity in reservations and not reservations[identity][1]:
            reservations[identity] = (tokens, True)
        else:
            raise ValueError("Invalid spending ledger transition")
    return sum(tokens for tokens, _ in reservations.values()) * USD_PER_MILLION_TOKENS / 1_000_000


class Classifier:
    """Single-writer paid client: no automatic retries or paid alias probe."""

    def __init__(self, workspace: Path, model: str, budget_usd: float, *, allow_paid: bool = False):
        if model != "jev-1.13.0":
            raise ValueError("A concrete Jev model version is required")
        if type(budget_usd) not in (int, float) or not math.isfinite(budget_usd) or budget_usd <= 0:
            raise ValueError("A positive finite workspace budget is required")
        self.workspace, self.model, self.budget_usd = workspace, model, budget_usd
        self.allow_paid = allow_paid
        self.requests = 0
        self.cache_hits = 0
        self.billed_tokens = 0
        self.next_start = 0.0
        self.request_lock = asyncio.Lock()

    async def __aenter__(self):
        self.workspace.mkdir(parents=True, exist_ok=True, mode=0o700)
        self.lock = (self.workspace / "spend.lock").open("a+")
        try:
            fcntl.flock(self.lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            self.ledger_path = self.workspace / "spend.jsonl"
            self.rows = ([json.loads(line) for line in self.ledger_path.read_text().splitlines()]
                         if self.ledger_path.exists() else [])
            ledger_total(self.rows)
            self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=120))
            return self
        except BaseException:
            self.lock.close()
            raise

    async def __aexit__(self, *exc):
        try:
            await self.session.close()
        finally:
            self.lock.close()

    def append(self, row: dict) -> None:
        with self.ledger_path.open("a") as stream:
            stream.write(encode(row).decode() + "\n")
            stream.flush()
            os.fsync(stream.fileno())
        directory = os.open(self.ledger_path.parent, os.O_RDONLY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
        self.rows.append(row)

    async def classify(self, state: dict, questions: dict, *, input_version: int) -> dict[str, float]:
        async with self.request_lock:
            return await self._classify(state, questions, input_version=input_version)

    async def _classify(self, state: dict, questions: dict, *, input_version: int) -> dict[str, float]:
        if not isinstance(state, dict) or not questions or any(q.get("type") != "noul" for q in questions.values()):
            raise ValueError("Only nonempty Noul question bundles and object states are supported")
        body = {"model": self.model, "state": state, "questions": questions}
        encoded = encode(body)
        if len(encoded) > MAX_REQUEST_BYTES:
            raise ValueError("Input exceeds the paid request size limit; transaction not evaluated")
        identity = hashlib.sha256(encode({"request": body, "input_version": input_version})).hexdigest()
        cache = self.workspace / "answers" / f"{identity}.json"
        if cache.exists():
            if cache.stat().st_size > MAX_RESPONSE_BYTES or cache.is_symlink():
                raise ValueError("Cached answer exceeds the size limit or is a symlink")
            payload = json.loads(cache.read_text())
            if not isinstance(payload, dict) or payload.get("request_sha256") != identity:
                raise ValueError("Cached request identity mismatch")
            scores, _ = validate_response(payload, self.model, questions)
            self.cache_hits += 1
            return scores
        if not self.allow_paid:
            raise RuntimeError("No cached answer; paid scoring requires --allow-paid")
        key = os.environ.get("TYPESAFE_API_KEY")
        if not key:
            raise RuntimeError("TYPESAFE_API_KEY is not set")
        reservation = RESERVED_TOKENS * USD_PER_MILLION_TOKENS / 1_000_000
        if ledger_total(self.rows) + reservation > self.budget_usd:
            raise RuntimeError("Workspace budget would be exceeded; no request sent")
        await asyncio.sleep(max(0, self.next_start - time.monotonic()))
        self.next_start = time.monotonic() + 1 / 18
        request_id = uuid.uuid4().hex
        self.append({"kind": "reserve", "id": request_id, "tokens": RESERVED_TOKENS})
        self.requests += 1
        try:
            async with self.session.post(API_URL, data=encoded,
                                         headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                                         allow_redirects=False) as response:
                if response.status != 200:
                    raise RuntimeError(f"Classifier HTTP {response.status}; no retry; spending reservation retained")
                chunks = bytearray()
                async for chunk in response.content.iter_chunked(65536):
                    chunks.extend(chunk)
                    if len(chunks) > MAX_RESPONSE_BYTES:
                        raise RuntimeError("Classifier response too large; reservation retained")
                try:
                    payload = json.loads(chunks)
                    scores, tokens = validate_response(payload, self.model, questions)
                except (ValueError, TypeError, KeyError):
                    raise RuntimeError("Invalid classifier response; transaction not evaluated; reservation retained") from None
        except (aiohttp.ClientError, asyncio.TimeoutError):
            raise RuntimeError("Classifier transport failed; outcome unknown; reservation retained") from None
        self.append({"kind": "settle", "id": request_id, "tokens": tokens})
        self.billed_tokens += tokens
        # Persist only validated fields, never the raw provider response body.
        atomic_json(cache, {"request_sha256": identity, "model": self.model,
                            "usage": {"input_tokens": tokens},
                            "answers": {name: {"noul": value} for name, value in scores.items()}})
        return scores
