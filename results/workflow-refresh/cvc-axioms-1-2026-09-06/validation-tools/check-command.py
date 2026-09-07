import datetime,hashlib,json,os,subprocess,sys,time
from pathlib import Path
root=Path('/Users/danphifer/Documents/ChatGPT/LeanAssuranceLab'); base=root/'results/workflow-refresh/cvc-axioms-1-2026-09-06'; base.mkdir(parents=True,exist_ok=True)
label=sys.argv[1]; cmd=sys.argv[2:]; record=base/(label+'.json'); log=base/(label+'.log')
if record.exists() or log.exists(): raise SystemExit('Refuse to overwrite validation receipt')
now=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
start=now(); tick=time.monotonic(); env=dict(os.environ)
if cmd[0]=='scripts/run-unit-tests':
 env['CVC_RUNNER2_FIXTURE_LEDGER']=str(base/'required-regression-fixtures/fixture-ledger.jsonl')
 env['CVC_PREP_FIXTURE_LEDGER']=str(base/'required-preparation-fixtures.jsonl')
 inputs=[p for folder in ('lib','scripts','tests') for p in (root/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts]
 source=[{'path':str(p.relative_to(root)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(inputs)]
 (base/(label+'-source-bindings.json')).write_text(json.dumps(source,indent=2)+'\n')
with log.open('wb') as f: r=subprocess.run(cmd,cwd=root,env=env,stdout=f,stderr=subprocess.STDOUT)
d={'command':cmd,'returncode':r.returncode,'started_at':start,'ended_at':now(),'elapsed_seconds':time.monotonic()-tick,'log':str(log.relative_to(root)),'log_sha256':hashlib.sha256(log.read_bytes()).hexdigest()}
record.write_text(json.dumps(d,indent=2)+'\n'); print(json.dumps(d)); raise SystemExit(r.returncode)
