"""Render scenes, assemble chapters, and extract reproducible review frames."""
from pathlib import Path
import argparse
import json
import subprocess
import sys
from PIL import Image,ImageDraw
from data_access import ROOT, Measurements, sha256

SCENES=[('NormalOperation',18),('FaultTransfer',26),('FaultComparison',28),('Recovery',30)]
CHAPTER_TITLES={
    'NormalOperation':'Current limiter: normal operation',
    'FaultTransfer':'Fault response and thyristor bypass',
    'FaultComparison':'Two-source network and fault-current comparison',
    'Recovery':'Fault clearing, recovery and reclosure',
}

def call(args,**kwargs):
    return subprocess.run([str(a) for a in args],check=True,cwd=ROOT,**kwargs)

def probe(path):
    return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(path)],text=True))


def exact_scene_frames(path,seconds,fps):
    """Resolve at most two frames of Manim hold quantization before assembly."""
    path=Path(path);info=probe(path)
    stream=next(x for x in info['streams'] if x['codec_type']=='video')
    expected=round(seconds*fps);actual=int(stream['nb_frames'])
    if actual==expected:return path
    if abs(actual-expected)>2:
        raise ValueError(f'{path.name}: {actual} frames instead of {expected}; rerender the scene')
    target=path.with_name(path.stem+'_exact.mp4')
    call(['ffmpeg','-v','error','-y','-i',path,'-an','-vf',
          f'tpad=stop_mode=clone:stop_duration={2/fps:.9f}',
          '-frames:v',expected,'-r',fps,'-c:v','libx264','-crf','16',
          '-preset','medium','-pix_fmt','yuv420p','-movflags','+faststart',target])
    fitted=next(x for x in probe(target)['streams'] if x['codec_type']=='video')
    assert int(fitted['nb_frames'])==expected
    assert abs(float(fitted['duration'])-seconds)<1e-5
    return target

def frames(path,times,folder):
    folder.mkdir(parents=True,exist_ok=True)
    thumbs=[]
    for i,t in enumerate(times):
        output=folder/f'frame_{i:02}_{t:06.2f}s.png'
        call(['ffmpeg','-v','error','-y','-ss',t,'-i',path,'-frames:v','1',output])
        im=Image.open(output).convert('RGB');im.thumbnail((640,360))
        tile=Image.new('RGB',(640,390),'white');tile.paste(im,(0,0));ImageDraw.Draw(tile).text((12,367),f'Video time: {t:.2f} s',fill='black');thumbs.append(tile)
    sheet=Image.new('RGB',(1280,390*((len(thumbs)+1)//2)),'#E8EDF1')
    for i,im in enumerate(thumbs):sheet.paste(im,((i%2)*640,(i//2)*390))
    sheet.save(folder/'contact_sheet.jpg',quality=92)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--preview',action='store_true');parser.add_argument('--only',choices=[x[0] for x in SCENES]);parser.add_argument('--reuse',action='store_true')
    args=parser.parse_args();Measurements()
    mode='preview' if args.preview else 'final';resolution='854,480' if args.preview else '1920,1080';fps=15 if args.preview else 30
    chosen=[x for x in SCENES if not args.only or x[0]==args.only]
    media=ROOT/'media'/mode;outputs=[]
    (ROOT/'output').mkdir(exist_ok=True);(ROOT/'evidence').mkdir(exist_ok=True)
    for name,seconds in chosen:
        path=media/f'videos/scenes/{480 if args.preview else 1080}p{fps}/{name}.mp4'
        if not (args.reuse and path.exists()):
            log=ROOT/'evidence'/f'render_{mode}_{name}.log'
            with log.open('w',encoding='utf-8') as stream:
                call([sys.executable,'-m','manim','render','--renderer','cairo','--resolution',resolution,'--fps',fps,
                      '--media_dir',media,'--verbosity','WARNING','--progress_bar','none','--disable_caching',ROOT/'scenes.py',name],stdout=stream,stderr=subprocess.STDOUT)
        path=exact_scene_frames(path,seconds,fps)
        p=probe(path);assert abs(float(p['format']['duration'])-seconds)<.00001
        outputs.append(path);print(f'RENDERED {mode} {name}: {seconds} seconds',flush=True)
    if args.only:
        target=ROOT/'output'/f'{args.only}_{mode}.mp4'
        import shutil;shutil.copy2(outputs[0],target)
        times=[1,7.8,9.8,10.8,13.3,18,24.5] if args.only=='FaultTransfer' else [2,chosen[0][1]*.7]
    else:
        concat=ROOT/'evidence'/f'concat_{mode}.txt'
        concat.write_text('\n'.join("file '"+str(p).replace('\\','/').replace("'","'\\''")+"'" for p in outputs),encoding='utf-8')
        chapters=';FFMETADATA1\ntitle=TPSC Short-Circuit Current Limiter\n';start=0
        for name,seconds in SCENES:
            chapters+=f'[CHAPTER]\nTIMEBASE=1/1000\nSTART={start*1000}\nEND={(start+seconds)*1000}\ntitle={CHAPTER_TITLES[name]}\n';start+=seconds
        chapterfile=ROOT/'evidence/chapters.txt';chapterfile.write_text(chapters)
        target=ROOT/'output'/f'SCCL_TPSC_{mode}.mp4'
        call(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',concat,'-i',chapterfile,'-map_metadata','1','-map_chapters','1','-c','copy','-movflags','+faststart',target])
        times=[0,3,11,20,27.8,28.8,31.3,41,45,51,60,69,77,80,84,88,93,96,98,100,101.9]
    frames(target,times,ROOT/'evidence'/f'frames_{target.stem}')
    (ROOT/'evidence'/f'{target.stem}_media.json').write_text(json.dumps({'sha256':sha256(target),'probe':probe(target)},indent=2)+'\n')
    print(f'DELIVERABLE {target}',flush=True)

if __name__=='__main__':main()
