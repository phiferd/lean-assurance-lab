import fcntl, hashlib, importlib.machinery, importlib.util, json, os, platform, tempfile, time, unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
loader=importlib.machinery.SourceFileLoader("authorized_campaign",str(ROOT/"scripts"/"run-campaign")); spec=importlib.util.spec_from_loader(loader.name,loader); runner=importlib.util.module_from_spec(spec); loader.exec_module(runner)
ml=importlib.machinery.SourceFileLoader("materializer",str(ROOT/"scripts"/"materialize-run-inputs")); ms=importlib.util.spec_from_loader(ml.name,ml); materializer=importlib.util.module_from_spec(ms); ml.exec_module(materializer)
from lib.authorized_runs import sha256_file, validate_manifest

class AuthorizedRuns(unittest.TestCase):
 def setUp(self):
  self.t=tempfile.TemporaryDirectory(); self.root=Path(self.t.name); (self.root/"docs").mkdir(); self.plan=self.root/"docs"/"plan.md"; self.plan.write_text("plan")
  (self.root/"docs"/"RESEARCH_STATUS.md").write_text("## Research Frontier\n### Active\n1. `F-ECOSYSTEM-CLOSURE-AND-AUTONOMY`: active\n### Waiting\n")
  exe=self.root/"scripts"/"ok"; exe.parent.mkdir(); exe.write_text("#!/bin/sh\nexit 0\n"); exe.chmod(0o755); self.exe=exe
  self.old=runner.ROOT; self.materializer_old=materializer.ROOT; runner.ROOT=self.root; materializer.ROOT=self.root
 def tearDown(self): runner.ROOT=self.old; materializer.ROOT=self.materializer_old; self.t.cleanup()
 def manifest(self, timeout=1, budget=3):
  return {"schema_version":1,"run_id":"fixture","frontier_id":"F-ECOSYSTEM-CLOSURE-AND-AUTONOMY","governing_plan":{"path":"docs/plan.md","sha256":sha256_file(self.plan)},"inputs":[{"path":"scripts/ok","sha256":sha256_file(self.exe),"bytes":self.exe.stat().st_size}],"platform":{"system":platform.system(),"machine":platform.machine()},"phases":[{"id":"one","command":["scripts/ok"],"timeout_seconds":timeout}],"total_budget_seconds":budget,"max_attempts":2,"completion_predicate":"fixture succeeds","external_actions":False}
 def write(self,m=None):
  p=self.root/"authorization.json"; p.write_text(json.dumps(m or self.manifest())); return p
 def test_changed_input_and_frontier_refused(self):
  p=self.write(); self.assertTrue(validate_manifest(json.loads(p.read_text()),self.root,p))
  self.exe.write_text("#!/bin/sh\nexit 1\n"); self.assertRaises(ValueError,validate_manifest,json.loads(p.read_text()),self.root,p)
  self.exe.write_text("#!/bin/sh\nexit 0\n"); m=self.manifest(); self.root.joinpath("docs/RESEARCH_STATUS.md").write_text("### Active\n1. `F-OTHER`: active\n"); self.assertRaises(ValueError,validate_manifest,m,self.root,p)
 def test_complete_resume_and_stale_running_charge(self):
  p=self.write(); self.assertEqual(runner.authorized(p),0); state=json.loads((self.root/"results/authorized-runs/fixture.json").read_text()); self.assertEqual(state["status"],"COMPLETE"); self.assertEqual(state["attempt_count"],1); self.assertEqual(runner.authorized(p, True),0)
  state["status"]="RUNNING"; state["running_pgid"]=999999; state["phases"]["one"]["status"]="RUNNING"; state["phases"]["one"]["reserved_seconds"]=1; self.root.joinpath("results/authorized-runs/fixture.json").write_text(json.dumps(state)); self.assertEqual(runner.authorized(p, True),0); state=json.loads((self.root/"results/authorized-runs/fixture.json").read_text()); self.assertGreaterEqual(state["elapsed_seconds"],1)
 def test_lock_excludes_and_stubborn_group_is_killed(self):
  p=self.write(); lock=self.root/"results/authorized-runs/fixture.lock"; lock.parent.mkdir(parents=True); handle=lock.open("a+"); fcntl.flock(handle.fileno(),fcntl.LOCK_EX|fcntl.LOCK_NB)
  self.assertRaises(ValueError,runner.authorized,p)
  handle.close(); self.assertEqual(runner.authorized(p),0)
  stubborn=self.root/"scripts"/"stubborn"; stubborn.write_text("#!/bin/sh\ntrap '' TERM\nwhile :; do sleep 1; done\n"); stubborn.chmod(0o755)
  m=self.manifest(timeout=.1,budget=.1); m["inputs"].append({"path":"scripts/stubborn","sha256":sha256_file(stubborn),"bytes":stubborn.stat().st_size}); m["run_id"]="stubborn"; m["phases"][0]["command"]=["scripts/stubborn"]; p=self.write(m); self.assertEqual(runner.authorized(p),1); state=json.loads((self.root/"results/authorized-runs/stubborn.json").read_text()); self.assertTrue(state["phases"]["one"]["attempts"][0]["timed_out"])
 def test_materialization_refuses_existing_mismatch(self):
  donor=self.root/"donor"; (donor/"scripts").mkdir(parents=True); shutil_target=donor/"scripts"/"ok"; shutil_target.write_bytes(self.exe.read_bytes()); shutil_target.chmod(0o755)
  p=self.write(); self.exe.unlink(); import sys
  old=sys.argv; sys.argv=["materialize-run-inputs","--authorization",str(p),"--source-root",str(donor)]
  try: self.assertEqual(materializer.main(),0)
  finally: sys.argv=old
  self.exe.write_text("bad"); sys.argv=["materialize-run-inputs","--authorization",str(p),"--source-root",str(donor)]
  try: self.assertEqual(materializer.main(),2)
  finally: sys.argv=old
 def test_unknown_or_live_orphan_refuses_resume(self):
  p=self.write(); self.assertEqual(runner.authorized(p),0)
  state=json.loads((self.root/"results/authorized-runs/fixture.json").read_text())
  state["phases"]["one"]["status"]="RUNNING"; state["phases"]["one"]["reserved_seconds"]=1
  self.root.joinpath("results/authorized-runs/fixture.json").write_text(json.dumps(state))
  self.assertRaises(ValueError,runner.authorized,p,True)
  state["running_pgid"]=os.getpgrp(); self.root.joinpath("results/authorized-runs/fixture.json").write_text(json.dumps(state))
  self.assertRaises(ValueError,runner.authorized,p,True)
if __name__=="__main__": unittest.main()
