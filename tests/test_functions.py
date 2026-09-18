"""Splitter checks: python -m pytest tests/ (or run this file directly)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from functions import contract_context, split_functions  # noqa: E402
from jevscan import numbered_lines  # noqa: E402

EDGE = (Path(__file__).parent / "edge_cases.sol").read_text()


def test_edge_case_functions():
    found = [(f["kind"], f["name"], f["start_line"], f["end_line"]) for f in split_functions(EDGE)]
    assert found == [
        ("modifier", "onlyOwner", 19, 22),        # modifier without parentheses
        ("modifier", "gated", 24, 24),
        ("constructor", "constructor", 26, 26),
        ("function", "thing", 28, 41),            # unchecked {}, assembly {}, braces in comments/strings
        ("receive", "receive", 45, 45),           # interface `receive() ...;` has no body: skipped
        ("fallback", "fallback", 47, 47),
        ("function", "f", 53, 53),                # `x.receive()` inside the body is not a header
    ]


def test_edge_case_context():
    context = contract_context(EDGE, split_functions(EDGE))
    assert "uint256 public total;" in context
    assert "modifier onlyOwner" in context and "modifier gated" in context
    assert "function abstractish() external virtual;" in context
    assert "unchecked" not in context and "constructor" not in context
    assert "fake function" not in context  # comments stripped
    assert "'} also not a brace \\' still string }'" in context  # strings kept


def test_line_numbers_ignore_unicode_line_separators():
    # U+2028 and \x0c are line breaks to str.splitlines() but not to solc or to "\n" offsets.
    source = "contract C {\n    // odd \u2028 comment \x0c here\n    function f() external {\n        x = 1;\n    }\n}\n"
    [f] = split_functions(source)
    assert (f["start_line"], f["end_line"]) == (3, 5)
    assert f["text"].startswith("    function f()") and f["text"].rstrip().endswith("}")
    text, options = numbered_lines(f)
    assert text.split("\n")[1] == "L4:         x = 1;"
    assert options == {"L3": "function f() external {", "L4": "x = 1;", "L5": "}"}
    file_lines = source.split("\n")
    assert all(file_lines[int(k[1:]) - 1].strip() == v for k, v in options.items())


if __name__ == "__main__":
    test_edge_case_functions()
    test_edge_case_context()
    test_line_numbers_ignore_unicode_line_separators()
    print("ok")
