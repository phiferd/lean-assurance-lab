"""Prepared baseline/mutant Kiota binaries for held-out transfer evaluation."""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
KIOTA_ROOT = ROOT / "external" / "lean-kernel-arena" / "_build" / "checkers" / "kiota" / "src"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_revision() -> str:
    return subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=KIOTA_ROOT, check=True, text=True,
        stdout=subprocess.PIPE,
    ).stdout.strip()


def classify_transfer(candidate: dict[str, Any], control: dict[str, Any], expected: str) -> tuple[str, str]:
    cb = candidate["baseline"]["normalized_outcome"]
    cm = candidate["mutant"]["normalized_outcome"]
    pb = control["baseline"]["normalized_outcome"]
    pm = control["mutant"]["normalized_outcome"]
    exceptional = {"DECLINE", "CRASH", "TIMEOUT", "UNKNOWN"}
    if {cb, cm, pb, pm} & exceptional:
        return "INCONCLUSIVE", "CHECKER_DID_NOT_PRODUCE_COMPARABLE_SEMANTIC_OUTCOMES"
    if pb != "ACCEPT":
        return "INCOMPATIBLE", "HELD_OUT_BASELINE_REJECTS_POSITIVE_CONTROL"
    if pm != "ACCEPT":
        return "NEGATIVE_TRANSFER", "HELD_OUT_MUTANT_REGRESSES_POSITIVE_CONTROL"
    if cb != expected:
        return "NEGATIVE_TRANSFER", "HELD_OUT_BASELINE_DIFFERS_FROM_REFERENCE_EXPECTATION"
    if candidate["different"] and cb == "REJECT" and cm == "ACCEPT":
        return "POSITIVE_TRANSFER", "FROZEN_CORPUS_KILLS_ANALOGOUS_HELD_OUT_MUTANT"
    if not candidate["different"]:
        return "NEUTRAL_TRANSFER", "FROZEN_CORPUS_DOES_NOT_DISTINGUISH_HELD_OUT_MUTANT"
    return "UNRESOLVED", "DISTINCTION_DIRECTION_DOES_NOT_MATCH_MODELED_FAULT"


class KiotaDifferentialSession:
    def __init__(self, spec_path: Path, timeout: float = 60.0) -> None:
        self.spec_path = spec_path
        self.spec = json.loads(spec_path.read_text(encoding="utf-8"))
        self.mutation = self.spec["mutation"]
        self.source_path = KIOTA_ROOT / self.mutation["source_file"]
        self.timeout = timeout
        self._temp: tempfile.TemporaryDirectory[str] | None = None
        self.baseline_binary: Path | None = None
        self.mutant_binary: Path | None = None
        self.preparation: dict[str, Any] = {}
        self.checker_runs = 0
        self.checker_seconds = 0.0

    def set_state(self, state: str) -> str:
        original = self.mutation["original"]
        mutated = self.mutation["mutated"]
        text = self.source_path.read_text(encoding="utf-8")
        if state == "baseline":
            if mutated in text:
                self.source_path.write_text(text.replace(mutated, original, 1), encoding="utf-8")
                return "changed"
            if original in text:
                return "already"
        elif state == "mutant":
            if mutated in text:
                return "already"
            if original in text:
                self.source_path.write_text(text.replace(original, mutated, 1), encoding="utf-8")
                return "changed"
        else:
            raise ValueError(f"unknown state: {state}")
        raise RuntimeError(f"{self.source_path}: neither expected source state found")

    def build(self) -> dict[str, Any]:
        started = time.monotonic()
        proc = subprocess.run(
            ["cargo", "build", "--release"], cwd=KIOTA_ROOT, text=True,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        )
        result = {
            "returncode": proc.returncode,
            "seconds": time.monotonic() - started,
            "output_tail": proc.stdout[-4000:] if proc.returncode else "",
        }
        if proc.returncode:
            raise RuntimeError(f"Kiota build failed: {result}")
        return result

    def prepare(self) -> None:
        if self._temp is not None:
            return
        expected = self.spec["held_out_source"]
        if git_revision() != expected["expected_revision"]:
            raise RuntimeError("Kiota revision differs from frozen experiment spec")
        self._temp = tempfile.TemporaryDirectory(prefix="leanverifier-m6-kiota-")
        temp_root = Path(self._temp.name)
        active = False
        try:
            self.preparation["restore_before"] = self.set_state("baseline")
            baseline_sha = sha256_file(self.source_path)
            if baseline_sha != expected["baseline_source_sha256"]:
                raise RuntimeError("Kiota baseline source hash differs from experiment spec")
            self.preparation["baseline_build"] = self.build()
            self.baseline_binary = temp_root / "kiota-baseline"
            shutil.copy2(KIOTA_ROOT / "target" / "release" / "kiota", self.baseline_binary)
            self.preparation["apply_mutant"] = self.set_state("mutant")
            active = True
            self.preparation["mutated_source_sha256"] = sha256_file(self.source_path)
            self.preparation["mutant_build"] = self.build()
            self.mutant_binary = temp_root / "kiota-mutant"
            shutil.copy2(KIOTA_ROOT / "target" / "release" / "kiota", self.mutant_binary)
        finally:
            if active:
                self.preparation["restore_after"] = self.set_state("baseline")
            self.preparation["restored_build"] = self.build()
            self.preparation["restored_source_sha256"] = sha256_file(self.source_path)
            self.preparation["source_restored"] = (
                self.preparation["restored_source_sha256"] == expected["baseline_source_sha256"]
            )
        if not self.preparation["source_restored"]:
            raise RuntimeError("Kiota source was not restored after held-out evaluation")

    def run_one(self, binary: Path, artifact: Path) -> dict[str, Any]:
        started = time.monotonic()
        try:
            proc = subprocess.run(
                [str(binary), str(artifact.resolve())], cwd=KIOTA_ROOT,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=self.timeout,
            )
            if proc.returncode == 0:
                outcome = "ACCEPT"
            elif proc.returncode == 1:
                outcome = "REJECT"
            elif proc.returncode == 2:
                outcome = "DECLINE"
            elif proc.returncode < 0:
                outcome = "CRASH"
            else:
                outcome = "UNKNOWN"
            result = {
                "normalized_outcome": outcome,
                "exit_code": proc.returncode,
                "signal": -proc.returncode if proc.returncode < 0 else None,
                "stdout_sha256": hashlib.sha256(proc.stdout).hexdigest(),
                "stderr_sha256": hashlib.sha256(proc.stderr).hexdigest(),
                "stdout_tail": proc.stdout.decode(errors="replace")[-2000:],
                "stderr_tail": proc.stderr.decode(errors="replace")[-2000:],
            }
        except subprocess.TimeoutExpired:
            result = {
                "normalized_outcome": "TIMEOUT", "exit_code": None, "signal": None,
                "stdout_sha256": None, "stderr_sha256": None,
                "stdout_tail": "", "stderr_tail": "",
            }
        result["seconds"] = time.monotonic() - started
        self.checker_runs += 1
        self.checker_seconds += result["seconds"]
        return result

    def evaluate(self, artifact: Path) -> dict[str, Any]:
        self.prepare()
        assert self.baseline_binary is not None and self.mutant_binary is not None
        baseline = self.run_one(self.baseline_binary, artifact)
        mutant = self.run_one(self.mutant_binary, artifact)
        return {
            "artifact_sha256": sha256_file(artifact),
            "baseline": baseline,
            "mutant": mutant,
            "different": baseline["normalized_outcome"] != mutant["normalized_outcome"],
        }

    def close(self) -> None:
        if self._temp is not None:
            self._temp.cleanup()
            self._temp = None

    def __enter__(self) -> "KiotaDifferentialSession":
        self.prepare()
        return self

    def __exit__(self, *_: object) -> None:
        self.close()
