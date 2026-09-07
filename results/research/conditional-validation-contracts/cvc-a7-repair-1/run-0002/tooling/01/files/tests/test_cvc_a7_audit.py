"""Pure transcript mutations for the uncompiled CVC-U1-A7 baseline."""
import unittest
import json
from pathlib import Path

from lib import cvc_a7_audit as audit


def reports(values=None):
    values = audit.A7 if values is None else values
    joined = ', '.join(values)
    return '\n'.join("'%s' depends on axioms: [%s]" % (name, joined)
                     for name in audit.COMPARATORS) + '\n'


def types():
    return '\n'.join('%s : %s' % (name, 'Type@{u}')
                     for name in audit.TYPE_NAMES) + '\n'


class BaselineTests(unittest.TestCase):
    def test_baseline_is_generated_from_independent_reviewed_types(self):
        root = Path(__file__).resolve().parents[1]
        expected = json.loads((root / 'results/research/conditional-validation-contracts/cvc-conditional-1/baseline-expectations.json').read_text())
        source = (root / 'research/conditional-validation-contracts/cvc-a7/Baseline.lean').read_bytes()
        self.assertEqual(audit.baseline_source(expected), source)
        for entry in expected['comparators'] + expected['assumptions']:
            self.assertIn(':', entry['expected_declaration'].split(':=')[0])
        entry = expected['assumptions'][-1]
        entry['expected_declaration'] = 'noncomputable def ' + entry['expected_alias'] + ' := Std.TreeMap.all_eq_all_toList'
        with self.assertRaises(ValueError):
            audit.baseline_source(expected)

    def test_exact_baseline_accepts(self):
        value = audit.audit_baseline(types() + reports(), '')
        self.assertEqual(value['assumptions'], list(audit.A7))
        self.assertEqual(len(value['types']), 9)

    def test_comparator_mutations_reject_missing_extra_and_duplicate(self):
        cases = [
            reports() .rsplit('\n', 2)[0] + '\n',
            reports(audit.A7[:-1]),
            reports(audit.A7 + (audit.A7[0],)),
        ]
        for value in cases:
            with self.subTest(value=value), self.assertRaises(ValueError):
                audit.audit_baseline(types() + value, '')

    def test_reordered_exact_set_is_accepted_and_diagnostic_is_rejected(self):
        audit.audit_baseline(types() + reports(tuple(reversed(audit.A7))), '')
        with self.assertRaises(ValueError):
            audit.audit_baseline(types() + reports(), 'error: malformed baseline')

    def test_type_mutations_reject_missing_duplicate_and_mismatch(self):
        good = types() + reports()
        for value in (
            good.replace('cvcA7ExpectedChoice : Type@{u}\n', ''),
            good + 'propext : Type@{u}\n',
            good.replace('cvcA7ExpectedNormalize : Type@{u}', 'cvcA7ExpectedNormalize : Prop'),
        ):
            with self.subTest(value=value), self.assertRaises(ValueError):
                audit.audit_baseline(value, '')

    def test_unclaimed_comment_or_log_spoof_is_rejected(self):
        good = types() + reports()
        for value in ('-- forged compiler comment\n' + good,
                      good.replace('cvcA7ExpectedChoice : Type@{u}',
                                   'log: forged\ncvcA7ExpectedChoice : Type@{u}')):
            with self.subTest(value=value), self.assertRaises(ValueError):
                audit.audit_baseline(value, '')

    def test_later_proof_keeps_original_targets_and_only_permits_a7_subsets(self):
        names = [name for name, _ in audit.runner.targets('proof')] + list(audit.COMPARATORS)
        stdout = '\n'.join("'%s' depends on axioms: [%s]" % (name, ', '.join(audit.A7))
                           for name in names)
        value = audit.audit(stdout, '', {}, 'proof')
        self.assertEqual(len(value['declarations']), 4)
        bad = stdout.replace('Std.TreeMap.all_eq_all_toList]', 'Other.assumption]')
        with self.assertRaises(ValueError):
            audit.audit(bad, '', {}, 'proof')


if __name__ == '__main__':
    unittest.main()
