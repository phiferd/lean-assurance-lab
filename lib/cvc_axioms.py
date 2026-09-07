"""Offline closure validation for the source-only CVC-AXIOMS-1 review.

The normal mode intentionally validates only committed evidence.  ``--require-
full-source`` is an optional stronger check for a workstation retaining the six
inspected sources; it never runs Lean or another external program.
"""
from datetime import datetime
import hashlib
import json
import math
from pathlib import Path
import re


BASE = 'results/research/conditional-validation-contracts/cvc-axioms-1'
ASSESSMENT = BASE + '/assessment.json'
EXCERPTS = BASE + '/source-excerpts.json'
WORK = BASE + '/work-record.json'
MANIFEST = BASE + '/evidence-manifest.json'
OLD_STDOUT = 'results/research/conditional-validation-contracts/cvc-3/run-0001/attempts/02/stdout'
OLD_DIAGNOSTIC = 'results/research/conditional-validation-contracts/cvc-3/stop-diagnostic.json'
OLD_ASSUMPTIONS = 'results/research/conditional-validation-contracts/cvc-2/assumptions.json'
OLD_PROTOCOL = 'results/research/conditional-validation-contracts/cvc-2/execution-protocol.json'
PREDECESSOR = 'config/cvc-u1-dependencies-0002.json'
COMPARATORS = ('Lean.Level.isEquiv\'_wf', 'Lean.Level.isEquiv\'_complete')
EXPECTED = (
    'propext', 'Classical.choice', 'Quot.sound',
    'Lean.Level.instLawfulBEqLevel', 'Lean.Level.isExplicitSubsumedAux_eq',
    'Lean.Level.normalize_eq', 'Std.TreeMap.all_eq_all_toList',
)
UNOBSERVED = 'Std.TreeMap.any_eq_any_toList'
STATEMENT_SOURCES = {
    'propext': 'Core', 'Classical.choice': 'Prelude', 'Quot.sound': 'Core',
    'Lean.Level.instLawfulBEqLevel': 'Axioms',
    'Lean.Level.isExplicitSubsumedAux_eq': 'Axioms',
    'Lean.Level.normalize_eq': 'Axioms', 'Std.TreeMap.all_eq_all_toList': 'Axioms',
}
_REPORT = re.compile(r"^'([^\n]+)' depends on axioms:\s*(\[[^\]]*\])\s*$", re.M)
_NAME = re.compile(r"[A-Za-z_][A-Za-z_0-9']*(?:\.[A-Za-z_][A-Za-z_0-9']*)*")
FROZEN = {
    OLD_STDOUT: ('2485ea0ebb306eec5583f470d8d9ca8c50ea398a5b483f4609e6a55cacfd633e', 2557),
    OLD_DIAGNOSTIC: ('85d22c712ce460faced94d8b197ffffea31f58a14940c81e4df07a79f5fcb59f', 4384),
    OLD_ASSUMPTIONS: ('faaa491087375e7bb2fb55060a74d14efecdd4edf80edb9591351fed3a28133f', 2931),
    OLD_PROTOCOL: ('5410789482c8474a367064b1d8ef047c76f2e9a74e3b3bce84d124a3dce5d6f0', 8994),
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def _json(root, relative):
    return json.loads((root / relative).read_text())


def _sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _binding(root, row):
    root = Path(root).resolve()
    require(set(row) == {'path', 'sha256', 'bytes'}, 'invalid manifest binding')
    require(isinstance(row['path'], str) and not Path(row['path']).is_absolute(), 'manifest path is not relative')
    path = (root / row['path']).resolve()
    require(path.is_relative_to(root), 'manifest path escapes root')
    require(path.is_file() and _sha(path) == row['sha256'] and path.stat().st_size == row['bytes'],
            'bound file changed: ' + row['path'])
    return row['path']


def comparator_reports(stdout):
    """Parse exact #print-axioms reports and reject malformed or duplicate lists."""
    reports = {}
    for match in _REPORT.finditer(stdout):
        name, encoded = match.groups()
        require(name not in reports, 'duplicate axiom report: ' + name)
        body = encoded[1:-1].strip()
        values = [] if not body else [value.strip() for value in body.split(',')]
        require(isinstance(values, list) and all(isinstance(x, str) and _NAME.fullmatch(x) for x in values),
                'malformed axiom names: ' + name)
        require(len(values) == len(set(values)), 'duplicate axiom in report: ' + name)
        reports[name] = values
    selected = {name: reports.get(name) for name in COMPARATORS}
    require(all(values is not None for values in selected.values()), 'missing mandatory comparator report')
    return selected


def _policy(assumptions):
    policy = assumptions.get('conditional_axiom_policy')
    require(isinstance(policy, dict), 'missing frozen conditional axiom policy')
    standard = policy.get('standard_allowed')
    helpers = policy.get('source_helpers_allowed')
    require(isinstance(standard, list) and isinstance(helpers, list), 'invalid frozen policy')
    values = standard + helpers
    require(all(isinstance(x, str) for x in values) and len(values) == len(set(values)), 'invalid frozen policy values')
    return standard, helpers, set(values)


def _sessions(work):
    sessions = work.get('sessions')
    require(isinstance(sessions, list) and 1 <= len(sessions) <= 2, 'invalid session count')
    total = 0.0
    for number, row in enumerate(sessions, 1):
        require(row.get('number') == number, 'session numbering reset')
        started, ended = row.get('started_at'), row.get('ended_at')
        start, end = datetime.fromisoformat(started), datetime.fromisoformat(ended)
        elapsed = row.get('elapsed_seconds')
        actual = (end - start).total_seconds()
        require(start.tzinfo and end.tzinfo and type(elapsed) in (int, float) and math.isfinite(elapsed),
                'invalid session timing')
        require(0 <= elapsed <= 3600 and abs(actual - elapsed) < 1e-6, 'invalid session duration')
        total += elapsed
    require(total <= 7200 and work.get('total_active_seconds') == total, 'active-session total disagreement')
    return total


def _sources(excerpts, full_source):
    sources = excerpts.get('sources')
    rows = excerpts.get('excerpts')
    require(isinstance(sources, list) and len(sources) == 6 and isinstance(rows, list) and rows, 'invalid source inventory')
    ids = set()
    paths = set()
    by_id = {}
    for row in sources:
        require(isinstance(row, dict) and isinstance(row.get('id'), str) and isinstance(row.get('path'), str), 'invalid source')
        require(row['id'] not in ids and row['path'] not in paths, 'duplicate source')
        require(type(row.get('bytes')) is int and row['bytes'] >= 0 and isinstance(row.get('sha256'), str), 'invalid source identity')
        prior = row.get('prior_binding')
        require(isinstance(prior, dict), 'missing prior source binding')
        ids.add(row['id']); paths.add(row['path']); by_id[row['id']] = row
    exact = [x for x in sources if x['prior_binding'].get('status') == 'EXACT_PREDECESSOR_HASH_VERIFIED']
    local = [x for x in sources if x['prior_binding'].get('status') == 'PREVIOUSLY_PINNED_RELEASE_LOCAL_SOURCE_HASHED_NOW']
    require(len(exact) == 2 and len(local) == 4 and len(exact) + len(local) == 6, 'invalid source binding status')
    excerpt_ids = set()
    for row in rows:
        require(isinstance(row, dict) and isinstance(row.get('id'), str) and row['id'] not in excerpt_ids, 'duplicate excerpt')
        source = by_id.get(row.get('source_id'))
        require(source is not None and type(row.get('start_line')) is int and type(row.get('end_line')) is int,
                'invalid excerpt source')
        require(1 <= row['start_line'] <= row['end_line'] and isinstance(row.get('text'), str), 'invalid excerpt range')
        require(_sha_bytes(row['text'].encode()) == row.get('sha256'), 'excerpt text hash mismatch: ' + row['id'])
        require(len(row['text'].splitlines()) == row['end_line'] - row['start_line'] + 1,
                'excerpt line count mismatch: ' + row['id'])
        excerpt_ids.add(row['id'])
        if full_source:
            source_path = Path(source['path'])
            require(source_path.is_file() and _sha(source_path) == source['sha256'] and source_path.stat().st_size == source['bytes'],
                    'source hash mismatch: ' + source['id'])
            lines = source_path.read_text().splitlines(keepends=True)
            actual = ''.join(lines[row['start_line'] - 1:row['end_line']])
            require(actual == row['text'], 'source excerpt differs: ' + row['id'])
    return by_id, excerpt_ids


def _sha_bytes(value):
    return hashlib.sha256(value).hexdigest()


def _statement(row, excerpts_by_id):
    declaration = row.get('declaration_text')
    name = row['name']
    require(isinstance(declaration, str) and declaration and 'axiom' in declaration
            and name.rsplit('.', 1)[-1] in declaration, 'invalid declaration text: ' + name)
    ids = row['statement_excerpt_ids']
    require(any(excerpts_by_id[excerpt_id]['source_id'] == STATEMENT_SOURCES[name]
                and declaration in excerpts_by_id[excerpt_id]['text'] for excerpt_id in ids),
            'declaration source/excerpt mismatch: ' + name)


def _check_predecessor(root, sources):
    config = _json(root, PREDECESSOR)
    donor_files = []
    for donor in config.get('materialization', {}).get('donors', []):
        donor_files.extend(donor.get('files', []))
    for source in sources.values():
        prior = source['prior_binding']
        if prior['status'] != 'EXACT_PREDECESSOR_HASH_VERIFIED':
            continue
        require(prior.get('path') == PREDECESSOR and prior.get('file') in source['path'], 'bad exact predecessor reference')
        matches = [row for row in donor_files if row.get('path') == prior['file']]
        require(len(matches) == 1 and matches[0].get('sha256') == source['sha256']
                and matches[0].get('bytes') == source['bytes'], 'prior source hash mismatch: ' + source['id'])


def validate(root, require_full_source=False):
    root = Path(root).resolve()
    manifest = _json(root, MANIFEST)
    require(manifest.get('schema_version') == 1 and manifest.get('item_id') == 'CVC-AXIOMS-1'
            and isinstance(manifest.get('files'), list), 'invalid evidence manifest')
    bound = {_binding(root, row) for row in manifest['files']}
    require(len(bound) == len(manifest['files']), 'duplicate evidence manifest path')
    required = {ASSESSMENT, EXCERPTS, WORK, OLD_STDOUT, OLD_DIAGNOSTIC, OLD_ASSUMPTIONS, OLD_PROTOCOL}
    require(required <= bound and MANIFEST not in bound, 'incomplete evidence-manifest closure')
    outputs = {str(path.relative_to(root)) for path in (root / BASE).rglob('*') if path.is_file()}
    require(outputs - {MANIFEST} <= bound, 'evidence-manifest omits closure output')
    for path, (digest, size) in FROZEN.items():
        require(_sha(root / path) == digest and (root / path).stat().st_size == size,
                'frozen predecessor changed: ' + path)

    assessment, excerpts, work, diagnostic, assumptions = (
        _json(root, path) for path in (ASSESSMENT, EXCERPTS, WORK, OLD_DIAGNOSTIC, OLD_ASSUMPTIONS))
    require(assessment.get('schema_version') == 1 and assessment.get('item_id') == 'CVC-AXIOMS-1'
            and assessment.get('outcome') == 'SUCCESS' and assessment.get('scientific_status') == 'SOURCE_ASSUMPTION_REVIEW_ONLY'
            and assessment.get('decision') == 'SUCCESSOR', 'assessment outcome is invalid')
    sources, excerpt_ids = _sources(excerpts, require_full_source)
    excerpts_by_id = {row['id']: row for row in excerpts['excerpts']}
    _check_predecessor(root, sources)
    require(work.get('item_id') == 'CVC-AXIOMS-1' and work.get('status') == 'COMPLETE', 'work record not complete')
    require(work.get('sources') == excerpts.get('sources'), 'work/source inventory differs')
    _sessions(work)
    operations = work.get('research_operations')
    operation_keys = {'proof_builds', 'dependency_builds', 'fixture_launches', 'checker_launches',
                      'network_requests', 'source_approvals', 'external_messages'}
    require(isinstance(operations, dict) and set(operations) == operation_keys
            and all(type(value) is int and value == 0 for value in operations.values()), 'forbidden research operation')
    require(work.get('budget') == {'max_sessions': 2, 'session_minutes': 60, 'max_source_files': 6},
            'work budget differs')

    standard, helpers, allowed = _policy(assumptions)
    reports = comparator_reports((root / OLD_STDOUT).read_text())
    require(all(values == list(EXPECTED) for values in reports.values()), 'comparator reports changed')
    require(all('sorryAx' not in values for values in reports.values()), 'comparator report contains sorryAx')
    require(diagnostic.get('mandatory_comparator_reports') == reports, 'diagnostic comparator reports differ')
    require(diagnostic.get('unlisted_axioms') == ['Lean.Level.instLawfulBEqLevel', 'Lean.Level.isExplicitSubsumedAux_eq'],
            'diagnostic unlisted axioms differ')
    require(set(EXPECTED) - allowed == set(diagnostic['unlisted_axioms']), 'policy derivation differs')

    rows = assessment.get('assumptions')
    require(isinstance(rows, list) and [row.get('name') for row in rows] == list(EXPECTED), 'assumption table names differ')
    for row in rows:
        require(isinstance(row.get('statement_excerpt_ids'), list) and row['statement_excerpt_ids']
                and set(row['statement_excerpt_ids']) <= excerpt_ids, 'assumption excerpt reference missing')
        _statement(row, excerpts_by_id)
        require(row.get('observed_in') == list(COMPARATORS), 'assumption observations differ')
        policy = 'STANDARD_ALLOWED' if row['name'] in standard else 'HELPER_ALLOWED' if row['name'] in helpers else 'UNLISTED'
        require(row.get('previous_policy') == policy and isinstance(row.get('interpretation'), str) and row['interpretation'],
                'assumption policy or interpretation differs')
        paths = row.get('dependency_paths')
        require(isinstance(paths, list) and paths, 'missing dependency path')
        for path in paths:
            require(isinstance(path.get('nodes'), list) and len(path['nodes']) >= 2
                    and all(isinstance(node, str) and node for node in path['nodes']) and path['nodes'][-1] == row['name']
                    and isinstance(path.get('evidence_excerpt_ids'), list)
                    and set(path['evidence_excerpt_ids']) <= excerpt_ids
                    and path.get('status') in {'SOURCE_VISIBLE_PARTIAL_PATH', 'SOURCE_VISIBLE_PATH', 'TRANSITIVE_REPORT_ONLY'},
                    'invalid dependency path')
        require(isinstance(row.get('discharge'), str) and row['discharge'], 'missing discharge')
    require(assessment.get('previous_allowed_not_observed') == [UNOBSERVED], 'previous allowed/not-observed set differs')
    require(isinstance(assessment.get('claim_limits'), list) and assessment['claim_limits'], 'missing claim limits')
    recommendation = assessment.get('recommendation')
    require(isinstance(recommendation, dict) and recommendation and assessment.get('successor_proposal') == 'successor-proposal.json',
            'missing successor recommendation/proposal')
    require((root / BASE / assessment['successor_proposal']).is_file(), 'successor proposal absent')
    return {'assumptions': len(rows), 'sources': len(sources), 'active_seconds': work['total_active_seconds']}
