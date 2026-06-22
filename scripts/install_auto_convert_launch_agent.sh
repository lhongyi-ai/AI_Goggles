#!/bin/zsh

set -euo pipefail

LABEL="com.stanley.ai-glasses.auto-convert"
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
SCRIPT_PATH="$ROOT_DIR/scripts/auto_convert_clips.sh"
TEMPLATE_PATH="$ROOT_DIR/macos/${LABEL}.plist.template"
PLIST_PATH="$HOME/Library/LaunchAgents/${LABEL}.plist"
LOG_DIR="$HOME/Library/Logs/AI_Goggles"
STDOUT_LOG_PATH="$LOG_DIR/auto_convert.launchd.out.log"
STDERR_LOG_PATH="$LOG_DIR/auto_convert.launchd.err.log"
USER_DOMAIN="gui/$(id -u)"

if [[ ! -x "$SCRIPT_PATH" ]]; then
  print -r -- "Auto-convert script is missing or not executable: $SCRIPT_PATH" >&2
  exit 1
fi

if [[ ! -f "$TEMPLATE_PATH" ]]; then
  print -r -- "LaunchAgent template is missing: $TEMPLATE_PATH" >&2
  exit 1
fi

mkdir -p "$HOME/Library/LaunchAgents" "$LOG_DIR"

escape_sed() {
  print -r -- "$1" | sed 's/[\/&]/\\&/g'
}

script_escaped="$(escape_sed "$SCRIPT_PATH")"
stdout_escaped="$(escape_sed "$STDOUT_LOG_PATH")"
stderr_escaped="$(escape_sed "$STDERR_LOG_PATH")"

sed \
  -e "s/__SCRIPT_PATH__/$script_escaped/g" \
  -e "s/__STDOUT_LOG_PATH__/$stdout_escaped/g" \
  -e "s/__STDERR_LOG_PATH__/$stderr_escaped/g" \
  "$TEMPLATE_PATH" > "$PLIST_PATH"

chmod 644 "$PLIST_PATH"
plutil -lint "$PLIST_PATH"

if launchctl print "$USER_DOMAIN/$LABEL" >/dev/null 2>&1; then
  print -r -- "Unloading existing LaunchAgent..."
  launchctl bootout "$USER_DOMAIN" "$PLIST_PATH" 2>/dev/null || true
else
  launchctl bootout "$USER_DOMAIN" "$PLIST_PATH" 2>/dev/null || true
fi

launchctl bootstrap "$USER_DOMAIN" "$PLIST_PATH"
launchctl print "$USER_DOMAIN/$LABEL" || true

print -r -- "Auto-convert LaunchAgent installed."
print -r -- "Insert an AI Goggles SD card to trigger conversion."
print -r -- "Logs:"
print -r -- "  $LOG_DIR/auto_convert.log"
print -r -- "  $LOG_DIR/auto_convert_error.log"
