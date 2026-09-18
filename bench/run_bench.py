"""Benchmark jevscan against a contest's answer key.

    python bench/run_bench.py ussd            # run one full pass with locating, then score it
    python bench/run_bench.py ussd --score    # score the saved run only

Benchmarks: ussd (Sherlock 2023-05, 22 H/M), beedle (CodeHawks 2023-07, 41 H/M), monolith (Sherlock 2025-12,
7 H/M; scanned with bench/monolith/jevscan.toml, the contest's scope list). Writes
bench/<name>/run/ (the scan's outputs; HEATMAP.md gets the answer key and is the only one committed) and
bench/<name>/results.md (ending with bench/<name>/notes.md, the hand-written part, when it exists). A fresh
clone has no saved run, so the first call scans; answers are cached after that.
Every resolution is scored on the same full run.
Needs TYPESAFE_API_KEY and BENCH_REPOS (the directory holding the contest checkouts, laid out as in
BENCHES) unless --score is given.
"""

import argparse
import json
import math
import os
import statistics
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
JEVSCAN = HERE.parent
sys.path.insert(0, str(JEVSCAN))
from jev import cost_usd  # noqa: E402
from jevscan import run_library  # noqa: E402
from heatmap import FLAG_THRESHOLDS, category_flags, grid_files, render_heatmap_md, strongest_hits  # noqa: E402
from report import build_heatmap, likely_issues  # noqa: E402

BENCHES = {
    "ussd": {"title": "Sherlock USSD (2023-05)", "repo": "2023-05-USSD/ussd-contracts", "scope": "contracts",
             "url": "https://github.com/sherlock-audit/2023-05-USSD"},
    "beedle": {"title": "CodeHawks Beedle (2023-07)", "repo": "beedle", "scope": "",
               "url": "https://github.com/Cyfrin/2023-07-beedle"},
    "monolith": {"title": "Sherlock Monolith Stablecoin Factory (2025-12)",
                 "repo": "2025-12-monolith-stablecoin-factory/Monolith", "scope": "",
                 "url": "https://github.com/sherlock-audit/2025-12-monolith-stablecoin-factory",
                 "config": HERE / "monolith" / "jevscan.toml",
                 # Notes on unmatched category flags, keyed by file or by category.
                 "flag_notes": {
                     "src/Lens.sol": "Lens.sol re-implements Lender.sol's debt and collateral views, so this may echo "
                                     "the Lender math",
                     "external_call_token_integration": "the contest excluded fee-on-transfer and rebasing tokens; "
                                                        "flags resting on those are likely false positives",
                 }},
}
THRESHOLDS = (0.3, 0.5, 0.7)
HIT = 0.5  # threshold for the hit/miss marks in the per-issue table
LEVELS = ("category", "subcategory", "detector")


def resolutions(run: dict) -> list[str]:
    """The question levels the run asked, in scoring order."""
    return [level for level in LEVELS if run["config"]["levels"][level]]


def bench_root(bench: dict) -> Path:
    """The directory jevscan scans: the contest checkout under $BENCH_REPOS, plus the bench's scope."""
    if "BENCH_REPOS" not in os.environ:
        raise SystemExit("set BENCH_REPOS to the directory holding the contest checkouts (see BENCHES for the layout)")
    return Path(os.environ["BENCH_REPOS"]) / bench["repo"] / bench["scope"]


def run_scan(bench: dict, out: Path) -> None:
    cmd = [sys.executable, str(JEVSCAN / "jevscan.py"), str(bench_root(bench)), "--out", str(out)]
    if "config" in bench:
        cmd += ["--config", str(bench["config"])]
    subprocess.run(cmd, check=True)


def targets(issue: dict, resolution: str, lib: dict) -> set[str] | None:
    """Question ids that count as detecting `issue` at this resolution; None if not applicable."""
    sub = issue["subcategory_id"]
    if resolution == "category":
        return {f"category:{issue['category_id']}"}
    if sub is None:
        return None
    if resolution == "subcategory":
        return {f"subcategory:{sub}"}
    return set(lib["children"][f"subcategory:{sub}"]) or None


def pairs(run: dict, resolution: str) -> dict[tuple[str, str], float]:
    """Every asked (file, question) pair at one resolution."""
    return {
        (r["path"], q): p for r in run["files"] for q, p in r["questions"].items() if q.startswith(resolution + ":")
    }


def best_true(issue: dict, qids: set[str], asked: dict) -> tuple[float, str | None]:
    """Highest p among the issue's true (file, question) pairs; 0 if none were asked."""
    found = [(asked[(f, q)], q) for f in issue["files"] for q in qids if (f, q) in asked]
    return max(found) if found else (0.0, None)


def rank(p: float, asked: dict) -> int:
    return 1 + sum(v > p for v in asked.values())


def fmt(p: float) -> str:
    return f"**{p:.2f}**" if p >= HIT else f"{p:.2f}"


def recall_table(run: dict, gt: list[dict], lib: dict) -> list[str]:
    lines = ["| Resolution | Issues scored | Recall@0.3 | Recall@0.5 | Recall@0.7 | Median rank of true pair "
             "| Pairs asked |", "|---|---|---|---|---|---|---|"]
    for res in resolutions(run):
        asked = pairs(run, res)
        scored = [(i, t) for i in gt if (t := targets(i, res, lib))]
        found = [best_true(i, t, asked) for i, t in scored]
        best = [p for p, _ in found]
        recalls = [f"{sum(b >= th for b in best)}/{len(best)} ({sum(b >= th for b in best) / len(best):.0%})"
                   for th in THRESHOLDS]
        med = statistics.median(rank(p, asked) for p, q in found if q)
        lines.append(f"| {res} | {len(best)} | {' | '.join(recalls)} | {med} | {len(asked)} |")
    levels = resolutions(run)
    distinct = {res: len({(f, q) for i in gt for q in (targets(i, res, lib) or ()) for f in i["files"]})
                for res in levels}
    scored = {res: [i for i in gt if targets(i, res, lib)] for res in levels}
    per_issue = {res: statistics.mean(len(targets(i, res, lib)) * len(i["files"]) for i in scored[res])
                 for res in levels}
    lines += ["", "Recall is generous: an issue counts as found when any of its true pairs passes, and several issues "
              "share one (file, question) pair, so one flag can count for many issues. Distinct true pairs vs issues "
              "scored: " + ", ".join(f"{res} {distinct[res]} for {len(scored[res])}" for res in levels)
              + ". True pairs per scored issue (questions x files), mean: "
              + ", ".join(f"{res} {per_issue[res]:.1f}" for res in levels)
              + ". At detector resolution that is every detector mapped to the issue's subcategory, in every issue "
              "file."]
    return lines


def issue_counts(gt: list[dict]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for i in gt:
        for f in i["files"]:
            counts[f] = counts.get(f, 0) + 1
    return counts


def broad_table(run: dict, gt: list[dict], lib: dict) -> list[str]:
    """any_bug / critical_bug per file."""
    counts = issue_counts(gt)
    items = likely_issues(run)
    lines = ["| File | H/M issues | any_bug | critical_bug | Likely issues listed |", "|---|---|---|---|---|"]
    results = sorted(run["files"], key=lambda r: (-counts.get(r["path"], 0), r["path"]))
    for r in results:
        q = r["questions"]
        listed = sum(i["file"] == r["path"] for i in items)
        lines.append(f"| `{r['path']}` | {counts.get(r['path'], 0)} | {q['broad:any_bug']:.2f} | "
                     f"{q['broad:critical_bug']:.2f} | {listed} |")
    lines.append("")
    series = {"any_bug": {r["path"]: r["questions"]["broad:any_bug"] for r in results},
              "critical_bug": {r["path"]: r["questions"]["broad:critical_bug"] for r in results}}
    for label, values in series.items():
        buggy = [p for f, p in values.items() if counts.get(f)]
        clean = [p for f, p in values.items() if not counts.get(f)]
        means = [f"{statistics.mean(v):.2f}" if v else "n/a (no such file)" for v in (buggy, clean)]
        lines.append(f"- {label}: mean {means[0]} on files with issues, {means[1]} on files without")
    return lines


def true_pairs(gt: list[dict], lib: dict) -> set[tuple[str, str]]:
    return {(f, q) for i in gt for res in LEVELS for q in (targets(i, res, lib) or ()) for f in i["files"]}


def fp_table(run: dict, gt: list[dict], lib: dict) -> list[str]:
    buggy = {f for i in gt for f in i["files"]}
    truth = true_pairs(gt, lib)
    clean_files = {r["path"] for r in run["files"]} - buggy
    lines = [f"Files with no issue ({len(clean_files)}): " + ", ".join(f"`{f}`" for f in sorted(clean_files)), "",
             "| Resolution | Threshold | Flags | True flags | Flags on files with no issue |",
             "|---|---|---|---|---|"]
    for res in resolutions(run):
        asked = pairs(run, res)
        for th in THRESHOLDS:
            flags = [k for k, p in asked.items() if p >= th]
            lines.append(f"| {res} | {th} | {len(flags)} | {sum(k in truth for k in flags)} "
                         f"| {sum(k[0] in clean_files for k in flags)} |")
    return lines


def flags_table(heatmap: dict, key: list[dict], notes: dict[str, str]) -> list[str]:
    """Category flags with and without a known finding of that category in that file."""
    lines = ["A flag is a (file, category) pair whose file-level p is at or over the threshold. It is matched when the "
             "ground truth has a finding in that file with that category.", "",
             "| Threshold | Flags | Matched | Unmatched | Unmatched share |", "|---|---|---|---|---|"]
    for th in sorted(FLAG_THRESHOLDS):
        flags = category_flags(heatmap, key, th)
        unmatched = sum(not matched for *_, matched in flags)
        lines.append(f"| {th} | {len(flags)} | {len(flags) - unmatched} | {unmatched} | {unmatched / len(flags):.0%} |")
    low = min(FLAG_THRESHOLDS)
    lines += ["", f"Unmatched flags at {low} (possibly unreported, or a false positive — not verified):", "",
              "| File | Category | p | Note |", "|---|---|---|---|"]
    lines += [f"| `{f}` | {c} | {p:.2f} | {notes.get(f) or notes.get(c, '')} |"
              for f, c, p, matched in category_flags(heatmap, key, low) if not matched]
    return lines


def chance(n: int, k: int, top: int) -> float:
    """Chance that a uniformly random order of n functions puts one of k true ones in the first `top`."""
    return 1 - math.comb(n - k, top) / math.comb(n, top) if n >= top else float(k > 0)


def scored_pair(issue: dict, qids: set[str], run: dict) -> tuple[str, str] | None:
    """The one (file, question) an issue's locating is scored on: its true pair with the highest file-level
    p. The choice uses only file-level answers, never the function ranking, so one ranking is scored per issue."""
    by_path = {r["path"]: r for r in run["files"]}
    found = [(by_path[f]["questions"][q], f, q) for f in issue["files"] if f in by_path for q in sorted(qids)]
    return max(found)[1:] if found else None


def locating(issue: dict, qids: set[str] | None, run: dict) -> tuple[str, float, float]:
    """('top1' / 'top3' / 'miss', random top-1 chance, random top-3 chance) on the issue's scored pair, or
    (why it could not be scored, 0, 0). The random chances use the same ranking: its n functions, k of them
    the issue's."""
    if not issue["functions"]:
        return "no function", 0.0, 0.0
    if not qids:
        return "n/a", 0.0, 0.0
    pair = scored_pair(issue, qids, run)
    rows = pair and next(r for r in run["files"] if r["path"] == pair[0]).get("located", {}).get(pair[1])
    if not rows:
        return "not located", 0.0, 0.0
    pos = next((n for n, row in enumerate(rows) if row["name"] in issue["functions"]), len(rows))
    n, k = len(rows), sum(row["name"] in issue["functions"] for row in rows)
    return "top1" if pos == 0 else "top3" if pos < 3 else "miss", chance(n, k, 1), chance(n, k, 3)


def locating_table(run: dict, gt: list[dict], lib: dict) -> tuple[list[str], dict]:
    per_issue = {i["id"]: {res: locating(i, targets(i, res, lib), run) for res in resolutions(run)} for i in gt}
    lines = ["| Resolution | Scorable issues | Located | Top-1 | Top-3 | Random top-1 (expected) "
             "| Random top-3 (expected) |", "|---|---|---|---|---|---|---|"]
    for res in resolutions(run):
        scorable = [per_issue[i["id"]][res] for i in gt if per_issue[i["id"]][res][0] not in ("no function", "n/a")]
        located = [v for v in scorable if v[0] != "not located"]
        top1 = sum(v[0] == "top1" for v in located)
        top3 = top1 + sum(v[0] == "top3" for v in located)
        lines.append(f"| {res} | {len(scorable)} | {len(located)} | {top1}/{len(located)} | {top3}/{len(located)} "
                     f"| {sum(v[1] for v in located):.1f} | {sum(v[2] for v in located):.1f} |")
    return lines, {issue: {res: v[0] for res, v in by_res.items()} for issue, by_res in per_issue.items()}


def cost_table(run: dict) -> list[str]:
    """Measured cost per phase, and the scan phase split by question level."""
    lines = ["| Phase | Requests | Cached | Input tokens | Cost | Wall time |", "|---|---|---|---|---|---|"]
    for phase, st in run["stats"].items():
        lines.append(f"| {phase} | {st['requests']} | {st['cache_hits']} | {st['tokens']:,} | ${st['cost_usd']:.4f} "
                     f"| {st['wall_s']}s |")
    lines += ["", "| Scan level (broad questions ride with category) | Requests | Input tokens | Cost |", "|---|---|---|---|"]
    for level in resolutions(run):
        req = sum(r["usage"][level]["requests"] for r in run["files"])
        tok = sum(r["usage"][level]["tokens"] for r in run["files"])
        lines.append(f"| {level} | {req} | {tok:,} | ${cost_usd(tok):.4f} |")
    return lines


def issue_table(run: dict, gt: list[dict], lib: dict, loc: dict) -> list[str]:
    levels = resolutions(run)
    lines = [f"| Issue | Files | Category / subcategory | {' | '.join(levels)} | Located ({' / '.join(levels)}) |",
             "|---|---|---|" + "---|" * len(levels) + "---|"]
    for i in gt:
        cells = []
        for res in levels:
            qids = targets(i, res, lib)
            if not qids:
                cells.append("n/a")
                continue
            p, q = best_true(i, qids, pairs(run, res))
            cells.append(("not asked" if q is None else fmt(p) + (f" `{q.split(':')[1]}`" if res == "detector" else "")))
        files = ", ".join(f"`{f.split('/')[-1]}`" for f in i["files"])
        tax = f"{i['category_id']} / {i['subcategory_id'] or '—'}"
        lines.append(f"| {i['id']} {i['title']} | {files} | {tax} | {' | '.join(cells)} "
                     f"| {' / '.join(loc[i['id']][res] for res in levels)} |")
    return lines


def unverified_table(run: dict, gt: list[dict], lib: dict) -> list[str]:
    truth = true_pairs(gt, lib)
    rows = sorted(
        ((p, r["path"], q) for r in run["files"] for q, p in r["questions"].items()
         if not q.startswith("broad:") and (r["path"], q) not in truth),
        reverse=True,
    )[:10]
    lines = ["| p | File | Question | Description | Status |", "|---|---|---|---|---|"]
    lines += [f"| {p:.2f} | `{f}` | {q} | {lib['descriptions'][q]} | unverified |" for p, f, q in rows]
    return lines


def line_table(run: dict, gt: list[dict], lib: dict) -> list[str]:
    """Experimental line step on the same scored pair as function locating: the issue function ranked highest
    for that pair, if it got a line answer. Is the chosen line inside a report-linked snippet of the issue's file?"""
    by_path = {r["path"]: r for r in run["files"]}
    lines = ["| Resolution | Issues with snippet and a line answer | Top-1 in snippet | Top-3 in snippet "
             "| Random top-1 (expected) | Random top-3 (expected) |", "|---|---|---|---|---|---|"]
    for res in resolutions(run):
        scored = top1 = top3 = 0
        base1 = base3 = 0.0
        for i in gt:
            qids = targets(i, res, lib)
            if not qids or not i.get("snippets") or not i["functions"]:
                continue
            pair = scored_pair(i, qids, run)
            rows = pair and by_path[pair[0]].get("located", {}).get(pair[1])
            row = next((row for row in rows or () if row["name"] in i["functions"]), None)
            if row is None or "line" not in row:
                continue
            inside = {f"L{n}" for s in i["snippets"] if s["file"] == pair[0] for n in range(s["start"], s["end"] + 1)}
            probs = row["line"]["probabilities"]
            ranked = sorted(probs, key=lambda k: -probs[k])
            pos = next((n for n, line in enumerate(ranked) if line in inside), len(ranked))
            n, k = len(ranked), len(inside & set(ranked))
            scored += 1
            top1 += pos == 0
            top3 += pos < 3
            base1, base3 = base1 + chance(n, k, 1), base3 + chance(n, k, 3)
        lines.append(f"| {res} | {scored} | {top1}/{scored} | {top3}/{scored} | {base1:.1f} | {base3:.1f} |")
    return lines


def repo_table(run: dict, gt: list[dict], lib: dict) -> list[str]:
    repo = run.get("repo")
    if not repo or not repo["fits"]:
        return ["Not run, or the scope did not fit in one request."]
    counts = issue_counts(gt)
    worst = max(counts, key=counts.get)
    lines = [f"One request over all {len(run['files'])} scanned files (~{repo['tokens']:,} estimated tokens). "
             f"Most suspicious file (Choice): `{repo['most_suspicious_file']}` "
             f"({repo['most_suspicious_probabilities'][repo['most_suspicious_file']]:.2f}); the file with the most "
             f"ground-truth issues is `{worst}` ({counts[worst]}).", "",
             "| Question | Repo-level p | Per-file max | Argmax file |", "|---|---|---|---|"]
    for q in [*lib["broad"], *lib["category"]]:
        top = max(run["files"], key=lambda r: r["questions"][q])
        lines.append(f"| {q} | {repo['questions'][q]:.2f} | {top['questions'][q]:.2f} | `{top['path']}` |")
    return lines


def heatmap_table(heatmap: dict, gt: list[dict]) -> list[str]:
    """Where each issue first appears in HEATMAP.md: its file among the grid rows, its function among the
    strongest-hit rows."""
    files = [f["path"] for f in grid_files(heatmap)]
    rows = [(f["path"], fn["name"]) for f, fn, _, _ in strongest_hits(heatmap)]
    lines = [f"HEATMAP.md's grid has {len(files)} files; its strongest-hits table has {len(rows)} functions.", "",
             "| Issues found within | First N rows | Count |", "|---|---|---|"]
    positions = [next((n for n, (f, fn) in enumerate(rows, start=1) if f in i["files"] and fn in i["functions"]), None)
                 for i in gt]
    with_fn = [p for i, p in zip(gt, positions) if i["functions"]]
    for n in (5, 10, 20, len(rows)):
        found = sum(p is not None and p <= n for p in with_fn)
        lines.append(f"| issue function in the strongest-hits table | {n} | {found}/{len(with_fn)} |")
    for n in (1, 3):
        found = sum(any(f in files[:n] for f in i["files"]) for i in gt)
        lines.append(f"| issue file among the top grid rows | {n} | {found}/{len(gt)} |")
    lines += ["", "Per issue (row of its first function in the strongest-hits table, or - if not listed): "
              + ", ".join(f"{i['id']} {p or '-'}" for i, p in zip(gt, positions))]
    return lines


def answer_key(gt: list[dict], lib: dict) -> list[dict]:
    """The ground truth as HEATMAP.md's answer key: each issue with the category and detector ids of its bug type."""
    return [{k: i[k] for k in ("id", "severity", "title", "files", "functions")}
            | {"questions": set().union(*(targets(i, res, lib) or () for res in ("category", "detector")))}
            for i in gt]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("bench", choices=BENCHES)
    parser.add_argument("--score", action="store_true", help="score the saved run without re-running")
    args = parser.parse_args()
    bench, out = BENCHES[args.bench], HERE / args.bench
    if not args.score:
        run_scan(bench, out / "run")
    gt = json.loads((out / "ground_truth.json").read_text())["issues"]
    run = json.loads((out / "run" / "results.json").read_text())
    lib = run_library(run)
    loc_lines, loc = locating_table(run, gt, lib)
    heatmap = build_heatmap(run, lib)
    key = answer_key(gt, lib)
    (out / "run" / "HEATMAP.md").write_text(render_heatmap_md(heatmap, Path(bench["repo"]).name, key))
    scanned = {r["path"] for r in run["files"]}
    not_scanned = [c for c in run["classification"] if c["path"] not in scanned]
    locate = run["config"]["thresholds"]["locate"]
    doc = [
        f"# jevscan benchmark: {bench['title']}",
        "",
        f"Ground truth: `bench/{args.bench}/ground_truth.json` ({len(gt)} H/M issues, categories assigned by hand). "
        f"Code: {bench['url']}. One run: `jevscan.py` with the default settings ({', '.join(resolutions(run))} "
        f"questions asked, locate threshold {locate}) and {run['model']}. "
        "A true pair is (issue file, the issue's category / subcategory / any detector mapped to its subcategory). "
        "Issues with no fitting subcategory are scored only at category resolution. Ranks are among all asked pairs "
        f"at that resolution (1 = highest p). Bold p values are >= {HIT}.",
        "",
        "Files not scanned (Jev file classification): "
        + (", ".join(f"`{c['path']}` ({c['kind']}, {c['confidence']:.2f})" for c in not_scanned) or "none") + ".",
        "",
        "## File-level recall", "", *recall_table(run, gt, lib),
        "", "## Broad questions per file", "",
        *broad_table(run, gt, lib),
        "", "## False-positive proxy", "", *fp_table(run, gt, lib),
        "", "## Flags without a known finding", "", *flags_table(heatmap, key, bench.get("flag_notes", {})),
        "", f"## Locating (file-level threshold {locate})", "",
        "An issue is scored when it names a function, on exactly one function ranking: its true (file, question) "
        "pair with the highest file-level p (ties broken by file and question id). The pair is chosen from the "
        "file-level answers alone, so no issue gets the best of several rankings. Top-1/top-3: one of the issue's "
        "functions is ranked first / in the top 3 in that ranking. The random baseline uses the same ranking: with n "
        "functions of which k are the issue's, top-1 chance k/n and top-3 chance 1 - C(n-k,3)/C(n,3), summed over "
        f"the located issues. 'Not located' means the scored pair was below {locate} at file level (so every true pair "
        "was), and nothing was re-asked per function.", "", *loc_lines,
        "", "## Line locating (experimental)", "",
        f"For each (function, question) whose function-level p >= {locate}, one Choice question picks the primary "
        "vulnerable line. An issue is scored on the same pair as above, at the issue function ranked highest for "
        "it, when the report links a snippet (line range) in that file and that function got a line answer. The "
        "random baseline uses the same Choice: with n options of which k fall in a snippet. Snippets that span a "
        "whole function make this easy.", "",
        *line_table(run, gt, lib),
        "", "## Repo-level", "", *repo_table(run, gt, lib),
        "", "## HEATMAP order", "", *heatmap_table(heatmap, gt),
        "", "## Cost", "", *cost_table(run),
        "", "## Issues", "", *issue_table(run, gt, lib, loc),
        "", "## Top 10 (file, question) pairs not in the ground truth", "",
        "These are candidate false positives or real issues the contest did not list. None were verified.", "",
        *unverified_table(run, gt, lib),
    ]
    notes = out / "notes.md"  # hand-written sections, kept across re-runs
    if notes.exists():
        doc += ["", notes.read_text().rstrip()]
    (out / "results.md").write_text("\n".join(doc) + "\n")
    print(f"wrote {out / 'results.md'}")


if __name__ == "__main__":
    main()
