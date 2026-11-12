# Final release validation

The final film is 128 seconds, 1920 x 1080, 30 fps, H.264 / yuv420p, with six chapters and no audio. FFmpeg decoded the complete stream without errors. SHA-256: `806f0698563347901f519ab4236129015a71aba395d438cb181d1e986e540ce3`.

- 47/47 final electrical, temporal, source-preservation and media checks passed (`evidence/validation.json`).
- 7/7 unit and regression tests passed, including first-frame initialization and exclusion of the solver's initial device state from event extraction.
- A fresh 26-second pilot rendered in a standalone path containing spaces, without original raw sources. All 39 applicable portable checks passed. Every copied Python source hash matches the final implementation (`evidence/portable_render.json`).
- All nine source cases' INF/OUT hashes were verified. The original A/B/C PSCX hashes remain unchanged.
- A separate licensed PSCAD 5.1.0 run extended recovery to 2.5 seconds. Final RMS ripple is 0.03834% of the pre-fault reference; all SCRs are off at the end.

## Quantitative evidence

| Quantity | Without SCCL | With SCCL |
|---|---:|---:|
| Source 1 symmetrical RMS | 39.9759 kA | 9.9272 kA |
| Source 2 symmetrical RMS | 39.9847 kA | 39.9910 kA |
| Measured fault symmetrical RMS | 79.9590 kA | 49.9135 kA |
| Maximum asymmetrical fault peak, any phase | 203.5578 kA | 128.5346 kA |

Both RMS fits use 0.95 <= t < 1.05 s. The reduction is 37.576%. The instantaneous video comparison is explicitly phase A; the peak table covers all phases. Waveforms are native, unscaled measurements.

The nominal fault command occurs at 0.50000 s; native fault-switch closure is first recorded at 0.50001 s. Detection at 0.50038 s and first sampled SCR conduction at 0.50049 s give displayed delays of 0.37 ms and 0.48 ms from electrical closure. Event extraction excludes the initial t=0 device state. At t=0.70 s the gate is off while an SCR still conducts; last native extinction is 0.818909297 s. Gate withdrawal is never used as forced SCR turn-off.

## Visual review and review closure

The six-scene contact sheet and detailed full-resolution frames were inspected. Symbols connect, labels fit, source grounds are visible and graph ranges contain the measurements. Magnified current-tail and sliding-RMS insets expose natural extinction and reclosure settling.

The independent reviewer verified native provenance, protected models, RMS calculations and switching interpretation. Three presentation findings were corrected: initialize the feeder chip before the initial pause; replace the steady-operation caption during the fault interval; replace the stale pilot with a fresh standalone render. The initial-chip regression was observed failing then passing. Corrected captions, gate-off conduction and restored operation were verified in rendered frames. The original review remains unchanged as a historical record; this report records closure.

Arial replaces the unavailable initial prose font; LaTeX renders electrical quantities. The phase-detail drawing omits MOV and individual SCR snubbers for readability, while the native circuit and recorded signals retain them. No thermal or manufacturer-rating claim is made.

## Packaging and reproducibility scope

`package_video.py` requires passing final validation, standalone-render evidence and the independent-review report. It verifies ZIP CRC and every payload SHA-256. The final archive identity is recorded outside the ZIP in `evidence/package_receipt.json`; the internal `manifest.json` lists payload hashes and sizes.

The archive contains the film, pilot, chapter clips, code, exact selected measurements, SVG symbols, configuration, native model snapshots, receipts and documentation. Large original INF/OUT files remain in the parent study. Portable validation explicitly reports their absence instead of claiming they were reverified. Relocated rendering was tested on this environment; compatibility with every OS or Python version is not asserted.
