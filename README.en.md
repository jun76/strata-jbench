# Sync-Strata jbench

[日本語](README.md) | **English** | [中文](README.zh.md)

Benchmarks of the Sync quantizations of Qwen3.8-Flash-Next on the local inference engine [Sync-Strata](https://github.com/hiruhiru2005/sync-strata). The plans, scripts and measurement records are included for reproduction.

## Division

This branch covers the [Sync-Strata plain division (`plain-sync`)](divisions/README.md). The runner calls the Sync-Strata OpenAI-compatible API directly, with no agent harness.

## The results

The newest three runs appear in the table. Earlier runs are folded below it.

| See | What it contains |
| --- | --- |
| 📈 Charts | Download the HTML and open it in a browser for results as of the end of the run, including speed by model, input length and waiting time, and temperatures, power and memory during measurement. The page links to `summary.csv` with all case values |
| 📋 Cases | Markdown and CSV by environment and tier, with each case’s conditions, result and evidence link |
| 📁 Evidence | The run’s request records, responses, summaries and engine launch records |

Charts and case lists combine results available at the end of the run. For repeated cases in the same environment, they use the result whose RUN_ID sorts last.

<!-- published-runs:start (scripts/publish.py writes this list) -->
| Finished | Environment | RUN_ID | Tier | Cases (done / all) | Content | See |
| --- | --- | --- | --- | --- | --- | --- |
| 2026-11-19 16:39 | GeForce RTX 5070 · Core Ultra 5 235 · 64 GB RAM · SATA SSD | `2026-11-19-sync-r10` | 1 | 54 / 54 | Tier 1 for Sync-XS, Sync-S and Sync-M on Sync-Strata 0.1.1 at R10 (tail skip off), 128K context, k8v4 KV and MTP. All 54 cases and 162 requests passed. | [📈](snapshots/plain-sync/rtx5070-cu5_235-64g-sata/2026-11-19-sync-r10/index.html "Charts") [📋](https://github.com/jun76/strata-jbench/blob/run/plain-sync/rtx5070-cu5_235-64g-sata/2026-11-19-sync-r10/cases/plain-sync/rtx5070-cu5_235-64g-sata/README.en.md "Cases") [📁](published/plain-sync/rtx5070-cu5_235-64g-sata/2026-11-19-sync-r10/ "Evidence") |
<!-- published-runs:end -->

## What is measured

The plan groups measurements into tiers. The results table shows the tiers covered by each run. Case lists and launch records give the sampling, tail skip, context length and other conditions. [scripts/build_cases.py](scripts/build_cases.py) defines the cases.

### How it is measured

- The [Sync-Strata integration](scripts/sync_engine.py) starts the engine on a dedicated port with `sync up --api-only`. The [runner](scripts/bench_runner.py) streams `POST /v1/chat/completions` and records prefill, decode and time to first token (TTFT).
- Speed cases measure decode with short prompts such as prose, JSON, code and copying, and prefill and TTFT with fixed inputs of different lengths. Each case uses seeds 1, 2 and 3. The charts show the median and range.
- The runner uses fixed [prompts](prompts/), sets sampling and thinking in each request, and prepends a unique marker to avoid reusing cache from earlier requests.
- Each run keeps Sync settings and process state in its own directory and reads preinstalled model files. Downloads and other heavy work are kept out of the measurement window.

### Environments

Results are grouped by hardware, including the GPU, CPU, RAM and model storage. Switch environments in the charts and compare cases run under the same conditions when multiple environments have results. Each run’s `machine.json` records the driver, power limits and Sync-Strata version. See the [environment definitions](envs/README.md).

## Where the data is

| What | Where |
| --- | --- |
| Run evidence | `published/plain-sync/<environment>/<RUN_ID>/` |
| Case lists | `cases/plain-sync/<environment>/` |
| Charts and summary CSV | `snapshots/plain-sync/<environment>/<RUN_ID>/` |
| Per-case summaries and responses | `cases/<case id>/summary.json`, `requests.jsonl` and `responses/` within the run |
| Launch configuration, engine log and telemetry | `sessions/<session>/start-N/` within the run |
| Machine and model distribution details | `machine.json` and `sync-models.json` |
| Temperature and power over time | `stats/thermal.csv` |
| Execution logs and verification | `queue.log`, `runner.log` and `verify.json` |

Logs prepared for publication replace the home directory with `~` and the hostname with `<host>`.

### What stays on your machine

| What | Where |
| --- | --- |
| Working results | `results/` |
| Raw streams and full reasoning | Each case’s `raw/` |
| Sync-Strata runtime settings and state | The run’s `sync-home/` |
| Machine-wide process, CPU, memory and disk snapshots | The run’s `stats/snapshots.jsonl.gz`. Set `"stats": false` in `bench.json` to disable collection |
| Plans, previews, status and preflight | `plan/`, `preview/` and `run-status/` |
| Local settings | Root `bench.json` and `envs/<environment>/env.json` |

## Running it again

Set up Sync-Strata and install the desired model packs and shared files through Sync-Strata. The current adapter uses the runtime and model settings under `~/sync-strata/.sync-local/`. Define a matching [environment](envs/README.md) and choose a RUN_ID and cases in `bench.json`.

```bash
python3 -I scripts/envs.py list          # Matching hardware environment
python3 -I scripts/bench.py config       # Settings and defaults
python3 -I scripts/bench.py plan         # Selected cases and estimated time
python3 -I scripts/acquire.py check     # Model packs and shared files
python3 -I scripts/bench.py start        # Start the supervisor and run preflight
python3 -I scripts/bench.py status       # Check progress
python3 -I scripts/bench.py stop         # Stop and resume later with the same RUN_ID
```

The supervisor runs independently of the terminal. See [AGENTS.md](AGENTS.md) for preflight, monitoring, recovery and preparing a result for publication.

## License

- Code is under the [MIT License](LICENSE).
- Measurement data and charts are under [CC BY 4.0](LICENSE-DATA.md). Credit strata-jbench with a repository link, environment and RUN_ID.
- Models and the engine follow their respective licenses.

## Credits

- [Sync-Strata](https://github.com/hiruhiru2005/sync-strata) supplies the inference engine and Sync quantizations.
- [Qwen3.8-Flash-Next](https://huggingface.co/Qwen/Qwen3.8-Flash-Next) is the base model.

| Model | Distribution |
| --- | --- |
| Sync-XS | [hiru2005/Sync-XS](https://huggingface.co/hiru2005/Sync-XS) |
| Sync-S | [hiru2005/Sync-S](https://huggingface.co/hiru2005/Sync-S) |
| Sync-M | [sync-strata/Sync-M](https://huggingface.co/sync-strata/Sync-M) |
