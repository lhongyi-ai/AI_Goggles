#!/bin/zsh

set -euo pipefail

MARKER_NAME="AI_GOGGLES.marker"
MARKER_CONTENT="AI_GOGGLES_SD_V1"

usage() {
  print -r -- "Usage: $0 \"/Volumes/SD_CARD_NAME\""
}

if (( $# != 1 )); then
  usage
  exit 1
fi

volume="$1"

if [[ "$volume" == "/" || "$volume" == "$HOME" || "$volume" == "/Users" || "$volume" == "/System" ]]; then
  print -r -- "Refusing unsafe target: $volume" >&2
  exit 1
fi

if [[ "$volume" != /Volumes/* ]]; then
  print -r -- "Target must be under /Volumes/: $volume" >&2
  exit 1
fi

if [[ ! -d "$volume" ]]; then
  print -r -- "Volume path does not exist: $volume" >&2
  exit 1
fi

marker_path="$volume/$MARKER_NAME"

if [[ -f "$marker_path" ]]; then
  print -r -- "Marker already exists: $marker_path"
  exit 0
fi

print -r -- "$MARKER_CONTENT" > "$marker_path"
print -r -- "Created AI Goggles marker: $marker_path"
print -r -- "This does not format the SD card and does not delete existing files."
