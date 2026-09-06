#!/usr/bin/env python3
"""Record one named repository validation command, preserving failure logs."""
import datetime,hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
name,*command=sys.argv[1:]
assert name and '/' not in name and command
record={'command':command,'started_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'log':str((OUT/(name+'.log')).relative_to(ROOT))}
with (ROOT/record['log']).open('xb') as log:
 process=subprocess.run(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
record.update(returncode=process.returncode,status='PASS' if process.returncode==0 else 'FAIL',ended_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),log_sha256=hashlib.sha256((ROOT/record['log']).read_bytes()).hexdigest())
(OUT/(name+'.json')).write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record),flush=True)
raise SystemExit(process.returncode)
