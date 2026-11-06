# AGENTS.md — for agents working on strata-jbench

A repository for measuring several models with Strata (a local LLM inference engine) and publishing the results so
that anyone can run them again.
The plan is [docs/SCOUTING.md](docs/SCOUTING.md) (internal notes, not in Git); every case per environment is in the
case lists, [cases/](cases/README.md) (Markdown and CSV read on GitHub, built by `scripts/build_cases.py`, which also
writes `plan/<division>/<env>/cases.jsonl`), and the charts are one page per published run under `snapshots/`, served
by GitHub Pages (`scripts/build_results.py`).

This document sets the procedure for long-running work such as fetching models and running the benchmark.

**Environment:** the hardware set-up the benchmark runs on (a GPU and an amount of RAM; swapping the card or adding
RAM makes another environment). `envs/<env>/env.json` is one environment; its plan is in `plan/<division>/<env>/`, its
results in `results/<division>/<env>/<RUN_ID>/`, its case list in `cases/<division>/<env>/`.
The environment is never typed by hand: `scripts/envs.py` picks the env.json that matches the hardware found now (GPU
name and RAM). With no matching environment, or with one named that does not match, preflight and the runner do not
start measuring. Fields and how to write one: [envs/README.md](envs/README.md).

**Division:** how the models are driven. It is independent of the environment; `divisions/<division>/division.json` is
one division ([divisions/README.md](divisions/README.md)). Everything measured so far is `plain` (no harness: the runner
calls the engine's API directly, no tool calls). `strata`, `dsh` and `opencode` (divisions through an agent harness) are
planned and cannot be measured while their `status` is `planned` (picked with `BENCH_DIVISION`; `plain` when unset).
Plans, results and case lists are kept in a folder per division.

**Working and published:** measurements are written to `results/` (not in Git), and only the RUN_IDs made final are
moved to `published/` (in Git) by `scripts/publish.py`. What is committed is built from `published/` alone: the case
lists (`cases/`, `build_cases.py --published`) and, per published run, the charts as they were when it was published
(`snapshots/<division>/<env>/<RUN_ID>/index.html` and `summary.csv`, `build_results.py --snapshot`; never rewritten).
Lists and charts built while measuring, or to check, also read `results/` and are written to `preview/` (not in Git),
so a running benchmark never changes what Git tracks.
The distinction between working and final is for the procedure only: the READMEs present every run in `published/`
as simply a result (no "final" or "published" wording in their results section), newest first.

## 1. Principles

1. **Long-running work runs neither in the agent's session nor in a terminal.**
   `scripts/start_pipeline.sh` starts it as systemd user units. The agent only starts, checks and recovers it, and does
   not wait for it to finish (no `sleep` loops or "wake me when it is done" waits over long-running work).
2. **Ask every question that needs a decision before starting.** Never leave a run waiting for a decision halfway.
3. **Preflight before starting.** The later a stage would fail, the more it deserves a cheap real run first
   (`scripts/preflight.py`). If anything is NG, start nothing.
4. **A stage that ended without results is FAILED.** Never treat it as "they will turn up if we wait". Whoever waits
   checks the other side's PID and result files.
5. **Check or stop our own scripts by their recorded PID (`kill -0`) or with `systemctl --user`.**
   Do not use `pgrep -f` / `pkill -f`: the string also matches other shells that mention the script's name (the agent's
   own shell included).
6. **Watch in two layers.** A systemd timer runs the healthcheck (every 15 minutes: detect and notify), and a scheduled
   task (hourly: find the cause, recover safely, report). Both run independently of the agent's session.
   The scheduled task runs whether a benchmark is running or not, so it exists only while one is: registered when a
   run starts and deleted when it ends, each time with the user's agreement (2.3, 2.6).
7. **Keep progress in files,** not in the conversation's memory: the state in `run-status/STATUS.md`, problems in
   `run-status/ALERTS.log`, each stage's logs as in section 4.
8. **Nothing else heavy during a measurement.** No downloads, conversions or another inference engine at the same time.

## 2. Procedures

### 2.0 When the hardware changes (another card, more RAM, another PC)
On a PC that has not run the benchmark yet, first: Strata (the desktop app) installed with one model installed through
it once (that writes `~/.local/share/strata/install/third_party/llama.cpp`), and Strata's source checked out at
`~/Strata` (its `setup.py` pins every file fetched). `scripts/setup_acquire.py` then makes the rest (the venvs, the
download list, the NVFP4-QAD converter); `scripts/start_pipeline.sh` runs it by itself. After the models are on disk,
the NVFP4 ready-made packs need Strata's setup once with `--no-start` to write their run configs (otherwise
`strata launch --plan` reports them as needing a download); it changes Strata's saved settings, so section 3 applies.

1. `python3 -I scripts/envs.py list` shows whether an environment matches the hardware now (marked `*`).
2. If none does, `python3 -I scripts/envs.py new <env>` writes `envs/<env>/env.json` (ids like `rtx5070-64g`: GPU and
   RAM). On a PC with two cards each card is an environment of its own: `--gpu N` picks the card (`gpu_index`; the
   runner launches with `--gpu N` and reads that card alone). When two environments match the PC, name one with `BENCH_ENV`. It fills in the GPU name, VRAM, RAM and whether DFlash2 is available (checked with `strata launch --plan`).
   Then fill in by hand:
   - `memory`: the output of `sudo dmidecode -t memory` (type, speed, modules; it needs root, so ask the user to run it)
   - `gpu_power_limit_w`: the power limit, if one is set for measuring; `null` to measure at the card's default
   - `cpu_power_limit_w`: the CPU's PL1 / PL2 (`{"pl1": 65, "pl2": 65}`), if set for measuring (in the BIOS; a
     system setting, so the user does it); `null` to measure at the board's setting. Preflight compares it with Intel
     RAPL, and machine.json records the limits in force either way
   - `models`: the list (in the form `"qwen IQ3_S"`) to measure only some models; `null` for every model of
     `scripts/build_cases.py` (including models added later). The downloads follow it too: `scripts/setup_acquire.py`
     lists only these models in `downloads/manifest.json`, and writes it again (removing `downloads/READY`) when it changes
3. The GPU power-limit unit `gpu-power-limit.service` is fixed at 500 W (for the RTX 5090). On another card, ask the
   user to disable it (`sudo systemctl disable --now gpu-power-limit.service`) or change the value (it is a system
   setting, so the agent does not do it).
4. `python3 -I scripts/build_cases.py` writes that environment's plan (`plan/<division>/<env>/`) and case list
   (`cases/<division>/<env>/`); check the number of cases and the estimate. The model size classes used for the
   estimate (small / edge / large against RAM + VRAM) come from that environment's VRAM and RAM (they are not shown on
   the pages).
5. Strata's launch settings (`~/.local/share/strata/install/`) were written by setup for the GPU of that time. After a
   card change, run the preflight of 2.2 (a real smoke launch) and one case under a `test-` RUN_ID, and check the launch
   settings in `sessions/*/start-1/launch.txt`.
6. From 2.2 on, everything is the same. RUN_IDs live in a folder per environment, so the same name in another
   environment does not clash.

### 2.1 When the plan changes
1. Edit `scripts/build_cases.py` (the only place cases are defined; differences between environments go in env.json).
2. Run `python3 -I scripts/build_cases.py` and check the number of cases and the estimated hours per environment.
   `preview/cases/` and `plan/<division>/<env>/cases.jsonl` are updated (`--published` for the committed `cases/`).
   The case lists have a Markdown file per language (`README.md`, `README.en.md`, `README.zh.md`, `tier-<Tier>.md`
   and so on) and the charts switch between Japanese, English and Chinese. When a case definition gains a Japanese
   string, add its English and Chinese to `TR` in `scripts/i18n.py` (strings without a translation are listed when the
   script runs, and shown in Japanese).
3. If a new fixture is needed, change `scripts/build_fixtures.py` and run it with the Python that ships with Strata (see
   the docstring at the top of the file).
   The long document of Tiers 4b–4d comes from ten works of Aozora Bunko and Project Gutenberg (five Japanese, five
   English), cleaned by `scripts/long_corpus.py` into `prompts/long-corpus.txt`, Japanese and English chunks in turns.
   Sources, editions, SHA-256 and Aozora's colophons are in `prompts/long-sources.json`; the downloads are in
   `work/corpus/raw/` (not in Git). A long fixture holds only the number of corpus lines, the made-up facts placed at
   10 / 50 / 90% ("the passwords of the east, central and west storehouses") and the questions; the runner assembles
   the document.
4. Update the matching part of [docs/SCOUTING.md](docs/SCOUTING.md) too.

### 2.2 Checks before starting (do not start until these pass)
1. Ask the user and get an answer for each of these:
   - Which environment to measure in (is the result of `python3 -I scripts/envs.py detect` the set-up the user meant?).
   - Whether a Strata engine other than the measuring one (the desktop app, say) is using the GPU (`nvidia-smi`,
     `pgrep -af "strata --serve"`), and if so, whether it may be stopped.
   - The RUN_ID and the Tiers (a new RUN_ID, or resuming an existing one).
   - Whether it runs across a logout. systemd user units stop at logout while linger is off; to run across one,
     `loginctl enable-linger` is needed (a system setting: the user does it).
   - Whether anything in section 3 ("Ask first") may become necessary during the run; if so, have the user decide
     beforehand what to do.
   - That the hourly watch task will be registered at the start (step 3 of 2.3) and deleted at the end (2.6).
2. After changing the runner or a fixture, run the affected cases under a RUN_ID starting with `test-` (`test-` results
   appear neither in the case lists nor in the charts):
   `python3 scripts/bench_runner.py --run-id test-xxx --steps 1 --ids <case id>,...`
3. `python3 scripts/preflight.py --phase all --steps "0,1,2,3,4a,4b,4c,4d,5"` (`--phase acquire` before every model is
   on disk). If anything is NG, fix it and run it again. The result is `run-status/preflight.json`.
   Preflight also checks the environment (which env.json this hardware is, that the plan is newer than env.json, and
   that the power limit is env.json's).

### 2.3 Starting
1. Start it:
   ```bash
   RUN_ID=<run id> STEPS="0 1 2 3 4a 4b 4c 4d 5" scripts/start_pipeline.sh
   ```
   The environment is found automatically, and the first line printed is
   `division: <division>, environment: <env>, run: results/<division>/<env>/<RUN_ID>`. With no matching environment,
   nothing starts. To measure only some models, add `MODELS="qwen:IQ3_S,..."` (for a re-run, say; the healthcheck's
   "cases without a result" then looks at those models only). The environment, RUN_ID, STEPS and MODELS started are
   kept in `run-status/current-run.json` (the watch task reads it, so a new RUN_ID needs no change to the task).
   - `strata-jbench-acquire`: `scripts/setup_acquire.py` first, then `scripts/overnight.py` (fetch the models → convert NVFP4-QAD → delete the conversion source
     → fetch the last model). Not started when `downloads/READY` exists.
   - `strata-jbench-queue`: `scripts/overnight_bench.sh` (wait for READY → Strata's run configs for the downloaded models,
     `scripts/install_configs.py` → preflight → `scripts/bench_runner.py` Tier by Tier). The run configs change Strata's
     saved settings (section 3): agree on it in 2.2.
   - `strata-jbench-health.timer`: `scripts/healthcheck.py` every 15 minutes.
   - `strata-jbench-stats`: `scripts/stats_watch.py` (follows runner.log and, at each session start, launch, case end,
     failure and Tier change, and every 5 minutes, takes a snapshot of the process list, CPU, memory, PSI, disk IO,
     temperatures and GPU). It ends by itself when the queue ends. Running `scripts/start_pipeline.sh` again attaches it
     to a RUN_ID already running (the queue is not touched).
2. Check that the STATUS printed right after starting is RUNNING or WAITING.
3. With the user's agreement from 2.2, register the hourly watch task with a scheduler (for example the desktop app's
   scheduled tasks, `taskId: strata-jbench-watch`). Its prompt must be self-contained, with the steps of 2.4 and
   section 3, and must say that the task does not delete itself: when the run is DONE, or stopped with no resume
   planned, its report says so and asks for the task to be deleted. If one is left over from an earlier run, check
   that it is enabled and that its prompt is still right. If it cannot be registered, do not report the run as
   started: tell the user why and have them decide on another way.
4. Report the expected end time and what happens if something goes wrong (notifications, recovery by the watch task).

To stop: `scripts/start_pipeline.sh --stop`. If the run will not be resumed, delete the watch task as in 2.6.

### 2.4 When something goes wrong (healthcheck FAILED / STUCK)
Read the logs and find the cause before acting. Never restart again and again without knowing why.

| Stage | Look at | Safe recovery |
| --- | --- | --- |
| acquire/download* | `downloads/overnight.log`, the end of `downloads/download.log`, `downloads/status.json` | For a passing network problem, `scripts/start_pipeline.sh` resumes (it goes on from where it stopped) |
| acquire/qad | `downloads/qad-prepare.log` | Fix the cause, then resume; finished steps are skipped by their `.done` marks |
| bench | `results/<division>/<env>/<RUN_ID>/queue.log`, its `runner.log`, the matching `sessions/*/start-*/launch.txt` and `engine.log` | Fix the cause, then `scripts/start_pipeline.sh`; finished cases are skipped |
| bench preflight | `run-status/preflight.json` | Fix the failing items |

After fixing a code or environment problem, run one affected case under a `test-` RUN_ID before resuming.

### 2.5 Checking the results
1. Read `run-status/STATUS.md` and `run-status/ALERTS.log` (STATUS.md's first line gives the environment and RUN_ID).
2. `python3 -I scripts/build_cases.py` puts the results into the case list (`preview/cases/<division>/<env>/`), and
   `python3 -I scripts/build_results.py` into the charts, `preview/RESULTS.html`, and `preview/summary.csv` (every
   environment, with an `env` column); the queue runs both after each Tier. `preview/` reads both `results/` and
   `published/` and is for checking; it says "Preview" at the top.
   The charts switch environments with the buttons at the top, and with results in two or more environments,
   "Across environments" appears (`?env=<env>` opens a given environment).
   When the same case is in several RUN_IDs of one environment, both use the RUN_ID whose name sorts last. To
   measure again under changed conditions, delete the old RUN_ID's results or use a RUN_ID that sorts later (`test-`
   RUN_IDs are never shown). Another environment is another case.

### 2.6 When the run ends
The watch task keeps firing every hour after the queue ends, so remove it as soon as the run is over.
1. The run is over when STATUS is DONE, or when it is FAILED or stopped and the user has decided not to resume it.
   A FAILED run that will be resumed after a fix is not over: keep the task.
2. Ask the user whether the watch task (`strata-jbench-watch`) may be deleted, and delete it only after they agree
   (the desktop app: the "Scheduled" section of the sidebar, or the scheduled-tasks tool). If the agent cannot delete
   it, ask the user to.
3. Check with the scheduler's list that no watch task is left.

### 2.7 Making results final and committing them
1. The user decides which RUN_ID becomes final (so that results meant to be thrown away are never published).
2. `python3 -I scripts/publish.py <env> <RUN_ID> --dry-run` shows how many files would move, and their size.
3. `python3 -I scripts/publish.py <env> <RUN_ID> --note "<one line on the run>"` moves it to
   `published/<division>/<env>/<RUN_ID>/`, rebuilds the case lists (`cases/`), writes the run's snapshot of the charts
   (`snapshots/<division>/<env>/<RUN_ID>/`: the published runs that finished by then, every environment) and rewrites
   the table of runs in the READMEs' "results" section (Japanese `README.md`, English `README.en.md`, Chinese
   `README.zh.md`; rewritten from `published/` every time, newest first). Each row links the snapshot on GitHub Pages,
   the case lists on GitHub at the run's tag, and the run's folder in `published/`. The line is kept in `NOTE.md`, and its English and Chinese, given with `--note-en` and
   `--note-zh`, in `NOTE.en.md` and `NOTE.zh.md` (the Japanese one is used where they are missing). After editing them
   later, `--readme` rebuilds only the tables. For a re-run, say in the line what was fixed and measured again.
   - `raw/` (SSE and the full thinking text) and the machine snapshots (`stats/snapshots.jsonl.gz`, with every
     process's command line) are not moved; they stay in `results/`.
   - In the files moved, the home folder is written as `~` and the host name as `<host>` (engine.log, launch.txt,
     machine.json and others; `--scrub` does the same to all of `published/`).
   - `configs/tuned/<family>-<model>.json` is rebuilt from the Tier 5 tune results (the presets the tuner saved;
     `scripts/tuned_configs.py`).
   - A RUN_ID whose queue did not finish is refused (`--force` to make final a RUN_ID stopped on purpose). `test-`
     RUN_IDs cannot be made final.
   - `--snapshots` writes the snapshot of any published run that has none (the snapshots of runs published before
     snapshots existed were made this way on 2026-11-05, with the scripts of that day). A snapshot is never rewritten;
     to change one, delete it and run `--snapshots` (ask first: it changes a published page).
4. Commit `published/`, `cases/`, `snapshots/`, `README*.md`, `index.html`, `configs/tuned/`, `plan/` and the scripts
   changed. Then tag that commit with the run's tag, `git tag -a run/<division>/<env>/<RUN_ID> -m <RUN_ID>`: the
   README and the snapshot link the case lists (and `models.json`, the divisions) at that tag, so they show the files
   as they were when the run was published. Push only after the user has agreed (section 3), with
   `git push --follow-tags` (an annotated tag goes with it; without the tag those links are broken).
5. GitHub Pages serves the repository's default branch from its root (Settings → Pages → Deploy from a branch,
   `master`, `/ (root)`; `.nojekyll` keeps files as they are). Its root `index.html` (written by `publish.py`) sends
   readers to the repository's README. Pages is free only for a public repository.

## 3. Ask first

Even if one of these becomes necessary during a run, do not do it yourself: follow the policy decided in 2.2. With no
policy, report the cause and a proposal, and stop.
- Deleting models or results (except the converted QAD source, which `scripts/overnight.py` deletes)
- Stopping a Strata engine other than the measuring one, or changing Strata's saved settings or presets
- Changing the case plan
- Publishing, such as `git push`
- Changing system settings (linger, power, the GPU power limit and so on)

## 4. Files and where they are

| What | Where |
| --- | --- |
| The models | `~/.local/share/strata/Strata-data/models` (`downloads/manifest.json` lists them with SHA-256) |
| Fetching state | `downloads/` (not in Git); `READY` marks that every model is on disk |
| Fixed prompts | `prompts/` (SHA-256 in `MANIFEST.json`); the long document's source is `prompts/long-corpus.txt` and `long-sources.json` |
| Divisions | `divisions/<division>/division.json` (only a division whose `status` is `active` can be measured; see [divisions/README.md](divisions/README.md)) |
| Environments | `envs/<env>/env.json` (written by hand; fields in [envs/README.md](envs/README.md); matching and templates in `scripts/envs.py`) |
| The plan | `plan/<division>/<env>/cases.jsonl` and `cases.csv` (written per environment by `scripts/build_cases.py`; the runner reads them) |
| Case lists | `cases/README*.md` (the environments) → `cases/<division>/<env>/README*.md` (the Tiers, models and shared conditions) → `tier-<Tier>*.md` (every case, with its result and a link to its record) and `tier-<Tier>.csv` (every parameter; a CSV per Tier because GitHub shows a CSV as a table only up to 512 KB); committed, from `published/` alone |
| Charts | `snapshots/<division>/<env>/<RUN_ID>/index.html` (every environment, switched and compared, as of that run) and `summary.csv` (every case of every environment, with an `env` column); committed, served by GitHub Pages |
| Pages to check | `preview/` (cases/, RESULTS.html, summary.csv, built with `results/` too; not in Git) |
| Results (working) | `results/<division>/<env>/<RUN_ID>/cases/<case id>/` (summary.json, requests.jsonl, responses/, artifact/, raw/); all of `results/` is outside Git |
| Results (final, published) | `published/<division>/<env>/<RUN_ID>/` (moved by `scripts/publish.py`; no raw/ and no machine snapshots) |
| Session records | `results/<division>/<env>/<RUN_ID>/sessions/<session>/start-N/` (launch output, /settings, /config, /props, telemetry.csv, engine.log) |
| Queue records | `results/<division>/<env>/<RUN_ID>/queue.log` and `queue.pid`; the runner's record is `runner.log` there |
| Run status | `run-status/` (not in Git) |
| The machine | `results/<division>/<env>/<RUN_ID>/machine.json` (written first by the runner; `env` is the "Test system" box at the top of the case lists and the charts, `env_id` the environment; made by `scripts/machine_info.py`; RAM type, speed and modules need root, so they are read from env.json's `memory`) |
| Internal notes | `docs/` (the plan's background and research notes; not in Git, not published) |
| The records checked against each other | `results/<division>/<env>/<RUN_ID>/verify.json` (`scripts/verify_run.py`, run last by the queue: the engine's timings against the client's SSE timing, whether the launch choices reached the engine's arguments, the presets the tuner saved) |
| Model versions | `results/<division>/<env>/<RUN_ID>/models.json` (written by the runner at each start, `scripts/model_files.py`: per model the repository and commit, per file the SHA-256 and whether the file on disk carries it; published). A model keeps its name across its publisher's updates, so this says which version a run measured; the case list marks a model measured in two versions within one environment |
| Tune results | each tune session's `tune-presets.json` (saved by the runner) → `configs/tuned/<family>-<model>.json` (`scripts/tuned_configs.py`; published) |
| Machine snapshots | `results/<division>/<env>/<RUN_ID>/stats/snapshots.jsonl.gz` (JSONL with `zcat`; every process's command line, so not in Git and not published) |
| Temperature and power over time | `results/<division>/<env>/<RUN_ID>/stats/thermal.csv` (every 5 s: CPU/GPU temperature, power, clocks, throttling share and the case running; the CPU's own power needs root and is not read) |

## 5. Notes on Strata

- The GPU power limit is env.json's `gpu_power_limit_w` per environment (500 W for `rtx5090-128g`; the card's default is
  575 W). `nvidia-smi -pl` is lost at every boot with this driver setting, so `scripts/system/gpu-power-limit.service`
  (a system unit the user installs; fixed at 500 W) sets it again at boot and after sleep. After a card change, see
  step 3 of 2.0.
- The measuring engine runs on a dedicated port (18600), started by `strata launch ... --no-tui --restart`. Strata
  creates a profile `launch-<model>-<context>` (shared with the app).
- `strata launch --stop` stops only what the CLI started; the desktop app's engine keeps running.
- The drafter is fixed with `--drafting mtp --mtp on` (the runner adds it). Since 0.2.10, Auto picks DFlash2 for qwen,
  gyro and unsloth and MTP for coder, swift and nvfp4, so without fixing it the drafter would differ between models.
  DFlash2 is measured again as its own launches for Tier 1 decode on the models that have it (qwen, gyro, unsloth), and no drafter in
  Tier 5. DFlash2 cases are made only in environments whose env.json lists `dflash2` in `drafters` (DFlash2 needs a
  CUDA 8.6 / 8.9 / 12.x GPU; a 7.5 card such as the RTX 2070 has none). Fetch the DFlash2 drafter (1.2 GB) with
  `strata drafting fetch` beforehand (preflight checks it).
- If setup runs during a launch with `--mtp off` or `--drafting off`, the model's
  `~/.local/share/strata/install/strata-<tag>.json` keeps `"mtp": false` and `--mtp <data>/mtp/rt` disappears from the
  arguments; after that, neither launch's `--drafting mtp` nor `--mtp on` brings MTP back (qwen IQ3_S in
  2026-11-03-main). Control's setup.py with `--mtp on` restores it (in
  `~/.local/share/strata/components/control/<version>/`,
  `setup.py --yes --no-start --family F --model M --context 131072 --vision no --mtp on`, with the same environment
  variables launch uses when it calls setup; it changes Strata's saved settings, so section 3 applies). Preflight is NG
  while any model keeps `"mtp": false`, and when a launch that should have MTP has no `strata mtp: draft layer loaded`
  in engine.log, the runner fails that session's cases with `MTP not loaded`.
- An unknown name in `--set` only gives a warning. The runner checks that the launch choices (`--context`, `--kv`,
  `--parallel`, `--pool-cores`, `--vision gpu`, the `--set` values, `--drafting off`) are on the engine's command line
  (`engine started` in engine.log), and fails the cases with `setting not applied` if not.
- Tier 5's `--tune quick / thorough` saves its result as a Strata preset, active for its choices (vision on and others,
  which overlap the desktop app's). It does not affect the measuring launches (vision off) but can affect the app. The
  runner keeps the presets made in `tune-presets.json`.
- State thinking and sampling in every request; left out, they are filled from the shared Chat settings or the config
  (docs/SCOUTING.md section 2).
- With thinking on and no `reasoning_budget_tokens`, answer_room fills in 3/4 of the cap. The runner states the same
  value (half the cap for the game task).
- The NVFP4-QAD conversion tools expect llama.cpp at `<root>/third_party/llama.cpp`, which neither Strata's source nor
  the app has, and need torch and transformers, which the app does not ship (its own setup refuses this model for that
  reason). `scripts/setup_acquire.py` makes `.venv-qad` (Strata's `requirements.txt` and `requirements-nvfp4-local.txt`)
  and `work/qad-root/` (a copy of the source's tools with a link to the install's llama.cpp), and `scripts/overnight.py`
  runs the conversion from there. `scripts/start_pipeline.sh` runs it while `downloads/READY` is missing.
- Q2_0's first launch builds a pack for AVX-512 (about 40 GB). The first launch's time is not part of the measurements.
