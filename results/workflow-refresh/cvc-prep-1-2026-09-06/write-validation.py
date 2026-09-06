#!/usr/bin/env python3
"""Summarize retained commands without erasing failed engineering/execution records."""
import datetime,hashlib,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
rows=[]
for path in sorted(OUT.glob('[0-9][0-9]-*.json')):
 row=json.loads(path.read_text());log=ROOT/row['log']
 assert hashlib.sha256(log.read_bytes()).hexdigest()==row['log_sha256'],path
 row={'record':str(path.relative_to(ROOT)),**row};rows.append(row)
required=['01-historical','03-predecessor','04-snapshot','12-controller-tests','15-stop-regression',
          '16-full-unit-suite','17-contribution','20-final-queue-tests','24-refresh','26-project-review',
          '27-artifact-status','28-final-queue','29-evidence-final','30-final-handoff','31-diff']
for name in required:
 assert json.loads((OUT/(name+'.json')).read_text())['status']=='PASS',name
suite=(OUT/'16-full-unit-suite.log').read_text();counts=[int(n) for n in re.findall(r'^Ran (\d+) tests in ',suite,re.M)]
assert counts==[402,73] and not re.search(r'^OK \(skipped=',suite,re.M)
known_failures={'07-source-review':'Initial extractor did not filter core-runtime rows; fixed before checkpoint, final source extraction passed.',
                '10-controller-tests':'Initial integration exposed missing fresh-workspace parent handling and unavailable ps fixture inspection; corrected before checkpoint.',
                '11-controller-tests':'Socket-based fixture inspection unavailable in the sandbox; replaced with FIFO EOF before checkpoint. Process control was tested without network access.',
                '14-preparation-run':'Authorized research stopped BOUNDED_UNRESOLVED on the characterized Path/string ordering defect after27 successful compilations. This failure is preserved, not relabeled a passing build.'}
for row in rows:
 if row['status']=='FAIL':assert Path(row['record']).stem in known_failures
assurance=json.loads((ROOT/'results/assurance/current.json').read_text())
assert assurance['gate']['status']=='FAIL' and assurance['gate']['checks']['semantic_checker_disagreements']['observed']['unresolved']==15
result={'schema_version':1,'item_id':'CVC-PREP-1','date':'2026-09-06','status':'PASS','research_outcome':'BOUNDED_UNRESOLVED',
        'required_final_checks':required,'commands':rows,'preserved_nonpassing_records':known_failures,
        'unit_suite':{'current_tests':402,'historical_tests':73,'total':475,'skips':0,'historical_transition_and_tampering_regressions':'INCLUDED_AND_PASSING'},
        'prelaunch_receipt_correction':'20 controller tests and8 runtime tests passed. The checkpoint receipt said9 runtime tests; original bytes and raw log remain, with a separate prelaunch-receipt-erratum.json.',
        'preserved_assurance_boundary':{'status':'FAIL','unresolved_semantic_disagreements':15,'change':'UNCHANGED'},
        'refresh':{'status':'PASS','record':str((OUT/'refresh/result.json').relative_to(ROOT))},
        'research_execution_note':'27 upstream module compilations only;119 products verified,10 modules unstarted. No Lab elaboration, proof, checker, Lake, native compiler, download or external message. CVC-PREP-2 is selected READY and has not started.',
        'completed_at':datetime.datetime.now(datetime.timezone.utc).isoformat()}
(OUT/'validation.json').write_text(json.dumps(result,indent=2)+'\n')
print('PASS: required checks,475 full-payload tests and preserved bounded-unresolved research result')
