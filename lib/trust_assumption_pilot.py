"""Exact transitive-assumption reporting pilot and negative-capable receipt audit.

Reuses Lean's report parser. This is a policy/transport audit, not a semantic
oracle or independent kernel. Prior attempts are immutable and version-bound.
"""
from __future__ import annotations
import hashlib
import json
import os
import re
from pathlib import Path
import subprocess
import time
from datetime import datetime, timezone

from lib.metamorphic_pilot_runner_v3 import run_supervised

ROOT = Path(__file__).resolve().parents[1]
BASE = Path('results/research/trust-assumption-pipeline-pilot-1')
PATHS = ['local-body-traversal', 'imported-olean-metadata']

TOOLING_PATHS = ['lib/trust_assumption_pilot.py', 'scripts/trust-assumption-pilot-1', 'tests/test_trust_assumption_pilot.py', 'lib/metamorphic_pilot_runner_v3.py', 'lib/metamorphic_pilot_runner.py']
SOURCE_PATHS = ['results/research/trust-assumption-pipeline-pilot-1/sources/Lean/Util/CollectAxioms.lean', 'results/research/trust-assumption-pipeline-pilot-1/sources/Lean/Elab/Print.lean', 'results/research/trust-assumption-pipeline-pilot-1/sources/Lean/Meta/Native.lean', 'results/research/trust-assumption-pipeline-pilot-1/sources/Lean/CoreM.lean', 'results/research/trust-assumption-pipeline-pilot-1/sources/Lean/Elab/Term/TermElabM.lean', 'results/research/trust-assumption-pipeline-pilot-1/sources/Lean/Elab/Tactic/Decide.lean', 'results/research/trust-assumption-pipeline-pilot-1/sources/Lean/Meta/Sorry.lean', 'results/research/trust-assumption-pipeline-pilot-1/sources/Lean/AddDecl.lean', 'results/research/trust-assumption-pipeline-pilot-1/sources/Init/Core.lean', 'results/research/trust-assumption-pipeline-pilot-1/sources/Init/Prelude.lean', 'results/research/trust-assumption-pipeline-pilot-1/sources/Init/Classical.lean', 'results/research/trust-assumption-pipeline-pilot-1/sources/Lean/Elab/MutualDef.lean', 'results/research/trust-assumption-pipeline-pilot-1/sources/Lean/Modifiers.lean', 'results/research/trust-assumption-pipeline-pilot-1/sources/Lean/PrivateName.lean', 'results/research/trust-assumption-pipeline-pilot-1/sources/Lean/Message.lean', 'results/research/trust-assumption-pipeline-pilot-1/sources/Lean/PrettyPrinter.lean', 'results/research/trust-assumption-pipeline-pilot-1/sources/Lean/PrettyPrinter/Delaborator/Options.lean', 'results/research/trust-assumption-pipeline-pilot-1/sources/Lean/PrettyPrinter/Delaborator/Builtins.lean']
COMPARATOR_PATHS = ['results/research/trust-assumption-pipeline-pilot-1/sources/comparator-Axioms.lean', 'results/research/trust-assumption-pipeline-pilot-1/sources/comparator-Comparator.lean', 'results/research/trust-assumption-pipeline-pilot-1/sources/comparator-tip.json']
CLAIM_LIMITS = ['Two reporting routes within official Lean 4.33.0, not independent implementations.', 'Assumption preservation does not establish soundness.', 'Compiled module export is .olean axiom metadata, not lean4export NDJSON.', 'Permission consumer is local reporting policy, not executed Comparator or kernel refusal.']


def require(ok, message):
    if not ok:
        raise ValueError(message)


def read(path):
    def unique(pairs):
        out = {}
        for k, v in pairs:
            require(k not in out, 'duplicate JSON key')
            out[k] = v
        return out
    return json.loads(Path(path).read_text(), object_pairs_hook=unique)


def write(path, value):
    Path(path).write_text(json.dumps(value, indent=2) + '\n')


def bind(path):
    path = Path(path)
    return {'path':str(path), 'bytes':path.stat().st_size,
            'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}


def verify(binding, root=ROOT):
    path = root / binding['path']
    require(path.is_file(), 'missing bound file: '+str(path))
    require(path.stat().st_size == binding['bytes'] and
            hashlib.sha256(path.read_bytes()).hexdigest() == binding['sha256'],
            'file binding mismatch: '+str(path))
    return path


def committed(binding, commit='HEAD'):
    verify(binding)
    data = subprocess.check_output(['git','show',f'{commit}:{binding["path"]}'], cwd=ROOT)
    require(hashlib.sha256(data).hexdigest() == binding['sha256'], 'uncommitted bound input')


def _reports(stdout, names):
    """Adapt the retained CVC parser for exact private Names with numeric components.

    Do not strip private prefixes or normalize names to user spellings.
    """
    pattern = re.compile(r"^'([^\n]+)' (?:does not depend on any axioms|depends on axioms:\s*(\[[^\]]*\]))[ \t]*$", re.M)
    found, spans = {}, []
    for match in pattern.finditer(stdout):
        name, listing = match.group(1), match.group(2)
        require(name in names and name not in found, 'unexpected or duplicate axiom report')
        items = [] if listing is None or listing == '[]' else [x.strip() for x in listing[1:-1].split(',')]
        require(all(re.fullmatch(r"[A-Za-z_][A-Za-z_0-9']*(?:\.(?:[A-Za-z_][A-Za-z_0-9']*|[0-9]+))*", x) for x in items), 'malformed full axiom list')
        require(len(items) == len(set(items)), 'duplicate axiom')
        found[name] = items
        spans.append(match.span())
    require(set(found) == set(names), 'missing required full axiom report')
    remainder = stdout
    for start, end in reversed(spans): remainder = remainder[:start] + remainder[end:]
    return found, remainder


def report_rows(stdout, stderr, fixtures):
    require(not stderr.strip(), 'unexpected stderr')
    names = [f['target'] for f in fixtures]
    reports, remainder = _reports(stdout, names)
    require(not remainder.strip(), 'unclaimed report output')
    require(list(reports) == names, 'report order mismatch')
    return [{'fixture':f['id'], 'target':f['target'], 'actual_axioms': sorted(reports[f['target']]),
             'expected_axioms':f['expected_axioms'],
             'preserved': sorted(reports[f['target']]) == sorted(f['expected_axioms'])}
            for f in fixtures]


def permission(axioms, allowed):
    require(len(axioms) == len(set(axioms)) and len(allowed) == len(set(allowed)),
            'duplicate policy member')
    forbidden = sorted(set(axioms) - set(allowed))
    return {'status':'DENIED' if forbidden else 'PERMITTED', 'unpermitted_axioms':forbidden}


def safety(receipt):
    require(receipt['cleanup_complete'] and not receipt['timed_out'] and
            not receipt['memory_exceeded'] and receipt['memory_monitor_error'] is None and
            receipt['memory_monitor_samples'] > 0 and receipt['maximum_observed_rss_bytes'] > 0,
            'process-safety failure; repair before another launch')


def validate_protocol(p, root=ROOT):
    require(set(p)=={'schema_version','item_id','tooling_revision','scientific_manifest','runtime_manifest','reuse_review','host_tools','tooling','launch_gate','supervisor','failure_policy','prelaunch_review','focused_validation'}, 'protocol fields')
    require(p['schema_version']==1 and p['item_id']=='TRUST-ASSUMPTION-PIPELINE-PILOT-1', 'protocol identity')
    require([b['path'] for b in p['tooling']]==TOOLING_PATHS, 'tooling inventory')
    for field,filename in [('scientific_manifest','scientific-manifest.json'),('runtime_manifest','runtime-manifest.json'),('reuse_review','source-reuse-review.json'),('host_tools','host-tools.json'),('prelaunch_review','prelaunch-review.json'),('focused_validation','focused-prelaunch.log')]:
        require(p[field]['path']==str(BASE/filename), 'mandatory protocol input path')
    s = read(verify(p['scientific_manifest'], root))
    runtime = read(verify(p['runtime_manifest'], root))
    require(runtime['toolchain']=='leanprover/lean4:v4.33.0', 'runtime identity')
    verify(p['reuse_review'], root)
    verify(p['host_tools'], root)
    verify(p['prelaunch_review'],root)
    verify(p['focused_validation'],root)
    for binding in p['tooling']: verify(binding, root)
    require([b['path'] for b in s['fixture_bindings']]==[str(BASE/'fixtures/ImportedReports.lean'),str(BASE/'fixtures/TrustFixtures.lean')], 'fixture file inventory')
    for binding in s['fixture_bindings']: verify(binding, root)
    sm = read(verify(s['source_manifest'], root))
    require(sm['toolchain']=='leanprover/lean4:v4.33.0' and sm['comparator_revision']=='32bd61da1d68fbaa310234964e9b820b03a0f82f', 'source identity')
    require([b['path'] for b in sm['sources']]==SOURCE_PATHS and [b['path'] for b in sm['comparator_sources']]==COMPARATOR_PATHS, 'source evidence inventory')
    for binding in sm['sources'] + sm['comparator_sources']:
        verify({k:binding[k] for k in ('path','bytes','sha256')}, root)
    require(set(s)=={'schema_version','item_id','fixtures','paths','cells','permission_control','fixture_bindings','source_manifest','claim_limits','safety'}, 'scientific fields')
    require(s['schema_version']==1 and s['item_id']=='TRUST-ASSUMPTION-PIPELINE-PILOT-1' and s['claim_limits']==CLAIM_LIMITS, 'scientific identity/claim scope')
    require(s['paths'] == PATHS and len(s['fixtures']) == 6, 'scientific matrix shape')
    require([f['id'] for f in s['fixtures']]==['pure','explicitLeaf','propextLeaf','choiceLeaf','sorryLeaf','nativeLeaf'], 'fixture identity/order')
    require([f['target'] for f in s['fixtures']]==['TrustAssumptionPilot.'+f['id'] for f in s['fixtures']], 'fixture targets')
    for fixture in s['fixtures']:
        require(set(fixture)=={'id','target','expected_axioms'} and len(fixture['expected_axioms'])==len(set(fixture['expected_axioms'])), 'fixture shape/duplicate axiom')
    require(s['cells'] == [{'path':route,'fixture':f['id']} for route in PATHS for f in s['fixtures']], 'scientific cell order')
    require(s['permission_control']=={'target':'explicitLeaf','sufficient':['TrustAssumptionPilot.explicit'],'insufficient':[], 'expected':['PERMITTED','DENIED'],'paths':PATHS}, 'permission control contract')
    require(s['safety']=={'timeout_seconds':120,'memory_bytes':2147483648,'failures':'REPAIR_AND_CONTINUE'}, 'process controls')
    return s


def protocol(root=ROOT, name='protocol-r1.json'):
    p = read(root/BASE/name)
    return p, validate_protocol(p,root)


def required_inputs(protocol_binding,p,s,root=ROOT):
    sm=read(root/s['source_manifest']['path'])
    sources=[{k:b[k] for k in ('path','bytes','sha256')} for b in sm['sources']+sm['comparator_sources']]
    return [protocol_binding,p['scientific_manifest'],p['runtime_manifest'],p['reuse_review'],p['host_tools'],
            *p['tooling'],*s['fixture_bindings'],s['source_manifest'],*sources,p['prelaunch_review'],p['focused_validation']]


def command_contract(route, attempt, runtime, producer_dir=None, root=ROOT):
    toolchain=Path(runtime['root'])
    module_dir=str(attempt) if route==PATHS[0] else str(producer_dir)
    environment={'PATH':str(toolchain/'bin')+':/usr/bin:/bin','HOME':runtime['home'],
                 'LEAN_PATH':module_dir,'LANG':'C.UTF-8'}
    argv=[str(toolchain/'bin/lean')]
    argv+=['-o',str(attempt/'TrustFixtures.olean'),'TrustFixtures.lean'] if route==PATHS[0] else ['ImportedReports.lean']
    return argv,environment,str(root/BASE/'fixtures')


def verify_runtime(p):
    runtime = read(verify(p['runtime_manifest']))
    base = Path(runtime['root'])
    seen = []
    for section in ('bin','lib'):
        for file in sorted((base/section).rglob('*')):
            if file.is_symlink():
                seen.append({'path':str(file.relative_to(base)), 'symlink':str(file.readlink())})
            elif file.is_file():
                b = bind(file); b['path'] = str(file.relative_to(base)); seen.append(b)
    require(seen == runtime['files'], 'installed runtime differs from frozen inventory')
    return base


def execute(route, protocol_name='protocol-r1.json', producer=None):
    os.chdir(ROOT)
    p,s = protocol(name=protocol_name)
    require(route in PATHS, 'unknown reporting path')
    review=read(verify(p['prelaunch_review']))
    require(review['status']=='PASS', 'independent prelaunch review not cleared')
    require(review['scientific_manifest']==p['scientific_manifest'] and review['tooling']==p['tooling'], 'stale independent review')
    require('\nOK\n' in verify(p['focused_validation']).read_text(), 'focused validation not passing')
    bindings = required_inputs(bind(BASE/protocol_name),p,s)
    for b in bindings: committed(b)
    toolchain = verify_runtime(p)
    for binary in read(verify(p['host_tools']))['binaries']: verify(binary)
    execution = ROOT/BASE/'execution'; execution.mkdir(exist_ok=True)
    # All earlier launch safety states must be reconciled before continuing.
    for old in sorted(execution.glob('attempt-*/receipt.json')): safety(read(old))
    attempt = execution/f'attempt-{len(list(execution.glob("attempt-*")))+1:04d}'
    attempt.mkdir()
    generated = None
    if route == PATHS[1]:
        require(producer is not None, 'import needs generated module binding')
        generated = bind(Path(producer)); committed(generated)
        exported = read(producer)
        require(exported['route'] == PATHS[0], 'producer route mismatch')
        for b in exported['module_files']: verify(b)
        module_dir = str((ROOT/exported['module_files'][0]['path']).parent)
    else:
        module_dir = str(attempt)
    argv,environment,cwd=command_contract(route,attempt,read(verify(p['runtime_manifest'])),module_dir)
    launch = {'schema_version':1, 'route':route, 'commit':subprocess.check_output(['git','rev-parse','HEAD']).decode().strip(),
              'started_at':datetime.now(timezone.utc).isoformat(), 'monotonic_start':time.monotonic(),
              'protocol':bind(BASE/protocol_name), 'generated_module_manifest':generated,
              'argv':argv, 'cwd':cwd, 'environment':environment, 'inputs':bindings}
    write(attempt/'launch.json', launch)
    try:
        receipt = run_supervised(argv=argv,cwd=ROOT/BASE/'fixtures',stdin=None,env=environment,
            timeout_seconds=s['safety']['timeout_seconds'],memory_bytes=s['safety']['memory_bytes'],
            raw_prefix=attempt/'process')
        write(attempt/'receipt.json',receipt)
        safety(receipt)
        require(receipt['exit_code']==0,'compiler failure; retain and diagnose this attempt')
        rows=report_rows((ROOT/receipt['raw_stdout_path']).read_text(),(ROOT/receipt['raw_stderr_path']).read_text(),s['fixtures'])
        observed={'route':route,'launch':bind((attempt/'launch.json').relative_to(ROOT)),
                  'receipt':bind((attempt/'receipt.json').relative_to(ROOT)),'rows':rows}
        if route == PATHS[0]:
            observed['module_files']=[bind(x.relative_to(ROOT)) for x in sorted(attempt.glob('TrustFixtures.olean*'))]
            require(any(x['path'].endswith('.olean') for x in observed['module_files']), 'missing .olean')
        write(attempt/'observation.json',observed)
        print(str((attempt/'observation.json').relative_to(ROOT)))
    except BaseException as exc:
        write(attempt/'failure.json',{'error':str(exc),'type':type(exc).__name__,'recorded_at':datetime.now(timezone.utc).isoformat()})
        raise


def rebuild_result(observation_bindings, root=ROOT):
    require(len(observation_bindings)==2, 'exactly two observations required')
    cells=[]; controls=[]
    scientific=None
    for route, ob in zip(PATHS,observation_bindings):
        observation=read(verify(ob,root)); require(observation['route']==route,'observation path order')
        launch=read(verify(observation['launch'],root))
        require(launch['route']==route,'launch path mismatch')
        protocol_binding=launch['protocol']; proto=read(verify(protocol_binding,root))
        s=validate_protocol(proto,root)
        review=read(verify(proto['prelaunch_review'],root))
        require(review['status']=='PASS' and review['scientific_manifest']==proto['scientific_manifest'] and review['tooling']==proto['tooling'], 'missing/stale launch clearance')
        require(launch['inputs']==required_inputs(protocol_binding,proto,s,root), 'incomplete launch inputs')
        if root==ROOT:
            for b in launch['inputs']: committed(b,launch['commit'])
        if scientific is None: scientific=proto['scientific_manifest']
        require(scientific==proto['scientific_manifest'],'mixed scientific inputs')
        require(s['paths']==PATHS and s['cells']==[{'path':p,'fixture':f['id']} for p in PATHS for f in s['fixtures']], 'matrix mismatch')
        receipt=read(verify(observation['receipt'],root)); safety(receipt)
        require(receipt['exit_code']==0,'unsuccessful report process')
        producer_dir=None
        if route==PATHS[1]:
            producer=read(verify(observation_bindings[0],root))
            producer_dir=(root/producer['module_files'][0]['path']).parent
        original_root=Path(read(verify(proto['host_tools'],root))['repository_root'])
        if producer_dir is not None:producer_dir=original_root/producer_dir.relative_to(root)
        argv,environment,cwd=command_contract(route,(original_root/ob['path']).parent,read(verify(proto['runtime_manifest'],root)),producer_dir,original_root)
        require(launch['argv']==receipt['argv']==argv and launch['cwd']==receipt['cwd']==cwd and launch['environment']==environment, 'command/cwd/environment mismatch')
        prefix=str(Path(ob['path']).parent/'process')
        require(receipt['raw_stdout_path']==prefix+'.stdout' and receipt['raw_stderr_path']==prefix+'.stderr','swapped raw output path')
        for stream in ('stdout','stderr'):
            verify({'path':receipt['raw_'+stream+'_path'],'bytes':receipt[stream+'_bytes'],'sha256':receipt[stream+'_sha256']},root)
        rows=report_rows((root/receipt['raw_stdout_path']).read_text(),(root/receipt['raw_stderr_path']).read_text(),s['fixtures'])
        require(rows==observation['rows'],'raw-report observation mismatch')
        if route==PATHS[0]:
            require(observation['module_files'] and any(b['path'].endswith('/TrustFixtures.olean') for b in observation['module_files']), 'missing module output')
            for b in observation['module_files']:
                require(Path(b['path']).parent==Path(ob['path']).parent and Path(b['path']).name.startswith('TrustFixtures.olean'), 'module output path mismatch')
                verify(b,root)
        else:
            require(launch['generated_module_manifest']==observation_bindings[0],'import producer binding mismatch')
            if root==ROOT:committed(launch['generated_module_manifest'],launch['commit'])
        cells.extend({'path':route,**row} for row in rows)
        control=s['permission_control']; row=next(r for r in rows if r['fixture']==control['target'])
        for label,expected in zip(('sufficient','insufficient'),control['expected']):
            actual=permission(row['actual_axioms'],control[label])
            controls.append({'path':route,'fixture':control['target'],'policy':label,'allowed_axioms':control[label],
                             'expected':expected,**actual})
    return {'schema_version':1,'item_id':'TRUST-ASSUMPTION-PIPELINE-PILOT-1','scientific_manifest':scientific,
            'observations':observation_bindings,'cells':cells,'permission_controls':controls,
            'status':'SUCCESS' if all(c['preserved'] for c in cells) and all(c['expected']==c['status'] for c in controls) else 'MISMATCH',
            'claim_limits':s['claim_limits']}


def validate_result(root=ROOT):
    result=read(root/BASE/'result.json')
    require(result==rebuild_result(result['observations'],root),'canonical result mismatch')
    return result
