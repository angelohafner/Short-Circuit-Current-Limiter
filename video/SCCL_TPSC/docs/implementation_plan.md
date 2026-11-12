# SCCL TPSC Manim Video Implementation Plan

> For agentic workers: use superpowers:executing-plans for inline execution.

Goal: Deliver a 120-140 s, 1920x1080, 30 fps English educational Manim video driven by recorded PSCAD data.

Architecture: Source-bound compact native data feed one simulation-time controller per scene. Schemdraw SVG symbols and Manim LaTeX labels form separately animatable circuits. Six independently rendered scenes are assembled with chapters.

Tech stack: Python 3.11, Manim Community 0.21.0, Schemdraw 0.23, NumPy, LaTeX, FFmpeg, licensed PSCAD 5.1 for an isolated extended-recovery copy.

Spec: The user's approved six-step prompt in this conversation. The user explicitly requested autonomous execution through the complete deliverable, including a pilot and continued full production.

## Global constraints

- English visible elements, code, labels and documentation. Minimal text; variables, numeric values and units in LaTeX.
- Preserve all existing PSCAD models, results, diagrams and ZIPs.
- Only actual native measurements determine graphs, arrows, gates and SCR conduction states.
- Keep sustained-fault comparison and clearing/reclosure cases separate.
- Render the pilot before the full film; review it and continue autonomously.
- Package scripts, SVG assets, compact data, provenance, instructions and validation.
- This is a non-Git artifact workspace. Use the user-requested isolated video folder and retained evidence rather than Git-specific workspace/commit helpers.

## Tasks

1. [x] Native evidence and data: run a 2.5 s recovery copy; retain original hashes and fresh outputs. Implement tests for stepwise states, out-of-range timestamps, peak-preserving thinning and corrupt-data rejection. Expected: native run succeeds, settling quantified, tests pass.
2. [x] Assets and pilot: export standalone Schemdraw symbols with terminal geometry, build phase circuit and 26 s current-transfer pilot with one time controller. Expected: readable pilot, accurate gate-versus-conduction behavior and connected symbols.
3. [x] Six scenes: network 14 s, normal 18 s, transfer 26 s, comparison 22 s, recovery 30 s, sizing 18 s. Expected: 128 s film with real waveform cursors, correct RMS definitions and fully settled recovery.
4. [ ] Validation and delivery: full decode, resolution/fps/duration, sampled-frame review, temporal/electrical checks, compact-data hashes, fresh independent review, portable render test and ZIP CRC/payload hashes. Expected: all checks pass and deliverable paths recorded.

## Interfaces

- prepare_data.py writes data/measurements.npz and data/metadata.json; source INF/OUT hashes are preserved in data/provenance.json.
- data_access.py exposes verified load, continuous interpolation, previous-sample states and min/max-preserving plotting indices.
- build_assets.py writes assets/*.svg and assets/geometry.json. visuals.py consumes both.
- scenes.py consumes the verified datasets and graphics; render_video.py renders, assembles and extracts review frames.
- validate_video.py validates electrical/temporal mappings, final media and protected sources. package_video.py freezes the portable payload.

## Review focus

- Gate commands must never be substituted for actual SCR conduction, especially after gate withdrawal.
- Comparison and recovery must use their own time windows; discrete states must never be linearly interpolated.
- Current-arrow direction must follow measured sign; small blocked leakage must not appear as significant conduction.
- SVG placement must retain terminals, and frame compositions must remain legible at 1080p.
- Modified compact data must fail before rendering; standalone packages must explicitly distinguish absent original raw evidence from hash-verified compact data.
