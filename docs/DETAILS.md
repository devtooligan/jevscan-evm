# jevscan-evm: technical details

The [README](../README.md) is the short version. Settings and output files are in [CONFIG.md](CONFIG.md). This page covers how a scan works, the output files, the benchmarks, speed and cost, and how the detector questions are built.

## How a scan works

1. **Find files.** Every file under `files.scope` with one of `files.extensions`, minus `files.skip_dirs` (vendored code).
2. **Classify.** One Jev Choice question per file reads its path and first 60 lines and picks a class (`source`, `interface`, `test`, `script`, `mock`). Only classes in `classes.scan` are scanned; `files.include_globs` forces files in. Every dropped file is printed with its class.
3. **Scan.** Each file gets every question of the levels turned on. The state is `{"source": <file>}`.
4. **Locate** (`run.locate`). Every non-broad question with file-level p ≥ `thresholds.locate` is asked again once per function. Where the function-level p also reaches it, a Choice question picks the vulnerable line.
5. **Repo level** (`run.repo_level`). If all scanned files fit in one request (about 28k tokens), the broad and category questions are asked once about the whole codebase, plus a Choice of the most suspicious file.
6. **Write outputs.** `results.json` is written after the scan and again at the end, so a failure while locating cannot lose the scan. `python render.py <out_dir>` rebuilds every other output from it without calling Jev.

## Output files

Outputs go to `out/<repo name>/`, or `--out <dir>`. Field-level detail is in [CONFIG.md](CONFIG.md#output-files).

| File | What it holds |
|---|---|
| `HEATMAP.md` | Verdict, the grid, and every function with a hit. Start here. |
| `findings.json` | One entry per likely issue, in a simple JSON shape. |
| `report.md` | Every hit and every table. |
| `jevheatmap.json` | The heat map as data. |
| `results.json` | Every probability. `python render.py <out dir>` rebuilds the rest from it. |

## HEATMAP.md

`heatmap.py` renders it from the same data as `jevheatmap.json`. Every number is a percentage: Jev's probability that the statement is true.

1. **Verdict.** Chance of a critical bug, chance of any exploitable bug, and the hottest file, from the repo-level answers (the per-file maximum when the scope does not fit one request).
2. **Codebase card.** Name, files found, non-blank lines of the scanned files, files scanned, files ignored by class, files over the size cap. Then requests, cost, and wall time, and any setting that differs from `jevscan.toml`.
3. **Heat grid.** One row per scanned file, sorted by its highest cell; columns Crit, Any, and the 14 categories. Cells are colors only: 🟥 85% or more (very likely), 🟧 70% to 85% (likely), 🟨 hit threshold to 70% (leaning yes), 🟩 30% to the hit threshold (possible), ⬜ under 30%. A legend explains each color; what each column means is in a collapsed block.
4. **Strongest function hits.** Every located function whose strongest category or detector hit reaches `thresholds.strong_hits` (70%), one row per function.
5. **File details.** One collapsed block per flagged file: each function with a hit (at or over the hit threshold) with its strongest hit and the rest under "More", then the file-level hits. Files with no hit are listed once as low risk.
6. **Ignored files.** The files not scanned, with their class or "over the size cap", in a collapsed block.

`bench/run_bench.py` re-renders the benchmark's `HEATMAP.md` with an answer key: a `Corresponding findings` column with the known findings (most severe first) whose file, function, and bug type match one of that function's hits (a finding that names no function is never listed against a function), and a known-findings table (found or not, the chance, and the location: the function and line pointed at). A finding counts as found from any function hit at or over the hit threshold, not only the strongest-hits rows. A finding that names no function counts as found only from a category hit in any function of its file, never from a detector hit. A finding's bug type is its category plus every detector mapped to that part of the taxonomy. After the known findings comes a list of flags without a known finding, at 70% and 50%. A flag is a file whose chance for a bug category is at or over the threshold; a flag without a known finding is one where the contest reported no finding of that category in that file. These may be unreported issues or false positives; none were verified.

## Questions

Every question has an id `<level>:<name>`. A scanned file gets up to 359 of them:

| Level | Count | Source |
|---|---|---|
| broad | 2 | `any_bug` (any exploitable vulnerability) and `critical_bug` (an attacker gains value at the protocol's or users' expense) |
| category | 14 | [`taxonomy.json`](../sources/taxonomy.json), described in [`TAXONOMY.md`](TAXONOMY.md) |
| detector | 343 | `detectors/*.json`: 299 from the Solodit checklist, 44 from [evm-cortex skills](https://github.com/ccashwell/evm-cortex) by Chris Cashwell (MIT) |

Detector questions are sent as the question, then "It is true when the file matches the description above; the following are examples of code that makes it true:", then the code patterns. That wording makes the list examples of the flaw, not a checklist where any one condition would do.

Located questions are reworded so they name only what the request holds. "The source file in `source`" becomes "The function in `function` (with its contract's declarations in `contract_context`)", and every other "the file" becomes "the function".

## Locating functions and lines

`functions.py` splits Solidity with a header regex (`function`, `modifier`, `constructor`, `receive`, `fallback`) and brace matching. It blanks comments and strings first, so braces inside them are ignored. Declarations without a body are skipped. Modifiers are not located.

The contract context is everything outside function bodies (pragma, imports, state variables, events, modifiers), without comments or blank lines, capped at about 4k tokens.

The line step numbers each line `L<n>: ` with its file line number. The options are the non-blank, non-comment lines. Functions with more than 60 such lines are skipped. The line step is experimental.

Only `.sol` files are located. Other scanned files keep file-level hits and are listed as not located.

`python functions.py <file.sol>` prints what the splitter finds. `python -m pytest tests` checks the edge cases in `tests/edge_cases.sol`.

## Requests, cache, and cost

- Questions are batched so each request stays under about 55k estimated tokens (characters / 3.5, which overestimates).
- `run.concurrency` requests (default 8) run at once. 429s are retried with `retry-after`; a 5xx is retried at most 3 times; anything else fails the run.
- `jev-latest` is resolved to a concrete version once per run. That version is pinned in every request, the cache key, and `results.json`, so a Jev upgrade cannot mix scores from two models.
- Answers are cached in `paths.cache_dir` under sha256(model + state + questions). A warm re-run costs one uncached probe request.
- Jev charges $0.042 per million input tokens. Every batch resends the file, and the detector level is most of the scan cost.

## Limits

- **Solidity only.** Other extensions can be scanned at file level, but only `.sol` files are located.
- **File size.** Files over 30k estimated tokens (about 26k real) are skipped and listed. Jev allows 32k for the state plus the longest question.
- **Literal reading.** Each statement is judged literally against one file. Broad checklist items (missing events, missing input validation) fire on ordinary code. Treat p as a ranking signal, not a verdict.
- **No cross-file context.** Interfaces can score high on "missing access control" because the modifiers live elsewhere. Bugs that span contracts are invisible.
- **The detector layer is noisier than the categories.** Generic checklist items cause most detector flags on files with no finding.
- **Every detector runs on every file.** Integration-specific items (Chainlink CCIP, LayerZero, Pyth) mostly score low on code that does not use them, but add tokens and some noise.
- **Noise.** The same request sent twice can differ by a few hundredths. A question's p also moves slightly with the other questions in its request; [`bench/BATCH_STABILITY.md`](../bench/BATCH_STABILITY.md) measured that at about the size of the repeat noise (~0.01, max 0.06). Treat a p within 0.05 of a threshold as a tie. A cold re-run can move recall near a threshold by a few issues, because several issues can share one (file, question) pair.

## Benchmarks

```sh
python bench/run_bench.py ussd            # scan and score (a few cents cold, free from cache)
python bench/run_bench.py ussd --score    # re-score the saved run
```

The harness scans with the default settings, so the benchmark measures what a user gets; `monolith` adds only `files.paths` (the contest scope list, in `bench/monolith/jevscan.toml`). It writes the run to `bench/<name>/run/` and the scores to `bench/<name>/results.md`.

| Name | Contest | Answer key |
|---|---|---|
| `ussd` | Sherlock USSD (2023-05), 22 H/M | [`bench/ussd/ground_truth.json`](../bench/ussd/ground_truth.json) |
| `beedle` | CodeHawks Beedle (2023-07), 26 H + 15 M | [`bench/beedle/ground_truth.json`](../bench/beedle/ground_truth.json) (42 entries; one duplicate) |
| `monolith` | Sherlock Monolith Stablecoin Factory (2025-12), 1 H + 6 M | [`bench/monolith/ground_truth.json`](../bench/monolith/ground_truth.json) |

Each ground-truth issue lists its files, functions, and a hand-assigned bug type.

**Results.** One run per contest, jev-1.13.0, default settings, 343 detectors. A finding counts when its file scores 50% or more on the finding's bug type.

| Contest | Right file + bug type @50% | Flags on files with no finding | Flags @70% not in the judged findings | Right function first (random) | Right function in top 3 (random) |
|---|---|---|---|---|---|
| [USSD](../bench/ussd/results.md) (Sherlock, May 2023, 22 findings) | 22/22 | 0 | 7 of 18 (not reviewed) | 14/21 (4.9) | 20/21 (11.0) |
| [Beedle](../bench/beedle/results.md) (CodeHawks, Jul 2023, 42 findings) | 34/42 | n/a (no such files) | 3 of 12 (not reviewed) | 14/34 (6.4) | 26/34 (14.7) |
| [Monolith](../bench/monolith/results.md) (Sherlock, Dec 2025, 7 findings) | 7/7 | 6 | 5 of 9: 2 real, 3 false positives | 3/7 (1.4) | 5/7 (2.1) |

- A flag is a file that scores at or over the threshold on a bug type: 50% in the "no finding" column, 70% in the next. A flag outside the judged findings is not automatically wrong. Monolith's five were checked by hand ([review A](../bench/monolith/unmatched_review_a.md), [review B](../bench/monolith/unmatched_review_b.md)): 2 were real bugs the contest did not count (one out of scope, one a view-only copy of a judged bug), 3 were false positives. So Monolith had 9 flags at 70%: 6 real, 3 false.
- Monolith is from December 2025, so it is the recency check: less likely to be in Jev's training data.
- On Beedle, six of the eight misses scored 0.49: three findings share one question on one file, and three share another. An earlier run scored the second group 0.52 and caught all three.
- The random baseline is the expected count if the function ranking were shuffled.

**Recall** counts an issue when any of its true (file, question) pairs passes the threshold. At detector level, a detector counts when [`detector_map.json`](../sources/detector_map.json) assigns it to the issue's bug type.

**Locating** is scored on one function ranking per issue: its true pair with the highest file-level p, chosen before looking at the ranking. The random baseline uses the same ranking.

`results.md` also scores the line step, the repo-level answers, and where each issue first appears in `HEATMAP.md`.

**Contamination.** USSD was re-scanned with comments blanked and every project identifier and file renamed (the renamed copy is in `bench/ussd/obfuscated/`); see [`bench/ussd/contamination.md`](../bench/ussd/contamination.md) (run 2026-09-18, before the config change; not re-run since).

[`bench/LIBRARY_NOTES.md`](../bench/LIBRARY_NOTES.md) has what we learned tuning the questions and pruning the library.

## Speed and cost

About 1¢ per scanned file, including locating functions and lines.

| Repo | Files (scanned) | Cost | Time |
|---|---|---|---|
| Monolith | 6 (6) | 7¢ | 6 s |
| USSD | 12 (8) | 7¢ | 7 s |
| Beedle | 12 (7) | 6¢ | n/a |
| 40-file lending protocol (private) | 40 (21) | 18¢ | 23 s |

Costs are for the 343-detector library. Times are from cold runs of the earlier 387-detector library, and so is the whole private-repo row; dropping 44 detectors cut cost by about 7%.

Jev answers in about 160 ms per request and costs $0.042 per million input tokens. Re-runs come from the local cache and cost one request.

One file (`USSD.sol`, 248 lines), the same 14 category questions, one call each:

| Model | Time | Cost |
|---|---|---|
| Jev (jev-1.13.0) | 0.74 s | 0.015¢ |
| GPT-5.6, high reasoning | 57 s | 3.9¢ |

## Syncing detectors with their sources

The sources are pinned git submodules under `sources/`. `detectors/*.json` is the committed output. The scanner reads those files and never calls an LLM; only a sync does.

```sh
git submodule update --init
# OPENROUTER_API_KEY in .env or the environment
python sources/sync.py --check          # what changed upstream; generates nothing
python sources/sync.py                  # generate new or changed items only
python sources/sync.py --force <name>   # regenerate one detector
python sources/build_detector_map.py    # after generating anything
```

- `sources/sync.py` reads each source at its pinned commit with `git show`, so it never runs source code.
- Solodit items come from `checklist.json`, minus `sources/exclusions.json`. evm-cortex items come from the `SKILL.md` files in `CORTEX_SKILLS`.
- Each detector records `source_hash`. Only items with no JSON or a changed hash go to the LLM (`anthropic/claude-sonnet-5` via OpenRouter).
- A second LLM call checks that every criterion alone makes the question true, and that alternatives are joined with "or". A failing detector is retried up to 3 times. Pure process checks go to `sources/skipped.json`.
- `sources/build_detector_map.py` assigns each detector to 1 to 3 parts of the taxonomy. The map drives detector recall in the benchmarks.

To take an upstream update: move the submodule, classify any new items, run the sync, rebuild the map, and commit the pointer with the regenerated files. [`sources/README.md`](../sources/README.md) has licenses and selection rules.

## Detector format

```json
{
  "name": "sol_am_dosa_1",
  "source": "solodit",
  "origin": "Cyfrin/audit-checklist@008855fe1798 checklist.json id=SOL-AM-DOSA-1",
  "source_hash": "sha256 prefix of the source text",
  "description": "One-line vulnerability class",
  "question": "The source file in `source` ... (gate + minimum true-positive conditions + exclusions)",
  "criteria": ["2-6 flawed-code patterns, each sufficient on its own"],
  "tags": [["Attacker's Mindset", "Denial-Of-Service(DOS) Attack"]]
}
```

Each criterion must describe a complete instance of the flaw. Gates ("implements ERC-4626"), bare absences ("no reentrancy guard"), and exclusions belong in the question. The sync rejects criteria that start with "No ", "Absence", "Excludes", "Lacks", "Implements", or "Uses".

## Next steps

Three things would move this forward: a larger benchmark of recent (2024 to 2025) contests as the headline number; building the detector map several times and keeping the majority assignment, to steady detector recall, then dropping detectors that never fire on a known finding; and feeding `jevheatmap.json` to an LLM auditor as its first pass, so it starts from the hottest files, functions, and bug types.
