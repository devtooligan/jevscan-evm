## Unmatched flags at 70%, reviewed

Each flag was checked by hand against the code, the 7 judged findings, and the contest's scope answers. Full write-ups: [`unmatched_review_a.md`](unmatched_review_a.md) (A1-A3), [`unmatched_review_b.md`](unmatched_review_b.md) (B1-B3).

| | File | Category | Chance | Verdict | Reason |
|---|---|---|---|---|---|
| A1 | `src/Lender.sol` | external_call_token_integration | 83% | real, not reportable | `liquidate` breaks checks-effects-interactions, but only a hook-bearing (ERC777) collateral can re-enter, and the contest excludes those |
| A3 | `src/Factory.sol` | business_logic_state_machine | 78% | false positive | deployment order and CREATE3 salts are sound; the Lender constructor validates the risk parameters |
| B1 | `src/Vault.sol` | business_logic_state_machine | 77% | false positive | the one-time `MIN_SHARES` dead-share burn is handled the same way in the previews and in `deposit` / `mint` |
| B2 | `src/Lens.sol` | arithmetic_precision | 74% | real, not reportable | a view-only copy of Lender's math: the rounding it copies is H-1's root cause, the interest path copies M-5 / M-6 |
| A2 | `src/Lender.sol` | dos_griefing | 73% | false positive | the flagged transfers go to the caller, `writeOff` is wrapped in try/catch, and full repay cannot strand a borrower |
| B3 | `src/Lens.sol` | business_logic_state_machine | 72% | false positive | the epoch rebase simulation matches what Lender charges after `updateBorrower` |

The table is from the run before the business-logic question gained its view-only sentence ("View or pure functions that change no state do not count, unless state-changing code in the file uses their result."). That run had 10 flags at 70%: 6 real (4 judged findings + 2 real bugs the contest did not count: one out of scope by the rules, one a view-only copy of a judged bug), 4 false positives. In the current run B3 drops to 28% and the others stay above 70%, so there are 9 flags at 70%: 6 real, 3 false positives.

## Notes (hand-written)

- Cold run, 2026-09-18, empty cache, same config: 157 billed requests, $0.077, 5.8 s wall time end to end. The cost table above is from the cached benchmark run, so its wall times are cache reads. The repo's `lib/forge-std` and `lib/solmate` submodules are empty, so the project cannot compile; jevscan read the six scope files as text.
- Clean files: `src/Coin.sol` and `src/Lens.sol` have no known finding, and neither does `src/Factory.sol`, so all three count as clean above. At 0.5, `Coin.sol` got 1 category flag (business logic 0.51); `Factory.sol` got 3 (business logic 0.79, external calls 0.56, DoS 0.56) and `Lens.sol` got 2 (arithmetic 0.75, accounting 0.68). `Lens.sol` re-implements `Lender.sol`'s debt and collateral views (`getDebtOf`, `getCollateralOf`), so its arithmetic and accounting flags may be echoing the Lender math; the 70% ones are reviewed above (B2, B3).
- Known-findings credit in `run/HEATMAP.md` is generous: it needs the right file, one of the finding's functions, and its bug type, not the exact line. M-5's formula is on lines 49-50 and M-6's division on line 36; the heat map's line pick for `calculateInterest` is line 37 for both.
- Contest dates: 2025-12-08 to 2025-12-14 (Sherlock contest 1212); judging closed 2026-02-24. Jev's training cutoff is not published, so recency lowers but does not rule out contamination.
