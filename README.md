# Qwen3.8-27B on 1 vs 2 RTX 3090s: full-context coding recipe

## Final real agentic run — ten prompts completed

**2 × RTX3090: 225,790 output tokens in 74.16 minutes; 83.55 tok/s weighted decode, 50.74 tok/s end-to-end including tools/tests/retries/compaction.** The installed ZCode0.16.9 CLI and local Qwen built a real TaskHarbor project from scratch. Final recorded verification:102 backend tests +69 browser checks passed. One-GPU comparison was stopped by the user after6completed prompts and a partial7th.

At **225,350–232,345 regular input tokens:64.56 tok/s**. Peak input233,631 was the automatic-compaction request at58.22tok/s; later faster rates use shorter summarized context. This agentic workload is separate from the near-full-capacity tests below.

- [English final report: stages, elapsed hours, context, TTFT, tools and temperatures](agentic/FINAL_REPORT.md)
- [Agentic server recipe and ten exact prompts](agentic/RECIPE.md)
- [Hugging Face model package](https://huggingface.co/Ibrahimsait/Qwen3.8-27B-EXL3-3.5bpw-Dual3090-Recipe): unmodified Mia-AiLab weights with recipe/provenance, **not a newly trained or requantized model**.

The following sections preserve the earlier three-hour controlled-length measurements; do not combine them with the natural agentic run as one experiment.

Three hours of local measurements, September 26, 2026. **18 completed long-response measurements** across 16 completed experiment processes; one additional repeat was stopped at the time limit before producing a measured response.

## Results worth sharing

Generation throughput, batch size 1, thinking disabled, real source-code context:

| Context capacity / output budget | 1 × RTX 3090 | 2 × RTX 3090 |
|---|---:|---:|
| 64K / 8K | 75.19 tok/s | 91.33 tok/s |
| 128K / 8K | 52.90 tok/s | 73.17 tok/s |
| 256K / 8K | 36.20 tok/s | **53.50 tok/s** |
| 256K / 16K | 38.91 tok/s | **57.16 tok/s** |

These are the best observed **cold-prompt** results in each bucket, not an average across repeated trials. K denotes 1,024 tokens. Context includes both input and output: the 256K/8K run used 253,276 input + 8,192 output tokens, reaching 99.74% occupancy at the end. The 256K/16K run used 245,085 input + 16,384 output tokens. The 64K and 128K runs ended at 99.43% and 99.55% occupancy.

**Repeat check:** the selected dual-GPU 256K/8K setting produced 53.42 and 53.50 tok/s in two separate runs. Most other configurations were measured once.

### Actual two-turn coding conversation

The second request included the original repository prompt, the generated assistant code, and a new continuation request. Both responses had an 8,192-token budget. This is a warm-cache scenario, separate from the cold table above.

| Follow-up request | 1 × RTX 3090 | 2 × RTX 3090 |
|---|---:|---:|
| Input tokens | 253,338 | 253,337 |
| Cached input tokens | 251,904 | 251,904 |
| Time to first text | **6.52 s** | **4.28 s** |
| Generation throughput | **42.37 tok/s** | **67.53 tok/s** |
| Total request time | 199.74 s | 125.53 s |

The first, uncached turn took 557.00 s / 410.81 s to first text on one / two GPUs. The follow-up has different requested content, so its decode-speed difference must not be attributed solely to caching.

### First / best / last: cold 256K, 8K output budget

| GPUs | First | Best | Last completed |
|---|---:|---:|---:|
| 1 | 34.92 | 36.20 | 35.79 |
| 2 | 34.98 | 53.50 | 53.50 |

The first measurements used EXL 1.4.4; the dual baseline used layer splitting. The final single-GPU measurement deliberately tested MTP-2. The best dual result used EXL 1.5.1 tensor parallelism. This is an optimization sequence, not a controlled claim about one change alone.

## Measured setup

- Model artifact: [Mia-AiLab/Qwen3.8-27B-EXL3-3.5bpw](https://huggingface.co/Mia-AiLab/Qwen3.8-27B-EXL3-3.5bpw), revision `19441ac874c4018295da848e250f23511361cda4`. The artifact's architecture metadata is `qwen3_5`; the model name here follows the artifact publisher.
- EXL3 weights: 3.5 bits/weight. **Weight quantization and KV-cache quantization are different settings.**
- Selected runtime: [ExLlamaV3](https://github.com/turboderp-org/exllamav3) `1.5.1+cu128.torch2.8.0`, PyTorch `2.8.0+cu128`, Python 3.11, native Windows, NVIDIA driver 610.88.
- GPU 0: Zotac RTX 3090 24 GB, PCIe 4.0 ×16, stock 350 W limit.
- GPU 1: EVGA RTX 3090 FTW3 Ultra 24 GB, PCIe 4.0 ×4, stock 420 W limit. All single-GPU runs used this card. Host RAM: 32 GB.
- Batch size 1, one request at a time, greedy sampling (`temperature=0`, `top_k=1`), seed 20260926, thinking disabled.
- Best settings: **4-bit KV, built-in MTP with 4 draft tokens, 1,024-token prefill chunks; tensor parallelism for 2 GPUs.** EXL GPU allocation budgets: `22` for one card; `21,21` for two.
- Recurrent-state CPU cache budget: 0.5 GiB in cold tests; 4 GiB for the two-turn conversation tests. This is system RAM, not VRAM.

### What did not help here

- Dual-GPU 8-bit KV: 44.10 tok/s vs 53.42 tok/s with 4-bit KV. This speed test does not establish a quality difference.
- Dual-GPU MTP-2: 51.76 tok/s vs 53.42 tok/s with MTP-4.
- Single-GPU MTP-2: 35.79 tok/s vs 36.20 tok/s with MTP-4.

## Run the recipe

The included runner is extracted and simplified from the measured harness. **The published wrapper has passed CPU-side configuration checks; it has not been rerun on the GPUs after packaging.** It runs one configuration, not the original unattended three-hour controller.

### 1. Match the runtime

Native Windows / Python 3.11 PowerShell example:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install torch==2.8.0 --index-url https://download.pytorch.org/whl/cu128
python -m pip install "https://github.com/turboderp-org/exllamav3/releases/download/v1.5.1/exllamav3-1.5.1%2Bcu128.torch2.8.0-cp311-cp311-win_amd64.whl"
python -m pip install -r requirements.txt huggingface_hub
hf download Mia-AiLab/Qwen3.8-27B-EXL3-3.5bpw --revision 19441ac874c4018295da848e250f23511361cda4 --local-dir models/qwen38-27b-3.5bpw
```

For another OS, use the matching wheel from the [upstream release](https://github.com/turboderp-org/exllamav3/releases/tag/v1.5.1). These measurements are native Windows results; another runtime is a new experiment.

### 2. Prepare real code context

```powershell
python scripts/build_corpus.py path/to/source1 path/to/source2 --out code-corpus.txt
```

The builder keeps `.py`, `.cu`, `.cuh`, `.h`, `.cpp` files up to 500 KB, in supplied root order and sorted path order, deduplicated by SHA-256. It does not pad with repeated text. The benchmark refuses a corpus too short for the input budget.

The measured corpus contained 823 unique files (10,399,845 bytes) from installed EXL 1.4.4, EXL 1.5.1 and a local Mia EXL fork. Each prompt used only a token prefix of that corpus. The exact third-party corpus is **not redistributed**: a relative-path/hash [manifest](results/corpus-manifest.json) is included for provenance. Using your own source corpus reproduces the procedure, not the exact numerical results. The task is in [task.txt](task.txt).

### 3. Cold full-context coding

```powershell
# Physical GPU index from nvidia-smi; the measured single card was index 1.
python scripts/bench.py --model models/qwen38-27b-3.5bpw --corpus code-corpus.txt --gpus 1 --out runs/single-256k
python scripts/bench.py --model models/qwen38-27b-3.5bpw --corpus code-corpus.txt --gpus 0,1 --out runs/dual-256k

# 16K output; the runner reserves room within the same 256K total context.
python scripts/bench.py --model models/qwen38-27b-3.5bpw --corpus code-corpus.txt --gpus 0,1 --output 16384 --out runs/dual-256k-16k
```

Use `--context 65536` or `--context 131072` for the smaller capacities. Use `--kv 8` or `--draft-tokens 2` for the ablations. Every invocation requires a new output directory. Add `--dry-run` to write and inspect a configuration without loading the model.

### 4. Warm continuation with actual history

```powershell
python scripts/bench.py --model models/qwen38-27b-3.5bpw --corpus code-corpus.txt --gpus 1 --conversation --out runs/single-conversation
python scripts/bench.py --model models/qwen38-27b-3.5bpw --corpus code-corpus.txt --gpus 0,1 --conversation --out runs/dual-conversation
```

Keep the generator alive across both turns. The first prompt reserves room for two responses; the second input contains the first generated answer. Read `cached_tokens`, `first_text_s`, and `context_fill_end` rather than assuming the entire prefix was reused.

## Timing, output integrity and temperature

Timing begins after model loading and input tokenization, when the request is enqueued. First-token values measure first emitted text. Decode throughput uses the engine's generation duration; E2E throughput includes prefill. Warmup is excluded. Per-approximately-1,024-token generation windows, actual input/output counts, and full request timings are in [measurements.json](results/measurements.json). [Chronological table](RESULTS.md).

Cold runs force the requested output length; conversation runs allow EOS but all measured conversation turns reached their 8K cap. Some code blocks remain unfinished at the limit. AST parsing checks complete Python blocks only; generated tests were not executed. **These are throughput measurements, not proof of coding quality or long-context retrieval accuracy.**

The original run used independent core/hotspot/memory monitoring and cooperative cooling. No in-request cooling pauses occurred. Observed maxima across completed requests: core 77°C, hotspot 91.72°C, memory junction 92°C. The three-hour deadline stopped the final incomplete repeat; it has no completed throughput result. The published simplified runner stops at a core temperature of 80°C; it does not reproduce the original NVAPI memory/hotspot watchdog. Keep suitable hardware monitoring active when reproducing. It does not change power limits, clocks, RGB or fan curves.

## Credits and scope

Model/quantization: [Mia-AiLab](https://huggingface.co/Mia-AiLab/Qwen3.8-27B-EXL3-3.5bpw). Runtime: [turboderp / ExLlamaV3](https://github.com/turboderp-org/exllamav3). Original model lineage: [Qwen](https://huggingface.co/Qwen/Qwen3.8-27B). This repository is an independent hardware recipe, not an upstream endorsement. No weights, tokens, private code, local account paths or generated source corpus are included.
