import json,os,sys,hashlib,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from lib.resource_envelope_supervisor import run_direct
RUN=Path(__file__).resolve().parent
SRC=ROOT.parent/'tree2-computation'
CACHE=ROOT.parent/'confirmation-fresh'
compiler='/Users/danphifer/.elan/toolchains/leanprover--lean4---v4.33.0/bin/lean'
name=sys.argv[1];attempt=sys.argv[2]
out=RUN/attempt;out.mkdir(exist_ok=False)
source=SRC/(name+'.lean');shutil.copyfile(source,out/(name+'.lean'))
outputs=SRC/'pilot-outputs';outputs.mkdir(exist_ok=True)
env=dict(os.environ);env['LEAN_PATH']=str(outputs)+':'+str(CACHE/'fresh-proofs')+':'+str(CACHE/'fresh-imports')
for k in ['LEAN_SRC_PATH','LEAN_SYSROOT']:env.pop(k,None)
argv=[compiler,'-o',str(outputs/(name+'.olean')),str(source)]
(out/'command.json').write_text(json.dumps(dict(argv=argv,cwd=str(SRC),LEAN_PATH=env['LEAN_PATH'],source_sha256=hashlib.sha256(source.read_bytes()).hexdigest()),indent=2)+'\n')
r=run_direct(argv=argv,cwd=SRC,env=env,stdin_bytes=None,timeout_seconds=3600,memory_ceiling_bytes=16*1024**3,sample_interval_seconds=.5,max_trace_gap_seconds=3,cleanup_seconds=10,output_cap_bytes=20000000)
(out/'stdout.log').write_bytes(r.stdout);(out/'stderr.log').write_bytes(r.stderr)
(out/'receipt.json').write_text(json.dumps(r.receipt,indent=2)+'\n')
print(json.dumps({k:r.receipt.get(k) for k in ['exit_code','elapsed_seconds','stop_reason','cleanup_ok','monitoring_complete','accounting_complete']},indent=2))
print(r.stdout.decode(errors='replace')[-5000:]);print(r.stderr.decode(errors='replace')[-1000:])
