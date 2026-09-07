#!/usr/bin/env python3
"""Bind the newly written CVC-AXIOMS-1 closure, never historical outputs."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = Path(__file__).resolve().parent
paths = [p for p in BASE.rglob('*') if p.is_file()
         and p.name != 'evidence-manifest.json' and '__pycache__' not in p.parts]
paths += [ROOT / p for p in [
    'results/research/conditional-validation-contracts/cvc-3/run-0001/attempts/02/stdout',
    'results/research/conditional-validation-contracts/cvc-3/stop-diagnostic.json',
    'results/research/conditional-validation-contracts/cvc-2/assumptions.json',
    'results/research/conditional-validation-contracts/cvc-2/execution-protocol.json',
    'config/cvc-u1-dependencies-0002.json',
    'lib/cvc_axioms.py', 'scripts/validate-cvc-axioms', 'tests/test_cvc_axioms.py',
]]
rows = []
for p in sorted(set(paths)):
    data = p.read_bytes()
    rows.append(dict(path=str(p.relative_to(ROOT)), bytes=len(data),
                     sha256=hashlib.sha256(data).hexdigest()))
(BASE / 'evidence-manifest.json').write_text(json.dumps(dict(
    schema_version=1, item_id='CVC-AXIOMS-1', files=rows), indent=2) + '\n')
