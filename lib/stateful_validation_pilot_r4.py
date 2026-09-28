"""R4 enforces exact generation provenance and adopts the unchanged R3 fixtures.

R3 code/manifests/bytes remain historical. This live revision disables further
generation and requires separately reviewed, committed adoption before science.
"""
import argparse
import json
from pathlib import Path
import sys
from lib import stateful_validation_pilot_r3
from lib import stateful_validation_pilot as p

p.TOOLING = [*p.TOOLING,'lib/stateful_validation_pilot_r4.py',
             'scripts/stateful-validation-pilot-r4','tests/test_stateful_validation_pilot_r4.py']
GEN=p.BASE/'generation-manifest.json'
ADOPTION=p.BASE/'adoption-manifest-r4.json'
ADOPTED=p.BASE/'artifact-adoption-r4.json'
ADOPT_REVIEW=p.BASE/'adoption-review-r4.json'
INCIDENT=p.BASE/'generation-control-incident.json'
COMPILE=p.BASE/'compile-0003/result.json'
_old_execution_inputs=p.execution_inputs
_old_freeze_execution=p.freeze_execution

def validate_generation_manifest(m):
    """Check original generation under its original R3 bindings, not current tooling."""
    p.source_check(); p.scientific_review(); doc=p.read(p.CONTRACT)
    p.audit.audit_contract(doc)
    original=p.read(p.BASE/'compile-manifest-r3.json')
    review=p.read(p.BASE/'tooling-review-r1.json')
    p.require(review['verdict']=='PASS' and review['tooling']==original['tooling'] and
              review['reviewed_compile_manifest']==p.bind(p.BASE/'compile-manifest-r3.json') and
              review['compile_evidence']==p.bind(COMPILE),'original generation review binding differs')
    expected=dict(item_id=p.ITEM,stage='GENERATION',contract=p.bind(p.CONTRACT),source=p.bind(p.SOURCE),
        scientific_review=p.bind(p.BASE/'scientific-review.json'),tooling_review=p.bind(p.BASE/'tooling-review-r1.json'),
        tooling=original['tooling'],cells=p.cells(doc))
    p.require(m==expected,'original generation manifest differs from exact canonical R3 bindings')
    for row in [m['contract'],m['source'],m['scientific_review'],m['tooling_review'],*m['tooling']]: p.verify(row)
    compile_result=p.read(COMPILE); p.verify(compile_result['manifest'])
    receipt=compile_result['receipt']
    p.receipt_custody(receipt,(p.ROOT/receipt['raw_stdout_path']).read_bytes(),(p.ROOT/receipt['raw_stderr_path']).read_bytes(),doc['controls'])
    p.require(compile_result['status']=='PASS' and receipt['exit_code']==0,'successful generic compile missing')
    return expected

def original_artifacts():
    doc=p.read(p.CONTRACT); p.audit.audit_contract(doc)
    validate_generation_manifest(p.read(GEN))
    record=p.read(p.BASE/'artifact-audit.json')
    p.require(set(record)=={'generation_manifest','rows'} and record['generation_manifest']==p.bind(GEN),'artifact generation provenance differs')
    expected=p.cells(doc)
    p.require(len(record['rows'])==len(expected),'artifact inventory count')
    for row,cell in zip(record['rows'],expected):
        p.require(set(row)=={'comparison','side','fixture','audit'} and row['comparison']==cell['comparison'] and
                  row['side']==cell['side'] and row['fixture']==p.bind(Path(cell['path'])),'artifact identity/order/hash differs')
        checked=p.audit.audit_fixture(p.verify(row['fixture']).read_bytes(),doc,cell['comparison'],cell['side'])
        p.require(checked==row['audit'],'original independent object audit differs')
    return doc,record

def adoption_value():
    doc,record=original_artifacts()
    return dict(item_id=p.ITEM,stage='ADOPT_UNCHANGED_ARTIFACTS',revision='R4',
       contract=p.bind(p.CONTRACT),source=p.bind(p.SOURCE),scientific_review=p.bind(p.BASE/'scientific-review.json'),
       original_generation=p.bind(GEN),original_artifact_audit=p.bind(p.BASE/'artifact-audit.json'),
       compile_result=p.bind(COMPILE),incident=p.bind(INCIDENT),tooling=p.tooling(),
       fixtures=[r['fixture'] for r in record['rows']],cells=p.cells(doc),
       disposition='Preserve and adopt exact existing scientific bytes after stronger canonical custody validation; no regeneration or scientific-input replacement.')

def validate_adoption_manifest(m):
    p.require(m==adoption_value(),'adoption manifest is not exact current reviewed inventory')
    return m

def adoption_inputs(m):
    return [m[k] for k in ['contract','source','scientific_review','original_generation','original_artifact_audit','compile_result','incident']]+m['tooling']+m['fixtures']

def freeze_adoption():
    p.active(); p.write_new(ADOPTION,adoption_value()); return p.bind(ADOPTION)

def adopt():
    p.active(); m=validate_adoption_manifest(p.read(ADOPTION)); review=p.read(ADOPT_REVIEW)
    p.require(review['verdict']=='PASS' and review['manifest']==p.bind(ADOPTION) and
              review['both_independent_reviewers_pass'] is True,'both exact adoption reviews required')
    p.committed([p.bind(ADOPTION),p.bind(ADOPT_REVIEW),*adoption_inputs(m)])
    _,record=original_artifacts()
    p.write_new(ADOPTED,dict(item_id=p.ITEM,status='PASS',manifest=p.bind(ADOPTION),review=p.bind(ADOPT_REVIEW),
       fixtures=[r['fixture'] for r in record['rows']],generation_provenance=p.bind(GEN),
       original_audit=p.bind(p.BASE/'artifact-audit.json'),new_scientific_bytes=0,
       prior_gate_assessment='Earlier protocol PASS is superseded for guard enforceability; original actual bytes are independently revalidated and retained unchanged.'))
    return p.bind(ADOPTED)

def artifacts():
    doc,record=original_artifacts(); m=validate_adoption_manifest(p.read(ADOPTION))
    adopted=p.read(ADOPTED); review=p.read(ADOPT_REVIEW)
    p.require(adopted['item_id']==p.ITEM and adopted['status']=='PASS' and adopted['manifest']==p.bind(ADOPTION)
      and adopted['review']==p.bind(ADOPT_REVIEW) and adopted['fixtures']==m['fixtures'] and adopted['new_scientific_bytes']==0
      and adopted['generation_provenance']==p.bind(GEN) and adopted['original_audit']==p.bind(p.BASE/'artifact-audit.json'),'adoption receipt differs')
    p.require(review['verdict']=='PASS' and review['manifest']==p.bind(ADOPTION) and review['both_independent_reviewers_pass'] is True,'adoption review differs')
    return doc,record

def freeze_execution(revision):
    p.require(revision=='r4','only repaired R4 execution permitted'); p.active(); doc,record=artifacts()
    value=dict(item_id=p.ITEM,stage='EXECUTION',revision='r4',contract=p.bind(p.CONTRACT),source=p.bind(p.SOURCE),
       generation=p.bind(GEN),artifact_audit=p.bind(p.BASE/'artifact-audit.json'),
       fixtures=[r['fixture'] for r in record['rows']],tooling=p.tooling(),cells=p.cells(doc),controls=doc['controls'],
       environment=p.environment(Path(p.read(p.SOURCE)['runtime_root'])),scientific_review=p.bind(p.BASE/'scientific-review.json'),
       adoption=p.bind(ADOPTED),adoption_manifest=p.bind(ADOPTION),adoption_review=p.bind(ADOPT_REVIEW))
    p.write_new(p.BASE/'execution-manifest-r4.json',value); return p.bind(p.BASE/'execution-manifest-r4.json')

def validate_manifest(m):
    p.source_check(); doc,record=artifacts()
    expected=dict(item_id=p.ITEM,stage='EXECUTION',revision='r4',contract=p.bind(p.CONTRACT),source=p.bind(p.SOURCE),
       generation=p.bind(GEN),artifact_audit=p.bind(p.BASE/'artifact-audit.json'),
       fixtures=[r['fixture'] for r in record['rows']],tooling=p.tooling(),cells=p.cells(doc),controls=doc['controls'],
       environment=p.environment(Path(p.read(p.SOURCE)['runtime_root'])),scientific_review=p.bind(p.BASE/'scientific-review.json'),
       adoption=p.bind(ADOPTED),adoption_manifest=p.bind(ADOPTION),adoption_review=p.bind(ADOPT_REVIEW))
    p.require(m==expected,'execution manifest differs from repaired exact canonical contract')
    return doc

def execution_inputs(m):
    return [*_old_execution_inputs(m),m['adoption'],m['adoption_manifest'],m['adoption_review'],p.bind(INCIDENT),p.bind(COMPILE)]

def refuse_generation():
    raise ValueError('R4 adopts the unchanged existing scientific inputs; further generation is disabled')

p.artifacts=artifacts
p.validate_manifest=validate_manifest
p.freeze_execution=freeze_execution
p.execution_inputs=execution_inputs
p.generate=refuse_generation
p.freeze_generation=refuse_generation

def main():
    parser=argparse.ArgumentParser(); parser.add_argument('action',choices=['freeze-adoption','adopt','freeze-execution','execute','replay'])
    parser.add_argument('--attempt',default='execution-0001'); args=parser.parse_args()
    if args.action=='freeze-adoption': result=freeze_adoption()
    elif args.action=='adopt': result=adopt()
    elif args.action=='freeze-execution': result=freeze_execution('r4')
    elif args.action=='execute': result=p.execute('r4',args.attempt)
    else: result=p.replay(p.BASE/args.attempt/'result.json')
    print(json.dumps(result,indent=2))
    if result.get('status')=='REPAIR_REQUIRED': sys.exit(1)

if __name__=='__main__': main()
