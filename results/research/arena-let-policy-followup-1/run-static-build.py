"""One exact, durably reserved static Arena build; no scientific byte generation."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,sys,time,shutil
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from lib.cvc_process import run_process,atomic
from lib.cvc_signal_retry import signal_retry
P=Path(__file__).resolve().parent

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 m=json.loads((P/'execution-manifest.json').read_text());w=json.loads((P/'work-record.json').read_text());cwd=Path(m['cwd'])
 assert time.monotonic()-w['start_monotonic']<3600
 for b in m['tooling']+m['package']+[m['source_lock'],m['patch'],m['candidate']]:assert sha(ROOT/b['path'])==b['sha256'],b['path']
 lock=json.loads((P/'source-lock.json').read_text())
 for b in lock['files']:assert sha(cwd/b['path'])==b['sha256'],b['path']
 for b in m['package']:
  rel=Path(b['path']).relative_to(P.relative_to(ROOT)/'package');assert sha(cwd/rel)==b['sha256']
 assert not (cwd/'_build').exists(),'Do not overwrite a previous static attempt'
 out=P/'static-build-01';out.mkdir(exist_ok=False)
 reservation={'item_id':w['item_id'],'number':1,'status':'RESERVED','seconds':300,'at':datetime.now(timezone.utc).isoformat(),'manifest_sha256':sha(P/'execution-manifest.json'),'runner_sha256':sha(__file__),'cumulative_reservations':1,'remaining_reservations':1,'argv':m['invocation'],'source_revision':m['source_revision']}
 atomic(out/'reservation.json',reservation)
 with signal_retry():r=run_process(m['invocation'],cwd,{'PATH':'/usr/bin:/bin','PYTHONNOUSERSITE':'1'},out,300,deadline_monotonic=min(time.monotonic()+300,w['start_monotonic']+3600))
 files=[]
 for name in [m['case_name']+'.ndjson',m['case_name']+'.stats.json']:
  src=cwd/'_build/tests'/name
  if src.exists():dest=out/src.name;shutil.copyfile(src,dest);files.append({'path':str(dest.relative_to(ROOT)),'sha256':sha(dest),'bytes':dest.stat().st_size})
 result={'item_id':w['item_id'],'number':1,'returncode':r['returncode'],'status':r['status'],'cleanup_completed':r['cleanup_completed'],'charged_seconds':r['charged_seconds'],'manifest_sha256':reservation['manifest_sha256'],'files':files,'validation_status':'PENDING'};atomic(out/'result.json',result)
 assert r['status']=='COMPLETE' and r['returncode']==0 and r['cleanup_completed'] and not r['deadline_exceeded'],r
 assert m['expected']['summary'] in (out/'stdout').read_text()
 assert sha(out/(Path(m['case_name']).name+'.ndjson'))==m['expected']['built_bytes_sha256']
 stats=json.loads((out/(Path(m['case_name']).name+'.stats.json')).read_text());assert stats['outcome']=='either' and stats['name']==m['case_name'] and stats['size']==601 and stats['lines']==13,stats
 result['validation_status']='PASS';atomic(out/'result.json',result);print(json.dumps(result))
if __name__=='__main__':main()
