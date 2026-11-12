"""Create immutable native and full packages; verify CRC and every payload hash."""
from pathlib import Path
from datetime import datetime,timezone
import zipfile
import json
from common import ROOT,sha,write_json

SCRIPT_NAMES=['common.py','probe_environment.py','build_project.py','run_simulations.py','run_matrix.py',
              'analysis_core.py','analyze_results.py','plot_results.py','write_reports.py','inspect_run.py',
              'finalize_native.py','package_results.py','verify_portability.py','delivery_checks.py','configure_graphs.py']

def selected_payload(full):
    files=[p for p in (ROOT/'pscad').glob('*') if p.suffix in ['.pscx','.pswx']]
    files += [ROOT/'scripts'/n for n in SCRIPT_NAMES if (ROOT/'scripts'/n).exists()]
    files += list((ROOT/'config').glob('*.json'))+list((ROOT/'tests').glob('*.py'))
    files += list((ROOT/'docs').glob('*.md'))
    files += [ROOT/n for n in ['README.md','technical_report.md','validation_report.md','requirements-lock.txt']]
    files += list((ROOT/'references').glob('*.png'))+list((ROOT/'results/figures').glob('*'))
    files += list((ROOT/'results/native_views').glob('*.png'))
    files += [p for p in (ROOT/'results').glob('*.json') if p.name not in ['package_verification.json','delivery_manifest.json']]
    if full:
        index=json.loads((ROOT/'results/selected_runs.json').read_text())
        for folder in index.values():files.extend(p for p in (ROOT/folder).iterdir() if p.is_file())
        port=json.loads((ROOT/'results/portability_receipt.json').read_text())
        files.extend(p for p in (ROOT/port['relative_evidence_directory']).rglob('*') if p.is_file() and '.gf81' not in str(p))
    else:
        # Native package supports opening/running and immediate figure/report review;
        # accepted raw data are in the full package.
        files=[p for p in files if p.name!='selected_runs.json']
    return sorted(set(files),key=lambda p:str(p.relative_to(ROOT)))

def create_archive(full=True):
    from delivery_checks import final_preflight
    print('FINAL PREFLIGHT',final_preflight(),flush=True)
    stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    destination=ROOT/'delivery';destination.mkdir(exist_ok=True)
    name='SCCL_TPSC_Full' if full else 'SCCL_TPSC_Native'
    target=destination/(name+'_'+stamp+'.zip')
    files=selected_payload(full)
    manifest={str(p.relative_to(ROOT)).replace('\\','/'):sha(p) for p in files}
    with zipfile.ZipFile(target,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as z:
        for i,p in enumerate(files):
            z.write(p,arcname='SCCL_TPSC_Study/'+str(p.relative_to(ROOT)).replace('\\','/'))
            if i%60==0:print('PACKING',name,i,'/',len(files),flush=True)
        z.writestr('SCCL_TPSC_Study/manifest.json',json.dumps(manifest,indent=2))
    import hashlib
    with zipfile.ZipFile(target) as z:
        assert z.testzip() is None,'ZIP CRC failed'
        for relative,digest in manifest.items():
            with z.open('SCCL_TPSC_Study/'+relative) as stream:
                actual=hashlib.file_digest(stream,'sha256').hexdigest()
            assert actual==digest,relative
    receipt={'archive':str(target),'full_results_included':full,'payload_files':len(files),'bytes':target.stat().st_size,
             'sha256':sha(target),'zip_crc_passed':True,'all_payload_hashes_verified':True}
    print('VERIFIED ARCHIVE',receipt,flush=True)
    return receipt

if __name__=='__main__':
    native=create_archive(False);full=create_archive(True)
    write_json(ROOT/'results/package_verification.json',{'native':native,'full':full})
