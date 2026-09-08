#!/usr/bin/env python3
"""Bind the assessment package; never regenerate historical scientific outputs."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PACKAGE = Path(__file__).resolve().parent
SUPPORT = [
    'lib/transfer_assessment.py', 'scripts/validate-transfer-assessment',
    'tests/test_transfer_assessment.py',
    'docs/research/PROSPECTIVE_TRANSFER_ASSESSMENT_PLAN.md',
]
PRESERVE = [
    'config/declaration-validation-catalog.json',
    'config/declaration-validation-identity-registry.json',
    'config/declaration-validation-target.json',
    'config/declaration-validation-source-lock.json',
    'config/declaration-validation-authority-rules.json',
    'config/declaration-validation-approved-authority-sources.json',
    'config/declaration-validation-approved-authority-sources/publication-study-v2.json',
    'config/declaration-validation-evidence-locks/publication-study-complete-adjudication.json',
    'results/research/survivor-let-association-1/evidence-manifest.json',
    'results/research/survivor-let-association-1/historical-transition.json',
    'results/research/survivor-let-reuse-1/evidence-manifest.json',
    'results/research/conditional-validation-contracts/cvc-1/assessment.json',
    'scripts/build-witness-admission',
]


def binding(path, data):
    return {'path': path, 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}


def main():
    work = json.loads((PACKAGE / 'work-record.json').read_text())
    local = json.loads((PACKAGE / 'local-independence-review.json').read_text())
    preserved = []
    for name in sorted(set(PRESERVE) | {row['path'] for row in local['sources']}):
        original = subprocess.check_output(['git', '-C', str(ROOT), 'cat-file', 'blob',
                                            work['base_commit'] + ':' + name])
        if (ROOT / name).read_bytes() != original:
            raise SystemExit('Current scientific input changed: ' + name)
        preserved.append(binding(name, original))
    files = {p for p in PACKAGE.rglob('*') if p.is_file() and p.name != 'evidence-manifest.json'}
    # Nested entry snapshots named evidence-manifest.json are still evidence.
    files |= {p for p in PACKAGE.rglob('evidence-manifest.json') if p.parent != PACKAGE}
    files |= {ROOT / name for name in SUPPORT}
    rows = [binding(p.relative_to(ROOT).as_posix(), p.read_bytes()) for p in sorted(files)]
    manifest = {'schema_version': 1, 'item_id': 'ALT-TRANSFER',
                'files': rows, 'preserved_inputs': preserved}
    (PACKAGE / 'evidence-manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps({'bound_files': len(rows), 'preserved_inputs': len(preserved)}))


if __name__ == '__main__':
    main()
