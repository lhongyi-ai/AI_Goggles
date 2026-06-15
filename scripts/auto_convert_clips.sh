#!/bin/zsh

set -u

FFMPEG="/opt/homebrew/bin/ffmpeg"
LOG_FILE="$HOME/Library/Logs/ai-glasses-auto-convert.log"
FRAME_RATE="10"
MIN_FRAME_COUNT="2"
QUIET_SECONDS="5"

log() {
  mkdir -p "$HOME/Library/Logs"
  print -r -- "[$(date '+%Y-%m-%d %H:%M:%S')] $*" >> "$LOG_FILE"
}

if [[ ! -x "$FFMPEG" ]]; then
  log "ffmpeg not found at $FFMPEG"
  exit 0
fi

for clip_dir in /Volumes/*/clip_*(N/); do
  first_frame="$clip_dir/frame_0001.jpg"

  if [[ ! -f "$first_frame" ]]; then
    continue
  fi

  clip_name="${clip_dir:t}"
  output_file="$clip_dir/${clip_name}.mp4"
  lock_file="$clip_dir/.${clip_name}.converting"

  if [[ -f "$output_file" || -f "$lock_file" ]]; then
    continue
  fi

  frame_count=$(find "$clip_dir" -maxdepth 1 -name 'frame_*.jpg' -type f | wc -l | tr -d ' ')
  if (( frame_count < MIN_FRAME_COUNT )); then
    continue
  fi

  newest_frame_mtime=$(find "$clip_dir" -maxdepth 1 -name 'frame_*.jpg' -type f -exec stat -f '%m' {} \; | sort -nr | head -n 1)
  now=$(date '+%s')
  age=$(( now - newest_frame_mtime ))

  if (( age < QUIET_SECONDS )); then
    continue
  fi

  log "Converting $clip_dir ($frame_count frames) -> $output_file"
  touch "$lock_file"

  (
    cd "$clip_dir" &&
      "$FFMPEG" -y \
        -framerate "$FRAME_RATE" \
        -i frame_%04d.jpg \
        -c:v libx264 \
        -pix_fmt yuv420p \
        "${clip_name}.mp4"
  ) >> "$LOG_FILE" 2>&1

  result=$?
  rm -f "$lock_file"

  if (( result == 0 )); then
    log "Done: $output_file"
  else
    log "Failed converting $clip_dir with exit code $result"
    rm -f "$output_file"
  fi
done
