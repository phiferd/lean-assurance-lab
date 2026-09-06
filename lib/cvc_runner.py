"""Fail-closed CVC-RUNNER-1 endpoint after unresolved control tests.

The incomplete implementation is retained as evidence under cvc-runner-1/draft.
An explicit successor must establish the controls before CVC-3 is promoted.
This module has no compiler, subprocess, materialization, or session-start path.
"""
from __future__ import annotations

PROTOCOL_ID = 'CVC3-U1-PROOF-0001'
DIAGNOSTIC = 'results/research/conditional-validation-contracts/cvc-runner-1/stop-diagnostic.json'
STOP = ('CVC-RUNNER-1 closed BOUNDED_UNRESOLVED: cancellation and accounting '
        'controls failed; CVC-3 execution is disabled. See ' + DIAGNOSTIC)


def refuse(*args, **kwargs):
    raise ValueError(STOP)


preflight = refuse
execute = refuse
start_session = refuse
end_session = refuse
run_process = refuse


def main(argv=None):
    import sys
    print(STOP, file=sys.stderr)
    return 1


if __name__ == '__main__':
    raise SystemExit(main())
