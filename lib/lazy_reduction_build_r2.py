"""R2 preserves clang++ driver spelling; R1's realpath selected C linkage."""
import argparse
import json
import os
from pathlib import Path
import subprocess
from lib import lazy_reduction_pilot as p

MANIFEST=p.BASE/'build-manifest-r2.json'
MODULE=Path('lib/lazy_reduction_build_r2.py')

def corrected_driver(argv):
    result=list(argv)
    result[0]='/Library/Developer/CommandLineTools/usr/bin/clang++'
    return result

def freeze():
    p.active(); old=p.load(p.BASE/'build-manifest-r1.json')
    value=dict(old)
    value['argv']=corrected_driver(old['argv'])
    value['predecessor']=p.bind(p.BASE/'build-manifest-r1.json')
    value['repair']=p.bind(p.BASE/'build-repair-r2.json')
    value['driver_invocation_path']=value['argv'][0]
    value['driver_resolves_to']=str(Path(value['argv'][0]).resolve())
    value['tooling']=[*old['tooling'],p.bind(MODULE),p.bind(Path('scripts/build-lazy-reduction-r2')),p.bind(Path('tests/test_lazy_reduction_build_r2.py'))]
    dry=subprocess.run([*value['argv'],'-###'],capture_output=True,text=True,env=p.ENV)
    value['dry_link_command']=dry.stdout+dry.stderr
    p.write_new(p.BASE/'dry-link-r2.json',dict(argv=[*value['argv'],'-###'],exit_code=dry.returncode,stdout=dry.stdout,stderr=dry.stderr,compilation=False))
    if dry.returncode: raise ValueError('dry link inspection failed; raw output preserved')
    if '"-lc++"' not in value['dry_link_command']: raise ValueError('C++ runtime not selected')
    p.write_new(MANIFEST,value); return {'manifest':str(MANIFEST),'cxx_runtime':True}

def build():
    p.active(); m=p.load(MANIFEST)
    p.require_committed([p.bind(MANIFEST),m['repair'],m['predecessor'],m['source'],m['patch_review'],*m['tooling'],*m['scan_receipts']])
    if Path(m['driver_invocation_path']).resolve()!=Path(m['driver_resolves_to']): raise ValueError('driver resolution changed')
    for row in m['dependencies']: p.verify(row)
    for row in m['scan_receipts']:
        r=p.load(Path(row['path'])); p.safe(r); p.raw(r)
    if (p.ROOT/p.BINARY).exists(): raise ValueError('output already exists')
    out=p.BASE/'build-0002'
    if (p.ROOT/out).exists(): raise ValueError('attempt already exists')
    (p.ROOT/out).mkdir()
    receipt=p.run_supervised(argv=m['argv'],cwd=p.ROOT,stdin=None,env=m['environment'],timeout_seconds=m['timeout_seconds'],memory_bytes=m['memory_bytes'],raw_prefix=p.ROOT/out/'build')
    result=dict(item_id=p.ITEM,manifest=p.bind(MANIFEST),receipt=receipt)
    if receipt['exit_code']==0 and (p.ROOT/p.BINARY).is_file() and os.access(p.ROOT/p.BINARY,os.X_OK): result['binary']=p.bind(p.BINARY)
    p.write_new(out/'result.json',result); p.safe(receipt)
    if 'binary' not in result: raise ValueError('build did not produce a new executable')
    for row in m['dependencies']: p.verify(row)
    return {'binary':result['binary'],'elapsed_seconds':receipt['elapsed_seconds']}

def main():
    parser=argparse.ArgumentParser(); parser.add_argument('command',choices=['freeze','build']); args=parser.parse_args()
    print(json.dumps(freeze() if args.command=='freeze' else build(),indent=2))

if __name__=='__main__': main()
