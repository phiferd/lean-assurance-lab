"""Deterministic derivation-directed generator for VALID-DEPENDENT-TERM-PILOT-1.

This module deliberately contains its own small semantic implementation.  The
independent auditor must not import any of the helpers in this file.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import math
from copy import deepcopy
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


DESIGN_PATH = Path("results/research/valid-dependent-term-pilot-1/design.json")
_TAGS = ("app", "bvar", "lam", "let", "pi", "sort")
_EXPR_KEYS = {
    "sort": frozenset(("level", "tag")),
    "bvar": frozenset(("index", "tag")),
    "pi": frozenset(("body", "domain", "tag")),
    "lam": frozenset(("body", "domain", "tag")),
    "app": frozenset(("argument", "function", "tag")),
    "let": frozenset(("body", "tag", "type", "value")),
}
_WITNESS_KEYS = {
    "sort": frozenset(("level", "result_level")),
    "bvar": frozenset(("index", "lookup_type")),
    "pi": frozenset(("body_level", "domain_level", "result_level")),
    "lam": frozenset(("body_type",)),
    "app": frozenset(
        (
            "argument_type",
            "argument_type_nf",
            "domain_nf",
            "function_type",
            "function_type_whnf",
            "result_type",
        )
    ),
    "let": frozenset(
        (
            "annotation_level",
            "annotation_nf",
            "body_type",
            "result_type",
            "value_type",
            "value_type_nf",
        )
    ),
}


class GenerationError(ValueError):
    """The frozen design or a generated candidate violated the contract."""


def _natural(value: Any, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise GenerationError(f"{label} must be a natural number")
    return value


def _reject_constant(value: str) -> None:
    raise GenerationError(f"non-finite JSON value is forbidden: {value}")


def _pairs_without_duplicates(pairs: Iterable[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise GenerationError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def canonical_bytes(obj: Any, newline: bool = False) -> bytes:
    """Return the design's canonical UTF-8 JSON representation."""
    if not isinstance(newline, bool):
        raise TypeError("newline must be a boolean")
    try:
        text = json.dumps(
            obj,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )
    except (TypeError, ValueError) as exc:
        raise GenerationError(f"value is not canonical JSON: {exc}") from exc
    if newline:
        text += "\n"
    return text.encode("utf-8")


def expr_hash(expr: Mapping[str, Any]) -> str:
    """Hash an embedded expression (canonical JSON without a newline)."""
    _validate_expr(expr)
    return hashlib.sha256(canonical_bytes(expr)).hexdigest()


def load_design(root: str | Path) -> dict[str, Any]:
    """Load and minimally bind the canonical design below ``root``."""
    path = Path(root) / DESIGN_PATH
    try:
        text = path.read_text(encoding="utf-8")
        design = json.loads(
            text,
            object_pairs_hook=_pairs_without_duplicates,
            parse_constant=_reject_constant,
        )
    except OSError as exc:
        raise GenerationError(f"cannot read design {path}: {exc}") from exc
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise GenerationError(f"invalid design JSON {path}: {exc}") from exc
    if not isinstance(design, dict):
        raise GenerationError("design must be a JSON object")
    _validate_design(design)
    return design


def _validate_design(design: Mapping[str, Any]) -> None:
    if design.get("design_id") != "valid-dependent-term-pilot-1.design.v1":
        raise GenerationError("unexpected dependent-term design id")
    if design.get("schema_version") != 1:
        raise GenerationError("unexpected dependent-term design schema")

    selection = design.get("deterministic_selection")
    if not isinstance(selection, Mapping):
        raise GenerationError("design lacks deterministic selection")
    preimage = selection.get("master_seed_preimage_ascii_no_newline")
    if not isinstance(preimage, str) or not preimage.isascii():
        raise GenerationError("master seed preimage must be ASCII")
    actual_master = hashlib.sha256(preimage.encode("ascii")).hexdigest()
    if actual_master != selection.get("master_seed_sha256"):
        raise GenerationError("master seed binding does not match its preimage")
    if selection.get("rng_version") != "hmac-sha256-rejection-v1":
        raise GenerationError("unsupported deterministic RNG version")
    if selection.get("expected_selection_attempt") != 0:
        raise GenerationError("frozen design must require selection attempt zero")

    case_contract = design.get("case_contract")
    if not isinstance(case_contract, Mapping):
        raise GenerationError("design lacks case contract")
    if case_contract.get("order") != ["pi", "lambda", "application", "let", "mixed"]:
        raise GenerationError("category order changed")
    if case_contract.get("count_per_category") != 10 or case_contract.get("total") != 50:
        raise GenerationError("case count changed")

    derivation = design.get("derivation_contract")
    if not isinstance(derivation, Mapping):
        raise GenerationError("design lacks derivation contract")
    shapes = derivation.get("witness_shapes")
    if not isinstance(shapes, Mapping):
        raise GenerationError("design lacks witness shapes")
    for rule, expected in _WITNESS_KEYS.items():
        actual = shapes.get(rule)
        if not isinstance(actual, list) or frozenset(actual) != expected or len(actual) != len(expected):
            raise GenerationError(f"witness shape changed for {rule}")

    metrics = design.get("metrics_contract")
    expected_metrics = {
        "ast_depth",
        "binder_depth",
        "constructor_counts",
        "maximum_derived_sort_level",
        "maximum_input_sort_level",
        "node_count",
        "normalized_type_nodes",
    }
    if not isinstance(metrics, Mapping) or set(metrics.get("exact_keys", ())) != expected_metrics:
        raise GenerationError("metrics contract changed")
    if set(metrics.get("constructor_count_exact_keys", ())) != set(_TAGS):
        raise GenerationError("constructor-count contract changed")


def _sort(level: int) -> dict[str, Any]:
    return {"tag": "sort", "level": _natural(level, "sort level")}


def _bvar(index: int) -> dict[str, Any]:
    return {"tag": "bvar", "index": _natural(index, "bound-variable index")}


def _pi(domain: Mapping[str, Any], body: Mapping[str, Any]) -> dict[str, Any]:
    return {"tag": "pi", "domain": dict(domain), "body": dict(body)}


def _lam(domain: Mapping[str, Any], body: Mapping[str, Any]) -> dict[str, Any]:
    return {"tag": "lam", "domain": dict(domain), "body": dict(body)}


def _app(function: Mapping[str, Any], argument: Mapping[str, Any]) -> dict[str, Any]:
    return {"tag": "app", "function": dict(function), "argument": dict(argument)}


def _let(
    annotation: Mapping[str, Any], value: Mapping[str, Any], body: Mapping[str, Any]
) -> dict[str, Any]:
    return {
        "tag": "let",
        "type": dict(annotation),
        "value": dict(value),
        "body": dict(body),
    }


def _validate_expr(expr: Any) -> None:
    if not isinstance(expr, Mapping):
        raise GenerationError("expression must be an object")
    tag = expr.get("tag")
    if tag not in _EXPR_KEYS or set(expr) != _EXPR_KEYS[tag]:
        raise GenerationError(f"invalid {tag!r} expression shape")
    if tag == "sort":
        _natural(expr["level"], "sort level")
    elif tag == "bvar":
        _natural(expr["index"], "bound-variable index")
    elif tag in ("pi", "lam"):
        _validate_expr(expr["domain"])
        _validate_expr(expr["body"])
    elif tag == "app":
        _validate_expr(expr["function"])
        _validate_expr(expr["argument"])
    else:
        _validate_expr(expr["type"])
        _validate_expr(expr["value"])
        _validate_expr(expr["body"])


def _shift(expr: Mapping[str, Any], amount: int, cutoff: int = 0) -> dict[str, Any]:
    amount = _natural(amount, "shift amount")
    cutoff = _natural(cutoff, "shift cutoff")
    tag = expr["tag"]
    if tag == "sort":
        return _sort(expr["level"])
    if tag == "bvar":
        index = expr["index"]
        return _bvar(index + amount if index >= cutoff else index)
    if tag == "pi":
        return _pi(
            _shift(expr["domain"], amount, cutoff),
            _shift(expr["body"], amount, cutoff + 1),
        )
    if tag == "lam":
        return _lam(
            _shift(expr["domain"], amount, cutoff),
            _shift(expr["body"], amount, cutoff + 1),
        )
    if tag == "app":
        return _app(
            _shift(expr["function"], amount, cutoff),
            _shift(expr["argument"], amount, cutoff),
        )
    if tag == "let":
        return _let(
            _shift(expr["type"], amount, cutoff),
            _shift(expr["value"], amount, cutoff),
            _shift(expr["body"], amount, cutoff + 1),
        )
    raise GenerationError(f"cannot shift unknown expression tag {tag!r}")


def _subst(
    expr: Mapping[str, Any], value: Mapping[str, Any], depth: int = 0
) -> dict[str, Any]:
    depth = _natural(depth, "substitution depth")
    tag = expr["tag"]
    if tag == "sort":
        return _sort(expr["level"])
    if tag == "bvar":
        index = expr["index"]
        if index < depth:
            return _bvar(index)
        if index == depth:
            return _shift(value, depth, 0)
        return _bvar(index - 1)
    if tag == "pi":
        return _pi(
            _subst(expr["domain"], value, depth),
            _subst(expr["body"], value, depth + 1),
        )
    if tag == "lam":
        return _lam(
            _subst(expr["domain"], value, depth),
            _subst(expr["body"], value, depth + 1),
        )
    if tag == "app":
        return _app(
            _subst(expr["function"], value, depth),
            _subst(expr["argument"], value, depth),
        )
    if tag == "let":
        return _let(
            _subst(expr["type"], value, depth),
            _subst(expr["value"], value, depth),
            _subst(expr["body"], value, depth + 1),
        )
    raise GenerationError(f"cannot substitute unknown expression tag {tag!r}")


class _ReductionBudget:
    def __init__(self, fuel: int = 100_000) -> None:
        self.fuel = fuel

    def spend(self) -> None:
        self.fuel -= 1
        if self.fuel < 0:
            raise GenerationError("beta-zeta normalization exhausted its fuel")


def _whnf(expr: Mapping[str, Any], budget: _ReductionBudget | None = None) -> dict[str, Any]:
    budget = budget or _ReductionBudget()
    budget.spend()
    tag = expr["tag"]
    if tag == "let":
        return _whnf(_subst(expr["body"], expr["value"], 0), budget)
    if tag == "app":
        function = _whnf(expr["function"], budget)
        if function["tag"] == "lam":
            return _whnf(_subst(function["body"], expr["argument"], 0), budget)
        return _app(function, expr["argument"])
    return deepcopy(dict(expr))


def _normalize(expr: Mapping[str, Any], budget: _ReductionBudget | None = None) -> dict[str, Any]:
    budget = budget or _ReductionBudget()
    budget.spend()
    tag = expr["tag"]
    if tag == "sort":
        return _sort(expr["level"])
    if tag == "bvar":
        return _bvar(expr["index"])
    if tag == "pi":
        return _pi(_normalize(expr["domain"], budget), _normalize(expr["body"], budget))
    if tag == "lam":
        return _lam(_normalize(expr["domain"], budget), _normalize(expr["body"], budget))
    if tag == "let":
        value = _normalize(expr["value"], budget)
        return _normalize(_subst(expr["body"], value, 0), budget)
    if tag == "app":
        function = _normalize(expr["function"], budget)
        argument = _normalize(expr["argument"], budget)
        if function["tag"] == "lam":
            return _normalize(_subst(function["body"], argument, 0), budget)
        return _app(function, argument)
    raise GenerationError(f"cannot normalize unknown expression tag {tag!r}")


def _sort_level(expr_type: Mapping[str, Any]) -> int:
    head = _whnf(expr_type)
    if head["tag"] != "sort":
        raise GenerationError("expected a sort-valued expression")
    return head["level"]


def _derivation(
    context: Sequence[Mapping[str, Any]],
    premises: Sequence[Mapping[str, Any]],
    rule: str,
    term: Mapping[str, Any],
    expr_type: Mapping[str, Any],
    witness: Mapping[str, Any],
) -> dict[str, Any]:
    if frozenset(witness) != _WITNESS_KEYS[rule]:
        raise GenerationError(f"internal witness shape error for {rule}")
    return {
        "context": deepcopy(list(context)),
        "premises": deepcopy(list(premises)),
        "rule": rule,
        "term": deepcopy(dict(term)),
        "type": deepcopy(dict(expr_type)),
        "witness": deepcopy(dict(witness)),
    }


def _infer(
    term: Mapping[str, Any], context: Sequence[Mapping[str, Any]] = ()
) -> dict[str, Any]:
    _validate_expr(term)
    tag = term["tag"]
    if tag == "sort":
        level = term["level"]
        expr_type = _sort(level + 1)
        return _derivation(
            context,
            (),
            "sort",
            term,
            expr_type,
            {"level": level, "result_level": level + 1},
        )
    if tag == "bvar":
        index = term["index"]
        if index >= len(context):
            raise GenerationError(f"loose bound variable {index} in context of size {len(context)}")
        lookup_type = _shift(context[index], index + 1, 0)
        return _derivation(
            context,
            (),
            "bvar",
            term,
            lookup_type,
            {"index": index, "lookup_type": lookup_type},
        )
    if tag == "pi":
        domain = _infer(term["domain"], context)
        domain_level = _sort_level(domain["type"])
        body = _infer(term["body"], (term["domain"], *context))
        body_level = _sort_level(body["type"])
        result_level = 0 if body_level == 0 else max(domain_level, body_level)
        expr_type = _sort(result_level)
        return _derivation(
            context,
            (domain, body),
            "pi",
            term,
            expr_type,
            {
                "domain_level": domain_level,
                "body_level": body_level,
                "result_level": result_level,
            },
        )
    if tag == "lam":
        domain = _infer(term["domain"], context)
        _sort_level(domain["type"])
        body = _infer(term["body"], (term["domain"], *context))
        expr_type = _pi(term["domain"], body["type"])
        return _derivation(
            context,
            (domain, body),
            "lam",
            term,
            expr_type,
            {"body_type": body["type"]},
        )
    if tag == "app":
        function = _infer(term["function"], context)
        function_type = function["type"]
        function_type_whnf = _whnf(function_type)
        if function_type_whnf["tag"] != "pi":
            raise GenerationError("application function type is not a Pi after beta-zeta WHNF")
        argument = _infer(term["argument"], context)
        argument_type = argument["type"]
        domain_nf = _normalize(function_type_whnf["domain"])
        argument_type_nf = _normalize(argument_type)
        if domain_nf != argument_type_nf:
            raise GenerationError("application argument does not have the function domain type")
        result_type = _subst(function_type_whnf["body"], term["argument"], 0)
        return _derivation(
            context,
            (function, argument),
            "app",
            term,
            result_type,
            {
                "function_type": function_type,
                "function_type_whnf": function_type_whnf,
                "argument_type": argument_type,
                "domain_nf": domain_nf,
                "argument_type_nf": argument_type_nf,
                "result_type": result_type,
            },
        )
    if tag == "let":
        annotation = _infer(term["type"], context)
        annotation_level = _sort_level(annotation["type"])
        value = _infer(term["value"], context)
        value_type = value["type"]
        annotation_nf = _normalize(term["type"])
        value_type_nf = _normalize(value_type)
        if annotation_nf != value_type_nf:
            raise GenerationError("let value does not have its annotation type")
        body = _infer(term["body"], (term["type"], *context))
        result_type = _subst(body["type"], term["value"], 0)
        return _derivation(
            context,
            (annotation, value, body),
            "let",
            term,
            result_type,
            {
                "annotation_level": annotation_level,
                "value_type": value_type,
                "annotation_nf": annotation_nf,
                "value_type_nf": value_type_nf,
                "body_type": body["type"],
                "result_type": result_type,
            },
        )
    raise GenerationError(f"cannot infer unknown expression tag {tag!r}")


class _BlockRng:
    """The frozen HMAC block stream with unbiased ``randbelow``."""

    def __init__(self, attempt_seed: bytes) -> None:
        if len(attempt_seed) != 32:
            raise GenerationError("attempt seed must contain 32 bytes")
        self._key = attempt_seed
        self._block_index = 0
        self._words: list[int] = []

    def _refill(self) -> None:
        message = b"block\x00" + self._block_index.to_bytes(8, "big")
        block = hmac.new(self._key, message, hashlib.sha256).digest()
        self._block_index += 1
        self._words.extend(int.from_bytes(block[index : index + 8], "big") for index in range(0, 32, 8))

    def randbelow(self, upper: int) -> int:
        if isinstance(upper, bool) or not isinstance(upper, int) or upper <= 0:
            raise GenerationError("randbelow upper bound must be positive")
        limit = (1 << 64) - ((1 << 64) % upper)
        while True:
            if not self._words:
                self._refill()
            word = self._words.pop(0)
            if word < limit:
                return word % upper


def _case_seed(design: Mapping[str, Any], category: str, slot: int) -> bytes:
    selection = design["deterministic_selection"]
    master = bytes.fromhex(selection["master_seed_sha256"])
    message = category.encode("utf-8") + b"\x00" + slot.to_bytes(2, "big")
    return hmac.new(master, message, hashlib.sha256).digest()


def _attempt_rng(case_seed: bytes, attempt: int) -> _BlockRng:
    message = b"attempt\x00" + attempt.to_bytes(8, "big")
    return _BlockRng(hmac.new(case_seed, message, hashlib.sha256).digest())


def _split_odd(total: int, left_min: int, right_min: int, rng: _BlockRng) -> tuple[int, int]:
    choices = [
        left
        for left in range(left_min, total - right_min + 1)
        if left % 2 == 1 and (total - left) % 2 == 1
    ]
    if not choices:
        raise GenerationError("cannot split node budget into odd subexpressions")
    choices.sort(key=lambda left: (abs(left - (total - left)), left))
    # Choosing the uniquely most balanced split is what makes every frozen
    # slot constructive on attempt zero, including the 47-node mixed case.
    # The RNG word is still consumed so later leaf-level choices remain bound
    # to the specified block stream rather than to Python traversal accidents.
    balanced = choices[:1]
    left = balanced[rng.randbelow(len(balanced))]
    return left, total - left


def _input_level(design: Mapping[str, Any], rng: _BlockRng) -> int:
    levels = design["size_policy"]["input_sort_levels"]
    minimum = _natural(levels["minimum"], "minimum input sort level")
    maximum = _natural(levels["maximum"], "maximum input sort level")
    if maximum < minimum:
        raise GenerationError("input sort-level range is empty")
    return minimum + rng.randbelow(maximum - minimum + 1)


def _closed_type(nodes: int, design: Mapping[str, Any], rng: _BlockRng) -> dict[str, Any]:
    """Build a closed sort-valued expression with an odd node count."""
    if nodes < 1 or nodes % 2 != 1:
        raise GenerationError("closed type node budget must be positive and odd")
    if nodes == 1:
        return _sort(_input_level(design, rng))
    left, right = _split_odd(nodes - 1, 1, 1, rng)
    return _pi(_closed_type(left, design, rng), _closed_type(right, design, rng))


def _closed_prop(nodes: int, design: Mapping[str, Any], rng: _BlockRng) -> dict[str, Any]:
    """Build a closed expression whose inferred type is ``Sort 0``."""
    if nodes < 3 or nodes % 2 != 1:
        raise GenerationError("closed proposition node budget must be odd and at least three")
    if nodes == 3:
        return _pi(_sort(0), _bvar(0))
    domain_nodes, body_nodes = _split_odd(nodes - 1, 1, 3, rng)
    return _pi(
        _closed_type(domain_nodes, design, rng),
        _closed_prop(body_nodes, design, rng),
    )


def _dependent_prop_body(
    nodes: int, design: Mapping[str, Any], rng: _BlockRng
) -> dict[str, Any]:
    """Build a proposition under ``x : Sort 0`` that refers to ``x``."""
    if nodes < 1 or nodes % 2 != 1:
        raise GenerationError("dependent body node budget must be positive and odd")
    if nodes == 1:
        return _bvar(0)
    return _pi(_closed_type(nodes - 2, design, rng), _bvar(1))


def _band_for_slot(design: Mapping[str, Any], slot: int) -> Mapping[str, Any]:
    matches = [band for band in design["size_policy"]["bands"] if slot in band["slots_zero_based"]]
    if len(matches) != 1:
        raise GenerationError(f"slot {slot} does not have exactly one size band")
    return matches[0]


def _target_nodes(design: Mapping[str, Any], category: str, slot: int) -> int:
    band = _band_for_slot(design, slot)
    lower = max(band["minimum_nodes"], design["size_policy"]["category_minimum_nodes"][category])
    upper = band["maximum_nodes"]
    parity = 0 if category == "let" else 1
    eligible = [nodes for nodes in range(lower, upper + 1) if nodes % 2 == parity]
    slots = band["slots_zero_based"]
    local = slots.index(slot)
    if not eligible:
        raise GenerationError(f"no eligible node count for {category} slot {slot}")
    if len(slots) == 1:
        return eligible[0]
    index = local * (len(eligible) - 1) // (len(slots) - 1)
    return eligible[index]


def _candidate_term(
    design: Mapping[str, Any], category: str, slot: int, rng: _BlockRng
) -> dict[str, Any]:
    target = _target_nodes(design, category, slot)
    if category == "pi":
        return _pi(_sort(0), _dependent_prop_body(target - 2, design, rng))
    if category == "lambda":
        return _lam(_sort(0), _dependent_prop_body(target - 2, design, rng))
    if category == "application":
        body_nodes, argument_nodes = _split_odd(target - 3, 1, 3, rng)
        return _app(
            _lam(_sort(0), _dependent_prop_body(body_nodes, design, rng)),
            _closed_prop(argument_nodes, design, rng),
        )
    if category == "let":
        value_nodes, body_nodes = _split_odd(target - 2, 3, 1, rng)
        return _let(
            _sort(0),
            _closed_prop(value_nodes, design, rng),
            _dependent_prop_body(body_nodes, design, rng),
        )
    if category == "mixed":
        # Keep the lambda-side binder chain shallow and place the remaining
        # size budget in the outer closed proposition.  This makes the frozen
        # 47-node slot satisfy both depth limits on its first attempt.
        lambda_sizes = [nodes for nodes in (1, 3, 5) if nodes <= target - 12]
        lambda_body_nodes = lambda_sizes[rng.randbelow(len(lambda_sizes))]
        value_nodes = target - 9 - lambda_body_nodes
        inner_application = _app(
            _lam(_sort(0), _dependent_prop_body(lambda_body_nodes, design, rng)),
            _bvar(0),
        )
        inner_let = _let(_sort(0), _bvar(0), inner_application)
        return _let(_sort(0), _closed_prop(value_nodes, design, rng), inner_let)
    raise GenerationError(f"unknown generation category {category!r}")


def _children(expr: Mapping[str, Any]) -> tuple[Mapping[str, Any], ...]:
    tag = expr["tag"]
    if tag in ("sort", "bvar"):
        return ()
    if tag in ("pi", "lam"):
        return (expr["domain"], expr["body"])
    if tag == "app":
        return (expr["function"], expr["argument"])
    return (expr["type"], expr["value"], expr["body"])


def _node_count(expr: Mapping[str, Any]) -> int:
    return 1 + sum(_node_count(child) for child in _children(expr))


def _ast_depth(expr: Mapping[str, Any]) -> int:
    children = _children(expr)
    return 1 if not children else 1 + max(_ast_depth(child) for child in children)


def _binder_depth(expr: Mapping[str, Any], current: int = 0) -> int:
    tag = expr["tag"]
    if tag in ("sort", "bvar"):
        return current
    if tag in ("pi", "lam"):
        return max(
            _binder_depth(expr["domain"], current),
            _binder_depth(expr["body"], current + 1),
        )
    if tag == "app":
        return max(
            _binder_depth(expr["function"], current),
            _binder_depth(expr["argument"], current),
        )
    return max(
        _binder_depth(expr["type"], current),
        _binder_depth(expr["value"], current),
        _binder_depth(expr["body"], current + 1),
    )


def _constructor_counts(expr: Mapping[str, Any]) -> dict[str, int]:
    counts = {tag: 0 for tag in _TAGS}

    def visit(node: Mapping[str, Any]) -> None:
        counts[node["tag"]] += 1
        for child in _children(node):
            visit(child)

    visit(expr)
    return counts


def _maximum_sort_level(expr: Mapping[str, Any]) -> int:
    values = [expr["level"]] if expr["tag"] == "sort" else []
    values.extend(_maximum_sort_level(child) for child in _children(expr))
    return max(values, default=0)


def _uses_binder(expr: Mapping[str, Any], target_index: int = 0) -> bool:
    tag = expr["tag"]
    if tag == "bvar":
        return expr["index"] == target_index
    if tag == "sort":
        return False
    if tag in ("pi", "lam"):
        return _uses_binder(expr["domain"], target_index) or _uses_binder(
            expr["body"], target_index + 1
        )
    if tag == "app":
        return _uses_binder(expr["function"], target_index) or _uses_binder(
            expr["argument"], target_index
        )
    return (
        _uses_binder(expr["type"], target_index)
        or _uses_binder(expr["value"], target_index)
        or _uses_binder(expr["body"], target_index + 1)
    )


def _has_using_binder(expr: Mapping[str, Any], binder_tag: str) -> bool:
    if expr["tag"] == binder_tag and _uses_binder(expr["body"], 0):
        return True
    return any(_has_using_binder(child, binder_tag) for child in _children(expr))


def _has_beta_redex(expr: Mapping[str, Any]) -> bool:
    if expr["tag"] == "app" and expr["function"]["tag"] == "lam":
        return True
    return any(_has_beta_redex(child) for child in _children(expr))


def _has_active_zeta(expr: Mapping[str, Any]) -> bool:
    if expr["tag"] == "let" and _uses_binder(expr["body"], 0):
        return True
    return any(_has_active_zeta(child) for child in _children(expr))


def _matches_category(expr: Mapping[str, Any], category: str) -> bool:
    counts = _constructor_counts(expr)
    if category == "pi":
        return (
            expr["tag"] == "pi"
            and counts["lam"] == counts["app"] == counts["let"] == 0
            and _has_using_binder(expr, "pi")
        )
    if category == "lambda":
        return (
            expr["tag"] == "lam"
            and counts["app"] == counts["let"] == 0
            and _has_using_binder(expr, "lam")
        )
    if category == "application":
        return (
            expr["tag"] == "app"
            and counts["let"] == 0
            and counts["lam"] > 0
            and _has_beta_redex(expr)
        )
    if category == "let":
        return expr["tag"] == "let" and counts["app"] == 0 and _has_using_binder(expr, "let")
    if category == "mixed":
        return (
            expr["tag"] == "let"
            and all(counts[tag] > 0 for tag in ("pi", "lam", "app", "let"))
            and _has_beta_redex(expr)
            and _has_active_zeta(expr)
        )
    return False


def _metrics(term: Mapping[str, Any], expected_type_nf: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "ast_depth": _ast_depth(term),
        "binder_depth": _binder_depth(term),
        "constructor_counts": _constructor_counts(term),
        "maximum_derived_sort_level": _maximum_sort_level(expected_type_nf),
        "maximum_input_sort_level": _maximum_sort_level(term),
        "node_count": _node_count(term),
        "normalized_type_nodes": _node_count(expected_type_nf),
    }


def _satisfies_policy(
    design: Mapping[str, Any], category: str, slot: int, term: Mapping[str, Any], metrics: Mapping[str, Any]
) -> bool:
    if not _matches_category(term, category):
        return False
    policy = design["size_policy"]
    band = _band_for_slot(design, slot)
    nodes = metrics["node_count"]
    return (
        nodes >= policy["category_minimum_nodes"][category]
        and band["minimum_nodes"] <= nodes <= band["maximum_nodes"]
        and metrics["ast_depth"] <= policy["maximum_ast_depth"]
        and metrics["binder_depth"] <= policy["maximum_binder_depth"]
        and metrics["maximum_input_sort_level"] <= policy["input_sort_levels"]["maximum"]
        and metrics["maximum_derived_sort_level"] <= policy["maximum_derived_sort_level"]
        and metrics["normalized_type_nodes"] <= policy["maximum_normalized_type_nodes"]
    )


def _generate_case(
    design: Mapping[str, Any], category: str, slot: int, used_hashes: set[str]
) -> dict[str, Any]:
    _validate_design(design)
    order = design["case_contract"]["order"]
    if category not in order:
        raise GenerationError(f"unknown category {category!r}")
    if isinstance(slot, bool) or not isinstance(slot, int) or not 0 <= slot < 10:
        raise GenerationError("slot must be an integer from zero through nine")
    case_seed = _case_seed(design, category, slot)
    attempt = design["deterministic_selection"]["expected_selection_attempt"]
    rng = _attempt_rng(case_seed, attempt)
    term = _candidate_term(design, category, slot, rng)
    derivation = _infer(term)
    expected_type_nf = _normalize(derivation["type"])
    metrics = _metrics(term, expected_type_nf)
    term_sha256 = expr_hash(term)
    if not _satisfies_policy(design, category, slot, term, metrics):
        raise GenerationError(f"constructive attempt zero is ineligible for {category} slot {slot}")
    if term_sha256 in used_hashes:
        raise GenerationError(f"constructive attempt zero is not unique for {category} slot {slot}")
    case = {
        "case_id": f"vdtp1-{category}-{slot + 1:02d}",
        "case_seed_sha256": case_seed.hex(),
        "category": category,
        "category_index": slot + 1,
        "derivation": derivation,
        "expected_type_nf": expected_type_nf,
        "metrics": metrics,
        "schema_version": 1,
        "selection_attempt": attempt,
        "term": term,
    }
    if set(case) != set(design["case_contract"]["exact_keys"]):
        raise GenerationError("generated case keys differ from the frozen contract")
    return case


def generate_case(
    design: Mapping[str, Any], category: str, zero_based_slot: int
) -> dict[str, Any]:
    """Generate the first valid deterministic candidate for one category slot."""
    return _generate_case(design, category, zero_based_slot, set())


def generate_all(design: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Generate the exact ordered 50-case suite without writing it anywhere."""
    _validate_design(design)
    cases: list[dict[str, Any]] = []
    used_hashes: set[str] = set()
    for category in design["case_contract"]["order"]:
        for slot in range(design["case_contract"]["count_per_category"]):
            case = _generate_case(design, category, slot, used_hashes)
            used_hashes.add(expr_hash(case["term"]))
            cases.append(case)
    if len(cases) != design["case_contract"]["total"]:
        raise GenerationError("generated case count differs from frozen total")
    if len(used_hashes) != design["case_contract"]["distinct_term_hashes"]:
        raise GenerationError("generated terms are not all distinct")
    return cases


def _render_expr(expr: Mapping[str, Any], environment: Sequence[str] = ()) -> str:
    tag = expr["tag"]
    if tag == "sort":
        return f"Sort {expr['level']}"
    if tag == "bvar":
        index = expr["index"]
        if index >= len(environment):
            raise GenerationError("cannot render a loose bound variable")
        return environment[index]
    if tag in ("pi", "lam"):
        name = f"x{len(environment)}"
        domain = _render_expr(expr["domain"], environment)
        body = _render_expr(expr["body"], (name, *environment))
        if tag == "pi":
            return f"(forall ({name} : {domain}), {body})"
        return f"(fun ({name} : {domain}) => {body})"
    if tag == "app":
        return f"({_render_expr(expr['function'], environment)} {_render_expr(expr['argument'], environment)})"
    if tag == "let":
        name = f"x{len(environment)}"
        annotation = _render_expr(expr["type"], environment)
        value = _render_expr(expr["value"], environment)
        body = _render_expr(expr["body"], (name, *environment))
        return f"(let {name} : {annotation} := {value}; {body})"
    raise GenerationError(f"cannot render unknown expression tag {tag!r}")


def render_module(cases: Sequence[Mapping[str, Any]]) -> str:
    """Render cases as the single frozen Lean source module."""
    if not cases:
        raise GenerationError("cannot render an empty case sequence")
    seen: set[str] = set()
    lines = [
        "-- Generated by generate-valid-dependent-term-pilot-1.",
        "-- Development output is not a frozen scientific cohort.",
        "namespace ValidDependentTermPilot1",
        "",
    ]
    for case in cases:
        case_id = case.get("case_id")
        category = case.get("category")
        index = case.get("category_index")
        if not isinstance(case_id, str) or case_id in seen:
            raise GenerationError("case ids must be unique strings")
        if category not in ("pi", "lambda", "application", "let", "mixed"):
            raise GenerationError("cannot render a case with an unknown category")
        if isinstance(index, bool) or not isinstance(index, int) or not 1 <= index <= 10:
            raise GenerationError("cannot render a case with an invalid category index")
        expected_id = f"vdtp1-{category}-{index:02d}"
        if case_id != expected_id:
            raise GenerationError("case id does not match category and index")
        seen.add(case_id)
        declaration = f"{category}{index:02d}"
        term = _render_expr(case["term"])
        expr_type = _render_expr(case["expected_type_nf"])
        lines.append(f"-- {case_id}; term-sha256 {expr_hash(case['term'])}")
        lines.append(f"def {declaration} : {expr_type} := {term}")
        lines.append("")
    lines.append("end ValidDependentTermPilot1")
    return "\n".join(lines) + "\n"


__all__ = [
    "canonical_bytes",
    "expr_hash",
    "generate_all",
    "generate_case",
    "load_design",
    "render_module",
]
