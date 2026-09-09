# Declaration-checking thread configuration survivor assessment

Frontier `F-SURVIVOR-THREAD-CONFIG-REACHABILITY`; bounded item
`SURVIVOR-THREAD-CONFIG-REACHABILITY-1`. This successor may start only after
`SURVIVOR-FVAR-REACHABILITY-1` closes and a project-wide review selects it.

## Question and useful result

Determine the exact public configuration states and declaration-checking
behavior changed by `nanoda-gen-2bdfe18a9ec2` and
`nanoda-gen-93b21593b0d8` at pinned Nanoda `check_all_declars`. Trace config
validation, zero/one/many-thread dispatch, task coverage, fresh checker state,
panic/error propagation and stack-size differences. A useful result is one
source-supported configuration counterexample, a scoped equivalence result, or
a precise operational boundary. Do not infer meaning from either historical
187-test no-difference result alone.

## Finite gate and stop

One source-only item of at most 3,600 active seconds. Reuse the pinned source,
both mutation identities, historical comparisons and current survivor state.
Run zero build, checker, proof, network or external-action launches and generate
no scientific export bytes. Stop after one exact reachability/exclusion result,
one named unclosed operational boundary, or the active-time cap. Any execution
proposal is a separate successor and must freeze exact configuration, bytes,
expected outcomes, controls, runtime and tooling before launch.
