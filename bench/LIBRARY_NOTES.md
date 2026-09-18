# Notes on the question library

What we learned building the current questions. The detector library replaced an earlier private detector set; the comparison numbers below are from cold runs with jev-1.13.0.

## Questions: describe the class, not the benchmark

Beedle exposed three weak subcategory questions. Each was rewritten in general terms, then both benchmarks were re-run.

| Question | Problem | Fix | Beedle `Lender.sol` (true) |
|---|---|---|---|
| `single_function_reentrancy` | Covered only a payout before the caller's balance update. | Any external call that can reach attacker code (a caller-chosen token, a hook token, a caller-supplied address) before the effect is recorded, with no guard. | 0.30 to 0.59 |
| `arbitrary_from_or_on_behalf_of` | Asked only about address parameters. | Also ids of a pool, vault, loan, or order owned by someone else. | 0.12 to 0.45 |
| `frontrunnable_state_change` | Missed a counterparty changing terms ahead of a user. | Terms owned by another user, applied with no user limit; admin changes excluded. | 0.56 to 0.89 |

Beedle subcategory recall went from 30/40 to 34/40 at 0.5, with USSD unchanged.

Lessons:

- A broad first draft fires everywhere. "Terms set by an admin, a counterparty, or a pool owner" raised USSD's clean oracle file from 0.14 to 0.31. Narrowing to terms owned by another user brought it back to 0.15.
- Keep attacker conditions. Dropping "can reach attacker-controlled code" made Beedle's `Staking.sol` score 0.74 on a WETH transfer that cannot re-enter.
- Stop before the wording fits the benchmark. The `buyLoan` issues stay at 0.45; more Beedle-shaped wording would fit the contest, not the class.
- Informational items (floating pragma, single-step ownership) are excluded on purpose. A linter finds them.

## The Solodit prune rule

Keep checklist items that describe an exploitable condition. Drop informational, best-practice, centralization, and legacy-compiler items. [`sources/exclusions.json`](../sources/exclusions.json) lists the 47 excluded ids with reasons.

| USSD, detector level | Before prune (434) | After prune (387) |
|---|---|---|
| Flags on clean files @0.5 / @0.7 | 19 / 9 | 12 / 4 |
| All flags @0.5 | 194 | 152 |
| Cost | $0.124 | $0.109 |

The prune lost two issues on each benchmark. All four were credited through the detector map to questions unrelated to the issue (missing events, comments that disagree with code). No issue caught by a detector that describes it was lost.

The 387 included 44 detectors from Slither's detector documentation. They were later dropped (387 to 343): no recall lost, 10 of their 12 flags at 0.7 matched no judged finding. See [ABLATION_SLITHER.md](ABLATION_SLITHER.md).

Most noise came from generic checklist items that a literal reader matches on nearly any contract: missing events, unhandled external-call reverts, generic input validation.

## Criteria are OR, not AND

A detector sends its question, then "It is true when the file matches the description above; the following are examples of code that makes it true:", then its criteria.

- Each criterion must be a complete instance of the flaw, sufficient on its own. Alternatives are joined with "or".
- Gates ("implements ERC-4626"), bare absences ("no reentrancy guard"), and exclusions belong in the question, not the criteria. A criterion like "no reentrancy guard" alone is not a bug, and Jev reads lists literally.
- The sync runs a second LLM check for this and rejects criteria that start with "No ", "Absence", "Excludes", "Lacks", "Implements", or "Uses".

## Compared with the earlier private detector set

- The public library finds more on protocol code. Beedle detector recall @0.5 went from 26/39 to 30/40 after the prune. New hits: counterparty front-running (0.01 to 0.73), single-step ownership (0.07 to 0.98), low-decimal tokens (0.41 to 0.83).
- It lost three classes: oracle quote-currency mistakes (USSD H-11), staking reward accounting (Beedle H-13, H-24, H-25), and oracle-priced arbitrage (USSD M-9).
- It costs about 30% more per scan and flags more on clean files.
- Category and subcategory scores did not change; those questions are the same.

## The detector map is noisy

A detector counts for an issue only through `detector_map.json`, one LLM pass that assigns each detector to subcategories. Two builds over nearly the same library moved USSD detector recall @0.5 from 11 to 14. Read detector-level recall as ±3 issues. Category-level recall does not depend on the map. A majority vote over several builds would steady it (see [next steps](../docs/DETAILS.md#next-steps)).
