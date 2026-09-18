"""HEATMAP.md checks on a USSD benchmark run (trimmed to the answers the heat map uses): python -m pytest tests/."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from heatmap import pct, render_heatmap_md, strongest_hits, usd  # noqa: E402
from jevscan import run_library  # noqa: E402
from report import build_heatmap  # noqa: E402

RUN = json.loads((Path(__file__).resolve().parent / "ussd_run.json").read_text())
HEATMAP = build_heatmap(RUN, run_library(RUN))
MD = render_heatmap_md(HEATMAP)


def section(title: str) -> list[str]:
    lines = MD.split("\n")
    start = next(n for n, line in enumerate(lines) if line.startswith(title))
    end = next(n for n in range(start + 1, len(lines)) if lines[n].startswith("## "))
    return lines[start:end]


def test_formatting():
    assert (pct(0.876), pct(0.001), usd(0.0), usd(0.111)) == ("88%", "<1%", "<$0.01", "$0.11")


def test_grid_cells_are_colors_only():
    rows = [line for line in section("## Heat grid") if line.startswith("| `")]
    assert len(rows) == len(RUN["files"])
    for row in rows:
        assert set(row.split(" | ")[1:-1]) <= {"⬜", "🟩", "🟨", "🟧", "🟥"}, row


def test_one_hit_row_per_strongly_flagged_function_without_subcategories():
    rows = strongest_hits(HEATMAP)
    strong = HEATMAP["thresholds"]["strong_hits"]
    flagged = {(f["path"], fn["name"], fn["lines"][0]) for f in HEATMAP["files"] for fn in f.get("functions", ())
               if any(not q.startswith("subcategory:") and p >= strong for q, p in fn["questions"].items())}
    assert {(f["path"], fn["name"], fn["lines"][0]) for f, fn, _, _ in rows} == flagged
    assert all(not q.startswith("subcategory:") and p >= strong for _, _, q, p in rows)
    table = [line for line in section("## Strongest function hits") if line.startswith("| `")]
    assert len(table) == len(rows)


def test_no_subcategory_outside_file_details():
    before_details = MD.split("## File details")[0]
    assert "subcategory" not in before_details.replace("levels.subcategory", "")
