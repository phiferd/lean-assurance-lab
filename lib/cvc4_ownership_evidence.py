"""Derive the finite ownership report from immutable launch and raw receipts."""
import json
from pathlib import Path
import re

from lib import cvc4_ownership_runner as runner
from lib.cvc4_ownership_inputs import BASE, build
from lib.cvc_prep import require


def classify(cell, terminal, stdout, stderr, control_expected):
    if terminal.get('control_error'):
        return 'ENGINEERING_PAUSE'
    if terminal.get('hypothesis_matched') is True:
        return 'ACCEPT' if cell['role'] == 'control' else 'REFUSED_OWNERSHIP'
    accepted = (terminal.get('returncode') == control_expected['returncode']
                and re.fullmatch(control_expected['stdout_pattern'], stdout) is not None
                and re.fullmatch(control_expected['stderr_pattern'], stderr) is not None)
    return 'ACCEPT' if accepted else 'UNRESOLVED_OUTPUT'


def result(root, require_payloads=True):
    root = Path(root).resolve()
    inputs = build(root)
    run = runner.validate_run(root, require_payloads=require_payloads)
    rows = []
    for attempt in run['attempts']:
        cell = attempt['reservation']['cell']
        terminal = attempt.get('terminal', {})
        matched = terminal.get('hypothesis_matched')
        directory = root / runner.OUT / 'attempts' / f"{attempt['reservation']['number']:02d}"
        control = next(c for c in run['manifest']['cells'] if c['role'] == 'control' and c['implementation'] == cell['implementation'])
        try:
            outcome = classify(cell, terminal, (directory / 'stdout').read_text(), (directory / 'stderr').read_text(), control['expected'])
        except (OSError, UnicodeError):
            outcome = 'ENGINEERING_PAUSE'
        case = next(r for r in inputs['cases'] if r['role'] == cell['role'])
        rows.append({'case': case['id'], 'observer': cell['implementation'], 'outcome': outcome,
                     'hypothesis_matched': matched, 'returncode': terminal.get('returncode'),
                     'process_status': terminal.get('process_status'),
                     'input': case['input'], 'raw_receipts': terminal.get('receipts', []),
                     'attempt': attempt['reservation']['number']})
    complete = run['matrix_complete'] and not run['pending'] and not run['control_stop']
    characterized = complete and all(r['outcome'] in ('ACCEPT', 'REFUSED_OWNERSHIP') for r in rows)
    outcome = 'SUCCESS' if characterized else 'BOUNDED_UNRESOLVED'
    return {'schema_version': 1, 'item_id': runner.ITEM, 'contract_id': 'CVC-U1-A7',
            'outcome': outcome, 'scientific_status': 'FINITE_OWNERSHIP_BOUNDARY_CHARACTERIZED' if characterized else 'BOUNDARY_UNRESOLVED',
            'checkpoint': run['checkpoint'], 'manifest': runner.file_receipt(root, root / runner.MANIFEST),
            'cases': rows, 'matrix_complete': complete,
            'research_counts': {'byte_streams': 2, 'pairs': 1, 'observer_launches': run['launch_count'],
                                'predecessor_observer_launches': 12, 'combined_observer_launches': run['combined_launch_count'],
                                'proof_builds': 0, 'setup_builds': 0, 'research_network_requests': 0},
            'accounting': {'process_seconds': run['known_process_seconds'],
                           'predecessor_process_seconds': runner.INHERITED_PROCESS_SECONDS,
                           'combined_process_seconds': run['combined_process_seconds'],
                           'active_seconds_at_last_observation': runner.work_total(run['work'], run['accounted_at']),
                           'final_active_work_record': runner.WORK,
                           'rule': 'Final active time includes engineering and closure validation; administrative inert fixtures remain separate. Every predecessor charge remains unchanged.'},
            'finding': ('Both pinned observers accept the owned control after the sole unused-v level insertion. Both refuse the candidate at their universe ownership checks. The repaired serialization reaches the previously unobserved boundary.' if all(r['outcome'] == 'REFUSED_OWNERSHIP' for r in rows if 'CONTROL' not in r['case']) else 'Both controls accepted, and the fixed candidate observations are characterized in the matrix. Acceptance of this unsupported candidate is outside the conditional model guarantee.') if characterized else 'The fixed comparison did not fully characterize ownership; retain all raw evidence and diagnose the exact remaining gap before declaring closure.',
            'model_interpretation': 'The candidate remains CHECKED_UNSUPPORTED under CVC-U1-A7, not a checked invalid proof. Its referenced Sort levels have the same equality as the control; the missing support condition is ownership of u. The control is MODEL_VALID_BY_DEFINITION, not an extension of the original checked finite acceptance theorem.',
            'recommendation': {'action': 'Reuse the local exact serialization regression and prepare a consolidated conditional-contract evidence package and phase decision using existing evidence.',
                               'target': 'CVC-5-CONDITIONAL: CVC-U1-A7 proof, fixed implementation boundaries and reusable Lab regression',
                               'priority': 1, 'prerequisites': ['Validated and delivered CVC-4-OWNERSHIP-1 closure', 'Preserve A7, all earlier costs/failures, provisional catalog status and upstream waiting decisions'],
                               'evidence_refs': [BASE + '/cases.json', BASE + '/source-mapping.json', BASE + '/run-0001/events.jsonl', 'tests/test_cvc4_ownership_inputs.py']},
            'external_action': {'decision': 'NO_EXTERNAL_ACTION_NOW', 'reason': 'The evidence repairs a Lab serializer prerequisite and characterizes unsupported input refusal; it does not establish an invalid accepted proof or a new universal defect. The local regression supplies immediate reuse. Any later external contribution needs a concrete target/value review and separate authorization.'},
            'nonclaims': ['No source approval or catalog promotion; ownership remains PROVISIONAL.',
                          'No parser/importer or executable-validator refinement, source-to-binary proof, A7 discharge or consistency result.',
                          'No new semantic family, additional pair, current-master observation or external research message.',
                          'Original CVC-4/CVC-5 dependencies remain unmet; all historical runs and failed evidence remain unchanged.']}


def render(record):
    lines = ['# CVC-4-OWNERSHIP-1 — exact serialization and ownership boundary', '',
             '**' + record['outcome'] + '** for one finite comparison.', '', record['finding'], '',
             '| Input | Official Lean | Nanoda |', '| --- | --- | --- |']
    for role in ('CONTROL', 'UNOWNED'):
        rows = [r for r in record['cases'] if ('CONTROL' in r['case']) == (role == 'CONTROL')]
        by = {r['observer']: r['outcome'] for r in rows}
        lines.append('| ' + ('Owned control' if role == 'CONTROL' else 'Unowned candidate') + ' | ' + by.get('official', 'UNEXECUTED') + ' | ' + by.get('nanoda', 'UNEXECUTED') + ' |')
    lines += ['', 'Each new stream inserts only the prescribed unused `v` level record immediately before its final definition. Removing that line recovers its predecessor byte-for-byte. The independent raw syntax projection preserves the name, ordered parameter list, value and type; the unchanged strict decoder accepts the control and refuses the unowned candidate.', '',
              record['model_interpretation'], '',
              'Nanoda previously failed at `parser.rs:506` while resolving declared parameters. The committed candidate refusal hypotheses identify `tc.rs:520` for Nanoda and undefined universe parameter `u` for official Lean. The table records whether these exact hypotheses were observed. These are profile observations tied to exact binaries and raw outputs.', '',
              'The four new reservations plus twelve preserved predecessor reservations consume the cumulative sixteen-launch ceiling. New process time is ' + str(record['accounting']['process_seconds']) + ' seconds. Final active time, including engineering and closure checks, is retained in [work-record.json](work-record.json); separately bounded administrative fixtures are recorded in closure validation.', '',
              record['external_action']['reason'], '',
              'Select **CVC-5-CONDITIONAL**, READY and unstarted, for existing-evidence packaging and the phase decision. No further observer run or new semantic family is selected.', '',
              'Limits: ' + ' '.join(record['nonclaims']), '',
              'Canonical [result](result.json), [cases](cases.json), [source mapping](source-mapping.json), [raw ledger](run-0001/events.jsonl), and [prelaunch review](entry-review.json). Recheck with `scripts/validate-cvc4-ownership`; use `--without-runtime-payloads` only for evidence inspection in a clone. This mode never permits launches.', '']
    return '\n'.join(lines)


def validate(root, write=False, require_payloads=True):
    root = Path(root).resolve()
    record = result(root, require_payloads=require_payloads)
    report = render(record)
    for path, raw in ((root / BASE / 'result.json', json.dumps(record, indent=2) + '\n'),
                      (root / BASE / 'report.md', report)):
        if write:
            require(not path.exists() or path.read_text() == raw, 'refuse to rewrite different completed evidence')
            path.write_text(raw)
        else:
            require(path.read_text() == raw, 'derived ownership evidence differs: ' + str(path))
    return {'item_id': runner.ITEM, 'outcome': record['outcome'], 'matrix_complete': record['matrix_complete'],
            'research_counts': record['research_counts'], 'accounting': record['accounting']}
