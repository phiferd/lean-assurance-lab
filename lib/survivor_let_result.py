"""Validate and render the fixed survivor-reuse result without new launches."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from lib.cvc_prep import require, bind
from lib.cvc_process import atomic, sha
from lib import survivor_let_reuse as run

BASE = run.BASE
OUT = run.OUT
OUTPUTS = ('result.json', 'association-recommendation.json', 'report.md',
           'evidence-manifest.json')
TRANSITION = 'results/research/survivor-let-association-1/historical-transition.json'
HISTORICAL = {
    'results/mutants/registry.jsonl':
        'results/research/alt-survivors-2026-09-08/evidence/historical/results/mutants/registry.jsonl',
    'results/survivors/inventory.jsonl':
        'results/research/alt-survivors-2026-09-08/evidence/historical/results/survivors/inventory.jsonl',
}


def binding(root, path):
    path = Path(path)
    if not path.is_absolute():
        path = root / path
    require(path.is_file() and not path.is_symlink(), 'missing closure input: ' + str(path))
    return {'path': str(path.relative_to(root)), 'bytes': path.stat().st_size,
            'sha256': sha(path)}


def validate_chain(events):
    state = run.derive(events)
    attempts = state['attempts']
    require(len(attempts) == 6 and len(state['repairs']) == 1,
            'wrong finite attempt/replay count')
    reservations = [row['reservation'] for row in attempts]
    terminals = [row['terminal'] for row in attempts]
    require([row['phase'] for row in reservations] ==
            ['build', 'checker', 'checker', 'checker', 'checker', 'checker'],
            'not one build plus fixed cells')
    require([row.get('cell') for row in reservations] == [None, 0, 1, 2, 2, 3],
            'fixed cell/replay sequence changed')
    require([row['classification'] for row in terminals[1:]] ==
            ['ACCEPT', 'ACCEPT', 'CRASH', 'TYPECHECK_REFUSAL', 'ACCEPT'],
            'normalized result sequence changed')
    require(reservations[3]['manifest']['path'].endswith('-r2.json') and
            reservations[4]['manifest']['path'].endswith('-r3.json'),
            'repair tooling identity missing')
    repair = state['repairs'][0]
    require(repair['after_number'] == 4 and repair['phase'] == 'checker' and
            repair['cell'] == 2, 'repair does not bind failed baseline cell')
    require(all(row['cleanup_completed'] for row in terminals) and
            all(row['charged_seconds'] >= 0 for row in terminals),
            'cleanup/cost failure')
    require(sum(row['reserved_seconds'] for row in reservations
                if row['phase'] == 'build') <= 240 and
            sum(row['reserved_seconds'] for row in reservations
                if row['phase'] == 'checker') <= 240,
            'reservation cap exceeded')
    require(max(row['active_seconds'] + row['reserved_seconds']
                for row in reservations) <= 5400, 'active cap exceeded')
    require(state['next_action'] == ('DONE', None), 'fixed matrix not complete')
    return state


def validate_pre_admission(root):
    root = Path(root).resolve()
    events, state = run.Ledger(root).read()
    validate_chain(events)
    proposal = json.loads((root / run.PROPOSAL).read_text())
    require(proposal['limits'] == run.LIMITS and
            proposal['limits']['max_scientific_byte_variants'] == 0,
            'fixed proposal or limits changed')
    for live, historical in HISTORICAL.items():
        binding(root, live)
        binding(root, historical)
        require((root / live).read_bytes() == (root / historical).read_bytes(),
                'live classification state changed before successor admission: ' + live)
    # Check the immutable pre-admission state before requiring the historical
    # build payload.  A successor must be refused for its changed live
    # classification even in a portable checkout that deliberately omits that
    # heavyweight payload; an unchanged predecessor still reaches the strict
    # receipt and binary verification below.
    run.verify_attempts(root, events, live=True)
    inventory = json.loads((root / 'results/research/alt-survivors-2026-09-08/inventory.json').read_text())
    require('nanoda-gen-9face4e6a6f7' in inventory['pending_ids'] and
            inventory['classification'] == 'SURVIVED_WITHOUT_WITNESS' and
            inventory['count'] == 7,
            'selected survivor classification was transferred or lost')
    repair = state['repairs'][0]
    bind(root, repair['record'])
    script = (root / 'scripts/build-witness-admission').read_text()
    require('PREDECESSOR_REGISTRY_LINES = 604' in script and
            'IDS = ("nanoda-gen-f19ffc8a2e9b", "nanoda-gen-21ef4d1d32a1")' in script and
            'registry is not the immutable predecessor prefix or this exact successor' in script,
            'historical admission blocker characterization changed')
    return events, state, proposal


def validate_historical_closure(root, require_full_payload=False):
    """Validate the completed reuse result through its successor's bound overlay."""
    root = Path(root).resolve()
    transition = json.loads((root / TRANSITION).read_text())
    require(transition.get('kind') == 'SURVIVOR_LET_ASSOCIATION_HISTORICAL_TRANSITION',
            'wrong survivor-reuse historical transition')
    frozen = {row['path']: row for row in transition['predecessor_reuse_outputs']}
    require(set(frozen) == {BASE + '/' + name for name in OUTPUTS},
            'historical transition does not bind every frozen reuse output')
    for path, row in frozen.items():
        require(binding(root, path) == row, 'frozen reuse output changed: ' + path)

    substitutions = {row['live_path']: row for row in transition['historical_substitutions']}
    require(set(substitutions) == set(HISTORICAL),
            'historical transition substitution set changed')
    manifest = json.loads((root / BASE / 'evidence-manifest.json').read_text())
    manifest_inputs = {row['path']: row for row in manifest['inputs']}
    for live, historical in HISTORICAL.items():
        substitution = substitutions[live]
        require(substitution['original_live_binding'] == manifest_inputs[live],
                'historical transition does not reproduce old live binding: ' + live)
        require(substitution['historical_binding']['path'] == historical and
                binding(root, historical) == substitution['historical_binding'] ==
                {**manifest_inputs[live], 'path': historical},
                'historical substitution bytes changed: ' + live)
    for path, row in manifest_inputs.items():
        if path in HISTORICAL:
            continue
        if path.startswith('external/') and not require_full_payload:
            continue
        require(binding(root, path) == row, 'historical reuse evidence changed: ' + path)

    events, state = run.Ledger(root).read()
    validate_chain(events)
    if require_full_payload:
        run.verify_attempts(root, events, live=True)
    proposal = json.loads((root / run.PROPOSAL).read_text())
    successor = transition['successor_state']
    registry = (root / successor['registry']['path']).read_bytes()
    prefix_bytes = successor['registry']['bytes']
    require(len(registry) >= prefix_bytes and
            hashlib.sha256(registry[:prefix_bytes]).hexdigest() ==
            successor['registry']['sha256'],
            'successor registry prefix changed')
    require(successor['survivor_inventory'] ==
            substitutions['results/survivors/inventory.jsonl']['original_live_binding'],
            'successor survivor inventory is not bound through the historical substitution')
    for key in ('association', 'confirmation'):
        require(binding(root, successor[key]['path']) == successor[key],
                'successor association evidence changed: ' + key)
    require(successor['new_corpus_byte_variants'] == 0,
            'historical transition claims new corpus bytes')
    return events, state, proposal


def validate(root, require_full_payload=False):
    root = Path(root).resolve()
    if (root / TRANSITION).is_file():
        return validate_historical_closure(root, require_full_payload)
    return validate_pre_admission(root)


def evidence_inputs(root, events, state, proposal):
    paths = {run.PROPOSAL, run.WORK, run.MANIFEST,
             'config/survivor-let-reuse-0001-r2.json',
             'config/survivor-let-reuse-0001-r3.json',
             BASE + '/entry-decision.json', BASE + '/source-materialization.json',
             BASE + '/runtime-manifest.json',
             'results/research/alt-survivors-2026-09-08/inventory.json',
             BASE + '/configs/control.json', BASE + '/configs/candidate.json',
             OUT + '/execution/events.jsonl', OUT + '/execution/state.json',
             'scripts/build-witness-admission', *HISTORICAL.keys(), *HISTORICAL.values()}
    for key in ('mutation_spec', 'source_lock', 'control', 'candidate',
                'historical_official_result', 'baseline'):
        paths.add(proposal[key]['path'])
    for attempt in state['attempts']:
        reservation, terminal = attempt['reservation'], attempt['terminal']
        paths.add(reservation['manifest']['path'])
        paths.update(row['path'] for row in terminal['receipts'])
        if terminal.get('binary'):
            paths.add(terminal['binary']['path'])
    paths.update(row['record']['path'] for row in state['repairs'])
    return [binding(root, path) for path in sorted(paths)]


def artifacts(root):
    root = Path(root).resolve()
    events, state, proposal = validate_pre_admission(root)
    evidence = evidence_inputs(root, events, state, proposal)
    build = state['attempts'][0]['terminal']
    final = {0: state['attempts'][1]['terminal'],
             1: state['attempts'][2]['terminal'],
             2: state['attempts'][4]['terminal'],
             3: state['attempts'][5]['terminal']}
    result = {
        'schema_version': 1, 'item_id': run.ITEM, 'run_id': run.RUN,
        'outcome': 'SUCCESS', 'scientific_status': 'FIXED_PAIR_DISTINGUISHES_MUTANT',
        'selected_mutant': proposal['selected_mutant'],
        'comparison': {proposal['matrix'][index]['id']: final[index]['classification']
                       for index in range(4)},
        'build': {'binary': build['binary'], 'charged_seconds': build['charged_seconds'],
                  'reservations': 1},
        'checker': {'reservations': 5,
                    'charged_seconds': sum(row['terminal']['charged_seconds']
                                           for row in state['attempts'][1:]),
                    'retained_repair_replays': 1},
        'total_process_seconds': state['charged_seconds'],
        'research_counts': {'offline_builds': 1, 'checker_launches': 5,
                            'scientific_byte_variants': 0, 'proof_launches': 0,
                            'research_network_requests': 0,
                            'external_research_actions': 0},
        'association': 'RECOMMENDED_PENDING_SUCCESSOR_ADMISSION_ROUTE',
        'classification_changed': False, 'pending_survivors': 7,
        'next_item': {'id': 'SURVIVOR-LET-ASSOCIATION-1', 'status': 'WAITING',
                      'started': False},
        'limits': ('The result is local to the exact pinned Nanoda source, binaries, '
                   'configuration and existing 601-byte pair. It is not semantic '
                   'authority, a transferred 21ef observation, an official-checker '
                   'result, or an upstream defect claim.'),
    }
    blocker = binding(root, 'scripts/build-witness-admission')
    recommendation = {
        'schema_version': 1, 'item_id': run.ITEM,
        'decision': 'RECOMMENDED_PENDING_SUCCESSOR',
        'target': proposal['selected_mutant'],
        'evidence': {'existing_candidate': binding(root, proposal['candidate']['path']),
                     'existing_control': binding(root, proposal['control']['path']),
                     'fresh_execution': binding(root, OUT + '/execution/events.jsonl')},
        'action': ('Implement and test a bounded successor association/admission route '
                   'that reuses these exact corpus bytes without a duplicate artifact.'),
        'admission_blocker': {**blocker,
            'reason': ('The frozen admission producer accepts only f19 and 21ef and '
                       'only its 604-line predecessor or exact two-row successor. '
                       'Editing it would invalidate historical producer bindings.')},
        'preserved_state': {'classification': 'SURVIVED_WITHOUT_WITNESS',
                            'pending_survivors': 7, 'registry_appends': 0,
                            'duplicate_corpus_artifacts': 0,
                            'external_actions': 0},
    }
    report = (
        '# Survivor let reuse result\n\n'
        'The exact fixed comparison succeeded. The pinned baseline and freshly built '
        '9face mutant both accepted the existing control. The baseline candidate then '
        'reached the bound let-value `assert_def_eq` refusal path, while the selected '
        'mutant accepted the same 601-byte candidate. One overly strict normalizer '
        'classified the first baseline-candidate receipt as `CRASH`; that receipt and '
        'charge remain, and a tested tooling revision replayed only the same cell.\n\n'
        'This supports associating the already admitted let regression with the '
        'distinct 9face mutation identity. Current registry and survivor inventory '
        'bytes remain unchanged because the historical admission producer is frozen '
        'around f19 and 21ef and cannot append 9face or reuse identical corpus bytes '
        'without a successor. `SURVIVOR-LET-ASSOCIATION-1` is selected WAITING to '
        'implement that no-duplicate route after separate authorization.\n\n'
        f'Total process time was {state["charged_seconds"]:.9f} seconds: one counted '
        'offline build and five checker reservations, including one retained audit '
        'replay. No new scientific export bytes, proof, research-network request, '
        'external action, official-observer run, or upstream report occurred.\n')
    manifest = {'schema_version': 1, 'kind': 'SURVIVOR_LET_REUSE_CLOSURE',
                'inputs': evidence, 'derived_outputs': list(OUTPUTS[:-1]),
                'note': 'Generated artifacts do not replace their canonical raw inputs.'}
    return {'result.json': result, 'association-recommendation.json': recommendation,
            'report.md': report, 'evidence-manifest.json': manifest}


def build(root, write=False, require_full_payload=False):
    root = Path(root).resolve()
    if (root / TRANSITION).is_file():
        require(not write, 'completed reuse outputs are frozen after successor association')
        validate_historical_closure(root, require_full_payload)
        return {
            name: ((root / BASE / name).read_text() if name == 'report.md'
                   else json.loads((root / BASE / name).read_text()))
            for name in OUTPUTS
        }
    rows = artifacts(root)
    if write:
        for name, value in rows.items():
            path = root / BASE / name
            path.parent.mkdir(parents=True, exist_ok=True)
            if isinstance(value, str):
                path.write_text(value)
            else:
                atomic(path, value)
    else:
        for name, value in rows.items():
            path = root / BASE / name
            require(path.is_file(), 'missing derived closure artifact: ' + name)
            actual = path.read_text() if isinstance(value, str) else json.loads(path.read_text())
            require(actual == value, 'derived closure artifact drift: ' + name)
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true')
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--require-full-payload', action='store_true')
    args = parser.parse_args()
    require(args.write != args.check, 'choose --write or --check')
    build(Path(__file__).resolve().parents[1], args.write, args.require_full_payload)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
