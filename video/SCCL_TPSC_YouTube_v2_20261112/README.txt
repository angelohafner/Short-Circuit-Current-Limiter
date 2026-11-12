SCCL / TPSC — ENGLISH YOUTUBE RELEASE V2

Main upload file:
  output/SCCL_TPSC_Narrated_EN.mp4

Optional English subtitles for a separate YouTube subtitle upload:
  narration/narration_en.srt

Other deliverables:
  output/SCCL_TPSC_Narration_EN.wav    Synchronized English voice track
  youtube/description_en.txt           Copy-ready description and chapters
  youtube/tags_en.txt                  Copy-ready tags
  youtube/thumbnail_youtube_1280x720.jpg
  docs/CHANGES.txt                     The three engineering-audit corrections
  evidence/revision_validation.json    Event/speech alignment and preservation
  evidence/narration_validation.json   Full audiovisual and loudness checks
  evidence/validation.json             Data and silent-master verification
  evidence/release_validation.json     Final upload-file verification
  evidence/package_manifest.json       Editable-package payload hashes

The film retains six chapters and a duration of 2 minutes 8 seconds at Full HD
30 fps. It uses the American male en-US-GuyNeural voice. English subtitles
are selectable; upload the supplied SRT separately if desired on YouTube.

Reproduction with the project's existing Python 3.11, Manim/LaTeX and FFmpeg:
  py -3.11 -m unittest discover -s tests -v
  py -3.11 render_video.py
  .\complete_narration.ps1
  py -3.11 validate_video.py

The synthesis command needs network access and regenerates all speech clips.
Event-specific word alignment must be checked after any new synthesis because
the provider can change speech duration. The saved MP3 segments and word
timestamps document the exact clips used in this release.

To reassemble the saved clips without requesting speech again:
  py -3.11 assemble_saved_narration.py

validate_revision.py checks the delivered speech against the recorded breaker
events. Its previous-version preservation check also requires the original
workspace paths in evidence/previous_version_hashes.json.

The prior video remains in ../SCCL_TPSC_Narrated_20261112. The models and recorded
electrical data are unchanged. This revision does not add new PSCAD simulations.

The ZIP contains the compact measured dataset, native PSCAD project files,
editable Manim source, saved speech clips and final scene renders. Large raw
INF/OUT files, compiled PSCAD binaries and installed Python packages are omitted.
Raw-source hash verification is available in the original study workspace;
a portable extraction still supports compact-data verification and video edits.
Install requirements-lock.txt and dependencies/schemdraw-0.23-py3-none-any.whl
in a suitable Python environment before rendering; FFmpeg and LaTeX are also
required. Edge speech synthesis is pinned separately in complete_narration.ps1.
