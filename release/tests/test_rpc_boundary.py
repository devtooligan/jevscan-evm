import json
import asyncio

import pytest

from jevscan_monitor.rpc import DiskCache, http_payload, rpc_envelope, cancel_inflight


@pytest.mark.parametrize("body", [
    [], {"jsonrpc": "2.0", "id": 2, "result": 1}, {"jsonrpc": "2.0", "id": True, "result": 1},
    {"jsonrpc": "2.0", "id": 1, "result": 1, "error": None},
    {"jsonrpc": "2.0", "id": 1, "error": "bad"}, {"id": 1, "result": 1},
    {"jsonrpc": "2.0", "id": 1, "error": {"code": True, "message": "bad"}},
])
def test_malformed_rpc_envelope_rejected(body):
    with pytest.raises(RuntimeError):
        rpc_envelope(json.dumps(body))


def test_valid_rpc_result_and_error():
    assert rpc_envelope('{"jsonrpc":"2.0","id":1,"result":null}')["result"] is None
    assert rpc_envelope('{"jsonrpc":"2.0","id":1,"error":{"code":3,"message":"reverted"}}')["error"]["code"] == 3


@pytest.mark.parametrize("body", ["<html>maintenance</html>", '{"status":"0","message":"NOTOK","result":"invalid key"}'])
def test_invalid_http_success_cannot_be_cached(body):
    with pytest.raises(RuntimeError):
        http_payload("etherscan", body)


def test_escaped_secret_echo_is_rejected_before_cache(tmp_path, monkeypatch):
    sentinel = "SYNTHETIC_CREDENTIAL_DO_NOT_PERSIST"
    monkeypatch.setenv("TYPESAFE_API_KEY", sentinel)
    escaped = "".join("\\u%04x" % ord(character) for character in sentinel)
    body = '{"echo":"' + escaped + '"}'
    with pytest.raises(RuntimeError, match="credential"):
        DiskCache(tmp_path).write("test", {}, body)
    assert not list(tmp_path.rglob("*.json"))


def test_cache_namespace_cannot_escape_root(tmp_path):
    with pytest.raises(ValueError):
        DiskCache(tmp_path).write("../escape", {}, "{}")
    with pytest.raises(ValueError):
        list(DiskCache(tmp_path).entries("../escape"))


def test_inflight_work_is_cancelled_and_joined_on_shutdown():
    async def scenario():
        task = asyncio.create_task(asyncio.sleep(3600))
        tasks = {"key": task}
        await cancel_inflight(tasks)
        assert task.cancelled() and tasks == {}
    asyncio.run(scenario())
