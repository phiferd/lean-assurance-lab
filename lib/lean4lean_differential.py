"""Prepared baseline/mutant Lean4Lean binaries for held-out evaluation."""

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
LEAN4LEAN_ROOT = ROOT / "external" / "lean-kernel-arena" / "_build" / "checkers" / "lean4lean" / "src"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def classify_fold(original_killed: int, augmented_killed: int, candidate: dict[str, Any],
                  control: dict[str, Any], expected: str) -> tuple[str, str]:
    outcomes = {
        candidate["baseline"]["normalized_outcome"], candidate["mutant"]["normalized_outcome"],
        control["baseline"]["normalized_outcome"], control["mutant"]["normalized_outcome"],
    }
    if outcomes & {"CRASH", "TIMEOUT", "UNKNOWN"}:
        return "INCONCLUSIVE", "NON_COMPARABLE_HELD_OUT_OUTCOME"
    if control["baseline"]["normalized_outcome"] != "ACCEPT":
        return "INCOMPATIBLE", "HELD_OUT_BASELINE_REJECTS_POSITIVE_CONTROL"
    if control["mutant"]["normalized_outcome"] != "ACCEPT":
        return "NEGATIVE", "HELD_OUT_MUTANT_REGRESSES_POSITIVE_CONTROL"
    if candidate["baseline"]["normalized_outcome"] != expected:
        return "NEGATIVE", "HELD_OUT_BASELINE_DIFFERS_FROM_REFERENCE_EXPECTATION"
    if candidate["different"] and not (
        candidate["baseline"]["normalized_outcome"] == "REJECT"
        and candidate["mutant"]["normalized_outcome"] == "ACCEPT"
    ):
        return "UNRESOLVED", "DISTINCTION_DIRECTION_DOES_NOT_MATCH_MODELED_FAULT"
    if augmented_killed < original_killed:
        return "NEGATIVE", "AUGMENTED_SCORE_REGRESSED"
    if augmented_killed > original_killed:
        return "POSITIVE", "AUGMENTED_CORPUS_KILLS_ADDITIONAL_HELD_OUT_MUTANT"
    if augmented_killed == original_killed:
        return "NEUTRAL", "AUGMENTED_CORPUS_DOES_NOT_CHANGE_HELD_OUT_SCORE"
    return "UNRESOLVED", "FOLD_DIRECTION_DOES_NOT_MATCH_MODELED_SCORE"


class Lean4LeanDifferentialSession:
    def __init__(self, spec_path: Path, timeout: float = 120.0) -> None:
        self.spec_path = spec_path
        self.spec = json.loads(spec_path.read_text(encoding="utf-8"))
        self.mutation = self.spec["held_out_mutation"]
        self.source_path = LEAN4LEAN_ROOT / self.mutation["source_file"]
        self.timeout = timeout
        self._temp: tempfile.TemporaryDirectory[str] | None = None
        self.baseline_binary: Path | None = None
        self.mutant_binary: Path | None = None
        self.preparation: dict[str, Any] = {}
        self.checker_runs = 0
        self.checker_seconds = 0.0

    def git_output(self, *args: str) -> str:
        return subprocess.run(
            ["git", *args], cwd=LEAN4LEAN_ROOT, check=True, text=True,
            stdout=subprocess.PIPE,
        ).stdout.strip()

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
            ["lake", "build", "lean4lean"], cwd=LEAN4LEAN_ROOT, text=True,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        )
        result = {
            "returncode": proc.returncode,
            "seconds": time.monotonic() - started,
            "output_tail": proc.stdout[-4000:] if proc.returncode else "",
        }
        if proc.returncode:
            raise RuntimeError(f"Lean4Lean build failed: {result}")
        return result

    def prepare(self) -> None:
        if self._temp is not None:
            return
        expected = self.spec["held_out_source"]
        if self.git_output("rev-parse", "HEAD") != expected["expected_revision"]:
            raise RuntimeError("Lean4Lean revision differs from experiment spec")
        self._temp = tempfile.TemporaryDirectory(prefix="lean-assurance-lab-m7-lean4lean-")
        temp_root = Path(self._temp.name)
        active = False
        try:
            self.preparation["restore_before"] = self.set_state("baseline")
            if sha256_file(self.source_path) != expected["baseline_source_sha256"]:
                raise RuntimeError("Lean4Lean baseline source hash differs from experiment spec")
            self.preparation["baseline_build"] = self.build()
            self.baseline_binary = temp_root / "lean4lean-baseline"
            shutil.copy2(LEAN4LEAN_ROOT / ".lake" / "build" / "bin" / "lean4lean", self.baseline_binary)
            self.preparation["apply_mutant"] = self.set_state("mutant")
            active = True
            self.preparation["mutated_source_sha256"] = sha256_file(self.source_path)
            self.preparation["mutant_build"] = self.build()
            self.mutant_binary = temp_root / "lean4lean-mutant"
            shutil.copy2(LEAN4LEAN_ROOT / ".lake" / "build" / "bin" / "lean4lean", self.mutant_binary)
        finally:
            if active:
                self.preparation["restore_after"] = self.set_state("baseline")
            self.preparation["restored_build"] = self.build()
            self.preparation["restored_source_sha256"] = sha256_file(self.source_path)
            self.preparation["source_restored"] = (
                self.preparation["restored_source_sha256"] == expected["baseline_source_sha256"]
                and not self.git_output("status", "--porcelain")
            )
        if not self.preparation["source_restored"]:
            raise RuntimeError("Lean4Lean source was not restored exactly")

    def run_one(self, binary: Path, artifact: Path) -> dict[str, Any]:
        started = time.monotonic()
        try:
            proc = subprocess.run(
                [str(binary), "--import", str(artifact.resolve())], cwd=LEAN4LEAN_ROOT,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=self.timeout,
            )
            if proc.returncode == 0:
                outcome = "ACCEPT"
            elif proc.returncode == 1:
                outcome = "REJECT"
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
                "stdout_tail": proc.stdout.decode(errors="replace")[-1000:],
                "stderr_tail": proc.stderr.decode(errors="replace")[-1000:],
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
            "artifact_bytes": artifact.stat().st_size,
            "baseline": baseline,
            "mutant": mutant,
            "different": baseline["normalized_outcome"] != mutant["normalized_outcome"],
        }

    def close(self) -> None:
        if self._temp is not None:
            self._temp.cleanup()
            self._temp = None

    def __enter__(self) -> "Lean4LeanDifferentialSession":
        self.prepare()
        return self

    def __exit__(self, *_: object) -> None:
        self.close()
