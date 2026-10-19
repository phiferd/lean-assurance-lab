"""Small local application of the existing sentinel's exact-identity contract.

The older sentinel is bound to its own True fixture. This adapter adds the
external request/process bindings; it is not a general receipt framework.
"""
import gzip
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text())
def exists(p): return p.exists() or p.with_suffix(p.suffix+'.gz').exists()
def sha(p):
    h=hashlib.sha256()
    stream=p.open('rb') if p.exists() else gzip.open(p.with_suffix(p.suffix+'.gz'),'rb')
    with stream as f:
        for chunk in iter(lambda:f.read(1024*1024),b''): h.update(chunk)
    return h.hexdigest()
NANODA='5e99b44c8b371ca1aedbc1a609a391ca5ac61b834b14fa60871298affb23d962'

def check(directory, expected, fresh_id):
    result=read(directory/'consumer-result.json')
    events=[json.loads(x) for x in (directory/'executions.jsonl').read_text().splitlines()]
    failures=[]
    if result['case']!=fresh_id: failures.append('FAIL_FRESH_EXECUTION_IDENTITY')
    config=read(directory/'config.json')
    if config['theorem_names']!=['OAI.WitnessedChoice.main']:
        failures.append('FAIL_REQUESTED_TARGET')
    if config!=expected['config']: failures.append('FAIL_BOUND_CONFIG_IDENTITY')
    if not config['enable_nanoda']: failures.append('FAIL_REQUESTED_CHECKER_SET')
    if read(directory/'source-hashes.json')!=expected['sources']:
        failures.append('FAIL_BOUND_SOURCE_DEPENDENCY_IDENTITY')
    if sha(directory/'challenge.ndjson')!=expected['challenge_sha256']:
        failures.append('FAIL_TRUSTED_CHALLENGE_IDENTITY')
    solution=directory/'solution.ndjson'
    digest=sha(solution) if exists(solution) else None
    if digest!=expected['solution_sha256']:
        failures.append('FAIL_CHECKED_ARTIFACT_IDENTITY')
    nano=[e for e in events if e['executable_sha256']==NANODA]
    if not any(e['event']=='invoked' for e in nano): failures.append('FAIL_NANODA_NOT_INVOKED')
    if not any(e['event']=='completed' and e['exit_code']==0 and
               e.get('artifact_sha256')==digest for e in nano):
        failures.append('FAIL_NANODA_COMPLETION')
    log=directory/'stdout.log'
    text=log.read_text() if log.exists() else gzip.decompress(log.with_suffix('.log.gz').read_bytes()).decode()
    if result['exit_code']!=0 or 'Lean default kernel accepts the solution' not in text:
        failures.append('FAIL_LEAN_COMPLETION')
    # The pinned Comparator source calls Lean kernel replay directly. Its process
    # exit and stream are observed; there is no second Lean child invocation.
    return {'case':fresh_id,'native_exit_code':result['exit_code'],
            'native_success_output':'Your solution is okay!' in text,
            'native_nanoda_accept_output':'nanoda kernel accepts the solution' in text,
            'requested_execution_matched':result['case']==fresh_id,
            'real_nanoda_invoked':any(e['event']=='invoked' for e in nano),
            'real_nanoda_completed':any(e['event']=='completed' for e in nano),
            'checked_artifact_sha256':digest,
            'additional_lal_check':'PASS' if not failures else 'FAIL',
            'failures':failures}

if __name__=='__main__':
    baseline=ROOT/'observations'/'baseline-r3'
    independent=read(ROOT/'independent-request.json')
    assert read(baseline/'source-hashes.json')==independent['sources']
    assert read(baseline/'config.json')==independent['config']
    expected={'requested_target':independent['requested_target'],
              'config':independent['config'],'sources':independent['sources'],
              'challenge_sha256':sha(baseline/'challenge.ndjson'),
              'solution_sha256':sha(baseline/'solution.ndjson')}
    reference=ROOT/'reference-expectation.json'
    if reference.exists(): assert read(reference)==expected
    else: reference.write_text(json.dumps(expected,indent=2)+'\n')
    cases=['baseline-r3','omitted-nanoda','substituted-target','changed-dependency']
    results=[check(ROOT/'observations'/c,expected,c) for c in cases]
    stale=read(ROOT/'stale-control.json')
    results.append(stale)
    (ROOT/'control-results.json').write_text(json.dumps(results,indent=2)+'\n')
    print(json.dumps(results,indent=2))
