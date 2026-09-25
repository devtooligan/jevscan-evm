import json
from pathlib import Path

from jevscan_monitor import cli


def test_results_are_offline_and_do_not_need_credentials(monkeypatch, capsys):
    for name in ("TYPESAFE_API_KEY", "MAINNET_RPC_URL", "ETHERSCAN_API_KEY"):
        monkeypatch.delenv(name, raising=False)
    assert cli.main(["results", "--evidence", str(Path(__file__).resolve().parents[1] / "evidence")]) == 0
    assert json.loads(capsys.readouterr().out)["historical"]["flagged_attack_transactions"] == 55


def test_question_command_prints_pending_exact_bundle(capsys):
    assert cli.main(["questions"]) == 0
    value = json.loads(capsys.readouterr().out)
    assert value["human_review"] == "pending"
    assert len(value["questions"]) == 2


def test_failure_does_not_echo_private_exception_text(monkeypatch, capsys):
    def failure(*args):
        raise ValueError("PRIVATE_SENTINEL_SHOULD_NOT_PRINT")
    monkeypatch.setattr(cli, "verify", failure)
    assert cli.main(["results", "--evidence", "missing"]) == 1
    output = capsys.readouterr()
    assert "PRIVATE_SENTINEL" not in output.out + output.err
    assert "Operation incomplete" in output.err
