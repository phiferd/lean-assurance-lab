"""Fetch only one candidate's OAI source-import closure before checker observation."""
from pathlib import Path
import json
import re
import sys
import urllib.request

HERE=Path(__file__).resolve().parent
REV='1581d4cbdd69a0faf34b2089614fe2a814316a6a'
entry=sys.argv[1] if len(sys.argv)>1 else 'OAI.Computability.WitnessedChoice.Main'
pending=[entry]; seen={}; external=set()
while pending:
    module=pending.pop()
    if module in seen: continue
    path='lean/'+module.replace('.','/')+'.lean'
    raw=urllib.request.urlopen('https://raw.githubusercontent.com/openai/math/'+REV+'/'+path,timeout=30).read()
    (HERE/'sources'/path.replace('/','__')).write_bytes(raw)
    imports=re.findall(r'^import\s+(\S+)',raw.decode(),re.M)
    seen[module]={'bytes':len(raw),'imports':imports}
    print(module,len(raw),flush=True)
    for name in imports:
        if name.startswith('OAI.'): pending.append(name)
        else: external.add(name)
record={'revision':REV,'endpoint_candidate':entry,'modules':seen,
        'external_imports':sorted(external),'total_bytes':sum(x['bytes'] for x in seen.values()),
        'other_candidates':'TypeSystem.Normalization has six direct OAI imports; BinarySweep.Main has three. WitnessedChoice.Main has one; inspect this closure first. No checker outcome has been observed.'}
(HERE/('candidate-'+entry.replace('.','_')+'.json')).write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps({'files':len(seen),'bytes':record['total_bytes'],'external':sorted(external)}))
