# Ablation: the 44 Slither detectors

Question: should the Slither-derived detectors be dropped?

Setup: all three benchmarks, run twice with jev-1.13.0. "With" is the current settings (Solodit, Slither, and evm-cortex sources). Its answers matched the benchmark runs' `results.json` exactly, since they came from the cache. "Without" is the same config plus `[sources] slither = false`, which leaves 343 detectors. Removing a source changes the detector batch boundaries, so most detector answers were asked again. The differences on the remaining detectors are therefore batch noise, not an effect of the missing questions. Scoring is the same as `run_bench.py`: an issue counts when any detector mapped to its subcategory scores at or over the threshold in one of its files. The same issue set is scored in both runs (62 issues with a mapped subcategory).

## 1. Detector-level recall

| Benchmark | Scored issues | @0.5 with | @0.5 without | @0.7 with | @0.7 without |
|---|---|---|---|---|---|
| USSD | 16 | 12 | 12 | 8 | 8 |
| Beedle | 40 | 30 | 32 | 29 | 29 |
| Monolith | 6 | 4 | 4 | 3 | 3 |
| **Total** | 62 | **46** | **48** | **40** | **40** |

Beedle's +2 at 0.5 is batch noise. H-5 and M-5 share `sol_heuristics_16` on `Lender.sol`, which moved from 0.48 to 0.50. No issue changed at 0.7. If the "with" run's own answers are scored with the Slither pairs removed, recall is identical (46 / 40), so dropping Slither loses nothing.

## 2. Detector flags on files with no known finding

| Benchmark | @0.5 with | @0.5 without | @0.7 with | @0.7 without | Of the "with" flags, Slither's (@0.5 / @0.7) |
|---|---|---|---|---|---|
| USSD | 12 | 9 | 4 | 2 | 2 / 2 |
| Beedle | 0 | 0 | 0 | 0 | 0 / 0 (every scanned file has a finding) |
| Monolith | 10 | 9 | 4 | 4 | 0 / 0 |
| **Total** | **22** | **18** | **8** | **6** | 2 / 2 |

USSD's two Slither flags on files with no known finding are `slither_incorrect_modifier` on `Migrations.sol` (0.96) and `slither_calls_loop` on `UniswapV3StaticOracle.sol` (0.86). They account for both of the drops at 0.7. The other two drops at 0.5 (USSD −1, Monolith −1) are batch noise.

## 3. Detector flags not matching any judged finding @0.7

A flag is a (file, detector) pair at or over 0.7. It is unmatched when no judged finding has that file with that detector mapped to its subcategory.

| Benchmark | Flags with | Flags without | Unmatched with | Unmatched without | Slither flags in "with" (all / unmatched) |
|---|---|---|---|---|---|
| USSD | 101 | 91 | 62 | 56 | 5 / 4 |
| Beedle | 56 | 49 | 25 | 19 | 6 / 5 |
| Monolith | 27 | 25 | 21 | 19 | 1 / 1 |
| **Total** | **184** | **165** | **108** | **94** | **12 / 10** |

At 0.7, Slither contributes 12 of 184 detector flags (7%), and 10 of those 12 match no judged finding. At 0.5 it contributes 20 of 315, with 17 unmatched.

## 4. Which Slither detectors mattered

**Top hit for a judged finding.** Only one Slither detector was ever the top hit:

| Benchmark | Issue | Top detector (with) | p | Best without Slither |
|---|---|---|---|---|
| Beedle | M-3 (blacklisted user freezes funds; `repay`, `seizeLoan`) | `slither_calls_loop` | 0.97 | `sol_basics_al_10` 0.86 (still caught @0.7) |

Slither detectors that scored ≥ 0.5 on a true pair without being the top hit:
- `slither_divide_before_multiply` on USSD M-8 at 0.73 (top was `sol_basics_math_12`, 0.86).
- `slither_divide_before_multiply` on Monolith M-6 at 0.68 (top was `sol_basics_math_12`, 0.81).

In every case a Solodit detector already covered the finding at a higher p.

**Strongest unmatched Slither hits (@0.7, "with" run).** File p, then the top located function with its function-level p and line. The verdicts come from reading the code.

| Benchmark | File | Detector | File p | Function (p, line) | Verdict |
|---|---|---|---|---|---|
| USSD | `Migrations.sol` | `slither_incorrect_modifier` | 0.96 | `setCompleted` (0.89, L24) | Pattern is real (`restricted` skips the body instead of reverting), but a non-owner call is a harmless no-op in a Truffle bookkeeping contract. Informational, the class the prune rule excludes. |
| USSD | `USSDRebalancer.sol` | `slither_calls_loop` | 0.94 | `SellUSSDBuyCollateral` (0.93, L201) | Swaps over the admin-set collateral list. One failing swap reverts that rebalance, but the list is trusted and the call is not attacker-reachable. The judged bugs in this function (H-2, M-10) are logic bugs, not loop DoS. Weak. |
| USSD | `oracles/UniswapV3StaticOracle.sol` | `slither_calls_loop` | 0.86 | `_prepare` (0.97, L156) | **Noise.** The loop calls `increaseObservationCardinalityNext` on pools the caller passes or that come from the factory. A revert only fails the caller's own transaction; no shared state or other user is blocked. This is the 97% row in the v0.1 README's USSD example table. |
| USSD | `USSD.sol` | `slither_token_reentrancy` | 0.71 | `mintForToken` (0.78, L158) | False positive: collateral tokens are admin-whitelisted (DAI, WETH, WBTC, WBGL; no hooks), and the mint amount comes from the oracle, not balances. |
| Beedle | `src/Staking.sol` | `slither_unchecked_transfer` | 0.94 | `deposit` (0.92, L39) | Real pattern (raw `TKN.transferFrom`, return value ignored), not a judged H/M. |
| Beedle | `src/Staking.sol` | `slither_token_reentrancy` | 0.88 | `deposit` (0.89, L39) | False positive: `TKN` is fixed at deploy. |
| Beedle | `src/Lender.sol` | `slither_timestamp` | 0.87 | `seizeLoan` (0.88, L557) | Noise: an ordinary auction-end check. |
| Beedle | `src/Lender.sol` | `slither_unchecked_transfer` | 0.82 | `seizeLoan` (0.85, L563) | Real pattern (raw `transfer`), not a judged H/M. |
| Beedle | `src/Lender.sol` | `slither_token_reentrancy` | 0.81 | `refinance` (0.87) | Plausible: pool tokens are arbitrary, next to the judged M-7 and H-20. It is unmatched only because `token_hook_reentrancy` is not those findings' subcategory. |
| Monolith | `src/Lender.sol` | `slither_timestamp` | 0.90 | `getCollateralPrice` (0.71, L733) | Noise: a correct staleness check. |

**HEATMAP strongest-hits table.** Slither led 5 of 32 rows on USSD and 1 of 18 on Beedle. Without Slither, `Migrations.setCompleted` leaves the USSD table, and `UniswapV3StaticOracle.prepareSpecificPoolsWithCardinality` enters at 0.70. The other slither-led rows stay, led by Solodit detectors: `_prepare` 0.78, `SellUSSDBuyCollateral` 0.93, `BuyUSSDSellCollateral` 0.93, `_quote` 0.89, and Beedle's `seizeLoan` 0.97 via `token_integration_safety`.

## 5. Category and broad questions

The category and broad answers are unchanged: all 336 file-level (file, category/broad) answers are identical (max difference 0.00), and so are the repo-level answers. These questions go in their own requests, so dropping a detector source does not re-batch them, and they came from the cache in both runs. No threshold crossings. The category tables in the README are unaffected.

The remaining detectors did re-batch. Their mean absolute change was 0.003, with a maximum of 0.11 to 0.12, and 11 / 5 / 4 (USSD / Beedle / Monolith) crossed 0.5 or 0.7, all by 0.06 or less. This is the usual ±0.05 noise and moves in both directions.

## 6. Cost

The cost of a cold run, computed from input tokens at $0.042 per million tokens whether or not the answer was cached:

| Benchmark | With | Without | Change | Detector pairs asked (with → without) |
|---|---|---|---|---|
| USSD | $0.0747 | $0.0702 | −6% | 3096 → 2744 |
| Beedle | $0.0644 | $0.0583 | −10% | 2709 → 2401 |
| Monolith | $0.0791 | $0.0745 | −6% | 2322 → 2058 |
| **Total** | **$0.2183** | **$0.2030** | **−7%** | 8127 → 7203 |

This ablation billed $0.19 in total, all on the "without" runs.

## Recommendation

**Drop all 44.** Across 62 scored findings, detector recall is identical at 0.7 (40 → 40), and at 0.5 it is identical once batch noise is removed. The one finding where Slither was the top hit, Beedle M-3 via `slither_calls_loop`, is still caught at 0.86 by a Solodit detector. The two other true pairs, from `slither_divide_before_multiply`, were already beaten by `sol_basics_math_12`. Slither's contribution is mostly noise: 10 of its 12 flags at 0.7 match no judged finding. Its strongest hits are a non-DoS loop (`_prepare`, the 97% row in the v0.1 README's USSD example), an informational modifier on Truffle's `Migrations.sol`, timestamp checks, and reentrancy on fixed or whitelisted tokens. Dropping it removes 2 of the 8 detector flags on files with no finding at 0.7, and it cuts 7% of the cost. Category scores do not move. No named subset is worth keeping. `slither_calls_loop` is the only candidate, and it produced as many unmatched strong hits (3) as true ones (1, which is redundant). `slither_unchecked_transfer` finds real but low-severity patterns that the prune rule already treats as out of scope. If the source is dropped, update the detector counts in README.md, sources/README.md, and docs/CONFIG.md (387 → 343).

Runs: scratch outputs, not committed. Scoring reuses `run_bench.py`'s `targets`, `pairs`, `best_true`, and `true_pairs`.

Outcome: dropped in v0.2. The library is now 343 detectors (Solodit checklist and evm-cortex), and the committed `bench/*/run` outputs are the "without" runs.
