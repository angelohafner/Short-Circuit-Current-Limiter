"""Keep measurement processing after the network solution to align native channels."""
from common import ROOT,connect
app=connect(63579)
for name in ['SCCL_B_With','SCCL_C_Recovery']:
    p=app.project(name);definition=p.definition('SCCL_Protection')
    scripts=definition.script
    if 'Fortran' in scripts:
        scripts['Dsout']=scripts['Fortran'];del scripts['Fortran']
    p.parameters(threads=1)
    p.save();p.build()
    messages=p.messages();errors=[str(m) for m in messages if m.status=='error']
    (ROOT/'diagnostics'/(name+'_aligned_build.txt')).write_text('\n'.join(str(m) for m in messages))
    print(name,'ERRORS',errors,flush=True)
    assert not errors
