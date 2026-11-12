# Execution ledger

Plan: docs/implementation_plan.md

- References: all three images inspected. Topology is series capacitor and reactor, with capacitor-only protective bypass. The recovery illustration includes a mechanical bypass option and unverified thermal claims; this study validates electrical recovery only.
- Ruling: Execute the supplied detailed specification without an additional approval gate, as explicitly requested by the user.
- Ruling: This is a new non-Git artifact folder. Preserve all originals; use timestamped evidence and archives rather than branch operations.

- Environment: fresh licensed PSCAD 5.1 session on port 63579 successfully saved the native project. Earlier session on 54070 could assemble but could not save in this workspace; do not reuse it.
- Analysis tests: 3/3 passed after observed expected failures.
- Native model: capacitor voltmeter was moved from x=130 to x=131 to prevent its lower port contacting the upper sensing wire. Reserved VDC label replaced with VDROPC. Final native builds have zero errors and warnings.
- Recording: source3 internal current PGBs were in DSDYN, one step behind feeder DSOUT meters. Replaced source-current exports with dedicated native ammeters; protection calculations execute in DSOUT. Native source/fault KCL is now below 2e-10 kA without post-processing time shifts.
- Nominal EMTDC results: baseline 79.959 kA total; limited 49.913 kA total, Source 1 9.927 kA, Source 2 39.991 kA. Current targets emerge from unchanged source equivalents and actual RLC/SCR branches.
- Recovery: gate removal at about 0.656 s; valve current persists about 162 ms; recovery complete before 1.2 s reclosure. Normal transfer restored. Actual breaker poles open at their current zeros after the 0.583333 s opening command.
- Ruling: use sustained 0.5-1.1 s faults for A/B plateau comparison and a separate five-cycle clearing command for C. This avoids confusing DC-offset RMS with symmetrical RMS.
- Sensitivity batch completed: all five reactor values by three source phase settings; two fixed-C cases; A/B/C 5 us checks. All 24 selected runs contain fresh native outputs and source snapshots.
- Final saved models: nominal L/C, phase setting and 10 us step restored and rerun after graph-range improvements. The accepted analysis passes 332/332 checks; six independent numerical regression tests also pass.
- Independent review: provenance, completeness, resume, phase labeling and short-window DC-mode issues were resolved. See `docs/review_resolution.md`.
- Native visual review: all three saved models have readable graph ranges, actual EMTDC curves and full network/control views. All nine publication figures were inspected.
- Reopen: three projects loaded through a relative-path workspace; protected native hashes remain unchanged.
- Extracted-workspace reproduction: three-project staging archive passed CRC/payload hashes, was extracted and reopened, and its limited case produced 49.9134806313 kA from fresh EMTDC outputs. Original reference hashes remain unchanged.
- Final packaging is gated by raw-output hashes, accepted-model hashes, complete validation and portability evidence. The archive integrity receipt is written externally after ZIP verification.
