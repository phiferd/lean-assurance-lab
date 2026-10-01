import os,json,time,hashlib,subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1];ev=root/'confirmation-evidence';repo=root/'confirmation-fresh';f=json.loads((ev/'frozen-inputs.json').read_text())
compiler=Path('/Users/danphifer/.elan/toolchains/leanprover--lean4---v4.33.0/bin/lean')
lib=repo/'fresh-imports';proof=repo/'fresh-proofs';lib.mkdir();proof.mkdir()
env=dict(os.environ);env['LEAN_PATH']=str(proof)+':'+str(lib)
for k in ['LEAN_SRC_PATH','LEAN_SYSROOT']:env.pop(k,None)
stdlib=subprocess.check_output([str(compiler),'--print-prefix'],env=env,text=True).strip();stdroot=Path(stdlib).resolve()
version=subprocess.check_output([str(compiler),'--version'],env=env,text=True)
assert 'version 4.33.0' in version and f['compiler_commit'] in version
(ev/'execution-env.json').write_text(json.dumps(dict(compiler=str(compiler),version=version,LEAN_PATH=env['LEAN_PATH'],official_stdlib_prefix=str(stdroot),initial_compiled_files=0,working_directory=str(repo)),indent=2)+'\n')
for name,h in f['pinned_auxiliary_files'].items():
 assert hashlib.sha256((repo/name).read_bytes()).hexdigest()==h
records=[];start=time.monotonic()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def compile_one(n,upstream):
 index=len(records);d=ev/'modules'/f'{index:03d}';d.mkdir(parents=True)
 src=repo/(n.replace('.','/')+'.lean');dest=(lib if upstream else proof)/(n.replace('.','/')+'.olean');dest.parent.mkdir(parents=True,exist_ok=True)
 expected=f['upstream_sources'][n] if upstream else f['sources'][n+'.lean'];assert sha(src)==expected
 argv=[str(compiler),'-o',str(dest),str(src)];t=time.monotonic()
 (ev/'progress.json').write_text(json.dumps(dict(module=n,index=index,total=len(f['upstream_order'])+len(f['sources']),elapsed_seconds=t-start),indent=2)+'\n')
 try:
  p=subprocess.run(argv,cwd=repo,env=env,capture_output=True,timeout=60 if upstream else 300)
 except subprocess.TimeoutExpired as ex:
  (d/'stdout.log').write_bytes(ex.stdout or b'');(d/'stderr.log').write_bytes(ex.stderr or b'')
  rec=dict(module=n,upstream=upstream,source_sha256=expected,argv=argv,LEAN_PATH=env['LEAN_PATH'],exit_code=None,stop_reason='module_timeout',elapsed_seconds=time.monotonic()-t)
  records.append(rec);(d/'record.json').write_text(json.dumps(rec,indent=2)+'\n');(ev/'module-records.json').write_text(json.dumps(records,indent=2)+'\n')
  print('MODULE TIMEOUT',n,flush=True);sys.exit(1)
 (d/'stdout.log').write_bytes(p.stdout);(d/'stderr.log').write_bytes(p.stderr)
 rec=dict(module=n,upstream=upstream,source_sha256=expected,argv=argv,LEAN_PATH=env['LEAN_PATH'],exit_code=p.returncode,elapsed_seconds=time.monotonic()-t)
 records.append(rec);(d/'record.json').write_text(json.dumps(rec,indent=2)+'\n');(ev/'module-records.json').write_text(json.dumps(records,indent=2)+'\n')
 if p.returncode:print('FAILED',n,p.stdout.decode(errors='replace')[-4000:],p.stderr.decode(errors='replace')[-1000:],flush=True);sys.exit(1)
 assert dest.is_file();rec['olean_sha256']=sha(dest)
 # Actual resolver evidence, not merely declared LEAN_PATH.
 dep=subprocess.run([str(compiler),'--deps',str(src)],cwd=repo,env=env,capture_output=True,timeout=30)
 (d/'deps.log').write_bytes(dep.stdout);(d/'deps-stderr.log').write_bytes(dep.stderr);assert dep.returncode==0
 paths=[]
 for line in dep.stdout.decode().splitlines():
  path=Path(line).resolve();assert path.is_file(),line
  assert path.is_relative_to(lib.resolve()) or path.is_relative_to(proof.resolve()) or path.is_relative_to(stdroot),line
  paths.append(dict(path=str(path),sha256=sha(path)))
 rec['resolved_imports']=paths;(d/'record.json').write_text(json.dumps(rec,indent=2)+'\n');(ev/'module-records.json').write_text(json.dumps(records,indent=2)+'\n')
 print('PASS',index,n,round(rec['elapsed_seconds'],3),flush=True)
for n in f['upstream_order']:compile_one(n,True)
for filename in f['sources']:compile_one(filename[:-5],False)
final=ev/'modules'/f'{len(records)-1:03d}'/'stdout.log';assert final.read_bytes()==(ev/'expected-final-stdout.log').read_bytes()
lines=[x for x in final.read_text().splitlines() if 'depends on axioms:' in x];assert len(lines)==16 and all(x.endswith('[propext, Classical.choice, Quot.sound]') for x in lines)
assert not any(x in final.read_text() for x in ['sorryAx','error:','warning:'])
(ev/'driver-success.json').write_text(json.dumps(dict(status='FRESH_IMPORT_CONFIRMATION_SUCCESS',upstream_modules=len(f['upstream_order']),proof_modules=7,elapsed_seconds=time.monotonic()-start,final_stdout_exact=True,standard_axiom_reports=16,final_stdout_sha256=sha(final),resolved_imports_restricted_to_fresh_outputs_and_official_toolchain=True,source_identities_preserved=True),indent=2)+'\n')
print('FRESH CONFIRMATION SUCCESS',flush=True)
