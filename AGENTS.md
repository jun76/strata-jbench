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

**Engine:** what is measured. `catalog/engines/<engine>.json` is one engine and names its adapter
(`scripts/engines/<adapter>.py`); bench.json's `engine` picks it (`strata` by default) and a run measures one engine,
recorded in the run's `engine.json`. `strata` is Strata itself (`strata launch`); `sync-strata` is a derived engine
with an adapter of its own (its launcher, a settings folder per run, its own builds Sync-XS / S / M); `endpoint`
attaches to a URL the user started (bench.json `engine_url`, `engine_note`): jbench starts and stops nothing, so
nothing about the launch is checked and the results say "attach only". An engine's entry limits what it is asked
(`steps`, `max_context`), and a build belongs to the engines its catalog entry lists (`catalog/models/`, "engines";
Strata where it says nothing), so the plan's rows carry the engine they are for. bench.json's `track` says how the
engine is set: `exact` (every approximation that changes the output off: Sync-Strata's tail skip at R10), `default`
(the engine as it comes) or `custom`. Only runs on the `exact` track of an engine jbench started itself share the
pages under the same case ids (`envs.comparable`); the others are results of their own. A page shows the results
of the engines ticked at its top (a checkbox each; `?engine=a,b` in a link): Strata alone by default, so a derived
engine's builds appear among Strata's only when it is ticked. The README's table of runs names each run's engine (a
derived engine's link opens with it ticked beside Strata), and the case lists have a table per engine.
What a run uses on this PC and where it came from (the engine, the harness, the models: fetched by jbench into
`tools/`, or a place the user named) is `tools/provision.json` (`scripts/provision.py`), copied into the run.

**Settings:** what a run measures and how it is run is `bench.json` at the repository's root (not in Git): the
RUN_ID, the division, the Tiers, models and cases chosen, whether to fetch what is missing, the watch's interval and
restarts. It holds only what differs from the defaults; every key, its default and what it does are in
`scripts/config.py`, listed by `python3 -I scripts/bench.py config`. The run keeps the settings it started with in its
folder (`bench.json`, the defaults filled in; `bench-starts.jsonl`, one line per start), published with it. What makes
results comparable is not a setting: the cases are the plan (`scripts/case_plan.py`, over the catalog in `catalog/`), and the hardware and the
measurer's choices per environment are its env.json.

**Tasks, presets and the recipe:** the Tiers have names by what they answer: the tasks of `catalog/tasks.json`
(`speed-decode`, `speed-prefill`, `official-standard`, `think-qa`, `code-oneshot`, `context-reserve`, `long-read`,
`yarn-check`, `launch-options`, `selfcheck`, `agent-oneshot`), each tied to its cases, and the presets that bundle them
(`quick`: the two headline speed numbers; `standard`; `full`). bench.json's `preset` and `tasks` choose by them
(`tiers` still does when neither is set). The metrics and the headline numbers (one fixed condition each: JB-decode,
JB-ttft-32k, JB-answer, JB-page, JB-agent) are `catalog/metrics.json`. What a configuration measures is one text, the
recipe (`python3 -I scripts/bench.py recipe`; `--apply FILE` writes a pasted one into bench.json; kept in the run as
`recipe.txt`): its id is a hash of the engine, the track, the division and the tasks with their versions, not of the
models. Every case also carries the hash of its own conditions (`cond`, `case_plan.condition`: the fixture's SHA-256,
the context, the options, thinking, the temperature, the cap, the seeds), and only cases with the same hash are the
same ruler across environments. A task's `version` in `catalog/tasks.json` is raised when what it asks changes.

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
   while a run does: registered when it starts, with the user's agreement (2.3), and deleted by the task itself as
   soon as it finds the run over, whether it succeeded or not (2.6). Without an agent the supervisor alone runs it, and after a reboot `bench.py start` resumes it.
7. **Keep progress in files,** not in the conversation's memory: the state in `run-status/STATUS.md`, problems in
   `run-status/ALERTS.log`, each stage's logs as in section 4.
8. **Nothing else heavy during a measurement.** No downloads, conversions or another inference engine at the same time.

## 2. Procedures

The procedures are the **strata-jbench skill**, in this repository: [.claude/skills/strata-jbench/SKILL.md](.claude/skills/strata-jbench/SKILL.md)
(the same folder is `.agents/skills/strata-jbench`). An agent that has skills loads it by name; any other agent reads
SKILL.md first and then the reference it points to. The section numbers below are the ones the scripts' messages and
the pages use.

| Section | What | Where |
| --- | --- | --- |
| 2.0 | When the hardware changes (another card, more RAM, another PC) | [references/setup.md](.claude/skills/strata-jbench/references/setup.md) |
| 2.0a | When a model, a harness or an engine is missing | [references/setup.md](.claude/skills/strata-jbench/references/setup.md) |
| – | Choosing what to measure: the configurator and the recipe | [references/configure.md](.claude/skills/strata-jbench/references/configure.md) |
| 2.1 | When the plan changes (cases, models, tasks) | [references/extend.md](.claude/skills/strata-jbench/references/extend.md) |
| – | Another engine: derived engines, tracks, attach only | [references/engines.md](.claude/skills/strata-jbench/references/engines.md) |
| 2.2 | Settings and checks before starting | [references/run.md](.claude/skills/strata-jbench/references/run.md) |
| 2.3 | Starting, and the watch task | [references/run.md](.claude/skills/strata-jbench/references/run.md) |
| 2.4 | When something goes wrong | [references/run.md](.claude/skills/strata-jbench/references/run.md) |
| 2.5 | Checking the results | [references/review.md](.claude/skills/strata-jbench/references/review.md) |
| 2.6 | When the run ends | [references/run.md](.claude/skills/strata-jbench/references/run.md) |
| 2.7 | Making results final and committing them | [references/publish.md](.claude/skills/strata-jbench/references/publish.md) |
| 4 | Files and where they are | [references/files.md](.claude/skills/strata-jbench/references/files.md) |
| 5 | Notes on Strata | [references/strata-notes.md](.claude/skills/strata-jbench/references/strata-notes.md) |

## 3. Ask first

Even if one of these becomes necessary during a run, do not do it yourself: follow the policy decided in 2.2. With no
policy, report the cause and a proposal, and stop.
- Deleting models or results (except the converted QAD source, which `scripts/overnight.py` deletes)
- Downloading or installing anything: models, the drafter, a harness, an engine (`"fetch": true`, `scripts/acquire.py fetch`).
  Ask it as a choice of two: fetch it for jbench alone into `tools/` inside the repository (not in Git; the version and
  SHA-256 are pinned and recorded), or use what is on the PC already at a path the user gives (recorded as the user's).
  Prefer the first: a run should measure fixed versions. For an engine, show the URL, the size and the SHA-256 first
- Stopping a Strata engine other than the measuring one, or changing Strata's saved settings or presets
- Changing the case plan
- Publishing, such as `git push`
- Changing system settings (linger, power, the GPU power limit and so on)
