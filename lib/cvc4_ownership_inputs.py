"""The exact two-stream input transition; no general importer or execution API."""
import hashlib
import json
from pathlib import Path

from lib.cvc2_artifact import decode_sort_definition
from lib.cvc_prep import require

BASE = 'results/research/conditional-validation-contracts/cvc-4-ownership-1'
PROPOSAL = 'results/research/conditional-validation-contracts/cvc-4-adapter-review/successor-proposal.json'
PROPOSAL_SHA = 'ed380aca76b5d54598ca155982a59a5c656aae7e5b7f72337afd1f561cc1f1c7'


def receipt(root, path):
    return {'path': path, 'sha256': hashlib.sha256((root / path).read_bytes()).hexdigest()}


def projection(raw):
    """Supplementary raw dependency projection, without a support/validity claim."""
    names, levels, expressions = {}, {0: ['zero']}, {}
    records = [json.loads(line) for line in raw.splitlines()]
    for row in records[1:-1]:
        if 'in' in row:
            names[row['in']] = row['str']['str']
        elif 'il' in row:
            if 'param' in row:
                levels[row['il']] = ['param', names[row['param']]]
            elif 'succ' in row:
                levels[row['il']] = ['succ', levels[row['succ']]]
            else:
                raise ValueError('unexpected level in fixed ownership projection')
        elif 'ie' in row:
            expressions[row['ie']] = levels[row['sort']]
        else:
            raise ValueError('unexpected record in fixed ownership projection')
    d = records[-1]['def']
    return {'name': names[d['name']], 'params': [names[n] for n in d['levelParams']],
            'value_level': expressions[d['value']], 'type_level': expressions[d['type']]}


def transition(original, spec, revised=None):
    require(hashlib.sha256(original).hexdigest() == spec['input']['sha256'], 'predecessor bytes changed')
    lines = original.splitlines(keepends=True)
    require(original.endswith(b'\n') and all(line.endswith(b'\n') for line in lines), 'LF records required')
    rows = [json.loads(line) for line in lines]
    require(set(rows[-1]) == {'def'} and sum('def' in r for r in rows) == 1, 'one final definition required')
    record = spec['insert_record']
    require(record == {'il': 3, 'param': 3 if spec['predecessor_case'] == 'E-OWNED-CONTROL' else 2}, 'exact insertion changed')
    require([r['il'] for r in rows if 'il' in r] == [1, 2], 'inserted level must be fresh and consecutive')
    names = {r['in']: r['str']['str'] for r in rows if 'in' in r}
    require(names[record['param']] == 'v' and record['param'] in rows[-1]['def']['levelParams'], 'inserted parameter must be declared v')
    # Only the selected grammar is admitted. Name IDs equal to 3 are unrelated
    # to level index 3; inspect level references in their own namespace.
    for row in rows[1:-1]:
        if 'il' in row:
            require(set(row) in ({'il', 'param'}, {'il', 'succ'}), 'unexpected old level form')
            if 'succ' in row:
                require(row['succ'] != 3, 'old level references inserted index')
        elif 'ie' in row:
            require(set(row) == {'ie', 'sort'} and row['sort'] != 3, 'old expression references inserted index')
        else:
            require(set(row) == {'in', 'str'}, 'unexpected old expression/record form')
    inserted = json.dumps(record, separators=(',', ':')).encode() + b'\n'
    expected = b''.join(lines[:-1]) + inserted + lines[-1]
    if revised is None:
        revised = expected
    require(revised == expected, 'successor must contain only the exact inserted line')
    revised_lines = revised.splitlines(keepends=True)
    require(b''.join(revised_lines[:-2] + revised_lines[-1:]) == original, 'deletion must recover predecessor bytes')
    require(projection(original) == projection(revised) == spec['unchanged_artifact'], 'raw declaration AST changed')
    if spec['predecessor_case'] == 'E-OWNED-CONTROL':
        require(decode_sort_definition(revised) == spec['unchanged_artifact'], 'strict owned decode differs')
        decoder = 'ACCEPTED_STRUCTURAL_SUBSET'
    else:
        try:
            decode_sort_definition(revised)
        except ValueError as error:
            require(str(error) == 'unowned universe parameter in a level record', 'wrong strict decoder refusal')
        else:
            raise ValueError('unsupported candidate silently admitted')
        decoder = 'REFUSED_UNOWNED_UNIVERSE_PARAMETER'
    return revised, decoder


def build(root, write=False):
    root = Path(root).resolve()
    proposal = json.loads((root / PROPOSAL).read_text())
    require(receipt(root, PROPOSAL)['sha256'] == PROPOSAL_SHA, 'frozen proposal changed')
    cases = []
    for spec in proposal['representation_change']['cases']:
        path = BASE + '/inputs/' + spec['successor_case'].lower() + '.ndjson'
        original = (root / spec['input']['path']).read_bytes()
        output = root / path
        if write and not output.exists():
            raw, _ = transition(original, spec)
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_bytes(raw)
        raw, decoder = transition(original, spec, output.read_bytes())
        cases.append({'id': spec['successor_case'], 'pair_id': 'ownership',
                      'role': 'control' if 'CONTROL' in spec['predecessor_case'] else 'candidate',
                      'predecessor': spec['input'], 'input': receipt(root, path),
                      'insert_record': spec['insert_record'], 'artifact': projection(raw),
                      'model_status': spec['model_status'], 'strict_decoder': decoder,
                      'invariants': 'Sole exact line before final def; deleting it recovers predecessor bytes; fresh index 3 names declared v and is unreferenced by original level/expression records.'})
    result = {'schema_version': 1, 'item_id': 'CVC-4-OWNERSHIP-1', 'contract_id': 'CVC-U1-A7',
              'proposal': receipt(root, PROPOSAL), 'cases': cases,
              'provenance': 'Lab-authored input successors. Retained metadata is grammar compatibility, not a claim these streams were produced by the named exporter.',
              'scope': 'Raw projection is supplementary syntax evidence only. Strict decoder and model support remain unchanged; E-UNOWNED is unsupported, not proved semantically invalid.'}
    dest = root / BASE / 'cases.json'
    if write and not dest.exists():
        dest.write_text(json.dumps(result, indent=2) + '\n')
    require(json.loads(dest.read_text()) == result, 'fixed case manifest drift')
    return result
