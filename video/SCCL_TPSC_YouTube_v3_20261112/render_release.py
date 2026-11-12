"""Render all five scenes in isolated media directories, then assemble them."""
from concurrent.futures import ThreadPoolExecutor, as_completed
import os
import shutil
import subprocess
import sys
from render_video import ROOT, SCENES


def render_scene(name):
    media=ROOT/'media/renders'/name
    log=ROOT/'evidence'/f'render_final_{name}.log'
    env=dict(os.environ, OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1')
    with log.open('w',encoding='utf-8') as stream:
        subprocess.run([sys.executable,'-m','manim','render','--renderer','cairo',
                        '--resolution','1920,1080','--fps','30','--media_dir',str(media),
                        '--verbosity','WARNING','--progress_bar','none','--disable_caching',
                        str(ROOT/'scenes.py'),name],stdout=stream,stderr=subprocess.STDOUT,
                       cwd=ROOT,env=env,check=True)
    source=media/'videos/scenes/1080p30'/f'{name}.mp4'
    target=ROOT/'media/final/videos/scenes/1080p30'/source.name
    target.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(source,target)
    print('FRESH SCENE',name,flush=True)


if __name__=='__main__':
    # Manim 0.21 writes temporary files beside source SVGs. Serialize scenes
    # because those SVG assets are shared, even with separate media directories.
    with ThreadPoolExecutor(max_workers=1) as pool:
        jobs=[pool.submit(render_scene,name) for name,duration in SCENES]
        for job in as_completed(jobs):
            job.result()
    subprocess.run([sys.executable,str(ROOT/'render_video.py'),'--reuse'],cwd=ROOT,check=True)
