import sys,json,os
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'lab'))
from lib.resource_envelope_supervisor import run_direct
r=run_direct(argv=['/Library/Frameworks/Python.framework/Versions/3.10/bin/python3',str(root/'confirmation-evidence/driver.py')],cwd=root,env=dict(os.environ),stdin_bytes=None,timeout_seconds=600,memory_ceiling_bytes=4*1024**3,sample_interval_seconds=.2,max_trace_gap_seconds=3,cleanup_seconds=5)
ev=root/'confirmation-evidence';(ev/'stdout.log').write_bytes(r.stdout);(ev/'stderr.log').write_bytes(r.stderr);(ev/'receipt.json').write_text(json.dumps(r.receipt,indent=2)+'\n')
print(r.stdout.decode(errors='replace')[-3000:]);print(r.stderr.decode(errors='replace')[-3000:]);print(json.dumps({k:r.receipt.get(k) for k in ['exit_code','elapsed_seconds','maximum_sampled_group_rss_bytes','cleanup_complete','stop_reason','accounting_error']}))
