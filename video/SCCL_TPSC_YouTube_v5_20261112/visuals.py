"""Small, independently animatable circuit objects and native-data plots."""
import json
import numpy as np
from manim import *
from data_access import ROOT, extrema_indices

PAPER='#F7FAFC'; INK='#172F46'; MUTED='#607487'; RULE='#D7E1E8'
BLUE='#167B9B'; ORANGE='#BA4B16'; GREEN='#16816A'; RED='#BD4053'; OFF='#A9B5C0'; GOLD='#9B7418'
config.background_color=PAPER
config.frame_width=128/9
config.frame_height=8

def pos(x,y): return np.array([x,y,0.])
def txt(s,size=24,color=INK): return Text(s,font='Arial',font_size=size,color=color)
def math(s,size=27,color=INK): return MathTex(s,font_size=size,color=color)
def wire(a,b,color=INK,width=2.5): return Line(pos(*a),pos(*b),color=color,stroke_width=width)
def ground(x,y):
    return VGroup(*[wire((x-w/2,y-.08*i),(x+w/2,y-.08*i)) for i,w in enumerate([.5,.32,.14])])

GEOMETRY=json.loads((ROOT/'assets/geometry.json').read_text())

def symbol(kind,a,b,color=INK):
    """Place using true bounding-box offset, including the asymmetrical SCR gate."""
    info=GEOMETRY[kind]; xmin,ymin,xmax,ymax=info['bbox']
    a,b=pos(*a),pos(*b); distance=np.linalg.norm(b-a); scale=distance/2
    angle=np.arctan2(*(b-a)[[1,0]])
    obj=SVGMobject(ROOT/f'assets/{kind}.svg',height=None,width=None)
    obj.scale((xmax-xmin)*scale/obj.width)
    offset=pos((xmin+xmax)/2-1,(ymin+ymax)/2)*scale
    obj.shift(offset-obj.get_center())
    obj.rotate(angle,about_point=ORIGIN).shift((a+b)/2)
    obj.set_color(color)
    return obj

def title(scene,number,heading,subtitle=None):
    heading_obj=txt(f'{number}  /  {heading}',30)
    if heading_obj.width>12.9: heading_obj.scale_to_fit_width(12.9)
    scene.add(heading_obj.move_to(pos(0,3.58)))
    if subtitle: scene.add(txt(subtitle,18,MUTED).move_to(pos(0,2.99)))
    scene.add(wire((-6.55,3.24),(6.55,3.24),RULE,1))

def footer(scene,s='Recorded PSCAD / EMTDC data  |  138 kV · 60 Hz'):
    scene.add(txt(s,14,MUTED).move_to(pos(0,-3.72)))

class PhaseCircuit(VGroup):
    """Phase-A detail: main R-L in series with a capacitor and protective bypass."""
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        y=1.9; by=.50; left=-1.65; right=5.0
        self.main=VGroup(wire((-6,y),(-5.6,y)),symbol('resistor',(-5.6,y),(-4.5,y)),
                        symbol('inductor',(-4.5,y),(-2.5,y)),wire((-2.5,y),(left,y)))
        self.cap=VGroup(wire((left,y),(-.1,y)),symbol('resistor',(-.1,y),(.8,y)),
                       symbol('capacitor',(.8,y),(3.8,y)),wire((3.8,y),(right,y)))
        self.shared=VGroup(wire((left,y),(left,by)),symbol('resistor',(left,by),(-.45,by)),
                          symbol('inductor',(-.45,by),(.8,by)),wire((.8,by),(1.35,by)),
                          wire((1.35,.08),(1.35,.92)),wire((4.05,.08),(4.05,.92)),
                          wire((4.05,by),(right,by)),wire((right,by),(right,y)))
        self.scr_p=VGroup(wire((1.35,.92),(1.8,.92)),symbol('scr',(1.8,.92),(3.6,.92)),wire((3.6,.92),(4.05,.92)))
        self.scr_n=VGroup(wire((1.35,.08),(1.8,.08)),symbol('scr',(3.6,.08),(1.8,.08)),wire((3.6,.08),(4.05,.08)))
        self.out=wire((right,y),(6,y))
        self.labels=VGroup(math(r'R_L',22).move_to(pos(-5.05,2.35)),math(r'L',28,BLUE).move_to(pos(-3.5,2.4)),
            math(r'R_C',19).move_to(pos(.35,2.32)),math(r'C',28,RED).move_to(pos(2.3,2.45)),
            math(r'R_b',20).move_to(pos(-1.06,.94)),math(r'L_b',20).move_to(pos(.1,.94)),
            math(r'T_+',20).move_to(pos(2.7,1.38)),math(r'T_-',20).move_to(pos(2.7,-.23)),
            txt('Phase A',17,MUTED).move_to(pos(-5.5,1.15)))
        self.dots=VGroup(Dot(pos(left,y),radius=.045,color=INK),Dot(pos(right,y),radius=.045,color=INK))
        # Sign arrows are an electrical reference, not particles moving one way in AC.
        self.arrows=VGroup(*[Arrow(LEFT*.3,RIGHT*.3,buff=0,color=c,stroke_width=2,max_tip_length_to_length_ratio=.22).move_to(pos(x,yy))
                            for x,yy,c in [(-2.05,2.28,BLUE),(4.3,2.28,RED),(4.5,.15,ORANGE)]])
        self.add(self.main,self.cap,self.shared,self.scr_p,self.scr_n,self.out,self.labels,self.dots,self.arrows)

    def update_native(self,data,case,time):
        currents=[data.value(case,n,time) for n in ['I1A','ICA','IVA']]
        p=data.value(case,'TONAP',time)>data.value(case,'TOFFAP',time)
        n=data.value(case,'TONAN',time)>data.value(case,'TOFFAN',time)
        self.main.set_color(BLUE)
        self.cap.set_color(RED if abs(currents[1])>.001 else OFF)
        self.shared.set_color(ORANGE if p or n else OFF)
        self.scr_p.set_color(ORANGE if p else OFF)
        self.scr_n.set_color(ORANGE if n else OFF)
        self.out.set_color(BLUE)
        for arr,current in zip(self.arrows,currents):
            center=arr.get_center(); sign=1 if current>=0 else -1
            arr.put_start_and_end_on(center-pos(.30*sign,0),center+pos(.30*sign,0))
            arr.set_opacity(1 if abs(current)>.001 else .15)
        return self

class NativePlot(VGroup):
    def __init__(self,data,case,names,colors,window,yrange,center,width=10.4,height=.66,label='',ticks=True,budget=1600,label_size=22,label_offset=1.0):
        super().__init__()
        self.window=window
        self.axes=Axes(x_range=[window[0],window[1],(window[1]-window[0])/4],y_range=yrange,
            x_length=width,y_length=height,tips=False,
            axis_config={'color':RULE,'stroke_width':1.1,'include_ticks':False})
        self.axes.move_to(pos(*center))
        self.add(self.axes)
        t=data.array(case,'time'); mask=(t>=window[0])&(t<=window[1]); ts=t[mask]
        for name,color in zip(names,colors):
            values=data.array(case,name)[mask]
            indices=extrema_indices(values,budget)
            curve=VMobject(color=color,stroke_width=1.8)
            curve.set_points_as_corners([self.axes.c2p(float(x),float(y)) for x,y in zip(ts[indices],values[indices])])
            self.add(curve)
        self.add(math(label,label_size,colors[0]).move_to(pos(center[0]-width/2-label_offset,center[1])))
        for y in sorted(set([yrange[0],0,yrange[1]])):
            self.add(math(f'{y:g}',17,MUTED).next_to(self.axes.c2p(window[0],y),LEFT,buff=.08))
        if ticks:
            for x in np.linspace(*window,5):
                self.add(math(f'{x:.3f}',17,MUTED).move_to(self.axes.c2p(x,yrange[0])+DOWN*.19))

    def cursor(self,tracker,only_in_window=False):
        y0,y1=self.axes.y_range[:2]
        def build():
            time=tracker.get_value()
            x=np.clip(time,*self.window) if only_in_window else time
            line=Line(self.axes.c2p(x,y0),self.axes.c2p(x,y1),color=INK,stroke_width=1.3)
            if only_in_window and not self.window[0]<=time<=self.window[1]:line.set_opacity(0)
            return line
        return always_redraw(build)

def clock(tracker,center=(4.8,2.9),size=21):
    value=DecimalNumber(tracker.get_value(),num_decimal_places=5,font_size=size,color=INK)
    value.add_updater(lambda m:m.set_value(tracker.get_value()))
    group=VGroup(math('t=',size),value,math(r'\mathrm{s}',size)).arrange(RIGHT,buff=.06).move_to(pos(*center))
    return group

def state_chip(label,active,center,color=ORANGE,width=2.2):
    box=RoundedRectangle(corner_radius=.08,width=width,height=.38,stroke_color=RULE,stroke_width=1,fill_color=color if active else '#E8EDF1',fill_opacity=1)
    text=txt(label,16,'#FFFFFF' if active else MUTED)
    return VGroup(box,text).move_to(pos(*center))

def indicator(label,predicate,center,color=ORANGE,width=2.2):
    # Stable geometry: only colors update, avoiding text re-layout each frame.
    chip=state_chip(label,False,center,color,width)
    def update(m):
        active=bool(predicate())
        m[0].set_fill(color if active else '#E8EDF1')
        m[1].set_color('#FFFFFF' if active else MUTED)
    chip.add_updater(update)
    update(chip)
    return chip

class CompactFaultNetwork(VGroup):
    """Single-line fault topology; only source 1 traverses the SCCL."""
    def __init__(self):
        super().__init__()
        for number,y,color in [(1,2.63,BLUE),(2,1.5,ORANGE)]:
            self.add(txt(f'Source {number}',17,color).move_to(pos(-6.0,y)),
                     symbol('source',(-5.15,y),(-4.4,y),color),
                     wire((-5.15,y),(-5.33,y),color),
                     wire((-5.33,y),(-5.33,y-.32),color),
                     ground(-5.33,y-.32),
                     wire((-4.4,y),(-3.85,y),color),
                     Rectangle(width=1.0,height=.43,color=color,stroke_width=2).move_to(pos(-3.35,y)),
                     math(f'Z_{{s{number}}}',20,color).move_to(pos(-3.35,y)))
        self.add(wire((-2.85,2.63),(-1.9,2.63),BLUE),
                 RoundedRectangle(width=1.6,height=.61,corner_radius=.06,color=BLUE,
                                  fill_color='#E1F0F4',fill_opacity=1).move_to(pos(-1.1,2.63)),
                 txt('SCCL',21,BLUE).move_to(pos(-1.1,2.63)),
                 wire((-.3,2.63),(1.0,2.63),BLUE),
                 wire((-2.85,1.5),(1.0,1.5),ORANGE),
                 wire((1.0,1.5),(1.0,2.63),ORANGE),
                 Dot(pos(1.0,2.63),radius=.05,color=INK),
                 wire((1.0,2.63),(2.1,2.63)),
                 Dot(pos(2.1,2.63),radius=.035,color=INK),
                 wire((2.1,2.63),(2.7,2.63),GREEN,4),
                 Dot(pos(2.7,2.63),radius=.035,color=INK),
                 wire((2.7,2.63),(4.35,2.63)),
                 txt('Feeder breaker',14,MUTED).move_to(pos(2.4,3.0)),
                 wire((4.35,2.63),(4.35,2.2),RED),
                 VMobject(color=RED,stroke_width=2.8).set_points_as_corners(
                     [pos(4.35,2.2),pos(4.12,1.86),pos(4.49,1.89),pos(4.27,1.5)]),
                 txt('Fault',18,RED).move_to(pos(5.15,1.93)),
                 txt('With SCCL, load omitted  |  138 kV, 60 Hz',15,MUTED).move_to(pos(.5,1.03)),
                 wire((-6.55,.82),(6.55,.82),RULE,1))


class Network(VGroup):
    def __init__(self):
        super().__init__()
        self.s1=VGroup(symbol('source',(-5.7,-.8),(-5.7,1.2)),ground(-5.7,-.8),txt('Source 1',22).move_to(pos(-5.7,-1.35)))
        self.z1=VGroup(wire((-5.7,1.2),(-5.1,1.2)),symbol('resistor',(-5.1,1.2),(-4.1,1.2)),symbol('inductor',(-4.1,1.2),(-2.9,1.2)),math(r'Z_{s1}',24).move_to(pos(-4.1,1.8)))
        self.device=VGroup(wire((-2.9,1.2),(-2.4,1.2)),RoundedRectangle(width=2,height=1,corner_radius=.08,color=BLUE,fill_color='#E1F0F4',fill_opacity=1).move_to(pos(-1.4,1.2)),txt('SCCL',27,BLUE).move_to(pos(-1.4,1.2)),wire((-.4,1.2),(.7,1.2)))
        self.bus1=VGroup(wire((-2.65,.75),(-2.65,1.65),INK,4),txt('Bus 1',18).move_to(pos(-2.65,2.15)))
        self.bus2=VGroup(wire((.7,.6),(.7,1.8),INK,4),txt('Bus 2',18).move_to(pos(.7,2.15)))
        self.s2=VGroup(symbol('source',(-2,-2.25),(-2,-.6)),ground(-2,-2.25),txt('Source 2',22).move_to(pos(-2,-2.8)),wire((-2,-.6),(-1.6,-.6)),symbol('resistor',(-1.6,-.6),(-.55,-.6)),symbol('inductor',(-.55,-.6),(.7,-.6)),wire((.7,-.6),(.7,1.2)),math(r'Z_{s2}',24).move_to(pos(-.6,-1.15)))
        self.feeder=VGroup(wire((.7,1.2),(2.2,1.2)),Dot(pos(2.2,1.2),radius=.045,color=INK),wire((2.2,1.2),(2.9,1.2),GREEN,4),Dot(pos(2.9,1.2),radius=.045,color=INK),wire((2.9,1.2),(5.5,1.2)),txt('Feeder breaker',18).move_to(pos(2.55,1.85)))
        self.load=VGroup(wire((5.5,1.2),(5.5,-.5)),Rectangle(width=1,height=.85,color=INK).move_to(pos(5.5,-.93)),txt('Load',20).move_to(pos(5.5,-.93)))
        self.fault=VGroup(wire((4.2,1.2),(4.2,-.2),RED),VMobject(color=RED,stroke_width=3).set_points_as_corners([pos(4.2,-.2),pos(3.9,-.65),pos(4.35,-.6),pos(4.05,-1.15)]),txt('Fault',20,RED).move_to(pos(4.1,-1.6)))
        self.add(self.s1,self.z1,self.device,self.bus1,self.bus2,self.s2,self.feeder,self.load,self.fault)
