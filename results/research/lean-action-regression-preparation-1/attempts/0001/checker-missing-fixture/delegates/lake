#!/usr/bin/env python3
"""Synthetic delegates only: no Lean, Rust, network or privileged operation."""
import os,sys,json,shutil
from pathlib import Path
name=Path(sys.argv[0]).name;a=sys.argv[1:];cell=Path(os.environ['MODEL_CELL']);b=cell/'delegates'
with (cell/'delegate-calls.jsonl').open('a') as f:f.write(json.dumps([name,a])+'\n')
if name=='elan':
 if a[0]=='which':
  missing=os.environ.get('MODEL_MISSING','')
  if missing=='both' or a[1]==missing:sys.exit(1)
  print(b/a[1])
 else:sys.exit(99)
elif name=='lake':
 if a[0]=='env':os.execv(a[1],a[1:])
 elif a==['build']:print('MODEL Lake build; no compiler')
 else:sys.exit(99)
elif name=='cargo':
 if a==['--version']:print('cargo MODEL')
 elif a==['build','--release']:print('MODEL Cargo build; no Rust')
 else:sys.exit(99)
elif name=='git':
 if a[0]!='clone':sys.exit(99)
 d=Path(a[-1]);target=d/('.lake/build/bin/lean4export' if d.name=='_lean4export' else 'target/release/nanoda_bin');target.parent.mkdir(parents=True);shutil.copy2(b/('leanexport' if d.name=='_lean4export' else 'nanoda_bin'),target)
elif name in ['leanexport','lean4export']:print('MODEL export of '+a[0])
elif name=='nanoda_bin':print('MODEL checker; no proof validation')
else: print('Unexpected delegate '+name,file=sys.stderr);sys.exit(99)
