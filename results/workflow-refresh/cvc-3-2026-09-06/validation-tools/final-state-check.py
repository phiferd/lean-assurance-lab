"""Read-only queue/review and tested-source consistency for CVC-3 delivery."""
import hashlib
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path.cwd()))
from lib.research_queue import load_queue
from lib.cvc3_evidence import validate_closure

root = Path.cwd()
base = root / 'results/workflow-refresh/cvc-3-2026-09-06'
queue = load_queue(root)
review = json.loads((root / 'results/research/queue-reviews/2026-09-06-cvc-3.json').read_text())
result = json.loads((root / 'results/research/conditional-validation-contracts/cvc-3/result.json').read_text())
assert review['stopped_item'] == result['item_id'] == 'CVC-3'
assert review['outcome'] == result['outcome'] == 'BOUNDED_UNRESOLVED'
assert review['after']['ordering'] == [row['id'] for row in queue['items']]
assert review['after']['selected_item'] == queue['selected_item'] == result['recommendation']['next_item']
selected = next(row for row in queue['items'] if row['id'] == queue['selected_item'])
assert selected['status'] == 'READY' and selected['closure'] is None
assert not (root / 'results/research/conditional-validation-contracts/cvc-axioms-1/work-record.json').exists()
bindings = json.loads((base / '08-full-tests-source-bindings.json').read_text())
for row in bindings:
    assert hashlib.sha256((root / row['path']).read_bytes()).hexdigest() == row['sha256'], row['path']
for path in base.glob('[0-9][0-9]-*.json'):
    value = json.loads(path.read_text())
    if isinstance(value, dict) and 'command' in value:
        assert value['returncode'] == 0, str(path)
        assert hashlib.sha256((root / value['log']).read_bytes()).hexdigest() == value['log_sha256']
summary = validate_closure(root)
print(json.dumps({'status': 'PASS', 'tested_source_bindings_unchanged': len(bindings),
                  'completed_item': result['item_id'], 'outcome': summary['outcome'],
                  'next_item': selected['id'], 'next_status': 'READY_UNSTARTED'}, indent=2))
