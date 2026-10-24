# Qwen vision example

Source experiment: October 23, 2026, 23:34 +02:00. Packaged October 26.
This Linux homelab used ExLlamaV3 1.4.4, Qwen3.8:27b and a 262144-token
context setting. It is separate from the Windows/1.5.1 benchmark in the root README.
The server was configured with vision enabled (`--vision auto`).

Use a trusted OpenAI-compatible endpoint that already serves this model:

```sh
export OPENAI_BASE_URL=http://127.0.0.1:11445/v1
python3 examples/vision/caption_image.py diagram.png
python3 -m pip install Pillow
python3 examples/vision/smoke_test.py
```

The caption example asks for a short Turkish description. The smoke script creates
an image in memory, sends it, then sends three short text requests. Inspect its
printed response: it is a manual smoke check, not a semantic assertion or benchmark.
These examples assume an endpoint requiring no bearer token. Images are sent to
the configured endpoint. Requests time out after 180 seconds.

The recorded image response correctly identified the red square, blue circle and
right-pointing arrow in 0.543 seconds on a warm server. The text requests ended at
the token budget; they do not establish quality or complete counting accuracy.
Startup CUDA allocation increased from 8.62 to 9.49 GiB. These are single-session
observations, not performance guarantees. GPU requests were not rerun when packaged.
