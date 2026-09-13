#!/usr/bin/env python3
"""Replay retained hashes, diagnostics and four recursor records; launch no checker."""
import argparse
import hashlib
import json
from pathlib import Path
import tarfile

ROOT = Path(__file__).resolve().parents[3]
PREFIX = 'results/research/arena-inductive-isolation-1/'
ITEM = 'ARENA-INDUCTIVE-ISOLATION-1'
TIP = '83d5e34a2de6f8cd7d0096f93a893179d724d3c9'
SHA = 'aaf1dad73e5ad2e4b22ec17165bbbfe2839a9aa4d739a3f2ebefa4730c26f6b0'
CASE_IDS = {'inductWrongCtorParams', 'inductWrongCtorResParams', 'inductWrongCtorResLevel', 'inductInIndex'}
REUSE = {
    'proof-param-swap': ('lal-ordinary-inductive-proof-parameter-candidate', 'lal-proof-parameter-uniformity-candidate'),
    'proof-param-ok': ('lal-ordinary-inductive-proof-parameter-control', 'lal-proof-parameter-uniformity-control'),
    'positivity-whnf': ('lal-ordinary-inductive-reducible-positivity-candidate', 'lal-reducible-hidden-positivity-candidate'),
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def read(root, path):
    require(isinstance(path, str) and path and not Path(path).is_absolute(), 'invalid retained path')
    target = (root / path).resolve()
    require(target.is_relative_to(root.resolve()), 'retained path escapes repository')
    return target.read_bytes()


def binding(path, data):
    return {'path': path, 'sha256': digest(data), 'bytes': len(data)}


def verify(root, row):
    data = read(root, row['path'])
    require(digest(data) == row['sha256'], 'review hash mismatch: ' + row['path'])
    if 'bytes' in row:
        require(type(row['bytes']) is int and row['bytes'] == len(data), 'review size mismatch')
    return data


def replay(root=ROOT):
    root = Path(root)
    review = json.loads(read(root, PREFIX + 'independent-case-review.json'))
    require(review['item_id'] == ITEM and review['arena_revision'] == TIP, 'review identity mismatch')
    ids = [case['id'] for case in review['cases']]
    require(len(ids) == 4 and set(ids) == CASE_IDS, 'four frozen review cases required')
    require(set(review['inspected_cases']) == CASE_IDS and len(review['inspected_cases']) == 4, 'inspection scope mismatch')
    lock = json.loads(read(root, PREFIX + 'source-lock.json'))
    archive_path = PREFIX + 'arena-source.tar.gz'
    archive = read(root, archive_path)
    require(lock['revision'] == TIP and lock['archive'] == archive_path and lock['archive_sha256'] == SHA
            and digest(archive) == SHA, 'locked archive mismatch')
    files = {}
    with tarfile.open(root / archive_path, 'r:gz') as retained:
        prefix = 'lean-kernel-arena-' + TIP + '/'
        for member in retained.getmembers():
            if member.isdir():
                continue
            require(member.isfile() and member.name.startswith(prefix), 'unexpected archive member')
            path = member.name[len(prefix):]
            require(path not in files, 'duplicate archive member')
            with retained.extractfile(member) as stream:
                files[path] = stream.read()
    inventory = [binding(path, data) for path, data in sorted(files.items())]
    require(len(inventory) == 232 and inventory == lock['inventory'], 'archive inventory mismatch')
    tests = [row for row in inventory if row['path'].startswith('tests/') and row['path'].endswith(('.yaml', '.ndjson'))]
    sources = {}
    for row in review['sources'] + [row for row in review['wiring'] if 'sha256' in row]:
        sources[row['path']] = binding(row['path'], verify(root, row))
    cases = []
    for case in review['cases']:
        candidate = verify(root, case['existing_candidate'])
        control = verify(root, case['existing_control'])
        retained = json.loads(verify(root, case['historical_observations']))
        recursors = [row['inductive']['recs'] for line in candidate.splitlines()
                     if 'inductive' in (row := json.loads(line))]
        require(recursors == case['existing_candidate']['recursor_records'], 'copied recursor records mismatch')
        require(retained['created_at'] == case['historical_observations']['created_at'], 'historical date mismatch')
        require(len(retained['validators']) == len(case['historical_observations']['validators']), 'historical observer count mismatch')
        diagnostics = []
        for copied, original in zip(case['historical_observations']['validators'], retained['validators']):
            index = len(diagnostics)
            require(copied['json_pointer'] == f'/validators/{index}/result', 'diagnostic pointer mismatch')
            require(copied['checker'] == original['checker'] and copied['outcome'] == original['result']['normalized_outcome']
                    and copied['diagnostic'] == original['result']['stderr_tail']
                    and copied['control_outcome'] == original['positive_control']['result']['normalized_outcome']
                    and copied['identity'] == original['compatibility']['checker_identity'], 'copied historical diagnostic/identity mismatch')
            require(original['positive_control']['sha256'] == digest(control), 'historical control identity mismatch')
            diagnostics.append({key: copied[key] for key in ('checker', 'outcome', 'diagnostic', 'control_outcome', 'json_pointer')})
        cases.append({'id': case['id'], 'candidate': binding(case['existing_candidate']['path'], candidate),
                      'control': binding(case['existing_control']['path'], control), 'recursor_records': recursors,
                      'historical_observations': binding(case['historical_observations']['path'], read(root, case['historical_observations']['path'])),
                      'diagnostics': diagnostics})
    duplicates = []
    for arena_name, (corpus_name, package_name) in REUSE.items():
        current_path = 'tests/corner-cases/' + arena_name + '.ndjson'
        current = files[current_path]
        comparisons = []
        for path in ('corpus/generated/' + corpus_name + '.ndjson',
                     'results/investigations/corpus-integration-2026-09-05/arena-package/' + package_name + '.ndjson'):
            data = read(root, path)
            comparisons.append({**binding(path, data), 'byte_identical': current == data})
        duplicates.append({'current': binding(current_path, current), 'retained_comparisons': comparisons})
    return {'schema_version': 1, 'item_id': ITEM, 'arena_revision': TIP, 'archive_sha256': SHA,
            'inspection_kind': 'READ_ONLY_EVIDENCE_REPLAY', 'archive_file_count': len(inventory),
            'test_manifest_count': len(tests), 'test_manifests': tests,
            'verified_source_copies': list(sources.values()), 'cases': cases, 'existing_complete_artifact_comparisons': duplicates,
            'scope': 'Archive inventory covers all 232 source files; test_manifests enumerates all tests/ .yaml and .ndjson files. Semantic NDJSON parsing is limited to the four frozen historical candidates. No current test generation or checker execution.'}


def encoded(value):
    return (json.dumps(value, indent=2, sort_keys=True) + '\n').encode()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--write', action='store_true')
    mode.add_argument('--check', action='store_true')
    args = parser.parse_args()
    try:
        generated = encoded(replay())
        target = ROOT / PREFIX / 'static-audit.json'
        if args.write:
            target.write_bytes(generated)
        else:
            require(target.read_bytes() == generated, 'static-audit.json is stale')
        print(json.dumps({'status': 'PASS', 'mode': 'write' if args.write else 'check', 'item_id': ITEM}))
    except (ValueError, KeyError, TypeError, OSError, tarfile.TarError) as error:
        parser.exit(1, 'FAIL: ' + str(error) + '\n')
