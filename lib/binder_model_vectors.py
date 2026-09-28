"""Frozen-rule candidate vector producer for BINDER-MODEL-PILOT-1.

Importing this module does not construct the scientific corpus. Construction
is gated by a separately committed scientific manifest and independent review.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from lib.binder_named_model import free_names, substitute, to_indices

SEED = 0xB17D3A9E5C204F61
MASK = (1 << 64) - 1
OPERATIONS = ("LIFT", "SUBST", "LIFT_COMPOSE", "SUBST_COMPOSE")
COUNT = 10000


class VectorError(ValueError):
    pass


class SplitMix64:
    def __init__(self, ordinal: int):
        self.state = (SEED ^ ordinal) & MASK

    def next(self) -> int:
        self.state = (self.state + 0x9E3779B97F4A7C15) & MASK
        z = self.state
        z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & MASK
        z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & MASK
        return (z ^ (z >> 31)) & MASK

    def choose(self, n: int) -> int:
        if n <= 0:
            raise VectorError("empty random range")
        return self.next() % n


def _var(name: str) -> list[Any]:
    return ["v", name]


def _source(family: int, variant: int, context: list[str], rng: SplitMix64) -> list[Any]:
    c0, c1, c2 = context[:3]
    tail = context[1 + rng.choose(len(context) - 1)]
    binder = c1 if family > 0 and variant % 2 == 0 else "x"
    other = c2 if variant % 3 == 0 else "y"
    if family == 0:
        return ["a", _var(c0), _var(tail)]
    if family == 1:
        return ["l", binder, ["s"],
                ["l", other, _var(c0), ["a", _var(c0), _var(binder)]]]
    if family == 2:
        return ["a", ["l", binder, _var(c0),
                      ["a", _var(c0), _var(binder)]], _var(tail)]
    if family == 3:
        return ["t", binder, _var(c0), _var(tail),
                ["a", _var(c0), _var(binder)]]
    if family == 4:
        return ["l", binder, _var(c0),
                ["t", other, _var(c0), ["a", _var(tail), _var(c0)],
                 ["a", ["a", _var(c0), _var(binder)], _var(other)]]]
    raise VectorError("unknown family")


def _replacement(context: list[str], variant: int, rng: SplitMix64) -> list[Any]:
    if not context:
        return ["s"]
    primary = context[0]
    tail = context[rng.choose(len(context))]
    which = variant % 4
    if which == 0:
        return _var(primary)
    if which == 1:
        return ["a", _var(primary), _var(tail)]
    if which == 2:
        return ["l", "r", ["s"], ["a", _var(primary), _var("r")]]
    return ["t", "r", ["s"], _var(tail), ["a", _var(primary), _var("r")]]


def _insert_context(context: list[str], ordinal: int, step: int, s: int, d: int) -> list[str]:
    if not (0 <= s <= len(context) and 0 <= d <= 2):
        raise VectorError("invalid lift parameters")
    fresh = [f"j{ordinal}_{step}_{k}" for k in range(d)]
    if set(fresh) & set(context):
        raise VectorError("fresh name collision")
    return context[:s] + fresh + context[s:]


def _size_depth(t: list[Any], depth: int = 0) -> tuple[int, int]:
    tag = t[0]
    if tag in {"v", "s"}:
        return 1, depth
    if tag == "a":
        a, ad = _size_depth(t[1], depth)
        b, bd = _size_depth(t[2], depth)
        return 1 + a + b, max(ad, bd)
    if tag == "l":
        a, ad = _size_depth(t[2], depth)
        b, bd = _size_depth(t[3], depth + 1)
        return 1 + a + b, max(ad, bd)
    if tag == "t":
        a, ad = _size_depth(t[2], depth)
        b, bd = _size_depth(t[3], depth)
        c, cd = _size_depth(t[4], depth + 1)
        return 1 + a + b + c, max(ad, bd, cd)
    raise VectorError("unknown term tag")


def make_vector(ordinal: int) -> dict[str, Any]:
    if type(ordinal) is not int or not 0 <= ordinal < COUNT:
        raise VectorError("ordinal outside fixed suite")
    op = OPERATIONS[ordinal // 2500]
    family = (ordinal % 2500) // 500
    variant = ordinal % 500
    rng = SplitMix64(ordinal)
    context = [f"c{k}" for k in range(3 + rng.choose(4))]
    source_named = _source(family, variant, context, rng)
    if not free_names(source_named) <= set(context):
        raise VectorError("source outside context")
    size, depth = _size_depth(source_named)
    if size > 20 or depth > 3:
        raise VectorError("source exceeds frozen size/depth")

    args_named: list[list[Any]] = []
    args_db: list[list[Any]] = []
    contexts_after: list[list[str]] = []
    named_expected: list[list[Any]] = []
    params: dict[str, int] = {}

    if op in {"LIFT", "LIFT_COMPOSE"}:
        s1, d1 = rng.choose(len(context) + 1), rng.choose(3)
        c1 = _insert_context(context, ordinal, 1, s1, d1)
        params = {"s": s1, "d": d1} if op == "LIFT" else {"s1": s1, "d1": d1}
        contexts_after.append(c1)
        named_expected.append(source_named)
        if op == "LIFT_COMPOSE":
            s2, d2 = rng.choose(len(c1) + 1), rng.choose(3)
            c2 = _insert_context(c1, ordinal, 2, s2, d2)
            params.update({"s2": s2, "d2": d2})
            contexts_after.append(c2)
            named_expected.append(source_named)
    else:
        a = _replacement(context[1:], variant, rng)
        if not free_names(a) <= set(context[1:]):
            raise VectorError("first argument outside context")
        args_named.append(a)
        args_db.append(to_indices(a, context[1:]))
        c1 = context[1:]
        first = substitute(source_named, context[0], a)
        contexts_after.append(c1)
        named_expected.append(first)
        if op == "SUBST_COMPOSE":
            b = _replacement(context[2:], variant // 4, rng)
            if not free_names(b) <= set(context[2:]):
                raise VectorError("second argument outside context")
            args_named.append(b)
            args_db.append(to_indices(b, context[2:]))
            c2 = context[2:]
            second = substitute(first, context[1], b)
            contexts_after.append(c2)
            named_expected.append(second)

    expected = [to_indices(term, ctx) for term, ctx in zip(named_expected, contexts_after)]
    return {
        "id": f"bmp1-{ordinal:05d}",
        "ordinal": ordinal,
        "operation": op,
        "family": family,
        "variant": variant,
        "context": context,
        "named_source": source_named,
        "source": to_indices(source_named, context),
        "named_arguments": args_named,
        "arguments": args_db,
        "parameters": params,
        "contexts_after": contexts_after,
        "named_expected": named_expected,
        "expected": expected,
    }


def construct(path: Path) -> None:
    """The guarded construction command calls this only after input freeze."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as stream:
        for i in range(COUNT):
            stream.write(json.dumps(make_vector(i), sort_keys=True, separators=(",", ":")) + "\n")
