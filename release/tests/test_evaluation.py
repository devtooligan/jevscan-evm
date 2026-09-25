from pathlib import Path

import pytest

from jevscan_monitor.evaluation import alerted, load_detector, verify

EVIDENCE = Path(__file__).resolve().parents[1] / "evidence"


def test_frozen_results_reproduce_exactly_offline():
    report = verify(EVIDENCE)
    assert report["historical"] == {
        "incidents": 50, "incidents_with_any_attack_flagged": 42,
        "incidents_with_every_declared_attack_flagged": 35,
        "declared_attack_transactions": 70, "flagged_attack_transactions": 55,
        "other_transactions": 12947, "potential_false_positives": 5,
    }
    assert report["ordinary_observation"] == {"blocks": 20, "transactions": 5420, "alerts": 0}


@pytest.mark.parametrize("value", [True, float("nan"), -1, 1.1, "0.7"])
def test_malformed_scores_never_count_as_clean(value):
    detector = load_detector(EVIDENCE / "detector.json")
    with pytest.raises(ValueError):
        alerted(dict.fromkeys(detector["questions"], value), detector)
