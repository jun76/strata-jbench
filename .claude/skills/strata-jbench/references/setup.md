<!-- Part of the strata-jbench skill. Section numbers (2.x) are the ones scripts and other pages point to. -->

# Setting up: a new PC, new hardware, what is missing

## 2.0 When the hardware changes (another card, more RAM, another PC)
On a PC that has not run the benchmark yet, first: Strata (the desktop app) installed with one model installed through
it once (that writes `~/.local/share/strata/install/third_party/llama.cpp`), and Strata's source checked out at
`~/Strata` (its `setup.py` pins every file fetched). `scripts/setup_acquire.py` then makes the rest (the venvs, the
download list, the NVFP4-QAD converter); `scripts/bench.py start` runs it by itself. After the models are on disk,
the NVFP4 ready-made packs need Strata's setup once with `--no-start` to write their run configs (otherwise
`strata launch --plan` reports them as needing a download); it changes Strata's saved settings, so section 3 applies.

1. `python3 -I scripts/envs.py list` shows whether an environment matches the hardware now (marked `*`).
2. If none does, `python3 -I scripts/envs.py new <env>` writes `envs/<env>/env.json` (with no name given, it
   suggests one: `<GPU>-<CPU>-<RAM>-<model disk>`, like `rtx5070-cu5_235-64g-sata`; the CPU's parts are joined with `_`
   so that `-` only separates the parts. The id is the folder in every path and URL, so it names what moves the
   results. `rtx5090-128g` is from before this rule). On a PC with two cards each card is an environment of its own:
   `--gpu N` picks the card (`gpu_index`; the runner launches with `--gpu N` and reads that card alone). When two
   environments match the PC, name one with bench.json's `env`. It fills in the GPU name, VRAM, RAM and whether DFlash2
   is available (checked with `strata launch --plan`).
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
     the largest, the smallest, the largest of each family: file sizes only), not by name (`scripts/case_plan.py`
     `representatives`)
   - `models`: the list (in the form `"qwen IQ3_S"`) to measure only some models; `null` for every model of
     the catalog (`catalog/models/`, including models added later). The downloads follow it too: `scripts/setup_acquire.py`
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

## 2.0a When a model, a harness or an engine is missing

**How to ask.** A run should measure fixed versions, so wherever possible what it needs is fetched for jbench alone,
not borrowed from what the user happens to have installed. For each missing piece, ask the user this, naming the
piece, its version, its size and where it comes from:

> ⟨Sync-Strata 0.1.4 (the Linux release, 1.1 GB, from github.com/hiruhiru2005/sync-strata/releases)⟩ is needed.
> 1. May I download it into `tools/` inside this repository (not in Git) and use it from there? Recommended: the
>    version and SHA-256 are pinned and recorded.
> 2. Or, if it is already on this PC, tell me where it is. I will record its version and SHA-256 as found, and the
>    results will say it was the user's own install.

Then act on the answer, and record it: `tools/provision.json` (`scripts/provision.py`) says for every engine,
harness and models folder what it is, its version, where it is and whether jbench fetched it (`"by": "jbench"`) or the
user named it (`"by": "user"`); every run copies that file into its folder.

| Piece | Fetched into | Using what is on the PC already |
| --- | --- | --- |
| An engine | `tools/engines/<engine>/<version>/` (`acquire.py fetch engine:<id>`: the pinned release, its SHA-256 checked before anything runs, its settings in that folder) | `provision.py set-engine <id> --path DIR --by user`; a version other than the pin is recorded as such |
| A harness | `tools/harness/<division>/<version>/` (`acquire.py fetch harness:<division>`) | only at the pinned version, found in its default place; another version is neither used nor touched |
| Models | a folder the user names when the repository's disk is small (`provision.py set-models <group> --path DIR`); hf CLI, pinned revisions | the same files elsewhere are as good **when every file's size and SHA-256 match the pin**: models are hundreds of GB, and equal bytes are the same version. Say so when asking |
| Strata itself | not yet: Strata is the user's install (the `strata` CLI on PATH), its version recorded per run | – |

Nothing is fetched during a measurement, and nothing before the user has answered.

`python3 -I scripts/acquire.py check` lists what the run needs on disk (the models of the plan, the DFlash2 drafter, a
harness division's pinned harness, bubblewrap; for another engine than Strata, the engine itself and its models, as its
adapter says) and whether each is there; it changes nothing (and writes
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
