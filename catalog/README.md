# catalog/ — what jbench can measure, as data

The plan builder and the runner read these files instead of naming models in code. Adding a base model or a build is an
edit here; `python3 -I scripts/catalog.py` lists the catalog and reports what is wrong in it, and
`python3 -I scripts/build_cases.py` then shows the plan it gives.

## models/<base>.json

One file per base model. What is said at the top holds for every build of it.

| Key | What it is |
| --- | --- |
| `base` | The id (the file's name) |
| `order` | Where it comes on the pages and in the lists (ascending) |
| `label` | Its name for readers |
| `tokenizer` | Builds with the same tokenizer are fed the same number of tokens by a fixture, so their tok/s compare directly; across tokenizers they are a reference only |
| `trained_context` | The trained length in tokens. Past it Strata uses YaRN, and the long-context cases are marked as the extended range |
| `max_context` | The longest context its engine takes (`null`: no limit of its own). Longer cases are not made |
| `thinking` | `false`: served with thinking off only. Its thinking-on cases are not made and the coding task is asked with thinking off |
| `lineup` | `main` or `other`. The representatives of the long-context and launch-option cases (the largest, the smallest) are picked among the `main` builds; an `other` base model still gets its own largest build there |
| `drafter` | `{"pin": "mtp", "also": {"dflash2": [families]}}`: the runner pins this drafter at launch, and the families listed are measured once more with the other one. `{"builtin": "dfly2", "label": "DFly2", "reports_counts": false}`: the builds carry their own drafter, the runner pins nothing and checks that the engine started with it; `reports_counts: false` when the engine's responses carry no draft counts (no acceptance rate) |
| `builds` | The builds, in page order |

A build:

| Key | What it is |
| --- | --- |
| `family`, `model` | Strata's names (`strata launch --family F --model M`). They are the case ids and the folders. A family belongs to one base model |
| `size_gb` | The download's size (GB), for the size classes of the estimates and for picking representatives |
| `role` | One line on what it is, in Japanese (its English and Chinese are in `scripts/i18n.py` `TR`) |
| `derivative` | `true` for a fine-tune or a pruned version: not a quantization of the original weights, so it is outside the official profile of standard-v1 and never a representative while another build is there |
| `display` | The name on the pages where the plain name would mislead (Unsloth's sets before and after Dynamic v3.1 share names) |

Notes on particular builds (kept here, JSON has no comments):

- **Unsloth, Qwen3.8-Flash-Next.** Unsloth re-published its repository on 2026-11-04 as Dynamic v3.1 under the same
  names. Of the sets Strata pinned before (commit 38bb39ee), UD-IQ4_XS and UD-Q4_K_XL were replaced on the Hub then;
  Strata keeps the old UD-Q4_K_XL and calls the new UD-IQ4_XS `UD-IQ4_XS-v31` (another file: 345 of 1224 tensors of
  another type). UD-Q5_K_XL, UD-Q6_K_XL and Q8_0 are the same files still. The v3.1 sets need engine 0.1.57 or later.
- **Hy4-Flash** (Strata 0.2.18 on): its own engine program (strata-hy4). The size is the build's file (Strata's hy4_fit
  footprint is within 0.6 GB of it); the Engram shard every build shares (67.6 GB) is a lookup table read as needed and
  is not counted.
- **Inkling-2-Mini** (Strata 0.2.19 on): its own engine program (strata-inkling), Strata's `.strata` v1.1 builds. The
  size is the build's file (Strata's inkling_fit footprint is the same).

Where a property belongs to the pair of an engine and a model rather than to the model (the drafter, today), it will
move to the engine's entry when engines get a catalog of their own.

## engines/<engine>.json

One file per engine a run can measure (bench.json "engine").

| Key | What it is |
| --- | --- |
| `id`, `order`, `label`, `source` | The id (the file's name), its place on the pages, its name, where it comes from |
| `adapter` | The module in `scripts/engines/` that drives it: `strata_cli` (Strata's CLI), `sync_cli` (Sync-Strata's launcher), `openai_endpoint` (attach to a running URL) |
| `managed` | `true`: jbench starts and stops it and checks what it asked for. `false`: attach only; the results say so and are never mixed with the others |
| `steps` | The Tiers it is asked (`null`: all). Another engine than Strata gets none of Strata's launch options (the DFlash2 launches, Tier 5) |
| `max_context` | The longest context it takes (`null`: no limit of its own) |
| `tracks` | How it can be set, with each track's settings: `exact` (approximations that change the output off), `default` (as it comes), `custom` |
| `approximations` | The options that trade quality for speed, with their `exact` and `default` values, for readers |
| `pin` | The release jbench fetches for itself: version, archive (URL, bytes, SHA-256), the installer's arguments |
| `about` | One paragraph for readers, in Japanese, English and Chinese |

A build names the engines that run it with `"engines": [...]` in `models/<base>.json` (Strata where it says nothing).

A build with `"own"` is a file Strata's setup does not list, of a model it does (Gyro-S v2: the same name, size and
tensor types as Gyro-S, other expert weights). jbench keeps the file, a pack built from it and a run config in a
folder of its own, and starts the model Strata knows (`"as"`) with `STRATA_INSTALL_DIR` pointing there, so Strata's
saved run configs and the known model's files stay as they are (`scripts/own_build.py`: `prepare`, and the state on
this PC). `"repo"`, `"revision"`, `"file"` and `"sha256"` say where the file comes from.

## tasks.json

`tasks`: what a run can do, by name. A task is tied to the plan's cases by `match` (`step`: the Tiers it covers;
`fixture_prefix`: the fixtures within them), so every case belongs to exactly one task (`scripts/catalog.py` checks the
plans on this PC). `label`, `question` (what it answers) and `sends` (what is sent, in plain words) are for readers, in
Japanese, English and Chinese. `metrics` are the metrics it gives (ids of metrics.json), `headline` its headline number,
`models` which models get it (`all`, `representatives`, `reference`), `engines` / `drivers` where it is limited to some.

`presets`: bundles of tasks. An entry may narrow a task with `only` (a case's field -> the values kept): `quick` keeps
just the cases the headline numbers are read from.

## metrics.json

`metrics`: every metric in one line: its unit, which way is better, and where the number comes from (`engine`: the
engine's own timings in the response; `client`: the runner's clock; `judge`: a check of the answer or the page;
`runner`, `proxy`: the runner's and the recording proxy's records).

`headlines`: the numbers shown first and compared across environments. Each is one metric of one task under one fixed
condition (`where`: a case's fields), never a summary over several kinds of cases, so that it can be said in one line.
