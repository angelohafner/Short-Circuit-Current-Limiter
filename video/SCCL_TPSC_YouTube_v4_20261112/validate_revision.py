"""Verify the shorter closing sequence and preserve all engineering corrections."""
import ast
import hashlib
import json
from pathlib import Path
from datetime import datetime, timezone
import numpy as np
from data_access import Measurements
from render_video import SCENES

ROOT=Path(__file__).resolve().parent

def sha(path):
    with path.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def main():
    checks=[]
    def check(name,condition,detail=None):
        checks.append({'name':name,'passed':bool(condition),'detail':detail})
    script=json.loads((ROOT/'narration/script.json').read_text())
    manifest=json.loads((ROOT/'narration/narration_manifest.json').read_text())
    narration=json.loads((ROOT/'evidence/narration_validation.json').read_text())
    data_validation=json.loads((ROOT/'evidence/validation.json').read_text())
    check('Narration validation passes',narration['passed']==narration['total'])
    check('Data and media validation passes',data_validation['passed']==data_validation['total'])
    check('Narrated output is the validated file',sha(ROOT/'output/SCCL_TPSC_Narrated_EN.mp4')==manifest['video_sha256'])
    before=json.loads((ROOT/'evidence/previous_version_hashes.json').read_text())
    previous=Path(before['directory'])
    for name,expected in before['sha256'].items():
        check('Previous version preserved: '+name,sha(previous/name)==expected)
    for name in ['data/measurements.npz','data/metadata.json','data_access.py']:
        check('Unchanged electrical input/helper: '+name,sha(ROOT/name)==sha(previous/name))
    for name in ['SCCL_A_Without.pscx','SCCL_B_With.pscx','SCCL_C_Extended.pscx']:
        check('Unchanged native model: '+name,sha(ROOT/'pscad'/name)==sha(previous/'pscad'/name))
    for name,duration in SCENES:
        relative=Path('media/final/videos/scenes/1080p30')/(name+'.mp4')
        if name=='Recovery':
            check('Recovery freshly rendered',sha(ROOT/relative)!=sha(previous/relative))
        else:
            check('Unchanged source scene: '+name,sha(ROOT/relative)==sha(previous/relative))
    prior_script=json.loads((previous/'narration/script.json').read_text())
    prior_by_id={r['id']:r for r in prior_script['segments']}
    by_id={r['id']:r for r in script['segments']}
    for row in manifest['segments']:
        check('Manifest agrees with current text: '+row['id'],row['text']==by_id[row['id']]['text'])
        if row['id'] not in ['13_reclose','14_conclusion']:
            p=Path('narration/segments')/(row['id']+'.mp3')
            check('Original speech source retained: '+row['id'],sha(ROOT/p)==sha(previous/p))
            check('Original words retained: '+row['id'],row['text']==prior_by_id[row['id']]['text'])
    recovery_text=ast.parse((ROOT/'scenes.py').read_text(encoding='utf-8'))
    previous_tree=ast.parse((previous/'scenes.py').read_text(encoding='utf-8'))
    for name in ['NormalOperation','FaultTransfer','FaultComparison']:
        current=next(n for n in recovery_text.body if isinstance(n,ast.ClassDef) and n.name==name)
        former=next(n for n in previous_tree.body if isinstance(n,ast.ClassDef) and n.name==name)
        check('Reused scene source unchanged: '+name,ast.dump(current)==ast.dump(former))
    recovery=next(n for n in recovery_text.body if isinstance(n,ast.ClassDef) and n.name=='Recovery')
    strings=[n.value for n in ast.walk(recovery) if isinstance(n,ast.Constant) and isinstance(n.value,str)]
    check('A1 explicit RMS definition','One-cycle RMS across all three phases (includes DC)' in strings)
    check('A1 misleading old header removed',not any('Phase A traces' in s for s in strings))
    check('A1 phase-A voltage/current heading',any('Phase-A voltage/current' in s for s in strings))
    check('A1 RMS labels identify aggregate phases',sum('I_{1,\\mathrm{rms}}^{(3\\phi)}' in s for s in strings)==2)
    check('A1 narration includes DC','including D C' in by_id['10_clear']['text'])
    stages=next(ast.literal_eval(n.value) for n in ast.walk(recovery)
                if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='stages' for t in n.targets))
    chapter_start=sum(s for name,s in SCENES[:3])
    def video_time(electrical):
        elapsed=chapter_start+1.;previous_t=.49
        for target,duration in stages:
            if previous_t<=electrical<=target:
                return elapsed+(electrical-previous_t)/(target-previous_t)*duration
            elapsed+=duration;previous_t=target
        raise ValueError(electrical)
    data=Measurements();t=data.array('C','time')
    poles={p:float(t[np.flatnonzero((t>.58)&(data.array('C','BR'+p)>1.5))[0]]) for p in 'ABC'}
    video_poles={p:video_time(when) for p,when in poles.items()}
    cue=next(r for r in manifest['segments'] if r['id']=='10_clear')
    words=[json.loads(line) for line in (ROOT/'narration/segments/10_clear.words.jsonl').read_text().splitlines()]
    opens=next(w for w in words if w['text'].lower()=='opens')
    start=cue['start_s']+opens['offset']/1e7/cue['tempo_factor']
    end=cue['start_s']+(opens['offset']+opens['duration'])/1e7/cue['tempo_factor']
    check('A2 word opens spans all pole openings',start<=min(video_poles.values()) and end>=max(video_poles.values()))
    check('A2 word midpoint lies during physical opening',min(video_poles.values())<=(start+end)/2<=max(video_poles.values()))
    check('A2 no tempo adjustment to event-anchored cue',cue['tempo_factor']==1.)
    check('A3 unqualified small removed','small' not in by_id['13_reclose']['text'].lower())
    corrected_words=[json.loads(line)['text'].lower() for line in (ROOT/'narration/segments/13_reclose.words.jsonl').read_text().splitlines()]
    check('A3 synthesized words omit small','small' not in corrected_words and 'damped' in corrected_words and 'transient' in corrected_words)
    check('Approved four-chapter sequence',SCENES==[('NormalOperation',18),('FaultTransfer',26),('FaultComparison',28),('Recovery',30)])
    check('Standalone network opening removed',not any(isinstance(n,ast.ClassDef) and n.name=='NetworkOverview' for n in recovery_text.body))
    check('Sizing scene removed',not any(isinstance(n,ast.ClassDef) and n.name=='Sizing' for n in recovery_text.body))
    check('Sizing narration removed',not any(r['id'] in ['14_reactor','15_tuning'] for r in script['segments']))
    check('Brief network voice appears during comparison',by_id['01_network']['window']==[44.3,50.2])
    check('Network integrated into comparison','network=CompactFaultNetwork()' in (ROOT/'scenes.py').read_text())
    check('Duration is 102 seconds',script['duration_s']==sum(duration for name,duration in SCENES)==102)
    restored_at=chapter_start+1+sum(duration for target,duration in stages)
    conclusion=next(r for r in manifest['segments'] if r['id']=='14_conclusion')
    check('Four-second final restored-state hold',restored_at==98 and script['duration_s']-restored_at==4)
    check('Conclusion entirely within restored-state hold',restored_at<=conclusion['start_s']<conclusion['end_s']<=101.9)
    check('Conclusion confirms restoration',conclusion['text']=='Normal operation and capacitor compensation are restored.')
    check('Final native feeder poles closed',all(data.value('C','BR'+p,2.5)<.5 for p in 'ABC'))
    check('Final native fault removed',all(data.value('C','FS'+p,2.5)>1.5 for p in 'ABC'))
    check('Final native SCRs off',not data.conducting('C',2.5))
    check('Final native recovery ready',data.value('C','Recovery',2.5)>.5)
    check('Final native gate disabled',data.value('C','Gate',2.5)<.5)
    check('Final RMS settled',data.meta['extension']['last_window_sliding_rms_ripple_percent']<.2)
    closing_words=[json.loads(line) for line in (ROOT/'narration/segments/14_conclusion.words.jsonl').read_text().splitlines()]
    last_word=closing_words[-1]
    final_word_end=conclusion['start_s']+(last_word['offset']+last_word['duration'])/1e7/conclusion['tempo_factor']
    check('Closing word preserved before end',last_word['text'].lower().rstrip('.')=='restored' and final_word_end<102)
    result={'verified_utc':datetime.now(timezone.utc).isoformat(),'passed':sum(c['passed'] for c in checks),
            'total':len(checks),'checks':checks,'word_opens_video_s':[start,end],
            'pole_opening_electrical_s':poles,'pole_opening_video_s':video_poles,
            'fresh_scenes':['Recovery'],'reused_scenes':[name for name,duration in SCENES if name!='Recovery'],
            'resynthesized_segments':['13_reclose','14_conclusion'],'video_sha256':manifest['video_sha256'],
            'restored_state_hold_s':[restored_at,102],
            'conclusion_audio_s':[conclusion['start_s'],conclusion['end_s']],
            'closing_word_end_s':final_word_end,
            'new_electrical_simulation':False,'timing_method':'Provider word boundaries mapped through measured clip placement; verified against native breaker states and scene timing.'}
    (ROOT/'evidence/revision_validation.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'passed':result['passed'],'total':result['total'],'word_opens_video_s':[start,end],
                      'pole_opening_video_s':video_poles,'failed':[c for c in checks if not c['passed']]},indent=2))
    if result['passed']!=result['total']:raise SystemExit(1)

if __name__=='__main__':main()
