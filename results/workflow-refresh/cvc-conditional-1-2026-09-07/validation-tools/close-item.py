from pathlib import Path
from datetime import datetime,timezone
import time,json,hashlib,subprocess,sys
sys.path.insert(0, str(Path.cwd()))
root=Path.cwd();base=Path('results/research/conditional-validation-contracts/cvc-conditional-1');val=Path('results/workflow-refresh/cvc-conditional-1-2026-09-07')
if (base/'result.json').exists() or (base/'entry-review.json').exists():
 raise SystemExit('Completed preparation closure is immutable; do not regenerate it')
load=lambda p:json.loads(Path(p).read_text())
write=lambda p,x:Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
binding=lambda p:{'path':str(p),'sha256':hashlib.sha256(Path(p).read_bytes()).hexdigest()}
now=datetime.now(timezone.utc);stamp=now.isoformat();mono=time.monotonic()
full=load(val/'15-full-tests.json');assert full['status']=='PASS' and full['fixtures_reconciled']
checkpoint=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
work=load(base/'work-record.json');session=work['sessions'][-1];session.update(ended_at=stamp,ended_monotonic=mono)
wall=(now-datetime.fromisoformat(session['started_at'])).total_seconds();session['charged_seconds']=max(wall,mono-session['started_monotonic']);assert session['charged_seconds']<=3600
work.update(status='COMPLETE',ended_at=stamp,active_seconds=sum(x['charged_seconds'] for x in work['sessions']),outcome='SUCCESS',stop_reason='Minimal successor controls and bound payloads validated; preserve uncompiled baseline for the separately selected counted proof stage.',implementation_checkpoint=checkpoint,
 delegation=[{'task':'runner_review','model':'gpt-5.6-terra','reasoning':'medium','scope':'read-only design review and tests/test_cvc_a7_runner.py; no launches'},{'task':'baseline_audit','model':'gpt-5.6-terra','reasoning':'medium','scope':'independent source-typed baseline/audit and pure tests; no launches'}],
 fixture_accounting={'reserved_launches':23,'reserved_seconds':115,'charged_seconds':full['fixture_charged_seconds'],'ledger_directory':str(val/'15-full-tests-fixtures'),'prior_unknown_fixture_duration':None,'scope':'Required unchanged process regression fixtures within this item cap; new stage/audit tests are pure mocks.'},
 review_repairs=['Replace inferred expected types with independent source-written annotations.','Generate Baseline.lean from canonical expectation declarations and validate exact source correspondence.','Reject unclaimed transcript output; preserve exact A7 sets and independent per-result subsets.'],
 closure_note='Implementation, source review and full required test run counted in this session. Final queue/report generation, validation and Git delivery are separately timed administrative closure, with zero additional fixture or proof launches.')
write(base/'work-record.json',work)
result={'schema_version':1,'item_id':'CVC-CONDITIONAL-1','outcome':'SUCCESS','scientific_status':'PROTOCOL_PREPARED_BASELINE_UNEXECUTED','model_id':'CVC-U1-A7','implementation_checkpoint':checkpoint,'manifest':binding('config/cvc-u1-a7-proof-0001.json'),'active_seconds':work['active_seconds'],'fixture_reserved_launches':23,'fixture_reserved_seconds':115,'fixture_charged_seconds':full['fixture_charged_seconds'],'proof_builds':0,'dependency_builds':0,'observer_launches':0,'research_network_requests':0,'materially_new_process_machinery':False,'prior_unknown_fixture_duration':None,'prior_preparation_runner_proof_active_seconds':7174.931631292,'combined_preparation_runner_proof_active_seconds':7174.931631292+work['active_seconds'],'validation_receipts':[str(p) for p in sorted(val.glob('*.json')) if not p.name.endswith('-start.json') and not p.name.endswith('-fixture-reservation.json')],'recommendation':{'action':'Execute the newly committed counted signature and imported-type/A7 baseline, then attempt only the original preservation/acceptance/boundary obligations or exact counterexample within six builds.','target':'CVC-3-CONDITIONAL / CVC3-U1-A7-PROOF-0001','priority':1,'prerequisites':['Committed and pushed entry promotion','Exact manifest/payload verification','Signature then exact baseline before proof feedback'],'evidence':['config/cvc-u1-a7-proof-0001.json',str(base/'execution-protocol.json'),str(base/'process-reuse-review.json'),str(val/'15-full-tests.json')],'external_action':'No upstream message or normative-source approval warranted by protocol preparation.'},'nonclaims':['No checked Lab proof or baseline compilation.','No assumption discharge, consistency, source-to-binary proof or executable validator refinement.','No CVC-4 activation; original terminal run and ten unused slots remain unchanged.']}
write(base/'result.json',result)
report=f'''# CVC-CONDITIONAL-1: prepared A7 protocol

Outcome: **SUCCESS** for protocol and runner preparation. Scientific status:
**PROTOCOL_PREPARED_BASELINE_UNEXECUTED**. No Lean, signature, imported baseline,
Lab proof, dependency compilation or observer ran in this item.

The explicit successor `CVC3-U1-A7-PROOF-0001` retains the exact original
Contract.lean, examples and four Lab obligations. Its named model `CVC-U1-A7`
uses the seven source-reviewed host assumptions. Both imported comparator
axiom reports must equal that set exactly; each later Lab result may use a
reported subset. All assumptions remain conditional trust, including the four
helper axioms. Source-to-binary correspondence remains unproved.

The runner enforces two 60-minute sessions and six counted builds of at most
300 seconds. Attempt 1 compiles the unchanged signature. Every subsequent
reservation remains BASELINE until the fixed imported-type and axiom audit
passes; failed reservations reduce the remaining slots. Only then may the
original proof or counterexample mode run. A baseline mismatch stops before
proof feedback. Normally four proof slots remain after signature and baseline.

The canonical expectation declarations generate `Baseline.lean` through
`scripts/render-cvc-a7-baseline`. The later counted baseline prints fully
elaborated imported and expected types under identical options and checks all
nine pairs. The aliases have independent source-written types; they do not
infer expectations from the declarations being audited. The baseline has not
been compiled, so syntax, elaboration and output formatting remain to be
checked by its authorized counted build. Its frozen expectations may not be
weakened after feedback.

No materially new process machinery was added. The successor changes paths,
stages, fixed inputs, audit and caps, while reusing the unchanged process
supervisor, timeout/cleanup engine, locking/WAL primitives and prior process
regressions. The evidence validator checks predecessor source hashes and
identical infrastructure function ASTs. Review corrected independently typed
expectations and the table-to-source generation link before the final test run.

All 19 new A7 tests use mocked compiler calls. The required full-payload suite
passed 607 tests (534 current, 73 unchanged historical; no skips). Its existing
process regressions consumed 23 reserved launches / 115 reserved seconds,
within the 64 / 320 ceiling; measured charge was
{full['fixture_charged_seconds']:.6f} process seconds. Active implementation and
validation time was {work['active_seconds']:.6f} seconds. Final administrative
closure is separately recorded. The earlier unknown fixture duration remains
unknown, and the original failed run's two builds / 199.947382292 active seconds /
2.357550584 compilation seconds remain unchanged.

Recommendation: select **CVC-3-CONDITIONAL** next, under the separately committed
entry review and exact manifest, and stop this turn before beginning its
session or workspace. Its first step is read-only payload verification followed
by its counted signature and baseline. No upstream message, new source approval,
CVC-4 activation or broader assurance claim follows from this preparation.
'''
(base/'report.md').write_text(report)
review_path='results/research/queue-reviews/2026-09-07-cvc-conditional-1.json'
q=load('config/research-queue.json');before={'ordering':[x['id'] for x in q['items']],'selected_item':q['selected_item']}
q['selected_item']='CVC-3-CONDITIONAL';q['updated_at']='2026-09-07'
refs=[str(base/n) for n in ['result.json','report.md','execution-protocol.json','assumptions.json','baseline-expectations.json','work-record.json','process-reuse-review.json','entry-review.json','evidence-manifest.json']]+['config/cvc-u1-a7-proof-0001.json',review_path]
for item in q['items']:
 if item['id']=='CVC-CONDITIONAL-1':
  item['status']='COMPLETE';item['closure']={'outcome':'SUCCESS','evidence_refs':refs,'recommendation':result['recommendation']['action']+' Select CVC-3-CONDITIONAL READY and unstarted; no checked Lab result or external research action.'}
 if item['id']=='CVC-3-CONDITIONAL':
  item['status']='READY';item['entry_gate']='CVC-CONDITIONAL-1 SUCCESS with exact committed implementation checkpoint, manifest and separately committed entry review. Read-only payload verification precedes counted signature, then fixed imported-type/exact-A7 baseline; proof feedback requires both successes.'
  item['rank_rationale']='Highest eligible local item: the minimal conditional protocol is tested, all original semantics and prepared payloads remain bound, and six counted builds cap the first checked bridge attempt. Upstream access remains unconfirmed; pure-normal-form replacement would change strategy, and other themes remain deferred.'
  item['evidence_refs']+=refs[:8]+['config/cvc-u1-a7-proof-0001.json']
write('config/research-queue.json',q)
entry={'schema_version':1,'reviewed_at':stamp,'item_id':'CVC-3-CONDITIONAL','decision':'PROMOTE','run_id':'CVC3-U1-A7-PROOF-0001','implementation_checkpoint':checkpoint,'manifest':binding('config/cvc-u1-a7-proof-0001.json'),'evidence':[str(base/'result.json'),str(val/'15-full-tests.json'),str(base/'process-reuse-review.json')],'entry_gates':{'CVC-CONDITIONAL-1':'SUCCESS: source-bound pure controls and full-payload regression suite pass','CVC-AXIOMS-1':'SUCCESS: source-reviewed seven-assumption conditional envelope','CVC-2':'SUCCESS: exact original unchecked signature/examples retained','CVC-PREP-2':'SUCCESS: exact 37-module/141-product bundle reverified','CVC-RUNNER-2':'SUCCESS: immutable process implementation and prior tests retained'},'proof_execution_started':False,'signature_attempts':0,'baseline_attempts':0,'next_action':'Begin a new CVC-3-CONDITIONAL session only in a subsequent turn. Use scripts/run-cvc-u1-a7-proof verify-inputs, then begin-session and attempt; --resume after the first reserved attempt. Fixed source/type mismatch is terminal before proof feedback.','stop_this_turn':'CVC-CONDITIONAL-1 is the single completed item. Do not start the selected proof item.'}
write(base/'entry-review.json',entry)
review={'schema_version':1,'date':'2026-09-07','frontier_id':q['frontier_id'],'stopped_item':'CVC-CONDITIONAL-1','outcome':'SUCCESS','scientific_status':result['scientific_status'],'before':before,'after':{'ordering':[x['id'] for x in q['items']],'selected_item':q['selected_item']},'reason':next(x['rank_rationale'] for x in q['items'] if x['id']=='CVC-3-CONDITIONAL'),'entry_gate_decisions':[{'item':'CVC-3-CONDITIONAL','decision':'PROMOTE_READY','reason':entry['entry_gates']['CVC-CONDITIONAL-1'],'not_started':True},{'item':'CVC-4','decision':'RETAIN_PLANNED','reason':'Original CVC-3 successful theorem dependency remains unmet; conditional result needs explicit successor.','not_started':True}],'candidate_review':[{'id':x['id'],'disposition':x['status'],'reason':x['rank_rationale']} for x in q['items']],'waiting_review':'Arena disposition access remains last-known blocked after CLI preflight; no fresh feedback or urgency has been supplied. No network research request or polling in this item.','literature_review':{'decision':'CURRENT_NO_NEW_SEARCH','evidence':['results/research/conditional-validation-contracts/cvc-1/assessment.json','results/research/conditional-validation-contracts/cvc-axioms-1/assessment.json'],'reason':'Recent source/reuse review remains applicable to the unchanged model strategy. This item introduces no new semantic method or process machinery.'},'alternative_review':'Pure-normal-form comparator replacement remains lower priority because it changes the strategy and needs a separate assumption audit. Renewed survivor/transfer work remains outside the authorized phase. Existing CVC-4 and CVC-5 dependencies remain unmet.','evidence_refs':refs[:-1],'recommendation':result['recommendation'],'stop':'Selected proof item READY and unstarted; complete at most this one preparation item.'}
write(review_path,review)
p=Path('docs/RESEARCH_STATUS.md');s=p.read_text();i=s.index('\n## Attempted\n')+len('\n## Attempted\n')
summary='''
- Completed `CVC-CONDITIONAL-1` on 2026-09-07 with `SUCCESS` for the minimal
  A7 protocol/runner preparation. No Lean, signature, baseline, Lab proof,
  dependency or observer launch ran. All 607 full-payload tests pass (534
  current and 73 unchanged historical; no skips), including 19 new pure A7
  regressions. The existing process tests consumed 23 reserved launches / 115
  reserved seconds within the 64 / 320 cap. Exact types, seven comparator
  assumptions, original semantic inputs, runner and payloads are bound in the
  [manifest](../config/cvc-u1-a7-proof-0001.json). See the
  [result](../results/research/conditional-validation-contracts/cvc-conditional-1/result.json),
  [report](../results/research/conditional-validation-contracts/cvc-conditional-1/report.md),
  [entry review](../results/research/conditional-validation-contracts/cvc-conditional-1/entry-review.json),
  and [queue review](../results/research/queue-reviews/2026-09-07-cvc-conditional-1.json).
  `CVC-3-CONDITIONAL` is selected READY and unstarted. Its counted baseline
  remains uncompiled; no assumptions are discharged and no Lab result is checked.
  Final administrative closure validation is retained in the
  [validation record](../results/workflow-refresh/cvc-conditional-1-2026-09-07/validation.json).
'''
s=s[:i]+summary+s[i:];s=s.replace('Selected next item: `CVC-CONDITIONAL-1`.','Selected next item: `CVC-3-CONDITIONAL`.')
a=s.index('`CVC-CONDITIONAL-1` is selected READY and unstarted.',s.index('### Active'));b=s.index('`CVC-RUNNER-2` remains SUCCESS',a)
s=s[:a]+'''`CVC-CONDITIONAL-1` is COMPLETE with `SUCCESS` for protocol and minimal runner
preparation, labeled `PROTOCOL_PREPARED_BASELINE_UNEXECUTED`. The new runner
reuses existing process supervision, accounting, timeouts and cleanup, with
successor paths, six-build/two-session limits, and an obligatory audited baseline
stage. No materially new process machinery was introduced. Canonical reviewed
type declarations generate the exact baseline source; both comparator axiom
reports must equal A7, while per-Lab-result reports may use subsets. The
607-test full-payload suite passes; 23 required inert fixture reservations use
115 of the 320 reserved-second cap. No Lean, dependency or observer launch ran.

`CVC-3-CONDITIONAL` is selected READY and unstarted under its separately committed
[entry review](../results/research/conditional-validation-contracts/cvc-conditional-1/entry-review.json).
The exact [manifest](../config/cvc-u1-a7-proof-0001.json) binds new run ID
`CVC3-U1-A7-PROOF-0001`, the original signature/examples, seven assumptions,
source-typed baseline, complete prepared payloads and tested runner. Use
`scripts/run-cvc-u1-a7-proof`. Its bound is six counted builds in two 60-minute
sessions, at most 300 seconds each: signature, exact imported type/axiom
baseline, then normally at most four proof builds. Baseline retries consume
slots and remain baseline until an exact audited success; a fixed-input
mismatch stops before proof feedback. The baseline is still uncompiled and its
first actual elaboration belongs to this later item. These are separate
successor reservations, never the old ten unused slots; original plus proposed
proof builds are at most eight. No session, ledger or workspace for the new
proof run has started. CVC-4/CVC-5 remain PLANNED; a usable conditional result
would require an explicit CVC-4 successor.

'''+s[b:]
s=s.replace('Aggregate recorded preparation/runner/proof active time is 7174.931631292 seconds;', 'Before CVC-CONDITIONAL-1, aggregate preparation/runner/proof active time was 7174.931631292 seconds;')
s=s.replace('Required closure validation costs and regression fixtures are\nreported separately.', f'CVC-CONDITIONAL-1 adds {work["active_seconds"]:.6f} active seconds, for a combined {7174.931631292+work["active_seconds"]:.6f} seconds before its final administrative closure. Its 23 fixture reservations / 115 reserved seconds include the required full-suite fixtures. Final closure time is separately recorded and remains within this item’s total bound. Prior unknown fixture duration stays unknown.')
p.write_text(s)
from lib.cvc_a7_runner import CODE,FIXED,MANIFEST
files={Path(p) for p in CODE}|{Path(p) for p in FIXED}|{Path(MANIFEST)}|{p for p in base.iterdir() if p.is_file() and p.name!='evidence-manifest.json'}
write(base/'evidence-manifest.json',{'schema_version':1,'item_id':'CVC-CONDITIONAL-1','outcome':'SUCCESS','files':[binding(p) for p in sorted(files)]})
print(json.dumps({'checkpoint':checkpoint,'active_seconds':work['active_seconds'],'next':q['selected_item']}))
