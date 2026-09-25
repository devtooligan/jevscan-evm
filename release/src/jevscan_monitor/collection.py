"""Complete finalized-block collection, independent of research manifests."""

import asyncio
import json
from pathlib import Path

from jevscan_monitor import enrich, facts, labels, mixers, views
from jevscan_monitor.evaluation import digest
from jevscan_monitor.inputs import require_hash, validate_block
from jevscan_monitor.provider import atomic_json
from jevscan_monitor.rpc import Http, Rpc

TRACER = {"tracer": "callTracer", "tracerConfig": {"withLog": True}}


async def prepare() -> dict:
    async with Rpc() as rpc, Http() as http:
        if not labels.LABELS_FILE.exists():
            accounts = await http.get("labels_dump", labels.DUMP_PATH + "/accounts.json", {})
            tokens = await http.get("labels_dump", labels.DUMP_PATH + "/tokens.json", {})
            atomic_json(labels.LABELS_FILE, labels.build(accounts, tokens))
        table = labels.load()
        pools = [address for address, entry in table.items() if entry["category"] == "mixer"]
        if not pools:
            raise ValueError("No mixer contracts available in the prepared labels")
        added, head = await mixers.sync(rpc, pools)
        enrich.mixer_payouts.cache_clear()
        return {"labels": len(table), "mixer_payouts_added": added, "mixer_index_finalized_through": head,
                "classifier_calls": 0}


async def collect(start: int, end: int, output: Path) -> dict:
    if type(start) is not int or type(end) is not int or start < 1 or not start <= end < start + 20:
        raise ValueError("Choose one to 20 consecutive historical blocks")
    if output.exists():
        raise FileExistsError("Refusing to overwrite an existing collection")
    table = labels.load()
    enrich.mixer_payouts.cache_clear()
    if enrich.mixer_payouts()[1] < end:
        raise ValueError("Mixer index is stale; run prepare before collection")
    cores, selected = [], []
    async with Rpc() as rpc, Http() as http:
        finalized = await rpc.call("eth_getBlockByNumber", ["finalized", False], cached=False)
        if not isinstance(finalized, dict) or end > int(finalized["number"], 16):
            raise ValueError("Only finalized historical blocks may be collected")
        for number in range(start, end + 1):
            # Canonical block identity is always refreshed; cached raw block data
            # cannot silently determine whether collection is complete.
            block = await rpc.call("eth_getBlockByNumber", [hex(number), True], cached=False)
            receipts, traces = await asyncio.gather(
                rpc.call("eth_getBlockReceipts", [hex(number)], cached=False),
                rpc.call("debug_traceBlockByNumber", [hex(number), TRACER], cached=False),
            )
            validate_block(block, receipts, traces, number)
            for tx, receipt, trace in zip(block["transactions"], receipts, traces):
                cores.append(facts.extract(block, tx, receipt, trace["result"]))
            selected.append({"number": number, "hash": block["hash"], "transactions": len(block["transactions"])})
        context = await enrich.gather(cores, table, rpc, http) if cores else None
        # finish mutates actor and contract history: never parallelize this loop.
        records = [facts.finish(core, context) for core in cores]
        for block in selected:
            refreshed = await rpc.call("eth_getBlockByNumber", [hex(block["number"]), False], cached=False)
            if not isinstance(refreshed, dict) or refreshed["hash"] != block["hash"]:
                raise RuntimeError("Canonical block changed during collection; output not saved")
    rows = [{"transaction": record["tx"]["hash"], "block": record["tx"]["block"],
             "index": record["tx"]["index"], "facts": record, "state": views.r2(record)} for record in records]
    result = {"schema": "jevscan-collection-v1", "chain_id": 1, "facts_version": facts.FACTS_VERSION,
              "extractor": "release-hardened", "historical_baseline_facts_version": 10,
              "blocks": selected, "rows": rows, "complete": True}
    result["content_sha256"] = digest(result)
    if len(json.dumps(result).encode()) > 128 * 1024 * 1024:
        raise ValueError("Collection exceeds supported file size; choose fewer blocks")
    if output.exists():
        raise FileExistsError("Collection destination appeared while collecting")
    atomic_json(output, result, overwrite=False)
    return {"blocks": len(selected), "transactions": len(rows), "facts_version": facts.FACTS_VERSION,
            "classifier_calls": 0, "output": str(output)}


def load_collection(path: Path) -> dict:
    if path.is_symlink() or not path.is_file() or path.stat().st_size > 128 * 1024 * 1024:
        raise ValueError("Collection missing, oversized, or a symbolic link")
    value = json.loads(path.read_text())
    if (not isinstance(value, dict) or value.get("schema") != "jevscan-collection-v1"
            or value.get("complete") is not True or value.get("chain_id") != 1
            or value.get("facts_version") != facts.FACTS_VERSION):
        raise ValueError("Incomplete or incompatible collection")
    checksum = value.pop("content_sha256", None)
    if digest(value) != checksum:
        raise ValueError("Collection integrity mismatch")
    rows, blocks = value["rows"], value["blocks"]
    if not isinstance(blocks, list) or not 1 <= len(blocks) <= 20:
        raise ValueError("Collection must contain one to 20 consecutive blocks")
    if not isinstance(rows, list) or len(rows) > 100000:
        raise ValueError("Invalid or oversized collection rows")
    expected, seen = {}, set()
    for block in blocks:
        if (not isinstance(block, dict) or type(block.get("number")) is not int
                or not 1 <= block["number"] < 2**63
                or type(block.get("transactions")) is not int
                or not 0 <= block["transactions"] <= 5000):
            raise ValueError("Invalid collection block metadata")
        require_hash(block.get("hash"))
        if expected and block["number"] != next(reversed(expected)) + 1:
            raise ValueError("Collection blocks are not consecutive and ordered")
        expected[block["number"]] = block["transactions"]
    if len(rows) != sum(expected.values()):
        raise ValueError("Collection transaction count mismatch")
    positions = {number: set() for number in expected}
    previous = None
    for row in rows:
        tx, block, index = row["transaction"], row["block"], row["index"]
        require_hash(tx)
        if (type(block) is not int or type(index) is not int or block not in expected
                or not 0 <= index < expected[block] or not isinstance(row.get("state"), dict)):
            raise ValueError("Invalid collection transaction position or state")
        if previous is not None and (block, index) <= previous:
            raise ValueError("Collection transactions are not ordered")
        previous = (block, index)
        if tx in seen or block not in expected or index in positions[block]:
            raise ValueError("Duplicate or unknown collection transaction")
        record = row["facts"]
        if (record["version"] != facts.FACTS_VERSION or record["tx"]["hash"] != tx
                or record["tx"]["block"] != block or record["tx"]["index"] != index
                or views.r2(record) != row["state"]):
            raise ValueError("Collection facts and rendered state disagree")
        seen.add(tx)
        positions[block].add(index)
    if any(positions[number] != set(range(count)) for number, count in expected.items()):
        raise ValueError("Collection omits transactions from a declared block")
    value["content_sha256"] = checksum
    return value
