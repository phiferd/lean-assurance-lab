"""Record one completed item and its existing-evidence phase-decision successor."""
from datetime import datetime, timezone
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = 'results/research/conditional-validation-contracts/cvc-4-ownership-1'
REVIEW = 'results/research/queue-reviews/2026-09-08-cvc-4-ownership-1.json'
ITEM, NEXT = 'CVC-4-OWNERSHIP-1', 'CVC-5-CONDITIONAL'


def load(p): return json.loads((ROOT / p).read_text())
def dump(p, v): (ROOT / p).write_text(json.dumps(v, indent=2) + '\n')


result = load(BASE + '/result.json')
assert result['outcome'] == 'SUCCESS' and result['research_counts']['observer_launches'] == 4
queue = load('config/research-queue.json')
assert queue['selected_item'] == ITEM and not any(r['id'] == NEXT for r in queue['items'])
before = {'selected_item': ITEM, 'ordering': [r['id'] for r in queue['items']]}
item = next(r for r in queue['items'] if r['id'] == ITEM)
assert item['status'] == 'ACTIVE'
item['status'] = 'COMPLETE'
item['rank_rationale'] = 'The sole insertion repaired the known importer prerequisite. Both fresh controls accepted, then both candidates reached exact ownership refusals. Four new plus twelve retained reservations exhaust the combined sixteen-launch ceiling; no new comparison is selected.'
item['closure'] = {'outcome': 'SUCCESS', 'evidence_refs': [BASE + '/result.json', BASE + '/report.md', BASE + '/work-record.json', REVIEW],
                   'recommendation': 'Reuse the exact local serialization regression. Select CVC-5-CONDITIONAL READY and unstarted for a consolidated existing-evidence package and phase decision; no new observer, proof, byte variant or external action.'}
next_item = {'id': NEXT, 'priority': item['priority'] + 1,
    'title': 'Consolidate the conditional result for reuse and decide the phase',
    'target': 'The checked CVC-U1-A7 bridge, three fixed implementation boundaries, and exact ownership serialization regression',
    'action': 'Use existing evidence to produce one stand-alone reusable entry point and a continue/reuse/redirect/stop phase decision. Evaluate whether a concrete external contribution adds value beyond the local regression and existing Lean/Arena interactions; prepare a draft only when that value is supported.',
    'expected_value': 'Makes the completed conditional bridge and finite limits usable together and prevents another experiment from being selected without comparing marginal value and existing evidence.',
    'rank_rationale': 'The proof and final ownership boundary are now available. A small existing-evidence consolidation directly serves the planned shared-value/phase decision at zero observer cost. A new semantic family lacks authorization and method review; another ownership pair exceeds the fixed comparison; waiting upstream work lacks a new substantive trigger.',
    'entry_gate': 'CVC-A7-REPAIR-1 and CVC-4-OWNERSHIP-1 SUCCESS, with exact result and required closure validation delivered. This is a distinct conditional packaging successor, not satisfaction of original CVC-4/CVC-5 dependencies.',
    'completion': 'One reproducible entry point tying exact conditional theorem, assumptions, streams and raw profile observations to the reusable regression; a concrete target/priority/prerequisite recommendation or justified no-external-action decision; comparative phase decision and ranked next queue.',
    'stop_condition': 'At most 3600 actual active seconds including engineering, recorded intervals at most 60 minutes. Existing evidence only; zero new byte variants, observer/proof/setup/build/research-network launches and external actions. No automatic new formal slice or implementation experiment. Stop with package/decision or explicit evidence/authority gap.',
    'kind': 'CONTRIBUTION', 'status': 'READY', 'depends_on': ['CVC-A7-REPAIR-1', ITEM],
    'budget': {'max_sessions': 1, 'session_minutes': 60, 'checker_launches': 0},
    'evidence_refs': [BASE + '/result.json', BASE + '/report.md', BASE + '/cases.json',
        'results/research/conditional-validation-contracts/cvc-a7-repair-1/result.json',
        'results/research/conditional-validation-contracts/cvc-4-conditional/result.json',
        'results/research/conditional-validation-contracts/cvc-1/assessment.json',
        'docs/UPSTREAM_ISSUES.md', 'tests/test_cvc4_ownership_inputs.py'],
    'issue_urls': [], 'closure': None, 'blocked_reason': ''}
queue['items'].insert(queue['items'].index(item) + 1, next_item)
for n, row in enumerate(queue['items'], 1): row['priority'] = n
queue['selected_item'] = NEXT
queue['updated_at'] = datetime.now(timezone.utc).date().isoformat()
review = {'schema_version': 1, 'recorded_at': queue['updated_at'], 'frontier_id': queue['frontier_id'],
    'stopped_item': ITEM, 'outcome': 'SUCCESS', 'before': before,
    'after': {'selected_item': NEXT, 'ordering': [r['id'] for r in queue['items']]},
    'entry_gate_decisions': [{'item': NEXT, 'decision': 'PROMOTE_READY', 'reason': next_item['entry_gate'], 'not_started': True}],
    'candidate_review': [
        {'id': NEXT, 'disposition': 'READY', 'reason': next_item['rank_rationale']},
        {'id': 'ANOTHER_OWNERSHIP_COMPARISON', 'disposition': 'DO_NOT_SELECT', 'reason': 'Fixed matrix completed and cumulative sixteen reservations consumed. Existing regression already distinguishes importer prerequisite from ownership; no supported need for another pair.'},
        {'id': 'STOP_AND_REUSE', 'disposition': 'INCORPORATE_IN_PHASE_DECISION', 'reason': 'Default scientific direction after this finite slice is reuse; one small consolidation and explicit comparative phase decision improves accessibility without further observations.'},
        {'id': 'CVC-4', 'disposition': 'RETAIN_PLANNED', 'reason': 'Original CVC-3 SUCCESS dependency remains unmet.'},
        {'id': 'CVC-5', 'disposition': 'RETAIN_PLANNED', 'reason': 'Original CVC-4 SUCCESS dependency remains unmet; use only the separately selected conditional successor.'},
        {'id': 'W-LEAN-IMAX-NORMALIZATION', 'disposition': 'WAIT', 'reason': 'Existing declaration-level comment delivered September 8. No new maintainer feedback supplied; retain source-only master comparison and no current-master execution claim.'},
        {'id': 'OPS-UPSTREAM-1', 'disposition': 'RETAIN_CLOSED', 'reason': 'No recorded CLI access repair or new owner feedback; no polling or new network request.'},
        {'id': 'ALT-SURVIVORS', 'disposition': 'RETAIN_DEFERRED', 'reason': 'Separate theme authorization absent; existing contract evidence has a concrete consolidation path.'},
        {'id': 'ALT-TRANSFER', 'disposition': 'RETAIN_DEFERRED', 'reason': 'Separate authorization and fresh independence/method review required.'}],
    'literature_review': {'decision': 'REUSE_CURRENT_BOUND_ASSESSMENT', 'basis': 'September 6 CVC-1 and A7 assumption reviews remain current within 30 days. No new theory, representation or substantial process tool is adopted; new methods need a fresh review before selection.'},
    'waiting_review': 'No fresh upstream GET, access survey or external message. All waiting dispositions remain dated last-known records.',
    'phase_decision': 'Stop scientific launches for this finite slice. Select one existing-evidence consolidation and phase decision; no automatic experiment or broader theme.',
    'recommendation': result['recommendation'], 'no_action_recommendation': result['external_action'],
    'evidence_refs': [BASE + '/result.json', BASE + '/report.md', BASE + '/source-mapping.json', BASE + '/run-0001/events.jsonl'],
    'stop': 'Only CVC-4-OWNERSHIP-1 completes; CVC-5-CONDITIONAL is selected READY and unstarted.'}
dump(REVIEW, review)
dump('config/research-queue.json', queue)
status = ROOT / 'docs/RESEARCH_STATUS.md'; text = status.read_text()
text = text.replace('Selected next item: `CVC-4-OWNERSHIP-1`.', 'Selected next item: `CVC-5-CONDITIONAL`.')
start = text.index('`CVC-4-OWNERSHIP-1` is selected ACTIVE under the exact')
end = text.index('\n\nThe review created no new scientific bytes', start)
text = text[:start] + '''`CVC-4-OWNERSHIP-1` is COMPLETE with `SUCCESS`. The exact sole unused-`v`
level insertion preserves every old byte in order and the fixed name, ordered
parameters, value and type syntax. Both pinned observers accepted fresh owned
controls before either candidate. Official refused unowned `u`; Nanoda reached
the ownership assertion at `tc.rs:520`, beyond its prior `parser.rs:506` failure.
The candidate remains CHECKED_UNSUPPORTED, not a checked invalid proof.

The four new reservations plus twelve preserved predecessor reservations use the
cumulative sixteen-launch ceiling. New process time is 0.13902070792391896 seconds;
combined process time is 0.5252482886426151 seconds. Final active work, including
engineering and closure validation, is recorded in the
[work record](../results/research/conditional-validation-contracts/cvc-4-ownership-1/work-record.json).
No proof, setup or research-network launch ran. See the
[result](../results/research/conditional-validation-contracts/cvc-4-ownership-1/result.json),
[report](../results/research/conditional-validation-contracts/cvc-4-ownership-1/report.md),
[review](../results/research/queue-reviews/2026-09-08-cvc-4-ownership-1.json), and
[validation](../results/workflow-refresh/cvc-4-ownership-1-2026-09-08/validation.json).

`CVC-5-CONDITIONAL` is selected READY and unstarted: one existing-evidence
consolidation and phase decision, capped at 3600 actual active seconds with zero
new byte variants, observer/proof/setup/research-network launches or external
actions. It will tie the checked conditional result, assumptions and finite
boundaries to the reusable local regression and decide the phase's next value.
No further scientific comparison or new semantic family is selected. Original
CVC-4/CVC-5 dependencies remain unchanged.''' + text[end:]
entry = '''- Completed `CVC-4-OWNERSHIP-1` on 2026-09-08 with `SUCCESS`: both pinned
  observers accepted the exact parameter-record control and then refused the
  unowned candidate at their ownership checks. The serializer regression
  preserves predecessor bytes and ASTs; no invalid accepted proof is shown.
  Four new plus twelve old reservations reach the cumulative sixteen-launch
  ceiling; new process time is 0.139021 seconds. See the
  [result](../results/research/conditional-validation-contracts/cvc-4-ownership-1/result.json),
  [report](../results/research/conditional-validation-contracts/cvc-4-ownership-1/report.md),
  [review](../results/research/queue-reviews/2026-09-08-cvc-4-ownership-1.json), and
  [validation](../results/workflow-refresh/cvc-4-ownership-1-2026-09-08/validation.json).
  `CVC-5-CONDITIONAL` is selected READY and unstarted for a bounded
  existing-evidence reuse package and phase decision; no new experiment starts.

'''
text = text.replace('## Attempted\n\n', '## Attempted\n\n' + entry, 1)
status.write_text(text)
plan = ROOT / 'docs/research/CONDITIONAL_VALIDATION_CONTRACTS_PLAN.md'
plan.write_text(plan.read_text() + '''
## Ownership comparison closure and conditional phase decision — 2026-09-08

`CVC-4-OWNERSHIP-1` completed SUCCESS: both fixed controls accepted, and both
candidates reached the exact ownership refusal hypotheses after the sole
parameter-record insertion. This supplies a local reproducible serialization
regression; E-UNOWNED remains outside Supported, not semantically disproved.
Four new plus twelve retained reservations exhaust the sixteen-launch combined
ceiling. Original evidence and conditional assumptions remain unchanged.

The [stopping review](../../results/research/queue-reviews/2026-09-08-cvc-4-ownership-1.json)
selects `CVC-5-CONDITIONAL`, READY and unstarted, as a distinct existing-evidence
successor to the shared-value/phase-decision question. Original CVC-4 and CVC-5
remain PLANNED under unmet original dependencies. This is an explicit ranking
decision after the fixed comparison, not an automatic further experiment.

Use at most 3600 actual active seconds, including engineering, in intervals of
at most 60 minutes. Produce one reusable entry point connecting the exact A7
theorem/assumptions, three finite boundaries, raw observations and regression;
state a concrete external-action recommendation or justified no-action result;
compare continue/reuse/redirect/stop options and select a next item or explicit
authority/state blocker. Use existing evidence only: zero new scientific bytes,
observer/proof/setup/build/research-network launches or external actions. Do not
activate a new semantic family or research theme. Apply the same required
closure validation and handoff procedure; do not start it in this closure.
''')
print('Recorded SUCCESS; selected CVC-5-CONDITIONAL READY and unstarted.')
