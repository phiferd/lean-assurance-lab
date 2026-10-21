import json,hashlib,subprocess,time
from pathlib import Path
P=Path(__file__).resolve().parent;C='lal-comparator-screen-native';base='/arena-current-nanoda/'
m=json.loads((P/'build-manifest.json').read_text())
for rel,digest in [('target/release/nanoda_bin',m['binary_sha256']),('config.json',m['config_sha256'])]:
 assert subprocess.check_output(['docker','exec',C,'sha256sum',base+rel],text=True).split()[0]==digest
assert subprocess.check_output(['docker','exec',C,'sha256sum',base+'config-diagnostic.json'],text=True).split()[0]==hashlib.sha256((P/'config-diagnostic.json').read_bytes()).hexdigest()
assert subprocess.check_output(['docker','exec',C,'sha256sum',base+'instrumented-run-diagnostic.sh'],text=True).split()[0]==hashlib.sha256((P/'instrumented-run-diagnostic.sh').read_bytes()).hexdigest()
out=P/'observations-control-diagnostic';out.mkdir(exist_ok=False);rows=[]
for case in [c for c in json.loads((P/'cases.json').read_text()) if c['id']=='control']:
 ident=case['id'];inp='/arena-current-inputs/'+ident+'.ndjson'
 assert subprocess.check_output(['docker','exec',C,'sha256sum',inp],text=True).split()[0]==case['sha256']
 status='/arena-current-results/'+ident+'-diagnostic.raw-status'
 argv=['docker','exec','--user','checker','--workdir',base,'--env','IN='+inp,'--env','RAW_STATUS='+status,C,'timeout','--kill-after=10','120','sh','instrumented-run-diagnostic.sh']
 start=time.monotonic();r=subprocess.run(argv,stdout=subprocess.PIPE,stderr=subprocess.PIPE);elapsed=time.monotonic()-start
 d=out/ident;d.mkdir();(d/'stdout.log').write_bytes(r.stdout);(d/'stderr.log').write_bytes(r.stderr)
 # Missing raw status is a setup/timeout failure, never inferred rejection.
 raw=subprocess.run(['docker','exec',C,'cat',status],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
 (d/'raw-status.log').write_bytes(raw.stdout);(d/'status-read-stderr.log').write_bytes(raw.stderr)
 row={'case':ident,'argv':argv,'input_sha256':case['sha256'],'wrapper_exit_code':r.returncode,'raw_status_read_exit':raw.returncode,'raw_exit_code':int(raw.stdout) if raw.returncode==0 else None,'elapsed_seconds':elapsed}
 (d/'execution.json').write_text(json.dumps(row,indent=2)+'\n');rows.append(row);print(json.dumps(row),flush=True)
 assert raw.returncode==0,'Repair missing raw status before next launch'
 assert subprocess.check_output(['docker','exec',C,'sha256sum',inp],text=True).split()[0]==case['sha256']
(out/'executions.json').write_text(json.dumps(rows,indent=2)+'\n')
