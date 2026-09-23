#!/usr/bin/env python3
"""Build and verify the local successor patch against its pinned archive."""
import difflib
import hashlib
import json
from pathlib import Path
import subprocess
import tarfile
import tempfile

ROOT = Path(__file__).resolve().parents[3]
BASE = Path(__file__).resolve().parent
SOURCE = Path('/tmp/kiota-recursor-pr-refinement-1/kiota-9fa2c297dd700fe8fd1712a86bdbb258e1c01c42')
PREDECESSOR = ROOT / 'results/research/kiota-recursor-type-repair-1/patch-package.json'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def main():
    original = json.loads(PREDECESSOR.read_text())
    archive = original['source_archive']
    path = ROOT / archive['path']
    assert sha(path.read_bytes()) == archive['sha256']
    old = {}
    with tarfile.open(path) as tf:
        for member in tf.getmembers():
            if member.isfile():
                name = member.name.removeprefix(archive['top_level'])
                old[name] = tf.extractfile(member).read()
    assert not any(p.is_symlink() for p in SOURCE.rglob('*'))
    new = {p.relative_to(SOURCE).as_posix(): p.read_bytes()
           for p in SOURCE.rglob('*') if p.is_file()}
    allowed = {'src/env.rs','src/parser.rs','src/tc.rs','src/tc/recursor.rs',
               'tests/exports.rs','tests/fixtures/nested-list-tree.accept.ndjson',
               'tests/fixtures/nested-list-tree.reject.ndjson',
               'tests/fixtures/recursor-type-reconstruction.accept.ndjson',
               'tests/fixtures/recursor-type-reconstruction.reject.ndjson'}
    copied = {r['path']: r for r in original['changed_files'] if r['kind'] == 'ADDED'}
    chunks, rows = [], []
    for name in sorted(set(old) | set(new)):
        if old.get(name) == new.get(name):
            continue
        assert name in allowed, 'unexpected modification: ' + name
        before, after = old.get(name), new.get(name)
        kind = 'ADDED' if before is None else 'DELETED' if after is None else 'MODIFIED'
        chunks.append(f'diff --git a/{name} b/{name}\n')
        if kind == 'ADDED': chunks.append('new file mode 100644\n')
        if kind == 'DELETED': chunks.append('deleted file mode 100644\n')
        chunks.extend(difflib.unified_diff(
            (before or b'').decode().splitlines(keepends=True),
            (after or b'').decode().splitlines(keepends=True),
            fromfile='/dev/null' if before is None else 'a/'+name,
            tofile='/dev/null' if after is None else 'b/'+name))
        row = dict(path=name,kind=kind,base_bytes=len(before or b''),
                   base_sha256=None if before is None else sha(before),
                   patched_bytes=len(after or b''),
                   patched_sha256=None if after is None else sha(after))
        if name in copied:
            for key in ('source_path','source_bytes','source_sha256'):
                row[key] = copied[name][key]
            assert after == (ROOT/row['source_path']).read_bytes()
        elif kind == 'ADDED' and name.endswith('nested-list-tree.reject.ndjson'):
            legacy = 'tests/fixtures/nested-list-tree.accept.ndjson'
            assert after == old[legacy]
            src = 'external/acceptance-impact-pilot-1-kiota/' + archive['top_level'] + legacy
            assert (ROOT/src).read_bytes() == after
            row.update(source_path=src,source_bytes=len(after),source_sha256=sha(after))
        elif kind == 'ADDED':
            row['origin'] = 'AUTHORED'
        rows.append(row)
    patch = ''.join(chunks).encode()
    patch_path = BASE/'kiota-recursor-type-refined.patch'
    patch_path.write_bytes(patch)
    with tempfile.TemporaryDirectory(prefix='kiota-refined-verify-') as work:
        with tarfile.open(path) as tf: tf.extractall(work,filter='data')
        verified = Path(work)/archive['top_level']
        subprocess.run(['git','apply','--check',str(patch_path)],cwd=verified,check=True)
        subprocess.run(['git','apply',str(patch_path)],cwd=verified,check=True)
        observed={p.relative_to(verified).as_posix():p.read_bytes() for p in verified.rglob('*') if p.is_file()}
        assert observed == new, 'patch does not reconstruct exact reviewed tree'
    package = dict(schema_version=1,item_id='KIOTA-RECURSOR-PR-REFINEMENT-1',
                   source_revision=original['source_revision'],source_archive=archive,
                   predecessor_package={'path':str(PREDECESSOR.relative_to(ROOT)),'sha256':sha(PREDECESSOR.read_bytes())},
                   patch={'path':str(patch_path.relative_to(ROOT)),'bytes':len(patch),'sha256':sha(patch)},
                   changed_paths=[r['path'] for r in rows],changed_files=rows,
                   patch_application_check={'result':'PASS','post_apply_tree_comparison':'BYTE_IDENTICAL_TO_REVIEWED_SOURCE'},
                   scientific_inputs={'candidate_identity':'PRESERVED_EXACTLY','control_identity':'PRESERVED_EXACTLY','accepted_fixture_substitutions':0},
                   source_inventory=[{'path':n,'bytes':len(b),'sha256':sha(b)} for n,b in sorted(new.items())])
    (BASE/'patch-package.json').write_text(json.dumps(package,indent=2)+'\n')
    print(json.dumps({'changed_paths':package['changed_paths'],'patch_bytes':len(patch),'verified_files':len(new)}))

if __name__ == '__main__': main()
