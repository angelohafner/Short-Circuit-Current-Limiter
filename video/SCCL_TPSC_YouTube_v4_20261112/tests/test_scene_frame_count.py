"""The picture timeline, not chapter metadata, must have the intended length."""
from pathlib import Path
import subprocess
import tempfile
import unittest
import render_video


class ExactSceneDurationTest(unittest.TestCase):
    def test_single_missing_hold_frame_is_restored(self):
        self.assertTrue(hasattr(render_video,'exact_scene_frames'),
                        'Assembly must correct frame quantization before concatenation')
        with tempfile.TemporaryDirectory() as folder:
            source=Path(folder)/'eleven_frames.mp4'
            subprocess.run(['ffmpeg','-v','error','-y','-f','lavfi','-i',
                            'color=c=blue:s=160x90:r=30','-frames:v','11','-c:v','libx264',str(source)],check=True)
            target=render_video.exact_scene_frames(source,.4,30)
            info=render_video.probe(target)
            stream=next(s for s in info['streams'] if s['codec_type']=='video')
            self.assertEqual(int(stream['nb_frames']),12)
            self.assertAlmostEqual(float(stream['duration']),.4,places=6)


if __name__=='__main__':unittest.main()
