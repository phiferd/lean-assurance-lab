#!/usr/bin/env python3
"""Small, durable execution ledger for the frozen publication-study protocol.

This module deliberately does not construct candidates or interpret checker
output.  The caller supplies a frozen candidate manifest and an attribution
function.  It is safe to import from a future Gate-10 constructor/validator.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import re
import subprocess
import time
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

OUTCOMES = frozenset({"ACCEPT", "REJECT", "DECLINE", "CRASH", "TIMEOUT", "PARSE_ERROR", "UNKNOWN"})
_SAFE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


class LedgerError(RuntimeError): pass
class ManifestError(LedgerError): pass
class TamperError(LedgerError): pass
class InterruptedReservation(LedgerError): pass
class ActiveSession(LedgerError): pass


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_bytes(value: Mapping[str, Any]) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode()


def digest(value: Mapping[str, Any]) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def _name(value: str) -> str:
    if not isinstance(value, str) or not _SAFE.fullmatch(value):
        raise ManifestError(f"unsafe ledger identifier: {value!r}")
    return value


def _atomic_json(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    except FileExistsError:
        raise
    with os.fdopen(fd, "wb") as handle:
        handle.write(canonical_bytes(value))
        handle.flush()
        os.fsync(handle.fileno())


def _read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise TamperError(f"invalid immutable ledger record {path}: {exc}") from exc


def verify_dependencies(manifest: Mapping[str, Any], root: Path) -> str:
    """Verify every path/hash dependency in an immutable manifest."""
    deps = manifest.get("dependencies")
    if not isinstance(deps, list) or not deps:
        raise ManifestError("manifest requires a non-empty dependencies list")
    seen: set[str] = set()
    for item in deps:
        if not isinstance(item, Mapping) or not {"path", "sha256"} <= set(item):
            raise ManifestError("each dependency requires path and sha256")
        rel, expected = item["path"], item["sha256"]
        if not isinstance(rel, str) or not isinstance(expected, str) or not re.fullmatch(r"[0-9a-f]{64}", expected):
            raise ManifestError("invalid dependency binding")
        if rel in seen or Path(rel).is_absolute() or ".." in Path(rel).parts:
            raise ManifestError(f"unsafe or duplicate dependency path: {rel!r}")
        seen.add(rel)
        path = root / rel
        if not path.is_file() or sha256_file(path) != expected:
            raise TamperError(f"dependency hash mismatch: {rel}")
    return digest(dict(manifest))


@dataclass(frozen=True)
class Observer:
    observer_id: str
    configuration_sha256: str
    command: tuple[str, ...]
    stdin: bool = False


@dataclass(frozen=True)
class Capture:
    returncode: int | None
    stdout: bytes
    stderr: bytes
    elapsed_seconds: float
    timed_out: bool = False


@dataclass
class Session:
    ledger: "ExecutionLedger"
    run_manifest_sha256: str
    token: str
    started_monotonic: float
    clock: Callable[[], float]
    downtime_seconds: float = 0.0
    candidate_ids: set[str] = None  # populated only by this live owner

    def __post_init__(self) -> None:
        if self.candidate_ids is None: self.candidate_ids = set()

    def active_seconds(self) -> float:
        return max(0.0, self.clock() - self.started_monotonic - self.downtime_seconds)

    def remaining_seconds(self) -> float:
        return 600.0 - self.active_seconds()

    def record_downtime(self, seconds: float) -> None:
        # This implementation keeps a single active session. Unknown interrupted
        # intervals cannot be excluded from budget by a caller-supplied number.
        if seconds != 0: raise LedgerError("interrupted downtime is unbounded; close unresolved")


class ExecutionLedger:
    """O_EXCL-backed immutable records for exactly one active protocol session."""
    def __init__(self, directory: Path):
        self.directory = directory

    @property
    def lock_path(self) -> Path: return self.directory / "active-session.json"

    def begin(self, run_manifest: Mapping[str, Any], root: Path, *, clock: Callable[[], float] = time.monotonic) -> Session:
        run_hash = verify_dependencies(run_manifest, root)
        manifest_path = self.directory / "run-manifest.json"
        try: _atomic_json(manifest_path, {"kind": "RUN_MANIFEST", "run_manifest": dict(run_manifest), "run_manifest_sha256": run_hash})
        except FileExistsError:
            persisted = _read_json(manifest_path)
            if persisted.get("run_manifest_sha256") != run_hash or persisted.get("run_manifest") != dict(run_manifest):
                raise TamperError("persisted run manifest differs")
        token = uuid.uuid4().hex
        record = {"kind": "RUN_SESSION", "run_manifest_sha256": run_hash, "owner_token": token}
        try:
            _atomic_json(self.lock_path, record)
        except FileExistsError:
            if (self.directory / "session-completion.json").exists():
                raise ActiveSession("session is complete; its immutable results are read-only")
            raise InterruptedReservation("prior active session has unknown elapsed time and is unresolved")
        return Session(self, run_hash, token, clock(), clock)

    def _assert_owner(self, session: Session) -> None:
        if (self.directory / 'session-completion.json').exists():
            raise ActiveSession('completed session is read-only')
        if session.ledger is not self or _read_json(self.lock_path) != {"kind": "RUN_SESSION", "run_manifest_sha256": session.run_manifest_sha256, "owner_token": session.token}:
            raise ActiveSession("operation lacks the exclusive live session token")

    def finish(self, session: Session, *, terminal_state: str, result_binding: Mapping[str, Any] | None = None) -> dict[str, Any]:
        self._assert_owner(session)
        active = session.active_seconds()
        record = {"kind": "SESSION_FINISH", "run_manifest_sha256": session.run_manifest_sha256, "terminal_state": terminal_state, "active_seconds": active, "downtime_seconds": session.downtime_seconds, "budget_exhausted": active > 600.0,
                  "result_binding": dict(result_binding) if result_binding else None,
                  "candidate_reservations": len(list((self.directory / 'candidates').glob('*.reservation.json'))),
                  "checker_reservations": len(list((self.directory / 'reservations').glob('*.json')))}
        try: _atomic_json(self.directory / "session-completion.json", record)
        except FileExistsError: raise TamperError("session finish already exists")
        return record

    def reserve_candidate(self, session: Session, candidate_id: str) -> Path:
        self._assert_owner(session)
        candidate_id = _name(candidate_id)
        if session.candidate_ids:
            raise InterruptedReservation('the single candidate budget is consumed')
        path = self.directory / "candidates" / f"{candidate_id}.reservation.json"
        record = {"kind": "CANDIDATE_RESERVATION", "run_manifest_sha256": session.run_manifest_sha256, "candidate_id": candidate_id}
        try:
            _atomic_json(path, record)
        except FileExistsError:
            raise InterruptedReservation(f"candidate reservation is already consumed: {candidate_id}")
        session.candidate_ids.add(candidate_id)
        return path

    def freeze_candidate(self, session: Session, candidate_manifest: Mapping[str, Any], root: Path) -> str:
        self._assert_owner(session)
        candidate_id = _name(str(candidate_manifest.get("candidate_id", "")))
        if candidate_id not in session.candidate_ids:
            raise InterruptedReservation("candidate was not reserved by this live session")
        candidate_hash = verify_dependencies(candidate_manifest, root)
        for key in ("negative", "control"):
            item = candidate_manifest.get(key)
            if not isinstance(item, Mapping) or not isinstance(item.get("path"), str) or not re.fullmatch(r"[0-9a-f]{64}", str(item.get("sha256", ""))):
                raise ManifestError(f"candidate manifest needs {key}.path and {key}.sha256")
            path = root / item["path"]
            if Path(item["path"]).is_absolute() or ".." in Path(item["path"]).parts or not path.is_file() or sha256_file(path) != item["sha256"]:
                raise TamperError(f"candidate {key} bytes differ from freeze")
        record = {"kind": "CANDIDATE_FREEZE", "run_manifest_sha256": session.run_manifest_sha256, "candidate_manifest": dict(candidate_manifest), "candidate_manifest_sha256": candidate_hash}
        path = self.directory / "candidates" / f"{candidate_id}.freeze.json"
        try: _atomic_json(path, record)
        except FileExistsError:
            if _read_json(path) != record: raise TamperError("candidate freeze differs from prior immutable freeze")
        return candidate_hash

    def _result_path(self, candidate_id: str, sequence: int, observer_id: str, artifact_id: str) -> Path:
        return self.directory / "results" / f"{candidate_id}.{sequence:02d}.{observer_id}.{artifact_id}.json"

    def _reserve_launch(self, record: Mapping[str, Any]) -> tuple[Path, bool]:
        candidate, observer, artifact = (_name(str(record[k])) for k in ("candidate_id", "observer_id", "artifact_id"))
        sequence = int(record["sequence"])
        path = self.directory / "reservations" / f"{candidate}.{sequence:02d}.{observer}.{artifact}.json"
        try:
            _atomic_json(path, record)
            return path, True
        except FileExistsError:
            if _read_json(path) != dict(record): raise TamperError(f"launch reservation differs: {path.name}")
        return path, False

    def reserve_launch(self, record: Mapping[str, Any]) -> Path:
        """Reserve a checker launch; a prior incomplete reservation is terminal."""
        path, created = self._reserve_launch(record)
        if not created:
            raise InterruptedReservation(f"pending reservation is consumed: {path.name}")
        return path


def _default_runner(observer: Observer, artifact: Path, timeout: float) -> Capture:
    command = [str(artifact) if part == "{artifact}" else part for part in observer.command]
    if "{artifact}" not in observer.command and not observer.stdin: command.append(str(artifact))
    started = time.monotonic()
    try:
        with artifact.open("rb") if observer.stdin else open(os.devnull, "rb") as handle:
            proc = subprocess.run(command, stdin=handle if observer.stdin else None, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout, check=False)
        return Capture(proc.returncode, proc.stdout, proc.stderr, time.monotonic() - started)
    except subprocess.TimeoutExpired as exc:
        return Capture(None, exc.stdout or b"", exc.stderr or b"", time.monotonic() - started, True)


def _verify_prior_result(path: Path, reservation: Mapping[str, Any]) -> dict[str, Any]:
    prior = _read_json(path)
    for key, value in reservation.items():
        if key == "kind":
            continue
        if prior.get(key) != value:
            raise TamperError(f"prior result binding differs for {key}: {path.name}")
    capture = prior.get("capture")
    if not isinstance(capture, Mapping) or not isinstance(prior.get("normalized_outcome"), str):
        raise TamperError(f"prior result is structurally incomplete: {path.name}")
    for key in ("stdout_sha256", "stderr_sha256"):
        value = capture.get(key)
        raw = path.parents[1] / "raw" / str(value)
        if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value) or not raw.is_file() or sha256_file(raw) != value:
            raise TamperError(f"prior raw output differs: {path.name}")
    if prior["normalized_outcome"] not in OUTCOMES:
        raise TamperError(f"prior result has non-frozen outcome: {path.name}")
    return prior


def execute_protocol(session: Session, run_manifest: Mapping[str, Any], candidate_manifest: Mapping[str, Any], observers: Sequence[Observer], *, root: Path, process_runner: Callable[[Observer, Path, float], Capture] = _default_runner, attribute: Callable[[Observer, str, Capture], str], utc_now: Callable[[], str] = lambda: datetime.now(timezone.utc).isoformat()) -> dict[str, Any]:
    """Execute only the fixed control/negative observer matrix, without retries."""
    ledger = session.ledger
    ledger._assert_owner(session)
    run_hash = verify_dependencies(run_manifest, root)
    if run_hash != session.run_manifest_sha256: raise TamperError("live session differs from run manifest")
    candidate_hash = digest(dict(candidate_manifest))
    candidate_id = _name(str(candidate_manifest["candidate_id"]))
    frozen = _read_json(ledger.directory / "candidates" / f"{candidate_id}.freeze.json")
    if frozen.get("candidate_manifest_sha256") != candidate_hash or frozen.get("run_manifest_sha256") != run_hash:
        raise InterruptedReservation("candidate is not frozen by this session")
    expected = run_manifest.get("observer_ids")
    if expected != [o.observer_id for o in observers] or len(observers) != 4:
        raise ManifestError("observers must be the exact frozen ordered four-observer list")
    protocol = run_manifest.get("budget", {})
    max_runs, max_wall, max_timeout = protocol.get("checker_executions"), protocol.get("wall_seconds"), protocol.get("checker_timeout_seconds")
    if (max_runs, max_wall, max_timeout) != (8, 600, 30): raise ManifestError("only the frozen 8/600/30 budget is supported")
    completed: list[dict[str, Any]] = []
    for sequence, (observer, artifact_id) in enumerate((pair for o in observers for pair in ((o, "control"), (o, "negative"))), start=1):
        artifact = root / candidate_manifest[artifact_id]["path"]
        result_path = ledger._result_path(candidate_id, sequence, observer.observer_id, artifact_id)
        verify_dependencies(run_manifest, root)
        verify_dependencies(candidate_manifest, root)
        if sha256_file(artifact) != candidate_manifest[artifact_id]['sha256']:
            raise TamperError('artifact differs from pre-feedback freeze')
        reservation = {"kind": "CHECKER_RESERVATION", "run_manifest_sha256": run_hash, "candidate_manifest_sha256": candidate_hash, "candidate_id": candidate_id, "sequence": sequence, "observer_id": observer.observer_id, "observer_configuration_sha256": observer.configuration_sha256, "artifact_id": artifact_id, "artifact_sha256": candidate_manifest[artifact_id]['sha256']}
        if result_path.exists():
            completed.append(_verify_prior_result(result_path, reservation)); continue
        pending = ledger.directory / 'reservations' / f'{candidate_id}.{sequence:02d}.{observer.observer_id}.{artifact_id}.json'
        if pending.exists():
            raise InterruptedReservation(f'pending launch is consumed: {pending.name}')
        remaining = session.remaining_seconds()
        if remaining <= 0:
            return {"terminal_state": "BOUNDED_FAILURE_ATTEMPT_OR_TIME_BUDGET_EXHAUSTED", "completed": completed, "active_seconds": session.active_seconds(), "downtime_seconds": session.downtime_seconds}
        timeout = min(float(max_timeout), remaining)
        recorded_command = [str(Path(x).relative_to(root)) if Path(x).is_absolute() and Path(x).is_relative_to(root) else x for x in observer.command]
        reservation.update(command=recorded_command, stdin=observer.stdin, timeout_seconds=timeout,
                           started_at_utc=utc_now(), active_seconds_before_launch=session.active_seconds())
        reservation_path, created = ledger._reserve_launch(reservation)
        # A pre-existing reservation without its immutable result has unknown active
        # elapsed time.  Its budget is consumed and it cannot safely be retried.
        if not created:
            raise InterruptedReservation(f"pending reservation is consumed: {reservation_path.name}")
        # Recheck every run dependency (including frozen observer binaries and
        # profiles) and the exact artifact immediately before process launch.
        if sha256_file(artifact) != reservation["artifact_sha256"]:
            raise TamperError("artifact bytes changed after reservation")
        remaining = session.remaining_seconds()
        if remaining <= 0:
            return {"terminal_state": "BOUNDED_FAILURE_ATTEMPT_OR_TIME_BUDGET_EXHAUSTED", "completed": completed, "active_seconds": session.active_seconds(), "downtime_seconds": session.downtime_seconds}
        started = session.clock()
        capture = process_runner(observer, artifact, timeout)
        elapsed = float(capture.elapsed_seconds)
        if not math.isfinite(elapsed) or elapsed < 0:
            raise InterruptedReservation('invalid elapsed interval; reservation consumed')
        outcome = attribute(observer, artifact_id, capture)
        if outcome not in OUTCOMES: raise ManifestError(f"attribution returned non-frozen outcome: {outcome!r}")
        raw_dir = ledger.directory / "raw"
        stdout_hash, stderr_hash = hashlib.sha256(capture.stdout).hexdigest(), hashlib.sha256(capture.stderr).hexdigest()
        for blob, blob_hash in ((capture.stdout, stdout_hash), (capture.stderr, stderr_hash)):
            raw_path = raw_dir / blob_hash
            raw_path.parent.mkdir(parents=True, exist_ok=True)
            try:
                fd = os.open(raw_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
                with os.fdopen(fd, "wb") as handle: handle.write(blob); handle.flush(); os.fsync(handle.fileno())
            except FileExistsError:
                if sha256_file(raw_path) != blob_hash: raise TamperError("raw output blob hash mismatch")
        result = {**reservation, "kind": "CHECKER_RESULT", "capture": {"returncode": capture.returncode, "timed_out": capture.timed_out, "elapsed_seconds": elapsed, "wall_observed_seconds": max(0.0, session.clock() - started), "stdout_sha256": stdout_hash, "stderr_sha256": stderr_hash}, "normalized_outcome": outcome, "downtime_seconds": session.downtime_seconds}
        try: _atomic_json(result_path, result)
        except FileExistsError: raise InterruptedReservation("concurrent result creation; inspect immutable ledger")
        completed.append(result)
    return {"terminal_state": "COMPLETE", "completed": completed, "active_seconds": session.active_seconds(), "downtime_seconds": session.downtime_seconds}
