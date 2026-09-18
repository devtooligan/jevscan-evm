# USSDRebalancer.sol unmatched flags (B1-B3)

Source: `USSD-Foundry/src/USSDRebalancer.sol` (line numbers match the Truffle copy). All swaps the rebalancer performs go through `USSD.UniV3SwapInput` (`USSD.sol:227-240`, `amountOutMinimum: 0`). The rebalancer has no swap code of its own.

## B1. Accounting / share math: real but not reportable (Low)

Most accounting defects in these functions are already judged:
- The price math is H-3 (L74/L76).
- The pool-balance delta used as the trade size (L97, L104) is H-9.
- `amountToSellUnits` (L121) is H-6 (wrong scaling) and M-8 (rounds to 0).
- The `amountToBuyLeftUSD -=` underflow (L123/L136) is M-3.
- The DAI branch that lacks a `pathsell` check (L130-138) is M-6.
- The `ratios[flutter]` out-of-bounds read (L191/L198) is M-10.

One accounting defect is not judged:
- **L127 overwrites `DAItosell` instead of adding to it.** In the "no need to swap DAI" branch, `DAItosell = DAIbal * amountToBuyLeftUSD / collateralval;` discards DAI already collected from earlier collateral that was fully sold in the same loop (L135-137 `+=`).
  - Example: WETH is sold fully for 400 DAI, leaving `amountToBuyLeftUSD` = 100e18. DAI collateral is then reached with `collateralval > 100e18`, so `DAItosell` becomes about 100 DAI instead of 500 DAI.
  - The rebalance buys back only part of the USSD it sized. The unspent DAI stays in USSD.sol as DAI collateral.
  - No funds are lost. The peg correction under-executes, and anyone can call `rebalance()` again. This is Low severity by Sherlock standards.

Checked and rejected:
- **`daibought / portions` (L201) when `portions == 0`.** The second loop repeats the first loop's condition, so no swap runs in that case. It divides by zero only if a balance flips between the loops. The only balance that changes is DAI's, and the H-2 fix skips DAI.
- **`portions` counts DAI but skips its buy (L199).** The comment at L200 ("it's already bought") says this is intended. The share that `portions` reserves for DAI stays as DAI.

## B2. External calls / token integration: duplicate of H-2 / M-6 (plus H-7)

The concrete external-call failures in these functions are already judged:
- `UniV3SwapInput(collateral[i].pathbuy, ...)` with DAI's empty `pathbuy` (L199-201) is H-2.
- `UniV3SwapInput(collateral[i].pathsell, ...)` with DAI's empty `pathsell` in the sell-all branch (L135) is M-6.
- Swaps with no minimum output are H-7.
- Oracle reads (L116/L190/L197 `getPriceUSD`) map to the oracle findings H-1, H-4, H-10, H-11, M-1, M-4 and M-7.

The only residual pattern is not reportable. The USSD/DAI paths hardcode the 0.05% fee tier (`hex"0001f4"`, L154/L156/L169/L173) instead of reading `uniPool.fee()`, and they rely on `baseAsset` (L120/L168) being the pool's non-USSD token. Both depend on admin configuration (`setPoolAddress` and `setBaseAsset` are `onlyControl`), so they fall under trusted-admin misconfiguration and Sherlock excludes them. `decimals()` (L116) is safe for the collateral set in scope: DAI, WETH, WBTC and WBGL.

## B3. Front-running / MEV: duplicate of H-7 (trigger side: H-5 / H-9)

The rebalancer's swaps have no slippage protection:
- DAI to USSD at L154/L156
- USSD to DAI at L169/L173
- collateral to DAI at L122/L135
- DAI to collateral at L201

This is the same root cause as H-7, not an independent instance. The rebalancer passes only `(path, amountIn)`, and `USSD.UniV3SwapInput` sets `amountOutMinimum: 0` and no deadline. The fix H-7 recommends is in that function, and it covers every rebalancer swap. The rebalancer has no path to the router that avoids the flaw.

`rebalance()` has no access control and decides using slot0 (L72) and pool balances (L84-85). An attacker can therefore trigger a rebalance and sandwich it within one transaction. That trigger side is already judged as H-5 (flash-loan manipulation of slot0) and H-9 (manipulable balance proportion).
