"""Staged freeze/generate/run/replay controls for exactly twelve science cells."""
from datetime import datetime, timezone
import argparse
import json
from pathlib import Path
import re
from lib import lazy_reduction_pilot as p
from lib import lazy_reduction_execute as e
from lib import lazy_reduction_cases as c
from lib import lazy_reduction_audit as a

CONTRACT=p.BASE/'scientific-contract.json'
GENERATION=p.BASE/'generation-manifest.json'
EXECUTION=p.BASE/'scientific-execution-manifest.json'
CAPABILITY=p.BASE/'capability-0001/result.json'
AUDIT=p.BASE/'artifact-audit.json'

def tooling():
    files=['lib/lazy_reduction_science.py','lib/lazy_reduction_cases.py','lib/lazy_reduction_audit.py',
      'scripts/lazy-reduction-science','tests/test_lazy_reduction_science.py',
      'lib/valid_dependent_term_generator.py','lib/valid_dependent_term_audit.py','lib/valid_dependent_term_pilot.py']
    return [*e.execution_tooling(),*[p.bind(Path(x)) for x in files]]

def capability():
    result=p.load(CAPABILITY); m=p.load(p.BASE/'capability-manifest-r1.json'); e.validate_capability(m)
    if result['manifest']!=p.bind(p.BASE/'capability-manifest-r1.json'): raise ValueError('unexpected capability manifest')
    p.verify(result['manifest'])
    if len(result['cells'])!=4 or not result['acceptance_matched']: raise ValueError('capability not passed')
    for row,cell in zip(result['cells'],m['cells']):
        p.safe(row['receipt']); stdout,stderr=p.raw(row['receipt'])
        if row['cell']!=cell or row['input_before']!=m['artifacts'][cell['artifact_id']] or row['input_after']!=row['input_before']:
            raise ValueError('capability custody or cell identity changed')
        observation=p.classify(row['receipt'],stdout,stderr,2,m['exact_rejection'])
        if observation!=row['observation'] or observation['verdict']!=cell['expected']: raise ValueError('capability replay failed')
    return result,m

def freeze_contract():
    p.active(); capability()
    doc=c.contract(); a.audit_contract(doc)
    p.write_new(CONTRACT,doc)
    return {'contract':p.bind(CONTRACT),'audit':a.audit_contract(doc)}

def freeze_generation():
    p.active(); capability(); doc=p.load(CONTRACT); a.audit_contract(doc)
    review=p.load(p.BASE/'scientific-review.json')
    if review['verdict']!='PASS' or review['contract']!=p.bind(CONTRACT): raise ValueError('exact scientific review absent')
    for row in review['tooling']: p.verify(row)
    value=dict(item_id=p.ITEM,stage='GENERATION',contract=p.bind(CONTRACT),review=p.bind(p.BASE/'scientific-review.json'),
               capability=p.bind(CAPABILITY),source=p.bind(p.BASE/'source-r1.json'),tooling=tooling(),
               expected_ids=c.IDS,generation='Exactly six deterministic direct NDJSON encodings; no checker or Lean producer launches.')
    p.write_new(GENERATION,value); return {'manifest':p.bind(GENERATION)}

def generate():
    p.active(); capability(); m=p.load(GENERATION)
    p.require_committed([p.bind(GENERATION),m['contract'],m['review'],m['capability'],m['source'],*m['tooling']])
    doc=p.load(CONTRACT); a.audit_contract(doc)
    directory=p.ROOT/p.BASE/'artifacts'
    if directory.exists(): raise ValueError('scientific artifacts already generated; never replace')
    directory.mkdir()
    rows=[]
    for case in doc['cases']:
        data=c.encode(case); audit=a.audit_export(data,case)
        output=directory/(case['case_id']+'.ndjson')
        with output.open('xb') as stream: stream.write(data)
        rows.append(dict(case_id=case['case_id'],artifact=p.bind(output),audit=audit))
    result=dict(item_id=p.ITEM,generation_manifest=p.bind(GENERATION),contract=p.bind(CONTRACT),rows=rows)
    p.write_new(AUDIT,result); return {'artifacts':len(rows),'audit':p.bind(AUDIT)}

def audit_artifacts():
    doc=p.load(CONTRACT); a.audit_contract(doc); result=p.load(AUDIT)
    p.verify(result['generation_manifest']); p.verify(result['contract'])
    if [row['case_id'] for row in result['rows']]!=c.IDS: raise ValueError('artifact IDs differ')
    for case,row in zip(doc['cases'],result['rows']):
        if a.audit_export(p.verify(row['artifact']).read_bytes(),case)!=row['audit']: raise ValueError('object audit changed')
    return doc,result

def cells():
    return [dict(cell_id=f'{engine}::{name}',engine=engine,artifact_id=name,declarations=1,expected='ACCEPT')
            for engine in ['subst','kam'] for name in c.IDS]

def freeze_execution():
    p.active(); _,cap=capability(); doc,audit=audit_artifacts()
    m=dict(item_id=p.ITEM,stage='SCIENCE',binary=cap['binary'],build_result=cap['build_result'],source=cap['source'],
      artifacts={row['case_id']:row['artifact'] for row in audit['rows']},contract=p.bind(CONTRACT),generation_manifest=p.bind(GENERATION),
      artifact_audit=p.bind(AUDIT),capability=p.bind(CAPABILITY),review=p.bind(p.BASE/'scientific-review.json'),tooling=tooling(),
      environment={**p.ENV,'LL_KAM_MODE':'3'},timeout_seconds=120,memory_bytes=2147483648,cells=cells(),jobs=1,keep_going=False,
      launch_owner='lazy_lead',expected_relation='Twelve ACCEPT cells and six qualified KAM demand observations')
    p.write_new(EXECUTION,m); return {'manifest':p.bind(EXECUTION)}

def validate_manifest(m):
    if (m['item_id']!=p.ITEM or m['stage']!='SCIENCE' or m['cells']!=cells() or m['jobs']!=1 or m['keep_going'] is not False
        or m['environment']!={**p.ENV,'LL_KAM_MODE':'3'} or m['timeout_seconds']!=120 or m['memory_bytes']!=2147483648
        or m['launch_owner']!='lazy_lead'): raise ValueError('scientific matrix/control differs')
    _,audit=audit_artifacts()
    if m['artifacts']!={row['case_id']:row['artifact'] for row in audit['rows']}: raise ValueError('scientific artifacts differ')
    _,cap=capability()
    for key in ['binary','build_result','source']:
        if m[key]!=cap[key]: raise ValueError('unexpected observer binding')
    for key,path in [('contract',CONTRACT),('generation_manifest',GENERATION),('artifact_audit',AUDIT),
                     ('capability',CAPABILITY),('review',p.BASE/'scientific-review.json')]:
        if m[key]!=p.bind(path): raise ValueError('unexpected scientific binding')

def classify(receipt,stdout,stderr,case,line_number):
    observation=p.classify(receipt,stdout,stderr,1)
    if observation['verdict'] in ['ACCEPT','PROCESS_CONTROL_FAILURE','PROCESS_FAILURE','PARSER_FAILURE']: return observation
    # Ordinary definition rejection has a separate source-qualified continuation.
    try: lines=stderr.decode().splitlines(); p.safe(receipt)
    except (UnicodeError,ValueError): return observation
    prefix=f"FAIL {case['declaration_name']} (line {line_number}): "
    failures=[x for x in lines if x.startswith('FAIL ')]
    loaded=[p.LOADED.fullmatch(x) for x in lines if x.startswith('loaded ')]
    if (receipt['exit_code']==1 and not stdout and len(loaded)==1 and loaded[0] and int(loaded[0][1])==1
        and len(failures)==1 and failures[0].startswith(prefix)
        and all(x.startswith(('loaded ',prefix,'  inferred: ','  declared: ')) for x in lines)):
        diagnostic=failures[0][len(prefix):]
        if any(x in diagnostic.lower() for x in ['timeout','maximum recursion depth','deep recursion','memory','resource']):
            return dict(verdict='RESOURCE_LIMIT',diagnostic=failures[0])
        if diagnostic==f"declaration type mismatch for '{case['declaration_name']}'":
            return dict(verdict='SEMANTIC_REJECT',diagnostic=failures[0])
        return dict(verdict='INTERNAL_OR_UNKNOWN_FAILURE',diagnostic=failures[0])
    return observation

def demand(observation,stderr,engine,case):
    if observation['verdict']!='ACCEPT': return 'NO_ACCEPTANCE_DEMAND_CLAIM'
    machine=observation['machine']
    nat=re.findall(rb'^nat ops: (\d+), first-operand limbs (\d+), GMP [0-9.e+-]+ Gcycles, literal interning [0-9.e+-]+ Gcycles$',stderr,re.M)
    if len(nat)!=1 or nat[0]!=(b'0',b'0') or any(machine[x] for x in ['delta','iota','proj']): return 'FORBIDDEN_ROUTE_OR_MISSING_COUNTER'
    if re.findall(rb'^declarations rechecked with fusion: (\d+)$',stderr,re.M)!=[b'0']:
        return 'FUSION_RETRY_OR_MISSING_COUNTER'
    if engine=='subst': return 'PASS' if machine['beta']==machine['let']==0 else 'PROFILE_MISMATCH'
    return 'PASS' if all(machine[k]>=v for k,v in case['kam_minimum'].items()) else 'UNSUPPORTED_DEMAND'

def execute(attempt='science-0001'):
    p.active(); capability(); m=p.load(EXECUTION); validate_manifest(m)
    refs=['contract','generation_manifest','artifact_audit','capability','review','build_result','source']
    p.require_committed([p.bind(EXECUTION),*[m[x] for x in refs],*m['tooling'],*m['artifacts'].values()])
    p.verify(m['binary']); doc,_=audit_artifacts(); cases={x['case_id']:x for x in doc['cases']}
    out=p.BASE/attempt
    if (p.ROOT/out).exists(): raise ValueError('attempt exists')
    (p.ROOT/out).mkdir(); results=[]
    for index,cell in enumerate(m['cells']):
        p.verify(m['binary']); artifact=p.verify(m['artifacts'][cell['artifact_id']]); case=cases[cell['artifact_id']]
        started=datetime.now(timezone.utc).isoformat()
        receipt=p.run_supervised(argv=[str(p.ROOT/m['binary']['path']),'--engine',cell['engine'],'--jobs','1',str(artifact)],
              cwd=p.ROOT,stdin=None,env=m['environment'],timeout_seconds=m['timeout_seconds'],memory_bytes=m['memory_bytes'],
              raw_prefix=p.ROOT/out/f'{index+1:02d}-{cell["engine"]}-{cell["artifact_id"]}')
        stdout,stderr=p.raw(receipt); observation=classify(receipt,stdout,stderr,case,len(artifact.read_bytes().splitlines()))
        result=dict(cell=cell,started_at=started,finished_at=datetime.now(timezone.utc).isoformat(),
                    input_before=m['artifacts'][cell['artifact_id']],input_after=p.bind(artifact),receipt=receipt,
                    observation=observation,demand=demand(observation,stderr,cell['engine'],case))
        p.write_new(out/f'cell-{index+1:02d}.json',result); results.append(result)
        p.safe(receipt); p.verify(m['binary'])
        if result['input_after']!=result['input_before']: raise ValueError('scientific input custody changed')
        if observation['verdict'] not in ['ACCEPT','SEMANTIC_REJECT']: raise ValueError('engineering incident; repair before further cells')
    result=dict(item_id=p.ITEM,manifest=p.bind(EXECUTION),cells=results,actual_process_count=len(results),
       acceptance_matched=all(x['observation']['verdict']=='ACCEPT' for x in results),
       demand_qualified=all(x['demand']=='PASS' for x in results),
       elapsed_seconds=sum(x['receipt']['elapsed_seconds'] for x in results))
    p.write_new(out/'result.json',result)
    return {k:v for k,v in result.items() if k!='cells'}

def main():
    parser=argparse.ArgumentParser(); parser.add_argument('command',choices=['freeze-contract','freeze-generation','generate','freeze-execution','execute']); args=parser.parse_args()
    commands={'freeze-contract':freeze_contract,'freeze-generation':freeze_generation,'generate':generate,'freeze-execution':freeze_execution,'execute':execute}
    print(json.dumps(commands[args.command](),indent=2))

if __name__=='__main__': main()
