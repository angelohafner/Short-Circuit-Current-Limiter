"""Create and reopen the relative workspace and render actual native schematics/graphs."""
from pathlib import Path
import argparse
import xml.etree.ElementTree as ET
from PIL import ImageGrab
from common import ROOT,connect,write_json,sha

ap=argparse.ArgumentParser();ap.add_argument('--port',type=int,default=63579);a=ap.parse_args()
app=connect(a.port)
names=['SCCL_A_Without','SCCL_B_With','SCCL_C_Recovery']
paths=[ROOT/'pscad'/(n+'.pscx') for n in names]
protected={str(p):sha(p) for p in paths}
workspace=ROOT/'pscad/SCCL_TPSC_Study.pswx'
# This dedicated session was launched for the study. Do not save restored projects.
app.new_workspace(str(workspace))
app.load(*(str(p) for p in paths))
app.save_workspace(str(workspace),save_projects=False)
text=workspace.read_text(encoding='utf8')
print('WORKSPACE',text,flush=True)
assert all(str(ROOT).lower() not in text.lower() for _ in [0]),'Workspace contains an absolute study path'
app.load(str(workspace))
loaded=[p['name'] for p in app.projects() if p['type']=='Case']
assert sorted(loaded)==sorted(names),(loaded,names)
assert all(sha(Path(p))==h for p,h in protected.items()),'Reopening changed a protected project file'
write_json(ROOT/'results/reopen_verification.json',{'workspace':str(workspace),'project_names':loaded,
           'workspace_sha256':sha(workspace),'project_hashes_by_name':{p.name:sha(p) for p in paths},
           'project_count':len(loaded),'relative_paths':True,'opened_and_reopened_in_pscad':True,'protected_project_hashes':protected,'unchanged_after_reopen':True})
out=ROOT/'results/native_views';out.mkdir(exist_ok=True)
for name in names:
    p=app.project(name);c=p.canvas('Main');p.focus()
    print('REFRESH NATIVE GRAPHS',name,flush=True)
    p.run()
    assert not [m for m in p.messages() if m.status=='error'],'Native graph refresh run failed'
    # These operations change only the live view; do not rewrite the source-bound files.
    from configure_graphs import configure
    configure(p)
    for suffix,rect in [('Network',(0,0,258,251)),('Phase_A',(55,19,225,89)),('Protection',(0,256,85,334)),('Graphs',(96,258,259,379))]:
        c.select_components(*rect);assert c.copy(),'Native canvas rendering failed'
        picture=ImageGrab.grabclipboard();assert hasattr(picture,'save'),'No native rendered image'
        picture.save(out/(name+'_'+suffix+'.png'));c.clear_selection()
        print('NATIVE VIEW',name,suffix,picture.size,flush=True)
assert all(sha(Path(p))==h for p,h in protected.items())
app.project('SCCL_B_With').focus()
