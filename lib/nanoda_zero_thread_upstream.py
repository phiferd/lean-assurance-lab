"""Bounded read-only collector for Nanoda zero-thread upstream readiness."""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urlparse
from urllib.request import Request, urlopen

BASE = Path("results/research/nanoda-zero-thread-upstream-readiness-1")
PROTOCOL = BASE / "source-identity-protocol.json"
REQUEST_LOG = BASE / "request-log.json"
WORK = BASE / "work-record.json"
ORDER = ["repository-metadata", "head-commit", "source-archive",
         "issues-page-1", "issues-page-2", "issues-page-3"]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def atomic_json(path: Path, value) -> None:
    data = (json.dumps(value, indent=2, sort_keys=False, allow_nan=False) + "\n").encode()
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def json_body(root: Path, log: dict, request_id: str) -> dict:
    row = next((item for item in log["requests"] if item["id"] == request_id), None)
    require(row is not None and row["outcome"] == "SUCCESS", request_id + " unavailable")
    return json.loads((root / row["body"]["path"]).read_text(encoding="utf-8"))


def next_link(value: str | None) -> str | None:
    if not value:
        return None
    for segment in value.split(","):
        match = re.fullmatch(r'\s*<([^>]+)>;\s*rel="([^"]+)"\s*', segment)
        if match and match.group(2) == "next":
            return match.group(1)
    return None


def validate_issue_url(url: str, page: int) -> str:
    parsed = urlparse(url)
    require(parsed.scheme == "https" and parsed.netloc == "api.github.com"
            and parsed.path == "/repos/ammkrn/nanoda_lib/issues",
            "pagination URL changed repository or host")
    query = parse_qs(parsed.query)
    require(query == {"state": ["all"], "per_page": ["100"],
                      "sort": ["updated"], "direction": ["desc"],
                      "page": [str(page)]}, "pagination query drift")
    return url


def resolve_url(root: Path, protocol: dict, log: dict, request_id: str) -> str:
    spec = next(row for row in protocol["requests"] if row["id"] == request_id)
    if request_id in {"repository-metadata", "issues-page-1"}:
        return spec["url"]
    if request_id == "head-commit":
        branch = json_body(root, log, "repository-metadata")["default_branch"]
        require(isinstance(branch, str) and re.fullmatch(r"[A-Za-z0-9._/-]+", branch),
                "invalid default branch")
        return spec["url_template"].format(default_branch=branch)
    if request_id == "source-archive":
        head = json_body(root, log, "head-commit")["sha"]
        require(isinstance(head, str) and re.fullmatch(r"[0-9a-f]{40}", head),
                "invalid head SHA")
        return spec["url_template"].format(head_sha=head)
    prior_id = "issues-page-1" if request_id == "issues-page-2" else "issues-page-2"
    prior = next(row for row in log["requests"] if row["id"] == prior_id)
    link = next_link(prior["response_headers"].get("link"))
    require(link is not None, "conditional pagination request has no rel=next")
    return validate_issue_url(link, 2 if request_id == "issues-page-2" else 3)


def checkpoint(root: Path) -> None:
    work = load(root / WORK)
    queue = load(root / "config/research-queue.json")
    require(work["status"] == "ACTIVE" and queue["selected_item"] == work["item_id"],
            "work or selected item is not ACTIVE")
    selected = next(row for row in queue["items"] if row["id"] == work["item_id"])
    require(selected["status"] == "ACTIVE", "queue item is not ACTIVE")
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root,
                                   text=True).strip()
    require(head != work["base_commit"], "entry checkpoint has not been committed")
    immutable = [str(PROTOCOL), str(WORK),
                 str(BASE / "decision-rubric.json"),
                 "lib/nanoda_zero_thread_upstream.py",
                 "scripts/collect-nanoda-zero-thread-upstream",
                 "tests/test_nanoda_zero_thread_upstream.py",
                 "config/research-queue.json", "docs/RESEARCH_STATUS.md"]
    status = subprocess.run(["git", "diff", "--quiet", "HEAD", "--", *immutable],
                            cwd=root, check=False).returncode
    require(status == 0, "immutable entry checkpoint differs from HEAD")


def collect(root: Path, opener=urlopen) -> dict:
    root = root.resolve()
    checkpoint(root)
    protocol, log = load(root / PROTOCOL), load(root / REQUEST_LOG)
    require(log["consumed_requests"] == len(log["requests"])
            and log["consumed_requests"] < log["request_cap"] == 6,
            "request accounting or cap differs")
    request_id = log["next_request_id"]
    require(request_id in ORDER and request_id not in {row["id"] for row in log["requests"]},
            "no authorized next request")
    url = resolve_url(root, protocol, log, request_id)
    parsed = urlparse(url)
    transport = protocol["transport"]
    require(parsed.scheme == "https" and parsed.hostname in transport["allowed_hosts"],
            "request host is not allowed")
    started = now()
    request = Request(url, method="GET", headers={"User-Agent": transport["user_agent"],
                                                   "Accept": "application/vnd.github+json"})
    body = b""
    response_headers = {}
    status = None
    error = None
    try:
        with opener(request, timeout=transport["timeout_seconds"]) as response:
            status = response.status
            body = response.read(transport["max_response_bytes"] + 1)
            response_headers = {name.lower(): value for name, value in response.headers.items()
                                if name.lower() in {"content-type", "etag", "last-modified", "link"}}
            require(len(body) <= transport["max_response_bytes"], "response exceeded byte cap")
            require(status == 200, "unexpected HTTP status")
    except HTTPError as caught:
        status, error = caught.code, "HTTP_ERROR"
        body = caught.read(transport["max_response_bytes"] + 1)
        response_headers = {name.lower(): value for name, value in caught.headers.items()
                            if name.lower() in {"content-type", "etag", "last-modified", "link"}}
    except (URLError, TimeoutError, OSError) as caught:
        error = type(caught).__name__
    directory = root / BASE / "evidence/requests" / request_id
    directory.mkdir(parents=True, exist_ok=False)
    body_path = directory / "body"
    body_path.write_bytes(body)
    outcome = "SUCCESS" if status == 200 and error is None else "FAILURE"
    row = {"id": request_id, "method": "GET", "url": url, "started_at": started,
           "ended_at": now(), "http_status": status, "outcome": outcome,
           "error": error, "response_headers": response_headers,
           "body": {"path": str(body_path.relative_to(root)), "bytes": len(body),
                    "sha256": digest(body)}}
    atomic_json(directory / "metadata.json", row)
    log["requests"].append(row)
    log["consumed_requests"] += 1
    if outcome != "SUCCESS":
        log["status"], log["next_request_id"] = "STOPPED_REQUEST_FAILURE", None
    elif request_id.startswith("issues-page"):
        link = next_link(response_headers.get("link"))
        page = int(request_id.rsplit("-", 1)[1])
        if link is None:
            log["status"], log["next_request_id"] = "REQUEST_SEQUENCE_COMPLETE", None
        elif page < 3 and log["consumed_requests"] < log["request_cap"]:
            log["status"] = "IN_PROGRESS"
            log["next_request_id"] = f"issues-page-{page + 1}"
        else:
            log["status"], log["next_request_id"] = "STOPPED_PAGINATION_CAP", None
    else:
        index = ORDER.index(request_id)
        log["status"], log["next_request_id"] = "IN_PROGRESS", ORDER[index + 1]
    atomic_json(root / REQUEST_LOG, log)
    return row


def validate_protocol(root: Path) -> dict:
    root = root.resolve()
    protocol, log, work = load(root / PROTOCOL), load(root / REQUEST_LOG), load(root / WORK)
    require([row["id"] for row in protocol["requests"]] == ORDER, "request order drift")
    require(protocol["transport"] == {
        "method": "GET", "authentication": "NONE", "timeout_seconds": 30,
        "max_response_bytes": 8000000,
        "allowed_hosts": ["api.github.com", "codeload.github.com"],
        "user_agent": "lean-assurance-lab-nanoda-readiness/1"}, "transport drift")
    require(log["request_cap"] == work["budget"]["read_only_upstream_requests"] == 6
            and work["budget"]["local_code_or_evidence_inspections"] == 6
            and all(work["budget"][name] == 0 for name in
                    ("builds", "checker_launches", "lean_proof_launches",
                     "new_scientific_byte_variants", "new_mutation_identities",
                     "external_writes")), "budget drift")
    return {"status": "PASS", "request_cap": 6,
            "conditional_pagination_slots": 2, "external_writes": 0}
