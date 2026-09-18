# jevscan-evm configuration

## What to read first

1. `HEATMAP.md`: verdict, codebase card, a colors-only files × categories grid, the strongest function hits (70%+), one collapsed block per flagged file, then the ignored files.
2. `findings.json`: one finding per likely issue, in a simple JSON shape.
3. `report.md`: every hit, with the full tables collapsed.

## Command line

```
python jevscan.py <repo_path> [--config my.toml] [--out DIR]        # scan (needs TYPESAFE_API_KEY)
python render.py <out_dir>                                          # rebuild the outputs from results.json, no Jev calls
```

- `--config FILE`: your settings, laid over [`jevscan.toml`](../jevscan.toml). Without it, `jevscan.toml` applies as is.
- `--out DIR`: the output directory. Defaults to `<paths.out_dir>/<repo name>`.

A user config needs only the keys it changes. An unknown key, a wrong type, or an inconsistent setting stops the run with an error. Relative paths resolve against the jevscan-evm directory. Answers are cached, so re-running with the same settings costs one uncached probe request.

`render.py` reads the settings recorded in `results.json`. It fails on a `results.json` written before the config file existed; re-run that scan (from the cache) to rewrite it.

## Keys

[`jevscan.toml`](../jevscan.toml) holds every key with its default.

| Key | Default | Meaning |
|---|---|---|
| `files.scope` | `""` | Subdirectory of the repo to scan; `""` scans the whole repo. Output paths are relative to it. |
| `files.extensions` | `[".sol"]` | File extensions to consider. |
| `files.skip_dirs` | `["lib", "node_modules"]` | Directories, relative to the repo root, whose files are never considered. |
| `files.include_globs` | `[]` | Scan files matching these globs (relative to the scope) whatever class they are in. |
| `files.paths` | `[]` | Exact files to scan, relative to the repo root (files only; no directories or globs). When non-empty it is the whole scan list: `files.scope`, `files.extensions`, `files.skip_dirs`, `files.include_globs`, and the file classification are bypassed, and every listed file is scanned as `source`. A path that is not a file stops the run with an error naming it. Paste a contest's scope list here. |
| `classes.scan` | `["source"]` | Which classes are scanned. Each must be a key of `classes.descriptions`. |
| `classes.descriptions` | source, interface, test, script, mock | Class name → the description Jev chooses between (it reads the path and first 60 lines). Setting this table replaces it whole. |
| `levels.broad` | `true` | Ask `any_bug` and `critical_bug`. Needed for the verdict and `run.repo_level`. |
| `levels.category` | `true` | Ask the 14 taxonomy categories. |
| `levels.subcategory` | `false` | off by default; noisy in testing |
| `levels.detector` | `true` | Ask the detector library, from the sources turned on. |
| `sources.solodit` | `true` | Detectors from the Cyfrin audit checklist. |
| `sources.evm-cortex` | `true` | Detectors from EVM Cortex skills. |
| `thresholds.taxonomy` | `0.5` | Hit threshold for broad and category questions, and any other taxonomy levels turned on. |
| `thresholds.detectors` | `0.5` | Hit threshold for detectors. |
| `thresholds.locate` | `0.5` | Locate every question whose file-level p is at least this; the line step uses it for the function-level p. |
| `thresholds.strong_hits` | `0.7` | HEATMAP.md's "Strongest function hits" table lists a function when its strongest hit is at least this; weaker hits stay in the per-file details. |
| `run.locate` | `true` | Re-ask located questions once per function, then ask which line (experimental). Solidity only. |
| `run.repo_level` | `true` | Also ask the broad and category questions about the whole scope in one request, when it fits (~28k tokens). |
| `run.concurrency` | `8` | Jev requests in flight at once. |
| `paths.detectors_dir` | `"detectors"` | Detector JSON files. |
| `paths.cache_dir` | `"cache"` | Jev answer cache. |
| `paths.out_dir` | `"out"` | Parent directory of the default output directory. |

## Output files

| File | Contents |
|---|---|
| `HEATMAP.md` | Verdict in percentages; codebase card (files found, lines of code, scanned, ignored by class); run cost and settings changed from the defaults; a colors-only grid of files × Crit, Any, and the 14 categories, with a legend; every function whose strongest hit reaches `thresholds.strong_hits`, one row each; one collapsed block per flagged file (every function hit, file-level hits); a low-risk file list; the ignored files. Details in [DETAILS.md](DETAILS.md#heatmapmd). |
| `findings.json` | Findings in that simple JSON shape, one per (file, top function) with a hit. |
| `report.md` | Likely issues and hits first; files by risk, classification, category matrices, detector hits, and located functions in collapsed blocks. |
| `jevheatmap.json` | The heat map as data: per file its line count, every category p, and every other question at or over its hit threshold; per function its p and chosen line for those questions; files not scanned and why; category names; question descriptions; settings and changes from the defaults; run stats. |
| `results.json` | The raw run: resolved settings (`config`), scan root, classification, every question's p per file, `located` rows per question, per-phase usage. The input to `render.py`. |

File risk is max(critical_bug, top category p). Line numbers are file line numbers.
