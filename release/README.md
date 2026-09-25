# Jevscan transaction monitor

Research software that turns blockchain transaction traces into structured facts and asks two fixed questions about possible exploitation. Each transaction is flagged independently at a fixed threshold. There is no ranking.

In the historical research cohort, it flagged at least one declared attack transaction in **42 of 50 incidents**, flagged **55 of 70 declared attack transactions**, and produced **5 potential false positives among 12,947 other transactions**. Those examples were used during calibration. These are research results, not a promise of future coverage. The hardened release extractor has different inputs and has not inherited those measurements.

This is a release candidate. It is not a live monitor, a mempool simulator, or an automatic pause system. Review [the exact questions](docs/QUESTIONS.md), [results and limitations](docs/RESULTS.md), [security guidance](SECURITY.md), and [release review](docs/RELEASE_REVIEW.md) before use.

## Install

Python 3.11 to 3.14 on macOS or Linux. Use the source checkout or source archive (the wheel alone does not include the evidence and documentation). From this directory:

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --require-hashes -r requirements.lock
python -m pip install --require-hashes -r requirements-build.lock
python -m pip install --no-deps --no-build-isolation .
```

## Reproduce the saved results offline

No credentials or provider calls:

```sh
jevscan-monitor results --evidence evidence
jevscan-monitor questions
```

The first command checks the evidence digests and recomputes the counts from stored scores. It does not rerun the model. The evidence includes every declared attack hash and every scored peer transaction.

## Evaluate historical blocks

Online collection needs an Alchemy archive mainnet RPC endpoint with block receipts and call traces, plus an Etherscan API key. NFT enrichment specifically depends on Alchemy's NFT API. Paid classification additionally needs a TypeSafe API key. Export these variables as shown in `.env.example`; the application does not load that file automatically.

```sh
export JEVSCAN_DATA_DIR="$PWD/workspace"
jevscan-monitor prepare
jevscan-monitor collect --start-block 22785461 --end-block 22785461 --output workspace/resupply.json
jevscan-monitor preflight --input workspace/resupply.json
jevscan-monitor score --input workspace/resupply.json --output workspace/resupply-scores.json --budget-usd 1 --allow-paid --acknowledge-unreviewed-questions
```

Collection accepts complete, finalized blocks, up to 20 per command. Initial label and mixer-index preparation can take time and use RPC quota. RPC/explorer pricing is separate from classifier costs. Collection uses public metadata services; classification sends rendered transaction facts to TypeSafe. There is no signing key or transaction-submission feature.

Scoring uses the pinned model and exact questions. If that model is unavailable, it stops rather than substituting another model. The budget is a conservative local workspace ceiling using an explicit price assumption, not a provider billing guarantee. Use provider-side quotas too. Uncertain requests retain their spending reservations and are not automatically retried.

## Where this could go

A production service could follow new blocks and maintain reusable state, but this repository does not implement that service or establish a latency guarantee. Public-mempool use would additionally require pending-transaction simulation and complete enough inputs; lifting provider rate limits alone is insufficient. Private transactions would remain unseen before inclusion.

A protocol-specific deployment could add known invariants, roles and accounting rules, reducing uncertainty about external systems. Better coverage is a hypothesis to evaluate with independent attack and normal-activity examples, not a measured result here.

## Development

```sh
python -m pip install --require-hashes -r requirements-test.lock
python -m pytest
```

The runtime lives in `src/jevscan_monitor/`; curated scores and provenance live in `evidence/`. The original exploratory scripts, private caches and legacy source-code scanner are deliberately outside this release candidate. See [notices](NOTICE.md) for provenance and distribution boundaries.
