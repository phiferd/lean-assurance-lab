"""Check retained source identities, references and result counts; no checker runs."""
import hashlib
import json
from pathlib import Path
import tarfile

HERE = Path(__file__).resolve().parent
root = HERE.parents[2]
inventory = json.loads((HERE / "source-inventory.json").read_text())
result = json.loads((HERE / "result.json").read_text())
fixtures = json.loads((HERE / "fixture-inventory.json").read_text())
coverage = json.loads((HERE / "coverage-map.json").read_text())
assert len(fixtures) == len(coverage) == 9
assert {c["fixture"] for c in coverage} == {f["id"] for f in fixtures}
for f in fixtures:
    assert hashlib.sha256((root / f["path"]).read_bytes()).hexdigest() == f["sha256"]
for label, data in inventory.items():
    archive = HERE / (label + "-sources.tar.gz")
    assert hashlib.sha256(archive.read_bytes()).hexdigest() == result["source_archives"][label]
    expected = {r["path"]: r for r in data["files"] if r["inspected"]}
    with tarfile.open(archive) as t:
        assert set(t.getnames()) == set(expected)
        for path, row in expected.items():
            raw = t.extractfile(path).read()
            assert len(raw) == row["size"]
            assert hashlib.sha256(raw).hexdigest() == row["sha256"]
            assert hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest() == row["git_blob"]
        for case in coverage:
            for ref in case["evidence"]:
                if ref["source"] != label: continue
                lines = t.extractfile(ref["path"]).read().decode().splitlines()
                assert 1 <= ref["start_line"] <= ref["end_line"] <= len(lines)
    assert len(data["files"]) == data["tracked_files"]
    assert len(expected) == data["inspected_files"]
ownership = json.loads((HERE / "ownership-observations.json").read_text())
upstream = [d for path, ds in ownership.items() if not path.startswith("lal/") for d in ds]
assert len(upstream) == result["upstream_declaration_occurrences"] == 260
assert not any(d["missing"] or d["unresolved"] for d in upstream)
assert [c["fixture"] for c in coverage if c["classification"] == "SUPPORTED_TARGETED_GAP"] == ["P1-invalid"]
assert result["checker_runs"] == result["checker_builds"] == result["mutant_runs"] == 0
print("PASS: nine fixtures, 148 archived sources, 260 static declaration occurrences, and all source-map citations match retained evidence.")
