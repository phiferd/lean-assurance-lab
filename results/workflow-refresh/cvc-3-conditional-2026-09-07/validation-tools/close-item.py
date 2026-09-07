"""Write this run's closure and explicit bounded successor selection; no launches."""
import hashlib, json
from pathlib import Path
root=Path(__file__).resolve().parents[4]
base=Path('results/research/conditional-validation-contracts/cvc-3-conditional')
review_path=Path('results/research/queue-reviews/2026-09-07-cvc-3-conditional.json')
load=lambda p: json.loads((root/p).read_text())
def write(p,v): (root/p).write_text(json.dumps(v,indent=2)+'\n')
def receipt(p):
    data=(root/p).read_bytes()
    return {'path':str(p),'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)}
assert not (root/base/'result.json').exists(), 'Refuse to overwrite completed closure'
state=load(base/'run-0001/execution/state.json')['state']
assert state['outcome']=='BOUNDED_UNRESOLVED' and len(state['attempts'])==2
assert all('end' in s for s in state['sessions'])
active=sum(s['charged_seconds'] for s in state['sessions'])
compilation=sum(a['terminal']['charged_seconds'] for a in state['attempts'])
next_id='CVC-A7-REPAIR-1'
rec={'action':'Repair the transcript audit through an explicit immutable-input successor, then attempt the unchanged conditional obligations only after its committed baseline gates pass.',
     'target':'CVC-U1-A7 fixed types/assumptions and original EncodingTarget, PreservationTarget, AcceptanceTarget, BoundaryTarget',
     'priority':'HIGHEST_ELIGIBLE_NEXT','next_item':next_id,
     'prerequisites':['Preserve CVC3-U1-A7-PROOF-0001 as terminal, including all raw failures, fixed controller and input bytes.',
                     'Use the retained real transcript for pure regressions covering universe-decorated axiom names, wrapped headers and exact known linter diagnostics; reject altered types, axiom additions, missing reports and unknown diagnostics.',
                     'Before any new Lean feedback, bind and commit an explicit successor manifest/controller/baseline and gate review; reuse existing process supervision without changing research semantics.',
                     'At most four new 300-second build reservations: fresh signature, exact audited baseline, then at most two proof attempts. Baseline retries consume these slots. Old plus new A7 builds stay at most six; including original CVC-3, at most eight.',
                     f'Carry the consumed {active} research seconds; at most 3600 additional active seconds in one remaining 60-minute session, including repair work. No dependencies/checkers/research network.',
                     'No proof feedback until the exact type/A7 baseline passes; repair ordinary implementation errors inside the successor while its cap and immutable inputs permit.'],
     'evidence_refs':[str(base/'stop-diagnostic.json'),str(base/'run-0001/attempts/02/stdout'),str(base/'report.md')],
     'external_action':'No upstream issue, message, source approval or scientific contribution is supported by this local parser failure.'}
prior=load(Path('results/research/conditional-validation-contracts/cvc-3/result.json'))
preparation=load(Path('results/research/conditional-validation-contracts/cvc-conditional-1/result.json'))
result={'schema_version':1,'item_id':'CVC-3-CONDITIONAL','run_id':'CVC3-U1-A7-PROOF-0001','model_id':'CVC-U1-A7','outcome':'BOUNDED_UNRESOLVED',
        'scientific_status':'NO_CHECKED_LAB_RESULT','stop_kind':'IMMUTABLE_BASELINE_AUDIT_IMPLEMENTATION_BOUNDARY',
        'input_checkpoint':'40cac6066856a25c8ff5d66691a75b743673ec4a','activation_checkpoint':load(base/'run-0001/start.json')['checkpoint'],
        'manifest':receipt(Path('config/cvc-u1-a7-proof-0001.json')),
        'sessions':len(state['sessions']),'active_seconds':active,'attempts':2,'signature_elaborations':1,
        'baseline_builds':1,'successful_baselines':0,'baseline_compiler_successes':1,'proof_builds':0,'successful_proof_builds':0,
        'compilation_seconds':compilation,'remaining_attempts_unspent':4,'checker_launches':0,'dependency_compilations':0,'research_network_requests':0,
        'prior_costs':{'original_proof_result':receipt(Path('results/research/conditional-validation-contracts/cvc-3/result.json')),
                       'conditional_preparation_result':receipt(Path('results/research/conditional-validation-contracts/cvc-conditional-1/result.json')),
                       'preparation_runner_proof_active_seconds':preparation['combined_preparation_runner_proof_active_seconds'],
                       'compilation_seconds':prior['aggregate_compilation_seconds'],'prior_failed_fixture_actual_duration':None,'prior_failed_fixture_cap_compliance':'NOT_ESTABLISHED',
                       'separate_costs':'Source-assumption-review and predecessor administrative closure remain in their own work/validation records; this aggregate retains the prior published scope.'},
        'aggregate_active_seconds':preparation['combined_preparation_runner_proof_active_seconds']+active,
        'aggregate_compilation_seconds':prior['aggregate_compilation_seconds']+compilation,
        'recommendation':rec,
        'evidence_refs':[str(base/'stop-diagnostic.json'),str(base/'work-record.json'),str(base/'run-0001/execution/events.jsonl'),str(base/'run-0001/execution/state.json')]}
write(base/'result.json',result)
w=load(base/'work-record.json'); w.update(status='COMPLETE',outcome=result['outcome'],sessions=state['sessions'],active_seconds=active,attempts_consumed=2,compilation_seconds=compilation,remaining_attempts_unspent=4,
    research_operations={'signature_builds':1,'baseline_builds':1,'lab_proof_builds':0,'dependency_builds':0,'observer_launches':0,'network_requests':0},
    stopping_reason='Frozen baseline output audit fails after compiler success. Controller and baseline inputs are immutable; repair requires an explicit successor. No counters or terminal receipts changed.',
    administrative_validation={'record':'results/workflow-refresh/cvc-3-conditional-2026-09-07/validation.json','fixture_launch_cap':46,'fixture_reserved_seconds_cap':230,'purpose':'Required closure tests only; separate from research build reservations.'})
write(base/'work-record.json',w)
t=state['attempts'][1]['terminal']
d={'schema_version':1,'item_id':'CVC-3-CONDITIONAL','run_id':result['run_id'],'outcome':result['outcome'],'failed_attempt':2,
   'baseline_audit_error':t['error'],'control_stop':state['control_stop'],
   'stdout':receipt(base/'run-0001/attempts/02/stdout'),'stderr':receipt(base/'run-0001/attempts/02/stderr'),
   'process_outcome':{'status':'COMPLETE','returncode':0,'cleanup_completed':True,'deadline_exceeded':False},'runner_terminal_status':'FAILED',
   'cause':'The frozen pp.universes/pp.all baseline prints universe-annotated axiom identifiers. The audit assumes undecorated identifiers and splits every comma, including commas inside universe argument lists.',
   'additional_incompatibilities':['The TreeMap declaration universe header wraps across a newline forbidden by the type-header regex.',
                                  'Source-positioned linter warnings from typed def declarations remain before the first type report; the diagnostic matcher misses them and the type parser rejects the preamble.'],
   'semantic_interpretation':'Compiler success and visually matching printed types do not satisfy the frozen baseline audit. No new assumption or changed semantic type is established by this engineering failure; no baseline acceptance or checked Lab result is claimed.',
   'repair_attempts':[{'action':'Replay frozen audit on the preserved raw transcript without compilation','result':'Reproduces malformed full axiom list; included in pure closure regression.'},
                      {'action':'Read-only diagnosis of later transcript parsing stages','result':'Identifies independent wrapped-header and linter-preamble failures; diagnostic transformations never authorize proof feedback.'}],
   'blocked_repair_options':[{'action':'Edit the current audit/baseline and retry','blocker':'Both are fixed inputs bound to committed checkpoint; the ledger is terminal. Changing them would invalidate the entry gate and prior evidence.'},
                             {'action':'Retry identical baseline or repair Lab proof','blocker':'Identical baseline deterministically fails the same audit; proof feedback is forbidden until successful audit, and a terminal run cannot reserve another attempt.'},
                             {'action':'Manually accept or alter the raw transcript/axiom envelope','blocker':'Would replace the fixed mechanical gate or frozen evidence; forbidden.'}],
   'feasible_authorized_path':'Complete closure and select an explicit input/controller successor. Preserve consumed budget; remaining four slots are not replayable in this run.'}
write(base/'stop-diagnostic.json',d)
q=load(Path('config/research-queue.json')); before={'ordering':[i['id'] for i in q['items']],'selected_item':q['selected_item']}
item=next(i for i in q['items'] if i['id']=='CVC-3-CONDITIONAL'); item['status']='COMPLETE'
item['closure']={'outcome':'BOUNDED_UNRESOLVED','evidence_refs':[str(base/n) for n in ('result.json','stop-diagnostic.json','work-record.json','report.md')]+[str(review_path)],'recommendation':rec['action']+' Select '+next_id+' READY and unstarted. No checked Lab result or new upstream action.'}
new={'id':next_id,'priority':13,'title':'Repair the fixed baseline audit and finish the bounded conditional bridge',
     'target':rec['target'],'action':rec['action'],'expected_value':'A small transcript compatibility repair can unlock the existing formal question using exact retained compiler evidence and a reduced remaining build allowance.',
     'rank_rationale':'Highest eligible local work: actual baseline output exposes deterministic parser defects, with no scientific counterexample or new semantic gap. A bounded repair retains the original strategy and caps aggregate A7 builds at six. Upstream access is unconfirmed; replacing the semantic strategy or activating other themes has weaker feasibility.',
     'entry_gate':'This stopping-point review authorizes local repair through new paths. Research launches require separately committed and tested successor controller, exact manifest and baseline gate review within this same bounded item. No existing terminal run may resume.',
     'completion':'A new parser/protocol binding with pure transcript and rejection regressions; then checked original obligations, checked counterexample, or bounded unresolved evidence with exact retained costs and next recommendation.',
     'stop_condition':f'One remaining 60-minute session with at most 3600 additional active seconds including repair; four new builds of at most 300 seconds, signature then baseline then normally two proofs. All A7 attempts combined at most six; original CVC-3 plus A7 at most eight. Zero dependency/checker/network launches. Required inert tests are separately reserved and bounded. Stop at true cap, immutable-input/authority boundary or documented unrepairable gap; repair ordinary errors within scope.',
     'kind':'PROOF','status':'READY','depends_on':['CVC-CONDITIONAL-1'],'budget':{'max_sessions':1,'session_minutes':60,'checker_launches':0},
     'evidence_refs':[str(base/'result.json'),str(base/'stop-diagnostic.json'),str(base/'run-0001/attempts/02/stdout'),str(review_path),'config/cvc-u1-a7-proof-0001.json'],
     'issue_urls':[],'closure':None,'blocked_reason':''}
q['items'].insert(12,new)
for n,i in enumerate(q['items'],1): i['priority']=n
q['selected_item']=next_id
next(i for i in q['items'] if i['id']=='CVC-4')['rank_rationale']='Original CVC-3 SUCCESS dependency remains unmet. CVC-3-CONDITIONAL also closed unresolved at its immutable parser boundary. Any later usable CVC-U1-A7 result requires an explicit CVC-4 successor.'
write(Path('config/research-queue.json'),q)
review={'schema_version':1,'date':'2026-09-07','frontier_id':q['frontier_id'],'stopped_item':'CVC-3-CONDITIONAL','outcome':'BOUNDED_UNRESOLVED','scientific_status':'NO_CHECKED_LAB_RESULT',
        'before':before,'after':{'ordering':[i['id'] for i in q['items']],'selected_item':next_id},'reason':new['rank_rationale'],
        'entry_gate_decisions':[{'item':next_id,'decision':'PROMOTE_READY','reason':new['entry_gate'],'not_started':True},{'item':'CVC-4','decision':'RETAIN_PLANNED','reason':'Neither original CVC-3 nor conditional A7 run has a usable checked result.','not_started':True}],
        'candidate_review':[{'id':i['id'],'disposition':i['status'],'reason':i['rank_rationale']} for i in q['items']],
        'waiting_review':'No new Arena feedback or repaired authentication supplied. Preserve last-known access blocker and Kiota deferral; no research GET or polling ran.',
        'literature_review':{'decision':'CURRENT_NO_NEW_SEARCH','evidence':['results/research/conditional-validation-contracts/cvc-1/assessment.json','results/research/conditional-validation-contracts/cvc-axioms-1/assessment.json'],'reason':'The same source/reuse and A7 assumption review applies; repairing transcript syntax introduces no new theory or comparator strategy.'},
        'alternative_review':'Pure normal-form replacement would change the selected strategy and require a new assumption assessment. CVC-4/CVC-5 lack a usable result; survivor/transfer themes remain deferred. Stop/redirect is retained if the reduced repair budget fails to yield a usable bridge.',
        'recommendation':rec,'evidence_refs':[str(base/n) for n in ('result.json','stop-diagnostic.json','report.md','work-record.json')],
        'budget_carry_forward':{'terminal_a7_attempts':2,'proposed_successor_attempts_max':4,'combined_a7_attempts_max':6,'original_cvc3_attempts':2,'all_proof_phase_builds_max':8,'a7_active_seconds_consumed':active,'successor_active_seconds_max':3600,'a7_sessions_consumed':1,'successor_sessions_max':1,'combined_a7_sessions_max':2,'combined_a7_active_seconds_max':active+3600,'counters_reused':False},
        'stop':'Only CVC-3-CONDITIONAL completed this turn. Selected repair successor READY and unstarted; no new successor manifest/workspace/session or proof source created.'}
write(review_path,review)
