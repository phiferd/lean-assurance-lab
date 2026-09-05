"""Exact Gate-10 construction, evidence derivation and reporting.

The tiny binder-only type calculation checks construction evidence; it is not
a general Lean checker or a source of normative authority. Authority remains
the frozen Gate-6 theorem-only approval carried through Gates 7–9.
"""
from __future__ import annotations

import hashlib
import importlib.machinery
import importlib.util
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL_COMMIT = '3429ca1412dc5a33259ef432e9b64670a5be4f54'
PROTOCOL = 'config/declaration-validation-publication-study-gate-9.json'
FREEZE = 'results/research/declaration-validation-publication-study-gate-8-input-freeze.json'
BASELINE = 'results/research/declaration-validation-publication-study-baseline-comparator.json'
RUN = 'results/research/publication-study-theorem-control-0001'
RESULT = RUN + '/result.json'
REPORT = 'docs/research/DECLARATION_VALIDATION_PUBLICATION_STUDY_GATE_10_REPORT.md'
ACTIONS = RUN + '/action-recommendations.json'
SCHEMA = 'schemas/declaration-validation-publication-study-gate-10.schema.json'
ENTRY = 'DECL.THEOREM.TYPE_PROP'


def encode(value):
    return (json.dumps(value, indent=2, sort_keys=True) + '\n').encode()


def sha(content):
    return hashlib.sha256(content).hexdigest()


def read(path):
    return json.loads((ROOT / path).read_bytes())


def binding(path):
    data = (ROOT / path).read_bytes()
    return {'path': path, 'sha256': sha(data), 'bytes': len(data)}


def git_binding(path, commit=PROTOCOL_COMMIT):
    blob = subprocess.check_output(['git', 'rev-parse', f'{commit}:{path}'], cwd=ROOT).decode().strip()
    data = subprocess.check_output(['git', 'cat-file', 'blob', blob], cwd=ROOT)
    return {'path': path, 'git_commit': commit, 'git_blob': blob, 'sha256': sha(data)}


def module(name, path):
    loader = importlib.machinery.SourceFileLoader(name, str(ROOT / path))
    spec = importlib.util.spec_from_loader(name, loader)
    value = importlib.util.module_from_spec(spec)
    loader.exec_module(value)
    return value


def protocol_inputs(full_chain=False):
    g9 = module('gate9_for_gate10', 'scripts/validate-declaration-validation-publication-study-gate-9')
    for path in [PROTOCOL, 'schemas/declaration-validation-publication-study-gate-9.schema.json',
                 'scripts/validate-declaration-validation-publication-study-gate-9',
                 'tests/test_declaration_validation_publication_study_gate_9.py']:
        bound = git_binding(path)
        if sha((ROOT / path).read_bytes()) != bound['sha256']:
            raise ValueError('frozen Gate-9 bytes changed: ' + path)
    errors = g9.validate_gate9(full_chain=full_chain)
    if errors:
        raise ValueError('\n'.join(errors))
    plan = read(PROTOCOL)
    for name in ('gate8_baseline', 'gate8_input_freeze'):
        b = plan['bindings'][name]
        if sha((ROOT / b['path']).read_bytes()) != b['sha256']:
            raise ValueError('current predecessor differs from frozen Gate-9 input: ' + name)
    return plan, read(FREEZE), read(BASELINE)


def frozen_negative(freeze):
    b = freeze['git_inputs']['m6_nonprop_candidate']
    if git_binding(b['path'], b['git_commit']) != {k: b[k] for k in ('path', 'git_commit', 'git_blob', 'sha256')}:
        raise ValueError('negative historical binding mismatch')
    data = subprocess.check_output(['git', 'cat-file', 'blob', b['git_blob']], cwd=ROOT)
    if sha(data) != b['sha256']:
        raise ValueError('negative digest mismatch')
    return data


def construct_control(negative):
    """Called only after candidate reservation, never during preflight."""
    rows = [json.loads(x) for x in negative.splitlines()]
    if len(rows) != 7 or rows[-1] != {'thm': {'all': [1], 'levelParams': [], 'name': 1, 'type': 0, 'value': 2}}:
        raise ValueError('unexpected frozen negative wrapper')
    # Preserve all six prefix records verbatim, including exporter metadata and
    # original binder name x. The proposed p is alpha-renamed x, without a new
    # outer name. h is the only new name. Old expression 2 remains unused.
    additions = [
        {'in': 3, 'str': {'pre': 0, 'str': 'h'}},
        {'ie': 3, 'bvar': 1},
        {'ie': 4, 'forallE': {'binderInfo': 'default', 'body': 3, 'name': 3, 'type': 1}},
        {'ie': 5, 'forallE': {'binderInfo': 'default', 'body': 4, 'name': 2, 'type': 0}},
        {'ie': 6, 'lam': {'binderInfo': 'default', 'body': 1, 'name': 3, 'type': 1}},
        {'ie': 7, 'lam': {'binderInfo': 'default', 'body': 6, 'name': 2, 'type': 0}},
        {'thm': {'all': [1], 'levelParams': [], 'name': 1, 'type': 5, 'value': 7}},
    ]
    return b'\n'.join(negative.splitlines()[:-1]) + b'\n' + b''.join(
        (json.dumps(x, sort_keys=True, separators=(',', ':')) + '\n').encode() for x in additions)


def shift(expr, amount, depth=0):
    tag = expr[0]
    if tag == 'bvar':
        return (tag, expr[1] + amount if expr[1] >= depth else expr[1])
    if tag == 'sort':
        return expr
    return (tag, shift(expr[1], amount, depth), shift(expr[2], amount, depth + 1))


def infer(expr, context=()):
    tag = expr[0]
    if tag == 'sort':
        return ('sort', expr[1] + 1)
    if tag == 'bvar':
        if expr[1] < 0 or expr[1] >= len(context):
            raise ValueError('loose bound variable')
        return shift(context[expr[1]], expr[1] + 1)
    if tag not in ('pi', 'lam'):
        raise ValueError('outside binder-only construction')
    domain, body = expr[1:]
    domain_sort = infer(domain, context)
    if domain_sort[0] != 'sort':
        raise ValueError('binder domain is not sort-valued')
    body_type = infer(body, (domain, *context))
    if tag == 'lam':
        return ('pi', domain, body_type)
    if body_type[0] != 'sort':
        raise ValueError('Pi codomain is not sort-valued')
    # Lean's imax rule: a Prop-valued body makes the entire Pi Prop-valued.
    return ('sort', 0 if body_type[1] == 0 else max(domain_sort[1], body_type[1]))


def inspect_pair_member(data):
    rows = [json.loads(x) for x in data.splitlines()]
    nodes, names, declarations = {}, {0: ''}, []
    for row in rows:
        if 'meta' in row:
            continue
        if 'in' in row:
            if row['in'] in names or set(row) != {'in', 'str'} or row['str']['pre'] != 0:
                raise ValueError('invalid name record')
            names[row['in']] = row['str']['str']
        elif 'ie' in row:
            idx = row['ie']
            if idx in nodes:
                raise ValueError('duplicate expression index')
            if set(row) == {'ie', 'sort'} and row['sort'] == 0:
                nodes[idx] = ('sort', 0)
            elif set(row) == {'ie', 'bvar'} and type(row['bvar']) is int and row['bvar'] >= 0:
                nodes[idx] = ('bvar', row['bvar'])
            elif set(row) in ({'ie', 'forallE'}, {'ie', 'lam'}):
                key = 'forallE' if 'forallE' in row else 'lam'
                b = row[key]
                if set(b) != {'binderInfo', 'body', 'name', 'type'} or b['binderInfo'] != 'default' or b['name'] not in names:
                    raise ValueError('invalid binder')
                nodes[idx] = ('pi' if key == 'forallE' else 'lam', nodes[b['type']], nodes[b['body']])
            else:
                raise ValueError('unregistered expression construct')
        elif set(row) == {'thm'}:
            declarations.append(row['thm'])
        else:
            raise ValueError('outside registered theorem family')
    if len(declarations) != 1:
        raise ValueError('expected exactly one theorem')
    decl = declarations[0]
    if set(decl) != {'all', 'levelParams', 'name', 'type', 'value'} or decl['all'] != [decl['name']] or decl['levelParams']:
        raise ValueError('unexpected theorem wrapper')
    typ, val = nodes[decl['type']], nodes[decl['value']]
    sort, value_type = infer(typ), infer(val)
    if sort[0] != 'sort' or value_type != typ:
        raise ValueError('declaration sorthood or proof typing failed')
    return {'declaration_name': names[decl['name']], 'declaration': decl,
            'type_ast': typ, 'value_ast': val, 'type_inferred_sort': sort,
            'value_inferred_type': value_type, 'metadata': rows[0]['meta'],
            'expression_records': [x for x in rows if 'ie' in x]}


def analyze_pair(negative, control, plan, freeze):
    if sha(negative) != freeze['git_inputs']['m6_nonprop_candidate']['sha256']:
        raise ValueError('negative is not exact frozen M6 input')
    if control != construct_control(negative):
        raise ValueError('control deviates from the single preregistered constructor')
    n, c = inspect_pair_member(negative), inspect_pair_member(control)
    if n['type_inferred_sort'] != ('sort', 1) or c['type_inferred_sort'] != ('sort', 0):
        raise ValueError('target predicate was not repaired')
    na = {'DECL.UNIVERSE.PARAM_OWNERSHIP', 'EXPR.CONST.UNIVERSE_ARITY',
          'DECL.ENV.CURRENT_DECL_NOT_VISIBLE', 'EXPR.LET.ANNOTATION_SORT',
          'EXPR.LET.VALUE_TYPE_MATCH', 'EXPR.APP.FUNCTION_TYPE', 'EXPR.APP.ARGUMENT_TYPE_MATCH'}
    bases = {
        'DECL.ENV.NAME_FRESHNESS': 'Single fresh m6TransferNonPropTheorem in empty-environment replay; no prior declarations or constants. Wrapper and name equal the frozen M6 auxiliary evidence.',
        'DECL.UNIVERSE.PARAM_UNIQUENESS': 'The exact levelParams list is empty in both wrappers.',
        'DECL.TYPE.NO_FREE_VARS': 'Binder-only AST contains no free-variable constructor; recursive scope/type checks succeed.',
        'DECL.TYPE.NO_METAVARS': 'Every expression record is sort, bvar, forallE or lam; no metavariable constructor.',
        'DECL.EXPR.NO_LOOSE_BOUND_VARS': 'Negative bvar 0 is under one Pi. Control Pi domain bvar 0 denotes outer x, Pi body bvar 1 denotes x under h, lambda body bvar 0 denotes h; all are checked at their actual context depths.',
        'DECL.UNIVERSE.PARAM_OWNERSHIP': 'Only implicit universe zero; no universe parameter or constant arguments occur.',
        'EXPR.CONST.UNIVERSE_ARITY': 'No constant expression occurs.',
        'DECL.TYPE.WELL_FORMED': 'Recursive binder-only inference checks the exact type AST and all domains/codomains.',
        'DECL.TYPE.SORT_VALUED': 'Negative Sort 0 : Sort 1. Control forall (x : Prop), x -> x : Sort 0 by imax(_,0)=0.',
        'DECL.VALUE.WELL_FORMED': 'Negative forall (x : Prop), x is a well-formed proposition. Control fun (x : Prop) (h : x) => h is well typed by variable and lambda rules in the displayed contexts.',
        'DECL.VALUE.TYPE_MATCH': 'Structural equality between inferred value type and declared type is checked for each exact AST; no reduction or unchecked constant is needed.',
        'DECL.ENV.CURRENT_DECL_NOT_VISIBLE': 'Neither member contains any constant reference, including self-reference.',
        'EXPR.BINDER.DOMAIN_SORT': 'Outer domain Prop : Sort 1. Each inner domain x : Sort 0 under x : Prop, for Pi and lambda. Recursive inference checks each occurrence.',
        'EXPR.PI.CODOMAIN_SORT': 'Negative body x : Sort 0. Control inner body x : Sort 0 under x,h; inner and outer Pi are Sort 0 by imax. Scope shifting preserves outer x under h.',
        'EXPR.LET.ANNOTATION_SORT': 'No let expression occurs.',
        'EXPR.LET.VALUE_TYPE_MATCH': 'No let expression occurs.',
        'EXPR.APP.FUNCTION_TYPE': 'No application expression occurs.',
        'EXPR.APP.ARGUMENT_TYPE_MATCH': 'No application expression occurs.',
    }
    competitors = [{'entry_id': entry, 'negative': 'NOT_APPLICABLE' if entry in na else 'SATISFIED',
                    'control': 'NOT_APPLICABLE' if entry in na else 'SATISFIED', 'basis': bases[entry]}
                   for entry in plan['targets'][0]['competing_obligation_ids']]
    return {'entry_id': ENTRY, 'negative': n, 'control': c,
            'expected_outcomes': {'negative': 'REJECT', 'control': 'ACCEPT'},
            'authority': {'source': 'gate6_catalog', 'binding': freeze['git_inputs']['gate6_catalog'],
                          'claim': 'CLAIM.SOURCE.MANUAL.DEFS.THEOREM_PROP',
                          'scope': 'Only theorem proposition-valued type; no other authority promoted.'},
            'competing_obligations': competitors,
            'transformation': {'preserved_prefix_records': 6, 'added_expression_ids': [3, 4, 5, 6, 7],
                               'replaced_declaration_fields': ['type', 'value'],
                               'added_name': 'h', 'retained_unused_expression_ids': [2],
                               'unavoidable_differences': plan['targets'][0]['matched_control']['unavoidable_differences'],
                               'alpha_renaming': 'The proposed p is serialized with the original binder name x.',
                               'minimality': 'Preserves all compatible records; no global edit-minimality claim.'},
            'evidence_scope': 'Exact binder-only construction calculation plus frozen admissible evidence; not a general verified Lean kernel or new normative authority.'}


def normalize(observer_id, code, stdout, stderr, timed_out=False):
    """Exact diagnostics or exact-profile successful validation, never votes."""
    text = (stdout + b'\n' + stderr).decode(errors='replace')
    low = text.lower()
    if timed_out:
        return {'outcome': 'TIMEOUT', 'pipeline_stage': 'UNKNOWN', 'basis': 'process deadline'}
    if code is None:
        return {'outcome': 'UNKNOWN', 'pipeline_stage': 'UNKNOWN', 'basis': 'no completed process'}
    if code < 0:
        return {'outcome': 'CRASH', 'pipeline_stage': 'UNKNOWN', 'basis': 'process signal'}
    if code == 2:
        return {'outcome': 'DECLINE', 'pipeline_stage': 'POLICY', 'basis': 'observer decline exit'}
    if any(x in low for x in ('json parse', 'parse error', 'invalid json', 'unexpected token')):
        return {'outcome': 'PARSE_ERROR', 'pipeline_stage': 'PARSE', 'basis': 'explicit parse diagnostic'}
    marker = ('must be `Prop` (sort 0)' if 'nanoda' in observer_id else
              'theorem type is not a Prop' if 'kiota' in observer_id else 'is not a proposition')
    if code != 0 and marker in text and 'm6TransferNonPropTheorem' in text:
        return {'outcome': 'REJECT', 'pipeline_stage': 'VALIDATION', 'basis': 'exact named theorem-Prop diagnostic', 'target_attributed': True}
    if code == 0:
        success = ('Accepted 1 declarations.' in text if 'official' in observer_id else
                   'checked 1 declarations' in text if 'lean4lean' in observer_id else
                   (not stdout.strip() and not stderr.strip()))
        if success:
            return {'outcome': 'ACCEPT', 'pipeline_stage': 'VALIDATION',
                    'basis': 'one-declaration replay count' if ('official' in observer_id or 'lean4lean' in observer_id) else
                    'exact frozen parser and CLI successful check path on the structurally verified one-theorem stream; default silent success',
                    'target_attributed': False}
    if code == 101:
        return {'outcome': 'CRASH', 'pipeline_stage': 'UNKNOWN', 'basis': 'unattributed Rust panic'}
    return {'outcome': 'UNKNOWN', 'pipeline_stage': 'UNKNOWN', 'basis': 'no exact attributed diagnostic; generic failure is not target rejection'}


def immutable(path, content):
    path = ROOT / path
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('xb') as handle:
        handle.write(content)
        handle.flush()
        os.fsync(handle.fileno())


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def engineering_paths():
    return [PROTOCOL, 'schemas/declaration-validation-publication-study-gate-9.schema.json',
            'scripts/validate-declaration-validation-publication-study-gate-9',
            'scripts/publication_study_gate10.py', 'scripts/publication_study_execution.py',
            'scripts/run-declaration-validation-publication-study-gate-10',
            'scripts/validate-declaration-validation-publication-study-gate-10', SCHEMA,
            'schemas/investigation-action-recommendations.schema.json']


def make_run_manifest(plan, freeze):
    dependencies = [binding(p) for p in engineering_paths()]
    for p in [FREEZE, BASELINE, 'external/lean-kernel-arena/_build/checkers/nanoda/src/config.json']:
        dependencies.append(binding(p))
    # Full Gate-9 preflight authenticates pipeline/source identities; repeat
    # binary and runtime-configuration hashes immediately before each launch.
    dependencies.extend(p['binary'] for p in freeze['observer_profiles'])
    config_path = 'external/lean-kernel-arena/_build/checkers/nanoda/src/config.json'
    cfg = read(config_path)
    expected_cfg = freeze['observer_profiles'][1]['configuration']
    if set(cfg) != {'use_stdin', 'nat_extension', 'string_extension', 'unpermitted_axiom_hard_error', 'unsafe_permit_all_axioms', 'num_threads'} or any(cfg[k] != expected_cfg[k] for k in cfg):
        raise ValueError('Nanoda runtime configuration differs from frozen profile')
    return {'schema_version': 1, 'run_id': plan['run_id'], 'recorded_at': utc_now(),
            'protocol_commit': PROTOCOL_COMMIT,
            'protocol_bindings': [git_binding(p) for p in engineering_paths()[:3]],
            'dependencies': dependencies, 'observer_ids': plan['execution_protocol']['observer_ids'],
            'observer_profiles': freeze['observer_profiles'], 'budget': plan['budget'],
            'preflight': 'Gate-9 full-chain and full-payload validation passed before reservation',
            'candidate_generation_started': False}


def attributed_rows(completed, ledger_path):
    rows = []
    for record in completed:
        cap = record['capture']
        raw = [ROOT / ledger_path / 'raw' / cap[k] for k in ('stdout_sha256', 'stderr_sha256')]
        for path, key in zip(raw, ('stdout_sha256', 'stderr_sha256')):
            if sha(path.read_bytes()) != cap[key]:
                raise ValueError('raw process evidence digest mismatch')
        attr = normalize(record['observer_id'], cap['returncode'], raw[0].read_bytes(), raw[1].read_bytes(), cap['timed_out'])
        if attr['outcome'] != record['normalized_outcome']:
            raise ValueError('normalized result does not derive from raw bytes')
        rows.append({'sequence': record['sequence'], 'observer_id': record['observer_id'],
                     'artifact_id': record['artifact_id'], 'artifact_sha256': record['artifact_sha256'],
                     **attr})
    return rows


def derive_result(experiment, completion):
    plan, freeze, baseline = protocol_inputs()
    rows = attributed_rows(experiment['completed'], RUN + '/ledger')
    candidate = read(RUN + '/candidate-manifest.json') if (ROOT / RUN / 'candidate-manifest.json').exists() else None
    analysis = None
    if candidate:
        analysis = analyze_pair((ROOT / candidate['negative']['path']).read_bytes(),
                                (ROOT / candidate['control']['path']).read_bytes(), plan, freeze)
        if encode(analysis) != (ROOT / candidate['analysis']['path']).read_bytes():
            raise ValueError('candidate analysis differs from exact expression calculation')
    elapsed = completion['active_seconds']
    expected_order = [(o, a) for o in plan['execution_protocol']['observer_ids'] for a in ('control', 'negative')]
    matrix = [(r['observer_id'], r['artifact_id']) for r in rows]
    if matrix != expected_order[:len(matrix)]:
        raise ValueError('observer matrix is not frozen execution order')
    complete = len(rows) == 8 and experiment['terminal_state'] == 'COMPLETE'
    success = bool(analysis and complete and elapsed <= 600 and all(
        r['outcome'] == ('ACCEPT' if r['artifact_id'] == 'control' else 'REJECT') and
        r['pipeline_stage'] == 'VALIDATION' and
        (r['artifact_id'] == 'control' or r.get('target_attributed')) for r in rows))
    state = 'ISOLATED_SUCCESS' if success else (
        'BOUNDED_FAILURE_ATTEMPT_OR_TIME_BUDGET_EXHAUSTED' if elapsed > 600 or experiment['terminal_state'] == 'BOUNDED_FAILURE_ATTEMPT_OR_TIME_BUDGET_EXHAUSTED' else
        'ISOLATION_UNRESOLVED' if complete else 'EXECUTION_UNRESOLVED')
    disagreements = 0
    for artifact in ('control', 'negative'):
        outcomes = {r['outcome'] for r in rows if r['artifact_id'] == artifact and r['outcome'] in ('ACCEPT', 'REJECT')}
        disagreements += len(outcomes) > 1
    baseline_elements = baseline['baseline_results'][0]['evidence_elements']
    elements = [{'element': e['element'], 'status': 'SATISFIED' if success else 'UNRESOLVED',
                 'evidence': RUN + ('/candidate-analysis.json' if e['element'] != 'CHECKER_REJECTION_ATTRIBUTION' else '/experiment.json')}
                for e in baseline_elements]
    return {'schema_version': 1, 'run_id': plan['run_id'], 'entry_id': ENTRY,
            'status': state, 'claim_tier': 'BOUNDED_PILOT',
            'inputs': [binding(RUN + '/run-manifest.json'), binding(RUN + '/experiment.json'),
                       binding(RUN + '/ledger/session-completion.json')] +
                      ([binding(RUN + '/candidate-manifest.json'), binding(RUN + '/candidate-analysis.json')] if candidate else []),
            'isolation_elements': elements, 'observer_results': rows,
            'budget': {'candidate_pairs_charged': 1, 'checker_launches_charged': completion['checker_reservations'],
                       'checker_results_persisted': len(rows), 'active_seconds': elapsed,
                       'downtime_seconds': completion.get('downtime_seconds', 0.0),
                       'new_negatives': 0, 'new_controls': int(candidate is not None),
                       'minimization_checks': 0, 'new_mutants': 0, 'new_coverage_runs': 0},
            'counts': {'qualification_candidates': 15, 'authority_established': 1,
                       'authority_provisional': 14, 'authority_unresolved': 0,
                       'primary_denominator': 1, 'existing_isolated_covered': 0,
                       'existing_observed_not_isolated': 1, 'existing_uncovered_or_unresolved': 0,
                       'synthesis_targets': 1, 'synthesis_isolated_successes': int(success),
                       'synthesis_bounded_failures': int(state == 'BOUNDED_FAILURE_ATTEMPT_OR_TIME_BUDGET_EXHAUSTED'),
                       'synthesis_unresolved': int(not success and state != 'BOUNDED_FAILURE_ATTEMPT_OR_TIME_BUDGET_EXHAUSTED'),
                       'final_isolated_covered': int(success),
                       'coarse_positive_but_not_isolated_at_baseline': 1,
                       'checker_disagreement_cases': disagreements,
                       'external_actions_recommended': int(success)},
            'incremental_value': 'COMPLETED_MISSING_MATCHED_CONTROL_FOR_KNOWN_NEGATIVE' if success else 'NO_VALIDATED_INCREMENTAL_ISOLATED_COVERAGE',
            'scientific_review': {
                'separate_ultra_review': 'RECOMMENDED_BEFORE_GATE_11_PUBLICATION_DECISION',
                'question': 'Does completing a matched control for a retrospectively known negative warrant the preregistered strong-positive label, or only a control-completeness/specification pilot result?',
                'reason': 'The 0/1 to 1/1 change supplies no newly discovered negative, defect, held-out transfer or evidence of general synthesis superiority. Gate 10 does not select the publication outcome.'},
            'scope_closure': {'gate_10_closed': True, 'next_gate': 11,
                              'gate_11_publication_decision': 'NOT_STARTED', 'gate_12_historical_freeze': 'NOT_STARTED',
                              'external_action_authorized': False, 'authority_changed': False,
                              'denominator_changed': False, 'baseline_changed': False},
            'nonclaims': ['No new negative or implementation defect discovered.',
                          'No checker consensus used as normative authority.',
                          'No broad methodology, Lean-wide adequacy or soundness claim.',
                          'Four profiles include shared official/Lean4Lean lineage and do not form four independent semantic authorities.',
                          'Exact frozen payloads are required for execution preflight; recorded-result verification can use tracked evidence.',
                          'Gate 11 interpretation and Gate 12 final historical freeze remain separate.']}


def action_document(result):
    success = result['status'] == 'ISOLATED_SUCCESS'
    action = {'id': 'ACTION.PUBLICATION_STUDY.THEOREM_CONTROL',
              'action': 'PROPOSE_CORPUS_TEST' if success else 'CONTINUE_INVESTIGATION',
              'target': 'leanprover/lean-kernel-arena: tutorial/012_nonPropThm matched accept-control companion' if success else 'LeanAssuranceLab: separately governed successor execution review',
              'priority': 'LOW',
              'rationale': 'Offer the exact identity-theorem control as a companion to the existing reject case, with the explicit control relation and expected-outcome evidence. No implementation issue is supported.' if success else 'Preserve the single failed/unresolved attempt; investigate its exact diagnostics before authorizing any successor.',
              'prerequisites': ['Review the paired construction and frozen evidence.',
                                'Check current Arena corpus and open issues/PRs for an equivalent linked control; duplicate search has not run.',
                                'Validate proposed corpus integration against current upstream under separate authorization; no extra run belongs to this protocol.',
                                'Obtain target-specific human authorization before submission.'] if success else ['Separate protocol and run identity required for any new candidate or checker launch.'],
              'external_action': success, 'human_gate': {'required': success, 'status': 'REVIEW_REQUIRED' if success else 'NOT_REQUIRED'},
              'execution_status': 'DEFERRED'}
    return {'schema_version': 1, 'generated_at': read(RUN + '/experiment.json')['recorded_at'],
            'policy': 'docs/INVESTIGATION_SOP.md',
            'findings': [{'id': 'FINDING.PUBLICATION_STUDY.THEOREM_CONTROL',
                          'summary': result['incremental_value'] + '. Security assessment: no new acceptance defect or exploit identified; no private disclosure recommended from these observations. Current-upstream reproduction and duplicate search remain unmet prerequisites, not completed checks.',
                          'disposition': 'DEFERRED', 'evidence': [{k: b[k] for k in ('path', 'sha256')} for b in [binding(RESULT)]],
                          'recommendations': [action]}]}


def render_report(result, actions):
    count, budget = result['counts'], result['budget']
    lines = ['# Gate 10 — bounded theorem-control result', '',
             'Generated by `scripts/run-declaration-validation-publication-study-gate-10 --render`. Presentation only; canonical facts are in `' + RESULT + '`.', '',
             f"Status: **{result['status']}**. Claim tier: **BOUNDED_PILOT**.", '',
             f"Frozen baseline: **0/1 (0.0%)** isolated. Final: **{count['final_isolated_covered']}/1 ({100 * count['final_isolated_covered']:.1f}%)** isolated.", '',
             'The negative is the exact known M6 non-Prop theorem. The sole new artifact is its same-family Prop-valued theorem control, `forall (x : Prop), x -> x`, with proof `fun (x : Prop) (h : x) => h`. Both type and proof change; six original prefix records, metadata, theorem name, empty level parameters and default binder convention are retained. No global edit-minimality is claimed.', '',
             'The exact binder-only calculation checks scope, type sorthood, proof typing and all 18 competing obligations for both members. This calculation is construction evidence, not a verified Lean kernel or a new authority source. Only the frozen theorem-Prop manual claim supplies normative rejection authority.', '',
             '| Observer | Artifact | Outcome | Attribution |', '|---|---|---|---|']
    for r in result['observer_results']:
        lines.append(f"| {r['observer_id']} | {r['artifact_id']} | {r['outcome']} | {r['pipeline_stage']}: {r['basis']} |")
    lines += ['', f"Budget: {budget['candidate_pairs_charged']}/1 pair charged; {budget['checker_launches_charged']}/8 checker reservations; {budget['active_seconds']:.3f}/600 active seconds. Each launch had a timeout of at most 30 seconds. No minimization, repair, new mutant or coverage collection occurred.", '',
              'The baseline contextual indicators remain SOURCE_REACHED, MUTANT_KILLED and EXISTING_CASE_LINKED. The baseline itself is unchanged. The control completes missing evidence for a known negative; the change does not show a new defect or general bug-finding superiority. Official and Lean4Lean have shared lineage.', '',
              '## Recommendation', '', actions['findings'][0]['recommendations'][0]['rationale'], '',
              'The recommendation is deferred pending the listed review, current-upstream and duplicate checks, and target-specific human authorization. No external contact or submission occurred. No new acceptance defect was identified, so no implementation issue or private disclosure is recommended.', '',
              '## Separate scientific review', '', result['scientific_review']['question'], '',
              result['scientific_review']['reason'] + ' A separate Ultra review is recommended before Gate 11; no Ultra agent or publication decision was started here.', '',
              '## Reproduction and boundary', '',
              '`scripts/validate-declaration-validation-publication-study-gate-10` validates tracked records and immutable predecessor bindings without launching checkers. Add `--require-full-payload` for the full predecessor chain and local payload verification. The run command refuses to overwrite an existing run. An interrupted reservation remains consumed; an unbounded active interval closes unresolved rather than permitting a retry.', '',
              'Gate 10 closes only result and recommendation. Gate 11 publish-or-kill interpretation and Gate 12 two-phase historical freeze remain pending. Frozen Gate-9 and all predecessor artifacts remain unchanged.', '']
    return '\n'.join(lines).encode()


def verify_file(item, *, allow_missing_external=False):
    path = item['path']
    if Path(path).is_absolute() or '..' in Path(path).parts:
        raise ValueError('unsafe bound path')
    if allow_missing_external and path.startswith('external/') and not (ROOT / path).exists():
        return
    data = (ROOT / path).read_bytes()
    if sha(data) != item['sha256'] or ('bytes' in item and len(data) != item['bytes']):
        raise ValueError('bound bytes differ: ' + path)


def validate_result(document=None, *, full_payload=False, check_report=True):
    """Independent rederivation from immutable reservations and raw captures."""
    import jsonschema
    import publication_study_execution as execution
    errors = []
    try:
        plan, freeze, baseline = protocol_inputs(full_chain=full_payload)
        manifest = read(RUN + '/run-manifest.json')
        if manifest['protocol_commit'] != PROTOCOL_COMMIT or manifest['run_id'] != plan['run_id']:
            raise ValueError('inexact protocol commit/run binding')
        if manifest['protocol_bindings'] != [git_binding(p) for p in engineering_paths()[:3]]:
            raise ValueError('protocol/schema/validator bindings differ')
        if manifest['observer_profiles'] != freeze['observer_profiles'] or manifest['observer_ids'] != plan['execution_protocol']['observer_ids'] or manifest['budget'] != plan['budget']:
            raise ValueError('frozen profiles/order/budgets differ')
        deps = {d['path']: d for d in manifest['dependencies']}
        required = set(engineering_paths() + [FREEZE, BASELINE, 'external/lean-kernel-arena/_build/checkers/nanoda/src/config.json'] + [o['binary']['path'] for o in freeze['observer_profiles']])
        if set(deps) != required or len(deps) != len(manifest['dependencies']):
            raise ValueError('run manifest dependency closure differs')
        for o in freeze['observer_profiles']:
            if deps[o['binary']['path']] != o['binary']:
                raise ValueError('observer binary binding differs')
        for d in deps.values():
            verify_file(d, allow_missing_external=not full_payload)
        run_hash = execution.digest(manifest)
        persisted_manifest = read(RUN + '/ledger/run-manifest.json')
        if persisted_manifest['run_manifest'] != manifest or persisted_manifest['run_manifest_sha256'] != run_hash:
            raise ValueError('pre-materialization ledger manifest differs')
        experiment = read(RUN + '/experiment.json')
        completion = read(RUN + '/ledger/session-completion.json')
        if completion['run_manifest_sha256'] != run_hash:
            raise ValueError('completion belongs to another run')
        if completion['result_binding'] != binding(RUN + '/experiment.json'):
            raise ValueError('completion does not bind exact persisted experiment')
        if completion['terminal_state'] != experiment['terminal_state'] or completion['downtime_seconds'] != 0:
            raise ValueError('completion state or single-session downtime differs')
        if not 0 <= completion['active_seconds'] < float('inf'):
            raise ValueError('invalid cumulative active elapsed time')
        candidates = list((ROOT / RUN / 'ledger/candidates').glob('*.reservation.json'))
        reservations = sorted((ROOT / RUN / 'ledger/reservations').glob('*.json'))
        result_files = sorted((ROOT / RUN / 'ledger/results').glob('*.json'))
        if len(candidates) != 1 or len(reservations) > 8 or completion['checker_reservations'] != len(reservations):
            raise ValueError('candidate/checker budget accounting does not close')
        if completion['candidate_reservations'] != 1:
            raise ValueError('candidate count differs')
        actual_results = [json.loads(p.read_bytes()) for p in result_files]
        actual_results.sort(key=lambda r: r['sequence'])
        if actual_results != experiment['completed']:
            raise ValueError('experiment does not preserve every persisted checker result')
        candidate = read(RUN + '/candidate-manifest.json') if (ROOT / RUN / 'candidate-manifest.json').exists() else None
        if candidate:
            for d in candidate['dependencies']:
                verify_file(d)
            if set(d['path'] for d in candidate['dependencies']) != {RUN + '/candidate-analysis.json', RUN + '/negative.ndjson', RUN + '/control.ndjson', RUN + '/run-manifest.json'}:
                raise ValueError('candidate manifest dependency closure differs')
            for key in ('negative', 'control', 'analysis'):
                if candidate[key] != binding(RUN + ('/candidate-analysis.json' if key == 'analysis' else '/' + key + '.ndjson')):
                    raise ValueError('candidate content binding differs')
            candidate_hash = execution.digest(candidate)
            frozen = read(RUN + '/ledger/candidates/pair-1.freeze.json')
            if frozen['candidate_manifest'] != candidate or frozen['candidate_manifest_sha256'] != candidate_hash or frozen['run_manifest_sha256'] != run_hash:
                raise ValueError('pre-feedback candidate freeze differs')
            if candidate['run_manifest_sha256'] != run_hash:
                raise ValueError('candidate belongs to a different run')
        elif actual_results:
            raise ValueError('checker feedback without candidate freeze')
        expected_order = [(o, a) for o in manifest['observer_ids'] for a in ('control', 'negative')]
        result_map = {r['sequence']: r for r in actual_results}
        last_finished = 0
        for i, path in enumerate(reservations, 1):
            res = json.loads(path.read_bytes())
            observer, artifact = expected_order[i - 1]
            if res['sequence'] != i or (res['observer_id'], res['artifact_id']) != (observer, artifact):
                raise ValueError('reservation order differs')
            if res['run_manifest_sha256'] != run_hash or res['candidate_manifest_sha256'] != candidate_hash or res['artifact_sha256'] != candidate[artifact]['sha256']:
                raise ValueError('reservation identity differs')
            profile = freeze['observer_profiles'][(i - 1) // 2]
            if res['observer_configuration_sha256'] != profile['configuration_sha256']:
                raise ValueError('reservation configuration differs')
            obs = observers_for(manifest, execution)[(i - 1) // 2]
            expected_command = [str(Path(x).relative_to(ROOT)) if Path(x).is_absolute() and Path(x).is_relative_to(ROOT) else x for x in obs.command]
            if res['command'] != expected_command or res['stdin'] != obs.stdin:
                raise ValueError('observer command/transport differs from frozen profile')
            if datetime.fromisoformat(res['started_at_utc'].replace('Z', '+00:00')) < datetime.fromisoformat(candidate['recorded_at']):
                raise ValueError('checker launch predates immutable candidate manifest')
            if not 0 < res['timeout_seconds'] <= 30:
                raise ValueError('launch timeout exceeds frozen ceiling')
            if res['active_seconds_before_launch'] < last_finished or res['active_seconds_before_launch'] >= 600:
                raise ValueError('launch active-time ordering/budget differs')
            prior = result_map.get(i)
            if prior:
                if any(prior.get(k) != v for k, v in res.items() if k != 'kind'):
                    raise ValueError('result and reservation differ')
                cap = prior['capture']
                if cap['elapsed_seconds'] < 0 or cap['wall_observed_seconds'] < 0:
                    raise ValueError('negative process elapsed time')
                last_finished = res['active_seconds_before_launch'] + cap['wall_observed_seconds']
        if completion['active_seconds'] < last_finished:
            raise ValueError('session time omits checker interval')
        derived = derive_result(experiment, completion)
        document = read(RESULT) if document is None else document
        schema = jsonschema.Draft202012Validator(read(SCHEMA), format_checker=jsonschema.FormatChecker())
        errors.extend(e.message for e in schema.iter_errors(document))
        if document != derived:
            errors.append('Gate-10 result differs from raw-evidence/budget rederivation')
        actions = read(ACTIONS)
        if actions != action_document(document):
            errors.append('action recommendations differ from result derivation')
        action_schema = jsonschema.Draft202012Validator(read('schemas/investigation-action-recommendations.schema.json'), format_checker=jsonschema.FormatChecker())
        errors.extend(e.message for e in action_schema.iter_errors(actions))
        if check_report and (ROOT / REPORT).read_bytes() != render_report(document, actions):
            errors.append('generated Gate-10 report is out of sync')
    except (OSError, ValueError, KeyError, TypeError, execution.LedgerError, subprocess.CalledProcessError) as exc:
        errors.append(str(exc))
    return errors


def render_outputs():
    result = derive_result(read(RUN + '/experiment.json'), read(RUN + '/ledger/session-completion.json'))
    (ROOT / RESULT).write_bytes(encode(result))
    actions = action_document(result)
    (ROOT / ACTIONS).write_bytes(encode(actions))
    (ROOT / REPORT).write_bytes(render_report(result, actions))
    return result


def observers_for(manifest, execution):
    observers = []
    for profile in manifest['observer_profiles']:
        command = [str(ROOT / profile['binary']['path'])]
        stdin = profile['observer'] == 'NANODA'
        if stdin:
            command += [str(ROOT / 'external/lean-kernel-arena/_build/checkers/nanoda/src/config.json')]
        elif profile['observer'] == 'LEAN4LEAN':
            command += ['--import', '{artifact}']
        else:
            command += ['{artifact}']
        observers.append(execution.Observer(profile['observer_id'], profile['configuration_sha256'], tuple(command), stdin))
    return observers


def run_once():
    import publication_study_execution as execution
    if (ROOT / RUN).exists():
        raise ValueError('run directory already exists: preserve it; use validation/render only. An interrupted run is consumed, never retry construction.')
    plan, freeze, _ = protocol_inputs(full_chain=True)
    manifest = make_run_manifest(plan, freeze)
    immutable(RUN + '/run-manifest.json', encode(manifest))
    ledger = execution.ExecutionLedger(ROOT / RUN / 'ledger')
    session = ledger.begin(manifest, ROOT)
    run_hash = session.run_manifest_sha256
    ledger.reserve_candidate(session, 'pair-1')
    experiment = {'recorded_at': utc_now(), 'terminal_state': 'EXECUTION_UNRESOLVED', 'completed': []}
    try:
        negative = frozen_negative(freeze)
        immutable(RUN + '/negative.ndjson', negative)
        control = construct_control(negative)
        immutable(RUN + '/control.ndjson', control)
        analysis = analyze_pair(negative, control, plan, freeze)
        immutable(RUN + '/candidate-analysis.json', encode(analysis))
        candidate = {'schema_version': 1, 'candidate_id': 'pair-1', 'recorded_at': utc_now(),
                     'run_manifest_sha256': run_hash,
                     'negative': binding(RUN + '/negative.ndjson'), 'control': binding(RUN + '/control.ndjson'),
                     'analysis': binding(RUN + '/candidate-analysis.json'),
                     'dependencies': [binding(RUN + '/' + p) for p in ('negative.ndjson', 'control.ndjson', 'candidate-analysis.json', 'run-manifest.json')],
                     'expected_outcomes': analysis['expected_outcomes']}
        immutable(RUN + '/candidate-manifest.json', encode(candidate))
        ledger.freeze_candidate(session, candidate, ROOT)
        def attribute(observer, artifact, capture):
            return normalize(observer.observer_id, capture.returncode, capture.stdout, capture.stderr, capture.timed_out)['outcome']
        experiment.update(execution.execute_protocol(session, manifest, candidate, observers_for(manifest, execution), root=ROOT, attribute=attribute))
    except (Exception, KeyboardInterrupt) as exc:
        experiment['diagnostic'] = type(exc).__name__ + ': ' + str(exc)
        result_dir = ROOT / RUN / 'ledger/results'
        experiment['completed'] = sorted((json.loads(p.read_bytes()) for p in result_dir.glob('*.json')), key=lambda x: x['sequence'])
    immutable(RUN + '/experiment.json', encode(experiment))
    ledger.finish(session, terminal_state=experiment['terminal_state'], result_binding=binding(RUN + '/experiment.json'))
    return render_outputs()
