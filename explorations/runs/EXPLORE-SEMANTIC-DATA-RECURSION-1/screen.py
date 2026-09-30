"""Campaign-local construction and supervised runner; no shared tool changes."""
import copy
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from lib.lazy_reduction_pilot import classify, safe
from lib.metamorphic_pilot_runner import run_supervised
RUN = Path(__file__).parent
BINARY = ROOT / 'external/lazy-reduction-conformance-pilot-1/lazylean-r1'
ENV = dict(PATH='/usr/bin:/bin:/usr/sbin:/sbin', LANG='C', LC_ALL='C', LL_KAM_MODE='3')

def save(path, obj):
    with path.open('x') as f:
        f.write(json.dumps(obj, indent=2, sort_keys=True)+'\n')

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

class Export:
    def __init__(self):
        self.rows=[json.loads((ROOT/'explorations/runs/EXPLORE-LAZYLEAN-SEMANTIC-EXTENSION-1/iota-candidate.ndjson').read_text().splitlines()[0])]
        self.ns=0; self.es=0
        self.rows += [{'il':1,'succ':0}, {'il':2,'param':self.name('u')}]
    def name(self,s,pre=0):
        self.ns+=1; self.rows.append({'in':self.ns,'str':{'pre':pre,'str':s}}); return self.ns
    def ex(self,k,v):
        i=self.es; self.es+=1; self.rows.append({'ie':i,k:v}); return i
    def const(self,n,us=[]): return self.ex('const',dict(name=n,us=us))
    def app(self,f,a): return self.ex('app',dict(fn=f,arg=a))
    def bv(self,i): return self.ex('bvar',i)
    def binder(self,k,t,b,info='default',name=0): return self.ex(k,dict(type=t,body=b,binderInfo=info,name=name))
    def definition(self,n,t,v): self.rows.append({'def':dict(all=[n],name=n,type=t,value=v,hints='abbrev',levelParams=[],safety='safe')})
    def write(self,p):
        with p.open('x') as f:
            for r in self.rows: f.write(json.dumps(r,sort_keys=True,separators=(',',':'))+'\n')

def data():
    x=Export(); u=1; tn=x.name('LALData'); an=x.name('a',tn); bn=x.name('b',tn); rn=x.name('rec',tn)
    s0=x.ex('sort',0); s1=x.ex('sort',1); su=x.ex('sort',2); t=x.const(tn); a=x.const(an); b=x.const(bn)
    motive=x.binder('forallE',t,su)
    ma=x.app(x.bv(0),a)
    mb=x.app(x.bv(1),b)
    major=x.binder('forallE',t,x.app(x.bv(3),x.bv(0)))
    rt=x.binder('forallE',motive,x.binder('forallE',ma,x.binder('forallE',mb,major)),info='implicit')
    def rule(which):
        return x.binder('lam',motive,x.binder('lam',ma,x.binder('lam',mb,x.bv(which))),info='implicit')
    common=dict(levelParams=[],isUnsafe=False)
    x.rows.append({'inductive':dict(types=[dict(common,name=tn,type=s1,all=[tn],ctors=[an,bn],numParams=0,numIndices=0,numNested=0,isRec=False,isReflexive=False)],
        ctors=[dict(common,name=n,type=t,induct=tn,cidx=i,numParams=0,numFields=0) for i,n in enumerate([an,bn])],
        recs=[dict(name=rn,type=rt,all=[tn],isUnsafe=False,levelParams=[u],numParams=0,numIndices=0,numMotives=1,numMinors=2,k=False,rules=[dict(ctor=an,nfields=0,rhs=rule(1)),dict(ctor=bn,nfields=0,rhs=rule(0))])])})
    # rule() appends expressions before the block append; each rhs is well scoped.
    return x,(s0,s1,t,a,b,rn)

def prepare():
    inv=[]
    for depth in [1,4]:
        x,(s0,s1,t,a,b,rn)=data(); previous=b
        for i in range(depth):
            n=x.name('alias'+str(i));x.definition(n,t,previous); previous=x.const(n)
        motive=x.binder('lam',t,s1)
        rec=x.app(x.app(x.app(x.const(rn,[1]),motive),s0),t)
        typ=x.app(rec,previous)
        n=x.name('target')
        for role in ['control','candidate']:
            y=copy.deepcopy(x); y.definition(n,t if role=='control' else typ,b)
            p=RUN/f'depth-{depth}-{role}.ndjson';y.write(p)
            inv.append(dict(path=str(p.relative_to(ROOT)),sha256=sha(p),depth=depth,role=role,declarations=depth+2))
    save(RUN/'inputs.json',inv)

def run(attempt):
    out=RUN/attempt;out.mkdir(); rows=[]
    try:
        assert sha(BINARY)=='8132451a5a3c122fcae1d62cf5e7a8d4ca07ed2aa787675d305b399e6d5f6c0e'
        for fixture in json.loads((RUN/'inputs.json').read_text()):
            p=ROOT/fixture['path'];assert sha(p)==fixture['sha256']
            for profile in ['subst','kam']:
                i=len(rows)+1
                receipt=run_supervised(argv=[str(BINARY),'--engine',profile,'--jobs','1',str(p)],cwd=ROOT,stdin=None,env=ENV,timeout_seconds=30,memory_bytes=2147483648,raw_prefix=out/f'{i:02d}-{profile}')
                observation=classify(receipt,Path(receipt['raw_stdout_path']).read_bytes(),Path(receipt['raw_stderr_path']).read_bytes(),fixture['declarations'])
                row=dict(input=fixture,profile=profile,receipt=receipt,observation=observation);save(out/f'cell-{i:02d}.json',row);rows.append(row);safe(receipt)
        save(out/'result.json',rows)
        print(json.dumps([r['observation'] for r in rows],indent=2))
    except BaseException as error:
        save(out/'error.json',dict(error=repr(error),completed_cells=len(rows)));raise

if __name__=='__main__':
    if sys.argv[1]=='--prepare': prepare()
    else: run(sys.argv[1])
