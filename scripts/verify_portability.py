"""Run a relocated native SCCL project in a fresh directory and preserve its outputs."""
from pathlib import Path
from datetime import datetime,timezone
import argparse
import shutil
import json
import zipfile
import hashlib
import numpy as np
from common import ROOT,connect,write_json,sha
from analysis_core import read_outputs,fit_phasor

ap=argparse.ArgumentParser();ap.add_argument('--port',type=int,default=63579);a=ap.parse_args()
stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S_%fZ')
dst=ROOT/'portability'/stamp;dst.mkdir(parents=True)
source=ROOT/'pscad/SCCL_B_With.pscx'
staging=dst/'SCCL_TPSC_Workspace_Staging.zip'
payload=sorted([p for p in (ROOT/'pscad').iterdir() if p.suffix in ['.pscx','.pswx']])
manifest={f'SCCL_TPSC_Study/pscad/{p.name}':sha(p) for p in payload}
with zipfile.ZipFile(staging,'x',compression=zipfile.ZIP_DEFLATED) as archive:
    for p in payload:archive.write(p,f'SCCL_TPSC_Study/pscad/{p.name}')
    archive.writestr('manifest.json',json.dumps(manifest,indent=2))
with zipfile.ZipFile(staging) as archive:
    assert archive.testzip() is None
    for relative,digest in manifest.items():assert hashlib.sha256(archive.read(relative)).hexdigest()==digest
    archive.extractall(dst/'extracted')
project_dir=dst/'extracted/SCCL_TPSC_Study/pscad'
relocated=project_dir/source.name
app=connect(a.port)
app.load(str(project_dir/'SCCL_TPSC_Study.pswx'))
loaded=[p['name'] for p in app.projects() if p['type']=='Case']
assert sorted(loaded)==['SCCL_A_Without','SCCL_B_With','SCCL_C_Recovery']
# Reopen the extracted relative-path workspace, not just an isolated model file.
app.load(str(project_dir/'SCCL_TPSC_Study.pswx'));p=app.project('SCCL_B_With')
assert Path(p.filename).resolve()==relocated.resolve()
started=datetime.now(timezone.utc);p.run();ended=datetime.now(timezone.utc)
messages=p.messages();errors=[str(m) for m in messages if m.status=='error']
build=relocated.with_suffix('.gf81');files=[build/'SCCL_B_With.inf']+sorted(build.glob('SCCL_B_With_*.out'))
assert not errors and len(files)>1
assert all(f.stat().st_mtime>=started.timestamp()-2 for f in files)
out=dst/'native_results';out.mkdir()
for f in files:shutil.copy2(f,out/f.name)
t,d=read_outputs(out);mask=(t>=.95)&(t<1.05)
result={prefix:float(np.mean([abs(fit_phasor(t[mask],d[prefix+ph][mask])) for ph in 'ABC'])) for prefix in ['I1','I2','IF']}
expected=json.loads((ROOT/'results/metrics.json').read_text())['with_sccl']
assert abs(result['IF']-expected['fault_rms_kA'])<1e-6
assert sha(source)==sha(relocated),'Relocation changed the native model'
receipt={'relocated_directory':str(dst),'start_utc':started.isoformat(),'finish_utc':ended.isoformat(),
         'relative_evidence_directory':str(dst.relative_to(ROOT)).replace('\\','/'),
         'relative_result_directory':str(out.relative_to(ROOT)).replace('\\','/'),
         'staging_archive_sha256':sha(staging),'staging_payload_hashes':manifest,
         'extracted_workspace_reopened':True,'extracted_project_count':len(loaded),
         'licensed':app.licensed(),'fresh_outputs':True,'errors':errors,'model_sha256':sha(relocated),
         'source_unchanged':True,'result':result,'reference_fault_rms_kA':expected['fault_rms_kA'],
         'output_sha256':{f.name:sha(f) for f in files}}
write_json(dst/'portability_receipt.json',receipt);write_json(ROOT/'results/portability_receipt.json',receipt)
app.load(str(ROOT/'pscad/SCCL_TPSC_Study.pswx'));app.project('SCCL_B_With').focus()
print('PORTABILITY VERIFIED',result,flush=True)
