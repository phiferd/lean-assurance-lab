import hashlib,json,os,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from lib.resource_envelope_supervisor import run_direct
folder=Path(__file__).resolve().parent/'attempts'/sys.argv[1]
folder.mkdir(parents=True,exist_ok=False)
argv=sys.argv[2:]
inputs={str(Path(a).relative_to(ROOT)):hashlib.sha256(Path(a).read_bytes()).hexdigest() for a in argv if Path(a).is_file() and Path(a).is_relative_to(ROOT)}
(folder/'inputs.json').write_text(json.dumps(inputs,indent=2)+'\n')
r=run_direct(argv=argv,cwd=ROOT,env=dict(os.environ),stdin_bytes=None,timeout_seconds=2592000,memory_ceiling_bytes=4*1024**3,sample_interval_seconds=1,max_trace_gap_seconds=5,cleanup_seconds=10,output_cap_bytes=20*1024**2)
(folder/'stdout.log').write_bytes(r.stdout);(folder/'stderr.log').write_bytes(r.stderr)
(folder/'receipt.json').write_text(json.dumps(r.receipt,indent=2,sort_keys=True)+'\n')
print(json.dumps({k:r.receipt.get(k) for k in ['exit_code','elapsed_seconds','cleanup_complete','accounting_error','monitor_errors','termination_reason']}))
print(r.stdout.decode(errors='replace')[-8000:]);print(r.stderr.decode(errors='replace')[-2000:])
if not r.receipt.get('cleanup_complete') or r.receipt.get('accounting_error') or r.receipt.get('monitor_errors'):raise SystemExit('CONTROL FAULT: stop launches')
sys.exit(r.receipt.get('exit_code') or 0)
