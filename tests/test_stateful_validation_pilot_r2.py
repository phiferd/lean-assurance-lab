import json
import unittest
from pathlib import Path

class SyntaxRepairTests(unittest.TestCase):
    def test_first_failure_preserved_and_new_harness_changes_only_record_syntax(self):
        root=Path(__file__).resolve().parents[1]
        base=root/'results/research/stateful-validation-pilot-1'
        old=(base/'StatefulHarness.lean').read_text()
        new=(base/'StatefulHarnessR2.lean').read_text()
        before='''    let d : DefinitionVal := {name := name.toName, levelParams := [], type, value,
      hints := .abbrev, safety := .safe}'''
        after='''    let d : DefinitionVal := {
      name := name.toName
      levelParams := []
      type := type
      value := value
      hints := .abbrev
      safety := .safe
    }'''
        self.assertEqual(old.replace(before,after),new)
        result=json.loads((base/'compile-0001/result.json').read_text())
        self.assertEqual(result['status'],'REPAIR_REQUIRED')
        self.assertEqual(result['receipt']['exit_code'],1)
        self.assertTrue(result['receipt']['cleanup_complete'])
        self.assertIn('unexpected identifier',(base/'compile-0001/compiler.stdout').read_text())

if __name__=='__main__': unittest.main()
