"""Create a timestamped portable archive and verify every payload hash and ZIP CRC."""
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import zipfile
from data_access import ROOT,sha256

def main():
    validation=json.loads((ROOT/'evidence/validation.json').read_text())
    assert validation['passed']==validation['total'] and validation['video_sha256']
    assert validation['video_sha256']==sha256(ROOT/'output/SCCL_TPSC_final.mp4')
    assert (ROOT/'evidence/portable_render.json').exists(),'Complete standalone render validation first'
    assert (ROOT/'evidence/independent_review.md').exists(),'Complete independent review first'
    payload=[]
    for pattern in ['*.py','*.md','*.txt','docs/*','assets/*','data/*.json','data/*.npz','data/receipts/*',
                    'dependencies/*','config/*','pscad/*.pscx','pscad/*.pswx','tests/*.py','output/*.mp4','evidence/*.json','evidence/*.md']:
        payload.extend(p for p in ROOT.glob(pattern) if p.is_file())
    payload.extend(ROOT.glob('evidence/frames_SCCL_TPSC_final/*.jpg'))
    payload=sorted(set(payload))
    manifest={'format':1,'files':{str(p.relative_to(ROOT)).replace('\\','/'):{'sha256':sha256(p),'bytes':p.stat().st_size} for p in payload}}
    stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    destination=ROOT.parent/f'SCCL_TPSC_Video_{stamp}.zip'
    with zipfile.ZipFile(destination,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for p in payload:z.write(p,'SCCL_TPSC/'+str(p.relative_to(ROOT)).replace('\\','/'))
        z.writestr('SCCL_TPSC/manifest.json',json.dumps(manifest,indent=2)+'\n')
    with zipfile.ZipFile(destination) as z:
        assert z.testzip() is None
        for name,info in manifest['files'].items():
            assert hashlib.sha256(z.read('SCCL_TPSC/'+name)).hexdigest()==info['sha256'],name
    result={'archive':str(destination),'sha256':sha256(destination),'bytes':destination.stat().st_size,
            'payload_files':len(payload),'crc_verified':True,'all_payload_hashes_verified':True}
    (ROOT/'evidence/package_receipt.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
