# Detector questions for human review

Human review is pending. These are the two unchanged questions behind the published historical results, including the complete guide. Review them before authorizing live classification or changing their wording. A wording change creates a new detector and needs a separately identified measurement.

The machine-readable source is [detector.json](../evidence/detector.json). Its `human_review` field is `pending`. This document does not grant approval, and the historical results are not evidence that the wording is safe for automated incident response.

## Decision rule

A transaction alerts when either question's score is at least 0.70. The detector does not rank transactions, average the scores, or require a fixed number of alerts. A score is a model output, not a calibrated probability of an attack.

The recorded model is `jev-1.13.0`, the view is `R2`, and the historical 50-incident measurement uses facts version 10. Later measurements with newer facts are reported separately in [Results](RESULTS.md). Exact question hashes use SHA-256 over `json.dumps(question, sort_keys=True, separators=(",", ":")).encode()`; the human-readable formatting below does not define the hash.

| Question identifier | Recorded SHA-256 |
|---|---|
| `c23_guided_lending_accounting_context` | `0f0abd880284714756646d57285d5a8b0c94a2a021bda2a6214241bd3e2507cc` |
| `p10_multi_pool_depletion` | `60b489739ca1701dc54401044bd25d757f69e31c0ba21ceb7b9f441509901f87` |

## Question 1: exploitation with lending-accounting context

This question asks whether the sender gains value through a flaw in contract logic, pricing, or access control. Its lending clarification distinguishes a recorded debt-accounting issuance from an unrelated payment. It does not establish whether collateral or authorization is legitimate.

The following JSON is the complete question, including all guidance, without wording changes:

```json
{
  "criteria": {
    "false": "Ordinary protocol use, including trading, lending, liquidation, arbitrage and other MEV, bridging, claims, deployments, and administrative actions by established operators, even when large or complex. Also a failed transaction, which takes nothing. When the facts directly link an established lender's Borrow event to a token issuance by that lender to the borrower in the same transaction, treat that issuance as part of the recorded lending operation rather than an independent payment. This alone does not establish authorization or adequate collateral; alert only when the facts show a concrete authorization, collateral, debt-accounting, or extraction mismatch.",
    "true": "The sender or the sender's contracts end up with substantial value that a protocol or its users did not intend to give, obtained by abusing a flaw in contract logic, pricing, or access control."
  },
  "instructions": {
    "guidance": {
      "definition": "An exploit takes value from a protocol or its users in a way the protocol did not intend.",
      "not_suspicious_alone": [
        "size",
        "complexity",
        "a flash loan"
      ],
      "signs_that_a_complex_transaction_is_normal": [
        "arbitrage and sandwich bots swap in a cycle, every pool is paid about what it gives out, profit is small next to the amounts swapped, the bot contract is old and reused, and the builder is tipped",
        "liquidations go through the protocol's own liquidation function and earn a modest bonus",
        "keepers, harvesters, oracle updaters, and bridge relayers are established operators doing repeated jobs"
      ],
      "signs_that_raise_suspicion": [
        "the sender's wallet is new, has few prior transactions, or was funded through a mixer",
        "the sender acts through its own unverified contract, created minutes or hours earlier",
        "the capital comes from a flash loan, and the sender side ends with a large gain while risking none of its own funds",
        "an established contract loses a large share of an asset it holds and receives little in return",
        "a protocol is entered again through the sender's contract before its first call has finished",
        "a price or pool balance is pushed sharply, used for a borrow, mint, redeem, or liquidation, and then pushed back",
        "an administrative function is called by an address with no visible role in that protocol",
        "tokens are pulled from many unrelated wallets through allowances",
        "assets are minted or released with no matching deposit, lock, or burn"
      ]
    },
    "question": "The transaction described in the state is an attack that exploits a flaw in a smart contract protocol to take funds from the protocol or its users."
  },
  "type": "noul"
}
```

## Question 2: multi-pool depletion

This narrower question requires linked proceeds from uncompensated losses in multiple established pools, using a fresh sender-controlled contract and transient capital. These requirements can reduce alerts on ordinary swaps while missing attacks that do not fit that shape.

```json
{
  "criteria": {
    "false": "The available facts are adequately explained by ordinary authorized activity, such as an exchange for independently supported value, repayment, backed borrowing, a valid claim, an ordinary deployment, or an authorized control change. Size, complexity, new contracts, missing prices, a mixer, or a flash loan alone do not establish exploitation. A completely reverted transaction has no completed exploit effect.",
    "true": "The transaction extracts value through a concrete multi-pool depletion mechanism. Require a sender-controlled fresh contract to use flash liquidity or similarly transient capital while multiple established pools lose meaningful pre-existing balances without recorded compensation, and the sender's side or a recipient it controls receives the resulting proceeds. Repeated swaps, burns, callbacks, or an ordinary arbitrage route do not suffice on their own: identify the uncompensated loss from more than one established pool and the linked beneficiary."
  },
  "instructions": "The transaction described in the state carries out a smart-contract exploit, including an exploit-enabling change or an unauthorized economic benefit.",
  "type": "noul"
}
```

## What R2 contains

R2 is a structured summary produced by the research fact extractor, not the raw transaction or a full contract audit. It describes the sender and entry contract, net asset changes, flash borrowing, minted assets, lending-accounting issuance, allowance pulls and changes, internal balances, moved positions, inferred losses, control changes, reentrant calls, event summaries, and transaction shape. Where available, it includes earlier activity in the selected window, contract ages, prices, and block-builder payments.

The original renderer substitutes aliases for addresses and excludes transaction hashes, dates, and block numbers. It retains approved protocol labels and token symbols, so it is not fully anonymous. Approximate value descriptions and heuristics help compress the input, but they can omit economically significant distinctions. Some sender-control and ordinary-activity descriptions are inferences rather than proven ownership or authorization facts.

Ground-truth incident membership and attacker labels belong in evaluation data, not in the submitted fact sheet. An arbitrary JSON object is not an equivalent R2 input merely because it uses the same field names. The release's saved scores do not certify a new upstream extractor or user-supplied state.

## Review points before approval

- Definition of harm: the guide treats arbitrage, sandwiches, and standard liquidations as normal for this smart-contract-exploit classification. That is not a claim that every such action is harmless to users.
- Authorization: old contracts, established operators, valid roles, debt records, and signed transactions can all participate in a compromise. These features cannot settle operator intent.
- Missing evidence: an absent deposit or repayment in a transaction-local view can be explained by earlier collateral, cross-chain backing, or off-chain issuance. Missing facts should not be silently interpreted as proof of a flaw.
- Heuristic bias: wallet age, mixer funding, contract verification, and transaction size are contextual features. They can describe legitimate users or be manipulated by attackers.
- Input integrity: untrusted labels, token metadata, logs, and source text can contain misleading instructions. Character filters and structured JSON do not establish prompt-injection resistance.
- Scope: key theft and direct wallet transfers may look ordinary in these facts. Attacks that require protocol-specific invariants can also be missed.
- Action boundary: an alert is a reason to investigate. These questions alone do not justify an automatic pause, transaction, accusation, or other external action.

Approval should record the reviewer, exact question hashes, intended input contract, and intended use. If the review leads to edits, preserve the historical questions and results as a separate version rather than rewriting their meaning retroactively.
