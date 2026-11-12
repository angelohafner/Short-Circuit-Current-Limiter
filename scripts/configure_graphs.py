"""Apply readable native graph ranges without changing electrical parameters."""
from common import connect

def configure(project):
    c=project.canvas('Main');recovery=project.name=='SCCL_C_Recovery'
    baseline=project.name=='SCCL_A_Without';xmin=.48;xmax=1.5 if recovery else .60
    ranges={'Source 1 currents [kA]':(-115,115) if baseline else (-35,35),
            'Source 2 currents [kA]':(-115,115),'Fault currents [kA]':(-230,230),
            'Sliding RMS including DC offset [kA]':(-5,130),
            'Protection and recovery states':(-.1,1.2),'Phase A current path [kA]':(-35,35),
            'Capacitor voltages [kV]':(-3,3),'MOV energy [kJ]':(0,.08)}
    for item in c.components():
        if type(item).__name__=='GraphFrame':
            item.auto_sizing=False;item.parameters(xmin=xmin,xmax=xmax)
        elif type(item).__name__=='OverlayGraph':
            title=item.parameters()['title'];lo,hi=ranges[title]
            item.parameters(manualscale=True,ymin=lo,ymax=hi)
            item.zoom(xmin,xmax,lo,hi)
    if recovery:
        for note in c.find_all('master:annotation'):
            if note.parameters()['AL1']=='THREE-PHASE SHORT-CIRCUIT CURRENT LIMITER':
                note.parameters(AL2='138 kV | 60 Hz | TPSC capacitor bypass + series reactor | RECOVERY AND RECLOSURE')

if __name__=='__main__':
    from run_simulations import run,NAMES
    app=connect()
    for case,name in NAMES.items():
        p=app.project(name);configure(p);p.save()
        run(case=case,port=63579,L_mH=None if case=='without_sccl' else 15.9,
            C_uF=None if case=='without_sccl' else 442.5,angle=0,step_us=10)
