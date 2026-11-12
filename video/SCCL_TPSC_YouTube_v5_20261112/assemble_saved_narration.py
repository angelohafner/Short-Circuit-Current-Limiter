"""Reassemble this release from its saved source speech clips."""
import json
import generate_narration as g

if __name__ == '__main__':
    script=json.loads((g.ROOT/'narration/script.json').read_text(encoding='utf-8'))
    g.prepare(script)
    paths=[g.ROOT/'narration/segments'/(r['id']+'.mp3') for r in script['segments']]
    assert all(p.exists() and p.stat().st_size>1000 for p in paths)
    g.assemble(script,paths,{'engine':'edge-tts','version':'7.3.1','voice':script['voice'],
                            'rate':script['rate'],'pitch':script['pitch']})
