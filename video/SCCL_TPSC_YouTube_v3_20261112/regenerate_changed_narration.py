"""Synthesize the three editorially changed cues; preserve the other twelve."""
import asyncio
import json
import generate_narration as g

if __name__ == '__main__':
    script=json.loads((g.ROOT/'narration/script.json').read_text(encoding='utf-8'))
    script['segments']=[r for r in script['segments'] if r['id'] in ['02_series','06_transfer','01_network']]
    asyncio.run(g.edge_synthesis(script,g.ROOT/'narration/segments'))
