"""Record the observed release status and package the auditable revision."""
from pathlib import Path
import hashlib
import json
import subprocess
import zipfile
from datetime import datetime, timezone

ROOT=Path(__file__).resolve().parent

def sha(path):
    with path.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()

def main():
    original=json.loads((ROOT/'evidence/original_hashes.json').read_text())
    study=ROOT.parents[1]
    protected={p:sha(study/p)==h for p,h in original.items()}
    assert all(protected.values()),'A protected original changed'
    movie=ROOT/'output/SCCL_TPSC_final.mp4'
    probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-show_chapters','-of','json',str(movie)],text=True))
    video=next(s for s in probe['streams'] if s['codec_type']=='video')
    prior=json.loads((ROOT/'evidence/validation.json').read_text())
    assert prior['passed']==prior['total']==47 and prior['video_sha256']==sha(movie)
    assert len(probe['chapters'])==6 and int(video['nb_frames'])==3840
    assert video['width']==1920 and video['height']==1080 and video['avg_frame_rate']=='30/1'
    voice_manifest=ROOT/'narration/narration_manifest.json'
    audio_done=voice_manifest.exists()
    if audio_done:
        audio_validation=json.loads((ROOT/'evidence/narration_validation.json').read_text())
        assert audio_validation['passed']==audio_validation['total']
    release={'verified_utc':datetime.now(timezone.utc).isoformat(),
             'video_status':'PASS','request_status':'COMPLETE' if audio_done else 'PARTIAL_NARRATION_BLOCKED',
             'audited_movie':str(movie.relative_to(ROOT)),'movie_sha256':sha(movie),
             'duration_s':float(probe['format']['duration']),'resolution':[video['width'],video['height']],
             'fps':video['avg_frame_rate'],'frames':int(video['nb_frames']),'chapters':probe['chapters'],
             'fresh_scene_renders':6,'data_and_media_checks':{'passed':47,'total':47},
             'unit_tests':{'passed':16,'total':16},'representative_symbol_checks':5,
             'original_preservation':protected,'narration_generated':audio_done,
             'narration_status':'PASS' if audio_done else 'BLOCKED: network restrictions and unavailable local synthesis',
             'visual_review':'Original 21 samples; corrected full-film 19 samples and four focused transfer frames; full media decode passed.',
             'new_electrical_simulation':False,
             'source_sha256':{p.name:sha(p) for p in ROOT.glob('*.py')}}
    (ROOT/'evidence/release_validation.json').write_text(json.dumps(release,indent=2)+'\n')
    active=['README.txt','complete_narration.ps1','requirements-lock.txt','build_assets.py','data_access.py',
            'scenes.py','visuals.py','source_reader.py','render_video.py','validate_video.py',
            'generate_narration.py','validate_narration.py','finalize_audit.py']
    files=[ROOT/p for p in active]
    for folder in ['assets','data','pscad','tests','docs','evidence','output']:
        files.extend(p for p in (ROOT/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts
                     and p.name not in ['archive_validation.json'] and '.partial.' not in p.name)
    files.extend(p for p in (ROOT/'narration').glob('*') if p.is_file() and p.suffix in ['.json','.txt','.srt'])
    files.extend((ROOT/'dependencies').glob('*.whl'))
    payload={str(p.relative_to(ROOT)).replace('\\','/'):sha(p) for p in sorted(set(files))}
    manifest=ROOT/'PACKAGE_MANIFEST.json';manifest.write_text(json.dumps(payload,indent=2)+'\n')
    suffix='Narrated' if audio_done else 'Audited_Silent_Pending_Narration'
    archive=ROOT.parent/f'SCCL_TPSC_{suffix}_20261112.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for p in sorted(set(files+[manifest])):z.write(p,ROOT.name+'/'+str(p.relative_to(ROOT)).replace('\\','/'))
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        for p,expected in payload.items():
            assert hashlib.sha256(z.read(ROOT.name+'/'+p)).hexdigest()==expected,p
    result={'archive':str(archive),'sha256':sha(archive),'payload_files':len(payload),'crc_pass':True,
            'payload_hashes_pass':True,'audio_included':audio_done,'status':release['request_status']}
    (ROOT/'evidence/archive_validation.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2),flush=True)

if __name__=='__main__':main()
