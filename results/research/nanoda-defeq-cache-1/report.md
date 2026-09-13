# Eager-mode negative-cache assessment

`NANODA-DEFEQ-CACHE-1` closes **BOUNDED_UNRESOLVED**. Current Nanoda
`4c544ed4099c8227f07d5de77ad1e69fb0740a27` contains the ordered
`(x, y, eager_mode)` failure key introduced by `0928383` / PR #31, but this
source-only assessment does not establish an identical-pair, same-context
false-to-true sequence. No checker defect, mode equivalence, executed test or
public-import reachability is claimed. No scientific process was launched.

The useful output is a source-bound exclusion of several tempting but invalid
regression designs, a complete static suite audit, and the exact remaining
entry conditions. The Boolean eager shortcut and asymmetric closed/open Nat
route remain unresolved beyond the exclusions below. Expanding into a proof of
all recursive calls would require a distinct scoped investigation.

## What the source actually establishes

The complete retained Git tree is bound in `source-lock.json`; its tip was
independently refreshed through the GitHub connector. `pr31-change.patch`
retains the original five-file change. It adds the failure cache, initializes
and clears it with the checker caches, and adds no tests. Source references
below refer to that fixed tree; `current-tc.rs.txt` and `current-util.rs.txt`
retain the principal files for convenient inspection.

1. `src/tc.rs:957–1009`: `def_eq_quick_check` runs before the new failure
   lookup. The ordered input pair and entry eager flag are captured before
   normalization. Only a false result reaching the final result block inserts
   this key. Pointer equality, sort and binder checks, the Boolean shortcut,
   and the normalized quick check can return earlier. A false assertion alone
   does not prove that the cache was exercised.
2. `src/tc.rs:1177–1189`: the positive equality cache precedes negative lookup.
   A success that reaches the final insertion block records a mode-independent
   sorted pair. Reversing an eager-success/lazy-failure experiment in the same
   checker can therefore mask the intended distinction. The eager Boolean
   shortcut returns directly and does **not** itself insert a positive entry;
   inspect actual cache membership rather than assuming all successes warm it.
3. `src/tc.rs:393–440, 1255–1267`: eager mode relaxes a *pair-level* condition
   around native Nat reduction. `try_reduce_nat` independently refuses every
   expression whose stored `has_fvars` is true. Toggling eager mode cannot make
   that helper natively reduce the same open expression. With both sides open
   the newly allowed helper calls both refuse; with both sides closed the outer
   gate is already enabled in either mode. With exactly one open side, eager
   mode can try reduction of the closed side: this is a real strategy difference,
   not by itself a Boolean-outcome witness.
4. `src/tc.rs:968–973, 758–785, 1274–1318`: eager mode can force WHNF of an
   open left side when the normalized right side is exactly cached `Bool.true`.
   WHNF itself has no direct eager-mode branch. It uses ordinary reduction,
   guarded native reduction and definition unfolding. Lazy delta also unfolds
   definitions, and later full projection/eta/proof rules can settle equality.
   Showing that the early shortcut fires does not show that the lazy result is
   false. The remaining task is to isolate a terminating well-typed example
   where the later path cannot independently find the equality.
5. `src/tc.rs:556–582`, `src/expr.rs:554–561`: checked application inference
   sets eager mode for an `eagerReduce` argument, compares binder type on the
   left with argument type on the right, and restores the outer mode after the
   successful comparison. A caught assertion panic bypasses restoration. Using
   a checker after such a panic would require separately justified recovery
   semantics; it is not the proposed normal same-context control.
6. `src/util.rs:830–869`: `TcCache::new` makes the failure set empty and
   `clear` empties it. Recreating the checker between warm-up and candidate, or
   clearing its caches, destroys the history whose effect is under study.

These are local code-path statements. For example, closed expressions can
introduce locals during binder comparison; the closed-pair observation is not
an induction over arbitrary recursive definitional equality. Neither checker
agreement nor this source review establishes a universal Lean obligation.

## Coverage and reuse

The independent review inventories 38 active unit-test attributes: 13 level,
4 name, 16 direct BigUint helpers, 3 utility tests and 2 parser version tests.
Eight documentation examples are ignored. The later TypeChecker Nat examples
in `src/tests/natlit.rs` are commented out; their missing Init fixture cannot
supply executable coverage. No direct test sets eager mode or inspects the new
failure cache. This is a static assertion/wiring audit, not a test run or a
claim that no indirect path ever exercises the cache.

The prior inference-cache regression provides same-checker fixture and cache
membership assertion patterns. Its checked/unchecked inference distinction is
a different contract and its malformed-let witness cannot establish eager-mode
definitional-equality sensitivity. The recent dispatcher patch is useful setup
reuse but calls `try_reduce_nat` directly and therefore cannot settle this key's
caller-level contract. Both prior results remain unchanged.

## Recommendation and next step

Prioritize `ARENA-INDUCTIVE-ISOLATION-1`, the independently READY four-case
shared-corpus audit, ahead of further speculative cache execution. Its bound
inventory and prior complete-recursor contribution provide a concrete route to
shared regression value. Select it without starting it.

For Nanoda maintainers, retain this assessment locally and prepare no PR or
implementation issue now. A future mode-sensitive regression needs an exact
well-typed environment and pair, a demonstrated source path to differing
outcomes, proof that the first failure inserts the targeted key, fresh-mode
controls, unchanged expression pointers/context, and inspection of confounding
positive/congruence/WHNF caches. Freeze the source, patch, expected cells,
finite build/test budget, tools and process accounting before any launch.

An ordinary negative-cache insertion/clear unit test could protect its recorded
lifecycle, but it would not answer this assessment's semantic mode-history
question. No additional queue item is manufactured for that implementation-
shaped test absent a stronger maintenance need. Reconsider the remaining cache
route if a concrete retained failing sequence or substantive upstream request
supplies the missing discriminator. Existing local Nanoda drafts remain held
under their separately recorded capacity/preflight/approval conditions.
