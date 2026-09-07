"""Fixed CVC-U1-A7 baseline and conditional proof audit.

The baseline is deliberately narrow.  It admits only the two imported
comparators, the seven source-reviewed assumptions, and paired ``#check``
output from ``cvc-a7/Baseline.lean``.  It is a parser for a fixed compiler
transcript, not a parser for arbitrary Lean output.
"""
import re

from lib import cvc_runner_audit as runner


COMPARATORS = tuple(runner.COMPARATORS)
A7 = (
    'propext',
    'Classical.choice',
    'Quot.sound',
    'Lean.Level.instLawfulBEqLevel',
    'Lean.Level.isExplicitSubsumedAux_eq',
    'Lean.Level.normalize_eq',
    'Std.TreeMap.all_eq_all_toList',
)

# Each actual imported name is immediately followed by its source-typed alias.
TYPE_PAIRS = (
    ("Lean.Level.isEquiv'_wf", 'cvcA7ExpectedIsEquivWf'),
    ("Lean.Level.isEquiv'_complete", 'cvcA7ExpectedIsEquivComplete'),
    ('propext', 'cvcA7ExpectedPropext'),
    ('Classical.choice', 'cvcA7ExpectedChoice'),
    ('Quot.sound', 'cvcA7ExpectedQuotSound'),
    ('Lean.Level.instLawfulBEqLevel', 'cvcA7ExpectedLawfulBEqLevel'),
    ('Lean.Level.isExplicitSubsumedAux_eq', 'cvcA7ExpectedExplicitSubsumed'),
    ('Lean.Level.normalize_eq', 'cvcA7ExpectedNormalize'),
    ('Std.TreeMap.all_eq_all_toList', 'cvcA7ExpectedTreeMapAll'),
)
TYPE_NAMES = tuple(name for pair in TYPE_PAIRS for name in pair)


def require(ok, message):
    if not ok:
        raise ValueError(message)


def _normal(text):
    """Compare compiler renderings, preserving every non-whitespace token."""
    return re.sub(r'\s+', '', text)


def _diagnostics(stdout, stderr):
    """A successful fixed baseline has no compiler diagnostic stream."""
    require(not stderr.strip(), 'unexpected compiler diagnostic')
    require(re.search(r'(?im)^(?:error|warning|information):', stdout) is None,
            'malformed compiler diagnostic')


def _reports(stdout, names):
    """Extract exactly the fixed ``#print axioms`` lines, including continuations."""
    pattern = re.compile(
        r"^'([^\n]+)' (?:does not depend on any axioms|depends on axioms:\s*(\[[^\]]*\]))[ \t]*$",
        re.M,
    )
    found, spans = {}, []
    for match in pattern.finditer(stdout):
        name, listing = match.group(1), match.group(2)
        require(name in names and name not in found, 'unexpected or duplicate axiom report')
        items = [] if listing is None or listing == '[]' else [x.strip() for x in listing[1:-1].split(',')]
        require(all(re.fullmatch(r"[A-Za-z_][A-Za-z_0-9']*(?:\.[A-Za-z_][A-Za-z_0-9']*)*", x)
                    for x in items), 'malformed full axiom list')
        require(len(items) == len(set(items)), 'duplicate axiom')
        found[name] = items
        spans.append(match.span())
    require(set(found) == set(names), 'missing required full axiom report')
    remainder = stdout
    for start, end in reversed(spans):
        remainder = remainder[:start] + remainder[end:]
    require('depends on axioms' not in remainder and 'does not depend on any axioms' not in remainder,
            'malformed extra axiom report')
    return found, remainder


def _types(stdout):
    """Read the nine fixed actual/expected ``#check`` pairs in source order."""
    # Lean may wrap a fully elaborated type.  A type block begins only at one
    # of our known declaration names and ends at the next such declaration or
    # at a #print-axioms line.  Any non-empty unclaimed output is rejected.
    name_re = '|'.join(re.escape(name) for name in TYPE_NAMES)
    start = re.compile(r'^@?(%s)(?:\.\{[^\n}]+\})?\s*:\s*(.*)$' % name_re, re.M)
    matches = list(start.finditer(stdout))
    require(len(matches) == len(TYPE_NAMES), 'missing, duplicate, or malformed type report')
    require(not stdout[:matches[0].start()].strip(), 'unclaimed type preamble')
    found = {}
    for index, match in enumerate(matches):
        name = match.group(1)
        require(name not in found, 'duplicate type report')
        end = matches[index + 1].start() if index + 1 < len(matches) else len(stdout)
        continuation = stdout[match.end():end]
        require(all(not line.strip() or line.startswith((' ', '\t'))
                    for line in continuation.splitlines()),
                'unclaimed or malformed type output')
        body = match.group(2) + continuation
        require(body, 'empty type report')
        found[name] = body
    require(tuple(found) == TYPE_NAMES, 'type reports are not in fixed source order')
    for actual, expected in TYPE_PAIRS:
        require(_normal(found[actual]) == _normal(found[expected]),
                'imported type differs from fixed source expectation: ' + actual)
    return [{'actual': actual, 'expected_alias': expected, 'type': found[actual]}
            for actual, expected in TYPE_PAIRS]


def audit_baseline(stdout, stderr):
    """Validate the uncompiled-until-counted A7 imported-comparator baseline."""
    require('sorry' not in (stdout + stderr).lower(), 'sorry diagnostic or axiom')
    _diagnostics(stdout, stderr)
    reports, type_output = _reports(stdout, COMPARATORS)
    require(all(len(reports[name]) == len(A7) and set(reports[name]) == set(A7) for name in COMPARATORS),
            'comparator assumptions must exactly equal the fixed A7 set')
    return {
        'mode': 'baseline',
        'status': 'BASELINE_TYPES_AND_AXIOMS_MATCH',
        'comparators': list(COMPARATORS),
        'assumptions': list(A7),
        'transitive_axioms': reports,
        'types': _types(type_output),
    }


def audit(stdout, stderr, assumptions, mode='proof'):
    """Audit a later Lab result under A7 without broadening the A7 envelope.

    ``assumptions`` remains in the signature for runner compatibility.  Its
    historical policy is intentionally not authority for this successor.
    """
    require('sorry' not in (stdout + stderr).lower(), 'sorry diagnostic or axiom')
    policy = {'conditional_axiom_policy': {
        'standard_allowed': list(A7), 'source_helpers_allowed': [],
    }}
    result = runner.audit(stdout, stderr, policy, mode)
    reports = result['transitive_axioms']
    require(all(len(reports[name]) == len(A7) and set(reports[name]) == set(A7) for name in COMPARATORS),
            'comparator assumptions must exactly equal the fixed A7 set')
    for name, values in reports.items():
        require(set(values) <= set(A7), 'Lab result has an assumption outside A7: ' + name)
    result.update(model_id='CVC-U1-A7', assumptions=list(A7), conditional=True)
    return result


def baseline_source(expectations):
    """Render the fixed, source-reviewed expectation declarations mechanically."""
    entries = expectations['comparators'] + expectations['assumptions']
    require([(r['name'], r['expected_alias']) for r in entries] == list(TYPE_PAIRS),
            'expectation declaration identities changed')
    require(expectations['exact_comparator_axioms'] == list(A7), 'expectation envelope changed')
    declarations = []
    for row in entries:
        declaration = row['expected_declaration']
        require(declaration.startswith('noncomputable def ' + row['expected_alias']) and
                ':=' in declaration and ':' in declaration.split(':=', 1)[0],
                'expected declaration must have an independent written type')
        declarations.append(declaration)
    return ('import Lean4Lean.Verify.Level\n\n'
            '-- Generated from the source-reviewed baseline-expectations.json; uncompiled in preparation.\n'
            '-- The counted baseline prints imported and independently written expected types.\n'
            'open Lean4Lean\nopen private isExplicitSubsumedAux from Lean.Level\n\n'
            + '\n\n'.join(declarations) + '\n\n'
            + 'set_option pp.universes true\nset_option pp.explicit true\n'
            + 'set_option pp.fullNames true\nset_option pp.all true\n'
            + '\n'.join('#check @' + name for name in TYPE_NAMES) + '\n\n'
            + '\n'.join('#print axioms ' + name for name in COMPARATORS) + '\n').encode()
