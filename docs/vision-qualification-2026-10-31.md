# Vision qualification and stage-3 preparation — 31 October 2026

Work and publication date: 31 October 2026, Europe/Luxembourg (CET).
The Git author time is a representative archive timestamp, not an exact experiment
start; the committer time records packaging. These are Linux follow-up experiments,
not revisions to the earlier Windows throughput measurements.

## Morning stage 2: speed passed, memory failed

Twenty different frozen pages returned HTTP 200 with zero prompt or image-cache
hits. The gateway batch lasted **72.197 s (3.610 s/page)**; individual calls ranged
from 2.754 to 4.392 s. This boundary excludes model startup and production restoration.
A separate fresh-process startup-to-first-image measurement was 22.543 s using
retained compiled/autotune caches, not an empty-cache or cold-machine start.

The corrected real-task benchmark completed **234/234 HTTP 200** in 591.558 s,
including request gaps. There were five prompt-cache hits and 127 image-cache hits;
2.528 s/record is therefore not uncached page throughput. One answer reached its
output cap. The candidate honored thinking-disabled settings while the comparison
Ollama route reportedly did not; generated work differed substantially. Do not
interpret the raw runtime ratio as matched engine speed or semantic quality.

Text controls before and after images matched original production full messages,
including reasoning. But the morning near-262k attempt reached **251 MiB free GPU
memory**, below the 300 MiB floor, and aborted safely. Production was restored and
baseline verification returned `same`. This original failure remains part of the
record; it was not a successful full-context result.

## Afternoon qualification: two complete independent passes

Subsequent memory investigations were followed by a separately approved qualification
window. The final configuration used **pair merging off, 2,048 scheduling chunks,
and cleanup after every image request**. Telemetry confirmed `EXL3_PREFILL_M4096=0`,
the native allocator and DFlash draft window 7. The pinned engine/model, 262,144
context, 270,336 cache tokens and cq=3 were retained.

Two fresh processes each ran the frozen controls, 20 images, the full-context request
and post-long controls. Both completed **261,632 input + 512 emitted tokens = 262,144**,
with `finish_reason=length`. Complete response text and all 512 emitted token IDs
matched across repeats. This supplies the full-output evidence missing from an
intermediate retry; merely setting `max_tokens` was not treated as completion.

| Measurement | First run | Fresh repeat |
|---|---:|---:|
| Startup, seconds | 19.601 | 17.512 |
| Image calls, all HTTP 200 | 20 | 20 |
| Image batch, seconds | 76.480 | 77.573 |
| Image average, seconds/page | 3.824 | 3.879 |
| Prompt/image cache hits in images | 0 / 0 | 0 / 0 |
| Long input / emitted tokens | 261,632 / 512 | 261,632 / 512 |
| Long request, seconds | 278.768 | 278.567 |
| Native prefill, seconds | 275.273 | 275.062 |
| Native decode, seconds | 2.973 | 2.962 |
| Minimum CUDA-observed free memory, MiB | 932.75 | 932.75 |
| Minimum external NVML sample, MiB | 933 | 933 |
| Post-long text parity / speed | Pass / Pass | Pass / Pass |

The window completed 210 successful generation HTTP calls: 168 controls, 40 image
calls (20 distinct pages replayed), and two boundary calls. All seven text-control
suites passed message/render/SSE comparisons. The 36 candidate/control decode-speed
ratios were 0.997548–1.008541, within the 5% slowdown limit. Reported preparation
checks were 17 safety tests and 13 mocked end-to-end scenarios, locally and on the rig.
These historical tests were not rerun during publication.

The observed memory floor was 632.75 MiB above the 300 MiB hard threshold. Per-image
cleanup reclaimed unused allocator reservations; it did not delete live model or
KV state. Sampling cannot exclude every transient. The two candidate runs establish
text-only full-context completion after this specific image history, not images
inside a full-context conversation, arbitrary workload longevity, mixed PDF/OCR
concurrency or general semantic quality. The 234-record benchmark was **not rerun**
under the final memory policy. Full-context equality was tested between the two
candidates, not against original production; production parity used fixed controls.

## Restoration and stage-3 status

The qualification window lasted 19 min 51.318 s. Postverification at 15:32:15 CET
reported baseline `same`, healthy production and a free GPU lease. Both candidates
were stopped; production routing, startup, autotune and network exposure were
restored/preserved. Ollama and its model copy were retained.

A local stage-3 preparation package subsequently covered backend-bound sessions,
routing, lifecycle/ownership handling and a rollback plan. It was **not deployed**.
The later v2 integration-window plan identified additional prerequisites including
quarantine notifications and executable rollback; these were not installed features.
A read-only check at 21:38:25 CET still found baseline `same`, both production lanes
healthy and the GPU lease free. The proposed default remained Ollama, with EXL3
requiring an explicit selector in a separately reviewed integration window.

## Evidence and privacy

This summary was checked against the original stage-2 result report, final
qualification report, local stage-3 preparation README and evening v2 plan.
It publishes aggregate measurements and scope limitations only. Client documents,
prompts, outputs, images, access tokens, host paths, private addresses, device
identifiers, chat transcripts, caches and backup snapshots remain excluded.
No production action or inference was performed for this publication.
