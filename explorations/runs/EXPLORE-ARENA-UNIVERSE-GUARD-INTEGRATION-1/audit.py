"""Audit four scoped observations, separating prior setup failures."""
import hashlib, json
from pathlib import Path
P=Path(__file__).resolve().parent
rows=json.loads((P/'observations-r2/executions.json').read_text())
assert len(rows)==4
for row in rows:
    ident,checker=row['case'],row['checker']
    d=P/'observations-r2'/(ident+'-'+checker)
    stdout=(d/'stdout.log').read_text(); stderr=(d/'stderr.log').read_text()
    expected=1 if ident=='candidate' and checker=='lean' else 101 if ident=='candidate' else 0
    assert row['exit_code']==expected
    if checker=='lean':
        assert 'NAME LAL_P1\n' in stdout
        assert ('PARAMS '+('u' if ident=='control' else '')+'\n') in stdout
        assert 'TYPE (sort (succ u))\nVALUE (sort u)\n' in stdout
    if ident=='control':
        assert stderr==''
        assert ('Accepted 1 declaration; empty environment; trust level 0.' if checker=='lean' else 'Checked 1 declarations with no errors') in stdout
    elif checker=='lean':
        assert "invalid reference to undefined universe level parameter 'u'" in stderr
    else:
        assert 'src/tc.rs:554:13' in stderr
        assert 'assertion failed: self.ctx.all_uparams_defined(l, declar_info.uparams)' in stderr
for case in json.loads((P/'cases.json').read_text()):
    assert hashlib.sha256((P/'inputs'/(case['id']+'.ndjson')).read_bytes()).hexdigest()==case['sha256']
assert json.loads((P/'discovery/result.json').read_text())['static_file_copy']=='PASS'
assert len(json.loads((P/'staged-preflight-r2.json').read_text()))==4
failed=list((P/'observations').glob('*/execution.json'))
assert len(failed)==2 and all(json.loads(f.read_text())['exit_code']==1 for f in failed)
result=dict(evidence_class='E0', outcome='NO_SIGNAL', integration='PASS',
    final_cells=4, expected_rejections=2, valid_control_accepts=2,
    actual_checker_launches=6, excluded_missing_file_launches=2,
    unresolved_engineering_failures=False,
    checker_seconds=sum(r['elapsed_seconds'] for r in rows),
    target_revision=(P/'target-revision.txt').read_text().strip(),
    candidate_patch_sha256=hashlib.sha256((P/'candidate.patch').read_bytes()).hexdigest(),
    interpretation='Known-case local integration succeeds on retained profiles; no unexpected validator behavior. Not independent fault evidence or current Arena full-matrix compatibility.')
(P/'result.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
