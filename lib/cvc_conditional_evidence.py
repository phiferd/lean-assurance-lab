"""Offline mechanical evidence checks for the CVC-CONDITIONAL-1 successor."""
import ast
from datetime import datetime
import json
from pathlib import Path

from lib.cvc_prep import require, sha, safe, read_events
from lib.cvc_fixture_budget import totals
from lib.cvc_runner2_evidence import _legacy
from lib import cvc_a7_runner as runner

BASE = 'results/research/conditional-validation-contracts/cvc-conditional-1'
VALIDATION = 'results/workflow-refresh/cvc-conditional-1-2026-09-07'
PROPOSAL = 'results/research/conditional-validation-contracts/cvc-axioms-1/successor-proposal.json'


def load(path):
    return json.loads(Path(path).read_text())


def verify_binding(root, row):
    p = safe(root, row['path'])
    require(sha(p) == row['sha256'], 'binding changed: ' + row['path'])
    if 'bytes' in row:
        require(p.stat().st_size == row['bytes'], 'size changed: ' + row['path'])


def preserved_functions(root):
    """Directly demonstrate unchanged process-independent infrastructure."""
    def definitions(path):
        return {n.name: ast.dump(n, include_attributes=False) for n in ast.parse(path.read_text()).body
                if isinstance(n, (ast.FunctionDef, ast.ClassDef))}
    old = definitions(root / 'lib/cvc_runner2.py')
    new = definitions(root / 'lib/cvc_a7_runner.py')
    names = ['load', 'binding', 'receipt', 'verify_receipt', 'environment', 'verify_payloads',
             'stamp', 'elapsed', 'active_seconds', 'Ledger', 'open_run']
    for name in names:
        require(old[name] == new[name], 'unnecessary infrastructure change: ' + name)
    return names


def validate(root, full=False, closure=False):
    root = Path(root).resolve()
    proposal = load(root / PROPOSAL)
    for binding in proposal['immutable_predecessors']:
        verify_binding(root, binding)
    manifest = runner.validate_manifest(root)
    require(manifest['run_id'] == 'CVC3-U1-A7-PROOF-0001' and
            manifest['item_id'] == 'CVC-3-CONDITIONAL', 'successor run identity')
    require(manifest['limits'] == {'sessions': 2, 'session_seconds': 3600, 'active_seconds': 7200,
        'attempts': 6, 'attempt_seconds': 300, 'checker_launches': 0,
        'network_requests': 0, 'dependency_compilations': 0}, 'proof limits changed')
    from lib.cvc_a7_audit import baseline_source
    require((root / runner.BASELINE).read_bytes() == baseline_source(load(root / runner.EXPECTATIONS)),
            'baseline source differs from canonical reviewed expectations')
    assumptions = load(root / runner.ASSUMPTIONS)
    policy = assumptions['conditional_axiom_policy']
    require(policy['standard_allowed'] + policy['source_helpers_allowed'] == proposal['proposed_assumptions'],
            'exact A7 envelope changed')
    protocol = load(root / runner.PROTOCOL)
    require(protocol['limits'] == proposal['proof']['budget'] and
            protocol['preparation_limits'] == proposal['preparation']['budget'], 'protocol cap changed')
    require(protocol['signature'] == proposal['immutable_predecessors'][0], 'semantic signature changed')
    unchanged = preserved_functions(root)
    from lib import cvc_runner2
    old_manifest = load(root / cvc_runner2.MANIFEST)
    # Historical runner and all prior process engine/test inputs remain byte-identical.
    for binding in old_manifest['controller_inputs'] + old_manifest['fixed_inputs']:
        verify_binding(root, binding)
    if full:
        runner.verify_payloads(root, manifest)
    if not closure:
        return {'status': 'PASS', 'full_payload': full, 'unchanged_functions': unchanged,
                'scientific_status': 'PROTOCOL_PREPARED_BASELINE_UNEXECUTED'}
    result, work = load(root / BASE / 'result.json'), load(root / BASE / 'work-record.json')
    require(result['item_id'] == work['item_id'] == 'CVC-CONDITIONAL-1' and
            result['outcome'] == 'SUCCESS' and work['status'] == 'COMPLETE', 'closure outcome')
    require(not (root / runner.OUT).exists() and not (root / runner.BASE).exists(), 'next proof run started')
    require(all(v == 0 for v in work['research_operations'].values()), 'forbidden research operation')
    sessions = work['sessions']
    require(0 < len(sessions) <= 2, 'session cap')
    total = 0.
    for n, row in enumerate(sessions, 1):
        wall = (datetime.fromisoformat(row['ended_at']) - datetime.fromisoformat(row['started_at'])).total_seconds()
        mono = row['ended_monotonic'] - row['started_monotonic']
        require(row['number'] == n and 0 <= wall <= 3600 and 0 <= mono <= 3600, 'session duration')
        require(row['charged_seconds'] == max(wall, mono), 'session charge')
        total += row['charged_seconds']
    require(total == work['active_seconds'] == result['active_seconds'] and total <= 7200, 'total duration')
    evidence = load(root / BASE / 'evidence-manifest.json')
    required = set(runner.CODE) | set(runner.FIXED) | {runner.MANIFEST, BASE+'/result.json', BASE+'/work-record.json', BASE+'/report.md'}
    require(required <= {b['path'] for b in evidence['files']}, 'incomplete evidence manifest')
    for binding in evidence['files']:
        verify_binding(root, binding)
    batches = sorted((root / VALIDATION).glob('*-fixture-reservation.json'))
    count = reserved = 0
    for path in batches:
        batch = load(path)
        require(batch['item_id'] == 'CVC-CONDITIONAL-1' and batch['reserved_launches'] == 23 and
                batch['reserved_seconds'] == 115, 'unrecognized fixture batch')
        count += batch['reserved_launches']; reserved += batch['reserved_seconds']
        for b in batch['source_bindings']:
            verify_binding(root, b)
        directory = root / batch['ledger_directory']
        events = read_events(directory / 'runner/fixture-ledger.jsonl')
        processes, charged = totals(events)
        legacy_count, legacy_charge = _legacy(directory / 'preparation.jsonl')
        require(processes + legacy_count == 23 and charged + legacy_charge <= 115,
                'fixture receipt count or duration')
        for event in events:
            if event['kind'] == 'TERMINAL':
                for b in event['files']:
                    verify_binding(directory / 'runner', b)
    require(count == result['fixture_reserved_launches'] <= 64 and
            reserved == result['fixture_reserved_seconds'] <= 320, 'combined fixture bound')
    return {'status': 'PASS', 'active_seconds': total, 'fixture_reservations': count,
            'reserved_seconds': reserved, 'next_item': 'CVC-3-CONDITIONAL', 'next_run_started': False}
