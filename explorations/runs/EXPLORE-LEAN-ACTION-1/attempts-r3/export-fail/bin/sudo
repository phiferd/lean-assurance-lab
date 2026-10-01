#!/usr/bin/env python3
import os,sys,json,pathlib,shutil
p=pathlib.Path;name=p(sys.argv[0]).name;a=sys.argv[1:];root=p(os.environ['CELL_ROOT']); log=root/'calls.jsonl'
with log.open('a') as f:f.write(json.dumps([name,a])+'\n')
if name=='sudo': print('FORBIDDEN sudo attempt',file=sys.stderr);sys.exit(99)
if name=='uname':print(os.environ.get('MOCK_OS','Linux'))
elif name=='elan':
 if os.environ.get('ROUTE')=='bundled' and not (os.environ.get('MISSING_NANODA')=='1' and a[-1]=='nanoda_bin'):print(root/'bin'/a[-1])
 else:sys.exit(1)
elif name=='git':
 if a[0]!='clone':sys.exit(99)
 dest=p(a[-1]);dest.mkdir();rel='.lake/build/bin/lean4export' if 'lean4export' in str(dest) else 'target/release/nanoda_bin';target=dest/rel;target.parent.mkdir(parents=True);shutil.copy2(root/'bin'/('leanexport' if 'lean4export' in str(dest) else 'nanoda_bin'),target)
elif name=='cargo':
 if a==['--version']:print('cargo MOCK; no Rust build')
elif name=='leanexport' or name=='lean4export':
 print('MOCK_EXPORT '+a[0]);sys.exit(int(os.environ.get('EXPORT_EXIT','0')))
elif name=='nanoda_bin':
 shutil.copy2(a[0],root/'captured-config.json');print('MOCK checker invoked; no semantic validation');sys.exit(int(os.environ.get('CHECKER_EXIT','0')))
elif name=='bwrap':
 if os.environ.get('PROBE_FAIL')=='1':print('bwrap: uid map denied',file=sys.stderr);sys.exit(1)
elif name=='lake':
 if a[:2]==['check','--help']:
  print('top-level legacy help' if os.environ.get('UNSUPPORTED')=='1' else 'Check this project against external checker(s) --paranoid')
 elif a and a[0]=='env': os.execv(a[1],a[1:])
 elif a and a[0]=='check':
  if os.environ.get('LATE_BWRAP')=='1':print('bwrap: pivot_root denied',file=sys.stderr)
  else:print('MOCK lake check')
  sys.exit(int(os.environ.get('CHECKER_EXIT','0')))
