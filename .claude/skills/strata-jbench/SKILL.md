---
name: strata-jbench
description: Measure local LLM inference engines (Strata and engines derived from it) with strata-jbench in this repository, set up a PC for it, choose what to measure with the configurator and a recipe, run and watch a benchmark, check and publish results, try another engine, or add a model, task or engine. Use whenever the user asks to run, plan, configure, resume, check or publish a jbench / strata-jbench benchmark, pastes a text starting with "jbench-recipe/1", or asks what jbench measures. このリポジトリの strata-jbench でベンチを測る・設定する・再開する・結果を確認・公開する、派生エンジンを試す、レシピ（jbench-recipe/1）を渡された、といったとき。
---

# strata-jbench

strata-jbench measures local LLM inference engines under fixed, repeatable conditions and publishes the results with
everything needed to run them again. One run measures **one engine** (Strata, a derived engine, or an endpoint the
user started) on **one environment** (this PC's hardware) through **one driver** (the engine's API directly, or an
agent harness), for the **models** and **tasks** chosen. What was chosen is one text, the **recipe**; its id says which
ruler was used.

Read [AGENTS.md](../../../AGENTS.md) first if you have not: its principles (section 1) and "Ask first" (section 3)
hold in every procedure below. In short: long work is started detached and never waited for in the session; every
question that needs the user's decision is asked before starting; nothing is downloaded, deleted, published or changed
in the system without the user's word.

## Where to go

| The user wants to … | Read |
| --- | --- |
| use jbench on this PC for the first time, or after a hardware change; something is missing | [references/setup.md](references/setup.md) |
| choose what to measure; open the configurator; "here is a recipe" | [references/configure.md](references/configure.md) |
| start, resume, watch, stop a run; a run failed or is stuck; a run ended | [references/run.md](references/run.md) |
| see or check results, rebuild the pages | [references/review.md](references/review.md) |
| make a run final, commit it, share results from another PC | [references/publish.md](references/publish.md) |
| measure another engine (a derived engine, an engine already running) | [references/engines.md](references/engines.md) |
| add or change a model, a case, a task, a headline number | [references/extend.md](references/extend.md) |
| know where a file is | [references/files.md](references/files.md) |
| understand a Strata behaviour the runner works around | [references/strata-notes.md](references/strata-notes.md) |

## The usual path, start to end

1. **Where are we.** `scripts/jb where` (the environment this hardware matches, the engines here, what bench.json
   says, whether a run is alive). No matching environment: [references/setup.md](references/setup.md) 2.0.
2. **Choose.** `scripts/jb configure` builds the configurator and prints its path; open it for the user (the browser
   pane if you have one, else give the path). The user picks the engine, the models and the tasks, sees the time and
   the metrics covered, and pastes the recipe back. `scripts/jb recipe --apply FILE` writes it into bench.json.
   A user who already knows what they want may just say it: write bench.json and show `scripts/jb recipe`.
3. **Show the plan and what is missing.** `scripts/jb plan` (cases, requests, hours) and `scripts/jb check` (what the
   run needs on disk). For each missing piece ask the user the two-way question of
   [references/setup.md](references/setup.md) 2.0a. Set `run_id`.
4. **Ask, then start.** Go through [references/run.md](references/run.md) 2.2 with the user (settings, the
   environment, other engines on the GPU, logout and reboot, the watch task). Then `scripts/jb start`, register the
   watch task (2.3), report the expected end.
5. **When it ends.** [references/review.md](references/review.md), then, if the user says the run is final,
   [references/publish.md](references/publish.md). Never push without the user's word.

## The commands

`scripts/jb` (in this skill's folder) runs the repository's scripts from any working directory:

| Command | What it does |
| --- | --- |
| `jb where` | the environment, the engines found, bench.json's recipe, the run's status |
| `jb configure [--published]` | build the configurator page and print where it is |
| `jb recipe [--apply FILE]` | the recipe of bench.json; or write a pasted one into it |
| `jb config` | every setting with its value, default and meaning |
| `jb plan` | the cases chosen and the estimated hours, by Tier and by task |
| `jb check` | what the run needs on disk and whether it is there (changes nothing) |
| `jb catalog` | the models, engines, tasks and headline numbers, and anything wrong in them |
| `jb start` / `jb status` / `jb stop` | the run's supervisor |
| `jb pages` | rebuild the preview case lists, charts and configurator |

They are thin: `python3 -I scripts/bench.py …`, `scripts/acquire.py check`, `scripts/catalog.py` and so on, which the
references name where a step needs more than the wrapper gives.

## What must not be skipped

- A measurement is only comparable if the engine was set as the recipe says. The runner fails a case whose setting
  it cannot confirm ("setting not applied", "MTP not loaded"); do not work around that, find the cause.
- `test-` run ids are for checks and are never shown or published. After changing the runner, an adapter or a
  fixture, run one affected case under a `test-` id before a real run.
- An engine, a harness or a model is fetched only after the user chose how
  ([references/setup.md](references/setup.md) 2.0a). Prefer fetching it for jbench alone into `tools/`: a run should
  measure pinned versions.
- Results of an attach-only engine, or of a track other than `exact`, are never mixed with the others.
