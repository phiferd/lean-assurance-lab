"""Main-only delivery guards; all Git operations are mocked, with no network."""
from contextlib import redirect_stderr, redirect_stdout
import io
from pathlib import Path
import runpy
import subprocess
import unittest
from unittest.mock import patch

MODULE = runpy.run_path(str(Path(__file__).resolve().parents[1] / 'scripts/push-main'))
main = MODULE['main']
G = main.__globals__
COMMIT = 'a' * 40


class MainDeliveryTests(unittest.TestCase):
    def run_guard(self, changes=None, args=None, push_code=0):
        replies = {('symbolic-ref', '--quiet', '--short', 'HEAD'): 'main',
                   ('status', '--porcelain'): '',
                   ('remote', 'get-url', 'origin'): G['ORIGIN'],
                   ('remote', 'get-url', '--push', '--all', 'origin'): G['ORIGIN'],
                   ('rev-parse', 'HEAD'): COMMIT,
                   ('ls-remote', '--exit-code', 'origin', 'refs/heads/main'): COMMIT + '\trefs/heads/main'}
        replies.update(changes or {})
        output = io.StringIO()
        with patch.dict(G, read_git=lambda *a: replies[a]), \
             patch.object(subprocess, 'run', return_value=subprocess.CompletedProcess([], push_code)) as push, \
             redirect_stdout(output), redirect_stderr(output):
            code = main([] if args is None else args)
        return code, push, output.getvalue()

    def test_clean_main_pushes_only_exact_nonforced_main_ref(self):
        code, push, output = self.run_guard()
        self.assertEqual(code, 0)
        push.assert_called_once_with(['git', 'push', 'origin', 'refs/heads/main:refs/heads/main'],
                                     cwd=G['ROOT'], check=False)
        self.assertIn('origin/main contains ' + COMMIT, output)

    def test_task_branch_cannot_be_delivered(self):
        code, push, _ = self.run_guard({('symbolic-ref', '--quiet', '--short', 'HEAD'): 'repair'})
        self.assertNotEqual(code, 0); push.assert_not_called()

    def test_dirty_tree_cannot_be_delivered(self):
        code, push, _ = self.run_guard({('status', '--porcelain'): ' M AGENTS.md'})
        self.assertNotEqual(code, 0); push.assert_not_called()

    def test_wrong_or_multiple_remote_destinations_cannot_be_delivered(self):
        key = ('remote', 'get-url', '--push', '--all', 'origin')
        for changed in [{key: 'https://github.com/other/repo.git'},
                        {key: G['ORIGIN'] + '\nhttps://github.com/other/repo.git'},
                        {('remote', 'get-url', 'origin'): 'https://github.com/other/repo.git'}]:
            with self.subTest(changed=changed):
                code, push, _ = self.run_guard(changed)
                self.assertNotEqual(code, 0); push.assert_not_called()

    def test_push_options_and_alternate_branches_are_refused(self):
        for args in [['--force'], ['topic'], ['--delete', 'main']]:
            with self.subTest(args=args):
                code, push, _ = self.run_guard(args=args)
                self.assertNotEqual(code, 0); push.assert_not_called()

    def test_rejected_push_does_not_retry_or_change_branch(self):
        code, push, output = self.run_guard(push_code=1)
        self.assertEqual(code, 1); self.assertEqual(push.call_count, 1)
        self.assertIn('Do not switch delivery branches', output)

    def test_remote_commit_must_match_before_reporting_delivery(self):
        code, push, output = self.run_guard({('ls-remote', '--exit-code', 'origin', 'refs/heads/main'): 'b'*40 + '\trefs/heads/main'})
        self.assertEqual(code, 1); self.assertEqual(push.call_count, 1)
        self.assertNotIn('PASS:', output)

    def test_detached_head_or_git_error_fails_before_push(self):
        with patch.dict(G, read_git=lambda *args: (_ for _ in ()).throw(subprocess.CalledProcessError(1, 'git'))), \
             patch.object(subprocess, 'run') as push, redirect_stderr(io.StringIO()):
            self.assertEqual(main([]), 1)
            push.assert_not_called()


if __name__ == '__main__':
    unittest.main()
