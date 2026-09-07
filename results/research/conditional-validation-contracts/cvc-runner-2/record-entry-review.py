import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[4]))
from lib.cvc_process import atomic,now
from lib.cvc_runner2 import binding,MANIFEST,RUN,CODE,FIXED
root=Path(__file__).resolve().parents[4];base=root/'results/research/conditional-validation-contracts/cvc-runner-2';checkpoint=sys.argv[1]
import subprocess
assert subprocess.run(['git','cat-file','-e','HEAD:results/research/conditional-validation-contracts/cvc-runner-2/result.json'],cwd=root,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode != 0, 'Historical closure cannot be regenerated; use an explicit successor.'
entry={'schema_version':1,'reviewed_at':now(),'item_id':'CVC-3','decision':'PROMOTE','run_id':RUN,
 'implementation_checkpoint':checkpoint,'manifest':binding(root,MANIFEST),
 'evidence':['results/research/conditional-validation-contracts/cvc-runner-2/result.json',
 'results/research/conditional-validation-contracts/cvc-runner-2/report.md',
 'results/workflow-refresh/cvc-runner-2-2026-09-06/16-full-final.json'],
 'entry_gates':{'CVC-2':'SUCCESS: fixed unchecked signature/contract/examples/assumptions already committed and pushed',
 'CVC-PREP-2':'SUCCESS: all 37 upstream modules/141 products plus exact full runtime verified; no Lab target compiled',
 'CVC-RUNNER-2':'SUCCESS: supervised protocol controls and required current/historical validation pass against checkpoint inputs'},
 'protocol_interpretations':[
 'Failed start, timeout and interruption consume one attempt slot; durable elapsed receipts account for normal time. Orphans conservatively consume full reserved timeout plus active-time charge.',
 'SUCCESS requires four exact result declarations plus both comparator axiom reports. NEGATIVE checks the exact existential Accepts a and not Contract a, with counterexample and both comparator axiom reports; it does not require the preservation theorem it refutes.',
 'OS/Python/reviewed proof source and local filesystem remain trusted; process supervision is not a hostile-code sandbox.'],
 'proof_execution_started':False,'signature_attempts':0,'next_action':'Begin a CVC-3 design session only when executing the selected next item. The first elaboration is attempt 1 of 12; use scripts/run-cvc-u1-proof-successor.',
 'stop_this_turn':'CVC-RUNNER-2 is the single completed bounded item; do not start CVC-3 in this turn.'}
atomic(base/'entry-review.json',entry)
qp=root/'config/research-queue.json';q=json.loads(qp.read_text());before={'ordering':[r['id'] for r in sorted(q['items'],key=lambda r:r['priority'])],'selected_item':q['selected_item']}
rows={r['id']:r for r in q['items']};r=rows['CVC-RUNNER-2']
refs=['results/research/conditional-validation-contracts/cvc-runner-2/'+n for n in ['result.json','report.md','work-record.json','entry-review.json','evidence-manifest.json']]+['results/research/queue-reviews/2026-09-06-cvc-runner-2.json','config/cvc-u1-proof-0001.json','scripts/validate-cvc-runner2']
r.update(status='COMPLETE',closure={'outcome':'SUCCESS','evidence_refs':refs,'recommendation':'Select CVC-3 READY after committed-input entry review. Start with the exact signature as counted attempt 1 of 12, then attempt the fixed conditional preservation result. No proof ran in this implementation item.'})
r['evidence_refs']=list(dict.fromkeys(r['evidence_refs']+refs))
r['rank_rationale']='Completed protocol-specific successor with cancellation-safe supervision, durable accounting, exact bindings and full declaration/axiom auditing. Preserve CVC-RUNNER-1 unresolved evidence unchanged.'
r=rows['CVC-3'];r.update(status='READY',rank_rationale='Highest eligible local work: fixed contract, complete pinned dependencies and tested committed runner are available. One bounded proof or counterexample can now settle the selected semantic question; upstream access remains unconfirmed and broader alternatives remain deferred.',entry_gate='CVC-2, CVC-PREP-2 and CVC-RUNNER-2 close SUCCESS. The separate entry review binds committed implementation '+checkpoint+' and the exact protocol/signature/examples/allowlist/runtime/commands. Selected READY, unstarted; first signature elaboration is counted attempt 1 of 12 under CVC3-U1-PROOF-0001. Use scripts/run-cvc-u1-proof-successor.')
r['evidence_refs']=list(dict.fromkeys(r['evidence_refs']+refs));q['selected_item']='CVC-3';atomic(qp,q)
review={'schema_version':1,'date':'2026-09-06','frontier_id':q['frontier_id'],'stopped_item':'CVC-RUNNER-2','outcome':'SUCCESS','scientific_status':'NO_PROOF_ATTEMPTS','before':before,'after':{'ordering':before['ordering'],'selected_item':'CVC-3'},'reason':r['rank_rationale'],
 'entry_gate_decisions':[{'item':'CVC-3','decision':'PROMOTE_READY','reason':r['entry_gate'],'not_started':True},{'item':'CVC-4','decision':'RETAIN_PLANNED','reason':'Requires a usable CVC-3 result and a separate fixed observer protocol; no observer launch authorized here.','not_started':True}],
 'candidate_review':[{'id':x['id'],'disposition':x['status'],'reason':x['rank_rationale']} for x in q['items']],
 'waiting_review':'No new upstream access or feedback evidence. OPS-UPSTREAM-1 retains BOUNDED_UNRESOLVED; no GET, poll or external message ran.',
 'literature_review':{'status':'CURRENT_BOUNDED_ASSESSMENT','completed_item':'CVC-1','evidence':'results/research/conditional-validation-contracts/cvc-1/assessment.json','reason':'Same local-date fixed universe fragment and reuse target; no new theory, family or alternative tool adoption.'},
 'evidence_refs':refs[:-3]+['config/cvc-u1-proof-0001.json','scripts/validate-cvc-runner2'],
 'validation_refs':['results/workflow-refresh/cvc-runner-2-2026-09-06/16-full-final.json'],
 'outstanding':'Deliver the single completed runner item and instructions on main; CVC-3 is selected READY but unstarted. Stop.'}
atomic(root/'results/research/queue-reviews/2026-09-06-cvc-runner-2.json',review)
sp=root/'docs/RESEARCH_STATUS.md';s=sp.read_text().replace('Selected next item: `CVC-RUNNER-2`.','Selected next item: `CVC-3`.')
a=s.index('`CVC-RUNNER-1` is COMPLETE with `BOUNDED_UNRESOLVED`.',s.index('### Active'))
b=s.index('`OPS-UPSTREAM-1` remains COMPLETE',a)
s=s[:a]+'''`CVC-RUNNER-2` is COMPLETE with `SUCCESS` for the protocol implementation.
The parent-independent supervisor, source-bound fixture ledger, fixed runtime and
command manifest, signature-first sequencing, crash accounting, terminal-time
budget stops and full axiom parser passed inert control tests and required
current/historical validation. See the
[result](../results/research/conditional-validation-contracts/cvc-runner-2/result.json),
[report](../results/research/conditional-validation-contracts/cvc-runner-2/report.md),
and [stopping-point review](../results/research/queue-reviews/2026-09-06-cvc-runner-2.json).
The instructions now require repair of solvable engineering failures within the
same item and remaining budget, preserving raw failures and assurance gates.

`CVC-RUNNER-1` remains `BOUNDED_UNRESOLVED`; its failed cancellation, orphan,
uninstrumented worker launches and unknown actual duration remain unchanged.
Its original endpoint still refuses execution. `CVC-PREP-2` remains SUCCESS with
37 upstream modules and 141 bound products, including the 119 unchanged
predecessor products. `CVC-PREP-1` remains `BOUNDED_UNRESOLVED`. Combined
preparation cost remains 3030.60362 active seconds and 49.75494 compilation seconds;
runner costs and prior uncertainty are linked in the new result.

`CVC-3` is selected READY and unstarted after the
[separate committed-input entry review](../results/research/conditional-validation-contracts/cvc-runner-2/entry-review.json).
Use `scripts/run-cvc-u1-proof-successor`, begin a design session before proof work,
and retain the fixed CVC3-U1-PROOF-0001 identity and budgets. No signature or proof
has been elaborated. The first elaboration of the unchanged CVC-2 signature is
counted attempt 1 of 12. SUCCESS requires all four exact declarations and six
axiom reports; the separately documented counterexample mode retains NEGATIVE.
CVC-4 and CVC-5 remain conditional PLANNED stages. This handoff does not execute
the next item or authorize observer launches.

'''+s[b:]
s=s.replace('## Attempted\n\n','''## Attempted

- Completed `CVC-RUNNER-2` on 2026-09-06 with `SUCCESS` for the bounded runner
  implementation and instruction repair. Required current/historical checks
  pass; no Lean, signature, proof or checker ran. The exact manifest and
  implementation checkpoint are bound by the
  [entry review](../results/research/conditional-validation-contracts/cvc-runner-2/entry-review.json).
  CVC-3 is selected READY and unstarted. The failed CVC-RUNNER-1 evidence and
  broader assurance disagreements remain unchanged.

''',1)
sp.write_text(s)
print('Recorded separate CVC-3 entry review and next selection; no proof started.')
