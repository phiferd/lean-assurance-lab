import copy
import json
import unittest
from lib import lazy_reduction_cases as c
from lib import lazy_reduction_audit as a

class IndependentAuditTests(unittest.TestCase):
    def test_all_derivations_and_fixed_demands(self):
        self.assertEqual(a.audit_contract(c.contract())['cases'],6)
    def test_wrong_annotation_is_rejected(self):
        doc=c.contract(); doc['cases'][0]['declared_type']['function']['domain']['level']=1
        with self.assertRaises(ValueError): a.audit_contract(doc)
    def test_shadow_off_by_one_is_rejected(self):
        doc=c.contract(); doc['cases'][4]['declared_type']['function']['body']['function']['body']['index']=0
        with self.assertRaises(ValueError): a.audit_contract(doc)
    def test_repeated_capture_is_rejected(self):
        doc=c.contract(); doc['cases'][5]['declared_type']['function']['body']['body']['index']=0
        with self.assertRaises(ValueError): a.audit_contract(doc)
    def test_extra_case_and_counter_weakening_rejected(self):
        doc=c.contract(); doc['cases'].append(copy.deepcopy(doc['cases'][0]))
        with self.assertRaises(ValueError): a.audit_contract(doc)
        doc=c.contract(); doc['cases'][0]['kam_minimum']['beta']=0
        with self.assertRaises(ValueError): a.audit_contract(doc)
    def test_graph_missing_extra_hidden_and_altered_definition(self):
        # Synthetic parser fixture, deliberately outside the scientific six-case files.
        row={'declaration_name':'synthetic','declared_type':{'tag':'sort','level':1},'value':{'tag':'sort','level':0}}
        data=c.encode(row); a.audit_export(data,row)
        rows=data.splitlines(keepends=True)
        for bad in [b''.join(rows[:-1]),data+rows[-1],data+b'{"ie":9,"const":{"name":1,"us":[]}}\n',data.replace(b'"safety":"safe"',b'"safety":"unsafe"'),
                    b''.join(rows[:-1])+b'{"ie":2,"sort":2}\n'+rows[-1],
                    data.replace(b'{"ie":0,"sort":1}',b'{"ie":0,"app":{"fn":1,"arg":1}}')]:
            with self.assertRaises(ValueError): a.audit_export(bad,row)

    def test_machine_demand_rejects_missing_counter_and_fusion(self):
        from lib.lazy_reduction_science import demand
        obs={'verdict':'ACCEPT','machine':dict(beta=1,let=0,delta=0,iota=0,proj=0)}
        raw=b'nat ops: 0, first-operand limbs 0, GMP 0 Gcycles, literal interning 0 Gcycles\ndeclarations rechecked with fusion: 0\n'
        case=c.templates()[0]
        self.assertEqual(demand(obs,raw,'kam',case),'PASS')
        self.assertNotEqual(demand(obs,raw.replace(b'fusion: 0',b'fusion: 1'),'kam',case),'PASS')
        self.assertNotEqual(demand(obs,raw.split(b'declarations')[0],'kam',case),'PASS')
        self.assertEqual(demand({**obs,'machine':{**obs['machine'],'beta':0}},raw,'kam',case),'UNSUPPORTED_DEMAND')

    def test_ordinary_semantic_failure_vs_contradictory_output(self):
        from lib.lazy_reduction_science import classify
        case=c.templates()[0]
        receipt=dict(exit_code=1,memory_monitor_samples=1,maximum_observed_rss_bytes=1024,cleanup_complete=True,timed_out=False,memory_exceeded=False,memory_monitor_error=None)
        raw=b'loaded 1 declarations, 7 exprs (8 unique), 2 names in 0.01s\nFAIL LAL_lazy_beta (line 20): type mismatch for LAL_lazy_beta\n  inferred: Sort 1\n  declared: Sort 2\n'
        self.assertEqual(classify(receipt,b'',raw,case,20)['verdict'],'SEMANTIC_REJECT')
        self.assertNotEqual(classify(receipt,b'',raw+b'error: later failure\n',case,20)['verdict'],'SEMANTIC_REJECT')

if __name__=='__main__': unittest.main()
