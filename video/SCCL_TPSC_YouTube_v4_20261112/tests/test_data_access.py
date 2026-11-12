"""Protect time semantics, switching states, transients and source provenance."""
import sys
from pathlib import Path
import tempfile
import unittest
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
try:
    from data_access import sample, extrema_indices, verify_hash
except ImportError:
    sample=extrema_indices=verify_hash=None

class DataTests(unittest.TestCase):
    def test_discrete_state_does_not_switch_early(self):
        self.assertIsNotNone(sample)
        self.assertEqual(sample(np.array([0.,1.,2.]),np.array([0.,1.,0.]),.999,discrete=True),0)
        self.assertEqual(sample(np.array([0.,1.,2.]),np.array([0.,1.,0.]),1.,discrete=True),1)

    def test_electrical_sample_is_interpolated(self):
        self.assertIsNotNone(sample)
        self.assertAlmostEqual(sample(np.array([0.,1.]),np.array([-2.,2.]),.75),1.)

    def test_out_of_range_time_is_rejected(self):
        self.assertIsNotNone(sample)
        with self.assertRaises(ValueError):sample(np.array([0.,1.]),np.array([2.,3.]),1.01)

    def test_peak_and_trough_survive_plot_thinning(self):
        self.assertIsNotNone(extrema_indices)
        x=np.zeros(10000);x[463]=57;x[521]=-81
        ix=extrema_indices(x,100)
        self.assertIn(463,ix);self.assertIn(521,ix)
        self.assertTrue(np.all(np.diff(ix)>0))

    def test_corrupt_data_is_rejected(self):
        self.assertIsNotNone(verify_hash)
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/'data.npz';p.write_bytes(b'corrupt')
            with self.assertRaisesRegex(ValueError,'Source hash mismatch'):verify_hash(p,'0'*64)

if __name__=='__main__':unittest.main()
class EventTests(unittest.TestCase):
    def test_fault_event_ignores_initial_solver_state(self):
        import data_access
        self.assertTrue(hasattr(data_access,'first_state_time'))
        time=data_access.first_state_time([0,.00001,.49,.5,.50001],[0,2,2,2,0],0,after=.49)
        self.assertEqual(time,.50001)

