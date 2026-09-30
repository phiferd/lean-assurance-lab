import copy
import hashlib
import importlib.util
import json
from pathlib import Path

RUN=Path(__file__).parent
ROOT=RUN.parents[2]
spec=importlib.util.spec_from_file_location('data_screen',RUN.parent/'EXPLORE-SEMANTIC-DATA-RECURSION-1/screen-r2.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
REF={'app':['fn','arg'],'forallE':['type','body'],'lam':['type','body'],'letE':['type','value','body']}

def reserialize(rows, shared):
    """Expand every root as a tree, then optionally hash-cons identical nodes."""
    expr={r['ie']:r for r in rows if 'ie' in r}; out=[]; memo={}; counter=0
    def emit(i):
        nonlocal counter
        r=copy.deepcopy(expr[i]); del r['ie']; k=next(iter(r))
        for f in REF.get(k,[]): r[k][f]=emit(r[k][f])
        key=json.dumps(r,sort_keys=True)
        if shared and key in memo: return memo[key]
        j=counter;counter+=1;out.append(dict(ie=j,**r));memo[key]=j;return j
    for row in rows:
        if 'ie' in row: continue
        r=copy.deepcopy(row)
        if 'inductive' in r:
            for kind in ['types','ctors','recs']:
                for d in r['inductive'][kind]:
                    d['type']=emit(d['type'])
                    for rule in d.get('rules',[]):rule['rhs']=emit(rule['rhs'])
        if 'def' in r:
            for f in ['type','value']:r['def'][f]=emit(r['def'][f])
        out.append(r)
    return out

inventory=[]; audits=[]
for family in ['beta','zeta','nested-beta']:
    x,(s0,s1,t,a,b,rn)=m.data()
    ident=x.binder('lam',s1,x.bv(0))
    if family=='beta':typ=x.app(ident,t)
    elif family=='zeta':typ=x.ex('letE',dict(name=0,type=s1,value=t,body=x.bv(0),nonDep=False))
    else:typ=x.app(ident,x.app(ident,t))
    x.definition(x.name('sharing_target'),typ,b)
    outputs={}
    for role in ['shared','duplicated']:
        rows=reserialize(x.rows,role=='shared');p=RUN/f'{family}-{role}.ndjson'
        with p.open('x') as f:
            for r in rows:f.write(json.dumps(r,sort_keys=True,separators=(',',':'))+'\n')
        inventory.append(dict(path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),family=family,role=role,declarations=2))
        outputs[role]=rows
    def expanded(rows):
        ex={r['ie']:r for r in rows if 'ie' in r}
        def expand(i):
            r=copy.deepcopy(ex[i]);del r['ie'];k=next(iter(r))
            for f in REF.get(k,[]):r[k][f]=expand(r[k][f])
            return r
        roots=[]
        for row in rows:
            if 'ie' in row:continue
            r=copy.deepcopy(row)
            if 'inductive' in r:
                for kind in ['types','ctors','recs']:
                    for d in r['inductive'][kind]:
                        d['type']=expand(d['type'])
                        for rule in d.get('rules',[]):rule['rhs']=expand(rule['rhs'])
            if 'def' in r:
                for f in ['type','value']:r['def'][f]=expand(r['def'][f])
            roots.append(r)
        return roots
    eq=expanded(outputs['shared'])==expanded(outputs['duplicated']);assert eq
    audits.append(dict(family=family,expanded_roots_equal=eq,expression_rows={k:sum('ie' in r for r in rs) for k,rs in outputs.items()}))
m.save(RUN/'inputs.json',inventory);m.save(RUN/'structure-audit.json',audits)
