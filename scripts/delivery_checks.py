"""Fail-closed completeness and provenance gates for the final engineering package."""
import json
from pathlib import Path
from common import ROOT,sha

def required_labels():
    labels={'without_sccl','with_sccl','recovery'}
    for angle in [0,45,90]:
        if angle:labels.add(f'baseline_angle_{angle}')
        for lm in [10,12,15.9,20,25]:
            if angle==0 and lm==15.9:continue
            labels.add(f'sensitivity/L_{lm:g}mH_angle_{angle}')
    labels.update(f'convergence/{c}_5us' for c in ['without_sccl','with_sccl','recovery'])
    labels.update(f'fixed_C/L_{lm}mH_C_442p5uF' for lm in [10,25])
    return labels

def require_run_index(index):
    missing=required_labels()-set(index)
    if missing:raise ValueError('Missing required native runs: '+', '.join(sorted(missing)))

def final_preflight(root=ROOT):
    index=json.loads((root/'results/selected_runs.json').read_text());require_run_index(index)
    validation=json.loads((root/'results/validation.json').read_text())
    assert not validation.get('partial_analysis',True),'Only a complete validation can authorize final packaging'
    assert validation['passed']==validation['total'] and validation['total']>0,'Numerical validation failed'
    assert validation['selected_run_index_sha256']==sha(root/'results/selected_runs.json'),'Validation uses a stale selected-run index'
    names={'without_sccl':'SCCL_A_Without','with_sccl':'SCCL_B_With','recovery':'SCCL_C_Recovery'}
    for label,relative in index.items():
        run=root/relative;r=json.loads((run/'run_receipt.json').read_text())
        assert r['fresh_outputs'] and not r['errors'],label
        assert sha(next(run.glob('*.pscx')))==r['project_sha256'],label+' snapshot changed'
        for file,digest in r['output_sha256'].items():assert sha(run/file)==digest,label+' native output changed: '+file
        if label in names:assert sha(root/'pscad'/(names[label]+'.pscx'))==r['project_sha256'],label+' canonical model differs from its accepted run'
    reopen=json.loads((root/'results/reopen_verification.json').read_text())
    assert reopen['project_count']==3 and reopen['relative_paths'] and reopen['unchanged_after_reopen']
    for filename,digest in reopen['project_hashes_by_name'].items():assert sha(root/'pscad'/filename)==digest
    assert sha(root/'pscad/SCCL_TPSC_Study.pswx')==reopen['workspace_sha256']
    portability=json.loads((root/'results/portability_receipt.json').read_text())
    assert portability['fresh_outputs'] and not portability['errors'] and portability['extracted_workspace_reopened']
    assert portability['model_sha256']==sha(root/'pscad/SCCL_B_With.pscx')
    folder=root/portability['relative_result_directory']
    for file,digest in portability['output_sha256'].items():assert sha(folder/file)==digest,'Portability evidence changed'
    return {'required_native_runs':len(required_labels()),'selected_native_runs':len(index),'checks_passed':validation['passed']}
