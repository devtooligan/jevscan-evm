"""Offline, deterministic arithmetic over the curated research evidence."""

import hashlib
import json
import math
import re
from pathlib import Path

HASH = re.compile(r"0x[0-9a-f]{64}")
FILES = {"detector.json", "incidents.json", "historical.jsonl", "ordinary-blocks.jsonl", "provenance.json"}
MAX_FILE_BYTES = 16 * 1024 * 1024


def read_bytes(path: Path) -> bytes:
    if path.is_symlink() or not path.is_file() or path.stat().st_size > MAX_FILE_BYTES:
        raise ValueError("Evidence file is missing, oversized, or a symbolic link")
    return path.read_bytes()


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def load_detector(path: Path) -> dict:
    detector = json.loads(read_bytes(path))
    if (detector.get("threshold") != .7 or detector.get("historical_facts_version") != 10
            or detector.get("model") != "jev-1.13.0" or detector.get("view") != "R2"):
        raise ValueError("Unsupported detector configuration")
    questions = detector.get("questions")
    if not isinstance(questions, dict) or len(questions) != 2:
        raise ValueError("Expected the two frozen detector questions")
    expected = {
        "c23_guided_lending_accounting_context": "0f0abd880284714756646d57285d5a8b0c94a2a021bda2a6214241bd3e2507cc",
        "p10_multi_pool_depletion": "60b489739ca1701dc54401044bd25d757f69e31c0ba21ceb7b9f441509901f87",
    }
    if {key: digest(value) for key, value in questions.items()} != expected or detector.get("question_sha256") != expected:
        raise ValueError("Question definitions differ from the reviewed historical bundle")
    return detector


def alerted(scores: dict, detector: dict) -> bool:
    if not isinstance(scores, dict) or set(scores) != set(detector["questions"]):
        raise ValueError("Incomplete detector scores")
    for score in scores.values():
        if type(score) not in (int, float) or not 0 <= score <= 1 or not math.isfinite(score):
            raise ValueError("Invalid detector score")
    return max(scores.values()) >= detector["threshold"]


def verify(directory: Path) -> dict:
    manifest = json.loads(read_bytes(directory / "manifest.json"))
    if not isinstance(manifest, dict) or set(manifest) != FILES:
        raise ValueError("Unexpected evidence manifest contents")
    for name, expected in manifest.items():
        if hashlib.sha256(read_bytes(directory / name)).hexdigest() != expected:
            raise ValueError("Evidence digest mismatch")
    detector = load_detector(directory / "detector.json")
    incidents = json.loads(read_bytes(directory / "incidents.json"))
    by_id = {}
    declared = {}
    for incident in incidents:
        identity = incident["id"]
        if identity in by_id or incident["chain_id"] != 1 or not incident["attack_txs"]:
            raise ValueError("Invalid incident manifest")
        by_id[identity] = incident
        for tx in incident["attack_txs"]:
            if not HASH.fullmatch(tx) or tx in declared:
                raise ValueError("Invalid or duplicate declared attack")
            declared[tx] = identity
    hits = {identity: [] for identity in by_id}
    seen = set()
    peers = 0
    potential_false_positives = []
    for line in read_bytes(directory / "historical.jsonl").splitlines():
        row = json.loads(line)
        tx, incident = row["transaction"], row["incident"]
        if not HASH.fullmatch(tx) or tx in seen or incident not in by_id or type(row["declared_attack"]) is not bool:
            raise ValueError("Invalid historical transaction row")
        seen.add(tx)
        if row["declared_attack"] != (tx in declared) or (tx in declared and declared[tx] != incident):
            raise ValueError("Historical attack labels disagree with the incident manifest")
        alert = alerted(row["scores"], detector)
        if tx in declared:
            hits[incident].append({"transaction": tx, "flagged": alert})
        else:
            peers += 1
            if alert:
                potential_false_positives.append({"transaction": tx, "incident_block": incident})
    if not set(declared) <= seen:
        raise ValueError("Missing declared attack transaction results")
    controls, blocks, control_alerts = set(), set(), 0
    for line in read_bytes(directory / "ordinary-blocks.jsonl").splitlines():
        row = json.loads(line)
        tx = row["transaction"]
        if not HASH.fullmatch(tx) or tx in controls or tx in seen:
            raise ValueError("Invalid, duplicate, or overlapping ordinary-sample transaction")
        if type(row["block"]) is not int or row["block"] < 0:
            raise ValueError("Invalid control block")
        controls.add(tx)
        blocks.add(row["block"])
        control_alerts += alerted(row["scores"], detector)
    per_incident = [{"id": identity, "name": item["name"], "declared": len(item["attack_txs"]),
                     "flagged": sum(tx["flagged"] for tx in hits[identity]), "transactions": hits[identity]}
                    for identity, item in by_id.items()]
    return {
        "mode": "offline arithmetic replay; no new classification or network requests",
        "historical": {"incidents": len(incidents), "incidents_with_any_attack_flagged": sum(any(tx["flagged"] for tx in group) for group in hits.values()),
                       "incidents_with_every_declared_attack_flagged": sum(all(tx["flagged"] for tx in group) for group in hits.values()),
                       "declared_attack_transactions": len(declared), "flagged_attack_transactions": sum(row["flagged"] for group in hits.values() for row in group),
                       "other_transactions": peers, "potential_false_positives": len(potential_false_positives)},
        "ordinary_observation": {"blocks": len(blocks), "transactions": len(controls), "alerts": control_alerts},
        "per_incident": per_incident, "potential_false_positive_transactions": potential_false_positives,
        "limitations": ["Historical cohort was used during calibration.",
                        "Other transactions are not all verified benign.",
                        "Stored-score replay does not reproduce original provider inference.",
                        "Modified extraction has not inherited historical coverage measurements."],
    }
