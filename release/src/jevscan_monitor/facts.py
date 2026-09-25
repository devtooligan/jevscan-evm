"""Raw chain data to versioned observations and explicitly heuristic features.

Three steps with no I/O; finish updates window context and must run in chain order:
    extract(block, tx, receipt, trace) -> Core     the transaction alone: movements, call structure, events
    cast(core, prices, labels)         -> Cast     which addresses, assets, and balance reads the record will mention
    finish(core, ctx)                  -> TxFacts  Core plus the lookups in a Context (monitor/enrich.py fills it)

TxFacts is versioned, language-neutral JSON (FACTS_VERSION). Raw amounts are decimal strings, because a uint256 does
not fit a JSON number. Views render it; they never see Core.
"""

import json
from collections import Counter
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import NotRequired, TypedDict

FACTS_VERSION = 13  # release hardening changes aliases and excludes external NFT names
HERE = Path(__file__).resolve().parent
SIGNATURES = json.loads((HERE / "signatures.json").read_text())
TOPIC: dict[str, str] = SIGNATURES["events"]
SELECTOR: dict[str, str] = SIGNATURES["functions"]
EVENT_NAME = {topic: sig.split("(")[0] for sig, topic in TOPIC.items()}
FUNCTION_NAME = {selector: sig.split("(")[0] for sig, selector in SELECTOR.items()}

ETH = "ETH"
ZERO = "0x" + "0" * 40
WETH = "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2"
VALUE_KINDS = {"CALL", "CREATE", "CREATE2", "SELFDESTRUCT"}  # DELEGATECALL repeats its parent's value; nothing moves
CREATE_KINDS = {"CREATE", "CREATE2"}
INHERITS_CONTEXT = {"DELEGATECALL", "CALLCODE"}
PRECOMPILE_LIMIT = 0x400

TRANSFER = TOPIC["Transfer(address,address,uint256)"]
WETH_DEPOSIT = TOPIC["Deposit(address,uint256)"]
WETH_WITHDRAWAL = TOPIC["Withdrawal(address,uint256)"]
NFT_BATCH_TOPICS = {TOPIC["TransferSingle(address,address,address,uint256,uint256)"],
                    TOPIC["TransferBatch(address,address,address,uint256[],uint256[])"]}
INTERNAL_BALANCE_CHANGED = TOPIC["InternalBalanceChanged(address,address,int256)"]
SWAP_TOPICS = {topic for sig, topic in TOPIC.items() if sig.startswith(("Swap(", "TokenExchange"))}
NOISE_TOPICS = {TRANSFER, TOPIC["Approval(address,address,uint256)"], TOPIC["ApprovalForAll(address,address,bool)"],
                TOPIC["Sync(uint112,uint112)"], WETH_DEPOSIT, WETH_WITHDRAWAL} | NFT_BATCH_TOPICS
UNISWAP_V3_FLASH = TOPIC["Flash(address,address,uint256,uint256,uint256,uint256)"]
# topic -> (where the asset is, where the amount is). ("topic", i) is topics[i]; ("data", i) is the i-th data word.
FLASH_LOAN_EVENTS = {
    TOPIC["FlashLoan(address,address,address,uint256,uint256,uint16)"]: (("topic", 3), ("data", 0)),  # Aave V2
    TOPIC["FlashLoan(address,address,address,uint256,uint8,uint256,uint16)"]: (("topic", 2), ("data", 1)),  # Aave V3
    TOPIC["FlashLoan(address,address,uint256,uint256)"]: (("topic", 2), ("data", 0)),  # Balancer V2, Maker (below)
    TOPIC["FlashLoan(address,address,uint256)"]: (("topic", 2), ("data", 0)),  # Morpho
}
# topic -> where the address that gains the power is, or None when the event names nobody
PRIVILEGED_EVENTS = {
    TOPIC["OwnershipTransferred(address,address)"]: ("topic", 2),
    TOPIC["OwnershipTransferStarted(address,address)"]: ("topic", 2),
    TOPIC["Upgraded(address)"]: ("topic", 1),
    TOPIC["BeaconUpgraded(address)"]: ("topic", 1),
    TOPIC["AdminChanged(address,address)"]: ("data", 1),
    TOPIC["RoleGranted(bytes32,address,address)"]: ("topic", 2),
    TOPIC["RoleRevoked(bytes32,address,address)"]: ("topic", 2),
    TOPIC["NewAdmin(address,address)"]: ("data", 1),
    TOPIC["NewPendingAdmin(address,address)"]: ("data", 1),
    TOPIC["NewImplementation(address,address)"]: ("data", 1),
    TOPIC["ChangedMasterCopy(address)"]: ("data", 0),
    TOPIC["EnabledModule(address)"]: ("data", 0),
    TOPIC["DisabledModule(address)"]: ("data", 0),
    TOPIC["ChangedGuard(address)"]: ("data", 0),
    TOPIC["Initialized(uint8)"]: None,
    TOPIC["Initialized(uint64)"]: None,
    TOPIC["Paused(address)"]: None,
    TOPIC["Unpaused(address)"]: None,
    TOPIC["AddedOwner(address)"]: None,
    TOPIC["RemovedOwner(address)"]: None,
    TOPIC["ChangedThreshold(uint256)"]: None,
}
TOKEN_SELECTORS = {SELECTOR[s] for s in (
    "transfer(address,uint256)", "transferFrom(address,address,uint256)", "approve(address,uint256)",
    "balanceOf(address)", "allowance(address,address)", "decimals()", "symbol()", "name()", "totalSupply()",
    "permit(address,address,uint256,uint256,uint8,bytes32,bytes32)", "deposit()", "withdraw(uint256)")}
# An entry point whose whole design is to call the caller back and be called again: flash accounting (Uniswap V4's and
# Balancer V3's unlock). Re-entering through it is how it is used, like repaying a flash loan inside its callback.
REENTRANT_BY_DESIGN = {SELECTOR["unlock(bytes)"]}
PRICE_READS = {selector for sig, selector in SELECTOR.items() if selector not in TOKEN_SELECTORS | REENTRANT_BY_DESIGN
               and not sig.startswith("uniswapV")}

ESTABLISHED_SECONDS = 30 * 86400  # the plan's 30-day rule, for labels and for calling a contract established
SLOT_SECONDS = 12  # turns a distance in blocks into a time
LEDGER_PARTIES = 8
DRAIN_CANDIDATES = 3
DRAIN_MIN_USD = 1_000.0
NEW_WALLET_CHECKS = 3
REPEAT_MIN = 3
REPEATS_SHOWN = 5
REENTRY_CAP = 50
PUBLIC_SENDERS = 3  # distinct wallets calling an entry contract in the prior day that make it public infrastructure
HIGH_VOLUME_TXS = 100_000  # prior transactions from which the views call a wallet very high-volume
TRANSFER_FROM = SELECTOR["transferFrom(address,address,uint256)"]
APPROVAL = TOPIC["Approval(address,address,uint256)"]
PULL_RECIPIENTS_SHOWN = 3
PULL_MIN_USD = 1_000.0  # a pull below this is protocol plumbing, not a sweep or a drain
PROCEEDS_MIN_USD = 1_000.0  # a gain below this is not "proceeds" worth attributing to anyone
PROCEEDS_SHARE = 0.5  # a party taking at least this share of the largest loss, while the sender's side keeps little
SIDE_KEEPS_SHARE = 0.1
IMPLIED_MIN_USD = 1_000.0  # an exchange this small says nothing about an unpriced asset's value
IMPLIED_PASSES = 3
IMPLIED_REACH = 10  # an implied price holds for amounts up to this many times the quantity that was exchanged
FRESH_CODE_SECONDS = 86400  # a delegatecall into code created within a day of the call
LOGIC_EVENTS = {"Upgraded", "BeaconUpgraded", "AdminChanged", "NewImplementation", "NewAdmin", "OwnershipTransferred",
                "ChangedMasterCopy", "EnabledModule", "DisabledModule", "ChangedGuard", "RoleGranted"}
WALLET_KINDS = ("wallet", "delegated wallet")
MULTISIG_EVENTS = {"ExecutionSuccess", "ExecutionFailure"}  # a Safe executing a signed transaction: its owners' wallet, nobody's bot
NEW_WALLET_NONCES = 5  # a wallet with fewer prior transactions than this is new
EVENTS_SHOWN = 12
PROTOCOLS_SHOWN = 8
TREE_TOKEN_CAP = 4_800  # the narrative view's cap is 6,000 tokens, and the fact sheet beside the tree needs up to 1,200
TREE_MAX_DEPTH = 12


# ---- Core: the transaction alone ------------------------------------------------------------------------------------

@dataclass
class Movement:
    asset: str  # token address, or ETH
    sender: str
    recipient: str
    amount: int


@dataclass
class Frame:
    kind: str
    caller: str
    target: str | None  # None only for a failed CREATE, which has no address
    context: str  # whose storage and balance the code runs against: the parent's for DELEGATECALL
    selector: str | None
    value: int
    depth: int
    failed: bool  # this frame or an ancestor reverted, so nothing in it happened
    static: bool
    start: int = 0  # movements[start:end] happened inside this frame
    end: int = 0
    children: list["Frame"] = field(default_factory=list)


@dataclass
class Core:
    tx: dict
    block_tx_count: int
    block_timestamp: int
    builder: str
    succeeded: bool
    root: Frame
    movements: list[Movement]  # ETH and token transfers that took effect, in execution order
    log_movements: list[Movement]  # what the receipt alone shows: token transfers plus the envelope's value
    nft_transfers: int
    events: list[tuple[str, str]]  # (emitter, event name) for known events other than transfers and approvals
    other_events: int
    swap_emitters: set[str]
    flash_loans: list[dict]  # {lender, asset, amount, source}
    reentries: list[dict]  # {contract, between, static, caller}
    privileged: list[dict]  # {emitter, event, subject}
    approvals: set[tuple[str, str, str, int]]  # observed Approval event values; not final or ordered authorization
    positions: list[tuple[str, str, str, int | None, int | None]]  # (issuer, from, to, id, raw amount) per ERC-1155 transfer
    internal_balances: list[tuple[str, str, str, int]]  # (vault, user, token, signed delta) from accounting events
    delegations: list[tuple[str, str, str | None]]  # (context, code target, selector) for every DELEGATECALL that ran
    nft_collections: set[str]  # ERC-721 contracts whose tokens moved
    created: list[tuple[str, str]]  # (creator, new contract)
    destroyed: list[str]
    calls: int
    max_depth: int
    reverted_inner_calls: int
    repeated: list[tuple[str, str | None, int]]  # (target, selector, count)
    gas_used: int
    log_count: int
    fee_wei: int
    builder_payment_wei: int
    trivial: bool


def word(data: str, i: int) -> int:
    return int(data[2 + 64 * i: 66 + 64 * i] or "0", 16)


def signed_word(data: str, i: int) -> int:
    value = word(data, i)
    return value - 2**256 if value >= 2**255 else value


def topic_address(topic: str) -> str:
    return "0x" + topic[-40:]


def located(log: dict, where: tuple[str, int]) -> int:
    kind, i = where
    return int(log["topics"][i], 16) if kind == "topic" else word(log["data"], i)


def located_if_present(log: dict, where: tuple[str, int]) -> int | None:
    """Read an ABI-mapped field only when this log actually contains it.

    Contracts can emit a familiar topic from assembly while using a different field layout.  It is still useful to
    retain the event name, but an absent indexed field must not make fact extraction fail or be guessed from data.
    """
    kind, i = where
    if kind == "topic":
        return int(log["topics"][i], 16) if len(log["topics"]) > i else None
    return word(log["data"], i) if len(log["data"]) >= 2 + 64 * (i + 1) else None


def as_address(value: int) -> str:
    return "0x" + format(value, "040x")


def is_precompile(address: str) -> bool:
    return int(address, 16) < PRECOMPILE_LIMIT


def log_movement(log: dict) -> Movement | None:
    """The fungible transfer a log records, if any. An ERC-721 Transfer has four topics and its last one is a token
    id, not an amount. WETH emits Deposit and Withdrawal, never Transfer, when it wraps and unwraps: model them as
    transfers from and to the WETH contract, so the wrapper nets to zero and every holder's balance comes out right."""
    topics, address = log["topics"], log["address"].lower()
    if not topics:
        return None
    if topics[0] == TRANSFER and len(topics) == 3 and len(log["data"]) == 66:
        return Movement(address, topic_address(topics[1]), topic_address(topics[2]), word(log["data"], 0))
    if topics[0] == TRANSFER and len(topics) == 4:  # ERC-721: one token, counted as one unit of the collection
        return Movement(address, topic_address(topics[1]), topic_address(topics[2]), 1)
    if address == WETH and len(topics) == 2 and len(log["data"]) == 66:
        if topics[0] == WETH_DEPOSIT:
            return Movement(WETH, WETH, topic_address(topics[1]), word(log["data"], 0))
        if topics[0] == WETH_WITHDRAWAL:
            return Movement(WETH, topic_address(topics[1]), WETH, word(log["data"], 0))
    return None


def extract(block: dict, tx: dict, receipt: dict, trace: dict) -> Core:
    """Everything the transaction's own data says. `trace` is the callTracer frame (withLog) for this transaction.
    Receipt logs are canonical; the trace supplies call structure, ETH movement, and ordering, and its surviving logs
    must equal the receipt's, or the trace handling is wrong."""
    for name in ("from", "hash", "input", "value", "nonce", "transactionIndex"):
        if name not in tx:
            raise ValueError(f"transaction is missing required field {name!r}")
    succeeded = receipt["status"] == "0x1"
    builder = block["miner"].lower()
    movements: list[Movement] = []
    surviving_logs: list[dict] = []
    stats = {"calls": 0, "max_depth": 0, "reverted": 0}
    created: list[tuple[str, str]] = []
    destroyed: list[str] = []
    call_counts: Counter = Counter()
    delegations: list[tuple[str, str, str | None]] = []

    def walk(node: dict, depth: int, parent: Frame | None) -> Frame:
        kind = node["type"]
        target = node["to"].lower() if node.get("to") else None
        caller = node["from"].lower()
        context = parent.context if parent and kind in INHERITS_CONTEXT else (target or caller)
        failed = bool(parent and parent.failed) or "error" in node
        if "error" in node and parent and not parent.failed:
            stats["reverted"] += 1
        data = node.get("input", "0x")
        frame = Frame(kind, caller, target, context, data[:10] if len(data) >= 10 else None,
                      int(node.get("value", "0x0"), 16), depth, failed,
                      bool(parent and parent.static) or kind == "STATICCALL", start=len(movements))
        stats["calls"] += 1
        stats["max_depth"] = max(stats["max_depth"], depth)
        if not failed and target:
            if kind in INHERITS_CONTEXT and parent is not None:
                delegations.append((context, target, frame.selector))
            if frame.value and kind in VALUE_KINDS:
                movements.append(Movement(ETH, caller, target, frame.value))
            if kind in CREATE_KINDS:
                created.append((caller, target))
            elif kind == "SELFDESTRUCT":
                destroyed.append(caller)
            elif kind == "CALL" and not is_precompile(target):
                call_counts[(target, frame.selector)] += 1
        logs = sorted(node.get("logs", ()), key=lambda entry: int(entry["position"], 16))
        emitted = 0
        for i, child in enumerate([*node.get("calls", ()), None]):
            # A log's position is the number of subcalls made before it.
            while emitted < len(logs) and (child is None or int(logs[emitted]["position"], 16) <= i):
                if not failed:
                    surviving_logs.append(logs[emitted])
                    moved = log_movement(logs[emitted])
                    if moved:
                        movements.append(moved)
                emitted += 1
            if child is not None:
                frame.children.append(walk(child, depth + 1, frame))
        frame.end = len(movements)
        return frame

    root = walk(trace, 0, None)
    if root.failed == succeeded:
        raise ValueError(f"{tx['hash']}: receipt status and trace disagree about success")
    seen = [(entry["address"].lower(), entry["topics"], entry["data"]) for entry in surviving_logs]
    canonical = [(entry["address"].lower(), entry["topics"], entry["data"]) for entry in receipt["logs"]]
    if seen != canonical:
        raise ValueError(f"{tx['hash']}: the trace's surviving logs differ from the receipt's "
                         f"({len(seen)} against {len(canonical)})")

    log_movements = [m for m in map(log_movement, receipt["logs"]) if m]
    value = int(tx["value"], 16)
    if succeeded and value and root.target:
        log_movements.insert(0, Movement(ETH, root.caller, root.target, value))
    nft_transfers, events, other_events, swap_emitters, privileged, approvals = 0, [], 0, set(), [], set()
    positions: list[tuple[str, str, str, int | None, int | None]] = []
    internal_balances: list[tuple[str, str, str, int]] = []
    nft_collections: set[str] = set()
    for entry in receipt["logs"]:
        topics, emitter = entry["topics"], entry["address"].lower()
        topic0 = topics[0] if topics else None
        if topic0 == TRANSFER and len(topics) == 4:
            nft_collections.add(emitter)
        if (topic0 in NFT_BATCH_TOPICS and len(topics) == 4
                and (topic0 != TOPIC["TransferSingle(address,address,address,uint256,uint256)"] or len(entry["data"]) >= 130)):
            token_id, amount = (word(entry["data"], 0), word(entry["data"], 1)) if topic0 == TOPIC["TransferSingle(address,address,address,uint256,uint256)"] else (None, None)
            positions.append((emitter, topic_address(topics[2]), topic_address(topics[3]), token_id, amount))
        if topic0 == APPROVAL and len(topics) == 3 and len(entry["data"]) == 66:  # a fourth topic is an NFT approval
            approvals.add((emitter, topic_address(topics[1]), topic_address(topics[2]), word(entry["data"], 0)))
        if topic0 == INTERNAL_BALANCE_CHANGED and len(topics) == 3 and len(entry["data"]) == 66:
            internal_balances.append((emitter, topic_address(topics[1]), topic_address(topics[2]), signed_word(entry["data"], 0)))
        if (topic0 == TRANSFER and len(topics) == 4) or topic0 in NFT_BATCH_TOPICS:
            nft_transfers += 1
        if topic0 in SWAP_TOPICS:
            swap_emitters.add(emitter)
        if topic0 in PRIVILEGED_EVENTS:
            where = PRIVILEGED_EVENTS[topic0]
            value = located_if_present(entry, where) if where else None
            subject = as_address(value & (2**160 - 1)) if value is not None else None
            privileged.append({"emitter": emitter, "event": EVENT_NAME[topic0], "subject": subject})
        if topic0 in EVENT_NAME and topic0 not in NOISE_TOPICS:
            events.append((emitter, EVENT_NAME[topic0]))
        elif topic0 not in NOISE_TOPICS:
            other_events += 1

    gas_used = int(receipt["gasUsed"], 16)
    gas_price = int(receipt["effectiveGasPrice"], 16)
    base_fee = int(block.get("baseFeePerGas", "0x0"), 16)
    direct_tip = sum(m.amount for m in movements if m.asset == ETH and m.recipient == builder)
    token_transfer_logs = sum(1 for entry in receipt["logs"] if entry["topics"] and entry["topics"][0] == TRANSFER)
    one_context = all(f.context == root.context for f in frames_of(root))
    # A proxy runs one implementation. A wallet contract that delegates into a second target is running code the
    # transaction chose, which is never trivial, whatever else happened.
    code_targets = {target for context, target, _ in delegations if context == root.context}
    repeated = [(target, selector, n) for (target, selector), n in call_counts.most_common() if n >= REPEAT_MIN]
    return Core(
        tx=tx, block_tx_count=len(block["transactions"]), block_timestamp=int(block["timestamp"], 16),
        builder=builder, succeeded=succeeded, root=root, movements=movements, log_movements=log_movements,
        nft_transfers=nft_transfers, events=events, other_events=other_events, swap_emitters=swap_emitters,
        flash_loans=find_flash_loans(root, movements, receipt["logs"]), reentries=find_reentries(root),
        privileged=privileged, approvals=approvals, positions=positions, internal_balances=internal_balances, delegations=delegations,
        nft_collections=nft_collections, created=created, destroyed=destroyed, calls=stats["calls"],
        max_depth=stats["max_depth"], reverted_inner_calls=stats["reverted"], repeated=repeated[:REPEATS_SHOWN],
        gas_used=gas_used, log_count=len(receipt["logs"]), fee_wei=gas_used * gas_price, builder_payment_wei=gas_used * max(0, gas_price - base_fee) + direct_tip,
        trivial=one_context and not created and token_transfer_logs <= 1 and len(code_targets) <= 1,
    )


def frames_of(frame: Frame):
    yield frame
    for child in frame.children:
        yield from frames_of(child)


def frame_holding(root: Frame, index: int, context: str) -> Frame | None:
    """The shallowest call into `context` in which movement `index` happened: the call that made a token move."""
    found = None
    for f in frames_of(root):
        if (f.context == context and f.kind not in INHERITS_CONTEXT and f.start <= index < f.end
                and (found is None or f.depth < found.depth)):
            found = f
    return found


def pulls_of(core: Core, side: list[str]) -> list[dict]:
    """Token transfers made with transferFrom on someone else's balance. The spender is the address that called the
    token. A transfer of the caller's own tokens, or of the sender's side's, is not a pull."""
    pulls = []
    for f in frames_of(core.root):
        if f.failed or f.selector != TRANSFER_FROM or f.kind in INHERITS_CONTEXT or not f.target:
            continue
        for m in core.movements[f.start:f.end]:
            if m.asset == f.context and m.sender not in side and m.sender != f.caller:
                pulls.append({"spender": f.caller, "owner": m.sender, "recipient": m.recipient, "asset": m.asset,
                              "amount": m.amount, "approved_now": any((m.asset, m.sender, f.caller) == approval[:3]
                                                                      for approval in core.approvals)})
    return pulls


def find_flash_loans(root: Frame, movements: list[Movement], logs: list[dict]) -> list[dict]:
    """Flash loans from lenders' own events, and from the shape every flash loan has whatever the lender: inside one
    frame, funds go to a contract, the frame calls that contract back, and at least as much of the same asset returns
    from it to where the funds came from before the frame ends. An arbitrage cycle does not match: its funds come back
    from the last pool, not from the contract that was called."""
    found: dict[tuple[str, int], dict] = {}
    for entry in logs:
        topic0 = entry["topics"][0] if entry["topics"] else None
        lender = entry["address"].lower()
        if topic0 == UNISWAP_V3_FLASH:
            if len(entry["data"]) < 2 + 64 * 2:
                continue
            amounts, named = {word(entry["data"], 0), word(entry["data"], 1)} - {0}, None  # the event names no token
        elif topic0 in FLASH_LOAN_EVENTS:
            asset_at, amount_at = FLASH_LOAN_EVENTS[topic0]
            if len(entry["topics"]) == 2:  # Maker's DssFlash shares Balancer's signature but indexes only the receiver
                asset_at, amount_at = ("data", 0), ("data", 1)
            amount, asset = located_if_present(entry, amount_at), located_if_present(entry, asset_at)
            if amount is None or asset is None:
                continue
            amounts, named = {amount}, as_address(asset & (2**160 - 1))
        else:
            continue
        # Lenders reuse each other's event signatures with other fields (Curve's crvUSD lender puts the receiver where
        # Morpho puts the token), so an event counts only with a matching transfer, and that transfer names the asset.
        for amount in amounts:
            moved = [m.asset for m in movements if m.amount == amount and m.asset != ETH
                     and (m.asset == named or m.sender == lender)]
            if moved:
                asset = named if named in moved else moved[0]
                found.setdefault((asset, amount), {"lender": lender, "asset": asset, "amount": amount, "source": "event"})
    for frame in frames_of(root):
        if frame.failed:
            continue
        for callback in frame.children:
            if callback.kind != "CALL" or callback.failed or not callback.children or not callback.target:
                continue
            borrower = callback.target
            for lent in movements[frame.start:callback.start]:
                if lent.recipient != borrower or lent.asset == ETH or not lent.amount:
                    continue
                repaid = any(m.asset == lent.asset and m.sender == borrower and m.recipient == lent.sender
                             and m.amount >= lent.amount for m in movements[callback.start:frame.end])
                if repaid:
                    found.setdefault((lent.asset, lent.amount), {"lender": frame.context, "asset": lent.asset,
                                                                 "amount": lent.amount, "source": "shape"})
    return list(found.values())


def find_reentries(root: Frame) -> list[dict]:
    """Every time a contract is entered while an earlier call into it is still running, with the contracts in between.
    Whether one of those is the sender's, and whether the outer call is a flash loan, is decided in `finish`."""
    found: dict[tuple, dict] = {}

    def visit(frame: Frame, stack: list[tuple[str, str | None]]) -> None:
        if frame.failed or len(found) >= REENTRY_CAP:
            return
        contexts = [context for context, _ in stack]
        if frame.context in contexts:
            outer = contexts.index(frame.context)
            between = sorted(set(contexts[outer + 1:]) - {frame.context})
            if between and stack[outer][1] not in REENTRANT_BY_DESIGN:
                found.setdefault((frame.context, tuple(between), frame.static, frame.caller),
                                 {"contract": frame.context, "between": between, "static": frame.static,
                                  "caller": frame.caller})
        stack.append((frame.context, frame.selector))
        for child in frame.children:
            visit(child, stack)
        stack.pop()

    visit(root, [])
    return list(found.values())


# ---- Context: what the lookups returned -----------------------------------------------------------------------------

class Label(TypedDict):
    name: str
    category: str  # exchange, lending, bridge, mixer, token, centralized exchange
    symbol: str | None  # tokens only


class Price(TypedDict):
    usd: float
    symbol: str
    decimals: int


class Creation(TypedDict):
    creator: str
    block: int
    timestamp: int


class Funding(TypedDict):
    timestamp: int  # of the first inbound transfer
    funder: str


@dataclass
class Context:
    """Lookup results for a window. An absent key was not looked up (a trivial transaction skips the Etherscan reads),
    and the record then says nothing about it; a None value means the lookup found nothing. Reads that depend on
    the block are keyed with the transaction's block."""
    labels: dict[str, Label]
    eth_usd: float
    prices: dict[str, Price] = field(default_factory=dict)  # only confident prices from before the window
    kinds: dict[tuple[str, int], str] = field(default_factory=dict)  # wallet, contract, delegated wallet
    creations: dict[str, Creation | None] = field(default_factory=dict)
    verified: dict[str, bool] = field(default_factory=dict)
    decimals: dict[str, int | None] = field(default_factory=dict)
    # (holder, asset, block, transaction index) -> the balance just before that transaction
    balances_before: dict[tuple[str, str, int, int], int | None] = field(default_factory=dict)
    nonces_before: dict[tuple[str, int], int] = field(default_factory=dict)
    funding: dict[str, Funding | None] = field(default_factory=dict)  # looked up only for wallets with few transactions
    # (sender, block, transaction index) -> (block, pool) of the sender's latest mixer payout inside the look-back
    mixer_payouts: dict[tuple[str, int, int], tuple[int, str] | None] = field(default_factory=dict)
    # (holder, asset, block, transaction index) -> (amount, index of the first such transaction): what earlier
    # transactions of the same block, sent by this transaction's sender, moved into the holder
    same_sender_deposits: dict[tuple[str, str, int, int], tuple[int, int]] = field(default_factory=dict)
    nfts: dict[str, dict] = field(default_factory=dict)  # collection -> {name, verified, floor_usd or None}
    # Filled by finish() as it walks the window in chain order: what each sender did earlier that looked like
    # preparation, and which contracts had their logic or control changed, so later transactions can say so.
    actor_notes: dict[str, list[dict]] = field(default_factory=dict)
    contract_watch: dict[str, dict] = field(default_factory=dict)
    prior_day_calls: dict[tuple[str, int], int] = field(default_factory=dict)
    prior_day_senders: dict[tuple[str, int], int] = field(default_factory=dict)  # distinct wallets behind those calls
    function_names: dict[str, str] = field(default_factory=dict)


@dataclass
class Cast:
    """What a finished record mentions, so enrichment fetches exactly what `finish` will read."""
    parties: list[str]  # addresses needing code kind, creation, and label checks, most important first
    assets: list[str]  # token addresses the record names
    drains: list[tuple[str, str]]  # (holder, asset) balance reads one block earlier
    new_wallet_checks: list[str]  # gainers whose prior transaction count is worth a read
    tree_selectors: list[str]  # selectors of calls into labeled contracts, the only calls whose functions are named
    proceeds_checks: list[str]  # wallets that took the bulk of a loss while the sender's side kept little: read their funding


def net_ledger(movements: list[Movement]) -> dict[str, dict[str, int]]:
    """party -> asset -> net change. A mint or burn (a transfer from or to the zero address) is booked against the
    token's own contract, so a vault that pays out assets is seen to take its shares back. A contract that only
    issues or redeems its own token is no party, and neither is the WETH wrapper, whose ETH always matches its WETH."""
    ledger: dict[str, dict[str, int]] = {}
    for m in movements:
        for party, sign in ((m.sender, -1), (m.recipient, 1)):
            party = m.asset if party == ZERO and m.asset != ETH else party
            changes = ledger.setdefault(party, {})
            changes[m.asset] = changes.get(m.asset, 0) + sign * m.amount
    return {party: {a: n for a, n in changes.items() if n} for party, changes in ledger.items()
            if party not in (ZERO, WETH) and any(n for a, n in changes.items() if a != party)}


def usd_value(asset: str, amount: int, prices: dict[str, Price], eth_usd: float) -> float | None:
    if asset == ETH:
        return amount / 1e18 * eth_usd
    price = prices.get(asset)
    if price is None or (price.get("max_amount") is not None and abs(amount) > price["max_amount"]):
        return None  # an implied price says nothing about a quantity far beyond the exchange that set it
    return amount / 10 ** price["decimals"] * price["usd"]


def flows(ledger: dict[str, dict[str, int]], prices: dict[str, Price], eth_usd: float) -> dict[str, tuple[float, float]]:
    """party -> (priced value given out, priced value received)."""
    out = {}
    for party, changes in ledger.items():
        values = [usd_value(asset, n, prices, eth_usd) for asset, n in changes.items()]
        out[party] = (-sum(v for v in values if v is not None and v < 0), sum(v for v in values if v and v > 0))
    return out


def created_side(core: Core) -> list[str]:
    """The sender and the contracts its side created in this transaction, in creation order."""
    side = [core.tx["from"].lower()]
    for creator, contract in core.created:
        if creator in side:
            side.append(contract)
    return side


def whole_side(core: Core, parties: list[str], creations: dict[str, Creation], block: int) -> list[str]:
    """The sender, the contracts its side created in this transaction, the contracts it deployed earlier (among the
    parties looked up), and, again, anything those created in this transaction: proceeds sent to a contract that an
    older sender contract deploys on the fly are still the sender's."""
    side = created_side(core)
    changed = True
    while changed:
        changed = False
        for address in parties:
            creation = creations.get(address)
            if address not in side and creation and creation.get("creator") in side and creation["block"] <= block:
                side.append(address)
                changed = True
        for creator, contract in core.created:
            if creator in side and contract not in side:
                side.append(contract)
                changed = True
    return side


def implied_prices(core: Core, side: list[str], prices: dict[str, Price], eth_usd: float,
                   decimals: dict[str, int | None]) -> dict[str, Price]:
    """A price for an asset nobody quotes, from what it was exchanged for in this transaction: a party outside the
    sender's side that took the asset in and gave out at least IMPLIED_MIN_USD of priced assets (or the reverse) sets
    its value. Passes repeat, because one implied price can price the next exchange."""
    ledger = net_ledger(core.movements)
    implied: dict[str, Price] = {}
    for _ in range(IMPLIED_PASSES):
        known = prices | implied
        added = False
        for asset in {a for p in ledger for a in ledger[p] if a != ETH and a not in known and a not in core.nft_collections}:
            best: tuple[float, int] | None = None
            for party, changes in ledger.items():
                n = changes.get(asset, 0)
                if not n or party in side or party == asset or party == core.builder:
                    continue
                opposite = sum(usd_value(b, abs(m), known, eth_usd) or 0.0 for b, m in changes.items()
                               if b != asset and (m < 0) == (n > 0))
                if opposite >= IMPLIED_MIN_USD and (best is None or opposite > best[0]):
                    best = (opposite, abs(n))
            if best:
                scale = decimals.get(asset)
                scale = 18 if scale is None else scale
                implied[asset] = {"usd": best[0] / (best[1] / 10**scale), "symbol": None, "decimals": scale, "implied": True,
                                  "max_amount": best[1] * IMPLIED_REACH}
                added = True
        if not added:
            break
    return implied


def shown_parties(ledger: dict[str, dict[str, int]], core: Core, prices: dict[str, Price], eth_usd: float) -> list[str]:
    """The ledger rows a record shows: the sender's side and the entry contract, then the largest flows."""
    side, flow = created_side(core), flows(ledger, prices, eth_usd)
    ranked = sorted(ledger, key=lambda p: (-max(flow[p]), p))
    first = [p for p in ranked if p in side or p == core.root.target]
    return (first + [p for p in ranked if p not in first])[:LEDGER_PARTIES]


def controlled_by_sender(core: Core, labels: dict[str, Label], entry_is_public: bool) -> set[str]:
    """The sender's side, plus the entry contract when it has no label and few wallets use it: the sender chose to
    run it, whoever deployed it (a bot's operator often deploys from another wallet). An unlabeled contract that
    many wallets call is someone's protocol or router: what it loses is a loss, and its own callbacks are not the
    sender re-entering anything. A multisig wallet executing a signed transaction is its owners' wallet, so what it
    loses is a loss too, whoever submitted the transaction."""
    controlled = set(created_side(core))
    multisig = any(emitter == core.root.target and name in MULTISIG_EVENTS for emitter, name in core.events)
    if core.root.target and core.root.target not in labels and not entry_is_public and not multisig:
        controlled.add(core.root.target)
    return controlled


def flash_loans_taken(core: Core, labels: dict[str, Label], entry_is_public: bool) -> list[dict]:
    """The detected flash loans, without shape matches whose lender is the sender's own contract. A contract that
    deposits into a protocol and withdraws at least as much in the same call has the loan's shape, with the roles
    reversed: nobody lent the sender anything. An attack that loops deposit and withdraw showed 52 of these."""
    controlled = controlled_by_sender(core, labels, entry_is_public)
    return [loan for loan in core.flash_loans if loan["source"] == "event" or loan["lender"] not in controlled]


def reentries_shown(core: Core, labels: dict[str, Label], entry_is_public: bool) -> list[tuple[str, str, bool]]:
    """(contract, the sender-controlled contract it was re-entered through, read-only) for the plan's indicator: a
    protocol contract twice on the call stack with a sender-controlled frame between, outside a flash loan callback.
    A read-only re-entry counts only when some other contract does the reading: a bot that reads a pool's price
    inside that pool's own callback is ordinary, a protocol that reads it there can be fooled."""
    controlled = controlled_by_sender(core, labels, entry_is_public)
    lenders = {loan["lender"] for loan in flash_loans_taken(core, labels, entry_is_public)}
    shown: dict[tuple[str, bool], tuple[str, str, bool]] = {}
    for r in core.reentries:
        through = [a for a in r["between"] if a in controlled]
        if through and r["contract"] not in controlled and r["contract"] not in lenders \
                and not (r["static"] and r["caller"] in controlled):
            shown.setdefault((r["contract"], r["static"]), (r["contract"], through[0], r["static"]))
    return list(shown.values())


def cast(core: Core, prices: dict[str, Price], eth_usd: float, labels: dict[str, Label],
         entry_is_public: bool) -> Cast:
    ledger, logs_only = net_ledger(core.movements), net_ledger(core.log_movements)
    shown = shown_parties(ledger, core, prices, eth_usd)
    logs_shown = shown_parties(logs_only, core, prices, eth_usd)
    side, flow = created_side(core), flows(ledger, prices, eth_usd)
    effective = [f for f in frames_of(core.root) if not f.failed and f.target and not is_precompile(f.target)]
    gainers = [p for p in sorted(ledger, key=lambda p: (flow[p][0] - flow[p][1], p))
               if p not in side and p != core.builder and flow[p][1] > flow[p][0]][:NEW_WALLET_CHECKS]
    controlled = controlled_by_sender(core, labels, entry_is_public)  # what the sender's own contracts spend is no one's loss
    losses = sorted(((usd_value(a, -n, prices, eth_usd) or 0.0, p, a) for p in ledger if p not in controlled
                     for a, n in ledger[p].items() if n < 0 and a != p), reverse=True)  # nor is issuing one's own token
    drains = [(p, a) for usd, p, a in losses[:DRAIN_CANDIDATES] if usd >= DRAIN_MIN_USD]
    largest_loss = losses[0][0] if losses else 0.0
    side_net = sum(flow[p][1] - flow[p][0] for p in side if p in flow)
    proceeds_checks = [p for p in gainers if largest_loss >= DRAIN_MIN_USD and side_net < SIDE_KEEPS_SHARE * largest_loss
                       and flow[p][1] - flow[p][0] >= PROCEEDS_SHARE * largest_loss][:1]
    entry_delegations = [target for context, target, _ in core.delegations if context == core.root.target]
    parties = [side[0]]  # the sender, even when it is the block's builder paying its proposer
    for address in ([core.root.target, *shown, *logs_shown, *gainers, *(p for p, _ in drains), *entry_delegations]
                    + [loan["lender"] for loan in flash_loans_taken(core, labels, entry_is_public)]
                    + [a for contract, through, _ in reentries_shown(core, labels, entry_is_public) for a in (contract, through)]
                    + [a for p in core.privileged for a in (p["emitter"], p["subject"])]
                    + [contract for _, contract in core.created] + [target for target, _, _ in core.repeated]
                    + sorted({f.context for f in effective if f.context in labels})):
        if address and address not in parties and address not in (ZERO, core.builder):
            parties.append(address)
    assets = sorted(({a for p in shown for a in ledger[p]} | {a for p in logs_shown for a in logs_only[p]}
                     | {loan["asset"] for loan in flash_loans_taken(core, labels, entry_is_public)} | {a for _, a in drains}
                     | {m.asset for m in core.movements if m.sender == ZERO and m.recipient in [*shown, *side]})
                    - {ETH})
    selectors = sorted({f.selector for f in effective if f.selector and f.target in labels})
    return Cast(parties, assets, drains, gainers, selectors, proceeds_checks)


# ---- TxFacts: the finished record -----------------------------------------------------------------------------------

class TxFacts(TypedDict):
    version: int
    tx: dict  # hash, block, index, raw addresses: for the harness and the raw view only
    status: str  # success, failed
    trivial: bool
    sender: dict
    entry: dict | None  # None when the transaction is sent to a wallet
    parties: dict[str, dict]  # alias -> what is known about the address
    assets: dict[str, dict]  # asset alias -> what is known about the token
    ledger: list[dict]
    ledger_logs_only: list[dict]  # what a receipt alone shows: no internal ETH movement
    minted: list[dict]
    lending_accounting_issuances: list[dict]  # a lending-pool Borrow event linked to a same-pool token issuance to its borrower
    v4_borrow_evidence: NotRequired[list[dict]]  # V11 only: amount-matched Spoke Borrow, Hub Draw, and token payout
    execution_provenance: NotRequired[dict]  # V14 only: bounded raw-call relationships for an isolated experiment
    sender_side: dict
    drains: list[dict]
    pulls: list[dict]  # tokens taken with transferFrom from addresses outside the sender's side, by spender
    allowance_changes: list[dict]  # standalone token approvals involving the sender's side
    internal_balance_changes: list[dict]  # protocol accounting credits/debits involving the sender's side
    positions_moved: list[dict]  # ERC-1155 position transfers, including raw identifier and quantity where encoded
    self_minted_collateral: list[dict]  # an asset the side minted itself, posted to a contract that then paid it
    precursor: bool  # deploys a contract and moves positions or unpriced assets while no priced value moves
    earlier_by_this_sender: list[dict]  # this sender's precursor-shaped transactions earlier in the window
    logic_changes: list[dict]  # contracts whose logic, control, or modules this transaction changed
    heightened: list[dict]  # contracts touched here whose logic or control changed earlier in the window
    flash_loans: list[dict]
    reentrancy: list[dict]
    privileged_events: list[dict]
    events: list[dict]
    protocols_touched: list[str]
    call_shape: dict
    call_tree: list[str]
    mev: dict


class Naming:
    """Aliases for one transaction. Filtered external names are still untrusted: an address shows its label,
    and a token its symbol, only when the label passed the filters in monitor/labels.py and the contract is older than
    30 days. Everything else is numbered."""

    def __init__(self, core: Core, ctx: Context, side: list[str]) -> None:
        self.core, self.ctx, self.side = core, ctx, side
        self.block = int(core.tx["blockNumber"], 16)
        self.born_here = {contract: creator for creator, contract in core.created}
        self.parties: dict[str, dict] = {}
        self.assets: dict[str, dict] = {}
        self.alias_of: dict[str, str] = {}
        self.asset_alias_of: dict[str, str] = {ETH: ETH}
        self.counts: Counter = Counter()

    def age(self, address: str) -> int | None:
        """Seconds since the contract was created, as of this transaction; None when unknown or not yet created."""
        if address in self.born_here:
            return 0
        creation = self.ctx.creations.get(address)
        if creation is None or creation["block"] > self.block:
            return None
        return max(0, self.core.block_timestamp - creation["timestamp"])

    def label(self, address: str) -> Label | None:
        """The label, if the 30-day rule lets it show. A labeled wallet, such as an exchange hot wallet, has no
        deployment to date, so its label stands."""
        label = self.ctx.labels.get(address)
        if label is None:
            return None
        if self.ctx.kinds.get((address, self.block)) in ("wallet", "delegated wallet"):
            return None if label["category"] == "token" else label
        age = self.age(address)
        return label if age is not None and age > ESTABLISHED_SECONDS else None

    def numbered(self, stem: str) -> str:
        self.counts[stem] += 1
        return f"{stem}_{self.counts[stem]}"

    def party(self, address: str, assume: str | None = None) -> str:
        """The alias for `address`, recording what is known about it. `assume` is the kind to use for an address whose
        code was not looked up (a minor party of the call tree)."""
        if address in self.alias_of:
            return self.alias_of[address]
        core, ctx = self.core, self.ctx
        kind = "contract" if address in self.born_here else ctx.kinds.get((address, self.block), assume)
        label = self.label(address)
        info: dict = {"address": address, "kind": kind, "label": None, "category": None,
                      "age_seconds": self.age(address), "created_in_tx": address in self.born_here,
                      "created_by": None, "exchange_pool": address in core.swap_emitters}
        if address == self.side[0]:
            alias = "sender"
        elif address == core.builder:
            alias, info["kind"] = "block_builder", "block builder"
        elif address in self.side:
            alias = self.numbered("sender_contract")
        elif label:
            alias, info["label"], info["category"] = label["name"], label["name"], label["category"]
            if alias in {"sender", "block_builder"}:
                alias = "labelled_" + alias
        else:
            alias = self.numbered({"wallet": "unknown_wallet", "delegated wallet": "unknown_wallet",
                                   "contract": "unknown_contract"}.get(kind, "unknown_address"))
        stem, suffix = alias, 2
        while alias in self.parties:
            alias = f"{stem}__{suffix}"
            suffix += 1
        self.alias_of[address] = alias
        creator = self.born_here.get(address) or (ctx.creations.get(address) or {}).get("creator")
        if creator and info["age_seconds"] is not None:
            info["created_by"] = ("sender" if creator == self.side[0] else
                                  "sender's contract" if creator in self.side else "someone else")
        if (address, self.block) in ctx.nonces_before:
            info["prior_transactions"] = ctx.nonces_before[(address, self.block)]
        if address in ctx.verified:
            info["source_verified"] = ctx.verified[address]
        elif address in self.born_here:
            info["source_verified"] = False  # nothing can be verified on an explorer before it exists
        self.parties[alias] = info
        return alias

    def asset(self, address: str) -> str:
        if address in self.asset_alias_of:
            return self.asset_alias_of[address]
        label, price, age = self.label(address), self.ctx.prices.get(address), self.age(address)
        symbol = label["symbol"] if label else None
        nft = self.ctx.nfts.get(address)
        # Marketplace verification does not make arbitrary collection text safe
        # as a model instruction. Keep only independently filtered label symbols.
        stem = "unrecognized_nft" if address in self.core.nft_collections else "unrecognized_token"
        alias = symbol if symbol and symbol not in self.asset_alias_of.values() else self.numbered(stem)
        creator = self.born_here.get(address) or (self.ctx.creations.get(address) or {}).get("creator")
        self.assets[alias] = {"address": address, "symbol": symbol, "priced": price is not None, "age_seconds": age,
                              "created_by_sender_side": bool(creator and creator in self.side),
                              "price_basis": ("implied from what it was exchanged for in this transaction" if price and price.get("implied")
                                              else "current floor price" if nft and price else None),
                              "nft": address in self.core.nft_collections}
        self.asset_alias_of[address] = alias
        return alias


def decimals_of(asset: str, ctx: Context) -> int | None:
    if asset == ETH:
        return 18
    if asset in ctx.prices:
        return ctx.prices[asset]["decimals"]
    return ctx.decimals.get(asset)


def amount_facts(asset: str, amount: int, names: Naming, ctx: Context) -> dict:
    usd, decimals = usd_value(asset, amount, ctx.prices, ctx.eth_usd), decimals_of(asset, ctx)
    return {"asset": names.asset(asset), "amount_raw": str(amount),
            "amount": None if decimals is None else amount / 10**decimals,
            "usd": None if usd is None else round(usd, 2)}


def logic_changes_of(core: Core, side: list[str], age_of) -> list[tuple[str, str, int]]:
    """(contract, what changed, the contract's age) for an established contract whose logic or control this
    transaction changed: a logic or control event, or a delegatecall into the sender's own contract or into code
    created within the last day. `age_of(address)` gives seconds since creation, 0 for a contract created here, None
    when unknown."""
    changes: list[tuple[str, str, int]] = []
    for change in core.privileged:  # a fresh deployment's own OwnershipTransferred is boilerplate, not a change
        age = age_of(change["emitter"])
        if change["event"] in LOGIC_EVENTS and age is not None and age > ESTABLISHED_SECONDS:
            changes.append((change["emitter"], f"{change['event']} event", age))
    born = {contract for _, contract in core.created}
    for context, target, _ in core.delegations:
        context_age, target_age = age_of(context), age_of(target)
        if context_age is None or context_age <= ESTABLISHED_SECONDS or context in side:
            continue
        if target in side or target in born:
            when = "created in this transaction" if not target_age else f"created {span_seconds(target_age)} earlier"
            changes.append((context, f"ran code from the sender's own contract ({when}) by delegatecall", context_age))
        elif target_age is not None and target_age <= FRESH_CODE_SECONDS:
            when = "created in this transaction" if target_age == 0 else f"created {span_seconds(target_age)} earlier"
            changes.append((context, f"ran code from a contract {when} by delegatecall", context_age))
    return list(dict.fromkeys(changes))


def watched_before(watch: dict[str, dict], address: str | None, block: int, index: int) -> bool:
    """Whether `address` had its logic or control changed earlier in the window than this transaction."""
    entry = watch.get(address) if address else None
    return bool(entry) and (entry["block"], entry["index"]) < (block, index)


def proceeds_reason(party: str, side: list[str], sender: str, block: int, names: "Naming", ctx: "Context") -> str | None:
    """Why value that landed on `party` counts as the sender's side's: a labeled mixer, a wallet with very few prior
    transactions, a wallet the sender funded, or one funded from the same source as the sender."""
    label = names.label(party)
    if label and label["category"] == "mixer":
        return "a labeled mixer"
    if ctx.kinds.get((party, block)) not in WALLET_KINDS:
        return None
    nonce = ctx.nonces_before.get((party, block))
    if nonce is not None and nonce < NEW_WALLET_NONCES:
        return "a wallet with no prior transactions" if nonce == 0 else f"a wallet with only {nonce} prior transaction{'s' if nonce != 1 else ''}"
    funding = ctx.funding.get(party)
    if funding:
        if funding["funder"] in side:
            return "a wallet the sender's side funded"
        sender_funding = ctx.funding.get(sender)
        if sender_funding and sender_funding["funder"] == funding["funder"]:
            return "a wallet funded from the same source as the sender"
    return None


def span_seconds(seconds: int) -> str:
    for size, name in ((86400 * 365, "year"), (86400 * 30, "month"), (86400, "day"), (3600, "hour"), (60, "minute")):
        if seconds >= size:
            n = seconds // size
            return f"{n} {name}{'s' if n != 1 else ''}"
    return f"{seconds} seconds"


def by_value(amounts: list[dict]) -> list[dict]:
    """Amount facts, largest priced value first; unpriced amounts last, by asset name."""
    return sorted(amounts, key=lambda a: (-(a["usd"] or 0.0), a["asset"]))


def ledger_rows(ledger: dict[str, dict[str, int]], shown: list[str], names: Naming, ctx: Context) -> list[dict]:
    rows = []
    for party in shown:
        changes = [{"direction": "gained" if net > 0 else "lost"} | amount_facts(asset, abs(net), names, ctx)
                   for asset, net in ledger[party].items()]
        changes.sort(key=lambda c: (-(c["usd"] or 0.0), c["asset"]))
        gave = sum(c["usd"] for c in changes if c["usd"] is not None and c["direction"] == "lost")
        received = sum(c["usd"] for c in changes if c["usd"] is not None and c["direction"] == "gained")
        rows.append({"party": names.party(party), "changes": changes, "gave_usd": round(gave, 2),
                     "received_usd": round(received, 2), "net_usd": round(received - gave, 2)})
    return rows


def own_capital_usd(core: Core, side: list[str], ctx: Context) -> float:
    """Priced value the sender's side had to hold before the transaction: for each asset, how far its running balance
    over the movements dips below zero. Borrowed funds arrive before they are spent, so they never count."""
    running: dict[str, int] = {}
    lowest: dict[str, int] = {}
    for m in core.movements:
        change = (m.recipient in side) - (m.sender in side)
        if change:
            running[m.asset] = running.get(m.asset, 0) + change * m.amount
            lowest[m.asset] = min(lowest.get(m.asset, 0), running[m.asset])
    return sum(usd_value(asset, -low, ctx.prices, ctx.eth_usd) or 0.0 for asset, low in lowest.items() if low < 0)


def finish(core: Core, ctx: Context) -> TxFacts:
    tx, block = core.tx, int(core.tx["blockNumber"], 16)
    sender, entry_address = tx["from"].lower(), core.root.target
    index = int(tx["transactionIndex"], 16)
    # A contract whose logic or control changed earlier in the window is nobody's bot, whoever calls it now.
    entry_is_public = (ctx.prior_day_senders.get((entry_address, block), 0) >= PUBLIC_SENDERS
                       or watched_before(ctx.contract_watch, entry_address, block, index))
    needed = cast(core, ctx.prices, ctx.eth_usd, ctx.labels, entry_is_public)
    side = whole_side(core, needed.parties, ctx.creations, block)
    implied = implied_prices(core, side, ctx.prices, ctx.eth_usd, ctx.decimals)
    if implied:  # a shallow copy: the shared lookups and the window memory stay the same objects
        ctx = replace(ctx, prices=ctx.prices | implied)
    names = Naming(core, ctx, side)
    names.party(sender)
    if entry_address:
        names.party(entry_address)

    ledger, logs_only = net_ledger(core.movements), net_ledger(core.log_movements)
    shown = shown_parties(ledger, core, ctx.prices, ctx.eth_usd)
    rows = ledger_rows(ledger, shown, names, ctx)
    logs_rows = ledger_rows(logs_only, shown_parties(logs_only, core, ctx.prices, ctx.eth_usd), names, ctx)

    flow = flows(ledger, ctx.prices, ctx.eth_usd)
    unpriced = sorted({names.asset(a) for p in side for a in ledger.get(p, {})
                       if usd_value(a, 1, ctx.prices, ctx.eth_usd) is None})
    burned: Counter = Counter()
    for m in core.movements:
        if m.recipient == ZERO and m.sender in side:
            burned[m.asset] += m.amount
    side_net = sum(flow[p][1] - flow[p][0] for p in side if p in flow)
    proceeds, extended = [], list(side)
    losses = [flow[p][0] - flow[p][1] for p in flow if p not in side and p != core.builder]
    largest_loss = max(losses, default=0.0)
    largest_gain = None
    for party in sorted((p for p in flow if p not in side and p not in (core.builder, ZERO)),
                        key=lambda p: flow[p][0] - flow[p][1]):
        gain = flow[party][1] - flow[party][0]
        if gain < PROCEEDS_MIN_USD:
            break
        reason = proceeds_reason(party, side, sender, block, names, ctx)
        if reason:
            proceeds.append({"party": names.party(party), "reason": reason, "usd": round(gain, 2)})
            extended.append(party)
        elif largest_gain is None and largest_loss >= DRAIN_MIN_USD and gain >= PROCEEDS_SHARE * largest_loss \
                and side_net < SIDE_KEEPS_SHARE * largest_loss:
            largest_gain = {"party": names.party(party), "usd": round(gain, 2)}
    sender_side = {"members": [names.party(p) for p in side],
                   "net_usd": round(sum(flow[p][1] - flow[p][0] for p in extended if p in flow), 2),
                   "own_side_net_usd": round(side_net, 2), "proceeds_to": proceeds, "largest_gain_elsewhere": largest_gain,
                   "own_capital_usd": round(own_capital_usd(core, side, ctx), 2), "unpriced_assets": unpriced,
                   "burned": by_value([amount_facts(a, n, names, ctx) for a, n in burned.items()])}

    minted: dict[tuple[str, str], list[int]] = {}  # (asset, recipient) -> [amount, first movement index]
    for i, m in enumerate(core.movements):
        if m.sender == ZERO and m.recipient in [*shown, *created_side(core)]:  # the side may sell a mint at once
            minted.setdefault((m.asset, m.recipient), [0, i])[0] += m.amount
    minted_rows = []
    lending_accounting_issuances = []
    lending_borrow_emitters = {
        emitter for emitter, event in core.events
        if event == "Borrow" and (label := names.label(emitter)) and label["category"] == "lending"
    }
    for (asset, recipient), (amount, first) in minted.items():
        call = frame_holding(core.root, first, asset)
        issuer = call.caller if call else None  # the contract whose call made the token mint
        row = {"to": names.party(recipient), "issued_by": names.party(issuer, "contract") if issuer else None,
               "issuer_received_from_side": None} | amount_facts(asset, amount, names, ctx)  # a caller below the root is a contract
        if issuer and recipient in side and issuer not in side:  # the robbed party, if there is one, is the issuer
            got: Counter = Counter()
            for m in core.movements:
                if m.sender in side and m.recipient == issuer:
                    got[m.asset] += m.amount
            row["issuer_received_from_side"] = by_value([amount_facts(a, n, names, ctx) for a, n in got.items()])
        minted_rows.append(row)
        if recipient in side and issuer in lending_borrow_emitters:
            lending_accounting_issuances.append({"borrower": names.party(recipient), "lender": names.party(issuer, "contract"),
                                                 "issued": amount_facts(asset, amount, names, ctx)})
    minted_rows.sort(key=lambda row: (-(row["usd"] or 0.0), row["asset"], row["to"]))
    lending_accounting_issuances.sort(key=lambda row: (row["lender"], row["borrower"], row["issued"]["asset"]))

    collateral = []
    for i, mint in enumerate(core.movements):
        if not (mint.sender == ZERO and mint.recipient in side):
            continue
        call = frame_holding(core.root, i, mint.asset)
        if not call or call.caller not in side:  # minted by someone else's contract: a purchase or a reward, not self-issue
            continue
        posted = next(((j, m) for j, m in enumerate(core.movements) if j > i and m.asset == mint.asset
                       and m.sender in side and m.recipient not in side and m.recipient != ZERO), None)
        if not posted:
            continue
        j, deposit = posted
        received = next((m for k, m in enumerate(core.movements) if k > j and m.recipient in side and m.asset != mint.asset
                         and (m.sender == deposit.recipient or (m.sender == ZERO and (issue := frame_holding(core.root, k, m.asset))
                                                                 and issue.caller == deposit.recipient))), None)
        if received:
            collateral.append({"posted_to": names.party(deposit.recipient, "contract"),
                               "posted": amount_facts(deposit.asset, deposit.amount, names, ctx),
                               "received": amount_facts(received.asset, received.amount, names, ctx)})
            break

    allowance_changes = []
    for asset, owner, spender, amount in core.approvals:
        if amount and (owner in side or spender in side):
            allowance_changes.append({"asset": amount_facts(asset, amount, names, ctx), "owner": names.party(owner),
                                      "spender": names.party(spender, "contract"), "owner_is_sender_side": owner in side,
                                      "spender_is_sender_side": spender in side})
    allowance_changes.sort(key=lambda row: (-(row["asset"]["usd"] or 0.0), row["asset"]["asset"], row["owner"], row["spender"],
                                            int(row["asset"]["amount_raw"])))

    internal_by_account_asset: dict[tuple[str, str, str], int] = {}
    for vault, account, asset, delta in core.internal_balances:
        if account in side:
            key = (vault, account, asset)
            internal_by_account_asset[key] = internal_by_account_asset.get(key, 0) + delta
    internal_balance_changes = []
    for (vault, account, asset), delta in internal_by_account_asset.items():
        if delta:
            internal_balance_changes.append({"vault": names.party(vault, "contract"), "account": names.party(account),
                                             "account_is_sender_side": account in side, "direction": "credited" if delta > 0 else "debited"}
                                            | amount_facts(asset, abs(delta), names, ctx))
    internal_balance_changes.sort(key=lambda row: (-(row["usd"] or 0.0), row["asset"], row["vault"], row["account"]))

    positions_moved = []
    for issuer in dict.fromkeys(emitter for emitter, _, _, _, _ in core.positions):
        mine = [(source, recipient, token_id, amount) for emitter, source, recipient, token_id, amount in core.positions if emitter == issuer]
        recipients = [names.party(recipient) for recipient in dict.fromkeys(recipient for _, recipient, _, _ in mine)
                      if recipient != ZERO][:PULL_RECIPIENTS_SHOWN]
        positions_moved.append({"issuer": names.party(issuer, "contract"), "count": len(mine), "to": recipients,
                                "to_sender_side": sum(recipient in side for _, recipient, _, _ in mine),
                                "minted": sum(source == ZERO for source, _, _, _ in mine),
                                "raw_ids": [str(token_id) for _, _, token_id, _ in mine if token_id is not None][:4],
                                "raw_amounts": [str(amount) for _, _, _, amount in mine if amount is not None][:4]})

    side_unpriced_moves = sum(1 for m in core.movements if (m.sender in side or m.recipient in side) and m.asset != ETH
                              and m.asset not in core.nft_collections and usd_value(m.asset, 1, ctx.prices, ctx.eth_usd) is None)
    nft_moves = sum(1 for m in core.movements if m.asset in core.nft_collections)
    precursor = bool(core.created) and (nft_moves > 0 or bool(core.positions) or side_unpriced_moves > 0) \
        and abs(sender_side["net_usd"]) < 1 and sender_side["own_capital_usd"] < 1
    earlier_notes = [{"blocks_earlier": block - note["block"], "summary": note["summary"]}
                     for note in ctx.actor_notes.get(sender, []) if (note["block"], note["index"]) < (block, index)]
    if precursor:
        ctx.actor_notes.setdefault(sender, []).append({
            "block": block, "index": index,
            "summary": (f"deployed {len(core.created)} contract{'s' if len(core.created) != 1 else ''} and moved "
                        f"{nft_moves + len(core.positions) + side_unpriced_moves} positions or unpriced tokens "
                        "while no priced value moved")})

    effective_frames = [f for f in frames_of(core.root) if not f.failed and f.target and not is_precompile(f.target)]
    logic_changes = [{"contract": names.party(address, "contract"), "what": what, "contract_age_seconds": age}
                     for address, what, age in logic_changes_of(core, side, names.age)]
    touched_here = {f.context for f in effective_frames} | {f.target for f in effective_frames}
    heightened = []
    for address, watch in ctx.contract_watch.items():
        if address in touched_here and (watch["block"], watch["index"]) < (block, index):
            heightened.append({"contract": names.party(address, "contract"), "what": watch["what"],
                               "blocks_earlier": block - watch["block"], "contract_age_seconds": watch["age_seconds"]})
    for change in logic_changes:
        address = names.parties[change["contract"]]["address"]
        # A protocol that many wallets call and that upgraded its code is doing business as usual; the watch is for a
        # contract few wallets call, such as a treasury or a multisig, whose logic or control changed.
        if ctx.prior_day_senders.get((address, block), 0) < PUBLIC_SENDERS:
            ctx.contract_watch.setdefault(address, {"block": block, "index": index, "what": change["what"],
                                                    "age_seconds": change["contract_age_seconds"]})

    drains = []
    for holder, asset in needed.drains:
        if holder in side:  # a contract the sender deployed earlier: its loss is the sender's own business
            continue
        position = (holder, asset, block, int(tx["transactionIndex"], 16))
        before = ctx.balances_before.get(position)
        lost, (gave, received) = -ledger[holder][asset], flow[holder]
        # What the holder gave and got across the whole transaction says whether the loss was a sale or a drain.
        earlier = ctx.same_sender_deposits.get(position)
        drains.append({"party": names.party(holder), "share_of_prior_balance": round(lost / before, 4) if before else None,
                       "gave_usd": round(gave, 2), "received_usd": round(received, 2),
                       "received_assets": [a["asset"] for a in by_value([amount_facts(a, n, names, ctx)
                                                                         for a, n in ledger[holder].items() if n > 0])],
                       "unpriced_legs": any(usd_value(a, 1, ctx.prices, ctx.eth_usd) is None for a in ledger[holder]),
                       "unpriced_received": any(n > 0 and usd_value(a, 1, ctx.prices, ctx.eth_usd) is None
                                                for a, n in ledger[holder].items()),
                       "events_recorded": sorted({name for emitter, name in core.events if emitter == holder})[:3],
                       "same_sender_put_in_earlier": ({"index": earlier[1]} | amount_facts(asset, earlier[0], names, ctx)
                                                      if earlier else None)}
                      | amount_facts(asset, lost, names, ctx))

    pulls = []
    # A pull from a contract is a protocol's own plumbing (a vault funding a market); the pulls that matter come from
    # wallets, or from addresses whose code was not looked up.
    pulled = [p for p in pulls_of(core, side) if ctx.kinds.get((p["owner"], block)) != "contract"]
    for spender in dict.fromkeys(p["spender"] for p in pulled):
        mine = [p for p in pulled if p["spender"] == spender]
        by_asset: Counter = Counter()
        for p in mine:
            by_asset[p["asset"]] += p["amount"]
        amounts = by_value([amount_facts(a, n, names, ctx) for a, n in by_asset.items()])
        priced = [a["usd"] for a in amounts if a["usd"] is not None]
        if sum(priced) < PULL_MIN_USD:
            continue
        pulls.append({"spender": names.party(spender, "contract" if spender != side[0] else None),
                      "spender_is": ("the sender" if spender == side[0] else "the sender's contract" if spender in side
                                     else "the contract the sender called" if spender == entry_address else "another contract"),
                      "owners": len({p["owner"] for p in mine}), "transfers": len(mine),
                      "recipients": [names.party(r) for r in dict.fromkeys(p["recipient"] for p in mine)][:PULL_RECIPIENTS_SHOWN],
                      "approved_in_this_transaction": sum(p["approved_now"] for p in mine),
                      "usd": round(sum(priced), 2) if priced else None, "assets": [a["asset"] for a in amounts][:3]})

    flash_loans = [{"lender": names.party(loan["lender"]), "detected_by": loan["source"]}
                   | amount_facts(loan["asset"], loan["amount"], names, ctx)
                   for loan in flash_loans_taken(core, ctx.labels, entry_is_public)]
    reentrancy = [{"contract": names.party(contract), "through": names.party(through), "read_only": static}
                  for contract, through, static in reentries_shown(core, ctx.labels, entry_is_public)]
    privileged = [{"contract": names.party(p["emitter"]), "event": p["event"],
                   "subject": names.party(p["subject"]) if p["subject"] and p["subject"] != ZERO else None}
                  for p in core.privileged]

    def emitter_name(emitter: str) -> str:
        if emitter in names.alias_of or emitter in needed.parties:
            return names.party(emitter)
        return "an exchange pool" if emitter in core.swap_emitters else "another contract"

    events = [{"contract": emitter_name(emitter), "event": name, "count": n}
              for (emitter, name), n in Counter(core.events).most_common(EVENTS_SHOWN)]

    effective = [f for f in frames_of(core.root) if not f.failed and f.target and not is_precompile(f.target)]
    touched: list[str] = []
    for f in effective:
        label = names.label(f.context)
        if label and label["category"] != "token" and label["name"] not in touched:
            touched.append(label["name"])
    repeated = [{"target": names.party(target, "contract"), "function": function_name(target, selector, names, ctx),
                 "count": n} for target, selector, n in core.repeated]
    call_shape = {"calls": core.calls, "max_depth": core.max_depth,
                  "distinct_contracts": len({f.target for f in effective}), "labeled_protocols": len(touched),
                  "contracts_created": len(core.created), "contracts_destroyed": len(core.destroyed),
                  "reverted_inner_calls": core.reverted_inner_calls, "repeated_calls": repeated,
                  "nft_transfers": core.nft_transfers, "other_events": core.other_events}

    funding = ctx.funding.get(sender)
    sender_label = names.label(sender)
    sender_facts = {"kind": ctx.kinds[(sender, block)], "prior_transactions": int(tx["nonce"], 16),
                    "label": sender_label["name"] if sender_label else None,
                    "category": sender_label["category"] if sender_label else None,
                    "funding_looked_up": sender in ctx.funding, "first_funded_seconds_earlier": None,
                    "funded_by": None, "funded_by_category": None, "mixer_funded_within_30_days": None,
                    "mixer_paid_seconds_earlier": None, "mixer_paid_by": None}
    if funding:
        funder = ctx.labels.get(funding["funder"])  # a funder's label needs no age check: the funding is in the past
        sender_facts |= {"first_funded_seconds_earlier": max(0, core.block_timestamp - funding["timestamp"]),
                         "funded_by": funder["name"] if funder else None,
                         "funded_by_category": funder["category"] if funder else None}
    position = (sender, block, int(tx["transactionIndex"], 16))
    if position in ctx.mixer_payouts:
        payout = ctx.mixer_payouts[position]
        sender_facts["mixer_funded_within_30_days"] = payout is not None
        if payout:
            paid_block, pool = payout  # every pool in the payout list comes from the label file
            sender_facts |= {"mixer_paid_seconds_earlier": (block - paid_block) * SLOT_SECONDS,
                             "mixer_paid_by": ctx.labels[pool]["name"]}

    entry = None
    if entry_address:
        entry = {"alias": names.party(entry_address), "function": function_name(entry_address, core.root.selector, names, ctx),
                 "calls_in_prior_day": ctx.prior_day_calls.get((entry_address, block))}

    value = int(tx["value"], 16)
    return {
        "version": FACTS_VERSION,
        "tx": {"hash": tx["hash"], "block": block, "index": int(tx["transactionIndex"], 16), "type": tx.get("type"),
               "from": sender, "to": tx["to"].lower() if tx.get("to") else None,
               "creates": None if tx.get("to") else entry_address,
               "selector": core.root.selector if tx.get("to") else None, "input_bytes": (len(tx["input"]) - 2) // 2,
               "value_wei": str(value), "gas_used": core.gas_used, "log_count": core.log_count},
        "status": "success" if core.succeeded else "failed",
        "trivial": core.trivial,
        "sender": sender_facts,
        "entry": entry,
        "ledger": rows,
        "ledger_logs_only": logs_rows,
        "minted": minted_rows,
        "lending_accounting_issuances": lending_accounting_issuances,
        "sender_side": sender_side,
        "drains": drains,
        "pulls": pulls,
        "allowance_changes": allowance_changes[:PULL_RECIPIENTS_SHOWN],
        "internal_balance_changes": internal_balance_changes[:PULL_RECIPIENTS_SHOWN],
        "positions_moved": positions_moved,
        "self_minted_collateral": collateral,
        "precursor": precursor,
        "earlier_by_this_sender": earlier_notes,
        "logic_changes": logic_changes,
        "heightened": heightened,
        "flash_loans": flash_loans,
        "reentrancy": reentrancy,
        "privileged_events": privileged,
        "events": events,
        "protocols_touched": touched[:PROTOCOLS_SHOWN],
        "call_shape": call_shape,
        "call_tree": call_tree(core, names, ctx),
        "mev": {"position": int(tx["transactionIndex"], 16) + 1, "block_transactions": core.block_tx_count,
                "builder_payment_usd": round(core.builder_payment_wei / 1e18 * ctx.eth_usd, 2),
                "fee_usd": round(core.fee_wei / 1e18 * ctx.eth_usd, 2),
                "value_sent_usd": round(value / 1e18 * ctx.eth_usd, 2)},
        # Last, so every alias the fields above introduced is described.
        "parties": names.parties,
        "assets": names.assets,
    }


def function_name(target: str, selector: str | None, names: Naming, ctx: Context) -> str | None:
    """A function's name, only for a call into a labeled, established contract. On any other contract the selector is
    its deployer's choice, so a name resolved from it is attacker-controlled text: bots in the first window mined
    selectors that resolve to names like IBribe2MuchZ7650399733."""
    if selector is None or names.label(target) is None:
        return None
    return FUNCTION_NAME.get(selector) or ctx.function_names.get(selector)


def call_tree(core: Core, names: Naming, ctx: Context) -> list[str]:
    """The call tree as indented lines, pruned: no read-only calls except known price reads, no calls into token
    contracts (the ledger has their effect), proxies folded into their callers, repeats collapsed to one line with a
    count, and depth cut until the text fits TREE_TOKEN_CAP."""
    tokens = {m.asset for m in core.movements}

    def is_token(address: str) -> bool:
        return address in tokens or ctx.labels.get(address, {}).get("category") == "token"

    def subtree(frame: Frame, depth: int, limit: int) -> list[str]:
        blocks: list[list[str]] = []
        for child in frame.children:
            if child.failed or not child.target or is_precompile(child.target):
                continue
            if child.kind in INHERITS_CONTEXT:  # a proxy's implementation: its calls are the proxy's calls
                blocks += [[line] for line in subtree(child, depth, limit)]
                continue
            if (child.static and child.selector not in PRICE_READS) or \
                    (is_token(child.target) and (child.static or child.selector in TOKEN_SELECTORS)):
                continue
            indent = "  " * depth
            if depth >= limit:
                blocks.append([f"{indent}({sum(1 for _ in frames_of(child))} deeper calls not shown)"])
                continue
            name = function_name(child.target, child.selector, names, ctx)
            bare_payment = child.value and not child.children and child.selector is None
            callee = names.party(child.target, "wallet" if bare_payment else "contract")
            if child.kind in CREATE_KINDS:
                text = f"{names.party(child.caller)} creates {callee}"
            elif child.static:
                text = f"{names.party(child.caller, 'contract')} reads {name or 'a price'} from {callee}"
            elif bare_payment:
                text = f"{names.party(child.caller, 'contract')} pays {callee}"
            else:
                text = f"{names.party(child.caller, 'contract')} calls {callee}" + (f".{name}" if name else "")
            if child.value and child.kind in VALUE_KINDS:
                text += f" with {child.value / 1e18:.4g} ETH"
            blocks.append([indent + text, *subtree(child, depth + 1, limit)])
        lines: list[str] = []
        for i, block in enumerate(blocks):
            if i and blocks[i - 1] == block:
                continue
            run = 1
            while i + run < len(blocks) and blocks[i + run] == block:
                run += 1
            lines += [block[0] + (f"  (x{run})" if run > 1 else ""), *block[1:]]
        return lines

    def tokens_of(lines: list[str]) -> float:
        return sum(len(line) + 1 for line in lines) / 3.5

    for limit in range(TREE_MAX_DEPTH, 0, -1):
        tree = subtree(core.root, 0, limit)
        if tokens_of(tree) <= TREE_TOKEN_CAP:
            return tree
    kept: list[str] = []
    for line in tree:
        if tokens_of(kept + [line]) > TREE_TOKEN_CAP - 20:
            return kept + [f"({len(tree) - len(kept)} more lines not shown)"]
        kept.append(line)
    return kept
