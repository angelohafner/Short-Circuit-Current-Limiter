"""Export genuine Schemdraw symbols and explicit electrical terminal geometry."""
from pathlib import Path
import json
import sys
import shutil
import importlib.util
import xml.etree.ElementTree as ET
from data_access import ROOT, sha256

def build():
    dependencies=ROOT/'dependencies'
    dependencies.mkdir(exist_ok=True)
    wheel=dependencies/'schemdraw-0.23-py3-none-any.whl'
    if not wheel.exists():
        shutil.copy2(ROOT.parents[1]/'educational_diagram/dependencies'/wheel.name,wheel)
    sys.path.insert(0,str(wheel))
    import schemdraw
    import schemdraw.elements as elm
    from schemdraw.segments import Segment
    class MOV(elm.ResistorIEC):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.segments.append(Segment([(.1,-.43),(.9,.43),(1.1,.43)]))
    assets=ROOT/'assets'
    assets.mkdir(exist_ok=True)
    geometry={}
    for name,kind in {'resistor':elm.ResistorIEC,'inductor':elm.Inductor2,'capacitor':elm.Capacitor,
                      'scr':elm.SCR,'source':elm.SourceSin,'mov':MOV}.items():
        d=schemdraw.Drawing(show=False,backend='svg',color='#172f46',lw=2,unit=2)
        e=d.add(kind().at((0,0)).to((2,0)).theta(0))
        assert abs(e.start.x)<1e-9 and abs(e.end.x-2)<1e-9
        bbox=d.get_bbox()
        svg=ET.fromstring(d.get_imagedata('svg'))
        # Matplotlib adds a page rectangle. It is not electrical geometry and
        # would corrupt Manim's terminal-to-terminal scale calculation.
        for parent in svg.iter():
            for child in list(parent):
                if child.attrib.get('id') == 'patch_1': parent.remove(child)
        ET.register_namespace('','http://www.w3.org/2000/svg')
        (assets/f'{name}.svg').write_bytes(ET.tostring(svg,encoding='utf-8',xml_declaration=True))
        geometry[name]={'start':list(e.start),'end':list(e.end),'bbox':list(bbox),
                        'gate':list(e.gate) if name=='scr' else None,
                        'sha256':sha256(assets/f'{name}.svg')}
    (assets/'geometry.json').write_text(json.dumps(geometry,indent=2)+'\n')
    (assets/'provenance.json').write_text(json.dumps({'library':'Schemdraw','version':schemdraw.__version__,
        'wheel_sha256':sha256(wheel),'terminal_checks':'All start=(0,0), end=(2,0); SVG symbols contain no labels.'},indent=2)+'\n')
    print('Six Schemdraw SVG symbols exported; all terminal checks passed.')

if __name__=='__main__': build()
