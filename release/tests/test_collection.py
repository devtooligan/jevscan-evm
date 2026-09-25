import json
import asyncio
from argparse import Namespace

import pytest

from jevscan_monitor import collection, facts
from jevscan_monitor.evaluation import digest
from jevscan_monitor import cli, provider
from tests.helpers import context, kinds, SENDER, WALLET, BUILDER, BLOCK_NUMBER
from tests.test_inputs import complete_block
from tests.test_provider import Response


def saved(tmp_path, blocks, rows=None):
    value = {"schema": "jevscan-collection-v1", "complete": True, "chain_id": 1,
             "facts_version": facts.FACTS_VERSION, "blocks": blocks, "rows": rows or []}
    value["content_sha256"] = digest(value)
    path = tmp_path / "collection.json"
    path.write_text(json.dumps(value))
    return path


def block(number=1, count=0):
    return {"number": number, "hash": "0x" + "11" * 32, "transactions": count}


@pytest.mark.parametrize("blocks", [[], [block(-5)], [block(True)], [block(count=10**12)],
    [block(count=-1)], [block(count=True)], [block(2), block(1)], [block(1), block(3)],
    [block(1), block(1)], [block() | {"hash": "not-a-hash"}], [block(i) for i in range(1, 22)]])
def test_invalid_metadata_rejected_before_rendering(tmp_path, blocks, monkeypatch):
    def forbidden(*args):
        pytest.fail("Rendering must not precede metadata validation")
    monkeypatch.setattr(collection.views, "r2", forbidden)
    with pytest.raises(ValueError):
        collection.load_collection(saved(tmp_path, blocks))


def test_genuine_empty_block_is_not_an_empty_collection(tmp_path):
    assert collection.load_collection(saved(tmp_path, [block()]))["blocks"] == [block()]


def test_declared_missing_transaction_rejected(tmp_path):
    with pytest.raises(ValueError, match="count"):
        collection.load_collection(saved(tmp_path, [block(count=1)]))


def test_modified_checksum_rejected(tmp_path):
    path = saved(tmp_path, [block()])
    value = json.loads(path.read_text())
    value["blocks"][0]["number"] = 2
    path.write_text(json.dumps(value))
    with pytest.raises(ValueError, match="integrity"):
        collection.load_collection(path)


def test_collect_preflight_and_score_complete_path_offline(tmp_path, monkeypatch):
    raw_block, receipts, traces = complete_block()

    class Rpc:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            pass

        async def call(self, method, params, **kwargs):
            return {"eth_getBlockByNumber": raw_block, "eth_getBlockReceipts": receipts,
                    "debug_traceBlockByNumber": traces}[method]

    async def gather(*args):
        return context(kinds=kinds(wallet=[SENDER, WALLET, BUILDER]))

    calls = []

    class Session:
        def __init__(self, **kwargs):
            pass

        async def close(self):
            pass

        def post(self, url, **kwargs):
            request = json.loads(kwargs["data"])
            calls.append(request)
            return Response({"model": request["model"], "usage": {"input_tokens": 100},
                             "answers": {name: {"noul": .8} for name in request["questions"]}})

    monkeypatch.setenv("JEVSCAN_DATA_DIR", str(tmp_path / "private"))
    monkeypatch.setenv("TYPESAFE_API_KEY", "synthetic-key-only")
    monkeypatch.setattr(collection, "Rpc", Rpc)
    monkeypatch.setattr(collection, "Http", Rpc)
    monkeypatch.setattr(collection.labels, "load", lambda: {})
    monkeypatch.setattr(collection.enrich.mixers, "load", lambda: (None, BLOCK_NUMBER))
    monkeypatch.setattr(collection.enrich, "gather", gather)
    monkeypatch.setattr(provider.aiohttp, "ClientSession", Session)
    path, output = tmp_path / "collected.json", tmp_path / "scored.json"
    collected = asyncio.run(collection.collect(BLOCK_NUMBER, BLOCK_NUMBER, path))
    assert collected["transactions"] == 1
    loaded, preview = cli.preflight(path)
    assert preview["classifier_calls"] == 0 and calls == []
    assert isinstance(loaded["rows"][0]["state"], dict)
    args = Namespace(input=path, output=output, budget_usd=1, allow_paid=True,
                     acknowledge_unreviewed_questions=True)
    result = asyncio.run(cli.score(args))
    assert result["complete"] and result["flagged"] == 1 and len(calls) == 1
    assert json.loads(output.read_text())["rows"][0]["scores"]
    with pytest.raises(FileExistsError):
        asyncio.run(cli.score(args))
    assert len(calls) == 1
