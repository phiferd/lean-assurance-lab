"""Portable execution context for the live cache historical validator.

The cache experiment receipts and the evolving historical validator remain
unchanged.  This adapter reads preserved bytes from the current checkout while
retaining the absolute workspace identity recorded by the checker attempts.
"""
from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path

from lib import survivor_cache_historical as historical
from lib import survivor_cache_runner as runner
from lib.portfolio_historical_snapshot_v2 import (
    _RecordedWorkspacePath,
    _recorded_workspace,
)


class _CacheWorkspacePath(_RecordedWorkspacePath):
    """Add the relative-path operation used by the cache receipt validator."""

    def relative_to(self, other):
        storage = other.storage if isinstance(other, _RecordedWorkspacePath) else other
        return self.storage.relative_to(storage)


def evidence(root):
    """Validate cache receipts without rebasing their recorded commands."""

    storage_root = Path(root).resolve()
    events, state = runner.Ledger(storage_root).read()
    recorded_root = _recorded_workspace(events)
    projected_root = _CacheWorkspacePath(storage_root, recorded_root)
    runner.verify_attempts(projected_root, events)
    return state


@contextmanager
def portable_validation():
    """Install the adapter only while the current unit suite is executing."""

    original = historical.evidence
    historical.evidence = evidence
    try:
        yield
    finally:
        historical.evidence = original
