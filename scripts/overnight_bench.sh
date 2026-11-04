#!/usr/bin/env bash
# Wait until every model is on disk (downloads/READY from scripts/overnight.py), check that the benchmark can run
# (scripts/preflight.py, including one real launch), then run the benchmark Tiers in order.
# The runner skips finished cases, so starting this again resumes where it stopped.
# Normally started by scripts/start_pipeline.sh as the systemd user unit strata-jbench-queue.
set -u
cd "$(dirname "$0")/.."
: "${RUN_ID:?}" "${BENCH_ENV:?}"   # set by scripts/start_pipeline.sh
STEPS="${STEPS:-0 1 2 3 4a 4b 4c 4d 5}"
MODELS="${MODELS:-}"               # family:model,... to measure only those models (default: all)
BENCH_DIVISION="${BENCH_DIVISION:-plain}"
export BENCH_DIVISION
RUN_DIR="results/$BENCH_DIVISION/$BENCH_ENV/$RUN_ID"
LOG="$RUN_DIR/queue.log"
mkdir -p "$RUN_DIR"
echo $$ > "$RUN_DIR/queue.pid"
echo "$(date -Is) queue start (pid $$), waiting for downloads/READY" >> "$LOG"
until [ -f downloads/READY ]; do
  # the orchestrator's own pid (a pgrep pattern also matched unrelated shells that mention the script name)
  pid=$(python3 -c "import json;print(json.load(open('downloads/overnight-state.json'))['pid'])" 2>/dev/null)
  if ! kill -0 "$pid" 2>/dev/null; then
    echo "$(date -Is) overnight.py is not running and READY is missing; stopping" >> "$LOG"
    exit 1
  fi
  sleep 60
done
python3 -I scripts/build_cases.py >> "$LOG" 2>&1
echo "$(date -Is) preflight" >> "$LOG"
if ! python3 scripts/preflight.py --phase bench --steps "$(echo $STEPS | tr ' ' ',')" >> "$LOG" 2>&1; then
  echo "$(date -Is) preflight failed; not starting (see run-status/preflight.json)" >> "$LOG"
  exit 1
fi
# A runner that dies (an exception, a kill) is logged with its exit code and the queue goes on with the next Tier;
# scripts/healthcheck.py reads these lines and, after the queue, checks that every planned case has a result.
failed=""
for steps in $STEPS; do
  echo "$(date -Is) steps $steps" >> "$LOG"
  python3 scripts/bench_runner.py --run-id "$RUN_ID" --steps "$steps" ${MODELS:+--models "$MODELS"} >> "$LOG" 2>&1
  rc=$?
  echo "$(date -Is) steps $steps: runner exit $rc" >> "$LOG"
  [ "$rc" -ne 0 ] && failed="$failed $steps"
  python3 -I scripts/build_cases.py >> "$LOG" 2>&1
  python3 -I scripts/build_results.py >> "$LOG" 2>&1
done
# the run's records checked against each other (engine timings vs the client's, settings on the engine command line,
# presets the tuner saved): verify.json in the run; a problem is a runner error for the healthcheck
python3 -I scripts/verify_run.py "$BENCH_ENV" "$RUN_ID" >> "$LOG" 2>&1
rc=$?
echo "$(date -Is) steps verify: runner exit $rc" >> "$LOG"
[ "$rc" -ne 0 ] && failed="$failed verify"
if [ -n "$failed" ]; then
  echo "$(date -Is) queue finished with runner errors in steps$failed" >> "$LOG"
  exit 1
fi
echo "$(date -Is) queue finished" >> "$LOG"
