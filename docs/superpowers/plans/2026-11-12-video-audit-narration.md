# SCCL video audit and narration implementation plan

> Execution: superpowers:executing-plans, within this session. The user explicitly requested the audit, its corrections, English narration, and a fresh video. No additional design approval is needed for this authorized revision.

**Goal:** Deliver a corrected, freshly rendered SCCL film with an animated American male English voice, an audit report, editable source, and reproducible validation.

**Architecture:** Preserve `video/SCCL_TPSC` unchanged. Work in `video/SCCL_TPSC_Narrated_20261112`, retaining the six chapters and verified recorded electrical data. Correct the drawings and timing where direct inspection establishes a problem. Generate speech in short event-aligned segments and mux it with the new Full HD render.

**Tech stack:** Existing Manim 0.21.0/Cairo, NumPy, LaTeX, FFmpeg, Windows SAPI if online neural speech is unavailable.

## Scope and decisions

- English visible text and narration; American male voice confirmed by user.
- Keep the electrical study and original movie intact; do not rerun PSCAD.
- Audit actual extracted frames, terminal geometry, measured states, comparison numbers, units, timing, and media streams.
- Prefer expressive neural speech; network access is currently unavailable. Test the installed David voice and document the actual engine used.
- Preserve six chapters; adjust scene duration only if needed for intelligible narration.
- Keep subtitles optional, outside the picture, to avoid covering electrical details.

## Tasks

- [x] Capture original hashes, extract review frames, and recompute existing electrical checks.
- [x] Record confirmed findings with before evidence; fix display causes in the revision. Add focused regression checks for errors affecting technical meaning.
- [ ] Write concise English narration tied to visible events; synthesize male speech, fit each cue without truncating words, and create SRT and WAV.
- [ ] Render every scene freshly, assemble a new silent master, and mux narration with optional subtitles and chapters.
- [ ] Inspect corrected frames and timing, decode the full audiovisual output, measure loudness/peaks, verify hashes and tests, and deliver report plus editable package.

## Narration continuation, 2026-11-12

The existing English script was synthesized successfully with en-US-GuyNeural.
The 15 speech clips fit the existing windows; three needed pitch-preserving
tempo adjustment (maximum 1.1122). WAV, measured SRT and narrated MP4 now exist.
The narrated output passed 46/46 checks and preserves the exact H.264 payload,
six chapters, Full HD 30 fps and 128-second duration of the audited master.
A trailing-log JSON parsing defect in the loudness scan was reproduced and
corrected in generation and validation. The historical blocked status below
is superseded; current release/package status is in the revision's evidence.

## Observed status

Visual work complete: six fresh renders, corrected two missing hold frames,
3840 frames at 30 fps, 128 seconds, 47/47 media/data checks, 16/16 unit tests,
and 140-file package CRC/payload hashes verified. Original files unchanged.
Fresh independent review found no further source defects before the final
frame-count correction; that correction has a failing-then-passing integration test.

Narration text, timing, generation, mux and validation scripts are prepared.
Actual synthesis is blocked by restricted networking / local Windows speech
access. No narrated movie is claimed. The user requested instructions to enable
access; official OpenAI documentation was consulted and UI instructions supplied.
Continue synthesis and audiovisual verification when permissions actually change.

## Review focus

Rotated asymmetric SCR terminals; chart origin and limits; label collisions; event captions versus native switching state; speech that precedes the visible event; end truncation; false claims of natural speech or a new electrical simulation.

## Completion evidence

Original hashes unchanged; numeric data checks pass; new visual evidence; full video/audio decode; correct resolution, fps, chapters and duration; complete narration manifest; artifact paths.
