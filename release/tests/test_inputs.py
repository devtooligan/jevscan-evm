import copy

import pytest

from jevscan_monitor.inputs import validate_block, validate_trace
from tests.helpers import BLOCK_NUMBER, SENDER, WALLET, chain_data, frame


def complete_block():
    block, tx, receipt, trace = chain_data(frame(SENDER, WALLET), index=0)
    block["hash"] = "0x" + "11" * 32
    block["transactions"] = [tx]
    tx["blockHash"] = block["hash"]
    receipt.update(blockHash=block["hash"], blockNumber=block["number"], transactionHash=tx["hash"], transactionIndex="0x0")
    return block, [receipt], [{"txHash": tx["hash"], "result": trace}]


def test_complete_block_validates():
    validate_block(*complete_block(), BLOCK_NUMBER)


@pytest.mark.parametrize("mismatch", ["receipt_hash", "trace_hash", "block_hash", "index", "missing_trace", "status"])
def test_incomplete_or_mismatched_block_never_passes(mismatch):
    block, receipts, traces = complete_block()
    if mismatch == "receipt_hash":
        receipts[0]["transactionHash"] = "0x" + "22" * 32
    elif mismatch == "trace_hash":
        traces[0]["txHash"] = "0x" + "22" * 32
    elif mismatch == "block_hash":
        receipts[0]["blockHash"] = "0x" + "22" * 32
    elif mismatch == "index":
        receipts[0]["transactionIndex"] = "0x1"
    elif mismatch == "missing_trace":
        traces = []
    else:
        receipts[0]["status"] = "0x0"
    with pytest.raises(ValueError):
        validate_block(block, receipts, traces, BLOCK_NUMBER)


def test_deep_or_cyclic_trace_fails_before_recursive_extraction():
    trace = frame(SENDER, WALLET)
    trace["calls"] = [trace]
    with pytest.raises(ValueError, match="complexity"):
        validate_trace(trace)


def test_duplicate_transaction_rejected():
    block, receipts, traces = complete_block()
    block["transactions"].append(copy.deepcopy(block["transactions"][0]))
    receipts.append(copy.deepcopy(receipts[0]))
    traces.append(copy.deepcopy(traces[0]))
    with pytest.raises(ValueError, match="Duplicate"):
        validate_block(block, receipts, traces, BLOCK_NUMBER)


@pytest.mark.parametrize("field,value", [("from", WALLET), ("to", SENDER), ("value", "0x1"),
    ("input", "0xabcdef"), ("value", "0x" + "f" * 1000)])
def test_root_trace_must_match_transaction(field, value):
    block, receipts, traces = complete_block()
    traces[0]["result"][field] = value
    with pytest.raises(ValueError):
        validate_block(block, receipts, traces, BLOCK_NUMBER)
