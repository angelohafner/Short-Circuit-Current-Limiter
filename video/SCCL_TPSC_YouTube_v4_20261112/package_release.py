"""Package the audited V4 release and verify every archived payload hash."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import struct
import zipfile
from PIL import Image

ROOT = Path(__file__).resolve().parent


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')


def main():
    video = ROOT / 'output/SCCL_TPSC_Narrated_EN.mp4'
    video_hash = sha(video)
    reports = {}
    for name in ['validation', 'narration_validation', 'revision_validation']:
        report = json.loads((ROOT / f'evidence/{name}.json').read_text())
        assert report['passed'] == report['total'], name
        reports[name] = {'passed': report['passed'], 'total': report['total']}
    revision = json.loads((ROOT / 'evidence/revision_validation.json').read_text())
    assert revision['video_sha256'] == video_hash
    manifest = json.loads((ROOT / 'narration/narration_manifest.json').read_text())
    assert manifest['video_sha256'] == video_hash
    review = json.loads((ROOT / 'evidence/visual_review.json').read_text())
    assert review['video_sha256'] == video_hash and review['passed']
    for frame in review['inspected_frames']:
        assert sha(ROOT / frame['path']) == frame['sha256']

    # Confirm the MP4 index precedes media data for progressive playback.
    atoms = []
    with video.open('rb') as stream:
        while stream.tell() < video.stat().st_size:
            start = stream.tell()
            size, kind = struct.unpack('>I4s', stream.read(8))
            if size == 1:
                size = struct.unpack('>Q', stream.read(8))[0]
            elif size == 0:
                size = video.stat().st_size - start
            assert size >= 8
            atoms.append(kind.decode('ascii'))
            stream.seek(start + size)
    assert atoms.index('moov') < atoms.index('mdat')
    thumbnail = ROOT / 'youtube/thumbnail_youtube_1280x720.jpg'
    with Image.open(thumbnail) as im:
        assert im.size == (1280, 720) and im.format == 'JPEG'
        im.verify()
    assert thumbnail.stat().st_size < 2_000_000
    for path in ['youtube/description_en.txt', 'youtube/tags_en.txt',
                 'narration/narration_en.srt']:
        assert (ROOT / path).stat().st_size > 0
    release = {
        'verified_utc': datetime.now(timezone.utc).isoformat(),
        'video': 'output/SCCL_TPSC_Narrated_EN.mp4',
        'video_sha256': video_hash,
        'duration_s': 102,
        'format': 'H.264 / yuv420p / 1920x1080 / 30 fps / AAC English',
        'faststart': True,
        'reports': reports,
        'visual_review': 'evidence/visual_review.json',
        'corrections': ['Sizing chapter removed',
                        'Final restored state held for closing English narration',
                        'Opening starts with normal operation',
                        'Compact network integrated into current comparison',
                        'Explicit three-phase RMS including DC',
                        'Opening speech aligned to recorded breaker events',
                        'Unqualified small removed from transient narration'],
        'word_opens_video_s': revision['word_opens_video_s'],
        'pole_opening_video_s': revision['pole_opening_video_s'],
        'restored_state_hold_s': revision['restored_state_hold_s'],
        'conclusion_audio_s': revision['conclusion_audio_s'],
        'closing_word_end_s': revision['closing_word_end_s'],
        'new_electrical_simulation': False,
        'previous_version_preserved': True,
    }
    write_json(ROOT / 'evidence/release_validation.json', release)

    def include(path):
        rel = path.relative_to(ROOT)
        if '__pycache__' in rel.parts:
            return False
        top = rel.parts[0]
        if top == 'dependencies':
            return path.suffix == '.whl'
        if top == 'pscad':
            return len(rel.parts) == 2 and path.suffix in {'.pscx', '.psmx'}
        if top == 'media':
            return path.parent == ROOT / 'media/final/videos/scenes/1080p30' and path.suffix == '.mp4'
        if top == 'output':
            return path.name in {'SCCL_TPSC_Narrated_EN.mp4', 'SCCL_TPSC_final.mp4',
                                 'SCCL_TPSC_Narration_EN.wav'}
        if top == 'narration':
            return path.suffix != '.wav'
        if top == 'evidence':
            return path.name not in {'archive_validation.json', 'package_manifest.json'}
        return top in {'assets', 'data', 'docs', 'tests', 'youtube'} or len(rel.parts) == 1

    paths = sorted(p for p in ROOT.rglob('*') if p.is_file() and include(p))
    inventory = {p.relative_to(ROOT).as_posix(): {'bytes': p.stat().st_size, 'sha256': sha(p)}
                 for p in paths}
    inventory_path = ROOT / 'evidence/package_manifest.json'
    write_json(inventory_path, {'files': inventory,
        'exclusions': ['Compiled PSCAD files and raw INF/OUT outputs',
                       'Installed Python packages and caches',
                       'Intermediate PCM narration files',
                       'Archive receipt (written after ZIP verification)']})
    archive = ROOT.with_suffix('.zip')
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as target:
        for path in paths + [inventory_path]:
            target.write(path, ROOT.name + '/' + path.relative_to(ROOT).as_posix())
    with zipfile.ZipFile(archive) as source:
        assert source.testzip() is None
        for relative, expected in inventory.items():
            with source.open(ROOT.name + '/' + relative) as stream:
                assert hashlib.file_digest(stream, 'sha256').hexdigest() == expected['sha256'], relative
    receipt = {'verified_utc': datetime.now(timezone.utc).isoformat(),
               'archive': archive.name, 'bytes': archive.stat().st_size,
               'sha256': sha(archive), 'crc_passed': True,
               'payload_hashes_verified': len(inventory),
               'video_sha256': video_hash}
    write_json(ROOT / 'evidence/archive_validation.json', receipt)
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    main()
