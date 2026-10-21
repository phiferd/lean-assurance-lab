"""Prepare one data-only candidate in a new detached local Arena checkout."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
revision = (HERE / "target-revision.txt").read_text().strip()
workspace = Path(tempfile.mkdtemp(prefix="lal-arena-universe-guard-"))
subprocess.run(["git", "clone", "--shared", "--no-checkout", str(ROOT / "external/lean-kernel-arena"), str(workspace)], check=True)
subprocess.run(["git", "-C", str(workspace), "checkout", "--detach", revision], check=True)
relative = Path("tests/other/undeclared-universe-parameter")
candidate = ROOT / "explorations/runs/EXPLORE-SYMBOLIC-UNIVERSE-REJECTION-1/inputs/P1-invalid.ndjson"
control = ROOT / "explorations/runs/EXPLORE-SYMBOLIC-UNIVERSE-1/inputs/P1.ndjson"
payload = candidate.read_bytes()
dest = workspace / relative.with_suffix(".ndjson")
assert not dest.exists()
dest.write_bytes(payload)
metadata = """description: |
  A definition uses universe parameter `u` in its type and value but omits it
  from its `levelParams` list. The value is `Sort u`, its declared type is
  `Sort (u + 1)`, and `levelParams` is empty, so a checker must reject the
  undeclared parameter. Adding `u` to the list makes the declaration valid.

  This checks parameter membership, separately from duplicate parameters or
  the number of universe arguments supplied to a constant.
file: tests/other/undeclared-universe-parameter.ndjson
outcome: reject
"""
(workspace / relative.with_suffix(".yaml")).write_text(metadata)
subprocess.run(["git", "-C", str(workspace), "add", "--intent-to-add", str(relative.with_suffix(".ndjson")), str(relative.with_suffix(".yaml"))], check=True)
patch = subprocess.check_output(["git", "-C", str(workspace), "diff", "--full-index", "--", str(relative.with_suffix(".ndjson")), str(relative.with_suffix(".yaml"))])
(HERE / "candidate.patch").write_bytes(patch)
subprocess.run(["git", "-C", str(workspace), "diff", "--check"], check=True)
inputs = HERE / "inputs"
inputs.mkdir()
for name, raw in (("candidate", payload), ("control", control.read_bytes())):
    (inputs / (name + ".ndjson")).write_bytes(raw)
    (inputs / (name + ".json")).write_text(json.dumps(dict(export_file_path="/arena-universe-guard-in/"+name+".ndjson",permitted_axioms=[],unpermitted_axiom_hard_error=True,num_threads=1,print_success_message=True,pp_declars=["LAL_P1"],pp_to_stdout=True),indent=2)+"\n")
(HERE / "candidate.yaml").write_text(metadata)
(HERE / "workspace-path.txt").write_text(str(workspace)+"\n")
(HERE / "cases.json").write_text(json.dumps([
    dict(id="candidate",expected="REJECT",params=[],type="(sort (succ u))",value="(sort u)",declaration="LAL_P1",sha256=hashlib.sha256(payload).hexdigest(),reason="Used parameter u is missing from levelParams; source parameter-membership guard must reject."),
    dict(id="control",expected="ACCEPT",params=["u"],type="(sort (succ u))",value="(sort u)",declaration="LAL_P1",sha256=hashlib.sha256(control.read_bytes()).hexdigest(),reason="The same definition owns u; Sort u has type Sort(succ u).")],indent=2)+"\n")
print("Prepared detached local candidate at",workspace,"against",revision)
print("Two-file patch; candidate/control bytes reused unchanged. No checker executed.")
