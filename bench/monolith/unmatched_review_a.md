# Monolith: review of unmatched jevscan flags (A1–A3)

Code: `2025-12-monolith-stablecoin-factory/Monolith/src`. Checked against the 7 judged findings (H-1, M-1..M-6) and the contest scope answers (Sherlock contest 1212 details).

## A1. `src/Lender.sol` — external calls / token integration (83%)

**Verdict: real but not reportable.** There is a real CEI violation in `liquidate`, but only a hook-bearing collateral token (ERC777 or similar) can exploit it, and the contest excludes those ("Only standard ERC20 tokens (with 6-18 decimals) are expected to be in scope"; ERC777 is listed under known restrictions).

In `liquidate`, debt is reduced at L384, collateral is pushed to the liquidator at L397, and only then is the borrower's balance written from a stack-cached value:

```solidity
384  decreaseDebt(borrower, repayAmount);
375  uint collateralBalance = _cachedCollateralBalances[borrower];
397  collateral.safeTransfer(msg.sender, collateralReward);
398  _cachedCollateralBalances[borrower] = collateralBalance - internalCollateralReward;
399  if(!isRedeemable[borrower]) nonRedeemableCollateral -= internalCollateralReward;
```

With a `tokensReceived` hook, the liquidator can re-enter `liquidate` during the L397 transfer. The inner call sees the lowered debt but the full collateral balance, pays a second reward, and writes `full - reward2`. The outer frame then overwrites that with `full - reward1`. The borrower's recorded collateral drops by only one reward while two leave the contract, and `nonRedeemableCollateral` is decremented twice. With standard ERC20 collateral there is no callback, so nothing can re-enter.

The other flagged sites are clean:
- `adjust` L250–256 credits collateral before `safeTransferFrom`, which reverts atomically for standard tokens. The >18-decimal round trip at L254 re-derives the transfer amount from the internal amount.
- `writeOff` L444–453 zeroes the borrower's state before `collateral.safeTransfer(to, ...)`.
- `redeem` L477–484 updates all accounting before the collateral push.
- Every collateral push goes to `msg.sender` or a caller-chosen `to`, never to a third party. A blocklisting token therefore cannot block another user's liquidation, redemption, or write-off.
- `coin` is the protocol's own solmate `Coin`, with no hooks.

Aside, outside the flagged functions: `psmAsset.approve(...)` (L169, L545) uses the solmate `ERC20` interface, which expects a `bool` return. A USDT-style psmAsset paired with a psmVault would make the constructor revert. The only effect is that such a deployment fails, and USDT falls outside the "standard ERC20" scope anyway.

## A2. `src/Lender.sol` — denial of service / griefing (73%)

**Verdict: false positive.** None of the flagged lines (L397, L453, L484, L294) gives anyone a way to block another user's operation.

- L397, L453, and L484 are collateral transfers to `msg.sender` or a caller-chosen `to`, so no victim address can make them revert. The `writeOff` that `liquidate` triggers is wrapped in `try this.writeOff(...) {} catch {...}` (L407–411), so a failing write-off cannot block the liquidation.
- L294 is the full-repay branch of `adjust` (`decreaseDebt(account, type(uint).max)`). Repayment is permissionless and sets the debt to exactly 0, so the minDebt check at L304 (`debtBalance == 0 || debtBalance >= minDebt`) cannot be abused to strand a borrower.
- `updateBorrower` loops at most 5 times (L575), so it cannot run out of gas.

DoS-shaped behaviors exist nearby, but none is reportable:
1. `redeem` intentionally reverts when it would drain `totalFreeDebt` to 0. The code says so at L486: "Intentional division by zero and revert if totalFreeDebt is 0".
2. A liquidator can supply just over `WRITEOFF_GAS_REQUIREMENT` (120k at L85, checked at L410) so that the inner `writeOff` runs out of gas under the 63/64 rule and the catch swallows it. That only skips the optional write-off, which anyone can call directly later, and the liquidator gives up the collateral `writeOff` would have sent them, so they have no incentive.
3. A free debtor can front-run a redeemer by repaying, so the redeemer's `amountIn > totalFreeDebt` and `getRedeemAmountOut` returns 0 (L763). The redeemer's transaction reverts, but no funds are lost.

The only judged finding with a DoS-like impact in these paths is M-4 (redeeming during bad debt leaves other free debtors unable to withdraw, via the L265–268 check). That is an accounting bug rooted in `redeem`'s collateral distribution, not these flagged lines, so this flag is not a duplicate of it.

## A3. `src/Factory.sol` — business logic / input validation / state machine (78%)

**Verdict: false positive.** The deployment flow is correctly ordered, and parameter validation happens in the Lender constructor.

```solidity
150  uint id = deployments.length;
151  lender = LenderDeployer.getAddress(msg.sender, id);
...
180  LenderDeployer.deployLender(msg.sender, id, lenderData);
181  CoinDeployer.deployCoin(msg.sender, id, coinData);
182  VaultDeployer.deployVault(msg.sender, id, vaultData);
183  deployments.push(lender);
```

- The library functions are `external`, so they run via DELEGATECALL. `address(this)` in `getHash` (L18, L32, L46) is therefore the Factory, and each CREATE3 salt binds `(tag, chainid, factory, caller, id)`. Because `id` strictly increases and `caller` is in the salt, nobody can squat or collide with another deployer's addresses.
- The deployment order has no dependency cycle:
  - The Lender only stores the predicted `coin` and `vault` addresses; its constructor never calls them.
  - The Coin needs only the lender address.
  - The Vault constructor calls `ILender(_lender).coin()`, then `ERC4626` calls `asset.decimals()`, and both the Lender and the Coin exist by then.
- `interestModel` at L162 is a single shared instance, which is safe because `calculateInterest` is `pure` (InterestModel.sol L28).
- The Lender constructor (Lender.sol L125–138) enforces the risk bounds, including `collateralFactor <= 8500`, `minDebt >= factory.minDebtFloor()`, and `psmVault.asset() == psmAsset`.
- `DeployParams` fields such as feed and operator are not validated, but the contest treats deployers as trusted for their own coin's collateral, oracle, and parameters.

Aside, informational only: `getFeeOf` (L116–119) treats `customFeeBps == 0` as "unset". As a result, the factory operator cannot give a specific lender a 0% global fee, because `setCustomFeeBps(x, 0)` falls back to `feeBps`. This is a trusted-role convenience limitation with no user impact.
