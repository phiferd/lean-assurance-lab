"""Portable successor replay for immutable stateful-pilot evidence."""
from contextlib import contextmanager
import hashlib
from pathlib import Path
from lib import stateful_validation_pilot_r4 as r4
from lib import stateful_validation_pilot as p


def recorded_source_check():
    source=p.read(p.SOURCE)
    p.require(source['source_commit']=='d8b18978322de05a8f3dba51ef03cf5461676c17','source revision')
    p.require(source['scientific_contract']==p.bind(p.CONTRACT),'scientific input changed')
    for row in [source['scientific_contract'],source['review'],source['runtime_inventory'],*source['sources']]: p.verify(row)
    for row in source['host_tools']:
        p.require(Path(row['path']).is_absolute() and len(row['sha256'])==64 and
                  all(c in '0123456789abcdef' for c in row['sha256']),'invalid recorded host tool identity')
    return source


@contextmanager
def recorded_host_context():
    original=p.source_check; p.source_check=recorded_source_check
    try: yield
    finally: p.source_check=original


def compile_history():
    rows=[]
    for directory in sorted((p.ROOT/p.BASE).glob('compile-[0-9]*')):
        result=p.read(directory/'result.json'); manifest=p.read(Path(result['manifest']['path']))
        p.verify(result['manifest'])
        for binding in [manifest['source'],manifest['contract'],*manifest['tooling']]: p.verify(binding)
        launch=p.read(directory/'launch.json'); review=p.read(Path(launch['review']['path']))
        p.verify(launch['review'])
        p.require(launch['manifest']==result['manifest'] and review['manifest']==result['manifest'] and review['verdict']=='PASS','historical compile gate differs')
        receipt=result['receipt']
        stdout=(p.ROOT/receipt['raw_stdout_path']).read_bytes(); stderr=(p.ROOT/receipt['raw_stderr_path']).read_bytes()
        p.receipt_custody(receipt,stdout,stderr,manifest['controls'])
        p.require(receipt['argv']==manifest['argv'] and '--run' not in receipt['argv'] and len(receipt['argv'])==2,'compile invoked science')
        p.require(receipt['cwd']==manifest['environment']['HOME'],'compile cwd')
        p.require((result['status']=='PASS')==(receipt['exit_code']==0),'compile outcome changed')
        rows.append(dict(attempt=directory.name,status=result['status'],result=p.bind(directory/'result.json'),receipt=receipt))
    p.require(rows and rows[-1]['status']=='PASS','successful generic compile absent')
    return rows


def replay(path):
    result=p.read(path); m=p.read(Path(result['manifest']['path'])); p.verify(result['manifest'])
    with recorded_host_context(): doc=validate_manifest(m)
    p.require(result['status']=='PASS' and len(result['cells'])==12,'incomplete science result')
    audits=[]
    for i,rowbinding in enumerate(result['cells']):
        row=p.read(Path(rowbinding['path'])); p.verify(rowbinding); cell=m['cells'][i]
        p.require(row['cell']==cell and row['input_before']==row['input_after']==m['fixtures'][i],'cell/input mismatch')
        receipt=row['receipt']; p.receipt_custody(receipt,p.verify(row['stdout']).read_bytes(),p.verify(row['stderr']).read_bytes(),m['controls'])
        p.require(receipt['exit_code']==0,'process exit')
        recorded_root=Path(receipt['cwd'])
        p.require(recorded_root.is_absolute() and receipt['cwd']==m['environment']['HOME'],'recorded cwd custody')
        expected=[str(Path(m['environment']['LEAN_SYSROOT'])/'bin/lean'),'--run',str(recorded_root/p.HARNESS),str(recorded_root/cell['path'])]
        p.require(receipt['argv']==expected,'command custody')
        p.require(row['stdout']['path']==receipt['raw_stdout_path'] and row['stderr']['path']==receipt['raw_stderr_path'],'raw path custody')
        audits.append(p.audit.audit_output(p.verify(row['stdout']).read_bytes(),p.verify(row['stderr']).read_bytes(),p.read(Path(cell['path'])),doc))
    return dict(status='PASS',comparisons=6,histories=12,requests=25,result=p.bind(path),audits=audits)


def validate_manifest(m):
    """Rebuild the exact manifest without substituting this checkout's HOME."""
    with recorded_host_context():
        p.source_check(); doc,record=r4.artifacts()
    source=p.read(p.SOURCE); recorded_root=Path(m['environment']['HOME'])
    p.require(recorded_root.is_absolute(),'recorded execution root')
    runtime=Path(source['runtime_root'])
    environment={'PATH':str(runtime/'bin')+':/usr/bin:/bin','HOME':str(recorded_root),
                 'LANG':'C.UTF-8','LEAN_PATH':'','LEAN_SRC_PATH':'','LEAN_SYSROOT':str(runtime)}
    expected=dict(item_id=p.ITEM,stage='EXECUTION',revision='r4',contract=p.bind(p.CONTRACT),source=p.bind(p.SOURCE),
       generation=p.bind(r4.GEN),artifact_audit=p.bind(p.BASE/'artifact-audit.json'),
       fixtures=[r['fixture'] for r in record['rows']],tooling=p.tooling(),cells=p.cells(doc),controls=doc['controls'],
       environment=environment,scientific_review=p.bind(p.BASE/'scientific-review.json'),
       adoption=p.bind(r4.ADOPTED),adoption_manifest=p.bind(r4.ADOPTION),adoption_review=p.bind(r4.ADOPT_REVIEW))
    p.require(m==expected,'execution manifest differs from repaired exact canonical contract')
    return doc


def validate():
    science=replay(p.BASE/'execution-0001/result.json'); compiles=compile_history()
    p.require(len(compiles)==3 and [r['status'] for r in compiles]==['REPAIR_REQUIRED','REPAIR_REQUIRED','PASS'],'compile history inventory')
    result=p.read(p.BASE/'execution-0001/result.json'); launch=p.read(p.BASE/'execution-0001/launch.json'); review=p.read(Path(result['review']['path']))
    p.verify(result['review'])
    p.require(launch['manifest']==result['manifest'] and launch['review']==result['review'] and review['manifest']==result['manifest'] and review['verdict']=='PASS','execution review/custody')
    return dict(item_id=p.ITEM,status='PASS',compile_attempts=3,failed_compile_attempts=2,
                comparisons=6,histories=12,requests=25,execution=science,
                compile_results=[{k:v for k,v in r.items() if k!='receipt'} for r in compiles],launches_during_validation=0)


def accounting():
    compiles=compile_history(); science=p.read(p.BASE/'execution-0001/result.json')
    rows=[p.read(Path(r['path'])) for r in science['cells']]
    receipts=[r['receipt'] for r in compiles]+[r['receipt'] for r in rows]
    return dict(item_id=p.ITEM,compile_attempts=len(compiles),failed_compile_attempts=sum(r['status']!='PASS' for r in compiles),
       scientific_processes=len(rows),scientific_requests=25,scientific_comparisons=6,generated_histories=12,
       total_supervised_processes=len(receipts),total_supervised_seconds=sum(r['elapsed_seconds'] for r in receipts),
       positive_rss_samples=sum(r['memory_monitor_samples'] for r in receipts),
       maximum_observed_rss_bytes=max(r['maximum_observed_rss_bytes'] for r in receipts),
       all_cleanup_complete=all(r['cleanup_complete'] for r in receipts),
       observed_scientific_utc_interval=[science['started_at'],science['finished_at']],
       observed_scientific_wall_seconds=science['elapsed_seconds'],manual_engineering_review_seconds=None,
       unmeasured_note='Reading, implementation, review and manual diagnosis were not captured by paired monotonic intervals; their duration is unknown, never zero.',
       preparation_incidents=['Sandbox /bin/ps EPERM then successful escalated host preflight.',
                              'Sandbox curl DNS failure then exact successful read-only fetch.'],
       policy='Counts/time are observations only; no terminal attempt/time caps.')


def validate_closure():
    current=validate(); result=p.read(p.BASE/'result.json'); closure=p.read(p.BASE/'closure.json')
    p.require(p.read(p.BASE/'evidence-replay.json')==current,'stored replay differs')
    p.require(p.read(p.BASE/'work-accounting.json')==accounting(),'accounting differs')
    for key,path in [('contract',p.CONTRACT),('execution',p.BASE/'execution-0001/result.json'),
                     ('replay',p.BASE/'evidence-replay.json'),('artifact_audit',p.BASE/'artifact-audit.json')]:
        p.require(result[key]==p.bind(path),'result binding differs: '+key)
    p.require(result['outcome']=='SUCCESS' and result['scientific_result']=='SIX_PRESERVED_ENVIRONMENT_HISTORY_RELATIONS'
          and result['comparisons']==6 and result['histories']==12 and result['requests']==25,'scientific result differs')
    p.require(closure['result']==p.bind(p.BASE/'result.json') and closure['accounting']==p.bind(p.BASE/'work-accounting.json')
          and closure['successor_started'] is False and result['successor_execution']=='NOT_STARTED','closure differs')
    p.require(closure['successor']==result['successor']=='REAL-PROOF-SLICES-PILOT-1','closure successor differs')
    p.require(result['nonclaims']==p.read(p.CONTRACT)['limits'],'claim limits differ')
    return current
