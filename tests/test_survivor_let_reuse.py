"""Pure mocked regressions; this module launches neither cargo nor Nanoda."""
from datetime import datetime, timezone
import copy
import json
import shutil
import tempfile
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
from lib import survivor_let_reuse as p

def start(): return [{'kind':'START','run_id':p.RUN}]
def reserve(n, phase, cell=None, active=0): return {'kind':'RESERVED','number':n,'phase':phase,'cell':cell,'reserved_seconds':120 if phase=='build' else 30,'active_seconds':active}
def terminal(n, status='COMPLETE', classification=None, binary=False, cleanup=True, pause=False): return {'kind':'TERMINAL','number':n,'status':status,'charged_seconds':1,'classification':classification,'binary':{'path':'b','sha256':'a'*64} if binary else None,'cleanup_completed':cleanup,'engineering_pause':pause}
def built(): return start()+[reserve(1,'build'),terminal(1,binary=True)]
def trace(): return b"panicked at src/tc.rs:921:71: assertion failed: self.def_eq(u, v)\n::assert_def_eq\n::infer_let\n::check_declar_info\n"

class ActiveTime(unittest.TestCase):
 def work(self): return {'started_utc':datetime(2026,1,1,tzinfo=timezone.utc).isoformat(),'started_monotonic':100.,'conservative_pre_record_seconds':120}
 def test_max_clock_and_conservative_charge(self): self.assertEqual(p.active_seconds(self.work(),110,datetime(2026,1,1,0,0,11,tzinfo=timezone.utc)),131)
 def test_rejects_clock_disagreement_and_rollback(self):
  with self.assertRaises(ValueError): p.active_seconds(self.work(),110,datetime(2026,1,1,0,1,tzinfo=timezone.utc))
  with self.assertRaises(ValueError): p.active_seconds(self.work(),99,datetime(2026,1,1,tzinfo=timezone.utc))
 def test_reservation_cannot_cross_budget(self):
  with self.assertRaises(ValueError): p.derive(start()+[reserve(1,'build',active=5281)])

class Classification(unittest.TestCase):
 def rec(self, **kw): return {'status':'COMPLETE','returncode':0,'cleanup_completed':True,'deadline_exceeded':False,**kw}
 def test_all_cells_exact_clean_success(self):
  for cell in ('control-baseline','control-mutant','candidate-baseline','candidate-mutant'): self.assertEqual(p.classify(cell,self.rec(),p.SUCCESS,b''),'ACCEPT')
 def test_precise_baseline_refusal_requires_full_backtrace(self):
  self.assertEqual(p.classify('candidate-baseline',self.rec(status='FAILED',returncode=101),b'',trace()),'TYPECHECK_REFUSAL')
  for part in (b'::assert_def_eq',b'::infer_let',b'::check_declar_info',b'assertion failed: self.def_eq(u, v)'):
   self.assertNotEqual(p.classify('candidate-baseline',self.rec(status='FAILED',returncode=101),b'',trace().replace(part,b'')),'TYPECHECK_REFUSAL')
 def test_refusal_not_transferred(self):
  for cell in ('candidate-mutant','control-baseline','control-mutant'): self.assertEqual(p.classify(cell,self.rec(status='FAILED',returncode=101),b'',trace()),'CRASH')
 def test_generic_crash_parser_timeout_and_extra_output(self):
  self.assertEqual(p.classify('candidate-baseline',self.rec(status='FAILED',returncode=101),b'',b'panicked at somewhere'),'CRASH')
  self.assertEqual(p.classify('candidate-baseline',self.rec(status='FAILED',returncode=1),b'',b'parser error'),'PARSE_ERROR')
  self.assertEqual(p.classify('candidate-baseline',self.rec(status='TIMED_OUT',returncode=None),b'',b''),'TIMEOUT')
  self.assertEqual(p.classify('control-baseline',self.rec(),p.SUCCESS+b'x',b''),'INDETERMINATE')
  self.assertEqual(p.classify('control-baseline',self.rec(cleanup_completed=False),p.SUCCESS,b''),'INDETERMINATE')

class Accounting(unittest.TestCase):
 def test_build_before_checker_controls_before_candidates(self):
  with self.assertRaises(ValueError): p.derive(start()+[reserve(1,'checker',0)])
  rows=built()+[reserve(2,'checker',0),terminal(2,classification='ACCEPT'),reserve(3,'checker',1),terminal(3,classification='ACCEPT')]
  self.assertEqual(p.derive(rows)['next_action'],('checker',2))
  with self.assertRaises(ValueError): p.derive(built()+[reserve(2,'checker',2)])
 def test_failed_build_and_control_failure_pause_or_stop(self):
  self.assertEqual(p.derive(start()+[reserve(1,'build'),terminal(1,'FAILED')])['next_action'],('PAUSED',None))
  rows=built()+[reserve(2,'checker',0),terminal(2,'FAILED',classification='CRASH')]
  self.assertEqual(p.derive(rows)['next_action'],('STOP',None))
 def test_repair_replays_same_cell_only_after_pause(self):
  rows=built()+[reserve(2,'checker',0),terminal(2,classification='INDETERMINATE',pause=True)]
  repair={'kind':'REPAIR','after_number':2,'phase':'checker','cell':0}
  self.assertEqual(p.derive(rows+[repair])['next_action'],('checker',0))
  with self.assertRaises(ValueError): p.derive(rows+[{**repair,'cell':1}])
 def test_caps_and_orphan_fail_closed(self):
  rows=built()
  for n,c in enumerate((0,1,2,3),2): rows += [reserve(n,'checker',c),terminal(n,classification='ACCEPT')]
  self.assertEqual(p.derive(rows)['next_action'],('DONE',None))
  with self.assertRaises(ValueError): p.derive(rows+[reserve(6,'checker',0)])
  orphan=built()+[reserve(2,'checker',0)]
  self.assertEqual(p.derive(orphan)['charged_seconds'],31)
  with self.assertRaises(ValueError): p.derive(orphan+[reserve(3,'checker',0)])

class LedgerAndManifest(unittest.TestCase):
 def test_ledger_truncation_refused(self):
  with tempfile.TemporaryDirectory() as d, patch.object(p,'OUT','out'):
   ledger=p.Ledger(Path(d)); ledger.initialize(); ledger.path.write_bytes(b'')
   with self.assertRaises(ValueError): ledger.read()
 def test_manifest_path_and_missing_auth_artifacts_refused(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d); (root/'config').mkdir()
   with self.assertRaises(ValueError): p.manifest_path(root,'config/nope.json')
   with self.assertRaises(ValueError): p.validate_manifest(root)
 def test_manifest_revision_names_are_narrowly_bounded(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d); (root/'config').mkdir()
   for name in ('config/survivor-let-reuse-0001-r2.json','config/survivor-let-reuse-0001-r99.json'):
    (root/name).write_text('{}'); self.assertEqual(p.manifest_path(root,name),root/name)
   with self.assertRaises(ValueError): p.manifest_path(root,'config/survivor-let-reuse-0001-r1.json')
 def test_unknown_event_and_wrong_terminal_are_rejected(self):
  with self.assertRaises(ValueError): p.derive(start()+[{'kind':'ERASE'}])
  with self.assertRaises(ValueError): p.derive(built()+[terminal(1)])

class GateTests(unittest.TestCase):
 def setUp(self):
  self.t=tempfile.TemporaryDirectory(); self.addCleanup(self.t.cleanup); self.root=Path(self.t.name).resolve()
  w=self.root/p.WORK; w.parent.mkdir(parents=True); w.write_text(json.dumps({'item_id':p.ITEM,'status':'ACTIVE','owner_authorization':'Authorized. Please execute SURVIVOR-LET-REUSE-1','active_seconds_limit':5400}))
  self.q={'frontier_id':'F-SURVIVOR-LET-REUSE','selected_item':p.ITEM,'items':[{'id':p.ITEM,'status':'ACTIVE'}]}
 def call(self, q=None, used=100, seconds=30):
  with patch('lib.research_queue_v2.load_queue',return_value=q or self.q), patch.object(p,'active_seconds',return_value=used): return p.gate(self.root,seconds)
 def test_active_authorized_selected_gate_passes(self): self.assertEqual(self.call(),5300)
 def test_wrong_frontier_or_status_rejected(self):
  q=copy.deepcopy(self.q); q['frontier_id']='F-other'
  with self.assertRaises(ValueError): self.call(q)
  q=copy.deepcopy(self.q); q['items'][0]['status']='WAITING'
  with self.assertRaises(ValueError): self.call(q)
 def test_owner_quote_and_work_closure_rejected(self):
  w=self.root/p.WORK; x=json.loads(w.read_text()); x['owner_authorization']='authorized-ish'; w.write_text(json.dumps(x))
  with self.assertRaises(ValueError): self.call()
  x['owner_authorization']='Authorized. Please execute SURVIVOR-LET-REUSE-1'; w.write_text(json.dumps(x)); c=self.root/p.BASE/'work-closure.json'; c.parent.mkdir(parents=True,exist_ok=True); c.write_text('{}')
  with self.assertRaises(ValueError): self.call()
 def test_gate_rejects_cap_before_launch(self):
  with self.assertRaises(ValueError): self.call(used=5371,seconds=30)

class ManifestFixture(unittest.TestCase):
 """A complete local binding fixture; payload validation remains disabled."""
 def setUp(self):
  self.t=tempfile.TemporaryDirectory(); self.addCleanup(self.t.cleanup); self.root=Path(self.t.name).resolve()
  self.proposal=json.loads((ROOT/p.PROPOSAL).read_text())
  paths=[p.PROPOSAL, p.WORK, 'results/research/survivor-let-reuse-1/entry-decision.json',
         'results/research/survivor-let-reuse-1/source-materialization.json',
         'results/research/survivor-let-reuse-1/runtime-manifest.json',
         self.proposal['configuration']['base']['path'],
         *[self.proposal[k]['path'] for k in ('mutation_spec','source_lock','control','candidate','historical_official_result')]]
  for rel in paths:
   src=ROOT/rel; dst=self.root/rel; dst.parent.mkdir(parents=True,exist_ok=True)
   if src.exists(): shutil.copyfile(src,dst)
   else: dst.write_text('{}\n')
  for rel in p.CODE:
   dst=self.root/rel; dst.parent.mkdir(parents=True,exist_ok=True); dst.write_text('tool '+rel+'\n')
  base=json.loads((self.root/self.proposal['configuration']['base']['path']).read_text())
  for role in ('control','candidate'):
   dst=self.root/'results/research/survivor-let-reuse-1/configs'/f'{role}.json'; dst.parent.mkdir(parents=True,exist_ok=True)
   dst.write_text(json.dumps({**base,'use_stdin':False,'print_axioms':False,'export_file_path':str(self.root/self.proposal[role]['path'])}))
  self.write_manifest()
 def b(self, rel): return p.binding(self.root,self.root/rel)
 def write_manifest(self):
  fixed=[{'path':self.proposal[k]['path'],'sha256':self.proposal[k]['sha256']} for k in ('mutation_spec','source_lock','control','candidate','historical_official_result')]
  tooling=[self.b(rel) for rel in p.CODE]
  receipt={'status':'PASS','tooling_inputs':tooling,'test_count':22,'real_process_launches':0,'logs':[]}
  rp='results/research/survivor-let-reuse-1/focused-test.json'; (self.root/rp).write_text(json.dumps(receipt))
  m={'schema_version':1,'item_id':p.ITEM,'run_id':p.RUN,'limits':p.LIMITS,'tooling_inputs':tooling,
     'focused_test_receipt':self.b(rp),'proposal':self.b(p.PROPOSAL),'work_record':self.b(p.WORK),
     'entry_decision':self.b('results/research/survivor-let-reuse-1/entry-decision.json'),
     'source_materialization':self.b('results/research/survivor-let-reuse-1/source-materialization.json'),
     'runtime_manifest':self.b('results/research/survivor-let-reuse-1/runtime-manifest.json'),'fixed_inputs':fixed,
     'configs':{r:self.b(f'results/research/survivor-let-reuse-1/configs/{r}.json') for r in ('control','candidate')},
     'matrix':self.proposal['matrix'],'observer_environment':p.ENV}
  mp=self.root/p.MANIFEST; mp.parent.mkdir(exist_ok=True); mp.write_text(json.dumps(m)); self.m=m
 def validate(self): return p.validate_manifest(self.root,payload=False)
 def test_real_valid_manifest_fixture_passes(self): self.assertEqual(self.validate()['run_id'],p.RUN)
 def test_config_science_drift_and_input_byte_drift_rejected(self):
  cfg=self.root/'results/research/survivor-let-reuse-1/configs/control.json'; x=json.loads(cfg.read_text()); x['print_axioms']=True; cfg.write_text(json.dumps(x))
  with self.assertRaises(ValueError): self.validate()
  self.setUp(); (self.root/self.proposal['candidate']['path']).write_bytes(b'changed')
  with self.assertRaises(ValueError): self.validate()
 def test_decision_tool_and_test_receipt_bindings_rejected(self):
  d=self.root/'results/research/survivor-let-reuse-1/entry-decision.json'; x=json.loads(d.read_text()); x['execution_authorized']=False; d.write_text(json.dumps(x)); self.m['entry_decision']=self.b(d.relative_to(self.root)); (self.root/p.MANIFEST).write_text(json.dumps(self.m))
  with self.assertRaises(ValueError): self.validate()
  self.setUp(); (self.root/p.CODE[0]).write_text('changed')
  with self.assertRaises(ValueError): self.validate()
  self.setUp(); rp=self.root/'results/research/survivor-let-reuse-1/focused-test.json'; x=json.loads(rp.read_text()); x['tooling_inputs']=[]; rp.write_text(json.dumps(x)); self.m['focused_test_receipt']=self.b(rp.relative_to(self.root)); (self.root/p.MANIFEST).write_text(json.dumps(self.m))
  with self.assertRaises(ValueError): self.validate()

class ProcessPersistence(unittest.TestCase):
 def fixture(self, root):
  from contextlib import ExitStack
  import json
  manifest = root / p.MANIFEST
  manifest.parent.mkdir(parents=True)
  manifest.write_text(json.dumps({'matrix': [], 'tooling_inputs': []}))
  stack = ExitStack()
  stack.enter_context(patch.object(p, 'validate_manifest', return_value={'matrix': []}))
  stack.enter_context(patch.object(p, 'gate', return_value=5400))
  stack.enter_context(patch.object(p, 'verify_attempts', side_effect=lambda root, events, **kw: p.derive(events)))
  stack.enter_context(patch('lib.survivor_let_payload.verify', return_value={'build': {'argv':['inert'], 'cwd':str(root), 'env':{}}}))
  stack.enter_context(patch.object(p.subprocess, 'check_output', return_value='a'*40))
  return stack
 def test_reservation_survives_launch_exception_and_blocks_retry(self):
  with tempfile.TemporaryDirectory() as temp:
   root = Path(temp)
   with self.fixture(root), patch.object(p, 'run_process', side_effect=ValueError('supervisor failure')) as run:
    with self.assertRaisesRegex(ValueError, 'supervisor failure'): p.execute(root)
    events, state = p.Ledger(root).read()
    self.assertEqual(events[-1]['kind'], 'RESERVED')
    self.assertEqual(state['charged_seconds'], 120)
    with self.assertRaisesRegex(ValueError, 'paused'): p.execute(root)
    self.assertEqual(run.call_count, 1)
 def test_cleanup_failure_receipt_is_terminal_and_retained(self):
  import json, hashlib
  def fake(argv, cwd, env, directory, seconds, **kw):
   # Exercise the real reservation/receipt path without forking a process.
   (directory/'stdout').write_bytes(b'')
   (directory/'stderr').write_bytes(b'cleanup denied')
   request = {'argv':argv, 'cwd':cwd, 'env':env, 'seconds':seconds}
   request['request_sha256'] = hashlib.sha256(json.dumps(request,sort_keys=True).encode()).hexdigest()
   p.atomic(directory/'request.json', request)
   rec = {'status':'INTERRUPTED','returncode':0,'charged_seconds':1.,'monotonic_started':10.,'monotonic_ended':11.,
          'request_sha256':request['request_sha256'],'stdout_sha256':p.sha(directory/'stdout'),
          'stderr_sha256':p.sha(directory/'stderr'),'cleanup_completed':False,'deadline_exceeded':False,'error':'cleanup denied'}
   p.atomic(directory/'supervisor.json',rec)
   return rec
  with tempfile.TemporaryDirectory() as temp:
   root=Path(temp)
   with self.fixture(root), patch.object(p,'run_process',side_effect=fake):
    result=p.execute(root)
    self.assertEqual(result['next_action'],('PAUSED',None))
    self.assertEqual(result['attempts'][0]['terminal']['status'],'INTERRUPTED')
    self.assertFalse(result['attempts'][0]['terminal']['cleanup_completed'])
    self.assertEqual(len(result['attempts'][0]['terminal']['receipts']),4)

if __name__=='__main__': unittest.main()
