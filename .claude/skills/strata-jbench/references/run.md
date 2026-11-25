<!-- Part of the strata-jbench skill. Section numbers (2.x) are the ones scripts and other pages point to. -->

# Running: settings, checks, start, watch, recover, end

## 2.2 Settings and checks before starting (do not start until these pass)
1. **Go through the settings with the user.** Run `python3 -I scripts/bench.py config` and show the user every
   parameter: its name, the value in force, the default and what it does (in the user's language). Ask whether any
   value should change, and in particular:
   - `run_id`: a new RUN_ID, or an existing one to resume (`test-` for a check).
   - `engine` and `track`: what is measured and how it is set ([engines.md](engines.md)). `preset` and `tasks`: what
     is run, by task ([configure.md](configure.md)); a recipe the user pasted sets all of these at once
     (`bench.py recipe --apply`). Show the recipe (`python3 -I scripts/bench.py recipe`) with the plan.
   - `division`, `tiers`, `models`, `cases`: what to measure. Not every Tier has to run: `python3 -I scripts/bench.py
     plan` shows the cases chosen and the estimated hours per Tier (and says when Tier 0 has never run in this
     environment). Show the plan to the user before starting.
   - `fetch`: only `true` when the user agreed to jbench fetching what `python3 -I scripts/acquire.py check` reports
     missing (2.0a).
   - The watch (`watch_interval_s`, `crash_restarts`, `stuck_restarts`, `notify`) and `smoke`, `stats`.
   Write the values agreed into `bench.json` (only the keys that differ from the default), then run `bench.py config`
   again and show the result. A user who edits `bench.json` by hand needs none of this: check it with `config`.
2. Ask the user and get an answer for each of these:
   - Which environment to measure in (is the result of `python3 -I scripts/envs.py detect` the set-up the user meant?).
   - Whether a Strata engine other than the measuring one (the desktop app, say) is using the GPU (`nvidia-smi`,
     `pgrep -af "strata --serve"`), and if so, whether it may be stopped.
   - Whether it runs across a logout or a reboot. The supervisor survives the terminal and the agent's session being
     closed, but while linger is off the user's last logout ends it (`loginctl enable-linger`, a system setting: the
     user does it), and a reboot always does (`bench.py start` again resumes; the watch task of 2.3 does it).
   - Whether anything in section 3 ("Ask first") may become necessary during the run; if so, have the user decide
     beforehand what to do. Strata's run configs for models just fetched (`scripts/install_configs.py`, run by the
     supervisor) change Strata's saved settings.
   - For a harness division: that the model will run shell commands and write files inside the sandboxed work folder
     (the network is not cut off: a harness reaches the proxy over it).
   - That the hourly watch task will be registered at the start (step 3 of 2.3: which scheduler, where it reports,
     what it does not survive) and deletes itself once the run is over, whether it succeeded or not (2.6).
3. After changing the runner or a fixture, run the affected cases under a RUN_ID starting with `test-` (`test-` results
   appear neither in the case lists nor in the charts): either with `bench.py start` and `"cases": [...]`, or directly
   `python3 scripts/bench_runner.py --run-id test-xxx --steps 1 --ids <case id>,...` (a harness division: with
   `BENCH_DIVISION=<division>` and `--steps G`).
4. Preflight: the supervisor runs it before measuring (with one real launch unless `"smoke": false`) and starts nothing
   if it fails. To see it first: `python3 scripts/preflight.py --phase all --steps "<the Tiers, comma separated>"`
   (`--phase acquire` before every model is on disk); the result is `run-status/preflight.json`. It also checks the
   environment (which env.json this hardware is, that the plan is newer than env.json, that the power limit is
   env.json's) and, for a harness division, the pinned harness run once against the mock engine
   (`scripts/mock_engine.py`) through the proxy, in the sandbox (no GPU).

## 2.3 Starting
1. Start it: `python3 -I scripts/bench.py start`. The first line printed is
   `division: <division>, environment: <env>, run: results/<division>/<env>/<RUN_ID>`. It refuses with no `run_id`,
   no matching environment, a division that is not active, nothing chosen, another run's supervisor alive, or something
   missing (without `fetch`). Starting the same `run_id` again resumes the run (finished cases are skipped); while its
   supervisor is alive it only shows the status. What was started is kept in `run-status/current-run.json`, so
   `status` and `stop` need no arguments. The supervisor (`scripts/supervise.py`), in order:
   - with `fetch`: `scripts/overnight.py` (fetch the models → convert NVFP4-QAD → delete the conversion source → fetch
     the last model) when models are missing, and waits until every download has ended
   - Strata's run configs for the models fetched (`scripts/install_configs.py`), then preflight
   - `scripts/stats_watch.py` beside the run (at each session start, launch, case end, failure and Tier change, and
     every 5 minutes, a snapshot of the process list, CPU, memory, PSI, disk IO, temperatures and GPU)
   - `scripts/bench_runner.py` Tier by Tier in the order of `tiers`, for the models and cases chosen, with the case
     lists and charts rebuilt after each Tier (`preview/`), then `scripts/verify_run.py`
   - the healthcheck every `watch_interval_s`; the restarts of 1.6; a notification at the end
2. Check that the STATUS printed right after starting is RUNNING or WAITING.
3. With the user's agreement from 2.2, register the hourly watch task with the agent's own scheduler, named or
   described as `strata-jbench-watch`. What matters is where it reports: **in the conversation that started the run,
   where the user talks with the agent**, as the agent would if the user asked. A scheduler whose runs each open a
   conversation of their own (a background session, a separate thread) leaves its reports where the user does not
   look, and a notification alone is easy to miss; neither counts as reporting. Before starting (2.2), tell the user
   which scheduler will be used, where its reports will appear and what it does not survive (a scheduler living in
   the conversation is usually gone when the agent's app quits or the PC reboots: after a reboot the user comes back
   to that conversation, and the agent resumes with `bench.py start` and registers the task again). If the agent has
   no scheduler that reports in the conversation, say so and agree with the user on another way (they ask in the
   conversation from time to time; the supervisor's desktop notification at the end).
   - **Claude Code** (CLI and desktop app): CronCreate in the session that started the run (the same as `/loop`; the
     prompt comes back into that session every hour while it is idle). Recurring jobs live only in that session's
     memory and expire after 7 days; CronList shows them and CronDelete removes them (2.6). Not the desktop app's
     "Scheduled" tasks: each of their runs is a session of its own, so the report stays there (the end of a
     run on 2026-11-07 was reported only in one of those).
   - **Other agents** (Codex, Cursor, Gemini CLI and so on): use their in-conversation scheduler if they have one, and
     check before starting where its runs report; a scheduled or background task that runs as a separate thread or
     job is the same case as Claude Code's "Scheduled" tasks.
   Its prompt must be self-contained, for example:
   > In <repository path>, run `python3 -I scripts/bench.py status --json`. RUNNING or WAITING: report nothing
   > unless `warn` is set. DONE: report the end (the run, the cases done and failed, `run-status/STATUS.md`) and
   > delete this task. STOPPED: say so and delete this task (the user resumes with `bench.py start`, which registers
   > it again). FAILED or STUCK, or `supervisor_pid` null while not DONE or STOPPED: follow AGENTS.md 2.4 (read the
   > logs, find the cause; after a reboot or a passing problem, `python3 -I scripts/bench.py start` resumes it, and
   > the task stays); when it cannot be resumed without the user (the cause is unknown, or the fix is in section 3),
   > report what was found and delete this task. Never act on section 3 without the user's policy; report what was
   > found and done.
   If one is left over from an earlier run, check that it is enabled and that its prompt is still right. If it cannot
   be registered, do not report the run as started: tell the user why and have them decide on another way (the
   supervisor alone, without recovery after a reboot).
4. Report the expected end time (`bench.py plan`) and what happens if something goes wrong (the supervisor's restarts
   and notifications, recovery by the watch task).

To stop: `python3 -I scripts/bench.py stop` (the supervisor, its children and the engine it launched). If the run will
not be resumed, delete the watch task as in 2.6.

## 2.4 When something goes wrong (healthcheck FAILED / STUCK)
Read the logs and find the cause before acting. Never restart again and again without knowing why.

| Stage | Look at | Safe recovery |
| --- | --- | --- |
| acquire/download* | `downloads/overnight.log`, `downloads/overnight.out`, the end of `downloads/download.log`, `downloads/status.json` | For a passing network problem, `scripts/bench.py start` resumes (it goes on from where it stopped) |
| acquire/qad | `downloads/qad-prepare.log` | Fix the cause, then resume; finished steps are skipped by their `.done` marks |
| bench | `results/<division>/<env>/<RUN_ID>/queue.log` (the supervisor's lines, with its restarts, and the runner's output), its `runner.log`, the matching `sessions/*/start-*/launch.txt` and `engine.log` | Fix the cause, then `scripts/bench.py start`; finished cases are skipped |
| supervisor gone (status FAILED, `supervisor_pid` null) | the end of `queue.log`, `supervise.err` in the run, `journalctl --user -b` for an OOM kill; a reboot or a logout | `scripts/bench.py start` resumes it |
| bench preflight | `run-status/preflight.json` | Fix the failing items |

After fixing a code or environment problem, run one affected case under a `test-` RUN_ID before resuming.

## 2.6 When the run ends
The watch task keeps firing every hour after the queue ends, so it deletes itself as soon as it finds the run over,
whether the run succeeded or not; no one is asked first (the user agreed to this when it was registered, 2.2).
1. The run is over when STATUS is DONE or STOPPED, or FAILED in a way the task cannot resume by itself (2.4: the
   cause is unknown, or its fix is in section 3). A FAILED run the task resumes after a reboot or a passing problem is
   not over: the task stays.
2. The task reports the end (or what it found) and then deletes itself with the scheduler it was registered with, in
   the conversation that registered it (Claude Code: CronList for its id, then CronDelete). If it cannot, it asks the
   user to. A run started again later registers a new task (2.3).
3. Check with the scheduler's list that no watch task is left.
