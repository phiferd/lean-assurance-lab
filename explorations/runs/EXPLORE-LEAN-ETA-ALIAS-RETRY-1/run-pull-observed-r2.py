#!/usr/bin/env python3
"""Mechanical CPU-time parser repair for the frozen pull observer."""

from __future__ import annotations

import importlib.util
from pathlib import Path


SOURCE = Path(__file__).with_name("run-pull-observed.py")
SPEC = importlib.util.spec_from_file_location("frozen_pull_observer", SOURCE)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def cpu_seconds(value: str) -> float:
    days = 0
    if "-" in value:
        day_text, value = value.split("-", 1)
        days = int(day_text)
    fields = value.split(":")
    seconds = float(fields[-1])
    minutes = int(fields[-2]) if len(fields) >= 2 else 0
    hours = int(fields[-3]) if len(fields) >= 3 else 0
    return days * 86400 + hours * 3600 + minutes * 60 + seconds


MODULE.cpu_seconds = cpu_seconds
raise SystemExit(MODULE.main())
