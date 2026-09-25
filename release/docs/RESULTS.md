# Research results

The frozen detector flagged at least one declared attack transaction in 42 of 50 historical incidents. It flagged 55 of the 70 declared attack transactions and five other transactions among 12,947 transactions in the same attack blocks.

These are results from a calibration-exposed research dataset. They are not an estimate of how often the detector will catch an unseen attack, and they do not establish that it could have prevented these losses.

## What the counts mean

| Measure | Frozen result | Meaning |
|---|---:|---|
| Incidents with an attack alert | 42/50 (84%) | At least one declared attack transaction alerted. |
| Attack transactions alerted | 55/70 (78.6%) | Each declared transaction is judged separately. |
| Incidents with every declared transaction alerted | 35/50 (70%) | No declared attack transaction was missed in that incident. |
| Potential false positives | 5/12,947 other transactions | These alerts were not among the declared attack transactions. Their benignness is not assumed. |

An incident's declared transactions are the selected hashes in the [incident manifest](../evidence/incidents.json). They need not include every preparation, execution, laundering, or recovery transaction associated with that incident. Catching a later withdrawal does not mean catching the initial compromise.

The [saved detector](../evidence/detector.json) uses model `jev-1.13.0`, historical facts version 10, and two questions over an R2 fact sheet. Either score at or above 0.70 produces an alert. There is no ranking or quota: zero, one, or every transaction in a block can alert. The scores are not calibrated probabilities. The [question review](QUESTIONS.md) contains the exact wording and its pending human-review status.

## The 50 historical incidents

The table is derived from the [frozen scores](../evidence/historical.jsonl). Counts are flagged / declared attack transactions. Explorer links identify the declared transactions; source reports and exact hashes are also in the [manifest](../evidence/incidents.json). A positive count says that the detector alerted, not that it explained the published exploit mechanism correctly.

| Incident | Date | Flagged | Declared transactions |
|---|---|---:|---|
| Resupply | 2025-06-26 | 1/1 | [1](https://etherscan.io/tx/0xffbbd492e0605a8bb6d490c3cd879e87ff60862b0684160d08fd5711e7a872d3) |
| Conic ETH omnipool | 2023-07-21 | 1/1 | [1](https://etherscan.io/tx/0x8b74995d1d61d3d7547575649136b8765acb22882960f0636941c44ec7bbe146) |
| Pike Finance | 2024-04-30 | 1/1 | [1](https://etherscan.io/tx/0xe2912b8bf34d561983f2ae95f34e33ecc7792a2905a3e317fcc98052bce66431) |
| Socket/Bungee | 2024-01-16 | 1/1 | [1](https://etherscan.io/tx/0xc6c3331fa8c2d30e1ef208424c08c039a89e510df2fb6ae31e5aa40722e28fd6) |
| Hedgey | 2024-04-19 | 1/2 | [1](https://etherscan.io/tx/0xa17fdb804728f226fcd10e78eae5247abd984e0f03301312315b89cae25aa517), [2](https://etherscan.io/tx/0x2606d459a50ca4920722a111745c2eeced1d8a01ff25ee762e22d5d4b1595739) |
| Summer.fi Lazy Summer | 2026-07-06 | 1/1 | [1](https://etherscan.io/tx/0x0db528c44f23fc7fa4544684a2fab81096450a14aae8bc89f42cd0592d43da12) |
| Flamincome VaultYUSDT | 2026-09-16 | 1/1 | [1](https://etherscan.io/tx/0x5ff8150482f5473bff16b4a142a98a7f72b159df5e9dd38afd90470551640d37) |
| rsETH Safe module | 2026-09-15 | 0/1 | [1](https://etherscan.io/tx/0x0e7680b06cb8a6f86c149d9ba90d98e3d334e7b072dde03909d43fcfd98a8705) |
| Notional V1 escrow | 2026-09-03 | 1/2 | [1](https://etherscan.io/tx/0xe1589a19fe742f0d553889214abade69551fe944acffac014c28cc07b325d60a), [2](https://etherscan.io/tx/0xc3f3e318f7ab2d0daaba59e6ec901d25d1fe8a89aafe2b2b62e3b9aee1a24efa) |
| Ajna v2 | 2026-08-28 | 1/1 | [1](https://etherscan.io/tx/0x12dfde527ef62882bfabb64362c9ae0e6bfb628363bd298d0d0956c9a114e4f5) |
| TrustedVolumes | 2026-05-07 | 1/1 | [1](https://etherscan.io/tx/0xc5c61b3ac39d854773b9dc34bd0cdbc8b5bbf75f18551802a0b5881fcb990513) |
| Ekubo EVM v2 | 2026-05-05 | 1/1 | [1](https://etherscan.io/tx/0x770bc9a1f7c32cb63a5002b9ceb5c7994cd3af0fc6b2309cb32d3c46f629daa0) |
| Aztec V1 escape hatch | 2026-06-17 | 3/3 | [1](https://etherscan.io/tx/0xab306cd2184d23b6ba3e151b10b3b9a0b81f211cc16f4f3b0c79f0b17a59c2b5), [2](https://etherscan.io/tx/0x5c196c37a109d74c9797254287a0331f30e0daa637af241bd28fdc43774705c3), [3](https://etherscan.io/tx/0x9e1d6ab7c20ae235409d7dd3a9cd47c04f07293585b3498b8beed82d6f6b03ca) |
| Token of Power | 2026-06-09 | 1/1 | [1](https://etherscan.io/tx/0x967aa34c69b7775c718545c7f94d92e965eb5fc553c0f27f6f1a9c65c93ac156) |
| Yearn yETH | 2025-11-30 | 1/1 | [1](https://etherscan.io/tx/0x53fe7ef190c34d810c50fb66f0fc65a1ceedc10309cf4b4013d64042a0331156) |
| Balancer V2 | 2025-11-03 | 1/2 | [1](https://etherscan.io/tx/0x6ed07db1a9fe5c0794d44cd36081d6a6df103fab868cdd75d581e3bd23bc9742), [2](https://etherscan.io/tx/0xd155207261712c35fa3d472ed1e51bfcd816e616dd4f517fa5959836f5b48569) |
| Abracadabra | 2025-10-04 | 1/1 | [1](https://etherscan.io/tx/0x842aae91c89a9e5043e64af34f53dc66daf0f033ad8afbf35ef0c93f99a9e5e6) |
| SuperRare | 2025-07-28 | 1/1 | [1](https://etherscan.io/tx/0xd813751bfb98a51912b8394b5856ae4515be6a9c6e5583e06b41d9255ba6e3c1) |
| Silo pre-release leverage contract | 2025-06-25 | 1/1 | [1](https://etherscan.io/tx/0x1f15a193db3f44713d56c4be6679b194f78c2bcdd2ced5b0c7495b7406f5e87a) |
| Cork | 2025-05-28 | 0/1 | [1](https://etherscan.io/tx/0xfd89cdd0be468a564dd525b222b728386d7c6780cf7b2f90d2b54493be09f64d) |
| Bybit Safe | 2025-02-21 | 4/5 | [1](https://etherscan.io/tx/0x46deef0f52e3a983b67abf4714448a41dd7ffd6d32d32da69d62081c68ad7882), [2](https://etherscan.io/tx/0xb61413c495fdad6114a7aa863a00b2e3c28945979a10885b12b30316ea9f072c), [3](https://etherscan.io/tx/0xbcf316f5835362b7f1586215173cc8b294f5499c60c029a3de6318bf25ca7b20), [4](https://etherscan.io/tx/0xa284a1bc4c7e0379c924c73fcea1067068635507254b03ebbbd3f4e222c1fae0), [5](https://etherscan.io/tx/0x847b8403e8a4816a4de1e63db321705cdb6f998fb01ab58f653b863fda988647) |
| vETH/Vista | 2024-11-14 | 3/3 | [1](https://etherscan.io/tx/0x900891b4540cac8443d6802a08a7a0562b5320444aa6d8eed19705ea6fb9710b), [2](https://etherscan.io/tx/0x1ae40f26819da4f10bc7c894a2cc507cdb31c29635d31fa90c8f3f240f0327c0), [3](https://etherscan.io/tx/0x90db330d9e46609c9d3712b60e64e32e3a4a2f31075674a58dd81181122352f8) |
| Onyx DAO | 2024-09-26 | 1/1 | [1](https://etherscan.io/tx/0x46567c731c4f4f7e27c4ce591f0aebdeb2d9ae1038237a0134de7b13e63d8729) |
| Shezmu | 2024-09-20 | 0/1 | [1](https://etherscan.io/tx/0x39328ea4377a8887d3f6ce91b2f4c6b19a851e2fc5163e2f83bbc2fc136d0c71) |
| Penpie | 2024-09-03 | 2/3 | [1](https://etherscan.io/tx/0x56e09abb35ff12271fdb38ff8a23e4d4a7396844426a94c4d3af2e8b7a0a2813), [2](https://etherscan.io/tx/0x7e7f9548f301d3dd863eac94e6190cb742ab6aa9d7730549ff743bf84cbd21d1), [3](https://etherscan.io/tx/0x42b2ec27c732100dd9037c76da415e10329ea41598de453bb0c0c9ea7ce0d8e5) |
| LI.FI | 2024-07-16 | 1/1 | [1](https://etherscan.io/tx/0xd82fe84e63b1aa52e1ce540582ee0895ba4a71ec5e7a632a3faa1aff3e763873) |
| Floor Protocol | 2023-12-17 | 3/3 | [1](https://etherscan.io/tx/0xa329b27fbe0f7b7f92060a9e5370fdf03d60e5c4835f09d7234e5bbecf417ccf), [2](https://etherscan.io/tx/0xec8f6d8e114caf8425736e0a3d5be2f93bbea6c01a50a7eeb3d61d2634927b40), [3](https://etherscan.io/tx/0xfb9942a119c45adab3980639cd829e57b41449e3b82d610892da4bb921e81d9c) |
| GoodDollar | 2023-12-16 | 1/1 | [1](https://etherscan.io/tx/0x726459a46839c915ee2fb3d8de7f986e3c7391c605b7a622112161a84c7384d0) |
| KyberSwap Elastic | 2023-11-22 | 1/1 | [1](https://etherscan.io/tx/0x485e08dc2b6a4b3aeadcb89c3d18a37666dc7d9424961a2091d6b3696792f0f3) |
| Raft | 2023-11-10 | 1/1 | [1](https://etherscan.io/tx/0xfeedbf51b4e2338e38171f6e19501327294ab1907ab44cfd2d7e7336c975ace7) |
| MEV bot 0x05f016…924a5 | 2023-11-07 | 1/1 | [1](https://etherscan.io/tx/0xbc08860cd0a08289c41033bdc84b2bb2b0c54a51ceae59620ed9904384287a38) |
| Orbit Chain | 2023-12-31 | 3/3 | [1](https://etherscan.io/tx/0xe0bada18fdc56dec125c31b1636490f85ba66016318060a066ed7050ff7271f9), [2](https://etherscan.io/tx/0x639d27e564214411ad8eb06cf00d85cd90f83503a53ab5bf35dd5c6e1148ae0a), [3](https://etherscan.io/tx/0x64a6f486c20671e1389b3c7948d46733325c407245a86bf510cb69ef401a3f0e) |
| Rubic | 2022-12-25 | 1/2 | [1](https://etherscan.io/tx/0x9a97d85642f956ad7a6b852cf7bed6f9669e2c2815f3279855acf7f1328e7d46), [2](https://etherscan.io/tx/0x6551b933b984342fd353d4b522aee7db500900e208dc1337b0c1f17647e36e56) |
| ElasticSwap | 2022-12-13 | 1/1 | [1](https://etherscan.io/tx/0xb36486f032a450782d5d2fac118ea90a6d3b08cac3409d949c59b43bcd6dbb8f) |
| DFX | 2022-11-10 | 2/2 | [1](https://etherscan.io/tx/0x390def749b71f516d8bf4329a4cb07bb3568a3627c25e607556621182a17f1f9), [2](https://etherscan.io/tx/0x6bfd9e286e37061ed279e4f139fbc03c8bd707a2cdd15f7260549052cbba79b7) |
| Team Finance | 2022-10-27 | 1/1 | [1](https://etherscan.io/tx/0xb2e3ea72d353da43a2ac9a8f1670fd16463ab370e563b9b5b26119b2601277ce) |
| TempleDAO | 2022-10-11 | 0/1 | [1](https://etherscan.io/tx/0x8c3f442fc6d640a6ff3ea0b12be64f1d4609ea94edd2966f42c01cd9bdcf04b5) |
| Beanstalk | 2022-04-17 | 1/1 | [1](https://etherscan.io/tx/0xcd314668aaa9bbfebaf1a0bd2b6553d01dd58899c508d4729fa7311dc5d33ad7) |
| Value DeFi | 2020-11-14 | 0/1 | [1](https://etherscan.io/tx/0x46a03488247425f845e444b9c10b52ba3c14927c687d38287c0faddc7471150a) |
| Warp Finance | 2020-12-17 | 1/1 | [1](https://etherscan.io/tx/0x8bb8dc5c7c830bac85fa48acad2505e9300a91c3ff239c9517d0cae33b595090) |
| Cheese Bank | 2020-11-06 | 0/1 | [1](https://etherscan.io/tx/0x600a869aa3a259158310a233b815ff67ca41eab8961a49918c2031297a02f1cc) |
| Revest | 2022-03-27 | 1/1 | [1](https://etherscan.io/tx/0xe0b0c2672b760bef4e2851e91c69c8c0ad135c6987bbf1f43f5846d89e691428) |
| Inverse Frontier | 2022-06-16 | 0/1 | [1](https://etherscan.io/tx/0x958236266991bc3fe3b77feaacea120f172c0708ad01c7a715b255f218f9313c) |
| bZx Fulcrum | 2020-02-15 | 1/1 | [1](https://etherscan.io/tx/0xb5c8bd9430b6cc87a0e2fe110ece6bf527fa4f170a4bc8cd032f768fc5219838) |
| bZx oracle manipulation | 2020-02-18 | 1/1 | [1](https://etherscan.io/tx/0x762881b07feb63c436dee38edd4ff1f7a74c33091e534af56c9f7d49b5ecac15) |
| Balancer V1 STA/STONK | 2020-06-28 | 1/2 | [1](https://etherscan.io/tx/0x013be97768b702fe8eccef1a40544d5ecb3c1961ad5f87fee4d16fdc08c78106), [2](https://etherscan.io/tx/0xeb008786a7d230180dbd890c76d6a7735430e836d55729a3ff6e22e254121192) |
| Pickle pDAI | 2020-11-21 | 0/1 | [1](https://etherscan.io/tx/0xe72d4e7ba9b5af0cf2a8cfb1e30fd9f388df0ab3da79790be842bfbed11087b0) |
| Cream yUSD | 2021-10-27 | 1/1 | [1](https://etherscan.io/tx/0x0fe2542079644e107cbf13690eb9c2c65963ccb79089ff96bfaf8dced2331c92) |
| xToken xBNTa/xSNXa | 2021-05-12 | 1/1 | [1](https://etherscan.io/tx/0x7cc7d935d895980cdd905b2a134597fb91004b5d551d6db0fb265e3d9840da22) |
| xToken xSNX | 2021-08-29 | 1/1 | [1](https://etherscan.io/tx/0x924e6a6288587b497f73ddcf6ae3c184f15ab35dfcb85f3074b55266974029ef) |

## What the detector missed

Eight incidents had no attack alert. Their observed mechanisms suggest where transaction-local summaries lack enough authorization, accounting, or valuation context:

| Incident | Missing distinction |
|---|---|
| rsETH Safe module | Caller-controlled delegatecall through an enabled module into a victim Safe. A permitted execution path need not represent the owner's intent. |
| Cork | Crafted market data accepted through a callback, leading to redemption-asset issuance. The summary did not establish why that issuance was invalid. |
| Shezmu | Borrowing against collateral the caller could fabricate. A recorded borrow does not prove sound collateral. |
| TempleDAO | An unprotected migration path created a withdrawable balance without the required prior position. |
| Value DeFi | Manipulated pool valuation affected vault share minting and redemption. |
| Cheese Bank | Manipulated collateral valuation supported an oversized borrow. |
| Inverse Frontier | Manipulated valuation enabled undercollateralized borrowing. |
| Pickle pDAI | A controller/upgrade path gave a malicious jar access to vault assets. |

Seven other incidents were partially caught. Hedgey's setup retained an approval before the later drain. Notional's first leg created claims before settlement. Balancer V2 first accrued an internal balance before withdrawal. Bybit's initial signed logic replacement did not alert, although four subsequent sweeps did. Penpie's middle reward-harvest leg, Rubic's second allowance drain, and Balancer V1's second drain also fell below the threshold.

These distinctions matter when evaluating prevention. An alert after the damaging action may help investigation or incident response without providing a useful pause window.

## What helped during calibration

The research began with broader questions and then traded a small amount of historical coverage for fewer potential false positives. The following stages summarize the retained experiment records. They are development results, not independent comparisons on an untouched test set. Their full intermediate inputs and outputs are not included in this compact public bundle.

| Development stage | Attack transactions alerted | Incidents with every declared transaction alerted | Potential false positives |
|---|---:|---:|---:|
| Before removing a broad extraction question | 61/70 | 41/50 | 66 |
| After removing that question | 57/70 | 37/50 | 19 |
| After removing the self-referential-price question | 56/70 | 36/50 | 10 |
| After requiring stronger internal-claim evidence | 55/70 | 35/50 | 7 |
| Current lending-accounting interpretation | 55/70 | 35/50 | 5 |

The current interpretation explicitly connects an established lender's Borrow event to a token issued to the borrower in the same transaction. This reduces alerts that treated lending-accounting issuance as an unrelated payment. The question still requires attention to authorization, collateral, debt-accounting, and extraction mismatches. A genuine debt record can coexist with an exploit.

The last transition preserved the aggregate coverage count but changed which attacks were caught: it lost Balancer V2's first declared transaction and gained Yearn yETH. Aggregate equality is not the absence of regressions.

Several changes were rejected or left inactive. Restoring historical-price compatibility recovered Akropolis but lost Origin Dollar in the separate measurement, leaving its total unchanged. Broader wording about authority, collateral, internal claims, or borrowing did not produce a qualifying gain with suitable controls. Some promising changes needed new source-controlled evidence or an independent validation case. Lowering the threshold or adding incident-specific exceptions was not used to erase these misses.

## Why five potential false positives, not three

The configured result remains five. Each row below is an alert outside the declared attack set, rather than a proven benign transaction.

| Transaction | Why it alerted | Follow-up interpretation |
|---|---|---|
| [Circle CCTP redemption](https://etherscan.io/tx/0x702533f7bef69458e82061d5a6ddafff4bc69e04f8eab627d6a58a9e1e2a34a0) | A 2 million USDC mint looked unsupported. | Source burn, message, recipient, and amount matched. Likely ordinary redemption. |
| [Alephium redemption](https://etherscan.io/tx/0x60720a5a46a40dd43b1124657e06f87ca0f5d7e0dfeb754f6a01dae7918749eb) | A 20,000 wrapped-ALPH mint looked unsupported. | Source custody increase and message matched the destination. Likely ordinary redemption. |
| [Aave V4 borrowing](https://etherscan.io/tx/0x7aa4993b5ceabfbb679882e05460b4292bf8f50e27878bec56eb9b97d7e29771) | A 120,000 USDT payout looked uncompensated. | Matching borrowing, debt shares, and later repayment support a loan explanation. Collateral provenance and authorization remain unresolved. |
| [Aave V3 borrowing](https://etherscan.io/tx/0x7dc0bea6bc48ee58dce85e56b5adc753884535e44576422bdaf389688c638736) | A 500,000 USDG payout still looked suspicious despite debt evidence. | Borrowing records and account state support a loan explanation. A healthy-looking account does not prove legitimate collateral provenance. |
| [PYUSD supply increase](https://etherscan.io/tx/0x001b48416f93297ddc8d6d8f74e64173caf9c41656f645a582b38b6f67544d3e) | About 829,162 PYUSD was minted to the caller without an observed payment. | The caller held the supply-controller role; later explorer attribution supports routine issuer activity. Off-chain backing and operator intent remain unverified. |

A bridge-source experiment suppressed the first two alerts while preserving historical coverage, giving three potential false positives. It was not activated: its attack guard had already been used during development, and suitable independent validation was missing. A separate borrowing experiment also reached three through different changes. Neither result replaces the configured five, and the reductions cannot be combined without another measurement.

These case interpretations summarize retained research notes. The public bundle includes the scores and transaction identities, not the complete cross-chain or historical-state adjudication evidence. Readers should independently verify an interpretation before using it to suppress alerts.

## Separate measurements

### Twenty consecutive blocks

The unchanged questions produced zero alerts across 5,420 transactions in blocks 26,042,369 through 26,042,388. The [ordinary-block scores](../evidence/ordinary-blocks.jsonl) preserve the transaction scores. This is a small consecutive observation with correlated activity, not a random sample of all chain behavior. Zero alerts does not establish that every transaction was benign or that future alert burden will be zero.

The verified public claim is 20 blocks. Larger partially collected or partially enriched samples are not included as completed alert measurements.

### Additional attack measurements

The retained research records also describe these separate measurements. Their detailed score bundles are not included here, so the offline evidence check does not reproduce them:

| Measurement | Attack result | Potential false positives | Interpretation |
|---|---:|---:|---|
| DBXen, sourced after the candidate was frozen | 1/1 | 0/179 other transactions | One fresh supporting case, not broad validation of the mechanism family. |
| OMNI404 | 1/1 | 0/79 | The case and an earlier result were already known. This was not a fresh holdout. |
| Separate coverage expansion | 7/10 | 0/1,022 | Six of nine full incidents plus a supplemental Seneca transaction; newer facts version 12. |

The expansion caught Harvest, Origin Dollar, Orion, Yearn iEarn, Uwerx, Seneca, and Fire Token. It missed Akropolis, the Aave ParaSwap repay adapter, and MetaPool. The questions and threshold were unchanged, but the newer fact representation prevents treating this as a simple extension of the historical facts-version-10 total.

### Bitget: two direct transfers did not alert

An exploratory check on September 24, 2026 scored two reported incident-linked transfers using the same questions and model, with facts version 12:

| Transfer | Lending-accounting score | Multi-pool score | Alert |
|---|---:|---:|---|
| [34,751,168.120990 USDT](https://etherscan.io/tx/0xa3ae35a0006ff4299f8f18614c2c21750eb8e0f5c047df4a526e1cc6ae599ce5) | 0.24 | 0.23 | No |
| [13,965.927231303 ETH](https://etherscan.io/tx/0x8469803a082c4d106c642874509ffb8b7a730cd52934ccd44af0c479d8f60bfa) | 0.24 | 0.16 | No |

The facts showed direct transfers rather than an observable smart-contract exploit. They did not include incident news, attacker attribution, or later movements. A compromised wallet can make a transaction that looks like an authorized payment. These two misses illustrate that boundary; they do not establish whole-incident coverage, the legitimacy of the payments, or the number of alerts in surrounding blocks. This exploratory result is separate from the benchmark and is not reproduced by the public score bundle.

## Limits on the claims

- Calibration exposure: the historical incidents and their neighboring alerts guided repeated changes. The 84% incident figure describes that dataset, not unseen generalization.
- Label look-ahead: the original extractor used a pinned public label dump assembled after many of the incidents. It filtered explicit exploit labels and applied contract-age checks, but historical label availability was not reconstructed for every input.
- Model memorization: removing hashes, addresses, and dates from R2 reduces direct identifiers. Protocol names and recognizable attack shapes remain. The results do not rule out model knowledge of famous incidents.
- Untrusted metadata: label and symbol filters limit text exposure; they are not a proof against prompt injection, misleading names, or malicious metadata.
- Heuristic facts: sender-control inference, accounting summaries, prices, and missing trace/state data can change a verdict. A score cannot recover facts omitted or misrepresented upstream.
- Unknown negative labels: transactions outside the declared attack set can include unrelated abuse or undeclared incident activity. The five alerts are potential false positives; conventional precision and a verified false-positive rate are not established.
- Provider and representation drift: rerunning with a different model, metadata snapshot, extraction version, or provider behavior can change scores. Even the same model identifier does not prove immutable provider behavior.
- Deployment gap: these are historical post-execution measurements. They establish neither sub-eight-second detection nor pending-transaction coverage. Mempool monitoring would also require appropriate pre-execution facts and cannot see private transactions.

Protocol-specific monitoring could add stronger invariants and authorization context. That is a research direction, not a measured improvement in this release.

## What is reproducible here

The public bundle supports offline arithmetic reproduction of the headline historical and 20-block results. [File digests](../evidence/manifest.json) identify the packaged files; [provenance](../evidence/provenance.json) records the original artifact digests and limitations. Digests detect changes relative to that manifest, not independent authenticity or correctness.

The original historical rows did not retain a complete model-input digest and model identifier on every row. The model is recorded at configuration level. The compact bundle therefore does not reproduce historical fact extraction, prove the provider's execution, or contain every intermediate experiment. Fresh end-to-end reproduction requires the corresponding raw data, metadata snapshots, exact fact representation, and provider access. Keep those limits separate from the offline check, which verifies the reported counts from the saved scores.
