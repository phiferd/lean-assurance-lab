"""Stage and execute the frozen E0 sample, preserving every supervised attempt."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from lib.resource_envelope_supervisor import run_direct

HERE = Path(__file__).resolve().parent
CID = "580ee65b7ba85f7e16898abdc16f3e5add59caf63a83c03fda765097209b16a4"
PINNED = {
    "/opt/lean-fast/bin/lean": "79fb1d26fa5a39385d59fdc48a711a14b0710ca6480271acce99b4d177cea085",
    "/opt/nanoda/target/release/nanoda_bin": "5e99b44c8b371ca1aedbc1a609a391ca5ac61b834b14fa60871298affb23d962",
    "/opt/comparator/.lake/packages/lean4export/.lake/build/lib/lean/Export/Parse.olean": "c264ea4ad5e30bd90cd03a1b48d944c4a7317e53b483b99c04df8c3a6882f133",
    "/opt/comparator/.lake/packages/lean4export/Export/Parse.lean": "1f943b5cc776eece6d528937b976509c8bd57d10bc69a39b1c119bfb6d664286",
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def attempt(label, args, timeout=30):
    out = HERE / "attempts" / label
    out.mkdir(parents=True, exist_ok=False)
    argv = [shutil.which(args[0]) or args[0], *args[1:]]
    (out / "command.json").write_text(json.dumps({"argv": argv, "timeout_seconds": timeout}, indent=2) + "\n")
    try:
        result = run_direct(argv=argv, cwd=ROOT, env=dict(os.environ), stdin_bytes=None,
                            timeout_seconds=timeout, memory_ceiling_bytes=4 * 1024**3,
                            sample_interval_seconds=0.5, max_trace_gap_seconds=5,
                            cleanup_seconds=10, output_cap_bytes=20 * 1024**2)
    except Exception as exc:
        (out / "setup_failure.json").write_text(json.dumps({"error": repr(exc)}) + "\n")
        raise
    (out / "stdout.log").write_bytes(result.stdout)
    (out / "stderr.log").write_bytes(result.stderr)
    (out / "receipt.json").write_text(json.dumps(result.receipt, indent=2) + "\n")
    if not result.receipt["cleanup_complete"] or result.receipt["monitor_errors"] or result.receipt["stop_reason"]:
        raise RuntimeError(f"supervision repair required: {label}")
    return result


def require_ok(label, args, timeout=30):
    result = attempt(label, args, timeout)
    if result.receipt["exit_code"] != 0:
        raise RuntimeError(f"setup failed: {label}; inspect retained raw output")
    return result.stdout.decode()


def main():
    cases = json.loads((HERE / "cases.json").read_text())
    assert len(cases) == 6
    for case in cases:
        assert sha(ROOT / case["path"]) == case["sha256"]
        assert sha(ROOT / case["config"]) == case["config_sha256"]
    expected = dict(PINNED)
    expected["/expression-tools/Replay.lean"] = sha(HERE / "Replay.lean")
    for case in cases:
        for suffix, key in ((".ndjson", "sha256"), (".json", "config_sha256")):
            expected["/expression-in/" + case["id"] + suffix] = case[key]
    require_ok("01-mkdir", ["docker", "exec", CID, "mkdir", "-p", "/expression-in", "/expression-tools"])
    require_ok("02-stage-inputs", ["docker", "cp", str(HERE / "inputs") + "/.", CID + ":/expression-in/"])
    require_ok("03-stage-importer", ["docker", "cp", str(HERE / "Replay.lean"), CID + ":/expression-tools/Replay.lean"])
    observed = require_ok("04-stage-hashes", ["docker", "exec", CID, "sha256sum", *expected])
    got = dict(line.split(maxsplit=1)[::-1] for line in observed.splitlines())
    assert got == expected, (got, expected)
    print("Staged scientific inputs and pinned runtimes verified.", flush=True)
    for case in cases:
        ident = case["id"]
        for checker in ("lean", "nanoda"):
            prefix = ["docker", "exec", "--user", "checker", "--workdir", "/expression-in",
                      "--env", "LEAN_PATH=/opt/comparator/.lake/packages/lean4export/.lake/build/lib/lean", CID,
                      "timeout", "--kill-after=10", "120"]
            command = (["/opt/lean-fast/bin/lean", "--run", "/expression-tools/Replay.lean",
                        "/expression-in/" + ident + ".ndjson"] if checker == "lean" else
                       ["/opt/nanoda/target/release/nanoda_bin", "/expression-in/" + ident + ".json"])
            result = attempt("cell-" + ident + "-" + checker, prefix + command, 145)
            print(json.dumps({"case": ident, "checker": checker,
                              "exit_code": result.receipt["exit_code"],
                              "elapsed_seconds": result.receipt["elapsed_seconds"]}), flush=True)
            # Keep the guest attribution check independent of the transport exit code.
            require_ok("post-" + ident + "-" + checker,
                       ["docker", "exec", CID, "sha256sum", "/expression-in/" + ident + ".ndjson"])
    print("All twelve cells launched; inspect raw outputs for classification.", flush=True)


if __name__ == "__main__":
    main()
