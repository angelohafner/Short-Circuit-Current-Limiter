"""Validate a genuinely synthesized narration; fail when no audio exists."""
from pathlib import Path
import hashlib
import json
import subprocess
import wave
import numpy as np

ROOT=Path(__file__).resolve().parent

def sha(path):
    with path.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()

def main():
    manifest=ROOT/'narration/narration_manifest.json'
    if not manifest.exists():
        raise SystemExit('BLOCKED: narration has not been generated. No narrated video can be certified.')
    receipt=json.loads(manifest.read_text());checks=[]
    def check(name,value,detail=None):checks.append(dict(name=name,passed=bool(value),detail=detail))
    source=ROOT/'output/SCCL_TPSC_final.mp4';target=ROOT/'output/SCCL_TPSC_Narrated_EN.mp4';audio=ROOT/'output/SCCL_TPSC_Narration_EN.wav'
    for key,path in [('video_sha256',target),('audio_sha256',audio),('silent_sha256',source),
                     ('script_sha256',ROOT/'narration/script.json'),('srt_sha256',ROOT/'narration/narration_en.srt')]:
        check('Hash '+key,sha(path)==receipt[key])
    p=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-show_chapters','-of','json',str(target)],text=True))
    v=next(s for s in p['streams'] if s['codec_type']=='video');a=next(s for s in p['streams'] if s['codec_type']=='audio')
    check('Full HD 30 fps H264',v['width']==1920 and v['height']==1080 and v['avg_frame_rate']=='30/1' and v['codec_name']=='h264')
    check('AAC English audio',a['codec_name']=='aac' and a['tags'].get('language')=='eng')
    check('120-second movie',abs(float(p['format']['duration'])-120)<.1)
    check('Five chapters',len(p['chapters'])==5)
    check('Reordered chapter starts',[round(float(c['start_time'])) for c in p['chapters']]==[0,18,44,72,102])
    check('Optional English captions',any(s['codec_type']=='subtitle' and s['tags'].get('language')=='eng' for s in p['streams']))
    decoded=subprocess.run(['ffmpeg','-v','error','-i',str(target),'-map','0:v:0','-map','0:a:0','-f','null','-'],capture_output=True,text=True)
    check('Full audiovisual decode',decoded.returncode==0 and not decoded.stderr,decoded.stderr)
    with wave.open(str(audio),'rb') as stream:
        check('Mono 48 kHz PCM',stream.getnchannels()==1 and stream.getframerate()==48000 and stream.getsampwidth()==2)
        samples=np.frombuffer(stream.readframes(stream.getnframes()),dtype=np.int16).astype(float)/32768
        check('120-second audio',abs(len(samples)/48000-120)<1/48000)
    check('Fifteen actual voice segments',len(receipt['segments'])==15)
    last_end=0
    for row in receipt['segments']:
        start,end=row['start_s'],row['end_s'];lo,hi=row['window']
        check(row['id']+' timing',lo<=start<end<=hi and start>=last_end)
        cut=samples[round(start*48000):round(end*48000)]
        check(row['id']+' audible signal',len(cut)>0 and np.sqrt(np.mean(cut**2))>.003)
        last_end=end
    measure=subprocess.run(['ffmpeg','-hide_banner','-i',str(target),'-af','loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json','-vn','-f','null','-'],capture_output=True,text=True,check=True)
    # FFmpeg may print progress and its mux summary after the loudnorm JSON.
    stats=json.JSONDecoder().raw_decode(measure.stderr[measure.stderr.rfind('{'):])[0]
    check('Integrated loudness',-18<float(stats['input_i'])<-14,stats['input_i'])
    check('No digital clipping',float(stats['input_tp'])<=-1,stats['input_tp'])
    result={'passed':sum(x['passed'] for x in checks),'total':len(checks),'checks':checks,'loudness':stats}
    (ROOT/'evidence/narration_validation.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
    if result['passed']!=result['total']:raise SystemExit(1)

if __name__=='__main__':main()
