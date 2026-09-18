"""Sync the detector library with the pinned public sources in sources/.

    python sources/sync.py                 # generate detectors whose source text changed or that have no JSON yet
    python sources/sync.py --check         # fetch each source and list items changed upstream; generates nothing
    python sources/sync.py --force <name>  # regenerate one detector even if its source text is unchanged

Sources (git submodules, see sources/README.md): Cyfrin's Solodit audit checklist and the
vulnerability-pattern skills of EVM Cortex. detectors/*.json is the committed
cache of generated questions: each records the sha256 of its source item's text, and an item whose
hash matches is never sent to the LLM again. Items excluded by rule (sources/exclusions.json,
CORTEX_DROP) produce no detector; their JSON, if any, is deleted. Checklist items the
LLM judges process-only are recorded in sources/skipped.json. Needs OPENROUTER_API_KEY to generate.
"""

import argparse
import asyncio
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import aiohttp

SOURCES = Path(__file__).resolve().parent
ROOT = SOURCES.parent
sys.path.insert(0, str(ROOT))
from config import load_dotenv  # noqa: E402

OUT_DIR = ROOT / "detectors"
SKIPPED_PATH = SOURCES / "skipped.json"
MAP_PATH = SOURCES / "detector_map.json"
SOLODIT_EXCLUSIONS = json.loads((SOURCES / "exclusions.json").read_text())  # checklist id -> reason
MODEL = "anthropic/claude-sonnet-5"
URL = "https://openrouter.ai/api/v1/chat/completions"
CONCURRENCY = 32
MAX_ATTEMPTS = 6
LINT_ATTEMPTS = 3  # re-ask the LLM when its criteria fail the lint or the sufficiency check
# A criterion is sent to Jev as an example of code that makes the question true, so it must describe the flaw
# itself. These openings mark a gate, an exclusion, or a missing mitigation, none of which is sufficient alone.
BAD_CRITERION_STARTS = ("No ", "Absence", "Excludes", "Lacks", "Implements", "Uses")

# EVM Cortex skills that describe vulnerability patterns or security pitfalls. CORTEX_DROP holds the rest
# (tooling, process, how-to, or gas guidance); --check reports skills in neither.
CORTEX_SKILLS = [
    "aave-integration", "access-control-patterns", "assembly-patterns", "beacon-proxy",
    "cctp-bridging", "chainlink-oracles", "compound-patterns", "constructor-patterns",
    "create2-patterns", "cross-chain-security", "curve-integration", "delegate-call-risks",
    "denial-of-service", "diamond-pattern", "dutch-auction-patterns", "economic-attack-vectors",
    "eip712-signing", "erc1155-patterns", "erc20-patterns", "erc4626-patterns", "erc721-patterns",
    "erc7702-patterns", "error-handling", "flash-loan-attacks", "front-running-patterns",
    "governance-attacks", "integer-overflow", "liquidity-mining",
    "minimal-proxy", "oracle-manipulation", "proxy-patterns", "reentrancy-patterns",
    "signature-vulnerabilities", "solidity-patterns", "solidity-security",
    "staking-reward-patterns", "storage-layout", "time-manipulation", "token-bonding-curves",
    "token-integration-safety", "uniswap-v4-hooks", "upgrade-safety", "usdc-integration",
    "yield-vault-patterns",
]

CORTEX_DROP = {
    "aderyn-analysis", "anvil-patterns", "audit-breadth-scan", "audit-depth-analysis", "audit-prep", "audit-recon",
    "audit-report-generation", "audit-verification", "blockscout-mcp", "cast-commands", "contract-verification",
    "coverage-analysis", "dapp-frontend-patterns", "erc8004-patterns", "event-design", "fizz", "fizz-convert",
    "fizz-sync", "flash-loan-usage", "forge-scripting", "fork-testing", "formal-verification", "foundry-setup",
    "foundry-testing", "fuzzing-patterns", "gas-optimization", "gas-snapshot-testing", "governance-patterns",
    "immutable-constants", "interface-design", "invariant-testing", "ipfs-deployment", "l2-deployment",
    "library-patterns", "lp-analyst", "multichain-deployment", "natspec-standards",
    "pool-finder", "scaffold-eth-patterns", "slither-analysis", "subgraph-patterns",
    "test-fixtures", "type-driven-design", "uniswap-math", "uniswap-v3-expert", "uniswap-v4-expert",
    "uniswap-v4-testing", "wallet-integration", "xray-pre-audit",
}

CORTEX_DROP_SUFFIXES = ("-audit-pipeline",)  # named auditors' end-to-end workflow skills: process, not a vulnerability pattern


def cortex_dropped_by_rule(skill: str) -> bool:
    return skill.endswith(CORTEX_DROP_SUFFIXES)


INSTRUCTIONS = """You convert one security source (an audit checklist item or a security skill document) into a compact yes/no question for a literal-minded binary classifier.

The classifier sees one JSON object `{"source": "<full text of ONE source file>"}` and judges whether a statement is true. It reads instructions literally, has no cross-file context, and cannot run code.

Return ONLY a JSON object (no prose, no code fences) with these keys:
- "description": one line (<= 20 words) naming the vulnerability class.
- "question": ONE self-contained declarative statement of at most ~120 words, to be judged true/false, that begins with "The source file in `source`" and is TRUE when the flaw is present. Checklist items are often phrased as questions about a safeguard ("Is there a check for X?"); turn them into a statement about the flawed code ("... performs Y without checking X, so ..."), never a question. It must encode (a) the applicability gate (what code must be present for the check to apply), (b) the minimum true-positive conditions (the concrete flaw and its security impact), and (c) the exclusions: the false-positive cases the source says not to report or that are clearly safe (trusted-admin powers, mitigated variants), phrased so they do not satisfy the statement. Name the concrete flaw, not "a vulnerability". Keep it language-neutral ("source file", not "Solidity file") unless the source is inherently about one language, compiler, or ecosystem, in which case name it. When the flaw can show up in alternative ways (for example a swap with no minimum-output limit, or with no deadline), join the alternatives with "or", never "and": the statement must be true when any one of them is present. Join conditions with "and" only when each is a genuine precondition that must hold for the flaw to exist.
- "criteria": 2 to 6 short strings. They are shown to the classifier as "examples of code that makes it true", so EACH criterion on its own must describe a complete, concrete instance of the flawed code: the vulnerable operation together with the missing or wrong check that makes it exploitable (for example "withdraw() sends ETH with call{value:} before setting balances[msg.sender] = 0, with no reentrancy guard"). Any one criterion alone must be enough to make the question true; give each alternative manifestation its own criterion. A criterion must never be only an applicability condition ("the contract implements ERC-4626"), only a missing mitigation ("no reentrancy guard"), or an exclusion ("excludes admin-only functions"); those belong in the question. Do not start a criterion with "No ", "Absence", "Excludes", "Lacks", "Implements", or "Uses".

Some checklist items are pure process, documentation, testing, deployment-operations, or off-chain checks that no single source file's code can make true or false (for example "Is the protocol documented?", "Are all tests passing?", "Was the multisig configured correctly off-chain?"). For those, and only those, return instead {"skip": "<one-line reason>"}."""


CHECK_INSTRUCTIONS = """You review a yes/no question written for a literal-minded binary classifier that judges it against one source file. The criteria are shown to the classifier as examples of code that makes the question true.

Check two things:
1. Each criterion on its own is enough to make the question true: a file containing only that flawed code (plus whatever the question's applicability gate requires) satisfies every condition of the question.
2. The question does not join alternative manifestations of the flaw with "and" (for example requiring both a missing slippage limit and a missing deadline, when either alone is the flaw). "And" is fine between genuine preconditions that must all hold.

Return ONLY a JSON object: {"ok": true} if both hold, otherwise {"ok": false, "problem": "<one or two sentences naming the criterion or the joined conditions and what to change>"}."""


def slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")


def git(repo: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True, text=True).stdout


def text_hash(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()[:16]


def solodit_items(rev: str) -> list[dict]:
    repo = SOURCES / "audit-checklist"
    commit = git(repo, "rev-parse", rev).strip()
    items, ids = [], []

    def walk(nodes: list[dict], path: list[str]) -> None:
        for node in nodes:
            if "question" in node:
                text = json.dumps({"category": " / ".join(path), **node}, indent=1)
                ids.append(node["id"])
                items.append({
                    "id": node["id"],
                    "name": slug(node["id"]),
                    "source": "solodit",
                    "origin": f"Cyfrin/audit-checklist@{commit[:12]} checklist.json id={node['id']}",
                    "tags": [path],
                    "text": text,
                })
            else:
                walk(node["data"], path + [node["category"]])

    walk(json.loads(git(repo, "show", f"{rev}:checklist.json")), [])
    unknown = set(SOLODIT_EXCLUSIONS) - set(ids)
    if unknown:
        raise SystemExit(f"exclusions.json names ids not in the checklist: {sorted(unknown)}")
    return [i for i in items if i["id"] not in SOLODIT_EXCLUSIONS]


def cortex_items(rev: str) -> list[dict]:
    repo = SOURCES / "evm-cortex"
    commit = git(repo, "rev-parse", rev).strip()
    return [
        {
            "name": slug(skill),
            "source": "evm-cortex",
            "origin": f"ccashwell/evm-cortex@{commit[:12]} skills/{skill}/SKILL.md",
            "tags": [],
            "text": git(repo, "show", f"{rev}:skills/{skill}/SKILL.md"),
        }
        for skill in CORTEX_SKILLS
    ]


LOADERS = {"audit-checklist": solodit_items, "evm-cortex": cortex_items}


def all_items(rev: str = "HEAD") -> list[dict]:
    items = [i for load in LOADERS.values() for i in load(rev)]
    names = [i["name"] for i in items]
    dupes = {n for n in names if names.count(n) > 1}
    if dupes:
        raise SystemExit(f"duplicate detector names: {sorted(dupes)}")
    for item in items:
        item["source_hash"] = text_hash(item["text"])
    return items


def check() -> None:
    """Fetch each submodule's upstream branch and list items added, removed, or changed since the pinned commit."""
    for sub, load in LOADERS.items():
        repo = SOURCES / sub
        branch = git(ROOT, "config", "-f", ".gitmodules", f"submodule.sources/{sub}.branch").strip()
        git(repo, "fetch", "origin", branch)
        pinned = git(repo, "rev-parse", "HEAD").strip()
        upstream = git(repo, "rev-parse", "FETCH_HEAD").strip()
        print(f"{sub}: pinned {pinned[:12]}, upstream {branch} {upstream[:12]}")
        if pinned == upstream:
            continue
        old = {i["name"]: text_hash(i["text"]) for i in load("HEAD")}
        new = {i["name"]: text_hash(i["text"]) for i in load("FETCH_HEAD")}
        for label, names in (("added", new.keys() - old.keys()), ("removed", old.keys() - new.keys()),
                             ("changed", {n for n in old.keys() & new.keys() if old[n] != new[n]})):
            for name in sorted(names):
                print(f"  {label}: {name}")
        if sub == "evm-cortex":
            skills = {p.split("/")[1] for p in git(repo, "ls-tree", "-r", "--name-only", "FETCH_HEAD", "skills").split()
                      if p.count("/") >= 2}
            for skill in sorted(skills - set(CORTEX_SKILLS) - CORTEX_DROP):
                if cortex_dropped_by_rule(skill):
                    continue
                print(f"  unclassified skill (add to CORTEX_SKILLS or CORTEX_DROP): {skill}")


class LintError(ValueError):
    pass


def parse_detector(content: str | None, item: dict) -> dict:
    if not content or "{" not in content:
        raise ValueError(f"{item['name']}: no JSON object in LLM output: {(content or '')[:300]!r}")
    data = json.loads(content[content.index("{") : content.rindex("}") + 1])
    if "skip" in data:
        if item["source"] != "solodit":
            raise ValueError(f"{item['name']}: only checklist items may be skipped: {data['skip']}")
        return data
    criteria = data["criteria"]
    if not (isinstance(data["question"], str) and isinstance(criteria, list) and 2 <= len(criteria) <= 6):
        raise ValueError(f"{item['name']}: malformed LLM output: {content[:300]}")
    bad = [c for c in criteria if c.startswith(BAD_CRITERION_STARTS)]
    if bad:
        raise LintError(f"{item['name']}: criteria that are gates, exclusions, or absences, not flaw patterns: {bad}")
    return {
        "name": item["name"],
        "source": item["source"],
        "origin": item["origin"],
        "source_hash": item["source_hash"],
        "description": data["description"],
        "question": data["question"],
        "criteria": criteria,
        "tags": item["tags"],
    }


async def openrouter_chat(session: aiohttp.ClientSession, sem: asyncio.Semaphore, body: dict, label: str) -> str:
    """POST a chat completion with retries on 429/5xx; return the message content."""
    async with sem:
        for attempt in range(MAX_ATTEMPTS):
            async with session.post(URL, json=body) as resp:
                if resp.status == 429 or resp.status >= 500:
                    await asyncio.sleep(float(resp.headers.get("retry-after", 2**attempt)))
                    continue
                if resp.status != 200:
                    raise RuntimeError(f"{label}: HTTP {resp.status}: {await resp.text()}")
                payload = await resp.json()
                return payload["choices"][0]["message"]["content"]
    raise RuntimeError(f"{label}: gave up after {MAX_ATTEMPTS} retryable errors")


async def sufficiency_problem(session: aiohttp.ClientSession, sem: asyncio.Semaphore, detector: dict) -> str | None:
    """An LLM review: None when every criterion alone makes the question true and no alternatives are ANDed."""
    criteria = "\n".join(f"- {c}" for c in detector["criteria"])
    body = {
        "model": MODEL,
        "max_tokens": 4000,
        "messages": [
            {"role": "system", "content": CHECK_INSTRUCTIONS},
            {"role": "user", "content": f"Question: {detector['question']}\n\nCriteria:\n{criteria}"},
        ],
    }
    content = await openrouter_chat(session, sem, body, f"check {detector['name']}")
    if not content or "{" not in content:
        raise ValueError(f"{detector['name']}: no JSON object in check output: {(content or '')[:300]!r}")
    verdict = json.loads(content[content.index("{") : content.rindex("}") + 1])
    return None if verdict["ok"] else verdict["problem"]


async def distill(session: aiohttp.ClientSession, sem: asyncio.Semaphore, item: dict, skipped: dict) -> None:
    body = {
        "model": MODEL,
        "max_tokens": 4000,
        "messages": [
            {"role": "system", "content": INSTRUCTIONS},
            {"role": "user", "content": f"Source ({item['source']}, {item['origin']}):\n\n{item['text']}"},
        ],
    }
    for attempt in range(LINT_ATTEMPTS):
        content = await openrouter_chat(session, sem, body, item["name"])
        try:
            result = parse_detector(content, item)
            if "skip" not in result and (problem := await sufficiency_problem(session, sem, result)):
                raise LintError(f"{item['name']}: {problem}")
            break
        except LintError as e:
            if attempt == LINT_ATTEMPTS - 1:
                raise
            body["messages"] += [{"role": "assistant", "content": content},
                                 {"role": "user", "content": f"Rejected: {e}. Make every criterion a complete "
                                  "flawed-code pattern that alone makes the question true, join alternative "
                                  "manifestations with \"or\", and keep gates and exclusions in the question. "
                                  "Return the whole JSON object again."}]
    path = OUT_DIR / f"{item['name']}.json"
    if "skip" in result:
        path.unlink(missing_ok=True)
        skipped[item["name"]] = {"origin": item["origin"], "source_hash": item["source_hash"], "reason": result["skip"]}
        SKIPPED_PATH.write_text(json.dumps(dict(sorted(skipped.items())), indent=2) + "\n")
        print(f"skipped {item['source']}/{item['name']}: {result['skip']}")
        return
    skipped.pop(item["name"], None)
    path.write_text(json.dumps(result, indent=2) + "\n")
    print(f"built {item['source']}/{item['name']}")


async def sync(force: str | None) -> None:
    items = all_items()
    if force and force not in {i["name"] for i in items}:
        raise SystemExit(f"--force {force}: no such source item (excluded items cannot be forced)")
    OUT_DIR.mkdir(exist_ok=True)
    skipped = json.loads(SKIPPED_PATH.read_text()) if SKIPPED_PATH.exists() else {}
    current = {i["name"] for i in items}
    for path in OUT_DIR.glob("*.json"):
        if path.stem not in current:
            path.unlink()
            print(f"removed {path.stem} (excluded, or no longer in the sources)")
    skipped = {n: s for n, s in skipped.items() if n in current}
    detector_map = json.loads(MAP_PATH.read_text())
    kept = {n: subs for n, subs in detector_map.items() if (OUT_DIR / f"{n}.json").exists()}
    if kept != detector_map:
        MAP_PATH.write_text(json.dumps(kept, indent=2) + "\n")
        print(f"dropped {len(detector_map) - len(kept)} removed detectors from {MAP_PATH.name}")

    def done(item: dict) -> bool:
        if item["name"] == force:
            return False
        path = OUT_DIR / f"{item['name']}.json"
        if path.exists():
            return json.loads(path.read_text()).get("source_hash") == item["source_hash"]
        return skipped.get(item["name"], {}).get("source_hash") == item["source_hash"]

    todo = [i for i in items if not done(i)]
    print(f"{len(items)} source items, {len(todo)} to generate")

    sem = asyncio.Semaphore(CONCURRENCY)
    headers = {"Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}"}
    async with aiohttp.ClientSession(headers=headers, timeout=aiohttp.ClientTimeout(total=300)) as session:
        results = await asyncio.gather(*(distill(session, sem, i, skipped) for i in todo), return_exceptions=True)
    SKIPPED_PATH.write_text(json.dumps(dict(sorted(skipped.items())), indent=2) + "\n")
    failures = [r for r in results if isinstance(r, BaseException)]
    for failure in failures:
        print(f"FAILED: {failure!r}", file=sys.stderr)
    if failures:
        raise SystemExit(f"{len(failures)} detectors failed; re-run to retry them")
    if todo:
        print("detectors changed: run sources/build_detector_map.py before scanning")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true", help="list source items changed upstream; generate nothing")
    parser.add_argument("--force", metavar="NAME", help="regenerate this detector even if its source text is unchanged")
    args = parser.parse_args()
    load_dotenv()
    if args.check:
        check()
    else:
        asyncio.run(sync(args.force))
