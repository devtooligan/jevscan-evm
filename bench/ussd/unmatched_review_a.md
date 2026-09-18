# USSD unmatched-flag review (A1–A4)

Source: `~/dev/ussd/2023-05-USSD/USSD-Foundry/src`. Judged findings from `answer_key.json`.

## A1. `USSD.sol`: oracle / price manipulation (83%)

**Verdict: duplicate of judged finding M-9 (primary), with M-2 also covering it**

`calculateMint` (L170-173) mints at the raw oracle price with no fee, spread, or bound: `uint256 assetPrice = collateral[getCollateralIndex(_token)].oracle.getPriceUSD(); return (((assetPrice * _amount) / 1e18) * (10 ** decimals())) / (10 ** IERC20MetadataUpgradeable(_token).decimals());`. The only price-related weakness in USSD.sol is that it trusts that number completely. That is M-9: it mints at 100% of the oracle price, so arbitrageurs can extract value inside the Chainlink deviation band. M-2 describes the same trust from the user's side, since `mintForToken` (L151-167) has no `minOut`. `collateralFactor` (L179-194) values holdings as `balanceOf(this) * oracle.getPriceUSD()`. Those prices come from the oracle files, whose bugs are already judged: H-1/H-4 for DAI, H-10/M-4 for WBTC, H-11 for WETH, and M-1/M-7 for staleness and minAnswer. `balanceOf` can be inflated by a donation, but that only raises the collateral factor at the donor's expense and gives the donor nothing back. USSD.sol has no spot or slot0 read of its own; the slot0 issue (H-5) is in the rebalancer. USSD.sol adds no new manipulation vector beyond M-9/M-2 and the oracle-file findings it inherits.

## A2. `USSD.sol`: arithmetic / precision (82%)

**Verdict: real but not reportable (informational: sub-unit truncation that rounds in the protocol's favor)**

`calculateMint` L172 does divide before multiplying: `((assetPrice * _amount) / 1e18) * (10 ** decimals())`. For an 18-decimal token, the first division truncates below 1e-18 USD before the result is scaled down to 6 decimals, so the loss is invisible. For WBTC, 8 decimals, 1 satoshi at $30k gives `30000e18*1/1e18 = 30000` and then `30000*1e6/1e8 = 300`, which is 0.0003 USSD. That is exact to within dust. `collateralFactor` L183-190 computes `balance*1e18/10**dec * price / 1e18`. It multiplies before its final division, and the only truncation is at the 1e-18 USD level. Every rounding goes down: the minter gets fewer USSD, and the collateral factor is understated slightly. Neither direction can be exploited. With realistic magnitudes, `price*amount` does not overflow, even with the 1e10-inflated DAI price from H-4. The one real arithmetic error that reaches these functions is the upstream oracle scaling from H-4, which is filed against StableOracleDAI.sol. The `/ totalSupply()` at L193 can divide by zero only if the supply is burned to 0, which runs through the H-8 `burnRebalancer` path. The formulas in USSD.sol are correct.

## A3. `USSD.sol`: external calls / token integration (81%)

**Verdict: real but not reportable (by design / informational). The `UniV3SwapInput` part is a duplicate of H-7.**

`approveToRouter` (L242-247) is `public` with no modifier, and it grants `type(uint256).max` of any `_token` from USSD to `uniRouter`. Anyone can call it, but it cannot be exploited. SwapRouter02 only pulls tokens from its caller (`payer = msg.sender` in `exactInput`/`pull`), and only `onlyBalancer` `UniV3SwapInput` makes USSD call the router. An attacker can therefore create an allowance but cannot spend it. The approve return value is ignored (`IERC20Upgradeable(_token).approve(...)`, not `safeApprove`). That only matters for tokens that return false or no value, such as USDT. The whitelisted DAI, WETH, WBTC, and WBGL all return true or revert, so this is informational. After `setUniswapRouter` (L223-225) changes the router, the old router keeps its max allowance. That is admin trust and is excluded. `UniV3SwapInput` (L227-240) uses `amountOutMinimum: 0` with the deadline commented out, which is exactly judged H-7. `collateralFactor` makes external `balanceOf`, `decimals`, and `getPriceUSD` calls in a loop over the admin-controlled whitelist. The loop is bounded by admin actions and does not create a token-integration bug. None of this is new and reportable.

## A4. `oracles/StableOracleDAI.sol`: arithmetic / precision (83%)

**Verdict: duplicate of judged finding H-4 (and H-1). This is a legitimate second label for the same root cause, not a new bug.**

The flagged expression is L50-52: `(wethPriceUSD * 1e18) / ((DAIWethPrice + uint256(price) * 1e10) / 2)`. `* 1e10` assumes the Chainlink feed has 8 decimals, but the DAI/ETH feed at `0x7736…F1f4` (L24-26) has 18 decimals. That is H-4, and it is a decimal-scaling error, which falls squarely under arithmetic/precision. The average also adds a WETH→DAI quote to a DAI→ETH answer, which is H-1. That is also a unit or dimension error that you could label arithmetic. The `/2` average and `uint256(price)` cast have no separate precision problem. Casting a negative answer is M-7 or validation territory, not arithmetic. For scoring, this flag should match H-4/H-1 as a cross-category hit and should not count as a false positive or a new finding. It does not represent an independent bug. Side note, outside this flag's category: `ethOracle` is hardcoded to `address(0)` (L30, `// TODO`). As written, `ethOracle.getPriceUSD()` at L44 always reverts, which is a deployment placeholder and was not judged.

---
Verdicts:
- A1: duplicate of judged finding M-9 (and M-2)
- A2: real but not reportable (sub-unit truncation that favors the protocol; informational)
- A3: real but not reportable (open `approveToRouter` cannot be exploited, since the router only pulls from its caller); the `UniV3SwapInput` part is a duplicate of H-7
- A4: duplicate of judged finding H-4 (and H-1); legitimate cross-label
