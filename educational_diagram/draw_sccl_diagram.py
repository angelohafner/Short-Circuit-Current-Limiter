"""Create an educational SCCL schematic with genuine Schemdraw circuit elements.

Python 3.11. Schemdraw provides symbols, connections, terminals and current arrows.
Matplotlib arranges the panels and produces vector PDF/SVG and a 300 dpi PNG.
The input file contains values copied from the accepted native PSCAD study.
This script draws the electrical topology; it does not simulate the network.
"""
from pathlib import Path
import argparse
import hashlib
import json
import math

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyBboxPatch
import schemdraw
import schemdraw.elements as elm
from schemdraw.segments import Segment

ROOT = Path(__file__).resolve().parent
INK = '#172f46'
MUTED = '#53697c'
BLUE = '#167b9b'
ORANGE = '#ba4b16'
GATE = '#94601c'
OFF = '#a2abb5'
RULE = '#d5dfe7'
PAPER = '#f4f8fb'
ENDPOINT_AUDIT = []

plt.rcParams.update({
    'font.family': 'DejaVu Sans', 'font.size': 11,
    'mathtext.fontset': 'dejavusans', 'svg.fonttype': 'none',
    'pdf.fonttype': 42, 'ps.fonttype': 42, 'savefig.facecolor': 'white',
    'axes.unicode_minus': False,
})


class MOV(elm.ResistorIEC):
    """Voltage-dependent resistor: a diagonal marker, deliberately without an arrow."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.segments.append(Segment([(.10, -.43), (.90, .43), (1.10, .43)]))


def label(ax, x, y, text, size=11, color=INK, weight='normal', ha='center', **kw):
    return ax.text(x, y, text, fontsize=size, color=color, ha=ha, va='center',
                   weight=weight, linespacing=1.45, **kw)


def wire(d, *points, color=INK, lw=1.8, ls='-'):
    for p, q in zip(points[:-1], points[1:]):
        d.add(elm.Line(color=color, lw=lw, ls=ls).at(p).to(q))


def part(d, kind, a, b, color=INK, lw=1.8, ls='-', **kwargs):
    # Source symbols default to 90 degrees even when .to() is horizontal.
    # Explicit orientation makes every actual terminal coincide with its wire.
    angle = math.degrees(math.atan2(b[1]-a[1], b[0]-a[0]))
    element = d.add(kind(color=color, lw=lw, ls=ls, **kwargs).at(a).to(b).theta(angle))
    assert math.dist(element.start, a) < 1e-8 and math.dist(element.end, b) < 1e-8, (kind, a, b)
    ENDPOINT_AUDIT.append({'symbol':kind.__name__,'start':list(a),'end':list(b)})
    return element


def dot(d, xy, color=INK, open_=False):
    return d.add(elm.Dot(open=open_, radius=.065, color=color).at(xy))


def arrow(d, a, b, color=INK, lw=1.7, ls='-'):
    d.add(elm.Arrow(color=color, lw=lw, ls=ls, headwidth=.14, headlength=.22).at(a).to(b))


def gate_lead(d, scr, offset, name, ax, color=GATE):
    g = scr.gate
    start = (g.x, g.y + offset)
    arrow(d, start, g, color=color, lw=1.2, ls='--')
    label(ax, start[0], start[1] + (.22 if offset > 0 else -.22), name, 10, color)


def finish_drawing(d, ax, xlim, ylim):
    d.draw(show=False, canvas=ax)
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_aspect('equal', adjustable='box')
    ax.axis('off')


def section(fig, y, letter, title, subtitle):
    fig.text(.04, y, letter, color='white', fontsize=14, weight='bold', va='center',
             bbox=dict(boxstyle='round,pad=.30', facecolor=INK, edgecolor=INK))
    fig.text(.072, y, title, color=INK, fontsize=15, weight='bold', va='center')
    fig.text(.96, y, subtitle, color=MUTED, fontsize=10.5, va='center', ha='right')


def network(ax, p):
    d = schemdraw.Drawing(show=False, unit=2, fontsize=11, color=INK, lw=1.8)
    y = 6.3
    # Both source return terminals are grounded. Each source has its own series R-L.
    part(d, elm.SourceSin, (1.4, 4.8), (1.4, y))
    d.add(elm.Ground().at((1.4, 4.8)))
    wire(d, (1.4, y), (2.4, y))
    part(d, elm.ResistorIEC, (2.4, y), (4.8, y))
    part(d, elm.Inductor2, (4.8, y), (7.2, y))
    wire(d, (7.2, y), (8.2, y))
    wire(d, (7.6, y-.4), (7.6, y+.4), lw=3.8)
    ax.add_patch(Rectangle((8.2, 5.72), 3.5, 1.16, facecolor='#e7f3f6', edgecolor=BLUE, lw=2))
    label(ax, 9.95, y, 'SCCL', 14, BLUE, 'bold')
    label(ax, 9.95, 5.30, 'Expanded in panel B', 9.5, BLUE)
    wire(d, (11.7, y), (15.7, y))
    wire(d, (15.7, y-.4), (15.7, y+.4), lw=3.8)
    dot(d, (15.7, y))
    # Source 2 joins Bus 2 directly, without passing through the SCCL.
    wire(d, (15.7, y), (23.3, y))
    part(d, elm.Inductor2, (23.3, y), (25.7, y))
    part(d, elm.ResistorIEC, (25.7, y), (28.1, y))
    wire(d, (28.1, y), (29.1, y))
    part(d, elm.SourceSin, (29.1, 4.8), (29.1, y))
    d.add(elm.Ground().at((29.1, 4.8)))
    label(ax, 1.4, 7.5, 'Source 1', 12, weight='bold')
    label(ax, 29.1, 7.5, 'Source 2', 12, weight='bold')
    label(ax, 3.6, 7.04, r'$R_s$', 11)
    label(ax, 6.0, 7.04, r'$L_s$', 11)
    label(ax, 24.5, 7.04, r'$L_s$', 11)
    label(ax, 26.9, 7.04, r'$R_s$', 11)
    label(ax, 7.6, 7.46, 'Bus 1', 11, weight='bold')
    label(ax, 15.7, 7.46, 'Bus 2', 11, weight='bold')
    label(ax, 15.7, 8.08, '138 kV line-to-line RMS  |  60 Hz  |  Balanced three-phase network', 10.5, MUTED)
    arrow(d, (12.2, 6.90), (14.1, 6.90), BLUE)
    label(ax, 13.15, 7.40, r'$i_1$', 12, BLUE)
    arrow(d, (21.5, 6.90), (19.6, 6.90), BLUE)
    label(ax, 20.55, 7.40, r'$i_2$', 12, BLUE)
    # The common feeder breaker is upstream of both load and fault branches.
    wire(d, (15.7, y), (15.7, 5.8))
    part(d, elm.Breaker, (15.7, 5.8), (15.7, 4.2))
    label(ax, 16.4, 5.05, 'Feeder breaker\n3-pole', 10.5, ha='left')
    wire(d, (15.7, 4.2), (15.7, 3.85))
    wire(d, (12.0, 3.85), (20.7, 3.85)); dot(d, (15.7, 3.85))
    part(d, elm.ResistorIEC, (12.0, 3.85), (12.0, 2.35))
    part(d, elm.Inductor2, (12.0, 2.35), (12.0, .85))
    d.add(elm.Ground().at((12.0, .85)))
    label(ax, 10.9, 2.35, f'R-L load\n{p["load_MW"]:g} MW\nPF = {p["load_pf"]:g} lagging', 11, ha='right')
    arrow(d, (12.60, 3.7), (12.60, 2.7), BLUE)
    label(ax, 13.13, 3.2, r'$i_{\mathrm{load}}$', 11, BLUE, ha='left')
    part(d, elm.Switch, (20.7, 3.85), (20.7, 2.35))
    part(d, elm.ResistorIEC, (20.7, 2.35), (20.7, .85))
    d.add(elm.Ground().at((20.7, .85)))
    arrow(d, (20.10, 3.7), (20.10, 2.7), ORANGE)
    label(ax, 19.5, 3.2, r'$i_{\mathrm{fault}}$', 11, ORANGE, ha='right')
    label(ax, 21.5, 2.65, 'Three-phase fault\nApplied by fault switches', 10.5, ha='left')
    label(ax, 21.5, 1.18, rf'$R_f={p["fault_R_ohm"]:g}\;\Omega$/phase', 11, ha='left')
    label(ax, 3.6, 3.65, 'IDENTICAL SOURCE EQUIVALENTS', 9, MUTED, 'bold')
    label(ax, 3.6, 2.82, rf'$R_s={p["source_R_ohm"]:g}\;\Omega$   $L_s={1000*p["source_L_H"]:g}\;\mathrm{{mH}}$', 11)
    label(ax, 3.6, 2.15, 'Per phase, unchanged in both cases', 9, MUTED)
    label(ax, 3.6, 1.05, r'$i_1(t)+i_2(t)=i_{\mathrm{fault}}(t)+i_{\mathrm{load}}(t)$', 11, BLUE)
    finish_drawing(d, ax, (-.3, 31.0), (.05, 8.5))


def internal(ax, p):
    d = schemdraw.Drawing(show=False, unit=2, fontsize=11, color=INK, lw=1.8)
    top, byp, mov = 7.4, 4.0, 1.2
    left, right = 7.0, 20.7
    wire(d, (.4, top), (1.1, top))
    part(d, elm.ResistorIEC, (1.1, top), (3.5, top))
    part(d, elm.Inductor2, (3.5, top), (6.1, top))
    wire(d, (6.1, top), (left, top), (7.8, top))
    part(d, elm.ResistorIEC, (7.8, top), (10.4, top))
    part(d, elm.Capacitor, (10.4, top), (13.4, top))
    wire(d, (13.4, top), (right, top), (22.3, top))
    dot(d, (.4, top), open_=True);dot(d, (22.3, top), open_=True)
    label(ax, .4, 6.73, 'Bus 1', 10)
    label(ax, 22.3, 6.73, 'Bus 2', 10)
    label(ax, 2.3, 8.27, '$R_L$'+'\n'+rf'{p["reactor_R_ohm"]:.2f} $\Omega$', 10.5)
    label(ax, 4.8, 8.27, '$L$'+'\n'+f'{1000*p["reactor_L_H"]:g} mH', 10.5)
    label(ax, 9.1, 8.27, '$R_{ESR}$'+'\n'+rf'{p["capacitor_ESR_ohm"]:g} $\Omega$', 10.5)
    label(ax, 11.9, 8.27, '$C$'+'\n'+rf'{p["capacitor_C_uF"]:g} $\mu$F', 10.5)
    label(ax, 3.5, 6.45, 'Main reactor: always in series', 10.5, BLUE, 'bold')
    arrow(d, (1.0, 9.0), (2.8, 9.0), BLUE)
    label(ax, 1.9, 9.42, r'$i_{\mathrm{reactor}}$', 11, BLUE)
    arrow(d, (15.0, 8.0), (17.2, 8.0), BLUE)
    label(ax, 16.1, 8.50, r'$i_{\mathrm{capacitor}}$', 11, BLUE)
    # Capacitor voltage is sensed across C alone, excluding its series ESR.
    label(ax, 10.65, 6.75, '+', 12, MUTED)
    label(ax, 13.15, 6.75, '-', 12, MUTED)
    label(ax, 11.9, 6.75, r'$v_{\mathrm{capacitor}}$', 10.5, MUTED)
    # Shared discharge R-L precedes the two antiparallel SCRs.
    wire(d, (left, top), (left, mov))
    wire(d, (right, top), (right, mov))
    wire(d, (left, byp), (7.8, byp))
    part(d, elm.ResistorIEC, (7.8, byp), (10.4, byp))
    part(d, elm.Inductor2, (10.4, byp), (13.0, byp))
    wire(d, (13.0, byp), (13.5, byp))
    wire(d, (13.5, 3.0), (13.5, 5.0))
    wire(d, (18.5, 3.0), (18.5, 5.0))
    pos = part(d, elm.SCR, (13.5, 5.0), (18.5, 5.0))
    neg = part(d, elm.SCR, (18.5, 3.0), (13.5, 3.0))
    wire(d, (18.5, byp), (right, byp))
    for xy in [(13.5,byp),(18.5,byp)]:dot(d, xy)
    gate_lead(d, pos, -.42, r'$G_+$', ax)
    gate_lead(d, neg, .42, r'$G_-$', ax)
    label(ax, 16.0, 5.55, r'$T_+$', 11)
    label(ax, 16.0, 2.42, r'$T_-$', 11)
    label(ax, 9.1, 3.23, rf'$R_b$ = {p["bypass_R_ohm"]:g} $\Omega$', 10.5)
    label(ax, 11.7, 3.23, rf'$L_b$ = {1000*p["bypass_L_H"]:g} mH', 10.5)
    arrow(d, (7.9, 4.8), (10.2, 4.8), ORANGE)
    label(ax, 9.05, 5.3, r'$i_{\mathrm{valve}}$', 11, ORANGE)
    wire(d, (left, mov), (11.0, mov))
    part(d, MOV, (11.0, mov), (14.0, mov))
    wire(d, (14.0, mov), (right, mov))
    label(ax, 12.5, 1.95, 'MOV', 11, weight='bold')
    label(ax, 12.5, .45, f'{p["MOV_rating_kV"]:g} kV reference', 10.5)
    for x in [left, right]:
        for y in [top, byp, mov]:dot(d, (x,y))
    finish_drawing(d, ax, (-.1, 23), (-.1, 9.8))


def snubber(ax, p):
    d = schemdraw.Drawing(show=False, color=INK, lw=1.6)
    label(ax, 4, 8.2, 'RC SNUBBER DETAIL', 11, weight='bold')
    label(ax, 4, 7.55, 'Repeated across each SCR', 10, MUTED)
    s=part(d, elm.SCR, (1, 6.0), (7, 6.0))
    wire(d, (1, 6), (1, 3.5))
    wire(d, (7, 6), (7, 3.5))
    part(d, elm.ResistorIEC, (1, 3.5), (4, 3.5))
    part(d, elm.Capacitor, (4, 3.5), (7, 3.5))
    dot(d, (1,6));dot(d, (7,6))
    label(ax, .4, 6, 'A', 10);label(ax, 7.6, 6, 'K', 10)
    gate_lead(d, s, -.52, 'Gate', ax)
    label(ax, 2.5, 2.70, f'{p["SCR_snubber_R_ohm"]:g} $\Omega$', 10.5)
    label(ax, 5.5, 2.70, f'{p["SCR_snubber_C_uF"]:g} $\mu$F', 10.5)
    label(ax, 4, 1.35, 'One series R-C branch per SCR.\nSix snubbers in the three-phase model.', 10, MUTED)
    arrow(d, (1.5, .25), (3, .25), GATE, ls='--')
    label(ax, 3.45, .25, 'Gate command', 9.5, GATE, ha='left')
    finish_drawing(d, ax, (0, 8.2), (-.4, 8.8))


def current_path(ax, fault=False):
    active = ORANGE if fault else BLUE
    capcolor, capls = (OFF,'--') if fault else (active,'-')
    bycolor, byls = (active,'-') if fault else (OFF,'--')
    d=schemdraw.Drawing(show=False, lw=1.8, color=INK)
    wire(d, (.4,4.0), (1.0,4.0), color=active, lw=2.6)
    part(d, elm.Inductor2, (1,4), (4,4), color=active, lw=2.6)
    wire(d, (4,4), (4.8,4), color=active, lw=2.6)
    wire(d, (4.8,4), (4.8,5.4), (7,5.4), color=capcolor, lw=2.6 if not fault else 1.3, ls=capls)
    part(d, elm.Capacitor, (7,5.4), (10,5.4), color=capcolor, lw=2.6 if not fault else 1.3, ls=capls)
    wire(d, (10,5.4), (14,5.4), (14,4), color=capcolor, lw=2.6 if not fault else 1.3, ls=capls)
    wire(d, (4.8,4), (4.8,2.0), color=bycolor, lw=2.6 if fault else 1.3, ls=byls)
    part(d, elm.Inductor2, (4.8,2), (7.8,2), color=bycolor, lw=2.6 if fault else 1.3, ls=byls)
    wire(d, (7.8,2), (8.4,2), (8.4,2.8), color=bycolor, lw=2.6 if fault else 1.3, ls=byls)
    part(d, elm.SCR, (8.4,2.8), (12.6,2.8), color=bycolor, lw=2.6 if fault else 1.3, ls=byls)
    wire(d, (12.6,2.8), (12.6,2), (14,2), (14,4), color=bycolor, lw=2.6 if fault else 1.3, ls=byls)
    wire(d, (8.4,2), (8.4,1.1), color=OFF, lw=1.3, ls='--')
    part(d, elm.SCR, (12.6,1.1), (8.4,1.1), color=OFF, lw=1.3, ls='--')
    wire(d, (12.6,1.1), (12.6,2), color=OFF, lw=1.3, ls='--')
    wire(d, (14,4), (15.6,4), color=active, lw=2.6)
    for xy in [(4.8,4),(14,4),(8.4,2),(12.6,2)]:dot(d,xy,active)
    arrow(d, (.9,4.65), (2.2,4.65), active)
    label(ax, 2.5, 3.3, 'Main reactor', 10, active)
    label(ax, 8.5, 6.05, 'Capacitor', 10, capcolor)
    label(ax, 6.1, 1.15, 'Bypass R-L', 9.5, bycolor)
    if fault:
        arrow(d, (5,2.6), (6.5,2.6), active)
        arrow(d, (14.55,3.0), (14.55,3.8), active)
        label(ax, 10.5, 3.5, 'Forward SCR conducting', 9, active)
        label(ax, 8, .08, 'Positive-current half-cycle shown; the opposite SCR conducts on reversal.', 8.5, MUTED)
    else:
        arrow(d, (5.0,6.0), (6.4,6.0), active)
        arrow(d, (14.55,5.25), (14.55,4.45), active)
        label(ax, 10.5, 3.5, 'Both SCRs blocked', 9, MUTED)
        label(ax, 8, .08, 'Current flows mainly through the capacitor; valve current is negligible.', 8.5, MUTED)
    finish_drawing(d, ax, (0,16.1), (-.35,6.65))


def create(inputs, output):
    ENDPOINT_AUDIT.clear()
    p=inputs['parameters'];m=inputs['measured_results'];output.mkdir(parents=True,exist_ok=True)
    fig=plt.figure(figsize=(18,17),facecolor='white')
    fig.text(.04,.968,'How the TPSC limits short-circuit current',fontsize=25,weight='bold',color=INK,va='center')
    fig.text(.04,.942,'Series reactor + protected series capacitor  |  Native PSCAD study, explained through its electrical topology',fontsize=12,color=MUTED)
    section(fig,.911,'A','Two sources, one faulted feeder','Single-line representation of the three-phase network')
    network(fig.add_axes([.04,.692,.92,.205]),p)
    fig.add_artist(plt.Line2D([.04,.96],[.681,.681],transform=fig.transFigure,color=RULE,lw=1))
    section(fig,.657,'B','Inside the SCCL','One phase shown; identical circuit in phases A, B and C')
    internal(fig.add_axes([.035,.367,.695,.274]),p)
    fig.add_artist(plt.Line2D([.752,.752],[.378,.633],transform=fig.transFigure,color=RULE,lw=1))
    snubber(fig.add_axes([.775,.37,.185,.267]),p)
    fig.text(.055,.355,'Only the capacitor assembly is bypassed. The main reactor remains in the power-current path.',fontsize=11.5,color=BLUE,weight='bold')
    section(fig,.326,'C','Follow the dominant current path','Solid + arrows: dominant current  |  Dashed: negligible current')
    fig.text(.052,.298,'NORMAL OPERATION',fontsize=13,weight='bold',color=BLUE)
    fig.text(.052,.276,r'$X_L \approx X_C$  |  Low series impedance  |  $i_{\mathrm{reactor}}\approx i_{\mathrm{capacitor}}$',fontsize=10.5,color=MUTED)
    fig.text(.535,.298,'FAULT LIMITATION',fontsize=13,weight='bold',color=ORANGE)
    fig.text(.535,.276,r'Capacitor bypassed  |  $X_L$ limits current  |  $i_{\mathrm{reactor}}\approx i_{\mathrm{valve}}$',fontsize=10.5,color=MUTED)
    current_path(fig.add_axes([.04,.097,.44,.174]),False)
    current_path(fig.add_axes([.525,.097,.44,.174]),True)
    fig.text(.04,.083,'Path views omit MOV, snubbers and individual loss resistances for clarity; panel B contains the electrical connections.',fontsize=9.5,color=MUTED)
    # The values below are read from accepted EMTDC measurements, not calculated by the diagram.
    fig.add_artist(FancyBboxPatch((.04,.022),.92,.047,boxstyle='round,pad=.008',transform=fig.transFigure,facecolor=PAPER,edgecolor=RULE,lw=.8))
    fig.text(.055,.054,'MEASURED SYMMETRICAL RMS FAULT CURRENTS',fontsize=9.5,weight='bold',color=MUTED)
    cards=[('Total without SCCL',m['without_sccl']['fault_rms_kA'],.055,INK),
           ('Total with SCCL',m['with_sccl']['fault_rms_kA'],.30,BLUE),
           ('Source 1 with SCCL',m['with_sccl']['source1_rms_kA'],.535,BLUE),
           ('Source 2 with SCCL',m['with_sccl']['source2_rms_kA'],.77,INK)]
    for title,value,x,color in cards:
        fig.text(x,.034,f'{title}:  {value:.3f} kA',fontsize=12,weight='bold',color=color)
    fig.text(.96,.006,'Engineering diagram | Per-phase component values | L and C remain independently editable',ha='right',fontsize=8.5,color=MUTED)
    stem='SCCL_TPSC_Didactic_Diagram'
    for fmt in ['png','svg','pdf']:
        destination=output/f'{stem}.{fmt}'
        fig.savefig(destination,dpi=300,facecolor='white',metadata={'Creator':f'Schemdraw {schemdraw.__version__} and Matplotlib {matplotlib.__version__}'} if fmt!='png' else None)
        print('CREATED',destination,flush=True)
    # Overview for visual review, separate from the 300 dpi deliverable.
    fig.savefig(output/'diagram_review.png',dpi=120,facecolor='white')
    plt.close(fig)
    manifest={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in output.glob(stem+'.*')}
    (output/'figure_manifest.json').write_text(json.dumps({'schemdraw_version':schemdraw.__version__,
        'matplotlib_version':matplotlib.__version__,'input_sha256':hashlib.sha256((ROOT/'diagram_inputs.json').read_bytes()).hexdigest(),
        'figure_size_inches':[18,17],'png_dpi':300,'outputs':manifest,
        'verified_component_terminal_placements':ENDPOINT_AUDIT},indent=2),encoding='utf8')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT/'output')
    args=parser.parse_args()
    create(json.loads((ROOT/'diagram_inputs.json').read_text(encoding='utf8')),args.output)
