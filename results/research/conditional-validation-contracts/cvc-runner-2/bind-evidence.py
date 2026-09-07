#!/usr/bin/env python3
"""Bind a new, uncommitted CVC-RUNNER-2 closure; never rewrite a bound closure."""
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from lib.cvc_runner2_evidence import BASE, MANIFEST, REQUIRED
from lib.cvc_prep import require, safe, sha
from lib.cvc_process import atomic

require(sys.argv[1:] == ['--write'], 'use --write only before the closure is committed')
prior = subprocess.run(['git', 'cat-file', '-e', 'HEAD:' + MANIFEST], cwd=ROOT,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
require(prior.returncode != 0, 'committed closure is historical; create an explicit successor')
result = json.loads((ROOT / BASE / 'result.json').read_text())
paths = set(REQUIRED)
for path in (ROOT / BASE).rglob('*'):
    if path.is_file() and not path.is_symlink() and not path.name.endswith('.lock') and '__pycache__' not in path.parts:
        paths.add(str(path.relative_to(ROOT)))
paths.discard(MANIFEST)
for rel in result['validation_receipts']:
    paths.add(rel)
    receipt = json.loads((ROOT / rel).read_text())
    log = receipt['log']
    paths.add(log if isinstance(log, str) else log['path'])
    start = Path(rel).with_name(Path(rel).stem + '-start.json')
    if (ROOT / start).exists(): paths.add(str(start))
for rel in result.get('additional_evidence', []): paths.add(rel)
atomic(ROOT / MANIFEST, {'schema_version': 1, 'item_id': 'CVC-RUNNER-2', 'outcome': 'SUCCESS',
       'files': [{'path': p, 'sha256': sha(safe(ROOT, p))} for p in sorted(paths)]})
print('PASS: closure evidence bound; historical bytes were not rewritten')
