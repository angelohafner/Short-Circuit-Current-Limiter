"""Repair the observed reserved VDC label in the initial native build."""
from common import ROOT,connect
import xml.etree.ElementTree as ET
app=connect(63579);p=app.project('SCCL_B_With');c=p.canvas('Main')
for kind in ['voltmeter','datalabel','pgb']:
    for ph in 'ABC':
        for item in c.find_all('master:'+kind,Name='VD'+ph):item.parameters(Name='VDROP'+ph)
p.parameters(branch_threshold=1e-7)
p.save()
tree=ET.parse(p.filename)
for k,ph in enumerate('ABC'):
    y=40+70*k
    # The original top sensing wire passed through the lower voltmeter port.
    # Remove both original sensing wires and move the meter between cap terminals.
    for element in tree.iter('Wire'):
        x0=float(element.get('x'))/18;y0=float(element.get('y'))/18
        pts=[(x0+float(v.get('x'))/18,y0+float(v.get('y'))/18) for v in element.findall('vertex')]
        if pts and pts[-1] in [(130,y-8),(130,y-6)] and pts[0] in [(130,y),(132,y)]:
            c.component(int(element.get('id'))).delete()
    c.find('master:voltmeter',Name='VC'+ph).location=(131,y-8)
    c.create_wire((130,y),(130,y-8),(131,y-8))
    c.create_wire((132,y),(132,y-6),(131,y-6))
p.save();p.build()
messages=p.messages()
(ROOT/'diagnostics/with_sccl_build_messages.txt').write_text('\n'.join(str(m) for m in messages),encoding='utf8')
print('ERRORS',[str(m) for m in messages if m.status=='error'],flush=True)
print('WARNINGS',[str(m) for m in messages if m.status=='warning'],flush=True)
