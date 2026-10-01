from pathlib import Path
import json,hashlib,tarfile,sys,shutil
r=Path('/Users/danphifer/Documents/Codex/2026-09-30/task-3/lab');sys.path.insert(0,str(r))
from lib.acceptance_impact_source import _tree_manifest
lock=json.loads((r/'results/research/kiota-ctor-index-test-1/dependency-lock.json').read_text());out=r/'results/research/lean-action-regression-preparation-1/closure/cargo-cache-restoration';out.mkdir(exist_ok=True);rows=[]
for p in lock['packages']:
 dest=Path(p['source_root'])
 if dest.exists():continue
 cached=Path('/Users/danphifer/.cargo/registry/cache/index.crates.io-1949cf8c6b5b557f')/(p['name']+'-'+p['version']+'.crate');digest=hashlib.sha256(cached.read_bytes()).hexdigest();assert digest==p['lock_checksum']
 local=out/dest.name
 if not local.exists():
  with tarfile.open(cached) as t:
   for m in t.getmembers():
    assert m.isfile() or m.isdir();assert '..' not in Path(m.name).parts and not Path(m.name).is_absolute();assert Path(m.name).parts[0]==dest.name
   t.extractall(out)
  (local/'.cargo-ok').write_bytes(b'{"v":1}')
 count,manifest=_tree_manifest(local);assert count==p['files'] and manifest==p['manifest_sha256'],p['name']
 rows.append({'source':str(cached),'archive_sha256':digest,'local_tree':str(local),'restore_destination':str(dest),'files':count,'manifest_sha256':manifest})
 if '--restore' in sys.argv:
  assert not dest.exists();shutil.copytree(local,dest);assert _tree_manifest(dest)==(count,manifest)
(r/'results/research/lean-action-regression-preparation-1/closure/cargo-cache-restoration.json').write_text(json.dumps({'mode':'restored' if '--restore' in sys.argv else 'verified-locally','packages':rows},indent=2)+'\n')
print('Verified '+str(len(rows))+' exact cached Cargo source trees; '+('restored absent cache directories' if '--restore' in sys.argv else 'not yet restored'))
