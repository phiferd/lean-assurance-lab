"""Streaming inventory of the complete checked export, using LAL's walker.

Records its entire dependency environment and declared axioms, without claiming
that this overexport is the minimal dependency closure of the requested theorem.
"""
import gzip
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from lib.real_proof_slices import row_kind, outputs

path=Path(sys.argv[1]);target=sys.argv[2]
names={0:''};consts={};declared=set();needed=set();axioms=set()
metadata=None;root=None;target_type=None;records=0;h=hashlib.sha256()
opener=gzip.open if path.suffix=='.gz' else open
with opener(path,'rb') as f:
    for line in f:
        records+=1;h.update(line);r=json.loads(line);k=row_kind(r)
        if k=='meta':metadata=r[k]
        if 'in' in r:
            v=r[k];prefix=names[v['pre']]
            names[r['in']]=prefix+('.' if prefix else '')+str(v['str'] if k=='str' else v['i'])
        if k=='const':
            consts[r['ie']]=r[k]['name'];needed.add(r[k]['name'])
        elif k=='proj':needed.add(r[k]['typeName'])
        ids=outputs(r);declared.update(ids)
        if k=='axiom':axioms.add(r[k]['name'])
        if k in {'thm','def','opaque','axiom'} and names[r[k]['name']]==target:
            root=r;target_type=names[consts[r[k]['type']]] if r[k]['type'] in consts else None
assert root is not None,'requested target absent from export'
missing=sorted(names[n] for n in needed-declared)
assert not missing,missing
result={'target':target,'artifact_sha256':h.hexdigest(),'records':records,
        'metadata':metadata,'checked_export_declarations':len(declared),
        'declared_axioms_in_checked_export':sorted(names[n] for n in axioms),
        'unresolved_constant_or_projection_dependencies':missing,
        'target_declaration':root,'target_type_constant':target_type,
        'scope':'Full exported environment (includes requested built-ins and permitted axioms); not a minimal theorem-only closure or semantic oracle.'}
base=path.with_suffix('') if path.suffix=='.gz' else path
out=base.with_suffix('.checked-inventory.json');out.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
