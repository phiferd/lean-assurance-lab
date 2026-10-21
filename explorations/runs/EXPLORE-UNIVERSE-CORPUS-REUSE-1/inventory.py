"""Inventory pinned Git blobs and retain source-only comparison evidence."""
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SOURCES = {
    "nanoda": ("external/comparator-screen-nanoda", "3a2407216ee84a75f9e1aead6803d0578be06ae7"),
    "arena": ("external/lean-kernel-arena", "37f7525b732808a49b746dc6999d53c3717db124"),
}
TERMS = re.compile(r"universe|levelParam|uparam|imax|\bmax\b|Sort|should_panic|#\[test\]|^--|expect|reject", re.I)

def git(repo, *args):
    return subprocess.check_output(["git", "-C", str(ROOT / repo), *args])

def selected(label, path):
    if label == "nanoda":
        return path.startswith(("src/", "test_resources/")) or path in ("README.md", "Cargo.toml", "LICENSE")
    return ((path.startswith(("tests/", "tutorial/")) and path.endswith((".lean", ".ndjson", ".yaml", ".json", ".md", "lean-toolchain")))
        or path in ("README.md", "lka.py", "schemas/test.json", "tests/lean-toolchain", ".github/workflows/build-and-deploy.yml"))

all_inventory = {}
hits = []
declarations = []
fixture_bytes = {}
fixtures = []
for filename in ("EXPLORE-SYMBOLIC-UNIVERSE-1", "EXPLORE-SYMBOLIC-UNIVERSE-REJECTION-1"):
    for case in json.loads((HERE.parent / filename / "cases.json").read_text()):
        raw = (ROOT / case["path"]).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == case["sha256"]
        if case["sha256"] in fixture_bytes: continue
        fixture_bytes[case["sha256"]] = raw
        fixtures.append(case)
assert len(fixtures) == 9
(HERE / "fixture-inventory.json").write_text(json.dumps(fixtures, indent=2) + "\n")
for label, (repo, revision) in SOURCES.items():
    rows = []
    with tarfile.open(HERE / (label + "-sources.tar.gz"), "w:gz") as archive:
        for record in git(repo, "ls-tree", "-rlz", revision).split(b"\0"):
            if not record: continue
            meta, name = record.split(b"\t", 1)
            mode, kind, blob, size = meta.decode().split()
            path = name.decode()
            row = dict(path=path, git_blob=blob, size=int(size), inspected=selected(label, path))
            if row["inspected"]:
                raw = git(repo, "show", revision + ":" + path)
                assert len(raw) == int(size)
                row["sha256"] = hashlib.sha256(raw).hexdigest()
                row["literal_fixture_matches"] = [c["id"] for c in fixtures if fixture_bytes[c["sha256"]] == raw]
                info = tarfile.TarInfo(path)
                info.size = len(raw)
                archive.addfile(info, io.BytesIO(raw))
                text = raw.decode("utf-8")
                for i, line in enumerate(text.splitlines(), 1):
                    if TERMS.search(line): hits.append(dict(source=label, path=path, line=i, text=line))
                    if re.search(r"fn\s+test|#\[test\]|^test_case|^def test|^\s*test\s", line):
                        declarations.append(dict(source=label, path=path, line=i, text=line))
            else: row["exclusion"] = "Non-test infrastructure, binary or generated artifact; complete path inventory retained."
            rows.append(row)
    all_inventory[label] = dict(revision=revision,
        tree=git(repo, "rev-parse", revision + "^{tree}").decode().strip(),
        files=rows, tracked_files=len(rows), inspected_files=sum(r["inspected"] for r in rows),
        inspected_bytes=sum(r["size"] for r in rows if r["inspected"]))
(HERE / "source-inventory.json").write_text(json.dumps(all_inventory, indent=2) + "\n")
(HERE / "search-leads.json").write_text(json.dumps(hits, indent=2) + "\n")
(HERE / "test-declaration-leads.json").write_text(json.dumps(declarations, indent=2) + "\n")
print(json.dumps({k:{f:v[f] for f in ("tracked_files", "inspected_files", "inspected_bytes")} for k,v in all_inventory.items()}, indent=2))
print("Search leads are not coverage conclusions; semantic comparison remains a separate recorded judgment.")
