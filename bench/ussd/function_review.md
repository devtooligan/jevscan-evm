# USSD: function-level review of top-1 misses

The benchmark's "identified the function" metric is strict: for each judged finding, the function jevscan ranks first for the finding's scored (file, category) pair (the same pair `run_bench.py` scores top-1 on) must be one the judges named. At category resolution USSD scores 14 of 21 (M-11 names no function).

This review checks the 7 misses against a looser rule: the #1 function counts when it is on the finding's exploit chain. It must call the buggy function, be called by it, produce the value the bug corrupts, or consume the corrupted value. A function in the same file with unrelated logic does not count, and neither does a sibling reached only through a shared caller.

Run: `bench/run_bench.py ussd`, regenerated from the answer cache (same numbers as `results.md`). Code: `ussd-contracts/contracts` at the contest commit.

| Finding | Judged function(s) | #1 (p) | #2 / #3 (p) | Verdict | Path |
|---|---|---|---|---|---|
| H-3 `getOwnValuation` price formula | `getOwnValuation` | `BuyUSSDSellCollateral` (0.88) | `getOwnValuation` (0.86) / `SellUSSDBuyCollateral` (0.86) | not on the chain | `BuyUSSDSellCollateral` never reads the valuation (its only use, L111, is commented out); it sizes the trade from `getSupplyProportion`. It is a sibling of `getOwnValuation` under `rebalance`. |
| H-9 pool balance proportion is not price | `getSupplyProportion`, `rebalance` | `getOwnValuation` (0.82) | `SellUSSDBuyCollateral` (0.80) / `BuyUSSDSellCollateral` (0.79) | on the chain | `rebalance` calls `getOwnValuation` (L93), and its `ownval` picks the peg-down branch where the balance-proportion subtraction underflows (L97). The finding is the mismatch between that price and the balances. |
| H-10 wrong oracle feed addresses (scored on `StableOracleDAI.sol`) | `constructor` | `getPriceUSD` (0.90) | `constructor` (0.48) / none (2 functions) | on the chain | `getPriceUSD` consumes the addresses the constructor sets: it queries the wrong `DAIEthOracle` (L36) and calls the zero-address `ethOracle` (L44). |
| M-2 `mintForToken` has no slippage parameter | `mintForToken` | `UniV3SwapInput` (0.81) | `mintForToken` (0.58) / `approveToRouter` (0.29) | not on the chain | `mintForToken` → `calculateMint` → oracle `getPriceUSD` never touches `UniV3SwapInput`, the rebalancer-only router swap (H-7's bug). |
| M-3 underflow when selling collateral | `BuyUSSDSellCollateral` | `SellUSSDBuyCollateral` (0.78) | `BuyUSSDSellCollateral` (0.72) / `rebalance` (0.57) | not on the chain | The underflow is in `BuyUSSDSellCollateral` (L123, L136). `SellUSSDBuyCollateral` is the opposite (peg-up) branch of `rebalance` and shares no value with it. |
| M-6 DAI collateral with no sell path | `BuyUSSDSellCollateral` | `SellUSSDBuyCollateral` (0.89) | `BuyUSSDSellCollateral` (0.84) / `rebalance` (0.78) | not on the chain | The missing `pathsell.length` check is in `BuyUSSDSellCollateral`'s else branch (L130-139). `SellUSSDBuyCollateral` has an analogous DAI check (H-2) but is the opposite branch, not on this path. |
| M-9 mint at 100% oracle price, no fee | `mintForToken`, `calculateMint` | `collateralFactor` (0.57) | `mintRebalancer` (0.44) / `mintForToken` (0.38) | not on the chain | `collateralFactor` reads the same oracles but neither calls nor is called by the mint path; only the rebalancer uses it. |

Strict: 14 of 21. Counting on-chain functions: 16 of 21.

In every miss, the judged function is at #2 or #3, except H-9. There, `rebalance` is at #4 (0.65) and `getSupplyProportion` at #5 (0.52).
