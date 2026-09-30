What did we find? All six exploratory screens found no missed semantic or
intended-target detection in their declared samples. The final observations
contain 34 accepts and six expected ill-typed rejections across 40 checker runs.
Two real proof slices transferred to both LazyLean engines with fresh official
Lean accepts. The data-recursion cases finally exercised alias unfolding and
branch selection. Three sharing pairs agreed, but the loader merged duplicated
expressions, so persistent runtime sharing was not tested. Lean4Lean emitted
environment-extension panics while formatting all three type-mismatch errors;
it still rejected those inputs. No correctness or general completeness claim
follows from this small exploratory sample.

Is it interesting? Yes, modestly: the campaign supplies reusable demanded
reduction fixtures, exact real-library compatibility observations, and invalid
and substituted-target controls. It also makes a practical diagnostic weakness
visible. Agreement between checkers supplies no semantic authority, and the
two LazyLean profiles share one implementation.

Does it require more work? No semantic confirmation or external action follows
from these six no-signal screens. Retain their fixtures and failures. Select a
separate source-only Lean4Lean diagnostic-panic triage READY and unstarted: its
target is the exact retained error-formatting route and its purpose is to decide
whether a small regression or fresh confirmation is useful. That follow-up is
driven by the incidental diagnostics, not invalid-proof acceptance. Memory
accounting remains deferred; independent holdout transfer retains its input gate.

| Trial | Final observations | Scope and outcome |
| --- | --- | --- |
| Data recursion | Eight accepts; KAM candidate delta/iota counts 1/1 and 4/1 at depths 1 and 4; controls zero | NO_SIGNAL; two-constructor data, same implementation |
| Serialized expression sharing | Twelve accepts with conversion demand; beta 1, zeta let 2, nested beta 2 in KAM | NO_SIGNAL; expanded roots equal; duplicated nodes merged on loading |
| Proof transfer A | Official Lean, LazyLean subst and KAM accept `Nat.lt_of_succ_le` | NO_SIGNAL; unchanged 15,070-byte init-04 slice |
| Proof transfer B | All three accept `Nat.add_assoc` | NO_SIGNAL; unchanged 48,333-byte init-01 slice |
| Invalid targets | Both baseline accepts; six rejections at first/middle/last target positions; sentinel flags changes | NO_SIGNAL for missed detection; Lean4Lean formatting panics retained |
| Substituted targets | Six accepts; sentinel distinguishes same-name changed proposition and renamed target | NO_SIGNAL for missed substitution; accepting valid supplied objects is expected |

The independent target sentinel compares the checked artifact with the intended
declaration identity and statement. Its detection result is distinct from a
kernel acceptance or rejection. A valid replacement can pass a checker while
failing that identity comparison. The invalid first/middle/last positions use
the twelve-theorem baseline and preserve dependency ordering.

All 48 actual checker launches, including eight construction-failure cells,
have verified raw-stream hashes, positive monitored memory observations and
complete cleanup; none hit the configured timeout or memory limit. Three
sandbox monitor preflights failed before child launch and were retried on the
host. The first data fixture used the wrong recursor elimination universe:
four controls accepted and four candidates had type mismatches. A retained
revision fixes that universe argument within the unchanged question. The first
classifier returned output-contract failure for its multiline diagnostic; no
semantic discrepancy was inferred. All original bytes and attempts remain.

The final sample used 40 launches; actual work used 48. Summed child elapsed
time was 3.714593 seconds, excluding construction, reasoning and administration.
Two bounded delegates handled proof transfer and target detection; the owner
handled reduction screens and all shared state. Two queue-entry schema corrections
and one finish-append count correction are administrative retries. Delivery aims
at one campaign commit; the exact delivered commit is checked separately.

The privacy-preserving usage snapshot covers 98 unique responses through
2026-09-30 22:54:56.987 UTC: 7,471,200 input tokens, of which 7,151,744 are cached
and 319,456 are derived uncached; 34,014 output tokens include 6,089 reasoning
tokens. Cache-write input is zero. It includes retained root, delegate and
automatic approval-review records for this root turn, deduplicated by response
identity. Later handoff, validation, delivery and final responses are outside
that cutoff. No monetary cost or savings estimate follows. See `model-usage.json`
for per-model totals and coverage limits, `operations.json` for deterministic
execution counts, and `evidence-inventory.json` for exact retained evidence.

This is E0 exploration only. No builds, new importer, checker source changes,
external contributions, frozen-history edits or assurance refresh occurred.
Prior real-proof accepts are dated context; the six transfer observations here
are fresh processes on reused cases, not fresh independent holdout evidence.
