# Qwen3.8-27B · 1 vs 2 RTX 3090s

**3-hour long-context coding benchmark**

| Context / output | 1×3090 | 2×3090 |
|---|---:|---:|
| 64K / 8K | 75.19 tok/s | 91.33 tok/s |
| 128K / 8K | 52.90 tok/s | 73.17 tok/s |
| 256K / 8K | 36.20 tok/s | **53.50 tok/s** |
| 256K / 16K | 38.91 tok/s | **57.16 tok/s** |

- Best observed cold-prompt generation rates; batch 1, thinking off.
- EXL3 3.5bpw weights · EXL 1.5.1 · 4-bit KV · MTP-4 · dual-GPU TP.
- 256K tests ended at **99.74% context occupancy**.
- Cached coding follow-up: **42.37 / 67.53 tok/s**, first token **6.52 / 4.28 s** (1 / 2 GPUs).
- Dual 256K/8K repeated at **53.42 → 53.50 tok/s**.
- Throughput benchmark; not a coding-quality evaluation.
