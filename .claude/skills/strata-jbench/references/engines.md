<!-- Part of the strata-jbench skill. -->

# Another engine: derived engines, tracks, attach only

A run measures one engine: bench.json `engine` (`strata` by default). `python3 -I scripts/catalog.py` lists the
engines of `catalog/engines/`. The run records what it measured in `engine.json` (the engine, its version, the track,
where it came from), and results are only put side by side under the same case conditions.

## Three ways an engine is driven

| Kind | Engines | What jbench does | What is checked |
| --- | --- | --- | --- |
| Managed, Strata's CLI (`strata_cli`) | `strata` | starts it with `strata launch`, stops it | the launch choices on the engine's own command line, the draft layer loaded |
| Managed, its own adapter (`sync_cli`, …) | `sync-strata` | starts its launcher with a settings folder of the run's own, stops it | the engine's resolved config against what was asked |
| Attach only (`openai_endpoint`) | `endpoint` | nothing: the user starts the engine, jbench sends the requests | nothing about the launch; the results say "attach only" |

## Tracks

Some engines trade quality for speed by default (Sync-Strata's tail skip uses fewer experts per token). bench.json
`track` says how the engine is set, and results of different tracks are never mixed:

- `exact`: every approximation the engine's entry lists (`approximations`) is off. The default, and the only track
  that shares the pages with other engines.
- `default`: the engine as it comes.
- `custom`: anything else. An attached endpoint is always `custom`.

To compare an engine's own default against exact, measure both tracks as two runs.

## Trying a derived engine today (attach only)

For an engine with no adapter. Nothing is installed or started by jbench.

1. The user installs and starts the engine themselves, with one model loaded at a 128K context, and gives its URL.
   jbench does not download or run a third party's programs here; that is the user's decision and action.
2. bench.json: `"engine": "endpoint"`, `"engine_url": "http://127.0.0.1:8080"`, `"models": ["<family> <model>"]` (the
   one model that is loaded, as the catalog names it; a build the catalog does not have is added first:
   [extend.md](extend.md)), `"engine_note"`: what is running, in the user's words (the engine, its version, how it was
   started). The note is kept as said; jbench cannot check it.
3. `python3 -I scripts/bench.py plan`: an attached engine gets the cases of one start (the speed and thinking tasks
   at 128K). Cases that need another context or another launch are not asked.
4. Run as usual ([run.md](run.md)). Timings the engine does not return stay "not measured": they are never filled in
   from the client's clock. The client-side numbers (time to the first token, to the end) are always there.

## A managed derived engine: Sync-Strata

`sync-strata` (github.com/hiruhiru2005/sync-strata) runs Qwen3.8-Flash-Next in its own quantizations Sync-XS / S / M;
its formats are not compatible with Strata's, so these builds belong to this engine alone.

1. `"engine": "sync-strata"` in bench.json, then `python3 -I scripts/acquire.py check`. It needs the engine itself
   (`tools/engines/sync-strata/<version>/`) and the model packs with the shared files.
2. The models folder is recorded first, wherever the files are or will be:
   `python3 -I scripts/provision.py set-models sync-strata --path DIR`. The packs are fetched with the hf CLI at the
   revisions of the engine's `models.dist.json` (the pinned release's catalog), into the layout that file names
   (`sync-xs-sb/`, `sync-s-sb/`, `sync-r1q2-sb/`, and `native-gguf/`, `mtp-rt/`, `tokenizer/` beside them).
3. `python3 -I scripts/acquire.py fetch engine:sync-strata` shows the release's URL, size and SHA-256 and asks; on a
   yes it downloads the archive, refuses it unless the SHA-256 is the pinned one, unpacks it and runs the engine's
   own installer into `tools/engines/sync-strata/<version>/` with no shortcuts, its own settings folder and no model
   download. Nothing outside that folder is changed. Ask the user first, as in [setup.md](setup.md) 2.0a; an install
   they already have is `provision.py set-engine sync-strata --path DIR --by user` instead.
4. Add the builds to the environment (`envs/<env>/env.json` "models": `"sync Sync-XS"`, …, unless it is `null`),
   `python3 -I scripts/build_cases.py`, then preflight and a `test-` case before a real run.

What the adapter checks per start: the model pack, the context, the KV format, the GPU, the draft layer loaded, and on
the `exact` track that tail skip is off both in the resolved config and in the engine process's environment.

## Adding an adapter

When an engine is worth more than attach-only: one file `scripts/engines/<name>.py` with `class Adapter(Engine)`
(`scripts/engines/__init__.py` documents each method: `probe`, `needs`, `preflight`, `start`, `verify`, `pid`,
`collect_log`, `stop`, `describe`; `fetch_plan` and `fetch` if jbench can fetch it), and its entry
`catalog/engines/<id>.json` ([catalog/README.md](../../../../catalog/README.md)). Rules that keep results honest:

- `start` returns an error rather than a session it could not set as asked; `verify` names what it could not confirm.
- `stop` stops only what this adapter started.
- The engine's settings live in a folder of the run's own; the user's install is neither read nor changed.
- Everything that changes the output for speed goes in `approximations`, with a way to turn it off on `exact`.

Then: `python3 -I scripts/catalog.py`, a `test-` run of one case, and `scripts/verify_run.py` on it.
