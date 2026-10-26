# Inference outage and recovery — October 25, 2026

Published from the incident record on October 26. This is the Linux homelab
serving Qwen3.8:27b with ExLlamaV3 1.4.4, not the Windows benchmark environment.

## Diagnosis

The gateway advertised the model while inference could not start. A model-list
response alone therefore did not establish inference health. The host's OOM
manager killed the service after memory and swap exceeded 90%; the service had
47.5 GiB of swap. Subsequent starts could not allocate shared memory.

Both shared-memory producer and consumer failed to update their cached-byte
counters. The configured four-GiB per-process limit was ineffective. This verified
retention bug is consistent with the exhaustion; historical allocation traces are
unavailable, so it is not proof of the sole cause.

## Recovery and evidence

The installed module was backed up and repaired using the [accounting patch](../patches/README.md).
After checking ownership PIDs and accessible process maps/file descriptors, 99
orphan shared-memory files (8,846,629,056 bytes) were archived to disk, preserving
the data. Do not treat this incident description as permission to remove shared
memory on another live system.

The repaired engine loaded behind the gateway with a 262144-token context and
vision enabled. The operator-disabled alternative model remained disabled.
Recorded verification completed October 25 at 01:03 +02:00:

- Original module failed the cache regression; patched module passed 40 transfers.
- A request through the shared endpoint returned `LLMRig OK`.
- Streaming returned `STREAM_OK` and completed.
- A forced streaming tool call returned `add` with arguments `a=2`, `b=3`.
- Gateway was ready, service active, service swap zero, shared memory 2.6 GiB used
  with 13 GiB available.

The remote user's own client/network was not directly tested. This short run does
not establish long-duration stability. Package replacement can overwrite the patch.
Private addresses, account paths and raw client records are omitted.

## Publication dates

These materials were assembled and pushed on October 26. At the repository owner's
request, the vision package's Git author date is October 24 and the patch package's
is October 25; committer dates retain the actual packaging time. Source experiment
and verification dates above are the evidence dates, independent of Git author dates.
