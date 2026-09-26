"""Isolated EXL3 benchmark worker. Native engine timing, real token counts, saved output."""

def main():
    import argparse
    import hashlib
    import json
    import os
    from pathlib import Path
    import sys
    import time

    cfg = json.loads(Path(sys.argv[1]).read_text())
    out = Path(cfg['out'])
    root = Path(__file__).resolve().parent
    import torch
    import importlib.metadata
    engine_version=importlib.metadata.version('exllamav3')
    from exllamav3 import model_init, Generator, Job
    from exllamav3.generator.sampler import ComboSampler

    torch.set_num_threads(cfg.get('threads', 4))
    parser = argparse.ArgumentParser()
    model_init.add_args(parser, add_draft_model_args=True)
    recurrent_gb = cfg.get('recurrent_gb', 0.5)
    args = ['-m', cfg['model'], '-cs', str(cfg['context']), '-gs', cfg['split'], '-rcs', str(recurrent_gb)]
    if cfg['kv'] != 'fp16':
        args += ['-cq', cfg['kv']]
    if cfg.get('tp'):
        args += ['-tp']
    draft = cfg.get('draft', 'mtp')
    if draft == 'mtp':
        args += ['-mtp']
    elif draft != 'none':
        args += ['-dm', draft]
    if cfg.get('ndt') is not None:
        args += ['-ndt', str(cfg['ndt'])]
    if cfg.get('dynamic'):
        args += ['-dds']
    args += cfg.get('extra_args', [])
    parsed = parser.parse_args(args)
    start = time.time()
    model, config, cache, tokenizer, draft_model, draft_config, draft_cache = model_init.init(parsed, progress=False)
    generator = Generator(model, cache, tokenizer, draft_model=draft_model, draft_cache=draft_cache,
        num_draft_tokens=cfg.get('ndt'), dynamic_draft_tokens=cfg.get('dynamic', False),
        draft_confidence=cfg.get('confidence', 0.4), max_chunk_size=cfg.get('chunk', 1024),
        recurrent_cache_size=int(recurrent_gb*1024**3), max_batch_size=cfg.get('batch', 1),
        ngram_match_min=cfg.get('ngram', 0))
    print(json.dumps({'event':'loaded','seconds':time.time()-start,'torch':torch.__version__, 'config':cfg}),flush=True)

    import pynvml as nv
    nv.nvmlInit()
    handles=[nv.nvmlDeviceGetHandleByIndex(i) for i in cfg['gpus']]
    def thermal_gate():
        if any(nv.nvmlDeviceGetTemperature(h, nv.NVML_TEMPERATURE_GPU)>=80 for h in handles):
            raise RuntimeError('GPU core reached 80 C; stopping this recipe run')
        return 0.0

    prompts = {
     'code': 'Implement a production-quality Python in-memory TTL cache with a fake clock for deterministic tests. Include a thread-safe class, LRU eviction, bounded capacity, expired-key removal, edge cases, and at least 12 unittest cases. Give complete executable code in one code block and explain tradeoffs after the code. Be thorough.',
     'prose': 'Write a detailed engineering guide with 40 numbered sections about diagnosing performance regressions in a local language-model serving system. Each section must explain a concrete measurement, an example, and a pitfall. Cover CPU, GPU, PCIe, memory bandwidth, batching, tokenization, caching, streaming, and reproducibility.',
     'json': 'Output only a JSON array of 120 realistic software test cases. Each object must have id, component, setup, action, expected, and priority. Use diverse test cases for a collaborative task management application. Do not abbreviate or omit any entries.',
     'warmup': 'Explain why repeatable benchmarks require a warmup. Give a detailed technical explanation.',
    }
    chat_history = {}
    def make_prompt(case, repeat):
        name=case['prompt']
        if case.get('multi_turn') and repeat:
            messages=chat_history[name]+[{'role':'user','content':'Continue the implementation from your previous response. Complete any unfinished code, improve error handling, and provide the missing integration tests. Give executable code without omissions.'}]
            chat_history[name]=messages
            return tokenizer.hf_chat_template(messages, add_generation_prompt=True, enable_thinking=False)
        text=case['custom_prompt'] if 'custom_prompt' in case else prompts[name]
        if case.get('input_tokens'):
            base = ('class Record:\n    def __init__(self, key, value):\n        self.key = key\n        self.value = value\n\n'
                    'def merge_records(left, right):\n    result = dict(left)\n    result.update(right)\n    return result\n\n')
            if case.get('context_file'):
                base=Path(case['context_file']).read_text(encoding='utf8')
                ids=tokenizer.encode(base)
                if ids.shape[-1]<case['input_tokens']:raise RuntimeError('Code corpus shorter than requested input; refusing repeated padding')
            else:
                ids = tokenizer.encode(base * (case['input_tokens']//20+1))
            text = 'Repository context follows.\n' + tokenizer.decode(ids[:,:case['input_tokens']])[0] + '\nTask:\n'+text
        if case.get('prefix_reuse'):
            text+='\nRevision request '+str(repeat)+': improve the error handling and expand the integration tests.'
        sample_repeat=0 if case.get('prefix_reuse') else repeat
        messages=[{'role':'system','content':f'Benchmark sample {name}-{case.get("input_tokens",0)}-{sample_repeat}. Follow the user instructions carefully.'},
                  {'role':'user','content':text}]
        if case.get('multi_turn'):chat_history[name]=messages
        return tokenizer.hf_chat_template(messages, add_generation_prompt=True, enable_thinking=False)

    for case in cfg.get('cases', [{'prompt':'code'},{'prompt':'prose'},{'prompt':'json'}]):
        for rep in range(case.get('repeats', cfg.get('repeats',1))):
            input_ids = make_prompt(case, rep)
            n_input = input_ids.shape[-1]
            n_output = case.get('output_tokens',cfg.get('output_tokens',1024))
            if n_input+n_output+32 > cfg['context']:
                raise RuntimeError('Prompt exceeds configured context; refusing truncation')
            sampler=ComboSampler(temperature=cfg.get('temperature',0.0),top_k=1 if cfg.get('temperature',0.0)==0 else 20,top_p=1.0)
            stops=[tokenizer.eos_token_id,'<|im_end|>'] if case.get('stop_at_eos') else []
            job=Job(input_ids=input_ids,max_new_tokens=n_output,stop_conditions=stops,sampler=sampler,seed=20260926)
            before_pause=thermal_gate()
            started=time.time(); tick=time.monotonic(); cool=0.0; result=None; text=''; first=None
            streamed=0;window_tokens=0;window_start=None;windows=[];last_progress=0;first_eos_at=None;prefilled=0
            (out/'active-request.json').write_text(json.dumps(dict(prompt=case['prompt'],started=started,actual_input_tokens=int(n_input),output_budget=n_output,context=cfg['context'])))
            generator.enqueue(job)
            while generator.num_remaining_jobs():
                cool += thermal_gate()
                for r in generator.iterate():
                    if r.get('stage')=='prefill':prefilled=r.get('curr_progress',prefilled)
                    now=time.monotonic()
                    if r.get('token_ids') is not None:
                        if first_eos_at is None:
                            emitted=r['token_ids'].reshape(-1).tolist()
                            if tokenizer.eos_token_id in emitted:first_eos_at=streamed+emitted.index(tokenizer.eos_token_id)+1
                        count=r['token_ids'].numel();streamed+=count;window_tokens+=count
                        if window_start is None:window_start=now
                        if window_tokens>=1024 and now>window_start:
                            windows.append(dict(end_token=streamed,tokens=window_tokens,seconds=now-window_start,tok_s=window_tokens/(now-window_start)))
                            window_tokens=0;window_start=now
                    chunk=r.get('text','')
                    if chunk:
                        if first is None:first=time.monotonic()-tick
                        text+=chunk
                    if r.get('eos'):result=r
                if time.monotonic()-last_progress>5:
                    (out/'progress.json').write_text(json.dumps(dict(time=time.time(),input_tokens=int(n_input),prefilled_tokens=prefilled,generated_tokens=streamed,elapsed_s=time.monotonic()-tick,first_text_s=first,cooling_s=cool,windows=windows)))
                    (out/'partial-output.txt').write_text(text,encoding='utf8')
                    last_progress=time.monotonic()
            elapsed=time.monotonic()-tick
            if result is None:raise RuntimeError('Missing final generation result')
            if case.get('multi_turn'):chat_history[case['prompt']].append({'role':'assistant','content':text})
            row={k:result.get(k) for k in ('new_tokens','prompt_tokens','cached_tokens','time_enqueued','time_prefill','time_generate','eos_reason','accepted_draft_tokens','rejected_draft_tokens')}
            row.update(experiment=cfg['id'],gpu_count=len(cfg['gpus']),gpus=cfg['gpus'],context=cfg['context'],kv=cfg['kv'],draft=draft,ndt=cfg.get('ndt'),tp=cfg.get('tp',False),
                       prompt=case['prompt'],requested_input_tokens=case.get('input_tokens',0),repeat=rep,started=started,hour=(started-cfg['session_start'])/3600,
                       actual_input_tokens=int(n_input),requested_output_tokens=n_output,elapsed_s=elapsed,first_text_s=first,cooling_s=cool,cooling_before_s=before_pause,
                       torch=torch.__version__,engine_version=engine_version,engine_path=cfg.get('engine_path'),fork=cfg.get('fork',False),output_sha256=hashlib.sha256(text.encode()).hexdigest(),warmup=case['prompt']=='warmup')
            row['recurrent_cache_gb']=recurrent_gb
            row['multi_turn']=case.get('multi_turn',False)
            row['decode_tps']=row['new_tokens']/row['time_generate'] if row.get('time_generate') else None
            row['e2e_tps']=row['new_tokens']/elapsed
            if window_start is not None and window_tokens and time.monotonic()>window_start:
                windows.append(dict(end_token=streamed,tokens=window_tokens,seconds=time.monotonic()-window_start,tok_s=window_tokens/(time.monotonic()-window_start)))
            row.update(context_fill_start=n_input/cfg['context'],context_fill_end=(n_input+row['new_tokens'])/cfg['context'],generation_windows=windows,context_file=case.get('context_file'),prefix_reuse=case.get('prefix_reuse',False),stop_at_eos=case.get('stop_at_eos',False),first_eos_at_token=first_eos_at)
            dest=out/f'{case["prompt"]}-{case.get("input_tokens",0)}-r{rep}.json'
            dest.write_text(json.dumps(dict(row,text=text),indent=2),encoding='utf8')
            with (out/'measurements.jsonl').open('a',encoding='utf8') as f:f.write(json.dumps(row)+'\n')
            print(json.dumps(row),flush=True)

if __name__ == '__main__':
    import multiprocessing
    multiprocessing.freeze_support()
    main()
