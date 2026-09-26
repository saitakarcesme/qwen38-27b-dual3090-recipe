# Final ZCode CLI agentic benchmark — 26 September 2026

**2 × RTX 3090: all ten substantial project prompts completed in one persistent ZCode CLI session.**
Total: **225,790 generated tokens**, **74.16 minutes**, **83.55 tok/s weighted decode**, **50.74 tok/s end-to-end**.

The two cards serve ONE model and ONE output stream. These rates are not a sum of separate GPU rates.
Wall time runs from the first prompt launch to the final prompt exit, includes tools, test/fix loops and automatic compaction, and excludes model loading and later publication. Decode divides all completed output tokens by summed engine generation time. It includes tool-call text and compaction output, not only user-visible prose.

## Maximum context and speed

- Natural agent history reached **232,345 input tokens on a regular request**; regular requests at 225,350–232,345 tokens averaged **64.56 tok/s**.
- The largest input was **233,631 tokens**, used by automatic compaction, at **58.22 tok/s** (6,301 output tokens). This is summarization, not a normal coding request.
- Compaction ran 12:17:26–12:19:20 UTC (~114 seconds) in stage 8. The next input fell to 19,663 tokens. Regular post-compaction stage-8 requests averaged 114.94 tok/s at 19,663–34,283 input tokens. This is NOT full-context speed.
- Configured capacity was 262,144 tokens; effective ZCode input budget was 245,760 and its compaction threshold 232,760. This agentic run did not continuously fill all 262,144 tokens.
- Separate earlier controlled-length tests reached 253,276 input + 8,192 output tokens at 53.50 tok/s (cold) and 253,337 input tokens at 67.53 tok/s (warm follow-up). See the original README/results; those are different workloads.

## Stage-by-stage measurements

Elapsed hours are measured independently from the first prompt of each GPU configuration. Tool seconds are summed tool durations; they are not necessarily an exclusive wall-clock category. Temperatures are stage maxima across active cards.

| GPUs | Prompt | State | Elapsed h | Input tokens | Decode tok/s | TTFT s | Tool s | Wall s | E2E tok/s | Max core/hotspot/memory °C |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | 1 | complete | 0.0672 | 8,174–27,628 | 95.13 | 1.008 | 39.132 | 242.08 | 61.02 | 73/88.1/74 |
| 1 | 2 | complete | 0.1764 | 29,005–62,972 | 85.56 | 1.36 | 12.462 | 393.11 | 67.98 | 74/90.1/76 |
| 1 | 3 | complete | 0.2579 | 64,441–85,690 | 74.06 | 1.616 | 22.256 | 293.08 | 53.7 | 75/91.9/74 |
| 1 | 4 | complete | 1.2535 | 87,099–190,274 | 56.35 | 2.632 | 1845.311 | 3584.44 | 21.64 | 75/91.3/76 |
| 1 | 5 | complete | 1.4503 | 191,783–222,668 | 47.88 | 2.785 | 108.982 | 708.2 | 28.68 | 76/91.5/74 |
| 1 | 6 | complete | 1.8482 | 16,590–233,118 | 60.8 | 1.754 | 261.466 | 1432.52 | 36.02 | 76/92.2/74 |
| 1 | 7 | interrupted by user | None | 121,312–150,559 | 55.9 | 2.259 | None | None | None | 75/91.2/74 |
| 2 | 1 | complete | 0.0714 | 8,174–39,360 | 114.31 | 0.943 | 39.2 | 257.08 | 67.69 | 76/87.6/92 |
| 2 | 2 | complete | 0.1412 | 40,576–71,427 | 106.17 | 1.1 | 7.588 | 251.1 | 83.24 | 76/88.2/94 |
| 2 | 3 | complete | 0.1981 | 72,828–91,656 | 97.67 | 1.138 | 18.762 | 205.08 | 65.7 | 76/87.6/94 |
| 2 | 4 | complete | 0.3332 | 93,097–129,831 | 92.06 | 1.421 | 101.049 | 486.15 | 61.38 | 77/88.6/94 |
| 2 | 5 | complete | 0.4188 | 131,188–151,770 | 86.19 | 1.776 | 53.687 | 308.09 | 58.74 | 77/88.3/92 |
| 2 | 6 | complete | 0.6016 | 153,155–187,914 | 75.58 | 1.811 | 225.116 | 658.25 | 35.42 | 76/88.2/92 |
| 2 | 7 | complete | 0.7575 | 189,392–223,838 | 69.06 | 2.2 | 51.621 | 561.19 | 45.08 | 77/88.5/92 |
| 2 | 8 | complete | 0.8556 | 19,663–233,631 | 69.47 | 1.328 | 56.71 | 353.12 | 45.71 | 77/89.2/92 |
| 2 | 9 | complete | 1.1196 | 35,593–146,988 | 81.93 | 1.674 | 169.742 | 950.38 | 47.94 | 77/88.5/92 |
| 2 | 10 | complete | 1.236 | 148,619–171,159 | 72.27 | 2.049 | 128.92 | 419.15 | 37.61 | 77/88.7/92 |

Stages 6 (one GPU) and 8 (two GPUs) mix pre-compaction, compaction and post-compaction requests. Use context-segments.json and request-level data for those boundaries.

## One-GPU comparison limits

The user stopped the single-GPU run after six completed prompts and during prompt 7 to prioritize dual GPUs. The six completed prompts generated 206,691 tokens in 110.89 minutes: 62.09 decode tok/s and 31.07 end-to-end tok/s. Prompt 7 is partial; prompts 8–10 were not run.
Both runs began from independent empty projects with the same ten prompt texts. They generated different implementations, test counts, repair loops and context lengths. This is a real agentic comparison, NOT a matched-workload causal hardware speedup. All single-GPU inference and detached app processes were stopped before/shortly after the switch; the two later-discovered detached app servers were explicitly cleaned up and did not use GPU inference.

## Project quality and actual verification

The local Qwen model, through installed ZCode 0.16.9 CLI, wrote TaskHarbor: a FastAPI/SQLite/plain-JS local project/task manager. The coordinating assistant supplied prompts, measurement and infrastructure only; it did not edit application source.
Final recorded verification output: **102 backend tests passed (8 deprecation warnings), 37 browser smoke checks passed, 7 browser scale checks passed, and 25 E2E acceptance checks passed**. The scale browser fixture contains 1,000 tasks. These are project-generated tests with output audited by the coordinator, not an independent held-out coding evaluation.
The model repaired browser modal/navigation failures, CSV parsing and search regressions, and pagination failures during the measured workflow. Failures and retries remain in elapsed time. Shell pipelines sometimes returned success despite failed tests; the actual output, not only process exit codes, was checked.
Implemented: persistent projects/tasks/subtasks/tags, priorities/due dates, CRUD, Kanban, search/filter/sort, dashboard, JSON/CSV transfer, migrations, demo data, backend/browser tests, and documentation.
Known limitations: local single-user/no authentication; substring search uses a full scan; Kanban shows only the currently loaded page (50 tasks); sidebar/topbar counts are page-local while the pagination footer shows total matches; no collaboration features. It is a working local prototype, not a production-readiness claim.
The model also ran a clean-environment install/start check, but its pip output contained unrelated ExLlama dependency warnings; do not interpret that as a pristine dependency-isolation certification.

## Recipe and provenance

Native Windows, Python 3.11, PyTorch 2.8.0+cu128, ExLlamaV3 1.5.1; EXL3 3.5bpw weights, KV4, MTP4, tensor parallelism, budgets21,21GiB, 262144 context, chunk1024, batch1, recurrent CPU cache4GiB, greedy sampling, thinking off, output cap16384 per model request. Stock limits350W/420W. One-GPU budget22GiB on physical GPU1.
Both GPU utilizations reached100%; agent tool/test waits and inter-GPU synchronization cause lower averages. No unrelated stress load was added. No thermal guard stop occurred. Original guard thresholds: core80C,hotspot95C,memory96C.
Inference was stopped at completion. The temporary ZCode config was restored byte-for-byte (SHA256 comparison). A detached clean-start app server was subsequently stopped. No model weights were trained, merged or requantized.
Model: Mia-AiLab/Qwen3.8-27B-EXL3-3.5bpw at revision19441ac874c4018295da848e250f23511361cda4; publisher base model Qwen/Qwen3.8-27B, architecture metadata qwen3_5. Original quantization credit belongs to Mia-AiLab. This is an independent recipe and benchmark, not an upstream endorsement.
The installed CLI was used, not the ZCode desktop GUI. No ZCode GUI screenshot is claimed. Public evidence excludes private machine paths, credentials and full conversation/code payloads.

See [RECIPE.md](RECIPE.md), prompts/, numeric requests.csv, stages.csv, context-segments.json and totals.json.
