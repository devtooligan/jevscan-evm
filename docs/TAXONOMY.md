# EVM Vulnerability Taxonomy (jevscan-evm)

A taxonomy for a top-down yes/no classifier. The scanner asks the category question per source file, then runs the detector library. There are 14 categories. The machine-readable version is [`sources/taxonomy.json`](../sources/taxonomy.json): each node has a `question` (a literal true/false statement about `source` that states the exploitable impact), `sources`, and `code_patterns`.

## Tree

- **access_control** (Access control and privilege): Privileged state changes or fund movements reachable by callers who should not have that power.
- **proxy_upgradeability** (Proxy, upgradeability, and storage layout): Proxy, clone, and upgrade patterns whose storage, initialization, or upgrade authority can be abused.
- **oracle_price_manipulation** (Oracle and price manipulation): Prices or exchange rates that attackers can manipulate or that are consumed without validation.
- **flash_loan_economic** (Flash-loan and economic attacks): Economic mechanisms whose assumptions break when an attacker has large transient capital or multi-step control.
- **reentrancy** (Reentrancy): External calls that let an attacker re-enter before state is consistent.
- **accounting_share_math** (Accounting and share math): Internal bookkeeping of deposits, shares, debt, fees, and rewards that diverges from reality.
- **arithmetic_precision** (Arithmetic and precision): Math errors in rounding, scaling, casting, and overflow that users can exploit.
- **signature_replay** (Signatures and replay): Off-chain signatures, permits, and meta-transactions that can be forged, replayed, or misused.
- **cross_chain_messaging** (Cross-chain, bridge, and L2 messaging): Message passing between chains or layers where sender, payload, or delivery is not validated.
- **external_call_token_integration** (External calls and token integration): Unsafe assumptions about external contracts and tokens: return values, fee-on-transfer, rebasing, approvals, arbitrary targets.
- **business_logic_state_machine** (Business logic, input validation, and state machine): Protocol rules implemented incorrectly: missing validation, broken state transitions, wrong ordering, or violated invariants.
- **dos_griefing** (Denial of service and griefing): Ways an attacker can block operations or permanently lock funds, even without profit.
- **frontrunning_mev** (Front-running, MEV, and randomness): Transaction-ordering dependence, missing slippage/deadline protection, and predictable randomness.
- **legacy_low_level** (Legacy and low-level EVM pitfalls): Classic EVM hazards: tx.origin auth, delegatecall to untrusted code, selfdestruct, storage/assembly misuse, hash collisions.

## Sources and how they were reconciled

- [OWASP Smart Contract Top 10 2025](https://owasp.org/www-project-smart-contract-top-10/) and [2026](https://scs.owasp.org/sctop10/) (the 2026 list is built from 122 deduplicated 2025 incidents, about $905M in losses): these set the backbone. Access control, oracle manipulation, logic errors, input validation, reentrancy, unchecked external calls, flash loans, arithmetic, insecure randomness, and DoS each map to a category. 2026 adds Proxy & Upgradeability (SC10) and splits Arithmetic Errors (rounding and precision) from overflow (SC07 vs SC09). Both changes are adopted here.
- [SWC Registry](https://swcregistry.io/): deprecated, but it gives canonical IDs for the low-level issues (SWC-101, 104, 105, 106, 107, 109, 112, 113, 114, 115, 116, 117, 120, 121, 122, 124, 128, 133). Most of these fit inside a modern category. The rest go in `legacy_low_level`.
- [DASP Top 10](https://dasp.co/): 2018-era. It confirms reentrancy, access control, arithmetic, unchecked calls, DoS, bad randomness, front-running, and time manipulation. Short addresses and "unknown unknowns" were dropped or folded into other categories.
- [Immunefi severity classification](https://immunefi.com/immunefi-vulnerability-severity-classification-system-v2-3/): an impact-based system (direct theft, permanent or temporary freezing, protocol insolvency, theft of unclaimed yield, griefing). Every question states one of these impacts, and gas and informational issues are excluded, so a "yes" means something reportable.
- [Solodit](https://solodit.cyfrin.io/) finding tags and the [Cyfrin](https://updraft.cyfrin.io/) audit checklists: these supplied audit-frequency detail that the top-10 lists lack. Examples are ERC4626 share inflation, reward accounting, fee-on-transfer and weird ERC20s, slippage and deadline, rounding direction, liquidation logic, and LayerZero/CCIP receivers.
- [Consensys smart-contract best practices: known attacks](https://consensys.github.io/smart-contract-best-practices/attacks/) and [Trail of Bits (not so) smart contracts](https://github.com/crytic/not-so-smart-contracts) plus the ToB token-integration checklist: sources for the reentrancy variants, DoS, front-running, and the `legacy_low_level` and token-integration patterns.
- Loss-weighted DeFi data from [Halborn Top 100 DeFi Hacks 2025](https://www.halborn.com/reports/top-100-defi-hacks-2025) and the [rekt.news](https://rekt.news/leaderboard/) and DefiLlama hack lists: these justify making `cross_chain_messaging`, `accounting_share_math`, and `flash_loan_economic` separate top-level categories even though no single top-10 list has all three. Bridges and accounting/rounding bugs (for example the 2025 Balancer V2 rounding exploit) account for a large share of losses.

Reconciliation rules:
1. Categories are organized by root-cause mechanism, which is what a classifier can see in one file. Impact is not a category; each question states it.
2. Overlapping labels were merged. "Logic errors" and "input validation" became `business_logic_state_machine`. "Insecure randomness" went under `frontrunning_mev` because both are ordering and predictability problems.
3. Off-chain key compromise and phishing cause the largest real losses but are not visible in source code, so they are excluded. On-chain privilege design stays in `access_control`.
4. Known overlaps are deliberate: donatable share-price oracles (oracle vs accounting), liquidation (economic vs logic), and initializers (access control vs proxy). Detectors can hang off either parent.
5. Best-practice and informational items have no question, even when a contest rated them Medium. Examples are single-step ownership transfer (a typo'd new owner, with no attacker) and a floating `pragma` (a compiler or target-chain choice made at deployment). Neither is an exploitable flaw in the code as written, and a linter finds both deterministically. The Beedle benchmark keeps them in the ground truth (M-6, M-9), so they show as misses there.
