"""Summarize retained required checks; no tests or research launches."""
import datetime
import hashlib
import json
from pathlib import Path
import re

root = Path(__file__).resolve().parents[4]
base = Path(__file__).resolve().parents[1]
evidence = root / 'results/research/conditional-validation-contracts/cvc-a7-repair-1'

def load(path):
    return json.loads(path.read_text())

def receipt(path):
    return {'path': str(path.relative_to(root)), 'bytes': path.stat().st_size,
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}

required = ['01-closure', '02-queue-tests', '03-historical', '04-snapshot',
            '05-contribution', '14-full-tests-repaired', '15-project-review',
            '16-artifact-status', '09-evidence', '10-prior-a7', '13-signal-repair']
checks = []
for label in required:
    p = base / (label + '.json'); value = load(p)
    assert value['status'] == 'PASS' and value['returncode'] == 0 and value['tested_inputs_unchanged']
    assert receipt(root / value['log']['path']) == value['log']
    checks.append(receipt(p))
fixtures = load(base / '14-full-tests-repaired.json')
assert fixtures['fixtures_reconciled'] and fixtures['fixture_launches'] == 23
counts = re.findall(r'Ran (\d+) tests? in', (base / '14-full-tests-repaired.log').read_text())
assert len(counts) == 2
current, historical = map(int, counts)
assert current == 618 and historical == 73
refresh = load(base / 'final-current-state/result.json')
assert refresh['status'] == 'COMPLETE'
assert len(refresh['completed_commands']) == 13
assert all(command['returncode'] == 0 for command in refresh['completed_commands'])
work = load(evidence / 'work-record.json'); result = load(evidence / 'result.json')
reconciliation = load(base / 'fixture-reconciliation.json')
assert reconciliation['status'] == 'RECONCILED_FOR_CONTINUATION'
assert reconciliation['unknown_actual_seconds'] is None
retry = load(base / '12-full-tests-retry.json')
diagnostics = [load(base / ('signal-diagnostic-' + str(i)) / 'result.json') for i in (1, 2)]
focus = load(base / '13-signal-repair.json')
known_fixtures = (reconciliation['known_actual_seconds'] + retry['fixture_charged_seconds']
    + sum(row['charged_seconds'] for row in diagnostics) + focus['fixture_charged_seconds']
    + fixtures['fixture_charged_seconds'])
now = datetime.datetime.now(datetime.timezone.utc)
portable = base / '11-portable.json'
if portable.exists():
    value = load(portable); assert value['status'] == 'PASS'
    checks.append(receipt(portable))
bindings = [root / path for path in (
    'AGENTS.md', 'docs/AGENT_WORKFLOW.md', 'docs/RESEARCH_WORKFLOW.md',
    'docs/research/CONDITIONAL_VALIDATION_CONTRACTS_PLAN.md',
    'config/research-queue.json', 'docs/RESEARCH_STATUS.md', 'docs/PROJECT_REVIEW.md',
    'docs/PUBLIC_STATUS.md', 'results/research/project-review.json', 'results/artifacts/graph.json')]
record = {
    'schema_version': 1, 'item_id': 'CVC-A7-REPAIR-1', 'status': 'PASS',
    'outcome': 'SUCCESS', 'scientific_status': result['scientific_status'],
    'validated_at': now.isoformat(), 'checks': checks,
    'tests': {'current': current, 'historical': historical, 'total': current + historical,
              'skipped': 0, 'focused_prelaunch': 44, 'new_pure_and_mocked': 74,
              'validation_runtime': 'Explicit bounded Darwin signal retry; unchanged complete original suite and assertions.'},
    'research': result['summary'],
    'administrative_closure_elapsed_seconds': (now - datetime.datetime.fromisoformat(work['closure_started'])).total_seconds(),
    'fixture_accounting': {'reservations': [receipt(base / (label + '-fixture-reservation.json'))
        for label in ('06-full-tests', '12-full-tests-retry', '13-signal-repair', '14-full-tests-repaired')],
        'diagnostic_reservations': [receipt(base / ('signal-diagnostic-' + str(i)) / 'reservation.json') for i in (1, 2)],
        'allocations': [receipt(base / 'additional-validation-allocation.json'), receipt(base / 'signal-repair-validation-plan.json')],
        'reserved_launches': 78, 'launch_cap': 78, 'reserved_seconds': 390,
        'reserved_seconds_cap': 390, 'aggregate_actual_seconds': None,
        'known_instrumented_charge_seconds': known_fixtures,
        'conservative_charged_seconds': known_fixtures + 10 + 15 + 15,
        'failed_reservation_actual_seconds': None, 'failed_reservation_cap_compliance': 'NOT_ESTABLISHED',
        'additional_unknown_descendant_lifetimes': ['12-full-tests-retry fixture06', 'signal-diagnostic-2 fixture01'],
        'final_batch_actual_seconds': fixtures['fixture_charged_seconds'], 'final_batch_reconciled': True,
        'reconciled_for_continuation': True, 'separate_from_research_reservations': True},
    'retained_validation_failures': {'failed_batches': [receipt(base / (label + '.json')) for label in ('06-full-tests','12-full-tests-retry')],
        'failed_diagnostic': receipt(base / 'signal-diagnostic-2/result.json'),
        'reconciliations': [receipt(base / name) for name in ('fixture-reconciliation.json', 'fixture-second-reconciliation.json', 'signal-diagnostic-2/reconciliation.json')],
        'cause': 'Darwin intermittently denied SIGKILL after SIGTERM succeeded and the group leader disappeared. Original supervisor cleanup failures and missing/unknown lifetimes remain unresolved historical facts.',
        'repair': 'A committed explicit validation-runtime adapter retries the same denied signal only while the leader remains absent, with a 50ms cap; failures and cleanup assertions remain strict. Full suite is passed under that prospective runtime, not retroactively in either failed environment.',
        'resolved_by': receipt(base / '14-full-tests-repaired.json')},
    'prior_unknown_fixture_duration': None,
    'prior_failed_fixture_cap_compliance': 'NOT_ESTABLISHED',
    'historical_evidence': 'Original CVC-3 and A7 terminal failures, frozen semantic inputs, tests and assumption decisions are unchanged. Historical transition and snapshot checks pass.',
    'broader_assurance_gate': 'Existing unresolved semantic disagreements remain FAIL; no assurance gate or normative disposition was weakened.',
    'refresh': receipt(base / 'final-current-state/result.json'),
    'evidence_manifest': receipt(evidence / 'evidence-manifest.json'),
    'final_state_bindings': [receipt(p) for p in bindings],
    'validation_tool_sources': [receipt(p) for p in sorted((base / 'validation-tools').glob('*.py'))],
    'portable_clone_check': 'PASS' if portable.exists() else 'PENDING_ADDITIONAL_DELIVERY_CHECK',
    'next_item': 'CVC-4-CONDITIONAL', 'next_item_status': 'READY_UNSTARTED',
    'stop': 'Completed only CVC-A7-REPAIR-1 after the requested policy checkpoint. The selected artifact/implementation successor remains unstarted.'}
(base / 'validation.json').write_text(json.dumps(record, indent=2) + '\n')
print(json.dumps({'status': record['status'], 'tests': record['tests'], 'portable': record['portable_clone_check']}))
