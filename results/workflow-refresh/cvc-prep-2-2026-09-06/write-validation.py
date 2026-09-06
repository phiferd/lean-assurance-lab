#!/usr/bin/env python3
"""Summarize the exact successful repair, bounded costs and retained checks."""
import datetime
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
rows = []
for path in sorted(OUT.glob('[0-9][0-9]-*.json')):
    row = json.loads(path.read_text())
    assert hashlib.sha256((ROOT / row['log']).read_bytes()).hexdigest() == row['log_sha256'], path
    rows.append({'record': str(path.relative_to(ROOT)), **row})
required = ['09-final-successor-tests', '12-dependency-execution', '13-historical', '14-snapshot',
            '15-contribution', '16-queue-tests', '17-closure-tests', '18-full-unit-suite', '19-close-evidence',
            '20-final-queue', '21-handoff', '22-evidence-final', '23-predecessor-final', '24-refresh',
            '25-project-review', '26-artifact-status', '27-final-queue', '28-diff']
for name in required:
    assert json.loads((OUT / (name + '.json')).read_text())['status'] == 'PASS', name
assert all(row['status'] == 'PASS' for row in rows)
suite = (OUT / '18-full-unit-suite.log').read_text()
counts = [int(n) for n in re.findall(r'^Ran (\d+) tests in ', suite, re.M)]
assert counts == [435, 73] and not re.search(r'^OK \(skipped=', suite, re.M)
assurance = json.loads((ROOT / 'results/assurance/current.json').read_text())
assert assurance['gate']['status'] == 'FAIL'
assert assurance['gate']['checks']['semantic_checker_disagreements']['observed']['unresolved'] == 15
result = json.loads((ROOT / 'results/research/conditional-validation-contracts/cvc-prep-2/result.json').read_text())
assert result['outcome'] == 'SUCCESS' and result['completed_modules'] == 37
assert result['compilation_attempts'] == 10 and len(result['outputs']) == 141
validation = {'schema_version': 1, 'item_id': 'CVC-PREP-2', 'date': '2026-09-06', 'status': 'PASS',
              'research_outcome': result['outcome'], 'required_final_checks': required, 'commands': rows,
              'unit_suite': {'current_tests': counts[0], 'historical_tests': counts[1], 'total': sum(counts), 'skips': 0,
                             'historical_transition_and_tampering_regressions': 'INCLUDED_AND_PASSING'},
              'prelaunch_tests': result['prelaunch_checks'],
              'preserved_predecessor': {'outcome': 'BOUNDED_UNRESOLVED', 'modules': 27, 'products': 119,
                                        'change': 'UNCHANGED; exact original products copied as inputs, no replay'},
              'preserved_assurance_boundary': {'status': 'FAIL', 'unresolved_semantic_disagreements': 15, 'change': 'UNCHANGED'},
              'refresh': {'status': 'PASS', 'record': str((OUT / 'refresh/result.json').relative_to(ROOT))},
              'costs': result['costs'],
              'research_execution_note': 'Only the fixed ten remaining upstream modules compiled, producing22 new files. The complete37-module/141-product bundle is verified. No Lab elaboration, proof or checker ran. CVC-RUNNER-1 is selected READY and unstarted.',
              'delivery_note': 'Deliver on cvc-prep-2-controller-repair; the earlier main push reported protection exceptions. This repair does not update main or bypass branch protections.',
              'completed_at': datetime.datetime.now(datetime.timezone.utc).isoformat()}
(OUT / 'validation.json').write_text(json.dumps(validation, indent=2) + '\n')
print('PASS: all required checks,508 full-payload tests, complete37-module bundle and unchanged predecessor')
