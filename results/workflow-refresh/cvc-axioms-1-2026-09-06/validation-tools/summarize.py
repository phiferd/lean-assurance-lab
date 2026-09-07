"""Persist completed closure checks and separately measured regression costs."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[4]
BASE = Path(__file__).resolve().parents[1]


def load(path):
    return json.loads(Path(path).read_text())


def bind(path):
    data = path.read_bytes()
    return dict(path=str(path.relative_to(ROOT)), bytes=len(data),
                sha256=hashlib.sha256(data).hexdigest())


checks = []
for path in sorted(BASE.glob('[0-9][0-9]-*.json')):
    value = load(path)
    if isinstance(value, dict) and 'command' in value:
        assert value['returncode'] == 0, path
        assert bind(ROOT / value['log'])['sha256'] == value['log_sha256']
        checks.append(bind(path))
assert len(checks) == 15
work = load(ROOT / 'results/research/conditional-validation-contracts/cvc-axioms-1/work-record.json')
text = (BASE / '11-full-tests.log').read_text()
counts = [int(n) for n in re.findall(r'^Ran (\d+) tests in ', text, re.M)]
assert len(counts) == 2 and text.count('\nOK\n') == 2
assert 'skipped=' not in text

ledger_path = BASE / 'required-regression-fixtures/fixture-ledger.jsonl'
rows = [json.loads(line) for line in ledger_path.read_text().splitlines()]
reserved = [r for r in rows if r['kind'] == 'RESERVED']
terminal = [r for r in rows if r['kind'] == 'TERMINAL']
assert [r['number'] for r in reserved] == [r['number'] for r in terminal]
assert all(r['source_bindings_unchanged'] for r in terminal)
previous = '0' * 64
for row in rows:
    value = dict(row)
    digest = value.pop('event_sha256')
    assert row['previous_sha256'] == previous
    encoded = json.dumps(value, sort_keys=True, separators=(',', ':')).encode()
    assert hashlib.sha256(encoded).hexdigest() == digest
    previous = digest
for row in terminal:
    for file in row['files']:
        assert bind(ledger_path.parent / file['path'])['sha256'] == file['sha256']

prep_path = BASE / 'required-preparation-fixtures.jsonl'
prep = [json.loads(line) for line in prep_path.read_text().splitlines()]
assert len(prep) % 2 == 0
for i in range(0, len(prep), 2):
    assert prep[i]['kind'] == 'RESERVED' and prep[i+1]['kind'] == 'TERMINAL'
    assert prep[i]['test'] == prep[i+1]['test']
    assert 0 <= prep[i+1]['charged_seconds'] <= prep[i]['reserved_seconds']

end = datetime.now(timezone.utc)
closure_seconds = (end - datetime.fromisoformat(work['ended_at'])).total_seconds()
closure_paths = [
    'config/research-queue.json', 'docs/RESEARCH_STATUS.md', 'docs/PROJECT_REVIEW.md',
    'results/research/project-review.json', 'results/artifacts/graph.json',
    'results/research/conditional-validation-contracts/cvc-axioms-1/assessment.json',
    'results/research/conditional-validation-contracts/cvc-axioms-1/evidence-manifest.json',
    'results/research/queue-reviews/2026-09-06-cvc-axioms-1.json',
]
result = dict(schema_version=1, item_id='CVC-AXIOMS-1', status='PASS',
    validated_at=end.isoformat(), checks=checks,
    tests=dict(current=counts[0], historical=counts[1], total=sum(counts), skipped=0),
    scientific_status='SOURCE_ASSUMPTION_REVIEW_ONLY', assumptions=7, source_files=6,
    research_operations=work['research_operations'],
    research_active_seconds=work['total_active_seconds'],
    administrative_closure_elapsed_seconds=closure_seconds,
    total_elapsed_including_closure_seconds=work['total_active_seconds'] + closure_seconds,
    required_regression_fixtures=dict(
        supervised_reserved_processes=sum(r['processes'] for r in reserved),
        supervised_charged_seconds=sum(r['charged_seconds'] for r in terminal),
        preparation_reserved_launches=sum(r['reserved_launches'] for r in prep if r['kind'] == 'RESERVED'),
        preparation_charged_seconds=sum(r['charged_seconds'] for r in prep if r['kind'] == 'TERMINAL'),
        accounting_note='Required unchanged repository regression checks, instrumented in new validation ledgers. No research fixture, proof, dependency or observer launch occurred. The test-family label does not resume CVC-RUNNER-2. Ordinary test-harness/Git subprocesses are administrative checks, not proof attempts.',
        evidence=[bind(ledger_path), bind(prep_path)]),
    prior_failed_fixture_actual_duration=None,
    prior_failed_fixture_cap_compliance='NOT_ESTABLISHED',
    final_closure_bindings=[bind(ROOT / p) for p in closure_paths],
    validation_tool_sources=[bind(p) for p in sorted((BASE / 'validation-tools').glob('*.py'))],
    next_item='CVC-CONDITIONAL-1', next_item_status='READY_UNSTARTED',
    accounting_note='Source review ended at its supported decision. Administrative closure includes pure evidence tooling, required unchanged instrumented regression fixtures, queue/report refresh and verification. Git delivery follows separately. Independent review overlapped the owner session; no unknown worker duration is invented or added as another session.')
(BASE / 'validation.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(dict(status='PASS', tests=result['tests'],
                     next_item=result['next_item'], fixture_costs=result['required_regression_fixtures'])))
