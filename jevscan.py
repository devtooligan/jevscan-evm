"""jevscan: ask TypeSafe's Jev classifier, per source file, which vulnerability classes are present.

Usage:
    python jevscan.py <repo_path> [--config jevscan.toml] [--out out/<repo>]
Settings live in the config file (every key and its default: jevscan.toml). Needs TYPESAFE_API_KEY
(from the environment or .env).

Every question has an id `<level>:<name>`, where level is broad, category, subcategory, or detector.
"""

import argparse
import asyncio
import fnmatch
import json
import re
import time
from pathlib import Path

from config import load_config, load_dotenv, resolve_paths
from functions import contract_context, mask, split_functions
from jev import Jev, cost_usd, est_tokens
from report import write_outputs

HERE = Path(__file__).resolve().parent
TAXONOMY = HERE / "sources" / "taxonomy.json"
DETECTOR_MAP = HERE / "sources" / "detector_map.json"
MAX_FILE_TOKENS = 30_000  # estimated; about 26k real tokens, under Jev's 32k state + longest question
FILE_SUBJECT = "The source file in `source`"
FUNCTION_SUBJECT = "The function in `function` (with its contract's declarations in `contract_context`)"
LINE_SUBJECT = "The function in `function` (each line prefixed with its file line number)"
EXAMPLES = " It is true when the {unit} matches the description above; the following are examples of code that makes it true: "
HEAD_LINES = 60
MAX_LINE_OPTIONS = 60
REPO_MAX_TOKENS = 28_000
REPO_SUBJECT = "The codebase in the state (each state field is one source file, keyed by its relative path)"

BROAD_QUESTIONS = {
    "broad:any_bug": "The source file in `source` contains at least one exploitable security vulnerability "
    "(not a gas, style, or informational issue).",
    "broad:critical_bug": "The source file in `source` contains a vulnerability that lets an attacker gain value "
    "at the expense of the protocol or its users — by stealing or permanently locking funds, or by exploiting "
    "mispricing, wrong accounting, or missing checks to extract value.",
}
FILE_KIND_QUESTION = "The role in the codebase of the file whose relative path is `path` and whose first lines are `head`."


def with_examples(question: str, examples: list[str]) -> str:
    return question + EXAMPLES.format(unit="file") + "; ".join(examples)


def load_library(detectors_dir: Path, taxonomy_path: Path, map_path: Path,
                 levels: dict[str, bool], sources: dict[str, bool]) -> dict:
    """The questions of the levels turned on (detectors only from the sources turned on; both tables as in the
    config), every question's one-line description, each detector's source, and the full taxonomy tree
    (category -> subcategories, subcategory -> mapped detectors of the sources turned on)."""
    lib = {"broad": dict(BROAD_QUESTIONS), "category": {}, "subcategory": {}, "detector": {}, "children": {},
           "source": {}}
    lib["descriptions"] = {q: q.split(":")[1] for q in BROAD_QUESTIONS}
    for c in json.loads(taxonomy_path.read_text())["categories"]:
        cid = f"category:{c['id']}"
        lib["category"][cid] = c["question"]
        lib["descriptions"][cid] = c["name"]
        lib["children"][cid] = []
        for s in c["subcategories"]:
            sid = f"subcategory:{s['id']}"
            lib["subcategory"][sid] = with_examples(s["question"], s["code_patterns"])
            lib["descriptions"][sid] = s["description"]
            lib["children"][cid].append(sid)
            lib["children"][sid] = []
    for p in sorted(detectors_dir.glob("*.json")):
        d = json.loads(p.read_text())
        did = f"detector:{d['name']}"
        lib["detector"][did] = with_examples(d["question"], d["criteria"])
        lib["descriptions"][did] = d["description"]
        if d["source"] not in sources:
            raise SystemExit(f"{p}: source {d['source']!r} is not in the config's [sources] table")
        lib["source"][did] = d["source"]
    if not lib["detector"]:
        raise SystemExit(f"no detectors found in {detectors_dir}")
    for name, subs in json.loads(map_path.read_text()).items():
        if f"detector:{name}" not in lib["detector"]:
            raise SystemExit(f"{map_path}: unknown detector {name}")
        if sources[lib["source"][f"detector:{name}"]]:
            for sub in subs:
                lib["children"][f"subcategory:{sub}"].append(f"detector:{name}")
    lib["detector"] = {d: text for d, text in lib["detector"].items() if sources[lib["source"][d]]}
    for level, on in levels.items():
        if not on:
            lib[level] = {}
    lib["text"] = lib["broad"] | lib["category"] | lib["subcategory"] | lib["detector"]
    return lib



def run_library(run: dict) -> dict:
    """The library a saved run (results.json) was asked with, from the settings recorded in it."""
    cfg = run["config"]
    return load_library(resolve_paths(cfg)["detectors_dir"], TAXONOMY, DETECTOR_MAP,
                        cfg["levels"], cfg["sources"])


def find_files(repo: Path, files_cfg: dict) -> tuple[Path, list[Path]]:
    """The scan root and the candidate files. An explicit files.paths list is taken as is, relative to the repo
    root; otherwise every file with one of the extensions under files.scope, minus anything under skip_dirs
    (typically vendored code), and the Jev file classification decides the rest."""
    if files_cfg["paths"]:
        files = [repo / p for p in files_cfg["paths"]]
        missing = [p for p, f in zip(files_cfg["paths"], files) if not f.is_file()]
        if missing:
            raise SystemExit(f"files.paths: not a file under {repo}: {', '.join(missing)}")
        return repo, files
    root = repo / files_cfg["scope"]
    skipped = [repo / d for d in files_cfg["skip_dirs"]]
    return root, sorted(p for p in root.rglob("*") if p.is_file() and p.suffix in files_cfg["extensions"]
                        and not any(p.is_relative_to(d) for d in skipped))


async def classify_file(jev: Jev, classes: dict[str, str], path: str, source: str) -> dict:
    head = "\n".join(source.split("\n")[:HEAD_LINES])
    answer = await jev.choose({"path": path, "head": head}, FILE_KIND_QUESTION, classes)
    return {"path": path, "kind": answer["choice"], "confidence": answer["confidence"]}


async def scan_file(jev: Jev, lib: dict, path: str, source: str) -> dict:
    """Every question about one file. Each level gets its own requests; usage is {level: {requests, tokens}}."""
    state = {"source": source}
    usage: dict[str, dict] = {}
    groups = {"category": lib["broad"] | lib["category"], "subcategory": lib["subcategory"], "detector": lib["detector"]}
    groups = {g: qs for g, qs in groups.items() if qs}
    parts = await asyncio.gather(*(jev.ask(state, qs, usage.setdefault(g, {})) for g, qs in groups.items()))
    answers = {k: v for part in parts for k, v in part.items()}
    critical = f", critical={answers['broad:critical_bug']:.2f}" if "broad:critical_bug" in answers else ""
    print(f"  {path}: {len(answers)} questions{critical}")
    return {"path": path, "tokens": est_tokens(json.dumps(state)), "lines": sum(bool(line.strip()) for line in source.split("\n")),
            "questions": answers, "usage": usage}


def reword(text: str, subject: str, unit: str) -> str:
    """A file-level question about another unit: swap the subject and every "the file" in the body, so the
    question only names fields the request's state contains."""
    if not text.startswith(FILE_SUBJECT):
        raise ValueError(f"question does not start with {FILE_SUBJECT!r}: {text[:80]}")
    body = re.sub(r"\b([Tt])he file\b", lambda m: f"{m.group(1)}he {unit}", text[len(FILE_SUBJECT) :])
    return subject + body


def function_question(text: str) -> str:
    return reword(text, FUNCTION_SUBJECT, "function")


def numbered_lines(function: dict) -> tuple[str, dict[str, str]]:
    """The function text with each line prefixed `L<n>: ` (file line numbers), and the choice options:
    {"L<n>": first 60 chars} for every line that is not blank or comment-only. Lines are split on "\n" only,
    as in functions.py, so the numbers match the file."""
    lines = function["text"].split("\n")
    code = mask(function["text"], strings=False).split("\n")
    numbers = range(function["start_line"], function["start_line"] + len(lines))
    text = "\n".join(f"L{n}: {line}" for n, line in zip(numbers, lines))
    options = {f"L{n}": line.strip()[:60] for n, line, c in zip(numbers, lines, code) if c.strip()}
    return text, options


async def locate_lines(jev: Jev, lib: dict, function: dict, questions: list[str]) -> dict[str, dict]:
    """Experimental: for each question, a Choice of the function's primary vulnerable line."""
    text, options = numbered_lines(function)
    if not questions or len(options) > MAX_LINE_OPTIONS:
        return {}
    asked = {
        q: {"type": "choice", "criteria": options,
            "instructions": "Which line is the primary vulnerable statement for: "
                            + reword(lib["text"][q], LINE_SUBJECT, "function")}
        for q in questions
    }
    answers = await jev.ask_objects({"function": text}, asked)
    return {q: {"choice": a["choice"], "confidence": a["confidence"], "probabilities": a["probabilities"]}
            for q, a in answers.items()}


async def locate_function(jev: Jev, lib: dict, context: str, function: dict, flagged: dict[str, str],
                          threshold: float) -> tuple[dict[str, float], dict[str, dict]]:
    scores = await jev.ask({"contract_context": context, "function": function["text"]}, flagged)
    hot = [q for q, p in scores.items() if p >= threshold]
    return scores, await locate_lines(jev, lib, function, hot)


async def locate_file(jev: Jev, lib: dict, source: str, result: dict, threshold: float) -> dict:
    """Re-ask every non-broad question whose file-level P is at least `threshold` once per function, then
    (experimental) pick the vulnerable line where the function-level P reaches it too.
    Returns {question_id: [{name, start_line, end_line, p, line?}] sorted by p}."""
    flagged = {
        q: function_question(lib["text"][q])
        for q, p in result["questions"].items()
        if not q.startswith("broad:") and p >= threshold
    }
    units = split_functions(source)
    functions = [f for f in units if f["kind"] != "modifier"]
    if not flagged or not functions:
        return {}
    context = contract_context(source, units)
    answers = await asyncio.gather(
        *(locate_function(jev, lib, context, f, flagged, threshold) for f in functions)
    )
    located = {}
    for q in flagged:
        rows = []
        for f, (scores, lines) in zip(functions, answers):
            row = {"name": f["name"], "start_line": f["start_line"], "end_line": f["end_line"], "p": scores[q]}
            if q in lines:
                row["line"] = lines[q]
            rows.append(row)
        located[q] = sorted(rows, key=lambda row: -row["p"])
    return located


async def ask_repo(jev: Jev, lib: dict, state: dict[str, str]) -> dict:
    """Repo-level broad and category questions over every scanned file ({path: source}) in one state, if it fits."""
    tokens = est_tokens(json.dumps(state))
    if tokens > REPO_MAX_TOKENS:
        return {"fits": False, "tokens": tokens}
    questions = {q: reword(lib["text"][q], REPO_SUBJECT, "codebase") for q in lib["broad"] | lib["category"]}
    answers, suspicious = await asyncio.gather(
        jev.ask(state, questions),
        jev.choose(state, "Which file most likely contains the most severe vulnerability",
                   {path: f"the file {path}" for path in state}),
    )
    return {"fits": True, "tokens": tokens, "questions": answers, "most_suspicious_file": suspicious["choice"],
            "most_suspicious_probabilities": suspicious["probabilities"]}


def phase_stats(jev: Jev, before: dict, start: float) -> dict:
    stats = {k: jev.stats[k] - before[k] for k in jev.stats}
    return stats | {"cost_usd": cost_usd(stats["tokens"]), "billed_usd": cost_usd(stats["billed_tokens"]),
                    "wall_s": round(time.monotonic() - start, 2)}


async def run(repo: Path, cfg: dict, out_dir: Path) -> None:
    files_cfg, classes = cfg["files"], cfg["classes"]
    explicit = bool(files_cfg["paths"])
    paths = resolve_paths(cfg)
    lib = load_library(paths["detectors_dir"], TAXONOMY, DETECTOR_MAP,
                       cfg["levels"], cfg["sources"])
    root, files = find_files(repo, files_cfg)
    if not files:
        raise SystemExit(f"no files with extensions {files_cfg['extensions']} under {root}")

    sources = {str(f.relative_to(root)): f.read_text() for f in files}
    out_dir.mkdir(parents=True, exist_ok=True)
    out = {"project": repo.name, "root": str(root.relative_to(repo.parent)), "config": cfg, "stats": {},
           "classification": [], "files": [], "skipped": [], "not_located": []}
    start = time.monotonic()
    async with Jev(paths["cache_dir"], cfg["run"]["concurrency"]) as jev:
        out["model"] = jev.model
        out["stats"]["model_probe"] = phase_stats(jev, dict.fromkeys(jev.stats, 0), start)
        if explicit:
            out["classification"] = [{"path": p, "kind": "source", "confidence": 1.0} for p in sources]
        else:
            start, before = time.monotonic(), dict(jev.stats)
            out["classification"] = list(await asyncio.gather(
                *(classify_file(jev, classes["descriptions"], p, s) for p, s in sources.items())))
            out["stats"]["classify"] = phase_stats(jev, before, start)
        to_scan = []
        for c in out["classification"]:
            tokens = est_tokens(json.dumps({"source": sources[c["path"]]}))
            scanned_class = explicit or c["kind"] in classes["scan"]
            c["forced"] = not scanned_class and any(fnmatch.fnmatch(c["path"], g) for g in files_cfg["include_globs"])
            if not scanned_class and not c["forced"]:
                print(f"not scanning {c['path']}: classified {c['kind']} ({c['confidence']:.2f}); "
                      "add a files.include_globs pattern to scan it anyway")
            elif tokens > MAX_FILE_TOKENS:
                print(f"WARNING: skipping {c['path']} (~{tokens:,} tokens > {MAX_FILE_TOKENS:,})")
                out["skipped"].append({"path": c["path"], "tokens": tokens})
            else:
                to_scan.append(c["path"])
                if c["forced"]:
                    print(f"scanning {c['path']} although classified {c['kind']} ({c['confidence']:.2f}): "
                          "files.include_globs")
        if not to_scan:
            raise SystemExit(f"no files to scan under {root}: every candidate was in a class outside classes.scan "
                             "or skipped for size (see above); add files.include_globs patterns to force files in")
        print(f"Scanning {len(to_scan)} of {len(files)} files with {jev.model}")

        start, before = time.monotonic(), dict(jev.stats)
        out["files"] = list(await asyncio.gather(*(scan_file(jev, lib, p, sources[p]) for p in to_scan)))
        out["stats"]["scan"] = phase_stats(jev, before, start)
        # Written now so a failure in a later phase cannot lose the scan.
        (out_dir / "results.json").write_text(json.dumps(out, indent=2) + "\n")
        if cfg["run"]["locate"]:
            start, before = time.monotonic(), dict(jev.stats)
            # The function splitter handles Solidity only.
            solidity = [r for r in out["files"] if r["path"].endswith(".sol")]
            out["not_located"] = [r["path"] for r in out["files"] if not r["path"].endswith(".sol")]
            for path in out["not_located"]:
                print(f"not locating {path}: the function splitter handles Solidity only")
            located = await asyncio.gather(*(locate_file(jev, lib, sources[r["path"]], r, cfg["thresholds"]["locate"])
                                             for r in solidity))
            for r, loc in zip(solidity, located):
                r["located"] = loc
            out["stats"]["locate"] = phase_stats(jev, before, start)
        if cfg["run"]["repo_level"]:
            start, before = time.monotonic(), dict(jev.stats)
            out["repo"] = await ask_repo(jev, lib, {p: sources[p] for p in to_scan})
            out["stats"]["repo"] = phase_stats(jev, before, start)

    (out_dir / "results.json").write_text(json.dumps(out, indent=2) + "\n")
    write_outputs(out, lib, out_dir)
    for phase, s in out["stats"].items():
        print(f"{phase}: {s['requests']} requests ({s['cache_hits']} cached), {s['tokens']:,} tokens, "
              f"${s['cost_usd']:.4f} (billed ${s['billed_usd']:.4f}), {s['wall_s']}s")
    print(f"Outputs in {out_dir}: HEATMAP.md, report.md, findings.json, jevheatmap.json, results.json")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("repo_path")
    parser.add_argument("--config", type=Path, help="TOML settings laid over jevscan.toml")
    parser.add_argument("--out", type=Path, help="output directory (default <paths.out_dir>/<repo name>)")
    args = parser.parse_args()
    load_dotenv()
    repo = Path(args.repo_path).resolve()
    cfg = load_config(args.config)
    asyncio.run(run(repo, cfg, args.out or resolve_paths(cfg)["out_dir"] / repo.name))


if __name__ == "__main__":
    main()
