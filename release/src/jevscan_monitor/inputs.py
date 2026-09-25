"""Bounded validation before raw chain data reaches recursive extraction."""

import re

HASH = re.compile(r"0x[0-9a-fA-F]{64}")
ADDRESS = re.compile(r"0x[0-9a-fA-F]{40}")
HEX = re.compile(r"0x(?:[0-9a-fA-F]{2})*")
QUANTITY = re.compile(r"0x[0-9a-fA-F]{1,64}")
MAX_TRACE_NODES = 2000
MAX_TRACE_DEPTH = 64
MAX_LOGS = 10000


def require_hash(value):
    if not isinstance(value, str) or not HASH.fullmatch(value):
        raise ValueError("Invalid transaction or block hash")
    return value.lower()


def require_address(value):
    if not isinstance(value, str) or not ADDRESS.fullmatch(value):
        raise ValueError("Invalid chain address")


def quantity(value):
    if not isinstance(value, str) or not QUANTITY.fullmatch(value):
        raise ValueError("Invalid or oversized chain quantity")
    return int(value, 16)


def validate_logs(logs):
    if not isinstance(logs, list) or len(logs) > MAX_LOGS:
        raise ValueError("Missing or oversized log list")
    for log in logs:
        if not isinstance(log, dict):
            raise ValueError("Invalid log object")
        require_address(log.get("address"))
        topics, data = log.get("topics"), log.get("data")
        if not isinstance(topics, list) or len(topics) > 4:
            raise ValueError("Invalid log topics")
        for topic in topics:
            require_hash(topic)
        if not isinstance(data, str) or len(data) > 1024 * 1024 or not HEX.fullmatch(data):
            raise ValueError("Invalid or oversized log data")


def validate_trace(root):
    todo, nodes, logs = [(root, 0)], 0, 0
    while todo:
        node, depth = todo.pop()
        nodes += 1
        if nodes > MAX_TRACE_NODES or depth > MAX_TRACE_DEPTH or not isinstance(node, dict):
            raise ValueError("Trace exceeds supported complexity; transaction not evaluated")
        if node.get("type") not in {"CALL", "STATICCALL", "DELEGATECALL", "CALLCODE", "CREATE", "CREATE2", "SELFDESTRUCT"}:
            raise ValueError("Unsupported trace frame")
        require_address(node.get("from"))
        if node.get("to") is not None:
            require_address(node["to"])
        for field in ("value", "gas", "gasUsed"):
            if field in node:
                quantity(node[field])
        data = node.get("input", "0x")
        if not isinstance(data, str) or len(data) > 1024 * 1024 or not HEX.fullmatch(data):
            raise ValueError("Invalid trace input")
        entries, children = node.get("logs", []), node.get("calls", [])
        validate_logs(entries)
        logs += len(entries)
        if logs > MAX_LOGS or not isinstance(children, list) or len(children) > MAX_TRACE_NODES:
            raise ValueError("Trace exceeds supported complexity")
        todo.extend((child, depth + 1) for child in children)


def validate_block(block, receipts, traces, expected_number):
    if not isinstance(block, dict) or quantity(block.get("number")) != expected_number:
        raise ValueError("Requested block number does not match response")
    block_hash = require_hash(block.get("hash"))
    require_address(block.get("miner"))
    for field in ("timestamp", "baseFeePerGas"):
        quantity(block.get(field))
    txs = block.get("transactions")
    if not isinstance(txs, list) or len(txs) > 5000:
        raise ValueError("Block transactions missing or too numerous")
    if not isinstance(receipts, list) or not isinstance(traces, list) or len(txs) != len(receipts) or len(txs) != len(traces):
        raise ValueError("Incomplete block, receipts or traces; block not evaluated")
    seen = set()
    for index, (tx, receipt, trace) in enumerate(zip(txs, receipts, traces)):
        if not all(isinstance(item, dict) for item in (tx, receipt, trace)):
            raise ValueError("Invalid transaction, receipt or trace object")
        tx_hash = require_hash(tx.get("hash"))
        if tx_hash in seen:
            raise ValueError("Duplicate block transaction")
        seen.add(tx_hash)
        if require_hash(receipt.get("transactionHash")) != tx_hash or require_hash(trace.get("txHash")) != tx_hash:
            raise ValueError("Receipt or trace transaction identity mismatch")
        for item in (tx, receipt):
            if (require_hash(item.get("blockHash")) != block_hash
                    or quantity(item["blockNumber"]) != expected_number
                    or quantity(item["transactionIndex"]) != index):
                raise ValueError("Block identity or transaction order mismatch")
        require_address(tx.get("from"))
        for field in ("value", "nonce", "type"):
            quantity(tx.get(field))
        for field in ("gasUsed", "effectiveGasPrice"):
            quantity(receipt.get(field))
        if receipt.get("status") not in {"0x0", "0x1"}:
            raise ValueError("Receipt execution status missing")
        validate_logs(receipt.get("logs"))
        if not isinstance(trace.get("result"), dict):
            raise ValueError("Call trace result missing")
        validate_trace(trace["result"])
        root = trace["result"]
        if (root["from"].lower() != tx["from"].lower() or root.get("input", "0x") != tx.get("input")
                or quantity(root.get("value", "0x0")) != quantity(tx["value"])):
            raise ValueError("Root trace disagrees with transaction caller, input or value")
        if tx.get("to") is not None:
            require_address(tx["to"])
            if root["type"] != "CALL" or (root.get("to") or "").lower() != tx["to"].lower():
                raise ValueError("Root trace target disagrees with transaction")
        elif root["type"] not in {"CREATE", "CREATE2"}:
            raise ValueError("Contract creation lacks a creation trace")
        elif receipt["status"] == "0x1":
            require_address(receipt.get("contractAddress"))
            if (root.get("to") or "").lower() != receipt["contractAddress"].lower():
                raise ValueError("Created contract differs between receipt and trace")
        if (receipt["status"] == "0x0") != bool(trace["result"].get("error")):
            raise ValueError("Trace and receipt disagree on execution success")
