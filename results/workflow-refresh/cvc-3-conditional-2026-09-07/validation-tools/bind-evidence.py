"""Bind exact closure evidence; never include this manifest's own bytes."""
import hashlib, json
from pathlib import Path
root=Path(__file__).resolve().parents[4]
base=root/'results/research/conditional-validation-contracts/cvc-3-conditional'
paths={p for p in base.rglob('*') if p.is_file() and p.name not in {'evidence-manifest.json','controller.lock'}}
paths|={root/p for p in ['lib/cvc3_a7_evidence.py','scripts/validate-cvc3-a7','tests/test_cvc3_a7_evidence.py','results/research/queue-reviews/2026-09-07-cvc-3-conditional.json','results/workflow-refresh/cvc-3-conditional-2026-09-07/validation-tools/diagnose-baseline.py']}
files=[{'path':str(p.relative_to(root)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size} for p in sorted(paths)]
(base/'evidence-manifest.json').write_text(json.dumps({'schema_version':1,'item_id':'CVC-3-CONDITIONAL','files':files},indent=2)+'\n')
print(json.dumps({'bound_files':len(files)}))
