#!/usr/bin/env python3
"""Repeat the bounded literal source-launch inventory without executing Lean."""
import hashlib,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).resolve().parent
CLOSURE=ROOT/'results/research/conditional-validation-contracts/alt-payloads/source-closure.json'
closure=json.loads(CLOSURE.read_text())
forbidden=re.compile(r'(?:\b(native_decide|IO\.Process|Process\.spawn|System\.Command|runCmd|dlopen|dlsym|loadLibrary)\b|#(?:eval|reduce)\b)')
review=re.compile(r'evalConstCheck|compileDecl|implemented_by')
files=[];hits=[];review_hits=[]
for row in closure['closure']['modules']:
 if row['kind']=='core_runtime':continue
 p=Path(row['source']['path']);data=p.read_bytes()
 assert len(data)==row['source']['bytes'] and hashlib.sha256(data).hexdigest()==row['source']['sha256'],p
 files.append({'module':row['module'],'source':row['source']})
 for number,line in enumerate(data.decode().splitlines(),1):
  detail={'module':row['module'],'line':number,'text':line}
  if forbidden.search(line):hits.append(detail)
  if review.search(line):review_hits.append(detail)
assert len(files)==37
result={'schema_version':1,'item_id':'CVC-PREP-1','source_closure_sha256':hashlib.sha256(CLOSURE.read_bytes()).hexdigest(),'files':files,'literal_search_pattern':forbidden.pattern,'literal_launch_hits':hits,'review_pattern':review.pattern,'review_hits':review_hits,'interpretation':'No literal launch API was found. evalConstCheck supports Lean code-action/linter registration; compileDecl appears in command elaborators and compiles Lean declarations. implemented_by matches in Verify.Axioms are comments/docstrings. This is scoped source inspection, not proof that arbitrary elaboration cannot perform IO or dynamically load code. A native compiler or missing dynamic import during the fixed build remains a first-failure stop.','reviewer':'Lead plus read-only Luna source_launch_review; model agreement is not semantic authority.','compiler_launches':0,'network_requests':0}
(OUT/'source-launch-review.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'modules':len(files),'literal_launch_hits':len(hits),'review_hits':len(review_hits)}))
