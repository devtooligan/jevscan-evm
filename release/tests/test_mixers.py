"""Tests for the mixer-payout list: log decoding, the look-back window, and the sweep's handling of refused ranges."""

import asyncio

import pytest

from jevscan_monitor import mixers
from jevscan_monitor.mixers import MixerPayouts, payout_of, sweep

WALLET = "0x" + "ab" * 20
POOL = "0x" + "11" * 20


def log(block: int, tx_index: int, recipient: str = WALLET) -> dict:
    data = "0x" + recipient[2:].rjust(64, "0") + "00" * 64  # to, nullifierHash, fee
    return {"data": data, "blockNumber": hex(block), "transactionIndex": hex(tx_index), "address": POOL,
            "transactionHash": "0x" + "cd" * 32, "blockHash": "0x" + format(block, "064x"),
            "logIndex": hex(tx_index), "removed": False, "topics": [mixers.WITHDRAWAL, "0x" + "00" * 32]}


def test_payout_of_reads_the_recipient_from_the_first_data_word():
    assert payout_of(log(100, 7)) == {"recipient": WALLET, "block": 100, "tx_index": 7, "pool": POOL}


def test_payout_of_rejects_a_log_without_a_recipient():
    with pytest.raises(ValueError):
        payout_of({"data": "0x", "blockNumber": "0x1", "transactionIndex": "0x0", "address": POOL,
                   "transactionHash": "0x00"})


def test_latest_counts_only_payouts_before_the_transaction_and_inside_the_lookback():
    payouts = MixerPayouts([payout_of(log(1_000, 5)), payout_of(log(5_000, 2))])
    assert payouts.latest(WALLET, 5_000, 3, 10_000) == (5_000, POOL)  # same block, earlier transaction
    assert payouts.latest(WALLET, 5_000, 2, 10_000) == (1_000, POOL)  # the payout at the same position is not "before"
    assert payouts.latest(WALLET, 5_000, 1, 3_000) is None  # only the old payout is before, and it is too old
    assert payouts.latest(WALLET, 900, 0, 10_000) is None  # nothing before this transaction
    assert payouts.latest(WALLET.upper().replace("0X", "0x"), 6_000, 0, 10_000) == (5_000, POOL)  # address case does not matter
    assert payouts.latest("0x" + "ef" * 20, 6_000, 0, 10_000) is None  # a wallet no mixer ever paid


class RefusingRpc:
    """Refuses any eth_getLogs range wider than `limit` blocks, as a provider does for an oversized response."""

    def __init__(self, limit: int, logs: list[dict]) -> None:
        self.limit, self.logs, self.ranges = limit, logs, []

    async def call(self, method: str, params: list, cached: bool = True) -> list[dict]:
        start, stop = int(params[0]["fromBlock"], 16), int(params[0]["toBlock"], 16)
        if stop - start + 1 > self.limit:
            raise RuntimeError("RPC eth_getLogs: HTTP 400: response too large")
        self.ranges.append((start, stop))
        return [entry for entry in self.logs if start <= int(entry["blockNumber"], 16) <= stop]


def test_sweep_halves_a_refused_range_and_still_returns_every_payout_once():
    rpc = RefusingRpc(limit=30_000, logs=[log(10, 0), log(40_000, 1), log(99_999, 2), log(150_000, 3)])
    found = asyncio.run(sweep(rpc, [POOL], 0, 150_000))
    assert [p["block"] for p in found] == [10, 40_000, 99_999, 150_000]
    assert rpc.ranges[0][0] == 0 and rpc.ranges[-1][1] == 150_000
    assert all(later[0] == earlier[1] + 1 for earlier, later in zip(rpc.ranges, rpc.ranges[1:]))  # no gap, no overlap


def test_sweep_raises_when_even_the_smallest_range_is_refused():
    rpc = RefusingRpc(limit=mixers.MIN_SWEEP_BLOCKS // 2, logs=[])
    with pytest.raises(RuntimeError):
        asyncio.run(sweep(rpc, [POOL], 0, 10_000))


@pytest.mark.parametrize("change", [{"removed": True}, {"address": WALLET}, {"topics": []},
    {"data": "0x"}, {"blockHash": "invalid"}])
def test_inconsistent_mixer_response_rejected(change):
    rpc = RefusingRpc(101, [log(1, 0) | change])
    with pytest.raises(ValueError):
        asyncio.run(sweep(rpc, [POOL], 0, 100))


def test_duplicate_mixer_log_rejected():
    rpc = RefusingRpc(101, [log(1, 0), log(1, 0)])
    with pytest.raises(ValueError):
        asyncio.run(sweep(rpc, [POOL], 0, 100))
