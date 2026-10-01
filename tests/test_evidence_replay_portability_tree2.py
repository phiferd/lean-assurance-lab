"""Narrow custody replay for the confirmed restricted Tree2 model proof."""
import hashlib,json,shutil,subprocess,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
REL=Path("results/research/tree2-confirmed-integration-1")
EXPECTED_SOURCES={'Tree2Bridge.lean': '1b308e9d0d518cdeee1ab704beb2855b8857bbb4792b746ec876b90f7b8cfd68', 'Tree2TowerSupport.lean': '917c998d7311d99d0ee344fa3f01262786bd977f5f95892b7bc9b0ad80d77561', 'Tree2TowerCore.lean': 'de630a6741350655fd50659c6d325879239de85a70521512773cf8a12abf74ea', 'Tree2TowerNative.lean': '7f669715054de5b5ca2fbb107cfc990ed83e47af604a3db4041546c29eb0b9ee', 'Tree2TowerWalk.lean': '0f7cfddf7032252df70da5311e658abc37f50765e7d7b74cb0a23bf7fb79c83c', 'Tree2TowerOfficial.lean': '202c6442fd47214436f8542dd6197369189a4f61f832cec3bd86cd67abdc842e', 'Tree2TowerCorrespondence.lean': '338e71b38d8aa8734a5b1d04cbfcf126925d3e447e5d79b4e32d52523606390a'}
EXPECTED_FINAL='130ff4163efae4f4e02438e73cf60de70f1e95dd8de13b67ba26c73310be9b43'

def replay(root):
 base=root/REL
 def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
 lock=json.loads((base/'source-lock.json').read_text())
 assert lock['sources']==EXPECTED_SOURCES
 assert lock['upstream_revision']=='10fe085e21773ff0b62a6aacf6db29fccf849bae'
 assert lock['proof_commit']=='e94d00b624951ccc0b4dd0a317eb5e952d948696'
 assert lock['toolchain']=='leanprover/lean4:v4.33.0'
 for n,h in EXPECTED_SOURCES.items():assert sha(base/'sources'/n)==h
 custody=json.loads((base/'custody.json').read_text())
 for n,row in custody.items():assert sha(base/n)==row['sha256'],n
 for p in (base/'attempts').glob('*/*/receipt.json'):
  rec=json.loads(p.read_text())
  for stream in ['stdout','stderr']:
   data=(p.parent/(stream+'.log')).read_bytes()
   assert len(data)==rec[stream+'_bytes'] and hashlib.sha256(data).hexdigest()==rec[stream+'_sha256']
 records=json.loads((base/'confirmation/module-records.json').read_text())
 freeze=json.loads((base/'confirmation/frozen-inputs.json').read_text())
 assert len(records)==108
 assert [r['module'] for r in records]==freeze['upstream_order']+[n[:-5] for n in EXPECTED_SOURCES]
 assert all(r['exit_code']==0 for r in records)
 env=json.loads((base/'confirmation/execution-env.json').read_text())
 allowed=[Path(p) for p in env['LEAN_PATH'].split(':')]+[Path(env['official_stdlib_prefix'])]
 for rec in records:
  for dep in rec['resolved_imports']:assert any(Path(dep['path']).is_relative_to(p) for p in allowed)
 final=base/'confirmation/modules/107/stdout.log'
 assert sha(final)==EXPECTED_FINAL
 assert final.read_bytes()==(base/'confirmation/expected-final-stdout.log').read_bytes()
 lines=[l for l in final.read_text().splitlines() if 'depends on axioms:' in l]
 assert len(lines)==16 and all(l.endswith('[propext, Classical.choice, Quot.sound]') for l in lines)
 receipt=json.loads((base/'confirmation/receipt.json').read_text())
 assert receipt['exit_code']==0 and receipt['cleanup_complete'] and receipt['stop_reason'] is None
 assert receipt['elapsed_seconds']<=600 and receipt['maximum_sampled_group_rss_bytes']<=4*1024**3
 claim=json.loads((base/'claim.json').read_text());assert claim['exact_statement']==freeze['exact_theorem']
 assert claim['only_hypothesis']=='N+5<=F' and claim['axioms']==['propext','Classical.choice','Quot.sound']

class Tree2ConfirmedEvidenceReplayPortabilityTests(unittest.TestCase):
 def test_tree2_replay_without_original_checkout_or_host_tools(self):
  with tempfile.TemporaryDirectory() as directory:
   checkout=Path(directory)/'foreign-checkout';dest=checkout/REL;dest.parent.mkdir(parents=True);shutil.copytree(ROOT/REL,dest)
   original=Path.read_bytes
   def reject_original(path):
    if Path(path).is_relative_to(ROOT):raise AssertionError('opened original evidence checkout')
    return original(path)
   with patch.object(Path,'read_bytes',reject_original),patch.object(subprocess,'run',side_effect=AssertionError('host process launch')),patch.object(subprocess,'Popen',side_effect=AssertionError('host process launch')):
    replay(checkout)
    p=dest/'sources/Tree2TowerCorrespondence.lean';raw=p.read_bytes();p.write_bytes(raw+b'tamper')
    with self.assertRaises(AssertionError):replay(checkout)
    p.write_bytes(raw)
    p=dest/'confirmation/modules/107/stdout.log';p.write_bytes(p.read_bytes()+b'tamper')
    with self.assertRaises(AssertionError):replay(checkout)
