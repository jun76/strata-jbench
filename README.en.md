<p align="center"><picture>
  <source media="(prefers-color-scheme: dark)" srcset="media/strata-jbench.png">
  <img src="media/strata-jbench-light.png" alt="strata-jbench" width="560">
</picture></p>

[日本語](README.md) | **English** | [中文](README.zh.md)

Benchmark results of 18 quantized and derived Qwen3.8-Flash-Next models on the local LLM inference engine Strata, all
measured under the same conditions. The plan, the measuring scripts and the raw records are here too, so the same
procedure can be run again.

Everything published so far is the **plain division** (no harness): the models and the engine themselves, with no agent
harness in between.

## Division: which harness was used

The results are split into "divisions" by how the models are driven ([divisions/](divisions/README.md)).

| Division | Status | What it is |
| --- | --- | --- |
| Plain (`plain`) | Measured, published | No harness. The runner calls the OpenAI-compatible API of the engine started by `strata launch` directly. No tool calls |
| Agentic (`strata`, `dsh`, `opencode`) | Planned | Through a harness such as Strata's own agent features, DeepSeek Harness (dsh) or opencode: some or all of the plain measurements, and tasks of their own (tool calls, many turns) |

Results of different divisions are never mixed. Used from an agent, the speed can differ from the plain results by what
the harness adds: a system prompt, tool definitions, long histories sent again.

## The results

A row is added at the top of this table every time a run finishes. The latest three are shown; earlier ones are folded below the table. "See" in each row opens:

| See | What it has |
| --- | --- |
| 📈 Charts | The results as of the end of that run (GitHub Pages): speed by model, input length and waiting, standard-v1, with and without thinking, the cost of reserving context, long documents (to 1M tokens), launch options, temperature, power and memory during the runs, and a table of all models. Every case's numbers (`summary.csv`) are linked from there. The top right switches between 日本語, English and 中文, and between light and dark |
| 📋 Cases | Every case per environment at the same point (Markdown and CSV on GitHub): a table per Tier with each case's conditions, result and a link to its record |
| 📁 Evidence | The run's own records (the requests sent, the answers received, the summaries, the launch records; see "Where the data is") |

The charts and the case lists show the results of every run measured up to that one. When the same case is in several runs of one environment, they use the run whose name sorts last.

<!-- published-runs:start (scripts/publish.py writes this list) -->
| Finished | Division | Environment | RUN_ID | Tier | Cases (done / all) | Content | See |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2026-11-08 17:24 | Plain (no harness) | GeForce RTX 5070 · Core Ultra 5 235 · 64 GB RAM · SATA SSD | `2026-11-08-gyro-coder` | 0, 1, 2, 3, 4a | 111 / 111 | gyro Gyro-S and coder IQ1_M measured in addition (Tiers 0-4a): the two models 2026-11-06-main had left out for disk space | [📈](https://jun76.github.io/strata-jbench/snapshots/plain/rtx5070-cu5_235-64g-sata/2026-11-08-gyro-coder/?env=rtx5070-cu5_235-64g-sata "Charts") [📋](https://github.com/jun76/strata-jbench/blob/run/plain/rtx5070-cu5_235-64g-sata/2026-11-08-gyro-coder/cases/plain/rtx5070-cu5_235-64g-sata/README.en.md "Cases") [📁](published/plain/rtx5070-cu5_235-64g-sata/2026-11-08-gyro-coder/ "Evidence") |
| 2026-11-08 08:46 | Plain (no harness) | GeForce RTX 5070 · Core Ultra 5 235 · 64 GB RAM · SATA SSD | `2026-11-06-main` | 0, 1, 2, 3, 4a, 4b, 4c, 4d, 5 | 719 / 727 | The first full run on an RTX 5070 · Core Ultra 5 235 (PL1/PL2 65 W) · 64 GB · SATA SSD (Tiers 0-5, 9 models). Unsloth UD-IQ3_XXS and UD-Q3_K_XL were dropped: they streamed their weights from the SSD | [📈](https://jun76.github.io/strata-jbench/snapshots/plain/rtx5070-cu5_235-64g-sata/2026-11-06-main/?env=rtx5070-cu5_235-64g-sata "Charts") [📋](https://github.com/jun76/strata-jbench/blob/run/plain/rtx5070-cu5_235-64g-sata/2026-11-06-main/cases/plain/rtx5070-cu5_235-64g-sata/README.en.md "Cases") [📁](published/plain/rtx5070-cu5_235-64g-sata/2026-11-06-main/ "Evidence") |
| 2026-11-04 22:51 | Plain (no harness) | GeForce RTX 5090 · 128 GB RAM | `2026-11-04-long` | 4b, 4c, 4d | 112 / 112 | Tiers 4b, 4c and 4d (long documents, 32K to 1M, and a YaRN check). 2026-11-03-main skipped them because the long fixtures did not exist yet; a long document was made from ten Japanese and English works of Aozora Bunko and Project Gutenberg and measured | [📈](https://jun76.github.io/strata-jbench/snapshots/plain/rtx5090-128g/2026-11-04-long/?env=rtx5090-128g "Charts") [📋](https://github.com/jun76/strata-jbench/blob/run/plain/rtx5090-128g/2026-11-04-long/cases/plain/rtx5090-128g/README.en.md "Cases") [📁](published/plain/rtx5090-128g/2026-11-04-long/ "Evidence") |

<details>
<summary>Earlier runs (3)</summary>

| Finished | Division | Environment | RUN_ID | Tier | Cases (done / all) | Content | See |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2026-11-04 18:20 | Plain (no harness) | GeForce RTX 5090 · 128 GB RAM | `2026-11-04-q8-t3` | 3 | 9 / 9 | Tier 3 for unsloth Q8_0 (with and without thinking, and the coding task). The first plan left Q8_0 out of Tier 3, so it was added and measured | [📈](https://jun76.github.io/strata-jbench/snapshots/plain/rtx5090-128g/2026-11-04-q8-t3/?env=rtx5090-128g "Charts") [📋](https://github.com/jun76/strata-jbench/blob/run/plain/rtx5090-128g/2026-11-04-q8-t3/cases/plain/rtx5090-128g/README.en.md "Cases") [📁](published/plain/rtx5090-128g/2026-11-04-q8-t3/ "Evidence") |
| 2026-11-04 15:25 | Plain (no harness) | GeForce RTX 5090 · 128 GB RAM | `2026-11-04-iq3s-mtp` | 0, 1, 2, 3, 4a, 5 | 159 / 159 | qwen IQ3_S measured again (in 2026-11-03-main its MTP draft layer was not loaded); the same Tiers, DFlash2 cases included | [📈](https://jun76.github.io/strata-jbench/snapshots/plain/rtx5090-128g/2026-11-04-iq3s-mtp/?env=rtx5090-128g "Charts") [📋](https://github.com/jun76/strata-jbench/blob/run/plain/rtx5090-128g/2026-11-04-iq3s-mtp/cases/plain/rtx5090-128g/README.en.md "Cases") [📁](published/plain/rtx5090-128g/2026-11-04-iq3s-mtp/ "Evidence") |
| 2026-11-04 10:41 | Plain (no harness) | GeForce RTX 5090 · 128 GB RAM | `2026-11-03-main` | 0, 1, 2, 3, 4a, 5 | 1231 / 1231 | The first full run (Tiers 0, 1, 2, 4a, 3, 5; 18 models). qwen IQ3_S ran without MTP here, so the pages use its re-run, 2026-11-04-iq3s-mtp | [📈](https://jun76.github.io/strata-jbench/snapshots/plain/rtx5090-128g/2026-11-03-main/?env=rtx5090-128g "Charts") [📋](https://github.com/jun76/strata-jbench/blob/run/plain/rtx5090-128g/2026-11-03-main/cases/plain/rtx5090-128g/README.en.md "Cases") [📁](published/plain/rtx5090-128g/2026-11-03-main/ "Evidence") |

</details>
<!-- published-runs:end -->

## What is measured

The plain division is measured in Tiers. The cases are defined in [scripts/build_cases.py](scripts/build_cases.py);
"Cases" in the table above shows each case's conditions.

| Tier | What it looks at | Models |
| --- | --- | --- |
| 0 | Whether the measurement itself is right, and how much it varies | Some |
| 1 | Each model's plain speed (prefill and decode, by kind of text, by temperature, by drafter) | All |
| 2 | Speed and sanity answers on standard-v1, the benchmark that ships with Strata | All |
| 3 | How thinking changes the time to answer, the answers and a coding task | All |
| 4 | The cost of reserving context (4a) and reading real long documents (4b–4d, to 1M tokens) | 4a all, 4b–4d representative ones |
| 5 | Changing one launch option at a time (automatic tuning included) | 3 representative ones |

The "Tier" column of the table above says which Tiers each run has.

### How it is measured

- Strata's desktop app is not used. The engine is started on a dedicated port with the CLI's `strata launch --no-tui`,
  and [scripts/bench_runner.py](scripts/bench_runner.py) calls its OpenAI-compatible HTTP API
  (`POST /v1/chat/completions`, streamed) directly. No agent harness and no tool definitions (the plain division); the
  chat template and tokenizing are done by Strata's server. Tier 2 alone runs the bundled
  `strata bench run --suite standard-v1` against the same engine.
- The drafter is fixed to MTP unless a case says otherwise (`--drafting mtp --mtp on`). Thinking and sampling are
  stated in every request.
- The inputs are the fixed prompts in [prompts/](prompts/) (SHA-256 in `MANIFEST.json`). Each request starts with its
  own ID, so that no cache of an earlier answer is used.
- The long document of Tiers 4b–4d is ten out-of-copyright works, Japanese and English in turns (Aozora Bunko: Natsume
  Sōseki, Shimazaki Tōson, Arishima Takeo, Dazai Osamu, Miyazawa Kenji; Project Gutenberg: Melville, Austen, Dickens,
  Shelley, Doyle; sources and editions in [prompts/long-sources.json](prompts/long-sources.json)). Made-up facts are
  placed at 10 / 50 / 90% of it and asked about. Later questions on the same document read it from the prefix cache.
- Nothing else heavy (downloads, conversions, another inference engine) runs during a measurement.

### Environments

Results are kept apart per hardware set-up (a GPU and an amount of RAM: an "environment"). Results of different
environments are never mixed; the buttons at the top of the charts switch between them, and with results in two or
more environments, "Across environments" compares the same models under the same conditions. Each environment's
set-up (GPU, CPU, memory, driver, Strata version) is at the top of the charts and of the case lists, and defined in
[envs/](envs/).

## Where the data is

The records of the runs are in `published/<division>/<environment>/<RUN_ID>/` (only `published/plain/…` so far).

| What | Where |
| --- | --- |
| Per case | `cases/<case id>/summary.json` (the summary), `requests.jsonl` (the requests sent), `responses/` (the answers), `artifact/` (what the coding task made) |
| Per launch | `sessions/<session>/start-N/` (`strata launch` output, the engine log, /settings, /config, /props, telemetry.csv) |
| standard-v1 output | `standard/` |
| Temperature and power over time | `stats/thermal.csv` (every 5 s) |
| The model versions measured | `models.json` (per model, the Hugging Face repository and commit; per file, its size and SHA-256, and whether the file on disk had that SHA-256 when the run started). A model keeps its name when its publisher updates it, so this is what says which version was measured. Linked from the case list's model table and from each RUN_ID line of the charts |
| Queue and runner logs | `queue.log`, `runner.log` |
| What the run is | `NOTE.md` (the "Content" of the table above) |
| The records checked against each other | `verify.json` (the engine's timings against the client's, and whether the launch settings reached the engine) |
| Tuning results | `sessions/*-tune-*/start-1/tune-presets.json`; per model in [configs/tuned/](configs/tuned/) |

The raw streams (SSE and the full thinking text) and the machine snapshots (every process on the PC) are not published.
In the published logs the home folder is written as `~` and the host name as `<host>`.

### What stays on your machine

Running the scripts creates these folders inside the repository. None of them is in Git ([.gitignore](.gitignore)),
and nothing in them is sent anywhere (the only network traffic is downloading the models).

| Folder | Written by | What it holds |
| --- | --- | --- |
| `results/` | `scripts/bench_runner.py` and others | Runs being measured; they stay here until moved to `published/` |
| `results/…/<RUN_ID>/raw/` | `scripts/bench_runner.py` | The raw streams (SSE and the full thinking text); never moved to `published/` |
| `results/…/<RUN_ID>/stats/snapshots.jsonl.gz`, `last.json` | `scripts/stats_watch.py` | **Snapshots of the whole PC during a run.** At each session start, launch, case end, failure and Tier change, and every 5 minutes: every running process (PID, user name, full command line, CPU, memory, disk IO), the processes using the GPU, and CPU, memory, PSI and temperatures. They are for checking afterwards that nothing running beside the benchmark disturbed it. They keep other programs' command lines (with any paths or values given as arguments), so they are never moved to `published/` |
| `preview/` | `scripts/build_cases.py`, `scripts/build_results.py` | Charts and case lists for checking, built with `results/` too |
| `run-status/` | `scripts/bench.py`, `scripts/healthcheck.py`, `scripts/preflight.py` | The state of an unattended run (`STATUS.md`, `ALERTS.log`, `current-run.json`, `preflight.json`) |
| `downloads/` | `scripts/download_models.py`, `scripts/overnight.py` | Download state and logs (`manifest.json` with SHA-256) |
| `work/` | `scripts/overnight.py` (the NVFP4-QAD conversion) | The working folder for the NVFP4-QAD conversion. The long corpus's sources (`work/corpus/raw/`, fetched by hand) are kept here too, and `scripts/long_corpus.py` reads them |

To take no snapshots, set `"stats": false` in `bench.json` before starting. Anything under `results/` can be deleted
once it is no longer needed. `bench.json` at the top of the repository (the benchmark's settings) is outside Git too.

Outside the repository, the model weights go to `~/.local/share/strata/Strata-data/models`, and Strata's launch
profiles (`launch-<model>-<context>`) and Tier 5's tuned presets go into Strata's settings. During a run, a supervisor
process detached from the terminal (`scripts/supervise.py`) and its children are running; no systemd unit is made.

## Running it again

The measurement takes a long time, so it runs unattended under a supervisor process detached from the terminal
(which also restarts a runner that fails or hangs, and records the state). The procedure (preparing an
environment, preflight, starting, watching, recovering, making a run final) is in [AGENTS.md](AGENTS.md),
and how to write an environment in [envs/README.md](envs/README.md).

It needs Strata (the desktop app) installed, with one model installed once, and Strata's source in `~/Strata` (its
`setup.py` pins the files fetched and their SHA-256). The Python environments for downloading and for the NVFP4-QAD
conversion are made by `scripts/setup_acquire.py`, which `scripts/bench.py start` runs by itself. The settings (the
RUN_ID, the division, the Tiers, models and cases to run, and so on) go in `bench.json`; `scripts/bench.py config` lists
every one with its default.

```bash
python3 -I scripts/envs.py list          # the environment this hardware matches
python3 -I scripts/bench.py config        # every setting (bench.json's values and the defaults)
python3 -I scripts/bench.py plan          # the cases chosen and the estimated hours
python3 -I scripts/bench.py start         # check, then start (the supervisor runs detached)
python3 -I scripts/bench.py status        # how it is going
python3 -I scripts/bench.py stop          # stop it (start again with the same run_id resumes)
```

## License

- **Code** (scripts, page templates, the pages' own code): [MIT License](LICENSE)
- **Measurement data** (`published/`, `snapshots/`, `cases/`, `configs/tuned/`, the numbers and charts on the pages):
  [CC BY 4.0](LICENSE-DATA.md). When citing, credit "strata-jbench" with a link to this repository and name the
  environment and RUN_ID (for example `rtx5090-128g / 2026-11-03-main`).
- **The long document's texts** (the ten works in `prompts/long-corpus.txt`): public domain; sources and editions in
  [prompts/long-sources.json](prompts/long-sources.json).
- The models, their names and Strata are under their own authors' licenses.

## Credits

- **[Strata](https://github.com/Niko1221/Strata)** (Niko1221 and the Strata contributors, MIT License): the local LLM
  inference engine measured here. Tier 2's standard-v1 is the benchmark that ships with it.
- **[Aozora Bunko](https://www.aozora.gr.jp/)**: the five Japanese works of the long document (Natsume Sōseki, *I Am a
  Cat*; Shimazaki Tōson, *The Broken Commandment*; Arishima Takeo, *A Certain Woman*; Dazai Osamu, *No Longer Human*;
  Miyazawa Kenji, *Night on the Galactic Railroad*). Thanks to the volunteers who typed and proofread them; each work's
  edition and credits are kept in `prompts/long-sources.json`.
- **[Project Gutenberg](https://www.gutenberg.org/)**: the five English works (Melville, *Moby-Dick*; Austen, *Pride and
  Prejudice*; Dickens, *A Tale of Two Cities*; Shelley, *Frankenstein*; Doyle, *The Adventures of Sherlock Holmes*). As
  its terms ask, only the texts are used, without its header, license and trademark.
- **Models**: Qwen3.8-Flash-Next (Qwen), and the authors of its quantized and derived versions:

| Repository | Name in this benchmark |
| --- | --- |
| [ISTA-DASLab/Qwen3.8-Flash-Next-GSQ-RCO-GGUF](https://huggingface.co/ISTA-DASLab/Qwen3.8-Flash-Next-GSQ-RCO-GGUF) | qwen Q2_0, IQ2_XS, IQ3_XXS, IQ3_S |
| [ISTA-DASLab/Qwen3.8-Flash-Next-GSQ-RCO-Coder-GGUF](https://huggingface.co/ISTA-DASLab/Qwen3.8-Flash-Next-GSQ-RCO-Coder-GGUF) | coder IQ1_M |
| [agentionai/Qwen3.8-Flash-Next-Gyro-GGUF](https://huggingface.co/agentionai/Qwen3.8-Flash-Next-Gyro-GGUF) | gyro Gyro-S, Gyro-M |
| [unsloth/Qwen3.8-Flash-Next-GGUF](https://huggingface.co/unsloth/Qwen3.8-Flash-Next-GGUF) | unsloth UD-IQ4_XS, UD-Q4_K_XL, UD-Q5_K_XL, UD-Q6_K_XL, Q8_0 |
| [ukisai/Swift-1.5-Qwen3.8-Flash-Next-GSQ-RCO-GGUF](https://huggingface.co/ukisai/Swift-1.5-Qwen3.8-Flash-Next-GSQ-RCO-GGUF) | swift IQ2_XS, IQ3_XXS, IQ3_S |
| [Maximilian228/Qwen3.8-Flash-Next-NVFP4-GPTQ-Strata](https://huggingface.co/Maximilian228/Qwen3.8-Flash-Next-NVFP4-GPTQ-Strata) | nvfp4 NVFP4 |
| [Maximilian228/Qwen3.8-Flash-Next-NVIDIA-NVFP4-Strata](https://huggingface.co/Maximilian228/Qwen3.8-Flash-Next-NVIDIA-NVFP4-Strata) | nvfp4 NVFP4-NVIDIA |
| [nvidia/Qwen3.8-Flash-Next-FP4-Local](https://huggingface.co/nvidia/Qwen3.8-Flash-Next-FP4-Local) | nvfp4 NVFP4-QAD (retrained for FP4; converted to Strata's format on the measuring PC with Strata's own tool, by `scripts/overnight.py`) |
