"""Builders for small hand-made transactions in the shapes the node returns (callTracer with logs, receipts)."""

from jevscan_monitor.facts import TOPIC, WETH, Context

TRANSFER = TOPIC["Transfer(address,address,uint256)"]
BLOCK_NUMBER = 20_000_000
BLOCK_TIME = 1_750_000_000
ETH_USD = 2_000.0


def addr(n: int) -> str:
    return "0x" + format(0x1000 + n, "040x")


SENDER, BOT, POOL_A, POOL_B, LENDER, VICTIM, TOKEN, TOKEN_2, BUILDER, WALLET, MIXER = (addr(i) for i in range(11))


def topic(address: str) -> str:
    return "0x" + address[2:].rjust(64, "0")


def amount_data(*words: int) -> str:
    return "0x" + "".join(format(w, "064x") for w in words)


def log(address: str, topics: list[str], data: str = "0x", position: int = 0) -> dict:
    return {"address": address, "topics": topics, "data": data, "position": hex(position)}


def transfer(token: str, sender: str, recipient: str, amount: int, position: int = 0) -> dict:
    return log(token, [TRANSFER, topic(sender), topic(recipient)], amount_data(amount), position)


def frame(caller: str, target: str | None, kind: str = "CALL", value: int | None = 0, selector: str = "0x12345678",
          calls: list[dict] | None = None, logs: list[dict] | None = None, error: str | None = None) -> dict:
    node = {"type": kind, "from": caller, "input": selector, "gas": "0x0", "gasUsed": "0x0"}
    if target is not None:
        node["to"] = target
    if value is not None:
        node["value"] = hex(value)
    if calls:
        node["calls"] = calls
    if logs:
        node["logs"] = logs
    if error:
        node["error"] = error
    return node


def surviving(node: dict, failed: bool = False) -> list[dict]:
    """The logs a receipt would hold for this trace: those outside reverted frames, in execution order."""
    failed = failed or "error" in node
    logs = sorted(node.get("logs", ()), key=lambda entry: int(entry["position"], 16))
    out, emitted = [], 0
    for i, child in enumerate([*node.get("calls", ()), None]):
        while emitted < len(logs) and (child is None or int(logs[emitted]["position"], 16) <= i):
            if not failed:
                out.append(logs[emitted])
            emitted += 1
        if child is not None:
            out += surviving(child, failed)
    return out


def chain_data(trace: dict, *, nonce: int = 7, index: int = 3, receipt_logs: list[dict] | None = None,
               tx_type: str = "0x2") -> tuple[dict, dict, dict, dict]:
    """(block, tx, receipt, trace) consistent with `trace`, as facts.extract takes them."""
    logs = surviving(trace) if receipt_logs is None else receipt_logs
    creation = trace["type"] in ("CREATE", "CREATE2")
    tx = {"hash": "0x" + "ab" * 32, "from": trace["from"], "to": None if creation else trace["to"],
          "input": trace["input"], "value": trace.get("value", "0x0"), "nonce": hex(nonce),
          "transactionIndex": hex(index), "blockNumber": hex(BLOCK_NUMBER), "type": tx_type}
    receipt = {"status": "0x0" if "error" in trace else "0x1", "gasUsed": hex(100_000), "effectiveGasPrice": hex(12 * 10**9),
               "logs": [{k: v for k, v in entry.items() if k != "position"} for entry in logs],
               "contractAddress": trace.get("to") if creation else None}
    block = {"number": hex(BLOCK_NUMBER), "timestamp": hex(BLOCK_TIME), "miner": BUILDER,
             "baseFeePerGas": hex(10 * 10**9), "transactions": [tx] * 10}
    return block, tx, receipt, trace


def context(**overrides) -> Context:
    """A Context in which TOKEN is an old, priced, labeled stablecoin, MIXER is a labeled mixer pool, and nothing
    else is known."""
    ctx = Context(labels={TOKEN: {"name": "USDX token", "category": "token", "symbol": "USDX"},
                          MIXER: {"name": "Some Mixer: 1 ETH", "category": "mixer", "symbol": None}}, eth_usd=ETH_USD,
                  prices={TOKEN: {"usd": 1.0, "symbol": "USDX", "decimals": 6},
                          WETH: {"usd": ETH_USD, "symbol": "WETH", "decimals": 18}},
                  creations={TOKEN: {"creator": addr(99), "block": 1, "timestamp": BLOCK_TIME - 400 * 86400}})
    for name, value in overrides.items():
        getattr(ctx, name).update(value)
    return ctx


def kinds(**by_kind: list[str]) -> dict:
    return {(address, BLOCK_NUMBER): kind.replace("_", " ") for kind, addresses in by_kind.items() for address in addresses}
