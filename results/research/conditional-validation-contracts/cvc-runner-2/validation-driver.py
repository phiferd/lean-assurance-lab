import datetime,hashlib,json,os,pathlib,subprocess,sys
root=pathlib.Path('/Users/danphifer/Documents/ChatGPT/LeanAssuranceLab')
out=root/'results/workflow-refresh/cvc-runner-2-2026-09-06'
name,*command=sys.argv[1:];log=out/(name+'.log');record=out/(name+'.json')
if log.exists() or record.exists():raise SystemExit('refuse overwrite')
now=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
base=root/'results/research/conditional-validation-contracts/cvc-runner-2'
env={**os.environ,'CVC_RUNNER2_FIXTURE_LEDGER':str(base/'fixture-ledger.jsonl'),'CVC_PREP_FIXTURE_LEDGER':str(base/'validation-fixture-ledger.jsonl'),'PYTHONDONTWRITEBYTECODE':'1'}
sys.path.insert(0,str(root))
from lib.cvc_runner2_evidence import SOURCES
paths=sorted(SOURCES)
bind=lambda p:{'path':p,'sha256':hashlib.sha256((root/p).read_bytes()).hexdigest()}
row={'command':command,'started_at':now(),'log':str(log.relative_to(root)),'tested_input_bindings':[bind(p) for p in paths]}
(out/(name+'-start.json')).write_text(json.dumps(row,indent=2)+'\n')
with log.open('wb') as stream:p=subprocess.run(command,cwd=root,env=env,stdout=stream,stderr=subprocess.STDOUT)
unchanged=row['tested_input_bindings']==[bind(p) for p in paths]
row.update(returncode=p.returncode,status='PASS' if p.returncode==0 and unchanged else 'FAIL',ended_at=now(),log_sha256=hashlib.sha256(log.read_bytes()).hexdigest(),tested_input_bindings_unchanged=unchanged)
record.write_text(json.dumps(row,indent=2)+'\n');print(json.dumps(row));print(log.read_text()[-6000:]);raise SystemExit(p.returncode or (0 if unchanged else 1))
