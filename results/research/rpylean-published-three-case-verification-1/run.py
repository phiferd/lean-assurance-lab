"""Replay the three registered comparisons. Use Python 3.13 and a new output directory."""
import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import platform
import re
import subprocess
import tarfile
import tempfile
import time


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def checked_file(path, expected):
    if digest(path) != expected:
        raise ValueError(f"Unexpected SHA-256 for {path}")
    return path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--arena", type=Path, required=True)
    parser.add_argument("--pypy-source", type=Path, required=True)
    parser.add_argument("--pypy", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    here = Path(__file__).resolve().parent
    lab = here.parents[2]
    lock = here / "inputs.json"
    spec = json.loads(lock.read_text())
    tooling = json.loads((here / "tooling-v2.json").read_text())
    checked_file(lock, tooling["inputs_sha256"])
    checked_file(Path(__file__), tooling["controller_sha256"])
    archive = checked_file(args.archive, spec["checker"]["archive_sha256"])
    exe = checked_file(args.pypy.resolve(), spec["runtime"]["executable_sha256"])
    output = args.output.resolve()
    output.mkdir(exist_ok=False)
    with tempfile.TemporaryDirectory(prefix="lal-rpylean-verify-") as work:
        work = Path(work)
        with tarfile.open(archive) as source:
            source.extractall(work, filter="data")
        checker = work / ("rpylean-" + spec["checker"]["commit"])
        # Import both the RPython modules and the py package from one pinned tree.
        deps = work / "deps"
        deps.mkdir()
        dep_tar = work / "rpython.tar"
        with dep_tar.open("wb") as stream:
            subprocess.run(["git", "-C", args.pypy_source, "archive",
                            spec["runtime"]["rpython_commit"], "rpython", "py"],
                           stdout=stream, check=True)
        with tarfile.open(dep_tar) as source:
            source.extractall(deps, filter="data")

        inputs = []
        for case in spec["cases"]:
            binding = case["input"]
            repo = args.arena if binding["repository"] == "arena" else lab
            data = subprocess.check_output(["git", "-C", repo, "show",
                                           binding["commit"] + ":" + binding["path"]])
            path = work / Path(binding["path"]).name
            path.write_bytes(data)
            inputs.append(checked_file(path, binding["sha256"]))

        env = {"PATH": os.defpath, "HOME": str(work), "TMPDIR": str(work),
               "LC_ALL": "C", "PYTHONPATH": os.pathsep.join(map(str, (checker, deps))),
               "PYTHONDONTWRITEBYTECODE": "1", "PYTHONNOUSERSITE": "1"}
        probe = subprocess.run([exe, "-m", "rpylean", "--help"], cwd=checker, env=env,
                               capture_output=True, timeout=spec["timeout_seconds_per_process"])
        (output / "preflight.txt").write_bytes(probe.stdout + probe.stderr)
        probe.check_returncode()

        for case, path in zip(spec["cases"], inputs):
            checked_file(path, case["input"]["sha256"])
            folder = output / case["id"]
            folder.mkdir()
            start = datetime.now(timezone.utc).isoformat()
            tick = time.monotonic()
            argv = [str(exe), *spec["checker"]["arguments"], str(path)]
            code = None
            timed_out = False
            with (folder / "stdout.txt").open("xb") as stdout, (folder / "stderr.txt").open("xb") as stderr:
                try:
                    proc = subprocess.run(argv, cwd=checker, env=env, stdout=stdout,
                                          stderr=stderr, stdin=subprocess.DEVNULL,
                                          timeout=spec["timeout_seconds_per_process"])
                    code = proc.returncode
                except subprocess.TimeoutExpired:
                    timed_out = True
            diagnostic = (folder / "stderr.txt").read_bytes()
            summary = re.search(rb"^summary: (\d+)/(\d+) decls checked,", diagnostic, re.M)
            reached_checker = bool(summary and int(summary[2]) > 0)
            receipt = {"id": case["id"], "controller_sha256": digest(Path(__file__)),
                       "checker_summary_present": reached_checker, "inputs_sha256": digest(lock), "started_at": start,
                       "elapsed_seconds": round(time.monotonic() - tick, 4),
                       "host": platform.platform(), "architecture": platform.machine(),
                       "argv": argv, "cwd": str(checker), "environment": env,
                       "input_sha256_after": digest(path), "exit_code": code,
                       "timed_out": timed_out,
                       "stdout_sha256": digest(folder / "stdout.txt"),
                       "stderr_sha256": digest(folder / "stderr.txt")}
            (folder / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
            if timed_out or code not in (0, 1) or not reached_checker or receipt["input_sha256_after"] != case["input"]["sha256"]:
                raise RuntimeError(f"Execution needs review: {case['id']}")


if __name__ == "__main__":
    main()
