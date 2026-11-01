# Pestka recursor rule-owner pilot

Pestka accepted both valid inputs and rejected the invalid recursor rule association. Both valid inputs checked all ten declarations, with zero admitted unchecked and zero skipped. The candidate was rejected as `LALNest: invalid recursor 'LALNest.rec_1'`. All three runs completed without timeout or stderr.

This is useful coverage evidence for this particular check, with no acceptance discrepancy found. It is a known-informed transfer test, not a new vulnerability or independent discovery. No result-driven follow-up is required; no successor was launched.

## Reproduction and interpretation

Pestka source `d584d4bee7114aa34e456bb3b80cb74f906c62b2`, Aver `9ecd7b4675c53e500fbd15f05c5a444a28924615`, Rust 1.99.0, Linux x86_64. Build commands and lock files are retained. The binary is a new exact-source build, not recovered historical bytes. The registered runner invokes `pestka.bin <fixture> 1` using Pestka's default original core and one worker, with 30 seconds and 4 GiB per process.

The three files are unchanged from the published Kefir pilot. Independent ownership expectation comes from the declared inductive blocks; the candidate changes only record 119, `LALNest.rec_1.rules[0].ctor`, from `LALWrap.mk` to unrelated `LALMarker.mark`. It retains the downstream reduction theorem. `fixture-check.json` rechecks the one-field difference; the earlier frozen fixture audit binds name ownership and consumer meaning. Source `indadd.av` derives/restores recursors, compares them and rejects mismatched rule constructor identities. Thus this is attributed rejection, rather than a decline, assertion failure or parser refusal. The invalid consumer is not admitted after rejection.

`protocol.json` freezes inputs before execution; `start.json` and the append-only ledger register the three cells. `attempts/` contains exact argv, exit codes, stream hashes and bytes. `result.json` summarizes observations. Acceptance by the controls and rejection of this one candidate do not establish general soundness. The alternative next core, other mutations and general historical assurance are untested here.

Only E0 records are delivered. The isolated execution context closes this campaign and restores the existing pending E1 selection unstarted; public E1/global assurance artifacts remain pending and unchanged. Preserved unpublished E1 history and its recovery bundle remain separate.
