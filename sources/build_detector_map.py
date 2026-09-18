"""One-time build: assign each detector to 1-3 taxonomy subcategories with an LLM; writes sources/detector_map.json.

    python sources/build_detector_map.py
Needs OPENROUTER_API_KEY. The benchmarks score a detector against an issue
through this map (a detector counts for the subcategories it is mapped to).
"""

import asyncio
import json
import os
import sys

import aiohttp

from sync import CONCURRENCY, MODEL, ROOT, SOURCES, openrouter_chat
from config import load_dotenv

MAP_PATH = SOURCES / "detector_map.json"
BATCH_SIZE = 25
MAP_ATTEMPTS = 3

INSTRUCTIONS = """You map smart-contract vulnerability detectors onto a fixed two-level taxonomy.

For each detector, choose the 1 to 3 subcategory ids (from the taxonomy below) whose bugs the detector is most likely to find. Pick the single best fit first; add a second or third only if the detector genuinely spans them. Use only the bare subcategory ids shown after "- " in the taxonomy, exactly as written, without the category prefix (for example "spot_price_dependency", not "oracle_price_manipulation:spot_price_dependency"). Even detectors for other ecosystems (Solana, Cosmos, C, node software) must get the closest subcategory.

Return ONLY a JSON object (no prose, no code fences) mapping every detector name you were given to a list of subcategory ids.

Taxonomy (category, then its subcategories):
"""


def taxonomy_outline(taxonomy: dict) -> str:
    lines = []
    for c in taxonomy["categories"]:
        lines.append(f"{c['id']}: {c['name']}. {c['description']}")
        lines += [f"  - {s['id']}: {s['description']}" for s in c["subcategories"]]
    return "\n".join(lines)


async def map_batch(session, sem, outline: str, detectors: list[dict], valid: set[str]) -> dict[str, list[str]]:
    user = "Detectors:\n" + "\n".join(f"- {d['name']}: {d['description']} {d['question']}" for d in detectors)
    body = {
        "model": MODEL,
        "max_tokens": 16000,  # the model reasons first; 4000 sometimes left no room for the answer
        "messages": [{"role": "system", "content": INSTRUCTIONS + outline}, {"role": "user", "content": user}],
    }
    for attempt in range(MAP_ATTEMPTS):  # the model occasionally drops or renames a detector; ask again
        content = await openrouter_chat(session, sem, body, f"batch starting {detectors[0]['name']}")
        try:
            return parse_mapping(content, {d["name"] for d in detectors}, valid)
        except ValueError:
            if attempt == MAP_ATTEMPTS - 1:
                raise


def parse_mapping(content: str | None, names: set[str], valid: set[str]) -> dict[str, list[str]]:
    if not content or "{" not in content:
        raise ValueError(f"no JSON object in LLM output: {(content or '')[:300]!r}")
    mapping = json.loads(content[content.index("{") : content.rindex("}") + 1])
    if set(mapping) != names:
        raise ValueError(f"LLM mapped {sorted(set(mapping) ^ names)} unexpectedly")
    for name, subs in mapping.items():
        if not (1 <= len(subs) <= 3 and set(subs) <= valid):
            raise ValueError(f"{name}: invalid subcategories {subs}")
    return mapping


async def main() -> None:
    taxonomy = json.loads((SOURCES / "taxonomy.json").read_text())
    valid = {s["id"] for c in taxonomy["categories"] for s in c["subcategories"]}
    detectors = [json.loads(p.read_text()) for p in sorted((ROOT / "detectors").glob("*.json"))]
    batches = [detectors[i : i + BATCH_SIZE] for i in range(0, len(detectors), BATCH_SIZE)]
    print(f"{len(detectors)} detectors in {len(batches)} batches")

    sem = asyncio.Semaphore(CONCURRENCY)
    headers = {"Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}"}
    async with aiohttp.ClientSession(headers=headers, timeout=aiohttp.ClientTimeout(total=300)) as session:
        results = await asyncio.gather(
            *(map_batch(session, sem, taxonomy_outline(taxonomy), b, valid) for b in batches), return_exceptions=True
        )
    failures = [r for r in results if isinstance(r, BaseException)]
    for failure in failures:
        print(f"FAILED: {failure!r}", file=sys.stderr)
    if failures:
        raise SystemExit(f"{len(failures)} batches failed; re-run")
    mapping = {name: subs for r in results for name, subs in r.items()}
    MAP_PATH.write_text(json.dumps(dict(sorted(mapping.items())), indent=2) + "\n")
    unmapped = sorted(valid - {s for subs in mapping.values() for s in subs})
    print(f"wrote {MAP_PATH} ({len(mapping)} detectors); subcategories with no detector: {unmapped}")


if __name__ == "__main__":
    load_dotenv()
    asyncio.run(main())
