SCCL / TPSC - ENGLISH YOUTUBE RELEASE V5

Upload video: output/SCCL_TPSC_Narrated_EN.mp4
English subtitles: narration/narration_en.srt
Description, tags and thumbnail: youtube/
Synchronized voice: output/SCCL_TPSC_Narration_EN.wav

Full HD 1920x1080, 30 fps, 1 minute 42 seconds, four chapters. The video begins
with normal operation, places network context beside the current comparison,
and ends with normal operation restored. The sizing chapter has been removed.
The final restored state remains visible for four seconds with a brief English
conclusion. The voice is en-US-GuyNeural. Upload the supplied SRT separately for
YouTube captions; optional captions are also embedded in the MP4.

The three bypass-current traces use i_{bypass,A} and the exact caption
"Phase-A bypass current". Native measured channels remain unchanged.

CHAPTERS
00:00 Current limiter: normal operation
00:18 Fault response and thyristor bypass
00:44 Two-source network and fault-current comparison
01:12 Fault clearing, recovery and reclosure

Reproduction with Python 3.11, Manim, LaTeX and FFmpeg:
  py -3.11 -m pip install -r requirements-lock.txt
  py -3.11 -m pip install dependencies/schemdraw-0.23-py3-none-any.whl
  py -3.11 -m unittest discover -s tests -v
  py -3.11 render_video.py
  py -3.11 assemble_saved_narration.py
  py -3.11 validate_video.py
  py -3.11 validate_narration.py

Saved MP3 clips reproduce this release without new speech requests. The
complete_narration.ps1 script installs edge-tts 7.3.1 and regenerates all speech.
V5 retains all fourteen English voice clips and their original synchronization.
New synthesis can change timing; check physical-event and closing alignment.

Evidence includes data/media validation, narration validation, V5 revision checks,
visual review and package hashes. validate_revision.py also compares preserved V4
files at the original workspace location in previous_version_hashes.json.

The ZIP contains editable source, compact measured data, native PSCAD projects,
saved speech clips, final scene renders and publishing assets. Raw INF/OUT files,
compiled PSCAD binaries and installed Python packages are omitted. Raw-source
verification requires the original study workspace; compact-data checks and video
rendering use the packaged dataset. No new PSCAD run was performed.
