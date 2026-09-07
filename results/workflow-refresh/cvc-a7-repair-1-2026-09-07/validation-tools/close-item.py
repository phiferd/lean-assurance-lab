"""Record the checked A7 repair outcome and select its unstarted mapping successor."""
import json
from pathlib import Path
import sys

root = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(root))
from lib import cvc_a7_repair_runner as runner
from lib.cvc_a7_repair_evidence import validate_run

base = Path(runner.WORK).parent
review_path = 'results/research/queue-reviews/2026-09-07-cvc-a7-repair-1.json'
next_item = 'CVC-4-CONDITIONAL'

def dump(path, value):
    (root / path).write_text(json.dumps(value, indent=2) + '\n')

summary = validate_run(root)
summary.pop('payloads_verified')
assert summary['run_outcome'] == 'SUCCESS'
state = json.loads((root / runner.OUT / 'execution/state.json').read_text())['state']
audit = state['attempts'][-1]['terminal']['axiom_audit']
receipt = lambda path: runner.receipt(root, root / path)
result = {
    'schema_version': 1, 'item_id': runner.ITEM, 'run_id': runner.RUN, 'contract_id': 'CVC-U1-A7',
    'outcome': 'SUCCESS', 'scientific_status': 'CHECKED_CONDITIONAL_LAB_PROOF', 'summary': summary,
    'protocol': receipt(runner.MANIFEST), 'execution_protocol': receipt(base / 'execution-protocol.json'),
    'predecessor_result': receipt('results/research/conditional-validation-contracts/cvc-3-conditional/result.json'),
    'work_record': receipt(runner.WORK), 'result_declarations': audit['declarations'],
    'transitive_axioms': audit['transitive_axioms'],
    'stop': {'kind': 'completed_proof', 'reason': 'Fresh counted signature and exact baseline passed; first proof attempt checked all four unchanged original Lab targets.',
             'evidence': [receipt(Path(runner.OUT) / 'attempts/03' / name) for name in
                          ('CVC2Proof.lean', 'stdout', 'stderr', 'supervisor.json')],
             'attempted_repairs': ['Strict universe-aware transcript parser and wrapped type headers; two generated style-linter options.',
                                   'Name lookup simplification; explicit Supported proofs and comparator completeness for acceptance.',
                                   'Versioned controller, cumulative accounting watermark, committed activation and retained process reconciliation.'],
             'remaining_options_blocked': []},
    'nonclaims': ['The seven-assumption envelope is conditional; no helper assumption or consistency claim is discharged.',
                  'No arbitrary-byte parser, importer or executable-validator refinement is proved.',
                  'Pinned source/runtime correspondence and all earlier failed evidence retain their existing boundaries.',
                  'No observer, dependency build, research network request or upstream message ran.'],
    'recommendation': {'next_item': next_item, 'action': 'Map this checked conditional result to exact artifact bytes and at most two implementation lineages under an explicit successor protocol.',
                       'status': 'READY_UNSTARTED', 'external_action': 'None; later upstream actions require exact owner approval.'}}
dump(base / 'result.json', result)

report = f'''# CVC-A7-REPAIR-1 — checked conditional bridge

Outcome: **SUCCESS**, under conditional model `CVC-U1-A7`.

The repaired parser accepted a fresh counted baseline with all nine independent
type pairs and both exact seven-assumption comparator reports. The first proof
attempt then checked the original `EncodingTarget`, `PreservationTarget`,
`AcceptanceTarget` and `BoundaryTarget`. The two positive examples and the zero
and unowned-name rejection boundaries are included in those fixed obligations.

`encoding_preserves` uses `propext` and `Quot.sound`. The other three Lab results
use exactly the reviewed seven assumptions. No `sorryAx`, new axiom, target
change or native-evaluation trust was introduced. The signature and original
meaning are unchanged. See [result](result.json), [proof](run-0002/attempts/03/CVC2Proof.lean)
and [raw axiom reports](run-0002/attempts/03/stdout).

The immediate blockers were engineering defects: universe-decorated names,
wrapped transcript headers, generated style warnings, lookup simplification and
missing decidability instances. The source repair uses existing completeness
lemmas and explicit propositions. New accounting checks also prevent erasing
previously observed work. Forty-four focused checks passed before any new Lean
launch; failed mocked-test setup output remains in `engineering-diagnostics/`.
All old attempts, parsers, contracts, allowlists and historical results remain
unchanged; the earlier baseline failure was not retroactively accepted.

The item used {summary['attempts']} builds (signature, baseline, proof),
{summary['active_seconds']:.6f} active seconds including all engineering work,
and {summary['compilation_seconds']:.6f} compiler seconds. A7 totals including the
prior failed run are {summary['combined_a7_attempts']} builds and
{summary['combined_a7_active_seconds']:.6f} active seconds, below six builds and
7200 seconds. Including original CVC-3, seven builds were consumed. One remaining
build is unused and this successful run is terminal. No resource cap caused the
stop. Administrative closure and its bounded inert test fixtures are separately
recorded in the [validation record](../../../workflow-refresh/cvc-a7-repair-1-2026-09-07/validation.json).

This proves a structured model connection under the named assumptions. It does
not prove arbitrary-byte decoding, importer behavior, executable validator
refinement, runtime correspondence, or the assumptions themselves. The next
item, `CVC-4-CONDITIONAL`, is READY and unstarted: connect the checked statement
to exact artifact bytes and implementation behavior. The original CVC-4 remains
PLANNED because its original CVC-3 SUCCESS dependency is still unmet. No upstream
action is supported solely by this local proof.
'''
(root / base / 'report.md').write_text(report)

queue_path = root / 'config/research-queue.json'
queue = json.loads(queue_path.read_text())
assert queue['selected_item'] == runner.ITEM
before = [row['id'] for row in queue['items']]
completed = next(row for row in queue['items'] if row['id'] == runner.ITEM)
refs = [str(base / name) for name in ('result.json', 'report.md', 'work-record.json')] + [review_path]
reason = 'A checked conditional bridge now exists. The highest-value next question is whether exact artifact and implementation behavior matches this scoped model; further proof polishing has lower information value. Upstream access has no new confirmed evidence, and broader themes remain deferred.'
completed['status'] = 'COMPLETE'
completed['closure'] = {'outcome': 'SUCCESS', 'evidence_refs': refs,
    'recommendation': 'Select CVC-4-CONDITIONAL READY and unstarted to connect the checked conditional bridge to exact artifacts and implementations. Preserve all assumptions and predecessor failures.'}
successor = {
    'id': next_item, 'priority': completed['priority'] + 1,
    'title': 'Connect the checked conditional bridge to real validation behavior',
    'target': 'CVC-U1-A7 owned-name level fragment, at most two implementation lineages and four fixed candidate/control pairs',
    'action': 'Bind exact artifact/implementation mappings and a finite successor protocol, then explain the fixed observed comparison using the checked conditional result.',
    'expected_value': 'Establishes the practical reach and remaining adapter boundary of the first checked Lab bridge.',
    'rank_rationale': reason,
    'entry_gate': 'CVC-A7-REPAIR-1 SUCCESS. Before any new validator launch, commit exact bytes, versions, expected hypotheses, source/runtime mapping, tested launch controller and finite matrix. Keep assumptions explicit; no inherited terminal run may resume.',
    'completion': 'Reproducible source-to-contract mapping and exact finite raw outcomes, or a characterized adapter boundary with a useful ecosystem recommendation. Testing instances does not prove refinement.',
    'stop_condition': 'At most 16200 actual active seconds across recorded intervals of at most 90 minutes, four fixed pairs, two implementation lineages and 16 validator launches of at most 30 seconds. No broad fuzzing or semantic expansion. Bind any setup/fixture/dependency budget before launches; no implicit additional allowance. Same-item engineering repair preserves all counters and fixed scientific inputs.',
    'kind': 'IMPLEMENTATION', 'status': 'READY', 'depends_on': [runner.ITEM],
    'budget': {'max_sessions': 3, 'session_minutes': 90, 'checker_launches': 16},
    'evidence_refs': refs + ['docs/research/CONDITIONAL_VALIDATION_CONTRACTS_PLAN.md', runner.MANIFEST],
    'issue_urls': [], 'closure': None, 'blocked_reason': ''}
queue['items'].insert(queue['items'].index(completed) + 1, successor)
for number, row in enumerate(queue['items'], 1):
    row['priority'] = number
    if row['id'] == 'CVC-4':
        row['rank_rationale'] = 'Original CVC-3 SUCCESS dependency remains unmet. The usable A7 result is handled only by explicit CVC-4-CONDITIONAL; original history and dependency are unchanged.'
queue.update(selected_item=next_item, updated_at='2026-09-07')
dump('config/research-queue.json', queue)
review = {
    'schema_version': 1, 'date': '2026-09-07', 'frontier_id': queue['frontier_id'],
    'stopped_item': runner.ITEM, 'outcome': 'SUCCESS', 'scientific_status': result['scientific_status'],
    'before': {'ordering': before, 'selected_item': runner.ITEM},
    'after': {'ordering': [row['id'] for row in queue['items']], 'selected_item': next_item},
    'reason': reason, 'entry_gate_decisions': [{'item': next_item, 'decision': 'PROMOTE_READY',
        'reason': successor['entry_gate'], 'not_started': True}],
    'candidate_review': [{'id': next_item, 'disposition': 'READY', 'reason': reason},
       {'id': 'CVC-4', 'disposition': 'RETAIN_PLANNED', 'reason': 'Preserve unmet original CVC-3 SUCCESS dependency.'},
       {'id': 'OPS-UPSTREAM-1', 'disposition': 'RETAIN_CLOSED', 'reason': 'No new access or feedback evidence; historical authentication failure remains.'},
       {'id': 'ALT-SURVIVORS', 'disposition': 'RETAIN_DEFERRED', 'reason': 'The checked result makes the finite implementation mapping more directly informative.'},
       {'id': 'ALT-TRANSFER', 'disposition': 'RETAIN_DEFERRED', 'reason': 'New semantic scope and dependency costs remain less feasible.'}],
    'literature_review': {'decision': 'CURRENT_NO_NEW_SEARCH', 'reason': 'The pinned source/reuse and assumption review remain applicable. No new method or semantic fragment was introduced.'},
    'waiting_review': 'No research GET, polling, upstream message or authorization change. Existing external blockers remain unchanged.',
    'recommendation': result['recommendation'], 'evidence_refs': refs[:-1],
    'budget': summary, 'stop': 'Only CVC-A7-REPAIR-1 completed after the requested policy checkpoint. CVC-4-CONDITIONAL is selected READY and unstarted; no successor protocol, workspace or launch exists.'}
dump(review_path, review)
print('Recorded checked result and selected CVC-4-CONDITIONAL unstarted')
