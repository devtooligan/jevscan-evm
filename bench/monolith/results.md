# jevscan benchmark: Sherlock Monolith Stablecoin Factory (2025-12)

Ground truth: `bench/monolith/ground_truth.json` (7 H/M issues, categories assigned by hand). Code: https://github.com/sherlock-audit/2025-12-monolith-stablecoin-factory. One run: `jevscan.py` with the default settings (category, detector questions asked, locate threshold 0.5) and jev-1.13.0. A true pair is (issue file, the issue's category / subcategory / any detector mapped to its subcategory). Issues with no fitting subcategory are scored only at category resolution. Ranks are among all asked pairs at that resolution (1 = highest p). Bold p values are >= 0.5.

Files not scanned (Jev file classification): none.

## File-level recall

| Resolution | Issues scored | Recall@0.3 | Recall@0.5 | Recall@0.7 | Median rank of true pair | Pairs asked |
|---|---|---|---|---|---|---|
| category | 7 | 7/7 (100%) | 7/7 (100%) | 6/7 (86%) | 4 | 84 |
| detector | 6 | 4/6 (67%) | 4/6 (67%) | 3/6 (50%) | 20.5 | 2058 |

Recall is generous: an issue counts as found when any of its true pairs passes, and several issues share one (file, question) pair, so one flag can count for many issues. Distinct true pairs vs issues scored: category 5 for 7, detector 31 for 6. True pairs per scored issue (questions x files), mean: category 1.3, detector 6.5. At detector resolution that is every detector mapped to the issue's subcategory, in every issue file.

## Broad questions per file

| File | H/M issues | any_bug | critical_bug | Likely issues listed |
|---|---|---|---|---|
| `src/Lender.sol` | 6 | 0.80 | 0.79 | 16 |
| `src/InterestModel.sol` | 2 | 0.45 | 0.48 | 1 |
| `src/Vault.sol` | 1 | 0.76 | 0.79 | 5 |
| `src/Coin.sol` | 0 | 0.49 | 0.36 | 3 |
| `src/Factory.sol` | 0 | 0.71 | 0.65 | 1 |
| `src/Lens.sol` | 0 | 0.63 | 0.69 | 3 |

- any_bug: mean 0.67 on files with issues, 0.61 on files without
- critical_bug: mean 0.69 on files with issues, 0.57 on files without

## False-positive proxy

Files with no issue (3): `src/Coin.sol`, `src/Factory.sol`, `src/Lens.sol`

| Resolution | Threshold | Flags | True flags | Flags on files with no issue |
|---|---|---|---|---|
| category | 0.3 | 33 | 5 | 12 |
| category | 0.5 | 22 | 5 | 6 |
| category | 0.7 | 9 | 4 | 2 |
| detector | 0.3 | 148 | 18 | 27 |
| detector | 0.5 | 69 | 12 | 9 |
| detector | 0.7 | 25 | 6 | 4 |

## Flags without a known finding

A flag is a (file, category) pair whose file-level p is at or over the threshold. It is matched when the ground truth has a finding in that file with that category.

| Threshold | Flags | Matched | Unmatched | Unmatched share |
|---|---|---|---|---|
| 0.5 | 22 | 5 | 17 | 77% |
| 0.7 | 9 | 4 | 5 | 56% |

Unmatched flags at 0.5 (possibly unreported, or a false positive — not verified):

| File | Category | p | Note |
|---|---|---|---|
| `src/Lender.sol` | external_call_token_integration | 0.84 | the contest excluded fee-on-transfer and rebasing tokens; flags resting on those are likely false positives |
| `src/Vault.sol` | business_logic_state_machine | 0.81 |  |
| `src/Factory.sol` | business_logic_state_machine | 0.79 |  |
| `src/Lender.sol` | dos_griefing | 0.75 |  |
| `src/Lens.sol` | arithmetic_precision | 0.75 | Lens.sol re-implements Lender.sol's debt and collateral views, so this may echo the Lender math |
| `src/Lens.sol` | accounting_share_math | 0.68 | Lens.sol re-implements Lender.sol's debt and collateral views, so this may echo the Lender math |
| `src/Vault.sol` | arithmetic_precision | 0.68 |  |
| `src/Vault.sol` | external_call_token_integration | 0.62 | the contest excluded fee-on-transfer and rebasing tokens; flags resting on those are likely false positives |
| `src/Lender.sol` | frontrunning_mev | 0.60 |  |
| `src/Lender.sol` | reentrancy | 0.60 |  |
| `src/Vault.sol` | dos_griefing | 0.58 |  |
| `src/Factory.sol` | dos_griefing | 0.56 |  |
| `src/Factory.sol` | external_call_token_integration | 0.56 | the contest excluded fee-on-transfer and rebasing tokens; flags resting on those are likely false positives |
| `src/Lender.sol` | access_control | 0.56 |  |
| `src/Lender.sol` | flash_loan_economic | 0.52 |  |
| `src/Coin.sol` | business_logic_state_machine | 0.51 |  |
| `src/Vault.sol` | frontrunning_mev | 0.50 |  |

## Locating (file-level threshold 0.5)

An issue is scored when it names a function, on exactly one function ranking: its true (file, question) pair with the highest file-level p (ties broken by file and question id). The pair is chosen from the file-level answers alone, so no issue gets the best of several rankings. Top-1/top-3: one of the issue's functions is ranked first / in the top 3 in that ranking. The random baseline uses the same ranking: with n functions of which k are the issue's, top-1 chance k/n and top-3 chance 1 - C(n-k,3)/C(n,3), summed over the located issues. 'Not located' means the scored pair was below 0.5 at file level (so every true pair was), and nothing was re-asked per function.

| Resolution | Scorable issues | Located | Top-1 | Top-3 | Random top-1 (expected) | Random top-3 (expected) |
|---|---|---|---|---|---|---|
| category | 7 | 7 | 3/7 | 5/7 | 1.4 | 2.1 |
| detector | 6 | 4 | 2/4 | 3/4 | 0.2 | 0.6 |

## Line locating (experimental)

For each (function, question) whose function-level p >= 0.5, one Choice question picks the primary vulnerable line. An issue is scored on the same pair as above, at the issue function ranked highest for it, when the report links a snippet (line range) in that file and that function got a line answer. The random baseline uses the same Choice: with n options of which k fall in a snippet. Snippets that span a whole function make this easy.

| Resolution | Issues with snippet and a line answer | Top-1 in snippet | Top-3 in snippet | Random top-1 (expected) | Random top-3 (expected) |
|---|---|---|---|---|---|
| category | 7 | 2/7 | 5/7 | 2.2 | 3.4 |
| detector | 3 | 0/3 | 1/3 | 0.3 | 0.7 |

## Repo-level

One request over all 6 scanned files (~20,705 estimated tokens). Most suspicious file (Choice): `src/Lender.sol` (0.71); the file with the most ground-truth issues is `src/Lender.sol` (6).

| Question | Repo-level p | Per-file max | Argmax file |
|---|---|---|---|
| broad:any_bug | 0.77 | 0.80 | `src/Lender.sol` |
| broad:critical_bug | 0.78 | 0.79 | `src/Lender.sol` |
| category:access_control | 0.56 | 0.56 | `src/Lender.sol` |
| category:proxy_upgradeability | 0.21 | 0.19 | `src/Factory.sol` |
| category:oracle_price_manipulation | 0.33 | 0.36 | `src/Lender.sol` |
| category:flash_loan_economic | 0.58 | 0.52 | `src/Lender.sol` |
| category:reentrancy | 0.49 | 0.60 | `src/Lender.sol` |
| category:accounting_share_math | 0.71 | 0.77 | `src/Vault.sol` |
| category:arithmetic_precision | 0.78 | 0.80 | `src/Lender.sol` |
| category:signature_replay | 0.07 | 0.08 | `src/Factory.sol` |
| category:cross_chain_messaging | 0.04 | 0.04 | `src/Factory.sol` |
| category:external_call_token_integration | 0.87 | 0.84 | `src/Lender.sol` |
| category:business_logic_state_machine | 0.83 | 0.86 | `src/Lender.sol` |
| category:dos_griefing | 0.71 | 0.75 | `src/Lender.sol` |
| category:frontrunning_mev | 0.63 | 0.60 | `src/Lender.sol` |
| category:legacy_low_level | 0.14 | 0.15 | `src/Factory.sol` |

## HEATMAP order

HEATMAP.md's grid has 6 files; its strongest-hits table has 33 functions.

| Issues found within | First N rows | Count |
|---|---|---|
| issue function in the strongest-hits table | 5 | 0/7 |
| issue function in the strongest-hits table | 10 | 4/7 |
| issue function in the strongest-hits table | 20 | 7/7 |
| issue function in the strongest-hits table | 33 | 7/7 |
| issue file among the top grid rows | 1 | 6/7 |
| issue file among the top grid rows | 3 | 6/7 |

Per issue (row of its first function in the strongest-hits table, or - if not listed): H-1 10, M-1 9, M-2 6, M-3 12, M-4 10, M-5 17, M-6 17

## Cost

| Phase | Requests | Cached | Input tokens | Cost | Wall time |
|---|---|---|---|---|---|
| model_probe | 1 | 0 | 282 | $0.0000 | 0.22s |
| scan | 25 | 25 | 705,876 | $0.0296 | 0.03s |
| locate | 127 | 127 | 1,027,503 | $0.0432 | 0.05s |
| repo | 2 | 2 | 40,542 | $0.0017 | 0.0s |

| Scan level (broad questions ride with category) | Requests | Input tokens | Cost |
|---|---|---|---|
| category | 6 | 28,837 | $0.0012 |
| detector | 19 | 677,039 | $0.0284 |

## Issues

| Issue | Files | Category / subcategory | category | detector | Located (category / detector) |
|---|---|---|---|---|---|
| H-1 User can abuse rounding issue in order to borrow unbacked tokens | `Lender.sol` | arithmetic_precision / rounding_direction_error | **0.80** | **0.64** `sol_basics_math_5` | top3 / top1 |
| M-1 If there's only a single user which has reached a state with bad debt, anyone can mint unbacked tokens. | `Lender.sol` | business_logic_state_machine / liquidation_logic_error | **0.86** | **0.82** `sol_defi_lending_3` | top1 / top3 |
| M-2 Inconsistency in position health checks will lead to the incorrect user liquidations | `Lender.sol` | business_logic_state_machine / liquidation_logic_error | **0.86** | **0.82** `sol_defi_lending_3` | top3 / top1 |
| M-3 EIP violation for `totalAssets()` in the `Vault` | `Vault.sol`, `Lender.sol` | accounting_share_math / — | **0.77** | n/a | miss / n/a |
| M-4 Accounting will be broken if a user redeems when there is a bad debt position | `Lender.sol` | accounting_share_math / debt_and_interest_accounting_error | **0.73** | 0.13 `sol_defi_lending_8` | top1 / not located |
| M-5 Incorrect interest calculation | `InterestModel.sol` | arithmetic_precision / incorrect_formula | **0.60** | 0.03 `sol_heuristics_7` | top1 / not located |
| M-6 Interest accrual can get stuck when `wadExp()` underflows to 0 causing division-by-zero | `InterestModel.sol`, `Lender.sol` | arithmetic_precision / precision_loss_division_before_multiplication | **0.80** | **0.82** `sol_basics_math_12` | miss / miss |

## Top 10 (file, question) pairs not in the ground truth

These are candidate false positives or real issues the contest did not list. None were verified.

| p | File | Question | Description | Status |
|---|---|---|---|---|
| 0.89 | `src/Vault.sol` | detector:sol_token_fe_6 | Fee-on-transfer token accounting mismatch from assuming transferred amount equals received amount | unverified |
| 0.87 | `src/Lender.sol` | detector:sol_token_fe_13 | ERC20 approve() called directly to non-zero value without resetting allowance to zero first | unverified |
| 0.87 | `src/Lender.sol` | detector:sol_defi_oracle_4 | Missing L2 sequencer uptime check when consuming Chainlink price feeds | unverified |
| 0.86 | `src/Lens.sol` | detector:error_handling | Silent failure from try/catch blocks that swallow external call errors instead of reverting | unverified |
| 0.86 | `src/Lender.sol` | detector:sol_token_fe_14 | Unconditional max-value ERC20 approval breaks on tokens that reject type(uint256).max amounts | unverified |
| 0.85 | `src/Lender.sol` | detector:sol_token_fe_8 | Honeypot attack via Solmate SafeTransferLib's lack of contract-existence check for ERC20 transfers | unverified |
| 0.84 | `src/Lender.sol` | category:external_call_token_integration | External calls and token integration | unverified |
| 0.83 | `src/Lender.sol` | detector:sol_token_fe_6 | Fee-on-transfer token accounting mismatch from assuming transferred amount equals received amount | unverified |
| 0.82 | `src/Lens.sol` | detector:sol_defi_lending_2 | Lending protocol lacks a working liquidation mechanism for undercollateralized or defaulted loans | unverified |
| 0.81 | `src/Vault.sol` | category:business_logic_state_machine | Business logic, input validation, and state machine | unverified |

## Unmatched flags at 70%, reviewed

Each flag was checked by hand against the code, the 7 judged findings, and the contest's scope answers. Full write-ups: [`unmatched_review_a.md`](unmatched_review_a.md) (A1-A3), [`unmatched_review_b.md`](unmatched_review_b.md) (B1-B3).

| | File | Category | Chance | Verdict | Reason |
|---|---|---|---|---|---|
| A1 | `src/Lender.sol` | external_call_token_integration | 83% | real, not reportable | `liquidate` breaks checks-effects-interactions, but only a hook-bearing (ERC777) collateral can re-enter, and the contest excludes those |
| A3 | `src/Factory.sol` | business_logic_state_machine | 78% | false positive | deployment order and CREATE3 salts are sound; the Lender constructor validates the risk parameters |
| B1 | `src/Vault.sol` | business_logic_state_machine | 77% | false positive | the one-time `MIN_SHARES` dead-share burn is handled the same way in the previews and in `deposit` / `mint` |
| B2 | `src/Lens.sol` | arithmetic_precision | 74% | real, not reportable | a view-only copy of Lender's math: the rounding it copies is H-1's root cause, the interest path copies M-5 / M-6 |
| A2 | `src/Lender.sol` | dos_griefing | 73% | false positive | the flagged transfers go to the caller, `writeOff` is wrapped in try/catch, and full repay cannot strand a borrower |
| B3 | `src/Lens.sol` | business_logic_state_machine | 72% | false positive | the epoch rebase simulation matches what Lender charges after `updateBorrower` |

The table is from the run before the business-logic question gained its view-only sentence ("View or pure functions that change no state do not count, unless state-changing code in the file uses their result."). That run had 10 flags at 70%: 6 real (4 judged findings + 2 real bugs the contest did not count: one out of scope by the rules, one a view-only copy of a judged bug), 4 false positives. In the current run B3 drops to 28% and the others stay above 70%, so there are 9 flags at 70%: 6 real, 3 false positives.

## Notes (hand-written)

- Cold run, 2026-09-18, empty cache, same config: 157 billed requests, $0.077, 5.8 s wall time end to end. The cost table above is from the cached benchmark run, so its wall times are cache reads. The repo's `lib/forge-std` and `lib/solmate` submodules are empty, so the project cannot compile; jevscan read the six scope files as text.
- Clean files: `src/Coin.sol` and `src/Lens.sol` have no known finding, and neither does `src/Factory.sol`, so all three count as clean above. At 0.5, `Coin.sol` got 1 category flag (business logic 0.51); `Factory.sol` got 3 (business logic 0.79, external calls 0.56, DoS 0.56) and `Lens.sol` got 2 (arithmetic 0.75, accounting 0.68). `Lens.sol` re-implements `Lender.sol`'s debt and collateral views (`getDebtOf`, `getCollateralOf`), so its arithmetic and accounting flags may be echoing the Lender math; the 70% ones are reviewed above (B2, B3).
- Known-findings credit in `run/HEATMAP.md` is generous: it needs the right file, one of the finding's functions, and its bug type, not the exact line. M-5's formula is on lines 49-50 and M-6's division on line 36; the heat map's line pick for `calculateInterest` is line 37 for both.
- Contest dates: 2025-12-08 to 2025-12-14 (Sherlock contest 1212); judging closed 2026-02-24. Jev's training cutoff is not published, so recency lowers but does not rule out contamination.
