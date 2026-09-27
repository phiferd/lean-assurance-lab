"""Exact-source build and fail-closed adapter for the fixed lazy-reduction pilot."""
from __future__ import annotations
import argparse
import difflib
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys
import time
from lib.cvc_prep import committed
from lib.metamorphic_pilot_runner import run_supervised

ROOT = Path(__file__).resolve().parents[1]
BASE = Path('results/research/lazy-reduction-conformance-pilot-1')
ORIGINAL = Path('results/research/workflow-closure-automation-1/observer-comparison/source/lazylean')
SOURCE_LOCK = ORIGINAL.parent.parent / 'source-inventory.json'
SOURCE = Path('external/lazy-reduction-conformance-pilot-1/source-r1')
BINARY = Path('external/lazy-reduction-conformance-pilot-1/lazylean-r1')
ITEM = 'LAZY-REDUCTION-CONFORMANCE-PILOT-1'
UNITS = ['name','level','expr','loader','tc','inductive','kam','fuse','fix','main']
ENV = {'PATH':'/usr/bin:/bin:/usr/sbin:/sbin','LANG':'C','LC_ALL':'C'}
PATCHES = {
 'src/main.cpp': [('#include <malloc.h>', '#ifdef __linux__\n#include <malloc.h>\n#endif'),
                  ('kam_pools_trim(); malloc_trim(0);', 'kam_pools_trim();\n#ifdef __linux__\n      malloc_trim(0);\n#endif')],
 'src/name.cpp': [('  if (e > b) madvise((void*)b, e - b, MADV_HUGEPAGE);', '#ifdef MADV_HUGEPAGE\n  if (e > b) madvise((void*)b, e - b, MADV_HUGEPAGE);\n#endif')],
 'src/kam.cpp': [('static inline u64 rdtsc_() { unsigned lo, hi; __asm__ __volatile__("rdtsc" : "=a"(lo), "=d"(hi)); return ((u64)hi << 32) | lo; }', '#if defined(__i386__) || defined(__x86_64__)\nstatic inline u64 rdtsc_() { unsigned lo, hi; __asm__ __volatile__("rdtsc" : "=a"(lo), "=d"(hi)); return ((u64)hi << 32) | lo; }\n#else\nstatic inline u64 rdtsc_() { return 0; } // profiling only; cycles unavailable\n#endif')]
}

def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def bind(path):
    p = Path(path)
    p = p if p.is_absolute() else ROOT / p
    p = p.resolve()
    return dict(path=str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p),bytes=p.stat().st_size,sha256=digest(p))

def verify(row):
    p = ROOT / row['path']
    if bind(p) != row:
        raise ValueError(f"stale binding: {row['path']}")
    return p

def load(path):
    def pairs(rows):
        result = {}
        for key,value in rows:
            if key in result: raise ValueError('duplicate JSON key')
            result[key]=value
        return result
    return json.loads((ROOT/path).read_text(),object_pairs_hook=pairs)

def write_new(path,value):
    p=ROOT/path
    p.parent.mkdir(parents=True,exist_ok=True)
    raw=(json.dumps(value,indent=2,sort_keys=True,allow_nan=False)+'\n').encode()
    if p.exists():
        if p.read_bytes()!=raw: raise ValueError(f'refuse overwrite: {path}')
    else:
        with p.open('xb') as stream: stream.write(raw)

def active():
    q=load(Path('config/research-queue.json'))
    if q['selected_item']!=ITEM or next(x for x in q['items'] if x['id']==ITEM)['status']!='ACTIVE':
        raise ValueError('pilot is not selected ACTIVE')

def tooling():
    return [bind(p) for p in ['lib/lazy_reduction_pilot.py','scripts/lazy-reduction-pilot',
                            'lib/metamorphic_pilot_runner.py','lib/cvc_prep.py',
                            'tests/test_lazy_reduction_pilot.py']]

def require_committed(rows):
    for row in rows:
        verify(row)
        if not Path(row['path']).is_absolute(): committed(ROOT,row['path'])

def safe(receipt):
    if receipt.get('memory_monitor_error') or not receipt.get('cleanup_complete'):
        raise ValueError('process observation/cleanup failure; repair before another launch')
    if receipt.get('timed_out') or receipt.get('memory_exceeded'):
        raise ValueError('process safety limit; diagnose before another launch')
    if receipt.get('memory_monitor_samples',0)<=0 or receipt.get('maximum_observed_rss_bytes',0)<=0:
        raise ValueError('missing positive RSS')

def raw(receipt):
    result=[]
    for kind in ['stdout','stderr']:
        p=Path(receipt['raw_'+kind+'_path'])
        p=p if p.is_absolute() else ROOT/p
        if digest(p)!=receipt[kind+'_sha256'] or p.stat().st_size!=receipt[kind+'_bytes']:
            raise ValueError('raw receipt mismatch')
        result.append(p.read_bytes())
    return result

def prepare():
    active()
    original=load(SOURCE_LOCK)
    rows=original['source_entries']
    patch=[]; bindings=[]
    for row in rows:
        p=ROOT/row['path']
        if p.stat().st_size!=row['bytes'] or digest(p)!=row['sha256']: raise ValueError('source input differs')
        rel=row['repository_path']; before=p.read_text(); after=before
        for old,new in PATCHES.get(rel,[]):
            if after.count(old)!=1: raise ValueError('patch anchor mismatch')
            after=after.replace(old,new)
        dest=ROOT/SOURCE/rel
        dest.parent.mkdir(parents=True,exist_ok=True)
        if dest.exists() and dest.read_text()!=after: raise ValueError('materialized source differs')
        if not dest.exists(): dest.write_text(after)
        bindings.append(bind(dest))
        patch.extend(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='a/'+rel,tofile='b/'+rel))
    patchpath=ROOT/BASE/'portability-r1.patch'
    patchpath.parent.mkdir(parents=True,exist_ok=True)
    if patchpath.exists() and patchpath.read_text()!=''.join(patch): raise ValueError('patch differs')
    if not patchpath.exists(): patchpath.write_text(''.join(patch))
    value=dict(item_id=ITEM,source_revision='68c66fa18c1afe029512b90ecfe0b162c0dcd8fb',
               original_inventory=bind(SOURCE_LOCK),patch=bind(patchpath),files=bindings,
               meaning='Linux allocator hints, huge-page hint and x86 profiling-cycle guard only; no checking/reduction edits.')
    write_new(BASE/'source-r1.json',value)
    return value

def freeze_build():
    active(); source=prepare()
    review=load(BASE/'portability-review-r1.json')
    if review['verdict']!='PASS' or review['patch']!=source['patch']: raise ValueError('exact patch review missing')
    compiler=Path(subprocess.check_output(['/usr/bin/xcrun','--find','clang++'],text=True).strip()).resolve()
    sdk=Path(subprocess.check_output(['/usr/bin/xcrun','--show-sdk-path'],text=True).strip()).resolve()
    gmp=Path('/opt/homebrew/opt/gmp').resolve()
    flags=['-std=c++20','-O2','-g','-isysroot',str(sdk),'-I',str(ROOT/SOURCE/'src'),'-I',str(gmp/'include')]
    depdir=ROOT/BASE/'dependency-scan-r1'
    if depdir.exists(): raise ValueError('dependency scan already exists')
    depdir.mkdir()
    deps=set(); scans=[]
    for unit in UNITS:
        argv=[str(compiler),*flags,'-M',str(ROOT/SOURCE/'src'/f'{unit}.cpp')]
        receipt=run_supervised(argv=argv,cwd=ROOT,stdin=None,env=ENV,timeout_seconds=60,memory_bytes=2147483648,raw_prefix=depdir/unit)
        scans.append(receipt); write_new(BASE/'dependency-scan-r1'/f'{unit}.json',receipt)
        stdout,stderr=raw(receipt); safe(receipt)
        if receipt['exit_code'] or stderr: raise ValueError('dependency scan failed')
        words=shlex.split(stdout.decode().replace('\\\n',' ').split(':',1)[1])
        deps.update(Path(w).resolve() for w in words)
    # Linker and SDK interfaces are build inputs in addition to preprocessor closure.
    deps.update([compiler,compiler.parent/'ld',gmp/'lib/libgmp.a',gmp/'lib/libgmpxx.a',sdk/'SDKSettings.json'])
    deps.update((sdk/'usr/lib').glob('*.tbd'))
    deps.update((compiler.parent.parent/'lib/clang/17/lib/darwin').glob('libclang_rt.osx.a'))
    argv=[str(compiler),*flags,*[str(ROOT/SOURCE/'src'/f'{x}.cpp') for x in UNITS],
          str(gmp/'lib/libgmpxx.a'),str(gmp/'lib/libgmp.a'),'-pthread','-o',str(ROOT/BINARY)]
    manifest=dict(item_id=ITEM,stage='BUILD',source=bind(BASE/'source-r1.json'),patch_review=bind(BASE/'portability-review-r1.json'),
                  argv=argv,cwd=str(ROOT),environment=ENV,timeout_seconds=1200,memory_bytes=4294967296,
                  dependencies=[bind(x) for x in sorted(deps)],tooling=tooling(),
                  sdk=str(sdk),compiler_version=subprocess.check_output([str(compiler),'--version'],text=True),
                  host_version=subprocess.check_output(['/usr/bin/sw_vers'],text=True),
                  runtime_scope='Host system C++/libSystem runtime supplied by recorded macOS; SDK link interfaces bound, GMP statically linked.',
                  scan_receipts=[bind(BASE/'dependency-scan-r1'/f'{x}.json') for x in UNITS])
    write_new(BASE/'build-manifest-r1.json',manifest)
    return {'dependencies':len(deps),'manifest':str(BASE/'build-manifest-r1.json')}

def build(attempt):
    active(); m=load(BASE/'build-manifest-r1.json')
    require_committed([bind(BASE/'build-manifest-r1.json'),m['source'],m['patch_review'],*m['tooling']])
    for row in m['dependencies']: verify(row)
    for row in load(BASE/'source-r1.json')['files']: verify(row)
    out=BASE/attempt
    if (ROOT/out).exists(): raise ValueError('attempt exists')
    (ROOT/out).mkdir()
    receipt=run_supervised(argv=m['argv'],cwd=ROOT,stdin=None,env=m['environment'],timeout_seconds=m['timeout_seconds'],memory_bytes=m['memory_bytes'],raw_prefix=ROOT/out/'build')
    result=dict(item_id=ITEM,manifest=bind(BASE/'build-manifest-r1.json'),receipt=receipt)
    if receipt['exit_code']==0 and (ROOT/BINARY).is_file(): result['binary']=bind(BINARY)
    write_new(out/'result.json',result)
    safe(receipt)
    if receipt['exit_code']!=0: raise ValueError('build failure preserved; repair')
    return result

MACHINE=re.compile(r'machine: app (\d+), bvar (\d+), beta (\d+), let (\d+), delta (\d+), iota (\d+), proj (\d+), enter value/delayed/re-eval (\d+)/(\d+)/(\d+), memo hit/insert (\d+)/(\d+)')
LOADED=re.compile(r'loaded (\d+) declarations, (\d+) exprs \((\d+) unique\), (\d+) names in ([0-9.e+-]+)s')
CHECKED=re.compile(r'checked (\d+) declarations, (\d+) failed, (\d+) added unchecked, in ([0-9.e+-]+)s; (\d+) reduction steps; (\d+) exprs live')

def classify(receipt,stdout,stderr,expected_declarations,expected_rejection=None):
    try: safe(receipt)
    except ValueError as e: return dict(verdict='PROCESS_CONTROL_FAILURE',reason=str(e))
    if receipt['exit_code']<0: return dict(verdict='PROCESS_FAILURE')
    if stdout: return dict(verdict='OUTPUT_CONTRACT_FAILURE')
    lines=stderr.decode('utf-8',errors='strict').splitlines()
    loaded=[LOADED.fullmatch(x) for x in lines if x.startswith('loaded ')]
    if len(loaded)!=1 or not loaded[0] or int(loaded[0][1])!=expected_declarations:
        return dict(verdict='PARSER_OR_OUTPUT_FAILURE')
    fail=[x for x in lines if x.startswith('FAIL ')]
    if fail:
        if receipt['exit_code']==1 and len(fail)==1 and expected_rejection and fail[0]==expected_rejection:
            return dict(verdict='INTENDED_REJECT',diagnostic=fail[0])
        return dict(verdict='SEMANTIC_REJECTION_OTHER',diagnostics=fail)
    if receipt['exit_code']!=0: return dict(verdict='PROCESS_OR_PARSE_FAILURE')
    checked=[CHECKED.fullmatch(x) for x in lines if x.startswith('checked ')]
    machines=[MACHINE.fullmatch(x) for x in lines if x.startswith('machine: ')]
    if len(checked)!=1 or not checked[0] or [int(checked[0][i]) for i in [1,2,3]]!=[expected_declarations,0,0] or len(machines)!=1 or not machines[0]:
        return dict(verdict='OUTPUT_CONTRACT_FAILURE')
    if any(x.startswith(('error:','FAIL ','skip ','unknown option')) for x in lines):
        return dict(verdict='OUTPUT_CONTRACT_FAILURE')
    return dict(verdict='ACCEPT',machine=dict(zip(['app','bvar','beta','let','delta','iota','proj','enter_value','enter_delayed','re_eval','memo_hit','memo_insert'],map(int,machines[0].groups()))),
                declarations=expected_declarations,reduction_steps=int(checked[0][5]))

def main():
    parser=argparse.ArgumentParser(); parser.add_argument('command',choices=['prepare','freeze-build','build']); parser.add_argument('--attempt',default='build-0001')
    args=parser.parse_args()
    result={'prepare':prepare,'freeze-build':freeze_build,'build':lambda:build(args.attempt)}[args.command]()
    print(json.dumps(result,indent=2))

if __name__=='__main__': main()
