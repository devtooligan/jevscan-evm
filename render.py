"""Rebuild a run's outputs (report.md, findings.json, jevheatmap.json, HEATMAP.md) from its results.json
without calling Jev, using the settings recorded in it.

Usage:
    python render.py <out_dir>
"""

import argparse
import json
from pathlib import Path

from jevscan import run_library
from report import write_outputs


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("out_dir", type=Path, help="a jevscan output directory containing results.json")
    out_dir = parser.parse_args().out_dir
    run = json.loads((out_dir / "results.json").read_text())
    if "config" not in run:
        raise SystemExit(f"{out_dir / 'results.json'} predates the config file (no `config`); re-run the scan "
                         "with equivalent settings (answers come from the cache) to rewrite it")
    write_outputs(run, run_library(run), out_dir)
    print(f"Rewrote the outputs in {out_dir}")


if __name__ == "__main__":
    main()
