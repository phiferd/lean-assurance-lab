"""Campaign-local construction and supervised runner; no shared tool changes."""
import copy
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from lib.lazy_reduction_pilot import classify, safe
from lib.metamorphic_pilot_runner import run_supervised
RUN = Path(__file__).parent
BINARY = ROOT / 'external/lazy-reduction-conformance-pilot-1/lazylean-r1'
ENV = dict(PATH='/usr/bin:/bin:/usr/sbin:/sbin', LANG='C', LC_ALL='C', LL_KAM_MODE='3')

def save(path, obj):
    with path.open('x') as f:
        f.write(json.dumps(obj, indent=2, sort_keys=True)+'\n')

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def run(attempt):
    out=RUN/attempt;out.mkdir(); rows=[]
    try:
        assert sha(BINARY)=='8132451a5a3c122fcae1d62cf5e7a8d4ca07ed2aa787675d305b399e6d5f6c0e'
        for fixture in json.loads((RUN/'inputs.json').read_text()):
            p=ROOT/fixture['path'];assert sha(p)==fixture['sha256']
            for profile in ['subst','kam']:
                i=len(rows)+1
                receipt=run_supervised(argv=[str(BINARY),'--engine',profile,'--jobs','1',str(p)],cwd=ROOT,stdin=None,env=ENV,timeout_seconds=30,memory_bytes=2147483648,raw_prefix=out/f'{i:02d}-{profile}')
                observation=classify(receipt,Path(receipt['raw_stdout_path']).read_bytes(),Path(receipt['raw_stderr_path']).read_bytes(),fixture['declarations'])
                row=dict(input=fixture,profile=profile,receipt=receipt,observation=observation);save(out/f'cell-{i:02d}.json',row);rows.append(row);safe(receipt)
        save(out/'result.json',rows)
        print(json.dumps([r['observation'] for r in rows],indent=2))
    except BaseException as error:
        save(out/'error.json',dict(error=repr(error),completed_cells=len(rows)));raise

if __name__=='__main__':
    run(sys.argv[1])
