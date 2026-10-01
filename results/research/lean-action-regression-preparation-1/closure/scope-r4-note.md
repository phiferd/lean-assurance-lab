# Scope dependency completeness correction

Attempt0003 failed before execution: publication dependencies must cover every declared path. Scope-r3 added repair records to paths but omitted their explicit publication dependencies. Scope-r4 includes every declared path in that dependency set, preserving all suite/status requirements and the same retained output directory. This is another avoidable declaration-preflight cost; no scientific replay or full-suite execution occurred in attempt0003. No implementation/docs changed.
