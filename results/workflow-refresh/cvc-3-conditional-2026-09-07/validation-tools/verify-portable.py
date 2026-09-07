"""Validate exact working closure in a fresh local full-history clone, without payloads."""
import json, shutil, subprocess, tempfile
from pathlib import Path
root=Path(__file__).resolve().parents[4]
container=Path(tempfile.mkdtemp(prefix='cvc3-a7-closure-'))
clone=container/'repo'
subprocess.run(['git','clone','--no-hardlinks','--quiet',str(root),str(clone)],check=True)
paths=subprocess.check_output(['git','ls-files','--cached','--others','--exclude-standard','-z'],cwd=root).decode().split('\0')
for name in filter(None,paths):
    src=root/name
    if src.is_file():
        dest=clone/name
        dest.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(src,dest)
assert not (clone/'external/cvc3-u1-a7-proof-0001').exists()
cmd=['scripts/validate-cvc3-a7','--closure']
completed=subprocess.run(cmd,cwd=clone,capture_output=True,text=True)
print(completed.stdout,end=''); print(completed.stderr,end='')
assert completed.returncode==0, 'portable tracked closure failed'
full=subprocess.run(cmd+['--require-full-payload'],cwd=clone,capture_output=True,text=True)
assert full.returncode!=0 and 'Contract.olean' in full.stderr, 'strict mode did not expose absent signature payload'
print(json.dumps({'status':'PASS','clone':str(clone),'full_history':True,'local_clone_no_network':True,'portable_closure_returncode':completed.returncode,'strict_payload_returncode':full.returncode,'strict_failure':full.stderr.splitlines()[-1],'compiler_launches':0}))
