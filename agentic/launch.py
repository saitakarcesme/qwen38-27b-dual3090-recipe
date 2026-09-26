"""Launch the measured local server settings. Packaging wrapper, not a benchmark controller."""
import argparse,json,os,subprocess,sys
from pathlib import Path
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--model',required=True,type=Path)
    p.add_argument('--out',required=True,type=Path,help='New diagnostics directory')
    p.add_argument('--gpus',default='0,1')
    p.add_argument('--dry-run',action='store_true')
    a=p.parse_args()
    ids=a.gpus.split(',')
    if len(ids) not in (1,2) or len(set(ids))!=len(ids) or not all(x.isdigit() for x in ids):p.error('Use one or two distinct GPU indices')
    if not (a.model/'config.json').is_file():p.error('Model config.json missing')
    a.out.mkdir(parents=True,exist_ok=False)
    out=a.out.resolve(); dual=len(ids)==2
    (out/'active.json').write_text(json.dumps(dict(profile='two3090' if dual else 'one3090',turn=0)))
    env=os.environ.copy()
    env.update(CUDA_VISIBLE_DEVICES=a.gpus,CUDA_DEVICE_ORDER='PCI_BUS_ID',AGENTIC_TP='1' if dual else '0',
        RESEARCH_PROFILE='two3090' if dual else 'one3090',RESEARCH_TIMINGS=str(out/'timings.jsonl'),
        AGENTIC_REQUESTS=str(out/'requests.jsonl'),AGENTIC_ACTIVE=str(out/'active.json'))
    cmd=[sys.executable,'-u',str(Path(__file__).with_name('server.py')),'-m',str(a.model.resolve()),
        '-gs','21,21' if dual else '22','-cs','262144','-cq','4','-dm','mtp',
        '--host','127.0.0.1','--port','11445','--model_id','qwen3.8:27b','--vision','off','--ui','off']
    print(json.dumps(dict(command=cmd,gpus=ids,output=str(out)),indent=2))
    if not a.dry_run:raise SystemExit(subprocess.call(cmd,env=env))
if __name__=='__main__':main()
