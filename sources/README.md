# Detector sources

Everything that builds the detector library in [`../detectors/`](../detectors) lives here. The scanner only reads `taxonomy.json`, `detector_map.json`, and the detectors; nothing here runs during a scan.

| File | What it is |
|---|---|
| `audit-checklist/`, `evm-cortex/` | The two upstream sources, pinned as git submodules. |
| `sync.py` | Turns each source item into a detector question with an LLM; only new or changed items are sent. |
| `build_detector_map.py` | Assigns each detector to 1 to 3 parts of the taxonomy; writes `detector_map.json`. |
| `taxonomy.json` | The 14 bug categories and their questions ([docs/TAXONOMY.md](../docs/TAXONOMY.md)). |
| `detector_map.json` | Detector → taxonomy parts. The benchmarks score detectors through it. |
| `exclusions.json` | Checklist items dropped by rule, with the reason for each. |
| `skipped.json` | Checklist items the LLM judged process-only, with the reason. Written by `sync.py`. |

To sync: `git submodule update --init`, set `OPENROUTER_API_KEY` (in `.env` or the environment), run `python sources/sync.py --check` to list what changed upstream, then `python sources/sync.py` to generate new or changed detectors, then `python sources/build_detector_map.py` if anything was generated. `sync.py` reads each source at its pinned commit with `git show` and never runs source code.

| Source | Submodule | Upstream | Pinned commit | License | Detectors |
|---|---|---|---|---|---|
| Solodit audit checklist | `sources/audit-checklist` | [Cyfrin/audit-checklist](https://github.com/Cyfrin/audit-checklist) (`main`), the data behind [solodit.cyfrin.io/checklist](https://solodit.cyfrin.io/checklist) | `008855fe1798` (2025-05-05) | none declared in the repo | 299 |
| EVM Cortex skills | `sources/evm-cortex` | [ccashwell/evm-cortex](https://github.com/ccashwell/evm-cortex) (`main`) | `bee3bf651d1d` (2026-08-10) | MIT | 44 |

After cloning jevscan-evm, fetch the sources with `git submodule update --init`.

## Solodit checklist

`checklist.json` holds 370 items, each with an `id`, `question`, `description`, `remediation`, and `references`, nested under categories. The detector name is the item id in snake case (`SOL-AM-DOSA-1` becomes `sol_am_dosa_1`), so a detector can be traced back to its checklist entry. 299 items become detectors:

- **Excluded by rule (47).** `exclusions.json` lists each id with its reason, and the sync produces no detector for them. The rule: keep items that describe an exploitable condition, and drop informational, best-practice, centralization, and legacy-compiler items. Single-step ownership transfer (`SOL-CR-6`) stays, because it is a known finding class. The checklist has no floating-pragma item.
- **Skipped by the LLM (24).** The rest are sent to the LLM with their category path. Most are questions about a safeguard ("Is there a check for X?"), and each becomes a statement that is true when the flawed code is present. The LLM skips items that no single file's code can decide (process, documentation, testing, off-chain operations). `skipped.json` records each skipped item with its reason.

### Excluded (47)

| Item | Reason |
|---|---|
| `SOL-AM-DOSA-6` | generic 'an external call may revert'; not a specific exploitable condition |
| `SOL-AM-RP-1` | centralization: a trusted admin can move funds |
| `SOL-Basics-AC-3` | design question about whether whitelisting is needed; no flaw pattern |
| `SOL-Basics-AC-6` | generic inheritance review prompt; no flaw pattern |
| `SOL-Basics-Event-1` | missing events; no security impact |
| `SOL-Basics-Function-1` | generic input validation |
| `SOL-Basics-Function-2` | generic output validation |
| `SOL-Basics-Function-4` | comments versus code; documentation |
| `SOL-Basics-Function-5` | generic zero/max input edge cases |
| `SOL-Basics-Function-6` | generic 'arbitrary user input' |
| `SOL-Basics-Function-7` | external versus public visibility; code quality |
| `SOL-Basics-Type-2` | use of time units such as `days`; informational |
| `SOL-Basics-VI-EAI-1` | selfdestruct deprecation notice (EIP-4758) |
| `SOL-CR-2` | centralization: a pause mechanism exists |
| `SOL-CR-3` | centralization: the admin can withdraw |
| `SOL-CR-4` | centralization: admin changes take effect immediately |
| `SOL-CR-5` | admin setter missing events; no security impact |
| `SOL-CR-7` | input validation in trusted admin setters |
| `SOL-Defi-Oracle-11` | generic 'an oracle call may revert'; not a specific exploitable condition |
| `SOL-Heuristics-1` | duplicated logic; code quality |
| `SOL-Integrations-Chainlink-VRF-2` | operational: keeping the VRF subscription funded |
| `SOL-Timelock-1` | centralization: no timelock on admin changes |
| `SOL-Token-FE-2` | ERC-20 approve race; an informational finding class |

These 24 compiler-bug items affect only Solidity versions before 0.6.0, so they are dropped as legacy-compiler items: `SOL-Basics-VI-SVI-1`, `SOL-Basics-VI-SVI-18`, `SOL-Basics-VI-SVI-2`, `SOL-Basics-VI-SVI-25`, `SOL-Basics-VI-SVI-26`, `SOL-Basics-VI-SVI-27`, `SOL-Basics-VI-SVI-28`, `SOL-Basics-VI-SVI-29`, `SOL-Basics-VI-SVI-3`, `SOL-Basics-VI-SVI-30`, `SOL-Basics-VI-SVI-31`, `SOL-Basics-VI-SVI-32`, `SOL-Basics-VI-SVI-33`, `SOL-Basics-VI-SVI-34`, `SOL-Basics-VI-SVI-35`, `SOL-Basics-VI-SVI-36`, `SOL-Basics-VI-SVI-37`, `SOL-Basics-VI-SVI-38`, `SOL-Basics-VI-SVI-39`, `SOL-Basics-VI-SVI-40`, `SOL-Basics-VI-SVI-41`, `SOL-Basics-VI-SVI-42`, `SOL-Basics-VI-SVI-43`, `SOL-Basics-VI-SVI-44`. The other compiler-version items are kept, because each names a code pattern and a compiler range that one file can decide.

## EVM Cortex skills

The 44 skills in `CORTEX_SKILLS` describe vulnerability patterns or integration pitfalls; each `skills/<name>/SKILL.md` is distilled into one detector.

The skills are evm-cortex skills by Chris Cashwell (ccashwell), MIT: [ccashwell/evm-cortex](https://github.com/ccashwell/evm-cortex). An earlier copy of the skills matches the pinned upstream for 43 of the 44 skills. Those 43 detectors keep the questions distilled and benchmarked before this change; only their `source`, `origin`, and `source_hash` fields were updated. Their text was built with the older prompt and does not pass the current criterion lint, and the builder leaves them alone until the skill text changes upstream. `uniswap-v4-hooks` differs and is built from upstream with the current prompt. A trial rebuild of all 44 with the current prompt lowered several scores on their benchmark files (`solidity_security` 0.81 to 0.02 on Beedle's Lender.sol, `access_control_patterns` 0.62 to 0.02 on USSD.sol), so it was not kept.

These skills (`CORTEX_DROP`) are tooling, process, how-to, or gas guidance rather than vulnerability patterns:

`aderyn-analysis`, `anvil-patterns`, `audit-breadth-scan`, `audit-depth-analysis`, `audit-prep`, `audit-recon`, `audit-report-generation`, `audit-verification`, `blockscout-mcp`, `cast-commands`, `contract-verification`, `coverage-analysis`, `dapp-frontend-patterns`, `erc8004-patterns`, `event-design`, `fizz`, `fizz-convert`, `fizz-sync`, `flash-loan-usage`, `forge-scripting`, `fork-testing`, `formal-verification`, `foundry-setup`, `foundry-testing`, `fuzzing-patterns`, `gas-optimization`, `gas-snapshot-testing`, `governance-patterns`, `immutable-constants`, `interface-design`, `invariant-testing`, `ipfs-deployment`, `l2-deployment`, `library-patterns`, `lp-analyst`, `multichain-deployment`, `natspec-standards`, `pool-finder`, `scaffold-eth-patterns`, `subgraph-patterns`, `test-fixtures`, `type-driven-design`, `uniswap-math`, `uniswap-v3-expert`, `uniswap-v4-expert`, `uniswap-v4-testing`, `wallet-integration`, `xray-pre-audit`, and one more static-analysis skill.

`immutable-constants` produced a question about SLOAD gas cost, not security. `governance-patterns` and `flash-loan-usage` are implementation guides; `governance-attacks` and `flash-loan-attacks` cover the security side.

A skill whose directory name ends in `-audit-pipeline` is dropped by rule (`cortex_dropped_by_rule` in `sync.py`), not by name: those are a named auditor's end-to-end review workflow, not a vulnerability pattern.
