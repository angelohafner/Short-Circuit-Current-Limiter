"""Validate the exported diagram and preserve portable, file-bound evidence."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import xml.etree.ElementTree as ET
from PIL import Image

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'output'
STEM='SCCL_TPSC_Didactic_Diagram'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def command(name, *args):
    executable=shutil.which(name)
    if not executable:raise RuntimeError('PDF verification requires Poppler command: '+name)
    return subprocess.run([executable,*map(str,args)],capture_output=True,check=True).stdout.decode('utf8')


def verify():
    record={'checks':{},'source_provenance':{}}
    checks=record['checks']
    manifest=json.loads((OUT/'figure_manifest.json').read_text())
    inputs=json.loads((ROOT/'diagram_inputs.json').read_text())
    for filename,digest in manifest['outputs'].items():
        checks['unchanged_export:'+filename]=sha(OUT/filename)==digest
    checks['input_hash_matches_exports']=sha(ROOT/'diagram_inputs.json')==manifest['input_sha256']
    image=Image.open(OUT/(STEM+'.png'));image.verify()
    image=Image.open(OUT/(STEM+'.png'))
    checks['png_5400_by_5100']=image.size==(5400,5100)
    checks['png_300_dpi']=all(abs(x-300)<.1 for x in image.info['dpi'])
    svg=ET.parse(OUT/(STEM+'.svg')).getroot()
    checks['svg_has_vector_paths']=len(svg.findall('.//{http://www.w3.org/2000/svg}path'))>100
    checks['svg_has_editable_text']=len(svg.findall('.//{http://www.w3.org/2000/svg}text'))>50
    checks['svg_has_no_raster_images']=not svg.findall('.//{http://www.w3.org/2000/svg}image')
    pdf=OUT/(STEM+'.pdf')
    info=command('pdfinfo',pdf);fonts=command('pdffonts',pdf);images=command('pdfimages','-list',pdf)
    checks['pdf_one_page']=any(x.split(':')[-1].strip()=='1' for x in info.splitlines() if x.startswith('Pages:'))
    checks['pdf_no_raster_images']=len([x for x in images.splitlines()[2:] if x.strip()])==0
    font_rows=[x for x in fonts.splitlines()[2:] if x.strip()]
    checks['pdf_embedded_fonts']=bool(font_rows) and all('yes yes yes' in x for x in font_rows)
    text=command('pdftotext','-layout',pdf,'-')
    expected=['Source 1','Source 2','Bus 1','Bus 2','Three-phase fault','RC SNUBBER DETAIL',
              '79.959','49.913','9.927','39.991','15.9','442.5','0.005','0.002',
              'NORMAL OPERATION','FAULT LIMITATION']
    checks['required_labels_and_values_present']=all(s in text for s in expected)
    checks['no_literal_newline_escape_in_labels']='\\n' not in text
    checks['all_component_anchors_verified_during_generation']=len(manifest['verified_component_terminal_placements'])>=30
    for relative,digest in inputs['provenance']['source_hashes'].items():
        path=ROOT.parent/relative
        if path.exists():
            checks['native_study_unchanged:'+relative]=sha(path)==digest
            record['source_provenance'][relative]='Verified unchanged'
        else:
            record['source_provenance'][relative]='Not included in standalone diagram package; original hash retained in diagram_inputs.json'
    command('pdftoppm','-scale-to','2400','-png','-singlefile',pdf,OUT/'pdf_render_review')
    (OUT/'pdf_text_review.txt').write_text(text,encoding='utf8')
    record['pdfinfo']=info
    record['pdffonts']=fonts
    record['pdfimages']=images
    record['verified_terminal_placements']=len(manifest['verified_component_terminal_placements'])
    record['passed']=sum(checks.values());record['total']=len(checks)
    record['outputs']={str(p.relative_to(ROOT)).replace('\\','/'):sha(p) for p in OUT.glob(STEM+'.*')}
    (OUT/'verification.json').write_text(json.dumps(record,indent=2),encoding='utf8')
    print('VERIFIED',record['passed'],'/',record['total'],'checks')
    assert all(checks.values()),[k for k,v in checks.items() if not v]
    return record


if __name__=='__main__':verify()
