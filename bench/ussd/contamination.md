# Contamination check: obfuscated USSD

A one-off script (not kept in the repo) copied the 12 USSD sources into `bench/ussd/obfuscated/` with every comment blanked (line numbers unchanged) and 185 project-declared identifiers renamed to `Contract<n>` / `fn<n>` / `var<n>`; files become `File<n>.sol`. External names (ERC20, OpenZeppelin, Uniswap `slot0`, Chainlink `latestRoundData`) are kept. Both runs use `jevscan.py --localize --localize-threshold 0.3 --repo-level` with jev-1.13.0. The ground truth is mapped through the same renaming.

| Metric | Original | Obfuscated |
|---|---|---|
| Files scanned (classified source) | 8 | 9 |
| Recall@0.5, category | 22/22 | 22/22 |
| Recall@0.5, subcategory | 14/16 | 14/16 |
| Recall@0.5, detector | 15/16 | 14/16 |
| Mean p on true (file, category) pairs | 0.80 | 0.76 |
| Mean critical_bug on files with issues | 0.66 | 0.56 |
| Mean category p on clean files | 0.10 | 0.14 |
| Mean any_bug on clean files | 0.40 | 0.48 |
| Mean category p on the original's clean files | 0.10 | 0.17 |
| Mean any_bug on the original's clean files | 0.40 | 0.51 |
| Localization top-1 / top-3, category | 14 / 20 of 21 | 13 / 20 of 21 |
| Localization top-1 / top-3, subcategory | 12 / 15 of 16 | 12 / 15 of 16 |
| Localization top-1 / top-3, detector | 12 / 15 of 16 | 11 / 14 of 16 |

Clean files: original `Migrations.sol`, `oracles/UniswapV3StaticOracle.sol`; obfuscated `Migrations.sol`, `oracles/UniswapV3StaticOracle.sol`, `oracles/SimOracle.sol`.

Obfuscated classification (original names): `Migrations.sol` → source (1.00), `USSD.sol` → source (1.00), `USSDRebalancer.sol` → source (1.00), `interfaces/IStableOracle.sol` → interface (1.00), `interfaces/IStaticOracle.sol` → interface (1.00), `interfaces/IUSSDRebalancer.sol` → interface (0.98), `oracles/StableOracleWBTC.sol` → source (0.98), `oracles/StableOracleWETH.sol` → source (0.98), `oracles/UniswapV3StaticOracle.sol` → source (1.00), `oracles/SimOracle.sol` → source (0.86), `oracles/StableOracleDAI.sol` → source (0.99), `oracles/StableOracleWBGL.sol` → source (0.99).
