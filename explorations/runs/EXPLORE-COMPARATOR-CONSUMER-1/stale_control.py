"""Offline stale-receipt control; native Comparator has no receipt interface."""
import json
from pathlib import Path
import runpy
root=Path(__file__).resolve().parent
m=runpy.run_path(str(root/'check_observations.py'))
expected=json.loads((root/'reference-expectation.json').read_text())
r=m['check'](root/'observations/baseline-r3',expected,'fresh-execution-required')
r.update(native_run='NOT_INVOKED_RECEIPT_INTERFACE_ABSENT',
         replayed_receipt_from='baseline-r3',historical_native_exit_code=r.pop('native_exit_code'),
         real_nanoda_invoked_for_requested_execution=False)
assert r['failures']==['FAIL_FRESH_EXECUTION_IDENTITY'],r
(root/'stale-control.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(r,indent=2))
