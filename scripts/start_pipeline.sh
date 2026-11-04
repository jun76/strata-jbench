#!/usr/bin/env bash
# Start the unattended pipeline as systemd user units, so nothing depends on a terminal or a Claude session:
#   strata-jbench-acquire   scripts/overnight.py      downloads, NVFP4-QAD prepare, Q8_0 (skipped when downloads/READY exists)
#   strata-jbench-queue     scripts/overnight_bench.sh waits for READY, preflight, then the benchmark Tiers
#   strata-jbench-health    scripts/healthcheck.py every 15 min: run-status/STATUS.md, alerts on FAILED / STUCK
#   strata-jbench-stats     scripts/stats_watch.py    process list and machine stats at the runner's key points
#
#   RUN_ID=2026-11-05-main STEPS="0 1" scripts/start_pipeline.sh
#   RUN_ID=2026-11-05-redo MODELS="qwen:IQ3_S" scripts/start_pipeline.sh     only these models (family:model,...)
#   scripts/start_pipeline.sh --stop      stop all of them
#
# The run belongs to the environment this hardware matches (scripts/envs.py detect; BENCH_ENV=<id> names it, and it
# must match) and to a division (BENCH_DIVISION, default plain: divisions/README.md): results/<division>/<env>/<RUN_ID>/.
# With no matching environment, or a division that is not measured yet, nothing starts.
#
# Every unit runs the acquisition preflight first; a failing check starts nothing.
set -eu
cd "$(dirname "$0")/.."
ROOT="$(pwd)"
STEPS="${STEPS:-0 1 2 3 4a 4b 4c 4d 5}"
MODELS="${MODELS:-}"

if [ "${1:-}" = "--stop" ]; then
  systemctl --user stop strata-jbench-health.timer strata-jbench-queue strata-jbench-acquire strata-jbench-stats 2>/dev/null || true
  strata launch --stop > /dev/null 2>&1 || true
  echo "stopped"
  exit 0
fi

: "${RUN_ID:?set RUN_ID, e.g. RUN_ID=2026-11-05-main}"
if [ -n "${BENCH_ENV:-}" ]; then
  BENCH_ENV=$(BENCH_ENV="$BENCH_ENV" python3 -I -c 'import sys; sys.path.insert(0, "scripts"); import envs; print(envs.current())') || exit 1
else
  BENCH_ENV=$(python3 -I scripts/envs.py detect) || { echo "no environment matches this hardware: python3 -I scripts/envs.py list"; exit 1; }
fi
BENCH_DIVISION=$(python3 -I -c 'import sys; sys.path.insert(0, "scripts"); import envs; print(envs.division(measuring=True))') || exit 1
echo "division: $BENCH_DIVISION, environment: $BENCH_ENV, run: results/$BENCH_DIVISION/$BENCH_ENV/$RUN_ID"
# What was started last, for the hourly watch task and anyone resuming it (run-status/ is outside Git).
mkdir -p run-status
printf '{"division": "%s", "env": "%s", "run_id": "%s", "steps": "%s", "models": "%s", "run_dir": "results/%s/%s/%s", "started_at": "%s"}\n' \
  "$BENCH_DIVISION" "$BENCH_ENV" "$RUN_ID" "$STEPS" "$MODELS" "$BENCH_DIVISION" "$BENCH_ENV" "$RUN_ID" "$(date -Is)" > run-status/current-run.json
UNIT=(--setenv=PATH="$HOME/.local/bin:/usr/local/bin:/usr/bin:/bin" --setenv=RUN_ID="$RUN_ID" --setenv=STEPS="$STEPS"
      --setenv=MODELS="$MODELS" --setenv=BENCH_ENV="$BENCH_ENV" --setenv=BENCH_DIVISION="$BENCH_DIVISION" --working-directory="$ROOT" --collect)

running() { systemctl --user is-active --quiet "$1"; }

if [ ! -f downloads/READY ]; then
  python3 scripts/preflight.py --phase acquire
  if running strata-jbench-acquire; then
    echo "acquire: already running"
  elif pid=$(python3 -c "import json;print(json.load(open('downloads/overnight-state.json'))['pid'])" 2>/dev/null) \
       && kill -0 "$pid" 2>/dev/null; then
    echo "acquire: already running outside systemd (pid $pid)"
  else
    systemd-run --user --unit=strata-jbench-acquire "${UNIT[@]}" .venv-hf/bin/python -u scripts/overnight.py
  fi
fi

if running strata-jbench-queue; then
  echo "queue: already running"
else
  systemd-run --user --unit=strata-jbench-queue "${UNIT[@]}" bash scripts/overnight_bench.sh
fi

if running strata-jbench-stats; then
  echo "stats: already running"
else
  systemd-run --user --unit=strata-jbench-stats "${UNIT[@]}" python3 -I scripts/stats_watch.py --run-id "$RUN_ID"
fi

# the timer carries the run it checks: one left from an earlier RUN_ID is replaced
if systemctl --user is-active --quiet strata-jbench-health.timer \
   && ! systemctl --user show strata-jbench-health.service -p Environment | grep -q "RUN_ID=$RUN_ID "; then
  systemctl --user stop strata-jbench-health.timer
fi
if ! systemctl --user is-active --quiet strata-jbench-health.timer; then
  systemd-run --user --unit=strata-jbench-health --on-calendar='*:0/15' "${UNIT[@]}" \
    python3 scripts/healthcheck.py --quiet --run-id "$RUN_ID" --env "$BENCH_ENV"
fi
sleep 3
python3 scripts/healthcheck.py --run-id "$RUN_ID" --env "$BENCH_ENV" || true
