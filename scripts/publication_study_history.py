"""Content-addressed historical validation for the publication study.

The functions in this module deliberately operate only on Git objects named by
an attestation.  They never read the corresponding live workspace paths while
checking historical content.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import stat
import subprocess
import sys
import tarfile
import tempfile
from typing import Any


_FULL_COMMIT_LENGTH = 40
_MANIFEST_TYPE = "PUBLICATION_STUDY_CONTENT_MANIFEST"
_ATTESTATION_TYPE = "PUBLICATION_STUDY_HISTORICAL_ATTESTATION"


def _sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _safe_path(value: Any) -> bool:
    """Return whether value is a canonical, repository-relative POSIX path."""

    if not isinstance(value, str) or not value or "\\" in value or ":" in value:
        return False
    path = PurePosixPath(value)
    return (
        not path.is_absolute()
        and path.parts
        and "." not in path.parts
        and ".." not in path.parts
        and str(path) == value
    )


def _full_commit(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == _FULL_COMMIT_LENGTH
        and all(character in "0123456789abcdef" for character in value)
    )


def _git(root: Path, *args: str, input_bytes: bytes | None = None) -> tuple[bytes | None, str | None]:
    result = subprocess.run(
        ["git", *args],
        cwd=root,
        input=input_bytes,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode:
        return None, result.stderr.decode("utf-8", errors="replace").strip()
    return result.stdout, None


def _exact_commit(root: Path, commit: Any) -> tuple[str | None, str | None]:
    if not _full_commit(commit):
        return None, "commit must be a full lowercase 40-hex object id"
    output, error = _git(root, "rev-parse", "--verify", f"{commit}^{{commit}}")
    if error is not None or output is None:
        return None, "commit is unavailable"
    resolved = output.decode("ascii", errors="replace").strip()
    if resolved != commit:
        return None, "commit does not resolve exactly"
    return resolved, None


def _binding_errors(root: Path, binding: Any, *, commit: str, label: str) -> tuple[bytes | None, list[str]]:
    if not isinstance(binding, dict):
        return None, [f"{label}: binding is not an object"]
    expected_keys = {"path", "git_commit", "git_blob", "sha256", "bytes"}
    if set(binding) != expected_keys:
        return None, [f"{label}: binding fields are not exact"]
    path = binding["path"]
    if not _safe_path(path):
        return None, [f"{label}: path is not safe"]
    if binding["git_commit"] != commit:
        return None, [f"{label}: commit differs from historical commit"]
    if not isinstance(binding["git_blob"], str) or not _full_commit(binding["git_blob"]):
        return None, [f"{label}: blob is not a full object id"]
    if not isinstance(binding["sha256"], str) or len(binding["sha256"]) != 64 or any(
        character not in "0123456789abcdef" for character in binding["sha256"]
    ):
        return None, [f"{label}: sha256 is invalid"]
    if not isinstance(binding["bytes"], int) or isinstance(binding["bytes"], bool) or binding["bytes"] < 0:
        return None, [f"{label}: byte count is invalid"]

    actual_blob, error = _git(root, "rev-parse", "--verify", f"{commit}:{path}")
    if error is not None or actual_blob is None:
        return None, [f"{label}: committed blob is unavailable"]
    blob = actual_blob.decode("ascii", errors="replace").strip()
    if blob != binding["git_blob"]:
        return None, [f"{label}: blob identity is stale"]
    object_type, error = _git(root, "cat-file", "-t", f"{commit}:{path}")
    if error is not None or object_type is None or object_type.strip() != b"blob":
        return None, [f"{label}: committed path is not a blob"]
    content, error = _git(root, "show", f"{commit}:{path}")
    if error is not None or content is None:
        return None, [f"{label}: committed blob content is unavailable"]
    errors: list[str] = []
    if _sha256(content) != binding["sha256"]:
        errors.append(f"{label}: SHA-256 is stale")
    if len(content) != binding["bytes"]:
        errors.append(f"{label}: byte count is stale")
    return content, errors


def git_binding(root: Path | str, commit: str, path: str) -> dict[str, Any]:
    """Bind one tracked file to exact bytes at a full historical commit."""

    root_path = Path(root).resolve()
    exact, error = _exact_commit(root_path, commit)
    if error is not None or exact is None:
        raise ValueError(f"invalid historical commit: {error}")
    if not _safe_path(path):
        raise ValueError("path must be a safe canonical repository-relative path")
    blob, error = _git(root_path, "rev-parse", "--verify", f"{exact}:{path}")
    if error is not None or blob is None:
        raise ValueError(f"committed path is unavailable: {path}")
    object_type, error = _git(root_path, "cat-file", "-t", f"{exact}:{path}")
    if error is not None or object_type is None or object_type.strip() != b"blob":
        raise ValueError(f"committed path is not a blob: {path}")
    content, error = _git(root_path, "show", f"{exact}:{path}")
    if error is not None or content is None:
        raise ValueError(f"committed content is unavailable: {path}")
    return {
        "path": path,
        "git_commit": exact,
        "git_blob": blob.decode("ascii").strip(),
        "sha256": _sha256(content),
        "bytes": len(content),
    }


def _manifest_files(document: Any, manifest_path: str) -> tuple[list[dict[str, Any]] | None, list[str]]:
    if not isinstance(document, dict) or set(document) != {"schema_version", "artifact_type", "files"}:
        return None, ["content manifest fields are not exact"]
    if document["schema_version"] != 1 or document["artifact_type"] != _MANIFEST_TYPE:
        return None, ["content manifest identity is invalid"]
    files = document["files"]
    if not isinstance(files, list):
        return None, ["content manifest files is not a list"]
    paths: list[str] = []
    for index, item in enumerate(files):
        if not isinstance(item, dict) or set(item) != {"path", "sha256", "bytes"}:
            return None, [f"content manifest file {index} fields are not exact"]
        path = item["path"]
        if not _safe_path(path):
            return None, [f"content manifest file {index} path is not safe"]
        if path == manifest_path:
            return None, ["content manifest must exclude itself"]
        if not isinstance(item["sha256"], str) or len(item["sha256"]) != 64 or any(
            character not in "0123456789abcdef" for character in item["sha256"]
        ):
            return None, [f"content manifest file {index} sha256 is invalid"]
        if not isinstance(item["bytes"], int) or isinstance(item["bytes"], bool) or item["bytes"] < 0:
            return None, [f"content manifest file {index} byte count is invalid"]
        paths.append(path)
    if paths != sorted(paths) or len(paths) != len(set(paths)):
        return None, ["content manifest paths are not sorted and unique"]
    return files, []


def make_attestation(root: Path | str, content_commit: str, manifest_path: str) -> dict[str, Any]:
    """Create a deterministic attestation from a committed content manifest."""

    root_path = Path(root).resolve()
    manifest_binding = git_binding(root_path, content_commit, manifest_path)
    content, errors = _binding_errors(
        root_path, manifest_binding, commit=content_commit, label="content manifest"
    )
    if errors or content is None:
        raise ValueError("invalid committed content manifest: " + "; ".join(errors))
    try:
        document = json.loads(content)
    except json.JSONDecodeError as error:
        raise ValueError("content manifest is not JSON") from error
    files, errors = _manifest_files(document, manifest_path)
    if errors or files is None:
        raise ValueError("invalid content manifest: " + "; ".join(errors))
    artifacts = [git_binding(root_path, content_commit, item["path"]) for item in files]
    for item, binding in zip(files, artifacts, strict=True):
        if item["sha256"] != binding["sha256"] or item["bytes"] != binding["bytes"]:
            raise ValueError(f"content manifest does not match committed content: {item['path']}")
    return {
        "schema_version": 1,
        "artifact_type": _ATTESTATION_TYPE,
        "historical_commit": content_commit,
        "manifest": manifest_binding,
        "artifacts": artifacts,
    }


def _read_manifest(root: Path, attestation: dict[str, Any], expected_manifest_path: str) -> tuple[list[dict[str, Any]] | None, list[str]]:
    commit = attestation["historical_commit"]
    binding = attestation["manifest"]
    if not isinstance(binding, dict) or binding.get("path") != expected_manifest_path:
        return None, ["attestation manifest path differs from expected manifest path"]
    content, errors = _binding_errors(root, binding, commit=commit, label="content manifest")
    if errors or content is None:
        return None, errors
    try:
        document = json.loads(content)
    except json.JSONDecodeError:
        return None, ["content manifest is not JSON"]
    return _manifest_files(document, expected_manifest_path)


def _safe_extract(archive: tarfile.TarFile, destination: Path) -> None:
    """Extract regular committed files only, without accepting archive links."""

    for member in archive.getmembers():
        if not _safe_path(member.name):
            raise ValueError("git archive contains an unsafe path")
        target = destination.joinpath(*PurePosixPath(member.name).parts)
        if member.isdir():
            target.mkdir(parents=True, exist_ok=True)
            continue
        if not member.isreg():
            raise ValueError("git archive contains a non-regular file")
        target.parent.mkdir(parents=True, exist_ok=True)
        source = archive.extractfile(member)
        if source is None:
            raise ValueError("git archive file content is unavailable")
        with source, target.open("xb") as output:
            output.write(source.read())
        target.chmod(0o555 if member.mode & 0o111 else 0o444)


def _archive_snapshot(root: Path, commit: str, destination: Path) -> list[str]:
    archive, error = _git(root, "archive", "--format=tar", commit)
    if error is not None or archive is None:
        return ["historical snapshot archive is unavailable"]
    try:
        import io

        with tarfile.open(fileobj=io.BytesIO(archive), mode="r:") as tar:
            _safe_extract(tar, destination)
    except (tarfile.TarError, OSError, ValueError) as error:
        return [f"historical snapshot extraction failed: {error}"]
    tree, error = _git(root, "ls-tree", "-r", "-z", "--full-tree", commit)
    if error is not None or tree is None:
        return ["historical snapshot tree is unavailable"]
    expected: dict[str, str] = {}
    for entry in tree.split(b"\0"):
        if not entry:
            continue
        try:
            metadata, encoded_path = entry.split(b"\t", 1)
            mode, object_type, object_id = metadata.decode("ascii").split(" ")
            path = encoded_path.decode("utf-8")
        except (UnicodeDecodeError, ValueError):
            return ["historical snapshot tree entry is malformed"]
        if mode not in {"100644", "100755"} or object_type != "blob" or not _safe_path(path):
            return ["historical snapshot tree contains an unsupported path"]
        expected[path] = object_id
    extracted = {
        str(path.relative_to(destination).as_posix())
        for path in destination.rglob("*")
        if path.is_file()
    }
    if extracted != set(expected):
        return ["historical snapshot does not contain exactly the committed tracked files"]
    for path, object_id in expected.items():
        content = destination.joinpath(*PurePosixPath(path).parts).read_bytes()
        # A local Git-blob digest avoids one subprocess per archived file while
        # still detecting export-subst/export-ignore changes to committed bytes.
        blob_id = hashlib.sha1(f'blob {len(content)}\0'.encode() + content).hexdigest()
        if blob_id != object_id:
            return [f"historical snapshot content differs from committed blob: {path}"]
    for directory, _, filenames in os.walk(destination):
        Path(directory).chmod(stat.S_IRUSR | stat.S_IXUSR | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)
        for filename in filenames:
            file = Path(directory, filename)
            file.chmod(0o555 if file.stat().st_mode & 0o111 else 0o444)
    return []


def validate_historical(
    root: Path | str,
    attestation: Any,
    expected_manifest_path: str,
    validator_path: str,
    validate_args: list[str],
) -> list[str]:
    """Validate an attested study snapshot with its historically bound validator."""

    root_path = Path(root).resolve()
    if not _safe_path(expected_manifest_path) or not _safe_path(validator_path):
        return ["expected manifest or validator path is not safe"]
    if not isinstance(validate_args, list) or not all(isinstance(arg, str) for arg in validate_args):
        return ["validator arguments must be a list of strings"]
    if not isinstance(attestation, dict) or set(attestation) != {
        "schema_version", "artifact_type", "historical_commit", "manifest", "artifacts"
    }:
        return ["historical attestation fields are not exact"]
    if attestation["schema_version"] != 1 or attestation["artifact_type"] != _ATTESTATION_TYPE:
        return ["historical attestation identity is invalid"]
    commit, error = _exact_commit(root_path, attestation["historical_commit"])
    if error is not None or commit is None:
        return [f"historical attestation {error}"]
    files, errors = _read_manifest(root_path, attestation, expected_manifest_path)
    if errors or files is None:
        return errors
    artifacts = attestation["artifacts"]
    if not isinstance(artifacts, list):
        return ["historical attestation artifacts is not a list"]
    expected = {item["path"]: item for item in files}
    actual_paths: list[str] = []
    for index, binding in enumerate(artifacts):
        content, binding_errors = _binding_errors(
            root_path, binding, commit=commit, label=f"historical artifact {index}"
        )
        errors.extend(binding_errors)
        if not isinstance(binding, dict):
            continue
        path = binding.get("path")
        if isinstance(path, str):
            actual_paths.append(path)
            manifest_item = expected.get(path)
            if manifest_item is None:
                errors.append(f"historical artifact {index}: path is absent from content manifest")
            elif binding.get("sha256") != manifest_item["sha256"] or binding.get("bytes") != manifest_item["bytes"]:
                errors.append(f"historical artifact {index}: content differs from content manifest")
        if content is None:
            continue
    if len(actual_paths) != len(set(actual_paths)):
        errors.append("historical attestation artifacts contain duplicate paths")
    if set(actual_paths) != set(expected):
        errors.append("historical attestation artifacts do not exactly match content manifest")
    if validator_path not in expected:
        errors.append("historical validator is not bound by the content manifest")
    if errors:
        return errors

    with tempfile.TemporaryDirectory(prefix="publication-study-history-") as temporary:
        snapshot = Path(temporary, "snapshot")
        snapshot.mkdir()
        errors = _archive_snapshot(root_path, commit, snapshot)
        if errors:
            return errors
        validator = snapshot.joinpath(*PurePosixPath(validator_path).parts)
        if not validator.is_file():
            return ["historical validator is absent from the extracted snapshot"]
        git_dir, error = _git(root_path, "rev-parse", "--absolute-git-dir")
        if error is not None or git_dir is None:
            return ["historical Git directory is unavailable"]
        environment = os.environ.copy()
        environment.update({
            "GIT_DIR": git_dir.decode("utf-8").strip(),
            "GIT_WORK_TREE": str(snapshot),
            "GIT_OPTIONAL_LOCKS": "0",
            "PYTHONDONTWRITEBYTECODE": "1",
        })
        command = [str(validator), *validate_args]
        if validator.suffix == ".py":
            command.insert(0, sys.executable)
        result = subprocess.run(
            command,
            cwd=snapshot,
            env=environment,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if result.returncode:
            message = result.stderr.decode("utf-8", errors="replace").strip()
            return [f"historical validator failed with exit {result.returncode}" + (f": {message}" if message else "")]
    return []
