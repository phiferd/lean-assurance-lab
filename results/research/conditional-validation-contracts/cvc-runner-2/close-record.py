import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[4]))
from datetime import datetime,timezone
from lib.cvc_prep import read_events
from lib.cvc_fixture_budget import totals
from lib.cvc_runner2_evidence import _legacy
from lib.cvc_runner2 import binding,MANIFEST,RUN
from lib.cvc_process import atomic
root=Path(__file__).resolve().parents[4];base=root/'results/research/conditional-validation-contracts/cvc-runner-2'
checkpoint=sys.argv[1]
import subprocess
assert subprocess.run(['git','cat-file','-e','HEAD:results/research/conditional-validation-contracts/cvc-runner-2/result.json'],cwd=root,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode != 0, 'Historical closure cannot be regenerated; use an explicit successor.'
work=json.loads((base/'work-record.json').read_text());end=datetime.now(timezone.utc).isoformat()
work.update(status='COMPLETE',ended_at=end);work['sessions'][-1]['ended_at']=end
active=sum((datetime.fromisoformat(r['ended_at'])-datetime.fromisoformat(r['started_at'])).total_seconds() for r in work['sessions'])
work['active_seconds']=active
work['closure_note']='All implementation, instruction updates and required validation counted in this session; subsequent git delivery is administrative.'
atomic(base/'work-record.json',work)
a=totals(read_events(base/'fixture-ledger.jsonl'));b=_legacy(base/'validation-fixture-ledger.jsonl')
logs=root/'results/workflow-refresh/cvc-runner-2-2026-09-06';checks=[];full=[]
for p in sorted(logs.glob('*.json')):
 r=json.loads(p.read_text())
 if not p.stem.endswith('-start') and r.get('status')=='PASS' and r.get('returncode')==0 and 'command' in r:
  checks.append(str(p.relative_to(root)))
  if r['command']==['scripts/run-unit-tests','--require-full-payload']:full.append(str(p.relative_to(root)))
prior=json.loads((base.parent/'cvc-runner-1/result.json').read_text())['costs']
result={'schema_version':1,'item_id':'CVC-RUNNER-2','outcome':'SUCCESS','scientific_outcome':'NO_PROOF_ATTEMPTS',
 'implementation_checkpoint':checkpoint,'manifest':binding(root,MANIFEST),'run_id':RUN,
 'fixture_processes':a[0]+b[0],'fixture_process_seconds':a[1]+b[1],'active_seconds':active,
 'supervised_fixture_processes':a[0],'supervised_fixture_process_seconds':a[1],
 'predecessor_validation_fixture_processes':b[0],'predecessor_validation_fixture_process_seconds':b[1],
 'proof_attempts':0,'checker_launches':0,'lean_launches':0,'signature_elaborations':0,'dependency_compilations':0,
 'research_network_requests':0,'validation_receipts':checks,'final_source_validation_receipts':full[-1:],
 'prior_costs_unchanged':prior,'aggregate_preparation_and_runner_active_seconds':prior['aggregate_runner_and_preparation_active_seconds']+active,
 'prior_failed_fixture_actual_duration':None,'prior_failed_fixture_cap_compliance':'NOT_ESTABLISHED',
 'accounting_scope':'New supervised runner fixtures plus separately instrumented unchanged dependency-preparation regression fixtures. Normal validation harness/git subprocesses and unrelated existing regression tests are recorded by the full suite, not item experiment launches.',
 'recommendation':{'action':'Select CVC-3 READY after separate entry review; stop without executing it.',
 'target':'CVC3-U1-PROOF-0001 fixed universe contract','priority':'HIGHEST_ELIGIBLE_NEXT',
 'prerequisites':['Committed exact implementation checkpoint','SUCCESS CVC-2 specification and CVC-PREP-2 complete bundle','Separate committed entry review'],
 'scientific_boundary':'Conditional model target remains unchecked. First signature elaboration is counted attempt 1 of 12.'},
 'additional_evidence':['results/research/queue-reviews/2026-09-06-cvc-runner-2.json']}
import re
latest=json.loads((root/full[-1]).read_text())
counts=[int(n) for n in re.findall(r'^Ran (\d+) tests in ',(root/latest['log']).read_text(),flags=re.MULTILINE)]
assert len(counts)==2
result['tests']={'current':counts[0],'historical':counts[1],'total':sum(counts),'skipped':0}
assert 'OK (skipped=' not in (root/latest['log']).read_text()
atomic(base/'result.json',result)
print(json.dumps({'active_seconds':active,'fixture_processes':a[0]+b[0],'fixture_process_seconds':a[1]+b[1],'final':full[-1:]}))
