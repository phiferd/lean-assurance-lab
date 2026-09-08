from copy import deepcopy
import json
from pathlib import Path
import unittest
from lib.cvc4_ownership_inputs import PROPOSAL, build, transition, projection

ROOT = Path(__file__).resolve().parents[1]


class OwnershipInsertionTests(unittest.TestCase):
    def setUp(self):
        self.specs = json.loads((ROOT / PROPOSAL).read_text())['representation_change']['cases']

    def test_exact_transition_and_strict_boundary(self):
        for spec in self.specs:
            old = (ROOT / spec['input']['path']).read_bytes()
            new, outcome = transition(old, spec)
            self.assertEqual(len(new.splitlines()), len(old.splitlines()) + 1)
            self.assertEqual(projection(old), projection(new))
            self.assertEqual(outcome, 'ACCEPTED_STRUCTURAL_SUBSET' if 'CONTROL' in spec['predecessor_case'] else 'REFUSED_UNOWNED_UNIVERSE_PARAMETER')

    def test_committed_successor_bytes(self):
        self.assertEqual(len(build(ROOT)['cases']), 2)

    def test_no_extra_edit_or_record(self):
        for spec in self.specs:
            old = (ROOT / spec['input']['path']).read_bytes()
            new, _ = transition(old, spec)
            for bad in (old, new + b'\n', new.replace(b'"safe"', b'"unsafe"'), new.replace(b'"il":3', b'"il":4')):
                with self.assertRaises(ValueError):
                    transition(old, spec, bad)

    def test_wrong_name_or_level_identity(self):
        for spec in self.specs:
            old = (ROOT / spec['input']['path']).read_bytes()
            for insertion in ({'il': 2, 'param': spec['insert_record']['param']}, {'il': 3, 'param': 1}):
                bad = deepcopy(spec)
                bad['insert_record'] = insertion
                with self.assertRaises(ValueError):
                    transition(old, bad)

    def test_ast_or_parameter_order_cannot_change(self):
        spec = deepcopy(self.specs[0])
        old = (ROOT / spec['input']['path']).read_bytes()
        spec['unchanged_artifact']['params'].reverse()
        with self.assertRaisesRegex(ValueError, 'AST changed'):
            transition(old, spec)

    def test_predecessor_cannot_change(self):
        for spec in self.specs:
            old = (ROOT / spec['input']['path']).read_bytes()
            with self.assertRaisesRegex(ValueError, 'predecessor bytes changed'):
                transition(old + b'\n', spec)


if __name__ == '__main__':
    unittest.main()
