#!/usr/bin/env python3
"""Validate and derive the unresolved runner closure, without process fixtures."""
import argparse
from datetime import datetime
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from lib import cvc_runner


def require(ok, message):
    if not ok:
        raise ValueError(message)


def load(path):
    return json.loads(Path(path).read_text())


def binding(path):
    path = Path(path)
    return {'path': str(path.relative_to(ROOT)), 'bytes': path.stat().st_size,
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def verify(row):
    path = Path(row['path'])
    require(not path.is_absolute() and '..' not in path.parts, 'unsafe evidence path')
    require(binding(ROOT / path) == row, 'evidence bytes changed: ' + str(path))


def fixture_costs(rows, allow_orphan=False):
    pending, count, charged = None, 0, 0.
    for row in rows:
        if row.get('kind') == 'RESERVED':
            n, seconds = row.get('reserved_launches'), row.get('reserved_seconds')
            require(pending is None and type(n) is int and n > 0
                    and type(seconds) in (int, float) and math.isfinite(seconds)
                    and 0 < seconds <= 5*n, 'invalid fixture reservation')
            count += n
            pending = row
        elif row.get('kind') == 'TERMINAL':
            seconds = row.get('charged_seconds')
            require(pending and row.get('test') == pending.get('test')
                    and type(seconds) in (int, float) and math.isfinite(seconds)
                    and 0 <= seconds <= pending['reserved_seconds'], 'invalid fixture terminal')
            charged += seconds
            pending = None
        else:
            raise ValueError('unknown fixture event')
    require(allow_orphan or pending is None, 'orphan fixture cannot be silently closed')
    return {'reserved_launches': count, 'measured_seconds': charged,
            'orphan_reserved_seconds': pending['reserved_seconds'] if pending else 0,
            'orphan_count': 1 if pending else 0}


def ledger(name):
    return [json.loads(line) for line in (OUT / name).read_text().splitlines()]


def session_seconds(initial, final):
    for name in ('item_id', 'started_at', 'baseline_commit', 'limits', 'inputs'):
        require(initial[name] == final[name], 'initial identity/cost inputs changed')
    require(final['status'] == 'COMPLETE' and final['outcome'] == 'BOUNDED_UNRESOLVED',
            'control failure must remain unresolved')
    require(1 <= len(final['sessions']) <= 2, 'session count')
    total, previous = 0., None
    for i, row in enumerate(final['sessions']):
        start, end = datetime.fromisoformat(row['started_at']), datetime.fromisoformat(row['ended_at'])
        require(start.tzinfo and end.tzinfo and 0 <= (end-start).total_seconds() <= 5400
                and (previous is None or previous <= start), 'invalid session chronology')
        if i < len(initial['sessions']):
            require(row['started_at'] == initial['sessions'][i]['started_at'], 'session start reset')
        total += (end-start).total_seconds()
        previous = end
    require(total == final['active_seconds'] and total <= 10800
            and final['ended_at'] == final['sessions'][-1]['ended_at'], 'active time changed')
    return total


def summarize():
    initial, work, stop = [load(OUT / name) for name in
                           ('initial-work-record.json', 'work-record.json', 'stop-diagnostic.json')]
    seconds = session_seconds(initial, work)
    for row in initial['inputs']:
        data = subprocess.check_output(['git', 'show', initial['baseline_commit'] + ':' + row['path']], cwd=ROOT)
        require(hashlib.sha256(data).hexdigest() == row['sha256'], 'initial input is not baseline content')
        if row['path'] != 'config/research-queue.json':
            require(hashlib.sha256((ROOT / row['path']).read_bytes()).hexdigest() == row['sha256'],
                    'unchanged predecessor input changed')
    require(stop['outcome'] == 'BOUNDED_UNRESOLVED' and stop['next_item'] == 'CVC-RUNNER-2',
            'stop outcome changed')
    raw_record = ROOT / stop['root_attempt']['record']
    failed = load(raw_record)
    raw = (ROOT / failed['log']).read_bytes()
    require(failed['returncode'] == -15 and failed['status'] == 'FAIL'
            and hashlib.sha256(raw).hexdigest() == failed['log_sha256'], 'lost original SIGTERM failure')
    fixtures = fixture_costs(ledger('fixture-ledger.jsonl'), allow_orphan=True)
    require(fixtures == {'reserved_launches': 1, 'measured_seconds': 0.,
                         'orphan_reserved_seconds': 5, 'orphan_count': 1}, 'original orphan was reset or retried')
    worker = load(OUT / 'worker-accounting.json')
    reported = sum(row.get('fixture_launches_reported', 0) for row in worker['commands'])
    require(reported == 2 and worker['utc_timestamps'] is None, 'worker accounting uncertainty changed')
    validation = fixture_costs(ledger('validation-fixture-ledger.jsonl'))
    require(fixtures['reserved_launches'] + reported + validation['reserved_launches'] <= 80
            and validation['measured_seconds'] <= 400, 'known fixture bound exceeded')
    # Passing closure tests establish a disabled endpoint, not a tested runner.
    for entry in (cvc_runner.preflight, cvc_runner.execute, cvc_runner.start_session,
                  cvc_runner.end_session, cvc_runner.run_process):
        try:
            entry(ROOT)
        except ValueError as error:
            require('BOUNDED_UNRESOLVED' in str(error), 'incorrect refusal')
        else:
            raise ValueError('failed runner is executable')
    prior = load(ROOT / 'results/research/conditional-validation-contracts/cvc-prep-2/result.json')
    require(prior['outcome'] == 'SUCCESS' and len(prior['outputs']) == 141, 'preparation evidence changed')
    require(all(value == 0 for value in stop['out_of_scope_launches'].values()), 'out-of-scope launch')
    return {'schema_version': 1, 'item_id': 'CVC-RUNNER-1', 'outcome': 'BOUNDED_UNRESOLVED',
            'scientific_status': 'RUNNER_CONTROLS_UNVERIFIED_NO_PROOF_EXECUTION',
            'stop_reason': stop['reason'], 'execution_enabled': False,
            'costs': {'runner_active_seconds': seconds, 'recorded_fixture_reservations': 1,
                      'worker_reported_uninstrumented_fixture_launches': reported,
                      'root_orphan_charge_seconds': 5,
                      'worker_conservative_reservation_charge_seconds': 5*reported,
                      'actual_failed_fixture_process_seconds': None,
                      'failed_fixture_cap_compliance': 'NOT_ESTABLISHED',
                      'required_validation_fixtures': validation,
                      'preparation_active_seconds': prior['costs']['aggregate_active_seconds'],
                      'aggregate_runner_and_preparation_active_seconds': seconds + prior['costs']['aggregate_active_seconds'],
                      'preparation_compilation_seconds': prior['costs']['aggregate_compilation_seconds'],
                      'accounting_note': 'Reservation charges do not establish actual process duration. Raw orphan and worker-reported missing receipts are retained. Required unchanged repository regression fixtures are separately measured after the research stop.'},
            'preserved_inputs': initial['inputs'], 'out_of_scope_launches': stop['out_of_scope_launches'],
            'gaps': stop['gaps'], 'recommendation': work['recommendation'],
            'evidence': [binding(path) for path in [raw_record, ROOT / failed['log'],
                         OUT / 'initial-work-record.json', OUT / 'work-record.json',
                         OUT / 'stop-diagnostic.json', OUT / 'worker-accounting.json',
                         OUT / 'fixture-ledger.jsonl', OUT / 'validation-fixture-ledger.jsonl',
                         *sorted((OUT / 'draft').glob('*.txt'))]]}


def report(result):
    return ('# CVC-RUNNER-1: unresolved execution controls\n\n'
            '**BOUNDED_UNRESOLVED** — runner controls unverified; proof execution disabled.\n\n'
            + result['stop_reason'] + '\n\n'
            'The root test process exited with SIGTERM (-15), leaving one five-second reservation without a terminal receipt. '
            'The worker reported two further discovery runs that reached process fixtures without durable launch receipts. '
            'Actual elapsed process cost and per-fixture cap compliance are unknown. A later process-list inspection found no matching fixture alive; it does not prove timely cleanup. '
            'The latest draft contains untested edits made after the failures; the exact bytes loaded by the failed runs were not bound.\n\n'
            'The failed test source and latest draft are retained as text evidence. The live endpoint refuses all execution and session modes. '
            'Passing closure regressions verify this refusal and preservation of the failures; they do not certify the draft runner. '
            'No Lean, Lake, signature elaboration, proof, checker, or network research launch occurred. '
            'The unchanged dependency bundle still contains 37 modules and 141 products.\n\n'
            f"Recorded runner work: {result['costs']['runner_active_seconds']/60:.2f} active minutes. "
            'The two preparation ledgers retain their original outcomes and 49.755 aggregate compilation seconds.\n\n'
            '**Recommendation:** ' + result['recommendation']['action'] + '\n\n'
            'Target: ' + result['recommendation']['target'] + '. Priority: ' + result['recommendation']['priority'] + '. '
            'Prerequisites: ' + '; '.join(result['recommendation']['prerequisites']) + '. '
            'CVC-3 remains PLANNED; signature elaboration remains its future counted attempt 1.\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = summarize()
    if args.write:
        (OUT / 'result.json').write_text(json.dumps(result, indent=2) + '\n')
        (OUT / 'report.md').write_text(report(result))
        files = [path for path in OUT.rglob('*') if path.is_file() and path.name != 'evidence-manifest.json'
                 and path.suffix != '.lock' and '__pycache__' not in path.parts]
        files += [ROOT / 'lib/cvc_runner.py', ROOT / 'scripts/run-cvc-u1-proof', ROOT / 'tests/test_cvc_runner.py',
                  ROOT / 'tests/test_cvc_runner_closure.py']
        (OUT / 'evidence-manifest.json').write_text(json.dumps({'schema_version': 1, 'item_id': 'CVC-RUNNER-1',
            'files': [binding(path) for path in sorted(files)]}, indent=2) + '\n')
    else:
        require(load(OUT / 'result.json') == result and (OUT / 'report.md').read_text() == report(result),
                'derived closure drift')
        for row in load(OUT / 'evidence-manifest.json')['files']:
            verify(row)
    print('PASS: unresolved cancellation/accounting evidence preserved; execution disabled; no proof claim')


if __name__ == '__main__':
    try:
        main()
    except (ValueError, KeyError, OSError, subprocess.CalledProcessError) as error:
        print('FAIL: ' + str(error), file=sys.stderr)
        raise SystemExit(1)
