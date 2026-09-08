"""Offline projection of retained conditional-contract evidence; never runs science."""
import hashlib
import json
from pathlib import Path
import re
import subprocess

BASE = Path('results/research/conditional-validation-contracts')
OUTPUT = BASE / 'cvc-5-conditional'
PROOF = BASE / 'cvc-a7-repair-1/result.json'
COMPARISON = BASE / 'cvc-4-conditional/result.json'
OWNERSHIP = BASE / 'cvc-4-ownership-1/result.json'
ZERO = dict.fromkeys(('new_scientific_byte_variants', 'observer_launches', 'proof_launches',
                     'setup_build_launches', 'research_network_launches', 'external_research_actions'), 0)
PROFILE_ONLY = {
    'external/lean-kernel-arena/_build/checkers/nanoda/src/target/release/nanoda_bin',
    'external/lean-kernel-arena/_build/checkers/nanoda/src/config.json',
    'external/lean-kernel-arena/_build/checkers/official/src/.lake/build/bin/kernel',
}
REQUIRED = [str(p) for p in (PROOF, COMPARISON, OWNERSHIP,
    BASE / 'cvc-2/contract.json', BASE / 'cvc-2/examples.json',
    BASE / 'cvc-4-ownership-1/cases.json', BASE / 'cvc-4-ownership-1/source-mapping.json')]
REQUIRED += ['research/conditional-validation-contracts/cvc2/Contract.lean',
             'lib/cvc4_ownership_inputs.py', 'tests/test_cvc4_ownership_inputs.py',
             'lib/cvc2_artifact.py', 'lib/cvc_prep.py',
             'corpus/generated/universe-imax-right-succ.ndjson',
             'corpus/generated/universe-imax-right-succ-control.ndjson',
             'config/declaration-validation-catalog.json', 'docs/UPSTREAM_ISSUES.md']


def require(value, message):
    if not value:
        raise ValueError(message)


def read(root, path):
    return json.loads((root / path).read_text())


def binding(root, path):
    raw = (root / path).read_bytes()
    return {'path': str(path), 'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}


def embedded_bindings(value):
    if isinstance(value, dict):
        if 'path' in value and 'sha256' in value:
            yield value
        for child in value.values():
            yield from embedded_bindings(child)
    elif isinstance(value, list):
        for child in value:
            yield from embedded_bindings(child)


def check_receipt_coverage(evidence, manifest):
    inventory = {row['path']: row for row in manifest['inputs']}
    for receipt in embedded_bindings(evidence):
        path = receipt['path']
        # Exactly these three observer payloads are historical profile metadata.
        # Portable package validation does not establish executable availability.
        if path in PROFILE_ONLY:
            continue
        require(path in inventory, 'unbound embedded receipt: ' + path)
        require(receipt['sha256'] == inventory[path]['sha256'], 'receipt digest mismatch: ' + path)
        if 'bytes' in receipt:
            require(receipt['bytes'] == inventory[path]['bytes'], 'receipt length mismatch: ' + path)


def check_bindings(root, manifest):
    """Pin every input to one existing commit and preserve immutable current bytes."""
    revision = manifest['base_commit']
    require(re.fullmatch('[0-9a-f]{40}', revision), 'invalid base commit')
    rows = manifest['inputs']
    paths = [row['path'] for row in rows]
    require(len(paths) == len(set(paths)) and set(REQUIRED) <= set(paths), 'missing or duplicate inputs')
    for path in paths:
        require(not Path(path).is_absolute() and '..' not in Path(path).parts
                and '\n' not in path and '\r' not in path, 'unsafe evidence path')
    result = subprocess.run(['git', 'cat-file', '--batch'], cwd=root,
                            input=''.join(f'{revision}:{p}\n' for p in paths).encode(),
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    raw, offset = result.stdout, 0
    for row in rows:
        end = raw.index(b'\n', offset)
        header = raw[offset:end].split()
        require(len(header) == 3 and header[1] == b'blob', 'missing historical input')
        size = int(header[2]); content = raw[end + 1:end + 1 + size]; offset = end + size + 2
        require(size == row['bytes'] and hashlib.sha256(content).hexdigest() == row['sha256'],
                'historical input binding changed: ' + row['path'])
        require(type(row['current_bytes_required']) is bool, 'invalid current binding policy')
        mutable = row['path'] in ('docs/RESEARCH_STATUS.md', 'config/research-queue.json',
                                  'docs/research/CONDITIONAL_VALIDATION_CONTRACTS_PLAN.md',
                                  'docs/UPSTREAM_ISSUES.md', 'results/assurance/current.json')
        require(row['current_bytes_required'] == (not mutable), 'binding policy changed')
        if not mutable:
            require((root / row['path']).read_bytes() == content, 'retained evidence changed: ' + row['path'])
    require(offset == len(raw), 'unexpected historical evidence response')
    return len(rows)


def projection(root):
    proof, comparison, ownership = [read(root, p) for p in (PROOF, COMPARISON, OWNERSHIP)]
    require(proof['outcome'] == ownership['outcome'] == 'SUCCESS'
            and comparison['outcome'] == 'BOUNDED_UNRESOLVED', 'predecessor outcomes changed')
    cases = read(root, BASE / 'cvc-4-ownership-1/cases.json')['cases']
    catalog = read(root, 'config/declaration-validation-catalog.json')
    authority = next(e for e in catalog['entries']
                     if e['characterization']['id'] == 'DECL.UNIVERSE.PARAM_OWNERSHIP')
    return {
        'proof': {'source': str(PROOF), 'contract_id': proof['contract_id'],
                  'scientific_status': proof['scientific_status'],
                  'declarations': proof['result_declarations'], 'transitive_axioms': proof['transitive_axioms'],
                  'raw_proof_evidence': proof['stop']['evidence'],
                  'required_acceptance_ids': read(root, BASE / 'cvc-2/examples.json')['required_acceptance_ids']},
        'original_observations': {'source': str(COMPARISON), 'rows': comparison['observations']},
        'ownership_observations': {'source': str(OWNERSHIP), 'rows': ownership['cases']},
        'regression': {'source': str(BASE / 'cvc-4-ownership-1/cases.json'), 'cases': cases,
                       'implementation': 'lib/cvc4_ownership_inputs.py',
                       'tests': 'tests/test_cvc4_ownership_inputs.py'},
        'observer_profiles': read(root, BASE / 'cvc-4-ownership-1/source-mapping.json')['observers'],
        'prior_costs': {'comparison': comparison['summary'], 'ownership': ownership['research_counts'],
                        'ownership_accounting': ownership['accounting'], 'proof': proof['summary'],
                        'note': 'Different historical active-time scopes are retained; prior unknown fixture costs remain unknown. No reservations are reopened.'},
        'catalog_boundary': {'id': authority['characterization']['id'],
                             'denotation': authority['identity_denotation'],
                             'authority': authority['characterization']['authority'],
                             'soundness_relevance': authority['characterization']['soundness_relevance']}}


def validate_result(root, result):
    require(result['item_id'] == 'CVC-5-CONDITIONAL' and result['outcome'] == 'SUCCESS'
            and result['scientific_status'] == 'EXISTING_EVIDENCE_REUSE_PACKAGE', 'package identity changed')
    require(result['evidence'] == projection(root), 'package differs from retained evidence')
    require(result['research_counts'] == ZERO and result['next_item_started'] is False,
            'package claims new scientific work')
    decision = result['phase_decision']
    require(decision['decision'] == 'REUSE' and decision['execution'] == 'PAUSED'
            and decision['next_item'] == 'CVC-NEXT-AUTHORIZATION', 'phase decision changed')
    require(result['external_action']['decision'] == 'NO_NEW_EXTERNAL_ACTION', 'external action changed')
    for name in ('action', 'target', 'priority', 'prerequisites', 'evidence_refs'):
        require(result['recommendation'].get(name), 'incomplete recommendation')
    for name in ('assumptions_discharged', 'executable_refinement_proved', 'invalid_accepted_proof',
                 'catalog_promoted', 'current_master_executed', 'broader_acceptance_proved'):
        require(result['nonclaims'].get(name) is False, 'unsupported assurance claim: ' + name)


def validate(root):
    root = Path(root)
    manifest = read(root, OUTPUT / 'evidence-manifest.json')
    count = check_bindings(root, manifest)
    result = read(root, OUTPUT / 'result.json')
    require(result == {**read(root, OUTPUT / 'decision.json'), 'evidence': projection(root)},
            'canonical decision/projection drift')
    validate_result(root, result)
    check_receipt_coverage(result['evidence'], manifest)
    work = read(root, OUTPUT / 'work-record.json')
    require(work['base_commit'] == manifest['base_commit'], 'work input commit changed')
    require(work['research_counts'] == ZERO, 'work records scientific execution')
    require(work['budget'] == {'max_active_seconds': 3600, 'max_interval_seconds': 3600, **ZERO},
            'work budget changed')
    from lib.cvc4_adapter_review import check_work
    # Reuse the existing strict paired-clock checker with only item/count naming adapted.
    normalized = {**work, 'item_id': 'CVC-4-ADAPTER-REVIEW',
                  'research_counts': dict.fromkeys(('byte_variants', 'observer_launches', 'proof_builds',
                                                   'setup_launches', 'research_network_launches'), 0)}
    normalized['budget'] = {'max_active_seconds': 3600, 'max_interval_seconds': 3600,
                            **normalized['research_counts']}
    elapsed = check_work(normalized)
    return {'item_id': result['item_id'], 'outcome': result['outcome'], 'bound_inputs': count,
            'active_seconds': elapsed, 'phase': 'REUSE; execution PAUSED', 'research_counts': ZERO}
