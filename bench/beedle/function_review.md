# Beedle: function-level review of top-1 misses

Run regenerated from cache (`bench/run_bench.py beedle`, category resolution, locate threshold 0.5). An issue is
scored on one function ranking: its true (file, question) pair with the highest file-level p, as in
`run_bench.py`. 34 issues were located; in 14 the #1-ranked function is one the judges named. The 20 others are
below.

Rule: the #1 function counts when it is on the finding's exploit chain: it calls a judged function, is called
by one, produces the value the bug corrupts, or is where that value is consumed. Sharing pool or loan state with
the judged function is not enough.

**Strict: 14 of 34. Counting on-chain functions: 18 of 34.**

| Id | Judged fn | #1 fn (p) | #2, #3 (p) | Verdict | Path |
|---|---|---|---|---|---|
| H-2 | `repay` | `refinance` (0.84) | `seizeLoan` (0.82), `setPool` (0.79) | not on the chain | The re-entrancy is `repay`'s collateral transfer before `delete loans[loanId]`; `refinance` neither calls nor is called by `repay`. |
| H-3 | `setPool` | `refinance` (0.84) | `seizeLoan` (0.82), `setPool` (0.79) | not on the chain | The re-entrancy is `setPool`'s refund transfer before `pools[poolId] = p`; `refinance` never calls `setPool` (only `zapBuyLoan` does). |
| H-5 | `refinance` | `repay` (0.93) | `giveLoan` (0.89), `seizeLoan` (0.89) | not on the chain | The attack is `startAuction` then `refinance`/`giveLoan` resetting `auctionStartTimestamp`; `repay` plays no part. |
| H-7 | `buyLoan` | `repay` (0.93) | `giveLoan` (0.89), `seizeLoan` (0.89) | not on the chain | Borrower pushes a high-LTV loan into another pool through `buyLoan`'s missing ratio check; `repay` is not involved. |
| H-9 | `buyLoan` | `repay` (0.93) | `giveLoan` (0.89), `seizeLoan` (0.89) | not on the chain | Fake pool with mismatched tokens passed to `buyLoan`, then the loan is seized; `repay` is not involved. |
| H-11 | `buyLoan` | `repay` (0.93) | `giveLoan` (0.89), `seizeLoan` (0.89) | not on the chain | Theft runs `setPool` (fake pool), `buyLoan`, `borrow`, `startAuction`, `seizeLoan`. The report notes `repay` then reverts for the victim, a side effect, not the exploit. |
| H-13 | `update`, `sellProfits` | `withdraw` (0.69) | `claim` (0.69), `update` (0.62) | **on the chain** | `withdraw` calls `updateFor`, which calls `update`: the lazy index is computed there and settled into `claimable` for the withdrawing staker. |
| H-19 | `buyLoan` | `repay` (0.93) | `giveLoan` (0.89), `seizeLoan` (0.89) | not on the chain | Attack runs `updateMaxLoanRatio`, `refinance`, `startAuction` front-running a victim's `buyLoan`; `repay` is not involved. |
| H-21 | `giveLoan` | `refinance` (0.84) | `giveLoan` (0.78), `repay` (0.74) | not on the chain | Interest is capitalised into `debt` inside `giveLoan`; `refinance` has its own, separate debt update. |
| H-23 | `borrow`, `setPool` | `buyLoan` (0.69) | `refinance` (0.64), `giveLoan` (0.56) | not on the chain | Sandwich is `setPool`, victim `borrow`, then `startAuction`/`seizeLoan`; `buyLoan` is not involved. |
| H-24 | `update`, `updateFor`, `deposit` | `withdraw` (0.69) | `claim` (0.69), `update` (0.62) | **on the chain** | `withdraw` calls the judged `updateFor` and `update`, the functions that fold pre-stake WETH into `index` with no holder. |
| H-25 | `claim` | `withdraw` (0.69) | `claim` (0.69), `update` (0.62) | not on the chain | `claim` overwrites `balance`; the loss lands in `update`'s `_diff`. `withdraw` only calls `update` and neither calls nor is called by `claim`. |
| H-26 | `borrow`, `refinance` | `buyLoan` (0.69) | `refinance` (0.64), `giveLoan` (0.56) | not on the chain | Lender front-runs `borrow`/`refinance` with `setPool` (short `auctionLength`), then `startAuction`/`seizeLoan`; `buyLoan` is not involved. |
| K-27 | `borrow`, `refinance` | `buyLoan` (0.69) | `refinance` (0.64), `giveLoan` (0.56) | not on the chain | Duplicate of H-26; same path, no `buyLoan`. |
| M-1 | `_calculateInterest`, `giveLoan` | `refinance` (0.81) | `giveLoan` (0.78), `borrow` (0.73) | **on the chain** | `refinance` calls the judged `_calculateInterest` and consumes its truncated interest. The report's impact lands in `giveLoan`'s ratio check, so this is the weakest of the four. |
| M-2 | `borrow`, `refinance` | `buyLoan` (0.69) | `refinance` (0.64), `giveLoan` (0.56) | not on the chain | Lender front-runs `borrow`/`refinance` with `setPool`/`updateInterestRate`; `buyLoan` is not involved. |
| M-5 | `giveLoan` | `repay` (0.93) | `giveLoan` (0.89), `seizeLoan` (0.89) | not on the chain | Lender calls `giveLoan` during an auction to cancel it and block `buyLoan`; `repay` is not involved. |
| M-7 | `seizeLoan` | `refinance` (0.84) | `seizeLoan` (0.82), `setPool` (0.79) | not on the chain | The re-entrancy is `seizeLoan`'s collateral transfer before `delete loans[loanId]`; `refinance` is not involved. |
| M-13 | `_calculateInterest` | `refinance` (0.81) | `giveLoan` (0.78), `borrow` (0.73) | **on the chain** | `refinance` calls `_calculateInterest` and settles the loan with `debtToPay = debt + interest`, so zero-truncated interest lets the borrower roll the loan without paying interest. |
| M-14 | `borrow`, `repay` | `seizeLoan` (0.84) | `repay` (0.77), `refinance` (0.69) | not on the chain | With `borrowerFee = 0` the attacker borrows and repays pool liquidity for free around victims; `seizeLoan` only reads `borrowerFee` for its gov fee. |

Close call: H-11. `repay` is where the corrupted `loan.lender` is consumed (it reverts), but that is a side effect,
not the collateral theft, so it is not counted.
