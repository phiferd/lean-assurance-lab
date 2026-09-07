"""Pure mutations of fixed, retained A7 output; no compiler or fixture launch."""
import copy
import hashlib
import json
from pathlib import Path
import unittest

from lib import cvc_a7_audit as historical
from lib import cvc_a7_repair_audit as audit


ROOT = Path(__file__).resolve().parents[1]
OLD_STDOUT = ROOT / 'results/research/conditional-validation-contracts/cvc-3-conditional/run-0001/attempts/02/stdout'
EXPECTED = ROOT / 'results/research/conditional-validation-contracts/cvc-conditional-1/baseline-expectations.json'


def representative():
    """Test data only: remove exactly the known nine-warning preamble.

    This does not admit historical evidence or run inside the production audit.
    A changed/unknown preamble fails the fixed digest before removal.
    """
    raw = OLD_STDOUT.read_bytes()
    preamble = raw[:1862]
    if hashlib.sha256(preamble).hexdigest() != 'f5da4d60a8f5fab22d9efa101e41ee4669c629a8a66846caf690aed6b5b034fc':
        raise AssertionError('retained warning preamble changed')
    return raw[1862:].decode()


def reports(names, values):
    return '\n'.join("'%s' depends on axioms: [%s]" % (name, ', '.join(values)) for name in names) + '\n'


def proof(values=()):
    return (reports([name for name, _ in audit.runner.targets('proof')], values)
            + reports(audit.COMPARATORS, audit.A7))


class RepairedBaselineTests(unittest.TestCase):
    def test_historical_warning_transcript_still_rejected(self):
        with self.assertRaisesRegex(ValueError, 'source-positioned compiler diagnostic'):
            audit.audit_baseline(OLD_STDOUT.read_text(), '')
        # The old parser is unchanged and still fails this representative format.
        with self.assertRaisesRegex(ValueError, 'malformed full axiom list'):
            historical.audit_baseline(representative(), '')

    def test_real_format_with_exact_warning_preamble_removed_in_fixture(self):
        result = audit.audit_baseline(representative(), '')
        self.assertEqual(result['status'], 'BASELINE_TYPES_AND_AXIOMS_MATCH')
        self.assertEqual(result['assumptions'], list(audit.A7))
        self.assertEqual([row['actual'] for row in result['types']], [p[0] for p in audit.TYPE_PAIRS])
        for values in result['transitive_axioms'].values():
            self.assertEqual(values, list(audit.A7))

    def test_wrapped_headers_can_use_whitespace_without_changing_types(self):
        raw = representative().replace('u_1,\n    u_2} :', 'u_1, u_2} :')
        raw = raw.replace('@cvcA7ExpectedPropext : ∀', '@cvcA7ExpectedPropext :  ∀')
        audit.audit_baseline(raw, '')

    def test_pair_type_mutations_are_scientific_mismatch(self):
        raw = representative()
        mutations = [
            raw.replace('@cvcA7ExpectedPropext : ∀ {a b : Prop}, Iff a b',
                        '@cvcA7ExpectedPropext : ∀ {a b : Prop}, Iff b a'),
            raw.replace('cvcA7ExpectedNormalize : @Eq.{1}', 'cvcA7ExpectedNormalize : @Eq.{2}'),
        ]
        for value in mutations:
            with self.subTest(value=value), self.assertRaises(audit.ScientificMismatch):
                audit.audit_baseline(value, '')

    def test_missing_extra_and_duplicate_axioms_rejected(self):
        raw = representative()
        for old, new in [
            ('propext,\n Classical.choice', 'Classical.choice'),
            ('propext,\n Classical.choice', 'Other.assumption,\n propext,\n Classical.choice'),
        ]:
            with self.subTest(new=new), self.assertRaises(audit.ScientificMismatch):
                audit.audit_baseline(raw.replace(old, new, 1), '')
        for value in (
            raw.replace('propext,\n Classical.choice', 'propext,\n propext,\n Classical.choice', 1),
            raw.replace('Classical.choice.{u},', 'Classical.choice,\n Classical.choice.{u},', 1),
        ):
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, 'duplicate axiom'):
                audit.audit_baseline(value, '')

    def test_missing_duplicate_and_extra_axiom_reports_rejected(self):
        raw = representative()
        first = raw.index("'Lean.Level.isEquiv'_wf' depends on")
        second = raw.index("'Lean.Level.isEquiv'_complete' depends on")
        for value in (raw[:second], raw + raw[first:second],
                      raw + "'Unknown.result' depends on axioms: [propext]\n"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                audit.audit_baseline(value, '')

    def test_missing_duplicate_reordered_and_extra_type_headers_rejected(self):
        raw = representative()
        actual = '@propext : ∀ {a b : Prop}, Iff a b → @Eq.{1} Prop a b\n'
        expected = '@cvcA7ExpectedPropext : ∀ {a b : Prop}, Iff a b → @Eq.{1} Prop a b\n'
        for value in (raw.replace(expected, ''), raw.replace(expected, actual),
                      raw.replace(actual + expected, expected + actual),
                      raw.replace(actual, 'Other.thing : Prop\n' + actual)):
            with self.subTest(value=value), self.assertRaises(ValueError):
                audit.audit_baseline(value, '')

    def test_universe_annotation_malformed_cases_rejected(self):
        raw = representative()
        for replacement in ('Classical.choice.{}', 'Classical.choice.{u,}',
                            'Classical.choice.{u,,v}', 'Classical.choice.{u, v}',
                            'Classical.choice.{u u}', 'Classical.choice.{u;warning}',
                            'Classical.choice.{u', 'Classical.choice.{{u}}',
                            'Classical.choice.{u}.extra', 'Classical.choice.{u} trailing'):
            with self.subTest(replacement=replacement), self.assertRaises(ValueError):
                audit.audit_baseline(raw.replace('Classical.choice.{u},', replacement + ',', 1), '')
        for old, new in [('propext,', 'propext.{u},'),
                         ('Std.TreeMap.all_eq_all_toList.{u, v}', 'Std.TreeMap.all_eq_all_toList.{u, u}'),
                         ('@Classical.choice.{u_1}', '@Classical.choice.{u_1,}'),
                         ('@Std.TreeMap.all_eq_all_toList.{u_1,\n    u_2}',
                          '@Std.TreeMap.all_eq_all_toList.{u_1,\nu_2}')]:
            with self.subTest(new=new), self.assertRaises(ValueError):
                audit.audit_baseline(raw.replace(old, new, 1), '')

    def test_both_header_universe_decorations_are_validated(self):
        raw = representative()
        with self.assertRaisesRegex(ValueError, 'paired header universe'):
            audit.audit_baseline(raw.replace('@cvcA7ExpectedChoice.{u_1}', '@cvcA7ExpectedChoice.{v}'), '')

    def test_diagnostics_are_never_removed_or_absorbed(self):
        raw = representative()
        for message in ('Baseline.lean:8:0: warning: unexpected warning\n',
                        'Baseline.lean:8:0: error: bad elaboration\n',
                        'Baseline.lean:8:0: unfamiliar: unknown diagnostic\n',
                        'warning: unpositioned warning\n',
                        '  information: indented diagnostic\n',
                        '  Note: diagnostic continuation\n',
                        'unknown compiler output\n'):
            with self.subTest(message=message), self.assertRaises(ValueError):
                audit.audit_baseline(message + raw, '')
            with self.subTest(stderr=message), self.assertRaises(ValueError):
                audit.audit_baseline(raw, message)
        # An identical diagnostic in both paired bodies must still be rejected.
        poisoned = raw.replace('Prop a b\n', 'Prop a b\n  warning: injected\n')
        with self.assertRaises(ValueError):
            audit.audit_baseline(poisoned, '')

    def test_repaired_source_keeps_independent_typed_declarations(self):
        expected = json.loads(EXPECTED.read_text())
        source = audit.baseline_source(expected)
        self.assertEqual(source, (ROOT / 'research/conditional-validation-contracts/cvc-a7-repair/Baseline.lean').read_bytes())
        for row in expected['comparators'] + expected['assumptions']:
            self.assertIn(row['expected_declaration'].encode(), source)
        old = historical.baseline_source(expected)
        added = source.replace(old.split(b'\n\n', 1)[1], b'').decode()
        self.assertEqual([line for line in added.splitlines() if line.startswith('set_option')],
                         ['set_option linter.defProp false', 'set_option warn.classDefReducibility false'])
        bad = copy.deepcopy(expected)
        bad['assumptions'][0]['expected_declaration'] = 'noncomputable def cvcA7ExpectedPropext := propext'
        with self.assertRaises(ValueError):
            audit.baseline_source(bad)


class RepairedProofTests(unittest.TestCase):
    def test_original_skeleton_and_a7_subsets_remain(self):
        result = audit.audit(proof(('propext', 'Classical.choice.{u}')), '', {})
        self.assertEqual(result['declarations'], [{'name': n, 'type': t} for n, t in audit.runner.TARGETS])
        self.assertEqual(result['transitive_axioms']['Lab.CVC2.preservation'], ['propext', 'Classical.choice'])
        self.assertEqual(result['model_id'], 'CVC-U1-A7')

    def test_empty_lab_assumptions_and_exact_counterexample_skeleton(self):
        value = proof().replace('depends on axioms: []', 'does not depend on any axioms')
        audit.audit(value, '', {})
        raw = reports([name for name, _ in audit.runner.targets('counterexample')], ())
        raw += reports(audit.COMPARATORS, audit.A7)
        result = audit.audit(raw, '', {}, 'counterexample')
        self.assertEqual(result['declarations'], [{'name': n, 'type': t} for n, t in audit.runner.NEGATIVE])

    def test_all_comparators_exact_and_unlisted_lab_axioms_rejected(self):
        for raw in (proof(('Other.assumption',)),
                    proof().replace('propext, Classical.choice', 'Classical.choice', 1)):
            with self.subTest(raw=raw), self.assertRaises(audit.ScientificMismatch):
                audit.audit(raw, '', {})

    def test_harmless_proof_warning_policy_preserved(self):
        audit.audit('Proof.lean:1:2: warning: unused simp argument\n' + proof(),
                    'warning: harmless linter diagnostic', {})

    def test_sorry_errors_and_duplicate_or_forged_reports_rejected(self):
        for raw, stderr in ((proof(('sorryAx',)), ''),
                            (proof(), 'error: invalid proof'),
                            ('Proof.lean:1:2: error: bad\n' + proof(), ''),
                            (proof() + reports(['Unknown.result'], ()), ''),
                            (proof() + "'Unknown.result' depends on axioms: broken\n", ''),
                            (proof() + reports(['Lab.CVC2.boundary'], ()), '')):
            with self.subTest(raw=raw, stderr=stderr), self.assertRaises(ValueError):
                audit.audit(raw, stderr, {})


if __name__ == '__main__':
    unittest.main()
