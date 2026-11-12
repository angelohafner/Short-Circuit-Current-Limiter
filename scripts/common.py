"""Shared configuration, connection and evidence helpers."""
from pathlib import Path
import hashlib
import json
import mhi.pscad

ROOT=Path(__file__).resolve().parents[1]
PARAM=json.loads((ROOT/'config/parameters.json').read_text())

def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream,'sha256').hexdigest()
def write_json(path,data):
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,indent=2,default=str),encoding='utf8')
def connect(port=63579):
    app=mhi.pscad.connect(port=port,timeout=15)
    assert app.licensed(),'A licensed PSCAD session is required for EMTDC execution'
    app.flags(silence=True)
    app.settings(fortran_version='GFortran 8.1 (64-bit)')
    return app
