# SCCL TPSC Implementation Plan

**Goal:** Build, execute, and validate a native three-phase PSCAD 5.1 SCCL study.

**Architecture:** Identical 138 kV, 60 Hz Thevenin sources feed a downstream fault. Source 1 passes through independently configurable L and C and a naturally commutated antiparallel SCR capacitor bypass. Native electrical measurements feed protection, output channels, and graphs. Python only generates, executes, analyzes, and packages the EMTDC model.

**Specification:** The complete user specification in this session and the three preserved reference images.

## Constraints and engineering choices

- English text throughout; preserve the supplied references.
- Native PSCAD Master Library sources, passive components, SCRs, breaker and MOV.
- Three explicit phase circuits with common three-phase protection; no controlled current injection.
- Both source equivalents remain identical in all comparisons.
- L and C remain independently editable. Sensitivity defaults to matched compensation, with additional fixed-C observations if needed.
- Modest feeder load; fault-current KCL includes load current where applicable.
- Equivalent SCR stack parameters and MOV curve are engineering assumptions, not certified equipment ratings.
- No thermal junction temperature claims.
- No success claim without fresh EMTDC results and source-bound receipts.

## Work sequence

- [x] Inspect references, licensed environment, local component ports and documented automation signatures.
- [x] Calculate analytical fault phasors and compensation; test phasor/RMS analysis against known signals with DC offset.
- [x] Create baseline and SCCL native circuits, protection, measurements, and native graphs; build and run.
- [x] Diagnose physical behavior; demonstrate natural valve turn-off, safe capacitor recovery and feeder reclosure.
- [x] Execute five reactor values, at least three fault angles, and reduced-step convergence cases.
- [x] Analyze source/fault KCL, internal branch KCL, electrical energy and stress, and comparable symmetrical RMS windows.
- [x] Produce nine English figures, technical report, validation report, parameter documentation and reproducible scripts.
- [x] Reopen native workspace, verify source hashes, rerun from an extracted package and inspect graphs.

ZIP manifest/CRC verification runs after archive assembly. Its final status and archive hashes are recorded externally in `results/package_verification.json`, avoiding a self-referential archive hash.

## Files and interfaces

`config/parameters.json` defines assumptions and independent parameters. `scripts/build_project.py` creates native projects. `scripts/run_simulations.py` executes and writes `results/<case>/<timestamp>/run_receipt.json` with raw `.inf/.out` files. `scripts/analyze_results.py` consumes only fresh native results and emits metrics and validation. `scripts/plot_results.py` creates figures from these results. `scripts/package_results.py` creates and verifies portable archives.

## Review focus

1. SCR conduction must persist after gate withdrawal until physical current zero.
2. Measurement polarity and feeder-load current must not invalidate KCL.
3. DC offsets must not be misreported as symmetrical RMS.
4. Stale results or modified source snapshots must fail provenance checks.
5. Fine-step sensitivity must include switching peaks and capacitor stress, not RMS alone.
