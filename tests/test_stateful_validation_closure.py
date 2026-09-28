import copy
import unittest
from unittest.mock import patch
from lib import stateful_validation_closure_portable as c

class StatefulClosureTests(unittest.TestCase):
    def test_exact_science_and_all_historical_compile_receipts_replay(self):
        result=c.validate_closure()
        self.assertEqual((result['comparisons'],result['histories'],result['requests']),(6,12,25))
        self.assertEqual((result['compile_attempts'],result['failed_compile_attempts']),(3,2))
        self.assertEqual(result['launches_during_validation'],0)

    def test_changed_scientific_result_is_not_accepted(self):
        original=c.p.read
        def altered(path):
            doc=original(path)
            if str(path)==str(c.p.BASE/'result.json'):
                doc=copy.deepcopy(doc); doc['requests']=24
            return doc
        with patch.object(c.p,'read',side_effect=altered):
            with self.assertRaises(ValueError): c.validate_closure()

    def test_lost_failed_attempt_is_not_relabelled_success(self):
        original=c.p.read
        def altered(path):
            doc=original(path)
            if str(path).endswith('/compile-0001/result.json'):
                doc=copy.deepcopy(doc); doc['status']='PASS'
            return doc
        with patch.object(c.p,'read',side_effect=altered):
            with self.assertRaises(ValueError): c.compile_history()

    def test_cumulative_accounting_counts_failed_work(self):
        value=c.accounting()
        self.assertEqual(value['total_supervised_processes'],15)
        self.assertEqual(value['failed_compile_attempts'],2)
        self.assertTrue(value['all_cleanup_complete'])
        self.assertIsNone(value['manual_engineering_review_seconds'])

    def test_wrong_successor_is_rejected(self):
        original=c.p.read
        def altered(path):
            doc=original(path)
            if str(path)==str(c.p.BASE/'closure.json'):
                doc=copy.deepcopy(doc); doc['successor']='BINDER-MODEL-PILOT-1'
            return doc
        with patch.object(c.p,'read',side_effect=altered):
            with self.assertRaises(ValueError): c.validate_closure()

if __name__=='__main__': unittest.main()
