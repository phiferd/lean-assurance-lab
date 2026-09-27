"""Independent semantic and graph auditor, with no producer imports."""
import json
from lib import valid_dependent_term_audit as a
from lib.valid_dependent_term_pilot import ExportGraph, BridgeError

IDS=['beta','zeta','beta-under-let','let-under-beta','shadowed-binder','repeated-bound-variable']
MINIMA=[(1,0),(0,1),(1,1),(1,1),(2,0),(1,0)]
METADATA={'format':{'version':'3.1.0'},'producer':{'name':'LeanAssuranceLab.lazy-reduction-pilot','version':'1'},'origin':'direct independently audited AST encoding; no Lean compiler/exporter run'}

def audit_contract(contract):
    if len(contract['cases'])!=6 or [x['case_id'] for x in contract['cases']]!=IDS:
        raise ValueError('fixed cases differ')
    for i,row in enumerate(contract['cases']):
        for role in ['declared_type','value']:
            expr=row[role]; a._validate_expr(expr,2)
            if a._derive(expr)!=row[role+'_derivation']: raise ValueError('derivation does not replay')
        typ=row['declared_type']; inferred=a._infer(row['value'])
        expected={'tag':'sort','level':1} if i<5 else {'tag':'pi','domain':{'tag':'sort','level':1},'body':{'tag':'sort','level':1}}
        if a._nf(typ)!=expected or a._nf(inferred)!=expected or row['expected_type_nf']!=expected:
            raise ValueError('conversion fails independent typing')
        if typ['tag'] not in ['app','let'] or typ==inferred: raise ValueError('head reduction not demanded')
        if a._nf(a._infer(typ))['tag']!='sort': raise ValueError('declared type is not a type')
        if row['kam_minimum']!={'beta':MINIMA[i][0],'let':MINIMA[i][1]}: raise ValueError('demand minima changed')
        if row['declaration_name']!='LAL_lazy_'+IDS[i].replace('-','_'): raise ValueError('declaration name changed')
    shadow=contract['cases'][4]['declared_type']['function']['body']['function']['body']
    if shadow!={'tag':'bvar','index':1}: raise ValueError('shadow case must refer past inner binder')
    repeated=contract['cases'][5]['declared_type']['function']['body']
    if repeated!={'tag':'pi','domain':{'tag':'bvar','index':0},'body':{'tag':'bvar','index':1}}:
        raise ValueError('repeated occurrence must cross binder depth')
    return {'status':'PASS','cases':6,'typing':'independent existing six-constructor auditor','demand':'static type-conversion head argument plus required execution counters'}

class Graph(ExportGraph):
    def __init__(self,data,expected_name):
        if not data.endswith(b'\n'): raise BridgeError('missing newline')
        self.rows=[json.loads(x,object_pairs_hook=a._pairs) for x in data.splitlines()]
        if not self.rows or self.rows[0]!={'meta':METADATA}: raise BridgeError('producer metadata differs')
        self.metadata=METADATA; self.names={0:''}; self.levels={0:0}; self.expressions={}; self.declaration=None
        self.expected_name=expected_name
        self._parse_records()
        if list(self.expressions)!=list(range(len(self.expressions))): raise BridgeError('noncontiguous expression inventory')
        if self.rows[-1]!={'def':self.declaration}: raise BridgeError('declaration must terminate file')
        if self.names!={0:'',1:expected_name,2:'A'} or self.levels!={0:0,1:1,2:2}: raise BridgeError('exact name/level inventory differs')
        reached=set()
        def visit(index):
            if index in reached: return
            if index not in self.expressions: raise BridgeError('unresolved root')
            reached.add(index)
            tag,value=self.expressions[index]
            for ref in self.references(tag,value): visit(ref)
        visit(self.declaration['type']); visit(self.declaration['value'])
        if reached!=set(self.expressions): raise BridgeError('unused expression record')

    @staticmethod
    def references(tag,value):
        fields={'app':['fn','arg'],'lam':['type','body'],'forallE':['type','body'],'letE':['type','value','body']}.get(tag,[])
        return [value[k] for k in fields]

    def _parse_expression(self,row):
        super()._parse_expression(row)
        index=row['ie']; tag,value=self.expressions[index]
        if any(ref>=index or ref not in self.expressions for ref in self.references(tag,value)):
            raise BridgeError('forward or unresolved expression reference')
        if tag in ['lam','forallE','letE'] and value['name']!=2: raise BridgeError('binder name is not frozen A')
        if tag=='sort' and self.levels[value]>2: raise BridgeError('input universe exceeds frozen bound')

def audit_export(data,row):
    graph=Graph(data,row['declaration_name']); decl=graph.declaration
    typ=graph.expression(decl['type']); value=graph.expression(decl['value'])
    if typ!=row['declared_type'] or value!=row['value']: raise ValueError('export object differs from frozen AST')
    if a._nf(a._infer(value))!=a._nf(typ): raise ValueError('export conversion invalid')
    return {'status':'PASS','declarations':1,'expressions':len(graph.expressions),'declared_type':typ,'value':value,'normal_form':a._nf(typ)}
