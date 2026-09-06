#!/usr/bin/env python3
"""Verify this one-item stop without starting its selected successor."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
def load(rel):return json.loads((ROOT/rel).read_text())
q=load('config/research-queue.json');by={r['id']:r for r in q['items']};out='results/research/conditional-validation-contracts/cvc-prep-1/'
r=load(out+'result.json');review=load('results/research/queue-reviews/2026-09-06-cvc-prep-1.json')
assert q['selected_item']=='CVC-PREP-2' and by['CVC-PREP-2']['status']=='READY'
assert by['CVC-PREP-1']['status']=='COMPLETE' and by['CVC-PREP-1']['closure']['outcome']==r['outcome']=='BOUNDED_UNRESOLVED'
assert r['completed_modules']==r['compilation_attempts']==27 and len(r['outputs'])==119
assert r['stop']['phase']=='BEFORE_RESERVATION_28' and r['stop']['same_paths_sizes_hashes'] and not r['stop']['same_list_order']
assert review['stopped_item']=='CVC-PREP-1' and review['after']['selected_item']==q['selected_item']
assert review['after']['ordering']==[x['id'] for x in sorted(q['items'],key=lambda x:x['priority'])]
assert by['CVC-RUNNER-1']['depends_on']==['CVC-PREP-2'] and by['CVC-3']['depends_on']==['CVC-2','CVC-PREP-2','CVC-RUNNER-1']
for key in ['CVC-RUNNER-1','CVC-3','CVC-4','CVC-5']:assert by[key]['status']=='PLANNED'
assert not (ROOT/'external/cvc-u1-dependencies-0002').exists()
assert not (ROOT/'config/cvc-u1-dependencies-0002.json').exists()
for path in ['lib/cvc_prep.py','tests/test_cvc_prep.py','scripts/prepare-cvc-u1-dependencies','config/cvc-u1-dependencies-0001.json']:
 assert (ROOT/path).read_bytes()==subprocess.check_output(['git','show',r['checkpoint_commit']+':'+path],cwd=ROOT)
for row in load(out+'evidence-manifest.json')['files']:
 data=(ROOT/out/row['path']).read_bytes();assert len(data)==row['bytes'] and hashlib.sha256(data).hexdigest()==row['sha256']
assert r['costs']['lab_elaborations']==r['costs']['proof_attempts']==r['costs']['checker_launches']==0
print('PASS: one bounded unresolved item, immutable27-module checkpoint, CVC-PREP-2 selected but unstarted')
