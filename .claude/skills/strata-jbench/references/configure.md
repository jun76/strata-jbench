<!-- Part of the strata-jbench skill. -->

# Choosing what to measure: the configurator and the recipe

## The configurator

`python3 -I scripts/build_configurator.py` writes `preview/configurator.html` (one file, no server needed; it also
opens from `file://`). It holds the catalog and, for every environment, each case with its estimated time. Open it for
the user:

- with a browser tool: the file itself, or through the repository's preview server (`.claude/launch.json` "pages",
  then `http://localhost:8765/preview/configurator.html`);
- without one: give the user the absolute path.

`#env=<id>` in the URL opens it on a given environment (the page picks this PC's by itself when it was built here),
`#engine=<id>` on an engine, `#lang=ja|en|zh` in a language. `--published` writes `configurator/index.html`, the
committed page GitHub Pages serves (published runs' environments only).

On the page the user picks, top to bottom: the environment (for the time estimate), the engine and its track, the
driver (the API directly, or a harness), the models, and the tasks (a preset, or task by task; each card shows what
is sent, and opens to the prompt itself). The right column follows every click: the estimated time by task, the
headline numbers the selection gives and what to add for the missing ones, the metrics covered, and the recipe.

Nothing on the page is written by hand: the template is `assets/configurator.template.html` in this skill, filled by
the script from `catalog/` and the plan. To change what it offers, change the catalog ([extend.md](extend.md)).

## The recipe

```text
jbench-recipe/1
engine: strata (track exact)
driver: plain
preset: standard
models: qwen IQ3_S, inkling-2-mini SQ-15
id: r1-123174da
```

- `python3 -I scripts/bench.py recipe` prints the recipe of bench.json as it is.
- `python3 -I scripts/bench.py recipe --apply FILE` (or `-` for stdin) checks a pasted recipe and writes it into
  bench.json: `engine`, `track`, `division`, `preset`, `tasks`, `tiers`, `models`. It leaves `run_id` and the watch
  settings alone. A line it does not know, a model or a task not in the catalog, or an `id` that does not match the
  lines is an error: say so to the user, do not guess.
- The id is a hash of the engine, the track, the driver and the tasks with their versions. The models are not in it.
  Two runs with the same id used the same ruler; a task whose prompts or conditions changed has a new version, hence a
  new id.

## From a recipe to a run

1. Save what the user pasted to a file (the scratchpad) and apply it. Show the recipe printed back.
2. `python3 -I scripts/bench.py plan`: the cases, the requests and the hours by Tier and by task. If it says "not in
   this plan", the model is not among this environment's (`envs/<env>/env.json` "models") or the engine does not take
   the task: tell the user which, do not drop it silently.
3. `python3 -I scripts/acquire.py check`: what is missing ([setup.md](setup.md) 2.0a).
4. Ask for a `run_id` (a date and a word, e.g. `2026-11-25-standard`; `test-…` for a check), then
   [run.md](run.md) 2.2.

## Without the page

A user who knows what they want can say it in words. Write bench.json yourself (only the keys that differ from the
defaults; `python3 -I scripts/bench.py config` lists them) and show them the recipe and the plan before anything
starts. `preset` and `tasks` choose by task; `tiers`, `models` and `cases` narrow further (a single case measured
again is `cases`, and such a run says "partial" where it is shown).

## What the presets are

| Preset | Tasks | For |
| --- | --- | --- |
| `quick` | the cases the two headline speed numbers are read from (JB-decode, JB-ttft-32k) | a first number in minutes; the entry for sharing results from another PC |
| `standard` | speed-decode, speed-prefill, think-qa, code-oneshot | all four headline numbers; about half an hour a model on a fast card |
| `full` | every task of the plain driver | the whole picture; hours to days |

`python3 -I scripts/catalog.py` lists the tasks with the metrics each gives.
