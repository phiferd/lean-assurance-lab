"""Finish only the missing manifest after the retained close-item import failure."""
import hashlib
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path.cwd()))
from lib.cvc_a7_runner import CODE, FIXED, MANIFEST
base = Path('results/research/conditional-validation-contracts/cvc-conditional-1')
target = base / 'evidence-manifest.json'
assert not target.exists(), 'Existing closure manifest must not be overwritten'
assert json.loads((base/'result.json').read_text())['outcome'] == 'SUCCESS'
files = {Path(p) for p in CODE} | {Path(p) for p in FIXED} | {Path(MANIFEST)} | {p for p in base.iterdir() if p.is_file()}
rows = [{'path': str(p), 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(files)]
target.write_text(json.dumps({'schema_version':1,'item_id':'CVC-CONDITIONAL-1','outcome':'SUCCESS','files':rows},indent=2)+'\n')
print('PASS: completed only missing closure manifest; no launch or state reset')
