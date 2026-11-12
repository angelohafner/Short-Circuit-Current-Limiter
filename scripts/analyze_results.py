"""Verify actual EMTDC results, phasors, KCL, switching, stress and convergence."""
import json
import math
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
from common import ROOT,PARAM,write_json,sha
from analysis_core import read_outputs,fit_phasor,fault_reference

def load_run(path):
    # The NPZ is a convenience export, never an authority for validation or figures.
    # Read indexed native data so a stale/edited cache cannot change accepted results.
    return read_outputs(path)

def first(t,condition,after=.4):
    ix=np.flatnonzero(condition & (t>=after))
    return float(t[ix[0]]) if len(ix) else None

def component_value(root,name,key):
    for e in root.iter('User'):
        p={v.get('name'):v.get('value') for v in e.findall('./paramlist/param')}
        if p.get('Name')==name:return float(p[key].split()[0])
    raise KeyError(name)

def metrics(path,label):
    t,d=load_run(path);receipt=json.loads((path/'run_receipt.json').read_text())
    model=next(path.glob('*.pscx'));xml=ET.parse(model).getroot()
    case=receipt['case'];enabled='VCA' in d;dt=float(np.median(np.diff(t)))
    lm=component_value(xml,'Reactor_L_A','L') if enabled else 1e-6
    # Native values may be saved with H or mH units.
    node=next((e for e in xml.iter('User') if any(q.get('value')=='Reactor_L_A' for q in e.findall('./paramlist/param'))),None)
    if node is not None:
        val=next(q.get('value') for q in node.findall('./paramlist/param') if q.get('name')=='L')
        if '[mH]' in val:lm*=1e-3
    cap=component_value(xml,'Capacitor_C_A','C')*1e-6 if enabled else 0
    window=(.95,1.05) if case!='recovery' else (.54,.58)
    mask=(t>=window[0])&(t<window[1]);normal=(t>=.4)&(t<.48);post=(t>=1.4)&(t<1.49)
    fault=(t>=.5)&(t<(.583333 if case=='recovery' else 1.1))
    zs=complex(PARAM['source_R_ohm'],2*np.pi*60*PARAM['source_L_H'])
    zd=complex(.152,2*np.pi*60*(lm+.0001)) if enabled else complex(.001,2*np.pi*60*1e-6)
    ref=fault_reference(138/np.sqrt(3),zs,zd,.0051)
    phasors={};rms={}
    for prefix in ['I1','I2','IF']:
        # Recovery has a short window. Fit both coupled source-network DC modes.
        l1=PARAM['source_L_H']+lm+(.0001 if enabled else 0)
        l2=PARAM['source_L_H'];r1=.1325+(.152 if enabled else .001);r2=.1325;rf=.0051
        state=np.array([[-(r1+rf)/l1,-rf/l1],[-rf/l2,-(r2+rf)/l2]])
        taus=-1/np.linalg.eigvals(state)
        phasors[prefix]=[fit_phasor(t[mask],d[prefix+ph][mask],tau=taus if case=='recovery' else None) for ph in 'ABC']
        rms[prefix]=float(np.mean(np.abs(phasors[prefix])))
    residuals=[d['I1'+ph]+d['I2'+ph]-d['IF'+ph]-d['ILOAD'+ph] for ph in 'ABC']
    result=dict(label=label,case=case,path=str(path.relative_to(ROOT)).replace('\\','/'),
                model_sha256=sha(model),fresh_outputs=receipt['fresh_outputs'],step_us=receipt['project_parameters']['time_step'],
                source_phase_deg=component_value(xml,'Source_1','Ph'),L_mH=lm*1000,C_uF=cap*1e6,
                measurement_window_s=window,source1_rms_kA=rms['I1'],source2_rms_kA=rms['I2'],fault_rms_kA=rms['IF'],
                theoretical_source1_kA=abs(ref['source1']),theoretical_source2_kA=abs(ref['source2']),theoretical_total_kA=abs(ref['total']),
                fault_peak_kA=max(float(np.max(np.abs(d['IF'+ph][fault]))) for ph in 'ABC'),
                reactor_peak_kA=max(float(np.max(np.abs(d['I1'+ph][fault]))) for ph in 'ABC'),
                network_kcl_max_kA=max(float(np.max(np.abs(r))) for r in residuals),
                prefault_source1_rms_kA=float(np.mean([abs(fit_phasor(t[normal],d['I1'+ph][normal])) for ph in 'ABC'])),
                post_source1_rms_kA=float(np.mean([abs(fit_phasor(t[post],d['I1'+ph][post])) for ph in 'ABC'])),
                post_source2_rms_kA=float(np.mean([abs(fit_phasor(t[post],d['I2'+ph][post])) for ph in 'ABC'])))
    result['fault_phasor_sum_error_kA']=float(np.mean([abs(phasors['I1'][i]+phasors['I2'][i]-phasors['IF'][i]) for i in range(3)]))
    result['fault_phase_peaks_kA']={ph:float(np.max(np.abs(d['IF'+ph][fault]))) for ph in 'ABC'}
    result['source_equivalents_match_specification']=all(
        abs(component_value(xml,f'Source_{i}',key)-expected)<1e-9
        for i in [1,2] for key,expected in [('R1s',.1325),('Vm',138),('Es',138),('F',60),('F0',60),('Tc',.05)]) and all(
        abs(component_value(xml,f'Source{i}_L_{ph}','L')-.005272)<1e-12 for i in [1,2] for ph in 'ABC')
    expected_angle=float(label.rsplit('_angle_',1)[1]) if '_angle_' in label else 0
    result['source_phase_settings_match_case']=all(abs(component_value(xml,f'Source_{i}','Ph')-expected_angle)<1e-9 for i in [1,2])
    for name in ['Detect','Gate','ValveOn','Recovery','Reclose']:
        result[name+'_first_s']=first(t,d[name]>.5,after=.5)
    result['gate_removal_s']=first(t,(d['Gate']<.5),after=.55) if enabled else None
    result['last_pole_open_s']=max(first(t,d['BR'+ph]>1.5,after=.5) or 1.5 for ph in 'ABC')
    result['all_valves_below_1A_s']=first(t,d['ValveOn']<.5,after=result['gate_removal_s'] or .55) if enabled else None
    result['actual_fault_inception_s']=first(t,d['FS'+ 'A']<.5,after=.49)
    result['detection_delay_ms']=(result['Detect_first_s']-result['actual_fault_inception_s'])*1000 if enabled else None
    result['bypass_response_ms']=(result['ValveOn_first_s']-result['actual_fault_inception_s'])*1000 if enabled else None
    result['energy_interlock_triggered']=bool(np.max(d['EnergyTrip'])>.5)
    result['prefault_gate_active']=bool(np.max(d['Gate'][normal])>.5)
    result['prefault_fault_current_A']=1000*max(float(np.max(np.abs(d['IF'+ph][normal]))) for ph in 'ABC')
    if enabled:
        result['internal_kcl_max_kA']=max(float(np.max(np.abs(d['I1'+ph]-d['IC'+ph]-d['IV'+ph]+d['IM'+ph]))) for ph in 'ABC')
        for prefix,out in [('VC','capacitor_peak_kV'),('VL','reactor_voltage_peak_kV'),('IV','valve_branch_peak_kA'),('EM','MOV_energy_max_kJ'),('IM','MOV_peak_kA')]:
            result[out]=max(float(np.max(np.abs(d[prefix+ph]))) for ph in 'ABC')
        result['normal_MOV_peak_A']=1000*max(float(np.max(np.abs(d['IM'+ph][normal]))) for ph in 'ABC')
        result['MOV_voltage_peak_kV']=max(float(np.max(np.abs(d['VC'+ph]+.002*d['IC'+ph]))) for ph in 'ABC')
        result['SCR_voltage_peak_kV']=max(float(np.max(np.abs(d['VT'+ph+pol]))) for ph in 'ABC' for pol in 'PN')
        result['normal_drop_percent']=100*float(np.mean([abs(fit_phasor(t[normal],d['VDROP'+ph][normal])) for ph in 'ABC']))/(138/np.sqrt(3))
        result['normal_reactor_MVAr']=3*(result['prefault_source1_rms_kA']**2)*2*np.pi*60*lm
        result['normal_capacitor_MVAr']=3*(result['prefault_source1_rms_kA']**2)/(2*np.pi*60*cap)
        result['valve_I2t_kA2s']={ph+pol:float(np.trapezoid(d['IT'+ph+pol]**2,t)) for ph in 'ABC' for pol in 'PN'}
        result['gate_off_conduction_duration_ms']=1000*(result['all_valves_below_1A_s']-result['gate_removal_s'])
        result['last_SCR_turn_off_s']=max(float(d['TOFF'+ph+pol][-1]) for ph in 'ABC' for pol in 'PN')
        result['gate_off_to_last_SCR_turn_off_ms']=1000*(result['last_SCR_turn_off_s']-result['gate_removal_s'])
        result['all_SCRs_off_at_end']=all(d['TOFF'+ph+pol][-1]>d['TON'+ph+pol][-1] for ph in 'ABC' for pol in 'PN')
        # Entire SCCL electrical energy balance. SCR and snubber branch power is measured
        # at the switch terminals, including their dissipation and stored snubber energy.
        energy=[]
        for ph in 'ABC':
            i=d['I1'+ph];ic=d['IC'+ph];iv=d['IV'+ph];v=d['VC'+ph]
            stored=500*(lm*i*i+cap*v*v+.0001*iv*iv)
            # ITT and VT are native device outputs; signed product is passive power.
            switch_power=sum(d['VT'+ph+pol]*d['ITT'+ph+pol] for pol in 'PN')
            losses=1000*(.1*i*i+.002*ic*ic+.05*iv*iv+switch_power-(v+.002*ic)*d['IM'+ph])
            incoming=1000*d['VDROP'+ph]*i
            interval=(t>=.49)&(t<=.56);ix=np.flatnonzero(interval)
            balance=float(np.trapezoid((incoming-losses)[interval],t[interval])-(stored[ix[-1]]-stored[ix[0]]))
            scale=max(float(np.max(stored[interval])),1)
            energy.append(dict(phase=ph,residual_kJ=balance,maximum_stored_kJ=scale,relative_residual_percent=100*abs(balance)/scale))
        result['energy_balance']=energy
    return result

def analyze(partial=False):
    selected=json.loads((ROOT/'results/selected_runs.json').read_text());summary={};checks=[]
    if not partial:
        from delivery_checks import require_run_index
        require_run_index(selected)
    def check(name,condition,value=None):checks.append(dict(name=name,pass_=bool(condition),value=value))
    for label,relative in selected.items():
        path=ROOT/relative;m=metrics(path,label);summary[label]=m
        r=json.loads((path/'run_receipt.json').read_text())
        check(label+': fresh EMTDC receipt',r['fresh_outputs'] and not r['errors'])
        check(label+': source-bound project',m['model_sha256']==r['project_sha256'])
        check(label+': complete native output hashes',all(sha(path/n)==h for n,h in r['output_sha256'].items()))
        check(label+': unchanged specified source equivalents',m['source_equivalents_match_specification'])
        check(label+': both source phase settings match case label',m['source_phase_settings_match_case'])
        check(label+': network KCL < 1 A',m['network_kcl_max_kA']<.001,m['network_kcl_max_kA'])
        if 'internal_kcl_max_kA' in m:
            check(label+': internal KCL < 1 A',m['internal_kcl_max_kA']<.001,m['internal_kcl_max_kA'])
            check(label+': capacitor within assumed 15 kV peak operating envelope',m['capacitor_peak_kV']<15,m['capacitor_peak_kV'])
            check(label+': bypass before feeder opening',m['ValveOn_first_s']<m['last_pole_open_s'])
            check(label+': no energy lockout',not m['energy_interlock_triggered'])
            check(label+': thyristors blocked during normal operation',not m['prefault_gate_active'])
            check(label+': bypass-transition energy residual below 1%',max(e['relative_residual_percent'] for e in m['energy_balance'])<1,max(e['relative_residual_percent'] for e in m['energy_balance']))
        if m['case']!='recovery':
            for source in ['source1','source2']:
                deviation=100*abs(m[source+'_rms_kA']/m['theoretical_'+source+'_kA']-1)
                check(label+': '+source+' phasor within 2% of circuit reference',deviation<2,deviation)
        print('ANALYZED',label,round(m['fault_rms_kA'],4),flush=True)
    if 'without_sccl' in summary:
        base=summary['without_sccl']['fault_rms_kA']
        for m in summary.values():m['total_rms_reduction_percent']=100*(1-m['fault_rms_kA']/base)
        for label,target in [('without_sccl',80),('with_sccl',50)]:
            if label in summary:check(label+': RMS within 5% of requested target',abs(summary[label]['fault_rms_kA']/target-1)<.05)
    if 'recovery' in summary:
        m=summary['recovery']
        check('recovery: naturally conducting after gate removal',m['gate_off_conduction_duration_ms']>0,m['gate_off_conduction_duration_ms'])
        check('recovery: native SCR turn-off before recovery-ready',m['last_SCR_turn_off_s']<m['Recovery_first_s'],m['last_SCR_turn_off_s'])
        check('recovery: all six native SCRs remain off after reclosure',m['all_SCRs_off_at_end'])
        check('recovery: ready before reclosure',m['Recovery_first_s']<m['Reclose_first_s'])
        check('recovery: reclosure at 1.20 s',abs(m['Reclose_first_s']-1.2)<.0001)
        check('recovery: source1 normal transfer restored within 5%',abs(m['post_source1_rms_kA']/m['prefault_source1_rms_kA']-1)<.05)
    convergence=[]
    for case in ['without_sccl','with_sccl','recovery']:
        key=f'convergence/{case}_5us'
        if key not in summary or case not in summary:continue
        row={'case':case}
        for metric in ['source1_rms_kA','source2_rms_kA','fault_rms_kA','fault_peak_kA','capacitor_peak_kV','valve_branch_peak_kA']:
            if metric not in summary[case]:continue
            err=100*abs(summary[key][metric]/summary[case][metric]-1);row[metric+'_change_percent']=err
            check(case+': 10/5 us '+metric+' change < 2%',err<2,err)
        convergence.append(row)
    write_json(ROOT/'results/metrics.json',summary);write_json(ROOT/'results/convergence.json',convergence)
    write_json(ROOT/'results/validation.json',{'passed':sum(c['pass_'] for c in checks),'total':len(checks),
        'partial_analysis':partial,'selected_run_index_sha256':sha(ROOT/'results/selected_runs.json'),'checks':checks})
    print('VALIDATION',sum(c['pass_'] for c in checks),'/',len(checks),flush=True)
    for c in checks:
        if not c['pass_']:print('FAIL',c,flush=True)
    return summary,checks

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--partial',action='store_true');args=parser.parse_args()
    _,checks=analyze(partial=args.partial)
    raise SystemExit(0 if all(c['pass_'] for c in checks) else 1)
