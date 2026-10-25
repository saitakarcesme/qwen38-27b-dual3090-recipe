# ExLlamaV3 shared-memory cache accounting

This patch was extracted from a local repair made on October 25, 2026.
The affected Linux installation was reported as ExLlamaV3 1.4.4. Upstream project:
https://github.com/turboderp-org/exllamav3 (its code retains its upstream license).
It is not a claim that all versions are affected or that upstream has accepted a fix.

The producer and consumer initialized `cache_size` but did not update it when
inserting or evicting tensors. The patch updates both sides, enforcing the existing
byte-limit eviction condition for the tested transfer sizes.

From the matching runtime source root, inspect and check before applying:

```sh
git apply --check /path/to/exllamav3-shared-cache-accounting.patch
git apply /path/to/exllamav3-shared-cache-accounting.patch
python /path/to/tests/test_shared_cache.py exllamav3/model/model_tp_shared.py
```

Use the runtime's Python environment with its Torch, NumPy and ExLlamaV3 dependencies.
The test dynamically loads the specified source module and uses the installed
ExLlamaV3 CUDA helper import. It transfers 40 one-MiB tensors with a two-MiB cache
limit, checking values, accounting, eviction, producer/consumer agreement and reuse.
It does not test oversized entries, all cache-key lifecycles or long-duration load.
Package upgrades may overwrite an installed-file patch.

Recorded October 25 evidence: the original failed on the first insertion with
reported bytes 0 versus actual 1048576; the patched version passed all 40 transfers.
Those runtime tests were not rerun during packaging on October 26.

Original snapshot SHA-256: `01ba0b8c162887c2356d514a8ac5fd8ab938a81b7ae25f5928321d7195bd8111`.
