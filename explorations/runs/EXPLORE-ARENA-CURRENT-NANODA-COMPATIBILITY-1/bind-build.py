import subprocess,json,hashlib,tarfile
from pathlib import Path
P=Path(__file__).resolve().parent; C='lal-comparator-screen-native'; base='/arena-current-nanoda/'
def get(path):return subprocess.check_output(['docker','exec',C,'cat',base+path])
sha=lambda b:hashlib.sha256(b).hexdigest()
ident=json.loads(subprocess.check_output(['docker','inspect',C]))[0]
assert not ident['NetworkSettings']['Networks']
assert len(ident['Mounts'])==2 and all(m['Type']=='bind' and not m['RW'] for m in ident['Mounts'])
assert ident['HostConfig']['Memory']<=12*1024**3 and ident['HostConfig']['PidsLimit']==512
rows=[]
with tarfile.open(P/'nanoda-source.tar') as t:
 for m in t:
  if m.isfile():
   original=t.extractfile(m).read(); expected=original
   if m.name=='src/lib.rs':
    assert original.count(b'STACK_SIZE: usize = 16_777_216;')==1
    expected=original.replace(b'STACK_SIZE: usize = 16_777_216;',b'STACK_SIZE: usize = 268_435_456;')
    import difflib
    (P/'applied-stack.patch').write_text(''.join(difflib.unified_diff(original.decode().splitlines(True),expected.decode().splitlines(True),fromfile='a/src/lib.rs',tofile='b/src/lib.rs')))
   actual=get(m.name); assert actual==expected,m.name
   rows.append({'path':m.name,'sha256':sha(actual)})
expected_cfg={'use_stdin':True,'nat_extension':True,'string_extension':True,'unpermitted_axiom_hard_error':False,'unsafe_permit_all_axioms':True,'num_threads':4}
config=get('config.json');assert json.loads(config)==expected_cfg
(P/'config.json').write_bytes(config)
for name in ['arena-run.sh','instrumented-run.sh','build.sh']:assert get(name)==(P/name).read_bytes()
manifest={'container':C,'image':ident['Image'],'platform':ident['Platform'],'network':'disconnected; no attached network','host_mounts':ident['Mounts'], 'memory_ceiling_bytes':ident['HostConfig']['Memory'],'sources':rows,'config_sha256':sha(config),'binary_sha256':sha(get('target/release/nanoda_bin')),'input_sha256':{}}
for case in json.loads((P/'cases.json').read_text()):
 path='/arena-current-inputs/'+case['id']+'.ndjson'
 digest=subprocess.check_output(['docker','exec',C,'sha256sum',path],text=True).split()[0]
 assert digest==case['sha256'];manifest['input_sha256'][path]=digest
(P/'build-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({k:v for k,v in manifest.items() if k!='sources'},indent=2));print('PASS: all',len(rows),'source files match pinned archive plus exact stack patch.')
