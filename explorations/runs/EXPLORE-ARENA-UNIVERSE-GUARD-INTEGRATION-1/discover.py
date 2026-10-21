"""Use the exact target's loader and static-file path; build no Lean code."""
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys

HERE = Path(__file__).resolve().parent
workspace = Path((HERE / "workspace-path.txt").read_text().strip())
spec = importlib.util.spec_from_file_location("arena_data_integration", workspace / "lka.py")
lka = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lka)
tests = lka.load_test_descriptions()
matches = [t for t in tests if t["name"] == "other/undeclared-universe-parameter"]
assert len(matches) == 1 and matches[0]["outcome"] == "reject"
out = workspace / "_build/tests"
assert lka.create_test(matches[0], out)
produced = out / "other/undeclared-universe-parameter.ndjson"
stats = json.loads((out / "other/undeclared-universe-parameter.stats.json").read_text())
expected = json.loads((HERE / "cases.json").read_text())[0]["sha256"]
assert hashlib.sha256(produced.read_bytes()).hexdigest() == expected
assert stats["sha256"] == expected and stats["outcome"] == "reject"
saved = HERE / "discovery"
saved.mkdir()
shutil.copyfile(produced, saved / "candidate.ndjson")
(saved / "stats.json").write_text(json.dumps(stats, indent=2)+"\n")
(saved / "result.json").write_text(json.dumps(dict(schema="PASS",discovery="PASS",matched_tests=1,total_loaded_tests=len(tests),static_file_copy="PASS",candidate_sha256=expected,target_revision=(HERE/"target-revision.txt").read_text().strip()),indent=2)+"\n")
print("PASS: actual target metadata loader, name discovery and static-file copy preserve the exact candidate.")
