import copy, sys, unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT))
from lib import survivor_let_result as r

def events():
 x=[{'kind':'START','run_id':'survivor-let-reuse-0001'}]
 cells=[None,0,1,2,2,3]; phases=['build']+['checker']*5; classes=[None,'ACCEPT','ACCEPT','CRASH','TYPECHECK_REFUSAL','ACCEPT']
 for n,(phase,cell,cls) in enumerate(zip(phases,cells,classes),1):
  x += [{'kind':'RESERVED','number':n,'phase':phase,'cell':cell,'reserved_seconds':120 if phase=='build' else 30,'active_seconds':100,'manifest':{'path':'config/survivor-let-reuse-0001-r2.json' if n<=4 else 'config/survivor-let-reuse-0001-r3.json','sha256':'a'*64}}, {'kind':'TERMINAL','number':n,'status':'COMPLETE' if cls in (None,'ACCEPT') else 'FAILED','charged_seconds':1,'cleanup_completed':True,'classification':cls,'binary':{'path':'b','sha256':'a'*64} if n==1 else None}]
  if n==4: x += [{'kind':'REPAIR','after_number':4,'phase':'checker','cell':2}]
 return x
class ClosureTests(unittest.TestCase):
 def test_valid_chain(self): self.assertEqual(r.validate_chain(events())['next_action'],('DONE',None))
 def reject(self,fn):
  x=events(); fn(x)
  with self.assertRaises(ValueError): r.validate_chain(x)
 def test_reject_extra_attempt(self): self.reject(lambda x:x.extend(copy.deepcopy(x[-2:])))
 def test_reject_wrong_order(self): self.reject(lambda x:x.__setitem__(5,{**x[5],'cell':3}))
 def test_reject_missing_repair(self): self.reject(lambda x:x.pop(8))
 def test_reject_wrong_attribution(self): self.reject(lambda x:x.__setitem__(11,{**x[11],'classification':'ACCEPT'}))
 def test_reject_cleanup_failure(self): self.reject(lambda x:x.__setitem__(2,{**x[2],'cleanup_completed':False}))
 def test_reject_budget(self): self.reject(lambda x:x.__setitem__(1,{**x[1],'active_seconds':5390}))
 def test_artifacts_declare_successor_blocker(self):
  # Static output contract is exercised separately from filesystem validation.
  self.assertIn('scripts/build-witness-admission',r.artifacts.__code__.co_consts)
 def test_successor_transition_preserves_frozen_reuse_closure(self):
  with self.assertRaisesRegex(ValueError,'live classification state changed'):
   r.validate_pre_admission(ROOT)
  events,state,_=r.validate_historical_closure(ROOT)
  self.assertEqual(r.validate_chain(events)['charged_seconds'],state['charged_seconds'])
  self.assertEqual(set(r.build(ROOT)),set(r.OUTPUTS))
 def test_later_registry_suffix_does_not_rebind_historical_reuse(self):
  registry=ROOT/'results/mutants/registry.jsonl'; original=registry.read_bytes()
  read_bytes=Path.read_bytes
  with patch.object(Path,'read_bytes',autospec=True,side_effect=lambda path,*args,**kwargs: original+b'{}\n' if path==registry else read_bytes(path,*args,**kwargs)):
   r.validate_historical_closure(ROOT)
  changed=bytes([original[0]^1])+original[1:]
  with patch.object(Path,'read_bytes',autospec=True,side_effect=lambda path,*args,**kwargs: changed if path==registry else read_bytes(path,*args,**kwargs)):
   with self.assertRaisesRegex(ValueError,'registry prefix changed'):
    r.validate_historical_closure(ROOT)
if __name__=='__main__': unittest.main()
