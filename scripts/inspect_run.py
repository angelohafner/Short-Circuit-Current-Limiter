"""Compact electrical diagnostic summary from a selected native run."""
import argparse
import json
import numpy as np
from common import ROOT
from analysis_core import read_outputs,fit_phasor
ap=argparse.ArgumentParser();ap.add_argument('label',nargs='?',default='with_sccl');a=ap.parse_args()
selected=json.loads((ROOT/'results/selected_runs.json').read_text());path=ROOT/selected[a.label]
t,d=read_outputs(path)
for lo,hi in [(0.4,0.48),(.53,.58),(.95,1.05),(1.4,1.49)]:
    ix=(t>=lo)&(t<hi)
    print('WINDOW',lo,hi)
    for prefix in ['I1','I2','IF']:
        print(prefix,'phasor RMS',[round(abs(fit_phasor(t[ix],d[prefix+ph][ix])),5) for ph in 'ABC'])
for ph in 'ABC':
    print('KCL',ph,'max kA',np.max(np.abs(d['I1'+ph]+d['I2'+ph]-d['IF'+ph]-d['ILOAD'+ph])))
    if 'IC'+ph in d:
        for sign in [-1,1]:print('INTERNAL KCL',ph,'MOV sign',sign,np.max(np.abs(d['I1'+ph]-d['IC'+ph]-d['IV'+ph]-sign*d['IM'+ph])))
for name in ['Detect','Gate','FeederOpen','FaultOpen','Recovery','Reclose','ValveOn','EnergyTrip','BRA','BRB','BRC']:
    transitions=np.flatnonzero(np.diff(d[name])!=0)+1
    print(name,'TRANSITIONS',[(round(float(t[i]),7),float(d[name][i])) for i in transitions[:30]],'COUNT',len(transitions))
for name in ['VCA','VCB','VCC','IVA','IVB','IVC','EMA','EMB','EMC']:
    if name in d:print(name,'MIN MAX',float(np.min(d[name])),float(np.max(d[name])))
