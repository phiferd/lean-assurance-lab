"""Derive the finite CVC-4 result from fixed bytes and supervisor receipts.

This validator checks provenance and scope, not semantic authority. Historical
proof/audit bytes are validated through their original binding mechanism.
"""
import hashlib
import json
from pathlib import Path

from lib.cvc4_artifacts import BASE, build, receipt
from lib.cvc4_runner2 import LIMITS, MANIFEST, WORK, validate_run, work_total
from lib.cvc_a7_repair_evidence import validate_closure as validate_a7
from lib.cvc_prep import require


def load(path):
    return json.loads(Path(path).read_text())


def check_binding(root, row):
    actual = receipt(root, root / row['path'])
    require(actual['sha256'] == row['sha256'], 'evidence binding changed: ' + row['path'])
    if 'bytes' in row:
        require((root / row['path']).stat().st_size == row['bytes'], 'evidence byte length changed')


def check_mapping(root, mapping):
    require(mapping['item_id'] == 'CVC-4-CONDITIONAL' and mapping['contract_id'] == 'CVC-U1-A7',
            'mapping model changed')
    for row in mapping['bindings'] + mapping['prior_observations']:
        check_binding(root, row)
    locked = {r['id']: r for r in load(root / 'config/declaration-validation-source-lock.json')['source_files']}
    for row in mapping['sources']:
        check_binding(root, row['copy'])
        raw = (root / row['copy']['path']).read_bytes()
        require(hashlib.sha256(raw).hexdigest() == row['source_sha256'], 'source identity differs')
        lines = raw.splitlines(keepends=True)
        for span in row['line_ranges']:
            start, end = span['start_line'], span['end_line']
            require(type(start) is int and type(end) is int and 1 <= start <= end <= len(lines),
                    'source locator outside exact file')
            require(hashlib.sha256(b''.join(lines[start-1:end])).hexdigest() == span['excerpt_sha256'],
                    'source excerpt changed')
        if row['provenance_status'] == 'EXACT_FROZEN_SOURCE_LOCK_MATCH':
            source = locked[row['source_lock_id']]
            require(source['blob_sha256'] == row['source_sha256'] and source['path'] == row['upstream_path'],
                    'source copy no longer matches original lock')
    proof = load(root / 'results/research/conditional-validation-contracts/cvc-a7-repair-1/result.json')
    require(mapping['checked_model']['declarations'] == proof['result_declarations']
            and mapping['checked_model']['transitive_axioms'] == proof['transitive_axioms'],
            'checked result or assumption envelope changed')
    require(len(mapping['observers']) == 2 and {r['observer'] for r in mapping['observers']} == {'NANODA', 'OFFICIAL'},
            'implementation lineage scope changed')
    return len(mapping['sources'])


def nanoda_missing_parameter_records(raw):
    """Inspect the exact parser prerequisite; this neither rewrites bytes nor validates Lean."""
    rows = [json.loads(line) for line in raw.splitlines()]
    present = set()
    missing = []
    for row in rows:
        if 'il' in row and 'param' in row:
            present.add(row['param'])
        for kind in ('def', 'axiom', 'thm', 'opaque'):
            if kind in row:
                missing.extend(x for x in row[kind]['levelParams'] if x not in present)
    return missing


def derive_result(root, require_full_payload=False):
    root = Path(root).resolve()
    cases = build(root)['cases']
    case_ids = {r['id']: r for r in cases}
    mapping = load(root / BASE / 'mapping/mapping.json')
    source_count = check_mapping(root, mapping)
    run = validate_run(root, require_payloads=require_full_payload)
    require(not run['matrix_complete'] and not run['hypotheses_all_matched'] and not run['control_stop']
            and not run['pending'] and run['hypothesis_mismatch'], 'adapter stop state differs')
    require(run['launch_count'] == 10 and run['inherited_launch_count'] == 2
            and run['combined_launch_count'] == 12 and len(cases) == 6, 'retained launch count differs')
    require(all(a['terminal']['hypothesis_matched'] for a in run['attempts'][:9])
            and not run['attempts'][9]['terminal']['hypothesis_matched'], 'raw matched prefix changed')
    last = run['attempts'][9]
    require(last['reservation']['cell']['id'] == 'E-OWNED-CONTROL-nanoda'
            and last['terminal']['returncode'] == 101, 'wrong adapter failure')
    require(nanoda_missing_parameter_records((root / case_ids['E-OWNED-CONTROL']['input']['path']).read_bytes()) == [3]
            and nanoda_missing_parameter_records((root / case_ids['E-UNOWNED']['input']['path']).read_bytes()) == [2],
            'fixed declared-parameter prerequisite differs')
    diagnostic = load(root / BASE / 'adapter-boundary.json')
    for row in diagnostic['evidence_bindings'] + diagnostic['observed_failure']['receipts']:
        check_binding(root, row)
    for source in diagnostic['sources']:
        check_binding(root, source['binding'])
        lines = (root / source['binding']['path']).read_bytes().splitlines(keepends=True)
        for span in source['excerpts']:
            start, end = span['start_line'], span['end_line']
            require(1 <= start <= end <= len(lines), 'adapter source locator outside exact file')
            raw = b''.join(lines[start-1:end])
            require(raw.decode() == span['text'] and hashlib.sha256(raw).hexdigest() == span['sha256'],
                    'adapter source excerpt changed')
    failure = diagnostic['observed_failure']
    require(failure['terminal_event'] == last['terminal'] and failure['cell_id'] == last['reservation']['cell']['id'],
            'adapter diagnosis differs from raw terminal')
    for stream in ('stdout', 'stderr'):
        path = next(r['path'] for r in failure['receipts'] if r['path'].endswith('/' + stream))
        require((root / path).read_bytes().decode() == failure[stream], 'adapter diagnostic text changed')
    require(diagnostic['recommended_outcome'] == 'BOUNDED_UNRESOLVED'
            and diagnostic['authority']['scientific_transition_required'] is True,
            'boundary classification differs')
    require(diagnostic['accounting']['combined_launches'] == run['combined_launch_count']
            and diagnostic['accounting']['combined_process_seconds'] == run['combined_process_seconds'],
            'adapter accounting differs')
    work = load(root / WORK)
    require(work['status'] == 'CLOSED' and work['outcome'] == 'BOUNDED_UNRESOLVED'
            and all(r.get('end') is not None for r in work['intervals']), 'logical work interval not closed')
    total = work_total(work, work['intervals'][-1]['end'], enforce=True)
    require(total == work['active_seconds_closed'] == run['active_seconds'], 'active total differs')
    require(work['research_operations'] == {'validator_launches': 12, 'setup_builds': 0, 'research_network_requests': 0},
            'operation count differs')
    proof = validate_a7(root, require_full_payload=False)
    require(proof['outcome'] == 'SUCCESS', 'checked conditional predecessor no longer validates')
    observations = []
    for index, cell in enumerate(run['manifest']['cells']):
        impl = cell['implementation']
        ident = cell['id'].removesuffix('-' + impl)
        case = case_ids[ident]
        require(case['role'] == cell['role'] and case['pair_id'] == cell['pair_id'], 'case attribution differs')
        row = {'cell_id': cell['id'], 'case_id': ident, 'pair_id': cell['pair_id'],
               'role': cell['role'], 'implementation': impl, 'input': case['input'], 'model_status': case['model_status']}
        if index >= len(run['attempts']):
            row.update(observed_outcome='NOT_RUN', hypothesis_matched=None, returncode=None,
                       process_seconds=0, receipts=[], reason='Ownership control failed before semantic checking; launches paused.')
        else:
            attempt = run['attempts'][index]
            require(attempt['reservation']['cell'] == cell, 'fixed cell order differs')
            terminal = attempt['terminal']
            rc = terminal['returncode']
            outcome = 'PARSER_ERROR' if not terminal['hypothesis_matched'] else 'ACCEPT' if rc == 0 else 'REFUSED_TYPE_COMPARISON'
            row.update(observed_outcome=outcome, hypothesis_matched=terminal['hypothesis_matched'], returncode=rc,
                       process_seconds=terminal['charged_seconds'], receipts=terminal['receipts'])
        observations.append(row)
    return {'schema_version': 1, 'item_id': 'CVC-4-CONDITIONAL', 'run_id': 'CVC4-U1-A7-0002',
            'contract_id': 'CVC-U1-A7', 'outcome': 'BOUNDED_UNRESOLVED',
            'scientific_status': 'PARTIAL_FINITE_COMPARISON_WITH_FROZEN_BYTE_ADAPTER_BOUNDARY',
            'checkpoint': run['checkpoint'], 'protocol': receipt(root, root / MANIFEST),
            'work_record': receipt(root, root / WORK), 'cases': receipt(root, root / BASE / 'cases.json'),
            'mapping': receipt(root, root / BASE / 'mapping/mapping.json'),
            'proof_result': receipt(root, root / 'results/research/conditional-validation-contracts/cvc-a7-repair-1/result.json'),
            'predecessor_run': receipt(root, root / BASE / 'revision-02/predecessor.json'),
            'repair_diagnostic': receipt(root, root / BASE / 'revision-02/repair-diagnostic.json'),
            'adapter_boundary': receipt(root, root / BASE / 'adapter-boundary.json'),
            'limits': LIMITS, 'summary': {'selected_pairs': 3, 'complete_pairs': 2, 'lineages': 2,
              'launches': run['combined_launch_count'], 'matrix_launches': run['launch_count'],
              'retained_prior_launches': run['inherited_launch_count'],
              'unused_launches': LIMITS['validator_launches'] - run['combined_launch_count'],
              'matrix_complete': run['matrix_complete'], 'matrix_hypotheses_matched': sum(r['hypothesis_matched'] is True for r in observations),
              'active_seconds': total, 'process_seconds': run['combined_process_seconds'],
              'matrix_process_seconds': run['local_process_seconds'], 'prior_process_seconds': run['inherited_process_seconds'],
              'source_files': source_count,
              'control_acceptances': sum(r['role'] == 'control' and r['observed_outcome'] == 'ACCEPT' for r in observations),
              'candidate_acceptances': sum(r['role'] == 'candidate' and r['observed_outcome'] == 'ACCEPT' for r in observations),
              'type_refusals': sum(r['observed_outcome'] == 'REFUSED_TYPE_COMPARISON' for r in observations),
              'parser_errors': sum(r['observed_outcome'] == 'PARSER_ERROR' for r in observations),
              'not_run': sum(r['observed_outcome'] == 'NOT_RUN' for r in observations),
              'setup_builds': 0, 'network_requests': 0},
            'observations': observations,
            'finding': 'The pinned official observer refuses E-POS, one of the exact required acceptances of CVC-U1-A7; Nanoda accepts it. Both accept the right-successor and zero controls and refuse the zero-invalid candidate. The ownership comparison is unresolved: the official control accepts, but Nanoda fails in its parser before checking the control; neither ownership candidate was launched.',
            'remaining_gaps': [mapping['boundary_explanation']['remaining_gap'],
                'The ownership streams omit a level record for a declared unused parameter. Nanoda requires this record before typechecking. Repair would change the frozen exact bytes or pinned binary; neither is authorized within this comparison.',
                'No executable-validator, parser/importer or source-to-binary refinement is proved. Finite testing does not discharge A7 or establish consistency.',
                'The new zero/owned controls have direct model arguments; they are not added to the original checked finite AcceptanceTarget.'],
            'recommendation': {'next_item': 'CVC-4-ADAPTER-REVIEW', 'priority': 1,
                'action': 'Review an explicit scientific-byte successor proposal versus stopping, using the existing evidence only. State the exact intended representation change, invariants, value and finite entry conditions before any implementation or launch.',
                'target': 'The unused declared-parameter serialization/import boundary in the same CVC-U1-A7 Sort fragment.',
                'prerequisites': ['Required CVC-4 closure checks pass.',
                    'Preserve all old byte strings, hypotheses, observer identities, failed receipts and charges.',
                    'No new byte generation, observer/proof/setup/research-network launch or changed scientific input during the review.',
                    'Compare reuse of the existing Arena imax contribution and justified stop/no-additional-action before proposing another experiment.',
                    'Any external submission needs exact target-specific owner authorization.'],
                'evidence_refs': [BASE + '/cases.json', BASE + '/mapping/mapping.json', BASE + '/adapter-boundary.json',
                                 BASE + '/run-0001/events.jsonl', BASE + '/run-0002/events.jsonl',
                                 'results/research/conditional-validation-contracts/cvc-a7-repair-1/result.json']},
            'external_action': {'decision': 'NO_EXTERNAL_ACTION_NOW',
                'reason': 'The partial comparison and Lab-authored stream/import mismatch do not show an invalid accepted proof. Prior withdrawn imax defect recommendations remain withdrawn; retain evidence locally for the input-boundary decision.'},
            'phase_decision': 'Retain the conditional phase for one existing-evidence scientific-input boundary review; do not promote the success-only contribution stage or begin a new comparison.',
            'stop': 'No same-byte, same-binary execution repair remains under the frozen protocol. Close at this documented scientific-input boundary; do not consume remaining slots or reset counters.'}


def report(result):
    s = result['summary']
    lines = ['# CVC-4-CONDITIONAL — exact artifact and implementation comparison', '',
             '**BOUNDED_UNRESOLVED** at a characterized frozen-byte/importer boundary.', '',
             '| Input | Model status | Official Lean 4.33.0 | Nanoda 6ae1f0c |',
             '| --- | --- | --- | --- |']
    for ident in dict.fromkeys(r['case_id'] for r in result['observations']):
        rows = [r for r in result['observations'] if r['case_id'] == ident]
        outcomes = {r['implementation']: r['observed_outcome'] for r in rows}
        lines.append(f"| {ident} | {rows[0]['model_status']} | {outcomes['official']} | {outcomes['nanoda']} |")
    lines += ['', result['finding'], '',
              'For every named natural-number assignment, `imax u (v+1) = max u (v+1)`. The checked bridge proves the supplied sort body meets the named model under A7. Refusal by the official observer therefore limits that observer’s acceptance relative to this model; it supplies no invalid accepted proof or universal defect claim.', '',
              'The exact source mapping separates parsing, reconstruction, validation and semantic use. Both parsers retain `imax`; Nanoda’s comparator simplifies right-successor `imax` to `max` and right-zero `imax` to zero. The official path reaches C++ `is_equivalent`, but its internal implementation bytes were unavailable locally. The installed Lean-level normalizer contains the rewrite and cannot substitute for that missing C++/binary connection.', '',
              'A7 remains explicit. The proof uses the official Lean runtime and imported Lean4Lean results; it is not an independent validation of the official observer. Nanoda and official use distinct parser lineages. Their source-to-binary correspondence and arbitrary-byte import/refinement remain unproved.', '',
              'E-POS and E-CONTROL retain their original byte hashes. Four new Lab-authored NDJSON streams instantiate the zero and ownership boundaries plus controls. New metadata describes format compatibility, not exporter-produced proof provenance. No frozen catalog, authority assignment or prior disagreement was changed.', '',
              'The first execution paused after two charged launches: the official control passed, while Nanoda reported typecheck success with an unexpected pretty-printer error. Source inspection found that default `print_axioms=true` requests printing without a destination. An explicit same-item tooling revision sets only that diagnostic flag false and runs fresh counted controls. Original configs, tests, raw logs and the failed output hypothesis remain unchanged; no earlier result is retroactively accepted.', '',
              'The revised execution then paused at its tenth launch. Nanoda panicked at `parser.rs:506` while importing the ownership control: the stream declares unused `v` but has no `Level::Param(v)` record. The parser unconditionally requires such a record for each declared parameter. The unowned candidate has the same missing-record prerequisite by source inspection, but was not executed. This parser error is not an ownership refusal or a model counterexample.', '',
              'Diagnosis found no repair that preserves the selected bytes and observer binaries. Adding a parameter record would retain the structured AST meaning but change the exact scientific artifact submitted for this comparison. A wrapper would likewise change observed bytes; a parser rebuild would change the pinned observer and exceed the zero-build allowance. Changing output classification would weaken the acceptance control. The source prerequisite is now covered by a pure regression. Original failures remain unchanged. A separately reviewed scientific-input transition is needed before any byte variant can be executed.', '',
              f"The item used {s['launches']} of 16 allowed validator launches ({s['retained_prior_launches']} retained first-run launches plus {s['matrix_launches']} revised launches), {s['process_seconds']:.6f} process seconds and {s['active_seconds']:.6f} active seconds including engineering, below the 16200-second cap. Every launch had a 30-second limit. Two pairs completed; nine revised hypotheses matched, one control hit a parser error and two cells were not launched. Four launch slots remain unused. No setup build or research-network request ran. Required administrative closure fixtures are recorded separately.", '',
              'Next: **CVC-4-ADAPTER-REVIEW**, selected READY and unstarted for one existing-evidence input-boundary proposal or stop decision. CVC-5 is not promoted. Existing imax defect recommendations remain withdrawn; the partial result and adapter diagnostic stay local. No new scientific inputs, successor execution or external submission start here.', '',
              'Reproduce the evidence checks with `scripts/validate-cvc4-evidence --require-full-payload`; omit that option to inspect retained evidence without ignored observer binaries. The stopped run cannot be resumed through the launch command. See [result](result.json), [source mapping](mapping/mapping.json), [fixed cases](cases.json), [adapter diagnosis](adapter-boundary.json), [original ledger](run-0001/events.jsonl), [revised ledger](run-0002/events.jsonl) and [closure validation](../../../workflow-refresh/cvc-4-conditional-2026-09-07/validation.json).', '']
    return '\n'.join(lines)


def validate(root, require_full_payload=False, write=False):
    root = Path(root).resolve()
    result = derive_result(root, require_full_payload)
    dest = root / BASE / 'result.json'
    prose = root / BASE / 'report.md'
    if write:
        require(not dest.exists() and not prose.exists(), 'cannot overwrite closed result')
        dest.write_text(json.dumps(result, indent=2) + '\n')
        prose.write_text(report(result))
    else:
        require(load(dest) == result, 'result differs from bound raw evidence')
        require(prose.read_text() == report(result), 'generated report drift')
    return {'status': 'PASS', 'outcome': result['outcome'], **result['summary'],
            'payloads_verified': require_full_payload}
