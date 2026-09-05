import importlib.machinery
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
loader = importlib.machinery.SourceFileLoader('ecosystem_cases', str(ROOT/'scripts/execute-ecosystem-cases'))
spec = importlib.util.spec_from_loader(loader.name, loader)
cases = importlib.util.module_from_spec(spec)
loader.exec_module(cases)

class EcosystemCasesTests(unittest.TestCase):
    def test_failure_classes_are_not_rejections(self):
        for checker in ['nanoda', 'kiota', 'official']:
            self.assertEqual(cases.normalize(checker, None, '', ''), 'TIMEOUT')
            self.assertEqual(cases.normalize(checker, -9, '', ''), 'CRASH')
            self.assertNotEqual(cases.normalize(checker, 1, '', 'unrelated failure'), 'REJECT')
        self.assertEqual(cases.normalize('nanoda', 101, '', 'index out of bounds'), 'CRASH')
        self.assertEqual(cases.normalize('kiota', 2, '', 'DECLINE: feature'), 'DECLINE')
        self.assertEqual(cases.normalize('kiota', 1, '', 'REJECT: type mismatch'), 'REJECT')
        self.assertEqual(cases.normalize('nanoda', 0, '', ''), 'UNATTRIBUTED_SUCCESS')

    def test_fixed_pairs_only_change_target_field(self):
        a,b = [records for _,records in cases.cases('nanoda-gen-f19ffc8a2e9b')]
        self.assertEqual(a[:-1], b[:-1])
        self.assertEqual(a[-1]['def']['type'], 1)
        self.assertEqual(b[-1]['def']['type'], 2)
        a,b = [records for _,records in cases.cases('nanoda-gen-21ef4d1d32a1')]
        self.assertEqual(a[:-2], b[:-2])
        self.assertEqual(a[-2]['letE']['type'], b[-2]['letE']['type'])
        self.assertNotEqual(a[-2]['letE']['value'], b[-2]['letE']['value'])
        self.assertEqual(a[-1]['def']['value'], b[-1]['def']['value'])

if __name__ == '__main__': unittest.main()
