#!/bin/zsh

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PID_FILE="$ROOT_DIR/recordings/live/live_recording.pid"

if [[ ! -f "$PID_FILE" ]]; then
  echo "No live recording PID file found."
  exit 0
fi

pid="$(cat "$PID_FILE")"
if [[ -z "$pid" ]] || ! kill -0 "$pid" 2>/dev/null; then
  echo "Live recording process is not running."
  rm -f "$PID_FILE"
  exit 0
fi

echo "Stopping live recording PID $pid..."
kill -INT "$pid"
sleep 2

if kill -0 "$pid" 2>/dev/null; then
  echo "Process did not stop after SIGINT; sending SIGTERM."
  kill -TERM "$pid"
fi
