# Architecture

The package has one supported command-line entry point, `jevscan-monitor`.

1. `prepare` downloads filtered labels and atomically builds a finalized mixer-payout index. It makes no classifier calls.
2. `collect` checks complete finalized blocks, receipts and call traces; extracts observations; adds external metadata; and renders transaction facts in order. A self-checksummed collection is saved only after canonical block identities are checked again.
3. `preflight` validates a saved collection and estimates the maximum local spending reservation. It does not contact a provider.
4. `score` validates the same collection and exact question bundle, uses a fixed model through the budgeted client, and writes output only when all transactions have valid scores. Each transaction independently crosses a fixed threshold or does not; transactions are never ranked.
5. `results` independently checks the curated historical evidence and recomputes published counts. It is not an execution of today's model or extractor.

`inputs` owns raw-chain bounds and structural checks; `facts` owns extraction and actor/asset naming; `enrich`, `labels`, `mixers` and `rpc` own observations from outside a transaction; `views` owns rendering; `provider` owns paid-call consent, accounting and response validation; `evaluation` owns the frozen evidence verifier. The CLI does not import the parent repository or experimental research scripts.

The facts schema is version 13 for the hardened release. Published headline scores were produced with version 10. The exact original questions are retained for human review, but preserving questions does not make these different input pipelines statistically equivalent.

Use a private workspace. This is a single-owner, single-writer research application, not a shared cache service. The most important trust boundaries and limitations are in `SECURITY.md`.
