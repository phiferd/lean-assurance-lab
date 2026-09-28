"""Small capture-avoiding named syntax model for BINDER-MODEL-PILOT-1.

This module deliberately does not implement de Bruijn shift or instantiation.
Its only index operation translates a completed named term into a finite
context. The independent auditor does not import this module.
"""
from __future__ import annotations

from typing import Any


class ModelError(ValueError):
    pass


def _tag(t: list[Any]) -> str:
    if not isinstance(t, list) or not t or not isinstance(t[0], str):
        raise ModelError("malformed named expression")
    return t[0]


def names(t: list[Any]) -> set[str]:
    """All names, including binders, used to choose a deterministic fresh name."""
    tag = _tag(t)
    if tag == "v" and len(t) == 2 and isinstance(t[1], str):
        return {t[1]}
    if tag == "s" and len(t) == 1:
        return set()
    if tag == "a" and len(t) == 3:
        return names(t[1]) | names(t[2])
    if tag == "l" and len(t) == 4 and isinstance(t[1], str):
        return {t[1]} | names(t[2]) | names(t[3])
    if tag == "t" and len(t) == 5 and isinstance(t[1], str):
        return {t[1]} | names(t[2]) | names(t[3]) | names(t[4])
    raise ModelError("malformed named expression")


def free_names(t: list[Any]) -> set[str]:
    tag = _tag(t)
    if tag == "v" and len(t) == 2 and isinstance(t[1], str):
        return {t[1]}
    if tag == "s" and len(t) == 1:
        return set()
    if tag == "a" and len(t) == 3:
        return free_names(t[1]) | free_names(t[2])
    if tag == "l" and len(t) == 4 and isinstance(t[1], str):
        return free_names(t[2]) | (free_names(t[3]) - {t[1]})
    if tag == "t" and len(t) == 5 and isinstance(t[1], str):
        return free_names(t[2]) | free_names(t[3]) | (free_names(t[4]) - {t[1]})
    raise ModelError("malformed named expression")


def _fresh(avoid: set[str]) -> str:
    i = 0
    while f"__alpha{i}" in avoid:
        i += 1
    return f"__alpha{i}"


def _rename_bound(t: list[Any], old: str, new: str) -> list[Any]:
    """Rename occurrences bound by an enclosing binder, respecting shadows."""
    tag = _tag(t)
    if tag == "v":
        return ["v", new if t[1] == old else t[1]]
    if tag == "s":
        return ["s"]
    if tag == "a":
        return ["a", _rename_bound(t[1], old, new), _rename_bound(t[2], old, new)]
    if tag == "l":
        ty = _rename_bound(t[2], old, new)
        body = t[3] if t[1] == old else _rename_bound(t[3], old, new)
        return ["l", t[1], ty, body]
    if tag == "t":
        ty = _rename_bound(t[2], old, new)
        val = _rename_bound(t[3], old, new)
        body = t[4] if t[1] == old else _rename_bound(t[4], old, new)
        return ["t", t[1], ty, val, body]
    raise ModelError("malformed named expression")


def substitute(t: list[Any], target: str, replacement: list[Any]) -> list[Any]:
    """Capture-avoiding free-name substitution; no index arithmetic."""
    if not isinstance(target, str):
        raise ModelError("non-string target")
    replacement_free = free_names(replacement)

    def go(e: list[Any]) -> list[Any]:
        tag = _tag(e)
        if tag == "v":
            return replacement if e[1] == target else e
        if tag == "s":
            return e
        if tag == "a":
            return ["a", go(e[1]), go(e[2])]
        if tag in {"l", "t"}:
            binder = e[1]
            if not isinstance(binder, str):
                raise ModelError("non-string binder")
            ty = go(e[2])
            val = go(e[3]) if tag == "t" else None
            body = e[4] if tag == "t" else e[3]
            if binder == target:
                new_binder, new_body = binder, body
            else:
                if binder in replacement_free and target in free_names(body):
                    new_binder = _fresh(names(body) | names(replacement) | {target, binder})
                    body = _rename_bound(body, binder, new_binder)
                else:
                    new_binder = binder
                new_body = go(body)
            return (["l", new_binder, ty, new_body] if tag == "l"
                    else ["t", new_binder, ty, val, new_body])
        raise ModelError("malformed named expression")

    return go(t)


def to_indices(t: list[Any], external_nearest_first: list[str]) -> list[Any]:
    if len(set(external_nearest_first)) != len(external_nearest_first):
        raise ModelError("duplicate external context name")
    if any(not isinstance(n, str) for n in external_nearest_first):
        raise ModelError("non-string external context name")

    def go(e: list[Any], binders: list[str]) -> list[Any]:
        tag = _tag(e)
        if tag == "v" and len(e) == 2 and isinstance(e[1], str):
            scope = binders + external_nearest_first
            try:
                return ["b", scope.index(e[1])]
            except ValueError as exc:
                raise ModelError(f"name outside context: {e[1]}") from exc
        if tag == "s" and len(e) == 1:
            return ["s"]
        if tag == "a" and len(e) == 3:
            return ["a", go(e[1], binders), go(e[2], binders)]
        if tag == "l" and len(e) == 4 and isinstance(e[1], str):
            return ["l", go(e[2], binders), go(e[3], [e[1]] + binders)]
        if tag == "t" and len(e) == 5 and isinstance(e[1], str):
            return ["t", go(e[2], binders), go(e[3], binders),
                    go(e[4], [e[1]] + binders)]
        raise ModelError("malformed named expression")

    return go(t, [])


def alpha_equal(a: list[Any], b: list[Any]) -> bool:
    """Compare binder structure directly, without the index translator."""
    def go(x: list[Any], y: list[Any], xb: list[str], yb: list[str]) -> bool:
        xt, yt = _tag(x), _tag(y)
        if xt != yt:
            return False
        if xt == "v":
            xi = xb.index(x[1]) if x[1] in xb else None
            yi = yb.index(y[1]) if y[1] in yb else None
            return xi == yi and (xi is not None or x[1] == y[1])
        if xt == "s":
            return True
        if xt == "a":
            return go(x[1], y[1], xb, yb) and go(x[2], y[2], xb, yb)
        if xt == "l":
            return go(x[2], y[2], xb, yb) and go(x[3], y[3], [x[1]] + xb, [y[1]] + yb)
        if xt == "t":
            return (go(x[2], y[2], xb, yb) and go(x[3], y[3], xb, yb)
                    and go(x[4], y[4], [x[1]] + xb, [y[1]] + yb))
        raise ModelError("malformed named expression")

    return go(a, b, [], [])
