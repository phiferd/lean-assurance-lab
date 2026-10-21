import json, subprocess, hashlib, tarfile, io
from pathlib import Path
P=Path(__file__).resolve().parent
arena=Path('external/lean-kernel-arena').resolve()
def run(*argv):return subprocess.check_output(argv,text=True).strip()
subprocess.run(['git','-C',str(arena),'fetch','origin','HEAD'],check=True)
rev=run('git','-C',str(arena),'rev-parse','FETCH_HEAD')
config=subprocess.check_output(['git','-C',str(arena),'show',rev+':checkers/nanoda.yaml'])
(P/'nanoda.yaml').write_bytes(config)
(P/'arena-revision.txt').write_text(rev+'\n')
(P/'arena-source.tar').write_bytes(subprocess.check_output(['git','-C',str(arena),'archive',rev,'checkers/nanoda.yaml','README.md','lka.py']))
print(json.dumps({'arena':rev,'config_sha256':hashlib.sha256(config).hexdigest()},indent=2))
print(config.decode())
