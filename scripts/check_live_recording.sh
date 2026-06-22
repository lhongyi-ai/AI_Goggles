#!/bin/zsh

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PID_FILE="$ROOT_DIR/recordings/live/live_recording.pid"
CONFIG_FILE="$ROOT_DIR/recordings/live/last_stream_url.txt"

if [[ -f "$PID_FILE" ]]; then
  pid="$(cat "$PID_FILE")"
  if [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null; then
    echo "Live recording is running with PID $pid."
  else
    echo "PID file exists but process is not running."
  fi
else
  echo "No live recording is running."
fi

if [[ -f "$CONFIG_FILE" ]]; then
  stream_url="$(cat "$CONFIG_FILE")"
  base_url="${stream_url%/stream}"
  echo "Last stream URL: $stream_url"
  echo "Checking XIAO status..."
  curl --max-time 3 --silent --show-error "$base_url/status" || true
  echo
fi
