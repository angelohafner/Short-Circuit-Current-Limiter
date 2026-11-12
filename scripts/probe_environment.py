"""Inspect the installed PSCAD automation environment and native definitions."""
from pathlib import Path
import json
import inspect
import xml.etree.ElementTree as ET
import argparse
import mhi.pscad

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'diagnostics'
OUT.mkdir(parents=True, exist_ok=True)
parser = argparse.ArgumentParser()
parser.add_argument('--port', type=int, default=0)
parser.add_argument('--launch', action='store_true')
args = parser.parse_args()
native = Path(r'C:\Program Files (x86)\PSCAD\5.1.0\master.pslx')
tree = ET.parse(native)
names = ['source3','source_1','peswitch','breaker','breaker3','capacitor','inductor','resistor','ammeter','voltmeter','voltmetergnd','arrester','mov','nonlin','nonlin_r','comparator','time-sig','logic','flipflop','pgb','rms3','rms','signal','datalabel','blackbox','fortran','compare','logic_mult','integral','realpole']
definitions = []
for d in tree.iter('Definition'):
    name = d.get('name','')
    definitions.append(name)
    if name in names or any(s in name.lower() for s in ['arrester','varistor','thyristor','breaker','latch']):
        (OUT/(name+'.xml')).write_text(ET.tostring(d,encoding='unicode'),encoding='utf8')
(OUT/'master_definition_names.json').write_text(json.dumps(definitions,indent=2))
print('DEFINITIONS', [n for n in definitions if any(x in n.lower() for x in ['mov','arr','switch','break','rms','fortran','signal','compar','logic'])], flush=True)
app = mhi.pscad.launch(version='5.1.0', minimize=True, timeout=50) if args.launch else mhi.pscad.connect(port=args.port,timeout=10)
print('APP', app, 'VERSION', app.version, 'LICENSED', app.licensed(), flush=True)
print('PROJECTS', app.projects(), flush=True)
(OUT/'environment.json').write_text(json.dumps({'version':app.version,'licensed':app.licensed(),'connection':str(app),'projects':app.projects()},indent=2,default=str))
for name in ['create_case','create_library','load','save_workspace']:
    method = getattr(app,name,None)
    print('API',name,inspect.signature(method) if method else 'UNAVAILABLE', flush=True)
