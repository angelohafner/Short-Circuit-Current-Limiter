"""Run the five-by-three reactor/inception-angle matrix and numerical checks."""
import argparse
import math
import json
from common import ROOT,PARAM,connect,write_json,sha
from run_simulations import run

ap=argparse.ArgumentParser();ap.add_argument('--port',type=int,default=63579);ap.add_argument('--resume',action='store_true');args=ap.parse_args()
selected=json.loads((ROOT/'results/selected_runs.json').read_text())
jobs=[]
for angle in PARAM['fault_inception_phase_degrees']:
    if angle:jobs.append(dict(case='without_sccl',label=f'baseline_angle_{angle:g}',angle=angle,step_us=10))
    for lm in PARAM['sensitivity_L_mH']:
        if angle==0 and lm==15.9:continue
        cap=PARAM['capacitor_C_uF'] if lm==15.9 else 1e6/((2*math.pi*60)**2*lm/1000)
        jobs.append(dict(case='with_sccl',label=f'sensitivity/L_{lm:g}mH_angle_{angle:g}',L_mH=lm,C_uF=cap,angle=angle,step_us=10))
for case in ['without_sccl','with_sccl','recovery']:
    jobs.append(dict(case=case,label=f'convergence/{case}_5us',L_mH=15.9 if case!='without_sccl' else None,C_uF=442.5 if case!='without_sccl' else None,angle=0,step_us=5))
for lm in [10,25]:
    jobs.append(dict(case='with_sccl',label=f'fixed_C/L_{lm}mH_C_442p5uF',L_mH=lm,C_uF=442.5,angle=0,step_us=10))
write_json(ROOT/'config/run_matrix.json',jobs)
def reusable(job):
    if job['label'] not in selected:return False
    folder=ROOT/selected[job['label']]
    try:
        receipt=json.loads((folder/'run_receipt.json').read_text())
        if receipt.get('configuration_sha256')!=sha(ROOT/'config/parameters.json'):return False
        if receipt['errors'] or not receipt['fresh_outputs']:return False
        for key in ['case','L_mH','C_uF']:
            if receipt.get(key)!=job.get(key):return False
        if receipt['source_phase_deg']!=job['angle']:return False
        if float(receipt['project_parameters']['time_step'])!=job['step_us']:return False
        if sha(next(folder.glob('*.pscx')))!=receipt['project_sha256']:return False
        return all(sha(folder/name)==digest for name,digest in receipt['output_sha256'].items())
    except (KeyError,StopIteration,OSError,ValueError):return False

for i,job in enumerate(jobs):
    if args.resume and reusable(job):
        print('SKIP completed',job['label'],flush=True);continue
    print('MATRIX',i+1,'OF',len(jobs),job['label'],flush=True)
    run(port=args.port,**job)
# Restore and execute final nominal native sources, binding their saved files to runs.
for case in ['without_sccl','with_sccl','recovery']:
    run(case=case,port=args.port,L_mH=15.9 if case!='without_sccl' else None,
        C_uF=442.5 if case!='without_sccl' else None,angle=0,step_us=10)
print('MATRIX COMPLETE',flush=True)
