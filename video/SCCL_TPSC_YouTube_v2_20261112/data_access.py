"""Verified native measurements and honest sampling for animation."""
from pathlib import Path
import hashlib
import json
import numpy as np

ROOT = Path(__file__).resolve().parent

def sha256(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()

def verify_hash(path, expected):
    actual = sha256(path)
    if actual != expected:
        raise ValueError(f'Source hash mismatch: {path}')
    return actual

def sample(t, values, when, discrete=False):
    t, values = np.asarray(t), np.asarray(values)
    if when < t[0] or when > t[-1]:
        raise ValueError(f'Time {when} outside native interval [{t[0]}, {t[-1]}]')
    if discrete:
        return values[np.searchsorted(t, when, side='right') - 1].item()
    return float(np.interp(when, t, values))

def extrema_indices(values, budget=1400):
    """Keep every bin's min/max in temporal order; never smooth or rescale."""
    values = np.asarray(values)
    if len(values) <= budget:
        return np.arange(len(values))
    result = [0, len(values)-1]
    for group in np.array_split(np.arange(len(values)), max(1, (budget-2)//2)):
        result.extend([group[np.argmin(values[group])], group[np.argmax(values[group])]])
    return np.unique(result)

def first_state_time(t,values,target,*,after):
    """Locate an event within the requested scenario, excluding initialization."""
    t,values=np.asarray(t),np.asarray(values)
    hits=np.flatnonzero((t>=after)&(values==target))
    if not len(hits):raise ValueError('Requested native state was not reached in the event interval')
    return float(t[hits[0]])

class Measurements:
    def __init__(self):
        self.provenance = json.loads((ROOT/'data/provenance.json').read_text())
        for name, expected in self.provenance['compact_sha256'].items():
            verify_hash(ROOT/'data'/name, expected)
        self.meta = json.loads((ROOT/'data/metadata.json').read_text())
        # Inflate each immutable channel once. NpzFile access otherwise repeats
        # decompression on every animation frame.
        with np.load(ROOT/'data/measurements.npz', allow_pickle=False) as packed:
            self.data = {name:packed[name] for name in packed.files}

    def array(self, case, name):
        return self.data[f'{case}__{name}']

    def value(self, case, name, when):
        discrete = name in self.meta['discrete_channels'] or name.startswith(('TON', 'TOFF', 'SCR'))
        return sample(self.array(case, 'time'), self.array(case, name), when, discrete)

    def conducting(self, case, when, phase=None):
        phases = phase or 'ABC'
        return any(self.value(case, 'TON'+p+s, when) > self.value(case, 'TOFF'+p+s, when)
                   for p in phases for s in 'PN')
