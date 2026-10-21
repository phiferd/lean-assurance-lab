"""Audit exact-profile cells and the declared diagnostic-only control replay."""
import hashlib,json
from pathlib import Path
P=Path(__file__).resolve().parent
rows=json.loads((P/'observations/executions.json').read_text());assert len(rows)==2
assert [(r['case'],r['raw_exit_code'],r['wrapper_exit_code']) for r in rows]==[('candidate',101,1),('control',0,0)]
err=(P/'observations/candidate/stderr.log').read_text()
assert 'src/tc.rs:579:13' in err and 'assertion failed: self.ctx.all_uparams_defined(l, declar_info.uparams)' in err
assert 'thread_0' in err or 'thread_1' in err or 'thread_2' in err or 'thread_3' in err
assert 'src/tc.rs:173:26' in err and 'panicked while being joined' in err
assert (P/'observations/control/stderr.log').read_bytes()==b''
assert (P/'observations/control/stdout.log').read_bytes()==b''
d=json.loads((P/'observations-control-diagnostic/executions.json').read_text());assert len(d)==1
assert d[0]['raw_exit_code']==d[0]['wrapper_exit_code']==0
assert (P/'observations-control-diagnostic/control/stdout.log').read_text().strip()=='Checked 1 declarations with no typechecker errors, 1 pretty printer errors: [\n    \"Unable to print axioms\",\n]'
assert (P/'observations-control-diagnostic/control/stderr.log').read_bytes()==b''
a=json.loads((P/'config.json').read_text());b=json.loads((P/'config-diagnostic.json').read_text());assert b.pop('print_success_message') is True and a==b
m=json.loads((P/'build-manifest.json').read_text());assert len(m['sources'])==34
for case in json.loads((P/'cases.json').read_text()):assert hashlib.sha256((P/'inputs'/(case['id']+'.ndjson')).read_bytes()).hexdigest()==case['sha256']
r=dict(evidence_class='E0',outcome='NO_SIGNAL',compatibility='PASS',configured_profile_cells=2,diagnostic_pretty_printer_warnings=1,diagnostic_only_control_replays=1,actual_checker_launches=3,checker_elapsed_seconds=sum(r['elapsed_seconds'] for r in rows+d),binary_sha256=m['binary_sha256'],arena_revision=(P/'arena-revision.txt').read_text().strip(),nanoda_revision='e0d76f5ec30bba244023466875b4845a57fd3ea5',interpretation='The fixed known candidate reaches the expected parameter guard under configured parallel/stdin profile; the control succeeds, with explicit completion visible in the logging-only replay. No unexpected validity behavior, defect or E1/E2 claim; one separate pretty-printer warning retained.')
(P/'result.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
