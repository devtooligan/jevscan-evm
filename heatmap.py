"""HEATMAP.md: a plain-English, colors-first view of a jevscan run, rendered from the jevheatmap.json dict."""

import json
from datetime import date

# Grid label and a plain-words blurb for each taxonomy category, in sources/taxonomy.json order.
CATEGORIES = {
    "access_control": ("Access", "who may call what: missing or wrong permission checks"),
    "proxy_upgradeability": ("Proxy", "proxies, upgrades, initializers, and storage layout"),
    "oracle_price_manipulation": ("Oracle", "price feeds and oracle manipulation"),
    "flash_loan_economic": ("Econ", "flash loans and economic attacks"),
    "reentrancy": ("Reentry", "reentrancy: an outside call re-enters before state is updated"),
    "accounting_share_math": ("Shares", "vault shares, balances, rewards, and fee accounting"),
    "arithmetic_precision": ("Math", "rounding, precision loss, overflow, and decimals"),
    "signature_replay": ("Sigs", "signatures and replay"),
    "cross_chain_messaging": ("Xchain", "bridges and cross-chain or L2 messages"),
    "external_call_token_integration": ("Tokens", "external calls and unusual token behavior"),
    "business_logic_state_machine": ("Logic", "business logic, input checks, and state transitions"),
    "dos_griefing": ("DoS", "denial of service and griefing"),
    "frontrunning_mev": ("MEV", "front-running, slippage, MEV, and randomness"),
    "legacy_low_level": ("LowLvl", "low-level EVM pitfalls: tx.origin, delegatecall, assembly, selfdestruct"),
}
BROAD = {"critical": ("Crit", "an attacker can gain value: steal or lock funds, or exploit mispricing"),
         "any_bug": ("Any", "at least one exploitable vulnerability of any kind")}
RED, ORANGE, GREEN = 0.85, 0.7, 0.3  # grid color floors; yellow starts at the hit threshold
SEVERITY_ORDER = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
FLAG_THRESHOLDS = (0.7, 0.5)  # file-level category chances at which unmatched flags are counted (benchmarks only)


def pct(p: float) -> str:
    return f"{p * 100:.0f}%" if p >= 0.005 else "<1%"


def usd(x: float) -> str:
    return f"${x:.2f}" if x >= 0.005 else "<$0.01"


def threshold_for(question: str, thresholds: dict) -> float:
    return thresholds["detectors" if question.startswith("detector:") else "taxonomy"]


def square(p: float, threshold: float) -> str:
    """A grid color: red and orange for likely, yellow from the hit threshold, green for possible, white below."""
    if p >= threshold:
        return "🟥" if p >= RED else "🟧" if p >= ORANGE else "🟨"
    return "🟩" if p >= GREEN else "⬜"


def md_cell(text: str) -> str:
    return text.replace("|", "\\|").replace("\n", " ")


def details(summary: str, body: list[str]) -> list[str]:
    """A collapsed <details> block; blank lines around the body so GitHub renders its Markdown."""
    return [f"<details><summary>{summary}</summary>", "", *body, "", "</details>", ""]


def qid(question: str) -> str:
    """`detector sol_token_fe_1`: a question's level and name."""
    return question.replace(":", " ", 1)


def grid_cells(f: dict, heatmap: dict) -> dict[str, float]:
    """Grid column label -> p for one scanned file: the broad questions asked, then every category."""
    cells = {BROAD[k][0]: f[k] for k in BROAD if f[k] is not None}
    return cells | {CATEGORIES[c][0]: f["categories"][c] for c in heatmap["categories"] if c in f["categories"]}


def grid_files(heatmap: dict) -> list[dict]:
    """Scanned files by their highest grid p (file risk when no grid question was asked)."""
    scanned = [f for f in heatmap["files"] if "risk" in f]
    return sorted(scanned, key=lambda f: (-max(grid_cells(f, heatmap).values(), default=f["risk"]), f["path"]))


def function_hits(fn: dict) -> list[tuple[str, float]]:
    """A function's hits, strongest first, with subcategory hits after every other level."""
    return sorted(fn["questions"].items(), key=lambda qp: (qp[0].startswith("subcategory:"), -qp[1]))


def strongest_hits(heatmap: dict) -> list[tuple[dict, dict, str, float]]:
    """(file, function, question, p) for every function whose strongest hit is not a subcategory and reaches
    thresholds.strong_hits, highest p first."""
    strong = heatmap["thresholds"]["strong_hits"]
    rows = [(f, fn, *function_hits(fn)[0]) for f in grid_files(heatmap) for fn in f["functions"] if fn["questions"]]
    rows = [row for row in rows if not row[2].startswith("subcategory:") and row[3] >= strong]
    return sorted(rows, key=lambda row: (-row[3], row[0]["path"], row[1]["lines"][0]))


def line_of(fn: dict, q: str) -> str:
    choice = fn["line_choices"].get(q)
    return str(choice["line"]) if choice else ""


def is_hot(f: dict, t: dict) -> bool:
    """A file with any question (broad included) at or over its threshold."""
    broad = [p for p in (f["critical"], f["any_bug"]) if p is not None]
    return any(p >= t["taxonomy"] for p in broad) or bool(f["questions"])


def answer_ids(f: dict, fn: dict, answer_key: list[dict]) -> list[str]:
    """Known findings in this file and function that one of the function's hits matches by bug type, most severe first.
    A finding that names no function is never pinned to a function row."""
    found = [i for i in answer_key if f["path"] in i["files"]
             and fn["name"] in i["functions"] and i["questions"] & fn["questions"].keys()]
    return [i["id"] for i in sorted(found, key=lambda i: SEVERITY_ORDER[i["severity"]])]


def best_match(issue: dict, heatmap: dict) -> tuple[float, dict, dict, str] | None:
    """The strongest function-level hit on the finding's file, function, and bug type: (p, file, function, question).
    A finding that names no function matches only category hits, in any function of its files."""
    found = [(p, f, fn, q) for f in heatmap["files"] if f["path"] in issue["files"] for fn in f.get("functions", ())
             if not issue["functions"] or fn["name"] in issue["functions"]
             for q, p in fn["questions"].items()
             if q in issue["questions"] and (issue["functions"] or q.startswith("category:"))]
    return max(found, key=lambda m: m[0]) if found else None


def header(heatmap: dict, name: str) -> list[str]:
    v, s = heatmap["repo"], heatmap["stats"]
    lines = [f"# 🔥 jevscan heat map: {name}", ""]
    if v is None:
        lines += ["**No verdict: the broad questions were not asked (levels.broad is off).**", ""]
    else:
        lines += [f"**{pct(v['critical'])} chance of a critical bug · {pct(v['any_bug'])} chance of at least one "
                  f"exploitable bug · hottest file: `{v['most_suspicious_file']}`**", "",
                  "Numbers are Jev's probability that the statement is true."
                  + ("" if v["source"] == "repo-level questions" else f" Verdict: {v['source']}."), ""]

    not_scanned = [f for f in heatmap["files"] if "skipped" in f]
    by_class: dict[str, int] = {}
    for f in not_scanned:
        if f["skipped"] == "class":
            by_class[f["class"]] = by_class.get(f["class"], 0) + 1
    too_big = sum(f["skipped"] == "size" for f in not_scanned)
    scanned = [f for f in heatmap["files"] if "risk" in f]
    lines += ["| Codebase | |", "|---|---|", f"| Name | {name} |", f"| Solidity files found | {len(heatmap['files'])} |",
              f"| Lines of code | {sum(f['lines'] for f in scanned):,} (non-blank, scanned files) |",
              f"| Scanned | {len(scanned)}{' (explicit scope)' if heatmap['explicit_scope'] else ''} |"]
    if not heatmap["explicit_scope"]:
        lines.append("| Ignored | " + (", ".join(f"{n} {c}{'s' if n != 1 else ''}" for c, n in by_class.items())
                                      or "none") + " |")
    if too_big:
        lines.append(f"| Over the size cap | {too_big} |")
    run = f"{s['requests']:,} requests · {usd(s['cost_usd'])} · {s['wall_s']:.1f} s"
    if s["cache_hits"]:
        run += f" · {s['cache_hits']:,} answers from cache (billed {usd(s['billed_usd'])})"
    lines += ["", run, ""]
    if heatmap["config_changes"]:
        lines += ["Settings changed from `jevscan.toml`: "
                  + ", ".join(f"`{k} = {json.dumps(v)}`" for k, v in heatmap["config_changes"].items()), ""]
    return lines


def grid(heatmap: dict) -> list[str]:
    t = heatmap["thresholds"]["taxonomy"]
    files = grid_files(heatmap)
    labels = list(grid_cells(files[0], heatmap))
    if not labels:
        return []
    lines = ["## Heat grid", "", "| File | " + " | ".join(labels) + " |", "|---|" + "---|" * len(labels)]
    lines += [f"| `{f['path']}` | " + " | ".join(square(p, t) for p in grid_cells(f, heatmap).values()) + " |"
              for f in files]
    lines += ["", f"- 🟥 {pct(RED)} or more: very likely", f"- 🟧 {pct(ORANGE)} to {pct(RED)}: likely",
              f"- 🟨 {pct(t)} to {pct(ORANGE)}: leaning yes", f"- 🟩 {pct(GREEN)} to {pct(t)}: possible",
              f"- ⬜ under {pct(GREEN)}: not flagged", ""]
    blurbs = {label: blurb for label, blurb in [*BROAD.values(), *CATEGORIES.values()]}
    return lines + details("What the columns mean", [f"- **{label}**: {blurbs[label]}" for label in labels])


def hits_table(heatmap: dict, answer_key: list[dict] | None) -> list[str]:
    rows = strongest_hits(heatmap)
    t = heatmap["thresholds"]
    strong = pct(t["strong_hits"])
    lines = [f"## Strongest function hits ({strong}+): {len(rows)}", "",
             f"Every function whose strongest hit is {strong} or more, by that hit. Its other hits, and every function "
             f"hit from {pct(min(t['taxonomy'], t['detectors']))} to {strong}, are under its file below.", ""]
    if not rows:
        return lines + [f"No function has a hit of {strong} or more.", ""] + (
            known_findings(heatmap, answer_key) if answer_key is not None else [])
    key = " Corresponding findings |" if answer_key is not None else ""
    lines += ["| File | Function | Lines | What it found | Chance | Line |" + key,
              "|---|---|---|---|---|---|" + ("---|" if answer_key is not None else "")]
    for f, fn, q, p in rows:
        ids = f" {', '.join(answer_ids(f, fn, answer_key))} |" if answer_key is not None else ""
        lines.append(f"| `{f['path']}` | `{fn['name']}` | {fn['lines'][0]}-{fn['lines'][1]} | "
                     f"{md_cell(heatmap['descriptions'][q])} | {pct(p)} | {line_of(fn, q)} |" + ids)
    lines.append("")
    if answer_key is not None:
        lines += known_findings(heatmap, answer_key)
    return lines


def known_findings(heatmap: dict, answer_key: list[dict]) -> list[str]:
    matches = {i["id"]: best_match(i, heatmap) for i in answer_key}
    lines = [f"### Known findings: {sum(m is not None for m in matches.values())} of {len(answer_key)} found", "",
             "Found: a function-level hit on the finding's file, one of its functions, and its bug type (category or "
             "a detector mapped to it).", "",
             "| Id | Severity | Title | Found? | Location |", "|---|---|---|---|---|"]
    for i in answer_key:
        m = matches[i["id"]]
        found, where = "❌", ""
        if m:
            p, f, fn, q = m
            found = f"✅ {pct(p)}"
            line = line_of(fn, q)
            where = f"`{fn['name']}`" + (f" line {line}" if line else "") + f" ({qid(q)})"
        lines.append(f"| {i['id']} | {i['severity']} | {md_cell(i['title'])} | {found} | {where} |")
    return lines + [""]


def category_flags(heatmap: dict, answer_key: list[dict], threshold: float) -> list[tuple[str, str, float, bool]]:
    """(file, category, p, matched) for every scanned file's category at or over `threshold`, highest p first. Matched:
    a known finding in that file has that category."""
    flags = [(f["path"], c, p) for f in heatmap["files"] if "risk" in f for c, p in f["categories"].items() if p >= threshold]
    return [(path, c, p, any(path in i["files"] and f"category:{c}" in i["questions"] for i in answer_key))
            for path, c, p in sorted(flags, key=lambda flag: (-flag[2], flag[0], flag[1]))]


def unmatched_flags(heatmap: dict, answer_key: list[dict]) -> list[str]:
    unmatched = {th: [flag for flag in category_flags(heatmap, answer_key, th) if not flag[3]] for th in FLAG_THRESHOLDS}
    desc = heatmap["descriptions"]

    def table(flags: list) -> list[str]:
        return ["| File | Category | Chance |", "|---|---|---|"] + [
            f"| `{path}` | {md_cell(desc[f'category:{c}'])} | {pct(p)} |" for path, c, p, _ in flags]

    high, low = FLAG_THRESHOLDS
    lines = ["### Flags without a known finding: " + ", ".join(f"{len(unmatched[th])} at {pct(th)}" for th in FLAG_THRESHOLDS),
             "", "A flag is a file whose chance for a category is at or over the threshold. These flags have no known "
             "finding of that category in that file: possibly unreported issues, or false positives. Not verified.", ""]
    lines += table(unmatched[high]) + [""] if unmatched[high] else [f"None at {pct(high)}.", ""]
    return lines + details(f"All {len(unmatched[low])} at {pct(low)}", table(unmatched[low]))


def file_block(f: dict, heatmap: dict) -> list[str]:
    t, desc = heatmap["thresholds"], heatmap["descriptions"]
    top = sorted(((c, p) for c, p in f["categories"].items() if p >= t["taxonomy"]), key=lambda kv: -kv[1])[:3]
    flagged = [fn for fn in f["functions"] if fn["questions"]]
    broad = [f"{BROAD[k][0]} {square(f[k], t['taxonomy'])}" for k in BROAD if f[k] is not None]
    categories = ", ".join(f"{CATEGORIES[c][0]} {pct(p)}" for c, p in top) or "no category hit"
    flagged_note = f"{len(flagged)} function{'s' if len(flagged) != 1 else ''} flagged" if f["located"] else "not located"
    summary = " · ".join([f["path"], *broad, categories, flagged_note])
    if not f["located"]:
        body = ["Not located: no function ranking for this file (Solidity only)."]
    elif not flagged:
        body = ["No function has a hit."]
    else:
        body = ["| Function | Lines | Strongest hit | Question | Chance | Line | More |", "|---|---|---|---|---|---|---|"]
        for fn in sorted(flagged, key=lambda fn: -function_hits(fn)[0][1]):
            (q, p), *rest = function_hits(fn)
            more = ""
            if rest:
                items = "<br>".join(f"{md_cell(desc[q2])} ({qid(q2)}) {pct(p2)}"
                                    + (f", line {line_of(fn, q2)}" if line_of(fn, q2) else "") for q2, p2 in rest)
                more = f"<details><summary>{len(rest)} more</summary>{items}</details>"
            body.append(f"| `{fn['name']}` | {fn['lines'][0]}-{fn['lines'][1]} | {md_cell(desc[q])} | {qid(q)} | "
                        f"{pct(p)} | {line_of(fn, q)} | {more} |")
    table = ["| Chance | Question | What it asks |", "|---|---|---|"]
    table += [f"| {pct(p)} | {qid(q)} | {md_cell(desc[q])} |" for q, p in f["questions"].items()]
    return details(summary, body + [""] + details(f"File-level hits ({len(f['questions'])})", table))


def render_heatmap_md(heatmap: dict, name: str | None = None, answer_key: list[dict] | None = None) -> str:
    """HEATMAP.md. `name` overrides the project name in the title; `answer_key` (benchmarks only) lists known findings
    as {id, severity, title, files, functions, questions}, where questions are the ids that count as its bug type."""
    name = name or heatmap["project"]
    t = heatmap["thresholds"]
    lines = header(heatmap, name) + grid(heatmap) + hits_table(heatmap, answer_key)
    if answer_key is not None:
        lines += unmatched_flags(heatmap, answer_key)
    files = grid_files(heatmap)
    hot = [f for f in files if is_hot(f, t)]
    cool = [f for f in files if not is_hot(f, t)]
    lines += ["## File details", ""]
    for f in hot:
        lines += file_block(f, heatmap)
    if cool:
        lines += [f"{len(cool)} {'file' if len(cool) == 1 else 'files'} with nothing at {pct(t['taxonomy'])} or more:", ""]
        lines += details("Low-risk files", [f"- `{f['path']}`" for f in cool])
    not_scanned = [f for f in heatmap["files"] if "skipped" in f]
    if not_scanned:
        lines += ["## Ignored files", ""]
        lines += details(f"Files not scanned ({len(not_scanned)})",
                         [f"- `{f['path']}`: {f['class'] if f['skipped'] == 'class' else 'over the size cap'}"
                          for f in not_scanned])
    threshold = pct(t["taxonomy"]) + (f", detectors {pct(t['detectors'])}" if t["detectors"] != t["taxonomy"] else "")
    lines += ["---", "", f"Jev model {heatmap['model']} · hit threshold {threshold} · generated {date.today().isoformat()}"]
    return "\n".join(lines).rstrip() + "\n"
