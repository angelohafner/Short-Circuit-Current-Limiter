"""Build native, editable PSCAD networks with the official Automation Library."""
from pathlib import Path
from datetime import datetime
import argparse
import math
import shutil
import faulthandler
from mhi.pscad.wizard import UserDefnWizard
from common import ROOT, PARAM, connect, write_json, sha

def protection_definition(project):
    w=UserDefnWizard('SCCL_Protection')
    w.description='Measured-current protective bypass and interlocked recovery; no electrical injection'
    inputs=['I1A','I1B','I1C','I2A','I2B','I2C','IFA','IFB','IFC',
            'VCA','VCB','VCC','IVA','IVB','IVC','EA','EB','EC','BA','BB','BC',
            'PickupI','PickupV','EnergyLimit','GateDelay','RecoverI','Hold',
            'FaultTime','RemoveTime','OpenTime','CloseTime','Enabled']
    outputs=['FaultOpen','FeederOpen','Gate','Detect','Pickup','Recovery','Reclose',
             'EnergyTrip','RMS1','RMS2','RMSF','Imax','Vmax','ValveOn']
    ints=set(outputs[:8])
    for i,n in enumerate(inputs):w.port.input(-8,2*i,n,'REAL')
    for i,n in enumerate(outputs):w.port.output(8,2*i,n,'INTEGER' if n in ints else 'REAL')
    w.graphics.rectangle(-7,-2,7,2*len(inputs))
    w.graphics.text('SCCL PROTECTION',0,-3,full_font='Tahoma, 10world')
    w.script['Dsout']='''#STORAGE REAL:24012 INTEGER:3
#LOCAL INTEGER K
#LOCAL INTEGER J
#LOCAL INTEGER Q
#LOCAL INTEGER N
#LOCAL INTEGER IDX
#LOCAL REAL X 3
      K=NSTORF
      Q=NSTORI
      NSTORF=NSTORF+24012
      NSTORI=NSTORI+3
      IF (TIMEZERO) THEN
        STORF(K:K+24011)=0.0
        STORI(Q:Q+2)=0
        STORF(K+3)=-1.0
      ENDIF
      N=NINT(1.0/(60.0*DELT))
      IF (N.GT.8000) STOP 'RMS buffer limit exceeded'
      IDX=STORI(Q+2)
      X(1)=($I1A**2+$I1B**2+$I1C**2)/3.0
      X(2)=($I2A**2+$I2B**2+$I2C**2)/3.0
      X(3)=($IFA**2+$IFB**2+$IFC**2)/3.0
      DO J=1,3
        STORF(K+6+J)=STORF(K+6+J)+X(J)
     +    -STORF(K+12+3*IDX+J-1)
        STORF(K+12+3*IDX+J-1)=X(J)
      ENDDO
      STORI(Q+2)=MOD(IDX+1,N)
      $RMS1=SQRT(MAX(0.0,STORF(K+7)/REAL(N)))
      $RMS2=SQRT(MAX(0.0,STORF(K+8)/REAL(N)))
      $RMSF=SQRT(MAX(0.0,STORF(K+9)/REAL(N)))
      $Imax=MAX(ABS($I1A),ABS($I1B),ABS($I1C))
      $Vmax=MAX(ABS($VCA),ABS($VCB),ABS($VCC))
      $ValveOn=0.0
      IF (MAX(ABS($IVA),ABS($IVB),ABS($IVC)).GT.0.001)
     +  $ValveOn=1.0
      $EnergyTrip=0
      IF (MAX($EA,$EB,$EC).GT.$EnergyLimit) STORI(Q+1)=1
      $EnergyTrip=STORI(Q+1)
      $FaultOpen=1
      IF (TIME.GE.$FaultTime.AND.TIME.LT.$RemoveTime)
     +  $FaultOpen=0
      $Pickup=0
      IF (TIME.GT.0.15.AND.$Enabled.GT.0.5) THEN
        IF ($Imax.GT.$PickupI.OR.$Vmax.GT.$PickupV)
     +    $Pickup=1
      ENDIF
      IF ($Pickup.EQ.1.AND.STORI(Q).EQ.0) THEN
        STORI(Q)=1
        STORF(K+3)=TIME
      ENDIF
      IF ($BA.GT.1.5.AND.$BB.GT.1.5.AND.$BC.GT.1.5
     + .AND.$Imax.LT.$RecoverI.AND.$Vmax.LT.$PickupV
     + .AND.$EnergyTrip.EQ.0) THEN
        STORF(K+4)=STORF(K+4)+DELT
      ELSE
        STORF(K+4)=0.0
      ENDIF
      IF (STORF(K+4).GE.$Hold) STORI(Q)=0
      $Detect=STORI(Q)
      $Gate=0
      IF (STORI(Q).EQ.1.AND.TIME.GE.STORF(K+3)+$GateDelay)
     + $Gate=1
      $Recovery=0
      IF ($Gate.EQ.0.AND.$ValveOn.LT.0.5.AND.
     + $Vmax.LT.$PickupV.AND.TIME.GT.$OpenTime) THEN
        STORF(K+5)=STORF(K+5)+DELT
      ELSE
        STORF(K+5)=0.0
      ENDIF
      IF (STORF(K+5).GT.$Hold) $Recovery=1
      IF ($Enabled.LT.0.5) $Recovery=1
      $FeederOpen=0
      IF (TIME.GE.$OpenTime) $FeederOpen=1
      $Reclose=0
      IF (TIME.GE.$CloseTime.AND.$Recovery.EQ.1.AND.
     + $EnergyTrip.EQ.0.AND.$FaultOpen.EQ.1) THEN
        $FeederOpen=0
        $Reclose=1
      ENDIF
      IF ($EnergyTrip.EQ.1) $FeederOpen=1
'''
    w.script['Dsout']=w.script['Dsout'].replace('60.0*DELT',f"{PARAM['frequency_Hz']:.12g}*DELT")
    (ROOT/'scripts/protection_fortran.txt').write_text(w.script['Dsout'],encoding='utf8')
    return w.create_definition(project),inputs,outputs

def build(case='with_sccl',port=63579):
    faulthandler.dump_traceback_later(180,repeat=True)
    names={'without_sccl':'SCCL_A_Without','with_sccl':'SCCL_B_With','recovery':'SCCL_C_Recovery'}
    name=names[case]; enabled=case!='without_sccl'; cfg=PARAM
    for folder in ['pscad','results','diagnostics','references']:(ROOT/folder).mkdir(exist_ok=True)
    for f in ROOT.parent.glob('*.png'):shutil.copy2(f,ROOT/'references'/f.name)
    path=ROOT/'pscad'/(name+'.pscx');app=connect(port)
    if path.exists():
        backup=ROOT/'diagnostics'/('previous_'+datetime.now().strftime('%Y%m%d_%H%M%S'))
        backup.mkdir(exist_ok=True);shutil.copy2(path,backup/path.name)
    if any(x['name']==name for x in app.projects()):
        p=app.project(name);assert Path(p.filename).resolve()==path.resolve();p.unload()
    p=app.create_case(name,folder=str(path.parent))
    p.parameters(time_duration=cfg['duration_s'],time_step=cfg['step_us'],sample_step=cfg['sample_us'],
                 StartType='STANDARD',PlotType='OUT',SnapType='NONE',output_filename=name+'.out',
                 send_output_ch=True,branch_threshold=1e-7,threads=1,description='138 kV 60 Hz TPSC current limiter; '+case)
    c=p.canvas('Main');c.parameters(size='100X100')
    def cmp(n,x,y,**kw):return c.create_component('master:'+n,x,y,**kw)
    def xy(o,n):q=o.ports()[n];return q.x,q.y
    def wire(*pts):
        pts=list(dict.fromkeys(pts))
        if len(pts)>1:return c.create_wire(*pts)
    def note(x,y,a,b=''):return c.create_annotation(x,y,a,b)
    def sig(o,n,label,dx=0):
        x,y=xy(o,n);wire((x,y),(x+dx,y));return cmp('datalabel',x+dx,y,Name=label)
    def h(n,x,y,**kw):
        o=cmp(n,x,y,**kw)
        return o,xy(o,'A'),xy(o,'B')
    def am(x,y,label):
        o=cmp('ammeter',x,y,Name=label)
        return xy(o,'N1'),xy(o,'N2')
    def vm(x,y,label,a,b):
        o=cmp('voltmeter',x,y,Name=label)
        # Route voltage sensing wires outside the series branch.
        wire(a,(a[0],y),xy(o,'N1'))
        wire(b,(b[0],y+2),xy(o,'N2'))
    def vert(n,x,y,**kw):
        o=cmp(n,x,y,**kw);o.rotate_right()
        ports=sorted([(q.x,q.y) for q in o.ports().values()],key=lambda z:z[1])
        return o,ports[0],ports[-1]
    channels=[]
    def add(label,unit):channels.append((label,unit))
    note(130,4,'THREE-PHASE SHORT-CIRCUIT CURRENT LIMITER',
         '138 kV | 60 Hz | TPSC capacitor bypass + series reactor | '+case.replace('_',' ').upper())
    note(128,10,'Source impedances are identical in every case. Electrical currents are measured, never imposed.',
         'Three identical phase circuits below. Positive source currents point toward Bus 2.')
    sources=[]
    for num,x in [(1,10),(2,245)]:
        src=cmp('source3',x,110,Name=f'Source_{num}',Type=1,Ctrl=0,View=0,Term=0,
                R1s=f"{cfg['source_R_ohm']} [ohm]",Vm=f"{cfg['source_LL_kV']} [kV]",Es=f"{cfg['source_LL_kV']} [kV]",
                F=f"{cfg['frequency_Hz']} [Hz]",F0=f"{cfg['frequency_Hz']} [Hz]",Ph='0 [deg]',Tc=f"{cfg['source_ramp_s']} [s]",TcTyp=1)
        if num==2:src.mirror()
        nx,ny=xy(src,'N');wire((nx,ny),(nx,ny+8));cmp('ground',nx,ny+8)
        sources.append(src)
    topology=[]
    for k,ph in enumerate('ABC'):
        y=40+70*k
        note(115,y-23,'PHASE '+ph, 'Capacitor-only bypass; reactor always remains in the power path')
        s1=xy(sources[0],ph);s2=xy(sources[1],ph)
        wire(s1,(22+2*k,s1[1]),(22+2*k,y),(36,y))
        wire(s2,(235-2*k,s2[1]),(235-2*k,y),(226,y))
        cmp('voltmetergnd',32,y,Name='VS1'+ph);cmp('voltmetergnd',230,y,Name='VS2'+ph)
        ls,a,b=h('inductor',44,y,Name='Source1_L_'+ph,L=f"{cfg['source_L_H']} [H]")
        wire((36,y),a)
        ma,mb=am(52,y,'I1'+ph);wire(b,ma);wire(mb,(60,y))
        ls,a,b=h('inductor',218,y,Name='Source2_L_'+ph,L=f"{cfg['source_L_H']} [H]")
        wire((226,y),b)
        meter=cmp('ammeter',208,y,Name='I2'+ph);meter.mirror()
        wire(a,xy(meter,'N1'));wire(xy(meter,'N2'),(194,y))
        cmp('voltmetergnd',60,y,Name='VB1'+ph);cmp('voltmetergnd',194,y,Name='VB2'+ph)
        note(59,y-3,'Bus 1');note(194,y-3,'Bus 2')
        if enabled:
            r,a,b=h('resistor',70,y,Name='Reactor_R_'+ph,R=f"{cfg['reactor_R_ohm']} [ohm]");wire((60,y),a)
            l,aa,bb=h('inductor',82,y,Name='Reactor_L_'+ph,L=f"{cfg['reactor_L_H']} [H]");wire(b,aa);wire(bb,(96,y))
            vm(76,y-7,'VL'+ph,(66,y),(90,y))
            a,b=am(102,y,'IC'+ph);wire((96,y),a)
            r,aa,bb=h('resistor',112,y,Name='Capacitor_ESR_'+ph,R=f"{cfg['capacitor_ESR_ohm']} [ohm]");wire(b,aa)
            cap,aa,bb=h('capacitor',130,y,Name='Capacitor_C_'+ph,C=f"{cfg['capacitor_C_uF']} [uF]");wire(xy(r,'B'),aa);wire(bb,(164,y))
            vm(131,y-8,'VC'+ph,xy(cap,'A'),xy(cap,'B'))
            # Shared discharge limiting R-L branch, then two antiparallel native SCR stacks.
            a,b=am(102,y+10,'IV'+ph);wire((96,y),(96,y+10),a)
            r,aa,bb=h('resistor',112,y+10,Name='Bypass_R_'+ph,R=f"{cfg['bypass_R_ohm']} [ohm]");wire(b,aa)
            l,aa,b=h('inductor',122,y+10,Name='Bypass_L_'+ph,L=f"{cfg['bypass_L_H']} [H]");wire(bb,aa)
            wire(b,(132,y+10),(132,y+6));wire((132,y+10),(132,y+14))
            for pol,yy in [('P',y+6),('N',y+14)]:
                sw=cmp('peswitch',144,yy,Name='SCR_'+ph+pol,L=ph+pol,Type=1,SNUB=1,INTR=0,
                       RON=f"{cfg['SCR_Ron_ohm']} [ohm]",ROFF=f"{cfg['SCR_Roff_ohm']} [ohm]",
                       EFVD=f"{cfg['SCR_forward_drop_kV']} [kV]",EBO=f"{cfg['SCR_withstand_kV']} [kV]",Erw=f"{cfg['SCR_withstand_kV']} [kV]",
                       TEXT=f"{cfg['SCR_extinction_us']} [us]",PFB=1,
                       RD=f"{cfg['SCR_snubber_R_ohm']} [ohm]",CD=f"{cfg['SCR_snubber_C_uF']} [uF]",
                       I='IT'+ph+pol,It='ITT'+ph+pol,V='VT'+ph+pol,Ton='TON'+ph+pol,Toff='TOFF'+ph+pol)
                sw.rotate_right()
                # Native switch positive branch current is DP -> DN.
                if (xy(sw,'DP')[0]<xy(sw,'DN')[0]) != (pol=='P'):sw.mirror()
                ends=sorted([xy(sw,'DP'),xy(sw,'DN')]);wire((132,yy),ends[0]);wire(ends[1],(158,yy),(158,y+10))
                sig(sw,'APUL','Gate',3)
                for s,u in [('IT','kA'),('ITT','kA'),('VT','kV'),('TON','s'),('TOFF','s')]:add(s+ph+pol,u)
            wire((158,y+10),(164,y+10),(164,y))
            # MOV spans the protected capacitor assembly; its tiny ESR is included.
            mov=cmp('arrester',132,y+23,Name='MOV_'+ph,VSCAL=f"{cfg['MOV_rating_kV']} [kV]",ISCAL=cfg['MOV_parallel_stacks'],Cnfg=0,ENAB=1,Curr='IM'+ph,Energy='EM'+ph)
            mov.rotate_right();ends=sorted([xy(mov,'NF'),xy(mov,'NT')]);wire((96,y),(96,y+23),ends[0]);wire(ends[1],(164,y+23),(164,y))
            wire((164,y),(194,y))
            vm(174,y-15,'VDROP'+ph,(60,y),(194,y))
            for prefix,unit in [('VL','kV'),('VC','kV'),('IC','kA'),('IV','kA'),('IM','kA'),('EM','kJ'),('VDROP','kV')]:add(prefix+ph,unit)
        else:
            r,a,b=h('resistor',90,y,Name='Busbar_R_'+ph,R=f"{cfg['interconnection_R_ohm']} [ohm]");wire((60,y),a)
            l,a,bb=h('inductor',130,y,Name='Busbar_L_'+ph,L=f"{cfg['interconnection_L_H']} [H]");wire(b,a);wire(bb,(194,y))
        # Feeder and fault are downstream of the combining bus. Load is on the feeder.
        br,aa,bb=vert('breaker1',194,y+13,NAME='FeederOpen',RON=f"{cfg['feeder_Ron_ohm']} [ohm]",ROFF='1e10 [ohm]',OPCUR=0,CLVL='0 [kA]',SBR='BR'+ph,IBR='IBR'+ph,VBR='VBR'+ph)
        wire((194,y),aa);wire(bb,(194,y+26),(216,y+26))
        fault,aa,bb=vert('breaker1',194,y+34,NAME='FaultOpen',RON=f"{cfg['fault_R_ohm']} [ohm]",ROFF='1e10 [ohm]',OPCUR=0,CLVL='0 [kA]',SBR='FS'+ph)
        wire((194,y+26),aa)
        met=cmp('ammeter',194,y+41,Name='IF'+ph);met.rotate_right()
        if xy(met,'N1')[1]>xy(met,'N2')[1]:met.mirror()
        wire(bb,xy(met,'N1'));wire(xy(met,'N2'),(194,y+47));cmp('ground',194,y+47)
        # Constant impedance grounded-wye load: 75 MW, 0.95 lagging at 138 kV.
        q=cfg['load_MW']*math.tan(math.acos(cfg['load_pf']))
        z=cfg['source_LL_kV']**2/complex(cfg['load_MW'],-q)
        met=cmp('ammeter',216,y+30,Name='ILOAD'+ph);met.rotate_right()
        if xy(met,'N1')[1]>xy(met,'N2')[1]:met.mirror()
        wire((216,y+26),xy(met,'N1'))
        rr,aa,bb=vert('resistor',216,y+36,Name='Load_R_'+ph,R=f'{z.real:.12g} [ohm]');wire(xy(met,'N2'),aa)
        ll,aa,b=vert('inductor',216,y+43,Name='Load_L_'+ph,L=f"{z.imag/(2*math.pi*cfg['frequency_Hz']):.12g} [H]");wire(bb,aa);wire(b,(216,y+47));cmp('ground',216,y+47)
        for prefix,unit in [('I1','kA'),('I2','kA'),('IF','kA'),('ILOAD','kA'),('IBR','kA'),('VBR','kV'),('VS1','kV'),('VS2','kV'),('VB1','kV'),('VB2','kV'),('BR','state'),('FS','state')]:add(prefix+ph,unit)
        print('BUILT PHASE',ph,flush=True)
        p.save()
    note(127,238,'SOURCE EQUIVALENT: R = 0.1325 ohm; L = 5.272 mH per phase; X/R = 15',
         'Load: 75 MW, 0.95 lagging. Feeder breaker poles interrupt at their physical current zeros.')
    note(127,245,'SCCL DEFAULTS: L = 15.9 mH; C = 442.5 uF; reactor R = 0.10 ohm',
         'Edit L and C independently in the circuit. Matched compensation is a study option, not a constraint.')
    definition,inputs,outputs=protection_definition(p)
    ctl=c.create_component(definition,50,266)
    controls={'PickupI':cfg['pickup_current_kA'],'PickupV':cfg['pickup_capacitor_kV'],
              'EnergyLimit':cfg['MOV_energy_interlock_kJ'],'GateDelay':cfg['gate_delay_s'],
              'RecoverI':cfg['recovery_current_kA'],'Hold':cfg['recovery_hold_s'],
              'FaultTime':cfg['fault_time_s'],
              'RemoveTime':cfg['recovery_fault_remove_s'] if case=='recovery' else cfg['comparison_fault_remove_s'],
              'OpenTime':cfg['recovery_open_s'] if case=='recovery' else cfg['comparison_open_s'],
              'CloseTime':cfg['reclosure_s'] if case=='recovery' else 2.0,'Enabled':int(enabled)}
    for i,(key,val) in enumerate(controls.items()):
        const=cmp('const',10,267+5*i,Name=key,Value=val);sig(const,'OUT','Set_'+key,2)
    zero=cmp('const',10,333,Name='Zero',Value=0);sig(zero,'OUT','Zero',2)
    for namein in inputs:
        label='Set_'+namein if namein in controls else namein
        if namein in ['BA','BB','BC']:label='BR'+namein[-1]
        if namein in ['EA','EB','EC']:label='EM'+namein[-1]
        if not enabled and namein[:2] in ['VC','IV']:label='Zero'
        if not enabled and namein in ['EA','EB','EC']:label='Zero'
        sig(ctl,namein,label,-5)
    for n in outputs:
        sig(ctl,n,n,5);add(n,'kA' if n in ['RMS1','RMS2','RMSF','Imax'] else 'kV' if n=='Vmax' else 'state')
    note(50,260,'PROTECTION AND RECOVERY', 'Measured pickup -> latch -> gate delay -> natural commutation -> reclosure interlock')
    # Named native output channels, no waveform scaling.
    pgb={}
    for i,(label,unit) in enumerate(channels):
        x,y=270+(i//26)*28,16+6*(i%26)
        cmp('datalabel',x,y,Name=label);wire((x,y),(x+5,y))
        pgb[label]=cmp('pgb',x+5,y,Name=label,UseSignalName=0,Units=unit,Group='SCCL',Scale=1,Min=-150,Max=150)
    plots=[('Source 1 currents [kA]',[f'I1{p}' for p in 'ABC']),('Source 2 currents [kA]',[f'I2{p}' for p in 'ABC']),
           ('Fault currents [kA]',[f'IF{p}' for p in 'ABC']),('Sliding RMS including DC offset [kA]',['RMS1','RMS2','RMSF']),
           ('Protection and recovery states',['Detect','Gate','ValveOn','Recovery','Reclose','FeederOpen'])]
    if enabled:plots.extend([('Phase A current path [kA]',['I1A','ICA','IVA','IMA']),('Capacitor voltages [kV]',['VCA','VCB','VCC']),('MOV energy [kJ]',['EMA','EMB','EMC'])])
    for i,(title,signals) in enumerate(plots):
        frame=c.create_graph_frame(100+(i//4)*80,265+(i%4)*28);frame.size=(76,25)
        frame.parameters(title=title,xtitle='Time [s]',xmin=.48,xmax=.65 if case=='recovery' else .65)
        graph,_=frame.add_overlay_graph(*(pgb[s] for s in signals));graph.parameters(title=title,manualscale=False)
        frame.auto_sizing=True
    from configure_graphs import configure
    configure(p)
    p.save();write_json(ROOT/'diagnostics'/(case+'_build.json'),{'project':str(path),'sha256':sha(path),'licensed':app.licensed(),'version':app.version,'parameters':cfg,'control':controls,'channels':channels})
    print('BUILD',name,flush=True);p.build()
    msgs=p.messages();(ROOT/'diagnostics'/(case+'_build_messages.txt')).write_text('\n'.join(str(m) for m in msgs),encoding='utf8')
    errors=[str(m) for m in msgs if m.status=='error'];warnings=[str(m) for m in msgs if m.status=='warning']
    print('ERRORS',errors,'WARNINGS',warnings,flush=True)
    assert not errors
    p.focus();faulthandler.cancel_dump_traceback_later()
    return p

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--case',choices=['without_sccl','with_sccl','recovery'],default='with_sccl');ap.add_argument('--port',type=int,default=63579)
    a=ap.parse_args();build(a.case,a.port)
