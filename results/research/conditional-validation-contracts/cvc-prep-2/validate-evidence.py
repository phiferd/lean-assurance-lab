#!/usr/bin/env python3
"""Derive/check the immutable CVC-PREP-2 closure without launching Lean.

``--write`` is for the stopping-point closure only.  Ordinary validation checks
the committed execution checkpoint, raw ledger and derived closure for drift;
``--check-local`` additionally rehashes the installed runtime, copied sources,
and complete isolated output bundle.
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
from lib import cvc_prep2 as prep


def load(path):
    return json.loads(Path(path).read_text())


def require(ok, message):
    if not ok:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def binding(path, relative_to=ROOT):
    path = Path(path)
    return {'path': str(path.relative_to(relative_to)), 'bytes': path.stat().st_size,
            'sha256': digest(path.read_bytes())}


def check_bytes(row, data):
    require(len(data) == row.get('bytes', len(data)) and digest(data) == row['sha256'],
            'binding mismatch: ' + row['path'])


def committed(checkpoint, path):
    return subprocess.check_output(['git', 'show', checkpoint + ':' + path], cwd=ROOT)


def test_counts(checkpoint, receipt):
    counts = []
    for check in receipt['checks']:
        raw = committed(checkpoint, check['log'])
        check_bytes({'path': check['log'], 'sha256': check['log_sha256']}, raw)
        require(check['returncode'] == 0 and check['status'] == 'PASS'
                and raw.rstrip().endswith(b'OK'), 'inert tests failed')
        found = re.findall(rb'^Ran (\d+) tests? in ', raw, re.MULTILINE)
        require(len(found) == 1, 'ambiguous test count')
        require(check['test_count'] == int(found[0]), 'per-check test count differs from raw log')
        counts.append(int(found[0]))
    require(receipt['test_count'] == sum(counts), 'receipt test total differs from logs')
    return counts


def fixture_costs(path):
    rows = [json.loads(line) for line in Path(path).read_text().splitlines() if line.strip()]
    reservations, pending, terminals = [], [], []
    for row in rows:
        kind, test = row.get('kind'), row.get('test')
        require(isinstance(test, str) and test, 'fixture test identity missing')
        if kind == 'RESERVED':
            launches, seconds = row.get('reserved_launches'), row.get('reserved_seconds')
            require(not pending and type(launches) is int and launches > 0
                    and prep.finite(seconds) and 0 < seconds <= 5 * launches,
                    'invalid fixture reservation')
            reservation = (test, launches, seconds)
            reservations.append(reservation)
            pending.append(reservation)
        elif kind == 'TERMINAL':
            charge = row.get('charged_seconds')
            require(pending and pending[-1][0] == test
                    and prep.finite(charge) and 0 <= charge <= pending[-1][2],
                    'fixture terminal without bounded reservation')
            pending.pop()
            terminals.append((test, charge))
        else:
            raise ValueError('unknown fixture event')
    require(not pending and len(reservations) == len(terminals), 'orphan fixture reservation')
    launches = sum(entry[1] for entry in reservations)
    seconds = sum(charge for _, charge in terminals)
    return launches, seconds


def output_map(rows):
    return prep.output_map(rows)


def closed_sessions(work, initial):
    require(work['started_at'] == initial['started_at'] and work['limits'] == initial['limits']
            and work['inputs'] == initial['inputs'], 'final work ledger changed frozen inputs')
    sessions, initial_sessions = work['sessions'], initial['sessions']
    require(1 <= len(sessions) <= 2 and len(sessions) >= len(initial_sessions), 'session count differs')
    previous_end, elapsed = None, 0.0
    for number, session in enumerate(sessions, 1):
        require(session.get('number') == number, 'session numbering differs')
        start, end = datetime.fromisoformat(session['started_at']), datetime.fromisoformat(session['ended_at'])
        require(start.tzinfo is not None and end.tzinfo is not None and start <= end
                and (previous_end is None or previous_end <= start), 'invalid or overlapping session')
        if number <= len(initial_sessions):
            frozen = initial_sessions[number - 1]
            require(session['started_at'] == frozen['started_at'], 'frozen session start changed')
        used = (end - start).total_seconds()
        require(0 <= used <= 5400, 'session duration differs')
        elapsed += used
        previous_end = end
    require(work['ended_at'] == sessions[-1]['ended_at']
            and any(datetime.fromisoformat(s['started_at']) <= datetime.fromisoformat(work['execution_stopped_at'])
                    <= datetime.fromisoformat(s['ended_at']) for s in sessions), 'execution/closure outside sessions')
    require(0 < elapsed <= prep.LIMITS['max_active_seconds']
            and work['active_seconds'] == elapsed, 'active seconds differ')
    return elapsed


def checked_checkpoint():
    marker = load(OUT / 'execution/start.json')
    checkpoint = marker['checkpoint_commit']
    manifest_bytes = committed(checkpoint, prep.MANIFEST)
    require(digest(manifest_bytes) == marker['manifest_sha256'], 'checkpoint manifest changed')
    require((ROOT / prep.MANIFEST).read_bytes() == manifest_bytes,
            'current manifest differs from execution checkpoint')
    manifest = json.loads(manifest_bytes)
    bound = [manifest[key] for key in ('source_closure', 'runtime_manifest', 'work_record',
                                        'controller', 'tests', 'predecessor', 'commands')]
    for row in bound + manifest['immutable_bindings']:
        exact = committed(checkpoint, row['path'])
        check_bytes(row, exact)
        if row['path'] != manifest['work_record']['path']:
            check_bytes(row, (ROOT / row['path']).read_bytes())
    queue = json.loads(committed(checkpoint, 'config/research-queue.json'))
    item = next(row for row in queue['items'] if row['id'] == prep.ITEM)
    require(queue['selected_item'] == prep.ITEM and item['status'] == 'ACTIVE',
            'checkpoint did not authorize active successor')
    return checkpoint, manifest


def summarize():
    checkpoint, manifest = checked_checkpoint()
    initial_work = json.loads(committed(checkpoint, manifest['work_record']['path']))
    require(initial_work['status'] == 'ACTIVE' and initial_work['ended_at'] is None,
            'initial work record was not an open active authorization')
    require((ROOT / manifest['work_record']['path']).read_bytes()
            == committed(checkpoint, manifest['work_record']['path']), 'live initial work record changed')
    receipt = json.loads(committed(checkpoint, str((OUT / 'inert-test-receipt.json').relative_to(ROOT))))
    require(receipt['item_id'] == prep.ITEM and receipt['status'] == 'PASS', 'missing inert receipt')
    counts = test_counts(checkpoint, receipt)
    for row in receipt['tested_files']:
        check_bytes(row, committed(checkpoint, row['path']))

    predecessor = json.loads(committed(checkpoint, manifest['predecessor']['path']))
    require(predecessor['item_id'] == 'CVC-PREP-1' and predecessor['outcome'] == 'BOUNDED_UNRESOLVED'
            and predecessor['completed_modules'] == predecessor['compilation_attempts'] == 27,
            'predecessor status or count differs')
    seed = prep.relocated_outputs(predecessor['outputs'])
    require(manifest['seed_outputs'] == seed and len(seed) == 119, 'seed identities differ')
    closure = load(ROOT / manifest['source_closure']['path'])['closure']
    modules = {row['module']: row for row in closure['modules'] if row['kind'] != 'core_runtime'}
    topology = closure['topological_noncore_order']
    order = topology[27:]
    successor = json.loads(committed(checkpoint, prep.SUCCESSOR))
    require([row['module'] for row in predecessor['attempts']] == topology[:27]
            and successor['remaining_order'] == order and len(order) == prep.COUNT,
            'frozen predecessor or successor module order differs')
    commands = json.loads(committed(checkpoint, manifest['commands']['path']))
    require(commands == prep.commands(ROOT, manifest, order) and len(commands['commands']) == prep.COUNT,
            'successor commands differ')

    state = prep.derive(prep.read_events(OUT / 'execution/events.jsonl'))
    require(set(state) == set(range(len(state))) and 0 in state, 'reservation numbering')
    attempts, new_outputs, charged = [], [], 0.0
    for number, row in state.items():
        if number == 0:
            require(row.get('module') == 'START' and row.get('terminal', {}).get('status') == 'COMPLETE',
                    'invalid start marker')
            continue
        require(number <= prep.COUNT and 'terminal' in row, 'unreconciled successor reservation')
        term, command = row['terminal'], commands['commands'][number - 1]
        require(row['module'] == order[number - 1] == command['module'], 'remaining module order differs')
        require(row['argv'] == command['argv'] and row['cwd'] == command['cwd']
                and row['env'] == manifest['compiler']['env'], 'launch command changed')
        require(row['source_sha256'] == modules[row['module']]['source']['sha256']
                and row['runtime_manifest_sha256'] == manifest['runtime_manifest']['sha256'],
                'launch source/runtime differs')
        require(row['prior_outputs'] == seed + new_outputs, 'prior output binding differs')
        before = {n: candidate for n, candidate in state.items() if n < number}
        allowed = prep.attempt_budget(initial_work, before, datetime.fromisoformat(row['at']))
        require(0 < row['reserved_seconds'] <= allowed + 1e-6, 'reservation exceeds budget')
        for stream in ('stdout', 'stderr'):
            raw = ROOT / row[stream]
            require(raw.is_file() and digest(raw.read_bytes()) == term[stream + '_sha256'], 'raw log changed')
        if term['status'] == 'COMPLETE':
            require(term['returncode'] == 0 and 0 <= term['charged_seconds'] <= row['reserved_seconds'],
                    'invalid successful charge')
            outputs = term.get('outputs')
            require(isinstance(outputs, list) and outputs, 'successful module lacks outputs')
            stem = manifest['materialization']['build_root'] + '/' + row['module'].replace('.', '/')
            require(all(candidate['path'].startswith(stem + '.') for candidate in outputs),
                    'output outside reserved successor module')
            require(stem + '.olean' in {candidate['path'] for candidate in outputs},
                    'successful olean missing')
            output_map(seed + new_outputs + outputs)
            new_outputs.extend(outputs)
        else:
            require(number == max(state), 'execution continued after first terminal failure')
        charged += term['charged_seconds']
        attempts.append({'number': number, 'module': row['module'], 'status': term['status'],
                         'seconds': term['charged_seconds'], 'outputs': term.get('outputs', [])})
    require(len(attempts) <= prep.COUNT and charged <= prep.LIMITS['max_compilation_seconds'],
            'successor compilation bound exceeded')

    work = load(OUT / 'work-record.json')
    require(work['status'] == 'COMPLETE' and work['outcome'] in {'SUCCESS', 'BOUNDED_UNRESOLVED'}
            and work['ended_at'] and work['execution_stopped_at'], 'successor work record is not closed')
    elapsed = closed_sessions(work, initial_work)
    fixtures, fixture_seconds = fixture_costs(OUT / 'fixture-ledger.jsonl')
    require(fixtures <= 80 and fixture_seconds <= 400, 'fixture bound exceeded')
    require(work['compilation_attempts'] == len(attempts) and work['compilation_seconds'] == charged
            and work['fixture_process_launches'] == fixtures and work['fixture_process_seconds'] == fixture_seconds,
            'work ledger counters differ')
    for forbidden in ('lab_elaborations', 'proof_attempts', 'checker_launches', 'lake_executions',
                      'native_compiler_invocations', 'network_requests', 'toolchain_installs'):
        require(work.get(forbidden) == 0, 'out-of-scope activity: ' + forbidden)

    succeeded = len(attempts) == prep.COUNT and all(row['status'] == 'COMPLETE' for row in attempts)
    total_outputs = seed + new_outputs
    full_map = output_map(total_outputs)
    required_oleans = {manifest['materialization']['build_root'] + '/' + module.replace('.', '/') + '.olean'
                       for module in topology}
    if succeeded:
        require(required_oleans <= set(full_map) and work['outcome'] == 'SUCCESS',
                'successful bundle is incomplete or has wrong outcome')
        stop = {'kind': 'COMPLETE', 'reason': work['stop_reason']}
    else:
        require(work['outcome'] == 'BOUNDED_UNRESOLVED', 'failed execution must remain unresolved')
        stop_path = OUT / 'execution/stop.json'
        if stop_path.exists():
            stop = load(stop_path)
        else:
            failed = next((row for row in attempts if row['status'] != 'COMPLETE'), None)
            require(failed is not None, 'unresolved outcome lacks persisted stop')
            stop = {'kind': 'TERMINAL_FAILURE', 'attempt': failed['number'], 'module': failed['module'],
                    'status': failed['status'], 'reason': work['stop_reason']}
    prior_costs = predecessor['costs']
    runtime = load(ROOT / manifest['runtime_manifest']['path'])
    return {'schema_version': 1, 'item_id': prep.ITEM, 'run_id': prep.RUN,
            'outcome': 'SUCCESS' if succeeded else 'BOUNDED_UNRESOLVED',
            'scientific_status': 'UPSTREAM_DEPENDENCY_BUNDLE_PREPARED' if succeeded else 'DEPENDENCY_PREPARATION_STOPPED',
            'checkpoint_commit': checkpoint, 'manifest': binding(ROOT / prep.MANIFEST),
            'module_count': 37, 'predecessor': {'item_id': predecessor['item_id'],
                                                'outcome': predecessor['outcome'],
                                                'completed_modules': 27, 'output_products': len(seed),
                                                'compilation_seconds': predecessor['compilation_seconds']},
            'compilation_attempts': len(attempts),
            'completed_modules': 27 + sum(row['status'] == 'COMPLETE' for row in attempts),
            'compilation_seconds': charged, 'attempts': attempts, 'outputs': total_outputs,
            'runtime_files': sum(row['type'] == 'file' for row in runtime['files']),
            'runtime_bytes': sum(row.get('bytes', 0) for row in runtime['files']),
            'prelaunch_checks': {'test_counts': counts, 'test_count': sum(counts)},
            'costs': {'successor_active_seconds': elapsed, 'successor_compilation_seconds': charged,
                      'successor_fixture_reserved_launches': fixtures,
                      'successor_fixture_process_seconds': fixture_seconds,
                      'predecessor_active_seconds': prior_costs['preparation_active_seconds'],
                      'predecessor_compilation_seconds': prior_costs['preparation_compilation_seconds'],
                      'predecessor_fixture_reserved_launches': prior_costs['fixture_reserved_launches'],
                      'predecessor_fixture_process_seconds': prior_costs['fixture_process_seconds'],
                      'aggregate_compilation_attempts': predecessor['compilation_attempts'] + len(attempts),
                      'aggregate_active_seconds': prior_costs['preparation_active_seconds'] + elapsed,
                      'aggregate_compilation_seconds': prior_costs['preparation_compilation_seconds'] + charged,
                      'aggregate_fixture_reserved_launches': prior_costs['fixture_reserved_launches'] + fixtures,
                      'aggregate_fixture_process_seconds': prior_costs['fixture_process_seconds'] + fixture_seconds,
                      'aggregate_note': 'CVC-PREP-1 remains BOUNDED_UNRESOLVED; its recorded costs are preserved and aggregated without relabeling its outcome.'},
            'recommendation': work['recommendation'], 'stop': stop,
            'scope': 'This establishes exact upstream dependency availability only. No Lab signature or proof was elaborated, and no checker, Lake, native compiler, network request, download or installation ran.',
            'runtime_limit': runtime['unresolved_inventory_interpretation'],
            'evidence': [binding(OUT / name) for name in ['execution/start.json', 'execution/events.jsonl',
                         'work-record.json', 'initial-work-record.json', 'inert-test-receipt.json',
                         'fixture-ledger.jsonl', 'command-manifest.json']]}


def report(result):
    return (f"# CVC-PREP-2: successor dependency preparation\n\n"
            f"**{result['outcome']}** — `{result['scientific_status']}`.\n\n"
            f"The successor completed {result['completed_modules']} of 37 jointly bound modules: 27 frozen predecessor successes and "
            f"{result['compilation_attempts']} successor attempts. The combined bundle contains {len(result['outputs'])} exact output products. It charged {result['compilation_seconds']:.3f} successor compilation seconds. "
            f"The exact execution checkpoint is `{result['checkpoint_commit']}`.\n\n"
            + result['scope'] + '\n\n'
            + '**Stop:** ' + result['stop']['reason'] + '\n\n'
            + 'CVC-PREP-1 remains `BOUNDED_UNRESOLVED`; its 119 prior products and recorded costs are retained as predecessor evidence, not replayed successes. '
            + f"Aggregate preparation accounting is {result['costs']['aggregate_active_seconds'] / 60:.2f} active minutes and "
            + f"{result['costs']['aggregate_compilation_seconds']:.3f} compilation seconds.\n\n"
            + '**Recommendation:** ' + result['recommendation']['action'] + ' Target: ' + result['recommendation']['target']
            + '. Priority: ' + result['recommendation']['priority'] + '.\n\n'
            + 'Validate tracked evidence with `python3 results/research/conditional-validation-contracts/cvc-prep-2/validate-evidence.py`; '
            + 'add `--check-local` to rehash the isolated successor sources, runtime and complete output bundle. No validation mode launches Lean.\n')


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
        files = [path for path in sorted(OUT.rglob('*')) if path.is_file() and path.name != 'evidence-manifest.json'
                 and path.suffix != '.lock' and '__pycache__' not in path.parts]
        (OUT / 'evidence-manifest.json').write_text(json.dumps({'schema_version': 1, 'item_id': prep.ITEM,
            'files': [binding(path, OUT) for path in files]}, indent=2) + '\n')
    else:
        require(load(OUT / 'result.json') == result and (OUT / 'report.md').read_text() == rendered,
                'derived closure drift')
        for row in load(OUT / 'evidence-manifest.json')['files']:
            check_bytes(row, (OUT / row['path']).read_bytes())
    if args.check_local:
        manifest = load(ROOT / prep.MANIFEST)
        prep.seed_inputs(ROOT, manifest)
        prep.runtime(ROOT, manifest)
        modules = {row['module']: row for row in load(ROOT / prep.CLOSURE)['closure']['modules']
                   if row['kind'] != 'core_runtime'}
        prep.check_sources(ROOT, manifest, modules)
        prep.verify_output_set(ROOT, ROOT / manifest['materialization']['build_root'], result['outputs'])
    print('PASS: checkpoint-bound successor evidence, first-failure accounting, exact joint outputs and scoped closure')


if __name__ == '__main__':
    try:
        main()
    except (ValueError, KeyError, OSError, subprocess.CalledProcessError, json.JSONDecodeError) as error:
        print('FAIL: ' + str(error), file=sys.stderr)
        raise SystemExit(1)
