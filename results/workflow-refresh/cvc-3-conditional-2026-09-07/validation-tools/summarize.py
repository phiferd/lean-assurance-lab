"""Bind required checks, retained failures, fixture accounting and final durable state."""
from datetime import datetime, timezone
import hashlib, json, re
from pathlib import Path
root=Path(__file__).resolve().parents[4]
base=Path(__file__).resolve().parents[1]
def load(p): return json.loads(p.read_text())
def receipt(p): return {'path':str(p.relative_to(root)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size}
required=['01-closure','02-refresh','03-queue','04-queue-tests','05-historical','06-snapshot','07-contribution','08-catalog','10-portable','11-old-proof-corrected','12-full-tests','13-review','14-artifacts']
checks=[base/(name+'.json') for name in required]
for p in checks:
    r=load(p)
    assert r['status']=='PASS' and r['returncode']==0 and r['tested_input_bindings_unchanged'],p
    assert hashlib.sha256((root/r['log']).read_bytes()).hexdigest()==r['log_sha256'],p
full=load(base/'12-full-tests.json')
assert full['fixtures_reconciled'] and full['fixture_launches']==23
log=(base/'12-full-tests.log').read_text()
counts=[int(n) for n in re.findall(r'^Ran (\d+) tests? in ',log,re.M)]
assert counts==[544,73] and not re.search(r'^OK \(skipped=',log,re.M) and not re.search(r'^FAILED',log,re.M),counts
inputs=load(base/'12-full-tests-start.json')['source_bindings']
for r in inputs: assert hashlib.sha256((root/r['path']).read_bytes()).hexdigest()==r['sha256'],r['path']
result=load(root/'results/research/conditional-validation-contracts/cvc-3-conditional/result.json')
work=load(root/'results/research/conditional-validation-contracts/cvc-3-conditional/work-record.json')
q=load(root/'config/research-queue.json'); assert q['selected_item']=='CVC-A7-REPAIR-1'
next_item=next(i for i in q['items'] if i['id']==q['selected_item']); assert next_item['status']=='READY' and next_item['budget']=={'max_sessions':1,'session_minutes':60,'checker_launches':0}
now=datetime.now(timezone.utc)
closed=datetime.fromisoformat(work['sessions'][-1]['end']['at'])
admin=(now-closed).total_seconds()
paths=[root/p for p in ['config/research-queue.json','docs/RESEARCH_STATUS.md','docs/PROJECT_REVIEW.md','docs/PUBLIC_STATUS.md','results/research/project-review.json','results/artifacts/graph.json','results/research/queue-reviews/2026-09-07-cvc-3-conditional.json']]
paths+=sorted((root/'results/research/conditional-validation-contracts/cvc-3-conditional').glob('*.json'))
record={'schema_version':1,'item_id':'CVC-3-CONDITIONAL','status':'PASS','validated_at':now.isoformat(),'outcome':'BOUNDED_UNRESOLVED','scientific_status':'NO_CHECKED_LAB_RESULT',
        'checks':[receipt(p) for p in checks],'tests':{'current':counts[0],'historical':counts[1],'total':sum(counts),'skipped':0,'new_closure_pure':10},
        'research_operations':work['research_operations'],'research_active_seconds':result['active_seconds'],'compilation_seconds':result['compilation_seconds'],
        'administrative_closure_elapsed_seconds':admin,'activation_to_validation_elapsed_seconds':(now-datetime.fromisoformat(work['activated_at'])).total_seconds(),
        'fixture_accounting':{'batch':receipt(base/'12-full-tests-fixture-reservation.json'),'reserved_launches':23,'launch_cap':46,'reserved_seconds':115,'reserved_seconds_cap':230,'actual_charged_seconds':full['fixture_charged_seconds'],'reconciled':True,'separate_from_research_reservations':True},
        'prior_unknown_fixture_duration':None,'prior_failed_fixture_cap_compliance':'NOT_ESTABLISHED',
        'retained_failures':[{'receipt':receipt(base/'09-old-proof.json'),'log':receipt(base/'09-old-proof.log'),'cause':'Administrative command used unsupported flags; argparse stopped before validation or research launch.','repair':'Used the existing --require-payloads flag with default closure mode.','resolved_by':receipt(base/'11-old-proof-corrected.json')},
          {'command':['scripts/validate-cvc3-a7'],'error':'permission denied: scripts/validate-cvc3-a7','cause':'Parent invoked new draft before executable bit was set.','repair':'Marked the new script executable before validation; no research launch involved.','resolved_by':receipt(base/'01-closure.json')}],
        'unchanged_history':'All 40 bindings in predecessor preparation evidence manifest remain exact; original terminal proof closure and historical publication/snapshot checks pass. Full suite includes historical-transition tests. No frozen validator or evidence was rewritten.',
        'broader_assurance_gate':'Pre-existing FAIL for unresolved semantic disagreements is preserved; generated metrics and dispositions unchanged.',
        'final_closure_bindings':[receipt(p) for p in paths],
        'validation_tool_sources':[receipt(p) for p in sorted((base/'validation-tools').glob('*.py'))],
        'next_item':q['selected_item'],'next_item_status':'READY_UNSTARTED','stop':'Completed only CVC-3-CONDITIONAL. No successor manifest, proof input, session, ledger or workspace created.'}
(base/'validation.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps({'status':'PASS','tests':record['tests'],'fixture_charge':full['fixture_charged_seconds'],'administrative_closure_seconds':admin,'next_item':q['selected_item']}))
