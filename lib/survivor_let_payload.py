"""Inert provenance preparation for the fixed SURVIVOR-LET-REUSE payload.

This module copies and verifies local inputs only.  It never invokes Cargo,
Nanoda, a compiler, or the network.  The returned recipe is deliberately data
for the separately authorized runner, not a launch instruction.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "results/research/survivor-let-reuse-1"
PLANNING = "results/research/alt-survivors-2026-09-08"
SOURCE_ROOT = "external/survivor-let-reuse-0001-nanoda"
TARGET_ROOT = "external/survivor-let-reuse-0001-target"
CARGO_HOME = "external/survivor-let-reuse-0001-cargo-home"
RUST_BIN = Path("/opt/homebrew/Cellar/rust/1.98.0/bin")
REGISTRY = Path.home() / ".cargo/registry/src/index.crates.io-1949cf8c6b5b557f"
REGISTRY_HOME = Path.home() / ".cargo/registry"
REGISTRY_ID = "index.crates.io-1949cf8c6b5b557f"
REVISION = "6ae1f0cd962f081f6c423454c5da729d841236a7"
MUTANT = "nanoda-gen-9face4e6a6f7"


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def bind(root: Path, path: Path) -> dict:
    path = path.resolve()
    try:
        name = path.relative_to(root.resolve()).as_posix()
    except ValueError:
        name = str(path)
    return {"path": name, "bytes": path.stat().st_size,
            "sha256": sha(path)}


def require(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def atomic_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name("." + path.name + ".tmp")
    with temp.open("x", encoding="utf-8") as f:
        json.dump(value, f, indent=2, sort_keys=True)
        f.write("\n")
    os.replace(temp, path)


def copy_exact(source: Path, destination: Path) -> None:
    require(source.is_file() and not source.is_symlink(), "unsafe source: " + str(source))
    if destination.exists():
        require(destination.is_file() and not destination.is_symlink() and sha(destination) == sha(source),
                "existing materialization differs: " + str(destination))
        return
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_name("." + destination.name + ".tmp")
    require(not temporary.exists(), "temporary path exists: " + str(temporary))
    shutil.copyfile(source, temporary)
    require(sha(temporary) == sha(source), "copy changed: " + str(source))
    os.replace(temporary, destination)


def load(root: Path, name: str) -> dict:
    return json.loads((root / name).read_text(encoding="utf-8"))


def lock_packages(lock: Path) -> dict[tuple[str, str], str]:
    """Parse Cargo lock v4's package/checksum fields without requiring tomllib."""
    rows, current = {}, {}
    for raw in lock.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if line == "[[package]]":
            if current.get("source", "").startswith("registry+"):
                require(set(("name", "version", "checksum")) <= set(current), "incomplete registry lock package")
                rows[(current["name"], current["version"])] = current["checksum"]
            current = {}
        elif "=" in line and line.split("=", 1)[0].strip() in {"name", "version", "source", "checksum"}:
            key, value = line.split("=", 1)
            current[key.strip()] = json.loads(value.strip())
    if current.get("source", "").startswith("registry+"):
        require(set(("name", "version", "checksum")) <= set(current), "incomplete final registry lock package")
        rows[(current["name"], current["version"])] = current["checksum"]
    return rows


def tree_files(path: Path, runtime_links: bool = False) -> dict[str, str]:
    files = {}
    for child in sorted(path.rglob("*")):
        if child.is_symlink():
            require(runtime_links and child.resolve().is_file(), "unexpected symlink in input tree: " + str(child))
            files[child.relative_to(path).as_posix()] = 'symlink:' + str(child.resolve()) + ':' + sha(child)
        elif child.is_file():
            files[child.relative_to(path).as_posix()] = sha(child)
    return files


def tree_binding(root: Path, path: Path) -> dict:
    files = tree_files(path, runtime_links=str(path) == '/opt/homebrew/Cellar/rust/1.98.0/lib')
    digest = hashlib.sha256("".join(name + "\0" + value + "\n" for name, value in sorted(files.items())).encode()).hexdigest()
    try:
        name = path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        name = str(path.resolve())
    return {"path": name, "file_count": len(files), "tree_sha256": digest, "files": files}


def copy_tree(source: Path, destination: Path) -> None:
    require(source.is_dir() and not source.is_symlink(), "unsafe source tree: " + str(source))
    if destination.exists():
        require(destination.is_dir() and not destination.is_symlink() and tree_files(destination) == tree_files(source),
                "existing copied tree differs: " + str(destination))
        return
    shutil.copytree(source, destination, symlinks=False)
    require(tree_files(destination) == tree_files(source), "copied tree changed: " + str(source))


def git_readme(root: Path) -> bytes:
    donor = root / "external/ecosystem-triage-nanoda"
    value = subprocess.run(["git", "-C", str(donor), "show", f"{REVISION}:README.md"],
                           check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout
    require(value.startswith(b"# About\n"), "pinned README content is unexpected")
    return value


def materialize(root: Path) -> tuple[dict, dict]:
    root = Path(root).resolve()
    require(not (root / "config/survivor-let-reuse-0001.json").exists(), "materialization manifest already frozen")
    proposal = load(root, PLANNING + "/execution-proposal.json")
    source_lock = load(root, PLANNING + "/source-lock.json")
    spec = load(root, "mutations/" + MUTANT + ".json")
    require(proposal["selected_mutant"] == MUTANT and source_lock["revision"] == REVISION,
            "proposal/source revision mismatch")
    require(spec["source_file"] == "src/tc.rs" and spec["source_span"] == "649"
            and spec["original"] == "flag == Check" and spec["mutated"] == "!(flag == Check)"
            and spec["replace_occurrence"] == 1, "unexpected selected patch")
    base_config = load(root, "config/ecosystem-nanoda.json")
    config_rows = []
    for role, binding in (("control", proposal["control"]), ("candidate", proposal["candidate"])):
        input_path = root / binding["path"]
        require(input_path.is_file() and input_path.stat().st_size == binding["bytes"] and sha(input_path) == binding["sha256"],
                "reused input drift: " + binding["path"])
        value = dict(base_config)
        value.update({"use_stdin": False, "export_file_path": str(input_path), "print_axioms": False})
        destination_config = root / BASE / "configs" / (role + ".json")
        encoded = json.dumps(value, indent=2, sort_keys=True) + "\n"
        if destination_config.exists():
            require(destination_config.read_text() == encoded, "per-input config differs: " + role)
        else:
            destination_config.parent.mkdir(parents=True, exist_ok=True)
            destination_config.write_text(encoded, encoding="utf-8")
        config_rows.append({"role": role, "input": bind(root, input_path), "config": bind(root, destination_config)})
    destination = root / SOURCE_ROOT
    source_files = []
    tc_already_patched = False
    for row in source_lock["files"]:
        binding = row["binding"]
        source = root / binding["path"]
        require(source.is_file() and source.stat().st_size == binding["bytes"] and sha(source) == binding["sha256"],
                "source-lock input drift: " + binding["path"])
        target = destination / row["source_path"]
        if row["source_path"] == "src/tc.rs" and target.exists():
            candidate = source.read_text(encoding="utf-8").splitlines(keepends=True)
            candidate[648] = candidate[648].replace(spec["original"], spec["mutated"], 1)
            require(target.read_text(encoding="utf-8") == "".join(candidate),
                    "existing materialized tc.rs differs")
            tc_already_patched = True
        else:
            copy_exact(source, target)
        source_files.append(bind(root, target))
    tc = destination / "src/tc.rs"
    if not tc_already_patched:
        lines = tc.read_text(encoding="utf-8").splitlines(keepends=True)
        index = int(spec["source_span"]) - 1
        require(lines[index].count(spec["original"]) == 1, "selected source occurrence changed")
        lines[index] = lines[index].replace(spec["original"], spec["mutated"], 1)
        tc.write_text("".join(lines), encoding="utf-8")
    readme = destination / "README.md"
    readme_bytes = git_readme(root)
    if readme.exists():
        require(readme.read_bytes() == readme_bytes, "pinned README differs")
    else:
        readme.write_bytes(readme_bytes)
    readme_snapshot = root / BASE / "evidence" / "nanoda-README.md"
    if readme_snapshot.exists():
        require(readme_snapshot.read_bytes() == readme_bytes, "bound README snapshot differs")
    else:
        readme_snapshot.write_bytes(readme_bytes)
    source_files = [bind(root, destination / row["source_path"]) for row in source_lock["files"]]
    source_manifest = {"schema_version": 1, "kind": "SURVIVOR_LET_SOURCE_MATERIALIZATION",
        "proposal": bind(root, root / (PLANNING + "/execution-proposal.json")),
        "source_lock": bind(root, root / (PLANNING + "/source-lock.json")),
        "mutation_spec": bind(root, root / ("mutations/" + MUTANT + ".json")),
        "revision": REVISION, "source_root": SOURCE_ROOT, "files_after_patch": source_files,
        "patch": {"path": "src/tc.rs", "line": 649, "occurrence": 1,
                  "original": spec["original"], "mutated": spec["mutated"]},
        "readme": bind(root, readme), "readme_snapshot": bind(root, readme_snapshot),
        "materialized_tc": bind(root, tc), "configs": config_rows}
    # Persist source provenance before the separately required offline payload
    # check, so a missing cached package is a durable, non-scientific blocker.
    atomic_json(root / BASE / "source-materialization.json", source_manifest)

    prior_runtime = root / BASE / "runtime-manifest.json"
    if prior_runtime.exists() and json.loads(prior_runtime.read_text()).get("status") == "BLOCKED_MISSING_OFFLINE_PAYLOAD":
        os.replace(prior_runtime, root / BASE / "runtime-manifest-preflight-v1.json")
    packages = lock_packages(destination / "Cargo.lock")
    isolated_registry = root / CARGO_HOME / "registry"
    copy_tree(REGISTRY_HOME / "index" / REGISTRY_ID, isolated_registry / "index" / REGISTRY_ID)
    package_rows = []
    for (name, version), checksum in sorted(packages.items()):
        source = REGISTRY / f"{name}-{version}"
        archive = REGISTRY_HOME / "cache" / REGISTRY_ID / (source.name + ".crate")
        row = {"name": name, "version": version, "lock_checksum": checksum, "source": None, "archive": None}
        if source.is_dir():
            target = isolated_registry / "src" / REGISTRY_ID / source.name
            copy_tree(source, target); row["source"] = tree_binding(root, target)
        if archive.is_file():
            target = isolated_registry / "cache" / REGISTRY_ID / archive.name
            copy_exact(archive, target); row["archive"] = bind(root, target)
            require(row["archive"]["sha256"] == checksum, "cached crate checksum disagrees with Cargo.lock: " + archive.name)
        package_rows.append(row)
    runtime = runtime_manifest(root, source_manifest, package_rows,
                               tree_binding(root, isolated_registry / "index" / REGISTRY_ID))
    atomic_json(root / BASE / "runtime-manifest.json", runtime)
    return source_manifest, runtime


def runtime_manifest(root: Path, source: dict, package_rows: list[dict], index: dict) -> dict:
    cargo, rustc, cc = RUST_BIN / "cargo", RUST_BIN / "rustc", Path("/usr/bin/cc")
    for tool in (cargo, rustc, cc):
        require(tool.is_file() and not tool.is_symlink(), "missing exact tool: " + str(tool))
    rustlib = Path("/opt/homebrew/Cellar/rust/1.98.0/lib")
    require(rustlib.is_dir(), "missing Rust lib tree")
    tools = {"cargo": bind(root, cargo), "rustc": bind(root, rustc), "cc": bind(root, cc),
             "rustlib": tree_binding(root, rustlib)}
    return {"schema_version": 1, "kind": "SURVIVOR_LET_RUNTIME_MANIFEST", "source": source,
            "registry_index": index, "locked_packages": package_rows,
            "tools": tools, "environment": {"HOME": str(Path.home()), "CARGO_HOME": str(root / CARGO_HOME),
            "CARGO_TARGET_DIR": str(root / TARGET_ROOT), "RUSTC": str(cargo.parent / "rustc"),
            "CARGO_NET_OFFLINE": "true", "PATH": "/usr/bin:/bin:/usr/sbin:/sbin:" + str(cargo.parent),
            "RUST_BACKTRACE": "full"}}


def verify(root: Path, require_commit: bool = False) -> dict:
    root = Path(root).resolve()
    source = load(root, BASE + "/source-materialization.json")
    runtime = load(root, BASE + "/runtime-manifest.json")
    require(runtime['source'] == source, 'source/runtime binding mismatch')
    require(runtime['environment'] == {"HOME": str(Path.home()), "CARGO_HOME": str(root / CARGO_HOME),
            "CARGO_TARGET_DIR": str(root / TARGET_ROOT), "RUSTC": str(RUST_BIN / "rustc"),
            "CARGO_NET_OFFLINE": "true", "PATH": "/usr/bin:/bin:/usr/sbin:/sbin:" + str(RUST_BIN),
            "RUST_BACKTRACE": "full"}, 'build environment changed')
    for ancestor in [root / SOURCE_ROOT, *(root / SOURCE_ROOT).parents, root / CARGO_HOME]:
        for name in ('config', 'config.toml'):
            location = ancestor / (name if ancestor == root / CARGO_HOME else '.cargo/' + name)
            require(not location.exists(), 'unexpected Cargo configuration: ' + str(location))
    require(source["revision"] == REVISION and source["source_root"] == SOURCE_ROOT and source["patch"]["mutated"] == "!(flag == Check)", "source manifest differs")
    proposal = load(root, PLANNING + '/execution-proposal.json')
    history = load(root, proposal['historical_official_result']['path'])
    require(history['baseline_binary'] == proposal['baseline'], 'historical baseline association differs')
    require(bind(root, root / proposal['baseline']['path']) == proposal['baseline'], 'baseline binary changed')
    lock = load(root, PLANNING + "/source-lock.json")
    require(history['source_before_sha256'] == next(row['binding']['sha256'] for row in lock['files']
                                                   if row['source_path'] == 'src/tc.rs'), 'baseline source association differs')
    require(len(lock["files"]) == len(source["files_after_patch"]), "source file inventory drift")
    expected_paths = {row["source_path"] for row in lock["files"]} | {"README.md"}
    actual_paths = {p.relative_to(root / SOURCE_ROOT).as_posix() for p in (root / SOURCE_ROOT).rglob("*") if p.is_file()}
    require(actual_paths == expected_paths, "unexpected or missing materialized source file")
    for expected in lock["files"]:
        original = root / expected["binding"]["path"]
        require(bind(root, original) == expected["binding"], "pinned donor changed")
        materialized = root / SOURCE_ROOT / expected["source_path"]
        if expected["source_path"] == "src/tc.rs":
            lines = original.read_text().splitlines(keepends=True)
            require(lines[648].count("flag == Check") == 1, "bound tc site changed")
            lines[648] = lines[648].replace("flag == Check", "!(flag == Check)", 1)
            require(materialized.read_text() == "".join(lines), "materialized tc patch differs")
        else:
            expected_materialized = {"path": materialized.relative_to(root).as_posix(),
                                     "bytes": expected["binding"]["bytes"], "sha256": expected["binding"]["sha256"]}
            require(bind(root, materialized) == expected_materialized, "materialized source drift: " + expected["source_path"])
    tc = root / SOURCE_ROOT / "src/tc.rs"
    line = tc.read_text().splitlines()[648]
    require(line.count("!(flag == Check)") == 1 and "flag == Check" not in line.replace("!(flag == Check)", ""), "selected patch drift")
    require(bind(root, root / source["readme"]["path"]) == source["readme"], "materialized README drift")
    require(bind(root, root / source["readme_snapshot"]["path"]) == source["readme_snapshot"], "README snapshot drift")
    index = root / runtime["registry_index"]["path"]
    require(tree_binding(root, index) == runtime["registry_index"], "registry index drift")
    locked = lock_packages(root / SOURCE_ROOT / 'Cargo.lock')
    require({(p['name'], p['version']): p['lock_checksum'] for p in runtime['locked_packages']} == locked,
            'runtime package identities changed')
    for package in runtime["locked_packages"]:
        for kind in ("source", "archive"):
            receipt = package[kind]
            if receipt is None: continue
            location = root / receipt["path"]
            actual = tree_binding(root, location) if kind == "source" else bind(root, location)
            require(actual == receipt, "runtime payload drift: " + package["name"])
    for name, row in runtime["tools"].items():
        if name == 'rustlib':
            require(tree_binding(root, Path(row['path'])) == row, 'Rust runtime library drift')
        else:
            require(bind(root, root / row["path"]) == row, "tool identity drift")
    if require_commit:
        for name in (BASE + "/source-materialization.json", BASE + "/runtime-manifest.json", BASE + "/configs/control.json", BASE + "/configs/candidate.json", BASE + "/evidence/nanoda-README.md"):
            result = subprocess.run(["git", "show", "HEAD:" + name], cwd=root, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
            require(result.returncode == 0 and (root / name).read_bytes() == result.stdout, "HEAD binding missing/different: " + name)
    return {"build": {"argv": [str(RUST_BIN / "cargo"), "build", "--release", "--locked", "--offline"],
             "cwd": str(root / SOURCE_ROOT), "env": runtime["environment"], "output": str(root / TARGET_ROOT / "release/nanoda_bin")}, "source": source, "runtime": runtime}
