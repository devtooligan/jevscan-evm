"""Render a jevscan run (the results.json dict): report.md, ScaBench findings.json, jevheatmap.json, HEATMAP.md."""

import json
import tomllib
from pathlib import Path

from config import DEFAULT
from heatmap import CATEGORIES, details, md_cell, render_heatmap_md, threshold_for


def name(question: str) -> str:
    return question.split(":", 1)[1]


def turned_on(table: dict[str, bool]) -> list[str]:
    return [k for k, on in table.items() if on]


def top_function(result: dict, question: str) -> dict | None:
    rows = result.get("located", {}).get(question)
    return rows[0] if rows else None


def hits(run: dict, level: str | None = None) -> list[tuple[dict, str, float]]:
    """(file result, question, p) for every non-broad answer over its threshold, highest p first."""
    found = [
        (r, q, p)
        for r in run["files"]
        for q, p in r["questions"].items()
        if not q.startswith("broad:") and p >= threshold_for(q, run["config"]["thresholds"])
        and (level is None or q.startswith(level + ":"))
    ]
    return sorted(found, key=lambda h: -h[2])


def likely_issues(run: dict) -> list[dict]:
    """One item per (file, top function) among the hits, or per file for hits without a function ranking,
    highest p first. An item is named by its best (highest p) question; the other questions that point at
    the same place are listed under `also`."""
    buckets: dict[tuple, list[tuple[str, float, dict | None]]] = {}
    for r, q, p in hits(run):  # highest p first, so each bucket starts with its best question
        fn = top_function(r, q)
        buckets.setdefault((r["path"], fn and (fn["name"], fn["start_line"])), []).append((q, p, fn))
    items = []
    for (path, _), entries in buckets.items():
        best_q, best_p, fn = entries[0]
        lined = [e[2]["line"]["choice"] for e in entries if e[2] and "line" in e[2]]
        items.append({
            "file": path, "question": best_q, "p": best_p,
            "also": [{"question": q, "p": p} for q, p, _ in entries[1:]],
            "function": fn and {k: fn[k] for k in ("name", "start_line", "end_line", "p")},
            "line": lined[0] if lined else None,
        })
    return sorted(items, key=lambda i: -i["p"])


def label(question: str) -> str:
    """`subcategory missing_slippage_protection`: a question's level and name."""
    return question.replace(":", " ", 1)


def issue_line(item: dict) -> str:
    where = ""
    if item["function"]:
        fn = item["function"]
        where = f" → {fn['name']}() L{fn['start_line']}-{fn['end_line']}" + (f", line {item['line']}" if item["line"] else "")
    also = ", ".join(f"{label(a['question'])} {a['p']:.2f}" for a in item["also"][:3])
    more = f", +{len(item['also']) - 3} more" if len(item["also"]) > 3 else ""
    return f"`{item['file']}` — {label(item['question'])}{where} ({item['p']:.2f})" + (f"; also {also}{more}" if also else "")


def render_findings(run: dict, lib: dict) -> dict:
    """ScaBench shape: one finding per likely issue."""
    findings = []
    for item in likely_issues(run):
        fn = item["function"]
        location = item["file"]
        if fn:
            location = f"{fn['name']} (L{fn['start_line']}-{fn['end_line']}" + (f", {item['line']})" if item["line"] else ")")
        also = "; ".join(f"{label(a['question'])} ({a['p']:.2f})" for a in item["also"])
        findings.append({
            "title": label(item["question"]),
            "description": f"{lib['text'][item['question']]} (Jev P(yes) = {item['p']:.2f})"
                           + (f" Also flagged here: {also}." if also else ""),
            "severity": "high" if item["p"] >= 0.8 else "medium" if item["p"] >= 0.5 else "low",
            "location": location,
            "file": item["file"],
        })
    return {"project": run["project"], "findings": findings}


def repo_verdict(run: dict) -> dict | None:
    """Repo-level answers when run.repo_level ran and the scope fit, else the per-file maximum; None when the
    broad level was off."""
    if not run["config"]["levels"]["broad"]:
        return None
    repo = run.get("repo")
    if repo and repo["fits"]:
        q = repo["questions"]
        return {"critical": q["broad:critical_bug"], "any_bug": q["broad:any_bug"],
                "most_suspicious_file": repo["most_suspicious_file"], "source": "repo-level questions"}
    top = max(run["files"], key=lambda r: r["questions"]["broad:critical_bug"])
    why = f"the scope is too large for one repo-level request, ~{repo['tokens']:,} tokens" if repo else "run.repo_level off"
    return {"critical": top["questions"]["broad:critical_bug"],
            "any_bug": max(r["questions"]["broad:any_bug"] for r in run["files"]),
            "most_suspicious_file": top["path"], "source": f"per-file maximum; {why}"}


def verdict_line(v: dict | None) -> str:
    if v is None:
        return "**Verdict:** not available (levels.broad is off)"
    return (f"**Verdict:** critical {v['critical']:.2f} · any bug {v['any_bug']:.2f} · most suspicious file "
            f"`{v['most_suspicious_file']}` ({v['source']})")


def run_stats(run: dict) -> dict:
    """Totals over every phase, plus file counts."""
    scanned = {r["path"] for r in run["files"]}
    skipped = {s["path"] for s in run["skipped"]}
    totals = {k: sum(s[k] for s in run["stats"].values())
              for k in ("requests", "cache_hits", "tokens", "cost_usd", "billed_usd", "wall_s")}
    return totals | {"candidates": len(run["classification"]), "scanned": len(scanned),
                     "over_size_cap": len(skipped),
                     "not_scanned_class": sum(c["path"] not in scanned | skipped for c in run["classification"])}


def stats_line(s: dict) -> str:
    return (f"Scanned {s['scanned']} of {s['candidates']} files ({s['not_scanned_class']} in classes not scanned, "
            f"{s['over_size_cap']} over the size cap) · {s['requests']:,} requests ({s['cache_hits']:,} cached) · "
            f"{s['tokens']:,} tokens · ${s['cost_usd']:.2f} (billed ${s['billed_usd']:.2f}) · {s['wall_s']:.1f} s")


def asked_line(asked: dict) -> str:
    """`asked` holds levels, sources, thresholds, locate, and model, as in jevheatmap.json."""
    t = asked["thresholds"]
    locate = f"locate ≥ {t['locate']}" if asked["locate"] else "locate off"
    return (f"Asked: {', '.join(asked['levels'])}; detector sources {', '.join(asked['sources'])} · hit threshold "
            f"{t['taxonomy']}, detectors {t['detectors']} · {locate} · {asked['model']}")


def asked_settings(run: dict) -> dict:
    cfg = run["config"]
    return {"levels": turned_on(cfg["levels"]), "sources": turned_on(cfg["sources"]), "thresholds": cfg["thresholds"],
            "locate": cfg["run"]["locate"], "model": run["model"]}


def matrix(results: list[dict], questions: list[str], rows_are_files: bool) -> tuple[list[str], int]:
    """A p table over files x questions (or questions x files), without rows whose every p rounds to 0.00.
    Returns the lines and the number of rows dropped."""

    def cell(r: dict, q: str) -> str:
        return f"{r['questions'][q]:.2f}" if q in r["questions"] else "-"

    def zero(values: list[float]) -> bool:
        return all(round(v, 2) == 0 for v in values)

    if rows_are_files:
        rows = [r for r in results if not zero([r["questions"][q] for q in questions])]
        lines = ["| File | " + " | ".join(name(q) for q in questions) + " |", "|---|" + "---|" * len(questions)]
        lines += [f"| `{r['path']}` | " + " | ".join(cell(r, q) for q in questions) + " |" for r in rows]
        return lines, len(results) - len(rows)
    rows = [q for q in questions if not zero([r["questions"][q] for r in results])]
    lines = ["| Question | " + " | ".join(f"`{r['path']}`" for r in results) + " |", "|---|" + "---|" * len(results)]
    lines += [f"| {name(q)} | " + " | ".join(cell(r, q) for r in results) + " |" for q in rows]
    return lines, len(questions) - len(rows)


def render_report(run: dict, lib: dict) -> str:
    results, t, desc = run["files"], run["config"]["thresholds"], lib["descriptions"]
    lines = ["# jevscan report", "", verdict_line(repo_verdict(run)), "",
             stats_line(run_stats(run)), "", asked_line(asked_settings(run)), ""]

    items = likely_issues(run)
    lines += [f"## Likely issues: {len(items)}", "",
              "One line per (file, top function) with a hit, named by its best question; the same list is in "
              "findings.json.", ""]
    lines += [f"- {issue_line(i)}" for i in items]

    found = hits(run)
    lines += ["", f"## Hits: {len(found)}", "", "| p | File | Question | Top function | Description |",
              "|---|---|---|---|---|"]
    for r, q, p in found:
        fn = top_function(r, q)
        where = f"`{fn['name']}` L{fn['start_line']}-{fn['end_line']} ({fn['p']:.2f})" if fn else ""
        lines.append(f"| {p:.3f} | `{r['path']}` | {q} | {where} | {md_cell(desc[q])} |")

    lines += ["", "## Full tables", ""]
    listed = {r["path"]: sum(i["file"] == r["path"] for i in items) for r in results}
    table = ["| File | critical_bug | any_bug | Likely issues listed | est. tokens |", "|---|---|---|---|---|"]
    by_risk = sorted(results, key=lambda r: -file_risk(r))
    for r in by_risk:
        q = r["questions"]
        broad = [f"{q[b]:.3f}" if b in q else "-" for b in ("broad:critical_bug", "broad:any_bug")]
        table.append(f"| `{r['path']}` | {' | '.join(broad)} | {listed[r['path']]} | {r['tokens']:,} |")
    lines += details(f"Files ranked by risk ({len(results)})", table)

    if not run["config"]["files"]["paths"]:  # an explicit files.paths list is not classified
        scanned = {r["path"] for r in results}
        classes = run["config"]["classes"]["scan"]
        table = [f"Files in classes {', '.join(classes)} are scanned, and so are files matched by files.include_globs.", "",
                 "| File | Class | Confidence | Scanned |", "|---|---|---|---|"]
        table += [f"| `{c['path']}` | {c['kind']} | {c['confidence']:.2f} | "
                  f"{('yes (include_globs)' if c['forced'] else 'yes') if c['path'] in scanned else 'no'} |"
                  for c in run["classification"]]
        lines += details(f"File classification ({len(run['classification'])} candidates)", table)

    for level, rows_are_files in (("category", True), ("subcategory", False)):
        if lib[level]:
            table, dropped = matrix(by_risk, list(lib[level]), rows_are_files)
            note = [f"{dropped} {'files' if rows_are_files else 'rows'} with every p at 0.00 omitted.", ""] if dropped else []
            lines += details(f"All {level} p (every file)", note + table)

    detector_hits = hits(run, "detector")
    table = ["Every detector probability is in results.json.", "", "| p | File | Detector | Source | Description |",
             "|---|---|---|---|---|"]
    table += [f"| {p:.3f} | `{r['path']}` | {name(q)} | {lib['source'][q]} | {md_cell(desc[q])} |"
              for r, q, p in detector_hits]
    if lib["detector"]:
        lines += details(f"Detector hits (p >= {t['detectors']}): {len(detector_hits)}", table)

    if run["config"]["run"]["locate"]:
        table = [f"Located: every question with file-level p ≥ {t['locate']}. Lines come from an experimental "
                 "Choice question, asked only where the function-level p reaches that threshold too.", ""]
        for r in by_risk:
            for q, rows in sorted(r.get("located", {}).items(), key=lambda kv: -r["questions"][kv[0]]):
                tops = ", ".join(
                    f"`{f['name']}` L{f['start_line']}-{f['end_line']} ({f['p']:.2f})"
                    + (f" → {f['line']['choice']} ({f['line']['confidence']:.2f})" if "line" in f else "")
                    for f in rows[:3] if round(f["p"], 2) > 0
                )
                table.append(f"- `{r['path']}` {q} ({r['questions'][q]:.2f}): {tops or 'every function at 0.00'}")
        lines += details("Located: file → function → line (top 3 functions per located question)", table)

    if run["not_located"]:
        lines += details(f"Not located: {len(run['not_located'])} (the function splitter handles Solidity only)",
                         [f"- `{path}`" for path in run["not_located"]])
    if run["skipped"]:
        lines += details(f"Skipped: {len(run['skipped'])} (source exceeds the file token cap)",
                         [f"- `{s['path']}` (~{s['tokens']:,} tokens)" for s in run["skipped"]])
    return "\n".join(lines).rstrip() + "\n"


def file_risk(r: dict) -> float:
    """max(critical_bug, top category p); the top non-broad p when neither level was asked."""
    q = r["questions"]
    main = [p for k, p in q.items() if k == "broad:critical_bug" or k.startswith("category:")]
    return max(main or [p for k, p in q.items() if not k.startswith("broad:")])


def file_functions(r: dict, t: dict) -> list[dict]:
    """Per-function view of a file's locating, highest p first: every located question whose function-level p reaches
    its threshold, highest first, and the chosen line for each of them where one was asked."""
    functions: dict[tuple, dict] = {}
    for q, rows in r.get("located", {}).items():
        for row in rows:
            fn = functions.setdefault((row["name"], row["start_line"]), {
                "name": row["name"], "lines": [row["start_line"], row["end_line"]], "max_p": 0.0, "questions": {},
                "line_choices": {}})
            fn["max_p"] = max(fn["max_p"], row["p"])
            if row["p"] >= threshold_for(q, t):
                fn["questions"][q] = row["p"]
                if "line" in row:
                    fn["line_choices"][q] = {"line": int(row["line"]["choice"][1:]), "confidence": row["line"]["confidence"]}
    for fn in functions.values():
        fn["questions"] = dict(sorted(fn["questions"].items(), key=lambda kv: -kv[1]))
    return sorted(functions.values(), key=lambda f: -f["max_p"])


def config_changes(cfg: dict) -> dict:
    """`section.key` -> value for every setting (paths aside) that differs from jevscan.toml."""
    default = tomllib.loads(DEFAULT.read_text())
    return {f"{section}.{key}": value for section, table in cfg.items() if section != "paths"
            for key, value in table.items() if default[section][key] != value}


def build_heatmap(run: dict, lib: dict) -> dict:
    """The run arranged per file and per function and sorted by risk: every category p, every other question at
    or over its hit threshold, and a description for each question listed."""
    t = run["config"]["thresholds"]
    kinds = {c["path"]: c["kind"] for c in run["classification"]}
    files = []
    for r in sorted(run["files"], key=lambda r: -file_risk(r)):
        q = r["questions"]
        files.append({
            "path": r["path"], "class": kinds[r["path"]], "lines": r["lines"], "risk": file_risk(r),
            "critical": q.get("broad:critical_bug"), "any_bug": q.get("broad:any_bug"),
            "categories": {name(k): p for k, p in q.items() if k.startswith("category:")},
            "questions": {k: p for k, p in sorted(q.items(), key=lambda kv: -kv[1])
                          if not k.startswith("broad:") and p >= threshold_for(k, t)},
            "located": bool(r.get("located")),
            "functions": file_functions(r, t),
        })
    listed = {k for f in files for k in f["questions"]} | {k for f in files for fn in f["functions"] for k in fn["questions"]}
    scanned = {r["path"] for r in run["files"]}
    too_big = {s["path"] for s in run["skipped"]}
    files += [{"path": c["path"], "class": c["kind"], "skipped": "size" if c["path"] in too_big else "class"}
              for c in run["classification"] if c["path"] not in scanned]
    return {"project": run["project"], "root": run["root"], "explicit_scope": bool(run["config"]["files"]["paths"]),
            **asked_settings(run),
            "config_changes": config_changes(run["config"]), "stats": run_stats(run), "repo": repo_verdict(run),
            "categories": {name(c): {"name": lib["descriptions"][c], "label": CATEGORIES[name(c)][0]}
                           for c in lib["children"] if c.startswith("category:")},
            "descriptions": {k: lib["descriptions"][k] for k in sorted(listed)},
            "files": files}


def write_outputs(run: dict, lib: dict, out_dir: Path) -> None:
    """Every output file except results.json."""
    (out_dir / "report.md").write_text(render_report(run, lib))
    (out_dir / "findings.json").write_text(json.dumps(render_findings(run, lib), indent=2) + "\n")
    heatmap = build_heatmap(run, lib)
    (out_dir / "jevheatmap.json").write_text(json.dumps(heatmap, indent=2) + "\n")
    (out_dir / "HEATMAP.md").write_text(render_heatmap_md(heatmap))
