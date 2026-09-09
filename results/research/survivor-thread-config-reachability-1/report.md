# Thread-configuration survivor reachability result

The two mutations are not equivalent as public configuration dispatches.
Pinned Nanoda accepts `num_threads = 0`, and omission deserializes to zero. The
baseline then checks every declaration serially. `nanoda-gen-93b21593b0d8`
instead enters `check_all_declars_par(0)`: it constructs no workers, invokes
`check_declar` zero times, returns normally, and lets the binary proceed to
pretty printing and optional “Checked … with no errors” reporting.

This is a concrete source-level semantic distinction. The already admitted
601-byte 21ef candidate is known to parse and reach a baseline declaration
rejection. Under the negated predicate with a valid zero-thread configuration,
the declaration is not examined. No new configuration, export, build, checker,
proof, network or external-action launch was made here. The canonical registry
therefore records the mutation as `MEANINGFUL_SEMANTIC` while retaining its
historical `SURVIVED` status; this is not a corpus-kill claim or semantic
authority.

`nanoda-gen-2bdfe18a9ec2` differs only at `num_threads = 1`. In the successful,
non-panicking case, its single worker claims declaration indices in order and
checks each exactly once, matching serial task coverage. It nevertheless uses
a named spawned thread with an explicit 16 MiB stack, adds a spawn failure
surface, and converts worker panics through the join expectation. Those
resource and failure-propagation differences prevent a scoped equivalence
claim, but this item did not establish a normalized checker-outcome witness.
Its `SURVIVED_WITHOUT_WITNESS` classification remains unchanged.

The next selected item is `SURVIVOR-THREAD-CONFIG-REGRESSION-1`, READY and
unstarted. It should bind the existing invalid candidate and matching control,
zero-thread configuration bytes, exact binaries/runtime and strict accounting,
then run controls before candidates. No external report is supported before
that local regression.
