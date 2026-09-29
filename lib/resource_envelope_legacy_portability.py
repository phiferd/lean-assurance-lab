"""Run the frozen resource portability test on its original attempt scope.

The test and historical replay remain byte-identical. This context changes
only the repository projection passed to the saved original replay, and is
used by current suite entry points after closure-control receipts were added.
"""

from contextlib import contextmanager

from lib import resource_envelope_replay
from lib.resource_envelope_attempt_projection import replay_attempts


@contextmanager
def historical_attempt_scope():
    original = resource_envelope_replay.replay

    def projected(root):
        return replay_attempts(root, original)

    resource_envelope_replay.replay = projected
    try:
        yield
    finally:
        resource_envelope_replay.replay = original
