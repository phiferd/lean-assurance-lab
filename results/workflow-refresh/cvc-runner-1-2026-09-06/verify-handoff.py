#!/usr/bin/env python3
"""Read-only consistency check for the CVC-RUNNER-1 stopping point."""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from lib.research_queue import load_queue


def check():
    q = load_queue(ROOT)
    rows = {row['id']: row for row in q['items']}
    assert q['selected_item'] == 'CVC-RUNNER-2'
    assert rows['CVC-RUNNER-2']['status'] == 'READY'
    assert rows['CVC-RUNNER-1']['status'] == 'COMPLETE'
    assert rows['CVC-RUNNER-1']['closure']['outcome'] == 'BOUNDED_UNRESOLVED'
    assert all(rows[key]['status'] == 'PLANNED' for key in ('CVC-3', 'CVC-4', 'CVC-5'))
    assert rows['CVC-3']['depends_on'] == ['CVC-2', 'CVC-PREP-2', 'CVC-RUNNER-2']
    out = ROOT / 'results/research/conditional-validation-contracts/cvc-runner-1'
    result = json.loads((out / 'result.json').read_text())
    review = json.loads((ROOT / 'results/research/queue-reviews/2026-09-06-cvc-runner-1.json').read_text())
    assert review['outcome'] == result['outcome'] == 'BOUNDED_UNRESOLVED'
    assert review['after']['selected_item'] == q['selected_item']
    assert review['after']['ordering'] == [row['id'] for row in sorted(q['items'], key=lambda row: row['priority'])]
    assert review['costs'] == result['costs']
    assert result['execution_enabled'] is False
    assert result['costs']['actual_failed_fixture_process_seconds'] is None
    assert result['costs']['failed_fixture_cap_compliance'] == 'NOT_ESTABLISHED'
    proposal = json.loads((out / 'successor-proposal.json').read_text())
    assert proposal['execution_status'] == {'fixture_launches': 0, 'proof_attempts': 0, 'started': False}
    assert not (ROOT / 'external/cvc3-u1-proof-0001').exists()
    assert not (ROOT / 'results/research/conditional-validation-contracts/cvc-3').exists()
    assert not (ROOT / 'results/research/conditional-validation-contracts/cvc-runner-2').exists()
    assert not (ROOT / 'config/cvc-u1-proof-0001.json').exists()
    print('PASS: one unresolved item closed; repair selected unstarted; proof stages remain PLANNED')


if __name__ == '__main__':
    check()
