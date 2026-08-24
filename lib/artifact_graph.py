"""Content-addressed artifact graph evaluation for Lean Assurance Lab."""

from __future__ import annotations

import fnmatch
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


SHA256_LENGTH = 64
VALID_TYPES = {
    "repository",
    "validator",
    "toolchain",
    "configuration",
    "script",
    "corpus",
    "mutation-model",
    "mutation-spec",
    "coverage",
    "run",
    "comparison",
    "witness",
    "classification",
    "report",
}
VALID_LIFECYCLES = {"current", "historical", "superseded"}
REQUIRED_PROVENANCE = {
    "repository_revision",
    "arena_revision",
    "validator_source_sha256",
    "lean_versions",
    "mutation_specs_sha256",
    "corpus_inventory_sha256",
    "scripts_sha256",
    "configurations_sha256",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_file_set(root: Path, includes: list[str], excludes: list[str] | None = None) -> str | None:
    excludes = excludes or []
    paths: set[Path] = set()
    for pattern in includes:
        paths.update(path for path in root.glob(pattern) if path.is_file())
    paths = {
        path
        for path in paths
        if not any(fnmatch.fnmatch(str(path.relative_to(root)), pattern) for pattern in excludes)
    }
    if not paths:
        return None
    digest = hashlib.sha256()
    for path in sorted(paths, key=lambda item: str(item.relative_to(root))):
        digest.update(str(path.relative_to(root)).encode())
        digest.update(b"\0")
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        digest.update(b"\0")
    return digest.hexdigest()


def composite_digest(dependencies: list[dict[str, str]], observed: dict[str, str | None]) -> str | None:
    if any(observed.get(dependency["id"]) is None for dependency in dependencies):
        return None
    payload = [
        {"id": dependency["id"], "sha256": observed[dependency["id"]]}
        for dependency in dependencies
    ]
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def locator_digest(root: Path, locator: dict[str, Any]) -> tuple[str | None, str | None]:
    kind = locator["kind"]
    if kind == "file":
        path = root / locator["path"]
        return (sha256_file(path), None) if path.is_file() else (None, None)
    if kind == "file_set":
        base = root / locator["root"]
        if not base.is_dir():
            return None, None
        return sha256_file_set(base, locator["include"], locator.get("exclude")), None
    if kind == "git_revision":
        path = root / locator["path"]
        if not path.is_dir():
            return None, None
        proc = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=path,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        )
        if proc.returncode != 0:
            return None, None
        revision = proc.stdout.strip()
        return hashlib.sha256(revision.encode()).hexdigest(), revision
    raise ValueError(f"unsupported locator kind: {kind}")


def validate_graph(graph: dict[str, Any]) -> None:
    if graph.get("schema_version") != 1:
        raise ValueError("artifact graph schema_version must be 1")
    nodes = graph.get("nodes")
    if not isinstance(nodes, list):
        raise ValueError("artifact graph nodes must be a list")
    ids = [node.get("id") for node in nodes]
    if len(ids) != len(set(ids)):
        raise ValueError("artifact graph contains duplicate node ids")
    missing_provenance = REQUIRED_PROVENANCE - set(graph.get("provenance", {}))
    if missing_provenance:
        raise ValueError(f"artifact graph missing provenance: {sorted(missing_provenance)}")
    by_id = {node["id"]: node for node in nodes}
    for node in nodes:
        if node.get("artifact_type") not in VALID_TYPES:
            raise ValueError(f"{node['id']}: invalid artifact_type")
        if node.get("lifecycle") not in VALID_LIFECYCLES:
            raise ValueError(f"{node['id']}: invalid lifecycle")
        expected = node.get("expected_sha256", "")
        if len(expected) != SHA256_LENGTH or any(char not in "0123456789abcdef" for char in expected):
            raise ValueError(f"{node['id']}: invalid expected_sha256")
        locator = node.get("locator")
        if locator:
            kind = locator.get("kind")
            if kind == "file" and not locator.get("path"):
                raise ValueError(f"{node['id']}: file locator needs path")
            if kind == "file_set" and (not locator.get("root") or not locator.get("include")):
                raise ValueError(f"{node['id']}: file_set locator needs root and include")
            if kind == "git_revision" and not locator.get("path"):
                raise ValueError(f"{node['id']}: git_revision locator needs path")
            if kind not in {"file", "file_set", "git_revision"}:
                raise ValueError(f"{node['id']}: invalid locator kind")
        for dependency in node.get("dependencies", []):
            if dependency["id"] not in by_id:
                raise ValueError(f"{node['id']}: unknown dependency {dependency['id']}")
            if dependency["expected_sha256"] != by_id[dependency["id"]]["expected_sha256"]:
                raise ValueError(
                    f"{node['id']}: dependency digest does not match attested node "
                    f"{dependency['id']}"
                )


def evaluate_graph(
    graph: dict[str, Any],
    root: Path,
    overrides: dict[str, str | None] | None = None,
) -> dict[str, dict[str, Any]]:
    validate_graph(graph)
    overrides = overrides or {}
    nodes = {node["id"]: node for node in graph["nodes"]}
    observed: dict[str, str | None] = {}
    details: dict[str, str | None] = {}
    visiting: set[str] = set()

    def observe(node_id: str) -> str | None:
        if node_id in observed:
            return observed[node_id]
        if node_id in visiting:
            raise ValueError(f"artifact dependency cycle at {node_id}")
        visiting.add(node_id)
        node = nodes[node_id]
        if node_id in overrides:
            value = overrides[node_id]
            detail = "simulated-change"
        elif "locator" in node:
            value, detail = locator_digest(root, node["locator"])
        else:
            dependency_values = {dependency["id"]: observe(dependency["id"]) for dependency in node["dependencies"]}
            value = composite_digest(node["dependencies"], dependency_values)
            detail = None
        visiting.remove(node_id)
        observed[node_id] = value
        details[node_id] = detail
        return value

    for node_id in nodes:
        observe(node_id)

    effective: dict[str, dict[str, Any]] = {}

    def classify(node_id: str) -> dict[str, Any]:
        if node_id in effective:
            return effective[node_id]
        node = nodes[node_id]
        reasons = []
        value = observed[node_id]
        if value is None:
            base_state = "MISSING"
            reasons.append("ARTIFACT_MISSING")
        elif value != node["expected_sha256"]:
            base_state = "STALE"
            reasons.append("CONTENT_DIGEST_CHANGED")
        else:
            base_state = "CURRENT"
        for dependency in node["dependencies"]:
            dependency_status = classify(dependency["id"])
            if dependency_status["effective_state"] == "MISSING":
                base_state = "MISSING"
                reasons.append(f"MISSING_DEPENDENCY:{dependency['id']}")
            elif dependency_status["effective_state"] != "CURRENT" and base_state != "MISSING":
                base_state = "STALE"
                reasons.append(f"STALE_DEPENDENCY:{dependency['id']}")
            if observed[dependency["id"]] != dependency["expected_sha256"]:
                reasons.append(f"DEPENDENCY_DIGEST_MISMATCH:{dependency['id']}")
        lifecycle = node["lifecycle"]
        display_state = base_state
        if lifecycle == "historical":
            display_state = "HISTORICAL" if base_state == "CURRENT" else f"HISTORICAL_{base_state}"
        elif lifecycle == "superseded":
            display_state = "SUPERSEDED" if base_state == "CURRENT" else f"SUPERSEDED_{base_state}"
        status = {
            "id": node_id,
            "artifact_type": node["artifact_type"],
            "lifecycle": lifecycle,
            "required_for_current_claims": node["required_for_current_claims"],
            "state": display_state,
            "effective_state": base_state,
            "expected_sha256": node["expected_sha256"],
            "observed_sha256": value,
            "observed_detail": details[node_id],
            "reasons": sorted(set(reasons)),
        }
        effective[node_id] = status
        return status

    return {node_id: classify(node_id) for node_id in nodes}


def load_graph(path: Path) -> dict[str, Any]:
    graph = json.loads(path.read_text(encoding="utf-8"))
    validate_graph(graph)
    return graph


def require_current(
    graph: dict[str, Any],
    root: Path,
    node_ids: list[str] | None = None,
    dependencies_only: bool = False,
) -> None:
    statuses = evaluate_graph(graph, root)
    nodes = {node["id"]: node for node in graph["nodes"]}
    selected = node_ids or [
        node_id for node_id, node in nodes.items() if node["required_for_current_claims"]
    ]
    if dependencies_only:
        selected = [dependency["id"] for node_id in selected for dependency in nodes[node_id]["dependencies"]]
    failures = [
        f"{node_id}={statuses[node_id]['state']}"
        for node_id in sorted(set(selected))
        if statuses[node_id]["effective_state"] != "CURRENT"
    ]
    if failures:
        raise RuntimeError("artifact gate failed: " + ", ".join(failures))
