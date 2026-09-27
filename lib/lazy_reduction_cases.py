"""Six preregistered conversion terms and deterministic NDJSON encoding.

Derivations reuse the existing producer's rules. The independent audit module
imports neither this producer nor its semantic helpers.
"""
import json
from pathlib import Path
from lib import valid_dependent_term_generator as g
from lib import lazy_reduction_pilot as p

IDS=['beta','zeta','beta-under-let','let-under-beta','shadowed-binder','repeated-bound-variable']
MINIMA=[(1,0),(0,1),(1,1),(1,1),(2,0),(1,0)]
META={'meta':{'format':{'version':'3.1.0'},'producer':{'name':'LeanAssuranceLab.lazy-reduction-pilot','version':'1'},'origin':'direct independently audited AST encoding; no Lean compiler/exporter run'}}

def templates():
    s=lambda n: dict(tag='sort',level=n)
    b=lambda n: dict(tag='bvar',index=n)
    lam=lambda t,v: dict(tag='lam',domain=t,body=v)
    pi=lambda t,v: dict(tag='pi',domain=t,body=v)
    app=lambda f,a: dict(tag='app',function=f,argument=a)
    let=lambda t,v,w: dict(tag='let',type=t,value=v,body=w)
    types=[app(lam(s(2),b(0)),s(1)),let(s(2),s(1),b(0)),
           let(s(2),s(1),app(lam(s(2),b(0)),b(0))),
           app(lam(s(2),let(s(2),b(0),b(0))),s(1)),
           app(lam(s(2),app(lam(s(2),b(1)),pi(s(0),s(1)))),s(1)),
           app(lam(s(2),pi(b(0),b(1))),s(1))]
    values=[s(0)]*5+[lam(s(1),s(0))]
    normal=[s(1)]*5+[pi(s(1),s(1))]
    descriptions=[
      'Apply the identity on types to Sort 1; declaration value Sort 0 has inferred Sort 1.',
      'Let binds A:Sort 2 to Sort 1 and returns A; zeta is needed to expose Sort 1.',
      'Outer let must expose an identity beta redex using its bound A.',
      'Outer beta must expose a let returning the parameter.',
      'Both binders print A; inner body b1 selects outer A=Sort 1, not inner A=(Pi z:Sort 0.Sort 1).',
      'A occurs in Pi domain b0 and body b1 across binder depth; both substitute Sort 1. Value is lambda x:Sort 1.Sort 0.']
    return [dict(case_id=name,declaration_name='LAL_lazy_'+name.replace('-','_'),declared_type=t,value=v,
                 expected_type_nf=n,kam_minimum={'beta':minimum[0],'let':minimum[1]},static_argument=description)
            for name,t,v,n,minimum,description in zip(IDS,types,values,normal,MINIMA,descriptions)]

def contract():
    rows=templates()
    for row in rows:
        row['declared_type_derivation']=g._infer(row['declared_type'])
        row['value_derivation']=g._infer(row['value'])
    return dict(item_id=p.ITEM,cases=rows,profiles=['subst','kam'],expected_relation='ACCEPT on both fresh-process profiles',
       demand_argument='tc.cpp:1016-1022 calls is_def_eq(infer(value),declared_type); top Sort/Pi versus App/Let defeats quick equality; tc.cpp:933-940 calls mode-3 whnf_core before proof irrelevance/eta. Every frozen redex therefore lies on a necessary type-conversion head path.',
       counter_contract='On ACCEPT require full loaded=checked=1, failed=unchecked=0, machine line; subst beta/let=0, KAM beta/let >= case minima. Both profiles delta/iota/proj=0 and nat ops=0. Missing demand is UNSUPPORTED_DEMAND, never replace a case.',
       scope='Closed numeric universe levels <=2 in inputs; Pi/lambda/app/let only; one safe definition; no constants, inductives, native operations, eta/proof-irrelevance obligation.',
       nonclaims=['Same implementation/source lineage; no independent semantic authority.','Repeated uses do not establish memoization benefit or that both uses are forced independently.','Global counters cannot assign every counted reduction to one specific source redex.','Only this exact patched Darwin arm64 build and experimental LL_KAM_MODE=3 profile.'])

def encode(row):
    rows=[META,{'in':1,'str':{'pre':0,'str':row['declaration_name']}},{'in':2,'str':{'pre':0,'str':'A'}},
          {'il':1,'succ':0},{'il':2,'succ':1}]
    cache={}
    def emit(expr):
        key=json.dumps(expr,sort_keys=True)
        if key in cache: return cache[key]
        tag=expr['tag']
        if tag=='sort': kind='sort'; value=expr['level']
        elif tag=='bvar': kind='bvar'; value=expr['index']
        elif tag=='app': kind='app'; value={'fn':emit(expr['function']),'arg':emit(expr['argument'])}
        elif tag in ['pi','lam']:
            kind='forallE' if tag=='pi' else 'lam'
            value={'name':2,'type':emit(expr['domain']),'body':emit(expr['body']),'binderInfo':'default'}
        else:
            kind='letE'; value={'name':2,'type':emit(expr['type']),'value':emit(expr['value']),'body':emit(expr['body']),'nondep':False}
        index=len(cache); cache[key]=index; rows.append({'ie':index,kind:value}); return index
    typ=emit(row['declared_type']); value=emit(row['value'])
    rows.append({'def':{'name':1,'levelParams':[],'type':typ,'value':value,'all':[1],'hints':'abbrev','safety':'safe'}})
    return ''.join(json.dumps(x,separators=(',',':'),sort_keys=True)+'\n' for x in rows).encode()
