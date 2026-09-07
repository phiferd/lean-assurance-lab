"""Preserve cumulative accounting at the selected, unstarted planning handoff."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
path = ROOT / 'config/research-queue.json'
queue = json.loads(path.read_text())
assert queue['selected_item'] == 'CVC-4-ADAPTER-REVIEW'
item = next(x for x in queue['items'] if x['id'] == queue['selected_item'])
assert item['status'] == 'READY' and item['closure'] is None
old = 'At most 3600 cumulative active seconds in one interval; existing evidence only. Zero byte-variant generation, observer/proof/setup/research-network launches and external actions.'
new = 'At most 3600 cumulative active seconds across recorded intervals, each at most 60 minutes; existing evidence only. Zero byte-variant generation, observer/proof/setup/research-network launches and external actions.'
assert item['stop_condition'] == old
item['stop_condition'] = new
path.write_text(json.dumps(queue, indent=2) + '\n')
print(json.dumps({'item': item['id'], 'before': old, 'after': new, 'reason': 'RESEARCH_WORKFLOW permits checkpoints and breaks within the cumulative allocation.', 'not_started': True}))
