"""Fresh affected-domain replay; no historical source or script is rewritten."""
import argparse, hashlib, json, os, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RUN = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from lib.resource_envelope_supervisor import run_direct

p = argparse.ArgumentParser()
p.add_argument('--compiler', type=Path, required=True)
p.add_argument('--cache', type=Path, required=True)
p.add_argument('--source', type=Path, required=True)
p.add_argument('--destination', type=Path, required=True)
a = p.parse_args()
a.compiler = a.compiler.resolve()
a.cache = a.cache.resolve()
a.source = a.source.resolve()
a.destination = a.destination.resolve()
pre = json.loads((RUN / 'preflight.json').read_text())
locked = json.loads((RUN / 'fresh-replay-inputs.json').read_text())
assert hashlib.sha256(a.compiler.read_bytes()).hexdigest() == pre['compiler_sha256']
for path, h in locked['prior_published_olean_sha256'].items():
    assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == h
for name, h in locked['new_source_sha256'].items():
    assert hashlib.sha256((a.source / (name + '.lean')).read_bytes()).hexdigest() == h
records = json.loads((ROOT / 'results/research/tree2-confirmed-integration-1/confirmation/module-records.json').read_text())
assert len(records) == pre['validated_cached_modules']
for rec in records:
    parts = Path(rec['argv'][2]).parts
    pos = parts.index('confirmation-fresh')
    relocated = a.cache.joinpath(*parts[pos + 1:])
    assert hashlib.sha256(relocated.read_bytes()).hexdigest() == rec['olean_sha256']
a.destination.mkdir(parents=True, exist_ok=False)
env = dict(os.environ)
env['LEAN_PATH'] = ':'.join(map(str, [a.destination,
    ROOT / 'explorations/runs/EXPLORE-TREE2-ARROW-TOWER-1/fresh-replay',
    a.cache / 'fresh-proofs', a.cache / 'fresh-imports']))
for k in ['LEAN_SRC_PATH', 'LEAN_SYSROOT']:
    env.pop(k, None)
for module in locked['new_modules']:
    source = a.destination / (module + '.lean')
    source.write_bytes((a.source / (module + '.lean')).read_bytes())
    for label, argv in [('deps', [str(a.compiler), '--deps', str(source)]),
                        ('compile', [str(a.compiler), '-o', str(source.with_suffix('.olean')), str(source)])]:
        prefix = module + '-' + label
        (a.destination / (prefix + '-command.json')).write_text(json.dumps(dict(
            argv=argv, cwd=str(a.destination), LEAN_PATH=env['LEAN_PATH'],
            source_sha256=hashlib.sha256(source.read_bytes()).hexdigest()), indent=2) + '\n')
        r = run_direct(argv=argv, cwd=a.destination, env=env, stdin_bytes=None,
            timeout_seconds=3600, memory_ceiling_bytes=16*1024**3,
            sample_interval_seconds=.5, max_trace_gap_seconds=3,
            cleanup_seconds=10, output_cap_bytes=20000000)
        (a.destination / (prefix + '-stdout.log')).write_bytes(r.stdout)
        (a.destination / (prefix + '-stderr.log')).write_bytes(r.stderr)
        (a.destination / (prefix + '-receipt.json')).write_text(json.dumps(r.receipt, indent=2) + '\n')
        print(module, label, json.dumps({k:r.receipt.get(k) for k in [
            'exit_code', 'elapsed_seconds', 'cleanup_complete', 'stop_reason',
            'maximum_sampled_group_rss_bytes']}), flush=True)
        print(r.stdout.decode(errors='replace'), flush=True)
        if r.receipt['exit_code'] != 0:
            sys.exit(1)
print('PASS: fresh6 domain modules, prior7 published imports and108 cache hashes checked.')
