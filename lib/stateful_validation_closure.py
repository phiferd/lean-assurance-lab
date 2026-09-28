"""Replay stateful pilot evidence and historical engineering receipts without launches."""
from pathlib import Path
from lib import stateful_validation_pilot_r4
from lib import stateful_validation_pilot as p

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
        p.require(receipt['cwd']==str(p.ROOT),'compile cwd')
        p.require((result['status']=='PASS')==(receipt['exit_code']==0),'compile outcome changed')
        rows.append(dict(attempt=directory.name,status=result['status'],result=p.bind(directory/'result.json'),receipt=receipt))
    p.require(rows and rows[-1]['status']=='PASS','successful generic compile absent')
    return rows

def validate():
    replay=p.replay(p.BASE/'execution-0001/result.json')
    compiles=compile_history()
    p.require(len(compiles)==3 and [r['status'] for r in compiles]==['REPAIR_REQUIRED','REPAIR_REQUIRED','PASS'],'compile history inventory')
    result=p.read(p.BASE/'execution-0001/result.json')
    launch=p.read(p.BASE/'execution-0001/launch.json'); review=p.read(Path(result['review']['path']))
    p.verify(result['review'])
    p.require(launch['manifest']==result['manifest'] and launch['review']==result['review'] and review['manifest']==result['manifest'] and review['verdict']=='PASS','execution review/custody')
    return dict(item_id=p.ITEM,status='PASS',compile_attempts=3,failed_compile_attempts=2,
                comparisons=6,histories=12,requests=25,execution=replay,
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
       observed_scientific_wall_seconds= science['elapsed_seconds'],
       manual_engineering_review_seconds=None,unmeasured_note='Reading, implementation, review and manual diagnosis were not captured by paired monotonic intervals; their duration is unknown, never zero.',
       preparation_incidents=['Sandbox /bin/ps EPERM then successful escalated host preflight.',
                              'Sandbox curl DNS failure then exact successful read-only fetch.'],
       policy='Counts/time are observations only; no terminal attempt/time caps.')

def validate_closure():
    replay=validate(); result=p.read(p.BASE/'result.json'); closure=p.read(p.BASE/'closure.json')
    p.require(p.read(p.BASE/'evidence-replay.json')==replay,'stored replay differs')
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
    return replay
