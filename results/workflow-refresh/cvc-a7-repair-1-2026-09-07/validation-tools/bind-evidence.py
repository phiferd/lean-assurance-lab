"""Generate/check the immutable completed-item evidence inventory."""
import hashlib
import json
from pathlib import Path
import sys

root = Path(__file__).resolve().parents[4]
base = root / 'results/research/conditional-validation-contracts/cvc-a7-repair-1'
output = base / 'evidence-manifest.json'
paths = {p for p in base.rglob('*') if p.is_file() and p != output and p.name != 'controller.lock'}
paths |= {root / p for p in (
    'config/cvc-a7-repair-policy.json', 'config/cvc-u1-a7-proof-0002.json',
    'lib/cvc_a7_repair_audit.py', 'lib/cvc_a7_repair_runner.py', 'lib/cvc_a7_repair_evidence.py',
    'scripts/bind-cvc-u1-a7-repair', 'scripts/run-cvc-u1-a7-repair',
    'scripts/render-cvc-a7-repair-baseline', 'scripts/validate-cvc-a7-repair',
    'tests/test_cvc_a7_repair_audit.py', 'tests/test_cvc_a7_repair_runner.py',
    'tests/test_cvc_a7_repair_evidence.py',
    'research/conditional-validation-contracts/cvc-a7-repair/Baseline.lean',
    'research/conditional-validation-contracts/cvc-a7-repair/Proof.lean',
    'results/research/queue-reviews/2026-09-07-cvc-a7-repair-1.json')}
paths.add(Path(__file__).resolve())
value = {'schema_version': 1, 'item_id': 'CVC-A7-REPAIR-1', 'outcome': 'SUCCESS',
         'frozen': True, 'files': [{'path': str(p.relative_to(root)), 'bytes': p.stat().st_size,
            'sha256': hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(paths)]}
if sys.argv[1:] == ['--check']:
    if json.loads(output.read_text()) != value:
        raise SystemExit('Evidence inventory differs')
elif not sys.argv[1:]:
    if output.exists():
        raise SystemExit('Cannot overwrite completed evidence; use --check')
    output.write_text(json.dumps(value, indent=2) + '\n')
else:
    raise SystemExit('Expected no argument or --check')
print('PASS: ' + str(len(paths)) + ' completed-item evidence bindings')
