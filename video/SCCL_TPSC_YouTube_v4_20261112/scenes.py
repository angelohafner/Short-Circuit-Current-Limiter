"""Four educational scenes, driven only by recorded EMTDC measurements."""
from manim import *
import numpy as np
from data_access import Measurements,first_state_time
from visuals import *


def recovery_caption(data,time):
    """Describe the recorded state, including command/physical-switch distinction."""
    if time < .50001:
        return 'Steady operation'
    if data.value('C','Reclose',time)>.5:
        if not all(data.value('C','BR'+p,time)<.5 for p in 'ABC'):
            return 'Reclosure commanded'
        return 'Normal operation restored' if time>=2.5 else 'Reclosed: compensation settling'
    if all(data.value('C','BR'+p,time)>1.5 for p in 'ABC'):
        if data.conducting('C',time):
            return 'Gates off; natural current decay' if data.value('C','Gate',time)<.5 else 'Feeder open; SCRs still conducting'
        return 'Ready for reclosure' if data.value('C','Recovery',time)>.5 else 'SCRs off; waiting for recovery'
    return 'Fault current and feeder clearing'

class StudyScene(Scene):
    def setup(self):
        self.d=Measurements()
    def finish(self,seconds):
        remaining=seconds-self.time
        if remaining>0: self.wait(remaining)
        assert abs(self.time-seconds)<.08,(self.__class__.__name__,self.time)

class NormalOperation(StudyScene):
    def construct(self):
        title(self,'01','Current limiter: normal operation')
        footer(self,'Phase detail; MOV and SCR snubbers omitted here for clarity')
        tr=ValueTracker(.45); c=PhaseCircuit()
        c.update_native(self.d,'B',tr.get_value())
        c.add_updater(lambda m:m.update_native(self.d,'B',tr.get_value()))
        self.add(c,clock(tr))
        eq=math(r'X_L=2\pi fL\approx\frac{1}{2\pi fC}=X_C',36).move_to(pos(0,-.7))
        self.play(Write(eq),run_time=2)
        ratings=VGroup(math(r'L=15.9\ \mathrm{mH}',29,BLUE),math(r'C=442.5\ \mathrm{\mu F}',29,RED)).arrange(RIGHT,buff=1.2).move_to(pos(0,-1.65))
        self.play(FadeIn(ratings),run_time=1)
        self.add(state_chip('SCRs blocked',False,(-4.2,-2.65),width=2.9),
                 math(r'I_1\approx0.164\ \mathrm{kA}_{\mathrm{rms}}',27,BLUE).move_to(pos(.3,-2.65)),
                 math(r'X_L\approx X_C\approx 5.99\ \Omega',26).move_to(pos(0,-3.25)))
        self.play(tr.animate.set_value(.483333),run_time=12,rate_func=linear)
        self.finish(18)

class FaultTransfer(StudyScene):
    def construct(self):
        title(self,'02','The current changes its path')
        self.add(txt('Protective bypass  |  slowed electrical time',18,MUTED).move_to(pos(-1.7,2.99)))
        tr=ValueTracker(.499); c=PhaseCircuit()
        c.update_native(self.d,'B',tr.get_value())
        fault_time=first_state_time(self.d.array('B','time'),self.d.array('B','FSA'),0,after=.49)
        detect_ms=1000*(self.d.meta['events']['B']['detect_s']-fault_time)
        scr_ms=1000*(self.d.meta['events']['B']['first_conduction_s']-fault_time)
        c.add_updater(lambda m:m.update_native(self.d,'B',tr.get_value()))
        self.add(c,clock(tr))
        window=(.499,.516)
        for i,(name,color,label,yr) in enumerate([
            ('I1A',BLUE,r'i_L\ /\ \mathrm{kA}',[-30,30,30]),
            ('ICA',RED,r'i_C\ /\ \mathrm{kA}',[-4,4,4]),
            ('IVA',ORANGE,r'i_v\ /\ \mathrm{kA}',[-30,30,30]),
            ('VCA',GREEN,r'v_C\ /\ \mathrm{kV}',[-2.5,2.5,2.5])]):
            plot=NativePlot(self.d,'B',[name],[color],window,yr,(.75,-.65-.73*i),height=.46,label=label,ticks=i==3)
            self.add(plot,plot.cursor(tr))
        self.add(indicator('Fault applied',lambda:self.d.value('B','FSA',tr.get_value())<.5,(-4.7,-.04),RED),
                 indicator('Gate enabled',lambda:self.d.value('B','Gate',tr.get_value())>.5,(-2.3,-.04)),
                 indicator('SCR conducting',lambda:self.d.conducting('B',tr.get_value(),'A'),(.1,-.04)))
        footer(self,'Shared simulation time / s  |  Different current scales are labeled  |  Native data')
        caption=txt('Compensated path',17,MUTED).move_to(pos(4.9,-.12))
        self.add(caption)
        self.wait(2)
        self.play(tr.animate.set_value(.5),run_time=3,rate_func=linear)
        self.play(tr.animate.set_value(.50038),run_time=3,rate_func=linear)
        updated=math(r'\Delta t_{\mathrm{detect}}='+f'{detect_ms:.2f}'+r'\ \mathrm{ms}',20).move_to(caption)
        self.remove(caption);caption=updated;self.add(caption);self.wait(.5)
        self.play(tr.animate.set_value(.50048),run_time=1,rate_func=linear)
        self.play(tr.animate.set_value(.50049),run_time=1,rate_func=linear)
        updated=math(r'\Delta t_{\mathrm{SCR}}='+f'{scr_ms:.2f}'+r'\ \mathrm{ms}',20).move_to(caption)
        self.remove(caption);caption=updated;self.add(caption);self.wait(.5)
        self.play(tr.animate.set_value(.5015),run_time=2.5,rate_func=linear)
        self.play(tr.animate.set_value(.516),run_time=9.5,rate_func=linear)
        self.finish(26)

class FaultComparison(StudyScene):
    def construct(self):
        title(self,'03','Fault current: the measured reduction')
        footer(self,'Symmetrical RMS: 60 Hz phasor fit, same 0.95–1.05 s window in both cases')
        network=CompactFaultNetwork()
        self.add(network)
        self.add(txt('Without SCCL',19,RED).move_to(pos(-3.5,.61)),txt('With SCCL',19,BLUE).move_to(pos(3.6,.61)))
        window=(.49,.62); center=(.7,-.38)
        plot=NativePlot(self.d,'A',['IFA'],[RED],window,[-220,220,220],center,width=10.5,height=1.45,label=r'i_{F,A}\ /\ \mathrm{kA}',budget=1800)
        second=NativePlot(self.d,'B',['IFA'],[BLUE],window,[-220,220,220],center,width=10.5,height=1.45,label='',budget=1800)
        self.add(plot,second[1])
        self.add(math(r't\ /\ \mathrm{s}',20,MUTED).move_to(pos(6.35,-1.65)))
        self.add(txt('Phase A instantaneous current',17,MUTED).move_to(pos(0,.61)))
        tr=ValueTracker(.49); self.add(plot.cursor(tr))
        self.wait(6)
        self.play(tr.animate.set_value(.62),run_time=8,rate_func=linear)
        m=self.d.meta['metrics']; a=m['A']; b=m['B']
        labels=VGroup(*[txt(s,19).move_to(pos(x,-1.72)) for x,s in zip([-3.6,0,3.6],['Source 1','Source 2','Total fault'])])
        rows=VGroup()
        for x,key in zip([-3.6,0,3.6],['I1_rms_kA','I2_rms_kA','IF_rms_kA']):
            rows.add(math(f'{a[key]:.2f}\\ \longrightarrow\\ {b[key]:.2f}\\ \\mathrm{{kA}}',30,BLUE).move_to(pos(x,-2.2)))
        self.play(FadeIn(labels),FadeIn(rows),run_time=1)
        reduction=100*(1-b['IF_rms_kA']/a['IF_rms_kA'])
        self.play(Write(math(f'{reduction:.2f}\\%\\quad\\mathrm{{less\\ symmetrical\\ RMS\\ current}}',31,GREEN).move_to(pos(0,-2.84))),run_time=1.5)
        self.add(txt('Instantaneous peaks and symmetrical RMS are different quantities.',17,MUTED).move_to(pos(0,-3.3)))
        self.finish(28)

class Recovery(StudyScene):
    def construct(self):
        title(self,'04','Clear the fault. Recover. Reclose.')
        self.add(txt('Phase-A voltage/current  |  all-phase switching states',17,MUTED).move_to(pos(-2,2.99)))
        footer(self,'Gate removal does not force turn-off  |  SCRs cease conduction at their own current zeros')
        tr=ValueTracker(.49); self.add(clock(tr))
        chips=[indicator('Fault applied',lambda:any(self.d.value('C','FS'+p,tr.get_value())<.5 for p in 'ABC'),(-4.9,2.37),RED),
               indicator('Gate enabled',lambda:self.d.value('C','Gate',tr.get_value())>.5,(-2.45,2.37)),
               indicator('Any SCR on',lambda:self.d.conducting('C',tr.get_value()),(0,2.37)),
               indicator('Feeder closed',lambda:all(self.d.value('C','BR'+p,tr.get_value())<.5 for p in 'ABC'),(2.45,2.37),GREEN),
               indicator('Recovery ready',lambda:self.d.value('C','Recovery',tr.get_value())>.5,(4.9,2.37),GREEN)]
        self.add(*chips)
        plots=[]
        for i,(name,color,label,yr) in enumerate([
            ('IVA',ORANGE,r'i_{v,A}\ /\ \mathrm{kA}',[-30,30,30]),
            ('VCA',RED,r'v_{C,A}\ /\ \mathrm{kV}',[-3,3,3]),
            ('RMS1',BLUE,r'I_{1,\mathrm{rms}}^{(3\phi)}\ /\ \mathrm{kA}',[0,16,8])]):
            plot=NativePlot(self.d,'C',[name],[color],(.49,2.5),yr,(.7,1.4-i*1.22),width=10.5,height=.75,label=label,ticks=i==2,budget=2200)
            self.add(plot,plot.cursor(tr));plots.append(plot)
        self.add(txt('One-cycle RMS across all three phases (includes DC)',17,BLUE).move_to(pos(.7,-.43)))
        # A separate magnified normal-current scale makes actual settling visible.
        inset=NativePlot(self.d,'C',['RMS1'],[BLUE],(1.2,2.5),[0,.3,.15],(3.4,-2.7),width=4.6,height=.65,label='',budget=900)
        tail=NativePlot(self.d,'C',['IVA'],[ORANGE],(.64,.84),[0,1,.5],(-2.7,-2.7),width=4.6,height=.65,label='',budget=900)
        self.add(inset,tail,inset.cursor(tr,True),tail.cursor(tr,True),
            VGroup(txt('Reclosing detail:',17,MUTED),math(r'I_{1,\mathrm{rms}}^{(3\phi)}\ /\ \mathrm{kA}',20,BLUE)).arrange(RIGHT,buff=.12).move_to(pos(3.4,-2.05)),
            VGroup(txt('Natural extinction:',17,MUTED),math(r'i_{v,A}\ /\ \mathrm{kA}',20,ORANGE)).arrange(RIGHT,buff=.12).move_to(pos(-2.7,-2.05)))
        self.add(math(r't\ /\ \mathrm{s}',18,MUTED).move_to(pos(6.55,-1.72)))
        caption=txt(recovery_caption(self.d,tr.get_value()),20).move_to(pos(0,1.98))
        last_caption=[None]
        def update_caption(m):
            current=recovery_caption(self.d,tr.get_value())
            if current!=last_caption[0]:
                m.become(txt(current,20).move_to(pos(0,1.98)))
                last_caption[0]=current
        caption.add_updater(update_caption);update_caption(caption);self.add(caption)
        self.wait(1)
        stages=[(.58994,7),(.65606,3),(.81892,4),(.83761,2),(1.2,3),(1.25,3),(2.5,3)]
        for target,duration in stages:
            self.play(tr.animate.set_value(target),run_time=duration,rate_func=linear)
        tr.set_value(2.5);update_caption(caption)
        # Hold the fully restored native state for the closing narration.
        self.finish(30)

