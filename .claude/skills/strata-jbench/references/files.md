<!-- Part of the strata-jbench skill. Section numbers (2.x) are the ones scripts and other pages point to. -->

# Files and where they are

| What | Where |
| --- | --- |
| The models | `~/.local/share/strata/Strata-data/models` (`downloads/manifest.json` lists them with SHA-256) |
| Fetching state | `downloads/` (not in Git); `READY` marks that every model of env.json is on disk (a run needs only its own: `scripts/acquire.py check`) |
| Fixed prompts | `prompts/` (SHA-256 in `MANIFEST.json`); the long document's source is `prompts/long-corpus.txt` and `long-sources.json` |
| What a run needs on disk | `run-status/acquire.json` (`scripts/acquire.py check`) |
| Harnesses | the pinned version per division in `divisions/<division>/division.json` "pin"; installed by jbench in `tools/harness/<division>/<version>/` (not in Git), or found at the pinned version in its default place; adapters in `scripts/harnesses.py`; the one a run drove in the run's `harness.json` |
| A harness case's record | `cases/<case id>/harness/seed-N/` (the harness's events and stderr, its config, the command, `proxy.jsonl`: one line per request with what the harness sent and what was forwarded); the work folder, the harness's folder and the request bodies stay in `raw/` |
| Engines | `catalog/engines/<engine>.json` (the adapter, what it is asked, its tracks, the pinned release); adapters in `scripts/engines/`; the one a run measured in the run's `engine.json`; engines jbench fetched in `tools/engines/<engine>/<version>/` (not in Git) |
| What is used on this PC | `tools/provision.json` (`scripts/provision.py`: what, version, SHA-256, where, fetched by jbench or named by the user); the run's copy `provision.json` |
| Divisions | `divisions/<division>/division.json` (only a division whose `status` is `active` can be measured; see [divisions/README.md](../../../../divisions/README.md)) |
| Environments | `envs/<env>/env.json` (written by hand on each PC, not in Git; fields in [envs/README.md](../../../../envs/README.md); matching and templates in `scripts/envs.py`); the copy a run measured with is `results/` or `published/<division>/<env>/<RUN_ID>/env.json` |
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
