"""Narration must never silently overlap or lose a word at a chapter boundary."""
import importlib.util
from pathlib import Path
import unittest


class NarrationTimingTest(unittest.TestCase):
    def module(self):
        path=Path(__file__).resolve().parents[1]/'generate_narration.py'
        self.assertTrue(path.exists(), 'Narration timing validator is required before muxing')
        spec=importlib.util.spec_from_file_location('narration_generator',path)
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        return module

    def test_overlong_audio_is_rejected(self):
        with self.assertRaisesRegex(ValueError,'exceeds'):
            self.module().place_segment(0,3,3.1)

    def test_clip_is_centered_and_fits(self):
        self.assertEqual(self.module().place_segment(10,16,4),(11,15))

    def test_script_windows_are_nonoverlapping_and_fit_video(self):
        import json
        script=json.loads((Path(__file__).resolve().parents[1]/'narration/script.json').read_text())
        last=0
        for row in script['segments']:
            a,b=row['window']
            self.assertGreaterEqual(a,last)
            self.assertGreater(b,a)
            self.assertLessEqual(b,script['duration_s'])
            last=b


if __name__=='__main__':unittest.main()
