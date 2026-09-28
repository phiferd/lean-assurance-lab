"""One-owner, staged exact-byte controls for six immutable public API comparisons."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

from lib.closure_controls import host_rss_preflight
from lib.metamorphic_pilot_runner_v3 import run_supervised
from lib import stateful_validation_audit as audit

ROOT = Path(__file__).resolve().parents[1]
BASE = Path('results/research/stateful-validation-pilot-1')
ITEM = 'STATEFUL-VALIDATION-PILOT-1'
CONTRACT = BASE/'scientific-contract.json'
SOURCE = BASE/'source-manifest.json'
HARNESS = BASE/'StatefulHarness.lean'
TOOLING = ['lib/stateful_validation_pilot.py', 'lib/stateful_validation_audit.py',
           'tests/test_stateful_validation_pilot.py', 'tests/test_stateful_validation_audit.py',
           'scripts/stateful-validation-pilot', 'lib/metamorphic_pilot_runner_v3.py',
           'lib/metamorphic_pilot_runner.py', 'lib/closure_controls.py', str(HARNESS)]

def require(ok, message):
    if not ok: raise ValueError(message)

def unique(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, 'duplicate JSON key')
        result[key] = value
    return result

def read(path):
    return json.loads((ROOT/path).read_text(), object_pairs_hook=unique)

def bind(path):
    path = Path(path)
    if path.is_absolute(): path = path.relative_to(ROOT)
    data = (ROOT/path).read_bytes()
    return dict(path=str(path),bytes=len(data),sha256=hashlib.sha256(data).hexdigest())

def verify(row):
    require(bind(row['path']) == row, 'binding differs: '+row['path'])
    return ROOT/row['path']

def write_new(path, value):
    path=ROOT/path; path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x') as out: json.dump(value,out,indent=2); out.write('\n')

def committed(rows):
    for row in rows:
        actual=verify(row).read_bytes()
        old=subprocess.run(['git','show','HEAD:'+row['path']],cwd=ROOT,capture_output=True,check=True).stdout
        require(actual==old,'not committed: '+row['path'])

def active():
    q=read(Path('config/research-queue.json'))
    require(q['selected_item']==ITEM and next(x for x in q['items'] if x['id']==ITEM)['status']=='ACTIVE','item not ACTIVE')

def source_check():
    source=read(SOURCE)
    require(source['source_commit']=='d8b18978322de05a8f3dba51ef03cf5461676c17','source revision')
    require(source['scientific_contract']==bind(CONTRACT),'scientific input changed')
    for row in [source['scientific_contract'],source['review'],source['runtime_inventory'],*source['sources']]: verify(row)
    for row in source['host_tools']:
        require(hashlib.sha256(Path(row['path']).read_bytes()).hexdigest()==row['sha256'],'host tool changed')
    return source

def runtime_check():
    source=source_check(); runtime=read(Path(source['runtime_inventory']['path']))
    root=Path(runtime['root']); rows=[]
    for section in ('bin','lib'):
        for path in sorted((root/section).rglob('*')):
            if path.is_symlink(): rows.append(dict(path=str(path.relative_to(root)),symlink=str(path.readlink())))
            elif path.is_file():
                data=path.read_bytes(); rows.append(dict(path=str(path.relative_to(root)),bytes=len(data),sha256=hashlib.sha256(data).hexdigest()))
    require(rows==runtime['files'],'installed runtime differs from exact retained inventory')
    return root

def scientific_review():
    review=read(BASE/'scientific-review.json')
    require(review['verdict']=='PASS' and review['contract_sha256']==bind(CONTRACT)['sha256'] and
            review['source_manifest_sha256']==bind(SOURCE)['sha256'],'scientific review absent/stale')
    return review

def tooling(): return [bind(Path(p)) for p in TOOLING]

def fixture(doc, comparison, side):
    return dict(comparison=comparison['id'],side=side,
                requests=[dict(id=name,**doc['declarations'][name]) for name in comparison[side]])

def cells(doc):
    return [dict(comparison=c['id'],side=side,path=str(BASE/'fixtures'/f'{c["id"]}-{side}.json'))
            for c in doc['comparisons'] for side in ['fresh','prefixed']]

def freeze_generation():
    active(); source_check(); scientific_review(); doc=read(CONTRACT); audit.audit_contract(doc)
    review=read(BASE/'tooling-review-r1.json')
    require(review['verdict']=='PASS' and review['tooling']==tooling(),'tooling review absent/stale')
    value=dict(item_id=ITEM,stage='GENERATION',contract=bind(CONTRACT),source=bind(SOURCE),
               scientific_review=bind(BASE/'scientific-review.json'),tooling_review=bind(BASE/'tooling-review-r1.json'),
               tooling=tooling(),cells=cells(doc))
    write_new(BASE/'generation-manifest.json',value)
    return bind(BASE/'generation-manifest.json')

def generate():
    active(); m=read(BASE/'generation-manifest.json'); doc=read(CONTRACT)
    require(m['cells']==cells(doc),'generation cell inventory')
    committed([bind(BASE/'generation-manifest.json'),m['contract'],m['source'],m['scientific_review'],m['tooling_review'],*m['tooling']])
    dest=ROOT/BASE/'fixtures'; require(not dest.exists(),'fixtures already exist; preserve frozen bytes'); dest.mkdir()
    rows=[]
    for c in doc['comparisons']:
        for side in ['fresh','prefixed']:
            value=fixture(doc,c,side); data=(json.dumps(value,indent=2)+'\n').encode()
            report=audit.audit_fixture(data,doc,c['id'],side)
            path=BASE/'fixtures'/f'{c["id"]}-{side}.json'
            with (ROOT/path).open('xb') as out: out.write(data)
            rows.append(dict(comparison=c['id'],side=side,fixture=bind(path),audit=report))
    write_new(BASE/'artifact-audit.json',dict(generation_manifest=bind(BASE/'generation-manifest.json'),rows=rows))
    return dict(histories=len(rows),artifact_audit=bind(BASE/'artifact-audit.json'))

def artifacts():
    doc=read(CONTRACT); audit.audit_contract(doc); record=read(BASE/'artifact-audit.json')
    verify(record['generation_manifest'])
    require([(r['comparison'],r['side']) for r in record['rows']]==[(r['comparison'],r['side']) for r in cells(doc)],'artifact inventory')
    for row in record['rows']:
        actual=audit.audit_fixture(verify(row['fixture']).read_bytes(),doc,row['comparison'],row['side'])
        require(actual==row['audit'],'artifact audit differs')
    return doc,record

def environment(runtime):
    return {'PATH':str(runtime/'bin')+':/usr/bin:/bin','HOME':str(ROOT), 'LANG':'C.UTF-8',
            'LEAN_PATH':'','LEAN_SRC_PATH':'','LEAN_SYSROOT':str(runtime)}

def freeze_execution(revision):
    active(); source_check(); doc,record=artifacts()
    value=dict(item_id=ITEM,stage='EXECUTION',revision=revision,contract=bind(CONTRACT),source=bind(SOURCE),
       generation=bind(BASE/'generation-manifest.json'),artifact_audit=bind(BASE/'artifact-audit.json'),
       fixtures=[r['fixture'] for r in record['rows']],tooling=tooling(),cells=cells(doc),
       controls=doc['controls'],environment=environment(Path(read(SOURCE)['runtime_root'])),
       scientific_review=bind(BASE/'scientific-review.json'))
    write_new(BASE/f'execution-manifest-{revision}.json',value)
    return bind(BASE/f'execution-manifest-{revision}.json')

def safe(receipt):
    require(receipt['cleanup_complete'] and not receipt['timed_out'] and not receipt['memory_exceeded'] and
      receipt['memory_monitor_error'] is None and receipt['memory_monitor_samples']>0 and receipt['maximum_observed_rss_bytes']>0,
      'process-control failure; preserve, diagnose and repair before more launches')

def receipt_custody(receipt, stdout, stderr, controls):
    safe(receipt)
    for key,data in [('stdout',stdout),('stderr',stderr)]:
        require(receipt[key+'_sha256']==hashlib.sha256(data).hexdigest() and
                receipt[key+'_bytes']==len(data),'raw '+key+' custody')
    require(receipt['memory_limit_bytes']==controls['memory_bytes'],'memory control differs')

def freeze_compile(revision):
    active(); source_check(); scientific_review()
    runtime=Path(read(SOURCE)['runtime_root'])
    value=dict(item_id=ITEM,stage='COMPILE_ONLY',revision=revision,source=bind(SOURCE),
       contract=bind(CONTRACT),tooling=tooling(),argv=[str(runtime/'bin/lean'),str(ROOT/HARNESS)],
       environment=environment(runtime),controls=read(CONTRACT)['controls'],
       non_scientific='Compile generic definitions only; no --run, no #eval, no scientific fixture input.')
    write_new(BASE/f'compile-manifest-{revision}.json',value)
    return bind(BASE/f'compile-manifest-{revision}.json')

def compile_harness(revision, attempt):
    active(); path=BASE/f'compile-manifest-{revision}.json'; m=read(path)
    review_path=BASE/f'compile-review-{revision}.json'; review=read(review_path)
    runtime=Path(read(SOURCE)['runtime_root'])
    require(m['stage']=='COMPILE_ONLY' and m['argv']==[str(runtime/'bin/lean'),str(ROOT/HARNESS)]
            and m['tooling']==tooling() and m['environment']==environment(runtime)
            and m['controls']==read(CONTRACT)['controls'],'compile contract differs')
    require(review['verdict']=='PASS' and review['manifest']==bind(path),'compile review absent/stale')
    committed([bind(path),bind(review_path),m['source'],m['contract'],*m['tooling']])
    runtime_check(); host_rss_preflight()
    require('/' not in attempt and attempt.startswith('compile-'),'unsafe compile attempt path')
    out=BASE/attempt; (ROOT/out).mkdir(exist_ok=False)
    started=datetime.now(timezone.utc).isoformat(); error=None; receipt=None
    write_new(out/'launch.json',dict(manifest=bind(path),review=bind(review_path),started_at=started))
    try:
        receipt=run_supervised(argv=m['argv'],cwd=ROOT,stdin=None,env=m['environment'],
            timeout_seconds=m['controls']['timeout_seconds'],memory_bytes=m['controls']['memory_bytes'],raw_prefix=ROOT/out/'compiler')
        receipt_custody(receipt,(ROOT/receipt['raw_stdout_path']).read_bytes(),(ROOT/receipt['raw_stderr_path']).read_bytes(),m['controls'])
        require(receipt['exit_code']==0,'generic harness compilation failed; repair within item')
        runtime_check()
    except Exception as exc: error=str(exc)
    result=dict(item_id=ITEM,manifest=bind(path),receipt=receipt,started_at=started,
                finished_at=datetime.now(timezone.utc).isoformat(),status='PASS' if error is None else 'REPAIR_REQUIRED',error=error)
    write_new(out/'result.json',result)
    return result

def validate_manifest(m):
    source_check(); doc,record=artifacts()
    require(m['item_id']==ITEM and m['stage']=='EXECUTION' and m['cells']==cells(doc) and
            m['controls']==doc['controls'] and m['environment']==environment(Path(read(SOURCE)['runtime_root'])),'execution contract differs')
    for key,path in [('contract',CONTRACT),('source',SOURCE),('generation',BASE/'generation-manifest.json'),
                     ('artifact_audit',BASE/'artifact-audit.json'),('scientific_review',BASE/'scientific-review.json')]:
        require(m[key]==bind(path),'unexpected '+key+' binding')
    require(m['fixtures']==[r['fixture'] for r in record['rows']] and m['tooling']==tooling(),'execution bytes changed')
    return doc

def execution_inputs(m):
    source=read(SOURCE)
    return [m[k] for k in ['contract','source','generation','artifact_audit','scientific_review']]+m['tooling']+m['fixtures']+[source['runtime_inventory'],source['review'],*source['sources']]

def execute(revision, attempt):
    active(); manifest_path=BASE/f'execution-manifest-{revision}.json'; m=read(manifest_path)
    doc=validate_manifest(m); review_path=BASE/f'execution-review-{revision}.json'; review=read(review_path)
    require(review['verdict']=='PASS' and review['manifest']==bind(manifest_path),'exact independent launch review missing/stale')
    committed([bind(manifest_path),bind(review_path),*execution_inputs(m)])
    host_rss_preflight(); runtime=runtime_check()
    require('/' not in attempt and attempt.startswith('execution-'),'unsafe attempt path')
    output=BASE/attempt; (ROOT/output).mkdir(exist_ok=False)
    started=datetime.now(timezone.utc).isoformat(); mono=time.monotonic()
    rows=[]; error=None
    write_new(output/'launch.json',dict(manifest=bind(manifest_path),review=bind(review_path),started_at=started,
              monotonic_start=mono,git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()))
    try:
        for i,cell in enumerate(m['cells']):
            committed([bind(manifest_path),*execution_inputs(m)])
            artifact=m['fixtures'][i]; verify(artifact)
            argv=[str(runtime/'bin/lean'),'--run',str(ROOT/HARNESS),str(ROOT/cell['path'])]
            receipt=run_supervised(argv=argv,cwd=ROOT,stdin=None,env=m['environment'],
                    timeout_seconds=m['controls']['timeout_seconds'],memory_bytes=m['controls']['memory_bytes'],
                    raw_prefix=ROOT/output/f'{i+1:02d}-{cell["comparison"]}-{cell["side"]}')
            row=dict(cell=cell,input_before=artifact,input_after=bind(Path(cell['path'])),receipt=receipt,
                     stdout=bind(Path(receipt['raw_stdout_path'])),stderr=bind(Path(receipt['raw_stderr_path'])))
            write_new(output/f'cell-{i+1:02d}.json',row); rows.append(bind(output/f'cell-{i+1:02d}.json'))
            receipt_custody(receipt,verify(row['stdout']).read_bytes(),verify(row['stderr']).read_bytes(),m['controls'])
            require(receipt['exit_code']==0,'harness compile/process failure; repair same item')
            require(row['input_before']==row['input_after'],'scientific input changed')
            observation=audit.audit_output(verify(row['stdout']).read_bytes(),verify(row['stderr']).read_bytes(),
                   read(Path(cell['path'])),doc)
            write_new(output/f'audit-{i+1:02d}.json',observation)
        runtime_check()
    except Exception as exc:
        error=str(exc)
    result=dict(item_id=ITEM,manifest=bind(manifest_path),review=bind(review_path),started_at=started,
                finished_at=datetime.now(timezone.utc).isoformat(),elapsed_seconds=time.monotonic()-mono,
                cells=rows,status='PASS' if error is None else 'REPAIR_REQUIRED',error=error)
    write_new(output/'result.json',result)
    return result

def replay(path):
    result=read(path); m=read(Path(result['manifest']['path'])); verify(result['manifest']); doc=validate_manifest(m)
    require(result['status']=='PASS' and len(result['cells'])==12,'incomplete science result')
    audits=[]
    for i,rowbinding in enumerate(result['cells']):
        row=read(Path(rowbinding['path'])); verify(rowbinding); cell=m['cells'][i]
        require(row['cell']==cell and row['input_before']==row['input_after']==m['fixtures'][i],'cell/input mismatch')
        receipt=row['receipt']; receipt_custody(receipt,verify(row['stdout']).read_bytes(),verify(row['stderr']).read_bytes(),m['controls'])
        require(receipt['exit_code']==0,'process exit')
        expected=[str(Path(read(SOURCE)['runtime_root'])/'bin/lean'),'--run',str(ROOT/HARNESS),str(ROOT/cell['path'])]
        require(receipt['argv']==expected and receipt['cwd']==str(ROOT),'command custody')
        require(row['stdout']['path']==receipt['raw_stdout_path'] and row['stderr']['path']==receipt['raw_stderr_path'],'raw path custody')
        audits.append(audit.audit_output(verify(row['stdout']).read_bytes(),verify(row['stderr']).read_bytes(),read(Path(cell['path'])),doc))
    return dict(status='PASS',comparisons=6,histories=12,requests=25,result=bind(path),audits=audits)

def main():
    parser=argparse.ArgumentParser(); parser.add_argument('action',choices=['freeze-compile','compile','freeze-generation','generate','freeze-execution','execute','replay'])
    parser.add_argument('--revision',default='r1'); parser.add_argument('--attempt',default='execution-0001')
    args=parser.parse_args()
    if args.action=='freeze-compile': result=freeze_compile(args.revision)
    elif args.action=='compile': result=compile_harness(args.revision,args.attempt)
    elif args.action=='freeze-generation': result=freeze_generation()
    elif args.action=='generate': result=generate()
    elif args.action=='freeze-execution': result=freeze_execution(args.revision)
    elif args.action=='execute': result=execute(args.revision,args.attempt)
    else: result=replay(BASE/args.attempt/'result.json')
    print(json.dumps(result,indent=2))
    if result.get('status')=='REPAIR_REQUIRED': sys.exit(1)

if __name__=='__main__': main()
