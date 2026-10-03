import json,hashlib,subprocess,difflib,shutil,sys
from pathlib import Path
root=Path.cwd(); run=root/'explorations/runs/EXPLORE-TEST-EFFECTIVENESS-1'; run.mkdir()
work=Path('/private/tmp/lal-test-effectiveness-20261003'); work.mkdir(exist_ok=False)
source=Path('/Users/danphifer/Documents/Codex/2026-09-30/task-4/nanoda-congruence-source')
revision=subprocess.check_output(['git','-C',str(source),'rev-parse','HEAD'],text=True).strip()
assert revision=='3a2407216ee84a75f9e1aead6803d0578be06ae7'
assert not subprocess.check_output(['git','-C',str(source),'status','--porcelain'])
paths=subprocess.check_output(['git','-C',str(source),'ls-files'],text=True).splitlines()
for name in ['baseline','congruence','lambda-binder','definition-type']:
 dst=work/name; dst.mkdir()
 for p in paths:
  f=source/p
  if not f.is_file(): raise ValueError(p)
  out=dst/p;out.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(f,out)
base=(source/'src/tc.rs').read_text()
edits={'congruence':('                            && l_args.iter().copied().zip(r_args.iter().copied()).rev().all(|(x, y)| self.def_eq(x, y))\n',''), 'lambda-binder':('''            if let Check = flag {
                self.infer_sort_of(binder_type, flag);
            }

            let local = self.ctx.mk_dbj_level''','''            if let Check = flag {
                // Seeded benchmark fault: omit lambda binder-sort check.
            }

            let local = self.ctx.mk_dbj_level'''), 'definition-type':('                    tc.assert_def_eq(inferred_type, d.info().ty);','                    let _ = inferred_type; // Seeded benchmark fault: omit declared-type check.')}
for name,(old,new) in edits.items():
 assert base.count(old)==1,(name,base.count(old))
 changed=base.replace(old,new)
 (work/name/'src/tc.rs').write_text(changed)
 (run/(name+'.patch')).write_text(''.join(difflib.unified_diff(base.splitlines(True),changed.splitlines(True),fromfile='a/src/tc.rs',tofile='b/src/tc.rs')))
files=subprocess.check_output(['git','ls-files','corpus/generated/*.ndjson','corpus/controls/*.ndjson','corpus/probes/*.ndjson','corpus/regression-candidates/*.ndjson'],text=True).splitlines()
rows=[dict(path=p,bytes=Path(p).stat().st_size,sha256=hashlib.sha256(Path(p).read_bytes()).hexdigest()) for p in sorted(files)]
selected=[r for r in rows if r['bytes']<=65536];excluded=[r for r in rows if r['bytes']>65536]
prior=Path('explorations/runs/EXPLORE-NANODA-CONGRUENCE-FAULT-1')
augmented=[dict(path=str(prior/p),bytes=(prior/p).stat().st_size,sha256=hashlib.sha256((prior/p).read_bytes()).hexdigest()) for p in ['control.ndjson','candidate.ndjson']]
selection=dict(selector='Complete sorted Git-tracked NDJSON corpus/generated, controls, probes, regression-candidates with bytes <=65536 at activation commit; unchanged inputs.',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),selected=selected,excluded=excluded,augmented=augmented)
(run/'selection.json').write_text(json.dumps(selection,indent=2)+'\n')
config={'unsafe_permit_all_axioms':True,'unpermitted_axiom_hard_error':False,'nat_extension':True,'string_extension':True,'num_threads':1,'print_success_message':True,'pp_to_stdout':False,'use_stdin':True}
(run/'checker-config.json').write_text(json.dumps(config,indent=2)+'\n')
preflight=dict(source_revision=revision,source_files={p:hashlib.sha256((source/p).read_bytes()).hexdigest() for p in paths},source_root=str(source),work_root=str(work),cargo=subprocess.check_output(['cargo','--version'],text=True).strip(),rustc=subprocess.check_output(['rustc','--version'],text=True).strip(),disk_free_bytes=shutil.disk_usage(work).free,build_command=['cargo','build','--offline','--locked','--bin','nanoda_bin'],test_command=['cargo','test','--offline','--locked','--lib'],host=sys.platform,process_limits='Cargo 3600s/16GiB; checker 30s/2GiB; existing supervisor; offline task-local copies only')
(run/'preflight.json').write_text(json.dumps(preflight,indent=2)+'\n')
print('Source copies prepared; compact corpus:',len(selected),'files,',sum(x['bytes'] for x in selected),'bytes;',len(excluded),'oversize file retained as excluded; augmented pair separate.')
