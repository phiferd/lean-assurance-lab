"""Independent, fail-closed replay for the frozen stateful validation pilot.

The small expression interpreter here does not import the fixture producer or
the Lean runner. It checks the declared six histories and every emitted
environment, including the state after rejected requests.
"""
from __future__ import annotations

import hashlib
import json
import re
from typing import Any


CONTRACT_SHA256 = "e50cf4aa5a37c819968d363553b3423bf61eafc746c4b0fc9c61d01de233f006"
EXPECTED_IDS = (
    "accepted-independent", "accepted-reduction", "rejected-malformed",
    "rejected-duplicate", "rejected-name-reuse", "independent-order",
)
REQUEST_KEYS = {"id", "name", "type", "value"}
DECLARATION_KEYS = {"name", "type", "value", "safety", "levelParams"}
BEGIN_KEYS = {"kind", "comparison", "side", "api", "skipKernelTC", "trustLevel", "environment"}
STEP_KEYS = {"kind", "comparison", "side", "index", "request", "outcome", "environment"}
END_KEYS = {"kind", "comparison", "side", "steps"}
NAME = re.compile(r"[A-Za-z][A-Za-z0-9_]*(?:\.[A-Za-z][A-Za-z0-9_]*)+\Z")
MAX_REWRITE_STEPS = 10_000


class AuditError(ValueError):
    def __init__(self, code: str, detail: str):
        self.code = code
        super().__init__(f"{code}: {detail}")


def _fail(code: str, detail: str) -> None:
    raise AuditError(code, detail)


def _keys(value: Any, expected: set[str], label: str) -> dict[str, Any]:
    if type(value) is not dict or set(value) != expected:
        _fail("E_SCHEMA", f"{label} has unexpected keys")
    return value


def _canonical(value: Any) -> bytes:
    try:
        return json.dumps(value, sort_keys=True, separators=(",", ":"),
                          ensure_ascii=False, allow_nan=False).encode("utf-8")
    except (TypeError, ValueError) as error:
        _fail("E_JSON", str(error))


def _pairs(items: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in items:
        if key in result:
            _fail("E_JSON", f"duplicate key {key}")
        result[key] = value
    return result


def _nonfinite(value: str) -> None:
    _fail("E_JSON", f"nonfinite value {value}")


def _json(raw: bytes) -> Any:
    try:
        return json.loads(raw.decode("utf-8"), object_pairs_hook=_pairs,
                          parse_constant=_nonfinite)
    except (UnicodeError, json.JSONDecodeError) as error:
        _fail("E_JSON", str(error))


def _expr(value: Any) -> tuple:
    """Parse only the committed array DSL into immutable expression nodes."""
    if type(value) is not list or not value or type(value[0]) is not str:
        _fail("E_EXPR", "expression is not a tagged array")
    tag = value[0]
    if tag in {"sort", "var"}:
        if len(value) != 2 or type(value[1]) is not int or value[1] < 0 or value[1] > 8:
            _fail("E_EXPR", f"invalid {tag} operand")
        return tag, value[1]
    if tag == "const":
        if len(value) != 2 or type(value[1]) is not str or not NAME.fullmatch(value[1]):
            _fail("E_EXPR", "invalid constant name")
        return tag, value[1]
    if tag in {"pi", "lam", "app"}:
        if len(value) != 3:
            _fail("E_EXPR", f"invalid {tag} arity")
        return tag, _expr(value[1]), _expr(value[2])
    _fail("E_EXPR", f"excluded constructor {tag}")


def _shift(term: tuple, amount: int, cutoff: int = 0) -> tuple:
    tag = term[0]
    if tag == "var":
        return tag, term[1] + amount if term[1] >= cutoff else term[1]
    if tag in {"sort", "const"}:
        return term
    if tag in {"pi", "lam"}:
        return tag, _shift(term[1], amount, cutoff), _shift(term[2], amount, cutoff + 1)
    return tag, _shift(term[1], amount, cutoff), _shift(term[2], amount, cutoff)


def _subst(term: tuple, replacement: tuple, depth: int = 0) -> tuple:
    tag = term[0]
    if tag == "var":
        index = term[1]
        if index == depth:
            return _shift(replacement, depth)
        return ("var", index - 1) if index > depth else term
    if tag in {"sort", "const"}:
        return term
    if tag in {"pi", "lam"}:
        return tag, _subst(term[1], replacement, depth), _subst(term[2], replacement, depth + 1)
    return tag, _subst(term[1], replacement, depth), _subst(term[2], replacement, depth)


class _Fuel:
    def __init__(self) -> None:
        self.left = MAX_REWRITE_STEPS

    def use(self) -> None:
        self.left -= 1
        if self.left < 0:
            _fail("E_RESOURCE", "expression reduction bound exceeded")


def _whnf(term: tuple, env: dict[str, tuple[tuple, tuple]], fuel: _Fuel) -> tuple:
    while True:
        fuel.use()
        tag = term[0]
        if tag == "const" and term[1] in env:
            term = env[term[1]][1]
            continue
        if tag == "app":
            function = _whnf(term[1], env, fuel)
            if function[0] == "lam":
                term = _subst(function[2], term[2])
                continue
            return "app", function, term[2]
        return term


def _nf(term: tuple, env: dict[str, tuple[tuple, tuple]], fuel: _Fuel | None = None) -> tuple:
    fuel = fuel or _Fuel()
    term = _whnf(term, env, fuel)
    tag = term[0]
    if tag in {"sort", "var", "const"}:
        return term
    if tag in {"pi", "lam"}:
        return tag, _nf(term[1], env, fuel), _nf(term[2], env, fuel)
    function = _nf(term[1], env, fuel)
    argument = _nf(term[2], env, fuel)
    if function[0] == "lam":
        return _nf(_subst(function[2], argument), env, fuel)
    return "app", function, argument


def _sort_level(term: tuple, env: dict[str, tuple[tuple, tuple]]) -> int:
    normal = _whnf(term, env, _Fuel())
    if normal[0] != "sort":
        _fail("E_TYPE", "inferred type does not reduce to Sort")
    return normal[1]


def _infer(term: tuple, env: dict[str, tuple[tuple, tuple]],
           context: tuple[tuple, ...] = ()) -> tuple:
    tag = term[0]
    if tag == "sort":
        return "sort", term[1] + 1
    if tag == "var":
        index = term[1]
        if index >= len(context):
            _fail("E_TYPE", "loose de Bruijn index")
        return _shift(context[index], index + 1)
    if tag == "const":
        if term[1] not in env:
            _fail("E_DEPENDENCY", f"undefined constant {term[1]}")
        return env[term[1]][0]
    if tag == "pi":
        domain_level = _sort_level(_infer(term[1], env, context), env)
        body_level = _sort_level(_infer(term[2], env, (term[1], *context)), env)
        return "sort", 0 if body_level == 0 else max(domain_level, body_level)
    if tag == "lam":
        _sort_level(_infer(term[1], env, context), env)
        body_type = _infer(term[2], env, (term[1], *context))
        return "pi", term[1], body_type
    function_type = _whnf(_infer(term[1], env, context), env, _Fuel())
    if function_type[0] != "pi":
        _fail("E_TYPE", "application function has no Pi type")
    argument_type = _infer(term[2], env, context)
    if _nf(argument_type, env) != _nf(function_type[1], env):
        _fail("E_TYPE", "application argument type mismatch")
    return _subst(function_type[2], term[2])


def _request(doc: dict, declaration_id: str) -> dict:
    declaration = doc["declarations"][declaration_id]
    return {"id": declaration_id, "name": declaration["name"],
            "type": declaration["type"], "value": declaration["value"]}


def _model_step(request: dict, env: dict[str, tuple[tuple, tuple]],
                projection: dict[str, dict]) -> tuple[str, dict[str, tuple[tuple, tuple]], dict[str, dict]]:
    name = request["name"]
    if name in env:
        return "alreadyDeclared", env, projection
    declared_type, value = _expr(request["type"]), _expr(request["value"])
    _sort_level(_infer(declared_type, env), env)
    actual_type = _infer(value, env)
    if _nf(actual_type, env) != _nf(declared_type, env):
        return "declTypeMismatch", env, projection
    next_env = {**env, name: (declared_type, value)}
    next_projection = {**projection, name: {
        "name": name, "type": request["type"], "value": request["value"],
        "safety": "safe", "levelParams": [],
    }}
    return "ACCEPT", next_env, next_projection


def _history(doc: dict, comparison_id: str, side: str) -> tuple[list[dict], list[tuple[str, list[dict]]]]:
    comparison = next(row for row in doc["comparisons"] if row["id"] == comparison_id)
    requests = [_request(doc, declaration_id) for declaration_id in comparison[side]]
    env: dict[str, tuple[tuple, tuple]] = {}
    projection: dict[str, dict] = {}
    states = []
    for request in requests:
        outcome, env, projection = _model_step(request, env, projection)
        states.append((outcome, [projection[name] for name in sorted(projection)]))
    return requests, states


def audit_contract(doc: dict) -> dict:
    """Bind the complete frozen contract and independently replay its expectations."""
    if type(doc) is not dict or hashlib.sha256(_canonical(doc)).hexdigest() != CONTRACT_SHA256:
        _fail("E_CONTRACT", "scientific contract differs from committed revision")
    if (doc["schema_version"] != 1 or doc["item_id"] != "STATEFUL-VALIDATION-PILOT-1"
        or doc["api"] != "Lean.Kernel.Environment.addDecl"
        or doc["source_commit"] != "d8b18978322de05a8f3dba51ef03cf5461676c17"
        or doc["toolchain"] != "leanprover/lean4:v4.33.0"
        or doc["options"] != {"debug.skipKernelTC": False, "maxRecDepth": 1000,
                              "maxHeartbeats": 200000}):
        _fail("E_CONTRACT", "source/API/options binding differs")
    if tuple(row["id"] for row in doc["comparisons"]) != EXPECTED_IDS:
        _fail("E_CONTRACT", "comparison identities/order differ")
    steps = 0
    for row in doc["comparisons"]:
        target_requests = []
        for side in ("fresh", "prefixed"):
            requests, states = _history(doc, row["id"], side)
            expected = row[f"{side}_outcomes"]
            if [outcome for outcome, _ in states] != expected:
                _fail("E_CONTRACT", f"independent outcome disagrees: {row['id']}/{side}")
            if requests[-1]["id"] != row["target"]:
                _fail("E_CONTRACT", "target is not final request")
            target_requests.append(requests[-1])
            steps += len(requests)
        if _canonical(target_requests[0]) != _canonical(target_requests[1]):
            _fail("E_CONTRACT", "paired target requests differ")
    if steps != 25:
        _fail("E_CONTRACT", "fixed history count is not 25")
    return {"status": "PASS", "comparisons": 6, "histories": 12, "steps": steps,
            "contract_sha256": CONTRACT_SHA256}


def _check_fixture(fixture: dict, doc: dict, comparison_id: str, side: str) -> None:
    _keys(fixture, {"comparison", "side", "requests"}, "fixture")
    if comparison_id not in EXPECTED_IDS or side not in {"fresh", "prefixed"}:
        _fail("E_FIXTURE", "unknown comparison or side")
    if fixture["comparison"] != comparison_id or fixture["side"] != side:
        _fail("E_FIXTURE", "fixture identity differs")
    expected, _ = _history(doc, comparison_id, side)
    if type(fixture["requests"]) is not list or len(fixture["requests"]) != len(expected):
        _fail("E_FIXTURE", "request count differs")
    for observed, request in zip(fixture["requests"], expected):
        _keys(observed, REQUEST_KEYS, "request")
        if _canonical(observed) != _canonical(request):
            _fail("E_FIXTURE", "request differs from scientific contract")


def audit_fixture(data: bytes, doc: dict, comparison_id: str, side: str) -> dict:
    """Audit a generated fixture before any public API invocation."""
    audit_contract(doc)
    fixture = _json(data)
    _check_fixture(fixture, doc, comparison_id, side)
    return fixture


def audit_output(stdout: bytes, stderr: bytes, fixture: dict, doc: dict) -> dict:
    """Replay one complete BEGIN/STEP*/END process receipt, rejecting all extras."""
    audit_contract(doc)
    if type(stderr) is not bytes or stderr:
        _fail("E_STDERR", "nonempty or nonbyte stderr")
    if type(stdout) is not bytes or not stdout.endswith(b"\n") or b"\r" in stdout:
        _fail("E_OUTPUT", "stdout must be newline-terminated NDJSON")
    if type(fixture) is not dict:
        _fail("E_FIXTURE", "fixture is not an object")
    comparison_id, side = fixture.get("comparison"), fixture.get("side")
    _check_fixture(fixture, doc, comparison_id, side)
    requests, states = _history(doc, comparison_id, side)
    lines = stdout.splitlines()
    if len(lines) != len(requests) + 2 or any(not line for line in lines):
        _fail("E_OUTPUT", "NDJSON record count or blank lines differ")
    records = [_json(line) for line in lines]
    begin = _keys(records[0], BEGIN_KEYS, "BEGIN")
    expected_begin = {"kind": "begin", "comparison": comparison_id, "side": side,
                      "api": doc["api"], "skipKernelTC": False, "trustLevel": 0,
                      "environment": []}
    if _canonical(begin) != _canonical(expected_begin):
        _fail("E_BEGIN", "BEGIN values differ")
    for index, (record, request, (outcome, environment)) in enumerate(
        zip(records[1:-1], requests, states)
    ):
        _keys(record, STEP_KEYS, "STEP")
        if (record["kind"] != "step" or record["comparison"] != comparison_id
            or record["side"] != side or type(record["index"]) is not int
            or record["index"] != index):
            _fail("E_STEP", f"STEP identity/order differs at {index}")
        _keys(record["request"], REQUEST_KEYS, "STEP.request")
        if _canonical(record["request"]) != _canonical(request):
            _fail("E_STEP", f"STEP request differs at {index}")
        if record["outcome"] != outcome:
            _fail("E_OUTCOME", f"STEP outcome differs at {index}")
        if type(record["environment"]) is not list:
            _fail("E_ENVIRONMENT", f"STEP environment is not an array at {index}")
        for declaration in record["environment"]:
            _keys(declaration, DECLARATION_KEYS, "STEP.environment declaration")
        if _canonical(record["environment"]) != _canonical(environment):
            _fail("E_ENVIRONMENT", f"complete environment differs at {index}")
    end = _keys(records[-1], END_KEYS, "END")
    expected_end = {"kind": "end", "comparison": comparison_id, "side": side,
                    "steps": len(requests)}
    if _canonical(end) != _canonical(expected_end):
        _fail("E_END", "END values differ")
    return {"status": "PASS", "comparison": comparison_id, "side": side,
            "steps": len(requests), "target_outcome": states[-1][0],
            "stdout_sha256": hashlib.sha256(stdout).hexdigest()}
