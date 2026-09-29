#!/usr/bin/env python3
"""Host retry of the unchanged E0 runner, writing a distinct attempt directory."""
from pathlib import Path

source_path = Path(__file__).with_name("run-screen.py")
source = source_path.read_text(encoding="utf-8")
old = 'RUN / "attempt-0001"'
new = 'RUN / "attempt-0002"'
if source.count(old) != 3:
    raise RuntimeError("unexpected frozen runner attempt-path shape")
code = compile(source.replace(old, new), str(source_path) + "#host-retry-r2", "exec")
exec(code, {"__name__": "__main__", "__file__": str(source_path)})
