#!/usr/bin/env python3
"""Task-local three-fault E0 benchmark; uses the existing process supervisor."""
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from lib.resource_envelope_supervisor import run_direct

RUN = Path(__file__).resolve().parent
WORK = Path('/private/tmp/lal-test-effectiveness-20261003')
SELECTION = json.loads((RUN / 'selection.json').read_text())
PREFLIGHT = json.loads((RUN / 'preflight.json').read_text())
PROFILES = ['baseline', 'congruence', 'lambda-binder', 'definition-type']
ENV = dict(os.environ, CARGO_INCREMENTAL='0')
CARGO = shutil.which('cargo')


def save(path, obj):
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + '\n')


def healthy(r):
    return (r['cleanup_complete'] and r['reap_complete'] and not any(
        r[k] for k in ['accounting_error', 'monitor_errors', 'pipe_errors',
                       'cleanup_errors', 'stop_reason', 'trace_gap_fault']))


def attempt(label, argv, cwd, stdin=None, cargo=False):
    actual_label = label
    retry = 2
    while (RUN / 'attempts' / actual_label).exists():
        actual_label = f'{label}-r{retry}'
        retry += 1
    directory = RUN / 'attempts' / actual_label
    directory.mkdir(parents=True, exist_ok=False)
    save(directory / 'command.json', dict(argv=argv, cwd=str(cwd), stdin_sha256=
        None if stdin is None else hashlib.sha256(stdin).hexdigest()))
    env = dict(ENV, CARGO_TARGET_DIR=str(WORK / 'targets' / cwd.name))
    result = run_direct(argv=argv, cwd=cwd, env=env, stdin_bytes=stdin,
        timeout_seconds=3600 if cargo else 30,
        memory_ceiling_bytes=(16 if cargo else 2) * 1024**3,
        sample_interval_seconds=3, max_trace_gap_seconds=10,
        cleanup_seconds=10, output_cap_bytes=20 * 1024**2)
    save(directory / 'receipt.json', result.receipt)
    (directory / 'stdout').write_bytes(result.stdout)
    (directory / 'stderr').write_bytes(result.stderr)
    if not healthy(result.receipt):
        raise RuntimeError('Pause launches: supervision fault in ' + label)
    return result, actual_label


def classify(result):
    out = result.stdout.decode('utf-8', 'replace')
    err = result.stderr.decode('utf-8', 'replace')
    if result.receipt['exit_code'] == 0:
        match = re.search(r'Checked (\d+) declarations with no (?:typechecker )?errors', out)
        return ('ACCEPT', int(match[1])) if match and int(match[1]) > 0 else ('INCOMPLETE_SUCCESS', None)
    if "panicked at" in err:
        return 'CHECKER_PANIC', None
    return 'IMPORT_OR_CLI_ERROR', None


def main():
    # Identities are checked immediately before observations. The preparation
    # recovered the named upstream commit, not the later local regression commit.
    for item in SELECTION['selected'] + SELECTION['augmented']:
        assert hashlib.sha256((ROOT / item['path']).read_bytes()).hexdigest() == item['sha256']
    for profile in PROFILES:
        for p, sha in PREFLIGHT['source_files'].items():
            if profile != 'baseline' and p == 'src/tc.rs':
                continue
            assert hashlib.sha256((WORK / profile / p).read_bytes()).hexdigest() == sha
    rows = []
    binary_ids = {}
    suites = {}
    for profile in PROFILES:
        source = WORK / profile
        build, _ = attempt('v2-' + profile + '-build', [CARGO, 'build', '--offline', '--locked',
            '--jobs', '2', '--bin', 'nanoda_bin'], source, cargo=True)
        if build.receipt['exit_code'] != 0:
            raise RuntimeError('Build failed: ' + profile)
        binary = WORK / ('v2-' + profile + '-nanoda_bin')
        shutil.copy2(WORK / 'targets' / profile / 'debug' / 'nanoda_bin', binary)
        binary_ids[profile] = hashlib.sha256(binary.read_bytes()).hexdigest()
        suite, _ = attempt('v2-' + profile + '-upstream-suite', [CARGO, 'test', '--offline',
            '--locked', '--jobs', '2', '--lib'], source, cargo=True)
        text = suite.stdout.decode('utf-8', 'replace')
        match = re.search(r'test result: (ok|FAILED)\. (\d+) passed; (\d+) failed; (\d+) ignored;', text)
        if not match:
            raise RuntimeError('No completed test summary: ' + profile)
        suites[profile] = dict(result=match[1], passed=int(match[2]),
            failed=int(match[3]), ignored=int(match[4]), exit_code=suite.receipt['exit_code'])
        if profile == 'baseline' and (suite.receipt['exit_code'] != 0 or int(match[3])):
            raise RuntimeError('Pristine upstream suite failed; repair before fault interpretation')
        print(json.dumps(dict(profile=profile, upstream_suite=suites[profile])), flush=True)
        for cohort in ['selected', 'augmented']:
            for idx, item in enumerate(SELECTION[cohort]):
                label = f'v2-{profile}-{cohort}-{idx:03d}'
                result, actual_label = attempt(label, [str(binary), str(RUN / 'checker-config.json')],
                    source, (ROOT / item['path']).read_bytes())
                category, declarations = classify(result)
                rows.append(dict(profile=profile, cohort=cohort, index=idx,
                    path=item['path'], sha256=item['sha256'], category=category,
                    checked_declarations=declarations, exit_code=result.receipt['exit_code'],
                    stdout_sha256=result.receipt['stdout_sha256'],
                    stderr_sha256=result.receipt['stderr_sha256'],
                    receipt=str((RUN / 'attempts' / actual_label / 'receipt.json').relative_to(ROOT))))
                with (RUN / 'outcomes-v2.jsonl').open('a') as output:
                    output.write(json.dumps(rows[-1], sort_keys=True) + '\n')
        save(RUN / 'progress-v2.json', dict(suites=suites, binary_sha256=binary_ids,
                                       completed_checker_cells=len(rows)))
        print(profile + ': complete checker sample', flush=True)
    if len(set(binary_ids.values())) != len(PROFILES):
        raise RuntimeError('Isolated source variants did not produce distinct binaries')
    save(RUN / 'execution-v2.json', dict(source_revision=PREFLIGHT['source_revision'],
        suites=suites, binary_sha256=binary_ids, checker_cells=len(rows)))
    print('COMPLETE', len(rows), 'checker observations plus eight Cargo processes', flush=True)


if __name__ == '__main__':
    main()
