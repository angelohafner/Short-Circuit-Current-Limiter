"""Make the recovery case by a native Save As of the validated SCCL circuit."""
from pathlib import Path
from common import ROOT,PARAM,connect
app=connect(63579);p=app.project('SCCL_B_With');p.save()
target=ROOT/'pscad/SCCL_C_Recovery.pscx'
assert not target.exists(),'Preserve the existing recovery project'
p=p.save_as(str(target));c=p.canvas('Main')
for key,value in [('OpenTime',PARAM['recovery_open_s']),('RemoveTime',PARAM['recovery_fault_remove_s']),('CloseTime',PARAM['reclosure_s'])]:
    c.find('master:const',Name=key).parameters(Value=value)
p.parameters(output_filename='SCCL_C_Recovery.out',threads=1,description='138 kV TPSC SCCL; five-cycle breaker trip and healthy-feeder reclosure')
p.save();app.load(str(ROOT/'pscad/SCCL_B_With.pscx'))
print('CREATED',target,flush=True)
