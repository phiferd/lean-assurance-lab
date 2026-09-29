#!/usr/bin/env python3
"""One E0 trial; reuse retained classification and supervision, no shared edits."""
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
PRIOR = ROOT / 'explorations/runs/EXPLORE-LAZYLEAN-SEMANTIC-EXTENSION-1'
ENV = {'PATH': '/usr/bin:/bin:/usr/sbin:/sbin', 'LANG': 'C', 'LC_ALL': 'C', 'LL_KAM_MODE': '3'}

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def save(p, value):
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open('x') as f:
        json.dump(value, f, indent=2, sort_keys=True)
        f.write('\n')

def prepare():
    old = [json.loads(x) for x in (PRIOR / 'iota-candidate.ndjson').read_text().splitlines()]
    inventory = []
    for depth in (1, 4):
        rows = copy.deepcopy(old[:-2])
        previous = 5  # True.intro
        for i in range(depth):
            name, expr = 9+i, 18+i
            rows += [{'in': name, 'str': {'pre': 0, 'str': f'LAL_alias_{i}'}},
                     {'def': {'all': [name], 'hints': 'abbrev', 'levelParams': [], 'name': name,
                              'safety': 'safe', 'type': 1, 'value': previous}},
                     {'ie': expr, 'const': {'name': name, 'us': []}}]
            previous = expr
        rec_expr = 18+depth
        rows.append({'ie': rec_expr, 'app': {'fn': 17, 'arg': previous}})
        for role in ('control', 'candidate'):
            final = copy.deepcopy(old[-1])
            final['def']['type'] = 1 if role == 'control' else rec_expr
            path = RUN / f'depth-{depth}-{role}.ndjson'
            with path.open('x') as f:
                for row in rows+[final]:
                    f.write(json.dumps(row, sort_keys=True, separators=(',', ':'))+'\n')
            inventory.append({'path': str(path.relative_to(ROOT)), 'sha256': sha(path),
                              'depth': depth, 'role': role, 'declarations': depth+2})
    save(RUN / 'inputs.json', inventory)

def summarize(rows):
    answers = {}
    for depth in (1, 4):
        selected = [r for r in rows if r['depth'] == depth]
        controls = all(r['observation']['verdict']=='ACCEPT' for r in selected if r['role']=='control')
        candidates = {r['profile']: r['observation'] for r in selected if r['role']=='candidate'}
        verdicts = {k: v['verdict'] for k,v in candidates.items()}
        machine = candidates['kam'].get('machine', {})
        demand = all(machine.get(k,0)>0 for k in ('delta','iota'))
        recognized = all(v in ('ACCEPT', 'SEMANTIC_REJECTION_OTHER', 'INTENDED_REJECT') for v in verdicts.values())
        # Rejections do not emit complete counters: retain as a candidate for
        # diagnostic review, never silently promote it to confirmation.
        difference = recognized and ('ACCEPT' in verdicts.values()) and len(set(verdicts.values()))>1
        outcome = 'SIGNAL' if controls and difference else 'NO_SIGNAL' if controls and demand and set(verdicts.values())=={'ACCEPT'} else 'INCONCLUSIVE'
        answers[str(depth)] = dict(outcome=outcome, controls_accept=controls,
                                  verdicts=verdicts, kam_machine=machine, demand_observed=demand)
    return answers

def run(attempt):
    output = RUN / attempt
    output.mkdir(exist_ok=False)
    rows = []
    try:
        assert sha(BINARY)=='8132451a5a3c122fcae1d62cf5e7a8d4ca07ed2aa787675d305b399e6d5f6c0e'
        inventory = json.loads((RUN / 'inputs.json').read_text())
        for fixture in inventory:
            path = ROOT / fixture['path']
            assert sha(path)==fixture['sha256']
            for profile in ('subst', 'kam'):
                index = len(rows)+1
                receipt = run_supervised(argv=[str(BINARY),'--engine',profile,'--jobs','1',str(path)],
                    cwd=ROOT, stdin=None, env=ENV, timeout_seconds=30, memory_bytes=2147483648,
                    raw_prefix=output/f'{index:02d}-{profile}')
                observation = classify(receipt, Path(receipt['raw_stdout_path']).read_bytes(),
                    Path(receipt['raw_stderr_path']).read_bytes(), fixture['declarations'])
                row = dict(depth=fixture['depth'],role=fixture['role'],profile=profile,input=fixture,
                           receipt=receipt,observation=observation)
                save(output/f'cell-{index:02d}.json', row)
                rows.append(row)
                safe(receipt)  # pause immediately on control/accounting failure
                assert sha(path)==fixture['sha256']
        result = summarize(rows)
        save(output/'result.json', result)
        print(json.dumps(result, indent=2))
    except BaseException as error:
        save(output/'error.json', dict(error=repr(error),completed_cells=len(rows)))
        raise

if __name__=='__main__':
    if sys.argv[1]=='--prepare': prepare()
    else: run(sys.argv[1])
