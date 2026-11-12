"""Execute an isolated, longer native recovery case without changing originals."""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import json
import shutil
import hashlib
import sys
import mhi.pscad

ROOT=Path(__file__).resolve().parent
STUDY=ROOT.parents[1]
sys.path.insert(0,str(STUDY/'scripts'))
from analysis_core import read_outputs,fit_phasor

def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def run(port=63579):
    import numpy as np
    protected={str(p.relative_to(STUDY)).replace('\\','/'):sha(p) for p in (STUDY/'pscad').glob('*.pscx')}
    app=mhi.pscad.connect(port=port,timeout=15);assert app.licensed()
    app.flags(silence=True);app.settings(fortran_version='GFortran 8.1 (64-bit)')
    directory=ROOT/'pscad';directory.mkdir(exist_ok=True)
    target=directory/'SCCL_C_Extended.pscx'
    assert not target.exists(),'Preserve an existing extended case; inspect its receipt before rerunning'
    original=STUDY/'pscad/SCCL_C_Recovery.pscx'
    if not any(p['name']=='SCCL_C_Recovery' for p in app.projects()):app.load(str(original))
    p=app.project('SCCL_C_Recovery').save_as(str(target))
    p.parameters(time_duration=2.5,output_filename='SCCL_C_Extended.out',description='TPSC recovery extension to 2.5 seconds for educational animation')
    p.save()
    stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S_%fZ')
    result=ROOT/'native_results'/stamp;result.mkdir(parents=True)
    shutil.copy2(target,result/target.name)
    start=datetime.now(timezone.utc);print('NATIVE EXTENDED RUN',result,flush=True);p.run();finish=datetime.now(timezone.utc)
    errors=[str(x) for x in p.messages() if x.status=='error']
    build=target.with_suffix('.gf81');files=[build/'SCCL_C_Extended.inf']+sorted(build.glob('SCCL_C_Extended_*.out'))
    assert len(files)>1 and not errors,errors
    assert all(x.stat().st_mtime>=start.timestamp()-2 for x in files)
    for x in files:shutil.copy2(x,result/x.name)
    (result/'run_messages.txt').write_text('\n'.join(str(x) for x in p.messages()),encoding='utf8')
    t,d=read_outputs(result);assert t[-1]>=2.49999
    pre=(t>=.4)&(t<.48);post=(t>=2.3)&(t<2.5)
    rms=lambda mask:float(np.mean([abs(fit_phasor(t[mask],d['I1'+ph][mask])) for ph in 'ABC']))
    before,after=rms(pre),rms(post)
    ripple=float(np.ptp(d['RMS1'][post])/before*100)
    alloff=all(d['TOFF'+ph+pol][-1]>d['TON'+ph+pol][-1] for ph in 'ABC' for pol in 'PN')
    assert abs(after/before-1)<.01 and ripple<.2 and alloff,(before,after,ripple,alloff)
    assert all(sha(STUDY/name)==digest for name,digest in protected.items())
    receipt={'case':'recovery_extended','project_sha256':sha(target),'start_utc':start.isoformat(),'finish_utc':finish.isoformat(),
        'licensed':app.licensed(),'pscad_version':app.version,'fresh_outputs':True,'errors':errors,'duration_s':2.5,
        'relative_result_directory':result.relative_to(ROOT).as_posix(),'output_sha256':{x.name:sha(x) for x in files},
        'protected_original_hashes':protected,'originals_unchanged':True,'prefault_source1_rms_kA':before,
        'settled_source1_rms_kA':after,'last_window_sliding_rms_ripple_percent':ripple,'all_SCRs_off_at_end':alloff}
    for dest in [result/'run_receipt.json',ROOT/'evidence/extended_recovery_receipt.json']:
        dest.parent.mkdir(exist_ok=True);dest.write_text(json.dumps(receipt,indent=2),encoding='utf8')
    app.load(str(original));app.project('SCCL_C_Recovery').focus()
    print('NATIVE EXTENSION VERIFIED',before,after,'RMS ripple %',ripple,flush=True)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--port',type=int,default=63579);run(ap.parse_args().port)
