import json
from pathlib import Path
import shutil
import tempfile
import unittest

from lib.cvc4_artifacts import BASE, EXAMPLES, build, finite_cases, serialize
from lib.cvc2_artifact import decode_sort_definition

ROOT = Path(__file__).resolve().parents[1]


class CVC4ArtifactsTests(unittest.TestCase):
    def test_actual_fixed_cases_bind(self):
        result = build(ROOT)
        self.assertEqual(len(result['cases']), 6)
        self.assertEqual(len({r['pair_id'] for r in result['cases']}), 3)

    def test_serializer_preserves_zero_and_ownership_boundaries(self):
        rows = finite_cases(ROOT)
        header = json.loads((ROOT / rows[0]['input']['path']).read_bytes().splitlines()[0])
        zero = next(x for x in rows if x['id'] == 'E-ZERO')['artifact']
        self.assertEqual(decode_sort_definition(serialize(zero, header)), zero)
        unowned = next(x for x in rows if x['id'] == 'E-UNOWNED')['artifact']
        with self.assertRaisesRegex(ValueError, 'unowned universe parameter'):
            decode_sort_definition(serialize(unowned, header))

    def test_changed_candidate_cannot_be_regenerated_over(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for rel in [EXAMPLES, BASE + '/cases.json'] + [r['input']['path'] for r in build(ROOT)['cases']]:
                dst = root / rel
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / rel, dst)
            candidate = root / BASE / 'inputs/e-zero.ndjson'
            candidate.write_bytes(candidate.read_bytes().replace(b'"imax"', b'"max"'))
            with self.assertRaisesRegex(ValueError, 'differs'):
                build(root)
            with self.assertRaisesRegex(ValueError, 'refuse to overwrite'):
                build(root, write=True)


if __name__ == '__main__':
    unittest.main()
