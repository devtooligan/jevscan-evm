# 🔥 jevscan heat map: Monolith

**78% chance of a critical bug · 77% chance of at least one exploitable bug · hottest file: `src/Lender.sol`**

Numbers are Jev's probability that the statement is true.

| Codebase | |
|---|---|
| Name | Monolith |
| Solidity files found | 6 |
| Lines of code | 1,353 (non-blank, scanned files) |
| Scanned | 6 (explicit scope) |

155 requests · $0.07 · 0.3 s · 154 answers from cache (billed <$0.01)

Settings changed from `jevscan.toml`: `files.paths = ["src/Coin.sol", "src/Factory.sol", "src/InterestModel.sol", "src/Lender.sol", "src/Lens.sol", "src/Vault.sol"]`

## Heat grid

| File | Crit | Any | Access | Proxy | Oracle | Econ | Reentry | Shares | Math | Sigs | Xchain | Tokens | Logic | DoS | MEV | LowLvl |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `src/Lender.sol` | 🟧 | 🟧 | 🟨 | ⬜ | 🟩 | 🟨 | 🟨 | 🟧 | 🟧 | ⬜ | ⬜ | 🟧 | 🟥 | 🟧 | 🟨 | ⬜ |
| `src/Vault.sol` | 🟧 | 🟧 | 🟩 | ⬜ | ⬜ | 🟩 | 🟩 | 🟧 | 🟨 | ⬜ | ⬜ | 🟨 | 🟧 | 🟨 | 🟨 | ⬜ |
| `src/Factory.sol` | 🟨 | 🟧 | 🟩 | ⬜ | ⬜ | 🟩 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | 🟨 | 🟧 | 🟨 | 🟩 | ⬜ |
| `src/Lens.sol` | 🟨 | 🟨 | ⬜ | ⬜ | ⬜ | 🟩 | ⬜ | 🟨 | 🟧 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| `src/InterestModel.sol` | 🟩 | 🟩 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | 🟨 | ⬜ | ⬜ | ⬜ | 🟩 | ⬜ | ⬜ | ⬜ |
| `src/Coin.sol` | 🟩 | 🟩 | 🟩 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | 🟨 | 🟩 | ⬜ | ⬜ |

- 🟥 85% or more: very likely
- 🟧 70% to 85%: likely
- 🟨 50% to 70%: leaning yes
- 🟩 30% to 50%: possible
- ⬜ under 30%: not flagged

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

## Strongest function hits (70%+): 33

Every function whose strongest hit is 70% or more, by that hit. Its other hits, and every function hit from 50% to 70%, are under its file below.

| File | Function | Lines | What it found | Chance | Line | Corresponding findings |
|---|---|---|---|---|---|---|
| `src/Lender.sol` | `constructor` | 124-175 | ERC20 approve() called directly to non-zero value without resetting allowance to zero first | 90% | 169 |  |
| `src/Lender.sol` | `reapprovePsmVault` | 543-546 | ERC20 approve() called directly to non-zero value without resetting allowance to zero first | 90% | 545 |  |
| `src/Lens.sol` | `_getSyncedTotalDebt` | 90-117 | Silent failure from try/catch blocks that swallow external call errors instead of reverting | 90% | 115 |  |
| `src/Lender.sol` | `decreaseDebt` | 639-666 | Division-by-zero causing unintended revert due to unchecked denominator | 89% | 647 |  |
| `src/Vault.sol` | `deposit` | 47-68 | Fee-on-transfer token accounting mismatch from assuming transferred amount equals received amount | 89% | 56 |  |
| `src/Lender.sol` | `liquidate` | 368-413 | Self-liquidation profit exploit in lending protocol liquidation logic | 88% | 397 | M-2 |
| `src/Lender.sol` | `buy` | 519-541 | AMM swap accounting assumes transferred token amount equals requested amount, breaking on fee-on-transfer tokens | 88% | 536 |  |
| `src/Lender.sol` | `getSellAmountOut` | 771-785 | Hardcoded 1:1 peg assumption between assets without validating real-time exchange rate or depeg | 88% | 783 |  |
| `src/Lender.sol` | `writeOff` | 420-456 | Access control and privilege | 87% | 420 | M-1 |
| `src/Lender.sol` | `redeem` | 463-495 | Business logic, input validation, and state machine | 87% | 487 | H-1, M-4 |
| `src/Lender.sol` | `sell` | 497-517 | AMM swap accounting assumes transferred token amount equals requested amount, breaking on fee-on-transfer tokens | 86% | 503 |  |
| `src/Vault.sol` | `totalAssets` | 39-41 | Accounting relies on token/ETH balanceOf instead of internal ledger, enabling donation-based manipulation | 85% | 40 | M-3 |
| `src/Lender.sol` | `adjust` | 241-323 | Fee-on-transfer token accounting mismatch from assuming transferred amount equals received amount | 84% | 253 | M-2 |
| `src/Lender.sol` | `getBuyAmountOut` | 813-834 | Hardcoded 1:1 peg assumption between assets without validating real-time exchange rate or depeg | 83% | 825 |  |
| `src/Lender.sol` | `setManager` | 962-965 | Single-step ownership/privilege transfer instead of secure two-step transfer pattern | 82% | 963 |  |
| `src/Factory.sol` | `deploy` | 149-186 | Business logic, input validation, and state machine | 81% | 183 |  |
| `src/InterestModel.sol` | `calculateInterest` | 20-65 | Precision loss from performing division before multiplication in arithmetic expressions | 81% | 37 | M-5, M-6 |
| `src/Lender.sol` | `getFeedPrice` | 745-757 | Missing L2 sequencer uptime check when consuming Chainlink price feeds | 81% | 746 |  |
| `src/Lender.sol` | `getLiquidationIncentiveBps` | 677-692 | Liquidation incentive scales purely with position size, leaving small positions unprofitable to liquidate | 80% | 690 |  |
| `src/Lender.sol` | `getCollateralPrice` | 713-743 | Missing L2 sequencer uptime check when consuming Chainlink price feeds | 80% | 718 |  |
| `src/Lender.sol` | `accrueInterest` | 196-239 | Unsafe unchecked arithmetic, silent truncation, or phantom overflow in Solidity integer math | 79% | 211 | M-6 |
| `src/Lender.sol` | `updateBorrower` | 567-601 | Accounting and share math | 79% | 583 |  |
| `src/Lender.sol` | `getPendingInterest` | 878-911 | Unsafe unchecked arithmetic, silent truncation, or phantom overflow in Solidity integer math | 79% | 893 |  |
| `src/Lens.sol` | `getDebtOf` | 43-84 | Arithmetic and precision | 79% | 70 |  |
| `src/Vault.sol` | `mint` | 75-94 | Business logic, input validation, and state machine | 79% | 84 |  |
| `src/Vault.sol` | `previewMint` | 139-146 | Price derived from spot token balance ratio, manipulable via flash loans/donations | 78% | 145 |  |
| `src/Coin.sol` | `mint` | 14-17 | Missing minimum transaction/amount check enabling dust-transaction denial-of-service or griefing | 77% | 16 |  |
| `src/Lender.sol` | `setRedemptionStatus` | 338-361 | Business logic, input validation, and state machine | 76% | 352 |  |
| `src/Lender.sol` | `getLiquidatableDebt` | 668-675 | Arithmetic and precision | 76% | 669 |  |
| `src/Lender.sol` | `getRedeemAmountOut` | 762-769 | Division-by-zero causing unintended revert due to unchecked denominator | 76% | 768 |  |
| `src/Lens.sol` | `getCollateralOf` | 11-37 | Arithmetic and precision | 74% | 27 |  |
| `src/Coin.sol` | `burn` | 19-21 | Missing access control on sensitive state-changing function | 73% | 19 |  |
| `src/Vault.sol` | `withdraw` | 101-107 | Same-block deposit-then-withdraw enabling flashloan deposit-harvest-withdraw exploits | 70% | 106 |  |

### Known findings: 7 of 7 found

Found: a function-level hit on the finding's file, one of its functions, and its bug type (category or a detector mapped to it).

| Id | Severity | Title | Found? | Location |
|---|---|---|---|---|
| H-1 | High | User can abuse rounding issue in order to borrow unbacked tokens | ✅ 81% | `redeem` line 487 (category arithmetic_precision) |
| M-1 | Medium | If there's only a single user which has reached a state with bad debt, anyone can mint unbacked tokens. | ✅ 87% | `writeOff` line 433 (category business_logic_state_machine) |
| M-2 | Medium | Inconsistency in position health checks will lead to the incorrect user liquidations | ✅ 88% | `liquidate` line 397 (detector sol_defi_lending_3) |
| M-3 | Medium | EIP violation for `totalAssets()` in the `Vault` | ✅ 52% | `totalAssets` line 40 (category accounting_share_math) |
| M-4 | Medium | Accounting will be broken if a user redeems when there is a bad debt position | ✅ 82% | `redeem` line 477 (category accounting_share_math) |
| M-5 | Medium | Incorrect interest calculation | ✅ 76% | `calculateInterest` line 37 (category arithmetic_precision) |
| M-6 | Medium | Interest accrual can get stuck when `wadExp()` underflows to 0 causing division-by-zero | ✅ 81% | `calculateInterest` line 37 (detector sol_basics_math_4) |

### Flags without a known finding: 5 at 70%, 17 at 50%

A flag is a file whose chance for a category is at or over the threshold. These flags have no known finding of that category in that file: possibly unreported issues, or false positives. Not verified.

| File | Category | Chance |
|---|---|---|
| `src/Lender.sol` | External calls and token integration | 84% |
| `src/Vault.sol` | Business logic, input validation, and state machine | 81% |
| `src/Factory.sol` | Business logic, input validation, and state machine | 79% |
| `src/Lender.sol` | Denial of service and griefing | 75% |
| `src/Lens.sol` | Arithmetic and precision | 75% |

<details><summary>All 17 at 50%</summary>

| File | Category | Chance |
|---|---|---|
| `src/Lender.sol` | External calls and token integration | 84% |
| `src/Vault.sol` | Business logic, input validation, and state machine | 81% |
| `src/Factory.sol` | Business logic, input validation, and state machine | 79% |
| `src/Lender.sol` | Denial of service and griefing | 75% |
| `src/Lens.sol` | Arithmetic and precision | 75% |
| `src/Lens.sol` | Accounting and share math | 68% |
| `src/Vault.sol` | Arithmetic and precision | 68% |
| `src/Vault.sol` | External calls and token integration | 62% |
| `src/Lender.sol` | Front-running, MEV, and randomness | 60% |
| `src/Lender.sol` | Reentrancy | 60% |
| `src/Vault.sol` | Denial of service and griefing | 58% |
| `src/Factory.sol` | Denial of service and griefing | 56% |
| `src/Factory.sol` | External calls and token integration | 56% |
| `src/Lender.sol` | Access control and privilege | 56% |
| `src/Lender.sol` | Flash-loan and economic attacks | 52% |
| `src/Coin.sol` | Business logic, input validation, and state machine | 51% |
| `src/Vault.sol` | Front-running, MEV, and randomness | 50% |

</details>

## File details

<details><summary>src/Lender.sol · Crit 🟧 · Any 🟧 · Logic 86%, Tokens 84%, Math 80% · 32 functions flagged</summary>

| Function | Lines | Strongest hit | Question | Chance | Line | More |
|---|---|---|---|---|---|---|
| `reapprovePsmVault` | 543-546 | ERC20 approve() called directly to non-zero value without resetting allowance to zero first | detector sol_token_fe_13 | 90% | 545 | <details><summary>6 more</summary>Unsafe ERC-20 integration: raw transfer/approve calls and unchecked transfer amounts for non-standard tokens (detector token_integration_safety) 85%, line 545<br>Unsafe ERC20 transfer calls without return-value checks or SafeERC20 wrapper (detector sol_token_fe_1) 84%, line 545<br>Unconditional max-value ERC20 approval breaks on tokens that reject type(uint256).max amounts (detector sol_token_fe_14) 83%, line 545<br>Unsafe ERC-20 token integration without SafeERC20 or received-amount accounting (detector erc20_patterns) 81%, line 545<br>External calls and token integration (category external_call_token_integration) 64%, line 545<br>Access control and privilege (category access_control) 53%, line 545</details> |
| `constructor` | 124-175 | ERC20 approve() called directly to non-zero value without resetting allowance to zero first | detector sol_token_fe_13 | 90% | 169 | <details><summary>7 more</summary>Unconditional max-value ERC20 approval breaks on tokens that reject type(uint256).max amounts (detector sol_token_fe_14) 86%, line 169<br>External calls and token integration (category external_call_token_integration) 69%, line 169<br>Unsafe ERC-20 token integration without SafeERC20 or received-amount accounting (detector erc20_patterns) 69%, line 169<br>Unsafe ERC20 transfer calls without return-value checks or SafeERC20 wrapper (detector sol_token_fe_1) 58%, line 169<br>Business logic, input validation, and state machine (category business_logic_state_machine) 57%, line 169<br>Unsafe ERC-20 integration: raw transfer/approve calls and unchecked transfer amounts for non-standard tokens (detector token_integration_safety) 57%, line 169<br>Arithmetic and precision (category arithmetic_precision) 55%, line 160</details> |
| `decreaseDebt` | 639-666 | Division-by-zero causing unintended revert due to unchecked denominator | detector sol_basics_math_6 | 89% | 647 | <details><summary>4 more</summary>Business logic, input validation, and state machine (category business_logic_state_machine) 71%, line 647<br>Unhandled min/max boundary values causing incorrect or unsafe arithmetic results (detector sol_basics_math_12) 66%, line 647<br>Arithmetic and precision (category arithmetic_precision) 64%, line 647<br>Accounting and share math (category accounting_share_math) 53%, line 645</details> |
| `liquidate` | 368-413 | Self-liquidation profit exploit in lending protocol liquidation logic | detector sol_defi_lending_3 | 88% | 397 | <details><summary>25 more</summary>Unsafe ERC-20 token integration without SafeERC20 or received-amount accounting (detector erc20_patterns) 87%, line 401<br>Unsafe ERC-20 integration: raw transfer/approve calls and unchecked transfer amounts for non-standard tokens (detector token_integration_safety) 85%, line 401<br>External calls and token integration (category external_call_token_integration) 80%, line 397<br>Reentrancy vulnerability from unguarded or misordered external calls before state updates (detector solidity_security) 80%, line 397<br>Unsafe ERC20 transfer calls without return-value checks or SafeERC20 wrapper (detector sol_token_fe_1) 79%, line 401<br>Missing L2 sequencer uptime check when consuming Chainlink price feeds (detector sol_defi_oracle_4) 77%, line 372<br>Business logic, input validation, and state machine (category business_logic_state_machine) 75%, line 410<br>Arithmetic and precision (category arithmetic_precision) 73%, line 388<br>Access control and privilege (category access_control) 71%, line 397<br>Missing sanity/range check on oracle price allows flash-crash price manipulation (detector sol_defi_oracle_14) 71%, line 372<br>Unhandled min/max boundary values causing incorrect or unsafe arithmetic results (detector sol_basics_math_12) 69%, line 389<br>Denial of service and griefing (category dos_griefing) 68%, line 397<br>Unsafe unchecked arithmetic, silent truncation, or phantom overflow in Solidity integer math (detector integer_overflow) 67%, line 388<br>Function vulnerable to front-running enabling DoS or value extraction by transaction ordering (detector sol_basics_function_3) 66%, line 372<br>Front-running, MEV, and randomness (category frontrunning_mev) 65%, line 372<br>Reentrancy via state changes occurring after external call/interaction (detector sol_am_reentrancyattack_2) 65%, line 397<br>Liquidation incentive scales purely with position size, leaving small positions unprofitable to liquidate (detector sol_defi_lending_7) 65%, line 388<br>Fee-on-transfer token accounting mismatch from assuming transferred amount equals received amount (detector sol_token_fe_6) 65%, line 401<br>Missing validation that user-supplied actor addresses aren't the protocol's own contracts (detector sol_heuristics_9) 63%, line 407<br>Division-by-zero causing unintended revert due to unchecked denominator (detector sol_basics_math_6) 62%, line 389<br>Honeypot attack via Solmate SafeTransferLib's lack of contract-existence check for ERC20 transfers (detector sol_token_fe_8) 62%, line 397<br>Reentrancy (category reentrancy) 61%, line 397<br>Accounting and share math (category accounting_share_math) 55%, line 390<br>Payment logic vulnerable to receiver-triggered denial of service (blocked funds transfer) (detector sol_basics_payment_1) 55%, line 397<br>Liquidation can be blocked by front-running with a minimal collateral top-up or partial repay (detector sol_defi_lending_6) 50%, line 378</details> |
| `buy` | 519-541 | AMM swap accounting assumes transferred token amount equals requested amount, breaking on fee-on-transfer tokens | detector sol_defi_as_9 | 88% | 536 | <details><summary>9 more</summary>Fee-on-transfer token accounting mismatch from assuming transferred amount equals received amount (detector sol_token_fe_6) 87%, line 536<br>Honeypot attack via Solmate SafeTransferLib's lack of contract-existence check for ERC20 transfers (detector sol_token_fe_8) 77%, line 529<br>External calls and token integration (category external_call_token_integration) 69%, line 529<br>Business logic, input validation, and state machine (category business_logic_state_machine) 67%, line 534<br>Reentrancy (category reentrancy) 63%, line 532<br>Front-running, MEV, and randomness (category frontrunning_mev) 63%, line 523<br>Reentrancy vulnerability from unguarded or misordered external calls before state updates (detector solidity_security) 62%, line 529<br>Accounting and share math (category accounting_share_math) 53%, line 534<br>Read-only reentrancy via unguarded view functions returning stale state (detector sol_am_reentrancyattack_1) 50%, line 529</details> |
| `getSellAmountOut` | 771-785 | Hardcoded 1:1 peg assumption between assets without validating real-time exchange rate or depeg | detector sol_defi_general_5 | 88% | 783 | <details><summary>2 more</summary>Unhandled min/max boundary values causing incorrect or unsafe arithmetic results (detector sol_basics_math_12) 68%, line 780<br>Arithmetic and precision (category arithmetic_precision) 62%, line 777</details> |
| `writeOff` | 420-456 | Access control and privilege | category access_control | 87% | 420 | <details><summary>18 more</summary>Business logic, input validation, and state machine (category business_logic_state_machine) 87%, line 433<br>Arithmetic and precision (category arithmetic_precision) 83%, line 437<br>Denial-of-service from blacklistable tokens blocking required push transfers (detector sol_am_dosa_3) 82%, line 453<br>Missing sanity/range check on oracle price allows flash-crash price manipulation (detector sol_defi_oracle_14) 82%, line 427<br>Accounting and share math (category accounting_share_math) 78%, line 433<br>Missing validation that user-supplied actor addresses aren't the protocol's own contracts (detector sol_heuristics_9) 77%, line 453<br>External calls and token integration (category external_call_token_integration) 75%, line 453<br>Missing L2 sequencer uptime check when consuming Chainlink price feeds (detector sol_defi_oracle_4) 70%, line 427<br>Unhandled min/max boundary values causing incorrect or unsafe arithmetic results (detector sol_basics_math_12) 68%, line 437<br>Payment logic vulnerable to receiver-triggered denial of service (blocked funds transfer) (detector sol_basics_payment_1) 67%, line 453<br>Denial of service and griefing (category dos_griefing) 66%, line 453<br>Precision loss from performing division before multiplication in arithmetic expressions (detector sol_basics_math_4) 66%, line 437<br>Honeypot attack via Solmate SafeTransferLib's lack of contract-existence check for ERC20 transfers (detector sol_token_fe_8) 65%, line 453<br>Front-running, MEV, and randomness (category frontrunning_mev) 61%, line 453<br>Function vulnerable to front-running enabling DoS or value extraction by transaction ordering (detector sol_basics_function_3) 61%, line 431<br>Calling token transfer/transferFrom with a zero amount without guarding, risking revert on tokens that reject zero-value transfers (detector sol_token_fe_10) 61%, line 453<br>Unsafe unchecked arithmetic, silent truncation, or phantom overflow in Solidity integer math (detector integer_overflow) 59%, line 437<br>Missing contract-existence check before low-level call/delegatecall, allowing silent success on non-existent targets (detector sol_ec_12) 53%, line 453</details> |
| `redeem` | 463-495 | Business logic, input validation, and state machine | category business_logic_state_machine | 87% | 487 | <details><summary>20 more</summary>Fee-on-transfer token accounting mismatch from assuming transferred amount equals received amount (detector sol_token_fe_6) 85%, line 477<br>Accounting and share math (category accounting_share_math) 82%, line 477<br>Arithmetic and precision (category arithmetic_precision) 81%, line 487<br>Division-by-zero causing unintended revert due to unchecked denominator (detector sol_basics_math_6) 81%, line 487<br>Access control and privilege (category access_control) 78%, line 463<br>Unhandled min/max boundary values causing incorrect or unsafe arithmetic results (detector sol_basics_math_12) 76%, line 487<br>Accounting relies on token/ETH balanceOf instead of internal ledger, enabling donation-based manipulation (detector sol_defi_general_3) 76%, line 473<br>External calls and token integration (category external_call_token_integration) 73%, line 478<br>Honeypot attack via Solmate SafeTransferLib's lack of contract-existence check for ERC20 transfers (detector sol_token_fe_8) 73%, line 484<br>Denial of service and griefing (category dos_griefing) 69%, line 487<br>Reentrancy (category reentrancy) 66%, line 484<br>Unsafe ERC-20 token integration without SafeERC20 or received-amount accounting (detector erc20_patterns) 64%, line 478<br>Incorrect rounding direction in share/asset conversion favors user over protocol (detector sol_basics_math_5) 62%, line 482<br>Reentrancy vulnerability from unguarded or misordered external calls before state updates (detector solidity_security) 62%, line 484<br>Front-running, MEV, and randomness (category frontrunning_mev) 60%, line 466<br>AMM swap accounting assumes transferred token amount equals requested amount, breaking on fee-on-transfer tokens (detector sol_defi_as_9) 60%, line 477<br>Payment logic vulnerable to receiver-triggered denial of service (blocked funds transfer) (detector sol_basics_payment_1) 57%, line 484<br>Unsafe ERC-20 integration: raw transfer/approve calls and unchecked transfer amounts for non-standard tokens (detector token_integration_safety) 53%, line 478<br>Rounding/fee inconsistency exploitable by splitting a financial operation into many small calls (detector sol_heuristics_17) 51%, line 482<br>Reentrancy via state changes occurring after external call/interaction (detector sol_am_reentrancyattack_2) 50%, line 484</details> |
| `sell` | 497-517 | AMM swap accounting assumes transferred token amount equals requested amount, breaking on fee-on-transfer tokens | detector sol_defi_as_9 | 86% | 503 | <details><summary>20 more</summary>Missing swap deadline parameter enabling delayed transaction sandwich/MEV attacks (detector sol_defi_as_2) 83%, line 497<br>Unsafe ERC-20 token integration without SafeERC20 or received-amount accounting (detector erc20_patterns) 82%, line 503<br>Reentrancy vulnerability from unguarded or misordered external calls before state updates (detector solidity_security) 75%, line 509<br>External calls and token integration (category external_call_token_integration) 74%, line 503<br>Fee-on-transfer token accounting mismatch from assuming transferred amount equals received amount (detector sol_token_fe_6) 70%, line 504<br>Front-running, MEV, and randomness (category frontrunning_mev) 69%, line 500<br>Unchecked unsigned integer subtraction that can underflow and revert unexpectedly (detector sol_basics_math_8) 69%, line 510<br>Reentrancy (category reentrancy) 64%, line 509<br>Business logic, input validation, and state machine (category business_logic_state_machine) 64%, line 510<br>Unsafe ERC-20 integration: raw transfer/approve calls and unchecked transfer amounts for non-standard tokens (detector token_integration_safety) 64%, line 503<br>Missing minimum deposit/withdrawal threshold enabling dust-amount rounding or DoS exploits (detector sol_basics_payment_4) 60%, line 501<br>Arithmetic and precision (category arithmetic_precision) 58%, line 508<br>Denial of service and griefing (category dos_griefing) 57%, line 509<br>Access control and privilege (category access_control) 56%, line 497<br>Accounting and share math (category accounting_share_math) 56%, line 510<br>Cross-function/read-only reentrancy from external calls before state updates (detector sol_ec_1) 56%, line 509<br>Read-only reentrancy via unguarded view functions returning stale state (detector sol_am_reentrancyattack_1) 52%, line 514<br>Honeypot attack via Solmate SafeTransferLib's lack of contract-existence check for ERC20 transfers (detector sol_token_fe_8) 51%, line 514<br>Slippage check enforced on intermediate swap amount instead of final output transferred to user (detector sol_defi_as_14) 50%, line 501<br>Calling token transfer/transferFrom with a zero amount without guarding, risking revert on tokens that reject zero-value transfers (detector sol_token_fe_10) 50%, line 503</details> |
| `adjust` | 241-323 | Fee-on-transfer token accounting mismatch from assuming transferred amount equals received amount | detector sol_token_fe_6 | 84% | 253 | <details><summary>24 more</summary>Business logic, input validation, and state machine (category business_logic_state_machine) 83%, line 294<br>Arithmetic and precision (category arithmetic_precision) 77%, line 321<br>External calls and token integration (category external_call_token_integration) 76%, line 256<br>Unsafe unchecked arithmetic, silent truncation, or phantom overflow in Solidity integer math (detector integer_overflow) 74%, line 321<br>Honeypot attack via Solmate SafeTransferLib's lack of contract-existence check for ERC20 transfers (detector sol_token_fe_8) 73%, line 256<br>Front-running, MEV, and randomness (category frontrunning_mev) 70%, line 319<br>Function vulnerable to front-running enabling DoS or value extraction by transaction ordering (detector sol_basics_function_3) 70%, line 319<br>Missing sanity/range check on oracle price allows flash-crash price manipulation (detector sol_defi_oracle_14) 68%, line 319<br>Reentrancy (category reentrancy) 67%, line 277<br>Unhandled min/max boundary values causing incorrect or unsafe arithmetic results (detector sol_basics_math_12) 66%, line 321<br>Unchecked unsigned integer subtraction that can underflow and revert unexpectedly (detector sol_basics_math_8) 66%, line 275<br>Accounting and share math (category accounting_share_math) 65%, line 294<br>Denial of service and griefing (category dos_griefing) 63%, line 277<br>Missing L2 sequencer uptime check when consuming Chainlink price feeds (detector sol_defi_oracle_4) 63%, line 319<br>Reentrancy vulnerability from unguarded or misordered external calls before state updates (detector solidity_security) 63%, line 277<br>Access control and privilege (category access_control) 58%, line 286<br>Unchecked forced type casting causing silent overflow/underflow truncation (detector sol_basics_type_1) 58%, line 247<br>Same-token lend and borrow allowed in one transaction, enabling flash-loan price manipulation (detector sol_defi_lending_10) 58%, line 286<br>Flash-loan and economic attacks (category flash_loan_economic) 55%, line 286<br>Missing minimum deposit/withdrawal threshold enabling dust-amount rounding or DoS exploits (detector sol_basics_payment_4) 55%, line 253<br>Cross-function/read-only reentrancy from external calls before state updates (detector sol_ec_1) 54%, line 256<br>Missing same-block withdrawal restriction enabling flashloan-based deposit/withdraw exploits (detector sol_defi_flashloan_1) 52%, line 277<br>Reentrancy via state changes occurring after external call/interaction (detector sol_am_reentrancyattack_2) 51%, line 277<br>Missing validation that user-supplied actor addresses aren't the protocol's own contracts (detector sol_heuristics_9) 51%, line 241</details> |
| `getBuyAmountOut` | 813-834 | Hardcoded 1:1 peg assumption between assets without validating real-time exchange rate or depeg | detector sol_defi_general_5 | 83% | 825 | <details><summary>4 more</summary>Unhandled min/max boundary values causing incorrect or unsafe arithmetic results (detector sol_basics_math_12) 73%, line 822<br>Arithmetic and precision (category arithmetic_precision) 68%, line 819<br>Rounding/fee inconsistency exploitable by splitting a financial operation into many small calls (detector sol_heuristics_17) 58%, line 831<br>Unsafe unchecked arithmetic, silent truncation, or phantom overflow in Solidity integer math (detector integer_overflow) 50%, line 831</details> |
| `setManager` | 962-965 | Single-step ownership/privilege transfer instead of secure two-step transfer pattern | detector sol_cr_6 | 82% | 963 |  |
| `getFeedPrice` | 745-757 | Missing L2 sequencer uptime check when consuming Chainlink price feeds | detector sol_defi_oracle_4 | 81% | 746 | <details><summary>3 more</summary>Arithmetic and precision (category arithmetic_precision) 67%, line 754<br>Unhandled min/max boundary values causing incorrect or unsafe arithmetic results (detector sol_basics_math_12) 64%, line 751<br>Missing sanity/range check on oracle price allows flash-crash price manipulation (detector sol_defi_oracle_14) 50%, line 746</details> |
| `getCollateralPrice` | 713-743 | Missing L2 sequencer uptime check when consuming Chainlink price feeds | detector sol_defi_oracle_4 | 80% | 718 | <details><summary>4 more</summary>Silent failure from try/catch blocks that swallow external call errors instead of reverting (detector error_handling) 79%, line 725<br>Precision loss from performing division before multiplication in arithmetic expressions (detector sol_basics_math_4) 77%, line 737<br>Arithmetic and precision (category arithmetic_precision) 61%, line 737<br>Missing sanity/range check on oracle price allows flash-crash price manipulation (detector sol_defi_oracle_14) 59%, line 719</details> |
| `getLiquidationIncentiveBps` | 677-692 | Liquidation incentive scales purely with position size, leaving small positions unprofitable to liquidate | detector sol_defi_lending_7 | 80% | 690 | <details><summary>4 more</summary>Unhandled min/max boundary values causing incorrect or unsafe arithmetic results (detector sol_basics_math_12) 69%, line 678<br>Arithmetic and precision (category arithmetic_precision) 66%, line 678<br>Precision loss from performing division before multiplication in arithmetic expressions (detector sol_basics_math_4) 61%, line 690<br>Unsafe unchecked arithmetic, silent truncation, or phantom overflow in Solidity integer math (detector integer_overflow) 60%, line 678</details> |
| `accrueInterest` | 196-239 | Unsafe unchecked arithmetic, silent truncation, or phantom overflow in Solidity integer math | detector integer_overflow | 79% | 211 | <details><summary>9 more</summary>Unchecked forced type casting causing silent overflow/underflow truncation (detector sol_basics_type_1) 73%, line 211<br>Unhandled min/max boundary values causing incorrect or unsafe arithmetic results (detector sol_basics_math_12) 68%, line 222<br>Precision loss from performing division before multiplication in arithmetic expressions (detector sol_basics_math_4) 66%, line 222<br>Arithmetic and precision (category arithmetic_precision) 64%, line 222<br>External calls and token integration (category external_call_token_integration) 64%, line 223<br>Business logic, input validation, and state machine (category business_logic_state_machine) 64%, line 230<br>Access control and privilege (category access_control) 55%, line 196<br>Accounting and share math (category accounting_share_math) 54%, line 230<br>Denial of service and griefing (category dos_griefing) 52%, line 223</details> |
| `updateBorrower` | 567-601 | Accounting and share math | category accounting_share_math | 79% | 583 | <details><summary>5 more</summary>Arithmetic and precision (category arithmetic_precision) 78%, line 583<br>Business logic, input validation, and state machine (category business_logic_state_machine) 77%, line 583<br>Unhandled min/max boundary values causing incorrect or unsafe arithmetic results (detector sol_basics_math_12) 63%, line 578<br>Denial of service and griefing (category dos_griefing) 52%, line 583<br>Incorrect rounding direction in share/asset conversion favors user over protocol (detector sol_basics_math_5) 52%, line 578</details> |
| `getPendingInterest` | 878-911 | Unsafe unchecked arithmetic, silent truncation, or phantom overflow in Solidity integer math | detector integer_overflow | 79% | 893 | <details><summary>4 more</summary>Unchecked forced type casting causing silent overflow/underflow truncation (detector sol_basics_type_1) 69%, line 893<br>Precision loss from performing division before multiplication in arithmetic expressions (detector sol_basics_math_4) 64%, line 902<br>Unhandled min/max boundary values causing incorrect or unsafe arithmetic results (detector sol_basics_math_12) 61%, line 896<br>Arithmetic and precision (category arithmetic_precision) 59%, line 902</details> |
| `setRedemptionStatus` | 338-361 | Business logic, input validation, and state machine | category business_logic_state_machine | 76% | 352 | <details><summary>4 more</summary>Unchecked unsigned integer subtraction that can underflow and revert unexpectedly (detector sol_basics_math_8) 68%, line 346<br>Accounting and share math (category accounting_share_math) 62%, line 352<br>Denial of service and griefing (category dos_griefing) 58%, line 352<br>Front-running, MEV, and randomness (category frontrunning_mev) 50%, line 352</details> |
| `getRedeemAmountOut` | 762-769 | Division-by-zero causing unintended revert due to unchecked denominator | detector sol_basics_math_6 | 76% | 768 | <details><summary>7 more</summary>Arithmetic and precision (category arithmetic_precision) 75%, line 768<br>Missing sanity/range check on oracle price allows flash-crash price manipulation (detector sol_defi_oracle_14) 75%, line 768<br>Unsafe unchecked arithmetic, silent truncation, or phantom overflow in Solidity integer math (detector integer_overflow) 74%, line 768<br>Unhandled min/max boundary values causing incorrect or unsafe arithmetic results (detector sol_basics_math_12) 74%, line 768<br>Missing L2 sequencer uptime check when consuming Chainlink price feeds (detector sol_defi_oracle_4) 68%, line 764<br>Rounding/fee inconsistency exploitable by splitting a financial operation into many small calls (detector sol_heuristics_17) 54%, line 768<br>Front-running, MEV, and randomness (category frontrunning_mev) 51%, line 764</details> |
| `getLiquidatableDebt` | 668-675 | Arithmetic and precision | category arithmetic_precision | 76% | 669 | <details><summary>2 more</summary>Unsafe unchecked arithmetic, silent truncation, or phantom overflow in Solidity integer math (detector integer_overflow) 76%, line 669<br>Unhandled min/max boundary values causing incorrect or unsafe arithmetic results (detector sol_basics_math_12) 73%, line 669</details> |
| `adjust` | 325-328 | Access control and privilege | category access_control | 68% | 325 | <details><summary>1 more</summary>Business logic, input validation, and state machine (category business_logic_state_machine) 58%, line 326</details> |
| `pullGlobalReserves` | 980-986 | Reentrancy vulnerability from unguarded or misordered external calls before state updates | detector solidity_security | 67% | 983 | <details><summary>6 more</summary>Reentrancy (category reentrancy) 64%, line 983<br>External calls and token integration (category external_call_token_integration) 62%, line 983<br>Reentrancy via state changes occurring after external call/interaction (detector sol_am_reentrancyattack_2) 56%, line 983<br>Business logic, input validation, and state machine (category business_logic_state_machine) 55%, line 983<br>Cross-function/read-only reentrancy from external calls before state updates (detector sol_ec_1) 52%, line 983<br>Missing validation that user-supplied actor addresses aren't the protocol's own contracts (detector sol_heuristics_9) 52%, line 983</details> |
| `pullLocalReserves` | 972-978 | Reentrancy vulnerability from unguarded or misordered external calls before state updates | detector solidity_security | 67% | 975 | <details><summary>3 more</summary>External calls and token integration (category external_call_token_integration) 63%, line 975<br>Reentrancy (category reentrancy) 57%, line 975<br>Business logic, input validation, and state machine (category business_logic_state_machine) 51%, line 975</details> |
| `increaseDebt` | 603-637 | Business logic, input validation, and state machine | category business_logic_state_machine | 66% | 619 | <details><summary>6 more</summary>Arithmetic and precision (category arithmetic_precision) 63%, line 608<br>Incorrect rounding direction in share/asset conversion favors user over protocol (detector sol_basics_math_5) 60%, line 608<br>Accounting and share math (category accounting_share_math) 56%, line 616<br>Unhandled min/max boundary values causing incorrect or unsafe arithmetic results (detector sol_basics_math_12) 56%, line 618<br>Missing validation that user-supplied actor addresses aren't the protocol's own contracts (detector sol_heuristics_9) 52%, line 613<br>Fee-on-transfer token accounting mismatch from assuming transferred amount equals received amount (detector sol_token_fe_6) 51%, line 611</details> |
| `accruePsmProfit` | 550-565 | Accounting relies on token/ETH balanceOf instead of internal ledger, enabling donation-based manipulation | detector sol_defi_general_3 | 65% | 559 | <details><summary>2 more</summary>Unsafe unchecked arithmetic, silent truncation, or phantom overflow in Solidity integer math (detector integer_overflow) 56%, line 555<br>Unchecked forced type casting causing silent overflow/underflow truncation (detector sol_basics_type_1) 52%, line 555</details> |
| `getDebtOf` | 701-707 | Incorrect rounding direction in share/asset conversion favors user over protocol | detector sol_basics_math_5 | 59% | 703 |  |
| `internalToCollateral` | 865-873 | Arithmetic and precision | category arithmetic_precision | 59% | 871 | <details><summary>1 more</summary>Unhandled min/max boundary values causing incorrect or unsafe arithmetic results (detector sol_basics_math_12) 56%, line 869</details> |
| `collateralToInternal` | 852-860 | Arithmetic and precision | category arithmetic_precision | 56% | 856 | <details><summary>1 more</summary>Unhandled min/max boundary values causing incorrect or unsafe arithmetic results (detector sol_basics_math_12) 56%, line 858</details> |
| `getFreeDebtRatio` | 696-699 | Unsafe unchecked arithmetic, silent truncation, or phantom overflow in Solidity integer math | detector integer_overflow | 55% | 698 | <details><summary>1 more</summary>Unhandled min/max boundary values causing incorrect or unsafe arithmetic results (detector sol_basics_math_12) 51%, line 698</details> |
| `normalizePsmAssets` | 839-847 | Unhandled min/max boundary values causing incorrect or unsafe arithmetic results | detector sol_basics_math_12 | 53% | 845 | <details><summary>1 more</summary>Arithmetic and precision (category arithmetic_precision) 52%, line 843</details> |
| `setHalfLife` | 915-920 | Unsafe unchecked arithmetic, silent truncation, or phantom overflow in Solidity integer math | detector integer_overflow | 51% | 918 |  |

<details><summary>File-level hits (51)</summary>

| Chance | Question | What it asks |
|---|---|---|
| 87% | detector sol_defi_oracle_4 | Missing L2 sequencer uptime check when consuming Chainlink price feeds |
| 87% | detector sol_token_fe_13 | ERC20 approve() called directly to non-zero value without resetting allowance to zero first |
| 86% | category business_logic_state_machine | Business logic, input validation, and state machine |
| 86% | detector sol_token_fe_14 | Unconditional max-value ERC20 approval breaks on tokens that reject type(uint256).max amounts |
| 85% | detector sol_token_fe_8 | Honeypot attack via Solmate SafeTransferLib's lack of contract-existence check for ERC20 transfers |
| 84% | category external_call_token_integration | External calls and token integration |
| 83% | detector sol_token_fe_6 | Fee-on-transfer token accounting mismatch from assuming transferred amount equals received amount |
| 82% | detector sol_basics_math_12 | Unhandled min/max boundary values causing incorrect or unsafe arithmetic results |
| 82% | detector sol_defi_lending_3 | Self-liquidation profit exploit in lending protocol liquidation logic |
| 80% | category arithmetic_precision | Arithmetic and precision |
| 80% | detector erc20_patterns | Unsafe ERC-20 token integration without SafeERC20 or received-amount accounting |
| 77% | detector integer_overflow | Unsafe unchecked arithmetic, silent truncation, or phantom overflow in Solidity integer math |
| 76% | detector solidity_security | Reentrancy vulnerability from unguarded or misordered external calls before state updates |
| 75% | category dos_griefing | Denial of service and griefing |
| 75% | detector sol_basics_math_4 | Precision loss from performing division before multiplication in arithmetic expressions |
| 75% | detector token_integration_safety | Unsafe ERC-20 integration: raw transfer/approve calls and unchecked transfer amounts for non-standard tokens |
| 73% | category accounting_share_math | Accounting and share math |
| 73% | detector sol_defi_lending_6 | Liquidation can be blocked by front-running with a minimal collateral top-up or partial repay |
| 72% | detector sol_defi_as_2 | Missing swap deadline parameter enabling delayed transaction sandwich/MEV attacks |
| 71% | detector sol_defi_as_9 | AMM swap accounting assumes transferred token amount equals requested amount, breaking on fee-on-transfer tokens |
| 70% | detector sol_basics_type_1 | Unchecked forced type casting causing silent overflow/underflow truncation |
| 66% | detector sol_heuristics_9 | Missing validation that user-supplied actor addresses aren't the protocol's own contracts |
| 65% | detector sol_am_reentrancyattack_1 | Read-only reentrancy via unguarded view functions returning stale state |
| 65% | detector sol_defi_general_5 | Hardcoded 1:1 peg assumption between assets without validating real-time exchange rate or depeg |
| 64% | detector sol_am_reentrancyattack_2 | Reentrancy via state changes occurring after external call/interaction |
| 64% | detector sol_basics_math_5 | Incorrect rounding direction in share/asset conversion favors user over protocol |
| 64% | detector sol_ec_1 | Cross-function/read-only reentrancy from external calls before state updates |
| 63% | detector sol_basics_payment_1 | Payment logic vulnerable to receiver-triggered denial of service (blocked funds transfer) |
| 63% | detector sol_defi_flashloan_1 | Missing same-block withdrawal restriction enabling flashloan-based deposit/withdraw exploits |
| 63% | detector sol_defi_oracle_14 | Missing sanity/range check on oracle price allows flash-crash price manipulation |
| 62% | detector sol_am_dosa_3 | Denial-of-service from blacklistable tokens blocking required push transfers |
| 62% | detector sol_basics_function_3 | Function vulnerable to front-running enabling DoS or value extraction by transaction ordering |
| 61% | detector error_handling | Silent failure from try/catch blocks that swallow external call errors instead of reverting |
| 61% | detector sol_token_fe_10 | Calling token transfer/transferFrom with a zero amount without guarding, risking revert on tokens that reject zero-value transfers |
| 60% | category reentrancy | Reentrancy |
| 60% | category frontrunning_mev | Front-running, MEV, and randomness |
| 59% | detector sol_defi_as_14 | Slippage check enforced on intermediate swap amount instead of final output transferred to user |
| 58% | detector sol_token_fe_1 | Unsafe ERC20 transfer calls without return-value checks or SafeERC20 wrapper |
| 56% | category access_control | Access control and privilege |
| 56% | detector sol_basics_math_6 | Division-by-zero causing unintended revert due to unchecked denominator |
| 56% | detector sol_defi_general_3 | Accounting relies on token/ETH balanceOf instead of internal ledger, enabling donation-based manipulation |
| 56% | detector sol_defi_lending_10 | Same-token lend and borrow allowed in one transaction, enabling flash-loan price manipulation |
| 56% | detector sol_heuristics_17 | Rounding/fee inconsistency exploitable by splitting a financial operation into many small calls |
| 54% | detector sol_basics_payment_4 | Missing minimum deposit/withdrawal threshold enabling dust-amount rounding or DoS exploits |
| 53% | detector sol_basics_math_8 | Unchecked unsigned integer subtraction that can underflow and revert unexpectedly |
| 53% | detector sol_cr_6 | Single-step ownership/privilege transfer instead of secure two-step transfer pattern |
| 53% | detector sol_defi_general_9 | Unsafe support for arbitrary/non-standard ERC20 tokens (fee-on-transfer, rebasing) without whitelisting |
| 53% | detector sol_defi_lending_7 | Liquidation incentive scales purely with position size, leaving small positions unprofitable to liquidate |
| 52% | category flash_loan_economic | Flash-loan and economic attacks |
| 52% | detector sol_ec_12 | Missing contract-existence check before low-level call/delegatecall, allowing silent success on non-existent targets |
| 50% | detector sol_basics_al_6 | Precision mismatch between summed aggregate calculation and sum of individual per-item calculations |

</details>


</details>

<details><summary>src/Vault.sol · Crit 🟧 · Any 🟧 · Logic 81%, Shares 77%, Math 68% · 8 functions flagged</summary>

| Function | Lines | Strongest hit | Question | Chance | Line | More |
|---|---|---|---|---|---|---|
| `deposit` | 47-68 | Fee-on-transfer token accounting mismatch from assuming transferred amount equals received amount | detector sol_token_fe_6 | 89% | 56 | <details><summary>13 more</summary>Business logic, input validation, and state machine (category business_logic_state_machine) 85%, line 62<br>Unchecked unsigned integer subtraction that can underflow and revert unexpectedly (detector sol_basics_math_8) 84%, line 62<br>Accounting and share math (category accounting_share_math) 81%, line 62<br>Honeypot attack via Solmate SafeTransferLib's lack of contract-existence check for ERC20 transfers (detector sol_token_fe_8) 76%, line 54<br>Arithmetic and precision (category arithmetic_precision) 75%, line 62<br>Missing validation that user-supplied actor addresses aren't the protocol's own contracts (detector sol_heuristics_9) 68%, line 56<br>External calls and token integration (category external_call_token_integration) 67%, line 54<br>Denial of service and griefing (category dos_griefing) 66%, line 62<br>Same-block deposit-then-withdraw enabling flashloan deposit-harvest-withdraw exploits (detector sol_defi_general_8) 62%, line 56<br>Front-running, MEV, and randomness (category frontrunning_mev) 61%, line 51<br>Unhandled min/max boundary values causing incorrect or unsafe arithmetic results (detector sol_basics_math_12) 56%, line 62<br>Missing access control on privileged/critical functions (detector access_control_patterns) 54%, line 47<br>ERC4626 vault share-price manipulation via flashloan-funded balance donation (inflation attack) (detector sol_defi_flashloan_2) 54%, line 51</details> |
| `totalAssets` | 39-41 | Accounting relies on token/ETH balanceOf instead of internal ledger, enabling donation-based manipulation | detector sol_defi_general_3 | 85% | 40 | <details><summary>3 more</summary>ERC4626 vault share-price manipulation via flashloan-funded balance donation (inflation attack) (detector sol_defi_flashloan_2) 75%, line 40<br>Donation/balance-manipulation attack via reliance on token.balanceOf instead of internal accounting (detector sol_am_da_1) 67%, line 40<br>Accounting and share math (category accounting_share_math) 52%, line 40</details> |
| `mint` | 75-94 | Business logic, input validation, and state machine | category business_logic_state_machine | 79% | 84 | <details><summary>11 more</summary>Fee-on-transfer token accounting mismatch from assuming transferred amount equals received amount (detector sol_token_fe_6) 75%, line 79<br>Honeypot attack via Solmate SafeTransferLib's lack of contract-existence check for ERC20 transfers (detector sol_token_fe_8) 74%, line 79<br>Missing validation that user-supplied actor addresses aren't the protocol's own contracts (detector sol_heuristics_9) 64%, line 84<br>Accounting and share math (category accounting_share_math) 62%, line 84<br>Missing access control on privileged/critical functions (detector access_control_patterns) 61%, line 75<br>External calls and token integration (category external_call_token_integration) 60%, line 79<br>Unchecked unsigned integer subtraction that can underflow and revert unexpectedly (detector sol_basics_math_8) 59%, line 86<br>Denial of service and griefing (category dos_griefing) 55%, line 84<br>Same-block deposit-then-withdraw enabling flashloan deposit-harvest-withdraw exploits (detector sol_defi_general_8) 55%, line 90<br>Front-running, MEV, and randomness (category frontrunning_mev) 54%, line 77<br>Griefing/DoS via dust-amount front-running that breaks exact-match state checks (detector sol_am_fra_3) 54%, line 81</details> |
| `previewMint` | 139-146 | Price derived from spot token balance ratio, manipulable via flash loans/donations | detector sol_am_pma_1 | 78% | 145 | <details><summary>1 more</summary>Accounting and share math (category accounting_share_math) 52%, line 141</details> |
| `withdraw` | 101-107 | Same-block deposit-then-withdraw enabling flashloan deposit-harvest-withdraw exploits | detector sol_defi_general_8 | 70% | 106 | <details><summary>5 more</summary>Denial-of-service from blacklistable tokens blocking required push transfers (detector sol_am_dosa_3) 61%, line 106<br>Front-running, MEV, and randomness (category frontrunning_mev) 56%, line 106<br>Missing same-block withdrawal restriction enabling flashloan-based deposit/withdraw exploits (detector sol_defi_flashloan_1) 55%, line 106<br>ERC4626 vault share-price manipulation via flashloan-funded balance donation (inflation attack) (detector sol_defi_flashloan_2) 55%, line 106<br>Missing validation that user-supplied actor addresses aren't the protocol's own contracts (detector sol_heuristics_9) 53%, line 106</details> |
| `redeem` | 114-120 | Same-block deposit-then-withdraw enabling flashloan deposit-harvest-withdraw exploits | detector sol_defi_general_8 | 69% | 119 | <details><summary>4 more</summary>ERC4626 vault share-price manipulation via flashloan-funded balance donation (inflation attack) (detector sol_defi_flashloan_2) 59%, line 119<br>Front-running, MEV, and randomness (category frontrunning_mev) 56%, line 119<br>Denial-of-service from blacklistable tokens blocking required push transfers (detector sol_am_dosa_3) 51%, line 119<br>Missing same-block withdrawal restriction enabling flashloan-based deposit/withdraw exploits (detector sol_defi_flashloan_1) 50%, line 119</details> |
| `previewDeposit` | 125-134 | Accounting and share math | category accounting_share_math | 67% | 131 | <details><summary>2 more</summary>Arithmetic and precision (category arithmetic_precision) 57%, line 131<br>Business logic, input validation, and state machine (category business_logic_state_machine) 56%, line 131</details> |
| `constructor` | 22-32 | ERC4626 vault share-price manipulation via flashloan-funded balance donation (inflation attack) | detector sol_defi_flashloan_2 | 56% | 26 |  |

<details><summary>File-level hits (21)</summary>

| Chance | Question | What it asks |
|---|---|---|
| 89% | detector sol_token_fe_6 | Fee-on-transfer token accounting mismatch from assuming transferred amount equals received amount |
| 81% | category business_logic_state_machine | Business logic, input validation, and state machine |
| 79% | detector sol_defi_flashloan_1 | Missing same-block withdrawal restriction enabling flashloan-based deposit/withdraw exploits |
| 77% | category accounting_share_math | Accounting and share math |
| 77% | detector sol_defi_general_3 | Accounting relies on token/ETH balanceOf instead of internal ledger, enabling donation-based manipulation |
| 73% | detector sol_basics_math_8 | Unchecked unsigned integer subtraction that can underflow and revert unexpectedly |
| 68% | category arithmetic_precision | Arithmetic and precision |
| 67% | detector sol_defi_general_8 | Same-block deposit-then-withdraw enabling flashloan deposit-harvest-withdraw exploits |
| 66% | detector sol_token_fe_8 | Honeypot attack via Solmate SafeTransferLib's lack of contract-existence check for ERC20 transfers |
| 64% | detector sol_am_pma_1 | Price derived from spot token balance ratio, manipulable via flash loans/donations |
| 63% | detector sol_am_da_1 | Donation/balance-manipulation attack via reliance on token.balanceOf instead of internal accounting |
| 63% | detector sol_heuristics_9 | Missing validation that user-supplied actor addresses aren't the protocol's own contracts |
| 62% | category external_call_token_integration | External calls and token integration |
| 59% | detector sol_am_dosa_3 | Denial-of-service from blacklistable tokens blocking required push transfers |
| 58% | category dos_griefing | Denial of service and griefing |
| 56% | detector access_control_patterns | Missing access control on privileged/critical functions |
| 55% | detector sol_basics_math_12 | Unhandled min/max boundary values causing incorrect or unsafe arithmetic results |
| 55% | detector sol_defi_flashloan_2 | ERC4626 vault share-price manipulation via flashloan-funded balance donation (inflation attack) |
| 54% | detector sol_am_fra_3 | Griefing/DoS via dust-amount front-running that breaks exact-match state checks |
| 51% | detector sol_am_reentrancyattack_1 | Read-only reentrancy via unguarded view functions returning stale state |
| 50% | category frontrunning_mev | Front-running, MEV, and randomness |

</details>


</details>

<details><summary>src/Factory.sol · Crit 🟨 · Any 🟧 · Logic 79%, Tokens 56%, DoS 56% · 5 functions flagged</summary>

| Function | Lines | Strongest hit | Question | Chance | Line | More |
|---|---|---|---|---|---|---|
| `deploy` | 149-186 | Business logic, input validation, and state machine | category business_logic_state_machine | 81% | 183 | <details><summary>2 more</summary>Paired state-changing functions (add/remove, deposit/withdraw) are asymmetric, leaving stale or incorrect state. (detector sol_heuristics_16) 71%, line 184<br>Lending protocol lacks a working liquidation mechanism for undercollateralized or defaulted loans (detector sol_defi_lending_2) 60%, line 149</details> |
| `deployLender` | 25-27 | Business logic, input validation, and state machine | category business_logic_state_machine | 64% | 26 |  |
| `deployVault` | 39-41 | Business logic, input validation, and state machine | category business_logic_state_machine | 64% | 40 |  |
| `deploy` | 11-13 | Business logic, input validation, and state machine | category business_logic_state_machine | 62% | 12 |  |
| `deployCoin` | 53-55 | Business logic, input validation, and state machine | category business_logic_state_machine | 61% | 54 |  |

<details><summary>File-level hits (5)</summary>

| Chance | Question | What it asks |
|---|---|---|
| 79% | category business_logic_state_machine | Business logic, input validation, and state machine |
| 60% | detector sol_heuristics_16 | Paired state-changing functions (add/remove, deposit/withdraw) are asymmetric, leaving stale or incorrect state. |
| 57% | detector sol_defi_lending_2 | Lending protocol lacks a working liquidation mechanism for undercollateralized or defaulted loans |
| 56% | category external_call_token_integration | External calls and token integration |
| 56% | category dos_griefing | Denial of service and griefing |

</details>


</details>

<details><summary>src/Lens.sol · Crit 🟨 · Any 🟨 · Math 75%, Shares 68% · 3 functions flagged</summary>

| Function | Lines | Strongest hit | Question | Chance | Line | More |
|---|---|---|---|---|---|---|
| `_getSyncedTotalDebt` | 90-117 | Silent failure from try/catch blocks that swallow external call errors instead of reverting | detector error_handling | 90% | 115 | <details><summary>2 more</summary>try/catch external call may fail from insufficient gas, causing unhandled or unsafe fallback behavior (detector sol_heuristics_5) 70%, line 102<br>Unhandled min/max boundary values causing incorrect or unsafe arithmetic results (detector sol_basics_math_12) 51%, line 112</details> |
| `getDebtOf` | 43-84 | Arithmetic and precision | category arithmetic_precision | 79% | 70 | <details><summary>4 more</summary>Unhandled min/max boundary values causing incorrect or unsafe arithmetic results (detector sol_basics_math_12) 68%, line 70<br>Accounting and share math (category accounting_share_math) 67%, line 70<br>Incorrect rounding direction in share/asset conversion favors user over protocol (detector sol_basics_math_5) 65%, line 56<br>Lending protocol lacks a working liquidation mechanism for undercollateralized or defaulted loans (detector sol_defi_lending_2) 58%, line 43</details> |
| `getCollateralOf` | 11-37 | Arithmetic and precision | category arithmetic_precision | 74% | 27 | <details><summary>3 more</summary>Accounting and share math (category accounting_share_math) 66%, line 27<br>Unhandled min/max boundary values causing incorrect or unsafe arithmetic results (detector sol_basics_math_12) 64%, line 22<br>Lending protocol lacks a working liquidation mechanism for undercollateralized or defaulted loans (detector sol_defi_lending_2) 58%, line 11</details> |

<details><summary>File-level hits (7)</summary>

| Chance | Question | What it asks |
|---|---|---|
| 86% | detector error_handling | Silent failure from try/catch blocks that swallow external call errors instead of reverting |
| 82% | detector sol_defi_lending_2 | Lending protocol lacks a working liquidation mechanism for undercollateralized or defaulted loans |
| 75% | category arithmetic_precision | Arithmetic and precision |
| 75% | detector sol_basics_math_12 | Unhandled min/max boundary values causing incorrect or unsafe arithmetic results |
| 68% | category accounting_share_math | Accounting and share math |
| 55% | detector sol_heuristics_5 | try/catch external call may fail from insufficient gas, causing unhandled or unsafe fallback behavior |
| 52% | detector sol_basics_math_5 | Incorrect rounding direction in share/asset conversion favors user over protocol |

</details>


</details>

<details><summary>src/InterestModel.sol · Crit 🟩 · Any 🟩 · Math 60% · 1 function flagged</summary>

| Function | Lines | Strongest hit | Question | Chance | Line | More |
|---|---|---|---|---|---|---|
| `calculateInterest` | 20-65 | Precision loss from performing division before multiplication in arithmetic expressions | detector sol_basics_math_4 | 81% | 37 | <details><summary>3 more</summary>Unhandled min/max boundary values causing incorrect or unsafe arithmetic results (detector sol_basics_math_12) 79%, line 37<br>Arithmetic and precision (category arithmetic_precision) 76%, line 37<br>Division-by-zero causing unintended revert due to unchecked denominator (detector sol_basics_math_6) 69%, line 36</details> |

<details><summary>File-level hits (4)</summary>

| Chance | Question | What it asks |
|---|---|---|
| 74% | detector sol_basics_math_12 | Unhandled min/max boundary values causing incorrect or unsafe arithmetic results |
| 68% | detector sol_basics_math_4 | Precision loss from performing division before multiplication in arithmetic expressions |
| 63% | detector sol_basics_math_6 | Division-by-zero causing unintended revert due to unchecked denominator |
| 60% | category arithmetic_precision | Arithmetic and precision |

</details>


</details>

<details><summary>src/Coin.sol · Crit 🟩 · Any 🟩 · Logic 51% · 2 functions flagged</summary>

| Function | Lines | Strongest hit | Question | Chance | Line | More |
|---|---|---|---|---|---|---|
| `mint` | 14-17 | Missing minimum transaction/amount check enabling dust-transaction denial-of-service or griefing | detector sol_am_dosa_2 | 77% | 16 |  |
| `burn` | 19-21 | Missing access control on sensitive state-changing function | detector sol_basics_function_9 | 73% | 19 | <details><summary>1 more</summary>Missing minimum transaction/amount check enabling dust-transaction denial-of-service or griefing (detector sol_am_dosa_2) 61%, line 20</details> |

<details><summary>File-level hits (3)</summary>

| Chance | Question | What it asks |
|---|---|---|
| 73% | detector sol_am_dosa_2 | Missing minimum transaction/amount check enabling dust-transaction denial-of-service or griefing |
| 65% | detector sol_basics_function_9 | Missing access control on sensitive state-changing function |
| 51% | category business_logic_state_machine | Business logic, input validation, and state machine |

</details>


</details>

---

Jev model jev-1.13.0 · hit threshold 50% · generated 2026-09-18
