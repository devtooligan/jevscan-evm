# jevscan benchmark: Sherlock USSD (2023-05)

Ground truth: `bench/ussd/ground_truth.json` (22 H/M issues, categories assigned by hand). Code: https://github.com/sherlock-audit/2023-05-USSD. One run: `jevscan.py` with the default settings (category, detector questions asked, locate threshold 0.5) and jev-1.13.0. A true pair is (issue file, the issue's category / subcategory / any detector mapped to its subcategory). Issues with no fitting subcategory are scored only at category resolution. Ranks are among all asked pairs at that resolution (1 = highest p). Bold p values are >= 0.5.

Files not scanned (Jev file classification): `interfaces/IStableOracle.sol` (interface, 1.00), `interfaces/IStaticOracle.sol` (interface, 1.00), `interfaces/IUSSDRebalancer.sol` (interface, 1.00), `oracles/SimOracle.sol` (mock, 0.96).

## File-level recall

| Resolution | Issues scored | Recall@0.3 | Recall@0.5 | Recall@0.7 | Median rank of true pair | Pairs asked |
|---|---|---|---|---|---|---|
| category | 22 | 22/22 (100%) | 22/22 (100%) | 20/22 (91%) | 3.0 | 112 |
| detector | 16 | 13/16 (81%) | 12/16 (75%) | 8/16 (50%) | 97.5 | 2744 |

Recall is generous: an issue counts as found when any of its true pairs passes, and several issues share one (file, question) pair, so one flag can count for many issues. Distinct true pairs vs issues scored: category 13 for 22, detector 94 for 16. True pairs per scored issue (questions x files), mean: category 1.3, detector 9.0. At detector resolution that is every detector mapped to the issue's subcategory, in every issue file.

## Broad questions per file

| File | H/M issues | any_bug | critical_bug | critical_bug (old wording) | Likely issues listed |
|---|---|---|---|---|---|
| `USSDRebalancer.sol` | 9 | 0.87 | 0.84 | 0.71 | 5 |
| `USSD.sol` | 6 | 0.89 | 0.85 | 0.76 | 10 |
| `oracles/StableOracleDAI.sol` | 5 | 0.81 | 0.68 | 0.25 | 2 |
| `oracles/StableOracleWBTC.sol` | 4 | 0.74 | 0.69 | 0.18 | 2 |
| `oracles/StableOracleWETH.sol` | 3 | 0.63 | 0.59 | 0.14 | 2 |
| `oracles/StableOracleWBGL.sol` | 1 | 0.62 | 0.41 | 0.13 | 2 |
| `Migrations.sol` | 0 | 0.33 | 0.08 | 0.08 | 0 |
| `oracles/UniswapV3StaticOracle.sol` | 0 | 0.43 | 0.38 | 0.13 | 4 |

- any_bug: mean 0.76 on files with issues, 0.38 on files without
- critical_bug: mean 0.68 on files with issues, 0.23 on files without
- critical_bug (old wording): mean 0.36 on files with issues, 0.11 on files without

## False-positive proxy

Files with no issue (2): `Migrations.sol`, `oracles/UniswapV3StaticOracle.sol`

| Resolution | Threshold | Flags | True flags | Flags on files with no issue |
|---|---|---|---|---|
| category | 0.3 | 37 | 13 | 3 |
| category | 0.5 | 28 | 13 | 0 |
| category | 0.7 | 18 | 11 | 0 |
| detector | 0.3 | 203 | 50 | 15 |
| detector | 0.5 | 145 | 44 | 9 |
| detector | 0.7 | 91 | 35 | 2 |

## Flags without a known finding

A flag is a (file, category) pair whose file-level p is at or over the threshold. It is matched when the ground truth has a finding in that file with that category.

| Threshold | Flags | Matched | Unmatched | Unmatched share |
|---|---|---|---|---|
| 0.5 | 28 | 13 | 15 | 54% |
| 0.7 | 18 | 11 | 7 | 39% |

Unmatched flags at 0.5 (possibly unreported, or a false positive — not verified):

| File | Category | p | Note |
|---|---|---|---|
| `USSD.sol` | oracle_price_manipulation | 0.83 |  |
| `oracles/StableOracleDAI.sol` | arithmetic_precision | 0.83 |  |
| `USSD.sol` | arithmetic_precision | 0.82 |  |
| `USSD.sol` | external_call_token_integration | 0.81 |  |
| `USSDRebalancer.sol` | external_call_token_integration | 0.81 |  |
| `USSDRebalancer.sol` | accounting_share_math | 0.75 |  |
| `USSDRebalancer.sol` | frontrunning_mev | 0.72 |  |
| `oracles/StableOracleWBTC.sol` | arithmetic_precision | 0.69 |  |
| `USSD.sol` | dos_griefing | 0.68 |  |
| `oracles/StableOracleWBGL.sol` | arithmetic_precision | 0.61 |  |
| `USSDRebalancer.sol` | reentrancy | 0.58 |  |
| `oracles/StableOracleWETH.sol` | arithmetic_precision | 0.55 |  |
| `USSD.sol` | reentrancy | 0.53 |  |
| `USSDRebalancer.sol` | access_control | 0.53 |  |
| `USSD.sol` | proxy_upgradeability | 0.51 |  |

## Locating (file-level threshold 0.5)

An issue is scored when it names a function, on exactly one function ranking: its true (file, question) pair with the highest file-level p (ties broken by file and question id). The pair is chosen from the file-level answers alone, so no issue gets the best of several rankings. Top-1/top-3: one of the issue's functions is ranked first / in the top 3 in that ranking. The random baseline uses the same ranking: with n functions of which k are the issue's, top-1 chance k/n and top-3 chance 1 - C(n-k,3)/C(n,3), summed over the located issues. 'Not located' means the scored pair was below 0.5 at file level (so every true pair was), and nothing was re-asked per function.

| Resolution | Scorable issues | Located | Top-1 | Top-3 | Random top-1 (expected) | Random top-3 (expected) |
|---|---|---|---|---|---|---|
| category | 21 | 21 | 14/21 | 20/21 | 4.9 | 11.0 |
| detector | 16 | 12 | 9/12 | 11/12 | 3.2 | 7.1 |

## Line locating (experimental)

For each (function, question) whose function-level p >= 0.5, one Choice question picks the primary vulnerable line. An issue is scored on the same pair as above, at the issue function ranked highest for it, when the report links a snippet (line range) in that file and that function got a line answer. The random baseline uses the same Choice: with n options of which k fall in a snippet. Snippets that span a whole function make this easy.

| Resolution | Issues with snippet and a line answer | Top-1 in snippet | Top-3 in snippet | Random top-1 (expected) | Random top-3 (expected) |
|---|---|---|---|---|---|
| category | 15 | 11/15 | 12/15 | 7.6 | 9.5 |
| detector | 6 | 5/6 | 5/6 | 4.5 | 5.0 |

## Repo-level

One request over all 8 scanned files (~9,612 estimated tokens). Most suspicious file (Choice): `USSDRebalancer.sol` (0.61); the file with the most ground-truth issues is `USSDRebalancer.sol` (9).

| Question | Repo-level p | Per-file max | Argmax file |
|---|---|---|---|
| broad:any_bug | 0.91 | 0.89 | `USSD.sol` |
| broad:critical_bug | 0.89 | 0.85 | `USSD.sol` |
| category:access_control | 0.74 | 0.73 | `USSD.sol` |
| category:proxy_upgradeability | 0.47 | 0.51 | `USSD.sol` |
| category:oracle_price_manipulation | 0.84 | 0.91 | `oracles/StableOracleDAI.sol` |
| category:flash_loan_economic | 0.63 | 0.51 | `USSD.sol` |
| category:reentrancy | 0.58 | 0.58 | `USSDRebalancer.sol` |
| category:accounting_share_math | 0.79 | 0.75 | `USSDRebalancer.sol` |
| category:arithmetic_precision | 0.89 | 0.90 | `USSDRebalancer.sol` |
| category:signature_replay | 0.08 | 0.06 | `USSD.sol` |
| category:cross_chain_messaging | 0.05 | 0.04 | `USSD.sol` |
| category:external_call_token_integration | 0.87 | 0.81 | `USSD.sol` |
| category:business_logic_state_machine | 0.89 | 0.89 | `USSD.sol` |
| category:dos_griefing | 0.81 | 0.72 | `USSDRebalancer.sol` |
| category:frontrunning_mev | 0.84 | 0.88 | `USSD.sol` |
| category:legacy_low_level | 0.15 | 0.09 | `USSDRebalancer.sol` |

## HEATMAP order

HEATMAP.md's grid has 8 files; its strongest-hits table has 32 functions.

| Issues found within | First N rows | Count |
|---|---|---|
| issue function in the strongest-hits table | 5 | 7/21 |
| issue function in the strongest-hits table | 10 | 16/21 |
| issue function in the strongest-hits table | 20 | 20/21 |
| issue function in the strongest-hits table | 32 | 21/21 |
| issue file among the top grid rows | 1 | 5/22 |
| issue file among the top grid rows | 3 | 20/22 |

Per issue (row of its first function in the strongest-hits table, or - if not listed): H-1 1, H-2 11, H-3 7, H-4 1, H-5 7, H-6 10, H-7 15, H-8 8, H-9 9, H-10 22, H-11 3, M-1 1, M-2 14, M-3 10, M-4 2, M-5 6, M-6 10, M-7 1, M-8 10, M-9 5, M-10 11, M-11 -

## Cost

| Phase | Requests | Cached | Input tokens | Cost | Wall time |
|---|---|---|---|---|---|
| model_probe | 1 | 0 | 282 | $0.0000 | 0.34s |
| classify | 12 | 12 | 10,517 | $0.0004 | 0.0s |
| scan | 32 | 32 | 863,564 | $0.0363 | 0.03s |
| locate | 101 | 101 | 773,366 | $0.0325 | 0.02s |
| repo | 2 | 2 | 23,450 | $0.0010 | 0.0s |

| Scan level (broad questions ride with category) | Requests | Input tokens | Cost |
|---|---|---|---|
| category | 8 | 23,447 | $0.0010 |
| detector | 24 | 840,117 | $0.0353 |

## Issues

| Issue | Files | Category / subcategory | category | detector | Located (category / detector) |
|---|---|---|---|---|---|
| H-1 StableOracleDAI calculates getPriceUSD with inverted base/rate tokens for Chainlink price | `StableOracleDAI.sol` | oracle_price_manipulation / oracle_decimals_and_units | **0.91** | **0.62** `sol_defi_oracle_8` | top1 / top1 |
| H-2 USSDRebalancer.sol#SellUSSDBuyCollateral the check of whether collateral is DAI is wrong | `USSDRebalancer.sol` | business_logic_state_machine / — | **0.89** | n/a | top1 / n/a |
| H-3 The getOwnValuation() function contains errors in the price calculation | `USSDRebalancer.sol` | arithmetic_precision / incorrect_formula | **0.90** | 0.16 `sol_heuristics_7` | top3 / not located |
| H-4 The price from StableOracleDAI is returned with the incorrect number of decimals | `StableOracleDAI.sol` | oracle_price_manipulation / oracle_decimals_and_units | **0.91** | **0.62** `sol_defi_oracle_8` | top1 / top1 |
| H-5 Price calculation susceptible to flashloan exploits | `USSDRebalancer.sol` | oracle_price_manipulation / spot_price_dependency | **0.84** | **0.95** `sol_integrations_uniswap_9` | top1 / top1 |
| H-6 Wrong computation of the amountToSellUnit variable | `USSDRebalancer.sol` | arithmetic_precision / incorrect_formula | **0.90** | 0.16 `sol_heuristics_7` | top1 / not located |
| H-7 Not using slippage parameter or deadline while swapping on UniswapV3 | `USSD.sol` | frontrunning_mev / missing_slippage_protection | **0.88** | **0.93** `front_running_patterns` | top1 / top1 |
| H-8 Lack of access control for mintRebalancer() and burnRebalancer() | `USSD.sol` | access_control / missing_auth_on_privileged_function | **0.73** | **0.74** `sol_basics_function_9` | top1 / top1 |
| H-9 Uniswap v3 pool token balance proportion does not necessarily correspond to the price, and it is easy to manipulate. | `USSDRebalancer.sol` | oracle_price_manipulation / spot_price_dependency | **0.84** | **0.95** `sol_integrations_uniswap_9` | miss / top3 |
| H-10 Wrong Oracle feed addresses | `StableOracleWBTC.sol`, `StableOracleDAI.sol`, `StableOracleWBGL.sol` | oracle_price_manipulation / — | **0.91** | n/a | top3 / n/a |
| H-11 Oracle price should be denominated in DAI instead of USD | `StableOracleWETH.sol` | oracle_price_manipulation / oracle_decimals_and_units | **0.86** | 0.07 `sol_defi_oracle_12` | top1 / not located |
| M-1 Calls to Oracles don't check for stale prices | `StableOracleDAI.sol`, `StableOracleWBTC.sol`, `StableOracleWETH.sol` | oracle_price_manipulation / chainlink_validation_missing | **0.91** | **0.98** `sol_defi_oracle_7` | top1 / top1 |
| M-2 Because of missing slippage parameter, mintForToken() can be front-runned | `USSD.sol` | frontrunning_mev / missing_slippage_protection | **0.88** | **0.93** `front_running_patterns` | top3 / top3 |
| M-3 rebalance process incase of selling the collateral, could revert because of underflow calculation | `USSDRebalancer.sol` | dos_griefing / — | **0.72** | n/a | top3 / n/a |
| M-4 StableOracleWBTC use BTC/USD chainlink oracle to price WBTC which is problematic if WBTC depegs | `StableOracleWBTC.sol` | oracle_price_manipulation / oracle_decimals_and_units | **0.89** | **0.56** `sol_defi_oracle_12` | top1 / top1 |
| M-5 Inaccurate collateral factor calculation due to missing collateral asset | `USSD.sol` | accounting_share_math / state_update_omission_or_double_count | **0.64** | **0.54** `sol_heuristics_16` | top1 / miss |
| M-6 Inconsistency handling of DAI as collateral in the BuyUSSDSellCollateral function | `USSDRebalancer.sol` | business_logic_state_machine / — | **0.89** | n/a | top3 / n/a |
| M-7 Risk of Incorrect Asset Pricing by StableOracle in Case of Underlying Aggregator Reaching minAnswer | `StableOracleDAI.sol`, `StableOracleWBTC.sol`, `StableOracleWETH.sol` | oracle_price_manipulation / chainlink_validation_missing | **0.91** | **0.98** `sol_defi_oracle_7` | top1 / top1 |
| M-8 BuyUSSDSellCollateral() always sells 0 amount if need to sell part of collateral | `USSDRebalancer.sol` | arithmetic_precision / precision_loss_division_before_multiplication | **0.90** | **0.86** `sol_basics_math_12` | top1 / top1 |
| M-9 Using the collateral assets' oracle price at 100% of its value to mint USSD without a fee can be used for arbitrage. | `USSD.sol` | flash_loan_economic / atomic_arbitrage_of_protocol_pricing | **0.51** | 0.39 `sol_defi_flashloan_2` | top3 / not located |
| M-10 If collateral factor is high enough, flutter ends up being out of bounds | `USSDRebalancer.sol` | business_logic_state_machine / — | **0.89** | n/a | top1 / n/a |
| M-11 Lack of Redeem Feature | `USSD.sol` | business_logic_state_machine / — | **0.89** | n/a | no function / no function |

## Top 10 (file, question) pairs not in the ground truth

These are candidate false positives or real issues the contest did not list. None were verified.

| p | File | Question | Description | Status |
|---|---|---|---|---|
| 0.96 | `USSDRebalancer.sol` | detector:sol_integrations_uniswap_10 | Hard-coded Uniswap V3 fee tier parameter in swap function | unverified |
| 0.96 | `USSD.sol` | detector:sol_defi_oracle_14 | Missing sanity/range check on oracle price allows flash-crash price manipulation | unverified |
| 0.94 | `USSD.sol` | detector:sol_token_fe_13 | ERC20 approve() called directly to non-zero value without resetting allowance to zero first | unverified |
| 0.93 | `USSD.sol` | detector:sol_token_fe_1 | Unsafe ERC20 transfer calls without return-value checks or SafeERC20 wrapper | unverified |
| 0.93 | `USSD.sol` | detector:sol_defi_oracle_2 | Unvalidated zero price from oracle feed used without a sanity check | unverified |
| 0.93 | `USSD.sol` | detector:sol_defi_general_6 | Unbounded/maximum token approval allowed without revert, enabling over-allowance abuse | unverified |
| 0.93 | `USSD.sol` | detector:erc20_patterns | Unsafe ERC-20 token integration without SafeERC20 or received-amount accounting | unverified |
| 0.92 | `oracles/StableOracleWBGL.sol` | detector:sol_defi_oracle_14 | Missing sanity/range check on oracle price allows flash-crash price manipulation | unverified |
| 0.92 | `oracles/StableOracleDAI.sol` | detector:sol_basics_math_6 | Division-by-zero causing unintended revert due to unchecked denominator | unverified |
| 0.92 | `USSDRebalancer.sol` | detector:sol_defi_oracle_14 | Missing sanity/range check on oracle price allows flash-crash price manipulation | unverified |
