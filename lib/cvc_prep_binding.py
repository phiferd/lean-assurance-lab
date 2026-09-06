"""Read-only exact runtime binding for the CVC-U1 preparation successor.

This inspects installed bytes; it never invokes Lean, Lake or a compiler.
The OS loader, Python, Git and trusted local filesystem remain assumptions.
"""
from __future__ import annotations

import hashlib
import os
from pathlib import Path
import re
import stat
import subprocess


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def file_binding(path, name=None):
    path = Path(path)
    require(path.is_file() and not path.is_symlink(), 'not a regular bound file: ' + str(path))
    return {'path': name if name is not None else str(path),
            'bytes': path.stat().st_size, 'sha256': digest(path)}


def platform_identity():
    u = os.uname()
    return {'system': u.sysname, 'machine': u.machine, 'release': u.release,
            'kernel_version': u.version,
            'os_build': subprocess.check_output(['/usr/bin/sw_vers', '-buildVersion'], text=True).strip()}


def runtime_files(runtime):
    """Enumerate every directory/file, rejecting unreviewed symlinks and devices."""
    runtime = Path(runtime)
    require(runtime.is_absolute() and runtime.resolve(strict=True) == runtime,
            'runtime path must be absolute and resolved')
    rows = []
    for top in ('bin', 'lib'):
        require((runtime / top).is_dir(), 'missing runtime tree: ' + top)
        paths = [runtime / top, *sorted((runtime / top).rglob('*'))]
        for path in paths:
            s = path.lstat()
            row = {'path': str(path.relative_to(runtime)), 'mode': stat.S_IMODE(s.st_mode)}
            # No symlinks exist in this exact installed runtime. Do not silently
            # broaden the input boundary to accept one on resume.
            require(not stat.S_ISLNK(s.st_mode), 'unreviewed runtime symlink: ' + str(path))
            if stat.S_ISDIR(s.st_mode):
                row['type'] = 'directory'
            else:
                require(stat.S_ISREG(s.st_mode), 'nonregular runtime input: ' + str(path))
                row.update(file_binding(path, row['path']))
                row['type'] = 'file'
            rows.append(row)
    return rows


def verify_runtime(root, manifest):
    """Called under the preparation controller lock before every launch/resume."""
    runtime = Path(manifest['runtime_root'])
    require(manifest['schema_version'] == 1, 'runtime schema')
    require(platform_identity() == manifest['platform'], 'platform changed')
    require(runtime_files(runtime) == manifest['files'], 'runtime inventory changed')
    header = manifest['version_header']
    require(file_binding(runtime / header['path'], header['path']) == header, 'runtime version header changed')
    reachable = reachable_libraries(manifest['linkage'])
    require(reachable == manifest['lean_static_loader_closure'], 'static loader closure changed')
    require(not any(r['object'] in reachable for r in manifest['unresolved_libraries']),
            'unresolved dependency in the permitted Lean loader closure')
    require(manifest['external_non_system_libraries'] == [], 'unreviewed external runtime dependency')
    # All resolved native inputs must be in the full bound file inventory.
    bound = {r['path'] for r in manifest['files'] if r['type'] == 'file'}
    for row in manifest['linkage']:
        require(row['path'] in bound, 'unbound native object')
        for dep in row['dependencies']:
            if dep['kind'] == 'runtime':
                require(dep['resolved'] in bound, 'unbound native library')
            else:
                require(dep['kind'] == 'system' and dep['name'].startswith(('/usr/lib/', '/System/Library/')),
                        'invalid platform trust dependency')


def reachable_libraries(linkage):
    by_path = {row['path']: row for row in linkage}
    require(len(by_path) == len(linkage), 'duplicate native object')
    seen, todo = set(), ['bin/lean']
    while todo:
        path = todo.pop()
        if path in seen:
            continue
        require(path in by_path, 'missing reachable native object: ' + path)
        seen.add(path)
        todo.extend(d['resolved'] for d in by_path[path]['dependencies'] if d['kind'] == 'runtime')
    return sorted(seen)


def linkage_inventory(runtime, files):
    """Static Mach-O load commands, with exact raw output retained inline."""
    runtime = Path(runtime)
    magic = {b'\xcf\xfa\xed\xfe', b'\xce\xfa\xed\xfe', b'\xfe\xed\xfa\xcf',
             b'\xfe\xed\xfa\xce', b'\xca\xfe\xba\xbe', b'\xbe\xba\xfe\xca'}
    objects = []
    for row in files:
        if row['type'] != 'file':
            continue
        path = runtime / row['path']
        with path.open('rb') as stream:
            if stream.read(4) in magic:
                objects.append(path)
    parsed = {}
    for path in objects:
        raw = subprocess.check_output(['/usr/bin/otool', '-l', str(path)], text=True)
        rpaths, deps = [], []
        for block in re.split(r'Load command \d+\n', raw)[1:]:
            cmd = re.search(r'^\s*cmd (\S+)', block, re.M).group(1)
            if cmd == 'LC_RPATH':
                rpaths.append(re.search(r'^\s*path (.+) \(offset', block, re.M).group(1))
            if cmd in {'LC_LOAD_DYLIB', 'LC_LOAD_WEAK_DYLIB', 'LC_REEXPORT_DYLIB', 'LC_LOAD_UPWARD_DYLIB', 'LC_LOAD_DYLINKER'}:
                deps.append(re.search(r'^\s*name (.+) \(offset', block, re.M).group(1))
        parsed[path] = (raw, rpaths, deps)
    executable = runtime / 'bin/lean'
    require(executable in parsed, 'Lean runtime is not a recognized Mach-O image')
    main_rpaths = parsed[executable][1]
    unresolved, external, result = [], [], []
    for path, (raw, rpaths, deps) in parsed.items():
        def expand(value, owner=path):
            return Path(value.replace('@loader_path', str(owner.parent)).replace('@executable_path', str(runtime / 'bin')))
        search = [expand(r) for r in rpaths] + [expand(r, executable) for r in main_rpaths]
        out = []
        for dep in deps:
            if dep.startswith(('/usr/lib/', '/System/Library/')):
                out.append({'name': dep, 'kind': 'system', 'trust': 'OS dynamic cache / platform loader; not verified'})
                continue
            candidates = [d / dep[len('@rpath/'):] for d in search] if dep.startswith('@rpath/') else [expand(dep)]
            found = next((p.resolve() for p in candidates if p.is_file()), None)
            if found is None:
                unresolved.append({'object': str(path.relative_to(runtime)), 'name': dep})
                continue
            if not found.is_relative_to(runtime):
                external.append(file_binding(found))
                continue
            out.append({'name': dep, 'kind': 'runtime', 'resolved': str(found.relative_to(runtime))})
        result.append({'path': str(path.relative_to(runtime)), 'rpaths': rpaths,
                       'dependencies': out, 'otool_command': ['/usr/bin/otool', '-l', str(path)],
                       'otool_stdout': raw, 'otool_stdout_sha256': hashlib.sha256(raw.encode()).hexdigest()})
    return result, unresolved, external
