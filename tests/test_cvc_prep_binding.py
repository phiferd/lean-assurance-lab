"""Runtime input integrity and static reachability boundary (no child processes)."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'lib'))
from cvc_prep_binding import file_binding, reachable_libraries, runtime_files, verify_runtime


class RuntimeBindingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        for f in ['bin/lean', 'lib/lean/core.olean', 'include/lean/version.h']:
            p = self.root / f
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(f.encode())
        self.manifest = {'schema_version': 1, 'runtime_root': str(self.root), 'platform': {'fixture': True},
                         'files': runtime_files(self.root),
                         'version_header': file_binding(self.root / 'include/lean/version.h', 'include/lean/version.h'),
                         'linkage': [{'path': 'bin/lean', 'dependencies': [{'kind': 'system', 'name': '/usr/lib/libSystem.B.dylib'}]}],
                         'lean_static_loader_closure': ['bin/lean'],
                         'unresolved_libraries': [], 'external_non_system_libraries': []}

    def verify(self):
        with patch('cvc_prep_binding.platform_identity', return_value={'fixture': True}):
            verify_runtime(ROOT, self.manifest)

    def test_exact_runtime(self):
        self.verify()

    def test_mutations_rejected(self):
        for name, mutate in [
            ('content', lambda: (self.root / 'lib/lean/core.olean').write_bytes(b'changed')),
            ('new_file', lambda: (self.root / 'lib/extra.olean').write_bytes(b'extra')),
            ('mode', lambda: (self.root / 'bin/lean').chmod(0o700)),
            ('header', lambda: (self.root / 'include/lean/version.h').write_bytes(b'new version')),
        ]:
            with self.subTest(name=name):
                p = self.root / 'lib/extra.olean'
                if p.exists():
                    p.unlink()
                (self.root / 'bin/lean').chmod(0o644)
                (self.root / 'lib/lean/core.olean').write_bytes(b'lib/lean/core.olean')
                (self.root / 'include/lean/version.h').write_bytes(b'include/lean/version.h')
                mutate()
                with self.assertRaises(ValueError):
                    self.verify()

    def test_symlink_rejected_even_if_resolved_content_matches(self):
        (self.root / 'lib/link').symlink_to(self.root / 'bin/lean')
        with self.assertRaisesRegex(ValueError, 'symlink'):
            self.verify()

    def test_platform_change_rejected(self):
        self.manifest['platform'] = {'changed': True}
        with self.assertRaisesRegex(ValueError, 'platform'):
            self.verify()

    def test_missing_reachable_dependency_rejected(self):
        self.manifest['unresolved_libraries'] = [{'object': 'bin/lean', 'name': '@rpath/missing.dylib'}]
        with self.assertRaisesRegex(ValueError, 'unresolved dependency'):
            self.verify()

    def test_unreachable_inventory_does_not_claim_lean_load_failure(self):
        self.manifest['unresolved_libraries'] = [{'object': 'lib/native-tool.dylib', 'name': '@rpath/missing.dylib'}]
        self.verify()

    def test_recursive_closure_and_missing_node(self):
        rows = [{'path': 'bin/lean', 'dependencies': [{'kind': 'runtime', 'resolved': 'lib/A.dylib'}]},
                {'path': 'lib/A.dylib', 'dependencies': [{'kind': 'runtime', 'resolved': 'lib/B.dylib'}]},
                {'path': 'lib/B.dylib', 'dependencies': [{'kind': 'runtime', 'resolved': 'lib/A.dylib'}]},
                {'path': 'lib/unused.dylib', 'dependencies': []}]
        self.assertEqual(reachable_libraries(rows), ['bin/lean', 'lib/A.dylib', 'lib/B.dylib'])
        with self.assertRaisesRegex(ValueError, 'missing reachable'):
            reachable_libraries(rows[:2])

    def test_unbound_native_target_rejected(self):
        self.manifest['linkage'][0]['dependencies'] = [{'kind': 'runtime', 'resolved': 'missing'}]
        with self.assertRaises(ValueError):
            self.verify()


if __name__ == '__main__':
    unittest.main()
