import asyncio
import json
import sys

import pytest

from jevscan_monitor import provider

QUESTIONS = {"a": {"type": "noul", "instructions": "test"}, "b": {"type": "noul", "instructions": "test"}}


class Content:
    def __init__(self, payload):
        self.payload = payload

    async def iter_chunked(self, size):
        yield json.dumps(self.payload).encode()


class Response:
    status = 200

    def __init__(self, payload):
        self.content = Content(payload)

    async def __aenter__(self):
        await asyncio.sleep(0)
        return self

    async def __aexit__(self, *exc):
        pass


def payload(tokens=55000, score=.8):
    return {"model": "jev-1.13.0", "usage": {"input_tokens": tokens},
            "answers": {name: {"noul": score} for name in QUESTIONS}}


@pytest.fixture
def fake_provider(monkeypatch):
    calls = []

    class Session:
        def __init__(self, **kwargs):
            pass

        def post(self, url, **kwargs):
            calls.append(json.loads(kwargs["data"]))
            return Response(payload())

        async def close(self):
            pass

    monkeypatch.setenv("TYPESAFE_API_KEY", "synthetic-key-only")
    monkeypatch.setattr(provider.aiohttp, "ClientSession", Session)
    return calls


def test_concurrent_different_states_cannot_exceed_one_reservation(tmp_path, fake_provider):
    async def scenario():
        async with provider.Classifier(tmp_path, "jev-1.13.0", .00231, allow_paid=True) as client:
            results = await asyncio.gather(*(client.classify({"value": n}, QUESTIONS, input_version=13)
                                             for n in range(2)), return_exceptions=True)
            assert sum(isinstance(result, RuntimeError) for result in results) == 1
            assert provider.ledger_total(client.rows) <= .00231
    asyncio.run(scenario())
    assert len(fake_provider) == 1


def test_concurrent_identical_states_pay_once(tmp_path, fake_provider):
    async def scenario():
        async with provider.Classifier(tmp_path, "jev-1.13.0", .00231, allow_paid=True) as client:
            results = await asyncio.gather(*(client.classify({"value": 1}, QUESTIONS, input_version=13)
                                             for _ in range(2)))
            assert results[0] == results[1]
            assert client.cache_hits == 1
    asyncio.run(scenario())
    assert len(fake_provider) == 1


def test_paid_opt_in_is_required(tmp_path, fake_provider):
    async def scenario():
        async with provider.Classifier(tmp_path, "jev-1.13.0", 1) as client:
            with pytest.raises(RuntimeError, match="allow-paid"):
                await client.classify({}, QUESTIONS, input_version=13)
    asyncio.run(scenario())
    assert fake_provider == []


@pytest.mark.parametrize("score", [float("nan"), float("inf"), -.1, 1.1, True, "0.8", None])
def test_invalid_score_is_rejected(score):
    with pytest.raises(ValueError):
        provider.validate_response(payload(score=score), "jev-1.13.0", QUESTIONS)


def test_wrong_model_or_missing_answer_rejected():
    bad = payload()
    with pytest.raises(ValueError):
        provider.validate_response(bad, "jev-1.12.0", QUESTIONS)
    del bad["answers"]["b"]
    with pytest.raises(ValueError):
        provider.validate_response(bad, "jev-1.13.0", QUESTIONS)


def test_unresolved_reservation_counts_and_corrupt_ledger_fails():
    assert provider.ledger_total([{"kind": "reserve", "id": "x", "tokens": 55000}]) == .00231
    with pytest.raises(ValueError):
        provider.ledger_total([{"kind": "settle", "id": "x", "tokens": 0}])


def test_request_size_fails_before_spend(tmp_path, fake_provider):
    async def scenario():
        async with provider.Classifier(tmp_path, "jev-1.13.0", 1, allow_paid=True) as client:
            with pytest.raises(ValueError, match="size limit"):
                await client.classify({"text": "x" * 50000}, QUESTIONS, input_version=13)
            assert not client.rows
    asyncio.run(scenario())
    assert fake_provider == []


@pytest.mark.parametrize("bad", [{}, {"model": "other"}, {"model": "jev-1.13.0", "usage": {"input_tokens": 1},
    "answers": {"a": {"noul": float("nan")}, "b": {"noul": .1}}}])
def test_invalid_response_keeps_reservation_and_never_caches_answer(tmp_path, fake_provider, monkeypatch, bad):
    monkeypatch.setattr(sys.modules[__name__], "payload", lambda: bad)
    async def scenario():
        async with provider.Classifier(tmp_path, "jev-1.13.0", 1, allow_paid=True) as client:
            with pytest.raises(RuntimeError, match="Invalid classifier response"):
                await client.classify({}, QUESTIONS, input_version=13)
            assert len(client.rows) == 1 and client.rows[0]["kind"] == "reserve"
            assert provider.ledger_total(client.rows) == .00231
    asyncio.run(scenario())
    assert len(fake_provider) == 1
    assert not list((tmp_path / "answers").glob("*.json"))
