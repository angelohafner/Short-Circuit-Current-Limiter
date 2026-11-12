"""Numerical analysis of native PSCAD output; never generates study waveforms."""
from pathlib import Path
import re
import numpy as np

def fit_phasor(t, x, frequency=60.0, tau=None):
    """Least-squares RMS phasor with constant and optional decaying DC term."""
    t=np.asarray(t); x=np.asarray(x)
    columns=[np.sqrt(2)*np.cos(2*np.pi*frequency*t),-np.sqrt(2)*np.sin(2*np.pi*frequency*t),np.ones_like(t)]
    if tau is not None:
        for decay in np.atleast_1d(tau):columns.append(np.exp(-(t-t[0])/decay))
    coefficients=np.linalg.lstsq(np.column_stack(columns),x,rcond=None)[0]
    return coefficients[0]+1j*coefficients[1]

def fault_reference(voltage_phase_kV, source_Z, device_Z, fault_Z):
    """Solve the common fault-bus voltage and add complex source currents."""
    y1=1/(source_Z+device_Z); y2=1/source_Z
    v=voltage_phase_kV*(y1+y2)/(y1+y2+1/fault_Z)
    i1=(voltage_phase_kV-v)*y1; i2=(voltage_phase_kV-v)*y2
    return dict(source1=i1,source2=i2,total=i1+i2,bus_voltage=v)

def read_outputs(folder):
    """Map PGB indices explicitly to 10-channel OUT blocks and verify time axes."""
    folder=Path(folder)
    infs=list(folder.glob('*.inf'))
    if len(infs)!=1: raise FileNotFoundError(f'Expected one INF in {folder}, found {len(infs)}')
    rows=re.findall(r'PGB\((\d+)\).*?Desc="([^"]+)"',infs[0].read_text())
    if not rows: raise ValueError('No indexed native channels')
    arrays={}; result={}; time=None
    for number,name in rows:
        index=int(number); block=(index-1)//10+1; col=(index-1)%10+1
        if block not in arrays:
            file=infs[0].with_name(f'{infs[0].stem}_{block:02}.out')
            a=np.loadtxt(file,skiprows=1)
            if time is None: time=a[:,0]
            if not np.array_equal(time,a[:,0]): raise ValueError('Native output time axes differ')
            arrays[block]=a
        if name in result: raise ValueError(f'Duplicate channel {name}')
        result[name]=arrays[block][:,col]
    if not np.all(np.diff(time)>0): raise ValueError('Output time is not strictly increasing')
    if not all(np.isfinite(a).all() for a in arrays.values()): raise ValueError('Non-finite native output')
    return time,result
