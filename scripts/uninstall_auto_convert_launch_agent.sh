#!/bin/zsh

set -euo pipefail

LABEL="com.stanley.ai-glasses.auto-convert"
PLIST_PATH="$HOME/Library/LaunchAgents/${LABEL}.plist"
USER_DOMAIN="gui/$(id -u)"

if launchctl print "$USER_DOMAIN/$LABEL" >/dev/null 2>&1; then
  print -r -- "Unloading LaunchAgent..."
  launchctl bootout "$USER_DOMAIN" "$PLIST_PATH" 2>/dev/null || true
else
  print -r -- "LaunchAgent is not loaded."
fi

if [[ -f "$PLIST_PATH" ]]; then
  rm "$PLIST_PATH"
  print -r -- "Deleted plist: $PLIST_PATH"
else
  print -r -- "No plist to delete: $PLIST_PATH"
fi

print -r -- "Uninstalled auto-convert LaunchAgent."
print -r -- "Recordings, MP4 files, and logs were not deleted."
