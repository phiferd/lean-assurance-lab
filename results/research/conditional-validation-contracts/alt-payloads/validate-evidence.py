#!/usr/bin/env python3
"""Validate the closed diagnostic proposal; optionally recheck local donors.

No compiler, proof runtime or network operation is launched. The default
checks tracked evidence and committed predecessors without local source donors.
"""
import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
FILES = {'work-record.json', 'source-closure.json', 'inspect-source-closure.py',
         'proposal.json', 'report.md', 'validate-evidence.py'}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def load(path):
    return json.loads(path.read_text())


def check_binding(row, data):
    require(hashlib.sha256(data).hexdigest() == row['sha256'],
            'digest mismatch: ' + row['path'])
    require(len(data) == row['bytes'], 'size mismatch: ' + row['path'])


def validate():
    manifest = load(OUT / 'evidence-manifest.json')
    require(manifest['item_id'] == 'ALT-PAYLOADS', 'manifest item')
    rows = manifest['files']
    require(len(rows) == len(FILES) and {r['path'] for r in rows} == FILES,
            'manifest must bind exactly the closed evidence files')
    for row in rows:
        check_binding(row, (OUT / row['path']).read_bytes())
    work = load(OUT / 'work-record.json')
    proposal = load(OUT / 'proposal.json')
    source = load(OUT / 'source-closure.json')
    require(work['item_id'] == proposal['item_id'] == source['item_id'] == 'ALT-PAYLOADS', 'item')
    require(work['status'] == 'COMPLETE' and work['outcome'] == proposal['outcome'] == 'SUCCESS', 'closure')
    require(proposal['scientific_status'] == 'STATIC_DEPENDENCY_REPAIR_PROPOSAL_UNEXECUTED', 'claim boundary')
    elapsed = (datetime.fromisoformat(work['ended_at']) -
               datetime.fromisoformat(work['started_at'])).total_seconds() / 60
    require(0 <= elapsed <= 90 and abs(elapsed - work['active_minutes']) < 1e-6, 'session time')
    require(work['budget']['max_sessions'] == work['consumed']['sessions'] == 1, 'session count')
    require(work['sessions'] == [{'started_at': work['started_at'], 'ended_at': work['ended_at']}], 'session ledger')
    for key in ('builds', 'checker_launches', 'lean_executions', 'lake_executions', 'downloads', 'toolchain_installs'):
        require(work['budget'][key] == work['consumed'][key] == 0, 'forbidden diagnostic action: ' + key)
    for row in work['inputs']:
        data = subprocess.check_output(['git', 'show', work['input_commit'] + ':' + row['path']], cwd=ROOT)
        check_binding(row, data)
    predecessor_path = ROOT / proposal['predecessor_protocol']['path']
    check_binding(proposal['predecessor_protocol'], predecessor_path.read_bytes())
    protocol = load(predecessor_path)
    require(protocol['status'] == 'SPECIFIED_NOT_EXECUTABLE', 'predecessor protocol changed')
    inventory = load(ROOT / 'results/research/conditional-validation-contracts/cvc-2/runtime-inventory.json')
    require(proposal['pins'] == inventory['selected_revision'], 'source pins')
    require(proposal['runtime']['lean_binary'] == inventory['lean_runtime']['binaries'][0], 'runtime binary identity')
    require(proposal['runtime']['version_header'] == inventory['lean_runtime']['reported_version_source'], 'runtime version identity')
    require(source['inputs']['contract']['sha256'] == protocol['signature']['sha256'], 'immutable signature binding')
    require(source['inputs']['runtime_inventory']['sha256'] == hashlib.sha256((ROOT / 'results/research/conditional-validation-contracts/cvc-2/runtime-inventory.json').read_bytes()).hexdigest(), 'source inventory binding')
    graph = source['closure']
    noncore = {r['module']: r for r in graph['modules'] if r['kind'] != 'core_runtime'}
    order = graph['topological_noncore_order']
    require(len(order) == len(noncore) == graph['noncore_module_count'] == 37 and set(order) == set(noncore), 'closure cardinality')
    seen = set()
    for module in order:
        row = noncore[module]
        require(all(i['module'] in seen for i in row['imports'] if i['module'] in noncore), 'dependency order')
        require(module.startswith(('Lean4Lean.', 'Batteries.')), 'Lab or unknown source in preparation')
        seen.add(module)
    l4l = {m: r for m, r in noncore.items() if r['kind'] == 'lean4lean'}
    require(len(l4l) == 12 and sum(r['kind'] == 'batteries' for r in noncore.values()) == 25, 'package counts')
    pinned = {r['module']: r for r in inventory['lean4lean_donor']['selected_source_closure']}
    for module, row in l4l.items():
        require(row['git_blob_sha1'] == row['target_pin']['expected_blob_sha1'] ==
                pinned[module]['pinned_git_blob']['expected_blob_sha1'], 'target correspondence')
        require(row['source']['sha256'] == pinned[module]['source']['sha256'], 'target source hash')
    for row in noncore.values():
        if row['kind'] == 'batteries':
            require(row['git_blob_sha1'] == row['batteries_tree_blob_sha1'], 'Batteries committed blob')
    require(graph['batteries_source_receipt'] == {'head': proposal['pins']['batteries_revision'], 'clean': True}, 'Batteries checkout receipt')
    previous = {r['module'] for r in inventory['batteries']['selected_source_closure']}
    added = sorted(m for m, r in noncore.items() if r['kind'] == 'batteries' and m not in previous)
    require(added == proposal['diagnostic_delta']['previously_omitted_batteries'], 'preserved inventory delta')
    comp = proposal['compilation']
    require(comp['status'] == 'PROPOSED_NOT_RUN' and comp['item_id'] == 'CVC-PREP-1', 'preparation status')
    require(comp['limits']['max_compilation_attempts'] == len(order), 'compilation attempt budget')
    require(comp['limits']['attempt_timeout_seconds'] == 300 and comp['limits']['max_compilation_seconds'] == 6600, 'compilation time budget')
    require(comp['limits']['max_sessions'] == 2 and comp['limits']['max_active_seconds'] == 10800, 'preparation sessions')
    for key in ('checker_launches', 'lab_elaborations', 'proof_attempts', 'lake_executions',
                'native_compiler_invocations', 'network_requests', 'toolchain_installs'):
        require(comp['limits'][key] == 0, 'preparation forbidden scope: ' + key)
    require(comp['argv_template'] == ['{bound_lean_binary}', '-o',
            '{repository}/external/cvc-u1-dependencies-0001/build/lib/lean/{module_path}.olean',
            '{module_path}.lean'], 'direct compiler argv')
    require(comp['environment']['inherit_environment'] is False, 'environment inheritance')
    for binding in proposal['inspected_reuse_bindings']:
        check_binding(binding, (ROOT / binding['path']).read_bytes())
    runner = proposal['runner_prerequisite']
    require(runner['status'] == 'PROPOSED_PLANNED_UNIMPLEMENTED', 'runner status')
    require(runner['cvc3_budget_unchanged']['proof_build_attempts'] == protocol['limits']['proof_build_attempts'] == 12, 'CVC-3 attempt cap')
    require(runner['cvc3_budget_unchanged']['signature_attempts_included'] == protocol['signature_attempt']['attempt_number'] == 1, 'counted signature')
    for key in ('lean_executions', 'checker_launches', 'proof_attempts'):
        require(runner['limits'][key] == 0, 'runner implementation scope')
    require(proposal['runtime']['binding_status'] ==
            'BINARY_AND_HEADER_BOUND_COMPLETE_RUNTIME_MANIFEST_REQUIRED_BEFORE_PREPARATION_LAUNCH', 'runtime limitation')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check-local', action='store_true')
    args = parser.parse_args()
    try:
        validate()
        if args.check_local:
            subprocess.run([sys.executable, str(OUT / 'inspect-source-closure.py'), '--check'], check=True, cwd=ROOT)
        print('PASS: exact diagnostic evidence, committed inputs, 37-module proposal and bounded zero-execution closure')
    except (ValueError, KeyError, OSError, subprocess.CalledProcessError) as error:
        print('FAIL: ' + str(error), file=sys.stderr)
        raise SystemExit(1)
