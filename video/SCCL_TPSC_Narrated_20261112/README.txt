SCCL / TPSC AUDITED VIDEO REVISION - 2026-11-12

Current scope: corrected Manim visuals, six freshly rendered Full HD chapters,
verified original electrical data, and completed English male narration.
CURRENT STATUS: narration generated, synchronized and incorporated into the MP4.
All 46 audiovisual checks passed. The silent master is also retained.

Main files
  output/SCCL_TPSC_Narrated_EN.mp4 Narrated 128-second film, 1080p30
  output/SCCL_TPSC_Narration_EN.wav Synchronized English voice track, 48 kHz
  narration/narration_en.srt       Optional English captions, measured timing
  output/SCCL_TPSC_final.mp4       Audited 128-second silent master, 1080p30
  docs/AUDIT_REPORT.txt            Findings, evidence and completion addendum
  scenes.py / visuals.py          Editable corrected Manim scenes
  narration/narration_en.txt       English narration script
  narration/script.json           Fifteen event windows and voice settings
  evidence/release_validation.json Final media and preservation checks

The original ../SCCL_TPSC directory remains unchanged. All recorded PSCAD/EMTDC
data are retained unchanged. No new electrical simulation was performed.

Reproduce visuals (Python 3.11, existing Manim/LaTeX/FFmpeg installation)
  py -3.11 -m unittest discover -s tests -v
  py -3.11 render_video.py
  py -3.11 validate_video.py

Regenerate narration in a normal local PowerShell session with network access
  & '.\complete_narration.ps1'

This installs edge-tts 7.3.1 only under dependencies/tts, synthesizes the
selected American male voice, writes timed WAV/SRT, muxes audio with the new
silent master, and checks the result. It does not change machine settings.
The selected voice must be available from the provider at execution time.

Generated and verified outputs:
  output/SCCL_TPSC_Narrated_EN.mp4
  output/SCCL_TPSC_Narration_EN.wav
  narration/narration_en.srt
  narration/narration_manifest.json
  evidence/narration_validation.json

The script fails explicitly on overlong clips instead of cutting off words.
The original text is unchanged. Three clips needed pitch-preserving tempo
adjustments, with a maximum factor of 1.1122. All 15 fit their original windows.
The selected voice is en-US-GuyNeural, rate +6%, pitch +4 Hz. Measured MP4
loudness is -16.14 LUFS, true peak -1.45 dBTP. The six chapters and exact H.264
video payload are preserved. Validation includes full audio/video decoding,
cue timing and signal checks; it does not constitute a subjective listening
review. See evidence/narration_completion.json and narration_validation.json.

Portable data scope
Compact measured channels, metadata, native model snapshots and original run
receipts are included. The large original raw INF/OUT archive is not duplicated.
validate_video.py reports absent raw sources explicitly in a standalone copy.
The study workspace retains them and their hashes were reverified in this audit.
