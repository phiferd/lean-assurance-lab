"""Independent synthetic-only classification probes; no selected observer runs."""
from pathlib import Path
import json
import os
import sys
from unittest.mock import patch
ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'tests'))
from test_resource_envelope_supervisor import run, synthetic_snapshot
from lib import resource_envelope_supervisor as supervisor
from lib.resource_envelope_observe import classify

def zero_rss(pgid, _ps, _timeout):
    try:
        os.kill(pgid, 0)
    except ProcessLookupError:
        return []
    return [{'pid': pgid, 'rss_bytes': 0, 'state': 'S'}]

out = []
for expected, options, argv, snapshot, stdout in (
    ('OBSERVED_TIME_LIMIT', {'timeout_seconds': .04}, ['/bin/sh', '-c', 'sleep 2'], synthetic_snapshot, b''),
    ('OBSERVED_MEMORY_LIMIT', {'memory_ceiling_bytes': 500000}, ['/bin/sh', '-c', 'sleep 2'], synthetic_snapshot, b''),
    ('OBSERVED_OVER_CEILING_AFTER_EXIT', {'memory_ceiling_bytes': 1}, ['/bin/sh', '-c', 'printf ok'], zero_rss, b'ok'),
):
    with patch.object(supervisor, '_group_snapshot', side_effect=snapshot):
        result = run(argv, **options)
    science = classify(result.receipt, result.stdout, result.stderr, expected_stdout=stdout, baseline=False)
    baseline = classify(result.receipt, result.stdout, result.stderr, expected_stdout=stdout, baseline=True)
    assert science['status'] == expected, science
    assert baseline['status'] == 'REPAIR_PAUSE', baseline
    out.append({'synthetic_case': expected, 'science_disposition': science['status'],
                'baseline_disposition': baseline['status'], 'exit_code': result.receipt['exit_code'],
                'cleanup_complete': result.receipt['cleanup_complete']})
print(json.dumps({'status': 'PASS', 'selected_observer_invocations': 0, 'checks': out}, indent=2))
