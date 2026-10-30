# Elpis recovery, GPU placement and document sessions — 30 October 2026

Work date: 30 October 2026 (Europe/Luxembourg, CET). Prepared for publication
on 31 October. At the repository owner's request the Git author date represents
the work day; the committer date records actual packaging. These Linux homelab
observations are separate from the repository's earlier Windows benchmarks.

## Terminal-failure recovery

A watchdog was installed for the two Elpis lanes. It requires three consecutive
observations of the exact sticky `503 generation_failed / Native generator requires
restart` response, an unhealthy idle lane, an active service and a running container.
It rechecks under the existing shared GPU lock and restarts only the failed lane.
Persistent budgets cap attempts at three per lane per hour, at least five minutes
apart. Healthy work, maintenance stops and transient errors are excluded; requests
are never replayed. The original report records **11 passing mocked tests**.

[Sanitized reference source and integration requirements](../examples/elpis-recovery/README.md)
are included. The snapshot is the original watchdog, not the later stage-3 variant.
Live checks used normal requests, not an injected OOM: 20,058-token cold text
completed in 13.373 s; cold text overlapping a small synthetic vision request
completed in 13.644 s. Both lanes ended healthy. Observed GPU0 free memory fell
to 427 MiB. This is bounded functional evidence, not full-262k qualification or
proof that recovery prevents OOM. The watchdog issued no restart during those
healthy checks.

## Ollama restricted to physical GPU1

Ollama 0.33.3 retained its model, 65,536-token context and Q8_0 KV cache. A replacement
container restricted device visibility to physical GPU1; the original container
was retained stopped. CLIP changed from CPU to the container's CUDA0, which maps
to physical GPU1. Layer offload changed from 65/66 to 66/66. Model files were preserved.

All three before and three after probes returned HTTP 200 with 988 prompt tokens.
The **first post-change call was slower**: 57.69 s HTTP, including a long warmup.
Subsequent calls took 18.39 and 20.98 s, with prompt evaluation of 1.43 and 1.38 s
versus a 14.47 s baseline average. Decode on those two calls was 40.87 and 39.91
tokens/s versus approximately 33.93 before. Output lengths differed.
Including the first call, the HTTP mean was **32.35 s after versus 31.48 s before**;
the complete small sample therefore does not establish an overall mean speedup.

## Bounded document session

The document-session path holds the vision model resident across calls and restores
the text lane once at close. The measured ten-call test used **the same image and
prompt repeatedly**, not ten distinct pages. All ten calls returned HTTP 200, with
one load and one unload; lane 0 stayed healthy in the observations.

| Server-observed component | Seconds |
|---|---:|
| Session open, including lane stop and preload | 8.393 |
| Ten inference HTTP responses combined | 60.454 |
| Mean inference HTTP response | 6.045 |
| Close to lane 1 ready | 16.449 |
| Full batch including gaps and restoration | 85.465 |
| Full batch per call | 8.547 |

Call one evaluated 988 prompt tokens; calls two through ten evaluated four tokens
each. Repeated-input cache reuse is part of this result. Output lengths ranged from
212 to 394 tokens. The full batch is reconstructed from server event timestamps,
not a client stopwatch; it must not be sold as uncached distinct-page throughput.

## Evidence and publication scope

Figures were checked against the dated recovery README and the original GPU1/CLIP
and document-session result reports. The public package deliberately omits raw
requests, images, client identities, addresses, device UUIDs, machine paths, API
keys, configuration dumps and backup archives. Operational sources remain private.
The source-directory substitution is a publication adaptation made on 31 October.
No deployment, recovery action or inference was performed to publish these records.
Ollama and its model copy remain preserved; this publication does not retire them.
