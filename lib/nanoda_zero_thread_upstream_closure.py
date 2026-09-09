"""Validate the bounded Nanoda zero-thread upstream-readiness closure."""
from __future__ import annotations

from io import BytesIO
import hashlib
import json
from pathlib import Path
import subprocess
import tarfile

from lib.research_queue_v3 import load_queue

BASE = Path("results/research/nanoda-zero-thread-upstream-readiness-1")
ITEM = "NANODA-ZERO-THREAD-UPSTREAM-READINESS-1"
NEXT = "SURVIVOR-CACHE-PREDICATE-TRANSFER-1"
ENTRY = "b7428e4295b4192d3159cb5fdde13b2e85ca7541"
HEAD = "05055695879dfebb6628a67da88ceca6cd6b0421"
TOP = "nanoda_lib-" + HEAD


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_bytes(root: Path, path: str) -> bytes:
    return subprocess.check_output(["git", "show", f"{ENTRY}:{path}"], cwd=root)


def member_bytes(archive: bytes, path: str) -> bytes:
    with tarfile.open(fileobj=BytesIO(archive), mode="r:gz") as stream:
        member = stream.getmember(TOP + "/" + path)
        file = stream.extractfile(member)
        require(file is not None, "archive member is not a file: " + path)
        return file.read()


def validate_source(archive: bytes) -> dict:
    with tarfile.open(fileobj=BytesIO(archive), mode="r:gz") as stream:
        names = stream.getnames()
    require(len(names) == 38 and all(name == TOP or name.startswith(TOP + "/")
                                     for name in names), "archive identity or member count differs")
    cargo = member_bytes(archive, "Cargo.toml")
    util = member_bytes(archive, "src/util.rs")
    tc = member_bytes(archive, "src/tc.rs")
    main = member_bytes(archive, "src/main.rs")
    require(digest(cargo) == "7d0e2d09ddac124d83d9d634bb7140fe7803047870f52fe4ea10d3ddb155d823"
            and b'version = "0.4.16"' in cargo, "Cargo identity differs")
    require(digest(util) == "e6de5f6f396dd119bf28eebe36e79a2f2828130549b3f50b9d0d3eaa9d4ea383"
            and b"#[serde(default)]\n    pub num_threads: usize," in util,
            "public zero-thread configuration differs")
    require(digest(tc) == "9aa8a3aa3bb8824075331f5cd1a21797f91fd585412ff690a05163488e578a5f"
            and b"for declar in self.declars.values() {\n            self.check_declar(declar);" in tc
            and b"if self.config.num_threads > 1 {\n            self.check_all_declars_par(self.config.num_threads)\n        } else {\n            self.check_all_declars_serial()" in tc,
            "current serial fallback differs")
    require(digest(main) == "245ceaef34e8925cacaa3c5b99ce096a8c744710ce1f9184423e5a0333e8b35a"
            and main.index(b"export_file.check_all_declars();")
            < main.index(b"Checked {} declarations with no errors"),
            "success reporting order differs")
    return {"version": "0.4.16", "head": HEAD, "members": len(names),
            "zero_thread_dispatch": "SERIAL"}


def validate(root: Path) -> dict:
    root = root.resolve()
    entry_paths = {
        "config/research-queue.json": "3d6d6d947d0b48ee0d8200cf73d932e259dd2170707de68cdedfeffb16c8f246",
        "docs/RESEARCH_STATUS.md": "027b096b686cc27666675ae8b543b7f4c32eeb37363a6123528335252b91e4be",
        str(BASE / "work-record.json"): "826533669333158d9602e8c6d2f132bda5e236e4715d6cf18ff0eba11f7e1d6f",
        str(BASE / "request-log.json"): "a02f27c52c07d25f87baef13ffedc3dc94368dd9108e905ff2e1c9d3ce35a047",
        str(BASE / "source-identity-protocol.json"): "2b4d43d7ea627e22d53b8843065871a2cab5c4e141ca924fe68800aac1bdf8ff",
        str(BASE / "decision-rubric.json"): "ee473b18c13075f2d68b7cca0fd8344f1398ca1cde6db5702a9ef486e2ea9c0b",
    }
    for path, expected in entry_paths.items():
        require(digest(git_bytes(root, path)) == expected, "entry binding differs: " + path)
    entry_queue = json.loads(git_bytes(root, "config/research-queue.json"))
    entry_log = json.loads(git_bytes(root, str(BASE / "request-log.json")))
    require(entry_queue["selected_item"] == ITEM
            and next(row for row in entry_queue["items"] if row["id"] == ITEM)["status"] == "ACTIVE"
            and entry_log["consumed_requests"] == 0 and entry_log["requests"] == [],
            "entry checkpoint was not active and request-clean")

    log = load(root / BASE / "request-log.json")
    require(log["status"] == "REQUEST_SEQUENCE_COMPLETE"
            and log["request_cap"] == 6 and log["consumed_requests"] == 4
            and log["next_request_id"] is None and log["external_writes"] == 0
            and [row["id"] for row in log["requests"]]
            == ["repository-metadata", "head-commit", "source-archive", "issues-page-1"],
            "request sequence or accounting differs")
    for row in log["requests"]:
        require(row["method"] == "GET" and row["outcome"] == "SUCCESS"
                and row["http_status"] == 200 and row["error"] is None,
                "request outcome differs: " + row["id"])
        body = (root / row["body"]["path"]).read_bytes()
        metadata = load((root / row["body"]["path"]).parent / "metadata.json")
        require(digest(body) == row["body"]["sha256"]
                and len(body) == row["body"]["bytes"] and metadata == row,
                "raw request custody differs: " + row["id"])
    by_id = {row["id"]: row for row in log["requests"]}
    repository = json.loads((root / by_id["repository-metadata"]["body"]["path"]).read_bytes())
    head = json.loads((root / by_id["head-commit"]["body"]["path"]).read_bytes())
    require(repository["full_name"] == "ammkrn/nanoda_lib"
            and repository["default_branch"] == "master"
            and repository["archived"] is False and repository["disabled"] is False
            and head["sha"] == HEAD
            and head["commit"]["tree"]["sha"] == "407fa5f738fb09a27c54060dae8f3ae5f9289b1c",
            "repository or head identity differs")
    archive = (root / by_id["source-archive"]["body"]["path"]).read_bytes()
    source = validate_source(archive)

    issues = json.loads((root / by_id["issues-page-1"]["body"]["path"]).read_bytes())
    numbers = [30, 29, 28, 25, 27, 26, 24, 23, 22, 21, 20, 18, 19, 17,
               15, 16, 14, 11, 13, 6, 10, 9, 8, 7, 5, 3, 4, 2, 1]
    require(len(issues) == 29 and [row["number"] for row in issues] == numbers
            and "link" not in by_id["issues-page-1"]["response_headers"],
            "issue/PR inventory completeness differs")

    assessment = load(root / BASE / "current-source-assessment.json")
    duplicate = load(root / BASE / "duplicate-assessment.json")
    no_action = load(root / BASE / "no-action-recommendation.json")
    result = load(root / BASE / "result.json")
    work = load(root / BASE / "work-record.json")
    closure = load(root / BASE / "work-closure.json")
    require(assessment["decision"] == result["gate_decision"] == closure["gate_decision"] == "NO_GO"
            and assessment["reason"] == "CURRENT_ZERO_THREAD_PATH_CHECKS_EVERY_DECLARATION_SERIALLY"
            and assessment["repository"]["head_sha"] == source["head"]
            and duplicate["inventory_scope"]["returned_numbers"] == numbers
            and duplicate["matching_report_or_regression_found"] is False
            and duplicate["inventory_scope"]["inventory_complete_within_protocol"] is True
            and no_action["recommended_action"] == "NO_UPSTREAM_ACTION"
            and no_action["external_writes_performed"] == 0
            and result["outcome"] == closure["outcome"] == work["outcome"] == "SUCCESS",
            "NO_GO result package differs")
    accounting = closure["accounting"]
    require(work["status"] == closure["status"] == "COMPLETE"
            and accounting["sessions"] == 1
            and accounting["active_seconds_charged_conservatively"] == 2400 <= 3600
            and accounting["read_only_upstream_requests"] == 4 <= 6
            and accounting["local_code_or_evidence_inspections"] == 6
            and all(accounting[name] == 0 for name in
                    ("builds", "checker_launches", "lean_proof_launches",
                     "new_scientific_byte_variants", "new_mutation_identities", "external_writes"))
            and closure["next_item"] == result["recommendation"]["next_item"] == NEXT
            and not closure["next_item_started"] and not work["next_item_started"]
            and not result["next_item_started"], "closure accounting or stop boundary differs")

    preservation = load(root / BASE / "canonical-state-preservation.json")
    require(preservation["status"] == "MUTATION_STATE_UNCHANGED_DERIVED_SNAPSHOT_REFRESHED",
            "canonical preservation record differs")
    for row in preservation["artifacts"]:
        data = (root / row["path"]).read_bytes()
        require(digest(data) == row["after_sha256"]
                and len(data.splitlines()) == row["lines"],
                "canonical artifact differs: " + row["path"])
        if row["path"] != "results/assurance/current.json":
            require(row["before_sha256"] == row["after_sha256"],
                    "canonical mutation input changed: " + row["path"])

    manifest = load(root / BASE / "evidence-manifest.json")
    require(manifest["item_id"] == ITEM and manifest["status"] == "PASS",
            "evidence manifest differs")
    paths = [row["path"] for row in manifest["artifacts"]]
    required = {str(BASE / name) for name in
                ("current-source-assessment.json", "duplicate-assessment.json",
                 "no-action-recommendation.json", "result.json", "report.md",
                 "request-log.json", "work-record.json", "work-closure.json")}
    require(required <= set(paths) and len(paths) == len(set(paths)),
            "evidence manifest is incomplete or duplicate")
    for row in manifest["artifacts"]:
        data = (root / row["path"]).read_bytes()
        require(digest(data) == row["sha256"] and len(data) == row["bytes"],
                "manifest binding differs: " + row["path"])

    queue = load_queue(root, require_ready=True)
    by_item = {row["id"]: row for row in queue["items"]}
    require(queue["frontier_id"] == "F-SURVIVOR-CACHE-PREDICATE-TRANSFER"
            and queue["selected_item"] == NEXT
            and by_item[ITEM]["status"] == "COMPLETE"
            and by_item[NEXT]["status"] == "READY"
            and not any(row["status"] == "ACTIVE" for row in queue["items"]),
            "queue handoff differs")
    return {"status": "PASS", "outcome": "SUCCESS", "gate_decision": "NO_GO",
            "head": HEAD, "requests": 4, "issues_and_prs": 29,
            "zero_thread_dispatch": source["zero_thread_dispatch"],
            "selected_item": NEXT}
