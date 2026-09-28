import json
import unittest
from pathlib import Path

class OptionsRepairTests(unittest.TestCase):
    def test_exact_supported_option_setter_and_preserved_failed_attempt(self):
        base=Path(__file__).resolve().parents[1]/'results/research/stateful-validation-pilot-1'
        old=(base/'StatefulHarnessR2.lean').read_text(); new=(base/'StatefulHarnessR3.lean').read_text()
        before='|>.setNat `maxRecDepth 1000 |>.setNat `maxHeartbeats 200000'
        after='|>.set `maxRecDepth (1000 : Nat) |>.set `maxHeartbeats (200000 : Nat)'
        self.assertEqual(old.replace(before,after),new)
        self.assertIn('def set {α : Type} [KVMap.Value α]',(base/'tooling-options.lean').read_text())
        result=json.loads((base/'compile-0002/result.json').read_text())
        self.assertEqual(result['status'],'REPAIR_REQUIRED')
        self.assertTrue(result['receipt']['cleanup_complete'])
        self.assertIn('Invalid field `setNat`',(base/'compile-0002/compiler.stdout').read_text())

if __name__=='__main__': unittest.main()
