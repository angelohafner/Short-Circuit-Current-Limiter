"""Use dedicated native ammeters so current channels are evaluated in DSOUT."""
import xml.etree.ElementTree as ET
from common import ROOT,connect
app=connect(63579)
for name in ['SCCL_B_With','SCCL_C_Recovery']:
    p=app.project(name);c=p.canvas('Main');p.save();tree=ET.parse(p.filename)
    for num in [1,2]:c.find('master:source3',Name=f'Source_{num}').parameters(Ia='',Ib='',Ic='')
    for k,ph in enumerate('ABC'):
        y=40+70*k
        for element in tree.iter('Wire'):
            x0=float(element.get('x'))/18;y0=float(element.get('y'))/18
            pts=[(x0+float(v.get('x'))/18,y0+float(v.get('y'))/18) for v in element.findall('vertex')]
            if pts in [[(46,y),(60,y)],[(218,y),(194,y)]]:c.component(int(element.get('id'))).delete()
        meter=c.create_component('master:ammeter',52,y,Name='I1'+ph)
        c.create_wire((46,y),(52,y));c.create_wire((54,y),(60,y))
        meter=c.create_component('master:ammeter',208,y,Name='I2'+ph);meter.mirror()
        ports=meter.ports();assert ports['N1'].x>ports['N2'].x
        c.create_wire((218,y),(ports['N1'].x,y));c.create_wire((ports['N2'].x,y),(194,y))
    p.save();p.build();errors=[str(m) for m in p.messages() if m.status=='error'];print(name,errors,flush=True);assert not errors
