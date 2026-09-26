"""Launch one measured configuration; --dry-run requires only Python."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--model',required=True,type=Path)
    p.add_argument('--corpus',required=True,type=Path)
    p.add_argument('--gpus',default='0',help='Physical GPU indices, e.g. 1 or 0,1')
    p.add_argument('--context',type=int,choices=[65536,131072,262144],default=262144)
    p.add_argument('--output',type=int,choices=[8192,16384],default=8192)
    p.add_argument('--kv',choices=['4','8'],default='4')
    p.add_argument('--draft-tokens',type=int,choices=[2,4],default=4)
    p.add_argument('--conversation',action='store_true',help='Two 8K turns with assistant history retained')
    p.add_argument('--out',type=Path,required=True,help='New output directory (never overwrite a run)')
    p.add_argument('--dry-run',action='store_true')
    a=p.parse_args()
    gpus=[int(x) for x in a.gpus.split(',')]
    if len(gpus) not in (1,2) or len(set(gpus))!=len(gpus) or min(gpus)<0:p.error('Use one or two distinct GPU indices')
    if a.conversation and (a.context!=262144 or a.output!=8192):p.error('Conversation preset requires 262144 context and 8192 output')
    if not a.model.is_dir() or not a.corpus.is_file():p.error('Model directory and corpus file must exist')
    a.out.mkdir(parents=True,exist_ok=False)
    task=(Path(__file__).resolve().parents[1]/'task.txt').read_text(encoding='utf8')
    case=dict(prompt='longcode',custom_prompt=task,context_file=str(a.corpus.resolve()),
              input_tokens=a.context-a.output-512,output_tokens=a.output)
    if a.conversation:case.update(input_tokens=245248,prefix_reuse=True,multi_turn=True,stop_at_eos=True,repeats=2)
    cfg=dict(id=a.out.name,model=str(a.model.resolve()),gpus=gpus,context=a.context,kv=a.kv,
             draft='mtp',ndt=a.draft_tokens,chunk=1024,repeats=2 if a.conversation else 1,output_tokens=a.output,
             split='22' if len(gpus)==1 else '21,21',tp=len(gpus)==2,
             recurrent_gb=4.0 if a.conversation else 0.5,session_start=time.time(),out=str(a.out.resolve()),
             cases=[dict(prompt='warmup',output_tokens=128),case])
    config=a.out/'config.json';config.write_text(json.dumps(cfg,indent=2),encoding='utf8')
    if a.dry_run:
        print(json.dumps(cfg,indent=2));return
    import pynvml as nv
    nv.nvmlInit()
    try:uuids=[nv.nvmlDeviceGetUUID(nv.nvmlDeviceGetHandleByIndex(i)) for i in gpus]
    finally:nv.nvmlShutdown()
    uuids=[u.decode() if isinstance(u,bytes) else u for u in uuids]
    env=os.environ.copy();env.update(CUDA_VISIBLE_DEVICES=','.join(uuids),PYTHONUTF8='1',PYTHONUNBUFFERED='1',OMP_NUM_THREADS='4')
    raise SystemExit(subprocess.call([sys.executable,str(Path(__file__).with_name('worker.py')),str(config.resolve())],env=env))

if __name__=='__main__':main()
