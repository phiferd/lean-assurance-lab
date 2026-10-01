from pathlib import Path
import os,sys,json,shutil,hashlib
root=Path(__file__).resolve().parents[3];sys.path.insert(0,str(root))
from lib.resource_envelope_supervisor import run_direct
r=Path(__file__).resolve().parent
cells=[('bundled-false','pr192',{'ROUTE':'bundled','NANODA_ALLOW_SORRY':'false'}),('bundled-true','pr192',{'ROUTE':'bundled','NANODA_ALLOW_SORRY':'true'}),('source-false','pr192',{'ROUTE':'source','NANODA_ALLOW_SORRY':'false'}),('source-true','pr192',{'ROUTE':'source','NANODA_ALLOW_SORRY':'true'}),('export-fail','pr192',{'ROUTE':'bundled','EXPORT_EXIT':'7'}),('checker-fail','pr192',{'ROUTE':'bundled','CHECKER_EXIT':'9'}),('one-tool-missing','pr192',{'ROUTE':'bundled','MISSING_NANODA':'1'}),('nonlinux','pr190',{'MOCK_OS':'Darwin'}),('unsupported','pr190',{'UNSUPPORTED':'1'}),('probe-fail','pr190',{'PROBE_FAIL':'1'}),('late-bwrap','pr190',{'LATE_BWRAP':'1','CHECKER_EXIT':'1'}),('check-reject','pr190',{'CHECKER_EXIT':'1'}),('check-success','pr190',{})]
result=[]
for name,rev,params in cells:
 cell=r/'attempts'/name;cell.mkdir(parents=True,exist_ok=False);(cell/'bin').mkdir()
 for tool in ['elan','lake','cargo','git','leanexport','nanoda_bin','bwrap','uname','sudo']:
  shutil.copy2(r/'mock-tool.py',cell/'bin'/tool);(cell/'bin'/tool).chmod(0o755)
 (cell/'lean-toolchain').write_text('leanprover/lean4:v4.35.0-rc2\n');(cell/'lakefile.toml').write_text('name = "foo"\ndefaultTargets = ["Foo"]\n[[lean_lib]]\nname = "Foo"\n');(cell/'github-output').touch()
 params={'NANODA_ALLOW_SORRY':'false','LAKE_CHECK_INPUT':'paranoid',**params,'PATH':str(cell/'bin')+':/usr/bin:/bin','CELL_ROOT':str(cell),'GITHUB_OUTPUT':str(cell/'github-output'),'RUNNER_TEMP':str(cell),'COMPARATOR_BWRAP':str(cell/'bin'/'bwrap')}
 script=r/'source'/f'{rev}-scripts_run_'+('nanoda' if rev=='pr192' else 'lake_check')+'.sh'
 argv=['/bin/bash',str(script)];(cell/'command.json').write_text(json.dumps({'argv':argv,'cwd':str(cell),'environment_overrides':params},indent=2)+'\n')
 x=run_direct(argv=argv,cwd=cell,env={**os.environ,**params},stdin_bytes=None,timeout_seconds=20,memory_ceiling_bytes=512*1024*1024,sample_interval_seconds=.01,max_trace_gap_seconds=2,cleanup_seconds=2)
 (cell/'stdout').write_bytes(x.stdout);(cell/'stderr').write_bytes(x.stderr);(cell/'receipt.json').write_text(json.dumps(x.receipt,indent=2)+'\n')
 row={'cell':name,'receipt':x.receipt,'status_output':(cell/'github-output').read_text(),'calls':(cell/'calls.jsonl').read_text() if (cell/'calls.jsonl').exists() else '', 'source_dirs_absent_after_exit':not any((cell/y).exists() for y in ['_lean4export','_nanoda_lib'])};result.append(row)
 (r/'control-result.json').write_text(json.dumps(result,indent=2)+'\n')
 if x.receipt.get('monitor_errors') or x.receipt.get('cleanup_errors') or x.receipt.get('stop_reason'):
  print('PAUSE supervision fault in '+name);sys.exit(2)
print('Completed '+str(len(result))+' controlled shell cells; zero real checkers or builds')
