"""Materialize the frozen publication study for bounded successor validation.

The frozen Gate-12 validator remains the authority for the study contents.  This
module only prepares a disposable worktree around that validated content, so a
successor can exercise payload-dependent checks without reinterpreting old
files against the current research frontier.
"""

from __future__ import annotations

from contextlib import contextmanager
import json
import os
from pathlib import Path, PurePosixPath
import stat
import subprocess
import tempfile
import types
from typing import Any, Iterator


PREFIX = "results/research/declaration-validation-publication-study-"
ATTESTATION_PATH = PREFIX + "historical.json"
MANIFEST_PATH = PREFIX + "content-manifest.json"
VALIDATOR_PATH = "scripts/close-declaration-validation-publication-study"
VALIDATOR_ARGS = ["validate", "--content-only"]
_PAYLOAD_PREFIXES = ("external", "results/coverage")


def _load_history(root: Path, commit: str) -> Any:
    """Load the helper bytes bound by the attestation, never its live successor."""

    if len(commit) != 40 or any(character not in "0123456789abcdef" for character in commit):
        raise ValueError("publication-study historical commit must be a full lowercase 40-hex object id")
    verified = subprocess.run(
        ["git", "rev-parse", "--verify", f"{commit}^{{commit}}"], cwd=root,
        env=subprocess_env(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
    )
    if verified.returncode or verified.stdout.decode("ascii", errors="replace").strip() != commit:
        raise ValueError("publication-study historical commit is unavailable or does not resolve exactly")
    result = subprocess.run(
        ["git", "show", f"{commit}:scripts/publication_study_history.py"], cwd=root,
        env=subprocess_env(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
    )
    if result.returncode:
        raise ValueError("bound publication-study historical helper is unavailable")
    module = types.ModuleType("publication_study_snapshot_history")
    module.__file__ = f"{commit}:scripts/publication_study_history.py"
    exec(compile(result.stdout, module.__file__, "exec"), module.__dict__)
    return module


def _attestation(root: Path) -> tuple[dict[str, Any], bytes]:
    path = root / ATTESTATION_PATH
    try:
        content = path.read_bytes()
        document = json.loads(content)
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"publication-study historical attestation is unavailable: {error}") from error
    if not isinstance(document, dict):
        raise ValueError("publication-study historical attestation is not an object")
    return document, content


def _tracked_under(history: Any, root: Path, commit: str, prefix: str) -> bool:
    """Return whether the historical tree owns any path where a payload link goes."""

    tree, error = history._git(root, "ls-tree", "-r", "-z", "--full-tree", commit, "--", prefix)
    if error is not None or tree is None:
        raise ValueError(f"historical tree check is unavailable for {prefix}")
    return bool(tree)


def _restore_modes(modes: list[tuple[Path, int]]) -> None:
    for path, mode in reversed(modes):
        path.chmod(mode)


def _make_writable(paths: list[Path]) -> list[tuple[Path, int]]:
    """Temporarily permit only the directories needed for successor additions."""

    modes: list[tuple[Path, int]] = []
    for path in paths:
        if not path.is_dir():
            raise ValueError(f"historical snapshot directory is unavailable: {path}")
        mode = stat.S_IMODE(path.stat().st_mode)
        modes.append((path, mode))
        path.chmod(mode | stat.S_IWUSR | stat.S_IXUSR)
    return modes


def _snapshot_path(snapshot: Path, relative: str) -> Path:
    return snapshot.joinpath(*PurePosixPath(relative).parts)


def subprocess_env() -> dict[str, str]:
    """Return an environment that lets snapshot-local Git discovery work normally."""

    environment = os.environ.copy()
    for name in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE"):
        environment.pop(name, None)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    return environment


@contextmanager
def materialized_study(
    root: Path | str, *, attach_payload: bool, include_attestation: bool = False
) -> Iterator[Path]:
    """Yield an exact frozen study snapshot with optional ignored local payloads.

    The existing attestation is validated before extraction.  Payload links are
    permitted only at prefixes absent from the historical Git tree, so they
    cannot replace a committed study input.  The yielded tree and every added
    link are removed on context exit.
    """

    root_path = Path(root).resolve()
    attestation, attestation_bytes = _attestation(root_path)
    commit = attestation.get("historical_commit")
    if not isinstance(commit, str):
        raise ValueError("publication-study historical attestation has no historical commit")
    history = _load_history(root_path, commit)
    errors = history.validate_historical(
        root_path, attestation, MANIFEST_PATH, VALIDATOR_PATH, VALIDATOR_ARGS
    )
    if errors:
        raise ValueError("publication-study historical validation failed: " + "; ".join(errors))

    attachments: list[tuple[str, Path]] = []
    if attach_payload:
        for relative in _PAYLOAD_PREFIXES:
            source = root_path / relative
            if not source.is_dir():
                continue
            if _tracked_under(history, root_path, commit, relative):
                raise ValueError(f"refusing payload attachment over tracked historical path: {relative}")
            attachments.append((relative, source))

    if include_attestation:
        manifest_paths = {item.get("path") for item in attestation.get("artifacts", []) if isinstance(item, dict)}
        if ATTESTATION_PATH in manifest_paths or attestation.get("manifest", {}).get("path") == ATTESTATION_PATH:
            raise ValueError("historical attestation must remain excluded from the content manifest")

    git_dir, error = history._git(root_path, "rev-parse", "--absolute-git-dir")
    if error is not None or git_dir is None:
        raise ValueError("historical Git directory is unavailable")
    absolute_git_dir = Path(git_dir.decode("utf-8").strip()).resolve()

    with tempfile.TemporaryDirectory(prefix="publication-study-snapshot-") as temporary:
        snapshot = Path(temporary, "snapshot")
        snapshot.mkdir()
        errors = history._archive_snapshot(root_path, commit, snapshot)
        if errors:
            raise ValueError("publication-study snapshot extraction failed: " + "; ".join(errors))

        attestation_destination = _snapshot_path(snapshot, ATTESTATION_PATH)
        if include_attestation and (attestation_destination.exists() or attestation_destination.is_symlink()):
            raise ValueError("refusing to overwrite an archived path with the historical attestation")

        writable = [snapshot]
        if include_attestation:
            writable.append(attestation_destination.parent)
        writable.extend(_snapshot_path(snapshot, relative).parent for relative, _ in attachments)
        # The archive has already made these directories read-only.  De-duplicate
        # parents while retaining a stable order for mode restoration.
        unique_writable = list(dict.fromkeys(writable))
        modes = _make_writable(unique_writable)
        try:
            (snapshot / ".git").write_text(f"gitdir: {absolute_git_dir}\n", encoding="utf-8")
            if include_attestation:
                attestation_destination.write_bytes(attestation_bytes)
            for relative, source in attachments:
                destination = _snapshot_path(snapshot, relative)
                if destination.exists() or destination.is_symlink():
                    raise ValueError(f"refusing payload attachment over existing snapshot path: {relative}")
                destination.symlink_to(source, target_is_directory=True)
        finally:
            _restore_modes(modes)
        yield snapshot
