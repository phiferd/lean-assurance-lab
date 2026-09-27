"""Fresh-process exact matrix execution; no case selection after observation."""
from datetime import datetime, timezone
from pathlib import Path
import argparse
import json
from lib import lazy_reduction_pilot as p
from lib.acceptance_impact_pair import CONTROL, CANDIDATE

REJECTION="FAIL LALNest (line 105): recursor 'LALNest.rec_1': exported type differs from the derived type"

CAPABILITY_CELLS=[dict(cell_id=f'{engine}::{name}',engine=engine,artifact_id=name,
                      declarations=2,expected='ACCEPT' if name=='control' else 'INTENDED_REJECT')
                 for engine in ['subst','kam'] for name in ['control','candidate']]

def validate_capability(m):
    if m['item_id']!=p.ITEM or m['stage']!='CAPABILITY' or m['cells']!=CAPABILITY_CELLS:
        raise ValueError('capability fixed matrix differs')
    if m['artifacts']!={'control':CONTROL,'candidate':CANDIDATE}:
        raise ValueError('capability fixtures differ')
    if (m['environment']!={**p.ENV,'LL_KAM_MODE':'3'} or m['exact_rejection']!=REJECTION
        or m['keep_going'] is not False or m['jobs']!=1 or m['launch_owner']!='lazy_lead'
        or m['timeout_seconds']!=120 or m['memory_bytes']!=2147483648):
        raise ValueError('capability controls differ')

def execution_tooling():
    return [*p.tooling(),p.bind(Path('lib/lazy_reduction_execute.py')),
            p.bind(Path('scripts/execute-lazy-reduction-pilot')),p.bind(Path('tests/test_lazy_reduction_execute.py'))]

def freeze_capability(build_result=p.BASE/'build-0001/result.json'):
    p.active()
    build=p.load(build_result)
    p.safe(build['receipt']); p.raw(build['receipt']); p.verify(build['binary'])
    artifacts={'control':CONTROL,'candidate':CANDIDATE}
    for row in artifacts.values(): p.verify(row)
    value=dict(item_id=p.ITEM,stage='CAPABILITY',binary=build['binary'],
               build_result=p.bind(build_result),artifacts=artifacts,
               tooling=execution_tooling(),source=p.bind(p.BASE/'source-r1.json'),
               environment={**p.ENV,'LL_KAM_MODE':'3'},timeout_seconds=120,memory_bytes=2147483648,
               cells=CAPABILITY_CELLS,
               exact_rejection=REJECTION,launch_owner='lazy_lead',keep_going=False,jobs=1,
               input_scope='Existing recursor capability pair only; no positive intake fixture launch.')
    validate_capability(value)
    p.write_new(p.BASE/'capability-manifest-r1.json',value)
    return value

def execute(manifest_path,attempt):
    p.active(); m=p.load(manifest_path)
    validate_capability(m)
    p.require_committed([p.bind(manifest_path),*m['tooling'],m['build_result'],m['source'],*m['artifacts'].values()])
    p.verify(m['binary'])
    out=p.BASE/attempt
    if (p.ROOT/out).exists(): raise ValueError('attempt directory exists')
    (p.ROOT/out).mkdir()
    results=[]
    for index,cell in enumerate(m['cells']):
        p.verify(m['binary']); artifact=p.verify(m['artifacts'][cell['artifact_id']])
        stamp=datetime.now(timezone.utc).isoformat()
        receipt=p.run_supervised(argv=[str(p.ROOT/m['binary']['path']),'--engine',cell['engine'],'--jobs','1',str(artifact)],
                  cwd=p.ROOT,stdin=None,env=m['environment'],timeout_seconds=m['timeout_seconds'],memory_bytes=m['memory_bytes'],
                  raw_prefix=p.ROOT/out/f'{index+1:02d}-{cell["engine"]}-{cell["artifact_id"]}')
        stdout,stderr=p.raw(receipt)
        result=dict(cell=cell,started_at=stamp,finished_at=datetime.now(timezone.utc).isoformat(),
                    input_before=m['artifacts'][cell['artifact_id']],input_after=p.bind(artifact),receipt=receipt,
                    observation=p.classify(receipt,stdout,stderr,cell['declarations'],m.get('exact_rejection')))
        p.write_new(out/f'cell-{index+1:02d}.json',result); results.append(result)
        if result['input_after']!=result['input_before']: raise ValueError('input custody changed')
        p.verify(m['binary'])
        # A semantic capability mismatch is a real gate result; process/parser faults pause.
        p.safe(receipt)
        if result['observation']['verdict'] in {'PARSER_FAILURE','OUTPUT_CONTRACT_FAILURE','PROCESS_FAILURE'}:
            raise ValueError('adapter/process incident preserved; diagnose before further cells')
    value=dict(item_id=p.ITEM,manifest=p.bind(manifest_path),cells=results,
               acceptance_matched=all(x['observation']['verdict']==x['cell']['expected'] for x in results),
               actual_process_count=len(results),elapsed_seconds=sum(x['receipt']['elapsed_seconds'] for x in results))
    p.write_new(out/'result.json',value)
    return value

def main():
    parser=argparse.ArgumentParser(); parser.add_argument('command',choices=['freeze-capability','execute']);
    parser.add_argument('--manifest',default=str(p.BASE/'capability-manifest-r1.json')); parser.add_argument('--attempt',default='capability-0001')
    parser.add_argument('--build-result',default=str(p.BASE/'build-0001/result.json'))
    args=parser.parse_args()
    value=freeze_capability(Path(args.build_result)) if args.command=='freeze-capability' else execute(Path(args.manifest),args.attempt)
    print(json.dumps(value,indent=2))

if __name__=='__main__': main()
