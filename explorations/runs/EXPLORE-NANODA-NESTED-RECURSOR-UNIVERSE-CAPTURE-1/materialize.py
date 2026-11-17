#!/usr/bin/env python3
"""Materialize the valid nested control export through the retained Arena exporter."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil
import subprocess


ROOT = Path(__file__).resolve().parents[3]
RUN = Path(__file__).resolve().parent
ARENA = ROOT / "external" / "lean-kernel-arena"
NAME = "lal-nested-recursor-universe-capture-control"
SOURCE = RUN / "fixture-source.lean"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    status = subprocess.run(
        ["git", "status", "--porcelain"], cwd=ARENA, check=True,
        text=True, stdout=subprocess.PIPE,
    ).stdout.strip()
    if status:
        raise RuntimeError("Arena checkout must be clean before fixture materialization")
    tests = ARENA / "tests"
    temporary_source = tests / f"{NAME}.lean"
    temporary_yaml = tests / f"{NAME}.yaml"
    output = RUN / "inputs" / "base.ndjson"
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        raise RuntimeError("base export already exists")
    try:
        shutil.copyfile(SOURCE, temporary_source)
        temporary_yaml.write_text(
            "description: Prospective nested-recursor universe-capture control.\n"
            f"leanfile: tests/{temporary_source.name}\n"
            "export-decls: [\"LALNest.mainConsumer_iota\"]\n"
            "outcome: accept\n",
            encoding="utf-8",
        )
        attempts = RUN / "attempts"
        attempts.mkdir(exist_ok=True)
        legacy_stdout = RUN / "materialize.stdout"
        legacy_stderr = RUN / "materialize.stderr"
        if legacy_stdout.exists() or legacy_stderr.exists():
            prior = attempts / "materialize-r1"
            prior.mkdir(exist_ok=False)
            if legacy_stdout.exists():
                legacy_stdout.rename(prior / "stdout.log")
            if legacy_stderr.exists():
                legacy_stderr.rename(prior / "stderr.log")
        attempt = attempts / "materialize-r2"
        attempt.mkdir(exist_ok=False)
        completed = subprocess.run(
            [str(ROOT / ".venv-arena" / "bin" / "python"), "lka.py", "build-test", NAME],
            cwd=ARENA, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        (attempt / "stdout.log").write_bytes(completed.stdout)
        (attempt / "stderr.log").write_bytes(completed.stderr)
        if completed.returncode != 0:
            raise RuntimeError(f"Arena build-test failed with {completed.returncode}")
        built = ARENA / "_build" / "tests" / f"{NAME}.ndjson"
        shutil.copyfile(built, output)
    finally:
        temporary_source.unlink(missing_ok=True)
        temporary_yaml.unlink(missing_ok=True)
    if subprocess.run(
        ["git", "status", "--porcelain"], cwd=ARENA, check=True,
        text=True, stdout=subprocess.PIPE,
    ).stdout.strip():
        raise RuntimeError("fixture materialization left the Arena checkout dirty")
    record = {
        "schema_version": 1,
        "arena_commit": subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=ARENA, check=True,
            text=True, stdout=subprocess.PIPE,
        ).stdout.strip(),
        "source": {"path": str(SOURCE.relative_to(ROOT)), "sha256": sha(SOURCE)},
        "base": {"path": str(output.relative_to(ROOT)), "sha256": sha(output),
                 "bytes": output.stat().st_size,
                 "records": len(output.read_bytes().splitlines())},
        "command": [str(ROOT / ".venv-arena" / "bin" / "python"),
                    "lka.py", "build-test", NAME],
        "temporary_arena_files_removed": True,
    }
    (RUN / "materialization.json").write_text(
        json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(record, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
