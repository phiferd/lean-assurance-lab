"""Cheap E0 records. No experiments, confirmation results or assurance writes."""
from collections import Counter
from datetime import datetime, timezone
import fcntl
import hashlib
import json
import os
import re
from pathlib import Path
import subprocess

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
LEDGER = 'explorations/ledger.jsonl'
LEGACY_IDENTITIES = 'explorations/legacy-input-identities.json'


def read_json(raw):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError('duplicate JSON key: ' + key)
            result[key] = value
        return result
    def nonfinite(value):
        raise ValueError('nonfinite JSON number: ' + value)
    return json.loads(raw, object_pairs_hook=unique, parse_constant=nonfinite)


def safe_path(root, value):
    path = Path(value)
    target = root / path
    if (path.is_absolute() or '..' in path.parts or target.is_symlink()
            or not target.resolve().is_relative_to(root.resolve())):
        raise ValueError('missing or unsafe evidence file: ' + value)
    return target


def local_file(root, value):
    target = safe_path(root, value)
    if not target.is_file():
        raise ValueError('missing or unsafe evidence file: ' + value)
    return target


def input_hashes(root, start):
    hashes = start['data'].get('input_sha256')
    if hashes is None and (root / LEGACY_IDENTITIES).is_file():
        # Exact historical start -> previously retained identity file. Never
        # rewrite an old ledger event or infer identity from today's payload.
        key = hashlib.sha256(json.dumps(start, sort_keys=True).encode()).hexdigest()
        binding = read_json(local_file(root, LEGACY_IDENTITIES).read_bytes()).get(key)
        if binding:
            raw = local_file(root, binding['path']).read_bytes()
            if hashlib.sha256(raw).hexdigest() != binding['sha256']:
                raise ValueError('historical input identity file changed')
            hashes = dict(read_json(raw)['files'])
            hashes[binding['path']] = binding['sha256']
    if hashes is not None:
        if set(hashes) != set(start['data']['inputs']) or any(
                not isinstance(h, str) or not re.fullmatch('[0-9a-f]{64}', h)
                for h in hashes.values()):
            raise ValueError('input identities must cover exactly the recorded inputs')
    return hashes


def validate(root, raw):
    schema = read_json((ROOT / 'schemas/exploration-event.schema.json').read_text())
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    states, confirmations = {}, set()
    for line in raw.splitlines():
        row = read_json(line)
        validator.validate(row)
        kind, ident, data = row['event'], row['id'], row['data']
        stamp = datetime.fromisoformat(row['at'].replace('Z', '+00:00'))
        state = states.get(ident)
        if kind == 'start':
            if state:
                raise ValueError('duplicate exploration start')
            for path in [s['patch'] for s in data['sources'] if 'patch' in s]:
                local_file(root, path)
            states[ident] = {'start': row, 'at': stamp}
            continue
        if not state or stamp < state['at']:
            raise ValueError('missing start or out-of-order event')
        if kind == 'finish':
            if 'finish' in state:
                raise ValueError('exploration is already closed; append a new linked pilot')
            for path in data['raw_output']:
                local_file(root, path)
            if data['outcome'] == 'NO_SIGNAL' and (
                    data['completed_runs'] != state['start']['data']['planned_runs']
                    or data['signal_count'] or not data['measurement_complete']
                    or data['engineering_failures_unresolved']):
                raise ValueError('NO_SIGNAL requires the complete planned observation without unresolved failures')
            if data['outcome'] == 'SIGNAL' and data['signal_count'] == 0:
                raise ValueError('SIGNAL requires an observed candidate signal')
            state['finish'] = row
        else:
            if 'finish' not in state or 'promote' in state:
                raise ValueError('promotion requires one closed, not previously promoted exploration')
            target = data['confirmation_id']
            if target in confirmations:
                raise ValueError('confirmation identity must be new')
            confirmations.add(target)
            state['promote'] = row
        state['at'] = stamp
    for state in states.values():
        hashes = input_hashes(root, state['start'])
        for path in state['start']['data']['inputs']:
            target = safe_path(root, path)
            if 'finish' not in state or hashes is None:
                local_file(root, path)
            if not target.exists():
                state.setdefault('unavailable_inputs', []).append(path)
            if target.exists():
                data = local_file(root, path).read_bytes()
                if hashes is not None and hashlib.sha256(data).hexdigest() != hashes[path]:
                    raise ValueError('recorded input bytes changed: ' + path)
    return states


def committed_prefix(root, raw, base='HEAD'):
    """Git retains the baseline; no second hash graph or receipt hierarchy."""
    tracked = subprocess.check_output(
        ['git', 'ls-tree', '--name-only', base, '--', LEDGER, LEGACY_IDENTITIES],
        cwd=root).decode().splitlines()
    if LEDGER in tracked:
        previous = subprocess.check_output(['git', 'show', f'{base}:{LEDGER}'], cwd=root)
        if not raw.startswith(previous):
            raise ValueError('exploration ledger must preserve the committed prefix')
        retained = {LEGACY_IDENTITIES} if LEGACY_IDENTITIES in tracked else set()
        for line in previous.splitlines():
            data = read_json(line)['data']
            retained.update(data.get('inputs', []) + data.get('raw_output', []))
            retained.update(s['patch'] for s in data.get('sources', []) if 'patch' in s)
        if retained and subprocess.check_output(
                ['git', 'diff', '--name-only', base, '--', *sorted(retained)], cwd=root).strip():
            raise ValueError('previously recorded exploratory evidence changed; retain it and use new paths')
    if raw and not raw.endswith(b'\n'):
        raise ValueError('ledger must end in a complete newline-delimited record')


def authorize_start(root, event):
    from lib.research_queue_v4 import load_queue
    queue = load_queue(root, require_ready=True)
    item = next(i for i in queue['items'] if i['id'] == event['data']['campaign'])
    if item['id'] != queue['selected_item'] or item['status'] != 'ACTIVE':
        raise ValueError('start requires the selected ACTIVE exploratory campaign')
    if not any(p.endswith('.md') and '\nEvidence class: E0\n' in local_file(root, p).read_text()
               for p in item['evidence_refs']):
        raise ValueError('campaign needs an explicit E0 plan in its queue evidence')


def append(root, event):
    ledger = local_file(root, LEDGER)
    with ledger.open('r+b') as stream:
        fcntl.flock(stream, fcntl.LOCK_EX)
        raw = stream.read()
        committed_prefix(root, raw)
        event = dict(event, at=datetime.now(timezone.utc).isoformat())
        if event['event'] == 'start':
            hashes = {p: hashlib.sha256(local_file(root, p).read_bytes()).hexdigest()
                      for p in event['data']['inputs']}
            if event['data'].get('input_sha256', hashes) != hashes:
                raise ValueError('supplied input identities differ from launch inputs')
            event['data'] = dict(event['data'], input_sha256=hashes)
        encoded = (json.dumps(event, sort_keys=True, allow_nan=False) + '\n').encode()
        validate(root, raw + encoded)
        if event['event'] == 'start':
            authorize_start(root, event)
        if event['event'] == 'promote':
            queue = read_json((root / 'config/research-queue.json').read_text())
            if any(i['id'] == event['data']['confirmation_id'] for i in queue['items']):
                raise ValueError('confirmation ID already exists in research queue')
        stream.write(encoded)
        stream.flush()
        os.fsync(stream.fileno())
    return event


def summary(states):
    counts = Counter(s['finish']['data']['outcome'] if 'finish' in s else 'OPEN'
                     for s in states.values())
    return {'evidence_class': 'E0', 'started': len(states),
            **{key: counts[key] for key in ('OPEN', 'NO_SIGNAL', 'SIGNAL', 'INCONCLUSIVE')},
            'confirmation_proposals': sum('promote' in s for s in states.values()),
            'unavailable_input_payloads': sorted({p for s in states.values()
                                                   for p in s.get('unavailable_inputs', [])}),
            'claim': 'Exploratory observations only; proposals are not confirmed discrepancies.'}


def proposal(states, confirmation_id):
    for ident, state in states.items():
        event = state.get('promote', {}).get('data', {})
        if event.get('confirmation_id') == confirmation_id:
            return {'id': confirmation_id, 'evidence_class': 'E1', 'status': 'PLANNED',
                    'derived_from': ident, 'hypothesis': event['hypothesis'],
                    'reason': event['reason'], 'execution_authorized': False,
                    'required': ['Separate queue selection and protocol',
                                 'Frozen inputs and independent expected-result review',
                                 'Fresh controlled execution and required validation'],
                    'nonclaim': 'E0 outputs cannot serve as confirmation results; reused cases are not fresh holdouts.'}
    raise ValueError('no such confirmation proposal')


def validation_lane(root, base):
    """Only ledger/raw additions bypass full CI; any shared change uses full CI."""
    paths = subprocess.check_output(['git', 'diff', '--name-only', base, 'HEAD', '--'], cwd=root).decode().splitlines()
    return 'exploration' if paths and all(
        p == LEDGER or p.startswith('explorations/runs/') for p in paths) else 'full'
