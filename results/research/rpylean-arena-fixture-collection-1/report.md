# One shared Arena test in the rpylean developer suite

**What did we find?** rpylean accepted all three declarations in Arena's valid
proof-parameter example. Its original test suite missed the example when pointed
at Arena's documented root. Pointing the suite directly at the case's directory
worked. With the local patch, the usual suite found the case by its full name
and checked Arena's expected acceptance. This comparison measured one shared
example on one checker revision. [Result](result.json)

**Is it interesting?** Yes. The checker already handled this example correctly
against Arena's stated expectation. The gain is in routine testing. A developer
can run the example alongside the existing tests, identify it in the output,
and distinguish an executed pass from a missing file or an optional skip.

**Does it require more work?** The local item is complete. Use the directory
override for a one-off check on unmodified rpylean. Retain the patch for
developers who want the example in their ordinary suite. An upstream proposal
has low priority until a maintainer wants that integration. The next separate
item is the already-scoped source review of a previously reported checker
disagreement. It is READY and unstarted. [Frontier plan](../../../docs/research/DISCOVERY_AND_CONFORMANCE_PLAN.md)

## What actually ran

| Entry point | Observed result | Attempt |
| --- | --- | --- |
| Original suite, Arena test root | Collection showed the empty parameter placeholder `case0`. Requesting the full case ID returned exit 4, “not found”. | 01–02 |
| Original checker CLI | Exit 0, with 3/3 declarations checked. The CLI takes the export directly. | 03 |
| Original suite, case directory | `proof-param-ok[accept]` collected and passed. The output uses a directory-local name. | 04–05 |
| Patched suite, Arena test root | `corner-cases/proof-param-ok[accept]` collected and passed. The original directory override also passed. | 17–18, 20–21 |
| Patched suite, missing selected export | The same descriptor in a temporary tree without the export produced exit 1. The diagnostic named the case and both possible input locations. | 22 |
| Patched suite, absent optional checkout | Five collector checks passed. The one optional Arena test skipped with a reason. | 19 |
| Full upstream suite with the pinned Arena root | 816 passed and one expected failure. The focused module had six passes, including the real shared case. | 18, 23 |

Each attempt records its command, working directory, explicit environment,
collector source hash, exit status, elapsed time and complete combined output.
The fixed comparison used rpylean `0ddcb018`, Arena `ef915093` and PyPy 8.0.1.
The 2,961-byte export's SHA-256 is
`7f9b3c07a64b441f8dd0f7dd2912274241fdb17118953fb089f796fdd1590af4`.
The 113 Arena descriptions counted at planning time are outside the verdict
denominator. [Pinned inputs and tools](work-record.json) · [Raw attempts](runs.json)

## Reproduce the comparison

Use checkouts of the two exact revisions above, with rpylean's normal PyPy and
`just` setup. From the rpylean checkout set `ARENA` to the absolute path of
the Arena checkout and `LAB` to the absolute path of this Lab checkout. These
are the two working invocations, before and after applying the local patch.

```sh
LKA_TESTS_DIR="$ARENA/tests/corner-cases" just test -v \
  'tests/test_lka_arena.py::test_arena_outcome[proof-param-ok[accept]]'

git apply "$LAB/results/research/rpylean-arena-fixture-collection-1/collector.patch"
LKA_TESTS_DIR="$ARENA/tests" just test -v \
  'tests/test_lka_arena.py::test_arena_outcome[corner-cases/proof-param-ok[accept]]'
```

The change names one nested regression. It uses Arena's declared file for
that shared case and preserves the directory in a prebuilt export's path.
Synthetic inputs cover colliding basenames, a top-level fixture, a missing
export, and both possible verdicts for an `either` expectation. Large corpora
and other nested cases retain their existing coverage. [Collector patch](collector.patch)

Two clean source checkouts and an existing PyPy installation sufficed for
setup. The patched selected test took 0.42 seconds including startup. The full
upstream suite took 7.83 seconds including its tutorial-cache check. The 23
recorded commands totaled 21.91 seconds. These single-run timings describe
this host. They exclude checkout preparation and Lab closure validation.

Independent review identified a draft path-resolution regression. Attempt 09
reproduced it, and attempts 12 and 20 verified the correction. Attempt 16
stopped during tutorial collection when the sandbox prevented a cache check.
Attempt 23 reached the upstream suite with network access. The intermediate
diffs preserve the exact tested collector versions, including the failed one.
[First draft](first.patch.gz) · [Reviewed draft](reviewed.patch.gz) · [Version hashes](result.json)
