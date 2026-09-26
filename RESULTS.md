# Chronological results

Elapsed hours are measured from the start of the three-hour session. These are completed responses only. Capacity includes input and output. See README for timing and quality limitations.

| Elapsed h | Experiment / turn | GPUs | Capacity | Input | Output | Cached | TTFT s | Decode tok/s | Total s |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.040 | 001-full256k-1gpu-8k-baseline / 0 | 1 | 262144 | 253276 | 8187 | 0 | 602.28 | 34.92 | 836.62 |
| 0.279 | 002-full256k-2gpu-pp-8k-baseline / 0 | 2 | 262144 | 253276 | 8187 | 0 | 649.38 | 34.98 | 883.34 |
| 0.534 | 003-full256k-2gpu-tp151-8k / 0 | 2 | 262144 | 253276 | 8192 | 0 | 437.26 | 53.42 | 590.34 |
| 0.706 | 004-full256k-1gpu-151-8k / 0 | 1 | 262144 | 253276 | 8192 | 0 | 587.88 | 36.20 | 814.09 |
| 0.940 | 013-64k-1gpu-151-8k / 0 | 1 | 65536 | 56972 | 8192 | 0 | 66.17 | 75.19 | 175.08 |
| 0.997 | 014-64k-2gpu-tp151-8k / 0 | 2 | 65536 | 56972 | 8192 | 0 | 59.39 | 91.33 | 149.05 |
| 1.046 | 007-128k-1gpu-151-8k / 0 | 1 | 131072 | 122290 | 8192 | 0 | 188.36 | 52.90 | 343.16 |
| 1.149 | 008-128k-2gpu-tp151-8k / 0 | 2 | 131072 | 122290 | 8192 | 0 | 153.22 | 73.17 | 265.12 |
| 1.233 | 005-full256k-2gpu-tp151-16k / 0 | 2 | 262144 | 245085 | 16384 | 0 | 410.09 | 57.16 | 696.66 |
| 1.435 | 015-full256k-1gpu-151-16k / 0 | 1 | 262144 | 245085 | 16384 | 0 | 556.84 | 38.91 | 977.84 |
| 1.714 | 011-full256k-1gpu-cached-coding / 0 | 1 | 262144 | 245101 | 8192 | 0 | 557.00 | 37.45 | 775.64 |
| 1.930 | 011-full256k-1gpu-cached-coding / 1 | 1 | 262144 | 253338 | 8192 | 251904 | 6.52 | 42.37 | 199.74 |
| 2.001 | 012-full256k-2gpu-cached-coding / 0 | 2 | 262144 | 245101 | 8192 | 0 | 410.81 | 55.04 | 559.58 |
| 2.156 | 012-full256k-2gpu-cached-coding / 1 | 2 | 262144 | 253337 | 8192 | 251904 | 4.28 | 67.53 | 125.53 |
| 2.207 | 006-full256k-2gpu-tp151-kv8 / 0 | 2 | 262144 | 253276 | 8192 | 0 | 436.20 | 44.10 | 621.89 |
| 2.390 | 009-full256k-2gpu-tp151-mtp2 / 0 | 2 | 262144 | 253276 | 8192 | 0 | 431.41 | 51.76 | 589.62 |
| 2.562 | 010-full256k-1gpu-151-mtp2 / 0 | 1 | 262144 | 253276 | 8192 | 0 | 587.62 | 35.79 | 816.45 |
| 2.798 | repeat2-003-full256k-2gpu-tp151-8k / 0 | 2 | 262144 | 253276 | 8192 | 0 | 431.28 | 53.50 | 584.33 |

The last single-GPU repeat was terminated at the three-hour deadline during prefill. It is excluded from completed-response comparisons. The older 1.4.4 baseline returned 8,187 tokens for an 8,192-token request; the table preserves actual counts.
