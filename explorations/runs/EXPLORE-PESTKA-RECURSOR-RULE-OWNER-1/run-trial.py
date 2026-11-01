#!/usr/bin/env python3
"""Run only the three frozen Pestka cells; retain every raw observation."""
import hashlib
import json
import os
from pathlib import Path
import resource
import signal
import subprocess
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def limit():
    os.setsid()
    resource.setrlimit(resource.RLIMIT_AS, (4 * 1024**3, 4 * 1024**3))


def main():
    protocol = json.loads((HERE / "protocol.json").read_text())
    for path, expected in protocol["input_sha256"].items():
        if sha(ROOT / path) != expected:
            raise RuntimeError("frozen input differs: " + path)
    receipts = []
    for cell in protocol["cells"]:
        out = HERE / "attempts" / cell["id"]
        out.mkdir(exist_ok=False)
        binary = ROOT / protocol["binary"]
        fixture = ROOT / cell["input"]
        argv = [str(binary), str(fixture), "1"]
        started = time.monotonic()
        proc = subprocess.Popen(argv, cwd=HERE, stdout=subprocess.PIPE,
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
        lines = stdout.decode(errors="replace").splitlines()
        last = lines[-1] if lines else ""
        verdict = ("accept" if last == "accepted" and proc.returncode == 0 else
                   "reject" if last.startswith("rejected: ") and proc.returncode == 1 else
                   "decline" if last.startswith("declined: ") and proc.returncode == 2 else
                   "error")
        receipt = {
            "id": cell["id"], "argv": argv, "cwd": str(HERE),
            "input": cell["input"], "input_sha256": sha(fixture),
            "binary_sha256": sha(binary), "exit_code": proc.returncode,
            "timed_out": timed_out, "elapsed_seconds": time.monotonic() - started,
            "stdout_sha256": hashlib.sha256(stdout).hexdigest(),
            "stderr_sha256": hashlib.sha256(stderr).hexdigest(),
            "stdout_bytes": len(stdout), "stderr_bytes": len(stderr),
            "verdict": verdict, "last_line": last,
            "cleanup_complete": proc.poll() is not None,
        }
        (out / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
        receipts.append(receipt)
        print(json.dumps({"id": cell["id"], "verdict": verdict,
                          "exit_code": proc.returncode, "last_line": last}), flush=True)
        if timed_out or verdict == "error":
            raise RuntimeError("engineering failure retained: " + cell["id"])
    (HERE / "observations.json").write_text(json.dumps(receipts, indent=2) + "\n")


if __name__ == "__main__":
    main()
