"""Bind required closure checks, retained failure and final durable state."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from lib.cvc_a7_runner import CODE, FIXED, MANIFEST, BASE as PROOF_BASE, OUT
from lib.cvc_conditional_evidence import validate
base = Path(__file__).resolve().parents[1]
research = ROOT / 'results/research/conditional-validation-contracts/cvc-conditional-1'
load = lambda p: json.loads(p.read_text())
def binding(p):
    return {'path': str(p.relative_to(ROOT)), 'bytes': p.stat().st_size,
            'sha256': hashlib.sha256(p.read_bytes()).hexdigest()}
required = ['04-a7-final-pure', '05-final-bind', '06-final-evidence', '09-historical',
            '10-snapshot', '11-contribution', '12-catalog', '13-old-runner', '14-old-proof',
            '15-full-tests', '17-closure-repaired', '18-final-queue', '19-final-queue-tests',
            '20-final-refresh', '21-review', '22-artifacts']
for name in required:
    row = load(base / (name + '.json'))
    assert row['status'] == 'PASS' and row['returncode'] == 0 and row['tested_input_bindings_unchanged']
    assert hashlib.sha256((ROOT / row['log']).read_bytes()).hexdigest() == row['log_sha256']
work, result, entry = (load(research / (p+'.json')) for p in ('work-record', 'result', 'entry-review'))
assert not (ROOT / PROOF_BASE).exists() and not (ROOT / OUT).exists()
queue = load(ROOT / 'config/research-queue.json')
rows = {r['id']:r for r in queue['items']}
assert queue['selected_item'] == 'CVC-3-CONDITIONAL' and rows['CVC-3-CONDITIONAL']['status'] == 'READY'
assert rows['CVC-CONDITIONAL-1']['closure']['outcome'] == 'SUCCESS'
assert rows['CVC-4']['status'] == 'PLANNED' and rows['CVC-4']['depends_on'] == ['CVC-3']
assert rows['CVC-5']['status'] == 'PLANNED'
for path in [MANIFEST, *CODE, *FIXED]:
    historical = subprocess.check_output(['git', 'show', entry['implementation_checkpoint']+':'+path], cwd=ROOT)
    assert historical == (ROOT/path).read_bytes(), path
validation = validate(ROOT, full=False, closure=True)
text = (base/'15-full-tests.log').read_text()
counts = [int(x) for x in re.findall(r'^Ran (\d+) tests', text, re.M)]
assert counts == [534,73] and not re.search(r'^FAILED|\.\.\. skipped', text, re.M)
full = load(base/'15-full-tests.json')
assert full['fixtures_reconciled'] and full['fixture_launches'] == 23
now = datetime.now(timezone.utc)
elapsed = (now-datetime.fromisoformat(work['started_at'])).total_seconds()
admin = (now-datetime.fromisoformat(work['ended_at'])).total_seconds()
assert 0 <= elapsed <= 3600  # all work and administrative closure fit the first session ceiling
paths = ['config/research-queue.json','docs/RESEARCH_STATUS.md','docs/PROJECT_REVIEW.md',
         'docs/PUBLIC_STATUS.md','results/research/project-review.json','results/artifacts/graph.json',
         'results/research/queue-reviews/2026-09-07-cvc-conditional-1.json']
paths += [str(p.relative_to(ROOT)) for p in research.iterdir() if p.is_file()]
summary = {'schema_version':1,'item_id':'CVC-CONDITIONAL-1','status':'PASS','validated_at':now.isoformat(),
           'implementation_checkpoint':entry['implementation_checkpoint'],
           'checks':[binding(base/(p+'.json')) for p in required],
           'tests':{'current':534,'historical':73,'total':607,'skipped':0,'new_a7_pure':19},
           'scientific_status':'PROTOCOL_PREPARED_BASELINE_UNEXECUTED',
           'research_operations':work['research_operations'],
           'research_and_required_test_active_seconds':work['active_seconds'],
           'administrative_closure_elapsed_seconds':admin,
           'total_elapsed_including_closure_seconds':elapsed,
           'budget_compliance':{'elapsed_within_first_3600_second_session_ceiling':True,
                                'reserved_fixture_launches':23,'launch_cap':64,
                                'reserved_fixture_seconds':115,'reserved_seconds_cap':320,
                                'actual_fixture_charge_seconds':full['fixture_charged_seconds']},
           'retained_failures':[{'check':binding(base/'16-closure.json'),'raw_script_failure':binding(base/'close-item-failure.log'),
                                'cause':'Nested script omitted repository import path at the final manifest step.',
                                'repair':'Preserved completed state, added import path, completed only missing manifest tail; closure passes.',
                                'resolved_by':binding(base/'17-closure-repaired.json')}],
           'prior_unknown_fixture_duration':None,'prior_failed_fixture_cap_compliance':'NOT_ESTABLISHED',
           'unchanged_history':'Original CVC2 inputs, original terminal CVC3 and old runner/process inputs remain hash-identical; historical-transition suite passes.',
           'broader_assurance_gate':'Pre-existing FAIL preserved; no scientific result or new disagreement claim.',
           'final_closure_bindings':[binding(ROOT/p) for p in sorted(paths)],
           'validation_tool_sources':[binding(p) for p in sorted((base/'validation-tools').glob('*.py'))],
           'next_item':'CVC-3-CONDITIONAL','next_item_status':'READY_UNSTARTED',
           'accounting_note':'All implementation, required fixtures/tests and administrative closure elapsed time remains within the first 60-minute ceiling. Git delivery follows; no next-item workspace, session, ledger, baseline, proof or observer launch started.'}
target=base/'validation.json'
assert not target.exists(), 'Do not overwrite a completed validation record'
target.write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps({'status':'PASS','tests':607,'fixture_reservations':23,'total_seconds':elapsed,'next':'CVC-3-CONDITIONAL READY_UNSTARTED'}))
