"""No Cargo/checker/inert subprocesses: controller I/O is mocked in every launch test."""
from contextlib import ExitStack
from datetime import datetime, timezone
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from lib import survivor_cache_runner as p


def start(): return [{'kind': 'START', 'run_id': p.RUN}]
def reserve(n, phase, cell=0, active=0):
    return {'kind': 'RESERVED', 'number': n, 'phase': phase, 'cell': cell,
            'reserved_seconds': 120 if phase == 'build' else 30, 'active_seconds': active}
def terminal(n, status='COMPLETE', classification=None, binary=False, cleanup=True, pause=False):
    return {'kind': 'TERMINAL', 'number': n, 'status': status, 'charged_seconds': 1,
            'classification': classification, 'binary': {'path': 'b', 'sha256': 'a'*64} if binary else None,
            'cleanup_completed': cleanup, 'engineering_pause': pause}
def built():
    return start() + [reserve(1, 'build', 0), terminal(1, binary=True),
                      reserve(2, 'build', 1), terminal(2, binary=True)]
def tests():
    return {'control': {'name': 'tc::cache_contract_tests::control'},
            'candidate': {'name': 'tc::cache_contract_tests::candidate',
                          'failure_message': 'expected checked inference to reject warmed malformed let',
                          'failure_location': 'src/tc.rs:1200:9'}}
def output(role, failed=False):
    name = tests()[role]['name']
    if not failed:
        return ('\nrunning 1 test\ntest ' + name + ' ... ok\n\n'
                'test result: ok. 1 passed; 0 failed; 0 ignored; 0 measured; 6 filtered out; finished in 0.00s\n\n').encode()
    return ('\nrunning 1 test\ntest ' + name + ' ... FAILED\n\nfailures:\n\n---- ' + name + ' stdout ----\n'
            "\nthread '" + name + "' (123) panicked at src/tc.rs:1200:9:\n"
            + tests()['candidate']['failure_message'] + '\nstack backtrace:\n   0: rust_begin_unwind\n'
            '\n\nfailures:\n    ' + name + '\n\ntest result: FAILED. 0 passed; 1 failed; 0 ignored; 0 measured; 6 filtered out; finished in 0.00s\n\n').encode()


class ActiveTime(unittest.TestCase):
    def work(self):
        return {'entry_overhead_conservative_seconds': 120, 'intervals': [
            {'started_at': '2026-01-01T00:00:00+00:00', 'started_monotonic': 100.}]}
    def test_time_includes_conservative_entry_overhead(self):
        self.assertEqual(p.active_seconds(self.work(), 110, datetime(2026,1,1,0,0,11,tzinfo=timezone.utc)), 131)
    def test_clock_rollback_and_disagreement_fail(self):
        for mono, utc in [(99, datetime(2026,1,1,tzinfo=timezone.utc)),
                          (110, datetime(2026,1,1,0,1,tzinfo=timezone.utc))]:
            with self.assertRaises(ValueError): p.active_seconds(self.work(), mono, utc)
    def test_closed_intervals_are_not_reset(self):
        w = self.work(); w['intervals'][0].update(ended_at='2026-01-01T00:00:10+00:00', ended_monotonic=110)
        w['intervals'].append({'started_at':'2026-01-01T00:01:00+00:00','started_monotonic':160})
        self.assertEqual(p.active_seconds(w, 165, datetime(2026,1,1,0,1,5,tzinfo=timezone.utc)), 135)
    def test_overlapping_intervals_and_small_overhead_fail(self):
        w = self.work(); w['entry_overhead_conservative_seconds'] = 0
        with self.assertRaises(ValueError): p.active_seconds(w, 110, datetime(2026,1,1,0,0,10,tzinfo=timezone.utc))
    def test_reservation_cannot_cross_cap(self):
        with self.assertRaises(ValueError): p.derive(start() + [reserve(1, 'build', active=5281)])


class Classifier(unittest.TestCase):
    def rec(self, **kw):
        return {'status':'COMPLETE', 'returncode':0, 'cleanup_completed':True, 'deadline_exceeded':False, **kw}
    def cell(self, role, observer='baseline'): return {'input':role, 'observer':observer}
    def test_exact_pass_all_cells(self):
        for role in ('control','candidate'):
            for observer in p.PROFILES:
                self.assertEqual(p.classify(self.cell(role,observer), tests(), self.rec(), output(role), b''), 'TEST_PASS')
    def test_specific_failure_has_source_and_assertion(self):
        self.assertEqual(p.classify(self.cell('candidate','mutant'),tests(),self.rec(status='FAILED',returncode=101),output('candidate',True),b''),'REGRESSION_FAILURE')
        for part in (b'src/tc.rs:1200:9', tests()['candidate']['failure_message'].encode(), b'0 passed; 1 failed'):
            self.assertEqual(p.classify(self.cell('candidate'),tests(),self.rec(status='FAILED',returncode=101),output('candidate',True).replace(part,b'different'),b''),'INDETERMINATE')
    def test_extra_bytes_and_stderr_are_rejected(self):
        for stdout, stderr in [(output('control')+b'x',b''),(output('control'),b'warning'),(b'running 0 tests',b'')]:
            self.assertEqual(p.classify(self.cell('control'),tests(),self.rec(),stdout,stderr),'INDETERMINATE')
    def test_wrong_test_or_duplicate_panic_rejected(self):
        self.assertEqual(p.classify(self.cell('control'),tests(),self.rec(),output('candidate'),b''),'INDETERMINATE')
        value=output('candidate',True).replace(b'stack backtrace:',b'panicked at elsewhere\nstack backtrace:')
        self.assertEqual(p.classify(self.cell('candidate'),tests(),self.rec(status='FAILED',returncode=101),value,b''),'INDETERMINATE')
    def test_failure_never_applies_to_control(self):
        self.assertEqual(p.classify(self.cell('control'),tests(),self.rec(status='FAILED',returncode=101),output('candidate',True),b''),'INDETERMINATE')
    def test_timeout_cleanup_and_supervisor_error_fail_closed(self):
        for rec in [self.rec(status='TIMED_OUT'), self.rec(cleanup_completed=False), self.rec(error='lost')]:
            self.assertIn(p.classify(self.cell('control'),tests(),rec,output('control'),b''), {'TIMEOUT','INDETERMINATE'})


class Accounting(unittest.TestCase):
    def test_two_builds_precede_exact_controls_then_candidates(self):
        self.assertEqual(p.derive(start())['next_action'], ('build',0))
        self.assertEqual(p.derive(start()+[reserve(1,'build'),terminal(1,binary=True)])['next_action'],('build',1))
        self.assertEqual(p.derive(built())['next_action'],('checker',0))
        for wrong in [reserve(1,'checker',0),reserve(1,'build',1)]:
            with self.assertRaises(ValueError): p.derive(start()+[wrong])
        with self.assertRaises(ValueError): p.derive(built()+[reserve(3,'checker',2)])
    def test_all_four_cells_finish_once(self):
        rows=built()
        for n,c in enumerate(range(4),3): rows += [reserve(n,'checker',c),terminal(n,classification='TEST_PASS' if c<3 else 'REGRESSION_FAILURE')]
        self.assertEqual(p.derive(rows)['next_action'],('DONE',None))
        with self.assertRaises(ValueError): p.derive(rows+[reserve(7,'checker',3)])
    def test_baseline_candidate_failure_stops_interpretation(self):
        rows=built()
        for n,c in enumerate(range(3),3): rows += [reserve(n,'checker',c),terminal(n,classification='TEST_PASS' if c<2 else 'REGRESSION_FAILURE')]
        self.assertEqual(p.derive(rows)['next_action'],('STOP',None))
    def test_failures_and_orphans_remain_charged(self):
        rows=start()+[reserve(1,'build'),terminal(1,'FAILED',pause=True)]
        self.assertEqual(p.derive(rows)['next_action'],('PAUSED',None))
        orphan=built()+[reserve(3,'checker',0)]
        self.assertEqual(p.derive(orphan)['charged_seconds'],32)
        with self.assertRaises(ValueError): p.derive(orphan+[reserve(4,'checker',0)])
    def test_repair_cannot_change_cell_or_reset_build_cap(self):
        rows=start()+[reserve(1,'build'),terminal(1,'FAILED',pause=True)]
        repair={'kind':'REPAIR','after_number':1,'phase':'build','cell':0}
        with self.assertRaises(ValueError): p.derive(rows+[{**repair,'cell':1}])
        rows += [repair,reserve(2,'build'),terminal(2,binary=True)]
        with self.assertRaises(ValueError): p.derive(rows+[reserve(3,'build',1)])
    def test_checker_repairs_share_eight_attempt_cap(self):
        rows=built()
        for n in range(3,11):
            rows += [reserve(n,'checker',0),terminal(n,classification='INDETERMINATE',pause=True),
                     {'kind':'REPAIR','after_number':n,'phase':'checker','cell':0}]
        with self.assertRaises(ValueError): p.derive(rows+[reserve(11,'checker',0)])
    def test_malformed_terminal_cannot_skip_audit_pause(self):
        for classification, pause in [('made-up',False),('INDETERMINATE',False),('TIMEOUT',False)]:
            rows=built()+[reserve(3,'checker'),terminal(3,classification=classification,pause=pause)]
            with self.assertRaises(ValueError): p.derive(rows)

    def test_unknown_event_and_terminal_fail(self):
        for row in [{'kind':'ERASE'}, terminal(1)]:
            with self.assertRaises(ValueError): p.derive(start()+[row])
    def test_ledger_reset_and_truncation_refused(self):
        with tempfile.TemporaryDirectory() as d:
            ledger=p.Ledger(Path(d)); ledger.initialize()
            with self.assertRaises(ValueError): ledger.initialize()
            ledger.path.write_text('')
            with self.assertRaises(ValueError): ledger.read()


class ManifestFixture(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup); self.root=Path(self.temp.name)
        self.m={'schema_version':1,'item_id':p.ITEM,'run_id':p.RUN,'limits':p.LIMITS,
                'tests':tests(),'observer_environment':p.ENV}
        required={'work_record':p.WORK,'entry_decision':p.BASE+'/entry-decision.json',
                  'source_materialization':p.BASE+'/source-materialization.json',
                  'runtime_manifest':p.BASE+'/runtime-manifest.json','mutation_spec':'mutations/'+p.MUTANT+'.json',
                  'source_lock':p.BASE+'/source-lock.json','harness':p.BASE+'/cache-contract-tests.rs'}
        for k,rel in required.items():
            self.write(rel, {'execution_authorized':True,'item_id':p.ITEM} if k=='entry_decision' else {})
            self.m[k]=self.b(rel)
        for rel in p.CODE: self.write(rel, {'tool':rel})
        self.m['tooling_inputs']=[self.b(x) for x in p.CODE]
        self.write(p.BASE+'/focused.log', {'passed':True})
        self.receipt={'status':'PASS','tooling_inputs':self.m['tooling_inputs'], 'test_count':30,
                      'real_process_launches':0,'logs':[self.b(p.BASE+'/focused.log')]}
        self.save_receipt(); self.save()
    def write(self, rel, value):
        f=self.root/rel; f.parent.mkdir(parents=True,exist_ok=True); f.write_text(json.dumps(value))
    def b(self,rel): return p.binding(self.root,self.root/rel)
    def save(self): self.write(p.MANIFEST,self.m)
    def save_receipt(self):
        rel=p.BASE+'/focused-test.json'; self.write(rel,self.receipt); self.m['focused_test_receipt']=self.b(rel)
    def validate(self): return p.validate_manifest(self.root,payload=False)
    def test_valid_fully_bound_manifest(self): self.assertEqual(self.validate()['run_id'],p.RUN)
    def test_missing_tool_and_stale_tests_fail(self):
        self.m['tooling_inputs']=self.m['tooling_inputs'][1:]; self.save()
        with self.assertRaises(ValueError): self.validate()
        self.setUp(); self.receipt['tooling_inputs']=[]; self.save_receipt(); self.save()
        with self.assertRaises(ValueError): self.validate()
    def test_wrong_science_or_input_hash_fails(self):
        self.m['tests']['candidate']['name']='other'; self.save()
        with self.assertRaises(ValueError): self.validate()
        self.setUp(); self.write(p.BASE+'/cache-contract-tests.rs',{'changed':True})
        with self.assertRaises(ValueError): self.validate()
    def test_no_authority_and_relaxed_cap_fail(self):
        self.write(p.BASE+'/entry-decision.json',{'execution_authorized':False,'item_id':p.ITEM}); self.m['entry_decision']=self.b(p.BASE+'/entry-decision.json'); self.save()
        with self.assertRaises(ValueError): self.validate()
        self.setUp(); self.m['limits']={**p.LIMITS,'offline_build_reservations':3}; self.save()
        with self.assertRaises(ValueError): self.validate()
    def test_engineering_revision_preserves_frozen_science(self):
        rel='config/survivor-cache-0001-r2.json'; changed=copy.deepcopy(self.m); changed['tests']['candidate']['failure_message']='other'; self.write(rel,changed)
        with self.assertRaises(ValueError): p.validate_manifest(self.root,rel,payload=False)
    def test_exact_manifest_paths_only(self):
        for rel in ['config/other.json','../config/survivor-cache-0001.json','config/survivor-cache-0001-r1.json']:
            with self.assertRaises(ValueError): p.manifest_path(self.root,rel)


class InheritedRuntimePackages(unittest.TestCase):
    def test_target_specific_absence_must_be_symmetric_and_inherited(self):
        absent = {'name':'wasi','version':'0.11.0','lock_checksum':'a'*64,
                  'source':None,'archive':None}
        self.assertFalse(p.package_has_payload(absent))
        for partial in ({**absent,'source':{}},{**absent,'archive':{}}):
            with self.assertRaises(ValueError): p.package_has_payload(partial)


class ProcessPersistence(unittest.TestCase):
    def fixture(self, root):
        m=root/p.MANIFEST; m.parent.mkdir(parents=True); m.write_text(json.dumps({'tests':tests(),'tooling_inputs':[]}))
        stack=ExitStack()
        stack.enter_context(patch.object(p,'validate_manifest',return_value={'tests':tests()}))
        stack.enter_context(patch.object(p,'gate',return_value=5400))
        stack.enter_context(patch.object(p,'verify_attempts',side_effect=lambda root,events,**kw:p.derive(events)))
        stack.enter_context(patch.object(p,'verify_payload',return_value={'baseline':{'argv':['not-launched'],'cwd':str(root),'env':{}}}))
        stack.enter_context(patch.object(p.subprocess,'check_output',return_value='a'*40))
        return stack
    def test_reservation_survives_supervisor_exception(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            with self.fixture(root), patch.object(p,'run_process',side_effect=ValueError('supervisor failed')) as run:
                with self.assertRaisesRegex(ValueError,'supervisor failed'): p.execute(root)
                self.assertEqual(p.Ledger(root).read()[1]['charged_seconds'],120)
                with self.assertRaisesRegex(ValueError,'paused'): p.execute(root)
                self.assertEqual(run.call_count,1)
    def test_cleanup_failure_keeps_raw_terminal_receipt(self):
        def fake(argv,cwd,env,directory,seconds,**kw):
            (directory/'stdout').write_bytes(b''); (directory/'stderr').write_bytes(b'cleanup denied')
            request={'argv':argv,'cwd':cwd,'env':env,'seconds':seconds}
            request['request_sha256']=hashlib.sha256(json.dumps(request,sort_keys=True).encode()).hexdigest()
            p.atomic(directory/'request.json',request)
            rec={'status':'INTERRUPTED','returncode':0,'charged_seconds':1.,'monotonic_started':10.,'monotonic_ended':11.,
                 'request_sha256':request['request_sha256'],'stdout_sha256':p.sha(directory/'stdout'),
                 'stderr_sha256':p.sha(directory/'stderr'),'cleanup_completed':False,'deadline_exceeded':False,'error':'cleanup denied'}
            p.atomic(directory/'supervisor.json',rec); return rec
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            with self.fixture(root), patch.object(p,'run_process',side_effect=fake):
                state=p.execute(root)
                self.assertEqual(state['next_action'],('PAUSED',None))
                self.assertEqual(len(state['attempts'][0]['terminal']['receipts']),4)
                self.assertEqual(state['charged_seconds'],1.)


class ArtifactParsing(unittest.TestCase):
    def fixture(self, root):
        f=root/p.TARGET_ROOTS['baseline']/'release/deps/nanoda-123'; f.parent.mkdir(parents=True); f.write_bytes(b'not executed')
        return {'reason':'compiler-artifact','executable':str(f),'profile':{'test':True},
                'target':{'kind':['lib'],'src_path':str(root/p.SOURCE_ROOTS['baseline']/'src/lib.rs')}}
    def parse(self,root,rows): return p.build_artifact(root,{'cell':0},b'\n'.join(json.dumps(r).encode() for r in rows))
    def test_unique_exact_library_test_artifact_required(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); artifact=self.fixture(root); done={'reason':'build-finished','success':True}
            self.assertEqual(self.parse(root,[artifact,done]),Path(artifact['executable']))
            for rows in [[done],[artifact,artifact,done],[artifact,{**done,'success':False}]]:
                with self.assertRaises(ValueError): self.parse(root,rows)
    def test_duplicate_json_keys_and_nonfinite_values_fail(self):
        for text in ['{"x":1,"x":2}', '{"x":NaN}', '{"x":Infinity}']:
            with self.assertRaises(ValueError): p.strict_json(text)

    def test_wrong_source_target_and_non_json_output_fail(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); artifact=self.fixture(root); artifact['target']['src_path']='elsewhere'
            with self.assertRaises(ValueError): self.parse(root,[artifact,{'reason':'build-finished','success':True}])
            with self.assertRaises(ValueError): p.build_artifact(root,{'cell':0},b'not JSON')

if __name__ == '__main__': unittest.main()
