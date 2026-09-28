import copy
import unittest
from unittest.mock import patch
from lib import lazy_reduction_pilot as p
from lib import lazy_reduction_science as s
from lib.lazy_reduction_validation_r2 import validate, validate_closure

class EvidenceReplayTests(unittest.TestCase):
    def test_exact_capability_and_scientific_receipts_replay(self):
        result=validate_closure()
        self.assertEqual(result['status'],'PASS')
        self.assertEqual(result['scientific_cells'],12)
        self.assertTrue(result['acceptance_matched']); self.assertTrue(result['demand_qualified'])

    def test_wrong_manifest_observer_and_scope_rejected(self):
        original=p.load(s.EXECUTION)
        for key,value in [('stage','CAPABILITY'),('cells',original['cells'][:-1]),('jobs',2),('binary',original['artifacts']['beta']),('contract',original['source'])]:
            m=copy.deepcopy(original); m[key]=value
            with self.assertRaises(ValueError): s.validate_manifest(m)

    def test_altered_result_is_not_accepted_by_replay(self):
        real=p.load
        def changed(path):
            value=real(path)
            if path==p.BASE/'science-0001/result.json':
                value=copy.deepcopy(value); value['cells'][6]['observation']['machine']['beta']=0
            return value
        with patch.object(p,'load',changed),self.assertRaises(ValueError): validate()
        def wrong_summary(path):
            value=real(path)
            if path==p.BASE/'work-accounting.json':
                value=copy.deepcopy(value); value['scientific_cells']=11
            return value
        with patch.object(p,'load',wrong_summary),self.assertRaises(ValueError): validate_closure()

if __name__=='__main__': unittest.main()
