import json,shutil,subprocess,tempfile
from pathlib import Path
root=Path.cwd(); base='results/research/conditional-validation-contracts/cvc-3'; manifest=base+'/evidence-manifest.json'
with tempfile.TemporaryDirectory(prefix='cvc3-clone-') as temp:
 clone=Path(temp)/'repo'
 subprocess.run(['git','clone','--quiet','--no-hardlinks',str(root),str(clone)],check=True)
 paths=[r['path'] for r in json.loads((root/manifest).read_text())['files']]+[manifest]
 for rel in paths:
  dest=clone/rel; dest.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(root/rel,dest)
 assert not (clone/'external/cvc3-u1-proof-0001/Contract.olean').exists()
 process=subprocess.run(['scripts/validate-cvc3-evidence'],cwd=clone,check=True,stdout=subprocess.PIPE,text=True)
 result=json.loads(process.stdout); assert result['outcome']=='BOUNDED_UNRESOLVED' and not result['payloads_verified']
 print(json.dumps({'status':'PASS','validation':'Fresh full-history local clone; exact closure overlay; no compiled proof or dependency payloads; no Lean or checker invocation','result':result},indent=2))
