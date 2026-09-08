# Exact upstream source whitespace

A read-only `git diff --no-index --check /dev/null` preflight on the copied
`evidence/pinned-nanoda/src/tc.rs` reported ten original trailing-whitespace
lines (5, 6, 158, 172, 181, 357, 541, 659, 722, 1035; exit 3).
Those are byte-exact upstream evidence, not edited Lab source. The original
output was shown in the tool transcript; this note records the diagnosis.

The local `.gitattributes` excludes only `evidence/pinned-nanoda/**` from
whitespace lint. Its content remains enforced byte-for-byte against the
historical donor bindings by `source-lock.json` and the proposal validator.
The source was not reformatted, and whitespace checks on Lab code and prose
remain enabled. The same read-only diff preflight then passed.
