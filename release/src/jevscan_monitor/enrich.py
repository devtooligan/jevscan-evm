"""The lookups a window's transactions need beyond their own data: prices, code, contract creation, balances one
block earlier, sender funding, source verification, and function names. All I/O of the facts layer is here, and every
successful cacheable responses are retained locally by rpc.py.

Etherscan reads are skipped for trivial transactions, except the
creation date of a labeled contract, which the 30-day label rule needs. Whether a mixer paid the sender comes from the
local payout list (mixers.py), not from Etherscan; a sender's first funding is still an Etherscan read, made
only for wallets with few prior transactions, where wallet age matters.
"""

import asyncio
from functools import cache
import json
import math
import re

from jevscan_monitor import mixers
from jevscan_monitor.facts import (
    ESTABLISHED_SECONDS,
    ETH,
    FUNCTION_NAME,
    PUBLIC_SENDERS,
    Context,
    Core,
    Creation,
    Funding,
    Label,
    Price,
    cast,
    created_side,
    logic_changes_of,
    watched_before,
    whole_side,
)
from jevscan_monitor.rpc import Http, Rpc, RpcError

PRICE_LEAD_SECONDS = 1800  # ask for prices half an hour before the window, so none can come from after the hack
PRICE_SEARCH_WIDTH = "1h"
MIN_PRICE_CONFIDENCE = 0.9  # DefiLlama's own score; below it a price is an illiquid pool's guess
PRICE_BATCH = 60
CREATION_BATCH = 5  # Etherscan's limit per call
SIGNATURE_BATCH = 40
FUNDING_ROWS = 50
NEW_WALLET_NONCES = 5  # first funding is looked up only for senders with fewer prior transactions than this
MIXER_LOOKBACK_BLOCKS = 30 * mixers.BLOCKS_PER_DAY  # 216,000 blocks; the fact is named mixer_funded_within_30_days
PRIOR_DAY_BLOCKS = 7200
PRIOR_DAY_ROWS = 100
BALANCE_OF = "0x70a08231"
DECIMALS = "0x313ce567"
PLAIN_FUNCTION = re.compile(r"[A-Za-z_][A-Za-z0-9_]{0,39}")


@cache
def mixer_payouts() -> tuple[mixers.MixerPayouts, int]:
    """Load the immutable local mixer index once per enrichment process."""
    return mixers.load()


def chunks(items: list, size: int) -> list[list]:
    return [items[i:i + size] for i in range(0, len(items), size)]


def kind_of(code: str) -> str:
    """EIP-7702 lets a wallet point at code (0xef0100 plus an address), so "has code" does not mean "contract"."""
    if code in ("0x", "0x0"):
        return "wallet"
    return "delegated wallet" if code.startswith("0xef0100") and len(code) == 48 else "contract"


def finite_positive(value: object) -> bool:
    return type(value) in (int, float) and 0 < value <= 1e18 and math.isfinite(value)


def valid_quote(coin: object, window_start: int, *, token: bool) -> bool:
    if not isinstance(coin, dict) or not finite_positive(coin.get("price")):
        return False
    timestamp, confidence = coin.get("timestamp"), coin.get("confidence")
    if (type(timestamp) is not int or not 0 < timestamp <= window_start
            or type(confidence) not in (int, float) or not MIN_PRICE_CONFIDENCE <= confidence <= 1):
        return False
    return not token or (type(coin.get("decimals")) is int and 0 <= coin["decimals"] <= 77
                         and isinstance(coin.get("symbol"), str) and len(coin["symbol"]) <= 128)


async def fetch_prices(http: Http, assets: set[str], window_start: int) -> tuple[dict[str, Price], float]:
    """Confident prices from before the window for `assets`, and the ETH price. A token with no such price is simply
    absent: it is unpriced, never given a default."""
    at = window_start - PRICE_LEAD_SECONDS
    path = f"/prices/historical/{at}/"
    known: dict[str, dict | None] = {}
    for request, body in http.cache.entries("llama"):
        if request["path"].startswith(path):
            coins = json.loads(body)["coins"]
            for key in request["path"][len(path):].split(","):
                known[key] = coins.get(key)
    wanted = sorted(({"coingecko:ethereum"} | {f"ethereum:{a}" for a in assets}) - set(known))
    for batch in chunks(wanted, PRICE_BATCH):
        answer = await http.get("llama", path + ",".join(batch), {"searchWidth": PRICE_SEARCH_WIDTH})
        for key in batch:
            known[key] = answer["coins"].get(key)
    prices: dict[str, Price] = {}
    for asset in assets:
        coin = known.get(f"ethereum:{asset}")
        if valid_quote(coin, window_start, token=True):
            prices[asset] = {"usd": coin["price"], "symbol": coin["symbol"], "decimals": coin["decimals"]}
    eth = known.get("coingecko:ethereum")
    if not valid_quote(eth, window_start, token=False):
        raise RuntimeError("no ETH price from before the window: every USD figure would be missing")
    return prices, eth["price"]


async def fetch_creations(http: Http, contracts: set[str]) -> dict[str, Creation | None]:
    known: dict[str, Creation | None] = {}
    for request, body in http.cache.entries(
            "etherscan", lambda request: request["params"].get("action") == "getcontractcreation"):
        rows = json.loads(body)["result"] or []
        for address in request["params"]["contractaddresses"].split(","):
            known[address] = None
        for row in rows:
            known[row["contractAddress"].lower()] = {"creator": row["contractCreator"].lower(),
                                                     "block": int(row["blockNumber"]),
                                                     "timestamp": int(row["timestamp"])}
    for batch in chunks(sorted(contracts - set(known)), CREATION_BATCH):
        rows = await http.etherscan({"module": "contract", "action": "getcontractcreation",
                                     "contractaddresses": ",".join(batch)}) or []
        for address in batch:
            known[address] = None
        for row in rows:
            known[row["contractAddress"].lower()] = {"creator": row["contractCreator"].lower(),
                                                     "block": int(row["blockNumber"]), "timestamp": int(row["timestamp"])}
    return {address: known[address] for address in contracts}


async def fetch_funding(http: Http, core: Core, address: str | None = None) -> Funding | None:
    """The first inbound ETH of the sender, or of `address`, from the first page of its normal and internal
    transactions up to this one. A contract pays out through an internal transaction, so both lists matter."""
    sender, block = (address or core.tx["from"]).lower(), int(core.tx["blockNumber"], 16)
    here = (block, int(core.tx["transactionIndex"], 16))
    inbound = []
    for action in ("txlist", "txlistinternal"):
        rows = await http.etherscan({"module": "account", "action": action, "address": sender, "startblock": "0",
                                     "endblock": str(block), "page": "1", "offset": str(FUNDING_ROWS), "sort": "asc"})
        for row in rows or []:
            at = (int(row["blockNumber"]), int(row.get("transactionIndex") or 0))
            if row["to"].lower() == sender and int(row["value"]) > 0 and row.get("isError", "0") == "0" and at < here:
                inbound.append((at, int(row["timeStamp"]), row["from"].lower()))
    if not inbound:
        return None
    _, timestamp, funder = min(inbound)
    return {"timestamp": timestamp, "funder": funder}


async def fetch_nfts(http: Http, collections: set[str], eth_usd: float) -> tuple[dict[str, dict], dict[str, Price]]:
    """Name, marketplace verification, and current floor price for each ERC-721 collection whose tokens moved. A
    floor becomes a price (one unit, decimals 0) only for a collection marked verified by OpenSea. That flag is not
    a trust guarantee. Floors are current, multiplied by historical ETH prices, not historical NFT valuations.
    Raw collection names are retained as metadata but never used as model-facing asset aliases."""
    nfts: dict[str, dict] = {}
    prices: dict[str, Price] = {}
    for address in sorted(collections):
        meta = await http.get("alchemy_nft", "/getContractMetadata", {"contractAddress": address})
        opensea = meta.get("openSeaMetadata") or {}
        verified = opensea.get("safelistRequestStatus") == "verified"
        floor_eth = None
        if verified:
            floor = await http.get("alchemy_nft", "/getFloorPrice", {"contractAddress": address})
            quote = (floor.get("openSea") or {})
            if finite_positive(quote.get("floorPrice")) and quote.get("priceCurrency") == "ETH":
                floor_eth = float(quote["floorPrice"])
        nfts[address] = {"name": (opensea.get("collectionName") or meta.get("name")) if verified else None,
                         "verified": verified, "floor_usd": None if floor_eth is None else round(floor_eth * eth_usd, 2)}
        if floor_eth is not None:
            prices[address] = {"usd": floor_eth * eth_usd, "symbol": nfts[address]["name"], "decimals": 0}
    return nfts, prices


def latest_mixer_payouts(cores: list[Core], senders: set[str],
                         payouts: mixers.MixerPayouts) -> dict[tuple[str, int, int], tuple[int, str] | None]:
    """(sender, block, transaction index) -> the (block, pool) of the sender's latest mixer payout before that
    transaction and inside the look-back, or None, for every transaction sent by one of `senders`."""
    found = {}
    for core in cores:
        sender, block, index = core.tx["from"].lower(), int(core.tx["blockNumber"], 16), int(core.tx["transactionIndex"], 16)
        if sender in senders:
            found[(sender, block, index)] = payouts.latest(sender, block, index, MIXER_LOOKBACK_BLOCKS)
    return found


async def fetch_function_names(http: Http, selectors: set[str]) -> dict[str, str]:
    """Names from the public signature database (Sourcify's 4byte API, where openchain's moved). A name is kept only
    if it looks like an identifier, preferring one seen in a verified contract."""
    known: dict[str, list] = {}
    for request, body in http.cache.entries("signatures"):
        known |= json.loads(body)["result"]["function"]
    for batch in chunks(sorted(selectors - set(known)), SIGNATURE_BATCH):
        answer = await http.get("signatures", "/signature-database/v1/lookup",
                                {"function": ",".join(batch), "filter": "true"})
        known |= answer["result"]["function"]
    names = {}
    for selector in selectors:
        matches = sorted(known.get(selector) or [], key=lambda m: not m.get("hasVerifiedContract"))
        name = matches[0]["name"].split("(")[0] if matches else ""
        if PLAIN_FUNCTION.fullmatch(name):
            names[selector] = name
    return names


def moved_earlier_in_block(cores: list[Core], reads: list[list[tuple[str, str]]]
                           ) -> tuple[dict[tuple[str, str, int, int], int], dict[tuple[str, str, int, int], tuple[int, int]]]:
    """For each transaction's balance reads (`reads` runs parallel to `cores`, which are in chain order), keyed by
    (holder, asset, block, transaction index): first, the net amount that earlier transactions of the same block
    moved into the holder, because the node reports balances as of the end of the previous block, so without it a
    pool that was paid earlier in the block reads as drained of more than it held; second, what earlier transactions
    of the block sent by the same sender put into the holder, as (amount, index of the first one), which is how the
    back leg of a sandwich takes out what the front leg put in."""
    earlier: dict[tuple[str, str, int, int], int] = {}
    same_sender: dict[tuple[str, str, int, int], tuple[int, int]] = {}
    running: dict[tuple[str, str], int] = {}
    put_in: dict[tuple[str, str, str], tuple[int, int]] = {}  # (transaction sender, holder, asset) -> (amount, index)
    current = None
    for core, wanted in zip(cores, reads):
        sender, block, index = core.tx["from"].lower(), int(core.tx["blockNumber"], 16), int(core.tx["transactionIndex"], 16)
        if block != current:
            current, running, put_in = block, {}, {}
        for holder, asset in wanted:
            earlier[(holder, asset, block, index)] = running.get((holder, asset), 0)
            if put_in.get((sender, holder, asset), (0, 0))[0] > 0:
                same_sender[(holder, asset, block, index)] = put_in[(sender, holder, asset)]
        for m in core.movements:
            running[(m.recipient, m.asset)] = running.get((m.recipient, m.asset), 0) + m.amount
            running[(m.sender, m.asset)] = running.get((m.sender, m.asset), 0) - m.amount
            amount, first = put_in.get((sender, m.recipient, m.asset), (0, index))
            put_in[(sender, m.recipient, m.asset)] = (amount + m.amount, first)
    return earlier, same_sender


async def gather(cores: list[Core], labels: dict[str, Label], rpc: Rpc, http: Http) -> Context:
    """Every lookup `facts.finish` will read for these transactions (one window)."""
    first_block = min(int(c.tx["blockNumber"], 16) for c in cores)
    window_start = min(c.block_timestamp for c in cores)
    collections = {a for c in cores for a in c.nft_collections}
    assets = {m.asset for c in cores for m in c.movements + c.log_movements} - {ETH} - collections
    prices, eth_usd = await fetch_prices(http, assets, window_start)
    nfts, floors = await fetch_nfts(http, collections, eth_usd)
    prices |= floors
    ctx = Context(labels=labels, eth_usd=eth_usd, prices=prices, nfts=nfts)
    for address in collections:
        ctx.decimals[address] = 0  # a token is a unit
    blocks = [int(c.tx["blockNumber"], 16) for c in cores]

    async def code(address: str, block: int) -> None:
        ctx.kinds[(address, block)] = kind_of(await rpc.call("eth_getCode", [address, hex(block)]))

    async def prior_day_calls(address: str) -> None:
        rows = await http.etherscan({"module": "account", "action": "txlist", "address": address,
                                     "startblock": str(first_block - PRIOR_DAY_BLOCKS), "endblock": str(first_block - 1),
                                     "page": "1", "offset": str(PRIOR_DAY_ROWS), "sort": "desc"}) or []
        for core, block in zip(cores, blocks):
            if core.root.target == address:
                ctx.prior_day_calls[(address, block)] = len(rows)
                ctx.prior_day_senders[(address, block)] = len({row["from"] for row in rows})

    # Who else uses each unlabeled entry contract comes first: it decides what counts as the sender's own side,
    # and so which losses and re-entries the cast asks about.
    unlabeled = {(c.root.target, b) for c, b in zip(cores, blocks)
                 if not c.trivial and c.root.target and c.root.target not in labels}
    await asyncio.gather(*(code(a, b) for a, b in unlabeled))
    entries = {(a, b) for a, b in unlabeled if ctx.kinds[(a, b)] == "contract"}
    await asyncio.gather(*(prior_day_calls(a) for a in sorted({a for a, _ in entries})))
    casts = [cast(c, prices, eth_usd, labels, ctx.prior_day_senders.get((c.root.target, b), 0) >= PUBLIC_SENDERS)
             for c, b in zip(cores, blocks)]
    await asyncio.gather(*(code(a, b) for a, b in {(a, b) for k, b in zip(casts, blocks) for a in k.parties}
                           - set(ctx.kinds)))

    contracts = set()
    for core, needed, block in zip(cores, casts, blocks):
        born_here = {contract for _, contract in core.created}
        for address in needed.parties:
            if ctx.kinds[(address, block)] == "contract" and address not in born_here \
                    and (not core.trivial or address in labels):
                contracts.add(address)
        contracts |= {a for a in needed.assets if a not in born_here and (not core.trivial or a in labels)}
    ctx.creations = await fetch_creations(http, contracts)

    # The upgrade watch, in chain order: a contract whose logic or control changed earlier in the window is nobody's
    # bot, so a later transaction that enters through it gets its losses read like any victim's. finish() rebuilds the
    # same watch with the same rule as it walks the window.
    watch: dict[str, dict] = {}
    for i, (core, needed, block) in enumerate(zip(cores, casts, blocks)):
        index = int(core.tx["transactionIndex"], 16)
        if watched_before(watch, core.root.target, block, index):
            casts[i] = cast(core, prices, eth_usd, labels, True)
            await asyncio.gather(*(code(a, block) for a in casts[i].parties if (a, block) not in ctx.kinds))
        born = {contract for _, contract in core.created}

        def age_of(address: str, core: Core = core, block: int = block, born: set[str] = born) -> int | None:
            if address in born:
                return 0
            creation = ctx.creations.get(address)
            if creation is None or creation["block"] > block:
                return None
            return max(0, core.block_timestamp - creation["timestamp"])

        side = whole_side(core, needed.parties, ctx.creations, block) if not core.trivial else created_side(core)
        for address, what, age in logic_changes_of(core, side, age_of):
            if ctx.prior_day_senders.get((address, block), 0) < PUBLIC_SENDERS:
                watch.setdefault(address, {"block": block, "index": index, "what": what, "age_seconds": age})

    async def decimals(asset: str, block: int) -> None:
        try:
            answer = await rpc.call("eth_call", [{"to": asset, "data": DECIMALS}, hex(block)])
        except RpcError:
            answer = "0x"
        ctx.decimals[asset] = int(answer, 16) if len(answer) == 66 and int(answer, 16) <= 77 else None

    earlier, ctx.same_sender_deposits = moved_earlier_in_block(cores, [[] if c.trivial else k.drains for c, k in zip(cores, casts)])

    async def balance(holder: str, asset: str, block: int, index: int) -> None:
        before = hex(block - 1)
        try:
            if asset == ETH:
                answer = await rpc.call("eth_getBalance", [holder, before])
            else:
                answer = await rpc.call("eth_call", [{"to": asset, "data": BALANCE_OF + holder[2:].rjust(64, "0")}, before])
        except RpcError:
            answer = "0x"
        at_block_start = int(answer, 16) if len(answer) > 2 else None
        ctx.balances_before[(holder, asset, block, index)] = (
            None if at_block_start is None else at_block_start + earlier[(holder, asset, block, index)])

    async def nonce(address: str, block: int) -> None:
        ctx.nonces_before[(address, block)] = int(await rpc.call("eth_getTransactionCount", [address, hex(block - 1)]), 16)

    reads = []
    unpriced: dict[str, int] = {}
    for core, needed, block in zip(cores, casts, blocks):
        for asset in needed.assets:
            if asset not in prices:
                unpriced.setdefault(asset, block)
        if not core.trivial:
            index = int(core.tx["transactionIndex"], 16)
            reads += [balance(holder, asset, block, index) for holder, asset in needed.drains]
            reads += [nonce(a, block) for a in needed.new_wallet_checks if ctx.kinds[(a, block)] == "wallet"]
    await asyncio.gather(*reads, *(decimals(asset, block) for asset, block in unpriced.items()))

    async def funding(core: Core) -> None:
        ctx.funding[core.tx["from"].lower()] = await fetch_funding(http, core)

    async def funding_of(address: str, core: Core) -> None:
        """First funding of a wallet other than the sender, read as of this transaction."""
        ctx.funding[address] = await fetch_funding(http, core, address)

    first_by_sender: dict[str, Core] = {}
    for core in cores:
        if not core.trivial:
            first_by_sender.setdefault(core.tx["from"].lower(), core)
    new_wallets = [core for core in first_by_sender.values() if int(core.tx["nonce"], 16) < NEW_WALLET_NONCES]
    proceeds_reads = {}
    for core, needed, block in zip(cores, casts, blocks):
        for address in needed.proceeds_checks:
            if ctx.kinds.get((address, block)) in ("wallet", "delegated wallet"):
                proceeds_reads.setdefault(address, core)
                sender = core.tx["from"].lower()
                if int(core.tx["nonce"], 16) >= NEW_WALLET_NONCES:
                    proceeds_reads.setdefault(sender, core)  # to compare funding sources, the sender's is needed too
    payouts, synced_to = mixer_payouts()
    if max(blocks) > synced_to:
        raise RuntimeError(f"the mixer payout list ends at block {synced_to}, before this window: "
                           "run `jevscan-monitor prepare`")
    ctx.mixer_payouts = latest_mixer_payouts(cores, set(first_by_sender), payouts)

    async def verified(address: str) -> None:
        rows = await http.etherscan({"module": "contract", "action": "getsourcecode", "address": address})
        ctx.verified[address] = bool(rows and rows[0].get("SourceCode"))

    young = set()
    for address, block in entries:
        creation = ctx.creations.get(address)
        timestamp = next(c.block_timestamp for c, b in zip(cores, blocks) if b == block)
        if creation and creation["block"] <= block and timestamp - creation["timestamp"] <= ESTABLISHED_SECONDS:
            young.add(address)
    selectors = {s for k in casts for s in k.tree_selectors} - set(FUNCTION_NAME)
    names, *_ = await asyncio.gather(
        fetch_function_names(http, selectors), *(funding(core) for core in new_wallets),
        *(funding_of(a, core) for a, core in proceeds_reads.items() if a not in {c.tx["from"].lower() for c in new_wallets}),
        *(verified(a) for a in sorted(young)))
    ctx.function_names = names
    return ctx
