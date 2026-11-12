SCCL / TPSC — ENGLISH YOUTUBE RELEASE V3

Upload video: output/SCCL_TPSC_Narrated_EN.mp4
English subtitles: narration/narration_en.srt
Description, tags and thumbnail: youtube/
Synchronized voice: output/SCCL_TPSC_Narration_EN.wav

Full HD 1920x1080, 30 fps, 2 minutes, five chapters. The video opens directly with
normal operation. A compact network diagram accompanies the current comparison.
The English voice remains en-US-GuyNeural. Upload the SRT separately for YouTube
captions. Optional captions are also embedded in the MP4.

CHAPTERS
00:00 Current limiter: normal operation
00:18 Fault response and thyristor bypass
00:44 Two-source network and fault-current comparison
01:12 Fault clearing, recovery and reclosure
01:42 Reactor sizing and capacitor tuning

Reproduction with Python 3.11, Manim, LaTeX and FFmpeg:
  py -3.11 -m pip install -r requirements-lock.txt
  py -3.11 -m pip install dependencies/schemdraw-0.23-py3-none-any.whl
  py -3.11 -m unittest discover -s tests -v
  py -3.11 render_video.py
  py -3.11 assemble_saved_narration.py
  py -3.11 validate_video.py
  py -3.11 validate_narration.py

Saved MP3 clips reproduce this release without requesting speech again. The
complete_narration.ps1 script installs edge-tts 7.3.1 and regenerates all clips;
regenerate_changed_narration.py regenerates only the three V3 editorial changes.
New synthesis can change word duration: recheck event alignment before release.

Evidence includes data/media validation, narration validation, V3 revision checks,
visual review and package hashes. validate_revision.py also compares preserved V2
files at the original workspace location recorded in previous_version_hashes.json.

The ZIP includes editable source, compact measured data, native PSCAD projects,
speech clips, final scene renders and publishing assets. Raw INF/OUT files,
compiled PSCAD binaries and installed Python packages are omitted. Raw source
verification requires the original study workspace; compact-data checks and
rendering are supported by the packaged dataset. No new PSCAD run was performed.
