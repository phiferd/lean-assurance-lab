"""One prospectively fixed, real bundled E0 sample; never edits shared tooling."""
import hashlib
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from lib.resource_envelope_supervisor import run_direct

RUN = Path(__file__).resolve().parent
BIN = ROOT / 'external/lean-prebuilt/lean-4.35.0-rc2-darwin_aarch64/bin'
def save(p, value):
    p.write_text(json.dumps(value, indent=2) + '\n')

def invoke(name, argv, cwd, overrides=None):
    out = RUN / 'attempts' / name
    out.mkdir(parents=True, exist_ok=False)
    overrides = {'PATH': str(BIN) + ':' + os.environ['PATH'], **(overrides or {})}
    save(out / 'command.json', {'argv': argv, 'cwd': str(cwd), 'environment_overrides': overrides})
    result = run_direct(argv=argv, cwd=cwd, env={**os.environ, **overrides}, stdin_bytes=None,
        timeout_seconds=30, memory_ceiling_bytes=1024**3, sample_interval_seconds=.01,
        max_trace_gap_seconds=2, cleanup_seconds=2)
    (out / 'stdout').write_bytes(result.stdout)
    (out / 'stderr').write_bytes(result.stderr)
    save(out / 'receipt.json', result.receipt)
    r = result.receipt
    print(name, 'exit', r['exit_code'], result.stdout.decode(errors='replace')[:400], result.stderr.decode(errors='replace')[:400], flush=True)
    if (not r['cleanup_complete'] or not r['reap_complete'] or r['monitor_errors']
        or r['pipe_errors'] or r['accounting_error'] or r['stop_reason'] or r['trace_gap_fault']):
        raise RuntimeError('Pause: supervision fault; retained ' + name)
    return r['exit_code']

if __name__ == '__main__':
    if invoke('00-lean-version', [str(BIN / 'lean'), '--version'], RUN):
        raise RuntimeError('Lean identity capability failed')
    if invoke('01-nanoda-help', [str(BIN / 'nanoda_bin'), '--help'], RUN):
        raise RuntimeError('Nanoda identity capability failed')
    results = []
    for case in ('clean', 'standard', 'sorry', 'custom'):
        cwd = RUN / 'fixtures' / case
        if invoke(case + '-compile', [str(BIN / 'lean'), '-o', 'Foo.olean', 'Foo.lean'], cwd):
            raise RuntimeError('Fixture compilation failed: ' + case)
        if invoke(case + '-export', [str(BIN / 'leanexport'), 'Foo'], cwd, {'LEAN_PATH': str(cwd)}):
            raise RuntimeError('Exporter failed: ' + case)
        export = RUN / 'attempts' / (case + '-export') / 'stdout'
        (cwd / 'export.txt').write_bytes(export.read_bytes())
        for toggle in ([False, True] if case == 'sorry' else [False]):
            config = cwd / ('config-' + str(toggle).lower() + '.json')
            status = invoke(case + '-check-' + str(toggle).lower(), [str(BIN / 'nanoda_bin'), str(config)], cwd)
            expected = 0 if case in ('clean', 'standard') or (case == 'sorry' and toggle) else 'nonzero'
            results.append({'case': case, 'allow_sorry': toggle, 'expected_exit': expected, 'observed_exit': status,
                'selected_module': 'Foo', 'export_sha256': hashlib.sha256(export.read_bytes()).hexdigest(),
                'config_sha256': hashlib.sha256(config.read_bytes()).hexdigest(),
                'matches_expected_exit': status == 0 if expected == 0 else status != 0})
    save(RUN / 'observations.json', {'evidence_class': 'E0', 'scope': 'direct bundled Darwin arm64 calls; exact PR192 config; no script/CI/fallback claim', 'results': results})
