"""Read the published rpylean experiment's six saved processes without invoking a checker."""

from hashlib import sha256
import json
from pathlib import Path, PurePosixPath
import re


BASE = Path("results/research/rpylean-published-three-case-verification-1")
INPUTS_SHA256 = "ba1c0bed823a596dbf97b3ef59ce4996728dd2b73e9d3eff261a4edd89803ed8"
TOOLING_SHA256 = "ccd7d2a115a1371bebd29a602fdfdd26a73cfc65eaa1fcf5e6975b6faa7ee82b"
HOST_WARNINGS = {
    "Warning: cannot find your CPU L2 cache size with sysctl()",
    "[version:WARNING] Errors getting Mercurial information: Not running from a Mercurial repository!",
    "sysctl: sysctl fmt -1 1024 1: Operation not permitted",
}
DIAGNOSTICS = {
    "rec-missing-ih": "field #3 of Native64TwoHashOwner.step has an invalid occurrence of the types being declared",
    "rec-rule-wrong-arg": "rule for W.mk is not the one its inductive gives rise to",
}


def _bound_bytes(path, expected):
    data = path.read_bytes()
    if sha256(data).hexdigest() != expected:
        raise ValueError(f"evidence digest differs: {path}")
    return data


def _verdict(case_id, code, lines):
    if len(lines) < 2 or not re.fullmatch(r"checked in [0-9.]+s", lines[-1]):
        raise ValueError(f"incomplete checker output: {case_id}")
    match = re.fullmatch(r"summary: (\d+)/(\d+) decls checked, heartbeats \d+", lines[-2])
    if not match or not (0 < int(match[1]) == int(match[2])):
        raise ValueError(f"incomplete declaration summary: {case_id}")
    messages = [line for line in lines[:-2] if line not in HOST_WARNINGS]
    diagnostic = DIAGNOSTICS.get(case_id)
    if code == 0 and not messages:
        return "accept", int(match[1]), None
    if code == 1 and messages and messages[-1] == diagnostic:
        return "reject", int(match[1]), diagnostic
    raise ValueError(f"unrecognized checker verdict: {case_id}")


def replay(root: Path) -> dict:
    base = root / BASE
    spec = json.loads(_bound_bytes(base / "inputs.json", INPUTS_SHA256))
    tooling = json.loads(_bound_bytes(base / "tooling-v2.json", TOOLING_SHA256))
    _bound_bytes(base / "run.py", tooling["controller_sha256"])
    result = json.loads((base / "result.json").read_bytes())
    if (result["experiment"] != spec["experiment"] or result["status"] != "COMPLETE"
            or result["checker_revision"] != spec["checker"]["commit"]
            or result["profile"] != spec["runtime"]["profile"]
            or result["input_lock_sha256"] != INPUTS_SHA256
            or result["tooling_repair_sha256"] != TOOLING_SHA256):
        raise ValueError("experiment binding differs")

    attempts = []
    verdicts = []
    receipt_paths = set()
    for attempt in ("attempt-1", "attempt-2"):
        processes = []
        for case in spec["cases"]:
            case_id = case["id"]
            folder = Path(attempt, case_id)
            path = folder / "receipt.json"
            receipt_paths.add(path)
            receipt = json.loads((base / path).read_bytes())
            cwd = PurePosixPath(receipt["cwd"])
            argv = receipt["argv"]
            fixture = cwd.parent / PurePosixPath(case["input"]["path"]).name
            if (receipt["id"] != case_id or receipt["inputs_sha256"] != INPUTS_SHA256
                    or receipt["input_sha256_after"] != case["input"]["sha256"]
                    or receipt["timed_out"] is not False or not cwd.is_absolute()
                    or cwd.name != "rpylean-" + spec["checker"]["commit"]
                    or not argv or not PurePosixPath(argv[0]).is_absolute()
                    or PurePosixPath(argv[0]).name != "pypy"
                    or argv[1:] != [*spec["checker"]["arguments"], str(fixture)]):
                raise ValueError(f"process binding differs: {path}")
            stdout = _bound_bytes(base / folder / "stdout.txt", receipt["stdout_sha256"])
            stderr = _bound_bytes(base / folder / "stderr.txt", receipt["stderr_sha256"])
            lines = stderr.decode().splitlines()
            code = receipt["exit_code"]
            if stdout:
                raise ValueError(f"unexpected checker stdout: {path}")
            if attempt == "attempt-1":
                if (code != 1 or not lines or lines[-1] != "ImportError: No module named py"
                        or any(line.startswith("summary:") for line in lines)):
                    raise ValueError(f"startup failure evidence differs: {path}")
                disposition = "STARTUP_FAILURE"
            else:
                if (receipt["controller_sha256"] != tooling["controller_sha256"]
                        or receipt["checker_summary_present"] is not True):
                    raise ValueError(f"repaired controller receipt differs: {path}")
                observed, count, diagnostic = _verdict(case_id, code, lines)
                verdicts.append({
                    "case": case["arena_case"], "expected": case["expected"], "observed": observed,
                    "matches_expected": observed == case["expected"], "sha256": case["input"]["sha256"],
                    "exit_code": code, "checked_at_summary": count, "seen_at_summary": count,
                    "semantic_diagnostic": diagnostic, "stdout": (folder / "stdout.txt").as_posix(),
                    "stderr": (folder / "stderr.txt").as_posix(), "receipt": path.as_posix(),
                })
                disposition = "CHECKER_VERDICT"
            processes.append({"id": case_id, "receipt": path.as_posix(),
                              "elapsed_seconds": receipt["elapsed_seconds"], "exit_code": code,
                              "disposition": disposition})
        attempts.append({"id": attempt, "processes": processes})
    if receipt_paths != {path.relative_to(base) for path in base.rglob("receipt.json")}:
        raise ValueError("process receipt inventory differs")
    if attempts != result["attempts"] or verdicts != result["cases"]:
        raise ValueError("published result differs from saved processes")
    return {"processes": len(receipt_paths), "cases": {row["case"]: row["observed"] for row in verdicts}}
