"""Fresh E1 model runner; each shell child uses the unchanged lab supervisor."""
from pathlib import Path
import os,sys,json,shutil,hashlib,re
package=Path(__file__).resolve().parent;root=package.parents[2];sys.path.insert(0,str(root))
from lib.resource_envelope_supervisor import run_direct
source=root/'explorations/runs/EXPLORE-LEAN-ACTION-1/source'
attempt=package/'attempts'/os.environ.get('LEAN_ACTION_ATTEMPT','0001');attempt.mkdir(parents=True,exist_ok=False)
rows=[];inputs=json.loads((package/'input-manifest.json').read_text())
for relative,expected in inputs['sha256'].items():assert hashlib.sha256((root/relative).read_bytes()).hexdigest()==expected,relative

def run(label,script,cell,env,expected):
 out=attempt/label;out.mkdir();argv=['/bin/bash',str(script)]
 (out/'command.json').write_text(json.dumps({'argv':argv,'cwd':str(cell),'environment_overrides':env,'manifest_sha256':hashlib.sha256((package/'input-manifest.json').read_bytes()).hexdigest()},indent=2)+'\n')
 x=run_direct(argv=argv,cwd=cell,env={**os.environ,**env},stdin_bytes=None,timeout_seconds=20,memory_ceiling_bytes=512*1024*1024,sample_interval_seconds=.01,max_trace_gap_seconds=2,cleanup_seconds=2)
 (out/'stdout').write_bytes(x.stdout);(out/'stderr').write_bytes(x.stderr);(out/'receipt.json').write_text(json.dumps(x.receipt,indent=2)+'\n');rr=x.receipt
 rows.append({'label':label,'expected_exit':expected,'actual_exit':rr['exit_code'],'cleanup':rr['cleanup_complete']});(attempt/'result.json').write_text(json.dumps(rows,indent=2)+'\n')
 assert rr['cleanup_complete'] and not any(rr[k] for k in ['monitor_errors','pipe_errors','accounting_error','stop_reason']),f'PAUSE supervision fault {label}'
 assert rr['exit_code']==expected,(label,rr['exit_code'],expected)
 return x

def script(cell,name,body):
 p=cell/name;p.write_text(body);return p

for name,missing,allow,status,oracle in [('bundled','',False,0,0),('neither','both',False,37,1),('fallback-success','both',True,0,1),('exporter-missing','leanexport',True,0,1),('checker-missing','nanoda_bin',False,37,1)]:
 cell=attempt/(name+'-fixture');cell.mkdir();(cell/'delegates').mkdir();(cell/'temp').mkdir()
 for tool in ['elan','git','cargo','lake','leanexport','nanoda_bin']:
  target=cell/'delegates'/tool;shutil.copy2(package/'mock-tools.py',target);target.chmod(0o755)
 for f in ['github-env','github-path','github-output']:(cell/f).touch()
 (cell/'lean-toolchain').write_text('leanprover/lean4:v4.35.0-rc2\n');(cell/'lakefile.toml').write_text('name = "foo"\ndefaultTargets = ["Foo"]\n[[lean_lib]]\nname = "Foo"\n')
 env={'MODEL_CELL':str(cell),'PATH':str(cell/'delegates')+':/usr/bin:/bin','RUNNER_TEMP':str(cell/'temp'),'GITHUB_ENV':str(cell/'github-env'),'GITHUB_PATH':str(cell/'github-path'),'GITHUB_OUTPUT':str(cell/'github-output'),'NANODA_ALLOW_SORRY':'false'}
 # Resolve healthy tool identities before changing the availability observation.
 setup=script(cell,'setup.sh',f'exec /bin/bash "{package}/observe_nanoda_tools.sh" --install\n');run(name+'-install',setup,cell,env,0)
 for line in (cell/'github-env').read_text().splitlines():k,v=line.split('=',1);env[k]=v
 env['PATH']=(cell/'github-path').read_text().strip()+':'+env['PATH'];env['MODEL_MISSING']=missing;env['NANODA_TEST_ALLOW_FALLBACK']='true' if allow else 'false'
 run(name+'-action',source/'pr192-scripts_run_nanoda.sh',cell,env,status)
 check=script(cell,'check.sh',f'exec /bin/bash "{package}/observe_nanoda_tools.sh" --check\n');run(name+'-oracle',check,cell,env,oracle)
 assert not (cell/'_lean4export').exists() and not (cell/'_nanoda_lib').exists()
 if allow:
  assert (cell/'github-output').read_text()=='nanoda-status=SUCCESS\n'
  assert 'forbidden-source-clone' in (Path(env['NANODA_TOOL_TRACE_DIR'])/'invocations').read_text()
 if name=='bundled':
  trace=Path(env['NANODA_TOOL_TRACE_DIR'])/'invocations';assert trace.read_text().splitlines()==['bundled-exporter','bundled-checker'];fault_dir=cell/'missing-marker-trace';fault_dir.mkdir();(fault_dir/'invocations').write_text('bundled-exporter\n')
  fault_env={**env,'NANODA_TOOL_TRACE_DIR':str(fault_dir)}
  run(name+'-missing-marker-oracle',check,cell,fault_env,1)

for version,path in [('original',source/'pr191-scripts_run_lake_check.sh'),('fixed',package/'pr191-fixed.sh')]:
 full=path.read_text();begin=full.index('        apparmor)\n')+len('        apparmor)\n');end=full.index('            ;;',begin);branch=full[begin:end]
 assert branch.count('sudo tee ')==1 and branch.count('sudo apparmor_parser ')==1
 for state,healthy in [('absent',False),('conventional',False),('destination',False),('both',False),('healthy-destination',True)]:
  cell=attempt/(version+'-'+state+'-fixture');cell.mkdir();policies=cell/'policies';policies.mkdir();(cell/'operation-log').touch()
  conventional=policies/'bwrap';destination=policies/'lean-action-bwrap'
  if state in ['conventional','both']:conventional.write_text('KEEP conventional\n')
  if state in ['destination','both','healthy-destination']:destination.write_text('KEEP destination\n')
  before=destination.read_text() if destination.exists() else None
  # Exact projection: synthetic policy directory, two intercepted commands; trusted-exe call retained as assumed precondition.
  projected=branch.replace('/etc/apparmor.d',str(policies)).replace('sudo tee ','model_tee ').replace('sudo apparmor_parser ','model_parser ')
  assert not re.search(r'(?m)^\s*(?:if ! )?sudo\b|/etc/apparmor\.d',projected)
  prefix='''#!/usr/bin/env bash
set -euo pipefail
sandbox_exe=/usr/bin/bwrap
failure_message=''
assert_trusted_sandbox_exe() { :; }
apparmor_parser() { echo 'forbidden real parser' >&2; exit 99; }
model_tee() { printf 'writer\\n' >> "$MODEL_CELL/operation-log"; cat > "$1"; }
model_parser() { printf 'loader\\n' >> "$MODEL_CELL/operation-log"; }
trap 'rc=$?; printf "%s\\n" "$failure_message"; exit "$rc"' EXIT
'''
  suffix='\nfi\n';projection=script(cell,'projected.sh',prefix+('if false; then\n' if healthy else 'if true; then\n')+projected+suffix)
  expected=2 if (not healthy and (state in ['conventional','both'] or version=='fixed' and state=='destination')) else 0
  run(version+'-'+state,projection,cell,{'MODEL_CELL':str(cell),'PATH':'/usr/bin:/bin'},expected)
  after=destination.read_text() if destination.exists() else None;ops=(cell/'operation-log').read_text()
  if expected==2 or healthy:assert after==before and ops==''
  else:assert after is not None and 'profile lean-action-bwrap' in after and ops=='writer\nloader\n'
  if state in ['conventional','both']:assert conventional.read_text()=='KEEP conventional\n'
print(f'PASS {len(rows)} fresh supervised shell controls; no real Lean/build/network/privileged operations')
