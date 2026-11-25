<p align="center"><picture>
  <source media="(prefers-color-scheme: dark)" srcset="media/strata-jbench.png">
  <img src="media/strata-jbench-light.png" alt="strata-jbench" width="560">
</picture></p>

[日本語](README.md) | **English** | [中文](README.zh.md)

A benchmark for measuring models with **the same ruler** on the local LLM inference engine [Strata](https://github.com/Niko1221/Strata) and engines derived from it, and its results.
Fixed prompts are sent under fixed conditions; speed, waits, correctness and the pages written are recorded. The plan, the measuring scripts and the raw records are here too, so anyone can measure the same way.

- **What to choose for which number, and how long it takes**: [the configurator](https://jun76.github.io/strata-jbench/configurator/) (pick in the browser; it writes the conditions as one text, the "recipe")
- **Measuring on your own PC**: clone this repository and ask an agent (Claude Code, say) to "measure with strata-jbench". The procedure is the [skill](.claude/skills/strata-jbench/SKILL.md) that comes with it ([Running it again](#running-it-again))

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
| 2026-11-22 15:52 | Plain (no harness) | GeForce RTX 5090 · 128 GB RAM | `2026-11-22-hy4` | 1, 2, 3, 4a, 4b | 140 / 147 | Added Tencent Hy4-Flash (SQ-64, SQ-96, SQ-128), supported since Strata 0.2.18, and measured it (Tiers 1-4b, 140 of 147 cases done). 1M ran out of GPU memory at launch, and SQ-128's 256K document is longer than the window in Hy4's tokenizer, so neither was measured | [📈](https://jun76.github.io/strata-jbench/snapshots/plain/rtx5090-128g/2026-11-22-hy4/?env=rtx5090-128g "Charts") [📋](https://github.com/jun76/strata-jbench/blob/run/plain/rtx5090-128g/2026-11-22-hy4/cases/plain/rtx5090-128g/README.en.md "Cases") [📁](published/plain/rtx5090-128g/2026-11-22-hy4/ "Evidence") |
| 2026-11-19 16:39 | Plain (no harness) | GeForce RTX 5070 · Core Ultra 5 235 · 64 GB RAM · SATA SSD | `2026-11-19-sync-r10` | 1 | 54 / 54 | Tier 1 for Sync-XS, Sync-S and Sync-M on Sync-Strata 0.1.1 at R10 (tail skip off), 128K context, k8v4 KV and MTP. All 54 cases and 162 requests passed. | [📈](https://jun76.github.io/strata-jbench/snapshots/plain/rtx5070-cu5_235-64g-sata/2026-11-19-sync-r10/?env=rtx5070-cu5_235-64g-sata "Charts") [📋](https://github.com/jun76/strata-jbench/blob/run/plain/rtx5070-cu5_235-64g-sata/2026-11-19-sync-r10/cases/plain/rtx5070-cu5_235-64g-sata/README.en.md "Cases") [📁](published/plain/rtx5070-cu5_235-64g-sata/2026-11-19-sync-r10/ "Evidence") |
| 2026-11-10 06:23 | Plain (no harness) | GeForce RTX 5070 · Core Ultra 5 235 · 64 GB RAM · SATA SSD | `2026-11-09-harbor-gyro-long-t5` | 0, 3, 4b, 4c, 5 | 224 / 236 | The cases not measured yet: the coding task "A sailing ship calling at a harbor" on all 11 models (Tiers 0 and 3), long documents on gyro Gyro-S, Gyro-M and unsloth UD-Q2_K_XL (Tiers 4b, 4c), and launch options on Gyro-S and Gyro-M (Tier 5). In Tier 3, 16 of the 33 harbor runs drew a scene and 1 was cut off. The 12 vram-reserve 40% / 50% cases did not launch: the model no longer fit in the 12 GB of VRAM | [📈](https://jun76.github.io/strata-jbench/snapshots/plain/rtx5070-cu5_235-64g-sata/2026-11-09-harbor-gyro-long-t5/?env=rtx5070-cu5_235-64g-sata "Charts") [📋](https://github.com/jun76/strata-jbench/blob/run/plain/rtx5070-cu5_235-64g-sata/2026-11-09-harbor-gyro-long-t5/cases/plain/rtx5070-cu5_235-64g-sata/README.en.md "Cases") [📁](published/plain/rtx5070-cu5_235-64g-sata/2026-11-09-harbor-gyro-long-t5/ "Evidence") |

<details>
<summary>Earlier runs (7)</summary>

| Finished | Division | Environment | RUN_ID | Tier | Cases (done / all) | Content | See |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2026-11-09 05:24 | Plain (no harness) | GeForce RTX 5090 · 128 GB RAM | `2026-11-09-harbor` | 0, 3 | 21 / 21 | Plain's coding task replaced by "A sailing ship calling at a harbor" (3D voxel art in one HTML file, the scene given by its title alone) and measured (Tiers 0 and 3, 20 models). With 64K of thinking and 130,048 output tokens, none of the 60 runs was cut off and 36 drew a scene | [📈](https://jun76.github.io/strata-jbench/snapshots/plain/rtx5090-128g/2026-11-09-harbor/?env=rtx5090-128g "Charts") [📋](https://github.com/jun76/strata-jbench/blob/run/plain/rtx5090-128g/2026-11-09-harbor/cases/plain/rtx5090-128g/README.en.md "Cases") [📁](published/plain/rtx5090-128g/2026-11-09-harbor/ "Evidence") |
| 2026-11-08 17:24 | Plain (no harness) | GeForce RTX 5070 · Core Ultra 5 235 · 64 GB RAM · SATA SSD | `2026-11-08-gyro-coder` | 0, 1, 2, 3, 4a | 111 / 111 | gyro Gyro-S and coder IQ1_M measured in addition (Tiers 0-4a): the two models 2026-11-06-main had left out for disk space | [📈](https://jun76.github.io/strata-jbench/snapshots/plain/rtx5070-cu5_235-64g-sata/2026-11-08-gyro-coder/?env=rtx5070-cu5_235-64g-sata "Charts") [📋](https://github.com/jun76/strata-jbench/blob/run/plain/rtx5070-cu5_235-64g-sata/2026-11-08-gyro-coder/cases/plain/rtx5070-cu5_235-64g-sata/README.en.md "Cases") [📁](published/plain/rtx5070-cu5_235-64g-sata/2026-11-08-gyro-coder/ "Evidence") |
| 2026-11-08 08:46 | Plain (no harness) | GeForce RTX 5070 · Core Ultra 5 235 · 64 GB RAM · SATA SSD | `2026-11-06-main` | 0, 1, 2, 3, 4a, 4b, 4c, 4d, 5 | 719 / 727 | The first full run on an RTX 5070 · Core Ultra 5 235 (PL1/PL2 65 W) · 64 GB · SATA SSD (Tiers 0-5, 9 models). Unsloth UD-IQ3_XXS and UD-Q3_K_XL were dropped: they streamed their weights from the SSD | [📈](https://jun76.github.io/strata-jbench/snapshots/plain/rtx5070-cu5_235-64g-sata/2026-11-06-main/?env=rtx5070-cu5_235-64g-sata "Charts") [📋](https://github.com/jun76/strata-jbench/blob/run/plain/rtx5070-cu5_235-64g-sata/2026-11-06-main/cases/plain/rtx5070-cu5_235-64g-sata/README.en.md "Cases") [📁](published/plain/rtx5070-cu5_235-64g-sata/2026-11-06-main/ "Evidence") |
| 2026-11-04 22:51 | Plain (no harness) | GeForce RTX 5090 · 128 GB RAM | `2026-11-04-long` | 4b, 4c, 4d | 112 / 112 | Tiers 4b, 4c and 4d (long documents, 32K to 1M, and a YaRN check). 2026-11-03-main skipped them because the long fixtures did not exist yet; a long document was made from ten Japanese and English works of Aozora Bunko and Project Gutenberg and measured | [📈](https://jun76.github.io/strata-jbench/snapshots/plain/rtx5090-128g/2026-11-04-long/?env=rtx5090-128g "Charts") [📋](https://github.com/jun76/strata-jbench/blob/run/plain/rtx5090-128g/2026-11-04-long/cases/plain/rtx5090-128g/README.en.md "Cases") [📁](published/plain/rtx5090-128g/2026-11-04-long/ "Evidence") |
| 2026-11-04 18:20 | Plain (no harness) | GeForce RTX 5090 · 128 GB RAM | `2026-11-04-q8-t3` | 3 | 9 / 9 | Tier 3 for unsloth Q8_0 (with and without thinking, and the coding task). The first plan left Q8_0 out of Tier 3, so it was added and measured | [📈](https://jun76.github.io/strata-jbench/snapshots/plain/rtx5090-128g/2026-11-04-q8-t3/?env=rtx5090-128g "Charts") [📋](https://github.com/jun76/strata-jbench/blob/run/plain/rtx5090-128g/2026-11-04-q8-t3/cases/plain/rtx5090-128g/README.en.md "Cases") [📁](published/plain/rtx5090-128g/2026-11-04-q8-t3/ "Evidence") |
| 2026-11-04 15:25 | Plain (no harness) | GeForce RTX 5090 · 128 GB RAM | `2026-11-04-iq3s-mtp` | 0, 1, 2, 3, 4a, 5 | 159 / 159 | qwen IQ3_S measured again (in 2026-11-03-main its MTP draft layer was not loaded); the same Tiers, DFlash2 cases included | [📈](https://jun76.github.io/strata-jbench/snapshots/plain/rtx5090-128g/2026-11-04-iq3s-mtp/?env=rtx5090-128g "Charts") [📋](https://github.com/jun76/strata-jbench/blob/run/plain/rtx5090-128g/2026-11-04-iq3s-mtp/cases/plain/rtx5090-128g/README.en.md "Cases") [📁](published/plain/rtx5090-128g/2026-11-04-iq3s-mtp/ "Evidence") |
| 2026-11-04 10:41 | Plain (no harness) | GeForce RTX 5090 · 128 GB RAM | `2026-11-03-main` | 0, 1, 2, 3, 4a, 5 | 1231 / 1231 | The first full run (Tiers 0, 1, 2, 4a, 3, 5; 18 models). qwen IQ3_S ran without MTP here, so the pages use its re-run, 2026-11-04-iq3s-mtp | [📈](https://jun76.github.io/strata-jbench/snapshots/plain/rtx5090-128g/2026-11-03-main/?env=rtx5090-128g "Charts") [📋](https://github.com/jun76/strata-jbench/blob/run/plain/rtx5090-128g/2026-11-03-main/cases/plain/rtx5090-128g/README.en.md "Cases") [📁](published/plain/rtx5090-128g/2026-11-03-main/ "Evidence") |

</details>
<!-- published-runs:end -->

## What is measured

One run measures **one engine** (Strata, a derived engine, or an engine already running) on **one environment** (that PC's hardware) for the **models** and **tasks** chosen.

### Tasks

| Task | What it answers | What is sent |
| --- | --- | --- |
| **Writing speed**<br>`speed-decode` | How fast does it write? | Five short instructions (Japanese prose, English prose, JSON, Python code, copying a given text), up to 512 output tokens, at temperature 0 / 0.7 / 1.0, thinking off, 3 times each. Models that have DFlash2 are measured once more with it |
| **Reading speed**<br>`speed-prefill` | How fast does it read a long input, and how long until the first character? | A fixed list of records cut to exactly 4K / 32K / 128,000 tokens (built as Strata's standard-v1 builds its own), up to 128 output tokens, temperature 0.7, thinking off, 3 times each |
| **Strata's own standard benchmark**<br>`official-standard` | What does Strata's standard benchmark (standard-v1) give? | strata bench run --suite standard-v1 as it is, 3 times (thinking xhigh, temperature 1.0, 9 performance requests + 12 sanity checks). Its fixtures are sized with the Qwen3.8 tokenizer; on another base model the token counts differ |
| **Thinking and answering**<br>`think-qa` | What does thinking do to the time to an answer, and to getting it right? | Four tasks whose answers are checked automatically (math, code judged by running its tests, reasoning in Japanese, reasoning in English), with thinking off and on (xhigh), up to 16,384 output tokens, temperature 1.0, 3 times each. A model without thinking: off only |
| **A page from one request**<br>`code-oneshot` | Can it write a working page from one request? | An English request for the scene "A sailing ship calling at a harbor" as 3D voxel art in one HTML file. Thinking 64K, output up to the whole 128K window, temperature 1.0, 3 times. Each page runs 10 s in headless Chrome; its errors, whether it froze and whether anything was drawn are recorded |
| **The cost of reserving context**<br>`context-reserve` | Does reserving a larger context alone make it slower? | Launched with a 128K / 256K / 1M context, the same 4K input + 512 output 3 times. Whether it starts at 1M at all shows here too |
| **Reading long documents**<br>`long-read` | Given a really long document, how fast is it and does it answer right? (up to 1M tokens) | A document made of ten works from Aozora Bunko and Project Gutenberg (Japanese and English) at 32K / 128K / 256K (trained range) and 512K / 1M (extended). One question per fact planted at 10% / 50% / 90%, then one that needs several places. 3 times each. Representative models only |
| **The effect of YaRN**<br>`yarn-check` | Does the setting for going past the trained length (YaRN) change the result on the same input? | About 300K of input at a 384K context with and without YaRN, and about 200K at 256K and at 1M. The reference model only |
| **What launch options do**<br>`launch-options` | Which launch options matter? | One change at a time from the baseline launch (drafter, draft depth, KV format, prefill chunk, VRAM reserve, vision, CPU assignment, where the PLE table lives, parallel slots, auto tune), two writing and two reading cases 3 times each. Representative models only |
| **Checking the instruments**<br>`selfcheck` | Are the measurements right, and how much do they vary between launches? | Writing and reading speed on the reference model over 3 separate launches; Gyro-S under its author's published protocol against the published figures; the coding task once, to check that the page is extracted. Once per environment |
| **Handing it to an agent**<br>`agent-oneshot` | Handed to an agent harness in one shot, how long does it take and what comes out? | "Make a Minecraft-like 3D sandbox game" (in Japanese), handed to the harness in one shot with no format instructions. Thinking 32K, output up to the whole window, 3,600 s per run, 3 times. A recording proxy sets sampling, thinking, seed and the output cap alike for every harness |

Presets bundle the tasks: `quick` (the two headline speed numbers, minutes), `standard` (writing, reading, thinking and answering, a page from one request), `full` (everything).
Which cases a task has, and each case's conditions, are in the case lists linked above (a Tier is a task's earlier name; the lists and the charts still show both). They are defined in [catalog/tasks.json](catalog/tasks.json) and [scripts/case_plan.py](scripts/case_plan.py).

### Headline numbers

The numbers shown first are each read from **one fixed condition**. A summary over several kinds of cases (a mean, a median of medians) is never a headline.

| Name | Definition |
| --- | --- |
| **JB-decode** Writing speed | decode tok/s writing English prose: temperature 0.7, thinking off, context 128K, the drafter the engine picks by itself (Strata's Auto: DFlash2 where the model has it, else MTP or the build's own), median of 3 runs |
| **JB-ttft-32k** First character after reading 32K | Seconds from sending a 32K-token input to the first character: thinking off, context 128K, median of 3 runs |
| **JB-answer** Thinking and answering | Tasks answered right out of 4 with thinking on (right when at least 2 of 3 runs are), and the median seconds to the end. A model without thinking: its thinking-off values |
| **JB-page** Pages from one request | Of 3 runs, the pages that were drawn without an error (0 to 3) |
| **JB-agent** Handed to an agent | Of 3 runs, the games that were drawn (0 to 3), and the median seconds to the end |

The breakdowns (by kind of text, temperature, drafter and so on) are all on the chart pages. Every metric is defined in one line in [catalog/metrics.json](catalog/metrics.json).

### Engines and models

| Engine | How it is measured |
| --- | --- |
| **Strata** (`strata`) | Strata itself. Started with `strata launch`; the choices asked for are checked against the engine's own command line. |
| **Sync-Strata** (`sync-strata`) | A fork of Strata that runs Qwen3.8-Flash-Next in its own quantizations Sync-XS / S / M (formats not compatible with upstream). Started with `sync up --api-only`, with a settings folder of its own per run. |
| **OpenAI-compatible endpoint (attach only)** (`endpoint`) | Attach to the URL of an engine that is already running. jbench neither starts nor stops it, so how it was started cannot be checked (the results say "attach only"). For a first try of an engine that has no adapter. |

A setting that trades quality for speed (Sync-Strata's tail skip, say) is off by default (`exact`). Results with the engine as it comes (`default`) are kept apart and never mixed in.

The models are in [catalog/models/](catalog/models/), one file per base model: Qwen3.8-Flash-Next (28 builds), Tencent Hy4-Flash (3 builds), Thinking Machines Inkling 2 Mini (3 builds). Models with the same tokenizer get the same number of input tokens, so their tok/s compare directly; across tokenizers they are a reference only.

### The same ruler

- What a run measures is one text, the recipe; its id (a hash of the engine, the track, the driver and the tasks with their versions) goes with the results.
- Every case also carries the hash of its own conditions (the prompt's SHA-256, the context, the launch options, thinking, the temperature, the output cap, the seeds). Only cases with the same hash are put side by side across environments.
- A case whose settings could not be confirmed on the engine is kept as a failure, never as a speed.

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

A run takes hours, so it runs unattended under a supervisor process detached from the terminal (which also restarts a stuck case and records the state).

**With an agent** (recommended): clone this repository and ask an agent such as Claude Code to "measure with strata-jbench".
The [strata-jbench skill](.claude/skills/strata-jbench/SKILL.md) in the repository takes it from checking the environment, through choosing in the configurator, the plan and what is missing, to starting, watching and checking the results.
For an engine, a harness or a model that is missing it asks first: may it be fetched into `tools/` inside the repository (not in Git), or is it on the PC already, and where.

**By hand**:

```bash
python3 -I scripts/envs.py list                  # the environment this hardware matches
python3 -I scripts/build_configurator.py         # writes preview/configurator.html (open it and choose)
python3 -I scripts/bench.py recipe --apply FILE  # the recipe you copied, into bench.json
python3 -I scripts/bench.py plan                 # the cases chosen and the estimated hours
python3 -I scripts/acquire.py check              # what is missing (models, the engine, a harness)
python3 -I scripts/bench.py start                # checks, then starts (the supervisor runs detached)
python3 -I scripts/bench.py status               # how it is going
python3 -I scripts/bench.py stop                 # stop (start again with the same run_id to resume)
```

Measuring Strata itself needs Strata (the desktop app) installed with one model installed through it once, and Strata's source checked out at `~/Strata` (its `setup.py` pins the files fetched and their SHA-256).
The whole procedure is in [AGENTS.md](AGENTS.md) and the skill's [references/](.claude/skills/strata-jbench/references/); how to write an environment is in [envs/README.md](envs/README.md).
To offer results you measured, send the run made final (`published/<division>/<env>/<RUN_ID>/`) as a pull request.

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
- **[Sync-Strata](https://github.com/hiruhiru2005/sync-strata)** (hiruhiru2005): a fork of Strata with its own quantizations Sync-XS / S / M, measured here as a derived engine.
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
