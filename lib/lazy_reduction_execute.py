"""Fresh-process exact matrix execution; no case selection after observation."""
from datetime import datetime, timezone
from pathlib import Path
import argparse
import json
from lib import lazy_reduction_pilot as p
from lib.acceptance_impact_pair import CONTROL, CANDIDATE

REJECTION="FAIL LALNest (line 105): recursor 'LALNest.rec_1': exported type differs from the derived type"

def execution_tooling():
    return [*p.tooling(),p.bind(Path('lib/lazy_reduction_execute.py')),
            p.bind(Path('scripts/execute-lazy-reduction-pilot'))]

def freeze_capability():
    p.active()
    build=p.load(p.BASE/'build-0001/result.json')
    p.safe(build['receipt']); p.raw(build['receipt']); p.verify(build['binary'])
    artifacts={'control':CONTROL,'candidate':CANDIDATE}
    for row in artifacts.values(): p.verify(row)
    value=dict(item_id=p.ITEM,stage='CAPABILITY',binary=build['binary'],
               build_result=p.bind(p.BASE/'build-0001/result.json'),artifacts=artifacts,
               tooling=execution_tooling(),source=p.bind(p.BASE/'source-r1.json'),
               environment={**p.ENV,'LL_KAM_MODE':'3'},timeout_seconds=120,memory_bytes=2147483648,
               cells=[dict(cell_id=f'{engine}::{name}',engine=engine,artifact_id=name,
                           declarations=2,expected='ACCEPT' if name=='control' else 'INTENDED_REJECT')
                      for engine in ['subst','kam'] for name in ['control','candidate']],
               exact_rejection=REJECTION,launch_owner='lazy_lead',keep_going=False,jobs=1,
               input_scope='Existing recursor capability pair only; no positive intake fixture launch.')
    p.write_new(p.BASE/'capability-manifest-r1.json',value)
    return value

def execute(manifest_path,attempt):
    p.active(); m=p.load(manifest_path)
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
    args=parser.parse_args()
    value=freeze_capability() if args.command=='freeze-capability' else execute(Path(args.manifest),args.attempt)
    print(json.dumps(value,indent=2))

if __name__=='__main__': main()
