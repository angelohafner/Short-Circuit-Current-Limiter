"""Synthesize event-aligned English narration, then mux the audited silent master.

No registry or machine settings are modified. Failed synthesis never produces a
file claiming to be the narrated deliverable. --prepare-only is offline.
"""
from pathlib import Path
import argparse
import asyncio
import hashlib
import json
import re
import subprocess
import sys
import textwrap
import wave
from xml.sax.saxutils import escape

ROOT=Path(__file__).resolve().parent
RATE=48000


def call(args,**kwargs):
    return subprocess.run([str(x) for x in args],check=True,**kwargs)


def sha(path):
    with Path(path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()


def place_segment(start,end,duration):
    if not (0<=start<end and 0<duration<=end-start):
        raise ValueError(f'Audio duration {duration:.3f} exceeds or invalidates window [{start}, {end}]')
    offset=start+(end-start-duration)/2
    return offset,offset+duration


def stamp(seconds):
    milliseconds=round(seconds*1000)
    hours,milliseconds=divmod(milliseconds,3600000)
    minutes,milliseconds=divmod(milliseconds,60000)
    seconds,milliseconds=divmod(milliseconds,1000)
    return f'{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}'


def write_srt(rows,path):
    path.write_text('\n\n'.join(f'{i}\n{stamp(r["start_s"])} --> {stamp(r["end_s"])}\n'
                     +textwrap.fill(r['text'],width=68) for i,r in enumerate(rows,1))+'\n',encoding='utf-8')


def prepare(script):
    (ROOT/'narration').mkdir(exist_ok=True)
    (ROOT/'narration/narration_en.txt').write_text('\n\n'.join(
        f'{r["id"]} | {r["window"][0]:.1f}-{r["window"][1]:.1f} s\n{r["text"]}'
        for r in script['segments'])+'\n',encoding='utf-8')
    write_srt([dict(start_s=r['window'][0],end_s=r['window'][1],text=r['text'])
               for r in script['segments']],ROOT/'narration/narration_planned.srt')


async def edge_synthesis(script,folder):
    sys.path.insert(0,str(ROOT/'dependencies/tts'))
    import edge_tts
    paths=[]
    for row in script['segments']:
        path=folder/(row['id']+'.mp3')
        await edge_tts.Communicate(row['text'],script['voice'],rate=script['rate'],pitch=script['pitch'],
                                  boundary='WordBoundary').save(str(path),str(path.with_suffix('.words.jsonl')))
        paths.append(path)
        print('SYNTHESIZED',row['id'],flush=True)
    return paths,{'engine':'edge-tts','version':edge_tts.__version__,'voice':script['voice'],
                  'rate':script['rate'],'pitch':script['pitch']}


def sapi_synthesis(script,folder):
    import win32com.client
    voice=win32com.client.Dispatch('SAPI.SpVoice');tokens=voice.GetVoices()
    choices=[tokens.Item(i) for i in range(tokens.Count) if 'DAVID' in tokens.Item(i).Id.upper()]
    if not choices:raise RuntimeError('The required American male David voice is not available.')
    voice.Voice=choices[0];voice.Rate=0;voice.Volume=95
    paths=[]
    for row in script['segments']:
        path=folder/(row['id']+'.wav')
        stream=win32com.client.Dispatch('SAPI.SpFileStream');stream.Open(str(path),3,False)
        voice.AudioOutputStream=stream
        try:
            voice.Speak('<pitch absmiddle="2">'+escape(row['text'])+'</pitch>',8)
        finally:stream.Close()
        paths.append(path);print('SYNTHESIZED',row['id'],flush=True)
    return paths,{'engine':'Windows SAPI','voice':voice.Voice.GetDescription(),'rate':0,'pitch':2}


def pcm(path):
    with wave.open(str(path),'rb') as stream:
        assert (stream.getnchannels(),stream.getsampwidth(),stream.getframerate())==(1,2,RATE)
        data=stream.readframes(stream.getnframes())
    return data,len(data)/(RATE*2)


def assemble(script,paths,engine):
    track=bytearray(round(script['duration_s']*RATE)*2);rows=[]
    for row,path in zip(script['segments'],paths,strict=True):
        normalized=ROOT/'narration/segments'/(row['id']+'_pcm.wav')
        call(['ffmpeg','-v','error','-y','-i',path,'-ac','1','-ar',RATE,'-c:a','pcm_s16le',normalized])
        data,duration=pcm(normalized);available=row['window'][1]-row['window'][0]
        factor=1.0
        if duration>available:
            factor=duration/(available-.15)
            if factor>1.15:raise ValueError(f'{row["id"]}: narration exceeds window; shorten this cue ({duration:.2f}s / {available:.2f}s).')
            call(['ffmpeg','-v','error','-y','-i',path,'-af',f'atempo={factor:.8f}',
                  '-ac','1','-ar',RATE,'-c:a','pcm_s16le',normalized])
            data,duration=pcm(normalized)
        if duration<.3 or len(set(data))<10:raise ValueError(f'{path}: empty or invalid synthesized audio')
        start,end=place_segment(*row['window'],duration)
        index=round(start*RATE)*2;stop=index+len(data)
        if stop>len(track):raise ValueError('Narration exceeds movie timeline')
        track[index:stop]=data
        rows.append(dict(id=row['id'],text=row['text'],window=row['window'],start_s=start,end_s=end,
                         duration_s=duration,tempo_factor=factor,source_sha256=sha(path)))
    raw=ROOT/'narration/narration_raw.wav'
    with wave.open(str(raw),'wb') as stream:
        stream.setnchannels(1);stream.setsampwidth(2);stream.setframerate(RATE);stream.writeframes(track)
    scan=subprocess.run(['ffmpeg','-hide_banner','-i',str(raw),'-af',
            'loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json','-f','null','-'],capture_output=True,text=True,check=True)
    # FFmpeg may print progress and its mux summary after the loudnorm JSON.
    stats=json.JSONDecoder().raw_decode(scan.stderr[scan.stderr.rfind('{'):])[0]
    loudness=(f'loudnorm=I=-16:TP=-1.5:LRA=11:measured_I={stats["input_i"]}:'
              f'measured_TP={stats["input_tp"]}:measured_LRA={stats["input_lra"]}:'
              f'measured_thresh={stats["input_thresh"]}:offset={stats["target_offset"]}:linear=true')
    audio=ROOT/'output/SCCL_TPSC_Narration_EN.wav'
    call(['ffmpeg','-v','error','-y','-i',raw,'-af',loudness,'-ar',RATE,'-ac','1','-c:a','pcm_s16le',audio])
    subtitles=ROOT/'narration/narration_en.srt';write_srt(rows,subtitles)
    source=ROOT/'output/SCCL_TPSC_final.mp4'
    pending=ROOT/'output/SCCL_TPSC_Narrated_EN.partial.mp4'
    target=ROOT/'output/SCCL_TPSC_Narrated_EN.mp4'
    call(['ffmpeg','-v','error','-y','-i',source,'-i',audio,'-i',subtitles,
          '-map','0:v:0','-map','1:a:0','-map','2:s:0','-map_chapters','0','-map_metadata','0',
          '-c:v','copy','-c:a','aac','-b:a','192k','-c:s','mov_text','-disposition:s:0','0',
          '-metadata:s:a:0','language=eng','-metadata:s:s:0','language=eng',
          '-metadata','title=TPSC Short-Circuit Current Limiter - Audited English Narration',
          '-t',script['duration_s'],'-movflags','+faststart',pending])
    call(['ffmpeg','-v','error','-i',pending,'-map','0:v:0','-map','0:a:0','-f','null','-'])
    pending.replace(target)
    manifest={'status':'GENERATED','engine':engine,'duration_s':script['duration_s'],'segments':rows,
              'audio_sha256':sha(audio),'video_sha256':sha(target),'silent_sha256':sha(source),
              'script_sha256':sha(ROOT/'narration/script.json'),'srt_sha256':sha(subtitles),
              'normalization_input':stats,'subtitle_timing':'Measured audio segment bounds; optional segment captions.'}
    (ROOT/'narration/narration_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    print('DELIVERABLE',target,flush=True)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--engine',choices=['edge','sapi'],default='edge')
    parser.add_argument('--prepare-only',action='store_true')
    args=parser.parse_args()
    script=json.loads((ROOT/'narration/script.json').read_text(encoding='utf-8'));prepare(script)
    if args.prepare_only:
        print('Prepared English script and planned subtitle windows. No audio was synthesized.');return
    folder=ROOT/'narration/segments';folder.mkdir(exist_ok=True)
    try:
        paths,engine=asyncio.run(edge_synthesis(script,folder)) if args.engine=='edge' else sapi_synthesis(script,folder)
        assemble(script,paths,engine)
    except Exception as exc:
        (ROOT/'evidence/narration_attempt.json').write_text(json.dumps({'status':'FAILED',
            'engine':args.engine,'error':str(exc),'script_sha256':sha(ROOT/'narration/script.json')},indent=2)+'\n')
        raise


if __name__=='__main__':main()
