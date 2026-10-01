# Lean-action checker policy and failure screening

Evidence class: E0

Owner-selected 2026-10-01; supersedes the selected but unstarted PR15373 source preparation for this campaign only. Preserve it DEFERRED without executing it. Isolated copy starts at lab 6be539c; no publication authorized.

Question: do PR192 bundled/source routes emit identical axiom configurations, select the expected single module and propagate exporter/checker failures? Real behavior sample would contain clean True, standard axioms, reachable sorry with both toggle values, reachable custom axiom, and native_decide/Lean.trustCompiler. Exact advertised v4.35.0-rc2 binaries are required for bundled checker conformance. Installed older toolchains are not substitutes. Stop that subquestion INCONCLUSIVE if missing; do not download a large stack.

Complement: test PR190 unavailable features, non-Linux runner, setup errors and checker failure classification using controlled shell stand-ins; read PR191 privileged setup only. Never run sudo, AppArmor, sysctl, setuid changes or an actual Linux sandbox.

Small fixed sample: PR192 bundled/source dispatch with sorry false/true (4), exporter/checker failure (2), missing one bundled tool fallback (1); PR190 unsupported runner, unsupported help, probe failure, late bwrap failure, checker rejection, success (6). Replay PR192 no-source-build directory assertion on a deliberately forced mocked fallback. This is a test-oracle control, not checker acceptance. Every command, output and input remains retained.

Use unchanged lib/resource_envelope_supervisor.py for each shell child: 20 seconds, 512MiB, process-group cleanup; stop launches on monitoring/cleanup faults and retry on actual host only if authorized and feasible. E0 SIGNAL means a concrete failure classification or test-oracle discrepancy; NO_SIGNAL needs all relevant observations. Real axiom-path measurement remains INCONCLUSIVE without exact binaries. Source equality alone proves no checker conformance or kernel soundness. Fresh E1/E2 gates precede external contribution.
