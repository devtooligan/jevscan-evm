# 🔥 jevscan heat map: ussd-contracts

**89% chance of a critical bug · 91% chance of at least one exploitable bug · hottest file: `USSDRebalancer.sol`**

Numbers are Jev's probability that the statement is true.

| Codebase | |
|---|---|
| Name | ussd-contracts |
| Solidity files found | 12 |
| Lines of code | 734 (non-blank, scanned files) |
| Scanned | 8 |
| Ignored | 3 interfaces, 1 mock |

148 requests · $0.07 · 0.4 s · 147 answers from cache (billed <$0.01)

## Heat grid

| File | Crit | Any | Access | Proxy | Oracle | Econ | Reentry | Shares | Math | Sigs | Xchain | Tokens | Logic | DoS | MEV | LowLvl |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `oracles/StableOracleDAI.sol` | 🟧 | 🟥 | 🟩 | 🟩 | 🟥 | 🟨 | 🟩 | 🟩 | 🟥 | 🟩 | 🟩 | 🟩 | 🟨 | 🟨 | 🟩 | 🟩 |
| `USSDRebalancer.sol` | 🟥 | 🟥 | 🟧 | 🟨 | 🟥 | 🟨 | 🟧 | 🟥 | 🟥 | 🟩 | 🟩 | 🟥 | 🟥 | 🟥 | 🟥 | 🟩 |
| `USSD.sol` | 🟥 | 🟥 | 🟥 | 🟧 | 🟥 | 🟧 | 🟧 | 🟧 | 🟥 | 🟩 | 🟩 | 🟥 | 🟥 | 🟧 | 🟥 | 🟩 |
| `oracles/StableOracleWBTC.sol` | 🟧 | 🟥 | 🟩 | 🟩 | 🟥 | 🟨 | 🟩 | 🟩 | 🟧 | 🟩 | 🟩 | 🟩 | 🟩 | 🟩 | 🟩 | 🟩 |
| `oracles/StableOracleWETH.sol` | 🟧 | 🟧 | 🟩 | 🟩 | 🟥 | 🟩 | 🟩 | 🟩 | 🟧 | 🟩 | 🟩 | 🟩 | 🟩 | 🟩 | 🟩 | 🟩 |
| `oracles/StableOracleWBGL.sol` | 🟨 | 🟧 | 🟩 | 🟩 | 🟥 | 🟩 | 🟩 | 🟩 | 🟧 | 🟩 | 🟩 | 🟩 | 🟩 | 🟩 | 🟩 | 🟩 |
| `oracles/UniswapV3StaticOracle.sol` | 🟨 | 🟨 | 🟩 | 🟩 | 🟨 | 🟩 | 🟩 | 🟩 | 🟨 | 🟩 | 🟩 | 🟩 | 🟨 | 🟩 | 🟩 | 🟩 |
| `Migrations.sol` | 🟩 | 🟨 | 🟩 | 🟩 | 🟩 | 🟩 | 🟩 | 🟩 | 🟩 | 🟩 | 🟩 | 🟩 | 🟩 | 🟩 | 🟩 | 🟩 |

- 🟥 70% or more
- 🟧 50% to 70%
- 🟨 30% to 50%
- 🟩 under 30%

<details><summary>What the columns mean</summary>

- **Crit**: an attacker can gain value: steal or lock funds, or exploit mispricing
- **Any**: at least one exploitable vulnerability of any kind
- **Access**: who may call what: missing or wrong permission checks
- **Proxy**: proxies, upgrades, initializers, and storage layout
- **Oracle**: price feeds and oracle manipulation
- **Econ**: flash loans and economic attacks
- **Reentry**: reentrancy: an outside call re-enters before state is updated
- **Shares**: vault shares, balances, rewards, and fee accounting
- **Math**: rounding, precision loss, overflow, and decimals
- **Sigs**: signatures and replay
- **Xchain**: bridges and cross-chain or L2 messages
- **Tokens**: external calls and unusual token behavior
- **Logic**: business logic, input checks, and state transitions
- **DoS**: denial of service and griefing
- **MEV**: front-running, slippage, MEV, and randomness
- **LowLvl**: low-level EVM pitfalls: tx.origin, delegatecall, assembly, selfdestruct

</details>

## Strongest function hits (70%+): 32

Every function whose strongest hit is 70% or more, by that hit. Its other hits, and every function hit from 50% to 70%, are under its file below.

| File | Function | Lines | What it found | Chance | Line | Corresponding findings |
|---|---|---|---|---|---|---|
| `oracles/StableOracleDAI.sol` | `getPriceUSD` | 33-53 | Unsafe Chainlink price feed consumption without staleness/validity/sequencer checks | 97% | 48 | H-1, H-4, M-1, M-7 |
| `oracles/StableOracleWBTC.sol` | `getPriceUSD` | 21-26 | Unsafe Chainlink price feed consumption without staleness/validity/sequencer checks | 97% | 23 | M-1, M-4, M-7 |
| `oracles/StableOracleWETH.sol` | `getPriceUSD` | 21-26 | Unsafe Chainlink price feed consumption without staleness/validity/sequencer checks | 97% | 23 | H-11, M-1, M-7 |
| `USSD.sol` | `approveToRouter` | 242-247 | Unsafe ERC20 transfer calls without return-value checks or SafeERC20 wrapper | 96% | 243 |  |
| `USSD.sol` | `calculateMint` | 170-173 | Missing sanity/range check on oracle price allows flash-crash price manipulation | 95% | 171 |  |
| `USSD.sol` | `collateralFactor` | 179-194 | Division-by-zero causing unintended revert due to unchecked denominator | 94% | 193 | M-5 |
| `USSDRebalancer.sol` | `getOwnValuation` | 71-80 | Manipulable Uniswap V3 spot price via slot0 used for sensitive price calculations | 94% | 72 | H-3, H-5 |
| `USSD.sol` | `mintRebalancer` | 204-206 | Missing access control on sensitive privileged functions | 93% | 205 | H-8 |
| `USSDRebalancer.sol` | `rebalance` | 92-107 | Missing access control on sensitive state-changing function | 93% | 92 | H-9 |
| `USSDRebalancer.sol` | `BuyUSSDSellCollateral` | 109-161 | Missing swap deadline parameter enabling delayed transaction sandwich/MEV attacks | 93% | 122 | H-6, M-3, M-6, M-8 |
| `USSDRebalancer.sol` | `SellUSSDBuyCollateral` | 163-205 | Missing slippage protection allowing sandwich attacks on user trades/swaps | 93% | 169 | H-2, M-10 |
| `oracles/StableOracleWBGL.sol` | `getPriceUSD` | 24-39 | Missing sanity/range check on oracle price allows flash-crash price manipulation | 93% | 38 |  |
| `oracles/UniswapV3StaticOracle.sol` | `addNewFeeTier` | 141-147 | Missing access control on sensitive state-changing function | 92% | 141 |  |
| `USSD.sol` | `mintForToken` | 151-167 | Fee-on-transfer token accounting mismatch from assuming transferred amount equals received amount | 91% | 163 | M-2 |
| `USSD.sol` | `UniV3SwapInput` | 227-240 | Missing minimum output amount check before AMM token swap, enabling sandwich/slippage attacks | 90% | 237 | H-7 |
| `oracles/UniswapV3StaticOracle.sol` | `_quote` | 160-176 | TWAP oracle period set too short, enabling price manipulation via short-window time-weighted average price | 89% | 165 |  |
| `USSD.sol` | `initialize` | 31-43 | Missing _disableInitializers() in upgradeable contract constructor allowing implementation takeover | 88% | 34 |  |
| `USSD.sol` | `removeCollateral` | 120-123 | Business logic, input validation, and state machine | 88% | 121 | M-5 |
| `USSD.sol` | `burnRebalancer` | 208-210 | Missing access control on sensitive state-changing function | 87% | 208 | H-8 |
| `USSDRebalancer.sol` | `initialize` | 38-43 | Missing _disableInitializers() in upgradeable contract constructor allowing implementation takeover | 86% | 38 |  |
| `USSD.sol` | `swapCollateralIndexes` | 110-118 | Business logic, input validation, and state machine | 80% | 116 |  |
| `oracles/StableOracleDAI.sol` | `constructor` | 23-31 | Hard-coded, non-updatable price feed/oracle address preventing replacement of deprecated or inaccurate feeds | 78% | 24 |  |
| `oracles/UniswapV3StaticOracle.sol` | `_prepare` | 154-158 | Missing whitelist/factory verification allows interaction with untrusted or malicious Uniswap pools | 78% | 156 |  |
| `oracles/UniswapV3StaticOracle.sol` | `_getCardinalityForTimePeriod` | 149-152 | Unsafe unchecked arithmetic, silent truncation, or phantom overflow in Solidity integer math | 77% | 151 |  |
| `USSD.sol` | `addCollateral` | 84-108 | Business logic, input validation, and state machine | 76% | 104 |  |
| `oracles/StableOracleWBGL.sol` | `constructor` | 17-22 | Hard-coded, non-updatable price feed/oracle address preventing replacement of deprecated or inaccurate feeds | 76% | 19 |  |
| `USSDRebalancer.sol` | `setPoolAddress` | 50-52 | Business logic, input validation, and state machine | 72% | 51 |  |
| `USSDRebalancer.sol` | `setFlutterRatios` | 62-64 | Business logic, input validation, and state machine | 72% | 63 |  |
| `oracles/StableOracleWETH.sol` | `constructor` | 15-19 | Hard-coded, non-updatable price feed/oracle address preventing replacement of deprecated or inaccurate feeds | 72% | 17 |  |
| `oracles/UniswapV3StaticOracle.sol` | `quoteSpecificFeeTiersWithTimePeriod` | 66-76 | TWAP oracle period set too short, enabling price manipulation via short-window time-weighted average price | 71% | 75 |  |
| `oracles/StableOracleWBTC.sol` | `constructor` | 15-19 | Hard-coded, non-updatable price feed/oracle address preventing replacement of deprecated or inaccurate feeds | 70% | 17 | H-10 |
| `oracles/UniswapV3StaticOracle.sol` | `prepareSpecificPoolsWithCardinality` | 136-138 | Missing access control on sensitive state-changing function | 70% | 137 |  |

### Known findings: 21 of 22 found

Found: a function-level hit on the finding's file, one of its functions, and its bug type (category or a detector mapped to it).

| Id | Severity | Title | Found? | Location |
|---|---|---|---|---|
| H-1 | High | StableOracleDAI calculates getPriceUSD with inverted base/rate tokens for Chainlink price | ✅ 90% | `getPriceUSD` line 36 (category oracle_price_manipulation) |
| H-2 | High | USSDRebalancer.sol#SellUSSDBuyCollateral the check of whether collateral is DAI is wrong | ✅ 89% | `SellUSSDBuyCollateral` line 199 (category business_logic_state_machine) |
| H-3 | High | The getOwnValuation() function contains errors in the price calculation | ✅ 86% | `getOwnValuation` line 74 (category arithmetic_precision) |
| H-4 | High | The price from StableOracleDAI is returned with the incorrect number of decimals | ✅ 90% | `getPriceUSD` line 36 (category oracle_price_manipulation) |
| H-5 | High | Price calculation susceptible to flashloan exploits | ✅ 94% | `getOwnValuation` line 72 (detector sol_integrations_uniswap_9) |
| H-6 | High | Wrong computation of the amountToSellUnit variable | ✅ 88% | `BuyUSSDSellCollateral` line 121 (category arithmetic_precision) |
| H-7 | High | Not using slippage parameter or deadline while swapping on UniswapV3 | ✅ 90% | `UniV3SwapInput` line 237 (detector sol_defi_as_11) |
| H-8 | High | Lack of access control for mintRebalancer() and burnRebalancer() | ✅ 93% | `mintRebalancer` line 205 (detector sol_basics_ac_2) |
| H-9 | High | Uniswap v3 pool token balance proportion does not necessarily correspond to the price, and it is easy to manipulate. | ✅ 76% | `rebalance` line 93 (detector flash_loan_attacks) |
| H-10 | High | Wrong Oracle feed addresses | ✅ 51% | `constructor` line 16 (category oracle_price_manipulation) |
| H-11 | High | Oracle price should be denominated in DAI instead of USD | ✅ 91% | `getPriceUSD` line 23 (category oracle_price_manipulation) |
| M-1 | Medium | Calls to Oracles don't check for stale prices | ✅ 97% | `getPriceUSD` line 48 (detector chainlink_oracles) |
| M-2 | Medium | Because of missing slippage parameter, mintForToken() can be front-runned | ✅ 58% | `mintForToken` line 163 (category frontrunning_mev) |
| M-3 | Medium | rebalance process incase of selling the collateral, could revert because of underflow calculation | ✅ 72% | `BuyUSSDSellCollateral` line 115 (category dos_griefing) |
| M-4 | Medium | StableOracleWBTC use BTC/USD chainlink oracle to price WBTC which is problematic if WBTC depegs | ✅ 91% | `getPriceUSD` line 23 (category oracle_price_manipulation) |
| M-5 | Medium | Inaccurate collateral factor calculation due to missing collateral asset | ✅ 52% | `collateralFactor` line 193 (category accounting_share_math) |
| M-6 | Medium | Inconsistency handling of DAI as collateral in the BuyUSSDSellCollateral function | ✅ 84% | `BuyUSSDSellCollateral` line 160 (category business_logic_state_machine) |
| M-7 | Medium | Risk of Incorrect Asset Pricing by StableOracle in Case of Underlying Aggregator Reaching minAnswer | ✅ 97% | `getPriceUSD` line 48 (detector chainlink_oracles) |
| M-8 | Medium | BuyUSSDSellCollateral() always sells 0 amount if need to sell part of collateral | ✅ 88% | `BuyUSSDSellCollateral` line 121 (category arithmetic_precision) |
| M-9 | Medium | Using the collateral assets' oracle price at 100% of its value to mint USSD without a fee can be used for arbitrage. | ❌ |  |
| M-10 | Medium | If collateral factor is high enough, flutter ends up being out of bounds | ✅ 89% | `SellUSSDBuyCollateral` line 199 (category business_logic_state_machine) |
| M-11 | Medium | Lack of Redeem Feature | ✅ 88% | `removeCollateral` line 121 (category business_logic_state_machine) |

### Flags without a known finding: 7 at 70%, 15 at 50%

A flag is a file whose chance for a category is at or over the threshold. These flags have no known finding of that category in that file: possibly unreported issues, or false positives. Not verified.

| File | Category | Chance |
|---|---|---|
| `USSD.sol` | Oracle and price manipulation | 83% |
| `oracles/StableOracleDAI.sol` | Arithmetic and precision | 83% |
| `USSD.sol` | Arithmetic and precision | 82% |
| `USSD.sol` | External calls and token integration | 81% |
| `USSDRebalancer.sol` | External calls and token integration | 81% |
| `USSDRebalancer.sol` | Accounting and share math | 75% |
| `USSDRebalancer.sol` | Front-running, MEV, and randomness | 72% |

<details><summary>All 15 at 50%</summary>

| File | Category | Chance |
|---|---|---|
| `USSD.sol` | Oracle and price manipulation | 83% |
| `oracles/StableOracleDAI.sol` | Arithmetic and precision | 83% |
| `USSD.sol` | Arithmetic and precision | 82% |
| `USSD.sol` | External calls and token integration | 81% |
| `USSDRebalancer.sol` | External calls and token integration | 81% |
| `USSDRebalancer.sol` | Accounting and share math | 75% |
| `USSDRebalancer.sol` | Front-running, MEV, and randomness | 72% |
| `oracles/StableOracleWBTC.sol` | Arithmetic and precision | 69% |
| `USSD.sol` | Denial of service and griefing | 68% |
| `oracles/StableOracleWBGL.sol` | Arithmetic and precision | 61% |
| `USSDRebalancer.sol` | Reentrancy | 58% |
| `oracles/StableOracleWETH.sol` | Arithmetic and precision | 55% |
| `USSD.sol` | Reentrancy | 53% |
| `USSDRebalancer.sol` | Access control and privilege | 53% |
| `USSD.sol` | Proxy, upgradeability, and storage layout | 51% |

</details>

## File details

<details><summary>oracles/StableOracleDAI.sol · Crit 🟧 · Any 🟥 · Oracle 91%, Math 83% · 2 functions flagged</summary>

| Function | Lines | Strongest hit | Question | Chance | Line | More |
|---|---|---|---|---|---|---|
| `getPriceUSD` | 33-53 | Unsafe Chainlink price feed consumption without staleness/validity/sequencer checks | detector chainlink_oracles | 97% | 48 | <details><summary>14 more</summary>Missing staleness/heartbeat check on price oracle data, allowing use of stale prices (detector sol_defi_oracle_7) 96%, line 48<br>Missing staleness check on oracle price feed timestamp allows use of outdated prices (detector sol_defi_oracle_3) 95%, line 48<br>Missing sanity/range check on oracle price allows flash-crash price manipulation (detector sol_defi_oracle_14) 94%, line 48<br>Oracle and price manipulation (category oracle_price_manipulation) 90%, line 36<br>Division-by-zero causing unintended revert due to unchecked denominator (detector sol_basics_math_6) 89%, line 51<br>Unvalidated zero price from oracle feed used without a sanity check (detector sol_defi_oracle_2) 86%, line 48<br>Incorrect handling of differing ERC20 token decimals in calculations (detector sol_token_fe_3) 84%, line 51<br>Unhandled min/max boundary values causing incorrect or unsafe arithmetic results (detector sol_basics_math_12) 83%, line 52<br>Use of deprecated Chainlink price feed functions returning stale or incorrect oracle data (detector sol_defi_oracle_1) 83%, line 48<br>Missing L2 sequencer uptime check when consuming Chainlink price feeds (detector sol_defi_oracle_4) 83%, line 48<br>Arithmetic and precision (category arithmetic_precision) 82%, line 52<br>Unsafe unchecked arithmetic, silent truncation, or phantom overflow in Solidity integer math (detector integer_overflow) 81%, line 51<br>Incorrect handling of ERC20 tokens with non-18 decimals causing miscalculation (detector sol_defi_general_1) 68%, line 51<br>Mismatched decimal precision across multiple price feeds causing incorrect price calculations (detector sol_defi_oracle_8) 62%, line 52</details> |
| `constructor` | 23-31 | Hard-coded, non-updatable price feed/oracle address preventing replacement of deprecated or inaccurate feeds | detector sol_defi_oracle_9 | 78% | 24 |  |

<details><summary>File-level hits (16)</summary>

| Chance | Question | What it asks |
|---|---|---|
| 97% | detector chainlink_oracles | Unsafe Chainlink price feed consumption without staleness/validity/sequencer checks |
| 96% | detector sol_defi_oracle_7 | Missing staleness/heartbeat check on price oracle data, allowing use of stale prices |
| 95% | detector sol_defi_oracle_3 | Missing staleness check on oracle price feed timestamp allows use of outdated prices |
| 93% | detector sol_defi_oracle_14 | Missing sanity/range check on oracle price allows flash-crash price manipulation |
| 92% | detector sol_basics_math_6 | Division-by-zero causing unintended revert due to unchecked denominator |
| 91% | category oracle_price_manipulation | Oracle and price manipulation |
| 89% | detector sol_defi_oracle_9 | Hard-coded, non-updatable price feed/oracle address preventing replacement of deprecated or inaccurate feeds |
| 87% | detector sol_defi_oracle_2 | Unvalidated zero price from oracle feed used without a sanity check |
| 85% | detector sol_defi_oracle_1 | Use of deprecated Chainlink price feed functions returning stale or incorrect oracle data |
| 83% | category arithmetic_precision | Arithmetic and precision |
| 83% | detector sol_token_fe_3 | Incorrect handling of differing ERC20 token decimals in calculations |
| 79% | detector sol_defi_oracle_4 | Missing L2 sequencer uptime check when consuming Chainlink price feeds |
| 78% | detector sol_basics_math_12 | Unhandled min/max boundary values causing incorrect or unsafe arithmetic results |
| 64% | detector integer_overflow | Unsafe unchecked arithmetic, silent truncation, or phantom overflow in Solidity integer math |
| 62% | detector sol_defi_oracle_8 | Mismatched decimal precision across multiple price feeds causing incorrect price calculations |
| 50% | detector sol_defi_general_1 | Incorrect handling of ERC20 tokens with non-18 decimals causing miscalculation |

</details>


</details>

<details><summary>USSDRebalancer.sol · Crit 🟥 · Any 🟥 · Math 90%, Logic 89%, Oracle 84% · 10 functions flagged</summary>

| Function | Lines | Strongest hit | Question | Chance | Line | More |
|---|---|---|---|---|---|---|
| `getOwnValuation` | 71-80 | Manipulable Uniswap V3 spot price via slot0 used for sensitive price calculations | detector sol_integrations_uniswap_9 | 94% | 72 | <details><summary>15 more</summary>Oracle price manipulation via AMM spot price used as price feed (detector sol_defi_oracle_13) 90%, line 72<br>Flash-loan-exploitable use of manipulable spot price/balance/voting power within a single transaction (detector flash_loan_attacks) 88%, line 72<br>Arithmetic and precision (category arithmetic_precision) 86%, line 74<br>Price derived from manipulable DEX spot reserves instead of TWAP/oracle (detector sol_am_pma_2) 85%, line 74<br>Using manipulable Uniswap pool reserves/spot price for critical pricing or logic (detector sol_integrations_uniswap_5) 84%, line 72<br>Oracle and price manipulation (category oracle_price_manipulation) 82%, line 72<br>Missing sanity/range check on oracle price allows flash-crash price manipulation (detector sol_defi_oracle_14) 82%, line 74<br>Manipulable spot-price oracle (DEX reserves) used for value-critical calculations without TWAP or safeguards (detector oracle_manipulation) 78%, line 72<br>Unhandled min/max boundary values causing incorrect or unsafe arithmetic results (detector sol_basics_math_12) 78%, line 78<br>Price derived from spot token balance ratio, manipulable via flash loans/donations (detector sol_am_pma_1) 77%, line 72<br>Incorrect handling of differing ERC20 token decimals in calculations (detector sol_token_fe_3) 76%, line 76<br>Unsafe unchecked arithmetic, silent truncation, or phantom overflow in Solidity integer math (detector integer_overflow) 69%, line 74<br>AMM miscalculates swaps/liquidity due to unhandled token decimal or non-standard token behavior (detector sol_defi_as_8) 64%, line 76<br>Division-by-zero causing unintended revert due to unchecked denominator (detector sol_basics_math_6) 57%, line 78<br>Unvalidated zero price from oracle feed used without a sanity check (detector sol_defi_oracle_2) 54%, line 72</details> |
| `rebalance` | 92-107 | Missing access control on sensitive state-changing function | detector sol_basics_function_9 | 93% | 92 | <details><summary>28 more</summary>Access control and privilege (category access_control) 91%, line 92<br>Missing slippage/deadline protection on swaps enabling sandwich/front-running attacks (detector front_running_patterns) 84%, line 97<br>Precision loss from performing division before multiplication in arithmetic expressions (detector sol_basics_math_4) 84%, line 104<br>Arithmetic and precision (category arithmetic_precision) 81%, line 104<br>Missing slippage protection in swap/trade functions allowing excessive price deviation losses (detector sol_defi_as_7) 80%, line 97<br>Missing slippage protection allowing sandwich attacks on user trades/swaps (detector sol_am_sandwichattack_1) 79%, line 97<br>Incorrect handling of differing ERC20 token decimals in calculations (detector sol_token_fe_3) 79%, line 97<br>Business logic, input validation, and state machine (category business_logic_state_machine) 78%, line 104<br>Front-running, MEV, and randomness (category frontrunning_mev) 78%, line 105<br>External calls and token integration (category external_call_token_integration) 76%, line 104<br>Flash-loan-exploitable use of manipulable spot price/balance/voting power within a single transaction (detector flash_loan_attacks) 76%, line 93<br>Missing swap deadline parameter enabling delayed transaction sandwich/MEV attacks (detector sol_defi_as_2) 76%, line 97<br>Unchecked unsigned integer subtraction that can underflow and revert unexpectedly (detector sol_basics_math_8) 75%, line 97<br>Missing minimum output amount check before AMM token swap, enabling sandwich/slippage attacks (detector sol_defi_as_11) 72%, line 97<br>Unhandled min/max boundary values causing incorrect or unsafe arithmetic results (detector sol_basics_math_12) 70%, line 97<br>Missing front-running/sandwich-attack protection due to transaction-order-sensitive logic (detector sol_am_ma_3) 68%, line 105<br>Accounting and share math (category accounting_share_math) 67%, line 104<br>Oracle and price manipulation (category oracle_price_manipulation) 65%, line 93<br>Reentrancy (category reentrancy) 64%, line 97<br>Function vulnerable to front-running enabling DoS or value extraction by transaction ordering (detector sol_basics_function_3) 63%, line 92<br>Price derived from spot token balance ratio, manipulable via flash loans/donations (detector sol_am_pma_1) 61%, line 93<br>Using manipulable Uniswap pool reserves/spot price for critical pricing or logic (detector sol_integrations_uniswap_5) 61%, line 94<br>AMM miscalculates swaps/liquidity due to unhandled token decimal or non-standard token behavior (detector sol_defi_as_8) 58%, line 97<br>Denial of service and griefing (category dos_griefing) 57%, line 105<br>Reentrancy vulnerability from unguarded or misordered external calls before state updates (detector solidity_security) 54%, line 97<br>Hardcoded slippage tolerance in AMM/swap trade execution instead of user-specified minimum (detector sol_defi_as_1) 53%, line 104<br>Oracle price manipulation via AMM spot price used as price feed (detector sol_defi_oracle_13) 50%, line 93<br>Cross-function/read-only reentrancy from external calls before state updates (detector sol_ec_1) 50%, line 97</details> |
| `BuyUSSDSellCollateral` | 109-161 | Missing swap deadline parameter enabling delayed transaction sandwich/MEV attacks | detector sol_defi_as_2 | 93% | 122 | <details><summary>33 more</summary>Missing slippage protection in swap/trade functions allowing excessive price deviation losses (detector sol_defi_as_7) 92%, line 122<br>Missing sanity/range check on oracle price allows flash-crash price manipulation (detector sol_defi_oracle_14) 92%, line 116<br>Missing slippage protection allowing sandwich attacks on user trades/swaps (detector sol_am_sandwichattack_1) 90%, line 122<br>Hard-coded Uniswap V3 fee tier parameter in swap function (detector sol_integrations_uniswap_10) 90%, line 154<br>Arithmetic and precision (category arithmetic_precision) 88%, line 121<br>Unhandled min/max boundary values causing incorrect or unsafe arithmetic results (detector sol_basics_math_12) 85%, line 121<br>Missing minimum output amount check before AMM token swap, enabling sandwich/slippage attacks (detector sol_defi_as_11) 85%, line 122<br>Business logic, input validation, and state machine (category business_logic_state_machine) 84%, line 160<br>External calls and token integration (category external_call_token_integration) 83%, line 122<br>Hardcoded slippage tolerance in AMM/swap trade execution instead of user-specified minimum (detector sol_defi_as_1) 82%, line 149<br>Front-running, MEV, and randomness (category frontrunning_mev) 80%, line 154<br>Missing slippage/deadline protection on swaps enabling sandwich/front-running attacks (detector front_running_patterns) 80%, line 122<br>Oracle and price manipulation (category oracle_price_manipulation) 79%, line 116<br>Missing front-running/sandwich-attack protection due to transaction-order-sensitive logic (detector sol_am_ma_3) 79%, line 122<br>Unvalidated zero price from oracle feed used without a sanity check (detector sol_defi_oracle_2) 78%, line 116<br>Missing staleness check on oracle price feed timestamp allows use of outdated prices (detector sol_defi_oracle_3) 78%, line 116<br>Flash-loan-exploitable use of manipulable spot price/balance/voting power within a single transaction (detector flash_loan_attacks) 77%, line 116<br>Precision loss from performing division before multiplication in arithmetic expressions (detector sol_basics_math_4) 76%, line 127<br>Denial-of-service via unbounded loop with external calls that can revert entire operation (detector sol_basics_al_10) 73%, line 135<br>Reentrancy (category reentrancy) 72%, line 122<br>Denial of service and griefing (category dos_griefing) 72%, line 115<br>Missing staleness/heartbeat check on price oracle data, allowing use of stale prices (detector sol_defi_oracle_7) 72%, line 116<br>Access control and privilege (category access_control) 71%, line 160<br>Division-by-zero causing unintended revert due to unchecked denominator (detector sol_basics_math_6) 71%, line 127<br>AMM miscalculates swaps/liquidity due to unhandled token decimal or non-standard token behavior (detector sol_defi_as_8) 71%, line 121<br>Reentrancy vulnerability from unguarded or misordered external calls before state updates (detector solidity_security) 71%, line 122<br>Accounting and share math (category accounting_share_math) 70%, line 160<br>Unchecked unsigned integer subtraction that can underflow and revert unexpectedly (detector sol_basics_math_8) 67%, line 123<br>Incorrect handling of differing ERC20 token decimals in calculations (detector sol_token_fe_3) 65%, line 116<br>Unsafe unchecked arithmetic, silent truncation, or phantom overflow in Solidity integer math (detector integer_overflow) 64%, line 121<br>Unbounded array/loop iteration causing out-of-gas denial of service (detector sol_basics_al_9) 63%, line 115<br>Cross-function/read-only reentrancy from external calls before state updates (detector sol_ec_1) 62%, line 122<br>Function vulnerable to front-running enabling DoS or value extraction by transaction ordering (detector sol_basics_function_3) 55%, line 116</details> |
| `SellUSSDBuyCollateral` | 163-205 | Missing slippage protection allowing sandwich attacks on user trades/swaps | detector sol_am_sandwichattack_1 | 93% | 169 | <details><summary>32 more</summary>Missing sanity/range check on oracle price allows flash-crash price manipulation (detector sol_defi_oracle_14) 93%, line 190<br>Division-by-zero causing unintended revert due to unchecked denominator (detector sol_basics_math_6) 92%, line 201<br>Missing slippage protection in swap/trade functions allowing excessive price deviation losses (detector sol_defi_as_7) 92%, line 169<br>Incorrect use of logical/comparison operators (==, !=, &&, \|\|, !) causing wrong control flow (detector sol_heuristics_8) 92%, line 199<br>Missing swap deadline parameter enabling delayed transaction sandwich/MEV attacks (detector sol_defi_as_2) 91%, line 169<br>Business logic, input validation, and state machine (category business_logic_state_machine) 89%, line 199<br>Missing minimum output amount check before AMM token swap, enabling sandwich/slippage attacks (detector sol_defi_as_11) 89%, line 169<br>Hard-coded Uniswap V3 fee tier parameter in swap function (detector sol_integrations_uniswap_10) 89%, line 169<br>Unvalidated zero price from oracle feed used without a sanity check (detector sol_defi_oracle_2) 88%, line 190<br>Flash-loan-exploitable use of manipulable spot price/balance/voting power within a single transaction (detector flash_loan_attacks) 87%, line 190<br>Arithmetic and precision (category arithmetic_precision) 86%, line 201<br>External calls and token integration (category external_call_token_integration) 84%, line 201<br>Unhandled min/max boundary values causing incorrect or unsafe arithmetic results (detector sol_basics_math_12) 84%, line 188<br>Denial-of-service via unbounded loop with external calls that can revert entire operation (detector sol_basics_al_10) 82%, line 201<br>Front-running, MEV, and randomness (category frontrunning_mev) 81%, line 169<br>Missing slippage/deadline protection on swaps enabling sandwich/front-running attacks (detector front_running_patterns) 81%, line 169<br>Missing front-running/sandwich-attack protection due to transaction-order-sensitive logic (detector sol_am_ma_3) 81%, line 169<br>Missing staleness check on oracle price feed timestamp allows use of outdated prices (detector sol_defi_oracle_3) 81%, line 190<br>Oracle and price manipulation (category oracle_price_manipulation) 80%, line 190<br>Denial of service and griefing (category dos_griefing) 78%, line 201<br>Missing staleness/heartbeat check on price oracle data, allowing use of stale prices (detector sol_defi_oracle_7) 78%, line 190<br>Accounting and share math (category accounting_share_math) 77%, line 199<br>Unsafe unchecked arithmetic, silent truncation, or phantom overflow in Solidity integer math (detector integer_overflow) 73%, line 188<br>Reentrancy vulnerability from unguarded or misordered external calls before state updates (detector solidity_security) 72%, line 201<br>Reentrancy (category reentrancy) 71%, line 201<br>Unbounded array/loop iteration causing out-of-gas denial of service (detector sol_basics_al_9) 70%, line 201<br>Precision loss from performing division before multiplication in arithmetic expressions (detector sol_basics_math_4) 69%, line 188<br>Access control and privilege (category access_control) 67%, line 163<br>AMM miscalculates swaps/liquidity due to unhandled token decimal or non-standard token behavior (detector sol_defi_as_8) 67%, line 190<br>Function vulnerable to front-running enabling DoS or value extraction by transaction ordering (detector sol_basics_function_3) 60%, line 201<br>Cross-function/read-only reentrancy from external calls before state updates (detector sol_ec_1) 54%, line 201<br>Unchecked unsigned integer subtraction that can underflow and revert unexpectedly (detector sol_basics_math_8) 53%, line 170</details> |
| `initialize` | 38-43 | Missing _disableInitializers() in upgradeable contract constructor allowing implementation takeover | detector constructor_patterns | 86% | 38 | <details><summary>5 more</summary>Uninitialized upgradeable implementation/proxy contract allowing attacker takeover via initializer (detector sol_basics_pu_5) 75%, line 38<br>Uninitialized upgradeable proxy/implementation allowing attacker to seize ownership via initialize() (detector upgrade_safety) 69%, line 38<br>Business logic, input validation, and state machine (category business_logic_state_machine) 64%, line 42<br>Missing access control on sensitive state-changing function (detector sol_basics_function_9) 63%, line 38<br>Uninitialized beacon/proxy implementation contract due to missing _disableInitializers() (detector beacon_proxy) 54%, line 38</details> |
| `setPoolAddress` | 50-52 | Business logic, input validation, and state machine | category business_logic_state_machine | 72% | 51 |  |
| `setFlutterRatios` | 62-64 | Business logic, input validation, and state machine | category business_logic_state_machine | 72% | 63 |  |
| `setBaseAsset` | 66-68 | Business logic, input validation, and state machine | category business_logic_state_machine | 60% | 67 |  |
| `setTreshold` | 58-60 | Business logic, input validation, and state machine | category business_logic_state_machine | 55% | 59 |  |
| `getSupplyProportion` | 83-90 | Flash-loan-exploitable use of manipulable spot price/balance/voting power within a single transaction | detector flash_loan_attacks | 53% | 84 | <details><summary>2 more</summary>Price derived from spot token balance ratio, manipulable via flash loans/donations (detector sol_am_pma_1) 53%, line 84<br>Oracle and price manipulation (category oracle_price_manipulation) 52%, line 84</details> |

<details><summary>File-level hits (47)</summary>

| Chance | Question | What it asks |
|---|---|---|
| 96% | detector sol_integrations_uniswap_10 | Hard-coded Uniswap V3 fee tier parameter in swap function |
| 95% | detector sol_integrations_uniswap_9 | Manipulable Uniswap V3 spot price via slot0 used for sensitive price calculations |
| 92% | detector flash_loan_attacks | Flash-loan-exploitable use of manipulable spot price/balance/voting power within a single transaction |
| 92% | detector sol_defi_oracle_14 | Missing sanity/range check on oracle price allows flash-crash price manipulation |
| 91% | detector constructor_patterns | Missing _disableInitializers() in upgradeable contract constructor allowing implementation takeover |
| 91% | detector sol_defi_as_7 | Missing slippage protection in swap/trade functions allowing excessive price deviation losses |
| 91% | detector sol_defi_oracle_13 | Oracle price manipulation via AMM spot price used as price feed |
| 90% | category arithmetic_precision | Arithmetic and precision |
| 89% | category business_logic_state_machine | Business logic, input validation, and state machine |
| 89% | detector sol_integrations_uniswap_5 | Using manipulable Uniswap pool reserves/spot price for critical pricing or logic |
| 88% | detector front_running_patterns | Missing slippage/deadline protection on swaps enabling sandwich/front-running attacks |
| 87% | detector sol_defi_as_2 | Missing swap deadline parameter enabling delayed transaction sandwich/MEV attacks |
| 86% | detector sol_basics_math_12 | Unhandled min/max boundary values causing incorrect or unsafe arithmetic results |
| 86% | detector sol_heuristics_8 | Incorrect use of logical/comparison operators (==, !=, &&, \|\|, !) causing wrong control flow |
| 85% | detector sol_basics_math_8 | Unchecked unsigned integer subtraction that can underflow and revert unexpectedly |
| 84% | category oracle_price_manipulation | Oracle and price manipulation |
| 84% | detector sol_am_sandwichattack_1 | Missing slippage protection allowing sandwich attacks on user trades/swaps |
| 81% | category external_call_token_integration | External calls and token integration |
| 80% | detector sol_am_pma_1 | Price derived from spot token balance ratio, manipulable via flash loans/donations |
| 80% | detector sol_basics_pu_5 | Uninitialized upgradeable implementation/proxy contract allowing attacker takeover via initializer |
| 80% | detector sol_defi_as_11 | Missing minimum output amount check before AMM token swap, enabling sandwich/slippage attacks |
| 79% | detector oracle_manipulation | Manipulable spot-price oracle (DEX reserves) used for value-critical calculations without TWAP or safeguards |
| 79% | detector upgrade_safety | Uninitialized upgradeable proxy/implementation allowing attacker to seize ownership via initialize() |
| 78% | detector sol_basics_math_4 | Precision loss from performing division before multiplication in arithmetic expressions |
| 76% | detector sol_basics_math_6 | Division-by-zero causing unintended revert due to unchecked denominator |
| 75% | category accounting_share_math | Accounting and share math |
| 75% | detector sol_basics_al_10 | Denial-of-service via unbounded loop with external calls that can revert entire operation |
| 72% | category dos_griefing | Denial of service and griefing |
| 72% | category frontrunning_mev | Front-running, MEV, and randomness |
| 72% | detector sol_am_pma_2 | Price derived from manipulable DEX spot reserves instead of TWAP/oracle |
| 71% | detector sol_am_ma_3 | Missing front-running/sandwich-attack protection due to transaction-order-sensitive logic |
| 71% | detector solidity_security | Reentrancy vulnerability from unguarded or misordered external calls before state updates |
| 70% | detector sol_defi_as_8 | AMM miscalculates swaps/liquidity due to unhandled token decimal or non-standard token behavior |
| 69% | detector integer_overflow | Unsafe unchecked arithmetic, silent truncation, or phantom overflow in Solidity integer math |
| 68% | detector sol_defi_oracle_2 | Unvalidated zero price from oracle feed used without a sanity check |
| 66% | detector beacon_proxy | Uninitialized beacon/proxy implementation contract due to missing _disableInitializers() |
| 66% | detector sol_basics_al_9 | Unbounded array/loop iteration causing out-of-gas denial of service |
| 66% | detector sol_basics_function_9 | Missing access control on sensitive state-changing function |
| 66% | detector sol_defi_as_1 | Hardcoded slippage tolerance in AMM/swap trade execution instead of user-specified minimum |
| 58% | category reentrancy | Reentrancy |
| 58% | detector sol_defi_oracle_3 | Missing staleness check on oracle price feed timestamp allows use of outdated prices |
| 54% | detector sol_defi_oracle_7 | Missing staleness/heartbeat check on price oracle data, allowing use of stale prices |
| 53% | category access_control | Access control and privilege |
| 53% | detector sol_token_fe_3 | Incorrect handling of differing ERC20 token decimals in calculations |
| 52% | detector sol_basics_function_3 | Function vulnerable to front-running enabling DoS or value extraction by transaction ordering |
| 52% | detector sol_integrations_uniswap_1 | On-chain slippage/minimum-output calculation manipulable via price oracle or reserve manipulation |
| 51% | detector sol_ec_1 | Cross-function/read-only reentrancy from external calls before state updates |

</details>


</details>

<details><summary>USSD.sol · Crit 🟥 · Any 🟥 · Logic 89%, MEV 88%, Oracle 83% · 15 functions flagged</summary>

| Function | Lines | Strongest hit | Question | Chance | Line | More |
|---|---|---|---|---|---|---|
| `approveToRouter` | 242-247 | Unsafe ERC20 transfer calls without return-value checks or SafeERC20 wrapper | detector sol_token_fe_1 | 96% | 243 | <details><summary>11 more</summary>Unsafe ERC-20 token integration without SafeERC20 or received-amount accounting (detector erc20_patterns) 94%, line 243<br>Unbounded/maximum token approval allowed without revert, enabling over-allowance abuse (detector sol_defi_general_6) 94%, line 245<br>Unconditional max-value ERC20 approval breaks on tokens that reject type(uint256).max amounts (detector sol_token_fe_14) 94%, line 243<br>ERC20 approve() called directly to non-zero value without resetting allowance to zero first (detector sol_token_fe_13) 92%, line 243<br>Unsafe ERC-20 integration: raw transfer/approve calls and unchecked transfer amounts for non-standard tokens (detector token_integration_safety) 91%, line 243<br>External calls and token integration (category external_call_token_integration) 83%, line 243<br>Access control and privilege (category access_control) 81%, line 242<br>Business logic, input validation, and state machine (category business_logic_state_machine) 74%, line 245<br>Missing access control on sensitive state-changing function (detector sol_basics_function_9) 71%, line 243<br>Missing access control on sensitive privileged functions (detector sol_basics_ac_2) 67%, line 243<br>Missing access control on privileged/critical functions (detector access_control_patterns) 65%, line 242</details> |
| `calculateMint` | 170-173 | Missing sanity/range check on oracle price allows flash-crash price manipulation | detector sol_defi_oracle_14 | 95% | 171 | <details><summary>12 more</summary>Unvalidated zero price from oracle feed used without a sanity check (detector sol_defi_oracle_2) 90%, line 171<br>Missing staleness check on oracle price feed timestamp allows use of outdated prices (detector sol_defi_oracle_3) 90%, line 171<br>Missing staleness/heartbeat check on price oracle data, allowing use of stale prices (detector sol_defi_oracle_7) 89%, line 171<br>Precision loss from performing division before multiplication in arithmetic expressions (detector sol_basics_math_4) 84%, line 172<br>Unsafe unchecked arithmetic, silent truncation, or phantom overflow in Solidity integer math (detector integer_overflow) 82%, line 172<br>Unhandled min/max boundary values causing incorrect or unsafe arithmetic results (detector sol_basics_math_12) 82%, line 172<br>Oracle and price manipulation (category oracle_price_manipulation) 79%, line 171<br>Arithmetic and precision (category arithmetic_precision) 79%, line 172<br>Division-by-zero causing unintended revert due to unchecked denominator (detector sol_basics_math_6) 56%, line 172<br>Accounting logic keyed on a single token address for tokens with multiple valid addresses (detector sol_token_fe_5) 51%, line 171<br>Missing staleness check on Proof of Reserves oracle data in liquid staking protocol (detector sol_defi_lsd_8) 50%, line 171<br>Rounding/fee inconsistency exploitable by splitting a financial operation into many small calls (detector sol_heuristics_17) 50%, line 172</details> |
| `collateralFactor` | 179-194 | Division-by-zero causing unintended revert due to unchecked denominator | detector sol_basics_math_6 | 94% | 193 | <details><summary>15 more</summary>Missing sanity/range check on oracle price allows flash-crash price manipulation (detector sol_defi_oracle_14) 94%, line 189<br>Accounting relies on token/ETH balanceOf instead of internal ledger, enabling donation-based manipulation (detector sol_defi_general_3) 90%, line 183<br>Unvalidated zero price from oracle feed used without a sanity check (detector sol_defi_oracle_2) 87%, line 189<br>Missing staleness/heartbeat check on price oracle data, allowing use of stale prices (detector sol_defi_oracle_7) 87%, line 189<br>Missing staleness check on oracle price feed timestamp allows use of outdated prices (detector sol_defi_oracle_3) 86%, line 189<br>Unhandled min/max boundary values causing incorrect or unsafe arithmetic results (detector sol_basics_math_12) 85%, line 193<br>Oracle and price manipulation (category oracle_price_manipulation) 78%, line 189<br>Unsafe unchecked arithmetic, silent truncation, or phantom overflow in Solidity integer math (detector integer_overflow) 76%, line 193<br>Arithmetic and precision (category arithmetic_precision) 74%, line 193<br>Donation/balance-manipulation attack via reliance on token.balanceOf instead of internal accounting (detector sol_am_da_1) 73%, line 183<br>Flash-loan-exploitable use of manipulable spot price/balance/voting power within a single transaction (detector flash_loan_attacks) 66%, line 183<br>Precision loss from performing division before multiplication in arithmetic expressions (detector sol_basics_math_4) 61%, line 185<br>External calls and token integration (category external_call_token_integration) 60%, line 183<br>Flash-loan and economic attacks (category flash_loan_economic) 57%, line 193<br>Accounting and share math (category accounting_share_math) 52%, line 193</details> |
| `mintRebalancer` | 204-206 | Missing access control on sensitive privileged functions | detector sol_basics_ac_2 | 93% | 205 | <details><summary>6 more</summary>Missing access control on sensitive state-changing function (detector sol_basics_function_9) 93%, line 204<br>Missing access control on privileged/critical functions (detector access_control_patterns) 88%, line 204<br>Access control and privilege (category access_control) 86%, line 204<br>Business logic, input validation, and state machine (category business_logic_state_machine) 78%, line 205<br>Missing minimum transaction/amount check enabling dust-transaction denial-of-service or griefing (detector sol_am_dosa_2) 65%, line 205<br>Missing replay/duplicate-call protection allowing repeated invocation with identical parameters (detector sol_heuristics_12) 62%, line 205</details> |
| `mintForToken` | 151-167 | Fee-on-transfer token accounting mismatch from assuming transferred amount equals received amount | detector sol_token_fe_6 | 91% | 163 | <details><summary>17 more</summary>Missing minimum transaction/amount check enabling dust-transaction denial-of-service or griefing (detector sol_am_dosa_2) 83%, line 153<br>AMM swap accounting assumes transferred token amount equals requested amount, breaking on fee-on-transfer tokens (detector sol_defi_as_9) 78%, line 163<br>Missing minimum deposit/withdrawal threshold enabling dust-amount rounding or DoS exploits (detector sol_basics_payment_4) 75%, line 163<br>Reentrancy (category reentrancy) 73%, line 158<br>Missing replay/duplicate-call protection allowing repeated invocation with identical parameters (detector sol_heuristics_12) 73%, line 164<br>Reentrancy via ERC777 transfer hooks in token integrations lacking reentrancy protection (detector sol_token_fe_7) 72%, line 158<br>Missing access control on privileged/critical functions (detector access_control_patterns) 70%, line 155<br>Function vulnerable to front-running enabling DoS or value extraction by transaction ordering (detector sol_basics_function_3) 65%, line 163<br>Missing validation that user-supplied actor addresses aren't the protocol's own contracts (detector sol_heuristics_9) 65%, line 164<br>Business logic, input validation, and state machine (category business_logic_state_machine) 63%, line 153<br>Access control and privilege (category access_control) 59%, line 156<br>External calls and token integration (category external_call_token_integration) 59%, line 158<br>Reentrancy vulnerability from unguarded or misordered external calls before state updates (detector solidity_security) 59%, line 158<br>Front-running, MEV, and randomness (category frontrunning_mev) 58%, line 163<br>Missing access control on sensitive privileged functions (detector sol_basics_ac_2) 56%, line 164<br>Oracle and price manipulation (category oracle_price_manipulation) 51%, line 163<br>Paired state-changing functions (add/remove, deposit/withdraw) are asymmetric, leaving stale or incorrect state. (detector sol_heuristics_16) 51%, line 164</details> |
| `UniV3SwapInput` | 227-240 | Missing minimum output amount check before AMM token swap, enabling sandwich/slippage attacks | detector sol_defi_as_11 | 90% | 237 | <details><summary>11 more</summary>Missing slippage protection in swap/trade functions allowing excessive price deviation losses (detector sol_defi_as_7) 88%, line 237<br>Missing slippage/deadline protection on swaps enabling sandwich/front-running attacks (detector front_running_patterns) 87%, line 237<br>Missing swap deadline parameter enabling delayed transaction sandwich/MEV attacks (detector sol_defi_as_2) 86%, line 239<br>Missing slippage protection allowing sandwich attacks on user trades/swaps (detector sol_am_sandwichattack_1) 83%, line 237<br>Front-running, MEV, and randomness (category frontrunning_mev) 81%, line 237<br>Business logic, input validation, and state machine (category business_logic_state_machine) 80%, line 237<br>External calls and token integration (category external_call_token_integration) 69%, line 239<br>Flash-loan-exploitable use of manipulable spot price/balance/voting power within a single transaction (detector flash_loan_attacks) 68%, line 237<br>Missing front-running/sandwich-attack protection due to transaction-order-sensitive logic (detector sol_am_ma_3) 60%, line 237<br>Reentrancy (category reentrancy) 56%, line 239<br>Denial of service and griefing (category dos_griefing) 55%, line 239</details> |
| `initialize` | 31-43 | Missing _disableInitializers() in upgradeable contract constructor allowing implementation takeover | detector constructor_patterns | 88% | 34 | <details><summary>7 more</summary>Uninitialized upgradeable implementation/proxy contract allowing attacker takeover via initializer (detector sol_basics_pu_5) 75%, line 34<br>Uninitialized upgradeable proxy/implementation allowing attacker to seize ownership via initialize() (detector upgrade_safety) 75%, line 39<br>Uninitialized beacon/proxy implementation contract due to missing _disableInitializers() (detector beacon_proxy) 69%, line 34<br>Business logic, input validation, and state machine (category business_logic_state_machine) 61%, line 42<br>Missing access control on sensitive privileged functions (detector sol_basics_ac_2) 55%, line 42<br>Access control and privilege (category access_control) 53%, line 42<br>Missing access control on privileged/critical functions (detector access_control_patterns) 50%, line 42</details> |
| `removeCollateral` | 120-123 | Business logic, input validation, and state machine | category business_logic_state_machine | 88% | 121 | <details><summary>2 more</summary>Stale array index used after array elements are removed/reordered, causing wrong-element access (detector sol_basics_al_5) 63%, line 121<br>Accounting and share math (category accounting_share_math) 52%, line 121</details> |
| `burnRebalancer` | 208-210 | Missing access control on sensitive state-changing function | detector sol_basics_function_9 | 87% | 208 | <details><summary>5 more</summary>Access control and privilege (category access_control) 71%, line 208<br>Business logic, input validation, and state machine (category business_logic_state_machine) 62%, line 209<br>Missing access control on sensitive privileged functions (detector sol_basics_ac_2) 62%, line 209<br>Missing access control on privileged/critical functions (detector access_control_patterns) 59%, line 208<br>Missing minimum transaction/amount check enabling dust-transaction denial-of-service or griefing (detector sol_am_dosa_2) 51%, line 209</details> |
| `swapCollateralIndexes` | 110-118 | Business logic, input validation, and state machine | category business_logic_state_machine | 80% | 116 |  |
| `addCollateral` | 84-108 | Business logic, input validation, and state machine | category business_logic_state_machine | 76% | 104 | <details><summary>2 more</summary>Paired state-changing functions (add/remove, deposit/withdraw) are asymmetric, leaving stale or incorrect state. (detector sol_heuristics_16) 65%, line 106<br>Solidity dirty-bytes-array-to-storage compiler bug from direct bytes copy to storage (detector sol_basics_vi_svi_8) 55%, line 99</details> |
| `setRebalancer` | 200-202 | Business logic, input validation, and state machine | category business_logic_state_machine | 59% | 201 |  |
| `setUniswapRouter` | 223-225 | Business logic, input validation, and state machine | category business_logic_state_machine | 58% | 224 |  |
| `hasCollateralMint` | 135-144 | Accounting logic keyed on a single token address for tokens with multiple valid addresses | detector sol_token_fe_5 | 56% | 139 |  |
| `getCollateralIndex` | 125-133 | Accounting logic keyed on a single token address for tokens with multiple valid addresses | detector sol_token_fe_5 | 54% | 129 |  |

<details><summary>File-level hits (64)</summary>

| Chance | Question | What it asks |
|---|---|---|
| 96% | detector sol_defi_oracle_14 | Missing sanity/range check on oracle price allows flash-crash price manipulation |
| 94% | detector sol_token_fe_13 | ERC20 approve() called directly to non-zero value without resetting allowance to zero first |
| 93% | detector erc20_patterns | Unsafe ERC-20 token integration without SafeERC20 or received-amount accounting |
| 93% | detector front_running_patterns | Missing slippage/deadline protection on swaps enabling sandwich/front-running attacks |
| 93% | detector sol_defi_general_6 | Unbounded/maximum token approval allowed without revert, enabling over-allowance abuse |
| 93% | detector sol_defi_oracle_2 | Unvalidated zero price from oracle feed used without a sanity check |
| 93% | detector sol_token_fe_1 | Unsafe ERC20 transfer calls without return-value checks or SafeERC20 wrapper |
| 91% | detector constructor_patterns | Missing _disableInitializers() in upgradeable contract constructor allowing implementation takeover |
| 91% | detector sol_token_fe_6 | Fee-on-transfer token accounting mismatch from assuming transferred amount equals received amount |
| 90% | detector sol_defi_as_2 | Missing swap deadline parameter enabling delayed transaction sandwich/MEV attacks |
| 90% | detector sol_defi_as_7 | Missing slippage protection in swap/trade functions allowing excessive price deviation losses |
| 90% | detector sol_defi_general_3 | Accounting relies on token/ETH balanceOf instead of internal ledger, enabling donation-based manipulation |
| 89% | category business_logic_state_machine | Business logic, input validation, and state machine |
| 89% | detector sol_token_fe_14 | Unconditional max-value ERC20 approval breaks on tokens that reject type(uint256).max amounts |
| 88% | category frontrunning_mev | Front-running, MEV, and randomness |
| 88% | detector flash_loan_attacks | Flash-loan-exploitable use of manipulable spot price/balance/voting power within a single transaction |
| 87% | detector sol_basics_math_6 | Division-by-zero causing unintended revert due to unchecked denominator |
| 86% | detector sol_basics_math_12 | Unhandled min/max boundary values causing incorrect or unsafe arithmetic results |
| 85% | detector sol_am_sandwichattack_1 | Missing slippage protection allowing sandwich attacks on user trades/swaps |
| 85% | detector sol_defi_oracle_7 | Missing staleness/heartbeat check on price oracle data, allowing use of stale prices |
| 83% | category oracle_price_manipulation | Oracle and price manipulation |
| 82% | category arithmetic_precision | Arithmetic and precision |
| 82% | detector sol_defi_oracle_3 | Missing staleness check on oracle price feed timestamp allows use of outdated prices |
| 81% | category external_call_token_integration | External calls and token integration |
| 80% | detector sol_defi_as_11 | Missing minimum output amount check before AMM token swap, enabling sandwich/slippage attacks |
| 78% | detector upgrade_safety | Uninitialized upgradeable proxy/implementation allowing attacker to seize ownership via initialize() |
| 76% | detector sol_am_dosa_2 | Missing minimum transaction/amount check enabling dust-transaction denial-of-service or griefing |
| 75% | detector integer_overflow | Unsafe unchecked arithmetic, silent truncation, or phantom overflow in Solidity integer math |
| 75% | detector sol_token_fe_7 | Reentrancy via ERC777 transfer hooks in token integrations lacking reentrancy protection |
| 75% | detector token_integration_safety | Unsafe ERC-20 integration: raw transfer/approve calls and unchecked transfer amounts for non-standard tokens |
| 74% | detector sol_basics_function_9 | Missing access control on sensitive state-changing function |
| 74% | detector sol_basics_math_4 | Precision loss from performing division before multiplication in arithmetic expressions |
| 73% | category access_control | Access control and privilege |
| 73% | detector sol_basics_pu_5 | Uninitialized upgradeable implementation/proxy contract allowing attacker takeover via initializer |
| 71% | detector sol_basics_al_5 | Stale array index used after array elements are removed/reordered, causing wrong-element access |
| 69% | detector access_control_patterns | Missing access control on privileged/critical functions |
| 69% | detector sol_basics_function_3 | Function vulnerable to front-running enabling DoS or value extraction by transaction ordering |
| 69% | detector sol_heuristics_9 | Missing validation that user-supplied actor addresses aren't the protocol's own contracts |
| 68% | category dos_griefing | Denial of service and griefing |
| 68% | detector sol_am_da_1 | Donation/balance-manipulation attack via reliance on token.balanceOf instead of internal accounting |
| 68% | detector sol_defi_general_9 | Unsafe support for arbitrary/non-standard ERC20 tokens (fee-on-transfer, rebasing) without whitelisting |
| 66% | detector beacon_proxy | Uninitialized beacon/proxy implementation contract due to missing _disableInitializers() |
| 66% | detector sol_basics_vi_svi_8 | Solidity dirty-bytes-array-to-storage compiler bug from direct bytes copy to storage |
| 66% | detector sol_token_fe_5 | Accounting logic keyed on a single token address for tokens with multiple valid addresses |
| 65% | detector sol_am_ma_3 | Missing front-running/sandwich-attack protection due to transaction-order-sensitive logic |
| 64% | category accounting_share_math | Accounting and share math |
| 64% | detector sol_basics_ac_2 | Missing access control on sensitive privileged functions |
| 63% | detector sol_defi_as_9 | AMM swap accounting assumes transferred token amount equals requested amount, breaking on fee-on-transfer tokens |
| 63% | detector solidity_security | Reentrancy vulnerability from unguarded or misordered external calls before state updates |
| 61% | detector sol_am_fra_2 | Two-step actions vulnerable to front-running/interception between the two transactions |
| 60% | detector sol_ec_12 | Missing contract-existence check before low-level call/delegatecall, allowing silent success on non-existent targets |
| 57% | detector sol_basics_payment_4 | Missing minimum deposit/withdrawal threshold enabling dust-amount rounding or DoS exploits |
| 56% | detector sol_am_reentrancyattack_1 | Read-only reentrancy via unguarded view functions returning stale state |
| 54% | detector sol_heuristics_16 | Paired state-changing functions (add/remove, deposit/withdraw) are asymmetric, leaving stale or incorrect state. |
| 53% | category reentrancy | Reentrancy |
| 53% | detector sol_heuristics_12 | Missing replay/duplicate-call protection allowing repeated invocation with identical parameters |
| 52% | detector sol_defi_as_8 | AMM miscalculates swaps/liquidity due to unhandled token decimal or non-standard token behavior |
| 52% | detector sol_defi_lsd_8 | Missing staleness check on Proof of Reserves oracle data in liquid staking protocol |
| 52% | detector sol_ec_1 | Cross-function/read-only reentrancy from external calls before state updates |
| 51% | category proxy_upgradeability | Proxy, upgradeability, and storage layout |
| 51% | category flash_loan_economic | Flash-loan and economic attacks |
| 51% | detector sol_am_reentrancyattack_2 | Reentrancy via state changes occurring after external call/interaction |
| 50% | detector sol_basics_inheritance_1 | Unrestricted exposure of inherited parent contract's public/external functions |
| 50% | detector sol_heuristics_17 | Rounding/fee inconsistency exploitable by splitting a financial operation into many small calls |

</details>


</details>

<details><summary>oracles/StableOracleWBTC.sol · Crit 🟧 · Any 🟥 · Oracle 89%, Math 69% · 2 functions flagged</summary>

| Function | Lines | Strongest hit | Question | Chance | Line | More |
|---|---|---|---|---|---|---|
| `getPriceUSD` | 21-26 | Unsafe Chainlink price feed consumption without staleness/validity/sequencer checks | detector chainlink_oracles | 97% | 23 | <details><summary>11 more</summary>Missing staleness check on oracle price feed timestamp allows use of outdated prices (detector sol_defi_oracle_3) 97%, line 23<br>Missing staleness/heartbeat check on price oracle data, allowing use of stale prices (detector sol_defi_oracle_7) 97%, line 23<br>Missing sanity/range check on oracle price allows flash-crash price manipulation (detector sol_defi_oracle_14) 93%, line 25<br>Oracle and price manipulation (category oracle_price_manipulation) 91%, line 23<br>Unvalidated zero price from oracle feed used without a sanity check (detector sol_defi_oracle_2) 90%, line 25<br>Use of deprecated Chainlink price feed functions returning stale or incorrect oracle data (detector sol_defi_oracle_1) 88%, line 23<br>Missing L2 sequencer uptime check when consuming Chainlink price feeds (detector sol_defi_oracle_4) 83%, line 23<br>Arithmetic and precision (category arithmetic_precision) 78%, line 25<br>Unhandled min/max boundary values causing incorrect or unsafe arithmetic results (detector sol_basics_math_12) 61%, line 25<br>Incorrect handling of differing ERC20 token decimals in calculations (detector sol_token_fe_3) 60%, line 25<br>Using a mismatched price feed (e.g., ETH feed for stETH) that ignores depeg risk (detector sol_defi_oracle_12) 56%, line 25</details> |
| `constructor` | 15-19 | Hard-coded, non-updatable price feed/oracle address preventing replacement of deprecated or inaccurate feeds | detector sol_defi_oracle_9 | 70% | 17 | <details><summary>1 more</summary>Oracle and price manipulation (category oracle_price_manipulation) 51%, line 16</details> |

<details><summary>File-level hits (13)</summary>

| Chance | Question | What it asks |
|---|---|---|
| 97% | detector chainlink_oracles | Unsafe Chainlink price feed consumption without staleness/validity/sequencer checks |
| 97% | detector sol_defi_oracle_3 | Missing staleness check on oracle price feed timestamp allows use of outdated prices |
| 97% | detector sol_defi_oracle_7 | Missing staleness/heartbeat check on price oracle data, allowing use of stale prices |
| 90% | detector sol_defi_oracle_14 | Missing sanity/range check on oracle price allows flash-crash price manipulation |
| 90% | detector sol_defi_oracle_2 | Unvalidated zero price from oracle feed used without a sanity check |
| 89% | category oracle_price_manipulation | Oracle and price manipulation |
| 85% | detector sol_defi_oracle_1 | Use of deprecated Chainlink price feed functions returning stale or incorrect oracle data |
| 78% | detector sol_defi_oracle_4 | Missing L2 sequencer uptime check when consuming Chainlink price feeds |
| 74% | detector sol_defi_oracle_9 | Hard-coded, non-updatable price feed/oracle address preventing replacement of deprecated or inaccurate feeds |
| 69% | category arithmetic_precision | Arithmetic and precision |
| 56% | detector sol_defi_oracle_12 | Using a mismatched price feed (e.g., ETH feed for stETH) that ignores depeg risk |
| 55% | detector sol_token_fe_3 | Incorrect handling of differing ERC20 token decimals in calculations |
| 51% | detector sol_basics_math_12 | Unhandled min/max boundary values causing incorrect or unsafe arithmetic results |

</details>


</details>

<details><summary>oracles/StableOracleWETH.sol · Crit 🟧 · Any 🟧 · Oracle 86%, Math 55% · 2 functions flagged</summary>

| Function | Lines | Strongest hit | Question | Chance | Line | More |
|---|---|---|---|---|---|---|
| `getPriceUSD` | 21-26 | Unsafe Chainlink price feed consumption without staleness/validity/sequencer checks | detector chainlink_oracles | 97% | 23 | <details><summary>8 more</summary>Missing staleness check on oracle price feed timestamp allows use of outdated prices (detector sol_defi_oracle_3) 97%, line 23<br>Missing staleness/heartbeat check on price oracle data, allowing use of stale prices (detector sol_defi_oracle_7) 97%, line 23<br>Missing sanity/range check on oracle price allows flash-crash price manipulation (detector sol_defi_oracle_14) 93%, line 25<br>Oracle and price manipulation (category oracle_price_manipulation) 91%, line 23<br>Unvalidated zero price from oracle feed used without a sanity check (detector sol_defi_oracle_2) 91%, line 25<br>Use of deprecated Chainlink price feed functions returning stale or incorrect oracle data (detector sol_defi_oracle_1) 87%, line 23<br>Missing L2 sequencer uptime check when consuming Chainlink price feeds (detector sol_defi_oracle_4) 83%, line 23<br>Arithmetic and precision (category arithmetic_precision) 75%, line 25</details> |
| `constructor` | 15-19 | Hard-coded, non-updatable price feed/oracle address preventing replacement of deprecated or inaccurate feeds | detector sol_defi_oracle_9 | 72% | 17 | <details><summary>1 more</summary>Oracle and price manipulation (category oracle_price_manipulation) 52%, line 16</details> |

<details><summary>File-level hits (10)</summary>

| Chance | Question | What it asks |
|---|---|---|
| 98% | detector chainlink_oracles | Unsafe Chainlink price feed consumption without staleness/validity/sequencer checks |
| 98% | detector sol_defi_oracle_7 | Missing staleness/heartbeat check on price oracle data, allowing use of stale prices |
| 97% | detector sol_defi_oracle_3 | Missing staleness check on oracle price feed timestamp allows use of outdated prices |
| 90% | detector sol_defi_oracle_2 | Unvalidated zero price from oracle feed used without a sanity check |
| 86% | category oracle_price_manipulation | Oracle and price manipulation |
| 85% | detector sol_defi_oracle_14 | Missing sanity/range check on oracle price allows flash-crash price manipulation |
| 84% | detector sol_defi_oracle_1 | Use of deprecated Chainlink price feed functions returning stale or incorrect oracle data |
| 78% | detector sol_defi_oracle_9 | Hard-coded, non-updatable price feed/oracle address preventing replacement of deprecated or inaccurate feeds |
| 76% | detector sol_defi_oracle_4 | Missing L2 sequencer uptime check when consuming Chainlink price feeds |
| 55% | category arithmetic_precision | Arithmetic and precision |

</details>


</details>

<details><summary>oracles/StableOracleWBGL.sol · Crit 🟨 · Any 🟧 · Oracle 79%, Math 61% · 2 functions flagged</summary>

| Function | Lines | Strongest hit | Question | Chance | Line | More |
|---|---|---|---|---|---|---|
| `getPriceUSD` | 24-39 | Missing sanity/range check on oracle price allows flash-crash price manipulation | detector sol_defi_oracle_14 | 93% | 38 | <details><summary>13 more</summary>Division-by-zero causing unintended revert due to unchecked denominator (detector sol_basics_math_6) 90%, line 38<br>Missing staleness/heartbeat check on price oracle data, allowing use of stale prices (detector sol_defi_oracle_7) 86%, line 36<br>Unvalidated zero price from oracle feed used without a sanity check (detector sol_defi_oracle_2) 83%, line 38<br>Incorrect handling of differing ERC20 token decimals in calculations (detector sol_token_fe_3) 82%, line 38<br>Oracle and price manipulation (category oracle_price_manipulation) 79%, line 36<br>Unsafe unchecked arithmetic, silent truncation, or phantom overflow in Solidity integer math (detector integer_overflow) 76%, line 38<br>Unhandled min/max boundary values causing incorrect or unsafe arithmetic results (detector sol_basics_math_12) 72%, line 38<br>Arithmetic and precision (category arithmetic_precision) 67%, line 38<br>Incorrect handling of ERC20 tokens with non-18 decimals causing miscalculation (detector sol_defi_general_1) 63%, line 38<br>Missing staleness check on oracle price feed timestamp allows use of outdated prices (detector sol_defi_oracle_3) 63%, line 36<br>Hard-coded, non-updatable price feed/oracle address preventing replacement of deprecated or inaccurate feeds (detector sol_defi_oracle_9) 60%, line 26<br>Mismatched decimal precision across multiple price feeds causing incorrect price calculations (detector sol_defi_oracle_8) 59%, line 38<br>Hardcoded assumption of Uniswap token0/token1 order instead of verifying dynamically per pool (detector sol_integrations_uniswap_3) 57%, line 30</details> |
| `constructor` | 17-22 | Hard-coded, non-updatable price feed/oracle address preventing replacement of deprecated or inaccurate feeds | detector sol_defi_oracle_9 | 76% | 19 |  |

<details><summary>File-level hits (14)</summary>

| Chance | Question | What it asks |
|---|---|---|
| 92% | detector sol_defi_oracle_14 | Missing sanity/range check on oracle price allows flash-crash price manipulation |
| 91% | detector sol_basics_math_6 | Division-by-zero causing unintended revert due to unchecked denominator |
| 83% | detector sol_defi_oracle_2 | Unvalidated zero price from oracle feed used without a sanity check |
| 81% | detector sol_defi_oracle_9 | Hard-coded, non-updatable price feed/oracle address preventing replacement of deprecated or inaccurate feeds |
| 80% | detector sol_defi_oracle_7 | Missing staleness/heartbeat check on price oracle data, allowing use of stale prices |
| 80% | detector sol_token_fe_3 | Incorrect handling of differing ERC20 token decimals in calculations |
| 79% | category oracle_price_manipulation | Oracle and price manipulation |
| 71% | detector sol_basics_math_12 | Unhandled min/max boundary values causing incorrect or unsafe arithmetic results |
| 68% | detector integer_overflow | Unsafe unchecked arithmetic, silent truncation, or phantom overflow in Solidity integer math |
| 61% | category arithmetic_precision | Arithmetic and precision |
| 60% | detector sol_defi_general_1 | Incorrect handling of ERC20 tokens with non-18 decimals causing miscalculation |
| 55% | detector sol_integrations_uniswap_3 | Hardcoded assumption of Uniswap token0/token1 order instead of verifying dynamically per pool |
| 50% | detector sol_defi_oracle_3 | Missing staleness check on oracle price feed timestamp allows use of outdated prices |
| 50% | detector sol_defi_oracle_8 | Mismatched decimal precision across multiple price feeds causing incorrect price calculations |

</details>


</details>

<details><summary>oracles/UniswapV3StaticOracle.sol · Crit 🟨 · Any 🟨 · no category hit · 12 functions flagged</summary>

| Function | Lines | Strongest hit | Question | Chance | Line | More |
|---|---|---|---|---|---|---|
| `addNewFeeTier` | 141-147 | Missing access control on sensitive state-changing function | detector sol_basics_function_9 | 92% | 141 | <details><summary>1 more</summary>Paired state-changing functions (add/remove, deposit/withdraw) are asymmetric, leaving stale or incorrect state. (detector sol_heuristics_16) 89%, line 146</details> |
| `_quote` | 160-176 | TWAP oracle period set too short, enabling price manipulation via short-window time-weighted average price | detector sol_defi_oracle_5 | 89% | 165 | <details><summary>4 more</summary>Missing whitelist/factory verification allows interaction with untrusted or malicious Uniswap pools (detector sol_integrations_uniswap_4) 88%, line 171<br>Missing sanity/range check on oracle price allows flash-crash price manipulation (detector sol_defi_oracle_14) 86%, line 175<br>Denial-of-service via unbounded loop with external calls that can revert entire operation (detector sol_basics_al_10) 66%, line 171<br>Unvalidated zero price from oracle feed used without a sanity check (detector sol_defi_oracle_2) 59%, line 175</details> |
| `_prepare` | 154-158 | Missing whitelist/factory verification allows interaction with untrusted or malicious Uniswap pools | detector sol_integrations_uniswap_4 | 78% | 156 | <details><summary>3 more</summary>Denial-of-service via unbounded loop with external calls that can revert entire operation (detector sol_basics_al_10) 76%, line 156<br>Missing uniqueness validation on user-supplied array allows duplicate entries to be processed (detector sol_basics_al_7) 64%, line 156<br>Paired state-changing functions (add/remove, deposit/withdraw) are asymmetric, leaving stale or incorrect state. (detector sol_heuristics_16) 50%, line 156</details> |
| `_getCardinalityForTimePeriod` | 149-152 | Unsafe unchecked arithmetic, silent truncation, or phantom overflow in Solidity integer math | detector integer_overflow | 77% | 151 | <details><summary>1 more</summary>TWAP oracle period set too short, enabling price manipulation via short-window time-weighted average price (detector sol_defi_oracle_5) 55%, line 151</details> |
| `quoteSpecificFeeTiersWithTimePeriod` | 66-76 | TWAP oracle period set too short, enabling price manipulation via short-window time-weighted average price | detector sol_defi_oracle_5 | 71% | 75 | <details><summary>1 more</summary>Missing sanity/range check on oracle price allows flash-crash price manipulation (detector sol_defi_oracle_14) 64%, line 75</details> |
| `prepareSpecificPoolsWithCardinality` | 136-138 | Missing access control on sensitive state-changing function | detector sol_basics_function_9 | 70% | 137 |  |
| `_getQueryablePoolsForTiers` | 183-201 | TWAP oracle period set too short, enabling price manipulation via short-window time-weighted average price | detector sol_defi_oracle_5 | 67% | 190 |  |
| `quoteSpecificPoolsWithTimePeriod` | 79-87 | TWAP oracle period set too short, enabling price manipulation via short-window time-weighted average price | detector sol_defi_oracle_5 | 66% | 86 | <details><summary>2 more</summary>Missing whitelist/factory verification allows interaction with untrusted or malicious Uniswap pools (detector sol_integrations_uniswap_4) 66%, line 86<br>Missing sanity/range check on oracle price allows flash-crash price manipulation (detector sol_defi_oracle_14) 59%, line 86</details> |
| `quoteAllAvailablePoolsWithTimePeriod` | 55-63 | TWAP oracle period set too short, enabling price manipulation via short-window time-weighted average price | detector sol_defi_oracle_5 | 65% | 59 | <details><summary>1 more</summary>Missing sanity/range check on oracle price allows flash-crash price manipulation (detector sol_defi_oracle_14) 58%, line 62</details> |
| `prepareSpecificPoolsWithTimePeriod` | 109-111 | TWAP oracle period set too short, enabling price manipulation via short-window time-weighted average price | detector sol_defi_oracle_5 | 52% | 110 |  |
| `prepareAllAvailablePoolsWithTimePeriod` | 90-96 | TWAP oracle period set too short, enabling price manipulation via short-window time-weighted average price | detector sol_defi_oracle_5 | 51% | 95 |  |
| `prepareSpecificFeeTiersWithTimePeriod` | 99-106 | TWAP oracle period set too short, enabling price manipulation via short-window time-weighted average price | detector sol_defi_oracle_5 | 50% | 103 |  |

<details><summary>File-level hits (9)</summary>

| Chance | Question | What it asks |
|---|---|---|
| 86% | detector sol_defi_oracle_5 | TWAP oracle period set too short, enabling price manipulation via short-window time-weighted average price |
| 71% | detector sol_basics_function_9 | Missing access control on sensitive state-changing function |
| 68% | detector sol_defi_oracle_14 | Missing sanity/range check on oracle price allows flash-crash price manipulation |
| 68% | detector sol_heuristics_16 | Paired state-changing functions (add/remove, deposit/withdraw) are asymmetric, leaving stale or incorrect state. |
| 59% | detector sol_basics_al_10 | Denial-of-service via unbounded loop with external calls that can revert entire operation |
| 56% | detector integer_overflow | Unsafe unchecked arithmetic, silent truncation, or phantom overflow in Solidity integer math |
| 53% | detector sol_integrations_uniswap_4 | Missing whitelist/factory verification allows interaction with untrusted or malicious Uniswap pools |
| 52% | detector sol_basics_al_7 | Missing uniqueness validation on user-supplied array allows duplicate entries to be processed |
| 51% | detector sol_defi_oracle_2 | Unvalidated zero price from oracle feed used without a sanity check |

</details>


</details>

1 file with nothing at 50% or more:

<details><summary>Low-risk files</summary>

- `Migrations.sol`

</details>

## Ignored files

<details><summary>Files not scanned (4)</summary>

- `interfaces/IStableOracle.sol`: interface
- `interfaces/IStaticOracle.sol`: interface
- `interfaces/IUSSDRebalancer.sol`: interface
- `oracles/SimOracle.sol`: mock

</details>

---

Jev model jev-1.13.0 · hit threshold 50% · generated 2026-09-18
