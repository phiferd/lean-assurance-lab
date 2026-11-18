# Decide whether Arena can use a released rpylean repair

**What did we find?** At Julian’s cited source revision, the untranslated
checker rejected two disputed files and accepted a valid control. The Arena
results inspected on November 18 used an earlier checker. Whether a suitable
release or Arena update already exists remains open.

**Is it interesting?** Yes. Arena runs the translated executable and asks
maintainers to update checker releases manually. Updating a stale pin could
change the verdicts users see for real cases.

**Does it require more work?** Check the newest appropriate published release,
its ancestry, Arena’s current descriptor and pending updates. This item is
READY and unstarted. [Verification](../../results/research/rpylean-published-three-case-verification-1/report.md)
· [Arena’s release-update instructions](https://github.com/leanprover/lean-kernel-arena/blob/ef915093da536931892f1bfdaffb2a2d59529fe7/README.md#L220)

## Decision and stopping conditions

Record the release tag, its resolved commit, the relationship to
`a31ca02a158b9aabeb040b9984c21b1f4c8e3216`, and a dated read-only check of
Arena’s checker descriptor, any equivalent pending update, and published
results. If Arena already has an equivalent update or no suitable release
contains the change, record that disposition and stop.

For an eligible unrepresented release, check the translated executable through
Arena’s existing entry point with an already identified valid control. Bind
the source, build or distributed binary, control bytes and expected outcome
before execution. Deliver a local one-file descriptor candidate if the
version and smoke check support it. Otherwise record the specific build or
compatibility evidence and resulting maintenance decision. A successful smoke
check covers that control only. Any external submission remains a separate
owner decision.
