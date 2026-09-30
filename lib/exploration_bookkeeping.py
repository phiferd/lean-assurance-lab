"""Unappended E0 drafts and conservative counts of existing retained receipts.

This is bookkeeping, not a runner, verdict interpreter or new receipt format.
Final result selection is explicit when earlier construction results also exist.
"""
import hashlib
import platform
import subprocess
from jsonschema import Draft202012Validator

from lib import exploration as e


def receipts(root, value):
    """Read only the supported supervisor / cell / result layouts."""
    if isinstance(value, list):
        return [receipt for row in value for receipt in receipts(root, row)]
    if not isinstance(value, dict):
        return []
    if 'raw_stdout_path' in value or 'raw_stderr_path' in value:
        required = ('argv', 'exit_code', 'timed_out', 'cleanup_complete',
                    'raw_stdout_path', 'raw_stderr_path', 'stdout_sha256', 'stderr_sha256')
        if any(key not in value for key in required) or not value['argv']:
            raise ValueError('incomplete supervisor receipt; counts unknown')
        if (not isinstance(value['argv'], list)
                or not all(isinstance(arg, str) for arg in value['argv'])
                or type(value['timed_out']) is not bool
                or type(value['cleanup_complete']) is not bool
                or value['exit_code'] is not None and type(value['exit_code']) is not int):
            raise ValueError('malformed supervisor receipt; counts unknown')
        for stream in ('stdout', 'stderr'):
            raw = e.local_file(root, value['raw_' + stream + '_path']).read_bytes()
            if hashlib.sha256(raw).hexdigest() != value[stream + '_sha256']:
                raise ValueError('raw stream differs from retained receipt')
        return [value]
    if 'receipt' in value:
        receipt = value['receipt']
        if isinstance(receipt, str):
            receipt = e.read_json(e.local_file(root, receipt).read_bytes())
        return receipts(root, receipt)
    if 'cells' in value:
        return receipts(root, value['cells'])
    return []


def merge(target, rows):
    for row in rows:
        key = (row['raw_stdout_path'], row['raw_stderr_path'])
        # Extended copies of the same supervisor may include sentinel metadata.
        # Core process and stream identities must still agree exactly.
        identity = {k: row[k] for k in ('argv', 'exit_code', 'timed_out',
                    'cleanup_complete', 'stdout_sha256', 'stderr_sha256')}
        if key in target and target[key] != identity:
            raise ValueError('conflicting copies of the same launch receipt')
        if any(set(key) & set(other) and key != other for other in target):
            raise ValueError('ambiguous overlapping raw stream identities')
        target[key] = identity


def inventory(root, paths):
    launches, prelaunch = {}, set()
    for path in paths:
        e.local_file(root, path)
        if not path.endswith('.json'):
            continue
        value = e.read_json(e.local_file(root, path).read_bytes())
        rows = receipts(root, value)
        merge(launches, rows)
        if isinstance(value, dict) and 'error' in value:
            error = str(value['error'])
            explicit = (value.get('checker_process_launched') is False
                        or value.get('status') == 'PREFLIGHT_FAILED_BEFORE_CHILD_LAUNCH')
            before = 'memory monitor backend unavailable before launch' in error
            empty = value.get('completed_cells') == 0 or value.get('cells') == []
            if rows or not (explicit or before and empty):
                raise ValueError('unclassified error receipt; launch counts unknown: ' + path)
            # Multiple exports of one failed attempt do not add attempts.
            prelaunch.add(str(e.safe_path(root, path).parent.relative_to(root)))
    return launches, prelaunch


def counts(root, campaign, final_results):
    states = e.validate(root, e.local_file(root, e.LEDGER).read_bytes())
    trials = {ident: state for ident, state in states.items()
              if state['start']['data']['campaign'] == campaign}
    if not trials or any('finish' not in state for state in trials.values()):
        raise ValueError('counts require a campaign with closed trials')
    final_results = set(final_results)
    if not final_results:
        raise ValueError('select final result paths explicitly; counts otherwise ambiguous')
    all_launches, final_launches, prelaunch, used = {}, {}, set(), set()
    for ident, state in trials.items():
        paths = state['finish']['data']['raw_output']
        selected = final_results.intersection(paths)
        if len(selected) != 1:
            raise ValueError('select exactly one retained final result for ' + ident)
        final_path = next(iter(selected))
        final = {}
        merge(final, receipts(root, e.read_json(e.local_file(root, final_path).read_bytes())))
        if len(final) != state['finish']['data']['completed_runs']:
            raise ValueError('final receipt count disagrees with completed_runs: ' + ident)
        merge(final_launches, receipts(root, e.read_json(e.local_file(root, final_path).read_bytes())))
        used.add(final_path)
        launches, failures = inventory(root, paths)
        for key, identity in launches.items():
            if key in all_launches and all_launches[key] != identity:
                raise ValueError('conflicting campaign launch identities')
            if any(set(key) & set(other) and key != other for other in all_launches):
                raise ValueError('ambiguous overlapping campaign raw streams')
            all_launches[key] = identity
        prelaunch.update(failures)
    if used != final_results:
        raise ValueError('final result path is outside the campaign finish evidence')
    if len(final_launches) != sum(s['finish']['data']['completed_runs'] for s in trials.values()):
        raise ValueError('trials overlap in final launch identities')
    if not set(final_launches).issubset(all_launches):
        raise ValueError('final receipts missing from retained launch inventory')
    # Earlier receipts are retained construction/other attempts, not discarded
    # waste. No assertion about why they ran follows from this count.
    return {'campaign': campaign, 'final_cells': len(final_launches),
            'actual_launches': len(all_launches), 'prelaunch_failures': len(prelaunch),
            'retained_nonfinal_cells': len(set(all_launches) - set(final_launches)),
            'final_results': sorted(final_results),
            'prelaunch_attempts': sorted(prelaunch),
            'limitations': 'Supported retained receipt layouts only; explicit final selection. '
                           'Nonfinal cells are not automatically waste or a scientific classification.'}


def draft(root, kind, ident, raw_output=(), final_result=None):
    """All researcher decisions stay null; append remains the only writer."""
    schema = e.read_json((e.ROOT / 'schemas/exploration-event.schema.json').read_bytes())
    if kind not in ('start', 'finish'):
        raise ValueError('draft event must be start or finish')
    Draft202012Validator(schema['properties']['id']).validate(ident)
    data = {key: None for key in schema['$defs'][kind]['required']}
    event = dict(schema_version=1, evidence_class='E0', event=kind, id=ident, data=data)
    if kind == 'start':
        if raw_output or final_result:
            raise ValueError('receipt options apply only to finish drafts')
        from lib.research_queue_v4 import load_queue
        queue = load_queue(root, require_ready=True)
        item = next(i for i in queue['items'] if i['id'] == queue['selected_item'])
        plans = [p for p in item['evidence_refs'] if p.endswith('.md')
                 and '\nEvidence class: E0\n' in e.local_file(root, p).read_text()]
        if item['status'] not in ('READY', 'ACTIVE') or not plans:
            raise ValueError('selected item must have an explicit E0 plan')
        data.update(campaign=item['id'], sources=[dict(name='lean-assurance-lab',
                    revision=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root).decode().strip())],
                    inputs=plans, versions='Python ' + platform.python_version())
    else:
        states = e.validate(root, e.local_file(root, e.LEDGER).read_bytes())
        if ident not in states or 'finish' in states[ident]:
            raise ValueError('finish draft requires an OPEN trial')
        if raw_output or final_result:
            paths = list(dict.fromkeys(raw_output))
            if final_result not in paths:
                raise ValueError('finish counts need a final result included in raw output')
            launches, prelaunch = inventory(root, paths)
            final = {}
            merge(final, receipts(root, e.read_json(e.local_file(root, final_result).read_bytes())))
            if not final or not set(final).issubset(launches):
                raise ValueError('unsupported or missing final receipts; completed_runs unknown')
            data.update(completed_runs=len(final), raw_output=paths,
                        cost=f'{len(final)} final cells; {len(launches)} retained launches; '
                             f'{len(prelaunch)} prelaunch failures; '
                             f'{len(set(launches) - set(final))} retained nonfinal cells. '
                             'Supported receipts only; model and other costs unknown.')
    return {'event': event, 'unresolved_fields': [k for k, v in data.items() if v is None],
            'instructions': 'Fill researcher fields and source/tool identities, then pass only the '
                            'event object to exploration-record append. This draft is unappended '
                            'and does not authorize execution.'}
