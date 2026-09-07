#!/usr/bin/env python3
"""Render this review from its canonical assessment; never touches predecessors."""
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
a = json.loads((BASE / 'assessment.json').read_text())
s = json.loads((BASE / 'successor-proposal.json').read_text())
lines = [
    '# CVC-AXIOMS-1: comparator assumption review', '',
    'Recorded 2026-09-06 (America/New_York). Outcome: **SUCCESS** for a source-only',
    'review. Decision: **SUCCESSOR**. Scientific status: `SOURCE_ASSUMPTION_REVIEW_ONLY`.',
    'No checked Lab theorem, counterexample or discharged axiom is claimed.', '',
    'The seven transitive assumptions in both retained imported comparator reports',
    'support a useful explicitly conditional successor. The omitted equality and',
    'partial-helper axioms are substantive trust conditions. The frozen CVC-2',
    'allowlist and terminal CVC-3 failure remain unchanged.', '',
    'Canonical inputs and findings: [assessment](assessment.json),',
    '[exact source excerpts](source-excerpts.json),',
    '[independent review](independent-review.json),',
    '[unexecuted successor proposal](successor-proposal.json), and',
    '[work record](work-record.json). Validate with `scripts/validate-cvc-axioms`;',
    'add `--require-full-source` to compare every slice to the retained local files.', '',
    '## Assumption table', '',
    'Every row occurs in both `Lean.Level.isEquiv\'_wf` and',
    '`Lean.Level.isEquiv\'_complete`. Exact declarations and source/context references',
    'are bound in the assessment, with a feasible discharge or replacement route.', '',
    '| Assumption | Old policy | Trust role |',
    '| --- | --- | --- |',
]
roles = [
    'Host propositional extensionality', 'Host nonconstructive choice',
    'Host quotient equality', 'Lawfulness of opaque runtime Level equality',
    'Opaque partial helper equals its total copy',
    'Opaque core normalization equals the supplied total algorithm',
    'Map-wide Boolean traversal agrees with its entry list',
]
for row, role in zip(a['assumptions'], roles):
    lines.append(f"| `{row['name']}` | `{row['previous_policy']}` | {role} |")
lines += [
    '', '`Std.TreeMap.any_eq_any_toList` was allowed previously but does not occur',
    'in either actual comparator report. It is excluded from the proposed A7 list.',
    'Other axioms present in imported source files are not automatically dependencies.',
    'Failed Lab declarations contain error-recovery `sorryAx`; those outputs are',
    'preserved as failures and supply no theorem evidence.', '',
    '## What this establishes', '', a['noncircularity'], '',
    a['dependency_evidence_scope'], '', a['provenance_limit'], '',
    'In particular, `LawfulBEq Level` promises equality of the actual Level values',
    'and reflexive Boolean equality, not just equal numerical denotations.',
    '`normalize_eq` asserts an extensional algorithm correspondence. Side-by-side',
    'source comparison does not turn either opaque runtime bridge into a proof.', '',
    'The initial attempt to find installed source hashes in the old runtime manifest',
    'failed because that manifest excludes `src/lean`. The work record preserves',
    'this diagnostic and the subsequent weaker release-source binding. No source',
    'revision was changed and no compilation was used to repair the inventory.', '',
    '## Discharge and alternatives', '',
]
for row in a['assumptions']:
    lines += [f"- **{row['name']}**: {row['discharge']}"]
lines += ['', 'The pure normal-form comparator is a credible alternative: omitting the',
          'core fast path may remove some runtime bridge dependencies. Its reduced',
          'transitive closure has not been printed, the map helper is still visibly',
          'used, and changing acceptance requires another explicit contract. The',
          'independent review supports this distinction; reviewer agreement supplies',
          'no semantic authority.', '', '## Selected next item', '',
          '`CVC-CONDITIONAL-1` is selected READY and unstarted. It prepares a new',
          'protocol/runner for model `CVC-U1-A7`, preserving the semantic signature',
          'and examples with an explicit seven-assumption envelope. Its ceiling is',
          'two 60-minute sessions and 64 supervised inert fixture launches, each at',
          'most five seconds and together at most 320 reserved seconds, including',
          'required regression fixtures. It permits no proof, dependency or observer',
          'launches, network requests or external messages.', '',
          '`CVC-3-CONDITIONAL` remains PLANNED. Only a later committed entry review',
          'can promote its new run ID. Its proposed ceiling is six counted builds',
          'in two 60-minute sessions, each build at most 300 seconds: signature,',
          'an exact imported-type/seven-axiom baseline, then normally at most four',
          'proof attempts. Failure reservations count. This is a new bounded',
          'successor, never a resumption of the old ten unused slots. Original plus',
          'proposed proof attempts are at most eight. Per-result dependencies must',
          'be printed; missing, extra, forbidden or unlisted axioms fail the gate.', '',
          'The original CVC-4 and CVC-5 remain PLANNED with unmet dependencies.',
          'A successful conditional proof would require an explicitly scoped',
          'implementation-connection successor. No upstream message is recommended',
          'now: the result identifies a Lab assumption-accounting gap, not a new',
          'implementation defect.', '', '## Scope and costs', '',
          'Six files under the existing source/release pins were allocated across',
          'the owner and independent reviewer. Their overlapping work is covered',
          'by the owner session; no separate worker elapsed total is invented.',
          'Research operations were source reads, local hashing and evidence analysis.',
          'Required repository closure tests and their instrumented inert fixture',
          'processes are separately measured in the validation record. Their costs',
          'are not proof attempts, and zero research launches does not mean zero',
          'administrative test processes.', '',
          'All previous measured costs and the unknown CVC-RUNNER-1 fixture duration',
          'remain as recorded. Normative approvals, catalog dispositions, assurance',
          'counts and historical attestations are unchanged.', '']
(BASE / 'report.md').write_text('\n'.join(lines))
