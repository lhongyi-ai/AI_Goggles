#!/bin/zsh

set -euo pipefail

LABEL="com.stanley.ai-glasses.auto-convert"
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
SCRIPT_PATH="$ROOT_DIR/scripts/auto_convert_clips.sh"
PLIST_PATH="$HOME/Library/LaunchAgents/${LABEL}.plist"
LOG_DIR="$HOME/Library/Logs/AI_Goggles"
LOG_FILE="$LOG_DIR/auto_convert.log"
ERROR_LOG_FILE="$LOG_DIR/auto_convert_error.log"
OUTPUT_DIR="${AI_GOGGLES_SD_OUTPUT_DIR:-$HOME/Movies/AI_Goggles/SD_Recordings}"
USER_DOMAIN="gui/$(id -u)"

yes_no() {
  if "$@"; then
    print -r -- "yes"
  else
    print -r -- "no"
  fi
}

tool_exists() {
  local tool_name="$1"
  command -v "$tool_name" >/dev/null 2>&1 ||
    test -x "/opt/homebrew/bin/$tool_name" ||
    test -x "/usr/local/bin/$tool_name"
}

launch_agent_loaded() {
  launchctl print "$USER_DOMAIN/$LABEL" >/dev/null 2>&1
}

print -r -- "LaunchAgent plist exists: $(yes_no test -f "$PLIST_PATH")"
print -r -- "LaunchAgent loaded: $(yes_no launch_agent_loaded)"
print -r -- "Auto-convert script exists: $(yes_no test -x "$SCRIPT_PATH")"
print -r -- "ffmpeg installed: $(yes_no tool_exists ffmpeg)"
print -r -- "ffprobe installed: $(yes_no tool_exists ffprobe)"
print -r -- "Output directory exists: $(yes_no test -d "$OUTPUT_DIR")"
print -r -- "Output directory: $OUTPUT_DIR"
print -r -- "Log file: $LOG_FILE"
print -r -- "Error log file: $ERROR_LOG_FILE"

if ! launchctl print "$USER_DOMAIN/$LABEL" >/dev/null 2>&1; then
  print -r -- ""
  print -r -- "Repair command:"
  print -r -- "  ./scripts/install_auto_convert_launch_agent.sh"
fi

print -r -- ""
print -r -- "Latest log entries:"
if [[ -f "$LOG_FILE" ]]; then
  tail -n 20 "$LOG_FILE"
else
  print -r -- "(no log yet)"
fi

print -r -- ""
print -r -- "Latest error log entries:"
if [[ -f "$ERROR_LOG_FILE" ]]; then
  tail -n 20 "$ERROR_LOG_FILE"
else
  print -r -- "(no error log yet)"
fi
