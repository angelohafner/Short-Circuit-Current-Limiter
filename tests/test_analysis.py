"""Independent numerical checks, not substitutes for EMTDC validation."""
import sys
import unittest
import tempfile
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
try:
    from analysis_core import fit_phasor, fault_reference, read_outputs
except ImportError:
    fit_phasor = fault_reference = read_outputs = None

class AnalysisTests(unittest.TestCase):
    def test_two_source_dc_modes_do_not_bias_fault_phasor(self):
        t=np.arange(.54,.58,1e-5)
        expected=50*np.exp(-1.51j)
        x=np.sqrt(2)*np.real(expected*np.exp(2j*np.pi*60*t))+30*np.exp(-(t-.5)/.074)+55*np.exp(-(t-.5)/.039)
        got=fit_phasor(t,x,60,tau=[.074,.039])
        self.assertLess(abs(got-expected),1e-7)

    def test_incomplete_study_cannot_pass_final_preflight(self):
        try:
            from delivery_checks import require_run_index
        except ImportError:
            require_run_index=None
        self.assertIsNotNone(require_run_index,'Final completeness gate is not implemented')
        with self.assertRaisesRegex(ValueError,'Missing required native runs'):
            require_run_index({'without_sccl':'a','with_sccl':'b','recovery':'c'})

    def test_untrusted_cache_cannot_replace_native_measurements(self):
        from analyze_results import load_run
        with tempfile.TemporaryDirectory() as temporary:
            folder=Path(temporary)
            (folder/'Case.inf').write_text('PGB(1) Output Desc="VCA" Group="SCCL"\n')
            (folder/'Case_01.out').write_text('time VCA\n0.00 1.0\n0.01 2.0\n')
            np.savez_compressed(folder/'waveforms.npz',time_s=np.array([0,.01]),VCA=np.array([999.,999.]))
            t,d=load_run(folder)
            np.testing.assert_array_equal(d['VCA'],[1.,2.])

    def test_phasor_separates_dc_offset(self):
        self.assertIsNotNone(fit_phasor,'Phasor estimator is not implemented')
        t=np.arange(0.54,0.58,1e-5)
        expected=40*np.exp(0.37j)
        x=np.sqrt(2)*np.real(expected*np.exp(2j*np.pi*60*t))+50*np.exp(-(t-.5)/.04)
        got=fit_phasor(t,x,60,tau=.04)
        self.assertLess(abs(got-expected),1e-7)

    def test_phasor_sum_not_magnitude_sum(self):
        self.assertIsNotNone(fault_reference,'Thevenin reference is not implemented')
        result=fault_reference(79.6743,0.1325+1.9874j,0.101+5.994j,.0051)
        self.assertAlmostEqual(abs(result['total']),abs(result['source1']+result['source2']),places=10)
        self.assertLess(abs(result['total']),abs(result['source1'])+abs(result['source2']))
        self.assertLess(abs(abs(result['total'])-50),1)

    def test_missing_output_is_rejected(self):
        self.assertIsNotNone(read_outputs,'Native output reader is not implemented')
        with self.assertRaises(FileNotFoundError):
            read_outputs(Path('definitely_missing_native_outputs'))

if __name__=='__main__': unittest.main()
