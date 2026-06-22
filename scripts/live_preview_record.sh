#!/bin/zsh

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
RECORDING_DIR="$ROOT_DIR/recordings/live"
LOG_DIR="$RECORDING_DIR/logs"
PID_FILE="$RECORDING_DIR/live_recording.pid"
CONFIG_FILE="$RECORDING_DIR/last_stream_url.txt"
DEFAULT_FPS="${AI_GOGGLES_LIVE_FPS:-10}"
FFMPEG="${FFMPEG:-/opt/homebrew/bin/ffmpeg}"
FFPLAY="${FFPLAY:-/opt/homebrew/bin/ffplay}"

mkdir -p "$RECORDING_DIR" "$LOG_DIR"

if [[ -f "$PID_FILE" ]]; then
  existing_pid="$(cat "$PID_FILE")"
  if [[ -n "$existing_pid" ]] && kill -0 "$existing_pid" 2>/dev/null; then
    echo "A live recording is already running with PID $existing_pid."
    exit 1
  fi
  rm -f "$PID_FILE"
fi

if [[ ! -x "$FFMPEG" ]]; then
  echo "ffmpeg not found at $FFMPEG. Install it with: brew install ffmpeg"
  exit 1
fi

input="${1:-}"
if [[ -z "$input" && -f "$CONFIG_FILE" ]]; then
  input="$(cat "$CONFIG_FILE")"
fi

if [[ -z "$input" ]]; then
  echo "Usage: $0 XIAO_IP_or_http_stream_url"
  echo "Example: $0 192.168.1.123"
  echo "Example: $0 http://192.168.1.123/stream"
  exit 1
fi

if [[ "$input" == http://* || "$input" == https://* ]]; then
  stream_url="$input"
else
  stream_url="http://$input/stream"
fi

base_url="${stream_url%/stream}"
status_url="$base_url/status"
timestamp="$(date '+%Y-%m-%d_%H%M%S')"
output_file="$RECORDING_DIR/live_${timestamp}.mp4"
log_file="$LOG_DIR/live_${timestamp}.log"
metadata_file="$RECORDING_DIR/live_${timestamp}.txt"

counter=1
while [[ -e "$output_file" ]]; do
  output_file="$RECORDING_DIR/live_${timestamp}_${counter}.mp4"
  metadata_file="$RECORDING_DIR/live_${timestamp}_${counter}.txt"
  log_file="$LOG_DIR/live_${timestamp}_${counter}.log"
  counter=$((counter + 1))
done

echo "$stream_url" > "$CONFIG_FILE"
echo "$$" > "$PID_FILE"

cleanup() {
  rm -f "$PID_FILE"
}
trap cleanup EXIT

echo "Checking XIAO status: $status_url"
if ! curl --max-time 3 --silent --show-error "$status_url" >/dev/null; then
  echo "Could not reach $status_url. Check Wi-Fi, IP address, and the XIAO serial 'w' command."
  exit 1
fi

cat > "$metadata_file" <<EOF
mac_start_time=$(date -u '+%Y-%m-%dT%H:%M:%SZ')
input_url=$stream_url
status_url=$status_url
output_file=$output_file
log_file=$log_file
fps=$DEFAULT_FPS
launcher_pid=$$
EOF

echo "Saving live MP4 to: $output_file"
echo "Log file: $log_file"
echo "Press Ctrl+C to stop cleanly."

if [[ -x "$FFPLAY" && "${AI_GOGGLES_NO_FFPLAY:-0}" != "1" ]]; then
  echo "Preview: ffplay enabled from the same ffmpeg network connection."
  set +e
  "$FFMPEG" -hide_banner -nostdin \
    -f mjpeg \
    -r "$DEFAULT_FPS" \
    -i "$stream_url" \
    -map 0:v -c:v libx264 -preset veryfast -pix_fmt yuv420p -movflags +faststart "$output_file" \
    -map 0:v -c:v copy -f mjpeg pipe:1 \
    2>> "$log_file" | "$FFPLAY" -hide_banner -loglevel warning -fflags nobuffer -flags low_delay -f mjpeg - 2>> "$log_file"
  result=${pipestatus[1]}
  set -e
else
  echo "Preview: ffplay not found or disabled. Open $base_url/ in a browser for preview."
  set +e
  "$FFMPEG" -hide_banner -nostdin \
    -f mjpeg \
    -r "$DEFAULT_FPS" \
    -i "$stream_url" \
    -c:v libx264 \
    -preset veryfast \
    -pix_fmt yuv420p \
    -movflags +faststart \
    "$output_file" >> "$log_file" 2>&1
  result=$?
  set -e
fi

cat >> "$metadata_file" <<EOF
mac_end_time=$(date -u '+%Y-%m-%dT%H:%M:%SZ')
ffmpeg_exit_code=$result
EOF

if (( result == 0 || result == 255 || result == 130 )); then
  echo "Live recording stopped. MP4: $output_file"
  exit 0
fi

echo "Live recording failed with exit code $result. See: $log_file"
exit "$result"
