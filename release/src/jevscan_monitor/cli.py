"""Explicit CLI; help, questions and stored results never make network requests."""

import argparse
import asyncio
import json
import sys
from pathlib import Path

from jevscan_monitor.evaluation import alerted, digest, load_detector, verify

DETECTOR_PATH = Path(__file__).resolve().parent / "data/detector.json"


def preflight(path: Path) -> tuple[dict, dict]:
    from jevscan_monitor.collection import load_collection
    from jevscan_monitor.provider import MAX_REQUEST_BYTES, RESERVED_TOKENS, USD_PER_MILLION_TOKENS, encode

    detector, collection = load_detector(DETECTOR_PATH), load_collection(path)
    for row in collection["rows"]:
        body = {"model": detector["model"], "state": row["state"], "questions": detector["questions"]}
        if len(encode(body)) > MAX_REQUEST_BYTES:
            raise ValueError("A transaction exceeds the request size limit; no scoring started")
    count = len(collection["rows"])
    return collection, {"transactions": count, "facts_version": collection["facts_version"],
                        "historical_baseline_facts_version": 10, "model": detector["model"],
                        "threshold": detector["threshold"], "question_review": detector["human_review"],
                        "maximum_new_request_reservations_usd": count * RESERVED_TOKENS * USD_PER_MILLION_TOKENS / 1e6,
                        "price_assumption_usd_per_million_input_tokens": USD_PER_MILLION_TOKENS,
                        "classifier_calls": 0}


async def score(args) -> dict:
    from jevscan_monitor.configuration import data_directory
    from jevscan_monitor.provider import Classifier, atomic_json

    if args.output.exists():
        raise FileExistsError("Refusing to overwrite score output")
    detector = load_detector(DETECTOR_PATH)
    if detector["human_review"] != "approved" and not args.acknowledge_unreviewed_questions:
        raise ValueError("Questions await human review; explicit acknowledgement is required")
    collection, _ = preflight(args.input)
    rows = []
    async with Classifier(data_directory() / "classifier", detector["model"], args.budget_usd,
                          allow_paid=args.allow_paid) as client:
        for row in collection["rows"]:
            answers = await client.classify(row["state"], detector["questions"], input_version=collection["facts_version"])
            rows.append({key: row[key] for key in ("transaction", "block", "index")} |
                        {"state_sha256": digest(row["state"]), "scores": answers,
                         "flagged": alerted(answers, detector)})
        result = {"schema": "jevscan-scores-v1", "complete": True, "collection_sha256": collection["content_sha256"],
                  "facts_version": collection["facts_version"], "model": detector["model"],
                  "question_sha256": detector["question_sha256"], "threshold": detector["threshold"],
                  "question_review": detector["human_review"], "rows": rows,
                  "new_requests": client.requests, "cache_hits": client.cache_hits, "billed_input_tokens": client.billed_tokens}
    atomic_json(args.output, result, overwrite=False)
    return {"transactions": len(rows), "flagged": sum(row["flagged"] for row in rows),
            "complete": True, "output": str(args.output), "facts_version": collection["facts_version"],
            "new_requests": result["new_requests"], "billed_input_tokens": result["billed_input_tokens"]}


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description="Research detector; never signs or submits transactions")
    sub = root.add_subparsers(dest="command", required=True)
    results = sub.add_parser("results", help="Recompute historical metrics offline from stored scores")
    results.add_argument("--evidence", type=Path, required=True)
    results.add_argument("--details", action="store_true")
    sub.add_parser("questions", help="Print exact questions and human-review status; no network")
    sub.add_parser("prepare", help="Collect public labels and finalized mixer index; RPC quota applies")
    collect = sub.add_parser("collect", help="Collect one to 20 finalized blocks; no classifier calls")
    collect.add_argument("--start-block", type=int, required=True)
    collect.add_argument("--end-block", type=int, required=True)
    collect.add_argument("--output", type=Path, required=True)
    preview = sub.add_parser("preflight", help="Validate a saved collection and estimate reservations offline")
    preview.add_argument("--input", type=Path, required=True)
    scoring = sub.add_parser("score", help="Classify a saved collection; paid calls need explicit consent")
    scoring.add_argument("--input", type=Path, required=True)
    scoring.add_argument("--output", type=Path, required=True)
    scoring.add_argument("--budget-usd", type=float, required=True, help="Cumulative workspace ceiling at documented assumed price")
    scoring.add_argument("--allow-paid", action="store_true")
    scoring.add_argument("--acknowledge-unreviewed-questions", action="store_true")
    return root


def main(argv=None) -> int:
    args = parser().parse_args(argv)
    try:
        if args.command == "results":
            result = verify(args.evidence)
            if not args.details:
                result = {key: result[key] for key in ("mode", "historical", "ordinary_observation", "limitations")}
        elif args.command == "questions":
            result = load_detector(DETECTOR_PATH)
        elif args.command == "preflight":
            _, result = preflight(args.input)
        elif args.command == "score":
            result = asyncio.run(score(args))
        else:
            from jevscan_monitor import collection
            result = asyncio.run(collection.prepare() if args.command == "prepare"
                                 else collection.collect(args.start_block, args.end_block, args.output))
        print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))
        return 0
    except (OSError, ValueError, RuntimeError, KeyError, TypeError, OverflowError, RecursionError) as error:
        # Decoder/filesystem errors can contain credentials or hostile text.
        # Never echo remote bodies or chained tracebacks to the terminal.
        print(f"Operation incomplete ({type(error).__name__}). No complete clean-result claim was produced. "
              "Check credentials, finalized-block support, input versions, output paths and budget. "
              "Paid scoring also requires explicit question-review acknowledgement.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
