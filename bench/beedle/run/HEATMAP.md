# 🔥 jevscan heat map: beedle

**86% chance of a critical bug · 88% chance of at least one exploitable bug · hottest file: `src/Lender.sol`**

Numbers are Jev's probability that the statement is true.

| Codebase | |
|---|---|
| Name | beedle |
| Solidity files found | 12 |
| Lines of code | 929 (non-blank, scanned files) |
| Scanned | 7 |
| Ignored | 1 script, 2 interfaces, 2 tests |

101 requests · $0.06 · 0.4 s · 100 answers from cache (billed <$0.01)

## Heat grid

| File | Crit | Any | Access | Proxy | Oracle | Econ | Reentry | Shares | Math | Sigs | Xchain | Tokens | Logic | DoS | MEV | LowLvl |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `src/Lender.sol` | 🟥 | 🟥 | 🟨 | 🟩 | 🟩 | 🟧 | 🟥 | 🟥 | 🟥 | 🟩 | 🟩 | 🟥 | 🟥 | 🟥 | 🟥 | 🟩 |
| `src/Staking.sol` | 🟧 | 🟥 | 🟥 | 🟩 | 🟩 | 🟨 | 🟧 | 🟧 | 🟧 | 🟩 | 🟩 | 🟥 | 🟥 | 🟥 | 🟨 | 🟩 |
| `src/Fees.sol` | 🟧 | 🟥 | 🟧 | 🟩 | 🟩 | 🟨 | 🟨 | 🟩 | 🟩 | 🟩 | 🟩 | 🟥 | 🟧 | 🟧 | 🟧 | 🟩 |
| `src/Beedle.sol` | 🟨 | 🟧 | 🟩 | 🟩 | 🟩 | 🟩 | 🟩 | 🟩 | 🟩 | 🟩 | 🟩 | 🟩 | 🟨 | 🟩 | 🟩 | 🟩 |
| `src/utils/Structs.sol` | 🟨 | 🟨 | 🟩 | 🟩 | 🟩 | 🟨 | 🟩 | 🟩 | 🟩 | 🟩 | 🟩 | 🟩 | 🟩 | 🟨 | 🟨 | 🟩 |
| `src/utils/Ownable.sol` | 🟩 | 🟩 | 🟩 | 🟩 | 🟩 | 🟩 | 🟩 | 🟩 | 🟩 | 🟩 | 🟩 | 🟩 | 🟩 | 🟩 | 🟩 | 🟩 |
| `src/utils/Errors.sol` | 🟩 | 🟩 | 🟩 | 🟩 | 🟩 | 🟩 | 🟩 | 🟩 | 🟩 | 🟩 | 🟩 | 🟩 | 🟩 | 🟩 | 🟩 | 🟩 |

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

## Strongest function hits (70%+): 18

Every function whose strongest hit is 70% or more, by that hit. Its other hits, and every function hit from 50% to 70%, are under its file below.

| File | Function | Lines | What it found | Chance | Line | Corresponding findings |
|---|---|---|---|---|---|---|
| `src/Fees.sol` | `sellProfits` | 26-44 | Hard-coded Uniswap V3 fee tier parameter in swap function | 98% | 34 | H-4, H-14, H-15, H-22, M-4, M-8, M-15 |
| `src/Lender.sol` | `repay` | 292-345 | Unsafe ERC-20 integration: raw transfer/approve calls and unchecked transfer amounts for non-standard tokens | 98% | 317 | H-2, H-20, M-3, M-12, M-14 |
| `src/utils/Ownable.sol` | `transferOwnership` | 19-22 | Single-step ownership/privilege transfer without two-step accept confirmation | 98% | 20 | M-6 |
| `src/Lender.sol` | `addToPool` | 182-192 | Unsafe ERC-20 integration: raw transfer/approve calls and unchecked transfer amounts for non-standard tokens | 97% | 187 | H-20 |
| `src/Lender.sol` | `borrow` | 232-287 | Unsafe ERC-20 token integration without SafeERC20 or received-amount accounting | 97% | 271 | H-1, H-20, H-23, H-26, K-27, M-2, M-14 |
| `src/Lender.sol` | `seizeLoan` | 548-586 | Unsafe ERC-20 integration: raw transfer/approve calls and unchecked transfer amounts for non-standard tokens | 97% | 563 | M-3, M-7 |
| `src/Lender.sol` | `refinance` | 591-710 | Unsafe ERC-20 token integration without SafeERC20 or received-amount accounting | 97% |  | H-1, H-5, H-6, H-20, H-26, K-27, M-2, M-11 |
| `src/Staking.sol` | `deposit` | 38-42 | Unsafe ERC-20 token integration without SafeERC20 or received-amount accounting | 97% | 39 | H-12, H-16, H-17, H-24, M-10 |
| `src/Staking.sol` | `withdraw` | 46-50 | Unsafe ERC-20 integration: raw transfer/approve calls and unchecked transfer amounts for non-standard tokens | 97% | 49 | H-12, H-17 |
| `src/Lender.sol` | `setPool` | 130-176 | Unsafe ERC-20 token integration without SafeERC20 or received-amount accounting | 96% | 152 | H-3, H-20 |
| `src/Lender.sol` | `removeFromPool` | 198-204 | Unsafe ERC-20 integration: raw transfer/approve calls and unchecked transfer amounts for non-standard tokens | 96% | 203 | M-3 |
| `src/Lender.sol` | `giveLoan` | 355-432 | Unsafe ERC-20 integration: raw transfer/approve calls and unchecked transfer amounts for non-standard tokens | 95% |  | H-1, H-21, M-1, M-5 |
| `src/Lender.sol` | `buyLoan` | 465-534 | Unsafe ERC-20 token integration without SafeERC20 or received-amount accounting | 95% | 505 | H-7, H-9, H-11, H-19 |
| `src/Staking.sol` | `claim` | 53-58 | Unsafe ERC-20 integration: raw transfer/approve calls and unchecked transfer amounts for non-standard tokens | 95% | 55 | H-16, H-17, H-25, M-10 |
| `src/Staking.sol` | `update` | 61-76 | Incorrect handling of ERC20 tokens with non-18 decimals causing miscalculation | 91% | 68 | H-13, H-24 |
| `src/Staking.sol` | `updateFor` | 80-94 | Incorrect handling of ERC20 tokens with non-18 decimals causing miscalculation | 91% | 88 | H-16, H-24 |
| `src/Lender.sol` | `_calculateInterest` | 720-727 | Unsafe unchecked arithmetic, silent truncation, or phantom overflow in Solidity integer math | 85% | 724 | M-1, M-13 |
| `src/Lender.sol` | `startAuction` | 437-459 | Business logic, input validation, and state machine | 82% | 448 |  |

### Known findings: 38 of 42 found

Found: a function-level hit on the finding's file, one of its functions, and its bug type (category or a detector mapped to it).

| Id | Severity | Title | Found? | Location |
|---|---|---|---|---|
| H-1 | High | Tokens with less than 18 decimals allow for draining of funds | ✅ 93% | `refinance` (detector sol_defi_general_1) |
| H-2 | High | Lender contract can be drained by re-entrancy in `repay` | ✅ 73% | `repay` line 329 (detector solidity_security) |
| H-3 | High | Lender contract can be drained by re-entrancy in `setPool` | ✅ 83% | `setPool` line 152 (detector solidity_security) |
| H-4 | High | Sandwich attack to steal all ERC-20 tokens in the Fees contract | ✅ 96% | `sellProfits` line 38 (detector sol_defi_as_11) |
| H-5 | High | Borrower can use Refinance to cancel auctions so they can extend their loan indefinitely | ✅ 89% | `refinance` (category business_logic_state_machine) |
| H-6 | High | During refinance() new Pool balance debt is subtracted twice | ✅ 84% | `refinance` (category accounting_share_math) |
| H-7 | High | Borrower can bypass maxLoanRatio's configuration of a pool via buyLoan() | ✅ 88% | `buyLoan` line 478 (category business_logic_state_machine) |
| H-8 | High | Lender#buyLoan - Malicious user could take over a loan for free without having a pool because of wrong access control | ❌ |  |
| H-9 | High | Using forged/fake lending pools to steal any loan opening for auction | ✅ 88% | `buyLoan` line 478 (category business_logic_state_machine) |
| H-10 | High | Stealing any loan opening for auction through others' lending pool | ❌ |  |
| H-11 | High | Attacker can steal a loan's collateral and break the protocol | ✅ 88% | `buyLoan` line 478 (category business_logic_state_machine) |
| H-12 | High | Fee on transfer tokens will cause users to lose funds | ✅ 97% | `withdraw` line 49 (detector token_integration_safety) |
| H-13 | High | update() not getting called right after a WETH amount has been sent will cause users to lose staking rewards | ✅ 62% | `update` line 70 (category accounting_share_math) |
| H-14 | High | Sandwich attack to steal all ERC-20 tokens in the Fees contract | ✅ 96% | `sellProfits` line 38 (detector sol_defi_as_11) |
| H-15 | High | Token spending by Uniswap router doesn't get approved | ✅ 86% | `sellProfits` line 42 (category external_call_token_integration) |
| H-16 | High | Front-runnig the first deposit on stake yealds the whole WETH amount | ✅ 60% | `claim` line 54 (detector sol_defi_general_8) |
| H-17 | High | Rewards can be sabotaged by large deposit and withdraw | ✅ 67% | `withdraw` line 49 (detector sol_defi_general_8) |
| H-18 | High | Borrower can prevent his/her loan from being liquidated | ❌ |  |
| H-19 | High | A pool lender can fully drain another user's pool by abusing `buyLoan` | ✅ 88% | `buyLoan` line 478 (category business_logic_state_machine) |
| H-20 | High | `Lender` does not handle correctly rebasing, inflationary, deflationary tokens and tokens with fee on transfer | ✅ 98% | `repay` line 317 (detector token_integration_safety) |
| H-21 | High | Forcing a borrower to pay a huge debt via the giveLoan() | ✅ 78% | `giveLoan` (category accounting_share_math) |
| H-22 | High | Hardcoded Router Address May Cause Token Lockup in Non-Standard Networks | ✅ 86% | `sellProfits` line 42 (category external_call_token_integration) |
| H-23 | High | Lender can Sandwich a borrower to seize his collateral | ✅ 59% | `borrow` line 243 (detector sol_basics_function_3) |
| H-24 | High | WETH staking rewards accumulated before the first staker deposits remain unutilized and stuck in the `Staking` contract | ✅ 62% | `update` line 70 (category accounting_share_math) |
| H-25 | High | WETH token balance is incorrectly updated when claiming staking rewards resulting in stuck WETH rewards | ✅ 69% | `claim` line 57 (category accounting_share_math) |
| H-26 | High | The `borrow` and `refinance` functions can be front-run by the pool lender leading to collateral being seized in the next block | ✅ 64% | `refinance` (category frontrunning_mev) |
| K-27 | High | The `borrow` and `refinance` functions can be front-run by the pool lender leading to collateral being seized in the next block | ✅ 64% | `refinance` (category frontrunning_mev) |
| M-1 | Medium | Precision loss allows users to giveLoans to pools with less collateral then required | ✅ 85% | `_calculateInterest` line 724 (detector integer_overflow) |
| M-2 | Medium | The `borrow` and `refinance` functions can be front-run by the pool lender to set high interest rates | ✅ 64% | `refinance` (category frontrunning_mev) |
| M-3 | Medium | If a borrower or lender got blacklisted by asset contract, their collateral or loan funds can be permanently frozen with the pool | ✅ 95% | `repay` line 317 (detector sol_basics_al_10) |
| M-4 | Medium | No expiration deadline leads to losing a lot of funds | ✅ 82% | `sellProfits` line 38 (detector front_running_patterns) |
| M-5 | Medium | Malicious lender can increment the loan interest using the auction process | ✅ 89% | `giveLoan` (category business_logic_state_machine) |
| M-6 | Medium | Single-step process for critical ownership transfer is risky | ✅ 98% | `transferOwnership` line 20 (detector sol_basics_ac_4) |
| M-7 | Medium | Lender contract can be drained by re-entrancy in `seizeLoan` | ✅ 90% | `seizeLoan` line 563 (detector solidity_security) |
| M-8 | Medium | Fixed fee level is used when swap tokens on Uniswap | ✅ 86% | `sellProfits` line 42 (category external_call_token_integration) |
| M-9 | Medium | Pragma non-specification can lead to non-functional / corrupted contract when deployed on Arbitrum | ❌ |  |
| M-10 | Medium | Frontrun can get the full reward, no staking time required | ✅ 60% | `claim` line 54 (detector sol_defi_general_8) |
| M-11 | Medium | Lender contract can be drained by re-entrancy in `refinance` (collateral) | ✅ 88% | `refinance` (detector solidity_security) |
| M-12 | Medium | Some ERC20 tokens would revert on zero value fee transfers. | ✅ 91% | `repay` line 317 (category external_call_token_integration) |
| M-13 | Medium | Rounding error leads to borrowing loans without paying interest | ✅ 85% | `_calculateInterest` line 724 (detector integer_overflow) |
| M-14 | Medium | Setting borrower fees to 0 permits the borrow functionality to be completely DoS | ✅ 77% | `repay` line 293 (category dos_griefing) |
| M-15 | Medium | The lack of a WETH-Profits Token pair upon calling sellProfits can expose it to malicious pool creation | ✅ 96% | `sellProfits` line 38 (detector sol_defi_as_11) |

### Flags without a known finding: 3 at 70%, 9 at 50%

A flag is a file whose chance for a category is at or over the threshold. These flags have no known finding of that category in that file: possibly unreported issues, or false positives. Not verified.

| File | Category | Chance |
|---|---|---|
| `src/Staking.sol` | Business logic, input validation, and state machine | 85% |
| `src/Staking.sol` | Access control and privilege | 72% |
| `src/Staking.sol` | Denial of service and griefing | 70% |

<details><summary>All 9 at 50%</summary>

| File | Category | Chance |
|---|---|---|
| `src/Staking.sol` | Business logic, input validation, and state machine | 85% |
| `src/Staking.sol` | Access control and privilege | 72% |
| `src/Staking.sol` | Denial of service and griefing | 70% |
| `src/Fees.sol` | Access control and privilege | 65% |
| `src/Staking.sol` | Reentrancy | 64% |
| `src/Fees.sol` | Business logic, input validation, and state machine | 62% |
| `src/Fees.sol` | Denial of service and griefing | 60% |
| `src/Staking.sol` | Arithmetic and precision | 58% |
| `src/Lender.sol` | Flash-loan and economic attacks | 53% |

</details>

## File details

<details><summary>src/Lender.sol · Crit 🟥 · Any 🟥 · Tokens 92%, Logic 89%, Math 80% · 16 functions flagged</summary>

| Function | Lines | Strongest hit | Question | Chance | Line | More |
|---|---|---|---|---|---|---|
| `repay` | 292-345 | Unsafe ERC-20 integration: raw transfer/approve calls and unchecked transfer amounts for non-standard tokens | detector token_integration_safety | 98% | 317 | <details><summary>26 more</summary>Unsafe ERC-20 token integration without SafeERC20 or received-amount accounting (detector erc20_patterns) 97%, line 317<br>Unsafe ERC20 transfer calls without return-value checks or SafeERC20 wrapper (detector sol_token_fe_1) 97%, line 317<br>Denial-of-service via unbounded loop with external calls that can revert entire operation (detector sol_basics_al_10) 95%, line 317<br>Business logic, input validation, and state machine (category business_logic_state_machine) 93%, line 296<br>Fee-on-transfer token accounting mismatch from assuming transferred amount equals received amount (detector sol_token_fe_6) 92%, line 312<br>External calls and token integration (category external_call_token_integration) 91%, line 317<br>Using delete on an array element to remove an item, leaving a stale/zero placeholder instead of shrinking the array (detector sol_basics_al_4) 90%, line 343<br>Missing uniqueness validation on user-supplied array allows duplicate entries to be processed (detector sol_basics_al_7) 90%, line 293<br>Denial-of-service from blacklistable tokens blocking required push transfers (detector sol_am_dosa_3) 89%, line 329<br>Payment logic vulnerable to receiver-triggered denial of service (blocked funds transfer) (detector sol_basics_payment_1) 86%, line 329<br>Calling token transfer/transferFrom with a zero amount without guarding, risking revert on tokens that reject zero-value transfers (detector sol_token_fe_10) 82%, line 323<br>Missing handling for blacklistable/blocking ERC20 tokens causing denial of service (detector sol_token_fe_12) 81%, line 329<br>Denial of service and griefing (category dos_griefing) 77%, line 293<br>Unchecked unsigned integer subtraction that can underflow and revert unexpectedly (detector sol_basics_math_8) 77%, line 314<br>Unsafe support for arbitrary/non-standard ERC20 tokens (fee-on-transfer, rebasing) without whitelisting (detector sol_defi_general_9) 77%, line 317<br>Accounting and share math (category accounting_share_math) 74%, line 312<br>Unbounded array/loop iteration causing out-of-gas denial of service (detector sol_basics_al_9) 73%, line 293<br>Reentrancy vulnerability from unguarded or misordered external calls before state updates (detector solidity_security) 73%, line 329<br>Reentrancy via ERC777 transfer hooks in token integrations lacking reentrancy protection (detector sol_token_fe_7) 72%, line 317<br>Reentrancy (category reentrancy) 67%, line 317<br>Lending protocol lacks a working liquidation mechanism for undercollateralized or defaulted loans (detector sol_defi_lending_2) 67%, line 292<br>Missing contract-existence check before low-level call/delegatecall, allowing silent success on non-existent targets (detector sol_ec_12) 63%, line 317<br>Arithmetic and precision (category arithmetic_precision) 62%, line 312<br>Paired state-changing functions (add/remove, deposit/withdraw) are asymmetric, leaving stale or incorrect state. (detector sol_heuristics_16) 57%, line 314<br>Unbounded loop over growing user-controlled array causing denial-of-service via block gas limit (detector denial_of_service) 56%, line 293<br>Reentrancy via state changes occurring after external call/interaction (detector sol_am_reentrancyattack_2) 52%, line 329</details> |
| `refinance` | 591-710 | Unsafe ERC-20 token integration without SafeERC20 or received-amount accounting | detector erc20_patterns | 97% |  | <details><summary>34 more</summary>Unsafe ERC-20 integration: raw transfer/approve calls and unchecked transfer amounts for non-standard tokens (detector token_integration_safety) 97%<br>Unsafe ERC20 transfer calls without return-value checks or SafeERC20 wrapper (detector sol_token_fe_1) 96%<br>Incorrect handling of ERC20 tokens with non-18 decimals causing miscalculation (detector sol_defi_general_1) 93%<br>Denial-of-service via unbounded loop with external calls that can revert entire operation (detector sol_basics_al_10) 90%<br>External calls and token integration (category external_call_token_integration) 89%<br>Business logic, input validation, and state machine (category business_logic_state_machine) 89%<br>Reentrancy vulnerability from unguarded or misordered external calls before state updates (detector solidity_security) 88%<br>Denial-of-service from blacklistable tokens blocking required push transfers (detector sol_am_dosa_3) 86%<br>Reentrancy (category reentrancy) 84%<br>Accounting and share math (category accounting_share_math) 84%<br>Fee-on-transfer token accounting mismatch from assuming transferred amount equals received amount (detector sol_token_fe_6) 84%<br>Calling token transfer/transferFrom with a zero amount without guarding, risking revert on tokens that reject zero-value transfers (detector sol_token_fe_10) 82%<br>Incorrect handling of differing ERC20 token decimals in calculations (detector sol_token_fe_3) 82%<br>Arithmetic and precision (category arithmetic_precision) 81%<br>Unhandled min/max boundary values causing incorrect or unsafe arithmetic results (detector sol_basics_math_12) 78%<br>Reentrancy via ERC777 transfer hooks in token integrations lacking reentrancy protection (detector sol_token_fe_7) 75%<br>Payment logic vulnerable to receiver-triggered denial of service (blocked funds transfer) (detector sol_basics_payment_1) 74%<br>Unsafe support for arbitrary/non-standard ERC20 tokens (fee-on-transfer, rebasing) without whitelisting (detector sol_defi_general_9) 74%<br>Reentrancy via state changes occurring after external call/interaction (detector sol_am_reentrancyattack_2) 72%<br>Cross-function/read-only reentrancy from external calls before state updates (detector sol_ec_1) 72%<br>Lending protocol lacks a working liquidation mechanism for undercollateralized or defaulted loans (detector sol_defi_lending_2) 70%<br>Denial of service and griefing (category dos_griefing) 69%<br>Unchecked unsigned integer subtraction that can underflow and revert unexpectedly (detector sol_basics_math_8) 69%<br>Missing uniqueness validation on user-supplied array allows duplicate entries to be processed (detector sol_basics_al_7) 67%<br>LTV/health-factor calculation omits accrued interest, causing incorrect credit/liquidation assessment (detector sol_defi_lending_8) 66%<br>Reentrancy vulnerability from external call before state update in Solidity contracts (detector reentrancy_patterns) 65%<br>Missing handling for blacklistable/blocking ERC20 tokens causing denial of service (detector sol_token_fe_12) 65%<br>Front-running, MEV, and randomness (category frontrunning_mev) 64%<br>Paired state-changing functions (add/remove, deposit/withdraw) are asymmetric, leaving stale or incorrect state. (detector sol_heuristics_16) 64%<br>Rounding/fee inconsistency exploitable by splitting a financial operation into many small calls (detector sol_heuristics_17) 62%<br>Missing contract-existence check before low-level call/delegatecall, allowing silent success on non-existent targets (detector sol_ec_12) 59%<br>Unsafe unchecked arithmetic, silent truncation, or phantom overflow in Solidity integer math (detector integer_overflow) 58%<br>Missing front-running/sandwich-attack protection due to transaction-order-sensitive logic (detector sol_am_ma_3) 58%<br>Unbounded array/loop iteration causing out-of-gas denial of service (detector sol_basics_al_9) 57%</details> |
| `borrow` | 232-287 | Unsafe ERC-20 token integration without SafeERC20 or received-amount accounting | detector erc20_patterns | 97% | 271 | <details><summary>31 more</summary>Unsafe ERC-20 integration: raw transfer/approve calls and unchecked transfer amounts for non-standard tokens (detector token_integration_safety) 97%, line 267<br>Unsafe ERC20 transfer calls without return-value checks or SafeERC20 wrapper (detector sol_token_fe_1) 96%, line 267<br>Denial-of-service via unbounded loop with external calls that can revert entire operation (detector sol_basics_al_10) 91%, line 267<br>Incorrect handling of ERC20 tokens with non-18 decimals causing miscalculation (detector sol_defi_general_1) 91%, line 246<br>External calls and token integration (category external_call_token_integration) 89%, line 267<br>Incorrect handling of differing ERC20 token decimals in calculations (detector sol_token_fe_3) 86%, line 246<br>Fee-on-transfer token accounting mismatch from assuming transferred amount equals received amount (detector sol_token_fe_6) 86%, line 263<br>Denial-of-service from blacklistable tokens blocking required push transfers (detector sol_am_dosa_3) 84%, line 267<br>Business logic, input validation, and state machine (category business_logic_state_machine) 80%, line 262<br>Calling token transfer/transferFrom with a zero amount without guarding, risking revert on tokens that reject zero-value transfers (detector sol_token_fe_10) 79%, line 267<br>Missing uniqueness validation on user-supplied array allows duplicate entries to be processed (detector sol_basics_al_7) 75%, line 233<br>Rounding/fee inconsistency exploitable by splitting a financial operation into many small calls (detector sol_heuristics_17) 75%, line 265<br>Arithmetic and precision (category arithmetic_precision) 73%, line 246<br>Reentrancy (category reentrancy) 70%, line 267<br>Payment logic vulnerable to receiver-triggered denial of service (blocked funds transfer) (detector sol_basics_payment_1) 70%, line 267<br>Lending protocol lacks a working liquidation mechanism for undercollateralized or defaulted loans (detector sol_defi_lending_2) 70%, line 258<br>Paired state-changing functions (add/remove, deposit/withdraw) are asymmetric, leaving stale or incorrect state. (detector sol_heuristics_16) 68%, line 276<br>Missing handling for blacklistable/blocking ERC20 tokens causing denial of service (detector sol_token_fe_12) 68%, line 267<br>Unsafe unchecked arithmetic, silent truncation, or phantom overflow in Solidity integer math (detector integer_overflow) 67%, line 246<br>Reentrancy vulnerability from unguarded or misordered external calls before state updates (detector solidity_security) 67%, line 269<br>Reentrancy via ERC777 transfer hooks in token integrations lacking reentrancy protection (detector sol_token_fe_7) 64%, line 267<br>Accounting and share math (category accounting_share_math) 63%, line 262<br>Denial of service and griefing (category dos_griefing) 62%, line 267<br>Function vulnerable to front-running enabling DoS or value extraction by transaction ordering (detector sol_basics_function_3) 59%, line 243<br>Unhandled min/max boundary values causing incorrect or unsafe arithmetic results (detector sol_basics_math_12) 57%, line 246<br>Unbounded array/loop iteration causing out-of-gas denial of service (detector sol_basics_al_9) 56%, line 233<br>Unsafe support for arbitrary/non-standard ERC20 tokens (fee-on-transfer, rebasing) without whitelisting (detector sol_defi_general_9) 56%, line 271<br>LTV/health-factor calculation omits accrued interest, causing incorrect credit/liquidation assessment (detector sol_defi_lending_8) 56%, line 246<br>Missing contract-existence check before low-level call/delegatecall, allowing silent success on non-existent targets (detector sol_ec_12) 56%, line 267<br>Reentrancy via state changes occurring after external call/interaction (detector sol_am_reentrancyattack_2) 53%, line 267<br>Missing front-running/sandwich-attack protection due to transaction-order-sensitive logic (detector sol_am_ma_3) 51%, line 243</details> |
| `seizeLoan` | 548-586 | Unsafe ERC-20 integration: raw transfer/approve calls and unchecked transfer amounts for non-standard tokens | detector token_integration_safety | 97% | 563 | <details><summary>30 more</summary>Unsafe ERC-20 token integration without SafeERC20 or received-amount accounting (detector erc20_patterns) 96%, line 563<br>Unsafe ERC20 transfer calls without return-value checks or SafeERC20 wrapper (detector sol_token_fe_1) 96%, line 563<br>Denial-of-service via unbounded loop with external calls that can revert entire operation (detector sol_basics_al_10) 94%, line 563<br>Denial-of-service from blacklistable tokens blocking required push transfers (detector sol_am_dosa_3) 93%, line 565<br>External calls and token integration (category external_call_token_integration) 90%, line 563<br>Payment logic vulnerable to receiver-triggered denial of service (blocked funds transfer) (detector sol_basics_payment_1) 90%, line 565<br>Reentrancy vulnerability from unguarded or misordered external calls before state updates (detector solidity_security) 90%, line 563<br>Business logic, input validation, and state machine (category business_logic_state_machine) 89%, line 575<br>Calling token transfer/transferFrom with a zero amount without guarding, risking revert on tokens that reject zero-value transfers (detector sol_token_fe_10) 89%, line 563<br>Missing handling for blacklistable/blocking ERC20 tokens causing denial of service (detector sol_token_fe_12) 88%, line 565<br>Reentrancy via state changes occurring after external call/interaction (detector sol_am_reentrancyattack_2) 87%, line 565<br>Using delete on an array element to remove an item, leaving a stale/zero placeholder instead of shrinking the array (detector sol_basics_al_4) 87%, line 584<br>Cross-function/read-only reentrancy from external calls before state updates (detector sol_ec_1) 85%, line 563<br>Denial of service and griefing (category dos_griefing) 84%, line 549<br>Reentrancy (category reentrancy) 82%, line 563<br>Reentrancy via ERC777 transfer hooks in token integrations lacking reentrancy protection (detector sol_token_fe_7) 82%, line 563<br>Missing uniqueness validation on user-supplied array allows duplicate entries to be processed (detector sol_basics_al_7) 77%, line 549<br>Unbounded array/loop iteration causing out-of-gas denial of service (detector sol_basics_al_9) 75%, line 549<br>Unchecked unsigned integer subtraction that can underflow and revert unexpectedly (detector sol_basics_math_8) 72%, line 575<br>Arithmetic and precision (category arithmetic_precision) 69%, line 561<br>Reentrancy vulnerability from external call before state update in Solidity contracts (detector reentrancy_patterns) 69%, line 563<br>Accounting and share math (category accounting_share_math) 64%, line 575<br>Rounding/fee inconsistency exploitable by splitting a financial operation into many small calls (detector sol_heuristics_17) 64%, line 561<br>Unbounded loop over growing user-controlled array causing denial-of-service via block gas limit (detector denial_of_service) 62%, line 549<br>Unsafe unchecked arithmetic, silent truncation, or phantom overflow in Solidity integer math (detector integer_overflow) 58%, line 561<br>Unhandled min/max boundary values causing incorrect or unsafe arithmetic results (detector sol_basics_math_12) 56%, line 561<br>Paired state-changing functions (add/remove, deposit/withdraw) are asymmetric, leaving stale or incorrect state. (detector sol_heuristics_16) 56%, line 575<br>Unsafe support for arbitrary/non-standard ERC20 tokens (fee-on-transfer, rebasing) without whitelisting (detector sol_defi_general_9) 54%, line 563<br>Missing contract-existence check before low-level call/delegatecall, allowing silent success on non-existent targets (detector sol_ec_12) 52%, line 563<br>Unsafe reliance on block.timestamp for time-sensitive/critical logic (detector sol_am_ma_1) 51%, line 557</details> |
| `addToPool` | 182-192 | Unsafe ERC-20 integration: raw transfer/approve calls and unchecked transfer amounts for non-standard tokens | detector token_integration_safety | 97% | 187 | <details><summary>12 more</summary>Unsafe ERC-20 token integration without SafeERC20 or received-amount accounting (detector erc20_patterns) 95%, line 187<br>Unsafe ERC20 transfer calls without return-value checks or SafeERC20 wrapper (detector sol_token_fe_1) 94%, line 187<br>Fee-on-transfer token accounting mismatch from assuming transferred amount equals received amount (detector sol_token_fe_6) 94%, line 185<br>External calls and token integration (category external_call_token_integration) 77%, line 187<br>Paired state-changing functions (add/remove, deposit/withdraw) are asymmetric, leaving stale or incorrect state. (detector sol_heuristics_16) 74%, line 185<br>Business logic, input validation, and state machine (category business_logic_state_machine) 67%, line 183<br>Reentrancy vulnerability from unguarded or misordered external calls before state updates (detector solidity_security) 62%, line 187<br>AMM/pool fails to handle rebasing tokens, causing balance accounting mismatches (detector sol_defi_as_10) 59%, line 185<br>Missing contract-existence check before low-level call/delegatecall, allowing silent success on non-existent targets (detector sol_ec_12) 52%, line 187<br>Accounting and share math (category accounting_share_math) 51%, line 185<br>Reentrancy (category reentrancy) 50%, line 187<br>Reentrancy via ERC777 transfer hooks in token integrations lacking reentrancy protection (detector sol_token_fe_7) 50%, line 187</details> |
| `setPool` | 130-176 | Unsafe ERC-20 token integration without SafeERC20 or received-amount accounting | detector erc20_patterns | 96% | 152 | <details><summary>15 more</summary>Unsafe ERC20 transfer calls without return-value checks or SafeERC20 wrapper (detector sol_token_fe_1) 96%, line 152<br>Unsafe ERC-20 integration: raw transfer/approve calls and unchecked transfer amounts for non-standard tokens (detector token_integration_safety) 96%, line 152<br>Fee-on-transfer token accounting mismatch from assuming transferred amount equals received amount (detector sol_token_fe_6) 91%, line 175<br>External calls and token integration (category external_call_token_integration) 88%, line 152<br>Reentrancy vulnerability from unguarded or misordered external calls before state updates (detector solidity_security) 83%, line 152<br>Unsafe support for arbitrary/non-standard ERC20 tokens (fee-on-transfer, rebasing) without whitelisting (detector sol_defi_general_9) 82%, line 152<br>Business logic, input validation, and state machine (category business_logic_state_machine) 81%, line 175<br>Reentrancy via ERC777 transfer hooks in token integrations lacking reentrancy protection (detector sol_token_fe_7) 81%, line 152<br>Reentrancy (category reentrancy) 79%, line 152<br>Missing contract-existence check before low-level call/delegatecall, allowing silent success on non-existent targets (detector sol_ec_12) 70%, line 152<br>Cross-function/read-only reentrancy from external calls before state updates (detector sol_ec_1) 66%, line 152<br>Reentrancy via state changes occurring after external call/interaction (detector sol_am_reentrancyattack_2) 64%, line 159<br>Denial of service and griefing (category dos_griefing) 59%, line 159<br>Reentrancy vulnerability from external call before state update in Solidity contracts (detector reentrancy_patterns) 56%, line 152<br>Accounting and share math (category accounting_share_math) 52%, line 175</details> |
| `removeFromPool` | 198-204 | Unsafe ERC-20 integration: raw transfer/approve calls and unchecked transfer amounts for non-standard tokens | detector token_integration_safety | 96% | 203 | <details><summary>9 more</summary>Unsafe ERC-20 token integration without SafeERC20 or received-amount accounting (detector erc20_patterns) 95%, line 203<br>Unsafe ERC20 transfer calls without return-value checks or SafeERC20 wrapper (detector sol_token_fe_1) 95%, line 203<br>Unchecked unsigned integer subtraction that can underflow and revert unexpectedly (detector sol_basics_math_8) 90%, line 201<br>External calls and token integration (category external_call_token_integration) 83%, line 203<br>Business logic, input validation, and state machine (category business_logic_state_machine) 78%, line 201<br>Denial of service and griefing (category dos_griefing) 64%, line 203<br>Accounting and share math (category accounting_share_math) 57%, line 201<br>Fee-on-transfer token accounting mismatch from assuming transferred amount equals received amount (detector sol_token_fe_6) 56%, line 201<br>AMM/pool fails to handle rebasing tokens, causing balance accounting mismatches (detector sol_defi_as_10) 51%, line 201</details> |
| `giveLoan` | 355-432 | Unsafe ERC-20 integration: raw transfer/approve calls and unchecked transfer amounts for non-standard tokens | detector token_integration_safety | 95% |  | <details><summary>30 more</summary>Unsafe ERC-20 token integration without SafeERC20 or received-amount accounting (detector erc20_patterns) 94%<br>Unsafe ERC20 transfer calls without return-value checks or SafeERC20 wrapper (detector sol_token_fe_1) 94%<br>Denial-of-service from blacklistable tokens blocking required push transfers (detector sol_am_dosa_3) 91%<br>Incorrect handling of ERC20 tokens with non-18 decimals causing miscalculation (detector sol_defi_general_1) 91%<br>Denial-of-service via unbounded loop with external calls that can revert entire operation (detector sol_basics_al_10) 90%<br>Business logic, input validation, and state machine (category business_logic_state_machine) 89%<br>External calls and token integration (category external_call_token_integration) 88%<br>Calling token transfer/transferFrom with a zero amount without guarding, risking revert on tokens that reject zero-value transfers (detector sol_token_fe_10) 84%<br>Missing uniqueness validation on user-supplied array allows duplicate entries to be processed (detector sol_basics_al_7) 79%<br>Accounting and share math (category accounting_share_math) 78%<br>Arithmetic and precision (category arithmetic_precision) 78%<br>Unhandled min/max boundary values causing incorrect or unsafe arithmetic results (detector sol_basics_math_12) 72%<br>Incorrect handling of differing ERC20 token decimals in calculations (detector sol_token_fe_3) 71%<br>Missing handling for blacklistable/blocking ERC20 tokens causing denial of service (detector sol_token_fe_12) 70%<br>Unbounded array/loop iteration causing out-of-gas denial of service (detector sol_basics_al_9) 68%<br>Reentrancy (category reentrancy) 66%<br>Denial of service and griefing (category dos_griefing) 66%<br>Reentrancy via state changes occurring after external call/interaction (detector sol_am_reentrancyattack_2) 66%<br>Payment logic vulnerable to receiver-triggered denial of service (blocked funds transfer) (detector sol_basics_payment_1) 66%<br>Unsafe unchecked arithmetic, silent truncation, or phantom overflow in Solidity integer math (detector integer_overflow) 62%<br>Fee-on-transfer token accounting mismatch from assuming transferred amount equals received amount (detector sol_token_fe_6) 62%<br>Missing front-running/sandwich-attack protection due to transaction-order-sensitive logic (detector sol_am_ma_3) 58%<br>Lending protocol lacks a working liquidation mechanism for undercollateralized or defaulted loans (detector sol_defi_lending_2) 58%<br>Paired state-changing functions (add/remove, deposit/withdraw) are asymmetric, leaving stale or incorrect state. (detector sol_heuristics_16) 58%<br>Front-running, MEV, and randomness (category frontrunning_mev) 56%<br>Function vulnerable to front-running enabling DoS or value extraction by transaction ordering (detector sol_basics_function_3) 56%<br>Reentrancy via ERC777 transfer hooks in token integrations lacking reentrancy protection (detector sol_token_fe_7) 56%<br>Reentrancy vulnerability from unguarded or misordered external calls before state updates (detector solidity_security) 53%<br>Unsafe support for arbitrary/non-standard ERC20 tokens (fee-on-transfer, rebasing) without whitelisting (detector sol_defi_general_9) 52%<br>Missing contract-existence check before low-level call/delegatecall, allowing silent success on non-existent targets (detector sol_ec_12) 51%</details> |
| `buyLoan` | 465-534 | Unsafe ERC-20 token integration without SafeERC20 or received-amount accounting | detector erc20_patterns | 95% | 505 | <details><summary>24 more</summary>Unsafe ERC20 transfer calls without return-value checks or SafeERC20 wrapper (detector sol_token_fe_1) 95%, line 505<br>Unsafe ERC-20 integration: raw transfer/approve calls and unchecked transfer amounts for non-standard tokens (detector token_integration_safety) 95%, line 505<br>Denial-of-service from blacklistable tokens blocking required push transfers (detector sol_am_dosa_3) 91%, line 505<br>Business logic, input validation, and state machine (category business_logic_state_machine) 88%, line 478<br>External calls and token integration (category external_call_token_integration) 87%, line 505<br>Calling token transfer/transferFrom with a zero amount without guarding, risking revert on tokens that reject zero-value transfers (detector sol_token_fe_10) 84%, line 505<br>Missing front-running/sandwich-attack protection due to transaction-order-sensitive logic (detector sol_am_ma_3) 74%, line 475<br>Function vulnerable to front-running enabling DoS or value extraction by transaction ordering (detector sol_basics_function_3) 73%, line 475<br>Accounting and share math (category accounting_share_math) 71%, line 502<br>Arithmetic and precision (category arithmetic_precision) 69%, line 475<br>Front-running, MEV, and randomness (category frontrunning_mev) 69%, line 478<br>Denial of service and griefing (category dos_griefing) 65%, line 505<br>Unsafe unchecked arithmetic, silent truncation, or phantom overflow in Solidity integer math (detector integer_overflow) 65%, line 475<br>Reentrancy via state changes occurring after external call/interaction (detector sol_am_reentrancyattack_2) 65%, line 505<br>Reentrancy (category reentrancy) 64%, line 505<br>Unhandled min/max boundary values causing incorrect or unsafe arithmetic results (detector sol_basics_math_12) 62%, line 475<br>Unsafe reliance on block.timestamp for time-sensitive/critical logic (detector sol_am_ma_1) 61%, line 471<br>Paired state-changing functions (add/remove, deposit/withdraw) are asymmetric, leaving stale or incorrect state. (detector sol_heuristics_16) 60%, line 490<br>Fee-on-transfer token accounting mismatch from assuming transferred amount equals received amount (detector sol_token_fe_6) 60%, line 505<br>Payment logic vulnerable to receiver-triggered denial of service (blocked funds transfer) (detector sol_basics_payment_1) 59%, line 505<br>Lending protocol lacks a working liquidation mechanism for undercollateralized or defaulted loans (detector sol_defi_lending_2) 58%, line 465<br>Unsafe support for arbitrary/non-standard ERC20 tokens (fee-on-transfer, rebasing) without whitelisting (detector sol_defi_general_9) 56%, line 505<br>Missing handling for blacklistable/blocking ERC20 tokens causing denial of service (detector sol_token_fe_12) 55%, line 505<br>Missing contract-existence check before low-level call/delegatecall, allowing silent success on non-existent targets (detector sol_ec_12) 52%, line 505</details> |
| `_calculateInterest` | 720-727 | Unsafe unchecked arithmetic, silent truncation, or phantom overflow in Solidity integer math | detector integer_overflow | 85% | 724 | <details><summary>4 more</summary>Unhandled min/max boundary values causing incorrect or unsafe arithmetic results (detector sol_basics_math_12) 77%, line 724<br>Unchecked unsigned integer subtraction that can underflow and revert unexpectedly (detector sol_basics_math_8) 74%, line 726<br>Arithmetic and precision (category arithmetic_precision) 71%, line 724<br>Accounting and share math (category accounting_share_math) 51%, line 724</details> |
| `startAuction` | 437-459 | Business logic, input validation, and state machine | category business_logic_state_machine | 82% | 448 | <details><summary>6 more</summary>Unbounded array/loop iteration causing out-of-gas denial of service (detector sol_basics_al_9) 70%, line 438<br>Denial of service and griefing (category dos_griefing) 61%, line 438<br>Missing uniqueness validation on user-supplied array allows duplicate entries to be processed (detector sol_basics_al_7) 57%, line 448<br>Lending protocol lacks a working liquidation mechanism for undercollateralized or defaulted loans (detector sol_defi_lending_2) 56%, line 443<br>Denial-of-service via unbounded loop with external calls that can revert entire operation (detector sol_basics_al_10) 53%, line 438<br>Paired state-changing functions (add/remove, deposit/withdraw) are asymmetric, leaving stale or incorrect state. (detector sol_heuristics_16) 53%, line 448</details> |
| `zapBuyLoan` | 540-543 | Missing front-running/sandwich-attack protection due to transaction-order-sensitive logic | detector sol_am_ma_3 | 69% | 542 | <details><summary>3 more</summary>Business logic, input validation, and state machine (category business_logic_state_machine) 67%, line 542<br>Function vulnerable to front-running enabling DoS or value extraction by transaction ordering (detector sol_basics_function_3) 63%, line 542<br>Front-running, MEV, and randomness (category frontrunning_mev) 51%, line 542</details> |
| `updateMaxLoanRatio` | 210-215 | Business logic, input validation, and state machine | category business_logic_state_machine | 67% | 213 |  |
| `_updatePoolBalance` | 732-735 | Business logic, input validation, and state machine | category business_logic_state_machine | 54% | 733 |  |
| `updateInterestRate` | 221-226 | Business logic, input validation, and state machine | category business_logic_state_machine | 53% | 224 |  |
| `constructor` | 73-75 | Lending protocol lacks a working liquidation mechanism for undercollateralized or defaulted loans | detector sol_defi_lending_2 | 52% | 73 |  |

<details><summary>File-level hits (44)</summary>

| Chance | Question | What it asks |
|---|---|---|
| 98% | detector erc20_patterns | Unsafe ERC-20 token integration without SafeERC20 or received-amount accounting |
| 98% | detector token_integration_safety | Unsafe ERC-20 integration: raw transfer/approve calls and unchecked transfer amounts for non-standard tokens |
| 96% | detector sol_token_fe_1 | Unsafe ERC20 transfer calls without return-value checks or SafeERC20 wrapper |
| 92% | category external_call_token_integration | External calls and token integration |
| 91% | detector sol_defi_general_9 | Unsafe support for arbitrary/non-standard ERC20 tokens (fee-on-transfer, rebasing) without whitelisting |
| 91% | detector sol_token_fe_6 | Fee-on-transfer token accounting mismatch from assuming transferred amount equals received amount |
| 89% | category business_logic_state_machine | Business logic, input validation, and state machine |
| 88% | detector sol_basics_al_4 | Using delete on an array element to remove an item, leaving a stale/zero placeholder instead of shrinking the array |
| 86% | detector sol_am_dosa_3 | Denial-of-service from blacklistable tokens blocking required push transfers |
| 86% | detector sol_basics_al_10 | Denial-of-service via unbounded loop with external calls that can revert entire operation |
| 83% | detector sol_basics_payment_1 | Payment logic vulnerable to receiver-triggered denial of service (blocked funds transfer) |
| 83% | detector sol_defi_general_1 | Incorrect handling of ERC20 tokens with non-18 decimals causing miscalculation |
| 82% | detector sol_basics_al_9 | Unbounded array/loop iteration causing out-of-gas denial of service |
| 82% | detector solidity_security | Reentrancy vulnerability from unguarded or misordered external calls before state updates |
| 80% | category arithmetic_precision | Arithmetic and precision |
| 79% | category accounting_share_math | Accounting and share math |
| 79% | detector sol_ec_12 | Missing contract-existence check before low-level call/delegatecall, allowing silent success on non-existent targets |
| 79% | detector sol_token_fe_3 | Incorrect handling of differing ERC20 token decimals in calculations |
| 78% | category dos_griefing | Denial of service and griefing |
| 78% | detector sol_token_fe_10 | Calling token transfer/transferFrom with a zero amount without guarding, risking revert on tokens that reject zero-value transfers |
| 75% | detector sol_basics_al_7 | Missing uniqueness validation on user-supplied array allows duplicate entries to be processed |
| 74% | category frontrunning_mev | Front-running, MEV, and randomness |
| 74% | detector integer_overflow | Unsafe unchecked arithmetic, silent truncation, or phantom overflow in Solidity integer math |
| 73% | detector sol_am_ma_3 | Missing front-running/sandwich-attack protection due to transaction-order-sensitive logic |
| 73% | detector sol_token_fe_12 | Missing handling for blacklistable/blocking ERC20 tokens causing denial of service |
| 73% | detector sol_token_fe_7 | Reentrancy via ERC777 transfer hooks in token integrations lacking reentrancy protection |
| 72% | detector sol_basics_function_3 | Function vulnerable to front-running enabling DoS or value extraction by transaction ordering |
| 72% | detector sol_basics_math_12 | Unhandled min/max boundary values causing incorrect or unsafe arithmetic results |
| 70% | category reentrancy | Reentrancy |
| 68% | detector sol_basics_math_4 | Precision loss from performing division before multiplication in arithmetic expressions |
| 66% | detector sol_am_reentrancyattack_2 | Reentrancy via state changes occurring after external call/interaction |
| 65% | detector sol_basics_math_8 | Unchecked unsigned integer subtraction that can underflow and revert unexpectedly |
| 60% | detector sol_defi_lending_10 | Same-token lend and borrow allowed in one transaction, enabling flash-loan price manipulation |
| 60% | detector sol_defi_lending_2 | Lending protocol lacks a working liquidation mechanism for undercollateralized or defaulted loans |
| 60% | detector sol_heuristics_17 | Rounding/fee inconsistency exploitable by splitting a financial operation into many small calls |
| 58% | detector sol_defi_as_10 | AMM/pool fails to handle rebasing tokens, causing balance accounting mismatches |
| 58% | detector sol_ec_1 | Cross-function/read-only reentrancy from external calls before state updates |
| 57% | detector sol_defi_lending_8 | LTV/health-factor calculation omits accrued interest, causing incorrect credit/liquidation assessment |
| 54% | detector denial_of_service | Unbounded loop over growing user-controlled array causing denial-of-service via block gas limit |
| 53% | category flash_loan_economic | Flash-loan and economic attacks |
| 53% | detector sol_am_ma_1 | Unsafe reliance on block.timestamp for time-sensitive/critical logic |
| 51% | detector reentrancy_patterns | Reentrancy vulnerability from external call before state update in Solidity contracts |
| 50% | detector sol_am_fra_2 | Two-step actions vulnerable to front-running/interception between the two transactions |
| 50% | detector sol_heuristics_16 | Paired state-changing functions (add/remove, deposit/withdraw) are asymmetric, leaving stale or incorrect state. |

</details>


</details>

<details><summary>src/Staking.sol · Crit 🟧 · Any 🟥 · Tokens 89%, Logic 85%, Access 72% · 6 functions flagged</summary>

| Function | Lines | Strongest hit | Question | Chance | Line | More |
|---|---|---|---|---|---|---|
| `withdraw` | 46-50 | Unsafe ERC-20 integration: raw transfer/approve calls and unchecked transfer amounts for non-standard tokens | detector token_integration_safety | 97% | 49 | <details><summary>16 more</summary>Unsafe ERC-20 token integration without SafeERC20 or received-amount accounting (detector erc20_patterns) 96%, line 49<br>Unsafe ERC20 transfer calls without return-value checks or SafeERC20 wrapper (detector sol_token_fe_1) 95%, line 49<br>Business logic, input validation, and state machine (category business_logic_state_machine) 87%, line 48<br>Unchecked unsigned integer subtraction that can underflow and revert unexpectedly (detector sol_basics_math_8) 87%, line 48<br>External calls and token integration (category external_call_token_integration) 84%, line 49<br>Missing minimum deposit/withdrawal threshold enabling dust-amount rounding or DoS exploits (detector sol_basics_payment_4) 82%, line 46<br>Calling token transfer/transferFrom with a zero amount without guarding, risking revert on tokens that reject zero-value transfers (detector sol_token_fe_10) 82%, line 49<br>Missing minimum transaction/amount check enabling dust-transaction denial-of-service or griefing (detector sol_am_dosa_2) 80%, line 46<br>Access control and privilege (category access_control) 78%, line 46<br>Denial of service and griefing (category dos_griefing) 73%, line 49<br>Fee-on-transfer token accounting mismatch from assuming transferred amount equals received amount (detector sol_token_fe_6) 73%, line 48<br>Missing access control on privileged/critical functions (detector access_control_patterns) 72%, line 46<br>Accounting and share math (category accounting_share_math) 69%, line 48<br>Same-block deposit-then-withdraw enabling flashloan deposit-harvest-withdraw exploits (detector sol_defi_general_8) 67%, line 49<br>Reentrancy (category reentrancy) 57%, line 49<br>Missing access control on sensitive state-changing function (detector sol_basics_function_9) 54%, line 49</details> |
| `deposit` | 38-42 | Unsafe ERC-20 token integration without SafeERC20 or received-amount accounting | detector erc20_patterns | 97% | 39 | <details><summary>13 more</summary>Unsafe ERC-20 integration: raw transfer/approve calls and unchecked transfer amounts for non-standard tokens (detector token_integration_safety) 97%, line 39<br>Fee-on-transfer token accounting mismatch from assuming transferred amount equals received amount (detector sol_token_fe_6) 95%, line 41<br>Unsafe ERC20 transfer calls without return-value checks or SafeERC20 wrapper (detector sol_token_fe_1) 94%, line 39<br>Missing minimum transaction/amount check enabling dust-transaction denial-of-service or griefing (detector sol_am_dosa_2) 91%, line 38<br>Reentrancy vulnerability from unguarded or misordered external calls before state updates (detector solidity_security) 86%, line 39<br>Calling token transfer/transferFrom with a zero amount without guarding, risking revert on tokens that reject zero-value transfers (detector sol_token_fe_10) 85%, line 39<br>Missing minimum deposit/withdrawal threshold enabling dust-amount rounding or DoS exploits (detector sol_basics_payment_4) 84%, line 41<br>External calls and token integration (category external_call_token_integration) 83%, line 39<br>Reentrancy (category reentrancy) 81%, line 39<br>Cross-function/read-only reentrancy from external calls before state updates (detector sol_ec_1) 77%, line 39<br>Business logic, input validation, and state machine (category business_logic_state_machine) 69%, line 41<br>Accounting and share math (category accounting_share_math) 59%, line 41<br>Same-block deposit-then-withdraw enabling flashloan deposit-harvest-withdraw exploits (detector sol_defi_general_8) 57%, line 40</details> |
| `claim` | 53-58 | Unsafe ERC-20 integration: raw transfer/approve calls and unchecked transfer amounts for non-standard tokens | detector token_integration_safety | 95% | 55 | <details><summary>17 more</summary>Unsafe ERC-20 token integration without SafeERC20 or received-amount accounting (detector erc20_patterns) 94%, line 55<br>Unsafe ERC20 transfer calls without return-value checks or SafeERC20 wrapper (detector sol_token_fe_1) 93%, line 55<br>Calling token transfer/transferFrom with a zero amount without guarding, risking revert on tokens that reject zero-value transfers (detector sol_token_fe_10) 92%, line 55<br>Reentrancy vulnerability from unguarded or misordered external calls before state updates (detector solidity_security) 85%, line 55<br>External calls and token integration (category external_call_token_integration) 83%, line 55<br>Missing access control on privileged/critical functions (detector access_control_patterns) 77%, line 55<br>Access control and privilege (category access_control) 75%, line 53<br>Reentrancy via state changes occurring after external call/interaction (detector sol_am_reentrancyattack_2) 73%, line 55<br>Business logic, input validation, and state machine (category business_logic_state_machine) 72%, line 55<br>Reentrancy (category reentrancy) 71%, line 55<br>Denial of service and griefing (category dos_griefing) 70%, line 55<br>Accounting and share math (category accounting_share_math) 69%, line 57<br>Missing time controls allow staking reward distribution to be delayed or claimed prematurely (detector sol_defi_staking_2) 65%, line 54<br>Reentrancy vulnerability from external call before state update in Solidity contracts (detector reentrancy_patterns) 61%, line 55<br>Same-block deposit-then-withdraw enabling flashloan deposit-harvest-withdraw exploits (detector sol_defi_general_8) 60%, line 54<br>Missing access control on sensitive state-changing function (detector sol_basics_function_9) 53%, line 55<br>Cross-function/read-only reentrancy from external calls before state updates (detector sol_ec_1) 52%, line 55</details> |
| `update` | 61-76 | Incorrect handling of ERC20 tokens with non-18 decimals causing miscalculation | detector sol_defi_general_1 | 91% | 68 | <details><summary>10 more</summary>Accounting relies on token/ETH balanceOf instead of internal ledger, enabling donation-based manipulation (detector sol_defi_general_3) 86%, line 64<br>Incorrect handling of differing ERC20 token decimals in calculations (detector sol_token_fe_3) 86%, line 68<br>Missing access control on sensitive state-changing function (detector sol_basics_function_9) 67%, line 61<br>Missing time controls allow staking reward distribution to be delayed or claimed prematurely (detector sol_defi_staking_2) 67%, line 61<br>Donation/balance-manipulation attack via reliance on token.balanceOf instead of internal accounting (detector sol_am_da_1) 65%, line 62<br>Access control and privilege (category access_control) 63%, line 61<br>Accounting and share math (category accounting_share_math) 62%, line 70<br>Business logic, input validation, and state machine (category business_logic_state_machine) 60%, line 70<br>Unsafe unchecked arithmetic, silent truncation, or phantom overflow in Solidity integer math (detector integer_overflow) 56%, line 68<br>Arithmetic and precision (category arithmetic_precision) 50%, line 68</details> |
| `updateFor` | 80-94 | Incorrect handling of ERC20 tokens with non-18 decimals causing miscalculation | detector sol_defi_general_1 | 91% | 88 | <details><summary>10 more</summary>Unsafe unchecked arithmetic, silent truncation, or phantom overflow in Solidity integer math (detector integer_overflow) 79%, line 88<br>Incorrect handling of differing ERC20 token decimals in calculations (detector sol_token_fe_3) 70%, line 88<br>Missing time controls allow staking reward distribution to be delayed or claimed prematurely (detector sol_defi_staking_2) 65%, line 81<br>Missing access control on sensitive state-changing function (detector sol_basics_function_9) 64%, line 80<br>Business logic, input validation, and state machine (category business_logic_state_machine) 60%, line 88<br>Arithmetic and precision (category arithmetic_precision) 57%, line 88<br>Accounting and share math (category accounting_share_math) 56%, line 85<br>Same-block deposit-then-withdraw enabling flashloan deposit-harvest-withdraw exploits (detector sol_defi_general_8) 56%, line 89<br>Access control and privilege (category access_control) 53%, line 80<br>Unhandled min/max boundary values causing incorrect or unsafe arithmetic results (detector sol_basics_math_12) 51%, line 88</details> |
| `constructor` | 31-34 | Business logic, input validation, and state machine | category business_logic_state_machine | 50% | 32 |  |

<details><summary>File-level hits (35)</summary>

| Chance | Question | What it asks |
|---|---|---|
| 98% | detector token_integration_safety | Unsafe ERC-20 integration: raw transfer/approve calls and unchecked transfer amounts for non-standard tokens |
| 97% | detector erc20_patterns | Unsafe ERC-20 token integration without SafeERC20 or received-amount accounting |
| 96% | detector sol_token_fe_1 | Unsafe ERC20 transfer calls without return-value checks or SafeERC20 wrapper |
| 96% | detector sol_token_fe_6 | Fee-on-transfer token accounting mismatch from assuming transferred amount equals received amount |
| 92% | detector sol_basics_math_8 | Unchecked unsigned integer subtraction that can underflow and revert unexpectedly |
| 90% | detector sol_am_dosa_2 | Missing minimum transaction/amount check enabling dust-transaction denial-of-service or griefing |
| 90% | detector sol_defi_general_1 | Incorrect handling of ERC20 tokens with non-18 decimals causing miscalculation |
| 89% | category external_call_token_integration | External calls and token integration |
| 87% | detector solidity_security | Reentrancy vulnerability from unguarded or misordered external calls before state updates |
| 85% | category business_logic_state_machine | Business logic, input validation, and state machine |
| 85% | detector sol_basics_payment_4 | Missing minimum deposit/withdrawal threshold enabling dust-amount rounding or DoS exploits |
| 82% | detector sol_defi_general_8 | Same-block deposit-then-withdraw enabling flashloan deposit-harvest-withdraw exploits |
| 82% | detector sol_token_fe_3 | Incorrect handling of differing ERC20 token decimals in calculations |
| 79% | detector sol_token_fe_10 | Calling token transfer/transferFrom with a zero amount without guarding, risking revert on tokens that reject zero-value transfers |
| 78% | detector sol_defi_flashloan_1 | Missing same-block withdrawal restriction enabling flashloan-based deposit/withdraw exploits |
| 74% | detector sol_token_fe_7 | Reentrancy via ERC777 transfer hooks in token integrations lacking reentrancy protection |
| 72% | category access_control | Access control and privilege |
| 70% | category dos_griefing | Denial of service and griefing |
| 67% | detector sol_am_ma_3 | Missing front-running/sandwich-attack protection due to transaction-order-sensitive logic |
| 66% | detector sol_basics_payment_1 | Payment logic vulnerable to receiver-triggered denial of service (blocked funds transfer) |
| 66% | detector sol_defi_general_3 | Accounting relies on token/ETH balanceOf instead of internal ledger, enabling donation-based manipulation |
| 66% | detector sol_defi_staking_2 | Missing time controls allow staking reward distribution to be delayed or claimed prematurely |
| 64% | category reentrancy | Reentrancy |
| 64% | detector integer_overflow | Unsafe unchecked arithmetic, silent truncation, or phantom overflow in Solidity integer math |
| 63% | detector sol_ec_12 | Missing contract-existence check before low-level call/delegatecall, allowing silent success on non-existent targets |
| 62% | detector sol_am_reentrancyattack_2 | Reentrancy via state changes occurring after external call/interaction |
| 61% | detector access_control_patterns | Missing access control on privileged/critical functions |
| 60% | detector sol_defi_general_9 | Unsafe support for arbitrary/non-standard ERC20 tokens (fee-on-transfer, rebasing) without whitelisting |
| 59% | detector sol_basics_function_9 | Missing access control on sensitive state-changing function |
| 58% | category arithmetic_precision | Arithmetic and precision |
| 58% | detector sol_basics_math_12 | Unhandled min/max boundary values causing incorrect or unsafe arithmetic results |
| 58% | detector sol_ec_1 | Cross-function/read-only reentrancy from external calls before state updates |
| 57% | category accounting_share_math | Accounting and share math |
| 54% | detector reentrancy_patterns | Reentrancy vulnerability from external call before state update in Solidity contracts |
| 52% | detector sol_am_da_1 | Donation/balance-manipulation attack via reliance on token.balanceOf instead of internal accounting |

</details>


</details>

<details><summary>src/Fees.sol · Crit 🟧 · Any 🟥 · Tokens 78%, MEV 66%, Access 65% · 1 function flagged</summary>

| Function | Lines | Strongest hit | Question | Chance | Line | More |
|---|---|---|---|---|---|---|
| `sellProfits` | 26-44 | Hard-coded Uniswap V3 fee tier parameter in swap function | detector sol_integrations_uniswap_10 | 98% | 34 | <details><summary>21 more</summary>Missing minimum output amount check before AMM token swap, enabling sandwich/slippage attacks (detector sol_defi_as_11) 96%, line 38<br>Missing slippage protection in swap/trade functions allowing excessive price deviation losses (detector sol_defi_as_7) 90%, line 38<br>Denial-of-service from blacklistable tokens blocking required push transfers (detector sol_am_dosa_3) 88%, line 43<br>Unsafe ERC-20 integration: raw transfer/approve calls and unchecked transfer amounts for non-standard tokens (detector token_integration_safety) 88%, line 43<br>External calls and token integration (category external_call_token_integration) 86%, line 42<br>Calling token transfer/transferFrom with a zero amount without guarding, risking revert on tokens that reject zero-value transfers (detector sol_token_fe_10) 84%, line 43<br>Missing slippage protection allowing sandwich attacks on user trades/swaps (detector sol_am_sandwichattack_1) 83%, line 38<br>Missing access control on privileged/critical functions (detector access_control_patterns) 82%, line 43<br>Missing slippage/deadline protection on swaps enabling sandwich/front-running attacks (detector front_running_patterns) 82%, line 38<br>Front-running, MEV, and randomness (category frontrunning_mev) 81%, line 38<br>Missing access control on sensitive privileged functions (detector sol_basics_ac_2) 79%, line 43<br>Missing access control on sensitive state-changing function (detector sol_basics_function_9) 78%, line 26<br>Access control and privilege (category access_control) 77%, line 26<br>Business logic, input validation, and state machine (category business_logic_state_machine) 76%, line 38<br>Function vulnerable to front-running enabling DoS or value extraction by transaction ordering (detector sol_basics_function_3) 73%, line 38<br>Denial of service and griefing (category dos_griefing) 66%, line 43<br>Unsafe ERC-20 token integration without SafeERC20 or received-amount accounting (detector erc20_patterns) 64%, line 43<br>Missing front-running/sandwich-attack protection due to transaction-order-sensitive logic (detector sol_am_ma_3) 59%, line 38<br>Unsafe ERC20 transfer calls without return-value checks or SafeERC20 wrapper (detector sol_token_fe_1) 59%, line 43<br>Reentrancy vulnerability from unguarded or misordered external calls before state updates (detector solidity_security) 58%, line 43<br>Flash-loan-exploitable use of manipulable spot price/balance/voting power within a single transaction (detector flash_loan_attacks) 57%, line 38</details> |

<details><summary>File-level hits (23)</summary>

| Chance | Question | What it asks |
|---|---|---|
| 97% | detector sol_integrations_uniswap_10 | Hard-coded Uniswap V3 fee tier parameter in swap function |
| 96% | detector sol_defi_as_11 | Missing minimum output amount check before AMM token swap, enabling sandwich/slippage attacks |
| 89% | detector sol_defi_as_7 | Missing slippage protection in swap/trade functions allowing excessive price deviation losses |
| 87% | detector sol_am_dosa_3 | Denial-of-service from blacklistable tokens blocking required push transfers |
| 85% | detector front_running_patterns | Missing slippage/deadline protection on swaps enabling sandwich/front-running attacks |
| 85% | detector token_integration_safety | Unsafe ERC-20 integration: raw transfer/approve calls and unchecked transfer amounts for non-standard tokens |
| 84% | detector sol_token_fe_10 | Calling token transfer/transferFrom with a zero amount without guarding, risking revert on tokens that reject zero-value transfers |
| 81% | detector sol_am_sandwichattack_1 | Missing slippage protection allowing sandwich attacks on user trades/swaps |
| 78% | category external_call_token_integration | External calls and token integration |
| 77% | detector erc20_patterns | Unsafe ERC-20 token integration without SafeERC20 or received-amount accounting |
| 74% | detector access_control_patterns | Missing access control on privileged/critical functions |
| 68% | detector sol_basics_ac_2 | Missing access control on sensitive privileged functions |
| 67% | detector sol_token_fe_1 | Unsafe ERC20 transfer calls without return-value checks or SafeERC20 wrapper |
| 66% | category frontrunning_mev | Front-running, MEV, and randomness |
| 66% | detector sol_basics_function_3 | Function vulnerable to front-running enabling DoS or value extraction by transaction ordering |
| 65% | category access_control | Access control and privilege |
| 62% | category business_logic_state_machine | Business logic, input validation, and state machine |
| 60% | category dos_griefing | Denial of service and griefing |
| 57% | detector sol_basics_function_9 | Missing access control on sensitive state-changing function |
| 56% | detector sol_am_ma_3 | Missing front-running/sandwich-attack protection due to transaction-order-sensitive logic |
| 55% | detector flash_loan_attacks | Flash-loan-exploitable use of manipulable spot price/balance/voting power within a single transaction |
| 55% | detector solidity_security | Reentrancy vulnerability from unguarded or misordered external calls before state updates |
| 54% | detector sol_defi_lending_2 | Lending protocol lacks a working liquidation mechanism for undercollateralized or defaulted loans |

</details>


</details>

<details><summary>src/Beedle.sol · Crit 🟨 · Any 🟧 · no category hit · 0 functions flagged</summary>

No function has a hit.

<details><summary>File-level hits (2)</summary>

| Chance | Question | What it asks |
|---|---|---|
| 63% | detector sol_defi_general_6 | Unbounded/maximum token approval allowed without revert, enabling over-allowance abuse |
| 51% | detector sol_basics_ac_4 | Single-step ownership/privilege transfer without two-step accept confirmation |

</details>


</details>

<details><summary>src/utils/Structs.sol · Crit 🟨 · Any 🟨 · no category hit · not located</summary>

Not located: no function ranking for this file (Solidity only).

<details><summary>File-level hits (1)</summary>

| Chance | Question | What it asks |
|---|---|---|
| 61% | detector sol_defi_lending_2 | Lending protocol lacks a working liquidation mechanism for undercollateralized or defaulted loans |

</details>


</details>

<details><summary>src/utils/Ownable.sol · Crit 🟩 · Any 🟩 · no category hit · 1 function flagged</summary>

| Function | Lines | Strongest hit | Question | Chance | Line | More |
|---|---|---|---|---|---|---|
| `transferOwnership` | 19-22 | Single-step ownership/privilege transfer without two-step accept confirmation | detector sol_basics_ac_4 | 98% | 20 | <details><summary>2 more</summary>Single-step ownership/privilege transfer instead of secure two-step transfer pattern (detector sol_cr_6) 98%, line 20<br>Single-step privilege/ownership transfer without new-owner confirmation, risking loss or takeover of admin control (detector sol_basics_ac_5) 97%, line 20</details> |

<details><summary>File-level hits (3)</summary>

| Chance | Question | What it asks |
|---|---|---|
| 98% | detector sol_basics_ac_4 | Single-step ownership/privilege transfer without two-step accept confirmation |
| 98% | detector sol_cr_6 | Single-step ownership/privilege transfer instead of secure two-step transfer pattern |
| 97% | detector sol_basics_ac_5 | Single-step privilege/ownership transfer without new-owner confirmation, risking loss or takeover of admin control |

</details>


</details>

1 file with nothing at 50% or more:

<details><summary>Low-risk files</summary>

- `src/utils/Errors.sol`

</details>

## Ignored files

<details><summary>Files not scanned (5)</summary>

- `script/LenderScript.s.sol`: script
- `src/interfaces/IERC20.sol`: interface
- `src/interfaces/ISwapRouter.sol`: interface
- `test/Fuzzing.t.sol`: test
- `test/Lender.t.sol`: test

</details>

---

Jev model jev-1.13.0 · hit threshold 50% · generated 2026-09-18
