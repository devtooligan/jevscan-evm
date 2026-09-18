# jevscan benchmark: CodeHawks Beedle (2023-07)

Ground truth: `bench/beedle/ground_truth.json` (42 H/M issues, categories assigned by hand). Code: https://github.com/Cyfrin/2023-07-beedle. One run: `jevscan.py` with the default settings (category, detector questions asked, locate threshold 0.5) and jev-1.13.0. A true pair is (issue file, the issue's category / subcategory / any detector mapped to its subcategory). Issues with no fitting subcategory are scored only at category resolution. Ranks are among all asked pairs at that resolution (1 = highest p). Bold p values are >= 0.5.

Files not scanned (Jev file classification): `script/LenderScript.s.sol` (script, 1.00), `src/interfaces/IERC20.sol` (interface, 1.00), `src/interfaces/ISwapRouter.sol` (interface, 1.00), `test/Fuzzing.t.sol` (test, 1.00), `test/Lender.t.sol` (test, 1.00).

## File-level recall

| Resolution | Issues scored | Recall@0.3 | Recall@0.5 | Recall@0.7 | Median rank of true pair | Pairs asked |
|---|---|---|---|---|---|---|
| category | 42 | 40/42 (95%) | 34/42 (81%) | 27/42 (64%) | 9.0 | 98 |
| detector | 40 | 35/40 (88%) | 32/40 (80%) | 29/40 (72%) | 41.0 | 2401 |

Recall is generous: an issue counts as found when any of its true pairs passes, and several issues share one (file, question) pair, so one flag can count for many issues. Distinct true pairs vs issues scored: category 24 for 42, detector 237 for 40. True pairs per scored issue (questions x files), mean: category 1.2, detector 11.7. At detector resolution that is every detector mapped to the issue's subcategory, in every issue file.

## Broad questions per file

| File | H/M issues | any_bug | critical_bug | Likely issues listed |
|---|---|---|---|---|
| `src/Lender.sol` | 27 | 0.84 | 0.84 | 11 |
| `src/Fees.sol` | 9 | 0.70 | 0.59 | 2 |
| `src/Staking.sol` | 8 | 0.77 | 0.67 | 5 |
| `src/utils/Ownable.sol` | 2 | 0.29 | 0.10 | 1 |
| `src/Beedle.sol` | 1 | 0.52 | 0.36 | 1 |
| `src/utils/Errors.sol` | 1 | 0.13 | 0.13 | 0 |
| `src/utils/Structs.sol` | 1 | 0.30 | 0.37 | 1 |

- any_bug: mean 0.51 on files with issues, n/a (no such file) on files without
- critical_bug: mean 0.44 on files with issues, n/a (no such file) on files without

## False-positive proxy

Files with no issue (0): 

| Resolution | Threshold | Flags | True flags | Flags on files with no issue |
|---|---|---|---|---|
| category | 0.3 | 29 | 13 | 0 |
| category | 0.5 | 20 | 11 | 0 |
| category | 0.7 | 12 | 9 | 0 |
| detector | 0.3 | 137 | 55 | 0 |
| detector | 0.5 | 88 | 39 | 0 |
| detector | 0.7 | 49 | 30 | 0 |

## Flags without a known finding

A flag is a (file, category) pair whose file-level p is at or over the threshold. It is matched when the ground truth has a finding in that file with that category.

| Threshold | Flags | Matched | Unmatched | Unmatched share |
|---|---|---|---|---|
| 0.5 | 20 | 11 | 9 | 45% |
| 0.7 | 12 | 9 | 3 | 25% |

Unmatched flags at 0.5 (possibly unreported, or a false positive — not verified):

| File | Category | p | Note |
|---|---|---|---|
| `src/Staking.sol` | business_logic_state_machine | 0.85 |  |
| `src/Staking.sol` | access_control | 0.72 |  |
| `src/Staking.sol` | dos_griefing | 0.70 |  |
| `src/Fees.sol` | access_control | 0.65 |  |
| `src/Staking.sol` | reentrancy | 0.64 |  |
| `src/Fees.sol` | business_logic_state_machine | 0.62 |  |
| `src/Fees.sol` | dos_griefing | 0.60 |  |
| `src/Staking.sol` | arithmetic_precision | 0.58 |  |
| `src/Lender.sol` | flash_loan_economic | 0.53 |  |

## Locating (file-level threshold 0.5)

An issue is scored when it names a function, on exactly one function ranking: its true (file, question) pair with the highest file-level p (ties broken by file and question id). The pair is chosen from the file-level answers alone, so no issue gets the best of several rankings. Top-1/top-3: one of the issue's functions is ranked first / in the top 3 in that ranking. The random baseline uses the same ranking: with n functions of which k are the issue's, top-1 chance k/n and top-3 chance 1 - C(n-k,3)/C(n,3), summed over the located issues. 'Not located' means the scored pair was below 0.5 at file level (so every true pair was), and nothing was re-asked per function.

| Resolution | Scorable issues | Located | Top-1 | Top-3 | Random top-1 (expected) | Random top-3 (expected) |
|---|---|---|---|---|---|---|
| category | 41 | 34 | 14/34 | 26/34 | 6.4 | 14.7 |
| detector | 39 | 32 | 15/32 | 20/32 | 7.1 | 15.2 |

## Line locating (experimental)

For each (function, question) whose function-level p >= 0.5, one Choice question picks the primary vulnerable line. An issue is scored on the same pair as above, at the issue function ranked highest for it, when the report links a snippet (line range) in that file and that function got a line answer. The random baseline uses the same Choice: with n options of which k fall in a snippet. Snippets that span a whole function make this easy.

| Resolution | Issues with snippet and a line answer | Top-1 in snippet | Top-3 in snippet | Random top-1 (expected) | Random top-3 (expected) |
|---|---|---|---|---|---|
| category | 14 | 6/14 | 11/14 | 2.3 | 4.5 |
| detector | 10 | 5/10 | 10/10 | 2.7 | 3.9 |

## Repo-level

One request over all 7 scanned files (~11,464 estimated tokens). Most suspicious file (Choice): `src/Lender.sol` (0.70); the file with the most ground-truth issues is `src/Lender.sol` (27).

| Question | Repo-level p | Per-file max | Argmax file |
|---|---|---|---|
| broad:any_bug | 0.88 | 0.84 | `src/Lender.sol` |
| broad:critical_bug | 0.86 | 0.84 | `src/Lender.sol` |
| category:access_control | 0.61 | 0.72 | `src/Staking.sol` |
| category:proxy_upgradeability | 0.10 | 0.06 | `src/Lender.sol` |
| category:oracle_price_manipulation | 0.28 | 0.13 | `src/Fees.sol` |
| category:flash_loan_economic | 0.78 | 0.53 | `src/Lender.sol` |
| category:reentrancy | 0.76 | 0.70 | `src/Lender.sol` |
| category:accounting_share_math | 0.80 | 0.79 | `src/Lender.sol` |
| category:arithmetic_precision | 0.79 | 0.80 | `src/Lender.sol` |
| category:signature_replay | 0.21 | 0.13 | `src/Beedle.sol` |
| category:cross_chain_messaging | 0.03 | 0.02 | `src/Beedle.sol` |
| category:external_call_token_integration | 0.91 | 0.92 | `src/Lender.sol` |
| category:business_logic_state_machine | 0.90 | 0.89 | `src/Lender.sol` |
| category:dos_griefing | 0.80 | 0.78 | `src/Lender.sol` |
| category:frontrunning_mev | 0.81 | 0.74 | `src/Lender.sol` |
| category:legacy_low_level | 0.09 | 0.06 | `src/Lender.sol` |

## HEATMAP order

HEATMAP.md's grid has 7 files; its strongest-hits table has 18 functions.

| Issues found within | First N rows | Count |
|---|---|---|
| issue function in the strongest-hits table | 5 | 19/41 |
| issue function in the strongest-hits table | 10 | 29/41 |
| issue function in the strongest-hits table | 20 | 41/41 |
| issue function in the strongest-hits table | 18 | 41/41 |
| issue file among the top grid rows | 1 | 27/42 |
| issue file among the top grid rows | 3 | 41/42 |

Per issue (row of its first function in the strongest-hits table, or - if not listed): H-1 5, H-2 2, H-3 10, H-4 1, H-5 7, H-6 7, H-7 13, H-8 13, H-9 13, H-10 13, H-11 13, H-12 8, H-13 1, H-14 1, H-15 1, H-16 8, H-17 8, H-18 13, H-19 13, H-20 2, H-21 12, H-22 1, H-23 5, H-24 8, H-25 14, H-26 5, K-27 5, M-1 12, M-2 5, M-3 2, M-4 1, M-5 12, M-6 3, M-7 6, M-8 1, M-9 -, M-10 8, M-11 7, M-12 2, M-13 17, M-14 2, M-15 1

## Cost

| Phase | Requests | Cached | Input tokens | Cost | Wall time |
|---|---|---|---|---|---|
| model_probe | 1 | 0 | 282 | $0.0000 | 0.31s |
| classify | 12 | 12 | 9,276 | $0.0004 | 0.0s |
| scan | 28 | 28 | 760,082 | $0.0319 | 0.03s |
| locate | 58 | 58 | 594,497 | $0.0250 | 0.02s |
| repo | 2 | 2 | 22,948 | $0.0010 | 0.0s |

| Scan level (broad questions ride with category) | Requests | Input tokens | Cost |
|---|---|---|---|
| category | 7 | 21,632 | $0.0009 |
| detector | 21 | 738,450 | $0.0310 |

## Issues

| Issue | Files | Category / subcategory | category | detector | Located (category / detector) |
|---|---|---|---|---|---|
| H-1 Tokens with less than 18 decimals allow for draining of funds | `Lender.sol` | arithmetic_precision / decimal_mismatch | **0.80** | **0.83** `sol_defi_general_1` | top1 / top1 |
| H-2 Lender contract can be drained by re-entrancy in `repay` | `Lender.sol` | reentrancy / single_function_reentrancy | **0.70** | **0.82** `solidity_security` | miss / miss |
| H-3 Lender contract can be drained by re-entrancy in `setPool` | `Lender.sol` | reentrancy / single_function_reentrancy | **0.70** | **0.82** `solidity_security` | top3 / top3 |
| H-4 Sandwich attack to steal all ERC-20 tokens in the Fees contract | `Fees.sol` | frontrunning_mev / missing_slippage_protection | **0.66** | **0.96** `sol_defi_as_11` | top1 / top1 |
| H-5 Borrower can use Refinance to cancel auctions so they can extend their loan indefinitely | `Lender.sol` | business_logic_state_machine / invalid_state_transition | **0.89** | **0.50** `sol_heuristics_16` | miss / top3 |
| H-6 During refinance() new Pool balance debt is subtracted twice | `Lender.sol` | accounting_share_math / state_update_omission_or_double_count | **0.79** | **0.88** `sol_basics_al_4` | top1 / miss |
| H-7 Borrower can bypass maxLoanRatio's configuration of a pool via buyLoan() | `Lender.sol` | business_logic_state_machine / missing_input_validation | **0.89** | **0.75** `sol_basics_al_7` | miss / miss |
| H-8 Lender#buyLoan - Malicious user could take over a loan for free without having a pool because of wrong access control | `Lender.sol` | access_control / arbitrary_from_or_on_behalf_of | 0.49 | 0.41 `sol_heuristics_9` | not located / not located |
| H-9 Using forged/fake lending pools to steal any loan opening for auction | `Lender.sol` | business_logic_state_machine / missing_input_validation | **0.89** | **0.75** `sol_basics_al_7` | miss / miss |
| H-10 Stealing any loan opening for auction through others' lending pool | `Lender.sol` | access_control / arbitrary_from_or_on_behalf_of | 0.49 | 0.41 `sol_heuristics_9` | not located / not located |
| H-11 Attacker can steal a loan's collateral and break the protocol | `Lender.sol` | business_logic_state_machine / missing_input_validation | **0.89** | **0.75** `sol_basics_al_7` | miss / miss |
| H-12 Fee on transfer tokens will cause users to lose funds | `Staking.sol` | external_call_token_integration / fee_on_transfer_or_rebasing_token | **0.89** | **0.98** `token_integration_safety` | top1 / top1 |
| H-13 update() not getting called right after a WETH amount has been sent will cause users to lose staking rewards | `Staking.sol`, `Fees.sol` | accounting_share_math / reward_accounting_error | **0.57** | 0.11 `staking_reward_patterns` | top3 / not located |
| H-14 Sandwich attack to steal all ERC-20 tokens in the Fees contract | `Fees.sol` | frontrunning_mev / missing_slippage_protection | **0.66** | **0.96** `sol_defi_as_11` | top1 / top1 |
| H-15 Token spending by Uniswap router doesn't get approved | `Fees.sol` | external_call_token_integration / approval_handling_flaw | **0.78** | 0.02 `sol_token_fe_14` | top1 / not located |
| H-16 Front-runnig the first deposit on stake yealds the whole WETH amount | `Staking.sol` | flash_loan_economic / instant_reward_or_snapshot_gaming | 0.49 | **0.82** `sol_defi_general_8` | not located / top3 |
| H-17 Rewards can be sabotaged by large deposit and withdraw | `Staking.sol` | flash_loan_economic / instant_reward_or_snapshot_gaming | 0.49 | **0.82** `sol_defi_general_8` | not located / top1 |
| H-18 Borrower can prevent his/her loan from being liquidated | `Lender.sol` | access_control / arbitrary_from_or_on_behalf_of | 0.49 | 0.41 `sol_heuristics_9` | not located / not located |
| H-19 A pool lender can fully drain another user's pool by abusing `buyLoan` | `Lender.sol` | business_logic_state_machine / missing_input_validation | **0.89** | **0.75** `sol_basics_al_7` | miss / miss |
| H-20 `Lender` does not handle correctly rebasing, inflationary, deflationary tokens and tokens with fee on transfer | `Lender.sol` | external_call_token_integration / fee_on_transfer_or_rebasing_token | **0.92** | **0.98** `token_integration_safety` | top1 / top1 |
| H-21 Forcing a borrower to pay a huge debt via the giveLoan() | `Lender.sol` | accounting_share_math / debt_and_interest_accounting_error | **0.79** | **0.57** `sol_defi_lending_8` | top3 / miss |
| H-22 Hardcoded Router Address May Cause Token Lockup in Non-Standard Networks | `Fees.sol` | external_call_token_integration / external_protocol_assumption | **0.78** | **0.84** `sol_token_fe_10` | top1 / top1 |
| H-23 Lender can Sandwich a borrower to seize his collateral | `Lender.sol` | frontrunning_mev / frontrunnable_state_change | **0.74** | **0.73** `sol_am_ma_3` | miss / miss |
| H-24 WETH staking rewards accumulated before the first staker deposits remain unutilized and stuck in the `Staking` contract | `Staking.sol` | accounting_share_math / reward_accounting_error | **0.57** | 0.11 `staking_reward_patterns` | top3 / not located |
| H-25 WETH token balance is incorrectly updated when claiming staking rewards resulting in stuck WETH rewards | `Staking.sol` | accounting_share_math / reward_accounting_error | **0.57** | 0.11 `staking_reward_patterns` | top3 / not located |
| H-26 The `borrow` and `refinance` functions can be front-run by the pool lender leading to collateral being seized in the next block | `Lender.sol` | frontrunning_mev / frontrunnable_state_change | **0.74** | **0.73** `sol_am_ma_3` | top3 / miss |
| K-27 The `borrow` and `refinance` functions can be front-run by the pool lender leading to collateral being seized in the next block | `Lender.sol` | frontrunning_mev / frontrunnable_state_change | **0.74** | **0.73** `sol_am_ma_3` | top3 / miss |
| M-1 Precision loss allows users to giveLoans to pools with less collateral then required | `Lender.sol` | arithmetic_precision / precision_loss_division_before_multiplication | **0.80** | **0.74** `integer_overflow` | top3 / top1 |
| M-2 The `borrow` and `refinance` functions can be front-run by the pool lender to set high interest rates | `Lender.sol` | frontrunning_mev / frontrunnable_state_change | **0.74** | **0.73** `sol_am_ma_3` | top3 / miss |
| M-3 If a borrower or lender got blacklisted by asset contract, their collateral or loan funds can be permanently frozen with the pool | `Lender.sol` | dos_griefing / external_call_revert_dos | **0.78** | **0.86** `sol_basics_al_10` | top1 / top1 |
| M-4 No expiration deadline leads to losing a lot of funds | `Fees.sol` | frontrunning_mev / missing_deadline | **0.66** | **0.85** `front_running_patterns` | top1 / top1 |
| M-5 Malicious lender can increment the loan interest using the auction process | `Lender.sol` | business_logic_state_machine / invalid_state_transition | **0.89** | **0.50** `sol_heuristics_16` | top3 / miss |
| M-6 Single-step process for critical ownership transfer is risky | `Ownable.sol` | access_control / role_management_flaw | 0.06 | **0.98** `sol_cr_6` | not located / top1 |
| M-7 Lender contract can be drained by re-entrancy in `seizeLoan` | `Lender.sol` | reentrancy / single_function_reentrancy | **0.70** | **0.82** `solidity_security` | top3 / top1 |
| M-8 Fixed fee level is used when swap tokens on Uniswap | `Fees.sol` | external_call_token_integration / external_protocol_assumption | **0.78** | **0.84** `sol_token_fe_10` | top1 / top1 |
| M-9 Pragma non-specification can lead to non-functional / corrupted contract when deployed on Arbitrum | `Beedle.sol`, `Fees.sol`, `Lender.sol`, `Staking.sol`, `Errors.sol`, `Ownable.sol`, `Structs.sol`, `IERC20.sol`, `ISwapRouter.sol` | cross_chain_messaging / l2_specific_assumptions | 0.02 | 0.18 `sol_mccc_3` | no function / no function |
| M-10 Frontrun can get the full reward, no staking time required | `Staking.sol` | flash_loan_economic / instant_reward_or_snapshot_gaming | 0.49 | **0.82** `sol_defi_general_8` | not located / top3 |
| M-11 Lender contract can be drained by re-entrancy in `refinance` (collateral) | `Lender.sol` | reentrancy / single_function_reentrancy | **0.70** | **0.82** `solidity_security` | top1 / top3 |
| M-12 Some ERC20 tokens would revert on zero value fee transfers. | `Lender.sol` | external_call_token_integration / — | **0.92** | n/a | top1 / n/a |
| M-13 Rounding error leads to borrowing loans without paying interest | `Lender.sol` | arithmetic_precision / precision_loss_division_before_multiplication | **0.80** | **0.74** `integer_overflow` | miss / top1 |
| M-14 Setting borrower fees to 0 permits the borrow functionality to be completely DoS | `Lender.sol` | dos_griefing / — | **0.78** | n/a | top3 / n/a |
| M-15 The lack of a WETH-Profits Token pair upon calling sellProfits can expose it to malicious pool creation | `Fees.sol` | frontrunning_mev / missing_slippage_protection | **0.66** | **0.96** `sol_defi_as_11` | top1 / top1 |

## Top 10 (file, question) pairs not in the ground truth

These are candidate false positives or real issues the contest did not list. None were verified.

| p | File | Question | Description | Status |
|---|---|---|---|---|
| 0.97 | `src/Fees.sol` | detector:sol_integrations_uniswap_10 | Hard-coded Uniswap V3 fee tier parameter in swap function | unverified |
| 0.96 | `src/Staking.sol` | detector:sol_token_fe_1 | Unsafe ERC20 transfer calls without return-value checks or SafeERC20 wrapper | unverified |
| 0.96 | `src/Lender.sol` | detector:sol_token_fe_1 | Unsafe ERC20 transfer calls without return-value checks or SafeERC20 wrapper | unverified |
| 0.92 | `src/Staking.sol` | detector:sol_basics_math_8 | Unchecked unsigned integer subtraction that can underflow and revert unexpectedly | unverified |
| 0.90 | `src/Staking.sol` | detector:sol_defi_general_1 | Incorrect handling of ERC20 tokens with non-18 decimals causing miscalculation | unverified |
| 0.90 | `src/Staking.sol` | detector:sol_am_dosa_2 | Missing minimum transaction/amount check enabling dust-transaction denial-of-service or griefing | unverified |
| 0.87 | `src/Staking.sol` | detector:solidity_security | Reentrancy vulnerability from unguarded or misordered external calls before state updates | unverified |
| 0.87 | `src/Fees.sol` | detector:sol_am_dosa_3 | Denial-of-service from blacklistable tokens blocking required push transfers | unverified |
| 0.85 | `src/Staking.sol` | detector:sol_basics_payment_4 | Missing minimum deposit/withdrawal threshold enabling dust-amount rounding or DoS exploits | unverified |
| 0.85 | `src/Staking.sol` | category:business_logic_state_machine | Business logic, input validation, and state machine | unverified |
