#!/usr/bin/env python3
"""Run the six frozen recursor-boundary assurance cells."""
import hashlib
import json
import os
from pathlib import Path
import resource
import signal
import subprocess
import time

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
PROTOCOL = json.loads((HERE / "protocol.json").read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def limit():
    os.setsid()
    resource.setrlimit(resource.RLIMIT_AS, (2 * 1024**3, 2 * 1024**3))


def main():
    for relative, expected in PROTOCOL["input_sha256"].items():
        path = ROOT / relative
        if not path.is_file() or sha(path) != expected:
            raise RuntimeError("input differs: " + relative)
    for cell in PROTOCOL["cells"]:
        out = HERE / "attempts" / cell["id"]
        if out.exists():
            raise RuntimeError("attempt already exists: " + str(out))
        out.mkdir(parents=True)
        binary = ROOT / cell["binary"]
        config = ROOT / PROTOCOL["config"]
        fixture = ROOT / cell["input"]
        argv = [str(binary), str(config)]
        started = time.monotonic()
        with fixture.open("rb") as stdin:
            proc = subprocess.Popen(argv, cwd=HERE, stdin=stdin, stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE, preexec_fn=limit)
            try:
                stdout, stderr = proc.communicate(timeout=30)
                timed_out = False
            except subprocess.TimeoutExpired:
                os.killpg(proc.pid, signal.SIGKILL)
                stdout, stderr = proc.communicate()
                timed_out = True
        (out / "stdout").write_bytes(stdout)
        (out / "stderr").write_bytes(stderr)
        receipt = {
            "id": cell["id"], "argv": argv, "cwd": str(HERE),
            "input": cell["input"], "input_sha256": sha(fixture),
            "binary_sha256": sha(binary), "config_sha256": sha(config),
            "exit_code": proc.returncode, "timed_out": timed_out,
            "elapsed_seconds": time.monotonic() - started,
            "stdout_sha256": hashlib.sha256(stdout).hexdigest(),
            "stderr_sha256": hashlib.sha256(stderr).hexdigest(),
            "stdout_bytes": len(stdout), "stderr_bytes": len(stderr),
            "cleanup_complete": proc.poll() is not None,
        }
        (out / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
        print(json.dumps({"id": cell["id"], "exit_code": proc.returncode,
                          "timed_out": timed_out, "stderr_bytes": len(stderr)}), flush=True)
        if timed_out:
            raise RuntimeError("trial timed out: " + cell["id"])


if __name__ == "__main__":
    main()
