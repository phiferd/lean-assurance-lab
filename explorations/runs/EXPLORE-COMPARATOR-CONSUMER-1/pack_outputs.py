"""Losslessly retain large raw exports; never run while a case is active."""
import gzip
import hashlib
import json
from pathlib import Path

root=Path(__file__).resolve().parent
records=[]
paths=set(root.rglob('*.ndjson')) | set(root.rglob('*.log'))
for f in (root/'sources').rglob('*'):
    if f.is_file():
        try: lines=f.read_text().splitlines()
        except UnicodeError: continue
        if any(line.rstrip(' \t')!=line for line in lines): paths.add(f)
for p in sorted(paths):
    raw=p.read_bytes()
    packed=gzip.compress(raw,compresslevel=6,mtime=0)
    assert gzip.decompress(packed)==raw
    out=p.with_name(p.name+'.gz');out.write_bytes(packed)
    records.append({'raw_path':str(p.relative_to(root)), 'raw_bytes':len(raw),
                    'raw_sha256':hashlib.sha256(raw).hexdigest(),
                    'retained_path':str(out.relative_to(root)), 'retained_bytes':len(packed),
                    'retained_sha256':hashlib.sha256(packed).hexdigest()})
    p.unlink()
(root/'packed-evidence.json').write_text(json.dumps(records,indent=2)+'\n')
print(json.dumps({'files':len(records),'raw_bytes':sum(r['raw_bytes'] for r in records),
                  'retained_bytes':sum(r['retained_bytes'] for r in records)}))
