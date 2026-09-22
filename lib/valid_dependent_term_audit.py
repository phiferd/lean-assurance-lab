"""Independent auditor for VALID-DEPENDENT-TERM-PILOT-1.

This module intentionally shares no semantic implementation with the generator.
It accepts only the six-constructor JSON language frozen in the pilot design and
recomputes typing, normalization, category, size, seed, and derivation facts.
"""
from __future__ import annotations

import copy
import hashlib
import hmac
import json
from pathlib import Path
import re
from typing import Any, Iterable


CASE_KEYS = {
    "case_id", "case_seed_sha256", "category", "category_index", "derivation",
    "expected_type_nf", "metrics", "schema_version", "selection_attempt", "term",
}
DERIVATION_KEYS = {"context", "premises", "rule", "term", "type", "witness"}
TAGS = ("sort", "bvar", "pi", "lam", "app", "let")
METRIC_KEYS = {
    "ast_depth", "binder_depth", "constructor_counts", "maximum_derived_sort_level",
    "maximum_input_sort_level", "node_count", "normalized_type_nodes",
}
HEX64 = re.compile(r"[0-9a-f]{64}\Z")
NORMALIZATION_FUEL = 100_000
NORMALIZATION_NODE_LIMIT = 4_096


class AuditError(ValueError):
    """Fail-closed audit error with a stable machine-readable classification."""

    def __init__(self, code: str, message: str):
        self.code = code
        super().__init__(f"{code}: {message}")


def _fail(code: str, message: str) -> None:
    raise AuditError(code, message)


def _natural(value: Any, label: str) -> int:
    if type(value) is not int or value < 0:
        _fail("E_NATURAL", f"{label} must be a natural number")
    return value


def _exact(value: Any, keys: set[str], code: str, label: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != keys:
        _fail(code, f"{label} keys differ")
    return value


def _canonical(value: Any) -> bytes:
    try:
        return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
                          allow_nan=False).encode("utf-8")
    except (TypeError, ValueError) as error:
        _fail("E_JSON_VALUE", f"value is not canonical JSON: {error}")


def _digest(value: Any) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _same(left: Any, right: Any) -> bool:
    """JSON equality that does not conflate booleans with integers."""
    return _canonical(left) == _canonical(right)


def _pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            _fail("E_DUPLICATE_KEY", f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _nonfinite(value: str) -> None:
    _fail("E_JSON_VALUE", f"non-finite JSON number: {value}")


def _load_strict(path: Path) -> tuple[Any, bytes]:
    if not path.is_file() or path.is_symlink():
        _fail("E_FILE", f"case path is absent, non-file, or symlink: {path}")
    try:
        raw = path.read_bytes()
    except OSError as error:
        _fail("E_FILE", f"cannot read {path}: {error}")
    if not raw.endswith(b"\n") or raw.endswith(b"\n\n"):
        _fail("E_CANONICAL_JSON", "case file must have exactly one terminal newline")
    try:
        text = raw.decode("utf-8")
        value = json.loads(text, object_pairs_hook=_pairs, parse_constant=_nonfinite)
    except UnicodeDecodeError as error:
        _fail("E_CANONICAL_JSON", f"case file is not UTF-8: {error}")
    except json.JSONDecodeError as error:
        _fail("E_CANONICAL_JSON", f"case file is not JSON: {error}")
    if raw != _canonical(value) + b"\n":
        _fail("E_CANONICAL_JSON", "case file bytes are not canonical")
    return value, raw


def _validate_expr(expr: Any, maximum_level: int, label: str = "expression") -> dict[str, Any]:
    if not isinstance(expr, dict) or not isinstance(expr.get("tag"), str):
        _fail("E_AST", f"{label} is not a tagged object")
    tag = expr["tag"]
    if tag == "sort":
        _exact(expr, {"tag", "level"}, "E_AST_KEYS", label)
        level = _natural(expr["level"], f"{label}.level")
        if level > maximum_level:
            _fail("E_SORT_LEVEL", f"{label}.level exceeds {maximum_level}")
    elif tag == "bvar":
        _exact(expr, {"tag", "index"}, "E_AST_KEYS", label)
        _natural(expr["index"], f"{label}.index")
    elif tag in {"pi", "lam"}:
        _exact(expr, {"tag", "domain", "body"}, "E_AST_KEYS", label)
        _validate_expr(expr["domain"], maximum_level, label + ".domain")
        _validate_expr(expr["body"], maximum_level, label + ".body")
    elif tag == "app":
        _exact(expr, {"tag", "function", "argument"}, "E_AST_KEYS", label)
        _validate_expr(expr["function"], maximum_level, label + ".function")
        _validate_expr(expr["argument"], maximum_level, label + ".argument")
    elif tag == "let":
        _exact(expr, {"tag", "type", "value", "body"}, "E_AST_KEYS", label)
        _validate_expr(expr["type"], maximum_level, label + ".type")
        _validate_expr(expr["value"], maximum_level, label + ".value")
        _validate_expr(expr["body"], maximum_level, label + ".body")
    else:
        _fail("E_AST_TAG", f"{label} uses excluded tag {tag!r}")
    return expr


def _shift(expr: dict[str, Any], amount: int, cutoff: int = 0) -> dict[str, Any]:
    tag = expr["tag"]
    if tag == "sort":
        return copy.deepcopy(expr)
    if tag == "bvar":
        index = expr["index"]
        return {"tag": "bvar", "index": index + amount if index >= cutoff else index}
    if tag in {"pi", "lam"}:
        return {"tag": tag, "domain": _shift(expr["domain"], amount, cutoff),
                "body": _shift(expr["body"], amount, cutoff + 1)}
    if tag == "app":
        return {"tag": "app", "function": _shift(expr["function"], amount, cutoff),
                "argument": _shift(expr["argument"], amount, cutoff)}
    if tag == "let":
        return {"tag": "let", "type": _shift(expr["type"], amount, cutoff),
                "value": _shift(expr["value"], amount, cutoff),
                "body": _shift(expr["body"], amount, cutoff + 1)}
    _fail("E_AST_TAG", f"cannot shift tag {tag!r}")


def _subst(expr: dict[str, Any], value: dict[str, Any], depth: int = 0) -> dict[str, Any]:
    tag = expr["tag"]
    if tag == "sort":
        return copy.deepcopy(expr)
    if tag == "bvar":
        index = expr["index"]
        if index < depth:
            return copy.deepcopy(expr)
        if index == depth:
            return _shift(value, depth, 0)
        return {"tag": "bvar", "index": index - 1}
    if tag in {"pi", "lam"}:
        return {"tag": tag, "domain": _subst(expr["domain"], value, depth),
                "body": _subst(expr["body"], value, depth + 1)}
    if tag == "app":
        return {"tag": "app", "function": _subst(expr["function"], value, depth),
                "argument": _subst(expr["argument"], value, depth)}
    if tag == "let":
        return {"tag": "let", "type": _subst(expr["type"], value, depth),
                "value": _subst(expr["value"], value, depth),
                "body": _subst(expr["body"], value, depth + 1)}
    _fail("E_AST_TAG", f"cannot substitute tag {tag!r}")


class _Fuel:
    def __init__(self) -> None:
        self.remaining = NORMALIZATION_FUEL

    def use(self) -> None:
        self.remaining -= 1
        if self.remaining < 0:
            _fail("E_RESOURCE", "normalization fuel exhausted")


def _node_count(expr: dict[str, Any]) -> int:
    tag = expr["tag"]
    if tag in {"sort", "bvar"}:
        return 1
    if tag in {"pi", "lam"}:
        return 1 + _node_count(expr["domain"]) + _node_count(expr["body"])
    if tag == "app":
        return 1 + _node_count(expr["function"]) + _node_count(expr["argument"])
    if tag == "let":
        return (1 + _node_count(expr["type"]) + _node_count(expr["value"])
                + _node_count(expr["body"]))
    _fail("E_AST_TAG", f"cannot count tag {tag!r}")


def _nf(expr: dict[str, Any], fuel: _Fuel | None = None) -> dict[str, Any]:
    fuel = fuel or _Fuel()
    fuel.use()
    tag = expr["tag"]
    if tag in {"sort", "bvar"}:
        result = copy.deepcopy(expr)
    elif tag in {"pi", "lam"}:
        result = {"tag": tag, "domain": _nf(expr["domain"], fuel),
                  "body": _nf(expr["body"], fuel)}
    elif tag == "let":
        value = _nf(expr["value"], fuel)
        result = _nf(_subst(expr["body"], value, 0), fuel)
    elif tag == "app":
        function = _nf(expr["function"], fuel)
        argument = _nf(expr["argument"], fuel)
        if function["tag"] == "lam":
            result = _nf(_subst(function["body"], argument, 0), fuel)
        else:
            result = {"tag": "app", "function": function, "argument": argument}
    else:
        _fail("E_AST_TAG", f"cannot normalize tag {tag!r}")
    if _node_count(result) > NORMALIZATION_NODE_LIMIT:
        _fail("E_RESOURCE", "normalization node limit exceeded")
    return result


def _whnf(expr: dict[str, Any], fuel: _Fuel | None = None) -> dict[str, Any]:
    fuel = fuel or _Fuel()
    current = copy.deepcopy(expr)
    while True:
        fuel.use()
        if current["tag"] == "let":
            current = _subst(current["body"], current["value"], 0)
            continue
        if current["tag"] == "app":
            function = _whnf(current["function"], fuel)
            if function["tag"] == "lam":
                current = _subst(function["body"], current["argument"], 0)
                continue
            return {"tag": "app", "function": function,
                    "argument": copy.deepcopy(current["argument"])}
        return current


def _as_sort(expr: dict[str, Any]) -> int:
    normalized = _nf(expr)
    if normalized["tag"] != "sort":
        _fail("E_NOT_SORT", "expected a sort-valued expression")
    return normalized["level"]


def _infer(expr: dict[str, Any], context: tuple[dict[str, Any], ...] = ()) -> dict[str, Any]:
    tag = expr["tag"]
    if tag == "sort":
        return {"tag": "sort", "level": expr["level"] + 1}
    if tag == "bvar":
        index = expr["index"]
        if index >= len(context):
            _fail("E_LOOSE_BVAR", f"bvar {index} is loose at context depth {len(context)}")
        return _shift(context[index], index + 1, 0)
    if tag == "pi":
        domain_level = _as_sort(_infer(expr["domain"], context))
        body_level = _as_sort(_infer(expr["body"], (expr["domain"], *context)))
        return {"tag": "sort", "level": 0 if body_level == 0 else max(domain_level, body_level)}
    if tag == "lam":
        _as_sort(_infer(expr["domain"], context))
        body_type = _infer(expr["body"], (expr["domain"], *context))
        return {"tag": "pi", "domain": copy.deepcopy(expr["domain"]), "body": body_type}
    if tag == "app":
        function_type = _infer(expr["function"], context)
        function_whnf = _whnf(function_type)
        if function_whnf["tag"] != "pi":
            _fail("E_APP_FUNCTION", "application function type does not reduce to Pi")
        argument_type = _infer(expr["argument"], context)
        if _nf(argument_type) != _nf(function_whnf["domain"]):
            _fail("E_APP_CONVERSION", "application argument type differs from domain")
        return _subst(function_whnf["body"], expr["argument"], 0)
    if tag == "let":
        _as_sort(_infer(expr["type"], context))
        value_type = _infer(expr["value"], context)
        if _nf(value_type) != _nf(expr["type"]):
            _fail("E_LET_CONVERSION", "let value type differs from annotation")
        body_type = _infer(expr["body"], (expr["type"], *context))
        return _subst(body_type, expr["value"], 0)
    _fail("E_AST_TAG", f"cannot infer tag {tag!r}")


def _derive(expr: dict[str, Any], context: tuple[dict[str, Any], ...] = ()) -> dict[str, Any]:
    tag = expr["tag"]
    context_value = copy.deepcopy(list(context))
    if tag == "sort":
        typ = {"tag": "sort", "level": expr["level"] + 1}
        premises: list[dict[str, Any]] = []
        witness = {"level": expr["level"], "result_level": expr["level"] + 1}
    elif tag == "bvar":
        if expr["index"] >= len(context):
            _fail("E_LOOSE_BVAR", "loose bvar in derivation")
        typ = _shift(context[expr["index"]], expr["index"] + 1, 0)
        premises = []
        witness = {"index": expr["index"], "lookup_type": copy.deepcopy(typ)}
    elif tag == "pi":
        domain = _derive(expr["domain"], context)
        domain_level = _as_sort(domain["type"])
        body = _derive(expr["body"], (expr["domain"], *context))
        body_level = _as_sort(body["type"])
        result_level = 0 if body_level == 0 else max(domain_level, body_level)
        typ = {"tag": "sort", "level": result_level}
        premises = [domain, body]
        witness = {"domain_level": domain_level, "body_level": body_level,
                   "result_level": result_level}
    elif tag == "lam":
        domain = _derive(expr["domain"], context)
        _as_sort(domain["type"])
        body = _derive(expr["body"], (expr["domain"], *context))
        body_type = copy.deepcopy(body["type"])
        typ = {"tag": "pi", "domain": copy.deepcopy(expr["domain"]),
               "body": body_type}
        premises = [domain, body]
        witness = {"body_type": body_type}
    elif tag == "app":
        function = _derive(expr["function"], context)
        argument = _derive(expr["argument"], context)
        function_type = copy.deepcopy(function["type"])
        function_whnf = _whnf(function_type)
        if function_whnf["tag"] != "pi":
            _fail("E_APP_FUNCTION", "application function type does not reduce to Pi")
        domain_nf = _nf(function_whnf["domain"])
        argument_nf = _nf(argument["type"])
        if argument_nf != domain_nf:
            _fail("E_APP_CONVERSION", "application argument type differs from domain")
        result_type = _subst(function_whnf["body"], expr["argument"], 0)
        typ = copy.deepcopy(result_type)
        premises = [function, argument]
        witness = {"function_type": function_type,
                   "function_type_whnf": copy.deepcopy(function_whnf),
                   "argument_type": copy.deepcopy(argument["type"]),
                   "domain_nf": domain_nf, "argument_type_nf": argument_nf,
                   "result_type": result_type}
    elif tag == "let":
        annotation = _derive(expr["type"], context)
        annotation_level = _as_sort(annotation["type"])
        value = _derive(expr["value"], context)
        annotation_nf = _nf(expr["type"])
        value_nf = _nf(value["type"])
        if value_nf != annotation_nf:
            _fail("E_LET_CONVERSION", "let value type differs from annotation")
        body = _derive(expr["body"], (expr["type"], *context))
        result_type = _subst(body["type"], expr["value"], 0)
        typ = copy.deepcopy(result_type)
        premises = [annotation, value, body]
        witness = {"annotation_level": annotation_level,
                   "annotation_nf": annotation_nf, "value_type": copy.deepcopy(value["type"]),
                   "value_type_nf": value_nf, "body_type": copy.deepcopy(body["type"]),
                   "result_type": result_type}
    else:
        _fail("E_AST_TAG", f"cannot derive tag {tag!r}")
    return {"context": context_value, "premises": premises, "rule": tag,
            "term": copy.deepcopy(expr), "type": copy.deepcopy(typ), "witness": witness}


def _replay(actual: Any, expected: dict[str, Any], path: str = "root") -> None:
    node = _exact(actual, DERIVATION_KEYS, "E_DERIVATION_KEYS", path)
    if node["rule"] != expected["rule"]:
        _fail("E_DERIVATION_RULE", f"{path} rule differs")
    if not _same(node["context"], expected["context"]):
        _fail("E_DERIVATION_CONTEXT", f"{path} context differs")
    if not _same(node["term"], expected["term"]):
        _fail("E_DERIVATION_TERM", f"{path} term differs")
    if not _same(node["type"], expected["type"]):
        _fail("E_DERIVATION_TYPE", f"{path} type differs")
    if not _same(node["witness"], expected["witness"]):
        _fail("E_DERIVATION_WITNESS", f"{path} witness differs")
    if not isinstance(node["premises"], list) or len(node["premises"]) != len(expected["premises"]):
        _fail("E_DERIVATION_PREMISES", f"{path} premise count differs")
    for index, (given, wanted) in enumerate(zip(node["premises"], expected["premises"])):
        _replay(given, wanted, f"{path}.premises[{index}]")


def _walk(expr: dict[str, Any]) -> Iterable[dict[str, Any]]:
    yield expr
    tag = expr["tag"]
    if tag in {"pi", "lam"}:
        yield from _walk(expr["domain"])
        yield from _walk(expr["body"])
    elif tag == "app":
        yield from _walk(expr["function"])
        yield from _walk(expr["argument"])
    elif tag == "let":
        yield from _walk(expr["type"])
        yield from _walk(expr["value"])
        yield from _walk(expr["body"])


def _uses(expr: dict[str, Any], target: int = 0) -> bool:
    tag = expr["tag"]
    if tag == "bvar":
        return expr["index"] == target
    if tag == "sort":
        return False
    if tag in {"pi", "lam"}:
        return _uses(expr["domain"], target) or _uses(expr["body"], target + 1)
    if tag == "app":
        return _uses(expr["function"], target) or _uses(expr["argument"], target)
    if tag == "let":
        return (_uses(expr["type"], target) or _uses(expr["value"], target)
                or _uses(expr["body"], target + 1))
    return False


def _active_binder(expr: dict[str, Any], tag: str) -> bool:
    for node in _walk(expr):
        if node["tag"] == tag and _uses(node["body"], 0):
            return True
    return False


def _counts(expr: dict[str, Any]) -> dict[str, int]:
    result = {tag: 0 for tag in TAGS}
    for node in _walk(expr):
        result[node["tag"]] += 1
    return result


def _has_beta(expr: dict[str, Any]) -> bool:
    return any(node["tag"] == "app" and node["function"]["tag"] == "lam" for node in _walk(expr))


def _category(expr: dict[str, Any]) -> str:
    counts = _counts(expr)
    root = expr["tag"]
    if root == "pi" and not any(counts[x] for x in ("lam", "app", "let")) and _active_binder(expr, "pi"):
        return "pi"
    if root == "lam" and not any(counts[x] for x in ("app", "let")) and _active_binder(expr, "lam"):
        return "lambda"
    if root == "app" and counts["let"] == 0 and counts["lam"] and _has_beta(expr):
        return "application"
    if root == "let" and counts["app"] == 0 and _active_binder(expr, "let"):
        return "let"
    if (root == "let" and all(counts[x] for x in ("pi", "lam", "app", "let"))
            and _has_beta(expr) and _active_binder(expr, "let")):
        return "mixed"
    _fail("E_CATEGORY", "term satisfies no frozen category predicate")


def _depth(expr: dict[str, Any]) -> int:
    tag = expr["tag"]
    if tag in {"sort", "bvar"}:
        return 1
    if tag in {"pi", "lam"}:
        return 1 + max(_depth(expr["domain"]), _depth(expr["body"]))
    if tag == "app":
        return 1 + max(_depth(expr["function"]), _depth(expr["argument"]))
    return 1 + max(_depth(expr["type"]), _depth(expr["value"]), _depth(expr["body"]))


def _binder_depth(expr: dict[str, Any], current: int = 0) -> int:
    tag = expr["tag"]
    if tag in {"sort", "bvar"}:
        return current
    if tag in {"pi", "lam"}:
        return max(_binder_depth(expr["domain"], current), _binder_depth(expr["body"], current + 1))
    if tag == "app":
        return max(_binder_depth(expr["function"], current), _binder_depth(expr["argument"], current))
    return max(_binder_depth(expr["type"], current), _binder_depth(expr["value"], current),
               _binder_depth(expr["body"], current + 1))


def _maximum_sort(expr: dict[str, Any]) -> int:
    values = [node["level"] for node in _walk(expr) if node["tag"] == "sort"]
    return max(values, default=0)


def _metrics(term: dict[str, Any], type_nf: dict[str, Any]) -> dict[str, Any]:
    return {
        "ast_depth": _depth(term),
        "binder_depth": _binder_depth(term),
        "constructor_counts": _counts(term),
        "maximum_derived_sort_level": _maximum_sort(type_nf),
        "maximum_input_sort_level": _maximum_sort(term),
        "node_count": _node_count(term),
        "normalized_type_nodes": _node_count(type_nf),
    }


def _case_seed(design: dict[str, Any], category: str, slot: int) -> str:
    selection = design["deterministic_selection"]
    master = bytes.fromhex(selection["master_seed_sha256"])
    return hmac.new(master, category.encode("utf-8") + b"\0" + slot.to_bytes(2, "big"),
                    hashlib.sha256).hexdigest()


def _band(design: dict[str, Any], slot: int) -> tuple[int, int]:
    for row in design["size_policy"]["bands"]:
        if slot in row["slots_zero_based"]:
            return row["minimum_nodes"], row["maximum_nodes"]
    _fail("E_DESIGN", f"no size band for slot {slot}")


def audit_case(case: Any, design: dict[str, Any]) -> dict[str, Any]:
    """Audit one in-memory case against the frozen design."""
    case = _exact(case, CASE_KEYS, "E_CASE_KEYS", "case")
    if type(case["schema_version"]) is not int or case["schema_version"] != 1:
        _fail("E_CASE_SCHEMA", "case schema_version differs")
    contract = design["case_contract"]
    category = case["category"]
    if category not in contract["order"]:
        _fail("E_CATEGORY", "unknown category")
    index = _natural(case["category_index"], "category_index")
    count = contract["count_per_category"]
    if index < 1 or index > count:
        _fail("E_CASE_ID", "category_index is out of range")
    expected_id = f"vdtp1-{category}-{index:02d}"
    if case["case_id"] != expected_id:
        _fail("E_CASE_ID", "case_id differs")
    attempt = _natural(case["selection_attempt"], "selection_attempt")
    expected_attempt = _natural(
        design["deterministic_selection"]["expected_selection_attempt"],
        "design.deterministic_selection.expected_selection_attempt",
    )
    if expected_attempt != 0:
        _fail("E_DESIGN", "frozen expected selection attempt differs from zero")
    if attempt != expected_attempt:
        _fail("E_SELECTION_ATTEMPT", "selection attempt differs from frozen design")
    if not isinstance(case["case_seed_sha256"], str) or not HEX64.fullmatch(case["case_seed_sha256"]):
        _fail("E_SEED", "case seed is not a lowercase SHA-256")
    if case["case_seed_sha256"] != _case_seed(design, category, index - 1):
        _fail("E_SEED", "case seed differs")

    maximum_input = design["size_policy"]["input_sort_levels"]["maximum"]
    maximum_derived = design["size_policy"]["maximum_derived_sort_level"]
    term = _validate_expr(case["term"], maximum_input, "term")
    expected_type = _validate_expr(case["expected_type_nf"], maximum_derived, "expected_type_nf")
    inferred_nf = _nf(_infer(term))
    if not _same(_nf(expected_type), expected_type) or not _same(inferred_nf, expected_type):
        _fail("E_EXPECTED_TYPE", "expected normalized type differs from independent inference")
    actual_category = _category(term)
    if actual_category != category:
        _fail("E_CATEGORY", f"term is {actual_category}, not {category}")

    expected_derivation = _derive(term)
    if not _same(_nf(expected_derivation["type"]), expected_type):
        _fail("E_DERIVATION_TYPE", "rederived root type differs")
    _replay(case["derivation"], expected_derivation)

    expected_metrics = _metrics(term, expected_type)
    _exact(case["metrics"], METRIC_KEYS, "E_METRICS", "metrics")
    counts = _exact(case["metrics"]["constructor_counts"], set(TAGS),
                    "E_METRICS", "metrics.constructor_counts")
    for name, value in case["metrics"].items():
        if name == "constructor_counts":
            continue
        _natural(value, "metrics." + name)
    for name, value in counts.items():
        _natural(value, "metrics.constructor_counts." + name)
    if not _same(case["metrics"], expected_metrics):
        _fail("E_METRICS", "metrics differ")
    policy = design["size_policy"]
    minimum, maximum = _band(design, index - 1)
    minimum = max(minimum, policy["category_minimum_nodes"][category])
    if not minimum <= expected_metrics["node_count"] <= maximum:
        _fail("E_SIZE", "node count is outside the frozen slot band")
    if expected_metrics["ast_depth"] > policy["maximum_ast_depth"]:
        _fail("E_SIZE", "AST depth exceeds policy")
    if expected_metrics["binder_depth"] > policy["maximum_binder_depth"]:
        _fail("E_SIZE", "binder depth exceeds policy")
    if expected_metrics["normalized_type_nodes"] > policy["maximum_normalized_type_nodes"]:
        _fail("E_SIZE", "normalized type exceeds policy")
    if expected_metrics["maximum_derived_sort_level"] > maximum_derived:
        _fail("E_SIZE", "derived sort level exceeds policy")

    return {
        "case_id": case["case_id"],
        "status": "PASS",
        "term_sha256": _digest(term),
        "expected_type_sha256": _digest(expected_type),
        "derivation_sha256": _digest(case["derivation"]),
        "metrics_sha256": _digest(expected_metrics),
    }


def audit_case_file(path: str | Path, design: dict[str, Any]) -> dict[str, Any]:
    """Strictly parse and audit one canonical case file."""
    source = Path(path)
    value, raw = _load_strict(source)
    result = audit_case(value, design)
    return {**result, "path": source.as_posix(), "sha256": hashlib.sha256(raw).hexdigest(),
            "bytes": len(raw)}


def audit_corpus(paths: Iterable[str | Path], design: dict[str, Any]) -> dict[str, Any]:
    """Audit exact case order, count, and distinctness for a complete corpus."""
    path_list = [Path(path) for path in paths]
    contract = design["case_contract"]
    expected_ids = [f"vdtp1-{category}-{index:02d}" for category in contract["order"]
                    for index in range(1, contract["count_per_category"] + 1)]
    if len(path_list) != contract["total"] or len(expected_ids) != contract["total"]:
        _fail("E_CORPUS_COUNT", "corpus count differs")
    results = [audit_case_file(path, design) for path in path_list]
    actual_ids = [row["case_id"] for row in results]
    if actual_ids != expected_ids:
        _fail("E_CORPUS_ORDER", "corpus case order differs")
    hashes = [row["term_sha256"] for row in results]
    if len(set(hashes)) != contract["distinct_term_hashes"]:
        _fail("E_CORPUS_DUPLICATE", "corpus term hashes are not all distinct")
    category_counts = {category: 0 for category in contract["order"]}
    for case_id in actual_ids:
        category = next(category for category in contract["order"]
                        if case_id.startswith(f"vdtp1-{category}-"))
        category_counts[category] += 1
    return {"status": "PASS", "case_count": len(results),
            "category_counts": category_counts, "cases": results,
            "aggregate_sha256": hashlib.sha256(_canonical(results)).hexdigest()}


__all__ = ["AuditError", "audit_case", "audit_case_file", "audit_corpus"]
