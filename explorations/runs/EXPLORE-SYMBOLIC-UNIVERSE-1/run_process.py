"""Small raw-output adapter for this E0 screen; shared supervision is unchanged."""
import json
import os
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from lib.resource_envelope_supervisor import run_direct

label, timeout, *argv = sys.argv[1:]
out = Path(__file__).resolve().parent / 'attempts' / label
out.mkdir(parents=True, exist_ok=False)
argv[0] = shutil.which(argv[0]) or argv[0]
cwd = Path(os.environ.get('LAL_SCREEN_CWD', str(ROOT)))
result = run_direct(argv=argv, cwd=cwd, env=dict(os.environ), stdin_bytes=None,
    timeout_seconds=float(timeout), memory_ceiling_bytes=4 * 1024**3,
    sample_interval_seconds=1, max_trace_gap_seconds=5, cleanup_seconds=10,
    output_cap_bytes=20 * 1024**2)
(out / 'stdout.log').write_bytes(result.stdout)
(out / 'stderr.log').write_bytes(result.stderr)
(out / 'receipt.json').write_text(json.dumps(result.receipt, indent=2)+'\n')
print(json.dumps({k:result.receipt[k] for k in
    ('exit_code','elapsed_seconds','cleanup_complete','monitor_errors','stop_reason')}))
print(result.stdout.decode('utf-8','replace')[-3000:])
print(result.stderr.decode('utf-8','replace')[-1500:])
if not result.receipt['cleanup_complete'] or result.receipt['monitor_errors']:
    raise SystemExit('SUPERVISION_REPAIR_REQUIRED')
raise SystemExit(result.receipt['exit_code'] or 0)
