"""Evidence replay without launching a compiler or scientific observer."""
import json
from pathlib import Path
from lib import lazy_reduction_pilot as p
from lib import lazy_reduction_science as s

def validate():
    source=p.load(p.BASE/'source-r1.json')
    p.verify(source['original_inventory']); p.verify(source['patch'])
    for row in p.load(p.SOURCE_LOCK)['source_entries']:
        if p.digest(p.ROOT/row['path'])!=row['sha256']: raise ValueError('historical source differs')
        data=(p.ROOT/row['path']).read_text()
        for old,new in p.PATCHES.get(row['repository_path'],[]):
            if data.count(old)!=1: raise ValueError('patch source changed')
            data=data.replace(old,new)
        import hashlib
        expected=next(x for x in source['files'] if x['path']==str(p.SOURCE/row['repository_path']))
        if expected['bytes']!=len(data.encode()) or expected['sha256']!=hashlib.sha256(data.encode()).hexdigest():
            raise ValueError('materialized source binding differs from exact archived transform')
        if (p.ROOT/expected['path']).exists(): p.verify(expected)
    for attempt,expected_code in [('build-0001',1),('build-0002',0)]:
        result=p.load(p.BASE/attempt/'result.json'); p.verify(result['manifest']); p.safe(result['receipt']); p.raw(result['receipt'])
        if result['receipt']['exit_code']!=expected_code: raise ValueError('build history changed')
        manifest=p.load(Path(result['manifest']['path']))
        for row in manifest['tooling']: p.verify(row)
        for row in manifest['scan_receipts']:
            scan=p.load(Path(p.verify(row).relative_to(p.ROOT))); p.raw(scan); p.safe(scan)
    _,cap=s.capability()
    for row in cap['tooling']: p.verify(row)
    doc,audit=s.audit_artifacts(); m=p.load(s.EXECUTION); s.validate_manifest(m)
    p.verify(m['source'])
    successful=p.load(p.BASE/'build-0002/result.json')
    if m['binary']!=successful['binary'] or m['build_result']!=p.bind(p.BASE/'build-0002/result.json'):
        raise ValueError('successful build/binary binding differs')
    if (p.ROOT/m['binary']['path']).exists(): p.verify(m['binary'])
    for row in m['tooling']: p.verify(row)
    result=p.load(p.BASE/'science-0001/result.json')
    if result['manifest']!=p.bind(s.EXECUTION) or len(result['cells'])!=12: raise ValueError('scientific result matrix differs')
    counts=[]
    for i,(row,cell) in enumerate(zip(result['cells'],s.cells()),1):
        if row!=p.load(p.BASE/'science-0001'/f'cell-{i:02d}.json') or row['cell']!=cell: raise ValueError('cell receipt differs')
        artifact=m['artifacts'][cell['artifact_id']]
        if row['input_before']!=artifact or row['input_after']!=artifact: raise ValueError('custody differs')
        stdout,stderr=p.raw(row['receipt']); p.safe(row['receipt'])
        expected_argv=[str(p.ROOT/m['binary']['path']),'--engine',cell['engine'],'--jobs','1',str(p.ROOT/artifact['path'])]
        if row['receipt']['argv']!=expected_argv or row['receipt']['cwd']!=str(p.ROOT): raise ValueError('actual invocation differs')
        case=next(x for x in doc['cases'] if x['case_id']==cell['artifact_id'])
        observation=s.classify(row['receipt'],stdout,stderr,case,len(p.verify(artifact).read_bytes().splitlines()))
        qualification=s.demand(observation,stderr,cell['engine'],case)
        if observation!=row['observation'] or qualification!=row['demand']: raise ValueError('scientific replay differs')
        counts.append({'cell_id':cell['cell_id'],'verdict':observation['verdict'],'demand':qualification,'machine':observation.get('machine')})
    if result['acceptance_matched']!=all(x['verdict']=='ACCEPT' for x in counts): raise ValueError('acceptance result incorrect')
    if result['demand_qualified']!=all(x['demand']=='PASS' for x in counts): raise ValueError('demand result incorrect')
    if result['actual_process_count']!=12: raise ValueError('process count differs')
    return dict(item_id=p.ITEM,status='PASS',build_attempts=2,capability_cells=4,scientific_cells=12,
      acceptance_matched=result['acceptance_matched'],demand_qualified=result['demand_qualified'],cells=counts,
      historical_source='UNCHANGED',launches_during_validation=0)

def validate_closure():
    replay=validate()
    if p.load(p.BASE/'evidence-replay.json')!=replay: raise ValueError('derived evidence replay differs')
    result=p.load(p.BASE/'result.json'); closure=p.load(p.BASE/'closure.json'); account=p.load(p.BASE/'work-accounting.json')
    for key,path in [('execution_manifest',s.EXECUTION),('matrix',p.BASE/'science-0001/result.json'),('capability',s.CAPABILITY),
                     ('contract',s.CONTRACT),('audit',s.AUDIT),('replay',p.BASE/'evidence-replay.json')]:
        if result[key]!=p.bind(path): raise ValueError('derived result binding differs')
    if (result['outcome']!='SUCCESS' or result['scientific_result']!='PRESERVED_ACCEPTANCE_WITH_DEMAND'
        or result['scientific_cells']!=12 or result['accepted_cells']!=12 or result['qualified_kam_cases']!=6
        or not replay['acceptance_matched'] or not replay['demand_qualified']): raise ValueError('derived result contradicts observations')
    if (closure['result']!=p.bind(p.BASE/'result.json') or closure['accounting']!=p.bind(p.BASE/'work-accounting.json')
        or closure['outcome']!=result['outcome'] or closure['successor']!=result['successor']
        or closure['successor_started'] is not False or result['successor_execution']!='NOT_STARTED'):
        raise ValueError('closure binding or successor differs')
    scans=[p.load(p.BASE/'dependency-scan-0002'/f'{name}.json') for name in p.UNITS]
    builds=[p.load(p.BASE/x/'result.json')['receipt'] for x in ['build-0001','build-0002']]
    cap=p.load(s.CAPABILITY); sci=p.load(p.BASE/'science-0001/result.json')
    observers=[x['receipt'] for x in cap['cells']+sci['cells']]
    expected=dict(dependency_scan_processes=len(scans),build_attempts=len(builds),failed_build_attempts=1,
      capability_cells=len(cap['cells']),scientific_cells=len(sci['cells']),total_checker_processes=len(observers),
      supervised_processes=len(scans+builds+observers),scientific_files_generated=len(p.load(s.AUDIT)['rows']),
      dependency_scan_seconds=sum(x['elapsed_seconds'] for x in scans),build_seconds=sum(x['elapsed_seconds'] for x in builds),
      checker_seconds=sum(x['elapsed_seconds'] for x in observers),total_supervised_seconds=sum(x['elapsed_seconds'] for x in scans+builds+observers),
      positive_rss_samples=sum(x['memory_monitor_samples'] for x in scans+builds+observers),
      every_supervised_process_cleanup_complete=all(x['cleanup_complete'] for x in scans+builds+observers),
      maximum_single_process_observed_rss_bytes=max(x['maximum_observed_rss_bytes'] for x in scans+builds+observers))
    if any(account.get(k)!=v for k,v in expected.items()): raise ValueError('derived accounting differs')
    return replay

if __name__=='__main__': print(json.dumps(validate(),indent=2))
