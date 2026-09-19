# Monolith: function-level review of the top-1 misses

The strict metric in `results.md` (Locating, category resolution) counts an issue as identified only when the function
ranked #1 on its scored (file, question) pair is one the judges named. This review takes the four misses and asks a
looser question: is the #1 function on the finding's exploit chain? A function is on the chain when it calls the buggy
function, is called by it, produces the value the bug corrupts, or is where the corrupted value is consumed. A function
that only touches the same state through a different path, or runs next to the exploit without affecting it, does not
count.

Source: a cached re-run of `bench/run_bench.py monolith` (same rankings as `results.md`), code at contest commit
b36e9ef (`Monolith/src`). The ranking is the one `locating()` scores: the issue's true pair with the highest
file-level p.

| Issue | Scored pair | Judged functions | #1 (p) | #2, #3 (p) | Ruling |
|---|---|---|---|---|---|
| H-1 Rounding lets a user borrow unbacked tokens | `Lender.sol`, arithmetic_precision | `increaseDebt`, `redeem` | `writeOff` (0.83) | `redeem` (0.81), `updateBorrower` (0.78) | **Not on the chain.** The exploit runs `redeem` (inflates shares/debt) -> `adjust` repay -> `decreaseDebt` (clamps `totalFreeDebt` to 0) -> `increaseDebt` (mints shares 1:1). `writeOff` also writes `totalFreeDebt` through `decreaseDebt(max)`, but it is not a step of this exploit and calls neither judged function. |
| M-2 Inconsistent health checks allow liquidating a healthy position | `Lender.sol`, business_logic_state_machine | `adjust`, `getLiquidatableDebt`, `liquidate` | `writeOff` (0.87) | `redeem` (0.87), `adjust` (0.83) | **Not on the chain.** `liquidate` calls `writeOff` after the wrongful liquidation, but `writeOff` applies its own 100x-debt threshold and is a no-op on a position at `debt == borrowingPower`. It neither produces nor consumes the `<=` vs `>` boundary. |
| M-3 `Vault.totalAssets()` can revert (EIP-4626 violation) | `Vault.sol`, accounting_share_math | `totalAssets`, `getPendingInterest` | `deposit` (0.81) | `previewDeposit` (0.67), `mint` (0.62) | **On the chain.** `deposit` calls `convertToShares` (Solmate ERC4626), which calls `totalAssets()`, which calls `Lender.getPendingInterest()`, whose catch block reverts on short gas. |
| M-6 `wadExp()` underflow to 0 leaves interest accrual stuck | `Lender.sol`, arithmetic_precision | `calculateInterest`, `accrueInterest`, `setHalfLife` | `writeOff` (0.83) | `redeem` (0.81), `updateBorrower` (0.78) | **On the chain.** `writeOff` calls `accrueInterest()` on its first line, which calls `calculateInterest` (division by a zero `growthDecay`) and silently skips accrual in the catch block. This is a weak lead: most Lender entry points (`redeem`, `adjust`, `liquidate`) open with the same call. |

The three hits (M-1 `writeOff`, M-4 `redeem`, M-5 `calculateInterest`) are unchanged. `writeOff` is #1 on the
Lender.sol arithmetic_precision and business_logic_state_machine rankings, so it stands for three issues. It is the
judged function for M-1 and on the chain for M-6 only.

Only the category-resolution ranking is reviewed, because it produces the 3 of 7. Detector resolution scores a
different ranking per issue (`results.md`).

**Strict: 3 of 7. Counting on-chain functions: 5 of 7.**
