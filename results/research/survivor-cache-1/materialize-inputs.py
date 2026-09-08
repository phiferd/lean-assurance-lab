#!/usr/bin/env python3
"""Materialize the frozen local cache comparison without invoking a compiler."""
from __future__ import annotations

import json
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from lib.survivor_let_payload import bind, require  # noqa: E402

BASE = ROOT / "results/research/survivor-cache-1"
LOCK_SOURCE = ROOT / "results/research/alt-survivors-2026-09-08/source-lock.json"
LOCK = BASE / "source-lock.json"
HARNESS = BASE / "cache-contract-tests.rs"
OLD_RUNTIME = ROOT / "results/research/survivor-let-reuse-1/runtime-manifest.json"
REVISION = "6ae1f0cd962f081f6c423454c5da729d841236a7"
ROOTS = {
    "baseline": "external/survivor-cache-0001-baseline",
    "mutant": "external/survivor-cache-0001-mutant",
}
TARGETS = {
    "baseline": "external/survivor-cache-0001-baseline-target",
    "mutant": "external/survivor-cache-0001-mutant-target",
}
MANIFEST = ROOT / "config/survivor-cache-0001.json"


def write_once(path: Path, value: dict, *, pre_freeze: bool) -> None:
    encoded = json.dumps(value, indent=2, sort_keys=True) + "\n"
    if path.exists():
        if path.read_text(encoding="utf-8") != encoded:
            require(pre_freeze, "frozen output differs: " + str(path))
            path.write_text(encoded, encoding="utf-8")
    else:
        path.write_text(encoded, encoding="utf-8")


def main() -> None:
    pre_freeze = not MANIFEST.exists()
    require(HARNESS.is_file(), "missing reviewed harness")
    if LOCK.exists():
        require(LOCK.read_bytes() == LOCK_SOURCE.read_bytes(), "source lock differs")
    else:
        shutil.copyfile(LOCK_SOURCE, LOCK)
    source_lock = json.loads(LOCK.read_text(encoding="utf-8"))
    require(source_lock["revision"] == REVISION, "wrong source revision")
    spec = json.loads((ROOT / "mutations/nanoda-gen-3365809b3c41.json").read_text())
    require(spec["source_file"] == "src/tc.rs" and spec["source_span"] == "483"
            and spec["replace_occurrence"] == 0
            and spec["original"] == "flag == InferFlag::InferOnly"
            and spec["mutated"] == "(flag != InferFlag::InferOnly)", "wrong mutation")
    harness = HARNESS.read_bytes()
    old_source_path = BASE / "source-materialization.json"
    old_source = json.loads(old_source_path.read_text()) if old_source_path.exists() else None
    inventories: dict[str, list[dict]] = {}
    for profile, relative_root in ROOTS.items():
        destination = ROOT / relative_root
        rows = []
        for row in source_lock["files"]:
            original = ROOT / row["binding"]["path"]
            require(bind(ROOT, original) == row["binding"], "canonical source drift")
            data = original.read_bytes()
            if row["source_path"] == "src/tc.rs":
                lines = data.splitlines(keepends=True)
                require(lines[482].count(spec["original"].encode()) == 1, "mutation site drift")
                if profile == "mutant":
                    lines[482] = lines[482].replace(
                        spec["original"].encode(), spec["mutated"].encode(), 1)
                data = b"".join(lines) + harness
            target = destination / row["source_path"]
            if target.exists():
                if target.read_bytes() != data:
                    require(pre_freeze and old_source is not None,
                            "existing materialization differs: " + str(target))
                    previous = {item["path"]: item for item in old_source["files_after_patch"][profile]}
                    require(target.relative_to(ROOT).as_posix() in previous,
                            "unbound pre-freeze materialization: " + str(target))
                    require(bind(ROOT, target) == previous[target.relative_to(ROOT).as_posix()],
                            "pre-freeze materialization drift: " + str(target))
                    target.write_bytes(data)
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(data)
            rows.append(bind(ROOT, target))
        inventories[profile] = rows
    source = {
        "schema_version": 1,
        "item_id": "SURVIVOR-CACHE-1",
        "revision": REVISION,
        "source_roots": ROOTS,
        "patch": {
            "path": "src/tc.rs",
            "line": 483,
            "occurrence": 0,
            "original": spec["original"],
            "mutated": spec["mutated"],
        },
        "harness": {"path": str(HARNESS.relative_to(ROOT)), "sha256": bind(ROOT, HARNESS)["sha256"]},
        "files_after_patch": inventories,
        "limits": "The identical appended harness and the selected cache predicate are the only source changes. This supports an internal cache-contract comparison, not exported-input reachability.",
    }
    write_once(BASE / "source-materialization.json", source, pre_freeze=pre_freeze)

    predecessor = json.loads(OLD_RUNTIME.read_text(encoding="utf-8"))
    environments = {}
    cargo = Path(predecessor["tools"]["cargo"]["path"])
    for profile in ROOTS:
        environments[profile] = {
            "HOME": str(Path.home()),
            "CARGO_HOME": predecessor["environment"]["CARGO_HOME"],
            "CARGO_TARGET_DIR": str(ROOT / TARGETS[profile]),
            "RUSTC": str(cargo.parent / "rustc"),
            "CARGO_NET_OFFLINE": "true",
            "PATH": "/usr/bin:/bin:/usr/sbin:/sbin:" + str(cargo.parent),
            "RUST_BACKTRACE": "full",
        }
    runtime = {
        "schema_version": 1,
        "kind": "SURVIVOR_CACHE_RUNTIME_MANIFEST",
        "source": source,
        "environments": environments,
        "locked_packages": predecessor["locked_packages"],
        "registry_index": predecessor["registry_index"],
        "tools": predecessor["tools"],
        "reuse": {
            "path": str(OLD_RUNTIME.relative_to(ROOT)),
            "sha256": bind(ROOT, OLD_RUNTIME)["sha256"],
            "decision": "Reuse its exact offline Cargo package and tool identities; use distinct source and target roots.",
        },
    }
    write_once(BASE / "runtime-manifest.json", runtime, pre_freeze=pre_freeze)
    print(json.dumps({
        "source": bind(ROOT, BASE / "source-materialization.json"),
        "runtime": bind(ROOT, BASE / "runtime-manifest.json"),
        "profiles": {name: len(rows) for name, rows in inventories.items()},
    }, indent=2))


if __name__ == "__main__":
    main()
