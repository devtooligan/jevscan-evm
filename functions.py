"""Split a Solidity file into functions, and extract the contract-level context around them.

Headers are found with a regex, and each body is matched brace by brace. Comments and string
literals are blanked out first, so braces inside them are ignored.

    python functions.py <file.sol> [...]   # print the functions found in each file
"""

import re
import sys
from pathlib import Path

CONTEXT_TOKEN_CAP = 4_000
# `function foo` / `modifier foo`, or `constructor(` / `receive(` / `fallback(`; not `x.receive(`.
HEADER = re.compile(r"(?<![.\w])(?:(function|modifier)\s+(\w+)|(constructor|receive|fallback)(?=\s*\())")
LEXEME = re.compile(r'//[^\n]*|/\*.*?\*/|"(?:\\.|[^"\\\n])*"|\'(?:\\.|[^\'\\\n])*\'', re.S)


def mask(source: str, strings: bool = True) -> str:
    """Replace comments (and string literals, if `strings`) with spaces, keeping newlines and offsets."""

    def blank(m: re.Match) -> str:
        text = m.group()
        if not strings and text[0] in "\"'":
            return text
        return re.sub(r"[^\n]", " ", text)

    return LEXEME.sub(blank, source)


def find_body(code: str, pos: int) -> int | None:
    """Return the index of the header's opening body brace, or None if it ends with `;` (no body)."""
    depth = 0
    for i in range(pos, len(code)):
        c = code[i]
        if c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
        elif depth == 0 and c == "{":
            return i
        elif depth == 0 and c == ";":
            return None
    raise ValueError(f"unterminated header at offset {pos}")


def match_brace(code: str, open_pos: int) -> int:
    depth = 0
    for i in range(open_pos, len(code)):
        if code[i] == "{":
            depth += 1
        elif code[i] == "}":
            depth -= 1
            if depth == 0:
                return i
    raise ValueError(f"unbalanced braces from offset {open_pos}")


def split_functions(source: str) -> list[dict]:
    """Return [{name, kind, start_line, end_line, text}] for every function and modifier with a body."""
    code = mask(source)
    lines = source.split("\n")  # "\n" only, like the offsets below; splitlines() also splits on U+2028 etc.
    found, pos = [], 0
    while m := HEADER.search(code, pos):
        body = find_body(code, m.end())
        if body is None:
            pos = m.end()
            continue
        end = match_brace(code, body)
        start_line = code.count("\n", 0, m.start()) + 1
        end_line = code.count("\n", 0, end) + 1
        found.append({
            "name": m.group(2) or m.group(3),
            "kind": m.group(1) or m.group(3),
            "start_line": start_line,
            "end_line": end_line,
            "text": "\n".join(lines[start_line - 1 : end_line]),
        })
        pos = end + 1
    return found


def contract_context(source: str, functions: list[dict]) -> str:
    """Everything at contract scope except function definitions (modifiers are kept), without
    comments or blank lines, capped to about CONTEXT_TOKEN_CAP tokens."""
    inside = {n for f in functions if f["kind"] != "modifier" for n in range(f["start_line"], f["end_line"] + 1)}
    kept = [
        line.rstrip()
        for n, line in enumerate(mask(source, strings=False).split("\n"), start=1)
        if n not in inside and line.strip()
    ]
    text = "\n".join(kept)
    max_chars = int(CONTEXT_TOKEN_CAP * 3.5)
    if len(text) > max_chars:
        print(f"WARNING: contract context is ~{len(text) / 3.5:,.0f} tokens; truncating to {CONTEXT_TOKEN_CAP:,}")
        text = text[:max_chars] + "\n// ... [contract context truncated]"
    return text


if __name__ == "__main__":
    for arg in sys.argv[1:]:
        print(arg)
        for f in split_functions(Path(arg).read_text()):
            print(f"  {f['kind']:<11} {f['name']:<40} L{f['start_line']}-{f['end_line']}")
