# Monolith unmatched flags, batch B (Vault, Lens)

Code: `Monolith/src` in the Sherlock Dec 2025 checkout. Judged set: H-1, M-1 through M-6 (`answer_key.json`). Contest rules also count any EIP-4626 MUST violation as Medium, so I checked Vault against the spec.

## B1. `src/Vault.sol`, business logic / input validation / state machine (77%)

**Verdict: false positive**

The flagged lines implement the one-time `MIN_SHARES` dead-share burn, and the previews and the state-changing functions handle it the same way. In `deposit`, the call `convertToShares(assets)` (L51) mints to the receiver and then moves 1e16 shares to `address(0)`:

```solidity
if(isFirstDeposit) {
        // if this underflows, the first deposit is less than MIN_SHARES which is not allowed
        balanceOf[receiver] -= MIN_SHARES;      // L62
        balanceOf[address(0)] += MIN_SHARES;
        shares -= MIN_SHARES;
```

`previewDeposit` subtracts the same amount (`} else shares -= MIN_SHARES;`, L131) and returns 0 instead of reverting when shares are below MIN_SHARES, as its comment says. `mint` gets its price from `previewMint` (L77), which adds `MIN_SHARES` on the first deposit (L141). It then mints `shares + MIN_SHARES` (L84) and burns the extra, so the receiver gets exactly `shares` and pays exactly the previewed assets. The "underflow" comment at L85 is misleading, because that subtraction can never underflow in `mint`. That is harmless: a first `mint(1)` still costs 1e16+1 assets and still burns 1e16 dead shares.

The dead shares stay in `totalSupply`, since `_mint` counts them and the manual balance move does not reduce it. The first-deposit branch therefore runs only once, and an attacker cannot reset the vault to zero supply. Before the first deposit, `totalAssets` can only be donations: `accrueInterest` mints `interestAfterFees * totalStaked / totalPaidDebt`, which is 0 while nothing is staked. The 1:1 first-deposit pricing therefore leaks nothing.

Any difference between the previews and execution after `accrueInterest` comes from `getPendingInterest` not matching the real accrual. That falls under M-3/M-5/M-6.

One informational nit: `deposit` emits `Deposit(..., shares)` at L58 before the MIN_SHARES deduction. The event over-reports the receiver's shares by 1e16 on the first deposit, while `mint` emits the net amount. This does not affect on-chain state.

## B2. `src/Lens.sol`, arithmetic / precision (74%)

**Verdict: real but not reportable (a view-only copy of Lender's math; the rounding it copies is the H-1 root cause, and the interest path copies M-5/M-6)**

`Lens.getCollateralOf` (L11-37) matches `Lender.updateBorrower` (L567-596) line for line. Both use the same 5-iteration epoch loop, the same `indexDelta.mulDivUp(borrowerDebtShares, 1e36)`, and the same rebase with 1-wei round-down:

```solidity
// Lens.sol:27
borrowerDebtShares = borrowerDebtShares.divWadUp(1e36) == 1 ? 0 : borrowerDebtShares.divWadUp(1e36);
// Lender.sol:583
borrowerDebtShares = borrowerDebtShares.divWadUp(1e36) == 1 ? 0 : borrowerDebtShares.divWadUp(1e36);
```

`Lens.getDebtOf` applies the same rebase at L70 and then prices shares with `mulDivUp(totalFreeDebt, totalFreeDebtShares)`. `Lender.getDebtOf` (L701-707) uses the identical expression. I found no case where Lens rounds differently from what Lender produces after its own sync.

`_getSyncedTotalDebt` adds the full `interest` to paid debt, as `accrueInterest` does at L230 (`totalPaidDebt += interest; // ... NOT interestAfterFees`). It therefore inherits any M-5 miscalculation. Its `catch` returns the unsynced totals, the same stuck state M-6 describes.

The up-rounding of the share rebase and of per-borrower debt is the mechanism that H-1 exploits. Lens is only a reporter: nothing in `src/` imports or calls it (`grep -rl Lens src` returns only `Lens.sol`), so it has no independent on-chain effect.

## B3. `src/Lens.sol`, business logic / state machine (72%)

**Verdict: false positive**

The epoch state machine in Lens simulates `updateBorrower` without writing state, and it does so correctly. For a borrower whose epoch is behind, `getDebtOf` first computes debt from the stale shares (L56). It then rebases the shares once per missed epoch (L68-71) and recomputes the result against the current `totalFreeDebtShares` (L73):

```solidity
for (uint256 i = 0; i < 5 && _borrowerEpoch < currentEpoch && borrowerDebtShares > 0; ++i) {
    _borrowerEpoch += 1;
    borrowerDebtShares = borrowerDebtShares.divWadUp(1e36) == 1 ? 0 : borrowerDebtShares.divWadUp(1e36);
}
debt = totalFreeDebtShares == 0 ? 0 : borrowerDebtShares.mulDivUp(totalFreeDebt, totalFreeDebtShares);
```

The result is exactly what Lender charges after `updateBorrower` runs, and `getCollateralOf` (L28, `lastIndex = 0` on each epoch rollover) matches Lender L584. The one real divergence goes the other way. `Lender.getDebtOf` (public view, L701) reads `freeDebtShares[account]` without the epoch rebase. For a borrower who missed an epoch rollover, it overstates debt by roughly 1e18 per missed epoch, while Lens returns the correct figure.

That stale Lender view has no state consequence. Every state-changing caller of `getDebtOf` calls `updateBorrower` first: `adjust` L243, `setRedemptionStatus` L340, `liquidate` L370, `writeOff` L422, and the `decreaseDebt` max path via `adjust`. It could only mislead off-chain integrators that read `Lender.getDebtOf` directly, which is at most an informational finding against Lender, not against Lens.
