```
     ██╗███████╗██╗   ██╗███████╗ ██████╗ █████╗ ███╗   ██╗      ███████╗██╗   ██╗███╗   ███╗
     ██║██╔════╝██║   ██║██╔════╝██╔════╝██╔══██╗████╗  ██║      ██╔════╝██║   ██║████╗ ████║
     ██║█████╗  ██║   ██║███████╗██║     ███████║██╔██╗ ██║█████╗█████╗  ██║   ██║██╔████╔██║
██   ██║██╔══╝  ╚██╗ ██╔╝╚════██║██║     ██╔══██║██║╚██╗██║╚════╝██╔══╝  ╚██╗ ██╔╝██║╚██╔╝██║
╚█████╔╝███████╗ ╚████╔╝ ███████║╚██████╗██║  ██║██║ ╚████║      ███████╗ ╚████╔╝ ██║ ╚═╝ ██║
 ╚════╝ ╚══════╝  ╚═══╝  ╚══════╝ ╚═════╝╚═╝  ╚═╝╚═╝  ╚═══╝      ╚══════╝  ╚═══╝  ╚═╝     ╚═╝
```

**Produce a heat map of likely bugs - in seconds, for pennies - built with TypeSafe's [Jev](https://docs.typesafe.ai).**

## Quick start

Python 3.11+ and a TypeSafe API key ([console.typesafe.ai](https://console.typesafe.ai)).

### Installation

```sh
git clone https://github.com/devtooligan/jevscan-evm.git && cd jevscan-evm
pip install aiohttp
cp .env.example .env              # then set TYPESAFE_API_KEY in .env
```

### Usage

```sh
python jevscan.py /path/to/repo
```

Results land in `out/<repo>/HEATMAP.md`. Settings (which folder, which files, thresholds) live in `jevscan.toml`; pass your own overrides with `--config` — see [docs/CONFIG.md](docs/CONFIG.md).

## What it checks

| Layer      | Questions | From                                                                                                                                                                                 |
| ---------- | --------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| General    | 2         | "Is there any exploitable bug?" and "Is there a bug that lets an attacker steal or lock funds?"                                                                                      |
| Categories | 14        | OWASP Smart Contract Top 10, SWC, Immunefi ([TAXONOMY.md](docs/TAXONOMY.md))                                                                                                         |
| Detectors  | 343       | Sourced from [Cyfrin audit-checklist](https://github.com/Cyfrin/audit-checklist) (the Solodit checklist) and [evm-cortex](https://github.com/ccashwell/evm-cortex) by Chris Cashwell |

## Example: USSD

The [Sherlock USSD contest](https://github.com/sherlock-audit/2023-05-USSD) (May 2023), 8 of 12 files scanned: [`HEATMAP.md`](bench/ussd/run/HEATMAP.md).

> **89% chance of a critical bug · 91% chance of at least one exploitable bug · hottest file: `USSDRebalancer.sol`**

Speed and cost: One file, 14 checks:

- GPT-5.6 (high reasoning) 57 seconds and 3.9¢
- Jev 0.7 seconds and costing 0.015¢ -- about 80× faster and 260× cheaper.

| File                                | Crit | Any | Access | Proxy | Oracle | Econ | Reentry | Shares | Math | Sigs | Xchain | Tokens | Logic | DoS | MEV | LowLvl |
| ----------------------------------- | ---- | --- | ------ | ----- | ------ | ---- | ------- | ------ | ---- | ---- | ------ | ------ | ----- | --- | --- | ------ |
| `oracles/StableOracleDAI.sol`       | 🟨   | 🟧  | ⬜     | ⬜    | 🟥     | 🟩   | ⬜      | ⬜     | 🟧   | ⬜   | ⬜     | ⬜     | 🟩    | 🟩  | ⬜  | ⬜     |
| `USSDRebalancer.sol`                | 🟧   | 🟥  | 🟨     | 🟩    | 🟧     | 🟩   | 🟨      | 🟧     | 🟥   | ⬜   | ⬜     | 🟧     | 🟥    | 🟧  | 🟧  | ⬜     |
| `USSD.sol`                          | 🟥   | 🟥  | 🟧     | 🟨    | 🟧     | 🟨   | 🟨      | 🟨     | 🟧   | ⬜   | ⬜     | 🟧     | 🟥    | 🟨  | 🟥  | ⬜     |
| `oracles/StableOracleWBTC.sol`      | 🟨   | 🟧  | ⬜     | ⬜    | 🟥     | 🟩   | ⬜      | ⬜     | 🟨   | ⬜   | ⬜     | ⬜     | ⬜    | ⬜  | ⬜  | ⬜     |
| `oracles/StableOracleWETH.sol`      | 🟨   | 🟨  | ⬜     | ⬜    | 🟥     | ⬜   | ⬜      | ⬜     | 🟨   | ⬜   | ⬜     | ⬜     | ⬜    | ⬜  | ⬜  | ⬜     |
| `oracles/StableOracleWBGL.sol`      | 🟩   | 🟨  | ⬜     | ⬜    | 🟧     | ⬜   | ⬜      | ⬜     | 🟨   | ⬜   | ⬜     | ⬜     | ⬜    | ⬜  | ⬜  | ⬜     |
| `oracles/UniswapV3StaticOracle.sol` | 🟩   | 🟩  | ⬜     | ⬜    | 🟩     | ⬜   | ⬜      | ⬜     | 🟩   | ⬜   | ⬜     | ⬜     | 🟩    | ⬜  | ⬜  | ⬜     |
| `Migrations.sol`                    | ⬜   | 🟩  | ⬜     | ⬜    | ⬜     | ⬜   | ⬜      | ⬜     | ⬜   | ⬜   | ⬜     | ⬜     | ⬜    | ⬜  | ⬜  | ⬜     |

🟥 85% or more · 🟧 70% to 85% · 🟨 50% to 70% · 🟩 30% to 50% · ⬜ under 30%

### Strongest hits

| File                           | Function          | What it found                                                                       | Confidence | Line | Contest finding            |
| ------------------------------ | ----------------- | ----------------------------------------------------------------------------------- | ---------- | ---- | -------------------------- |
| `oracles/StableOracleDAI.sol`  | `getPriceUSD`     | Unsafe Chainlink price feed consumption without staleness/validity/sequencer checks | 97%        | 48   | H-1, H-4, M-1, M-7         |
| `oracles/StableOracleWBTC.sol` | `getPriceUSD`     | Unsafe Chainlink price feed consumption without staleness/validity/sequencer checks | 97%        | 23   | M-1, M-4, M-7              |
| `oracles/StableOracleWETH.sol` | `getPriceUSD`     | Unsafe Chainlink price feed consumption without staleness/validity/sequencer checks | 97%        | 23   | H-11, M-1, M-7             |
| `USSD.sol`                     | `approveToRouter` | Unsafe ERC20 transfer calls without return-value checks or SafeERC20 wrapper        | 96%        | 243  | none judged (real pattern) |
| `USSD.sol`                     | `calculateMint`   | Missing sanity/range check on oracle price allows flash-crash price manipulation    | 95%        | 171  | M-7                        |

_Contest finding: the judged issue it matches._

## How it did in other benchmarks

| Contest                        | Confirmed findings | Identified the file (bug type, ≥ 70% confidence) | Identified the function | False positives (≥ 70%, reviewed by hand) |
| ------------------------------ | ------------------ | ------------------------------------------------ | ----------------------- | ----------------------------------------- |
| Monolith · Sherlock · Dec 2025 | 7                  | 6                                                | 3                       | 3 of 9 flags                              |
| Beedle · CodeHawks · Jul 2023  | 42                 | 27                                               | 14                      | 1 of 12 flags                             |
| USSD · Sherlock · May 2023     | 22                 | 20                                               | 14                      | 0 of 18 flags                             |

Identified the file: the file scored 70% or more on the finding's bug type. Identified the function: the function it ranked highest for that bug type was the one the judges named. False positives: file-level flags at 70% that a human review found to be wrong; flags that were real but out of scope, or judged findings under another label, are not counted ([Monolith](bench/monolith/notes.md), [Beedle](bench/beedle/unmatched_review.md), [USSD](bench/ussd/unmatched_review_a.md)).

Full results: [Monolith](bench/monolith/results.md) · [Beedle](bench/beedle/results.md) · [USSD](bench/ussd/results.md)

## More

Details, benchmarks, and how to sync or add detectors: [docs/DETAILS.md](docs/DETAILS.md)

## Credits and license

Detectors come from the [Cyfrin audit-checklist](https://github.com/Cyfrin/audit-checklist) and [evm-cortex](https://github.com/ccashwell/evm-cortex) by Chris Cashwell (MIT). Answers come from Jev by [TypeSafe](https://docs.typesafe.ai). MIT license. See [LICENSE](LICENSE).
