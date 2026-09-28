"""Independent translation and expectation auditor for BINDER-MODEL-PILOT-1.

This module deliberately imports neither the named-variable model nor the
vector producer. It replays only the frozen ordinal-to-input construction
rule, translates named syntax independently, and evaluates lifting and
instantiation directly over de Bruijn syntax.
"""
from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
from typing import Any, Iterable


COUNT = 10_000
SEED = 0xB17D3A9E5C204F61
MASK = (1 << 64) - 1
OPERATIONS = ("LIFT", "SUBST", "LIFT_COMPOSE", "SUBST_COMPOSE")
VECTOR_KEYS = {
    "id", "ordinal", "operation", "family", "variant", "context",
    "named_source", "source", "named_arguments", "arguments", "parameters",
    "contexts_after", "named_expected", "expected",
}


class AuditError(ValueError):
    """Fail-closed audit error with a stable classification."""

    def __init__(self, code: str, message: str):
        self.code = code
        super().__init__(f"{code}: {message}")


def _fail(code: str, message: str) -> None:
    raise AuditError(code, message)


def _nat(value: Any, label: str) -> int:
    if type(value) is not int or value < 0:
        _fail("E_NATURAL", f"{label} must be a nonnegative integer")
    return value


def _exact(value: Any, keys: set[str], label: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != keys:
        _fail("E_FIELDS", f"{label} fields differ from the frozen schema")
    return value


def _name(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value:
        _fail("E_NAME", f"{label} must be a nonempty string")
    return value


def _same(left: Any, right: Any) -> bool:
    """JSON equality that keeps bool distinct from integer values."""
    try:
        return json.dumps(left, sort_keys=True, separators=(",", ":"),
                          ensure_ascii=False, allow_nan=False) == json.dumps(
                              right, sort_keys=True, separators=(",", ":"),
                              ensure_ascii=False, allow_nan=False)
    except (TypeError, ValueError):
        return False


def _strict_json_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            _fail("E_JSON_DUPLICATE_KEY", f"duplicate JSON key {key!r}")
        result[key] = value
    return result


def _canonical_line(value: Any) -> bytes:
    try:
        return json.dumps(value, sort_keys=True, separators=(",", ":"),
                          ensure_ascii=False, allow_nan=False).encode("utf-8") + b"\n"
    except (TypeError, ValueError) as error:
        _fail("E_JSON", f"value is not canonical JSON: {error}")


def _load_rows(path: Path) -> list[Any]:
    try:
        raw = path.read_bytes()
    except OSError as error:
        _fail("E_FILE", f"cannot read vector file: {error}")
    if not raw or not raw.endswith(b"\n"):
        _fail("E_NDJSON", "vector file must be nonempty and end with newline")
    rows: list[Any] = []
    for number, line in enumerate(raw.splitlines(keepends=True), start=1):
        if line == b"\n":
            _fail("E_NDJSON", f"blank line at {number}")
        try:
            row = json.loads(line, object_pairs_hook=_strict_json_pairs,
                             parse_constant=lambda value: _fail("E_JSON", f"nonfinite value {value}"))
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            _fail("E_NDJSON", f"invalid JSON line {number}: {error}")
        if line != _canonical_line(row):
            _fail("E_NDJSON_CANONICAL", f"line {number} is not canonical JSON")
        rows.append(row)
    return rows


def _validate_named(term: Any, label: str = "named term") -> None:
    if not isinstance(term, list) or not term or not isinstance(term[0], str):
        _fail("E_NAMED_AST", f"{label} is not a tagged list")
    tag = term[0]
    arities = {"v": 2, "s": 1, "a": 3, "l": 4, "t": 5}
    if tag not in arities or len(term) != arities[tag]:
        _fail("E_NAMED_AST", f"{label} has an unknown tag or wrong arity")
    if tag == "v":
        _name(term[1], label + ".name")
    elif tag == "a":
        _validate_named(term[1], label + ".function")
        _validate_named(term[2], label + ".argument")
    elif tag == "l":
        _name(term[1], label + ".binder")
        _validate_named(term[2], label + ".domain")
        _validate_named(term[3], label + ".body")
    elif tag == "t":
        _name(term[1], label + ".binder")
        for field, child in zip(("type", "value", "body"), term[2:]):
            _validate_named(child, label + "." + field)


def _validate_db(term: Any, label: str = "de Bruijn term") -> None:
    if not isinstance(term, list) or not term or not isinstance(term[0], str):
        _fail("E_DB_AST", f"{label} is not a tagged list")
    tag = term[0]
    arities = {"b": 2, "s": 1, "a": 3, "l": 3, "t": 4}
    if tag not in arities or len(term) != arities[tag]:
        _fail("E_DB_AST", f"{label} has an unknown tag or wrong arity")
    if tag == "b":
        _nat(term[1], label + ".index")
    elif tag == "a":
        _validate_db(term[1], label + ".function")
        _validate_db(term[2], label + ".argument")
    elif tag == "l":
        _validate_db(term[1], label + ".domain")
        _validate_db(term[2], label + ".body")
    elif tag == "t":
        for field, child in zip(("type", "value", "body"), term[1:]):
            _validate_db(child, label + "." + field)


def _translate(term: Any, context: list[str], locals_near: tuple[str, ...] = ()) -> list[Any]:
    """Translate names with nearest lexical binder before external context."""
    _validate_named(term)
    tag = term[0]
    if tag == "s":
        return ["s"]
    if tag == "v":
        name = term[1]
        if name in locals_near:
            return ["b", locals_near.index(name)]
        try:
            return ["b", len(locals_near) + context.index(name)]
        except ValueError:
            _fail("E_OUT_OF_CONTEXT", f"free name {name!r} is absent from its context")
    if tag == "a":
        return ["a", _translate(term[1], context, locals_near),
                _translate(term[2], context, locals_near)]
    if tag == "l":
        binder = term[1]
        return ["l", _translate(term[2], context, locals_near),
                _translate(term[3], context, (binder,) + locals_near)]
    binder = term[1]
    return ["t", _translate(term[2], context, locals_near),
            _translate(term[3], context, locals_near),
            _translate(term[4], context, (binder,) + locals_near)]


def _scoped(term: Any, external_count: int, depth: int = 0) -> None:
    tag = term[0]
    if tag == "b":
        if term[1] >= external_count + depth:
            _fail("E_DB_SCOPE", "de Bruijn index escapes the declared context")
    elif tag == "a":
        _scoped(term[1], external_count, depth)
        _scoped(term[2], external_count, depth)
    elif tag == "l":
        _scoped(term[1], external_count, depth)
        _scoped(term[2], external_count, depth + 1)
    elif tag == "t":
        _scoped(term[1], external_count, depth)
        _scoped(term[2], external_count, depth)
        _scoped(term[3], external_count, depth + 1)


def _shift(term: list[Any], amount: int, cutoff: int = 0, depth: int = 0) -> list[Any]:
    tag = term[0]
    if tag == "b":
        index = term[1]
        if index >= cutoff + depth:
            moved = index + amount
            if moved < cutoff + depth:
                _fail("E_SHIFT_UNDERFLOW", "shift moved a variable below its cutoff")
            return ["b", moved]
        return ["b", index]
    if tag == "s":
        return ["s"]
    if tag == "a":
        return ["a", _shift(term[1], amount, cutoff, depth),
                _shift(term[2], amount, cutoff, depth)]
    if tag == "l":
        return ["l", _shift(term[1], amount, cutoff, depth),
                _shift(term[2], amount, cutoff, depth + 1)]
    return ["t", _shift(term[1], amount, cutoff, depth),
            _shift(term[2], amount, cutoff, depth),
            _shift(term[3], amount, cutoff, depth + 1)]


def _instantiate1(term: list[Any], arg: list[Any], depth: int = 0) -> list[Any]:
    tag = term[0]
    if tag == "b":
        index = term[1]
        if index == depth:
            return _shift(arg, depth)
        return ["b", index - 1] if index > depth else ["b", index]
    if tag == "s":
        return ["s"]
    if tag == "a":
        return ["a", _instantiate1(term[1], arg, depth),
                _instantiate1(term[2], arg, depth)]
    if tag == "l":
        return ["l", _instantiate1(term[1], arg, depth),
                _instantiate1(term[2], arg, depth + 1)]
    return ["t", _instantiate1(term[1], arg, depth),
            _instantiate1(term[2], arg, depth),
            _instantiate1(term[3], arg, depth + 1)]


class _SplitMix64:
    """Independent replay of the committed ordinal selection rule."""
    def __init__(self, ordinal: int):
        self.state = (SEED ^ ordinal) & MASK

    def choose(self, bound: int) -> int:
        if bound <= 0:
            _fail("E_REPLAY_RULE", "invalid deterministic draw bound")
        self.state = (self.state + 0x9E3779B97F4A7C15) & MASK
        z = self.state
        z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & MASK
        z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & MASK
        return ((z ^ (z >> 31)) & MASK) % bound


def _var(name: str) -> list[Any]:
    return ["v", name]


def _source_for(family: int, variant: int, context: list[str], rng: _SplitMix64) -> list[Any]:
    c0, c1, c2 = context[:3]
    tail = context[1 + rng.choose(len(context) - 1)]
    binder = c1 if family > 0 and variant % 2 == 0 else "x"
    other = c2 if variant % 3 == 0 else "y"
    if family == 0:
        return ["a", _var(c0), _var(tail)]
    if family == 1:
        return ["l", binder, ["s"], ["l", other, _var(c0), ["a", _var(c0), _var(binder)]]]
    if family == 2:
        return ["a", ["l", binder, _var(c0), ["a", _var(c0), _var(binder)]], _var(tail)]
    if family == 3:
        return ["t", binder, _var(c0), _var(tail), ["a", _var(c0), _var(binder)]]
    if family == 4:
        return ["l", binder, _var(c0), ["t", other, _var(c0), ["a", _var(tail), _var(c0)],
                                             ["a", ["a", _var(c0), _var(binder)], _var(other)]]]
    _fail("E_REPLAY_RULE", "ordinal family is outside 0..4")


def _replacement_for(context: list[str], variant: int, rng: _SplitMix64) -> list[Any]:
    if not context:
        return ["s"]
    primary = context[0]
    tail = context[rng.choose(len(context))]
    case = variant % 4
    if case == 0:
        return _var(primary)
    if case == 1:
        return ["a", _var(primary), _var(tail)]
    if case == 2:
        return ["l", "r", ["s"], ["a", _var(primary), _var("r")]]
    return ["t", "r", ["s"], _var(tail), ["a", _var(primary), _var("r")]]


def _replay_inputs(ordinal: int) -> dict[str, Any]:
    operation = OPERATIONS[ordinal // 2500]
    family = (ordinal % 2500) // 500
    variant = ordinal % 500
    rng = _SplitMix64(ordinal)
    context = [f"c{k}" for k in range(3 + rng.choose(4))]
    named_source = _source_for(family, variant, context, rng)
    args: list[list[Any]] = []
    contexts: list[list[str]] = []
    parameters: dict[str, int] = {}
    if operation in {"LIFT", "LIFT_COMPOSE"}:
        s1, d1 = rng.choose(len(context) + 1), rng.choose(3)
        c1 = context[:s1] + [f"j{ordinal}_1_{k}" for k in range(d1)] + context[s1:]
        contexts.append(c1)
        parameters = {"s": s1, "d": d1} if operation == "LIFT" else {"s1": s1, "d1": d1}
        if operation == "LIFT_COMPOSE":
            s2, d2 = rng.choose(len(c1) + 1), rng.choose(3)
            c2 = c1[:s2] + [f"j{ordinal}_2_{k}" for k in range(d2)] + c1[s2:]
            contexts.append(c2)
            parameters.update({"s2": s2, "d2": d2})
    else:
        first = _replacement_for(context[1:], variant, rng)
        args.append(first)
        contexts.append(context[1:])
        if operation == "SUBST_COMPOSE":
            second = _replacement_for(context[2:], variant // 4, rng)
            args.append(second)
            contexts.append(context[2:])
    return {"operation": operation, "family": family, "variant": variant,
            "context": context, "named_source": named_source,
            "named_arguments": args, "parameters": parameters,
            "contexts_after": contexts}


def audit_operation(*, operation: str, context: Any, named_source: Any, source: Any,
                    named_arguments: Any, arguments: Any, parameters: Any,
                    contexts_after: Any, named_expected: Any, expected: Any) -> None:
    """Check a standalone, non-corpus structural operation record.

    This primitive interface supports auditor unit fixtures without reserving
    any scientific ordinal. Corpus rows additionally pass deterministic input
    replay in :func:`audit_vector`.
    """
    if operation not in OPERATIONS:
        _fail("E_OPERATION", "unknown operation")
    if (not isinstance(context, list) or not all(isinstance(name, str) and name for name in context)
            or len(set(context)) != len(context)):
        _fail("E_CONTEXT", "context must contain unique nonempty names")
    if not isinstance(parameters, dict):
        _fail("E_PARAMETERS", "parameters must be an object")
    source_db = _validate_and_translate(named_source, source, context, "source")
    arg_count = {"LIFT": 0, "LIFT_COMPOSE": 0, "SUBST": 1, "SUBST_COMPOSE": 2}[operation]
    if not isinstance(named_arguments, list) or not isinstance(arguments, list) or len(arguments) != arg_count or len(named_arguments) != arg_count:
        _fail("E_ARGUMENTS", "named/de Bruijn argument counts do not match operation")
    arg_dbs = []
    for i, (named_arg, arg) in enumerate(zip(named_arguments, arguments)):
        arg_context = context[1:] if i == 0 else context[2:]
        arg_dbs.append(_validate_and_translate(named_arg, arg, arg_context, f"argument[{i}]"))

    step_count = 2 if operation in {"LIFT_COMPOSE", "SUBST_COMPOSE"} else 1
    if (not isinstance(contexts_after, list) or len(contexts_after) != step_count
            or not isinstance(named_expected, list) or len(named_expected) != step_count
            or not isinstance(expected, list) or len(expected) != step_count):
        _fail("E_EXPECTED", "context/result arrays have the wrong length")
    if operation == "LIFT":
        param_keys = {"s", "d"}
    elif operation == "LIFT_COMPOSE":
        param_keys = {"s1", "d1", "s2", "d2"}
    else:
        param_keys = set()
    if set(parameters) != param_keys:
        _fail("E_PARAMETERS", "parameter fields differ from operation contract")
    for key, value in parameters.items():
        _nat(value, "parameters." + key)

    current_context = context
    current_term = source_db
    for index in range(step_count):
        next_context = contexts_after[index]
        if (not isinstance(next_context, list)
                or not all(isinstance(name, str) and name for name in next_context)
                or len(set(next_context)) != len(next_context)):
            _fail("E_CONTEXT", f"contexts_after[{index}] is malformed")
        if operation in {"LIFT", "LIFT_COMPOSE"}:
            suffix = "" if operation == "LIFT" else str(index + 1)
            cutoff = parameters["s" + suffix]
            amount = parameters["d" + suffix]
            if cutoff > len(current_context) or len(next_context) != len(current_context) + amount:
                _fail("E_CONTEXT", "lift context has the wrong cutoff or length")
            inserted = next_context[cutoff:cutoff + amount]
            if (next_context[:cutoff] != current_context[:cutoff]
                    or next_context[cutoff + amount:] != current_context[cutoff:]
                    or set(inserted) & set(current_context)):
                _fail("E_CONTEXT", "lift context is not the declared fresh insertion")
            computed = _shift(current_term, amount, cutoff)
        else:
            wanted_context = context[1:] if index == 0 else context[2:]
            if next_context != wanted_context:
                _fail("E_CONTEXT", "substitution context is not the declared suffix")
            computed = _instantiate1(current_term, arg_dbs[index])
        translated = _validate_and_translate(named_expected[index], expected[index],
                                             next_context, f"expected[{index}]")
        if computed != translated:
            _fail("E_EXPECTATION", f"expected[{index}] disagrees with direct operation semantics")
        current_term = translated
        current_context = next_context


def _validate_and_translate(named: Any, db: Any, context: list[str], label: str) -> list[Any]:
    _validate_db(db, label)
    translated = _translate(named, context)
    if db != translated:
        _fail("E_TRANSLATION", f"{label} does not match independent named-to-index translation")
    _scoped(db, len(context))
    return db


def audit_vector(row: Any) -> dict[str, Any]:
    row = _exact(row, VECTOR_KEYS, "vector")
    ordinal = _nat(row["ordinal"], "ordinal")
    if ordinal >= COUNT:
        _fail("E_ORDINAL", "ordinal is outside the fixed suite")
    replay = _replay_inputs(ordinal)
    if row["id"] != f"bmp1-{ordinal:05d}":
        _fail("E_ID", "id does not match ordinal")
    for key in ("operation", "family", "variant", "context", "named_source", "named_arguments",
                "parameters", "contexts_after"):
        if not _same(row[key], replay[key]):
            _fail("E_REPLAY_MISMATCH", f"{key} does not match the frozen ordinal construction rule")

    audit_operation(operation=row["operation"], context=row["context"],
                    named_source=row["named_source"], source=row["source"],
                    named_arguments=row["named_arguments"], arguments=row["arguments"],
                    parameters=row["parameters"], contexts_after=row["contexts_after"],
                    named_expected=row["named_expected"], expected=row["expected"])
    return {"id": row["id"], "ordinal": ordinal, "status": "PASS"}


def _audit_corpus_rows(rows: Iterable[Any]) -> dict[str, Any]:
    seen: set[int] = set()
    seen_ids: set[str] = set()
    strata: Counter[tuple[str, int]] = Counter()
    capture_count = 0
    lift_cutoffs: dict[str, set[str]] = {"first": set(), "second": set()}
    lift_amounts: dict[str, set[int]] = {"first": set(), "second": set()}
    ordinals: list[int] = []
    for row in rows:
        result = audit_vector(row)
        ordinal = result["ordinal"]
        vector_id = result["id"]
        ordinals.append(ordinal)
        if vector_id in seen_ids:
            _fail("E_DUPLICATE_ID", f"id {vector_id} occurs more than once")
        seen.add(ordinal)
        seen_ids.add(vector_id)
        strata[(row["operation"], row["family"])] += 1
        if row["operation"] in {"SUBST", "SUBST_COMPOSE"}:
            if (row["family"] in {1, 2, 3, 4} and row["variant"] % 2 == 0
                    and "c1" in _free_names(row["named_arguments"][0])
                    and _has_binder(row["named_source"], "c1")):
                capture_count += 1
        if row["operation"] in {"LIFT", "LIFT_COMPOSE"}:
            parameters = row["parameters"]
            steps = 2 if row["operation"] == "LIFT_COMPOSE" else 1
            for step in range(1, steps + 1):
                label = "first" if step == 1 else "second"
                cutoff = parameters["s"] if steps == 1 else parameters[f"s{step}"]
                amount = parameters["d"] if steps == 1 else parameters[f"d{step}"]
                input_size = len(row["context"]) if step == 1 else len(row["contexts_after"][0])
                lift_cutoffs[label].add("zero" if cutoff == 0 else
                                        "end" if cutoff == input_size else "interior")
                lift_amounts[label].add(amount)
    _check_ordinals(ordinals)
    if seen != set(range(COUNT)):
        missing = sorted(set(range(COUNT)) - seen)
        extra = sorted(seen - set(range(COUNT)))
        _fail("E_COHORT", f"cohort ordinals differ; missing={missing[:3]} extra={extra[:3]}")
    expected_strata = {(operation, family): 500 for operation in OPERATIONS for family in range(5)}
    if strata != Counter(expected_strata):
        _fail("E_STRATA", "operation/family strata do not match the fixed 500-case layout")
    if capture_count != 2000:
        _fail("E_CAPTURE_COVERAGE", "expected the fixed 2,000 capture-collision vectors")
    for label in ("first", "second"):
        if lift_cutoffs[label] != {"zero", "interior", "end"} or lift_amounts[label] != {0, 1, 2}:
            _fail("E_LIFT_COVERAGE", f"{label} lifts omit a cutoff or increment boundary")
    return {"status": "PASS", "count": COUNT, "operation_family_strata": 20,
            "capture_collision_vectors": capture_count,
            "lift_cutoff_classes": {key: sorted(value) for key, value in lift_cutoffs.items()},
            "lift_increments": {key: sorted(value) for key, value in lift_amounts.items()}}


def _check_ordinals(ordinals: list[Any]) -> None:
    seen: set[int] = set()
    for position, value in enumerate(ordinals):
        ordinal = _nat(value, "ordinal")
        if ordinal >= COUNT:
            _fail("E_ORDINAL", "ordinal is outside the fixed suite")
        if ordinal in seen:
            _fail("E_DUPLICATE_ORDINAL", f"ordinal {ordinal} occurs more than once")
        if ordinal != position:
            _fail("E_ORDER", "vectors must appear in ascending ordinal order")
        seen.add(ordinal)
    if seen != set(range(COUNT)):
        _fail("E_COHORT", "cohort does not contain every ordinal exactly once")


def _free_names(term: Any, bound: tuple[str, ...] = ()) -> set[str]:
    tag = term[0]
    if tag == "s":
        return set()
    if tag == "v":
        return set() if term[1] in bound else {term[1]}
    if tag == "a":
        return _free_names(term[1], bound) | _free_names(term[2], bound)
    if tag == "l":
        return _free_names(term[2], bound) | _free_names(term[3], (term[1],) + bound)
    return (_free_names(term[2], bound) | _free_names(term[3], bound)
            | _free_names(term[4], (term[1],) + bound))


def _has_binder(term: Any, name: str) -> bool:
    tag = term[0]
    if tag == "l":
        return (term[1] == name or _has_binder(term[2], name)
                or _has_binder(term[3], name))
    if tag == "t":
        return (term[1] == name or _has_binder(term[2], name)
                or _has_binder(term[3], name) or _has_binder(term[4], name))
    if tag == "a":
        return _has_binder(term[1], name) or _has_binder(term[2], name)
    return False


def audit_corpus(path_or_rows: Path | str | Iterable[Any]) -> dict[str, Any]:
    """Audit canonical NDJSON or an iterable of already-decoded vector rows."""
    rows = _load_rows(Path(path_or_rows)) if isinstance(path_or_rows, (str, Path)) else path_or_rows
    return _audit_corpus_rows(rows)
