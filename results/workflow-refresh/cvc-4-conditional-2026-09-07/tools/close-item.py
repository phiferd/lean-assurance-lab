"""Close the characterized frozen-byte boundary and select an unstarted input-boundary review."""
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from lib.cvc4_artifacts import BASE
from lib.cvc4_evidence import validate
from lib.cvc4_runner2 import WORK, validate_run, stamp, elapsed


def dump(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')


run = validate_run(ROOT)
assert not run['matrix_complete'] and run['hypothesis_mismatch'] and not run['control_stop']
assert run['launch_count'] == 10 and not run['pending']
assert run['combined_launch_count'] == 12
work_path = ROOT / WORK
work = json.loads(work_path.read_text())
assert work['status'] == 'ACTIVE' and work['intervals'][-1]['end'] is None
end = stamp()
interval = work['intervals'][-1]
interval['end'] = end
interval['charged_seconds'] = elapsed(interval['start'], end)
work.update(status='CLOSED', outcome='BOUNDED_UNRESOLVED', closure_started=end['at'],
            active_seconds_closed=sum(r['charged_seconds'] for r in work['intervals']),
            research_operations={'validator_launches': 12, 'setup_builds': 0, 'research_network_requests': 0})
work['repair_pauses'][-1]['status'] = 'DIAGNOSED_FROZEN_BYTE_BOUNDARY'
dump(work_path, work)
summary = validate(ROOT, require_full_payload=True, write=True)
result = json.loads((ROOT / BASE / 'result.json').read_text())
queue_path = ROOT / 'config/research-queue.json'
queue = json.loads(queue_path.read_text())
before = {'ordering': [r['id'] for r in queue['items']], 'selected_item': queue['selected_item']}
assert queue['selected_item'] == 'CVC-4-CONDITIONAL'
item = next(r for r in queue['items'] if r['id'] == queue['selected_item'])
assert item['status'] == 'ACTIVE'
review_path = 'results/research/queue-reviews/2026-09-07-cvc-4-conditional.json'
item['status'] = 'COMPLETE'
item['closure'] = {'outcome': 'BOUNDED_UNRESOLVED', 'evidence_refs': [BASE + '/result.json', BASE + '/report.md',
                  BASE + '/work-record.json', review_path],
                  'recommendation': 'Select CVC-4-ADAPTER-REVIEW for an existing-evidence scientific-input boundary proposal or stop decision; no new byte generation or observer execution is authorized.'}
item['rank_rationale'] = 'Two fixed pairs completed; the ownership control exposed a missing declared-parameter level record before Nanoda typechecking. No same-byte/binary repair remains. Both pauses and all twelve charges are preserved; input-boundary review has value before any new scientific inputs.'
next_item = dict(next(r for r in queue['items'] if r['id'] == 'CVC-5'))
next_item.update(id='CVC-4-ADAPTER-REVIEW', priority=item['priority']+1,
    title='Decide the frozen-byte adapter boundary using existing evidence',
    target='The unused declared-parameter serialization/import prerequisite in CVC-U1-A7',
    action='Review an explicit scientific-input successor proposal versus stopping. Define intended representation change, retained invariants, reuse value and finite entry conditions; do not generate byte variants or launch anything.',
    expected_value='Determines whether resolving the remaining ownership comparison adds useful evidence beyond the completed right-successor and zero pairs and existing Arena contribution.',
    rank_rationale='The diagnosed gap needs a scientific-byte transition rather than another same-input tooling repair. One existing-evidence decision has greater immediate value than blind retries, success-only packaging or a new semantic family.',
    entry_gate='CVC-A7-REPAIR-1 SUCCESS and documented CVC-4-CONDITIONAL BOUNDED_UNRESOLVED closure with required checks. Existing evidence only; current six streams, hypotheses and observer binaries remain frozen.',
    completion='A justified stop/no-additional-action decision or exact scientific-input successor proposal with value, prerequisites, finite cap and explicit entry gate; rank the next useful action without executing it.',
    stop_condition='At most 3600 cumulative active seconds in one interval; existing evidence only. Zero byte-variant generation, observer/proof/setup/research-network launches and external actions.',
    kind='CONTRACT', status='READY', depends_on=['CVC-A7-REPAIR-1'],
    budget={'max_sessions': 1, 'session_minutes': 60, 'checker_launches': 0},
    evidence_refs=[BASE + '/result.json', BASE + '/report.md', BASE + '/adapter-boundary.json',
                   'results/research/conditional-validation-contracts/cvc-a7-repair-1/result.json',
                   'docs/research/CONDITIONAL_VALIDATION_CONTRACTS_PLAN.md'], closure=None, blocked_reason='')
assert not any(r['id'] == next_item['id'] for r in queue['items'])
index = queue['items'].index(item) + 1
queue['items'].insert(index, next_item)
for rank, row in enumerate(queue['items'], 1):
    row['priority'] = rank
queue.update(selected_item=next_item['id'], updated_at='2026-09-07')
review = {'schema_version': 1, 'date': '2026-09-07', 'frontier_id': queue['frontier_id'],
          'stopped_item': item['id'], 'outcome': 'BOUNDED_UNRESOLVED', 'before': before,
          'after': {'ordering': [r['id'] for r in queue['items']], 'selected_item': next_item['id']},
          'reason': next_item['rank_rationale'], 'budget': result['summary'],
          'entry_gate_decisions': [{'item': next_item['id'], 'decision': 'PROMOTE_READY',
                                   'reason': next_item['entry_gate'], 'not_started': True}],
          'candidate_review': [{'id': next_item['id'], 'disposition': 'READY', 'reason': next_item['rank_rationale']},
              {'id': 'CVC-4', 'disposition': 'RETAIN_PLANNED', 'reason': 'Original CVC-3 SUCCESS dependency remains unmet.'},
              {'id': 'CVC-5', 'disposition': 'RETAIN_PLANNED', 'reason': 'Original CVC-4 dependency remains unmet; conditional path is explicit.'},
              {'id': 'OPS-UPSTREAM-1', 'disposition': 'RETAIN_CLOSED', 'reason': 'No new access repair or owner feedback; retain waiting prerequisite and Kiota deferral.'},
              {'id': 'ALT-SURVIVORS', 'disposition': 'RETAIN_DEFERRED', 'reason': 'One input-boundary decision has immediate value; separate survivor authorization remains absent.'},
              {'id': 'ALT-TRANSFER', 'disposition': 'RETAIN_DEFERRED', 'reason': 'A new semantic family is outside current authority and less immediately useful than the characterized input-boundary decision.'}],
          'literature_review': {'decision': 'CURRENT_NO_NEW_SEARCH', 'reason': 'The 2026-09-06 reuse assessment and A7 assumption review remain applicable; only a fixed implementation connection and diagnostic repair were added.'},
          'waiting_review': 'No research GET, upstream polling or message. Existing access and authorization blockers remain unchanged.',
          'phase_decision': result['phase_decision'], 'no_action_recommendation': result['external_action'],
          'recommendation': result['recommendation'], 'evidence_refs': item['closure']['evidence_refs'][:-1],
          'stop': 'Only CVC-4-CONDITIONAL completed. CVC-4-ADAPTER-REVIEW selected READY and unstarted; no scientific-input transition or success-only contribution stage started.'}
dump(ROOT / review_path, review)
dump(queue_path, queue)
status_path = ROOT / 'docs/RESEARCH_STATUS.md'
status = status_path.read_text()
s = result['summary']
attempted = f'''- Completed `CVC-4-CONDITIONAL` on 2026-09-07 with `BOUNDED_UNRESOLVED`
  at a characterized frozen-byte/importer boundary. The right-successor and zero
  pairs completed: Nanoda accepted E-POS while official Lean refused it, and both
  refused the zero-invalid candidate after accepted controls. Nanoda's ownership
  control failed in parsing because unused declared `v` lacks a parameter-level
  record. Neither ownership candidate ran. The parser error is not a model
  counterexample or ownership rejection. No same-byte/binary repair remains.
  Original reporting failure and all twelve charges remain preserved, with four
  launch slots unused, {s['active_seconds']:.6f} active seconds and
  {s['process_seconds']:.6f} process seconds. No setup or research-network launch
  ran. See the [result](../{BASE}/result.json), [report](../{BASE}/report.md),
  [adapter diagnosis](../{BASE}/adapter-boundary.json), [review](../{review_path})
  and [validation](../results/workflow-refresh/cvc-4-conditional-2026-09-07/validation.json).
  `CVC-4-ADAPTER-REVIEW` is selected READY and unstarted. A7 and refinement gaps
  remain explicit; withdrawn imax defect recommendations remain withdrawn.

'''
status = status.replace('## Attempted\n\n', '## Attempted\n\n' + attempted, 1)
status = status.replace('Selected next item: `CVC-4-CONDITIONAL`.', 'Selected next item: `CVC-4-ADAPTER-REVIEW`.')
start = status.index('`CVC-4-CONDITIONAL` is selected ACTIVE.')
end = status.index('`CVC-RUNNER-2` remains SUCCESS', start)
status = status[:start] + f'''`CVC-4-CONDITIONAL` is COMPLETE with `BOUNDED_UNRESOLVED`. The fixed
right-successor and zero pairs completed under A7: official Lean refused E-POS,
Nanoda accepted it, and both refused the zero-invalid candidate after accepting
controls. Both parsers preserve raw imax. Nanoda's comparator simplifies its
right-successor case to max. Internal C++ comparator bytes and executable
refinement remain unproved; no invalid accepted proof is demonstrated.

The ownership comparison is unresolved. Official accepted its control, but
Nanoda failed before typechecking because the stream declares unused `v`
without a parameter-level record. Neither ownership candidate ran. Diagnosis
found no configuration repair that preserves both frozen scientific bytes and
observer binaries. A wrapper would change observed bytes; rebuilding would
change the pinned binary and exceed the zero-build allowance. This is an
explicit scientific-input boundary, not a semantic rejection or an automatic
stop for an undiagnosed tooling error. Original evidence remains unchanged.

The initial two-launch reporting pause was repaired within the same item by
disabling only axiom printing. Its two charges plus ten revised launches total
12/16, with {s['active_seconds']:.6f}/16200 active seconds and
{s['process_seconds']:.6f} process seconds. Four slots remain unused. No setup or
research-network launch ran. See the [result](../{BASE}/result.json),
[adapter diagnosis](../{BASE}/adapter-boundary.json) and [review](../{review_path}).

`CVC-4-ADAPTER-REVIEW` is selected READY and unstarted. One existing-evidence
review, capped at 3600 active seconds, must decide a justified stop or an exact
scientific-input successor proposal with value, prerequisites and finite entry
conditions. It authorizes no byte-variant generation, proof/observer/setup or
research-network launch. Original CVC-4 and CVC-5 remain PLANNED under their unmet
original dependencies. No success-only contribution stage is promoted, and
withdrawn imax defect recommendations remain withdrawn.

''' + status[end:]
status_path.write_text(status)
plan = ROOT / 'docs/research/CONDITIONAL_VALIDATION_CONTRACTS_PLAN.md'
text = plan.read_text()
text += f'''
## Frozen-byte adapter boundary handoff — 2026-09-07

CVC-4-CONDITIONAL closed `BOUNDED_UNRESOLVED` after two complete pairs and a
source-characterized ownership-control parser failure. Its
[stopping review](../../{review_path}) makes the immediate no-external-action
and phase decision; it does not promote original CVC-5 or defer required closure.
No repair preserves the selected bytes and pinned observer binaries. Adding a
parameter-level record preserves the structured AST but changes the exact
scientific artifact, so a distinct input-boundary decision must precede it.

Select **CVC-4-ADAPTER-REVIEW**, READY and unstarted, for one existing-evidence
review capped at 3600 actual active seconds. Decide a justified stop or exact
scientific-input successor proposal, including scientific identity, intended
representation change, expected value, reuse alternatives, prerequisites,
finite cap and entry conditions. Generate no byte variant, run no observer,
proof, setup or research-network process, and perform no external action.
Preserve every existing artifact, failure, charge, assumption and withdrawn
recommendation. This narrowly ranked decision stays in the conditional phase;
it activates no new comparison or semantic family. Original CVC-4/CVC-5
requirements remain unchanged. Only CVC-4-CONDITIONAL closes in this work.
'''
plan.write_text(text)
print(json.dumps(summary))
