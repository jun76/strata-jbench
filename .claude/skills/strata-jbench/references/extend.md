<!-- Part of the strata-jbench skill. Section numbers (2.x) are the ones scripts and other pages point to. -->

# Changing what is measured: cases, models, engines, tasks

What can be measured is data, in `catalog/` ([catalog/README.md](../../../../catalog/README.md)); how a case is built
from it is code, in `scripts/case_plan.py`. `python3 -I scripts/catalog.py` checks all of it.

| To add or change … | Edit | Then |
| --- | --- | --- |
| a build of a base model that is there | `catalog/models/<base>.json` "builds" (its role's English and Chinese in `scripts/i18n.py` `TR`) | `catalog.py`, `build_cases.py`; the downloads and Strata's run config for it ([setup.md](setup.md)) |
| a base model | a new `catalog/models/<base>.json`: its tokenizer, trained length, whether it thinks, its drafter | the same; no code names a model, so the plan follows what the file says |
| an engine | `catalog/engines/<id>.json` and, unless it is attach only, `scripts/engines/<adapter>.py` | [engines.md](engines.md) |
| a task, a preset, a metric, a headline number | `catalog/tasks.json`, `catalog/metrics.json` | `catalog.py` (every case must belong to exactly one task) |
| what a task asks (a prompt, a cap, a condition) | `scripts/case_plan.py`, `scripts/build_fixtures.py`, and **raise the task's `version`** in `catalog/tasks.json` | 2.1 below. The cases' condition hashes change by themselves; the version makes the recipe's id change too |

## 2.1 When the plan changes
1. Edit `scripts/case_plan.py` (the only place cases are defined; differences between environments go in env.json).
   A model or a base model is added in the catalog instead (`catalog/models/<base>.json`, [catalog/README.md](../../../../catalog/README.md));
   `python3 -I scripts/catalog.py` checks it, the tasks and the headline numbers (`catalog/tasks.json`, `metrics.json`) included.
2. Run `python3 -I scripts/build_cases.py` and check the number of cases and the estimated hours per environment.
   `preview/cases/` and `plan/<division>/<env>/cases.jsonl` are updated (`--published` for the committed `cases/`).
   The case lists have a Markdown file per language (`README.md`, `README.en.md`, `README.zh.md`, `tier-<Tier>.md`
   and so on) and the charts switch between Japanese, English and Chinese. When a case definition gains a Japanese
   string, add its English and Chinese to `TR` in `scripts/i18n.py` (strings without a translation are listed when the
   script runs, and shown in Japanese).
3. If a new fixture is needed, change `scripts/build_fixtures.py` and run it with the Python that ships with Strata (see
   the docstring at the top of the file; `--only <fixture>` rewrites one chat fixture without counting the long ones again).
   The coding cases: plain's Tiers 0 and 3 ask for a scene titled "A sailing ship calling at a harbor" in 3D voxel art
   as one HTML file (`coding-harbor`; the scene is given by its title alone, thinking is fixed at 64K and the cap is the
   whole 128K window, since every model thinks all of its budget on it); the
   Minecraft prompt (`game-minecraft`) is the harness divisions' case.
   The long document of Tiers 4b–4d comes from ten works of Aozora Bunko and Project Gutenberg (five Japanese, five
   English), cleaned by `scripts/long_corpus.py` into `prompts/long-corpus.txt`, Japanese and English chunks in turns.
   Sources, editions, SHA-256 and Aozora's colophons are in `prompts/long-sources.json`; the downloads are in
   `work/corpus/raw/` (not in Git). A long fixture holds only the number of corpus lines, the made-up facts placed at
   10 / 50 / 90% ("the passwords of the east, central and west storehouses") and the questions; the runner assembles
   the document.
4. Update the matching part of [docs/SCOUTING.md](../../../../docs/SCOUTING.md) too.
5. No backward compatibility: the case lists and the charts show the plan as it is now. A case taken out of the plan,
   or replaced by another (say, one coding prompt by another), leaves them, with the results earlier runs have for it;
   those results stay readable in each run's own snapshot (`snapshots/<division>/<env>/<RUN_ID>/`, never rewritten)
   and in `published/`. Do not keep old cases on the pages as "retired" ones, and do not write how a case used to be
   in the lists or the pages (the history goes in docs/SCOUTING.md and the commit message).
   A model is another matter: one left out of env.json `models` (its files replaced, a disk too small) keeps its
   results on the pages and in the lists, for every case the plan builder still makes the same way
   (`case_plan.measured_rows`); only the plan and the estimate follow `models`. The charts list every model of
   the catalog in every environment, the same set everywhere: which models an environment measures is the
   measurer's choice (a disk too small for some), so a model with no value reads "not measured".
