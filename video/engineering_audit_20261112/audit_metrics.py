"""Read-only engineering cross-checks of the delivered video and its data."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import subprocess
import numpy as np

HERE = Path(__file__).resolve().parent
REV = HERE.parent / 'SCCL_TPSC_Narrated_20261112'

def sha(path):
    with path.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()

def at(t, x, when):
    return float(x[np.searchsorted(t, when, side='right') - 1])

def first(t, condition, after=.49):
    return float(t[np.flatnonzero((t >= after) & condition)[0]])

def recovery_screen_time(electrical_time):
    stages = [(81., .49), (88., .58994), (91., .65606), (95., .81892),
              (97., .83761), (100., 1.2), (103., 1.25), (108., 2.5)]
    for (v0, t0), (v1, t1) in zip(stages, stages[1:]):
        if t0 <= electrical_time <= t1:
            return v0 + (electrical_time-t0)/(t1-t0)*(v1-v0)
    raise ValueError(electrical_time)

def main():
    provenance = json.loads((REV/'data/provenance.json').read_text())
    data_hashes = {name: sha(REV/'data'/name) == expected
                   for name, expected in provenance['compact_sha256'].items()}
    assert all(data_hashes.values())
    manifest = json.loads((REV/'narration/narration_manifest.json').read_text())
    movie = REV/'output/SCCL_TPSC_Narrated_EN.mp4'
    assert sha(movie) == manifest['video_sha256']
    with np.load(REV/'data/measurements.npz', allow_pickle=False) as packed:
        d = {name: packed[name] for name in packed.files}
    rms = {}
    kcl = {}
    for case in 'ABC':
        t = d[case+'__time']
        kcl[case] = max(float(np.max(np.abs(d[case+'__I1'+p] + d[case+'__I2'+p]
                           - d[case+'__IF'+p] - d[case+'__ILOAD'+p]))) for p in 'ABC')
        if case in 'AB':
            mask = (t >= .95) & (t < 1.05)
            fit = np.column_stack([np.cos(2*np.pi*60*t[mask]),
                                   np.sin(2*np.pi*60*t[mask]), np.ones(mask.sum())])
            rms[case] = {}
            for prefix in ['I1', 'I2', 'IF']:
                values = []
                for p in 'ABC':
                    a, b, dc = np.linalg.lstsq(fit, d[case+'__'+prefix+p][mask], rcond=None)[0]
                    values.append(float(np.hypot(a,b)/np.sqrt(2)))
                rms[case][prefix] = {'phases_kA': values, 'mean_kA': float(np.mean(values))}
    t = d['C__time']
    events = {}
    for name, condition in [
        ('feeder_trip_command', d['C__FeederOpen'] > .5),
        *[(f'feeder_pole_{p}_open', d['C__BR'+p] > 1.5) for p in 'ABC'],
        ('fault_removed_all_phases', np.all([d['C__FS'+p] > 1.5 for p in 'ABC'],axis=0)),
        ('gates_off', d['C__Gate'] < .5),
        ('all_SCR_off', np.all([d['C__TON'+p+s] <= d['C__TOFF'+p+s] for p in 'ABC' for s in 'PN'],axis=0)),
        ('recovery_ready', d['C__Recovery'] > .5),
        ('reclose_command', d['C__Reclose'] > .5),
    ]:
        when = first(t, condition, after=.58)
        events[name] = {'electrical_s': when, 'video_s_approx': recovery_screen_time(when)}
    n = round(1/(60*(t[1]-t[0])))
    def sliding_rms(values):
        sums=np.cumsum(np.r_[0., values])
        return np.sqrt(np.maximum(0., (sums[n:]-sums[:-n])/n))
    aggregate=sliding_rms(sum(d['C__I1'+p]**2 for p in 'ABC')/3)
    phase_a=sliding_rms(d['C__I1A']**2)
    rms_times=t[n-1:]
    rms_definition={'window_samples':n,'window_s':n*float(t[1]-t[0]),
                    'max_error_against_native_kA':float(np.max(np.abs(aggregate-d['C__RMS1'][n-1:]))),
                    'examples':[]}
    for when in [.51,.64,1.2431]:
        i=np.searchsorted(rms_times,when)
        rms_definition['examples'].append({'electrical_s':float(rms_times[i]),
                   'aggregate_RMS_kA':float(aggregate[i]),'phase_A_RMS_kA':float(phase_a[i])})
    after_close=(t>=1.2)&(t<=2.5)
    settled=(t>=2.4)&(t<=2.5)
    peak=float(np.max(d['C__RMS1'][after_close]))
    steady=float(np.mean(d['C__RMS1'][settled]))
    transient={'RMS1_peak_kA':peak,'RMS1_settled_mean_kA':steady,
               'overshoot_percent':100*(peak/steady-1)}
    widths = {}
    plot_windows = [('fault_transfer', 'B', .499, .516,
                     {'I1A': [-30,30], 'ICA': [-4,4], 'IVA': [-30,30], 'VCA': [-2.5,2.5]}),
                    ('recovery', 'C', .49, 2.5,
                     {'IVA': [-30,30], 'VCA': [-3,3], 'RMS1': [0,16]}),
                    ('reclosure_detail', 'C', 1.2, 2.5, {'RMS1': [0,.3]}),
                    ('comparison_A','A',.49,.62,{'IFA':[-220,220]}),
                    ('comparison_B','B',.49,.62,{'IFA':[-220,220]})]
    for scene, case, lo, hi, limits in plot_windows:
        times=d[case+'__time']; mask=(times>=lo)&(times<=hi)
        for channel,(lower,upper) in limits.items():
            values=d[case+'__'+channel][mask]
            low,high=float(values.min()),float(values.max())
            widths[scene+'_'+channel]={'min':low,'max':high,'display_limits':[lower,upper],
                                      'within_axes':low>=lower and high<=upper}
    tb=d['B__time']
    fault=first(tb,d['B__FSA']<.5)
    detect=first(tb,d['B__Detect']>.5)
    conduction=first(tb,np.any([d['B__TON'+p+s]>d['B__TOFF'+p+s] for p in 'ABC' for s in 'PN'],axis=0))
    decode=subprocess.run(['ffmpeg','-v','error','-i',str(movie),'-map','0:v:0','-map','0:a:0','-f','null','-'],capture_output=True,text=True)
    result={'verified_utc':datetime.now(timezone.utc).isoformat(),'video':str(movie),
            'video_sha256':sha(movie),'compact_hashes_match':data_hashes,
            'full_audio_video_decode':decode.returncode==0 and not decode.stderr,
            'kcl_max_absolute_error_kA':kcl,'independent_fundamental_rms':rms,
            'reduction_percent':100*(1-rms['B']['IF']['mean_kA']/rms['A']['IF']['mean_kA']),
            'reactance_ohm':{'L':2*np.pi*60*.0159,'C':1/(2*np.pi*60*442.5e-6)},
            'detection_ms':1000*(detect-fault),'first_conduction_ms':1000*(conduction-fault),
            'recovery_events':events,'recovery_RMS_definition':rms_definition,
            'reclosing_transient':transient,
            'clearing_narration':next(row for row in manifest['segments'] if row['id']=='10_clear'),
            'plot_extents':widths,
            'frame_sampling':'32 frames at exactly 0,4,...124 s plus 17 exact-time full-resolution frames',
            'new_simulation':False}
    (HERE/'audit_metrics.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))

if __name__=='__main__':
    main()
