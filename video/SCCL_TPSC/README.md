# TPSC short-circuit current limiter: Manim film

The film explains a three-phase TPSC plus series reactor using recorded PSCAD 5.1 / EMTDC measurements. Python draws and animates the evidence; it does not synthesize the electrical waveforms.

## Deliverables

- `output/SCCL_TPSC_final.mp4`: complete 128-second film, 1920 x 1080 at 30 fps.
- `output/FaultTransfer_preview.mp4`: 26-second current-transfer pilot.
- `scenes.py`, `visuals.py`: editable scenes and electrical graphics.
- `assets/`: genuine Schemdraw vector symbols with explicit terminal geometry.
- `data/measurements.npz`: full-resolution selected native channels, without amplitude scaling or smoothing.
- `data/provenance.json`, `data/receipts/`: original INF/OUT hashes and licensed simulation receipts.
- `pscad/`: source-bound native A/B snapshots and the separately extended recovery project.
- `evidence/validation.json`: electrical, temporal, source-preservation and video checks.
- `docs/storyboard.md`: scene timing and teaching notes.

## Reproduce the video

Use Python 3.11, the locked Python versions in `requirements-lock.txt`, a LaTeX installation with `latex` and `dvisvgm`, and FFmpeg/FFprobe on PATH. Windows uses Arial; install Arial or deliberately select an available font when rendering on another platform. The tested renderer is Manim Community 0.21.0 with Cairo.

```powershell
py -3.11 -m pip install -r requirements-lock.txt
py -3.11 -m unittest discover -s tests -v
py -3.11 build_assets.py
py -3.11 -u render_video.py --preview --only FaultTransfer
py -3.11 -u render_video.py
py -3.11 validate_video.py
```

Rendering verifies the compact dataset and metadata hashes before opening any scene. `--reuse` reuses already rendered scene MP4s and should only be used when their source has not changed. The final video is silent and includes chapter metadata.

Schemdraw 0.23 is supplied as an unmodified pure-Python wheel under `dependencies/`; the asset builder reads it directly. The original study's diagram and native simulations remain unchanged outside this video directory.

## Traceability and electrical definitions

The A/B comparison uses the same source equivalents and the same 0.95-1.05 s measurement window. The displayed symmetrical RMS value is the mean of three phase fundamental phasor magnitudes, fitted to actual waveforms with a DC intercept. Total fault current is the measured fault-branch current. RMS source magnitudes are not arithmetically imposed on that branch.

Measured results are 79.9590 kA without SCCL and 49.9135 kA with SCCL: a 37.576% reduction. Source 1 changes from 39.9759 to 9.9272 kA; Source 2 remains near 39.99 kA. The instantaneous plot is explicitly phase A. Its DC offset is not labeled as symmetrical RMS. The recovery plot uses PSCAD's sliding RMS estimate, a different measurement.

The phase detail preserves the series main R-L, capacitor ESR, bypass R-L and antiparallel SCR topology. MOV and individual SCR snubbers are omitted from the animated drawing for readability, but remain in the native model and measured waveforms. `IV` includes the SCR/snubber branch. For the native measurement signs, `I1 = IC + IV - IM`; network conservation is `I1 + I2 = IF + ILOAD`. The downstream load explains why source currents do not sum to precisely the fault branch alone.

Native SCR conduction is decoded from `TON > TOFF`, never from gate commands or a current threshold. Digital states use the previous native sample; analog cursor values use linear interpolation only between adjacent 10-microsecond samples. Display curves preserve each pixel-bin minimum and maximum. Their visual thinning never changes cursor data or reported peaks.

## Regenerate source-derived data

The portable video archive includes compact measurements and provenance, not the very large original raw output archive. The original study retains every INF/OUT file and its existing engineering package. To rebuild the compact data, place this directory under the original `SCCL_TPSC_Study/video/` structure and run:

```powershell
py -3.11 prepare_data.py --study ../..
```

Every raw input and PSCX snapshot is hash-checked against its simulation receipt first. A standalone extracted video package reports absent raw sources explicitly while still validating the included compact dataset. It never claims raw evidence was reverified when unavailable.

The extra recovery run was performed on `SCCL_C_Extended.pscx`, in a licensed PSCAD 5.1.0 session, with a duration of 2.5 s and 10-microsecond step. Its original native outputs are retained under `native_results/` in the workspace. `extend_recovery.py` documents how that copy was created; it deliberately refuses to overwrite an existing extended project. Another engineer can open the included extended PSCX, choose an available compiler, and rerun it in licensed PSCAD. No junction-temperature or manufacturer-rating claim is made.

## Independent L and C

The original study exposes L and C as separate engineering parameters. The final chapter plots the five actual retuned-compensation cases at 10, 12, 15.9, 20 and 25 mH; it does not fabricate intermediate simulation points. Connecting lines guide the eye. Two additional fixed-C runs (10 and 25 mH with 442.5 microfarads) are retained in metadata for teaching normal-compensation tradeoffs.

See the parent study's report for the detailed EMT energy, MOV, inception-angle and smaller-time-step validation. This film is an educational presentation of those recorded cases, not equipment certification.
