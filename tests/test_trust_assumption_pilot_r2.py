import copy
import json
import shutil
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from lib import trust_assumption_pilot_r2 as pilot

class ReportTests(unittest.TestCase):
    fixtures=[{'id':'pure','target':'T.pure','expected_axioms':[]},
              {'id':'transitive','target':'T.leaf','expected_axioms':['T.ax']}]
    raw="'T.pure' does not depend on any axioms\n'T.leaf' depends on axioms: [T.ax]\n"

    def test_global_printing_options_survive_frozen_namespace_scope(self):
        runtime={'root':'/exact/lean','home':'/exact/home'}
        for route in pilot.PATHS:
            argv,_,_=pilot.command_contract(route,Path('/exact/attempt'),runtime,Path('/exact/producer'))
            self.assertEqual(argv[1:3],['-Dpp.privateNames=true','-Dpp.fullNames=true'])
        source=(pilot.ROOT/pilot.BASE/'fixtures/TrustFixtures.lean').read_text()
        self.assertLess(source.index('namespace TrustAssumptionPilot'),source.index('set_option pp.privateNames'))
        self.assertLess(source.index('end TrustAssumptionPilot'),source.index('#print axioms'))
        # R1 output is not silently aliased: the unchanged canonical expectation still mismatches.
        fixture=[{'id':'native','target':'T.native','expected_axioms':['_private.T.0.native.ax_1']}]
        row=pilot.report_rows("'T.native' depends on axioms: [T.native.ax_1]\n",'',fixture)[0]
        self.assertFalse(row['preserved'])

    def test_exact_and_wrapped_report(self):
        rows=pilot.report_rows(self.raw.replace('[T.ax]','[\n T.ax]'),' ',self.fixtures)
        self.assertTrue(all(x['preserved'] for x in rows))

    def test_malformed_missing_duplicate_extra_and_order_fail_closed(self):
        variants=[self.raw.splitlines()[0], self.raw+self.raw,
                  self.raw+"'X' does not depend on any axioms\n",
                  self.raw.replace('[T.ax]','[T.ax, T.ax]'),
                  self.raw.replace('[T.ax]','[T.ax,,]'),
                  '\n'.join(reversed(self.raw.splitlines())),
                  'warning: hidden diagnostic\n'+self.raw,
                  self.raw.replace('axioms: [T.ax]','axioms: [T.ax')]
        for raw in variants:
            with self.subTest(raw=raw),self.assertRaises(ValueError):
                pilot.report_rows(raw,'',self.fixtures)

    def test_stderr_rejected(self):
        with self.assertRaises(ValueError):pilot.report_rows(self.raw,'warning',self.fixtures)

    def test_unexpected_axiom_is_preserved_as_scientific_mismatch(self):
        rows=pilot.report_rows(self.raw.replace('[T.ax]','[T.ax, sorryAx]'),'',self.fixtures)
        self.assertFalse(rows[1]['preserved'])
        self.assertEqual(rows[1]['actual_axioms'],['T.ax','sorryAx'])

    def test_policy_pair_and_transitive_omission(self):
        row=pilot.report_rows(self.raw,'',self.fixtures)[1]
        self.assertEqual(pilot.permission(row['actual_axioms'],['T.ax'])['status'],'PERMITTED')
        self.assertEqual(pilot.permission(row['actual_axioms'],[]),{'status':'DENIED','unpermitted_axioms':['T.ax']})
        self.assertEqual(pilot.permission([],[])['status'],'PERMITTED')
        with self.assertRaises(ValueError):pilot.permission(['T.ax','T.ax'],[])

    def test_binding_detects_content_and_size_change(self):
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/'file';p.write_text('abc');b=pilot.bind(p)
            pilot.verify(b)
            p.write_text('def')
            with self.assertRaises(ValueError):pilot.verify(b)
            p.write_text('ab')
            with self.assertRaises(ValueError):pilot.verify(b)

    def test_missing_positive_rss_or_cleanup_is_nonterminal_fault(self):
        receipt={'cleanup_complete':True,'timed_out':False,'memory_exceeded':False,
                 'memory_monitor_error':None,'memory_monitor_samples':1,'maximum_observed_rss_bytes':1}
        pilot.safety(receipt)
        for key,value in [('cleanup_complete',False),('timed_out',True),('memory_exceeded',True),
                          ('memory_monitor_error','denied'),('memory_monitor_samples',0),('maximum_observed_rss_bytes',0)]:
            with self.subTest(key=key),self.assertRaises(ValueError):pilot.safety({**receipt,key:value})

class ResultTests(unittest.TestCase):
    def test_repository_result_if_closed(self):
        # At source/tooling preparation the canonical result intentionally does not exist.
        if (pilot.ROOT/pilot.BASE/'result-r2.json').exists():pilot.validate_result()

    def test_import_refuses_uncommitted_generated_payload_before_launch(self):
        proto,science=pilot.protocol()
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);(root/pilot.BASE/'execution').mkdir(parents=True)
            producer=root/'producer.json'
            files=[pilot.bind(pilot.ROOT/pilot.BASE/'execution/attempt-0001'/name) for name in pilot.MODULE_FILES]
            pilot.write(producer,{'route':pilot.PATHS[0],'module_files':files})
            def commit_gate(binding,*args):
                if binding['path'].endswith('TrustFixtures.ir'):
                    raise ValueError('uncommitted generated payload')
            original_read=pilot.read
            def reader(path):
                value=original_read(path)
                if str(path).endswith('prelaunch-review-r2.json'):value={**value,'status':'PASS'}
                return value
            previous=Path.cwd()
            try:
                with patch.object(pilot,'read',side_effect=reader),patch.object(pilot,'ROOT',root),patch.object(pilot,'protocol',return_value=(proto,science)),patch.object(pilot,'verify_runtime'),patch.object(pilot,'committed',side_effect=commit_gate),patch.object(pilot,'bind',side_effect=lambda p: {'path':str(p),'bytes':0,'sha256':'0'*64}),patch.object(pilot,'run_supervised') as launch:
                    with self.assertRaisesRegex(ValueError,'uncommitted generated payload'):
                        pilot.execute(pilot.PATHS[1],producer=str(producer))
                    launch.assert_not_called()
            finally:os.chdir(previous)

    def test_synthetic_receipt_tampering(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory); base=root/pilot.BASE;base.mkdir(parents=True)
            scientific=pilot.read(pilot.ROOT/pilot.BASE/'scientific-manifest.json')
            fixtures=scientific['fixtures']
            def put(rel,v):
                path=root/rel;path.parent.mkdir(exist_ok=True,parents=True)
                pilot.write(path,v); b=pilot.bind(path);b['path']=str(rel);return b
            def data(rel,v):
                path=root/rel;path.parent.mkdir(exist_ok=True,parents=True);path.write_text(v)
                b=pilot.bind(path);b['path']=str(rel);return b
            proto=pilot.read(pilot.ROOT/pilot.BASE/'protocol-r2.json')
            sm=pilot.read(pilot.ROOT/scientific['source_manifest']['path'])
            repair_binding=pilot.read(pilot.ROOT/proto['prelaunch_review']['path'])['repair']
            repair=pilot.read(pilot.ROOT/repair_binding['path'])
            for binding in [proto['runtime_manifest'],proto['reuse_review'],proto['host_tools'],proto['prelaunch_review'],proto['focused_validation'],*proto['tooling'],*scientific['fixture_bindings'],scientific['source_manifest'],*sm['sources'],*sm['comparator_sources'],repair_binding,*repair['source_bindings'],*pilot.repair_inputs(proto)]:
                dest=root/binding['path'];dest.parent.mkdir(parents=True,exist_ok=True)
                shutil.copyfile(pilot.ROOT/binding['path'],dest)
            sb=put(pilot.BASE/'scientific-manifest.json',scientific);proto['scientific_manifest']=sb
            review={'status':'PASS','scientific_manifest':sb,'tooling':proto['tooling'],'repair':repair_binding}
            proto['prelaunch_review']=put(Path(proto['prelaunch_review']['path']),review)
            pb=put(pilot.BASE/'protocol-r2.json',proto)
            obs=[]
            for index,route in enumerate(pilot.PATHS):
                dest=pilot.BASE/('attempt-'+str(index));raw=''.join("'"+f['target']+"' "+('depends on axioms: ['+', '.join(f['expected_axioms'])+']' if f['expected_axioms'] else 'does not depend on any axioms')+'\n' for f in fixtures)
                stdout=data(dest/'process.stdout',raw);stderr=data(dest/'process.stderr','')
                argv,env,cwd=pilot.command_contract(route,pilot.ROOT/dest,pilot.read(root/proto['runtime_manifest']['path']),pilot.ROOT/pilot.BASE/'attempt-0',pilot.ROOT)
                launch={'route':route,'protocol':pb,'argv':argv,'cwd':cwd,'environment':env,'inputs':pilot.required_inputs(pb,proto,scientific,root),'generated_module_manifest':obs[0] if obs else None}
                lb=put(dest/'launch.json',launch)
                receipt={'argv':argv,'cwd':cwd,'exit_code':0,'cleanup_complete':True,'timed_out':False,'memory_exceeded':False,'memory_monitor_error':None,'memory_monitor_samples':1,'maximum_observed_rss_bytes':1}
                for stream,b in [('stdout',stdout),('stderr',stderr)]:
                    receipt.update({'raw_'+stream+'_path':b['path'],stream+'_sha256':b['sha256'],stream+'_bytes':b['bytes']})
                rb=put(dest/'receipt.json',receipt)
                observation={'route':route,'launch':lb,'receipt':rb,'rows':pilot.report_rows(raw,'',fixtures)}
                if index==0:observation['module_files']=[data(dest/name,'module') for name in pilot.MODULE_FILES]
                obs.append(put(dest/'observation.json',observation))
            broken=copy.deepcopy(proto);broken['repair_record']['sha256']='0'*64
            with self.assertRaises(ValueError):pilot.validate_protocol(broken,root)
            for key in ('tooling',):
                shortened=copy.deepcopy(proto);shortened[key].pop()
                with self.assertRaises(ValueError):pilot.validate_protocol(shortened,root)
            result=pilot.rebuild_result(obs,root)
            self.assertEqual(result['status'],'SUCCESS');self.assertEqual(len(result['cells']),12)
            with self.assertRaises(ValueError):pilot.rebuild_result(list(reversed(obs)),root)
            # Omitted input and changed executable fail even if the receipt chain is rebound.
            original_ob=pilot.read(root/obs[1]['path'])
            original_launch=pilot.read(root/original_ob['launch']['path'])
            for change in ('omit-input','command','environment'):
                ob=copy.deepcopy(original_ob);launch=copy.deepcopy(original_launch)
                if change=='omit-input':launch['inputs'].pop()
                elif change=='command':launch['argv']=['echo','fabricated']
                else:launch['environment']['LEAN_PATH']='wrong-module'
                ob['launch']=put(Path(original_ob['launch']['path']),launch)
                candidate=put(Path(obs[1]['path']),ob)
                with self.subTest(change=change),self.assertRaises(ValueError):pilot.rebuild_result([obs[0],candidate],root)
            put(Path(original_ob['launch']['path']),original_launch);put(Path(obs[1]['path']),original_ob)
            # Scientific shape and policy-path changes cannot silently narrow the matrix.
            for change in ('duplicate-target','policy-path'):
                altered=copy.deepcopy(scientific)
                if change=='duplicate-target':altered['fixtures'][1]['target']=altered['fixtures'][0]['target']
                else:altered['permission_control']['paths']=pilot.PATHS[:1]
                changed=put(pilot.BASE/'scientific-manifest.json',altered)
                with self.subTest(change=change),self.assertRaises(ValueError):pilot.validate_protocol({**proto,'scientific_manifest':changed},root)
            put(pilot.BASE/'scientific-manifest.json',scientific)
            # Raw path tampering remains invalid even after rebinding intermediate receipts.
            ob=pilot.read(root/obs[1]['path']);receipt=pilot.read(root/ob['receipt']['path'])
            receipt['raw_stdout_path']=str(pilot.BASE/'attempt-0/process.stdout')
            ob['receipt']=put(Path(ob['receipt']['path']),receipt)
            bad=[obs[0],put(Path(obs[1]['path']),ob)]
            with self.assertRaises(ValueError):pilot.rebuild_result(bad,root)
            # Rebind the old receipt chain while corrupting its command: exact R1 replay must refuse.
            old_ob=pilot.read(root/repair['failed_attempt']['path'])
            old_receipt=pilot.read(root/old_ob['receipt']['path']);old_receipt['argv']=['echo','fabricated']
            old_ob['receipt']=put(Path(old_ob['receipt']['path']),old_receipt)
            altered_repair=copy.deepcopy(repair)
            altered_repair['failed_attempt']=put(Path(repair['failed_attempt']['path']),old_ob)
            altered_proto=copy.deepcopy(proto)
            altered_proto['repair_record']=put(Path(proto['repair_record']['path']),altered_repair)
            altered_review=pilot.read(root/proto['prelaunch_review']['path']);altered_review['repair']=altered_proto['repair_record']
            altered_proto['prelaunch_review']=put(Path(proto['prelaunch_review']['path']),altered_review)
            with self.assertRaisesRegex(ValueError,'prior command'):
                pilot.validate_repair(altered_proto,root)



    def test_result_requires_two_ordered_paths(self):
        for observations in ([],[{}],[{},{},{}]):
            with self.assertRaises(ValueError):pilot.rebuild_result(observations)

    def test_closed_result_tampering_fails(self):
        source=pilot.ROOT/pilot.BASE/'result-r2.json'
        if not source.exists():return
        original=pilot.read(source)
        mutations=[]
        for key in ('cells','permission_controls'):
            v=copy.deepcopy(original);v[key].pop();mutations.append(v)
            v=copy.deepcopy(original);v[key].reverse();mutations.append(v)
        v=copy.deepcopy(original);v['cells'][1]['expected_axioms']=[];mutations.append(v)
        v=copy.deepcopy(original);v['cells'][1]['actual_axioms']=[];mutations.append(v)
        v=copy.deepcopy(original);v['permission_controls'][1]['status']='PERMITTED';mutations.append(v)
        for value in mutations:
            def reader(path):
                return value if Path(path)==source else json.loads(Path(path).read_text())
            with patch.object(pilot,'read',side_effect=reader),self.assertRaises(ValueError):pilot.validate_result()

if __name__=='__main__':unittest.main()
