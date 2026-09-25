# Release-candidate review

Reviewed September 25, 2026. This record describes preparation of the standalone candidate, not approval to publish the original research repository or a guarantee of security.

## What changed

The supported transaction pipeline is now a standalone package with explicit collection, cost preview, paid scoring and offline-results commands. Research experiments, private operational data and the legacy source scanner are outside its distribution boundary. Existing research files and scores were preserved.

Adversarial review covered security-research, AI-security, architecture and first-time-user perspectives. Findings led to fixes for concurrent budget reservations; malformed model responses; wallet and native/token alias collisions; unchecked NFT naming; malformed event layouts; incomplete or oversized collection files; invalid price metadata; label preparation consistency; request cancellation; mixer-log validation and atomic snapshots; and two unused-by-default rendering helpers. Installation now uses hash-pinned runtime, test and build dependencies.

Reviewers revisited those changes. Offline checks exercise complete collection through scoring using synthetic external responses, and reject malformed input without publishing a complete clean result. Network calls are forbidden during the test suite. Negative controls deliberately removed the budget lock, native-asset alias protection and price validation in memory; their corresponding regressions failed as expected. No paid classifier experiments were performed for this review.

## Verification and its limits

- A clean temporary Python 3.11 environment on macOS built a source archive and wheel. The installed CLI reproduced the saved metrics outside the research checkout without credentials. Linux and other supported Python versions have not received the same local installation check.
- A dependency advisory check of the pinned runtime, build and test packages found no known vulnerabilities on the review date. This is not a guarantee against undisclosed vulnerabilities or malicious packages.
- A local secret scan, with network verification disabled, found expected transaction/checksum hashes rather than credentials. Distribution membership was inspected separately. Do not include the original Git history, parent directory or a runtime workspace in the public repository.
- Exact questions and evidence digests were checked. The historical score arithmetic remains 42/50 incidents, 55/70 declared attacks and five potential false positives. This is not a fresh model evaluation or a measured claim for the hardened extractor.

The review did not establish prompt-injection immunity, lossless extraction, independent truth of external metadata, live-provider compatibility today, adversarial worst-case throughput or prevention of hacks. Complete block collection does not mean every semantic detail survives feature selection and rendering. Approval events and familiar event topics are observations, not proof of authorization. See `../SECURITY.md` and `RESULTS.md`.

## Owner decisions before publication

1. Personally review the exact questions and guidance in `QUESTIONS.md`; their status remains pending.
2. Confirm the transaction-only release boundary, MIT ownership notice and a private security-reporting contact.
3. Decide whether to perform an explicitly budgeted live smoke check before inviting external users. Online behavior was validated against synthetic boundaries, not a new paid provider run.
4. Authorize publication separately. Publish only the reviewed candidate contents, never the entire research workspace by accident.
