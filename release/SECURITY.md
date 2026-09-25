# Security and responsible use

This is research software, not a protection boundary. An unflagged transaction is not proven safe; a flagged transaction is not proven malicious. Never connect these scores directly to signing keys, contract administration, automatic pauses, withdrawals or other irreversible actions. This package has no transaction-submission feature.

## Before running

- Use a dedicated, unprivileged account and a private workspace you own. Do not share writable caches or spending ledgers with other users or accept someone else's workspace as trusted.
- Use scoped API keys with provider-side quotas. Do not put keys in command arguments, commits, screenshots or reports. Environment variables are read explicitly; `.env` files are not loaded automatically.
- Review `docs/QUESTIONS.md`. The bundled questions deliberately remain marked `pending` human review. The explicit acknowledgment flag is not a security endorsement.
- Expect transaction data, metadata and even apparently familiar labels to be adversarial. Text filtering reduces exposure; it does not prove resistance to prompt injection or semantic evasion.
- Keep Python and pinned dependencies current. A clean dependency advisory scan is only a point-in-time check.

## Data and network boundaries

Collection reads mainnet RPC data from the configured HTTPS Alchemy endpoint, public label files from GitHub, historical prices from DefiLlama, explorer metadata from Etherscan and current NFT metadata from Alchemy. These services can observe the requests. Classification sends rendered transaction facts and the two questions to TypeSafe over HTTPS. Do not use the tool on confidential transaction data without permission to send it there.

TLS and schema checks do not prove provider honesty. Complete finalized-block checks verify consistency against one provider, not independent consensus. File digests catch accidental modification, not a malicious writer who can replace both content and digest. Cache contents and the local ledger are trusted owner-controlled state, not signed audit records.

Collection rejects unsupported complexity, missing data and inconsistent block identities instead of declaring a partial block clean. A failed run does not write a complete score output. Some successful raw responses are cached locally; do not publish the workspace. Error output intentionally omits raw provider bodies and credential-bearing URLs. Scrubbing is defense in depth, not a guarantee that arbitrary sensitive data can safely be logged or shared.

## Paid calls

Classification requires explicit `--allow-paid`, a positive workspace budget and the pinned model. Requests are serialized within the workspace; a process lock excludes concurrent writers. A durable reservation is recorded before each request. A timeout or malformed response retains that reservation and is not retried automatically.

The calculation assumes $0.042 per million input tokens and reserves 55,000 input tokens per request. These are local assumptions, not a provider-enforced maximum charge or a pricing contract. Changed pricing, provider-side accounting, tax, other accounts and RPC/explorer costs are outside that estimate. Apply provider-side quotas; do not delete the ledger to bypass a reservation you have not reconciled.

## Research limitations

The original calibration cohort was reused while choosing questions and thresholds. Current label dumps, present explorer verification status and NFT metadata can introduce hindsight. NFT values combine current floors with historical ETH prices; they are not historical NFT valuations. Incomplete accounting, missing off-chain authorization and cross-transaction context can hide attacks. Model scores are not calibrated probabilities. The hardened extractor changes inputs and has not been given a new paid coverage benchmark. See `docs/RESULTS.md` for the measured version and misses.

The command-line tool is bounded historical-block research tooling. It has not been validated as an internet-facing multi-tenant service, a live monitor or a mempool simulator. Resource limits intentionally exclude some complex transactions; failure means not evaluated, not benign.

## Reporting a problem

Do not post credentials, private cache files or exploit details that endanger a live protocol in a public issue. Ask the repository owner for a private reporting channel first. This release candidate does not yet designate a monitored security contact or promise a response time; the owner must set that policy before publication.
