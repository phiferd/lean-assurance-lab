import subprocess,hashlib,json
from pathlib import Path
P=Path(__file__).resolve().parent
C='lal-comparator-screen-native'
def run(*args):subprocess.run(args,check=True)
run('docker','exec',C,'mkdir','/arena-current-nanoda')
run('docker','cp',str(P/'nanoda-source.tar'),C+':/arena-current-nanoda/source.tar')
run('docker','exec',C,'tar','-xf','/arena-current-nanoda/source.tar','-C','/arena-current-nanoda')
for name in ['build.sh','arena-run.sh','instrumented-run.sh']:
 run('docker','cp',str(P/name),C+':/arena-current-nanoda/'+name)
run('docker','exec',C,'mkdir','/arena-current-inputs','/arena-current-results')
for f in (P/'inputs').glob('*.ndjson'):run('docker','cp',str(f),C+':/arena-current-inputs/'+f.name)
run('docker','exec',C,'chown','-R','checker:checker','/arena-current-results')
run('docker','exec',C,'chmod','-R','a+rX','/arena-current-nanoda','/arena-current-inputs')
run('docker','inspect','--format','{{json .HostConfig}} {{json .NetworkSettings.Networks}}',C)
