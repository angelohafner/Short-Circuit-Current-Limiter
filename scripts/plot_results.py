"""Publication figures generated exclusively from selected native EMTDC outputs."""
import json
import math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle,Circle,FancyArrowPatch
from common import ROOT
from analyze_results import load_run

OUT=ROOT/'results/figures';OUT.mkdir(exist_ok=True)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.titlesize':12,'axes.labelsize':10,
                     'axes.spines.top':False,'axes.spines.right':False,'svg.fonttype':'none','savefig.dpi':240})
COLORS=['#c83f49','#2062ad','#22864f'];INK='#17334b';ACCENT='#007f87'
selected=json.loads((ROOT/'results/selected_runs.json').read_text())
metrics=json.loads((ROOT/'results/metrics.json').read_text())
data={k:load_run(ROOT/selected[k]) for k in ['without_sccl','with_sccl','recovery']}

def save(fig,name):
    fig.savefig(OUT/(name+'.png'),bbox_inches='tight',facecolor='white')
    fig.savefig(OUT/(name+'.svg'),bbox_inches='tight',facecolor='white')
    plt.close(fig);print('FIGURE',name,flush=True)
def decorate(ax,ylabel=None):
    ax.grid(alpha=.18);ax.set_axisbelow(True)
    if ylabel:ax.set_ylabel(ylabel)
def phases(ax,t,d,prefix,window,ylim):
    m=(t>=window[0])&(t<=window[1]);stride=max(1,np.sum(m)//12000)
    for ph,color in zip('ABC',COLORS):ax.plot(t[m][::stride],d[prefix+ph][m][::stride],color=color,lw=1,label='Phase '+ph)
    ax.set_xlim(*window);ax.set_ylim(*ylim);decorate(ax,'Current [kA]')

def topology():
    fig,ax=plt.subplots(figsize=(13.5,7));ax.set_xlim(0,15);ax.set_ylim(0,8);ax.axis('off')
    def line(a,b,**kw):ax.plot([a[0],b[0]],[a[1],b[1]],color=INK,lw=2,**kw)
    def box(x,y,w,h,label,fc='#eaf2f6'):
        ax.add_patch(Rectangle((x,y),w,h,fc=fc,ec=INK,lw=1.5));ax.text(x+w/2,y+h/2,label,ha='center',va='center',color=INK)
    for x,label in [(1,'Source 1'),(13.8,'Source 2')]:
        ax.add_patch(Circle((x,6.4),.43,ec=INK,fc='white',lw=2));ax.text(x,6.4,'3~',ha='center',va='center',fontsize=14);ax.text(x,7.15,label,ha='center',weight='bold',color=INK)
    line((1.43,6.4),(2,6.4));box(2,6,2,.8,'Thevenin R-L');line((4,6.4),(5,6.4));line((5,5.8),(5,7))
    ax.text(5,7.15,'Bus 1',ha='center',weight='bold',color=INK)
    line((5,6.4),(5.7,6.4));box(5.7,5.95,2.2,.9,'SCCL',fc='#d6f1ec');line((7.9,6.4),(9,6.4))
    line((9,5.8),(9,7));ax.text(9,7.15,'Bus 2',ha='center',weight='bold',color=INK)
    line((9,6.4),(10.2,6.4));box(10.2,6,2,.8,'Thevenin R-L');line((12.2,6.4),(13.37,6.4))
    line((9,6.4),(9,5.3));box(8.45,4.6,1.1,.7,'Feeder\nbreaker');line((9,4.6),(9,4.1));line((9,4.1),(12.6,4.1))
    box(11.7,3,1.8,.75,'75 MW load\n0.95 lagging');line((12.6,4.1),(12.6,3.75))
    ax.text(9,3.6,'Three-phase\nbolted fault',ha='center',color=COLORS[0],weight='bold');ax.plot(9,4.1,'x',ms=14,color=COLORS[0],mew=3)
    for a,b,txt in [((4.1,6.75),(4.8,6.75),'$I_1$'),((10,6.75),(9.3,6.75),'$I_2$')]:
        ax.add_patch(FancyArrowPatch(a,b,arrowstyle='->',mutation_scale=13,color=ACCENT,lw=2));ax.text((a[0]+b[0])/2,7,txt,ha='center',color=ACCENT)
    ax.text(.6,5.1,'Identical source equivalents in every case\n138 kV line-to-line RMS, 60 Hz\nR = 0.1325 ohm; L = 5.272 mH per phase',color=INK,va='top')
    ax.text(.6,2.75,'SCCL internal circuit (one of three identical phases)',weight='bold',fontsize=12,color=INK)
    line((.7,1.85),(1.1,1.85));box(1.1,1.5,2,.7,'Series reactor\n15.9 mH, 0.10 ohm');line((3.1,1.85),(3.7,1.85));line((3.7,1.85),(4.4,1.85))
    box(4.4,1.5,2,.7,'Series capacitor\n442.5 uF');line((6.4,1.85),(7.1,1.85));line((7.1,1.85),(7.8,1.85))
    line((3.7,1.85),(3.7,.65));line((3.7,.65),(4.1,.65));box(4.1,.3,2.9,.7,'0.1 mH + 0.05 ohm\nAntiparallel SCR valve',fc='#d6f1ec');line((7,.65),(7.1,.65));line((7.1,.65),(7.1,1.85))
    ax.text(8.4,1.8,'Normal: valve blocked; reactor and capacitor compensate.\nFault: valve conducts; current passes through the reactor.\nNative MOV and SCR snubbers protect the capacitor branch.',va='top',color=INK,linespacing=1.6)
    fig.suptitle('TPSC short-circuit current limiter | physical network',fontsize=17,weight='bold',color=INK,y=.99)
    save(fig,'Figure_1_Network_Topology')

def comparison_case(key,num):
    t,d=data[key];m=metrics[key];fig,axes=plt.subplots(3,2,figsize=(13,8.4),sharex='col',gridspec_kw={'width_ratios':[1.35,1]})
    for row,(prefix,label,meas,lim) in enumerate([('I1','Source 1',m['source1_rms_kA'],(-120,120)),('I2','Source 2',m['source2_rms_kA'],(-120,120)),('IF','Fault current',m['fault_rms_kA'],(-225,225))]):
        phases(axes[row,0],t,d,prefix,(.48,.60),lim);phases(axes[row,1],t,d,prefix,(.95,1.0),lim)
        axes[row,0].axvline(.5,color=INK,ls=':',lw=.9)
        axes[row,0].set_title(label,loc='left',weight='bold');axes[row,1].set_title(f'{meas:.2f} kA symmetrical RMS',loc='left',color=ACCENT)
    axes[0,0].legend(ncol=3,loc='upper left',fontsize=8);axes[2,0].set_xlabel('Time [s]');axes[2,1].set_xlabel('Time [s]')
    title='Without SCCL' if key=='without_sccl' else 'With SCCL'
    fig.suptitle(title+' | measured three-phase fault contributions',fontsize=17,color=INK,weight='bold',y=.99)
    fig.text(.5,.015,'Left: fault inception and DC offset. Right: settled fault. Identical axes in Figures 2 and 3.',ha='center',color=INK)
    fig.tight_layout(rect=(0,.04,1,.95));save(fig,f'Figure_{num}_{title.replace(" ","_")}')

def direct():
    fig,ax=plt.subplots(3,1,figsize=(12.5,9),gridspec_kw={'height_ratios':[1.15,1.15,1]})
    for key,label,color in [('without_sccl','Without SCCL','#677789'),('with_sccl','With SCCL',ACCENT)]:
        t,d=data[key];mask=(t>=.49)&(t<=.61)
        ax[0].plot(t[mask],d['IFA'][mask],label=label,color=color,lw=1.2)
        mask=(t>=.95)&(t<=1.0);ax[1].plot(t[mask],d['IFA'][mask],label=label,color=color,lw=1.2)
        mask=(t>=.45)&(t<=1.08);ax[2].plot(t[mask][::5],d['RMSF'][mask][::5],label=label,color=color,lw=1.5)
        ax[2].axhline(metrics[key]['fault_rms_kA'],color=color,lw=1,ls='--')
    for a in ax[:2]:decorate(a,'Phase A fault current [kA]');a.set_ylim(-125,225)
    decorate(ax[2],'Sliding RMS [kA]');ax[0].legend(ncol=2);ax[2].set_xlabel('Time [s]')
    ax[0].set_title('Fault inception | asymmetrical instantaneous current',loc='left');ax[1].set_title('Settled fault | identical time and current scales',loc='left');ax[2].set_title('One-cycle, three-phase averaged RMS includes DC offset; dashed lines show symmetrical RMS',loc='left',fontsize=10)
    fig.suptitle(f'Direct comparison | {metrics["with_sccl"]["total_rms_reduction_percent"]:.2f}% reduction in symmetrical RMS',fontsize=17,color=INK,weight='bold',y=.99)
    fig.tight_layout(rect=(0,0,1,.95));save(fig,'Figure_4_Direct_Comparison')

def internal():
    t,d=data['with_sccl'];fig,ax=plt.subplots(4,3,figsize=(16,10),sharex='col',gridspec_kw={'height_ratios':[1.6,1,1,.65]})
    for col,win in enumerate([(.45,.483333),(.499,.516),(.95,.983333)]):
        mask=(t>=win[0])&(t<=win[1]);tx=t[mask]
        for s,l,color in [('I1A','Reactor current',INK),('ICA','Capacitor current',COLORS[0]),('IVA','Thyristor bypass current',ACCENT)]:ax[0,col].plot(tx,d[s][mask],label=l,color=color,lw=1.3)
        ax[1,col].plot(tx,d['VCA'][mask],color='#a45c12',lw=1.1)
        for s,l,color in [('ITAP','Positive SCR',ACCENT),('ITAN','Negative SCR',COLORS[1])]:ax[2,col].plot(tx,d[s][mask],label=l,color=color,lw=1.1)
        ax[3,col].step(tx,d['Gate'][mask],where='post',color=INK);ax[3,col].set_ylim(-.1,1.2);ax[3,col].set_yticks([0,1])
        for a,y in zip(ax[:,col],['Branch current [kA]','Capacitor voltage [kV]','SCR current [kA]','Firing command']):decorate(a,y);a.set_xlim(*win)
        ax[3,col].set_xlabel('Time [s]')
    ax[0,0].legend(fontsize=8,loc='upper left');ax[2,0].legend(ncol=2,fontsize=8)
    ax[2,0].set_ylim(-.001,.001)
    ax[2,0].text(.5,.70,'Blocked SCRs: leakage below 2 microampere',ha='center',transform=ax[2,0].transAxes,fontsize=8,color=INK)
    ax[0,0].set_title('Normal: reactor current flows through the capacitor',loc='left',fontsize=10)
    ax[0,1].set_title('Activation: capacitor discharge and current transfer',loc='left',fontsize=10)
    ax[0,2].set_title('Limited fault: reactor current flows through the valve',loc='left',fontsize=10)
    fig.suptitle('Inside the SCCL | capacitor, thyristor and reactor currents',fontsize=17,color=INK,weight='bold',y=.99)
    fig.tight_layout(rect=(0,0,1,.95));save(fig,'Figure_5_Internal_Current_Path')

def recovery():
    t,d=data['recovery'];m=metrics['recovery'];fig,ax=plt.subplots(5,1,figsize=(13,11),sharex=True,gridspec_kw={'height_ratios':[1.15,1.15,1,.85,.8]})
    mask=(t>=.45)&(t<=1.5);tx=t[mask][::4]
    for ph,color in zip('ABC',COLORS):
        ax[0].plot(tx,d['IF'+ph][mask][::4],color=color,lw=.8,label='Phase '+ph)
        ax[1].plot(tx,d['IV'+ph][mask][::4],color=color,lw=.8)
        ax[2].plot(tx,d['VC'+ph][mask][::4],color=color,lw=.8)
    conducting=np.maximum.reduce([(d['TON'+ph+pol]>d['TOFF'+ph+pol]).astype(float) for ph in 'ABC' for pol in 'PN'])
    for values,label,color in [(d['Gate'],'Gate command',INK),(conducting,'Native SCR conduction state',COLORS[0]),(d['Recovery'],'Recovery complete',ACCENT)]:ax[3].step(tx,values[mask][::4],label=label,color=color,where='post',lw=1.2)
    ax[4].step(tx,1-d['FeederOpen'][mask][::4],where='post',label='Feeder close command',color=INK,lw=1.4)
    ax[4].step(tx,1-d['FaultOpen'][mask][::4],where='post',label='Fault applied',color=COLORS[0],lw=1.1)
    for a,label in zip(ax,['Fault current [kA]','Bypass current [kA]','Capacitor voltage [kV]','Valve / recovery','Feeder / fault']):decorate(a,label)
    for tm,label in [(.5,'Fault'),(.583333,'Trip'),(m['gate_removal_s'],'Gate removed'),(m['Recovery_first_s'],'Recovered'),(1.2,'Reclose')]:
        for a in ax:a.axvline(tm,color='#6e7884',ls=':',lw=.7)
        ax[0].text(tm,1.04,label,rotation=45,transform=ax[0].get_xaxis_transform(),ha='left',fontsize=9)
    ax[0].legend(ncol=3,loc='lower right',fontsize=8);ax[3].legend(ncol=3,loc='upper right',fontsize=8);ax[4].legend(ncol=2,loc='upper right',fontsize=8)
    ax[-1].set_xlabel('Time [s]');ax[-1].set_xlim(.45,1.5)
    fig.suptitle('Fault clearing, natural thyristor turn-off and healthy-feeder reclosure',fontsize=16,color=INK,weight='bold',y=.995)
    fig.tight_layout(rect=(0,0,1,.94));save(fig,'Figure_6_Fault_Clearing_Recovery')

def recovery_detail():
    t,d=data['recovery'];m=metrics['recovery'];fig,ax=plt.subplots(3,1,figsize=(12,8.5))
    mask=(t>=.62)&(t<=.85)
    for ph,color in zip('ABC',COLORS):
        # Display absolute measured branch current in amperes on a declared logarithmic scale.
        ax[0].semilogy(t[mask],np.maximum(np.abs(d['IV'+ph][mask])*1000,1e-5),color=color,lw=1,label='Phase '+ph)
    ax[0].axvline(m['gate_removal_s'],color=INK,ls='--',label='Gate removed')
    ax[0].axvline(m['last_SCR_turn_off_s'],color=ACCENT,ls=':',label='Last native SCR turn-off')
    ax[0].set_ylim(1e-4,3000);decorate(ax[0],'Absolute bypass current [A]');ax[0].legend(ncol=5,fontsize=8);ax[0].set_title('Valve current persists after gate removal and ceases by natural commutation',loc='left')
    mask=(t>=1.18)&(t<=1.5)
    for s,label,color in [('RMS1','Source 1',INK),('RMS2','Source 2',ACCENT)]:ax[1].plot(t[mask],d[s][mask],color=color,label=label)
    ax[1].axhline(m['prefault_source1_rms_kA'],color='#63778b',ls=':',label='Source 1 pre-fault level');decorate(ax[1],'Sliding current RMS [kA]');ax[1].legend(ncol=3,fontsize=9);ax[1].set_title('Normal power transfer resumes after healthy-feeder reclosure',loc='left')
    mask=(t>=1.45)&(t<=1.5)
    for s,label,color in [('I1A','Reactor current',INK),('ICA','Capacitor current',COLORS[0]),('IVA','Valve bypass current',ACCENT)]:ax[2].plot(t[mask],d[s][mask],color=color,label=label,lw=1.2)
    decorate(ax[2],'Phase A current [kA]');ax[2].legend(ncol=3,fontsize=9);ax[2].set_title('The compensated current path is restored',loc='left')
    for a in ax:a.set_xlabel('Time [s]')
    fig.suptitle('Recovery detail | physical SCR turn-off and restored transfer',fontsize=17,color=INK,weight='bold',y=.99);fig.tight_layout(rect=(0,0,1,.95));save(fig,'Figure_9_Recovery_Detail')

def performance():
    a=metrics['without_sccl'];b=metrics['with_sccl'];rows=[]
    for title,key,unit in [('Source 1 symmetrical RMS','source1_rms_kA','kA'),('Source 2 symmetrical RMS','source2_rms_kA','kA'),('Fault symmetrical RMS','fault_rms_kA','kA'),('Maximum asymmetrical fault peak','fault_peak_kA','kA'),('Total RMS reduction','total_rms_reduction_percent','%'),('Fault detection delay','detection_delay_ms','ms'),('First effective valve response','bypass_response_ms','ms'),('Maximum capacitor voltage','capacitor_peak_kV','kV'),('Maximum reactor / interconnection current','reactor_peak_kA','kA'),('Maximum per-phase MOV energy','MOV_energy_max_kJ','kJ')]:
        fmt=lambda m:f'{m[key]:.3f}' if m.get(key) is not None else 'Not applicable'
        rows.append([title,unit,fmt(a),fmt(b)])
    fig,ax=plt.subplots(figsize=(12,6.5));ax.axis('off');table=ax.table(cellText=rows,colLabels=['Measured quantity','Unit','Without SCCL','With SCCL'],loc='center',cellLoc='left',colWidths=[.51,.08,.205,.205]);table.auto_set_font_size(False);table.set_fontsize(10);table.scale(1,2.1)
    for (r,c),cell in table.get_celld().items():
        cell.set_edgecolor('#d5e0e8')
        if r==0:cell.set_facecolor(INK);cell.get_text().set_color('white');cell.get_text().set_weight('bold')
        else:cell.set_facecolor('#eef5f7' if r%2 else 'white')
    fig.suptitle('Quantitative performance | native PSCAD results',fontsize=17,color=INK,weight='bold',y=.98)
    fig.text(.5,.04,'Symmetrical RMS: 0.95–1.05 s least-squares fundamental phasor. Peaks: 0.50–1.10 s.\nInstantaneous peaks include DC offset and must not be interpreted as RMS.',ha='center',fontsize=10,color=INK)
    save(fig,'Figure_7_Performance_Summary')

def sensitivity():
    fig,ax=plt.subplots(2,2,figsize=(12,8));default=metrics['with_sccl']
    for angle,color in zip([0,45,90],COLORS):
        rows=[v for k,v in metrics.items() if k.startswith('sensitivity/') and v['source_phase_deg']==angle]
        if angle==0:rows+=[default]
        rows=sorted(rows,key=lambda m:m['L_mH'])
        x=[m['L_mH'] for m in rows]
        for a,key,label in [(ax[0,0],'source1_rms_kA','Source 1 symmetrical RMS [kA]'),(ax[0,1],'fault_rms_kA','Fault symmetrical RMS [kA]'),(ax[1,0],'fault_peak_kA','Maximum asymmetrical peak [kA]'),(ax[1,1],'capacitor_peak_kV','Maximum capacitor voltage [kV]')]:
            a.plot(x,[m[key] for m in rows],'-o',color=color,label=f'{angle} deg',lw=1.5,ms=4);decorate(a,label);a.set_xlabel('Reactor inductance [mH]')
    ax[0,0].legend(title='Source phase setting',ncol=3,fontsize=8)
    fig.suptitle('Sensitivity | reactor size and fault inception angle',fontsize=17,color=INK,weight='bold',y=.99);fig.tight_layout(rect=(0,0,1,.95));save(fig,'Figure_8_Parameter_Sensitivity')

if __name__=='__main__':
    topology();comparison_case('without_sccl',2);comparison_case('with_sccl',3);direct();internal();recovery();performance();sensitivity();recovery_detail()
