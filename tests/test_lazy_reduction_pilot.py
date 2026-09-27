import unittest
from lib.lazy_reduction_pilot import classify

class AdapterTests(unittest.TestCase):
    def setUp(self):
        self.receipt=dict(exit_code=0,memory_monitor_samples=1,maximum_observed_rss_bytes=1024,cleanup_complete=True)
        self.output=b'loaded 1 declarations, 7 exprs (8 unique), 2 names in 0.01s\nchecked 1 declarations, 0 failed, 0 added unchecked, in 0.01s; 2 reduction steps; 8 exprs live\nmachine: app 1, bvar 1, beta 1, let 0, delta 0, iota 0, proj 0, enter value/delayed/re-eval 1/0/0, memo hit/insert 0/0\n'
    def test_accept_and_machine(self):
        result=classify(self.receipt,b'',self.output,1)
        self.assertEqual(result['verdict'],'ACCEPT'); self.assertEqual(result['machine']['beta'],1)
    def test_no_thread_no_accept(self):
        self.assertNotEqual(classify(self.receipt,b'',b'',1)['verdict'],'ACCEPT')
    def test_missing_counters_no_accept(self):
        self.assertNotEqual(classify(self.receipt,b'',self.output.split(b'machine:')[0],1)['verdict'],'ACCEPT')
    def test_wrong_count_and_unchecked(self):
        for value in [self.output.replace(b'checked 1',b'checked 0'),self.output.replace(b'0 added unchecked',b'1 added unchecked')]:
            self.assertNotEqual(classify(self.receipt,b'',value,1)['verdict'],'ACCEPT')
    def test_negative_is_exact_and_needs_loaded(self):
        r={**self.receipt,'exit_code':1}; failure='FAIL LALNest (line 99): exact type mismatch'
        output=self.output.split(b'checked')[0]+failure.encode()+b'\n'
        self.assertEqual(classify(r,b'',output,1,failure)['verdict'],'INTENDED_REJECT')
        self.assertNotEqual(classify(r,b'',output,1,'other')['verdict'],'INTENDED_REJECT')
        self.assertNotEqual(classify(r,b'',failure.encode(),1,failure)['verdict'],'INTENDED_REJECT')
    def test_resource_and_cleanup_fail_closed(self):
        for updates in [dict(timed_out=True),dict(memory_exceeded=True),dict(cleanup_complete=False),dict(memory_monitor_samples=0)]:
            self.assertEqual(classify({**self.receipt,**updates},b'',self.output,1)['verdict'],'PROCESS_CONTROL_FAILURE')
    def test_signal_and_parse_not_reject(self):
        self.assertEqual(classify({**self.receipt,'exit_code':-9},b'',b'',1)['verdict'],'PROCESS_FAILURE')
        self.assertNotEqual(classify({**self.receipt,'exit_code':1},b'',b'error: invalid JSON\n',1)['verdict'],'INTENDED_REJECT')

if __name__=='__main__': unittest.main()
