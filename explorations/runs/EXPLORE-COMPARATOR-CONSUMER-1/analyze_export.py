"""Reuse the existing 3.1 reference walker for one exported endpoint inventory."""
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from lib.real_proof_slices import row_kind, refs, outputs, environment_refs

path=Path(sys.argv[1]); target=sys.argv[2]
names={0:''}; tables={'name':{},'level':{},'expr':{}}; declarations={}
metadata=None; rows=0; h=hashlib.sha256()
with path.open('rb') as f:
    for line in f:
        h.update(line); rows+=1
        row=json.loads(line); kind=row_kind(row)
        if kind=='meta': metadata=row['meta']; continue
        for field,space in [('in','name'),('il','level'),('ie','expr')]:
            if field in row: tables[space][row[field]]=row
        if 'in' in row:
            v=row[kind]; parent=names[v['pre']]
            names[row['in']]=parent+('.' if parent else '')+str(v['str'] if kind=='str' else v['i'])
        for name in outputs(row): declarations[name]=row
root_name=next(n for n,name in names.items() if name==target)
pending=[('decl',root_name)]; seen=set(); axioms=set(); reached=set(); absent_group_metadata=set()
while pending:
    space,index=pending.pop()
    if (space,index) in seen: continue
    seen.add((space,index))
    if space=='decl':
        row=declarations[index]; reached.add(names[index])
        if row_kind(row)=='axiom': axioms.add(names[index])
    else:
        if space in {'name','level'} and index==0: continue
        row=tables[space][index]
    pending.extend(refs(row))
    for name in environment_refs(row):
        if name in declarations: pending.append(('decl',name))
        else:
            if row_kind(row) in {'const','proj'}:
                raise ValueError('unresolved semantic constant dependency '+names[name])
            absent_group_metadata.add(names[name])
result={'target':target,'artifact_sha256':h.hexdigest(),'metadata':metadata,
        'records':rows,'declarations_in_export':len(declarations),
        'reachable_declarations':len(reached),'transitive_axioms':sorted(axioms),
        'absent_group_metadata_names':sorted(absent_group_metadata),
        'target_declaration':declarations[root_name],
        'target_type_record':tables['expr'][declarations[root_name][row_kind(declarations[root_name])]['type']],
        'scope':'Typed export-reference reachability using the retained slicer walker; not a new semantic oracle.'}
out=path.with_suffix('.inventory.json');out.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
