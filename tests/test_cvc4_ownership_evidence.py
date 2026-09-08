import unittest
from lib.cvc4_ownership_evidence import classify


class OwnershipEvidenceTests(unittest.TestCase):
    def test_candidate_acceptance_is_characterized_without_changing_hypothesis(self):
        expected = {'returncode': 0, 'stdout_pattern': 'Accepted 1 declarations\\.\\n', 'stderr_pattern': ''}
        self.assertEqual(classify({'role': 'candidate'}, {'returncode': 0, 'hypothesis_matched': False},
                                  'Accepted 1 declarations.\n', '', expected), 'ACCEPT')
        self.assertEqual(classify({'role': 'candidate'}, {'returncode': 101, 'hypothesis_matched': False},
                                  '', 'some panic', expected), 'UNRESOLVED_OUTPUT')

    def test_engineering_failure_is_not_refusal(self):
        self.assertEqual(classify({'role': 'candidate'}, {'control_error': 'cleanup unknown'}, '', '', {}), 'ENGINEERING_PAUSE')


if __name__ == '__main__':
    unittest.main()
