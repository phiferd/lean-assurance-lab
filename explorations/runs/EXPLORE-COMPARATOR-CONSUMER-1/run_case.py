#!/usr/bin/python3
"""Run one declared scenario and retain the consumer's real streams."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

label=sys.argv[1]
out=Path('/out')/label
out.mkdir(exist_ok=False)
root=Path('/work')
config=json.loads((root/'baseline.json').read_text())
if label=='substituted-target': config['theorem_names']=['Nat.add_comm']
if label=='changed-dependency':
    p=root/'OAI/Computability/WitnessedChoice/Model.lean'
    before=p.read_text()
    old='def mk (l : Lists A) : HF A := Quotient.mk Lists.instSetoidLists l'
    new='def mk (l : Lists A) : HF A := id (Quotient.mk Lists.instSetoidLists l)'
    assert before.count(old)==1
    p.write_text(before.replace(old,new))
(out/'config.json').write_text(json.dumps(config,indent=2)+'\n')
files={str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest()
       for p in sorted(root.glob('OAI/**/*.lean'))}
files['ComparatorChallenges/WitnessedChoice.lean']=hashlib.sha256((root/'ComparatorChallenges/WitnessedChoice.lean').read_bytes()).hexdigest()
(out/'source-hashes.json').write_text(json.dumps(files,indent=2)+'\n')
env=dict(os.environ,PATH='/opt/lean/bin:/opt/bin:/usr/bin:/bin',
         COMPARATOR_LANDRUN='/opt/lal/observe_landrun.py',
         COMPARATOR_LEAN4EXPORT='/opt/comparator/.lake/packages/lean4export/.lake/build/bin/lean4export',
         COMPARATOR_NANODA='/opt/nanoda/target/release/nanoda_bin',LAL_CASE=label)
if label=='omitted-nanoda': env['COMPARATOR_NANODA']='/opt/lal/omit-nanoda.sh'
argv=['/opt/lean/bin/lake','env','/opt/comparator/.lake/build/bin/comparator',str(out/'config.json')]
started=time.time_ns()
with (out/'stdout.log').open('wb') as stdout,(out/'stderr.log').open('wb') as stderr:
    result=subprocess.run(argv,cwd=root,env=env,stdout=stdout,stderr=stderr)
record={'case':label,'argv':argv,'started_ns':started,'completed_ns':time.time_ns(),
        'exit_code':result.returncode,'requested_checkers':['Lean','Nanoda'],
        'requested_target':'OAI.WitnessedChoice.main','supplied_config':config,
        'nanoda_command':env['COMPARATOR_NANODA']}
(out/'consumer-result.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record))
print((out/'stdout.log').read_text()[-3500:])
print((out/'stderr.log').read_text()[-1500:])
raise SystemExit(result.returncode)
