"""Pure adversarial unit tests for CVC-AXIOMS-1 evidence parsing."""
import json
from pathlib import Path
import tempfile
import unittest
from contextlib import contextmanager
import shutil

from lib import cvc_axioms as evidence


class CvcAxiomsHelpersTests(unittest.TestCase):
    def test_comparator_reports_extract_exact_multiline_lists(self):
        stdout = "'Lean.Level.isEquiv'_wf' depends on axioms: [propext,\n Classical.choice]\n'Lean.Level.isEquiv'_complete' depends on axioms: [propext, Classical.choice]\n"
        self.assertEqual(evidence.comparator_reports(stdout)[evidence.COMPARATORS[0]], ['propext', 'Classical.choice'])

    def test_comparator_reports_reject_missing_and_duplicate(self):
        missing = "'Lean.Level.isEquiv'_wf' depends on axioms: [propext]\n"
        with self.assertRaises(ValueError): evidence.comparator_reports(missing)
        duplicate = "'Lean.Level.isEquiv'_wf' depends on axioms: [propext, propext]\n'Lean.Level.isEquiv'_complete' depends on axioms: [propext]\n"
        with self.assertRaises(ValueError): evidence.comparator_reports(duplicate)

    def test_sessions_reject_counter_and_duration_tampering(self):
        work = {'sessions': [{'number': 1, 'started_at': '2026-09-07T00:00:00+00:00',
                              'ended_at': '2026-09-07T00:01:00+00:00', 'elapsed_seconds': 60}],
                'total_active_seconds': 60}
        self.assertEqual(evidence._sessions(work), 60)
        work['sessions'][0]['number'] = 2
        with self.assertRaises(ValueError): evidence._sessions(work)
        work['sessions'][0]['number'] = 1; work['sessions'][0]['elapsed_seconds'] = 61
        with self.assertRaises(ValueError): evidence._sessions(work)

    def test_source_excerpt_rejects_misbinding_and_changed_hash(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); source = root / 'source'; source.write_text('one\ntwo\n')
            value = {'sources': [{'id': 'x', 'path': str(source), 'sha256': evidence._sha(source), 'bytes': 8,
                                  'prior_binding': {'status': 'PREVIOUSLY_PINNED_RELEASE_LOCAL_SOURCE_HASHED_NOW'}}] * 6,
                     'excerpts': []}
            # Duplicate six sources fails before any source can be trusted.
            with self.assertRaises(ValueError): evidence._sources(value, False)

    def test_manifest_binding_rejects_changed_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); path = root / 'evidence'; path.write_text('old')
            row = {'path': 'evidence', 'sha256': evidence._sha(path), 'bytes': 3}
            self.assertEqual(evidence._binding(root, row), 'evidence')
            path.write_text('new')
            with self.assertRaises(ValueError): evidence._binding(root, row)

    def test_statement_rejects_valid_but_unrelated_excerpt(self):
        row = {'name': 'propext', 'declaration_text': 'axiom propext {a b : Prop} : (a ↔ b) → a = b',
               'statement_excerpt_ids': ['wrong']}
        excerpts = {'wrong': {'source_id': 'Core', 'text': 'axiom Quot.sound : True'}}
        with self.assertRaises(ValueError): evidence._statement(row, excerpts)


class CvcAxiomsClosureTests(unittest.TestCase):
    """Mutate a copied real closure and rebind it; never launch a runtime."""

    @contextmanager
    def copied_closure(self):
        donor = Path(__file__).resolve().parents[1]
        manifest = json.loads((donor / evidence.MANIFEST).read_text())
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for relative in [evidence.MANIFEST] + [r['path'] for r in manifest['files']]:
                target = root / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(donor / relative, target)
            yield root

    def mutate_and_rebind(self, root, relative, mutation):
        path = root / relative
        value = json.loads(path.read_text())
        mutation(value)
        path.write_text(json.dumps(value, indent=2) + '\n')
        manifest_path = root / evidence.MANIFEST
        manifest = json.loads(manifest_path.read_text())
        row = next(r for r in manifest['files'] if r['path'] == relative)
        row.update(sha256=evidence._sha(path), bytes=path.stat().st_size)
        manifest_path.write_text(json.dumps(manifest))

    def test_real_closure_validates_without_source_payloads(self):
        with self.copied_closure() as root:
            self.assertEqual(evidence.validate(root)['assumptions'], 7)

    def test_omitted_assumption_rejected_after_rebinding(self):
        with self.copied_closure() as root:
            self.mutate_and_rebind(root, evidence.ASSESSMENT, lambda a: a['assumptions'].pop())
            with self.assertRaisesRegex(ValueError, 'assumption table'):
                evidence.validate(root)

    def test_missing_or_nonzero_operation_rejected_after_rebinding(self):
        for replacement in ({}, {'proof_builds': 1}):
            with self.subTest(replacement=replacement), self.copied_closure() as root:
                self.mutate_and_rebind(root, evidence.WORK,
                    lambda w: w.update(research_operations=replacement))
                with self.assertRaisesRegex(ValueError, 'forbidden research operation'):
                    evidence.validate(root)

    def test_old_allowlist_cannot_be_rewritten_and_rebound(self):
        with self.copied_closure() as root:
            self.mutate_and_rebind(root, evidence.OLD_ASSUMPTIONS,
                lambda a: a['conditional_axiom_policy']['source_helpers_allowed'].append(
                    'Lean.Level.instLawfulBEqLevel'))
            with self.assertRaisesRegex(ValueError, 'frozen predecessor changed'):
                evidence.validate(root)

    def test_changed_statement_type_rejected_after_rebinding(self):
        with self.copied_closure() as root:
            self.mutate_and_rebind(root, evidence.ASSESSMENT,
                lambda a: a['assumptions'][0].update(declaration_text='axiom propext : False'))
            with self.assertRaisesRegex(ValueError, 'declaration source/excerpt mismatch'):
                evidence.validate(root)

    def test_valid_unrelated_statement_excerpt_rejected_after_rebinding(self):
        with self.copied_closure() as root:
            self.mutate_and_rebind(root, evidence.ASSESSMENT,
                lambda a: a['assumptions'][0].update(statement_excerpt_ids=['Core:781-804']))
            with self.assertRaisesRegex(ValueError, 'declaration source/excerpt mismatch'):
                evidence.validate(root)

    def test_source_byte_mismatch_fails_full_check(self):
        with tempfile.TemporaryDirectory() as directory:
            donor = Path(__file__).resolve().parents[1]
            excerpts = json.loads((donor / evidence.EXCERPTS).read_text())
            excerpts['excerpts'] = []
            for row in excerpts['sources']:
                source = Path(directory) / (row['id'] + '.lean')
                source.write_text('unchanged\n')
                digest = evidence._sha(source)
                row.update(path=str(source), sha256=digest, bytes=source.stat().st_size)
                excerpts['excerpts'].append(dict(id=row['id'], source_id=row['id'],
                    start_line=1, end_line=1, text='unchanged\n', sha256=digest))
            (Path(directory) / 'Core.lean').write_text('changed\n')
            with self.assertRaisesRegex(ValueError, 'source hash mismatch: Core'):
                evidence._sources(excerpts, True)


if __name__ == '__main__':
    unittest.main()
