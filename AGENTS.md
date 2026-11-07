# AGENTS.md — for agents working on strata-jbench

A repository for measuring several models with Strata (a local LLM inference engine) and publishing the results so
that anyone can run them again.
The plan is [docs/SCOUTING.md](docs/SCOUTING.md) (internal notes, not in Git); every case per environment is in the
case lists, [cases/](cases/README.md) (Markdown and CSV read on GitHub, built by `scripts/build_cases.py`, which also
writes `plan/<division>/<env>/cases.jsonl`, not in Git), and the charts are one page per published run under `snapshots/`, served
by GitHub Pages (`scripts/build_results.py`).

This document sets the procedure for long-running work such as fetching models and running the benchmark.

**Environment:** the hardware set-up the benchmark runs on (a GPU and an amount of RAM; swapping the card or adding
RAM makes another environment). `envs/<env>/env.json` is one environment; its plan is in `plan/<division>/<env>/`, its
results in `results/<division>/<env>/<RUN_ID>/`, its case list in `cases/<division>/<env>/`.
The environment is never typed by hand: `scripts/envs.py` picks the env.json that matches the hardware found now (GPU
name and RAM). With no matching environment, or with one named that does not match, preflight and the runner do not
start measuring. Fields and how to write one: [envs/README.md](envs/README.md).
`envs/<env>/` and `plan/` are not in Git: each PC writes its own env.json (its models and power limits are the
measurer's choices) and builds its plan from it. The runner keeps the env.json it measured with in the run's folder
(`env.json`, written at each start), which is published with the run; the committed pages read the environment from
the newest published run's copy. An env.json lost on a PC can be taken back from there.

**Division:** how the models are driven. It is independent of the environment; `divisions/<division>/division.json` is
one division ([divisions/README.md](divisions/README.md)), picked with bench.json's `division` (`plain` by default). `plain`
has no harness: the runner calls the engine's API directly (Tiers 0–5). The harness divisions (`dsh`, `strata`,
`opencode`, `hermes`, `pi`) hand one case, the Minecraft coding task, to an agent harness in one shot (step `G`): the runner
starts the harness inside bubblewrap in a fresh work folder, with the recording proxy (`scripts/agent_proxy.py`, port
18601) between it and the engine, which puts the case's sampling, thinking, seed and cap into every request. The
harness's pinned version, its models and its status are in its division.json; only a division whose `status` is
`active` can be measured (all five: each harness installed at its pinned version and its adapter in
`scripts/harnesses.py` run against the mock engine). `strata` drives the Strata desktop app's own agent code
(`scripts/strata_agent.mjs` on the extracted app in `tools/harness/strata/<version>/`). Plans, results and case lists are kept in a folder per division, and each
division has its own pages (`preview/RESULTS-<division>.html`, `snapshots/<division>/...`).

**Settings:** what a run measures and how it is run is `bench.json` at the repository's root (not in Git): the
RUN_ID, the division, the Tiers, models and cases chosen, whether to fetch what is missing, the watch's interval and
restarts. It holds only what differs from the defaults; every key, its default and what it does are in
`scripts/config.py`, listed by `python3 -I scripts/bench.py config`. The run keeps the settings it started with in its
folder (`bench.json`, the defaults filled in; `bench-starts.jsonl`, one line per start), published with it. What makes
results comparable is not a setting: the cases are the plan (`scripts/build_cases.py`), and the hardware and the
measurer's choices per environment are its env.json.

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
   `python3 -I scripts/bench.py start` starts the run's supervisor (`scripts/supervise.py`) detached from the terminal
   and the agent's session (no systemd unit). The agent only starts, checks and recovers it, and does not wait for it to
   finish (no `sleep` loops or "wake me when it is done" waits over long-running work).
2. **Ask every question that needs a decision before starting.** Never leave a run waiting for a decision halfway.
3. **Preflight before starting.** The later a stage would fail, the more it deserves a cheap real run first
   (`scripts/preflight.py`). If anything is NG, start nothing.
4. **A stage that ended without results is FAILED.** Never treat it as "they will turn up if we wait". Whoever waits
   checks the other side's PID and result files.
5. **Check or stop our own scripts by their recorded PID** (`kill -0`; the run's `queue.pid` and `supervisor.json`),
   or with `scripts/bench.py status` / `stop`. Do not use `pgrep -f` / `pkill -f`: the string also matches other shells
   that mention the script's name (the agent's own shell included).
6. **Watch in two layers.** The supervisor watches the run itself: every `watch_interval_s` it runs the healthcheck
   (`run-status/STATUS.md`, `ALERTS.log`, a desktop notification on a new problem), starts again a runner that crashed
   or hung (up to `crash_restarts` / `stuck_restarts` times), and notifies when the run ends. What it cannot cover is
   its own end: a reboot, a logout without linger, a kill. For that, an agent that runs the benchmark registers a
   scheduled task with its own scheduler in the conversation that started the run (hourly: check, find the cause,
   recover safely, report the end; 2.3), which reports in that conversation, the end of the run included. The task exists only
   while a run does: registered when it starts and deleted when it ends, each time with the user's agreement (2.3,
   2.6). Without an agent the supervisor alone runs it, and after a reboot `bench.py start` resumes it.
7. **Keep progress in files,** not in the conversation's memory: the state in `run-status/STATUS.md`, problems in
   `run-status/ALERTS.log`, each stage's logs as in section 4.
8. **Nothing else heavy during a measurement.** No downloads, conversions or another inference engine at the same time.

## 2. Procedures

### 2.0 When the hardware changes (another card, more RAM, another PC)
On a PC that has not run the benchmark yet, first: Strata (the desktop app) installed with one model installed through
it once (that writes `~/.local/share/strata/install/third_party/llama.cpp`), and Strata's source checked out at
`~/Strata` (its `setup.py` pins every file fetched). `scripts/setup_acquire.py` then makes the rest (the venvs, the
download list, the NVFP4-QAD converter); `scripts/bench.py start` runs it by itself. After the models are on disk,
the NVFP4 ready-made packs need Strata's setup once with `--no-start` to write their run configs (otherwise
`strata launch --plan` reports them as needing a download); it changes Strata's saved settings, so section 3 applies.

1. `python3 -I scripts/envs.py list` shows whether an environment matches the hardware now (marked `*`).
2. If none does, `python3 -I scripts/envs.py new <env>` writes `envs/<env>/env.json` (ids like `rtx5070-64g`: GPU and
   RAM). On a PC with two cards each card is an environment of its own: `--gpu N` picks the card (`gpu_index`; the
   runner launches with `--gpu N` and reads that card alone). When two environments match the PC, name one with
   bench.json's `env`. It fills in the GPU name, VRAM, RAM and whether DFlash2 is available (checked with `strata launch --plan`).
   Then fill in by hand:
   - `memory`: the output of `sudo dmidecode -t memory` (type, speed, modules; it needs root, so ask the user to run it)
   - `gpu_power_limit_w`: the power limit, if one is set for measuring; `null` to measure at the card's default
   - `cpu_power_limit_w`: the CPU's PL1 / PL2 (`{"pl1": 65, "pl2": 65}`), if set for measuring (in the BIOS; a
     system setting, so the user does it); `null` to measure at the board's setting. Preflight compares it with Intel
     RAPL (the lower of the MSR and MCHBAR copies, which the CPU holds to; a BIOS may write only one), and machine.json
     records the limits in force either way
   - `ref`: the reference model (Tier 0, Tier 4d, the base of the representatives of Tiers 4b, 4c and 5, the harness
     divisions' `"ref"`). `new` writes the model Strata itself recommends for that RAM + VRAM (`MEMORY_TIERS` in the
     source's `setup.py`). Strata's recommendation is the only grounds jbench uses: to try another model as the
     reference, change `ref` (when `models` leaves the recommended one out, Tiers 0 and 4d stay out of the plan until
     `ref` names a measured model). The representatives are chosen from the environment's models by role (the reference,
     the largest, the smallest, the largest of each family: file sizes only), not by name (`scripts/build_cases.py`
     `representatives`)
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

### 2.0a When a model or a harness is missing
`python3 -I scripts/acquire.py check` lists what the run needs on disk (the models of the plan, the DFlash2 drafter, a
harness division's pinned harness, bubblewrap) and whether each is there; it changes nothing (and writes
`run-status/acquire.json`); it looks at the cases bench.json chooses. `scripts/bench.py start` runs it first and
starts nothing while something is missing, unless bench.json has `"fetch": true`. For each missing piece, the user chooses before anything is fetched:
1. **jbench fetches it**: `python3 -I scripts/acquire.py fetch <item>` (`models`, `dflash2`, `harness:<division>`, or
   `--all`), which shows the size and the source and asks first. Models are the files Strata's setup.py pins (hf CLI, as
   `scripts/overnight.py` detached; hours, not waited for); a harness is its pinned version installed into
   `tools/harness/<division>/<version>/` (npm, a venv, or the Strata app's AppImage checked and extracted), never into
   the user's global packages.
2. **The user puts it in place**: what needs root (bubblewrap), Strata itself, or model files the user already has
   elsewhere (copied into Strata's models folder by the user). Then run `check` again.
3. **Leave it out**: remove the model from env.json `models` (or from the division's `models`), or do not measure that
   division. It changes the plan: 2.1.

Nothing is downloaded without that choice: without `"fetch": true`, `bench.py start` runs `setup_acquire.py
--no-fetch` (a missing venv is an error instead of a PyPI install) and fetches nothing, and a run whose own models are
all on disk starts even while other models of env.json are not (the supervisor waits on `acquire.py check`, not on
`downloads/READY`). With `"fetch": true` the supervisor starts `scripts/overnight.py` and measures only once every
download has ended (1.8).
A harness already in its own default place at another version is neither used nor touched (updating or removing it is
the user's call); the pinned version goes into `tools/harness/` beside it. Nothing is fetched while a measurement runs
(1.8): `acquire.py fetch` refuses while the queue of the run started last is alive.

### 2.1 When the plan changes
1. Edit `scripts/build_cases.py` (the only place cases are defined; differences between environments go in env.json).
2. Run `python3 -I scripts/build_cases.py` and check the number of cases and the estimated hours per environment.
   `preview/cases/` and `plan/<division>/<env>/cases.jsonl` are updated (`--published` for the committed `cases/`).
   The case lists have a Markdown file per language (`README.md`, `README.en.md`, `README.zh.md`, `tier-<Tier>.md`
   and so on) and the charts switch between Japanese, English and Chinese. When a case definition gains a Japanese
   string, add its English and Chinese to `TR` in `scripts/i18n.py` (strings without a translation are listed when the
   script runs, and shown in Japanese).
3. If a new fixture is needed, change `scripts/build_fixtures.py` and run it with the Python that ships with Strata (see
   the docstring at the top of the file; `--only <fixture>` rewrites one chat fixture without counting the long ones again).
   The coding cases: plain's Tiers 0 and 3 ask for Shuri Castle in 3D voxel art as one HTML file (`coding-shuri`); the
   Minecraft prompt (`game-minecraft`) is the harness divisions' case.
   The long document of Tiers 4b–4d comes from ten works of Aozora Bunko and Project Gutenberg (five Japanese, five
   English), cleaned by `scripts/long_corpus.py` into `prompts/long-corpus.txt`, Japanese and English chunks in turns.
   Sources, editions, SHA-256 and Aozora's colophons are in `prompts/long-sources.json`; the downloads are in
   `work/corpus/raw/` (not in Git). A long fixture holds only the number of corpus lines, the made-up facts placed at
   10 / 50 / 90% ("the passwords of the east, central and west storehouses") and the questions; the runner assembles
   the document.
4. Update the matching part of [docs/SCOUTING.md](docs/SCOUTING.md) too.
5. No backward compatibility: the case lists and the charts show the plan as it is now. A case taken out of the plan,
   or replaced by another (Minecraft by Shuri Castle in plain), leaves them, with the results earlier runs have for it;
   those results stay readable in each run's own snapshot (`snapshots/<division>/<env>/<RUN_ID>/`, never rewritten)
   and in `published/`. Do not keep old cases on the pages as "retired" ones, and do not write how a case used to be
   in the lists or the pages (the history goes in docs/SCOUTING.md and the commit message).

### 2.2 Settings and checks before starting (do not start until these pass)
1. **Go through the settings with the user.** Run `python3 -I scripts/bench.py config` and show the user every
   parameter: its name, the value in force, the default and what it does (in the user's language). Ask whether any
   value should change, and in particular:
   - `run_id`: a new RUN_ID, or an existing one to resume (`test-` for a check).
   - `division`, `tiers`, `models`, `cases`: what to measure. Not every Tier has to run: `python3 -I scripts/bench.py
     plan` shows the cases chosen and the estimated hours per Tier (and says when Tier 0 has never run in this
     environment). Show the plan to the user before starting.
   - `fetch`: only `true` when the user agreed to jbench fetching what `python3 -I scripts/acquire.py check` reports
     missing (2.0a).
   - The watch (`watch_interval_s`, `crash_restarts`, `stuck_restarts`, `notify`) and `smoke`, `stats`.
   Write the values agreed into `bench.json` (only the keys that differ from the default), then run `bench.py config`
   again and show the result. A user who edits `bench.json` by hand needs none of this: check it with `config`.
2. Ask the user and get an answer for each of these:
   - Which environment to measure in (is the result of `python3 -I scripts/envs.py detect` the set-up the user meant?).
   - Whether a Strata engine other than the measuring one (the desktop app, say) is using the GPU (`nvidia-smi`,
     `pgrep -af "strata --serve"`), and if so, whether it may be stopped.
   - Whether it runs across a logout or a reboot. The supervisor survives the terminal and the agent's session being
     closed, but while linger is off the user's last logout ends it (`loginctl enable-linger`, a system setting: the
     user does it), and a reboot always does (`bench.py start` again resumes; the watch task of 2.3 does it).
   - Whether anything in section 3 ("Ask first") may become necessary during the run; if so, have the user decide
     beforehand what to do. Strata's run configs for models just fetched (`scripts/install_configs.py`, run by the
     supervisor) change Strata's saved settings.
   - For a harness division: that the model will run shell commands and write files inside the sandboxed work folder
     (the network is not cut off: a harness reaches the proxy over it).
   - That the hourly watch task will be registered at the start (step 3 of 2.3: which scheduler, where it reports,
     what it does not survive) and deleted at the end (2.6).
3. After changing the runner or a fixture, run the affected cases under a RUN_ID starting with `test-` (`test-` results
   appear neither in the case lists nor in the charts): either with `bench.py start` and `"cases": [...]`, or directly
   `python3 scripts/bench_runner.py --run-id test-xxx --steps 1 --ids <case id>,...` (a harness division: with
   `BENCH_DIVISION=<division>` and `--steps G`).
4. Preflight: the supervisor runs it before measuring (with one real launch unless `"smoke": false`) and starts nothing
   if it fails. To see it first: `python3 scripts/preflight.py --phase all --steps "<the Tiers, comma separated>"`
   (`--phase acquire` before every model is on disk); the result is `run-status/preflight.json`. It also checks the
   environment (which env.json this hardware is, that the plan is newer than env.json, that the power limit is
   env.json's) and, for a harness division, the pinned harness run once against the mock engine
   (`scripts/mock_engine.py`) through the proxy, in the sandbox (no GPU).

### 2.3 Starting
1. Start it: `python3 -I scripts/bench.py start`. The first line printed is
   `division: <division>, environment: <env>, run: results/<division>/<env>/<RUN_ID>`. It refuses with no `run_id`,
   no matching environment, a division that is not active, nothing chosen, another run's supervisor alive, or something
   missing (without `fetch`). Starting the same `run_id` again resumes the run (finished cases are skipped); while its
   supervisor is alive it only shows the status. What was started is kept in `run-status/current-run.json`, so
   `status` and `stop` need no arguments. The supervisor (`scripts/supervise.py`), in order:
   - with `fetch`: `scripts/overnight.py` (fetch the models → convert NVFP4-QAD → delete the conversion source → fetch
     the last model) when models are missing, and waits until every download has ended
   - Strata's run configs for the models fetched (`scripts/install_configs.py`), then preflight
   - `scripts/stats_watch.py` beside the run (at each session start, launch, case end, failure and Tier change, and
     every 5 minutes, a snapshot of the process list, CPU, memory, PSI, disk IO, temperatures and GPU)
   - `scripts/bench_runner.py` Tier by Tier in the order of `tiers`, for the models and cases chosen, with the case
     lists and charts rebuilt after each Tier (`preview/`), then `scripts/verify_run.py`
   - the healthcheck every `watch_interval_s`; the restarts of 1.6; a notification at the end
2. Check that the STATUS printed right after starting is RUNNING or WAITING.
3. With the user's agreement from 2.2, register the hourly watch task with the agent's own scheduler, named or
   described as `strata-jbench-watch`. What matters is where it reports: **in the conversation that started the run,
   where the user talks with the agent**, as the agent would if the user asked. A scheduler whose runs each open a
   conversation of their own (a background session, a separate thread) leaves its reports where the user does not
   look, and a notification alone is easy to miss; neither counts as reporting. Before starting (2.2), tell the user
   which scheduler will be used, where its reports will appear and what it does not survive (a scheduler living in
   the conversation is usually gone when the agent's app quits or the PC reboots: after a reboot the user comes back
   to that conversation, and the agent resumes with `bench.py start` and registers the task again). If the agent has
   no scheduler that reports in the conversation, say so and agree with the user on another way (they ask in the
   conversation from time to time; the supervisor's desktop notification at the end).
   - **Claude Code** (CLI and desktop app): CronCreate in the session that started the run (the same as `/loop`; the
     prompt comes back into that session every hour while it is idle). Recurring jobs live only in that session's
     memory and expire after 7 days; CronList shows them and CronDelete removes them (2.6). Not the desktop app's
     "Scheduled" tasks: each of their runs is a session of its own, so the report stays there (the end of a
     run on 2026-11-07 was reported only in one of those).
   - **Other agents** (Codex, Cursor, Gemini CLI and so on): use their in-conversation scheduler if they have one, and
     check before starting where its runs report; a scheduled or background task that runs as a separate thread or
     job is the same case as Claude Code's "Scheduled" tasks.
   Its prompt must be self-contained, for example:
   > In <repository path>, run `python3 -I scripts/bench.py status --json`. RUNNING or WAITING: report nothing
   > unless `warn` is set. DONE: report the end (the run, the cases done and failed, `run-status/STATUS.md`) and ask
   > the user to delete this task. STOPPED: say so and ask whether to resume or delete this task. FAILED or STUCK, or
   > `supervisor_pid` null while not DONE or STOPPED: follow AGENTS.md 2.4 (read the logs, find the cause; after a
   > reboot or a passing problem, `python3 -I scripts/bench.py start` resumes it), never act on section 3 without the
   > user's policy, and report what was found and done. This task never deletes itself.
   If one is left over from an earlier run, check that it is enabled and that its prompt is still right. If it cannot
   be registered, do not report the run as started: tell the user why and have them decide on another way (the
   supervisor alone, without recovery after a reboot).
4. Report the expected end time (`bench.py plan`) and what happens if something goes wrong (the supervisor's restarts
   and notifications, recovery by the watch task).

To stop: `python3 -I scripts/bench.py stop` (the supervisor, its children and the engine it launched). If the run will
not be resumed, delete the watch task as in 2.6.

### 2.4 When something goes wrong (healthcheck FAILED / STUCK)
Read the logs and find the cause before acting. Never restart again and again without knowing why.

| Stage | Look at | Safe recovery |
| --- | --- | --- |
| acquire/download* | `downloads/overnight.log`, `downloads/overnight.out`, the end of `downloads/download.log`, `downloads/status.json` | For a passing network problem, `scripts/bench.py start` resumes (it goes on from where it stopped) |
| acquire/qad | `downloads/qad-prepare.log` | Fix the cause, then resume; finished steps are skipped by their `.done` marks |
| bench | `results/<division>/<env>/<RUN_ID>/queue.log` (the supervisor's lines, with its restarts, and the runner's output), its `runner.log`, the matching `sessions/*/start-*/launch.txt` and `engine.log` | Fix the cause, then `scripts/bench.py start`; finished cases are skipped |
| supervisor gone (status FAILED, `supervisor_pid` null) | the end of `queue.log`, `supervise.err` in the run, `journalctl --user -b` for an OOM kill; a reboot or a logout | `scripts/bench.py start` resumes it |
| bench preflight | `run-status/preflight.json` | Fix the failing items |

After fixing a code or environment problem, run one affected case under a `test-` RUN_ID before resuming.

### 2.5 Checking the results
1. Read `run-status/STATUS.md` and `run-status/ALERTS.log` (STATUS.md's first line gives the environment and RUN_ID).
2. `python3 -I scripts/build_cases.py` puts the results into the case list (`preview/cases/<division>/<env>/`), and
   `python3 -I scripts/build_results.py` into the charts, `preview/RESULTS.html`, and `preview/summary.csv` (every
   environment, with an `env` column); the supervisor runs both after each Tier. `preview/` reads both `results/` and
   `published/` and is for checking; it says "Preview" at the top.
   The page has one tab per Tier (an overview with the summary table first), each opening with what the Tier asks,
   its conditions, what its numbers are and how to read them; only the tab shown is drawn (`#tab-<id>` opens one, and
   a section's `#s-…` opens the tab holding it). The charts switch environments with the buttons at the top, and with
   results in two or more environments, "Across environments" appears in the overview (`?env=<env>` opens a given
   environment).
   When the same case is in several RUN_IDs of one environment, both use the RUN_ID whose name sorts last. To
   measure again under changed conditions, delete the old RUN_ID's results or use a RUN_ID that sorts later (`test-`
   RUN_IDs are never shown). Another environment is another case.

### 2.6 When the run ends
The watch task keeps firing every hour after the queue ends, so remove it as soon as the run is over.
1. The run is over when STATUS is DONE, or when it is FAILED or STOPPED and the user has decided not to resume it.
   A FAILED run that will be resumed after a fix is not over: keep the task.
2. Ask the user whether the watch task (`strata-jbench-watch`) may be deleted, and delete it only after they agree
   (with the scheduler it was registered with, in the conversation that registered it; Claude Code: CronDelete). If
   the agent cannot delete it, ask the user to.
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
4. Commit `published/`, `cases/`, `snapshots/`, `README*.md`, `index.html`, `configs/tuned/` and the scripts
   changed (not `envs/<env>/` or `plan/`: the run's own `env.json` goes with it in `published/`). Then tag that commit with the run's tag, `git tag -a run/<division>/<env>/<RUN_ID> -m <RUN_ID>`: the
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
- Downloading or installing anything: models, the drafter, a harness (`"fetch": true`, `scripts/acquire.py fetch`)
- Stopping a Strata engine other than the measuring one, or changing Strata's saved settings or presets
- Changing the case plan
- Publishing, such as `git push`
- Changing system settings (linger, power, the GPU power limit and so on)

## 4. Files and where they are

| What | Where |
| --- | --- |
| The models | `~/.local/share/strata/Strata-data/models` (`downloads/manifest.json` lists them with SHA-256) |
| Fetching state | `downloads/` (not in Git); `READY` marks that every model of env.json is on disk (a run needs only its own: `scripts/acquire.py check`) |
| Fixed prompts | `prompts/` (SHA-256 in `MANIFEST.json`); the long document's source is `prompts/long-corpus.txt` and `long-sources.json` |
| What a run needs on disk | `run-status/acquire.json` (`scripts/acquire.py check`) |
| Harnesses | the pinned version per division in `divisions/<division>/division.json` "pin"; installed by jbench in `tools/harness/<division>/<version>/` (not in Git), or found at the pinned version in its default place; adapters in `scripts/harnesses.py`; the one a run drove in the run's `harness.json` |
| A harness case's record | `cases/<case id>/harness/seed-N/` (the harness's events and stderr, its config, the command, `proxy.jsonl`: one line per request with what the harness sent and what was forwarded); the work folder, the harness's folder and the request bodies stay in `raw/` |
| Divisions | `divisions/<division>/division.json` (only a division whose `status` is `active` can be measured; see [divisions/README.md](divisions/README.md)) |
| Environments | `envs/<env>/env.json` (written by hand on each PC, not in Git; fields in [envs/README.md](envs/README.md); matching and templates in `scripts/envs.py`); the copy a run measured with is `results/` or `published/<division>/<env>/<RUN_ID>/env.json` |
| The plan | `plan/<division>/<env>/cases.jsonl` and `cases.csv` (written per environment by `scripts/build_cases.py`, also by the queue before preflight; the runner reads them; not in Git, and each case's definition is kept in its `summary.json`) |
| Case lists | `cases/README*.md` (the environments) → `cases/<division>/<env>/README*.md` (the Tiers, models and shared conditions) → `tier-<Tier>*.md` (every case, with its result and a link to its record) and `tier-<Tier>.csv` (every parameter; a CSV per Tier because GitHub shows a CSV as a table only up to 512 KB); committed, from `published/` alone |
| Charts | `snapshots/<division>/<env>/<RUN_ID>/index.html` (every environment, switched and compared, as of that run) and `summary.csv` (every case of every environment, with an `env` column); committed, served by GitHub Pages |
| Pages to check | `preview/` (cases/, RESULTS.html, summary.csv, built with `results/` too; another division's: RESULTS-<division>.html, summary-<division>.csv; not in Git) |
| Results (working) | `results/<division>/<env>/<RUN_ID>/cases/<case id>/` (summary.json, requests.jsonl, responses/, artifact/, raw/); all of `results/` is outside Git |
| Results (final, published) | `published/<division>/<env>/<RUN_ID>/` (moved by `scripts/publish.py`; no raw/ and no machine snapshots) |
| Session records | `results/<division>/<env>/<RUN_ID>/sessions/<session>/start-N/` (launch output, /settings, /config, /props, telemetry.csv, engine.log) |
| Settings | `bench.json` (this PC's, not in Git; keys and defaults in `scripts/config.py`); the run's own copy `results/` or `published/<division>/<env>/<RUN_ID>/bench.json` and `bench-starts.jsonl` |
| Supervisor records | `results/<division>/<env>/<RUN_ID>/queue.log`, `queue.pid` (the supervisor's PID), `supervisor.json` (its children's process groups) and `supervise.err`; the runner's record is `runner.log` there |
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
- What is measured is the engine and Control (`~/.local/share/strata/components/`, `strata update`; the version is in
  each session's `launch.txt` and engine.log), driven by the `strata` CLI. The desktop app's own version does not
  matter to a run: the `strata` division uses the AppImage its division.json pins, extracted into `tools/harness/`, not
  an installed app. The app matters only where it shares something: its engine on the GPU (2.2), the profiles and
  presets the CLI shares with it, and the first model installed through it on a new PC (2.0).
- When Strata has a new release: `strata update --check`, then `strata update` (engine and Control; the previous
  engine stays for `strata components rollback`); `~/Strata` to the release's tag (`git pull --ff-only` when main is
  at it), then `scripts/setup_acquire.py --no-fetch`; the `strata` division's pin (version, URL, SHA-256 from the
  release's asset list) and `acquire.py fetch harness:strata`; `acquire.py check` for the drafter and the models (a
  release that changes setup.py's pins changes the files); `scripts/install_configs.py --dry-run` for the run configs;
  `strata launch --plan` per model for Auto's drafter; then preflight and a `test-` run (2.2). Downloads and the run
  configs are section 3: agree on them first.
- The drafter is fixed with `--drafting mtp --mtp on` (the runner adds it). Since 0.2.10, Auto picks DFlash2 for qwen,
  gyro and unsloth and MTP for coder, swift and nvfp4, so without fixing it the drafter would differ between models.
  DFlash2 is measured again as its own launches for Tier 1 decode on the models that have it (qwen, gyro, unsloth), and no drafter in
  Tier 5. DFlash2 cases are made only in environments whose env.json lists `dflash2` in `drafters` (DFlash2 needs a
  CUDA 8.6 / 8.9 / 12.x GPU; a 7.5 card such as the RTX 2070 has none). The drafter depends on the model: the stock
  pack (1.2 GB), and since 0.2.12 Strata's tuned pack (0.34 GB) beside it for the models its table names (on CUDA,
  IQ3_S and UD-IQ4_XS-v31), so `scripts/acquire.py` checks it per model with `strata drafting plan --config <run config>
  --mode dflash2` and `acquire.py fetch dflash2` fetches it the same way (preflight checks it too). The split between
  the families was the same on 0.2.12 (`strata launch --plan` on the RTX 5090).
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
  value (half the cap for the coding task).
- The NVFP4-QAD conversion tools expect llama.cpp at `<root>/third_party/llama.cpp`, which neither Strata's source nor
  the app has, and need torch and transformers, which the app does not ship (its own setup refuses this model for that
  reason). `scripts/setup_acquire.py` makes `.venv-qad` (Strata's `requirements.txt` and `requirements-nvfp4-local.txt`)
  and `work/qad-root/` (a copy of the source's tools with a link to the install's llama.cpp), and `scripts/overnight.py`
  runs the conversion from there. `scripts/bench.py start` runs it while `downloads/READY` is missing.
- Q2_0's first launch builds a pack for AVX-512 (about 40 GB). The first launch's time is not part of the measurements.
