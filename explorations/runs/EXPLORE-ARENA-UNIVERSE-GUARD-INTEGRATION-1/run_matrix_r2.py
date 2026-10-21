"""Run exactly the two frozen integration cases on two cached, unmodified validators."""
import hashlib
import json
from pathlib import Path
import subprocess
import time

HERE = Path(__file__).resolve().parent
CID = "580ee65b7ba85f7e16898abdc16f3e5add59caf63a83c03fda765097209b16a4"
cases = json.loads((HERE / "cases.json").read_text())
# Revision 2: refuse all launches until discovery and every staged file match.
discovery = json.loads((HERE / "discovery/result.json").read_text())
assert discovery["discovery"] == "PASS" and discovery["static_file_copy"] == "PASS"
preflight = []
for case in cases:
    ident = case["id"]
    for suffix in (".ndjson", ".json"):
        local = HERE / ("discovery" if ident == "candidate" and suffix == ".ndjson" else "inputs") / (ident + suffix)
        digest = hashlib.sha256(local.read_bytes()).hexdigest()
        if suffix == ".ndjson":
            assert digest == case["sha256"]
        guest_file = "/arena-universe-guard-in/" + ident + suffix
        observed = subprocess.check_output(["docker", "exec", CID, "sha256sum", guest_file], text=True).split()[0]
        assert observed == digest, (guest_file, observed, digest)
        preflight.append({"path": guest_file, "sha256": digest})
(HERE / "staged-preflight-r2.json").write_text(json.dumps(preflight, indent=2)+"\n")
out = HERE / "observations-r2"
out.mkdir(exist_ok=False)
results = []
for case in cases:
    ident = case["id"]
    path = HERE / "inputs" / (ident + ".ndjson")
    assert hashlib.sha256(path.read_bytes()).hexdigest() == case["sha256"]
    guest = "/arena-universe-guard-in/" + path.name
    for checker in ("lean", "nanoda"):
        argv = ["docker", "exec", "--user", "checker", "--workdir", "/universe-out",
            "--env", "LEAN_PATH=/opt/comparator/.lake/packages/lean4export/.lake/build/lib/lean", CID,
            "timeout", "--kill-after=10", "120"]
        argv += (["/opt/lean-fast/bin/lean", "--run", "/universe-tools/Replay.lean", guest]
                 if checker == "lean" else ["/opt/nanoda/target/release/nanoda_bin", "/arena-universe-guard-in/" + ident + ".json"])
        start = time.monotonic()
        result = subprocess.run(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        elapsed = time.monotonic() - start
        cell = out / (ident + "-" + checker)
        cell.mkdir()
        (cell / "stdout.log").write_bytes(result.stdout)
        (cell / "stderr.log").write_bytes(result.stderr)
        row = {"case": ident, "checker": checker, "argv": argv,
            "input_sha256": case["sha256"], "exit_code": result.returncode,
            "elapsed_seconds": elapsed}
        (cell / "execution.json").write_text(json.dumps(row, indent=2) + "\n")
        results.append(row)
        print(json.dumps({k: row[k] for k in ("case", "checker", "exit_code", "elapsed_seconds")}), flush=True)
    # Recheck the actual staged input after both validators finish.
    observed = subprocess.check_output(["docker", "exec", CID, "sha256sum", guest], text=True).split()[0]
    assert observed == case["sha256"]
(out / "executions.json").write_text(json.dumps(results, indent=2) + "\n")
