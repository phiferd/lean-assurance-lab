"""Prepared baseline/mutant nanoda binaries and normalized differential runs."""

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
CHECKER_ROOT = ROOT / "external" / "lean-kernel-arena" / "_build" / "checkers" / "nanoda" / "src"
MUTATIONS = ROOT / "mutations"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def replace_nth(text: str, old: str, new: str, occurrence: int) -> str | None:
    offset = 0
    for _ in range(occurrence + 1):
        index = text.find(old, offset)
        if index < 0:
            return None
        offset = index + len(old)
    return text[:index] + new + text[index + len(old) :]


def source_digest() -> str:
    digest = hashlib.sha256()
    for path in sorted((CHECKER_ROOT / "src").rglob("*.rs")):
        digest.update(str(path.relative_to(CHECKER_ROOT)).encode())
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


class DifferentialSession:
    """Build both checker states once and evaluate many artifacts safely."""

    def __init__(self, mutant_id: str, timeout: float = 60.0) -> None:
        self.mutant_id = mutant_id
        self.timeout = timeout
        self.spec_path = MUTATIONS / f"{mutant_id}.json"
        self.spec = json.loads(self.spec_path.read_text(encoding="utf-8"))
        self.source_path = CHECKER_ROOT / self.spec["source_file"]
        self.config = CHECKER_ROOT / "config.json"
        self._temp: tempfile.TemporaryDirectory[str] | None = None
        self.baseline_binary: Path | None = None
        self.mutant_binary: Path | None = None
        self.preparation: dict[str, Any] = {}
        self.checker_runs = 0
        self.checker_seconds = 0.0

    def set_state(self, state: str) -> str:
        original = self.spec["original"]
        mutated = self.spec["mutated"]
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
            replaced = replace_nth(text, original, mutated, self.spec.get("replace_occurrence", 0))
            if replaced is not None:
                self.source_path.write_text(replaced, encoding="utf-8")
                return "changed"
        else:
            raise ValueError(f"unknown source state: {state}")
        raise RuntimeError(f"{self.source_path}: neither expected source state found")

    def build(self) -> dict[str, Any]:
        started = time.monotonic()
        proc = subprocess.run(
            ["cargo", "build", "--release"],
            cwd=CHECKER_ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        result = {
            "returncode": proc.returncode,
            "seconds": time.monotonic() - started,
            "output_tail": proc.stdout[-4000:] if proc.returncode else "",
        }
        if proc.returncode:
            raise RuntimeError(f"nanoda build failed: {result}")
        return result

    def prepare(self) -> None:
        if self._temp is not None:
            return
        self._temp = tempfile.TemporaryDirectory(prefix=f"leanverifier-{self.mutant_id}-")
        temp_root = Path(self._temp.name)
        active = False
        baseline_source = None
        try:
            self.preparation["restore_before"] = self.set_state("baseline")
            baseline_source = source_digest()
            self.preparation["baseline_build"] = self.build()
            self.baseline_binary = temp_root / "nanoda-baseline"
            shutil.copy2(CHECKER_ROOT / "target" / "release" / "nanoda_bin", self.baseline_binary)
            self.preparation["apply_mutant"] = self.set_state("mutant")
            active = True
            self.preparation["mutant_build"] = self.build()
            self.mutant_binary = temp_root / "nanoda-mutant"
            shutil.copy2(CHECKER_ROOT / "target" / "release" / "nanoda_bin", self.mutant_binary)
        finally:
            if active:
                self.preparation["restore_after"] = self.set_state("baseline")
            self.preparation["restored_build"] = self.build()
            self.preparation["baseline_source_sha256"] = baseline_source
            self.preparation["restored_source_sha256"] = source_digest()
            self.preparation["source_restored"] = baseline_source == source_digest()
        if not self.preparation["source_restored"]:
            raise RuntimeError("nanoda source was not restored after differential preparation")

    def run_one(self, binary: Path, artifact: Path) -> dict[str, Any]:
        started = time.monotonic()
        try:
            with artifact.open("rb") as handle:
                proc = subprocess.run(
                    [str(binary), str(self.config)],
                    cwd=CHECKER_ROOT,
                    stdin=handle,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=self.timeout,
                )
            if proc.returncode == 0:
                outcome = "ACCEPT"
            elif proc.returncode == 2:
                outcome = "DECLINE"
            elif proc.returncode < 0:
                outcome = "CRASH"
            else:
                outcome = "REJECT"
            result = {
                "normalized_outcome": outcome,
                "exit_code": proc.returncode,
                "stdout_sha256": hashlib.sha256(proc.stdout).hexdigest(),
                "stderr_sha256": hashlib.sha256(proc.stderr).hexdigest(),
                "stderr_tail": proc.stderr.decode(errors="replace")[-1000:],
            }
        except subprocess.TimeoutExpired:
            result = {
                "normalized_outcome": "TIMEOUT",
                "exit_code": None,
                "stdout_sha256": None,
                "stderr_sha256": None,
                "stderr_tail": "",
            }
        seconds = time.monotonic() - started
        result["seconds"] = seconds
        self.checker_runs += 1
        self.checker_seconds += seconds
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

    def __enter__(self) -> "DifferentialSession":
        self.prepare()
        return self

    def __exit__(self, *_: object) -> None:
        self.close()
