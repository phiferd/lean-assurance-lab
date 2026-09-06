"""Read-only consistency check at the ALT-PAYLOADS delivery boundary."""
import json
from pathlib import Path
root=Path(__file__).resolve().parents[3]
q=json.loads((root/'config/research-queue.json').read_text())
r=json.loads((root/'results/research/queue-reviews/2026-09-06-alt-payloads.json').read_text())
items={i['id']:i for i in q['items']}
assert r['after']['ordering']==[i['id'] for i in sorted(q['items'],key=lambda i:i['priority'])]
assert r['after']['selected_item']==q['selected_item']=='CVC-PREP-1'
assert r['stopped_item']=='ALT-PAYLOADS' and r['outcome']==items['ALT-PAYLOADS']['closure']['outcome']=='SUCCESS'
assert items['ALT-PAYLOADS']['status']=='COMPLETE'
assert items['CVC-PREP-1']['status']=='READY'
assert not any(i['status']=='ACTIVE' for i in q['items'])
assert not (root/'external/cvc-u1-dependencies-0001').exists()
assert not (root/'scripts/prepare-cvc-u1-dependencies').exists()
assert all(items[i]['status']=='PLANNED' for i in ('CVC-RUNNER-1','CVC-3','CVC-4','CVC-5'))
assert items['CVC-3']['depends_on']==['CVC-2','CVC-PREP-1','CVC-RUNNER-1']
print('PASS: one closed item; exact queue/review agreement; selected successor unstarted; proof gates preserved')
