"""Versioned A7 transcript repair; historical audit/evidence remain unchanged.

This parses the declaration reports emitted by the fixed baseline and proof
suffix. Universe annotations contain declaration parameters, not arbitrary Lean
expressions. The baseline fails closed on all diagnostics/unclaimed output;
proof output retains the original policy permitting harmless linter warnings.
"""
import re

from lib import cvc_a7_audit as predecessor
from lib import cvc_runner_audit as runner


A7 = predecessor.A7
COMPARATORS = predecessor.COMPARATORS
TYPE_PAIRS = predecessor.TYPE_PAIRS
TYPE_NAMES = predecessor.TYPE_NAMES
require = predecessor.require

# These are declaration universe parameters printed by #check / #print axioms,
# not instantiated universe expressions occurring inside a printed type body.
_PARAMETER = r"[A-Za-z_][A-Za-z_0-9']*"
_DECLARATION = _PARAMETER + r'(?:\.' + _PARAMETER + r')*'
_ARITIES = {
    'Classical.choice': 1, 'cvcA7ExpectedChoice': 1,
    'Quot.sound': 1, 'cvcA7ExpectedQuotSound': 1,
    'Std.TreeMap.all_eq_all_toList': 2, 'cvcA7ExpectedTreeMapAll': 2,
}


class ScientificMismatch(ValueError):
    """A fully parsed report disagrees with the immutable scientific contract."""


def _scientific_require(ok, message):
    if not ok:
        raise ScientificMismatch(message)


def _diagnostics(stdout, stderr):
    require(not stderr.strip(), 'unexpected compiler diagnostic')
    # Lean diagnostics can carry a source location and a multi-line continuation.
    # Reject even unknown diagnostic kinds when they have a source position.
    require(re.search(r'(?m)^[ \t]*[^\n]*?:[0-9]+:[0-9]+:', stdout) is None,
            'source-positioned compiler diagnostic')
    require(re.search(r'(?im)^[ \t]*(?:error|warning|information|info|note|trace|debug|fatal):',
                      stdout) is None, 'unexpected compiler diagnostic')


def _declaration(text):
    """Return an exact declaration name and validated optional universe list."""
    match = re.fullmatch(r'(' + _DECLARATION + r')(?:\.\{([^{}]*)\})?', text.strip())
    require(match is not None, 'malformed declaration universe annotation')
    name, decoration = match.groups()
    if decoration is None:
        return name, None
    parameters = tuple(part.strip() for part in decoration.split(','))
    require(all(re.fullmatch(_PARAMETER, part) for part in parameters),
            'malformed declaration universe parameters')
    require(len(parameters) == len(set(parameters)), 'duplicate declaration universe parameter')
    require(len(parameters) == _ARITIES.get(name, 0), 'wrong declaration universe arity')
    return name, parameters


def _axioms(listing):
    """Split an axiom list only at commas outside universe braces."""
    if listing is None or listing == '[]':
        return []
    parts, start, depth = [], 1, 0
    for index in range(1, len(listing) - 1):
        char = listing[index]
        if char == '{':
            require(depth == 0, 'nested universe annotation')
            depth = 1
        elif char == '}':
            require(depth == 1, 'unbalanced universe annotation')
            depth = 0
        elif char == ',' and depth == 0:
            parts.append(listing[start:index])
            start = index + 1
    require(depth == 0, 'unbalanced universe annotation')
    parts.append(listing[start:-1])
    names = [_declaration(part)[0] for part in parts]
    require(len(names) == len(set(names)), 'duplicate axiom')
    return names


def _reports(stdout, names):
    pattern = re.compile(
        r"^'([^\n]+)' (?:does not depend on any axioms|depends on axioms:\s*(\[[^\]]*\]))[ \t]*$",
        re.M,
    )
    found, spans = {}, []
    for match in pattern.finditer(stdout):
        name, listing = match.groups()
        require(name in names and name not in found, 'unexpected or duplicate axiom report')
        found[name] = _axioms(listing)
        spans.append(match.span())
    require(set(found) == set(names), 'missing required full axiom report')
    remainder = stdout
    for start, end in reversed(spans):
        remainder = remainder[:start] + remainder[end:]
    require('depends on axioms' not in remainder and 'does not depend on any axioms' not in remainder,
            'malformed extra axiom report')
    return found, remainder


def _types(stdout):
    # Headers may wrap inside .{u_1, u_2}. Require line-start declaration names;
    # every continuation must be indented, including wrapped header parameters.
    name_re = '|'.join(re.escape(name) for name in TYPE_NAMES)
    start = re.compile(r'^@?((?:%s)(?:\.\{[^{}]*\})?)[ \t]*:[ \t]*(.*)$' % name_re, re.M)
    matches = list(start.finditer(stdout))
    require(len(matches) == len(TYPE_NAMES), 'missing, duplicate, or malformed type report')
    require(not stdout[:matches[0].start()].strip(), 'unclaimed type preamble')
    found, universes = {}, {}
    for index, match in enumerate(matches):
        name, parameters = _declaration(match.group(1))
        require(name not in found, 'duplicate type report')
        end = matches[index + 1].start() if index + 1 < len(matches) else len(stdout)
        continuation = stdout[match.end():end]
        require(all(not line.strip() or line.startswith((' ', '\t'))
                    for line in (match.group(1).splitlines()[1:] + continuation.splitlines())),
                'unclaimed or malformed type output')
        body = match.group(2) + continuation
        require(body.strip(), 'empty type report')
        found[name], universes[name] = body, parameters
    require(tuple(found) == TYPE_NAMES, 'type reports are not in fixed source order')
    for actual, expected in TYPE_PAIRS:
        require(universes[actual] == universes[expected], 'paired header universe annotations differ')
        _scientific_require(predecessor._normal(found[actual]) == predecessor._normal(found[expected]),
                            'imported type differs from fixed source expectation: ' + actual)
    return [{'actual': actual, 'expected_alias': expected, 'type': found[actual]}
            for actual, expected in TYPE_PAIRS]


def _exact_comparators(reports):
    _scientific_require(all(len(reports[name]) == len(A7) and set(reports[name]) == set(A7)
                            for name in COMPARATORS),
                        'comparator assumptions must exactly equal the fixed A7 set')


def audit_baseline(stdout, stderr):
    """Audit the newly counted fixed baseline; never clean a prior transcript."""
    require('sorry' not in (stdout + stderr).lower(), 'sorry diagnostic or axiom')
    _diagnostics(stdout, stderr)
    reports, type_output = _reports(stdout, COMPARATORS)
    _exact_comparators(reports)
    return {
        'mode': 'baseline', 'status': 'BASELINE_TYPES_AND_AXIOMS_MATCH',
        'comparators': list(COMPARATORS), 'assumptions': list(A7),
        'transitive_axioms': reports, 'types': _types(type_output),
    }


def audit(stdout, stderr, assumptions, mode='proof'):
    """Keep the original result skeleton and exact comparator A7 envelope."""
    require('sorry' not in (stdout + stderr).lower(), 'sorry diagnostic or axiom')
    # Proof admission still relies on successful compiler exit plus the trusted
    # generated fixed-type skeleton. Preserve historical warning tolerance; an
    # unused simp argument does not alter theorem derivability. Errors are not
    # harmless, even if a malformed compiler process were to exit successfully.
    require(re.search(r'(?im)^[ \t]*(?:[^\n]*?:[0-9]+:[0-9]+:[ \t]*)?error:',
                      stdout + '\n' + stderr) is None, 'compiler error diagnostic')
    declarations = runner.targets(mode)
    reports, _ = _reports(stdout, [name for name, _ in declarations] + list(COMPARATORS))
    _exact_comparators(reports)
    for name, _ in declarations:
        _scientific_require(set(reports[name]) <= set(A7),
                            'Lab result has an assumption outside A7: ' + name)
    return {
        'mode': mode, 'declarations': [{'name': name, 'type': typ} for name, typ in declarations],
        'transitive_axioms': reports, 'conditional': True,
        'model_id': 'CVC-U1-A7', 'assumptions': list(A7),
    }


def baseline_source(expectations):
    """Preserve independent typed definitions and suppress only two known linters."""
    source = predecessor.baseline_source(expectations)
    return source.replace(
        b'import Lean4Lean.Verify.Level\n\n',
        b'import Lean4Lean.Verify.Level\n\n'
        b'-- Same reviewed definitions; these two style diagnostics are intentionally disabled.\n'
        b'set_option linter.defProp false\n'
        b'set_option warn.classDefReducibility false\n\n',
        1,
    )
