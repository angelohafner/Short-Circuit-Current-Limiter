"""Execute native PSCAD cases and preserve timestamped, hash-bound evidence."""
from pathlib import Path
from datetime import datetime,timezone
import argparse
import shutil
import json
import numpy as np
from common import ROOT,PARAM,connect,write_json,sha
from analysis_core import read_outputs

NAMES={'without_sccl':'SCCL_A_Without','with_sccl':'SCCL_B_With','recovery':'SCCL_C_Recovery'}

def run(case='with_sccl',port=63579,label=None,L_mH=None,C_uF=None,angle=None,step_us=None):
    app=connect(port);name=NAMES[case];path=ROOT/'pscad'/(name+'.pscx')
    if not any(d['name']==name for d in app.projects()):app.load(str(path))
    p=app.project(name);assert Path(p.filename).resolve()==path.resolve()
    c=p.canvas('Main')
    for phase in 'ABC':
        if L_mH is not None:c.find('master:inductor',Name='Reactor_L_'+phase).parameters(L=f'{L_mH} [mH]')
        if C_uF is not None:c.find('master:capacitor',Name='Capacitor_C_'+phase).parameters(C=f'{C_uF} [uF]')
    if angle is not None:
        for i in [1,2]:c.find('master:source3',Name=f'Source_{i}').parameters(Ph=f'{angle} [deg]')
    if step_us is not None:p.parameters(time_step=step_us,sample_step=step_us)
    actual_phases=[float(str(c.find('master:source3',Name=f'Source_{i}').parameters()['Ph']).split()[0]) for i in [1,2]]
    assert abs(actual_phases[0]-actual_phases[1])<1e-9,'This balanced study requires equal source phase settings'
    p.save();assert path.exists() and not p.is_dirty(),'PSCAD did not save the project'
    stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S_%fZ')
    label=label or case;dst=ROOT/'results'/label/stamp;dst.mkdir(parents=True)
    shutil.copy2(path,dst/path.name)
    started=datetime.now(timezone.utc)
    print('RUN',label,'STEP',p.parameters()['time_step'],'DEST',dst,flush=True)
    p.run()
    finished=datetime.now(timezone.utc)
    messages=p.messages();errors=[str(m) for m in messages if m.status=='error']
    (dst/'run_messages.txt').write_text('\n'.join(str(m) for m in messages),encoding='utf8')
    build=path.with_suffix('.gf81')
    files=[build/(name+'.inf')]+sorted(build.glob(name+'_*.out'))
    fresh=len(files)>1 and all(f.exists() and f.stat().st_mtime>=started.timestamp()-2 for f in files)
    receipt={'case':case,'label':label,'start_utc':started.isoformat(),'finish_utc':finished.isoformat(),
             'pscad_version':app.version,'licensed':app.licensed(),'project_sha256':sha(path),
             'fresh_outputs':fresh,'errors':errors,'project_parameters':p.parameters(),
             'L_mH':L_mH,'C_uF':C_uF,'requested_source_phase_deg':angle,'source_phase_deg':actual_phases[0],
             'configuration_sha256':sha(ROOT/'config/parameters.json'),
             'output_sha256':{f.name:sha(f) for f in files if f.exists()},'result_directory':str(dst)}
    for f in files:
        if f.exists():shutil.copy2(f,dst/f.name)
    for ext in ['*.f','*.mak','*.log','*.map']:
        for f in build.glob(ext):shutil.copy2(f,dst/f.name)
    write_json(dst/'run_receipt.json',receipt)
    assert fresh and not errors,receipt
    t,d=read_outputs(dst)
    assert t[-1]>=PARAM['duration_s']-2*float(p.parameters()['sample_step'])*1e-6,'Incomplete EMTDC run'
    np.savez_compressed(dst/'waveforms.npz',time_s=t,**d)
    selection=ROOT/'results/selected_runs.json';selected=json.loads(selection.read_text()) if selection.exists() else {}
    selected[label]=str(dst.relative_to(ROOT)).replace('\\','/');write_json(selection,selected)
    for group in ['I1','I2','IF']:
        mask=(t>.95)&(t<1.05)
        print(group,'RMS',np.sqrt(np.mean(np.column_stack([d[group+ph][mask] for ph in 'ABC'])**2)),flush=True)
    print('GATE',[(k,float(np.min(d[k])),float(np.max(d[k]))) for k in ['Gate','Detect','Vmax','ValveOn','Recovery']],flush=True)
    print('FINISHED',label,'SAMPLES',len(t),flush=True)
    return dst

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--case',choices=list(NAMES),default='with_sccl');a.add_argument('--port',type=int,default=63579)
    a.add_argument('--label');a.add_argument('--L-mH',type=float);a.add_argument('--C-uF',type=float);a.add_argument('--angle',type=float);a.add_argument('--step-us',type=float)
    q=a.parse_args();run(q.case,q.port,q.label,q.L_mH,q.C_uF,q.angle,q.step_us)
