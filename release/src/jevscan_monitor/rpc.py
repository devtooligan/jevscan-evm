"""Bounded read-only chain clients for finalized historical collection.

Credentials come from the process environment. Cache indexes omit credentials;
configured-secret echo checks provide defense in depth, not an authenticity or
privacy guarantee for arbitrary remote content. Keep workspaces private.
"""

import asyncio
import fcntl
import hashlib
import json
import os
import re
import time
from pathlib import Path
from typing import Callable, Self
from urllib.parse import unquote, urlsplit

import aiohttp

from jevscan_monitor.configuration import data_directory

HERE = Path(__file__).resolve().parent
CACHE_DIR = data_directory() / "cache"
MAX_RESPONSE_BYTES = 32 * 1024 * 1024
SECRET_ENV = ("MAINNET_RPC_URL", "ETHERSCAN_API_KEY", "TYPESAFE_API_KEY")
RPC_CONCURRENCY = 24
MAX_ATTEMPTS = 6
RATE_LIMIT_CODES = {429, -32005}  # JSON-RPC error codes providers use for "slow down"
REVERT_CODE = 3  # "execution reverted": at a fixed block it is the same every time, so it is cached like a result
TRANSIENT_ETHERSCAN = ("rate limit", "timeout", "server too busy")  # words in a status-0 answer that mean "try again"
# service -> (base URL, seconds between requests). Etherscan's three-per-second ceiling needs slack for its rolling
# window and retries, so use two per second; the others publish no limit and get a polite half second.
SERVICES = {
    "etherscan": ("https://api.etherscan.io/v2/api", 0.5),
    "alchemy_nft": ("", 0.2),  # base built at request time from MAINNET_RPC_URL, so the key is never in a constant
    "llama": ("https://coins.llama.fi", 0.5),
    "signatures": ("https://api.4byte.sourcify.dev", 0.5),
    "labels_dump": ("https://raw.githubusercontent.com", 0.5),
}


def scrub(text: str) -> str:
    """`text` with every configured secret, and the key in the RPC URL's path or query, replaced by its name."""
    for name in SECRET_ENV:
        value = os.environ.get(name)
        if not value:
            continue
        parts = [value]
        if name == "MAINNET_RPC_URL":
            url = urlsplit(value)
            parts += [p for p in url.path.split("/") + url.query.replace("=", "&").split("&") if len(p) >= 16]
        for part in parts:
            text = text.replace(part, f"<{name}>")
    return text


class DiskCache:
    """Raw response bodies at <root>/<namespace>/<key>.json, byte for byte as received, so they double as fixtures
    for a port. index.jsonl in each namespace maps a key back to the request that produced it."""

    def __init__(self, root: Path) -> None:
        self.root = root

    def path(self, namespace: str, request: dict) -> Path:
        if not re.fullmatch(r"[A-Za-z0-9_-]+(?:/[A-Za-z0-9_-]+)*", namespace):
            raise ValueError("Invalid cache namespace")
        key = hashlib.sha256(json.dumps(request, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        return self.root / namespace / f"{key}.json"

    def read(self, namespace: str, request: dict) -> str | None:
        path = self.path(namespace, request)
        return path.read_text() if path.exists() else None

    def write(self, namespace: str, request: dict, body: str) -> None:
        decoded = unquote(json.dumps(json.loads(body), ensure_ascii=False))
        if scrub(body) != body or scrub(decoded) != decoded:
            raise RuntimeError("Response contains configured credential material; refusing to cache")
        path = self.path(namespace, request)
        path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        # Enrichment fans out the same lookup from several processes when a resumed collection overlaps a prior one.
        # Lock the namespace to serialize writers. Body replacement is atomic;
        # the subsequent index append is not a cross-file transaction. A crash
        # may leave an unindexed body, which is safe to refetch but costs quota.
        with (path.parent / ".write.lock").open("a+") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            try:
                if path.exists():
                    return
                tmp = path.with_suffix(".tmp")
                tmp.write_text(body)
                os.replace(tmp, path)
                with (path.parent / "index.jsonl").open("a") as index:
                    index.write(json.dumps({"key": path.stem, "request": request}, sort_keys=True) + "\n")
            finally:
                fcntl.flock(lock, fcntl.LOCK_UN)

    def entries(self, namespace: str, predicate: Callable[[dict], bool] | None = None):
        """(request, raw body) for matching cached responses in `namespace`.

        Batch lookups read these first, so a change in how addresses fall into batches does not refetch what an earlier
        batch already answered. `predicate` examines the small index row before its raw body is opened; this matters
        for Etherscan, whose unrelated account-history responses are much larger than creation records.
        """
        self.path(namespace, {})  # validate even when reading the index directly
        index = self.root / namespace / "index.jsonl"
        if index.is_file():
            for line in index.read_text().splitlines():
                entry = json.loads(line)
                if not isinstance(entry.get("key"), str) or not re.fullmatch(r"[0-9a-f]{64}", entry["key"]):
                    raise ValueError("Invalid cache index key")
                if predicate is not None and not predicate(entry["request"]):
                    continue
                yield entry["request"], (index.parent / f"{entry['key']}.json").read_text()


class RpcError(RuntimeError):
    """The node answered with a JSON-RPC error."""

    def __init__(self, method: str, code: int, message: str) -> None:
        super().__init__(f"RPC {method} failed: {code} {scrub(message)}")
        self.code = code


class Rpc:
    """`async with Rpc(cache_dir) as rpc: block = await rpc.call("eth_getBlockByNumber", ["0x10", True])`.
    `stats` counts network requests and cache hits, so a warm run can show it made no network calls."""

    def __init__(self, cache_dir: Path = CACHE_DIR) -> None:
        self.cache = DiskCache(cache_dir)
        self.stats = {"network": 0, "cache_hits": 0}
        self.sem = asyncio.Semaphore(RPC_CONCURRENCY)
        self.inflight: dict[str, asyncio.Task[str]] = {}
        self.inflight_lock = asyncio.Lock()

    async def __aenter__(self) -> Self:
        self.url = os.environ.get("MAINNET_RPC_URL")
        if not self.url:
            raise RuntimeError("Export MAINNET_RPC_URL for an archive node with debug trace APIs")
        endpoint = urlsplit(self.url)
        if endpoint.scheme != "https" or not endpoint.hostname or endpoint.username or endpoint.password:
            raise ValueError("MAINNET_RPC_URL must be an HTTPS endpoint without userinfo")
        self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=180))
        try:
            chain = json.loads(await self.post("eth_chainId", []))["result"]
            if chain != "0x1":
                raise RuntimeError("Only Ethereum mainnet (chain ID 1) is supported")
            genesis = json.loads(await self.post("eth_getBlockByNumber", ["0x0", False]))["result"]
            if not isinstance(genesis, dict) or not re.fullmatch(r"0x[0-9a-fA-F]{64}", genesis.get("hash", "")):
                raise RuntimeError("Cannot establish RPC chain identity")
            self.chain_identity = genesis["hash"].lower()
            return self
        except BaseException:
            await self.session.close()
            raise

    async def __aexit__(self, *exc) -> None:
        await cancel_inflight(self.inflight)
        await self.session.close()

    async def call(self, method: str, params: list, cached: bool = True) -> object:
        """The `result` of one JSON-RPC call. With `cached` false the cache is neither read nor written."""
        def mutable(value):
            if isinstance(value, str):
                return value in {"latest", "pending", "safe", "finalized"}
            if isinstance(value, (list, tuple)):
                return any(mutable(item) for item in value)
            if isinstance(value, dict):
                return any(mutable(item) for item in value.values())
            return False
        cached = cached and method not in {"eth_blockNumber", "eth_chainId"} and not mutable(params)
        request = {"chain": self.chain_identity, "method": method, "params": params}
        namespace = f"rpc/{method}"
        body = self.cache.read(namespace, request) if cached else None
        if body is not None:
            self.stats["cache_hits"] += 1
        else:
            if cached:
                body = await self.cached_post(namespace, request, method, params)
            else:
                body = await self.post(method, params)
        parsed = rpc_envelope(body)
        if "error" in parsed:
            raise RpcError(method, parsed["error"]["code"], str(parsed["error"].get("message", "")))
        return parsed["result"]

    async def cached_post(self, namespace: str, request: dict, method: str, params: list) -> str:
        """Fetch one cache miss once when concurrent fact reads ask the same immutable question."""
        key = self.cache.path(namespace, request).stem
        async with self.inflight_lock:
            task = self.inflight.get(key)
            if task is None:
                task = asyncio.create_task(self.post(method, params))
                self.inflight[key] = task
        try:
            body = await asyncio.shield(task)
            parsed = json.loads(body)
            if parsed.get("result") is not None or "error" in parsed:
                self.cache.write(namespace, request, body)
            return body
        finally:
            if task.done():
                async with self.inflight_lock:
                    if self.inflight.get(key) is task:
                        del self.inflight[key]

    async def post(self, method: str, params: list) -> str:
        """The raw response body of a call that succeeded or reverted; rate limits and server errors are retried
        with backoff, and any other node error is raised."""
        payload = {"jsonrpc": "2.0", "id": 1, "method": method, "params": params}
        async with self.sem:
            for attempt in range(MAX_ATTEMPTS):
                self.stats["network"] += 1
                try:
                    async with self.session.post(self.url, json=payload, allow_redirects=False) as resp:
                        status, body = resp.status, await bounded_text(resp)
                except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                    # `from None`: the original exception text holds the URL, and the URL holds a key.
                    failure = RuntimeError(f"RPC {method}: transport error ({type(e).__name__})")
                    if attempt == MAX_ATTEMPTS - 1:
                        raise failure from None
                    await asyncio.sleep(2**attempt)
                    continue
                error = None
                if status == 200:
                    parsed = rpc_envelope(body)
                    error = parsed.get("error")
                    if error is None and "result" not in parsed:
                        raise RuntimeError(f"RPC {method}: response has neither result nor error")
                    if error is None or error.get("code") == REVERT_CODE:
                        return body
                    if error.get("code") not in RATE_LIMIT_CODES:
                        raise RpcError(method, error.get("code", 0), str(error.get("message", "")))
                elif status != 429 and status < 500:
                    raise RuntimeError(f"RPC {method}: HTTP {status}")
                if attempt < MAX_ATTEMPTS - 1:
                    await asyncio.sleep(2**attempt)
        raise RuntimeError(f"RPC {method}: still rate-limited or failing after {MAX_ATTEMPTS} attempts")


class Http:
    """Cached, paced GET for the public APIs in SERVICES. Credentials go in `secret`, which is sent but never
    hashed into the cache key or written to the index."""

    def __init__(self, cache_dir: Path = CACHE_DIR) -> None:
        self.cache = DiskCache(cache_dir)
        self.stats = {"network": 0, "cache_hits": 0}
        self.locks = {service: asyncio.Lock() for service in SERVICES}
        self.next_at = dict.fromkeys(SERVICES, 0.0)
        self.inflight: dict[str, asyncio.Task[str]] = {}
        self.inflight_lock = asyncio.Lock()

    async def __aenter__(self) -> Self:
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=60), headers={"User-Agent": "jevscan-chain-monitor"}
        )
        return self

    async def __aexit__(self, *exc) -> None:
        await cancel_inflight(self.inflight)
        await self.session.close()

    async def get(self, service: str, path: str, params: dict[str, str], secret: dict[str, str] | None = None,
                  cached: bool = True) -> dict | list:
        request = {"path": path, "params": params}
        body = self.cache.read(service, request) if cached else None
        if body is not None:
            self.stats["cache_hits"] += 1
            return http_payload(service, body)
        if cached:
            body = await self.cached_get(service, request, path, params, secret)
            return http_payload(service, body)

        body = await self.get_uncached(service, path, params, secret)
        return http_payload(service, body)

    async def cached_get(self, service: str, request: dict, path: str, params: dict[str, str],
                         secret: dict[str, str] | None) -> str:
        key = service + ":" + self.cache.path(service, request).stem
        async with self.inflight_lock:
            task = self.inflight.get(key)
            if task is None:
                task = asyncio.create_task(self.get_uncached(service, path, params, secret))
                self.inflight[key] = task
        try:
            body = await asyncio.shield(task)
            self.cache.write(service, request, body)
            return body
        finally:
            if task.done():
                async with self.inflight_lock:
                    if self.inflight.get(key) is task:
                        del self.inflight[key]

    async def get_uncached(self, service: str, path: str, params: dict[str, str],
                           secret: dict[str, str] | None) -> str:
        base, interval = SERVICES[service]
        if service == "alchemy_nft":
            base = alchemy_nft_base()
        for attempt in range(MAX_ATTEMPTS):
            async with self.locks[service]:
                wait = self.next_at[service] - time.monotonic()
                if wait > 0:
                    await asyncio.sleep(wait)
                self.next_at[service] = time.monotonic() + interval
            self.stats["network"] += 1
            try:
                async with self.session.get(base + path, params=params | (secret or {}), allow_redirects=False) as resp:
                    status, body = resp.status, await bounded_text(resp)
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                failure = RuntimeError(f"{service} {path}: transport error ({type(e).__name__})")
                if attempt == MAX_ATTEMPTS - 1:
                    raise failure from None
                await asyncio.sleep(2**attempt)
                continue
            if status == 200 and not transient(service, body):
                http_payload(service, body)
                return body
            if status != 200 and status != 429 and status < 500:
                raise RuntimeError(f"{service}: HTTP {status}")
            if attempt < MAX_ATTEMPTS - 1:
                await asyncio.sleep(2**attempt)
        raise RuntimeError(f"{service} {path}: still rate-limited or failing after {MAX_ATTEMPTS} attempts")

    async def etherscan(self, params: dict[str, str], cached: bool = True) -> list | str | None:
        """The `result` of an Etherscan V2 mainnet call. "No data"/"No transactions" answers are results (empty
        or null); any other NOTOK is an error."""
        key = os.environ.get("ETHERSCAN_API_KEY")
        if not key:
            raise RuntimeError("Export ETHERSCAN_API_KEY before collecting enriched facts")
        answer = await self.get("etherscan", "", {"chainid": "1"} | params, {"apikey": key}, cached)
        if answer["status"] != "1" and not answer["message"].startswith("No "):
            raise RuntimeError(f"etherscan {params.get('action')}: {scrub(str(answer['result'])[:300])}")
        return answer["result"]


def alchemy_nft_base() -> str:
    """Alchemy's NFT API lives beside the JSON-RPC endpoint and takes the same key, in the path. The key is read from
    MAINNET_RPC_URL here and nowhere else; `scrub` removes it from any error text, and the cache key holds only the
    request path and parameters."""
    url = os.environ.get("MAINNET_RPC_URL", "")
    parts = urlsplit(url)
    key = parts.path.rstrip("/").rsplit("/", 1)[-1]
    if not parts.hostname or not parts.hostname.endswith(".g.alchemy.com") or len(key) < 16:
        raise RuntimeError("NFT floor prices need an Alchemy MAINNET_RPC_URL with the key in its path")
    return f"https://{parts.hostname}/nft/v3/{key}"


def transient(service: str, body: str) -> bool:
    """Etherscan reports its rate limit, and its own timeouts and overloads, as HTTP 200 with a status-0 body. Those
    must be retried and never cached: a cached one would fail every later run. Any other status-0 body is an answer
    ("No transactions found") or a real error, and is left to `etherscan` to judge."""
    if service != "etherscan":
        return False
    try:
        answer = json.loads(body)
    except ValueError:
        return False
    if not isinstance(answer, dict) or answer.get("status") != "0":
        return False
    text = f"{answer.get('message', '')} {answer.get('result', '')}".lower()
    return any(word in text for word in TRANSIENT_ETHERSCAN)


async def cancel_inflight(inflight: dict) -> None:
    tasks = list(inflight.values())
    for task in tasks:
        task.cancel()
    if tasks:
        await asyncio.gather(*tasks, return_exceptions=True)
    inflight.clear()


async def bounded_text(response) -> str:
    chunks = bytearray()
    async for chunk in response.content.iter_chunked(65536):
        chunks.extend(chunk)
        if len(chunks) > MAX_RESPONSE_BYTES:
            raise RuntimeError("External response exceeds collection size limit")
    try:
        return chunks.decode("utf-8")
    except UnicodeError:
        raise RuntimeError("External response is not valid UTF-8") from None


def rpc_envelope(body: str) -> dict:
    try:
        value = json.loads(body)
    except (ValueError, TypeError):
        raise RuntimeError("RPC returned invalid JSON") from None
    if (not isinstance(value, dict) or value.get("jsonrpc") != "2.0"
            or type(value.get("id")) is not int or value["id"] != 1
            or (("result" in value) == ("error" in value))):
        raise RuntimeError("RPC returned an invalid response envelope")
    if "error" in value:
        error = value["error"]
        if not isinstance(error, dict) or type(error.get("code")) is not int or not isinstance(error.get("message"), str):
            raise RuntimeError("RPC returned an invalid error object")
    return value


def http_payload(service: str, body: str):
    try:
        value = json.loads(body)
    except (ValueError, TypeError):
        raise RuntimeError("External service returned invalid JSON; response not cached") from None
    if not isinstance(value, (dict, list)):
        raise RuntimeError("External service returned an invalid payload")
    if service == "etherscan":
        if (not isinstance(value, dict) or not isinstance(value.get("message"), str)
                or "result" not in value or value.get("status") not in {"0", "1"}):
            raise RuntimeError("Explorer returned an invalid response")
        if value["status"] != "1" and not value["message"].startswith("No "):
            raise RuntimeError("Explorer rejected the request; response not cached")
    return value
