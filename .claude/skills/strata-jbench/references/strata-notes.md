<!-- Part of the strata-jbench skill. Section numbers (2.x) are the ones scripts and other pages point to. -->

# Notes on Strata

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
- Hy4-Flash (`hy4-flash`, since 0.2.18) is another model with its own engine program (`strata-hy4`, a component) and its
  own files (`<models>/hy4-flash/`: one build, the Engram shard every build shares, the Vision shard; pinned by
  `strata_control/hy4_family.py`, listed in `downloads/manifest.json` by `scripts/download_models.py`). Its drafter is
  DFly2, built in: the runner launches it without `--drafting mtp --mtp on` and fails a case whose engine line lacks
  `--draft dfly2`. Its responses carry no draft counts (`draft_n` 0), so Hy4 has no acceptance rate. `strata install`
  puts the files in Strata's saved data folder (`data_dir` in `~/.config/strata/settings.json`; on `rtx5090-128g`
  `/mnt/data/strata/Strata-data`), and fetches them again if they are anywhere else; the folder in the models root
  links there. `scripts/download_models.py` makes that link before fetching (and refuses when the folder is
  elsewhere), and `scripts/install_configs.py` installs such a model only when its files are there, and stops a setup
  that starts downloading a model file (`envs.STRATA_FOLDER_ONLY`; SQ-64 and Engram were fetched twice on 2026-11-22).
  Run `strata install` by hand only through `install_configs.py`.
- Since 0.2.18 Strata's source keeps `setup.py`, `tools/` and the requirements in `terminal/`; the scripts read either layout.
- Q2_0's first launch builds a pack for AVX-512 (about 40 GB). The first launch's time is not part of the measurements.
