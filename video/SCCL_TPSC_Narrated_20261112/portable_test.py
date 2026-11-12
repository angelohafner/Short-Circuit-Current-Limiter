"""Render a fresh pilot from a standalone copy with no raw study outputs."""
from datetime import datetime,timezone
import json
import shutil
import subprocess
import sys
from data_access import ROOT,sha256

def main():
    stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    target=ROOT.parent/'portability checks'/stamp/'SCCL_TPSC'
    target.mkdir(parents=True)
    for pattern in ['*.py','*.md','*.txt','tests/*.py','assets/*','data/*.json','data/*.npz','data/receipts/*','dependencies/*','docs/*','config/*','pscad/*.pscx']:
        for p in ROOT.glob(pattern):
            if p.is_file():
                out=target/p.relative_to(ROOT);out.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,out)
    (target/'evidence').mkdir(exist_ok=True)
    log=target/'evidence/portable_test.log'
    with log.open('w',encoding='utf-8') as stream:
        for cmd in [[sys.executable,'-m','unittest','discover','-s','tests','-v'],
                    [sys.executable,'render_video.py','--preview','--only','FaultTransfer'],
                    [sys.executable,'validate_video.py','--data-only']]:
            subprocess.run(cmd,cwd=target,check=True,stdout=stream,stderr=subprocess.STDOUT)
    report=json.loads((target/'evidence/validation.json').read_text())
    assert report['passed']==report['total']
    assert all(v.startswith('RAW SOURCE ABSENT') for v in report['source_status'].values())
    pilot=target/'output/FaultTransfer_preview.mp4'
    result={'directory':str(target),'native_raw_sources_absent':True,'data_checks_passed':report['passed'],
            'pilot_rendered':True,'pilot_sha256':sha256(pilot),'pilot_seconds':26,
            'compact_sha256':report['compact_sha256'],'fresh_path_with_spaces':True,
            'source_sha256':{p.name:sha256(p) for p in target.glob('*.py')}}
    (ROOT/'evidence/portable_render.json').write_text(json.dumps(result,indent=2)+'\n')
    # Publish the fresh standalone pilot as the portable package's preview.
    shutil.copy2(pilot,ROOT/'output/FaultTransfer_preview.mp4')
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
