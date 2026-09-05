"""Deterministic Gate-11 decision and two-phase Gate-12 publication-study closure."""
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

import jsonschema
import publication_study_gate10 as g10
import publication_study_history as history

ROOT = Path(__file__).resolve().parents[1]
GATE10_COMMIT = '193e95cdf7ae42eb022986e4655ed46427fa3240'
PREFIX = 'results/research/declaration-validation-publication-study-'
DECISION = PREFIX + 'closure.json'
MANIFEST = PREFIX + 'content-manifest.json'
HISTORICAL = PREFIX + 'historical.json'
REPORT = 'docs/research/DECLARATION_VALIDATION_PUBLICATION_STUDY_FINAL_REPORT.md'
SCHEMA = 'schemas/declaration-validation-publication-study-closure.schema.json'
ENTRYPOINT = 'scripts/close-declaration-validation-publication-study'
INPUTS = [
    'config/declaration-validation-publication-study-preregistration.json',
    PREFIX + 'source-discovery.json', PREFIX + 'authority-source-approval.json',
    PREFIX + 'authority-adjudication.json', PREFIX + 'denominator.json',
    PREFIX + 'baseline-comparator.json', g10.RESULT, g10.ACTIONS,
]


def load(path):
    return json.loads((ROOT / path).read_bytes())


def write(path, value):
    (ROOT / path).parent.mkdir(parents=True, exist_ok=True)
    (ROOT / path).write_bytes(g10.encode(value))


def input_bindings():
    bindings = [history.git_binding(ROOT, GATE10_COMMIT, path) for path in INPUTS]
    for bound in bindings:
        if g10.sha((ROOT / bound['path']).read_bytes()) != bound['sha256']:
            raise ValueError('frozen Gate-10 input changed: ' + bound['path'])
    return bindings


def classify(facts, priority):
    """Literal preregistered outcome rules; review prose cannot override them."""
    denominator = facts['primary_denominator']
    fatal = not facts['discovery_closed'] or not facts['evidence_closed'] or (
        denominator > 0 and facts['execution_unresolved'] / denominator > .25)
    triggers = {
        'STRONG_POSITIVE': facts['coarse_positive_newly_isolated'] > 0 or (
            facts['synthesis_isolated_successes'] > 0 and
            (facts['newly_exposed_checker_disagreements'] > 0 or facts['schema_valid_corpus_recommendations'] > 0)),
        'MODERATE_POSITIVE': denominator > 0 and facts['existing_isolated_covered'] / denominator >= .8 and facts['baseline_complete'],
        'SPECIFICATION_RESULT': facts['qualification_gap_candidates'] >= 5 or (
            denominator == 0 and facts['qualification_gap_candidates'] > 0),
        'NEGATIVE_METHOD_RESULT': denominator > 0 and facts['coarse_positive_but_not_isolated'] == 0 and
            facts['synthesis_isolated_successes'] == 0 and facts['newly_exposed_checker_disagreements'] == 0 and facts['external_actions_recommended'] == 0,
        'INCONCLUSIVE': True,
    }
    selected = 'INCONCLUSIVE' if fatal else next(outcome for outcome in priority if triggers[outcome])
    return selected, triggers, fatal


def derive_decision():
    bindings = input_bindings()
    prereg, discovery, approval, adjudication, denominator, baseline, result, actions = [load(p) for p in INPUTS]
    counts = result['counts']
    isolated = result['status'] == 'ISOLATED_SUCCESS'
    target_baseline = next(x for x in baseline['baseline_results'] if x['entry_id'] == result['entry_id'])
    target_comparator = next(x for x in baseline['comparator_results'] if x['entry_id'] == result['entry_id'])
    coarse = target_baseline['primary_status'] != 'ISOLATED_COVERED' and (
        target_comparator['source_coverage']['classification'] == 'SOURCE_REACHED' or
        target_comparator['semantic_mutation']['classification'] == 'MUTANT_KILLED')
    recommendations = [r for f in actions['findings'] for r in f['recommendations']]
    facts = {
        'discovery_closed': discovery['execution_summary']['closure_status'] == 'CLOSED',
        'evidence_closed': result['scope_closure']['gate_10_closed'],
        'primary_denominator': denominator['primary_normative_denominator']['count'],
        'baseline_complete': len(baseline['baseline_results']) == counts['primary_denominator'],
        'existing_isolated_covered': counts['existing_isolated_covered'],
        'synthesis_isolated_successes': counts['synthesis_isolated_successes'],
        'coarse_positive_newly_isolated': int(coarse and isolated),
        'coarse_positive_but_not_isolated': counts['coarse_positive_but_not_isolated_at_baseline'],
        'newly_exposed_checker_disagreements': counts['checker_disagreement_cases'],
        'schema_valid_corpus_recommendations': sum(r['action'] == 'PROPOSE_CORPUS_TEST' for r in recommendations),
        'external_actions_recommended': sum(r['external_action'] for r in recommendations),
        'execution_unresolved': int(result['status'] in ('EXECUTION_UNRESOLVED', 'PIPELINE_NOT_REPRESENTABLE_AT_EXECUTION')),
        'qualification_gap_candidates': adjudication['counts']['provisional'] + adjudication['counts']['unresolved'],
    }
    priority = prereg['outcome_criteria']['classification_priority']
    outcome, triggers, fatal = classify(facts, priority)
    tier = denominator['claim_tier']['id'] if isinstance(denominator['claim_tier'], dict) else denominator['claim_tier']
    # This closure is the exact frozen pilot, not a reusable outcome selector for
    # unapproved future slices. A changed tier or population needs a successor.
    if tier != result['claim_tier'] or tier != 'BOUNDED_PILOT':
        raise ValueError('closure scope is the exact frozen BOUNDED_PILOT')
    publication = 'STOP' if fatal or outcome == 'INCONCLUSIVE' else 'PUBLISH_BOUNDED'
    return {
        'schema_version': 1, 'artifact_type': 'PUBLICATION_STUDY_GATE_11_DECISION',
        'status': 'GATE_11_COMPLETE', 'input_commit': GATE10_COMMIT,
        'bindings': bindings, 'facts': facts, 'outcome_triggers': triggers,
        'classification_priority': priority, 'outcome_class': outcome, 'claim_tier': tier,
        'publication_decision': publication, 'publication_format': 'BOUNDED_TECHNICAL_REPORT',
        'publication_execution': 'NOT_AUTHORIZED',
        'frontier_recommendation': 'STOP_THIS_STUDY_AFTER_GATE_12',
        'claim': 'For the sole established obligation, a missing same-family theorem control prevented existing isolated coverage despite positive coarse indicators. One registered construction supplied that control and closed the paired evidence.',
        'interpretation': 'STRONG_POSITIVE is the literal preregistered outcome category. It does not signify a broad method result: the change completes control evidence for a retrospectively known negative, with no new negative, defect or transfer result.',
        'secondary_specification_result': 'Fourteen candidates retain insufficient approved qualification for the exact modeled judgment. This preserves target-correspondence, raw-expression mapping and proof-dependency/axiom-closure limitations; it does not prove global absence of Lean documentation.',
        'scientific_review': {
            'reviewer': 'separate gpt-6-astra Ultra review',
            'role': 'ADVISORY_INTERPRETATION_NOT_NORMATIVE_AUTHORITY',
            'disposition': 'NO_CONSEQUENTIAL_ISOLATION_DEFECT_FOUND',
            'construction': 'Sort 0 : Sort 1 violates theorem proposition-valued type; its forall value has the declared type. The identity proposition is Sort 0 and its lambda has exactly the declared type. Both wrappers remain theorems. Changing type and proof together avoids a value mismatch.',
            'recommendation': 'Retain STRONG_POSITIVE / BOUNDED_PILOT / PUBLISH_BOUNDED, issue a bounded technical report, and stop this frontier after the historical freeze. No Gate-10 erratum is recommended.',
            'evidence_paths': [g10.RESULT, g10.RUN + '/candidate-analysis.json', INPUTS[0], INPUTS[2]],
        },
        'recommendation_binding': history.git_binding(ROOT, GATE10_COMMIT, g10.ACTIONS),
        'limitations': result['nonclaims'][:4] + [
            'One established obligation in one semantic family cannot estimate general coverage or comparative synthesis performance.',
            'The authority qualification process is bounded by the exact discovered sources and separately approved claim mappings.',
            'Current-upstream duplicate and corpus-integration checks remain prerequisites to the deferred control proposal.',
            'Historical recorded-evidence validation does not execute checkers or prove that ignored local payloads are materialized.',
        ],
        'gate_12_requirement': 'Separate Phase-A content commit followed by a Phase-B Git-blob attestation; neither manifest nor attestation attests to itself.',
    }


def render_report(decision):
    result = load(g10.RESULT)
    counts = result['counts']
    lines = [
        '# Declaration-validation publication study: final bounded report', '',
        'Generated by `scripts/close-declaration-validation-publication-study render`. Presentation only; the canonical decision is `' + DECISION + '`.', '',
        f"**{decision['outcome_class']} / {decision['claim_tier']} / {decision['publication_decision']}**. Recommended format: bounded technical report. External publication is not authorized.", '',
        '## 1. Problem and motivation', '', 'Measure exact obligation-sensitive negative coverage and show where coarse testing indicators lack the evidence needed to isolate a rule.', '',
        '## 2. Bounded Lean trust boundary', '', 'The frozen target is checked ordinary declaration addition at Lean 4.33.0. Import/export reconstruction, checker policy and implementation lineage remain explicit context rather than normative authority.', '',
        '## 3. Related work and scope', '', 'This report uses only the already-frozen study inputs and source-discovery corpus. It performs no additional literature search and makes no claim to a comprehensive related-work survey.', '',
        '## 4. Normative authority methodology', '', decision['secondary_specification_result'], '',
        'The fixed cohort has 15 candidates: 1 established, 14 provisional, 0 unresolved. Only the human-approved theorem-Prop manual claim qualifies for the primary denominator; checker agreement and model review do not supply authority.', '',
        '## 5. Obligation-sensitive negative coverage', '', 'Counting requires all seven M10 isolation elements under erratum 1, including a theorem positive control with a matching proof and closure of all 18 competing obligations.', '',
        '## 6. Experimental design', '', 'Gates 0–9 freeze source approval, cohort, denominator, baseline, observers, prior knowledge and the single-pair protocol in order. Gate 10 preserves the known M6 negative and constructs one identity-theorem control. No repair, retry, alternate pair, mutant or coverage run occurs.', '',
        '## 7. Baseline and synthesis tables', '',
        '| Obligation | Baseline isolated | Coarse indicators | Final isolated | New negative | New control |',
        '|---|---|---|---|---|---|',
        '| DECL.THEOREM.TYPE_PROP | 0/1 (0.0%) | SOURCE_REACHED; MUTANT_KILLED; EXISTING_CASE_LINKED | 1/1 (100.0%) | 0 | 1 |', '',
        f"The single pair used {result['budget']['checker_launches_charged']}/8 launches and {result['budget']['active_seconds']:.3f}/600 active seconds. All four frozen observers accepted the control and rejected the negative with theorem-Prop attribution. New checker-disagreement cases: {counts['checker_disagreement_cases']}.", '',
        '## 8. Threats to validity', '', *['- ' + item for item in decision['limitations']], '',
        '## 9. Results and preregistered decision', '', decision['claim'], '', decision['interpretation'], '',
        'The strong-positive trigger precedes the secondary specification trigger in the frozen classification priority. Relabeling the outcome after seeing its size is forbidden. The bounded tier rules out a full-method-paper claim.', '',
        '## 10. Ecosystem consequences', '', 'Retain the low-priority Arena companion-control proposal as DEFERRED pending current-upstream/duplicate checks, integration validation and target-specific authorization. No implementation issue, private disclosure or external submission is supported or performed by this closure.', '',
        '## 11. Reproducibility', '',
        '`scripts/close-declaration-validation-publication-study validate --require-full-payload` checks current closure and local predecessor payloads. `validate-historical` reconstructs the exact Phase-A committed tree and runs its bound validator, without checker execution. The content manifest and separate Git-blob attestation close Gate 12; their own bytes are excluded from self-reference.', '',
        'The immutable Gate-10 run retains every candidate record, raw process output, manifest and reservation. All predecessor milestones remain bound to their historical Git blobs.', '',
        '## 12. Limitations and next frontier', '',
        decision['frontier_recommendation'] + '. Preserve the technical report and deferred action. Any repeat or later semantic slice needs a new explicit plan and run identity. The project-wide review proposes the next work separately; this report activates no experiment.', '',
    ]
    return '\n'.join(lines).encode()


def content_paths():
    paths = set(['CONSTITUTION.md', 'AGENTS.md', 'docs/RESEARCH_STATUS.md', SCHEMA, ENTRYPOINT,
                 'schemas/investigation-action-recommendations.schema.json'])
    for pattern in (
        'config/declaration-validation*', 'schemas/declaration-validation*',
        'scripts/*declaration-validation*', 'scripts/publication_study*.py',
        'tests/test_declaration_validation*.py', 'tests/test_publication_study*.py',
        'results/research/declaration-validation*',
        'results/research/evidence/declaration-validation*',
        'docs/research/DECLARATION_VALIDATION_*', 'lib/*.py', g10.RUN,
    ):
        for path in ROOT.glob(pattern):
            candidates = path.rglob('*') if path.is_dir() else [path]
            paths.update(str(p.relative_to(ROOT)) for p in candidates if p.is_file() and '__pycache__' not in p.parts)
    return sorted(paths - {MANIFEST, HISTORICAL})


def derive_manifest():
    return {'schema_version': 1, 'artifact_type': 'PUBLICATION_STUDY_CONTENT_MANIFEST',
            'files': [g10.binding(path) for path in content_paths()]}


def validate_content(*, full_payload=False, check_manifest=True):
    errors = g10.validate_result(full_payload=full_payload)
    if errors:
        return errors
    # Verify the full M7-through-M10+erratum chain even in payload-free snapshots.
    gate8 = g10.module('closure_predecessors', 'scripts/validate-declaration-validation-publication-study')
    errors += gate8.validate_preregistration()
    if errors:
        return errors
    try:
        decision = load(DECISION)
        errors += [e.message for e in jsonschema.Draft202012Validator(load(SCHEMA)).iter_errors(decision)]
        if decision != derive_decision():
            errors.append('Gate-11 decision differs from preregistered evidence/priority derivation')
        if (ROOT / REPORT).read_bytes() != render_report(decision):
            errors.append('final generated report differs from canonical decision')
        if check_manifest and load(MANIFEST) != derive_manifest():
            errors.append('study content manifest is incomplete, changed, or self-referential')
    except (ValueError, KeyError, OSError, TypeError) as exc:
        errors.append(str(exc))
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['render', 'freeze-content', 'attest', 'validate', 'validate-historical'])
    parser.add_argument('--content-commit')
    parser.add_argument('--content-only', action='store_true', help='validate Phase-A snapshot without its later attestation')
    parser.add_argument('--require-full-payload', action='store_true')
    args = parser.parse_args()
    if args.mode in ('render', 'freeze-content') and (ROOT / HISTORICAL).exists():
        raise SystemExit('study is historically frozen; create an explicit successor instead of regenerating')
    if args.mode == 'render':
        errors = g10.validate_result()
        if errors:
            raise SystemExit('\n'.join(errors))
        decision = derive_decision()
        write(DECISION, decision)
        (ROOT / REPORT).write_bytes(render_report(decision))
    elif args.mode == 'freeze-content':
        errors = validate_content(check_manifest=False)
        if errors:
            raise SystemExit('\n'.join(errors))
        write(MANIFEST, derive_manifest())
    elif args.mode == 'attest':
        if not args.content_commit or (ROOT / HISTORICAL).exists():
            raise SystemExit('exact content commit required; never overwrite an attestation')
        attestation = history.make_attestation(ROOT, args.content_commit, MANIFEST)
        errors = history.validate_historical(ROOT, attestation, MANIFEST, ENTRYPOINT, ['validate', '--content-only'])
        if errors:
            raise SystemExit('\n'.join(errors))
        write(HISTORICAL, attestation)
    else:
        historical = args.mode == 'validate-historical' or (not args.content_only and (ROOT / HISTORICAL).exists())
        errors = (history.validate_historical(ROOT, load(HISTORICAL), MANIFEST, ENTRYPOINT, ['validate', '--content-only'])
                  if historical else validate_content(full_payload=args.require_full_payload))
        if historical and args.require_full_payload:
            errors += g10.validate_result(full_payload=True)
        if errors:
            raise SystemExit('\n'.join(errors))
        print('PASS: publication-study closure; no checker execution')


if __name__ == '__main__':
    main()
