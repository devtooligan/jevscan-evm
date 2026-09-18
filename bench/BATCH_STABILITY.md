# Batch stability

A one-off script (not kept in the repo), jev-1.13.0, seed 20260918. The 8 USSD files the benchmark scans; 20 (file, question) pairs: 10 drawn from pairs whose normal-batch p is 0.15-0.85, 10 from the rest (broad questions excluded). Each is asked (a) alone, (b) in the batch jevscan sends (same request, so the same cache entry as a scan), (c) with 10 random other questions from any level, at a random position, and (d) alone again, sent past the cache. Jev is not deterministic: the same request sent twice can differ, so (a) vs (d) is the floor the batch effects are compared with. (d) was sent fresh. Size: 81 cached or uncached requests plus 20 repeats, 990,496 input tokens through the cache ($0.0416 uncached).

| Comparison | Mean abs delta (all 20) | Max (all 20) | Mean (10 uncertain) | Max (10 uncertain) |
|---|---|---|---|---|
| alone vs the same request repeated (repeat noise) | 0.009 | 0.030 | 0.016 | 0.030 |
| alone vs normal batch | 0.007 | 0.030 | 0.013 | 0.030 |
| random batch vs normal batch | 0.008 | 0.030 | 0.015 | 0.030 |
| alone vs random batch | 0.011 | 0.060 | 0.020 | 0.060 |

Largest mean abs batch delta: 0.011. That is below the 0.03 bar set before the run, so batching was left as is: question order is already fixed (library order), and only the batch boundaries move with file size. The batch effects are about the size of the repeat noise, so fixing the batches would not make scores reproducible. Single moves of 0.05-0.08 do occur, so a p within about 0.05 of a threshold should be read as a tie.

| File | Question | (a) alone | (b) normal batch | (c) random batch | (d) alone, repeated |
|---|---|---|---|---|---|
| `USSDRebalancer.sol` | subcategory:arbitrary_external_call | 0.180 | 0.180 | 0.170 | 0.170 |
| `USSD.sol` | subcategory:invariant_violation_solvency | 0.670 | 0.660 | 0.690 | 0.680 |
| `oracles/UniswapV3StaticOracle.sol` | detector:oracle | 0.300 | 0.290 | 0.290 | 0.290 |
| `USSD.sol` | detector:deploy_uninitialized_impl | 0.740 | 0.750 | 0.760 | 0.760 |
| `oracles/UniswapV3StaticOracle.sol` | detector:general_dos | 0.300 | 0.330 | 0.300 | 0.310 |
| `oracles/StableOracleDAI.sol` | subcategory:uninitialized_or_shadowed_state | 0.300 | 0.300 | 0.330 | 0.320 |
| `USSDRebalancer.sol` | subcategory:rounding_direction_error | 0.390 | 0.380 | 0.380 | 0.370 |
| `oracles/UniswapV3StaticOracle.sol` | subcategory:external_protocol_assumption | 0.290 | 0.300 | 0.300 | 0.260 |
| `USSDRebalancer.sol` | subcategory:fee_on_transfer_or_rebasing_token | 0.420 | 0.400 | 0.390 | 0.400 |
| `USSD.sol` | subcategory:manipulable_twap_or_custom_oracle | 0.260 | 0.290 | 0.320 | 0.270 |
| `oracles/StableOracleWBGL.sol` | subcategory:single_function_reentrancy | 0.020 | 0.020 | 0.020 | 0.020 |
| `USSD.sol` | detector:kinetiq_native_receive_handling | 0.030 | 0.020 | 0.020 | 0.020 |
| `oracles/UniswapV3StaticOracle.sol` | detector:kinetiq_instant_unstake_pool | 0.010 | 0.010 | 0.010 | 0.010 |
| `oracles/UniswapV3StaticOracle.sol` | subcategory:liquidation_logic_error | 0.020 | 0.020 | 0.020 | 0.020 |
| `oracles/StableOracleWBTC.sol` | detector:c_field_truncation | 0.010 | 0.010 | 0.010 | 0.010 |
| `USSD.sol` | detector:vyper_augassign_oob | 0.010 | 0.010 | 0.010 | 0.010 |
| `USSD.sol` | detector:diamond_selector_collision | 0.030 | 0.030 | 0.020 | 0.020 |
| `oracles/StableOracleDAI.sol` | detector:compound_patterns | 0.010 | 0.010 | 0.010 | 0.010 |
| `USSDRebalancer.sol` | detector:vyper_range_negative | 0.010 | 0.010 | 0.010 | 0.010 |
| `Migrations.sol` | detector:solana | 0.010 | 0.010 | 0.010 | 0.010 |
