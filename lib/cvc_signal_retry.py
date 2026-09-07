"""Prospective Darwin validation adapter for a disappearing process group.

Retained diagnostics show SIGKILL may transiently return EPERM after SIGTERM
has removed the group leader. Retry the same kernel operation only while that
leader is absent. Success, ESRCH and persistent denial retain their OS meaning;
this adapter never certifies cleanup or changes historical process receipts.
"""
from contextlib import contextmanager
import errno
import os
import sys
import time


RETRY_SECONDS = .05
RETRY_SLEEP_SECONDS = .001
MAX_RETRIES = 50


def _leader_absent(group):
    try:
        os.getpgid(group)
    except ProcessLookupError:
        return True
    except OSError:
        return False
    return False


def _killpg_with_retry(original, group, sig):
    deadline = time.monotonic() + RETRY_SECONDS
    retries = 0
    while True:
        try:
            return original(group, sig)
        except OSError as error:
            if error.errno != errno.EPERM:
                raise
            # A live or reused leader PID, or inability to inspect it, supplies
            # no evidence for this narrowly observed disappearing-group case.
            if not _leader_absent(group):
                raise
            remaining = deadline - time.monotonic()
            if remaining <= 0 or retries >= MAX_RETRIES:
                raise
            time.sleep(min(RETRY_SLEEP_SECONDS, remaining))
            # Never initiate another signal after the monotonic retry deadline,
            # including when scheduling delayed the preceding short sleep.
            if time.monotonic() >= deadline or not _leader_absent(group):
                raise
            # Inspection can itself be delayed. Check the deadline once more
            # immediately before the identical retry is permitted.
            if time.monotonic() >= deadline:
                raise
            retries += 1


@contextmanager
def signal_retry():
    """Temporarily apply the bounded adapter only to Darwin validation runs."""
    if sys.platform != 'darwin':
        yield
        return
    original = os.killpg
    if getattr(original, '_cvc_signal_retry', False) is True:
        # Nested validation contexts must not multiply the retry time bound.
        yield
        return

    def adapted(group, sig):
        return _killpg_with_retry(original, group, sig)

    adapted._cvc_signal_retry = True
    os.killpg = adapted
    try:
        yield
    finally:
        os.killpg = original
