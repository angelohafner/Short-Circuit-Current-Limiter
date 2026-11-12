"""Validate real-data synchronization, media, source preservation, and reproducibility."""
import argparse
import json
import subprocess
import sys
import numpy as np
from data_access import ROOT, Measurements, verify_hash, sha256, first_state_time
from source_reader import fit_phasor
from render_video import probe, SCENES

def validate(media=True):
    d=Measurements(); checks=[]
    def check(name,ok,detail=None):
        checks.append({'name':name,'pass':bool(ok),'detail':detail})
    for case in 'ABC':
        t=d.array(case,'time')
        check(case+' native step and continuity',np.allclose(np.diff(t),1e-5,rtol=0,atol=1e-10),len(t))
        for p in 'ABC':
            error=d.array(case,'I1'+p)+d.array(case,'I2'+p)-d.array(case,'IF'+p)-d.array(case,'ILOAD'+p)
            check(case+p+' network KCL',np.max(np.abs(error))<1e-5,float(np.max(np.abs(error))))
        if case in 'BC':
            for p in 'ABC':
                error=d.array(case,'I1'+p)-d.array(case,'IC'+p)-d.array(case,'IV'+p)+d.array(case,'IM'+p)
                check(case+p+' internal KCL',np.max(np.abs(error))<1e-5,float(np.max(np.abs(error))))
            before=(t>=.4)&(t<.49)
            check(case+' no protective firing before fault',not np.any(d.array(case,'Gate')[before]))
            native=np.any([d.array(case,'TON'+p+s)>d.array(case,'TOFF'+p+s) for p in 'ABC' for s in 'PN'],axis=0)
            check(case+' conduction decoded from device timestamps',np.array_equal(native,d.array(case,'SCR_ANY')))
    for case in 'AB':
        t=d.array(case,'time');mask=(t>=.95)&(t<1.05)
        for prefix in ['I1','I2','IF']:
            rms=float(np.mean([abs(fit_phasor(t[mask],d.array(case,prefix+p)[mask])) for p in 'ABC']))
            check(case+prefix+' displayed RMS matches native fit',abs(rms-d.meta['metrics'][case][prefix+'_rms_kA'])<1e-9,rms)
    check('Gate-off does not extinguish SCRs',d.value('C','Gate',.70)==0 and d.conducting('C',.70))
    fault_time=first_state_time(d.array('B','time'),d.array('B','FSA'),0,after=.49)
    check('Fault uses recorded closure after initialization',abs(fault_time-.50001)<1e-10 and d.value('B','FSA',.5)==2,fault_time)
    check('Detection delay from physical closure',abs((d.meta['events']['B']['detect_s']-fault_time)*1000-.37)<1e-8)
    check('Conduction delay from physical closure',abs((d.meta['events']['B']['first_conduction_s']-fault_time)*1000-.48)<1e-8)
    check('All SCRs off before reclosure',not d.conducting('C',1.19))
    check('Feeder opens before gate withdrawal',d.meta['events']['C']['all_poles_open_s']<d.meta['events']['C']['gate_off_s'])
    check('Fault removed before reclosure',all(d.value('C','FS'+p,1.19)==2 for p in 'ABC'))
    check('All feeder poles closed after reclosure',all(d.value('C','BR'+p,1.201)==0 for p in 'ABC'))
    check('No SCR retrigger on reclosure',not np.any(d.array('C','SCR_ANY')[d.array('C','time')>1.19]))
    extension=d.meta['extension']
    check('Recovery settled at 2.5 s',extension['last_window_sliding_rms_ripple_percent']<.2,extension['last_window_sliding_rms_ripple_percent'])
    check('Native extended run licensed and fresh',extension['licensed'] and extension['fresh_outputs'] and not extension['errors'])
    # Sources may be absent in a portable video-only extraction. Report absence;
    # it must never be represented as a successful raw-source reverification.
    source_status={};study=ROOT.parents[1]
    for case,source in d.provenance['sources'].items():
        folder=study/source['relative_to_study']
        if folder.exists():
            for filename,expected in source['output_sha256'].items():verify_hash(folder/filename,expected)
            source_status[case]='ALL RAW INF/OUT HASHES VERIFIED'
        else:source_status[case]='RAW SOURCE ABSENT; compact dataset verified'
    for path,expected in extension['protected_original_hashes'].items():
        original=study/path
        if original.exists():
            check('Protected original '+path,sha256(original)==expected)
    if media:
        path=ROOT/'output/SCCL_TPSC_final.mp4';p=probe(path)
        video=next(x for x in p['streams'] if x['codec_type']=='video')
        check('1920 x 1080',video['width']==1920 and video['height']==1080)
        check('30 fps',video['avg_frame_rate']=='30/1',video['avg_frame_rate'])
        check('102 seconds',abs(float(p['format']['duration'])-102)<.1,p['format']['duration'])
        check('H.264 portable video',video['codec_name']=='h264' and video['pix_fmt']=='yuv420p')
        decoded=subprocess.run(['ffmpeg','-v','error','-i',str(path),'-f','null','-'],capture_output=True,text=True)
        check('Full video decode',decoded.returncode==0 and not decoded.stderr,decoded.stderr)
    report={'passed':sum(c['pass'] for c in checks),'total':len(checks),'checks':checks,'source_status':source_status,
            'compact_sha256':d.provenance['compact_sha256'],'video_sha256':sha256(ROOT/'output/SCCL_TPSC_final.mp4') if media else None}
    (ROOT/'evidence/validation.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'passed':report['passed'],'total':report['total'],'failed':[x for x in checks if not x['pass']]},indent=2))
    if report['passed']!=report['total']:raise SystemExit(1)
    return report

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--data-only',action='store_true');args=parser.parse_args();validate(not args.data_only)
