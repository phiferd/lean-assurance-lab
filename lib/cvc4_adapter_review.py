"""Validate the existing-evidence adapter decision without producing input variants."""
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import subprocess
import time

BASE = Path('results/research/conditional-validation-contracts/cvc-4-adapter-review')
PRIOR = Path('results/research/conditional-validation-contracts/cvc-4-conditional')
ZERO = dict.fromkeys(('byte_variants', 'observer_launches', 'proof_builds',
                     'setup_launches', 'research_network_launches'), 0)
BUDGET = {'active_seconds': 5400, 'interval_seconds': 5400, 'pairs': 1,
          'new_byte_streams': 2, 'implementation_lineages': 2,
          'validator_launches': 4, 'launch_seconds': 30, 'proof_builds': 0,
          'setup_builds': 0, 'research_network_requests': 0}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load(path):
    return json.loads(path.read_text())


def check_proposal(proposal, cases, observer_payloads):
    require(proposal['item_id'] == 'CVC-4-OWNERSHIP-1'
            and proposal['status'] == 'PROPOSED_UNEXECUTED'
            and proposal['contract_id'] == 'CVC-U1-A7', 'proposal identity changed')
    require(proposal['budget'] == BUDGET, 'successor scope or budget changed')
    change = proposal['representation_change']
    require(change['operation'] == 'INSERT_ONE_UNUSED_DECLARED_PARAMETER_LEVEL_BEFORE_FINAL_DEF',
            'representation operation changed')
    expected = []
    for ident, name_id in [('E-OWNED-CONTROL', 3), ('E-UNOWNED', 2)]:
        prior = cases[ident]
        expected.append({'predecessor_case': ident, 'successor_case': ident + '-PARAM-RECORD',
                         'input': prior['input'], 'insert_record': {'il': 3, 'param': name_id},
                         'unchanged_artifact': prior['artifact'], 'model_status': prior['model_status']})
    require(change['cases'] == expected, 'exact transition or model status changed')
    require(proposal['retained_inputs']['observer_payloads'] == observer_payloads,
            'pinned observer payloads changed')
    matrix = [{'case': case + '-PARAM-RECORD', 'observer': observer, 'expected': outcome}
              for case, outcome in [('E-OWNED-CONTROL', 'ACCEPT'), ('E-UNOWNED', 'REFUSED_OWNERSHIP')]
              for observer in ('official', 'nanoda')]
    require(proposal['matrix'] == matrix, 'fresh control gate or finite matrix changed')
    accounting = proposal['accounting']
    require(accounting['predecessor_launches'] == 12
            and accounting['predecessor_unused_slots'] == 4
            and accounting['maximum_combined_launches'] == 16
            and accounting['terminal_runs_resumed'] is False, 'predecessor accounting changed')
    require(len(proposal['prelaunch_gates']) == 6 and all(proposal['prelaunch_gates']),
            'prelaunch gates missing')


def check_work(work):
    require(work['item_id'] == 'CVC-4-ADAPTER-REVIEW'
            and work['status'] in ('ACTIVE', 'COMPLETE'), 'work identity changed')
    require(work['research_counts'] == ZERO, 'review performed forbidden research operations')
    require(work['budget'] == {'max_active_seconds': 3600, 'max_interval_seconds': 3600,
                              'byte_variants': 0, 'observer_launches': 0, 'proof_builds': 0,
                              'setup_launches': 0, 'research_network_launches': 0}, 'review budget changed')
    total, previous_end = 0.0, None
    for index, interval in enumerate(work['intervals'], 1):
        require(interval['id'] == index, 'interval order changed')
        start = datetime.fromisoformat(interval['start_utc'])
        require(start.tzinfo is not None, 'interval lacks timezone')
        if interval['end_utc'] is None:
            require(work['status'] == 'ACTIVE' and index == len(work['intervals']), 'unclosed interval')
            end, tick = datetime.now(timezone.utc), time.monotonic()
        else:
            end, tick = datetime.fromisoformat(interval['end_utc']), interval['end_monotonic']
        elapsed = tick - interval['start_monotonic']
        require(math.isfinite(elapsed) and 0 <= elapsed <= 3600, 'interval exceeds cap')
        require(abs((end-start).total_seconds() - elapsed) < 2, 'UTC/monotonic mismatch')
        require(previous_end is None or start >= previous_end, 'overlapping intervals')
        if interval['end_utc'] is not None:
            require(abs(interval['active_seconds'] - elapsed) < 1e-6, 'active charge mismatch')
        total += elapsed
        previous_end = end
    require(work['intervals'] and total <= 3600, 'cumulative active cap exceeded')
    if work['status'] == 'COMPLETE':
        require(abs(work['active_seconds'] - total) < 1e-6, 'total charge mismatch')
    return total


def validate(root):
    root = Path(root)
    assessment = load(root / BASE / 'assessment.json')
    proposal = load(root / BASE / 'successor-proposal.json')
    manifest = load(root / BASE / 'evidence-manifest.json')
    require(assessment['item_id'] == 'CVC-4-ADAPTER-REVIEW'
            and assessment['outcome'] == 'SUCCESS' and assessment['decision'] == 'SUCCESSOR'
            and assessment['scientific_status'] == 'EXISTING_EVIDENCE_INPUT_TRANSITION_REVIEW_ONLY',
            'review scope or outcome changed')
    require(assessment['research_counts'] == ZERO and assessment['next_item_started'] is False,
            'review claims successor execution')
    require(assessment['external_action']['decision'] == 'NO_EXTERNAL_ACTION_NOW',
            'external-action decision changed')
    work = load(root / BASE / 'work-record.json')
    require(manifest['base_commit'] == work['base_commit'], 'entry commit changed')
    bound = {}
    for binding in manifest['inputs']:
        path = binding['path']
        require(path not in bound and not Path(path).is_absolute() and '..' not in Path(path).parts,
                'invalid or duplicate binding')
        raw = subprocess.check_output(['git', 'show', f"{manifest['base_commit']}:{path}"], cwd=root)
        require(len(raw) == binding['bytes'] and hashlib.sha256(raw).hexdigest() == binding['sha256'],
                'historical evidence identity changed: ' + path)
        if path.startswith(('results/research/conditional-validation-contracts/', 'corpus/generated/')):
            require((root / path).read_bytes() == raw, 'frozen evidence changed: ' + path)
        bound[path] = raw
    cases = {row['id']: row for row in json.loads(bound[str(PRIOR / 'cases.json')])['cases']}
    observer_payloads = json.loads(bound['config/cvc4-u1-a7-0002.json'])['payloads']
    check_proposal(proposal, cases, observer_payloads)
    prior = json.loads(bound[str(PRIOR / 'result.json')])
    require(prior['outcome'] == 'BOUNDED_UNRESOLVED', 'predecessor outcome changed')
    require(json.loads(bound['results/workflow-refresh/cvc-4-conditional-2026-09-07/validation.json'])['status']
            == 'PASS', 'predecessor closure not validated')
    # Inspect old bytes only. Do not serialize, construct, or execute either proposed variant.
    for row in proposal['representation_change']['cases']:
        records = [json.loads(line) for line in bound[row['input']['path']].splitlines()]
        require([r['il'] for r in records if 'il' in r] == [1, 2], 'fresh level index is not 3')
        declared = records[-1]['def']['levelParams']
        names = {r['in']: r['str']['str'] for r in records if 'in' in r}
        require(row['insert_record']['param'] in declared
                and names[row['insert_record']['param']] == 'v', 'insertion is not declared v')
        require([r['param'] for r in records if 'param' in r] == [next(i for i, n in names.items() if n == 'u')],
                'retained parameter-level prerequisite changed')
    for claim in assessment['source_claims']:
        lines = bound[claim['source']].splitlines()
        start, end = claim['lines']
        require(1 <= start <= end <= len(lines), 'source locator outside bound file')
    return {'item_id': assessment['item_id'], 'outcome': assessment['outcome'],
            'decision': assessment['decision'], 'bound_inputs': len(bound),
            'active_seconds': check_work(work), 'research_counts': ZERO,
            'next_item': proposal['item_id'], 'next_item_started': False}


def render(root):
    assessment = load(Path(root) / BASE / 'assessment.json')
    proposal = load(Path(root) / BASE / 'successor-proposal.json')
    lines = ['# CVC-4-ADAPTER-REVIEW — ownership input decision', '',
             '**SUCCESS** for an existing-evidence review; **SUCCESSOR** recommended. No successor bytes or observations were produced.', '',
             assessment['finding'], '', '## Value and alternatives', '']
    for alternative in assessment['alternatives']:
        lines += [f"- **{alternative['id']} ({alternative['decision']}):** {alternative['value']} {alternative['cost_or_limit']}"]
    lines += ['', '## Exact proposed transition', '',
              'Insert one unused `v` parameter-level record immediately before the final definition in each retained ownership stream: fresh level index 3, name index 3 for the control and 2 for the candidate. Preserve every original byte in order. These are new scientific artifacts even though referenced declaration syntax is unchanged.', '',
              'Keep the same observers and revision-02 semantic options. Cap the successor at one pair, two streams, four launches of at most 30 seconds, and 5400 cumulative active seconds including engineering. All twelve predecessor charges remain; cumulative observer reservations are capped at sixteen. Terminal run IDs and their unused slots remain closed.', '',
              'Both fresh controls must accept before either candidate runs. Parser error, ownership refusal, other refusal, acceptance, timeout and unknown remain distinct. A return code alone cannot establish which boundary was reached.', '',
              '## Entry gates', '']
    lines += [f'{i}. {gate}' for i, gate in enumerate(proposal['prelaunch_gates'], 1)]
    lines += ['', '## Limits and recommendation', '', proposal['stop_condition'], '',
              assessment['literature_review']['basis'], '', assessment['external_action']['reason'], '']
    lines += ['- ' + item for item in assessment['limitations']]
    lines += ['', 'Select **CVC-4-OWNERSHIP-1**, READY and unstarted. Original CVC-4/CVC-5 remain PLANNED under unmet original dependencies. Upstream access is still unconfirmed; other themes remain deferred.', '',
              'Canonical records: [assessment](assessment.json), [exact proposal](successor-proposal.json), [input bindings](evidence-manifest.json), [work accounting](work-record.json). Recheck with `scripts/validate-cvc4-adapter-review`. The validator reads existing bytes and generates no scientific input.', '']
    return '\n'.join(lines)
