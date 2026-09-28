import copy
import unittest
from unittest.mock import patch
from lib import stateful_validation_pilot as p

class StatefulControlTests(unittest.TestCase):
    def test_process_controls_fail_closed(self):
        receipt=dict(cleanup_complete=True,timed_out=False,memory_exceeded=False,
                     memory_monitor_error=None,memory_monitor_samples=3,maximum_observed_rss_bytes=100)
        p.safe(receipt)
        for key,value in [('cleanup_complete',False),('timed_out',True),('memory_exceeded',True),
                          ('memory_monitor_error','lost RSS'),('memory_monitor_samples',0),('maximum_observed_rss_bytes',0)]:
            with self.assertRaises(ValueError): p.safe({**receipt,key:value})

    def test_duplicate_json_keys_rejected(self):
        with self.assertRaises(ValueError): p.unique([('status','PASS'),('status','FAIL')])

    def test_raw_receipt_and_memory_control_custody(self):
        receipt=dict(cleanup_complete=True,timed_out=False,memory_exceeded=False,
          memory_monitor_error=None,memory_monitor_samples=3,maximum_observed_rss_bytes=100,
          stdout_sha256=p.hashlib.sha256(b'out').hexdigest(),stderr_sha256=p.hashlib.sha256(b'').hexdigest(),
          stdout_bytes=3,stderr_bytes=0,memory_limit_bytes=2147483648)
        controls={'memory_bytes':2147483648}
        p.receipt_custody(receipt,b'out',b'',controls)
        for key,value in [('stdout_sha256','0'*64),('stderr_sha256','0'*64),('stdout_bytes',2),
                          ('stderr_bytes',1),('memory_limit_bytes',2147483647)]:
            with self.assertRaises(ValueError): p.receipt_custody({**receipt,key:value},b'out',b'',controls)

    def test_generation_is_separate_from_review(self):
        # Synthetic unrelated schema fixture, not construction of the six scientific files.
        d={'declarations':{'x':{'name':'Synthetic.X','type':['sort',1],'value':['sort',0]}}}
        c={'id':'synthetic','fresh':['x']}
        self.assertEqual(p.fixture(d,c,'fresh')['requests'][0]['name'],'Synthetic.X')

    def test_review_requires_exact_contract_and_source(self):
        with patch.object(p,'read',return_value={'verdict':'PASS','contract_sha256':'bad','source_manifest_sha256':'bad'}):
            with self.assertRaises(ValueError): p.scientific_review()

    def test_runtime_environment_excludes_ambient_search_paths(self):
        env=p.environment(p.Path('/exact/runtime'))
        self.assertEqual(env['LEAN_PATH'],'')
        self.assertEqual(env['LEAN_SRC_PATH'],'')
        self.assertEqual(env['LEAN_SYSROOT'],'/exact/runtime')

if __name__=='__main__': unittest.main()
