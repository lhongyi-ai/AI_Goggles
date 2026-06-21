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

read_info_value() {
  local info_file="$1"
  local key="$2"

  if [[ ! -f "$info_file" ]]; then
    return 1
  fi

  awk -F, -v k="$key" '$1 == k { print $2; exit }' "$info_file"
}

for clip_dir in /Volumes/*/clip_*(N/); do
  first_frame="$clip_dir/frame_0001.jpg"

  if [[ ! -f "$first_frame" ]]; then
    continue
  fi

  clip_name="${clip_dir:t}"
  output_file="$clip_dir/${clip_name}.mp4"
  lock_file="$clip_dir/.${clip_name}.converting"
  info_file="$clip_dir/clip_info.csv"

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

  actual_fps="$(read_info_value "$info_file" "actual_average_fps" || true)"
  if [[ -z "$actual_fps" ]]; then
    actual_fps="$FRAME_RATE"
  fi

  log "Converting $clip_dir ($frame_count frames) at ${actual_fps} fps -> $output_file"
  touch "$lock_file"

  (
    cd "$clip_dir" &&
      "$FFMPEG" -y \
        -framerate "$actual_fps" \
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

for mjpeg_file in /Volumes/*/clip_*.mjpeg(N.); do
  clip_name="${mjpeg_file:t:r}"
  volume_dir="${mjpeg_file:h}"
  output_file="$volume_dir/${clip_name}.mp4"
  lock_file="$volume_dir/.${clip_name}.converting"
  info_file="$volume_dir/${clip_name}_info.csv"

  if [[ -f "$output_file" || -f "$lock_file" ]]; then
    continue
  fi

  newest_mtime=$(stat -f '%m' "$mjpeg_file")
  now=$(date '+%s')
  age=$(( now - newest_mtime ))

  if (( age < QUIET_SECONDS )); then
    continue
  fi

  actual_fps="$(read_info_value "$info_file" "actual_average_fps" || true)"
  if [[ -z "$actual_fps" ]]; then
    actual_fps="$FRAME_RATE"
  fi

  log "Converting $mjpeg_file at ${actual_fps} fps -> $output_file"
  touch "$lock_file"

  "$FFMPEG" -y \
    -framerate "$actual_fps" \
    -f mjpeg \
    -i "$mjpeg_file" \
    -c:v libx264 \
    -pix_fmt yuv420p \
    "$output_file" >> "$LOG_FILE" 2>&1

  result=$?
  rm -f "$lock_file"

  if (( result == 0 )); then
    log "Done: $output_file"
  else
    log "Failed converting $mjpeg_file with exit code $result"
    rm -f "$output_file"
  fi
done
