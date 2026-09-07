"""Finite CVC-4 byte bindings; no general parser/refinement claim or launch API.

Original CVC-2 bytes and decoder remain unchanged. New boundary streams are
Lab-authored instances of the same NDJSON grammar, not exporter-produced proofs.
"""
from copy import deepcopy
import hashlib
import json
from pathlib import Path

from lib.cvc2_artifact import decode_sort_definition

BASE = 'results/research/conditional-validation-contracts/cvc-4-conditional'
EXAMPLES = 'results/research/conditional-validation-contracts/cvc-2/examples.json'


def receipt(root, path):
    path = Path(path)
    return {'path': str(path.relative_to(root)), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def serialize(artifact, header):
    """Encode exactly the supplied finite syntax, retaining imax and ownership.

    Names and children precede references. Never normalize a level, infer an
    owner, change the supplied value, or consult a validator.
    """
    rows, names, levels = [deepcopy(header)], {}, {('zero',): 0}

    def name(text):
        if text not in names:
            names[text] = len(names) + 1
            rows.append({'in': names[text], 'str': {'pre': 0, 'str': text}})
        return names[text]

    def freeze(node):
        return tuple(freeze(x) if isinstance(x, list) else x for x in node)

    def level(node):
        key = freeze(node)
        if key in levels:
            return levels[key]
        tag = node[0]
        if tag == 'param':
            value = name(node[1])
        elif tag == 'succ':
            value = level(node[1])
        elif tag in ('max', 'imax'):
            value = [level(node[1]), level(node[2])]
        else:
            raise ValueError('unsupported level constructor')
        index = len(levels)
        levels[key] = index
        rows.append({'il': index, tag: value})
        return index

    decl = name(artifact['name'])
    params = [name(n) for n in artifact['params']]
    value, typ = level(artifact['value_level']), level(artifact['type_level'])
    rows.extend([{'ie': 0, 'sort': typ}, {'ie': 1, 'sort': value},
                 {'def': {'all': [decl], 'hints': 'opaque', 'levelParams': params,
                          'name': decl, 'safety': 'safe', 'type': 0, 'value': 1}}])
    return ('\n'.join(json.dumps(x, separators=(',', ':')) for x in rows) + '\n').encode()


def finite_cases(root):
    root = Path(root)
    examples = json.loads((root / EXAMPLES).read_text())['examples']
    by_id = {x['id']: x for x in examples}
    rows = []
    for ident, role in [('E-CONTROL', 'control'), ('E-POS', 'candidate')]:
        source = by_id[ident]
        rows.append({'id': ident, 'pair_id': 'right-succ', 'role': role,
                     'artifact': source['artifact'], 'input': source['input_binding'],
                     'model_status': 'CHECKED_REQUIRED_ACCEPTANCE',
                     'model_evidence': 'Lab.CVC2.required_acceptance; Lab.CVC2.preservation',
                     'construction': 'UNCHANGED_CVC2_BYTES'})
    zero = deepcopy(by_id['E-ZERO']['artifact'])
    zcontrol = deepcopy(zero)
    zcontrol['name'] += 'Control'
    zcontrol['type_level'] = ['succ', ['zero']]
    unowned = deepcopy(by_id['E-UNOWNED']['artifact'])
    ucontrol = deepcopy(unowned)
    ucontrol['name'] += 'Control'
    ucontrol['params'] = ['u', 'v']
    for ident, pair, role, ast, status, evidence in [
        ('E-ZERO-CONTROL', 'right-zero', 'control', zcontrol, 'MODEL_VALID_BY_DEFINITION',
         'meaning(imax u zero)=0; inferred and declared type levels are both 1 for every assignment.'),
        ('E-ZERO', 'right-zero', 'candidate', zero, 'CHECKED_MODEL_INVALID',
         'Lab.CVC2.boundary: Supported zeroBoundary and not Contract and not Accepts.'),
        ('E-OWNED-CONTROL', 'ownership', 'control', ucontrol, 'MODEL_VALID_BY_DEFINITION',
         'All names are owned; both inferred and declared type levels equal rho(u)+1.'),
        ('E-UNOWNED', 'ownership', 'candidate', unowned, 'CHECKED_UNSUPPORTED',
         'Lab.CVC2.boundary: not Supported unownedBoundary and not Accepts.')]:
        rows.append({'id': ident, 'pair_id': pair, 'role': role, 'artifact': ast,
                     'input': {'path': BASE + '/inputs/' + ident.lower() + '.ndjson'},
                     'model_status': status, 'model_evidence': evidence,
                     'construction': 'LAB_SERIALIZATION_OF_FIXED_AST'})
    return rows


def build(root, write=False):
    root = Path(root)
    rows = finite_cases(root)
    header = json.loads((root / rows[0]['input']['path']).read_bytes().splitlines()[0])
    for row in rows:
        path = root / row['input']['path']
        if row['construction'] != 'UNCHANGED_CVC2_BYTES':
            raw = serialize(row['artifact'], header)
            if write:
                path.parent.mkdir(parents=True, exist_ok=True)
                if path.exists() and path.read_bytes() != raw:
                    raise ValueError('refuse to overwrite different input bytes: ' + str(path))
                path.write_bytes(raw)
            if path.read_bytes() != raw:
                raise ValueError('serialized input differs: ' + row['id'])
        if row['id'] == 'E-UNOWNED':
            try:
                decode_sort_definition(path.read_bytes())
            except ValueError as error:
                if str(error) != 'unowned universe parameter in a level record':
                    raise
            else:
                raise ValueError('unsupported boundary was silently admitted')
            row['byte_mapping'] = 'Exact deterministic serialization of E-UNOWNED AST; unchanged decoder refuses ownership, as required.'
        elif decode_sort_definition(path.read_bytes()) != row['artifact']:
            raise ValueError('decoded AST differs: ' + row['id'])
        else:
            row['byte_mapping'] = 'Unchanged strict structural decoder equals independently fixed AST; not a parser proof.'
        actual = receipt(root, path)
        if 'sha256' in row['input'] and row['input'] != actual:
            raise ValueError('original CVC-2 identity differs')
        row['input'] = actual
    result = {'schema_version': 1, 'item_id': 'CVC-4-CONDITIONAL', 'model_id': 'CVC-U1-A7',
              'examples_binding': receipt(root, root / EXAMPLES), 'cases': rows,
              'scope': 'Six fixed byte streams in three matched pairs. Two original acceptance bytes remain unchanged; four new streams instantiate the same structured model. Only E-POS/E-CONTROL have the original checked finite acceptance promise.',
              'metadata_provenance': 'New streams reuse the fixed format 3.1.0 header solely for grammar compatibility; they were authored by this Lab serializer, not produced by the named Lean/exporter binary. Their construction and exact bytes are explicit.',
              'nonclaims': ['No arbitrary-byte parser proof.', 'No executable-validator refinement.',
                            'No assumption discharge or normative catalog promotion.']}
    dest = root / BASE / 'cases.json'
    if write:
        if dest.exists() and json.loads(dest.read_text()) != result:
            raise ValueError('refuse to rewrite a different fixed case manifest')
        dest.write_text(json.dumps(result, indent=2) + '\n')
    elif json.loads(dest.read_text()) != result:
        raise ValueError('case manifest drift')
    if not write:
        execution_root = Path(json.loads((root / BASE / 'execution-protocol.json').read_text())['runtime']['execution_root'])
        if not execution_root.is_absolute():
            raise ValueError('execution root must be explicit and absolute')
        for row in rows:
            config = json.loads((root / BASE / 'configurations' / (row['id'].lower() + '.json')).read_text())
            expected = {'use_stdin': False, 'nat_extension': True, 'string_extension': True,
                        'unpermitted_axiom_hard_error': False, 'unsafe_permit_all_axioms': True,
                        'num_threads': 4, 'print_success_message': True,
                        'export_file_path': str(execution_root / row['input']['path'])}
            if config != expected:
                raise ValueError('Nanoda profile or exact input target differs: ' + row['id'])
    return result
