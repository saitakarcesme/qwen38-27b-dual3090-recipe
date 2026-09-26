# Measured dual-3090 agentic recipe

Use the parent README's Python3.11/PyTorch2.8.0+cu128/ExLlamaV3 1.5.1 installation, then install `aiohttp pillow requests` in that inference environment. Download either the pinned upstream model in the parent README or the unmodified repack:

```powershell
hf download Ibrahimsait/Qwen3.8-27B-EXL3-3.5bpw-Dual3090-Recipe --local-dir models/qwen38-dual3090
python agentic/launch.py --model models/qwen38-dual3090 --gpus 0,1 --out runs/agentic-dual
```

Physical GPU order uses PCI_BUS_ID. The inference server runs in the foreground at `http://127.0.0.1:11445/v1`. Stop with Ctrl+C when finished. It loads the exact model settings in recipe.json: native TP, KV4, MTP4, 262144 capacity, 4GiB recurrent CPU cache, chunk1024, batch1, thinking off, greedy and16384 output cap. Server source is the measured file, adapted from MiaAI-Lab's one-click kit (revision622c7965ed5e02a13b188c9ef21bb9857fd2ba28); its MIT notice is LICENSE-MIA-SERVER. Measurements/tool logging and TP/runtime settings were changed for this experiment.

`launch.py` is a portable packaging wrapper: syntax and --dry-run were checked; it has not been rerun on GPUs after packaging. It does not reproduce the original controller's NVAPI thermal watchdog. The original run stopped at80C core/95C hotspot/96C memory, and no guard stop occurred. Keep hardware monitoring active. The wrapper does not change fans, clocks or power limits. Requests.jsonl contains full prompts/tool payloads and should stay local unless reviewed.

## Actual ZCode CLI workflow

Install ZCode separately (measured version0.16.9). This uses the installed CLI, not desktop GUI automation; ZCode code is not redistributed. In another terminal configure paths for YOUR installation:

```powershell
$env:ZCODE_CLI = 'C:/path/to/ZCode-Source/resources/glm/zcode.cjs'
$env:ZCODE_BUILTIN_PROVIDER_CONFIG_FILE = 'C:/path/to/ZCode-Source/resources/config/provider/zcode-builtin.json'
$env:ZCODE_BUILTIN_PROVIDER_BUNDLED_CONFIG_FILE = $env:ZCODE_BUILTIN_PROVIDER_CONFIG_FILE
$env:ZCODE_PERSONAL_PROVIDER_CONFIG_FILE = (Resolve-Path agentic/personal-provider.json).Path
New-Item -ItemType Directory -Path projects/taskharbor-dual
node agentic/prompt.cjs agentic/prompts/prompt-01.txt projects/taskharbor-dual
# Copy sessionId from the returned JSON. Continue with prompts02–10, same project and session:
node agentic/prompt.cjs agentic/prompts/prompt-02.txt projects/taskharbor-dual YOUR_SESSION_ID
```

The wrapper enables ZCode's `yolo` mode so the local model can edit files and execute commands within the requested project workflow. Use an isolated new project. Confirm the selected provider is rig-research/qwen3.8:27b in the returned records. Use an independent empty project/new session for a one-GPU comparison (`--gpus 1`, budget22GiB), never copy generated code across runs.

For stage attribution, update the launch output's active.json before each prompt to `{"profile":"two3090","turn":1}` (then2…10). Do not edit it during a model request. Keep the server and session alive across prompts to retain actual cache/history. No artificial context padding and no manual summarization were used. ZCode compacted automatically at its context threshold.

The recorded run temporarily used local-only CLI features (subagent/memory/MCP/skill off), a262144 context limit and16384 output limit; the original user config was restored byte-for-byte afterward. The portable package does not overwrite your global config. Align your local CLI settings deliberately; other ZCode versions/features can change prompts and results.

Public numeric traces omit full message/code bodies and private paths. Same prompts do not ensure the same generated code, tool calls, tests or speed. See FINAL_REPORT.md for actual results and limitations.
