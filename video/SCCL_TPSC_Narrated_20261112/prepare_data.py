"""Extract real PSCAD measurements; verify source receipts before reading OUT files."""
from pathlib import Path
import argparse
import json
import re
import shutil
import numpy as np
from data_access import ROOT, sha256, verify_hash
from source_reader import read_outputs, fit_phasor

DISCRETE = ['Gate','Detect','Pickup','FeederOpen','FaultOpen','Recovery','Reclose','BRA','BRB','BRC','FSA','FSB','FSC','EnergyTrip']

def metric(t, d):
    m = (t >= .95) & (t < 1.05)
    result = {p+'_rms_kA': float(np.mean([abs(fit_phasor(t[m], d[p+ph][m])) for ph in 'ABC']))
              for p in ['I1','I2','IF']}
    fault = (t >= .5) & (t < 1.1)
    result['peak_kA'] = max(float(np.max(np.abs(d['IF'+ph][fault]))) for ph in 'ABC')
    result['window_s'] = [.95, 1.05]
    if 'VCA' in d:
        result['capacitor_peak_kV'] = max(float(np.max(np.abs(d['VC'+ph]))) for ph in 'ABC')
    return result

def first(t, mask, after=0):
    indices = np.flatnonzero(mask & (t >= after))
    return float(t[indices[0]]) if len(indices) else None

def main(study):
    selected = json.loads((study/'results/selected_runs.json').read_text())
    extension = json.loads((ROOT/'evidence/extended_recovery_receipt.json').read_text())
    paths = {'A':study/selected['without_sccl'], 'B':study/selected['with_sccl'],
             'C':ROOT/extension['relative_result_directory']}
    for L in [10,12,20,25]:
        paths[f'L{L}'] = study/selected[f'sensitivity/L_{L}mH_angle_0']
    for L in [10,25]:
        paths[f'fixed{L}'] = study/selected[f'fixed_C/L_{L}mH_C_442p5uF']
    arrays, sources, metrics, sensitivity, events = {}, {}, {}, [], {}
    (ROOT/'data').mkdir(exist_ok=True)
    (ROOT/'data/receipts').mkdir(exist_ok=True)
    (ROOT/'pscad').mkdir(exist_ok=True)
    for case, path in paths.items():
        receipt = json.loads((path/'run_receipt.json').read_text())
        assert receipt['licensed'] and receipt['fresh_outputs'] and not receipt['errors']
        for filename, expected in receipt['output_sha256'].items():
            verify_hash(path/filename, expected)
        models = list(path.glob('*.pscx'))
        assert len(models) == 1
        verify_hash(models[0], receipt['project_sha256'])
        shutil.copy2(path/'run_receipt.json', ROOT/f'data/receipts/{case}.json')
        if case in 'ABC':
            shutil.copy2(models[0], ROOT/'pscad'/models[0].name)
        print(f'VERIFIED NATIVE SOURCE {case}: {path.name}', flush=True)
        t,d = read_outputs(path)
        units = dict(re.findall(r'Desc="([^"]+)".*?Units="([^"]+)"', next(path.glob('*.inf')).read_text()))
        sources[case] = {'relative_to_study': str(path.relative_to(study)).replace('\\','/'),
                         'output_sha256':receipt['output_sha256'], 'project_sha256':receipt['project_sha256'],
                         'samples':len(t), 'step_s':float(np.median(np.diff(t))), 'units':units}
        if case != 'C':
            metrics[case] = metric(t,d)
        if case in 'ABC':
            arrays[case+'__time'] = t
            names = [n for n in d if n.startswith(('I1','I2','IF','ILOAD','IC','IV','VC','IM','EM','TON','TOFF')) or n in DISCRETE or n in ['RMS1','RMS2','RMSF','ITAP','ITAN','ITBP','ITBN','ITCP','ITCN']]
            for name in names:
                arrays[case+'__'+name] = d[name].astype(np.uint8) if name in DISCRETE else d[name]
            if case in 'BC':
                on = np.any([d['TON'+p+s] > d['TOFF'+p+s] for p in 'ABC' for s in 'PN'], axis=0)
                arrays[case+'__SCR_ANY'] = on.astype(np.uint8)
                events[case] = {'detect_s':first(t,d['Detect']>.5,.5),'gate_on_s':first(t,d['Gate']>.5,.5),
                               'first_conduction_s':first(t,on,.5)}
                if case == 'C':
                    events[case].update(gate_off_s=first(t,d['Gate']<.5,.6),
                        all_poles_open_s=first(t,(d['BRA']>.5)&(d['BRB']>.5)&(d['BRC']>.5),.58),
                        last_SCR_off_s=float(max(d['TOFF'+p+s][-1] for p in 'ABC' for s in 'PN')),
                        recovery_s=first(t,d['Recovery']>.5,.6),reclose_s=first(t,d['Reclose']>.5,1))
        if case.startswith('L') or case == 'B' or case.startswith('fixed'):
            sensitivity.append({'case':case, 'L_mH':receipt['L_mH'],'C_uF':receipt['C_uF'], **metrics[case]})
    meta = {'frequency_Hz':60,'voltage_LL_kV':138,'discrete_channels':DISCRETE,
            'metrics':metrics,'events':events,'sensitivity':sensitivity,'extension':extension,
            'waveforms':'Native EMTDC samples, unscaled; plotting retains local extrema.',
            'signs':'I1 = IC + IV - IM; I1 + I2 = IF + ILOAD; IV includes SCR snubbers.',
            'rms_definition':'Mean of three phase 60 Hz phasor magnitudes, least squares with DC term, 0.95 <= t < 1.05 s.'}
    np.savez_compressed(ROOT/'data/measurements.npz', **arrays)
    (ROOT/'data/metadata.json').write_text(json.dumps(meta,indent=2)+'\n')
    prov={'sources':sources,'compact_sha256':{p.name:sha256(p) for p in [ROOT/'data/measurements.npz',ROOT/'data/metadata.json']},
          'generator_sha256':sha256(__file__),'reader_sha256':sha256(ROOT/'source_reader.py'),
          'raw_policy':'Raw INF/OUT files remain in the study; the video package contains exact selected channels and source hashes.'}
    (ROOT/'data/provenance.json').write_text(json.dumps(prov,indent=2)+'\n')
    print(json.dumps({'metrics':{k:v for k,v in metrics.items() if k in 'AB'},'events':events},indent=2))

if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--study',type=Path,default=ROOT.parents[1])
    main(parser.parse_args().study.resolve())
