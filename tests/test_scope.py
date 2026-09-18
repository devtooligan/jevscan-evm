"""files.paths, the explicit scan list: python -m pytest tests/."""

import copy
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from heatmap import render_heatmap_md  # noqa: E402
from jevscan import find_files, run_library  # noqa: E402
from report import build_heatmap  # noqa: E402
from test_heatmap import RUN  # noqa: E402

FILES_CFG = {"scope": "src", "extensions": [".sol"], "skip_dirs": ["lib"], "include_globs": [], "paths": []}


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    for rel in ("src/A.sol", "src/B.sol", "lib/Dep.sol", "vyper/C.vy"):
        (tmp_path / rel).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / rel).write_text("contract X {}\n")
    return tmp_path


def test_without_paths_scope_extensions_and_skip_dirs_apply(repo: Path):
    root, files = find_files(repo, FILES_CFG)
    assert root == repo / "src"
    assert files == [repo / "src/A.sol", repo / "src/B.sol"]


def test_paths_bypass_scope_extensions_and_skip_dirs(repo: Path):
    root, files = find_files(repo, FILES_CFG | {"paths": ["lib/Dep.sol", "vyper/C.vy", "src/A.sol"]})
    assert root == repo
    assert files == [repo / "lib/Dep.sol", repo / "vyper/C.vy", repo / "src/A.sol"]


@pytest.mark.parametrize("bad", ["src/Missing.sol", "src", "src/*.sol"])
def test_a_listed_path_that_is_not_a_file_is_an_error_naming_it(repo: Path, bad: str):
    with pytest.raises(SystemExit, match=r"files\.paths: .*" + bad.replace("*", r"\*")):
        find_files(repo, FILES_CFG | {"paths": ["src/A.sol", bad]})


def test_heatmap_card_for_explicit_scope():
    run = copy.deepcopy(RUN)
    run["config"]["files"]["paths"] = [f["path"] for f in run["files"]]
    md = render_heatmap_md(build_heatmap(run, run_library(run)))
    assert f"| Scanned | {len(run['files'])} (explicit scope) |" in md
    assert "| Ignored |" not in md
