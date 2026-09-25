"""Wallets paid by a mixer, from the mixers' own payout logs, so "was this sender funded by a mixer?" is a local lookup.

A Tornado-style pool emits Withdrawal(address to, bytes32 nullifierHash, address indexed relayer, uint256 fee) on
every payout, and `to` is the first word of the log data. One eth_getLogs sweep over the labeled mixer contracts lists
every payout ever made (two years: about 99,000 payouts in under a minute); a live monitor would extend the same list
from the logs of each new block it already reads. This replaces asking Etherscan for every sender's first transfers,
which was the slowest step of a run and missed payouts beyond the first page of results.

Not covered: mixers that do not emit this event (Privacy Pools, Railgun) and funds that pass through one more wallet
before reaching the sender.

Use `jevscan-monitor prepare` to build or extend the finalized mixer index.
"""

import bisect
import fcntl
import json
from pathlib import Path

from jevscan_monitor.inputs import quantity, require_hash, validate_logs
from jevscan_monitor.rpc import CACHE_DIR, Rpc
from jevscan_monitor.provider import atomic_json

# cast sig-event "Withdrawal(address,bytes32,address,uint256)"
WITHDRAWAL = "0xe9e508bad6d4c3227e881ca19068f099da81b5164dd6d62b2eaf1e8bc6c34931"
FIRST_BLOCK = 9_000_000  # November 2019, before the first Tornado pool existed
SWEEP_BLOCKS = 100_000
MIN_SWEEP_BLOCKS = 1_000  # a range this small that still fails is a real error, not an oversized response
BLOCKS_PER_DAY = 7_200  # 12-second slots; missed slots make a "day" a few minutes longer, which does not matter here
MIXERS_DIR = CACHE_DIR / "mixers"


def payout_of(log: dict) -> dict:
    """One payout from its Withdrawal log. The recipient is the low 20 bytes of the first data word."""
    data = log["data"]
    if len(data) < 2 + 64:
        raise ValueError(f"Withdrawal log {log['transactionHash']} has no recipient word")
    return {"recipient": "0x" + data[2:66][-40:].lower(), "block": int(log["blockNumber"], 16),
            "tx_index": int(log["transactionIndex"], 16), "pool": log["address"].lower()}


async def sweep(rpc: Rpc, pools: list[str], start: int, end: int) -> list[dict]:
    """Every payout by `pools` in blocks start..end. A provider refuses a response that is too large, so a refused
    range is halved and retried; a refusal at MIN_SWEEP_BLOCKS is raised, because it is not about size."""
    payouts, span, seen = [], SWEEP_BLOCKS, set()
    allowed = {pool.lower() for pool in pools}
    while start <= end:
        stop = min(start + span - 1, end)
        try:
            logs = await rpc.call("eth_getLogs", [{"address": pools, "topics": [WITHDRAWAL], "fromBlock": hex(start),
                                                   "toBlock": hex(stop)}], cached=False)
        except RuntimeError:
            if span <= MIN_SWEEP_BLOCKS:
                raise
            span //= 2
            continue
        if not isinstance(logs, list) or len(logs) > 100000:
            raise ValueError("Invalid or oversized mixer log response")
        for log in logs:
            validate_logs([log])
            block, index = quantity(log.get("blockNumber")), quantity(log.get("logIndex"))
            identity = (require_hash(log.get("blockHash")), index)
            require_hash(log.get("transactionHash"))
            quantity(log.get("transactionIndex"))
            if (log["address"].lower() not in allowed or not start <= block <= stop
                    or log.get("removed") is not False or len(log["topics"]) != 2
                    or log["topics"][0].lower() != WITHDRAWAL or len(log["data"]) != 194
                    or identity in seen):
                raise ValueError("Mixer log does not match the finalized query")
            seen.add(identity)
            payouts.append(payout_of(log))
        if len(payouts) > 1000000:
            raise ValueError("Mixer snapshot exceeds supported size")
        start = stop + 1
    return payouts


class MixerPayouts:
    """`payouts.latest(recipient, block, tx_index, lookback_blocks)`: the (block, pool) of the wallet's most recent
    mixer payout strictly before that transaction and within the look-back, or None."""

    def __init__(self, payouts: list[dict]) -> None:
        self.by_recipient: dict[str, list[tuple[int, int, str]]] = {}
        for p in payouts:
            self.by_recipient.setdefault(p["recipient"], []).append((p["block"], p["tx_index"], p["pool"]))
        for positions in self.by_recipient.values():
            positions.sort()

    def latest(self, recipient: str, block: int, tx_index: int, lookback_blocks: int) -> tuple[int, str] | None:
        positions = self.by_recipient.get(recipient.lower())
        if not positions:
            return None
        # A two-part key sorts before every payout at that position, so the transaction's own position is not "before".
        before = bisect.bisect_left(positions, (block, tx_index))
        if before == 0:
            return None
        paid_block, _, pool = positions[before - 1]
        return (paid_block, pool) if block - paid_block <= lookback_blocks else None


def load(directory: Path = MIXERS_DIR) -> tuple[MixerPayouts, int]:
    """The saved payouts and the last block they cover. A lookup for a later block would silently miss payouts, so
    callers must compare that block with the one they ask about."""
    snapshot = directory / "snapshot.json"
    if snapshot.is_file():
        value = json.loads(snapshot.read_text())
        return MixerPayouts(value["payouts"]), value["meta"]["synced_to"]
    meta_file = directory / "meta.json"
    if not meta_file.is_file():
        raise RuntimeError("Mixer index missing: run `jevscan-monitor prepare` first")
    payouts = [json.loads(line) for line in (directory / "payouts.jsonl").read_text().splitlines()]
    return MixerPayouts(payouts), json.loads(meta_file.read_text())["synced_to"]


async def sync(rpc: Rpc, pools: list[str], directory: Path = MIXERS_DIR) -> tuple[int, int]:
    """Stage a complete finalized snapshot before replacing the previous one.

    A failed rebuild leaves the prior snapshot intact. A separate nonblocking
    lock excludes simultaneous writers without blocking the event loop.
    """
    directory.mkdir(parents=True, exist_ok=True, mode=0o700)
    with (directory / "sync.lock").open("a+") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        snapshot = directory / "snapshot.json"
        previous = json.loads(snapshot.read_text()) if snapshot.exists() else None
        if previous and previous["meta"]["pools"] == sorted(pools):
            meta, payouts = previous["meta"], previous["payouts"]
        else:
            meta, payouts = {"pools": sorted(pools), "synced_to": FIRST_BLOCK - 1}, []
        finalized = await rpc.call("eth_getBlockByNumber", ["finalized", False], cached=False)
        if not isinstance(finalized, dict):
            raise RuntimeError("Node does not provide a finalized block; mixer index not changed")
        head = int(finalized["number"], 16)
        if head < meta["synced_to"]:
            raise RuntimeError("Finalized chain moved behind the mixer snapshot")
        added = await sweep(rpc, meta["pools"], meta["synced_to"] + 1, head)
        atomic_json(snapshot, {"meta": meta | {"synced_to": head}, "payouts": payouts + added})
        return len(added), head
