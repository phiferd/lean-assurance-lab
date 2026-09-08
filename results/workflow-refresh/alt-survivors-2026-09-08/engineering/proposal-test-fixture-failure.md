# Pure proposal-test fixture repair

The first focused test invocation was
`python3 -m unittest discover -s tests -p 'test_survivor_proposal.py'`.
Tool chunk `dbd774` returned exit 1: 12 tests ran in 0.803 seconds,
with 20 subtest failures and one error. All came from the same missing
temporary-fixture input, `config/authorized-runs/triage.json`.

The full raw output remains in the tool transcript and was not separately
saved to a local log. This is a transcript diagnostic, not a reconstructed
raw log. The initial traceback's exact terminal error was:

```text
ValueError: missing evidence: config/authorized-runs/triage.json
```

The validator reads that historical manifest to compare copied source files
against their original donor bindings. The test copied only the initial
proposal evidence manifest, which omitted that prerequisite. The repair adds
the historical manifest and nested old artifact paths to the temporary test
copy. The proposal owner also added the historical manifest to the canonical
evidence bindings. No historical artifact or scientific input changed.

The next focused invocation passed all 12 tests in 0.916 seconds (tool chunk
`bbcc68`). No checker, build, network or administrative process fixture ran.
Subsequent focused tests also cover prospective historical bindings and
canonical result claims; their final receipt is retained by the closure owner.
