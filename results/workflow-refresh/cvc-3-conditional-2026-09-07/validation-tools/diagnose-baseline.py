"""Reproduce transcript incompatibilities offline; never an acceptance audit."""
import hashlib, json, re, sys
from pathlib import Path
root=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(root))
from lib import cvc_a7_audit as audit
p=root/'results/research/conditional-validation-contracts/cvc-3-conditional/run-0001/attempts/02/stdout'
raw=p.read_text()
assert hashlib.sha256(p.read_bytes()).hexdigest()=='213b11ae530344b01cf07378639ae171b116d3880509a13c6b1f87becc724bda'
def failure(call):
    try: call()
    except ValueError as e: return str(e)
    raise AssertionError('Expected frozen parser rejection')
first=failure(lambda:audit.audit_baseline(raw,''))
assert first=='malformed full axiom list'
pattern=re.compile(r"^'([^\n]+)' depends on axioms:\s*(\[[^\]]*\])[ \t]*$",re.M)
reports=list(pattern.finditer(raw)); assert len(reports)==2
names={m[1]:re.sub(r'\.\{[^{}]*\}','',m[2][1:-1]).split(',') for m in reports}
names={name:[x.strip() for x in values] for name,values in names.items()}
assert set(names)==set(audit.COMPARATORS) and all(set(v)==set(audit.A7) and len(v)==7 for v in names.values())
types=pattern.sub('',raw)
second=failure(lambda:audit._types(types))
assert second=='missing, duplicate, or malformed type report'
wrapped=re.sub(r'\.\{u_1,\s*\n\s*u_2\}', '.{u_1, u_2}', types)
third=failure(lambda:audit._types(wrapped))
assert third=='unclaimed type preamble'
first_header=wrapped.index('@Lean.Level.isEquiv\'_wf :')
preamble=wrapped[:first_header]
assert len(re.findall(r'^Baseline\.lean:\d+:\d+: warning:',preamble,re.M))==9
pairs=audit._types(wrapped[first_header:])
assert len(pairs)==9
print(json.dumps({'status':'DIAGNOSTIC_ONLY_NOT_BASELINE_ACCEPTANCE','stdout_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),
 'replayed_frozen_error':first,'next_error_after_axiom_report_removal':second,'next_error_after_header_whitespace_diagnostic':third,
 'source_positioned_warnings':9,'preamble_bytes':len(preamble.encode()),'diagnostic_axiom_declaration_names':names,
 'whitespace_normalized_type_pairs_equal':len(pairs),'raw_evidence_changed':False,
 'interpretation':'All transformations are diagnostic in memory. The original terminal FAILED audit remains unchanged; no Lab proof or baseline success is claimed.'},indent=2))
