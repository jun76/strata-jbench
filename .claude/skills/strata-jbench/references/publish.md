<!-- Part of the strata-jbench skill. Section numbers (2.x) are the ones scripts and other pages point to. -->

# Making results final, committing, sharing

## 2.7 Making results final and committing them
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

## Results from another PC

Anyone can measure with the same recipe and offer the results: a run made final on their PC is the folder
`published/<division>/<env>/<RUN_ID>/` with its snapshot and the rebuilt lists, as a pull request.

- The environment id names the hardware (`envs.py new` suggests `<GPU>-<CPU>-<RAM>-<model disk>`); two people with the
  same hardware add a suffix of their own rather than share an id.
- Before accepting one: `python3 -I scripts/verify_run.py --published <env> <RUN_ID>` (the timings against the client's,
  the settings each session asked for), the run's `recipe.txt` and `engine.json` (which engine, which version, which
  track, managed or attach only), `models.json` (every file's SHA-256 against the pins) and `provision.json`.
  A run whose `engine.json` says `"managed": false` or a track other than `exact` is kept as a result of its own and
  does not enter the shared tables.
- The quickest entry for a newcomer is the `quick` preset: the two headline speed numbers, in minutes.
