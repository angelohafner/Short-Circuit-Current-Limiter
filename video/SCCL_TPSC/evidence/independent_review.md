# Independent final review

Review date: 2026-11-03. Scope: implementation and completed six-scene 1080p renders available during production, native compact measurements, provenance, and packaging code. This review did not modify implementation, run PSCAD, or render scenes.

## Critical findings

None found. Native switching state, recorded waveform selection, and the symmetrical RMS comparison are technically consistent in the inspected implementation and data.

## Important findings

1. **Recovery starts with an incorrect feeder state during the initial hold.** `visuals.py:130-138` constructs every indicator inactive and registers an updater without evaluating it. `scenes.py:104-112,130-131` then holds the scene before its first animation. The rendered `media/final/videos/scenes/1080p30/Recovery.mp4` at 0.5 video seconds shows an inactive "Feeder closed" chip at simulation time 0.49000 s, although all three native breaker states are zero (closed). Evidence: `evidence/review_recovery_initial.png`. Evaluate the indicator updater once before returning the chip, rerender Recovery, and inspect its initial hold. This is a display-initialization error, not an electrical model error.

2. **The delivered preview predates the initialization correction.** `output/FaultTransfer_preview.mp4`, referenced as a deliverable in `README.md:8`, shows all initial current arrows pointing right and the bypass at its default dark appearance during the initial 0-2 s hold. At its displayed native time 0.499 s, I1A=-0.1442321059 kA, ICA=-0.1441517967 kA, IVA=-0.00001315185 kA, and both phase-A SCRs are blocked. The reactor/capacitor arrows therefore must point left, and the small leakage arrow must be faded. The current `scenes.py:54` explicitly initializes the circuit, and the completed full-HD FaultTransfer is correct (`evidence/review_transfer_initial.png`). Regenerate the preview from current source before including it in the portable package. Existing preview evidence: `evidence/frames_FaultTransfer_preview/contact_sheet.jpg`, first tile.

3. **Recovery labels the active fault interval as steady operation.** `scenes.py:130-137` changes each caption only after completing its time advance. The initial "Steady operation" caption remains visible while simulation time moves from 0.49 to 0.58994 s (video time 1-8 s). At video time 4 s / simulation time 0.53283 s, the fault, gate, and conducting-SCR chips are active while the caption still says "Steady operation". Evidence: `evidence/review_recovery_fault_caption.png`. Keep the steady caption for the initial hold, then replace it with an interval-appropriate caption such as "Fault current and feeder clearing" before advancing toward pole opening. Preserve event-specific captions only when their events have occurred.

## Minor findings

No additional required changes identified. The already recorded plan to rerender NetworkOverview with the added ground references remains applicable: the inspected pre-rerender `NetworkOverview.mp4` still shows dangling source terminals, while current `visuals.py` contains ground references.

## Checks independently performed

- All five `tests/test_data_access.py` tests pass.
- Loaded `Measurements()` and verified both compact hashes. In a separate temporary directory, replaced the NPZ with corrupt bytes while preserving provenance; `Measurements()` raised `ValueError: Source hash mismatch` before data loading/rendering. Actual payload was untouched.
- Inspected `data_access.py:20-27,55-61`: digital channels and TON/TOFF use previous samples; conduction is decoded from TON > TOFF. At C=0.70 s, native Gate=0 while at least one SCR still conducts. The 14-second Recovery frame demonstrates the same distinction visibly.
- Recomputed the three-phase mean fundamental RMS fault currents from the native selected channels using 0.95 <= t < 1.05 s: A=79.9590286084 kA and B=49.9134806313 kA. Comparison uses A/B; recovery exclusively uses C. Displayed 79.96 -> 49.91 kA and 37.58% are consistent.
- Verified every INF/OUT hash in provenance for all nine source cases (A, B, C, L10, L12, L20, L25, fixed10, fixed25) against files currently present in the study.
- Independently verified protected original PSCX hashes for `pscad/SCCL_A_Without.pscx`, `pscad/SCCL_B_With.pscx`, and `pscad/SCCL_C_Recovery.pscx` against the extension receipt. All match. This is evidence for these three protected files, not an independently captured before/after inventory of every historical study artifact.
- Verified the extended project's included PSCX hash and all 12 extended INF/OUT hashes against its receipt. Its selected native time array reaches 2.5 s. The receipt records PSCAD 5.1.0, licensed=true, fresh_outputs=true, and no errors. This review verified retained evidence; it did not itself observe or repeat that simulation.
- Confirmed current arrows use measured signs and fade below 0.001 kA. The measured pre-fault bypass leakage at the sampled inspected times is far below that threshold. Inspected current-transfer plotting ranges contain the recorded extrema; the extinction inset contains the substantive residual current (maximum 0.7493 kA; minimum approximately -0.0000002245 kA).
- Inspected Schemdraw generation and placement logic, stored terminals/bounds, and full-HD phase-detail frames. Visible main-wire and antiparallel-SCR terminals align; asymmetric SCR gates retain their offsets. Labels, waveform scales, and current direction are legible at 1080p in sampled frames.
- Inspected full-HD network, normal operation, transfer, comparison, recovery initial/tail/final, and sizing samples. Recovery final hold shows t=2.50000 s, feeder closed, recovery ready, and SCRs off. The normal-current inset makes settling visible.
- Sizing uses five recorded retuned-compensation cases, not fabricated intermediate measurements. The separate fixed-C cases are retained in metadata and documented. L and C remain separate model parameters.
- `validate_video.py:43-56` and README explicitly distinguish unavailable original raw sources in standalone extraction from hash-verified compact data. Packaging collects provenance/receipts; it does not falsely describe omitted raw files as included.

## Scope and release limits

The three Important findings above require correction or explicit disposition before calling the deliverable final. This report describes the artifacts available at review time and does not certify later replacements. Full assembled-film decode, duration/fps verification, standalone extraction/render validation, and final ZIP CRC/payload verification remain the parent's release checks; these were not duplicated by this reviewer. No heavy rendering or native study mutation was performed.

Reviewed compact SHA-256 values:

- measurements.npz: fcb3a5c6f4b1c90f86bcd380c6234378a303804f470d0859d2aa2b288652c0b5
- metadata.json: fb8454d72d2cec7c6d0e005864c51dcc78b4e3e54aacfe8baabbd8272d329372

Reviewed source snapshots before corrective changes:

- scenes.py: a543f86e528a3ad84cd272b108340b8f4ec9055e357a7afc6488af3eecc99f5f
- visuals.py: 840c3b124b2c02e84e171bf496b690fc26ef8f553d5a498a9a607c35130b8537
- data_access.py: 88bdc4019cbf5251d23f7b1d3d472732a1c588d362a38d58810f170a11e2de15

## Implementation response received after review

The implementer accepted all three Important findings and reported these corrections:

1. `indicator()` now calls `update(chip)` before returning. A focused initial-display regression was observed failing before the fix and passing afterward; implementer reports the complete suite now passes 6/6.
2. The preview will be freshly rendered in the standalone portable copy and republished from current code.
3. Recovery now changes its initial caption to "Fault and feeder clearing" after the steady initial hold and before its first animated interval.

The implementer is rerendering Recovery, NetworkOverview with ground references, and FaultComparison with an explicit time-axis unit, followed by reassembly. No further confirmed issues were found. Code corrections and reported tests address the causes; replacement media, portable rendering, and archive receipts remain the implementer's final verification responsibility. The reviewer was explicitly asked not to duplicate rerendering or rereview. This addendum records the implementation response without representing the pending replacement renders as independently inspected.
