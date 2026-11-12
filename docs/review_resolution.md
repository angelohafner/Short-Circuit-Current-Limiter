# Independent engineering review and resolution

The review independently inspected the native circuit, accepted EMTDC outputs, source contributions, KCL, natural SCR turn-off and analysis/packaging scripts. It reproduced approximately 79.959 kA without SCCL and 49.913 kA with SCCL. No critical electrical defect was identified.

## Resolved findings

- Analysis previously trusted a convenience NPZ cache before reading native files. Analysis and plotting now always read indexed original INF/OUT data. A regression test deliberately corrupts the cache and verifies that native measurements remain authoritative.
- Final packaging previously lacked a complete study requirement. The final gate now requires all 24 selected runs, a current all-pass full validation, raw output hashes, saved-model hashes, the reopened relative workspace, and extracted-workspace execution evidence. Partial studies cannot pass this gate.
- An unspecified phase angle in an old receipt could be mislabeled as zero. Analysis reads both actual source phase settings from each native model snapshot and verifies them against the case label. The runner now records the observed phase settings separately from requested overrides.
- Portability previously targeted only a copied case. The delivery workflow now archives and extracts all three models with their relative workspace, reopens that workspace, reruns the extracted limited case and includes its actual raw outputs and receipt in the full package.
- Resume previously skipped runs by label alone. It now requires matching configuration hash, requested L/C/angle/time step and intact source/output hashes. Old receipts without configuration hashes rerun conservatively.
- Several exposed builder parameters were hardcoded. The builder now consumes the configured source voltage/frequency/ramp, SCR withstand, MOV rating/stacks, busbar impedance and feeder resistance. Final acceptance references remain explicitly scoped to the specified 138 kV, 60 Hz study.
- The short five-cycle phasor estimator used a single DC mode. It now fits both coupled source-network exponential modes. An independent numerical regression test verifies DC-offset rejection. Settled A/B measurements remain the principal acceptance reference.

## Additional final verification

Six analysis regression tests pass. The 24 native runs pass 332 numerical/provenance checks. All three nominal native files were rerun after native graph-range improvements; their selected receipts bind those exact saved files. Native graph panels and all nine publication figures were visually reviewed. Reopen, extracted-workspace execution and archive integrity have separate machine-readable receipts in the results directory; the archive receipt is external to avoid self-reference.

## Engineering limits retained

SCR stack, snubber and MOV values are documented electrical equivalents, not manufacturer-certified ratings. The model has no junction-temperature or breaker TRV withstand model. The reference illustration's optional mechanical capacitor bypass and absolute thermal curves are not reproduced. Reclosure restores the compensated path; small decaying RLC oscillations remain at the 1.50 s endpoint.
