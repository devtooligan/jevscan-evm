"""Lookups: what counts as a wallet, which prices are trusted, and how a sender's funding and mixer payouts are read."""

import asyncio
import json

import pytest

from jevscan_monitor import enrich, facts
from jevscan_monitor.mixers import MixerPayouts
from tests.helpers import (
    BLOCK_NUMBER,
    BLOCK_TIME,
    MIXER,
    SENDER,
    TOKEN,
    WALLET,
    addr,
    chain_data,
    frame,
    transfer,
)

EXCHANGE, OLD_HAND = addr(81), addr(82)


class FakeCache:
    def entries(self, namespace: str, predicate=None):
        return iter(())


class FakeHttp:
    """Answers Etherscan and price requests from canned tables."""

    def __init__(self, etherscan: dict | None = None, coins: dict | None = None) -> None:
        self.cache, self.answers, self.coins = FakeCache(), etherscan or {}, coins or {}

    async def etherscan(self, params: dict) -> list:
        return self.answers.get(params["action"], [])

    async def get(self, service: str, path: str, params: dict) -> dict:
        return {"coins": {key: self.coins[key] for key in path.rsplit("/", 1)[1].split(",") if key in self.coins}}


def test_a_wallet_with_delegated_code_is_still_a_wallet():
    assert enrich.kind_of("0x") == "wallet"
    assert enrich.kind_of("0xef0100" + "ab" * 20) == "delegated wallet"
    assert enrich.kind_of("0x6080604052") == "contract"


def row(sender: str, block: int, index: int, seconds_ago: int, value: int = 10**18, error: str = "0") -> dict:
    return {"from": sender, "to": SENDER, "value": str(value), "blockNumber": str(block), "transactionIndex": str(index),
            "timeStamp": str(BLOCK_TIME - seconds_ago), "isError": error}


def funding(etherscan: dict) -> facts.Funding | None:
    core = facts.extract(*chain_data(frame(SENDER, WALLET, value=1)))
    return asyncio.run(enrich.fetch_funding(FakeHttp(etherscan), core))


def test_first_funding_is_the_earliest_inbound_transfer_in_either_list():
    found = funding({"txlist": [row(EXCHANGE, 19_000_000, 4, 9_000)],
                     "txlistinternal": [row(MIXER, 18_999_999, 1, 9_012)]})
    assert found == {"timestamp": BLOCK_TIME - 9_012, "funder": MIXER}


def test_failed_empty_and_later_transfers_do_not_fund_the_sender():
    later = row(MIXER, 20_000_000, 9, 0)  # same block, after this transaction (index 3): the future
    assert funding({"txlist": [row(EXCHANGE, 5, 0, 99, error="1"), row(EXCHANGE, 6, 0, 98, value=0), later]}) is None


def payout(recipient: str, block: int, tx_index: int) -> dict:
    return {"recipient": recipient, "block": block, "tx_index": tx_index, "pool": MIXER}


def busy(sender: str, nonce: int, index: int) -> tuple[dict, dict, dict, dict]:
    """A transaction that is not trivial: two token transfers."""
    trace = frame(sender, TOKEN, logs=[transfer(TOKEN, sender, WALLET, 5), transfer(TOKEN, sender, EXCHANGE, 6)])
    return chain_data(trace, nonce=nonce, index=index)


def test_mixer_payouts_are_looked_up_per_transaction_for_the_given_senders_only():
    cores = [facts.extract(*busy(SENDER, 0, 3)), facts.extract(*busy(SENDER, 1, 9)), facts.extract(*busy(OLD_HAND, 7, 4))]
    paid = MixerPayouts([payout(SENDER, BLOCK_NUMBER - enrich.MIXER_LOOKBACK_BLOCKS - 1, 0), payout(SENDER, BLOCK_NUMBER, 5),
                         payout(OLD_HAND, BLOCK_NUMBER - 10, 0)])
    assert enrich.latest_mixer_payouts(cores, {SENDER}, paid) == {
        (SENDER, BLOCK_NUMBER, 3): None,  # the only payout before it is one block outside the look-back
        (SENDER, BLOCK_NUMBER, 9): (BLOCK_NUMBER, MIXER)}  # paid earlier in the same block


class FakeRpc:
    """Every address is a wallet with no balance and no history."""

    async def call(self, method: str, params: list, cached: bool = True) -> str:
        return "0x0" if method in ("eth_getTransactionCount", "eth_getBalance") else "0x"


def gather(monkeypatch, synced_to: int) -> facts.Context:
    paid = MixerPayouts([payout(OLD_HAND, BLOCK_NUMBER - 10, 0)])
    monkeypatch.setattr(enrich.mixers, "load", lambda: (paid, synced_to))
    cores = [facts.extract(*busy(SENDER, enrich.NEW_WALLET_NONCES - 1, 3)),
             facts.extract(*busy(OLD_HAND, enrich.NEW_WALLET_NONCES, 4)),
             facts.extract(*chain_data(frame(WALLET, EXCHANGE, value=1), nonce=0, index=5))]  # trivial: a plain payment
    eth = {"price": 2000.0, "symbol": "ETH", "timestamp": BLOCK_TIME - 900, "confidence": 0.99}
    http = FakeHttp({"txlist": [row(EXCHANGE, 19_000_000, 4, 9_000)]}, {"coingecko:ethereum": eth})
    return asyncio.run(enrich.gather(cores, {}, FakeRpc(), http))


def test_first_funding_is_read_only_for_new_wallets_and_mixer_payouts_for_every_busy_sender(monkeypatch):
    ctx = gather(monkeypatch, synced_to=BLOCK_NUMBER)
    assert ctx.funding == {SENDER: {"timestamp": BLOCK_TIME - 9_000, "funder": EXCHANGE}}  # OLD_HAND has 5 prior transactions
    assert ctx.mixer_payouts == {(SENDER, BLOCK_NUMBER, 3): None, (OLD_HAND, BLOCK_NUMBER, 4): (BLOCK_NUMBER - 10, MIXER)}


def test_a_payout_list_that_ends_before_the_window_is_an_error(monkeypatch):
    with pytest.raises(RuntimeError, match="mixer payout list ends at block"):
        gather(monkeypatch, synced_to=BLOCK_NUMBER - 1)


def prices(coins: dict) -> tuple[dict, float]:
    return asyncio.run(enrich.fetch_prices(FakeHttp(coins=coins), {addr(1), addr(2), addr(3)}, BLOCK_TIME))


def test_a_price_must_be_confident_and_from_before_the_window():
    eth = {"price": 2000.0, "symbol": "ETH", "timestamp": BLOCK_TIME - 900, "confidence": 0.99}
    good = {"price": 1.0, "symbol": "GOOD", "decimals": 6, "timestamp": BLOCK_TIME - 60, "confidence": 0.99}
    found, eth_usd = prices({"coingecko:ethereum": eth, f"ethereum:{addr(1)}": good,
                             f"ethereum:{addr(2)}": good | {"confidence": 0.5},
                             f"ethereum:{addr(3)}": good | {"timestamp": BLOCK_TIME + 60}})
    assert eth_usd == 2000.0
    assert found == {addr(1): {"usd": 1.0, "symbol": "GOOD", "decimals": 6}}  # the others are unpriced, not defaulted


def test_no_eth_price_is_an_error_not_a_default():
    with pytest.raises(RuntimeError, match="no ETH price"):
        prices({})


@pytest.mark.parametrize("field,bad", [("price", -1), ("price", True), ("price", float("nan")),
    ("price", float("inf")), ("price", 10**400), ("decimals", 1000000), ("decimals", -1),
    ("decimals", True), ("confidence", 2), ("confidence", float("nan")), ("timestamp", -1)])
def test_invalid_external_token_quote_stays_unpriced(field, bad):
    eth = {"price": 2000, "symbol": "ETH", "timestamp": BLOCK_TIME - 1, "confidence": .99}
    quote = eth | {"decimals": 18, field: bad}
    assert prices({"coingecko:ethereum": eth, f"ethereum:{addr(1)}": quote}) == ({}, 2000)


@pytest.mark.parametrize("bad", [-1, 0, True, float("nan"), float("inf")])
def test_invalid_eth_price_stops_collection(bad):
    with pytest.raises(RuntimeError, match="no ETH price"):
        prices({"coingecko:ethereum": {"price": bad, "timestamp": BLOCK_TIME - 1, "confidence": .99}})


def test_cached_batches_answer_before_the_network_is_asked():
    class Cached(FakeHttp):
        async def get(self, service, path, params):
            raise AssertionError("everything asked for is already cached")

    http = Cached()
    path = f"/prices/historical/{BLOCK_TIME - enrich.PRICE_LEAD_SECONDS}/coingecko:ethereum,ethereum:{addr(1)}"
    body = {"coins": {"coingecko:ethereum": {"price": 1500.0, "symbol": "ETH", "timestamp": BLOCK_TIME - 5, "confidence": 0.99}}}
    http.cache.entries = lambda namespace: iter([({"path": path, "params": {}}, json.dumps(body))])
    assert asyncio.run(enrich.fetch_prices(http, {addr(1)}, BLOCK_TIME)) == ({}, 1500.0)


def test_a_balance_read_counts_what_earlier_transactions_in_the_block_moved():
    """The node answers as of the end of the previous block. A pool paid 100 earlier in the block and drained of 100
    now has lost its whole balance, not more than it held."""
    from tests.helpers import POOL_A, TOKEN, transfer
    paid = facts.extract(*chain_data(frame(SENDER, TOKEN, logs=[transfer(TOKEN, SENDER, POOL_A, 100)]), index=1))
    drained = facts.extract(*chain_data(frame(SENDER, TOKEN, logs=[transfer(TOKEN, POOL_A, WALLET, 100)]), index=4))
    block = int(paid.tx["blockNumber"], 16)
    earlier, same_sender = enrich.moved_earlier_in_block([paid, drained], [[(POOL_A, TOKEN)], [(POOL_A, TOKEN)]])
    assert earlier == {(POOL_A, TOKEN, block, 1): 0, (POOL_A, TOKEN, block, 4): 100}
    # the same sender put the 100 in at index 1: the shape of a sandwich's front and back legs
    assert same_sender == {(POOL_A, TOKEN, block, 4): (100, 1)}


def test_a_deposit_by_another_sender_earlier_in_the_block_is_not_a_pairing():
    from tests.helpers import POOL_A, TOKEN, transfer
    paid = facts.extract(*chain_data(frame(WALLET, TOKEN, logs=[transfer(TOKEN, WALLET, POOL_A, 100)]), index=1))
    drained = facts.extract(*chain_data(frame(SENDER, TOKEN, logs=[transfer(TOKEN, POOL_A, SENDER, 100)]), index=4))
    _, same_sender = enrich.moved_earlier_in_block([paid, drained], [[], [(POOL_A, TOKEN)]])
    assert same_sender == {}


def test_nft_floors_price_only_verified_collections_and_name_them():
    apes, fake = addr(84), addr(85)
    answers = {
        ("/getContractMetadata", apes): {"name": "BoredApeYachtClub", "openSeaMetadata": {"collectionName": "Bored Ape Yacht Club", "safelistRequestStatus": "verified"}},
        ("/getFloorPrice", apes): {"openSea": {"floorPrice": 6.5, "priceCurrency": "ETH"}},
        ("/getContractMetadata", fake): {"name": "Bored Ape Yacht Club", "openSeaMetadata": {"collectionName": "Bored Ape Yacht Club", "safelistRequestStatus": "not_requested"}},
    }

    calls = []

    class NftHttp:
        async def get(self, service, path, params, secret=None, cached=True):
            assert service == "alchemy_nft"
            calls.append((path, params["contractAddress"]))
            return answers[(path, params["contractAddress"])]

    nfts, prices = asyncio.run(enrich.fetch_nfts(NftHttp(), {apes, fake}, 2_000.0))
    assert nfts == {apes: {"name": "Bored Ape Yacht Club", "verified": True, "floor_usd": 13_000.0},
                    fake: {"name": None, "verified": False, "floor_usd": None}}
    assert prices == {apes: {"usd": 13_000.0, "symbol": "Bored Ape Yacht Club", "decimals": 0}}
    assert ("/getFloorPrice", fake) not in calls  # no floor is asked for an unverified collection


def test_the_lookups_read_a_watched_contracts_balance_when_a_later_transaction_enters_through_it(monkeypatch):
    """A Safe delegatecalls into the sender's own contract; the next transaction through the Safe drains it. The drain's
    entry contract has few callers and no label, which alone would make it 'the sender's own'; the watch overrides that,
    so the Safe's balance is read and its loss can be described."""
    from jevscan_monitor.facts import TOPIC
    from tests.helpers import TOKEN, transfer
    safe, own, thief = addr(86), addr(87), addr(88)
    executed = {"address": safe, "topics": [TOPIC["ExecutionSuccess(bytes32,uint256)"]], "data": "0x" + "00" * 64, "position": "0x1"}
    singleton = addr(89)
    swap = frame(SENDER, safe, calls=[frame(safe, singleton, kind="DELEGATECALL", calls=[frame(safe, own, kind="DELEGATECALL")])], logs=[executed])
    drain = frame(thief, safe, calls=[frame(safe, TOKEN, logs=[transfer(TOKEN, safe, thief, 400_000_000 * 10**6)])])
    cores = [facts.extract(*chain_data(swap, nonce=42, index=3)), facts.extract(*chain_data(drain, nonce=7, index=8))]
    reads = []

    class WatchRpc(FakeRpc):
        async def call(self, method, params, cached=True):
            if method == "eth_getCode":
                return "0x60" if params[0] in (safe, own, singleton, TOKEN) else "0x"
            if method == "eth_call" and params[0]["to"] == TOKEN:
                reads.append(params[0]["data"][-40:])
                return "0x" + format(400_000_000 * 10**6, "064x")
            return await super().call(method, params, cached)

    monkeypatch.setattr(enrich.mixers, "load", lambda: (MixerPayouts([]), BLOCK_NUMBER))
    old = {safe: {"creator": addr(97), "block": 1, "timestamp": BLOCK_TIME - 4 * 365 * 86400}, own: {"creator": SENDER, "block": 1, "timestamp": BLOCK_TIME - 2 * 86400}}
    monkeypatch.setattr(enrich, "fetch_creations", lambda http, contracts: _ready(old))
    eth = {"price": 2000.0, "symbol": "ETH", "timestamp": BLOCK_TIME - 900, "confidence": 0.99}
    usdx = {"price": 1.0, "symbol": "USDX", "decimals": 6, "timestamp": BLOCK_TIME - 900, "confidence": 0.99}
    http = FakeHttp({"txlist": []}, {"coingecko:ethereum": eth, f"ethereum:{TOKEN}": usdx})
    ctx = asyncio.run(enrich.gather(cores, {}, WatchRpc(), http))
    assert (safe, BLOCK_NUMBER, 8) not in ctx.same_sender_deposits
    assert ctx.balances_before[(safe, TOKEN, BLOCK_NUMBER, 8)] == 400_000_000 * 10**6  # the Safe's balance was read for the drain
    assert reads == [safe[2:]]


async def _ready(value):
    return value
