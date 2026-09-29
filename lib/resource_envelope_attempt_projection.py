"""Project retained scientific attempts for the frozen resource custody replay.

Later closure-control fixtures live beside the research item but are not part
of its frozen process inventory. The original replay receives a temporary
repository mirror containing every preflight, construction, smoke, and science
attempt directory, including any newly added attempt in those families.
"""

from pathlib import Path
import shutil
import tempfile
from typing import Callable

from lib.resource_envelope_replay import REL, ReplayError


def replay_attempts(root: Path, historical_replay: Callable[[Path], dict]) -> dict:
    root = root.resolve()
    base = root / REL
    with tempfile.TemporaryDirectory(prefix="resource-attempt-replay-") as directory:
        mirror = Path(directory)
        target = mirror / REL
        target.mkdir(parents=True)
        for family in ("preflight", "construction", "smoke", "science"):
            for source in sorted(base.glob(f"{family}-run-*")):
                if not source.is_dir() or source.is_symlink():
                    raise ReplayError(f"invalid attempt directory: {source}")
                if any(path.is_symlink() for path in source.rglob("*")):
                    raise ReplayError(f"symlink in attempt directory: {source}")
                shutil.copytree(source, target / source.name)
        return historical_replay(mirror)
