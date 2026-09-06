#!/usr/bin/env python3
"""Build/check the CVC-PREP-1 closure from checkpoint-bound inputs and raw ledger.

Default validation is clone-safe; --check-local additionally rehashes the exact
installed runtime and isolated source/output bundle. No Lean process is run.
"""
import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from lib import cvc_prep as prep


def load(path):
    return json.loads(Path(path).read_text())


def require(ok, message):
    if not ok:
        raise ValueError(message)


def binding(path, relative_to=ROOT):
    return {'path': str(path.relative_to(relative_to)), 'bytes': path.stat().st_size,
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def check_bytes(row, data):
    require(len(data) == row.get('bytes', len(data)) and hashlib.sha256(data).hexdigest() == row['sha256'],
            'binding mismatch: ' + row['path'])


def committed(checkpoint, path):
    return subprocess.check_output(['git', 'show', checkpoint + ':' + path], cwd=ROOT)


def verify_output_set(root, build, expected):
    """Read-only closure check; it does not repair or rerun the bound controller."""
    actual = prep.inventory(root, build)
    require(len({r['path'] for r in expected}) == len(expected), 'duplicate output receipt')
    require({r['path']: r for r in actual} == {r['path']: r for r in expected},
            'changed, missing or additional output bytes')
    return actual


def summarize():
    marker = load(OUT / 'execution/start.json')
    checkpoint = marker['checkpoint_commit']
    manifest_bytes = committed(checkpoint, prep.MANIFEST)
    require(hashlib.sha256(manifest_bytes).hexdigest() == marker['manifest_sha256'], 'checkpoint manifest changed')
    require((ROOT / prep.MANIFEST).read_bytes() == manifest_bytes, 'current manifest differs from execution checkpoint')
    manifest = json.loads(manifest_bytes)
    for row in [manifest[k] for k in ('source_closure', 'runtime_manifest', 'work_record', 'controller', 'tests')] + manifest['immutable_bindings']:
        check_bytes(row, committed(checkpoint, row['path']))
        if row['path'] != manifest['work_record']['path']:
            check_bytes(row, (ROOT / row['path']).read_bytes())
    q = json.loads(committed(checkpoint, 'config/research-queue.json'))
    require(q['selected_item'] == 'CVC-PREP-1' and next(r for r in q['items'] if r['id'] == 'CVC-PREP-1')['status'] == 'ACTIVE',
            'checkpoint did not authorize selected item')
    receipt = json.loads(committed(checkpoint, str((OUT / 'inert-test-receipt.json').relative_to(ROOT))))
    require(receipt['status'] == 'PASS', 'missing committed inert checks')
    actual_test_counts = []
    for check in receipt['checks']:
        raw = committed(checkpoint, check['log'])
        check_bytes({'path': check['log'], 'sha256': check['log_sha256']}, raw)
        require(check['returncode'] == 0 and raw.rstrip().endswith(b'OK'), 'prelaunch tests failed')
        counts = re.findall(rb'^Ran (\d+) tests? in ', raw, re.MULTILINE)
        require(len(counts) == 1, 'ambiguous test count')
        actual_test_counts.append(int(counts[0]))
    require(actual_test_counts == [20, 8], 'prelaunch test coverage changed')
    erratum = load(OUT / 'prelaunch-receipt-erratum.json')
    require(erratum['recorded_runtime_tests'] == receipt['runtime_tests'] == 9
            and erratum['actual_runtime_tests'] == actual_test_counts[1], 'receipt erratum differs')
    for row in receipt['tested_files']:
        check_bytes(row, committed(checkpoint, row['path']))
    commands = load(OUT / 'command-manifest.json')['commands']
    closure = load(ROOT / manifest['source_closure']['path'])['closure']
    modules = {r['module']: r for r in closure['modules'] if r['kind'] != 'core_runtime'}
    state = prep.derive(prep.read_events(OUT / 'execution/events.jsonl'))
    require(set(state) == set(range(len(state))), 'reservation numbering')
    attempts, outputs, seconds = [], [], 0.
    for number, row in state.items():
        if number == 0:
            continue
        require('terminal' in row, 'unreconciled orphan')
        term, command = row['terminal'], commands[number - 1]
        require(row['module'] == closure['topological_noncore_order'][number - 1] == command['module'], 'module order')
        require(row['argv'] == command['argv'] and row['cwd'] == command['cwd']
                and row['env'] == manifest['compiler']['env'], 'command changed')
        require(row['source_sha256'] == modules[row['module']]['source']['sha256']
                and row['runtime_manifest_sha256'] == manifest['runtime_manifest']['sha256'], 'launch inputs changed')
        require(row['prior_outputs'] == outputs, 'prior output binding changed')
        initial_work = json.loads(committed(checkpoint, manifest['work_record']['path']))
        before = {n: r for n, r in state.items() if n < number}
        allowed = prep.attempt_budget(initial_work, before, datetime.fromisoformat(row['at']))
        require(0 < row['reserved_seconds'] <= allowed + 1e-6, 'reservation exceeds active/compilation budget')
        for stream in ('stdout', 'stderr'):
            path = ROOT / row[stream]
            require(path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest() == term[stream + '_sha256'], 'raw log changed')
        if term['status'] == 'COMPLETE':
            require(term['returncode'] == 0 and 0 <= term['charged_seconds'] <= row['reserved_seconds'], 'invalid success charge')
            expected = manifest['materialization']['build_root'] + '/' + row['module'].replace('.', '/') + '.olean'
            require(expected in {r['path'] for r in term['outputs']}, 'successful olean missing')
            outputs.extend(term['outputs'])
        else:
            require(number == max(state), 'execution continued after first failure')
        seconds += term['charged_seconds']
        attempts.append({'number': number, 'module': row['module'], 'status': term['status'],
                         'seconds': term['charged_seconds'], 'outputs': term.get('outputs', [])})
    require(len(attempts) <= 37 and seconds <= 6600, 'compilation bound exceeded')
    successful = len(attempts) == 37 and all(r['status'] == 'COMPLETE' for r in attempts)
    work = load(OUT / 'work-record.json')
    require(work['status'] == 'COMPLETE' and work['ended_at'], 'item work ledger is not closed')
    elapsed = sum((datetime.fromisoformat(s['ended_at']) - datetime.fromisoformat(s['started_at'])).total_seconds()
                  for s in work['sessions'])
    require(0 < elapsed <= 10800 and len(work['sessions']) <= 2, 'active/session bound')
    require(all(0 <= (datetime.fromisoformat(s['ended_at']) - datetime.fromisoformat(s['started_at'])).total_seconds() <= 5400
                for s in work['sessions']), 'session duration')
    fixtures = [json.loads(line) for line in (OUT / 'fixture-ledger.jsonl').read_text().splitlines()]
    fixture_launches = sum(r.get('reserved_launches', 0) for r in fixtures)
    fixture_seconds = sum(r.get('charged_seconds', 0) for r in fixtures)
    require(fixture_launches <= 80 and fixture_seconds <= 400, 'fixture bound')
    require(work['compilation_attempts'] == len(attempts) and work['compilation_seconds'] == seconds
            and work['fixture_process_launches'] == fixture_launches and work['fixture_process_seconds'] == fixture_seconds,
            'work ledger counters differ')
    runtime = load(OUT / 'runtime-manifest.json')
    return {'schema_version': 1, 'item_id': 'CVC-PREP-1', 'run_id': prep.RUN,
            'outcome': 'SUCCESS' if successful else 'BOUNDED_UNRESOLVED',
            'scientific_status': 'UPSTREAM_DEPENDENCY_BUNDLE_PREPARED' if successful else 'DEPENDENCY_PREPARATION_STOPPED',
            'checkpoint_commit': checkpoint, 'manifest': binding(ROOT / prep.MANIFEST),
            'module_count': 37, 'compilation_attempts': len(attempts),
            'completed_modules': sum(r['status'] == 'COMPLETE' for r in attempts),
            'compilation_seconds': seconds, 'attempts': attempts, 'outputs': outputs,
            'runtime_files': sum(r['type'] == 'file' for r in runtime['files']),
            'runtime_bytes': sum(r.get('bytes', 0) for r in runtime['files']),
            'prelaunch_checks': {'controller_tests': actual_test_counts[0], 'runtime_tests': actual_test_counts[1],
                                 'receipt_erratum': 'prelaunch-receipt-erratum.json'},
            'costs': {'preparation_active_seconds': elapsed, 'preparation_compilation_seconds': seconds,
                      'fixture_reserved_launches': fixture_launches, 'fixture_process_seconds': fixture_seconds,
                      'runner_active_seconds': 0, 'proof_attempts': 0, 'lab_elaborations': 0,
                      'checker_launches': 0, 'network_requests': 0, 'aggregate_active_seconds': elapsed,
                      'aggregate_note': 'Overlapping delegation is included once in wall-clock active sessions. Repository delivery/validation time after this item stop is retained separately.'},
            'recommendation': work['recommendation'],
            'stop': load(OUT / 'stop-diagnostic.json'),
            'scope': 'Availability of exact upstream dependency products only. No Lab signature or proof was elaborated. No theorem, axiom closure, executable-validator refinement, normative authority, or binary/OS correctness is established.',
            'runtime_limit': runtime['unresolved_inventory_interpretation'],
            'evidence': [binding(OUT / name) for name in ['execution/start.json', 'execution/events.jsonl', 'work-record.json',
                         'runtime-manifest.json', 'source-launch-review.json', 'inert-test-receipt.json', 'fixture-ledger.jsonl']]}


def report(result):
    recommendation = result['recommendation']
    return ('# CVC-PREP-1: exact upstream dependency preparation\n\n'
            + '**' + result['outcome'] + '** — `' + result['scientific_status'] + '`.\n\n'
            + f"{result['completed_modules']} of 37 modules completed in {result['compilation_attempts']} compiler launches, "
            + f"charging {result['compilation_seconds']:.3f} compilation seconds. The exact execution checkpoint is "
            + '`' + result['checkpoint_commit'] + '`. Sources, runtime, commands, reservations, raw logs and outputs are bound.\n\n'
            + result['scope'] + '\n\n'
            + '**Stop:** ' + result['stop']['interpretation'] + '\n\n'
            + f"Preparation used {result['costs']['preparation_active_seconds'] / 60:.2f} active minutes and "
            + f"{result['costs']['fixture_reserved_launches']} reserved inert process attempts, including failed starts and fixture children. "
            + 'All fit the two 90-minute sessions, 37 launches, 300 seconds per launch and 6600 compilation-second caps. '
            + 'Runner development and proof costs remain zero; preparation cost is retained for aggregate reporting.\n\n'
            + result['runtime_limit'] + '\n\n'
            + 'The initial inventory assembler failure and early engineering/test failures remain in the diagnostic and validation records. '
            + 'The final controller/runtime acceptance tests passed before the first Lean launch.\n\n'
            + 'The immutable checkpoint receipt lists 9 runtime tests; its bound raw log records 8. '
            + 'A separate receipt erratum preserves that counting error. Actual prelaunch totals were 20 controller plus 8 runtime tests, all passing.\n\n'
            + '**Recommendation:** ' + recommendation['action'] + ' Target: ' + recommendation['target']
            + '. Priority: ' + recommendation['priority'] + '. Prerequisites: ' + '; '.join(recommendation['prerequisites']) + '.\n\n'
            + 'Validate tracked evidence with `python3 results/research/conditional-validation-contracts/cvc-prep-1/validate-evidence.py`; '
            + 'add `--check-local` to verify the installed runtime and isolated payloads. No validator invocation launches Lean.\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    parser.add_argument('--check-local', action='store_true')
    args = parser.parse_args()
    result = summarize()
    rendered = report(result)
    if args.write:
        (OUT / 'result.json').write_text(json.dumps(result, indent=2) + '\n')
        (OUT / 'report.md').write_text(rendered)
        files = [p for p in sorted(OUT.rglob('*')) if p.is_file() and p.name != 'evidence-manifest.json'
                 and p.suffix != '.lock' and '__pycache__' not in p.parts]
        (OUT / 'evidence-manifest.json').write_text(json.dumps({'schema_version': 1, 'item_id': 'CVC-PREP-1',
                                                            'files': [binding(p, OUT) for p in files]}, indent=2) + '\n')
    else:
        require(load(OUT / 'result.json') == result and (OUT / 'report.md').read_text() == rendered, 'derived closure drift')
        for row in load(OUT / 'evidence-manifest.json')['files']:
            check_bytes(row, (OUT / row['path']).read_bytes())
    if args.check_local:
        m = load(ROOT / prep.MANIFEST)
        prep.runtime(ROOT, m)
        modules = {r['module']: r for r in load(ROOT / prep.CLOSURE)['closure']['modules'] if r['kind'] != 'core_runtime'}
        prep.check_sources(ROOT, m, modules)
        verify_output_set(ROOT, ROOT / m['materialization']['build_root'], result['outputs'])
    print('PASS: checkpoint-bound preparation evidence, first-failure accounting, exact outputs and scoped closure')


if __name__ == '__main__':
    try:
        main()
    except (ValueError, KeyError, OSError, subprocess.CalledProcessError) as error:
        print('FAIL: ' + str(error), file=sys.stderr)
        raise SystemExit(1)
