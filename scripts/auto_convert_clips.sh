#!/bin/zsh

set -euo pipefail

MARKER_NAME="AI_GOGGLES.marker"
MARKER_CONTENT="AI_GOGGLES_SD_V1"
DEFAULT_FPS="10"
QUIET_SECONDS="${AI_GOGGLES_QUIET_SECONDS:-5}"
STALE_LOCK_SECONDS=$((6 * 60 * 60))
GLOBAL_LOCK_DIR="/tmp/ai-goggles-auto-convert.lock"
OUTPUT_DIR="${AI_GOGGLES_SD_OUTPUT_DIR:-$HOME/Movies/AI_Goggles/SD_Recordings}"
LOG_DIR="$HOME/Library/Logs/AI_Goggles"
LOG_FILE="$LOG_DIR/auto_convert.log"
ERROR_LOG_FILE="$LOG_DIR/auto_convert_error.log"

mkdir -p "$LOG_DIR" "$OUTPUT_DIR"

log() {
  local line="[$(date '+%Y-%m-%d %H:%M:%S')] $*"
  print -r -- "$line"
  { print -r -- "$line" >> "$LOG_FILE" } 2>/dev/null || true
}

log_error() {
  local line="[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: $*"
  print -r -- "$line" >&2
  { print -r -- "$line" >> "$LOG_FILE" } 2>/dev/null || true
  { print -r -- "$line" >> "$ERROR_LOG_FILE" } 2>/dev/null || true
}

log_note() {
  local line="[$(date '+%Y-%m-%d %H:%M:%S')] $*"
  print -r -- "$line" >&2
  { print -r -- "$line" >> "$LOG_FILE" } 2>/dev/null || true
}

find_tool() {
  local tool_name="$1"
  local candidate

  for candidate in "/opt/homebrew/bin/$tool_name" "/usr/local/bin/$tool_name" "/usr/bin/$tool_name"; do
    if [[ -x "$candidate" ]]; then
      print -r -- "$candidate"
      return 0
    fi
  done

  if command -v "$tool_name" >/dev/null 2>&1; then
    command -v "$tool_name"
    return 0
  fi

  return 1
}

FFMPEG="$(find_tool ffmpeg || true)"
FFPROBE="$(find_tool ffprobe || true)"

if [[ -z "$FFMPEG" ]]; then
  log_error "ffmpeg not found. Install it with: brew install ffmpeg"
  exit 0
fi

if [[ -z "$FFPROBE" ]]; then
  log_error "ffprobe not found. Install it with: brew install ffmpeg"
  exit 0
fi

if ! mkdir "$GLOBAL_LOCK_DIR" 2>/dev/null; then
  log "Another auto-convert instance is already running; exiting."
  exit 0
fi

cleanup_global_lock() {
  if [[ "$GLOBAL_LOCK_DIR" == /tmp/ai-goggles-auto-convert.lock && -d "$GLOBAL_LOCK_DIR" ]]; then
    rmdir "$GLOBAL_LOCK_DIR" 2>/dev/null || true
  fi
}
trap cleanup_global_lock EXIT INT TERM

sanitize_name() {
  local raw="$1"
  local safe
  safe="$(print -r -- "$raw" | tr -c 'A-Za-z0-9._-' '_')"
  safe="${safe##_}"
  safe="${safe%%_}"
  if [[ -z "$safe" ]]; then
    safe="AI_GOGGLES"
  fi
  print -r -- "$safe"
}

read_info_value() {
  local info_file="$1"
  local key="$2"

  if [[ ! -f "$info_file" ]]; then
    return 1
  fi

  awk -F, -v k="$key" '
    $1 == k {
      gsub(/\r/, "", $2)
      gsub(/^[ \t]+|[ \t]+$/, "", $2)
      print $2
      exit
    }
  ' "$info_file"
}

fps_for_info_file() {
  local info_file="$1"
  local fps=""

  fps="$(read_info_value "$info_file" "actual_fps" || true)"
  if [[ -z "$fps" ]]; then
    fps="$(read_info_value "$info_file" "actual_average_fps" || true)"
  fi
  if [[ -z "$fps" ]]; then
    fps="$(read_info_value "$info_file" "target_fps" || true)"
    if [[ -n "$fps" ]]; then
      log_note "Using target_fps from metadata because actual FPS was missing: $fps"
    fi
  fi
  if [[ -z "$fps" ]]; then
    fps="$DEFAULT_FPS"
    log_note "Metadata FPS missing; falling back to ${DEFAULT_FPS} FPS for $info_file"
  fi

  print -r -- "$fps"
}

file_age_seconds() {
  local file_path="$1"
  local mtime now
  mtime="$(stat -f '%m' "$file_path")"
  now="$(date '+%s')"
  print -r -- $((now - mtime))
}

validate_mp4() {
  local mp4_file="$1"
  local codec width height duration

  if [[ ! -s "$mp4_file" ]]; then
    return 1
  fi

  codec="$("$FFPROBE" -v error -select_streams v:0 -show_entries stream=codec_name -of default=noprint_wrappers=1:nokey=1 "$mp4_file" 2>/dev/null | head -n 1 || true)"
  width="$("$FFPROBE" -v error -select_streams v:0 -show_entries stream=width -of default=noprint_wrappers=1:nokey=1 "$mp4_file" 2>/dev/null | head -n 1 || true)"
  height="$("$FFPROBE" -v error -select_streams v:0 -show_entries stream=height -of default=noprint_wrappers=1:nokey=1 "$mp4_file" 2>/dev/null | head -n 1 || true)"
  duration="$("$FFPROBE" -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$mp4_file" 2>/dev/null | head -n 1 || true)"

  [[ "$codec" == "h264" ]] || return 1
  [[ "$width" =~ '^[0-9]+$' ]] || return 1
  [[ "$height" =~ '^[0-9]+$' ]] || return 1
  awk -v d="$duration" 'BEGIN { exit !(d + 0 > 0) }'
}

handle_existing_output() {
  local final_output="$1"
  local timestamp invalid_output

  if [[ ! -e "$final_output" ]]; then
    return 0
  fi

  if validate_mp4 "$final_output"; then
    log "Skipping existing valid MP4: $final_output"
    return 1
  fi

  timestamp="$(date '+%Y%m%d_%H%M%S')"
  invalid_output="${final_output:r}.invalid_${timestamp}.mp4"
  log_error "Existing MP4 failed validation; renaming to $invalid_output"
  mv "$final_output" "$invalid_output"
  return 0
}

acquire_clip_lock() {
  local lock_dir="$1"
  local age

  if mkdir "$lock_dir" 2>/dev/null; then
    return 0
  fi

  if [[ -d "$lock_dir" ]]; then
    age="$(file_age_seconds "$lock_dir")"
    if (( age > STALE_LOCK_SECONDS )); then
      log "Removing stale clip lock: $lock_dir"
      rmdir "$lock_dir" 2>/dev/null || true
      mkdir "$lock_dir" 2>/dev/null && return 0
    fi
  fi

  log "Skipping active lock: $lock_dir"
  return 1
}

release_clip_lock() {
  local lock_dir="$1"
  if [[ -n "$lock_dir" && -d "$lock_dir" ]]; then
    rmdir "$lock_dir" 2>/dev/null || true
  fi
}

mark_temp_failed() {
  local temp_output="$1"
  local failed_output
  if [[ -e "$temp_output" ]]; then
    failed_output="${temp_output:r}.failed_$(date '+%Y%m%d_%H%M%S').mp4"
    mv "$temp_output" "$failed_output" 2>/dev/null || true
    log_error "Kept failed temporary output as $failed_output"
  fi
}

validate_jpeg_sequence() {
  local clip_dir="$1"
  local expected=1
  local frame base frame_number
  local frame_count=0

  if [[ ! -f "$clip_dir/frame_0001.jpg" ]]; then
    log "Skipping JPEG sequence without frame_0001.jpg: $clip_dir"
    return 1
  fi

  while IFS= read -r frame; do
    if [[ ! -s "$frame" ]]; then
      log_error "Skipping JPEG sequence because an empty frame exists: $frame"
      return 1
    fi

    base="${frame:t}"
    if [[ ! "$base" =~ '^frame_([0-9]{4})\.jpg$' ]]; then
      log_error "Unexpected frame filename: $base"
      return 1
    fi

    frame_number=$((10#${match[1]}))
    if (( frame_number != expected )); then
      log_error "Skipping JPEG sequence with non-continuous numbering in $clip_dir; expected frame $(printf '%04d' "$expected"), found $base"
      return 1
    fi

    expected=$((expected + 1))
    frame_count=$((frame_count + 1))
  done < <(find "$clip_dir" -maxdepth 1 -type f -name 'frame_[0-9][0-9][0-9][0-9].jpg' -print | sort)

  if (( frame_count < 2 )); then
    log "Skipping JPEG sequence with fewer than 2 frames: $clip_dir"
    return 1
  fi

  return 0
}

convert_mjpeg() {
  local volume="$1"
  local volume_prefix="$2"
  local input="$3"
  local clip_name="${input:t:r}"
  local info_file="$volume/${clip_name}_info.csv"
  local fps final_output temp_output lock_dir age result

  if [[ ! -f "$input" ]]; then
    log_error "MJPEG input disappeared before conversion: $input"
    return 1
  fi

  age="$(file_age_seconds "$input")"
  if (( age < QUIET_SECONDS )); then
    log "Skipping recently modified MJPEG: $input"
    return 0
  fi

  fps="$(fps_for_info_file "$info_file")"
  final_output="$OUTPUT_DIR/${volume_prefix}_sd_${clip_name}.mp4"
  temp_output="$OUTPUT_DIR/.${volume_prefix}_sd_${clip_name}.partial.mp4"
  lock_dir="$OUTPUT_DIR/.${volume_prefix}_sd_${clip_name}.converting.lock"

  handle_existing_output "$final_output" || return 0
  acquire_clip_lock "$lock_dir" || return 0
  rm -f "$temp_output"

  log "Found ${clip_name}.mjpeg"
  log "Using FPS: $fps"
  log "Converting MJPEG: $input -> $final_output"

  set +e
  if { : >> "$LOG_FILE"; } 2>/dev/null && { : >> "$ERROR_LOG_FILE"; } 2>/dev/null; then
    "$FFMPEG" -hide_banner -loglevel warning -y \
      -f mjpeg \
      -framerate "$fps" \
      -i "$input" \
      -c:v libx264 \
      -preset veryfast \
      -pix_fmt yuv420p \
      -movflags +faststart \
      "$temp_output" >> "$LOG_FILE" 2>> "$ERROR_LOG_FILE"
  else
    "$FFMPEG" -hide_banner -loglevel warning -y \
      -f mjpeg \
      -framerate "$fps" \
      -i "$input" \
      -c:v libx264 \
      -preset veryfast \
      -pix_fmt yuv420p \
      -movflags +faststart \
      "$temp_output"
  fi
  result=$?
  set -e

  if (( result != 0 )); then
    log_error "ffmpeg failed for $input with exit code $result"
    mark_temp_failed "$temp_output"
    release_clip_lock "$lock_dir"
    return 1
  fi

  if validate_mp4 "$temp_output"; then
    log "ffprobe validation passed"
    mv "$temp_output" "$final_output"
    log "Created: $final_output"
  else
    log_error "ffprobe validation failed for $temp_output"
    mark_temp_failed "$temp_output"
    release_clip_lock "$lock_dir"
    return 1
  fi

  release_clip_lock "$lock_dir"
  return 0
}

convert_jpeg_sequence() {
  local volume="$1"
  local volume_prefix="$2"
  local clip_dir="$3"
  local clip_name="${clip_dir:t}"
  local info_file="$clip_dir/clip_info.csv"
  local fps final_output temp_output lock_dir result

  validate_jpeg_sequence "$clip_dir" || return 0

  fps="$(fps_for_info_file "$info_file")"
  final_output="$OUTPUT_DIR/${volume_prefix}_sd_${clip_name}.mp4"
  temp_output="$OUTPUT_DIR/.${volume_prefix}_sd_${clip_name}.partial.mp4"
  lock_dir="$OUTPUT_DIR/.${volume_prefix}_sd_${clip_name}.converting.lock"

  handle_existing_output "$final_output" || return 0
  acquire_clip_lock "$lock_dir" || return 0
  rm -f "$temp_output"

  log "Found JPEG sequence: $clip_dir"
  log "Using FPS: $fps"
  log "Converting JPEG sequence: $clip_dir -> $final_output"

  set +e
  if { : >> "$LOG_FILE"; } 2>/dev/null && { : >> "$ERROR_LOG_FILE"; } 2>/dev/null; then
    "$FFMPEG" -hide_banner -loglevel warning -y \
      -framerate "$fps" \
      -i "$clip_dir/frame_%04d.jpg" \
      -c:v libx264 \
      -preset veryfast \
      -pix_fmt yuv420p \
      -movflags +faststart \
      "$temp_output" >> "$LOG_FILE" 2>> "$ERROR_LOG_FILE"
  else
    "$FFMPEG" -hide_banner -loglevel warning -y \
      -framerate "$fps" \
      -i "$clip_dir/frame_%04d.jpg" \
      -c:v libx264 \
      -preset veryfast \
      -pix_fmt yuv420p \
      -movflags +faststart \
      "$temp_output"
  fi
  result=$?
  set -e

  if (( result != 0 )); then
    log_error "ffmpeg failed for $clip_dir with exit code $result"
    mark_temp_failed "$temp_output"
    release_clip_lock "$lock_dir"
    return 1
  fi

  if validate_mp4 "$temp_output"; then
    log "ffprobe validation passed"
    mv "$temp_output" "$final_output"
    log "Created: $final_output"
  else
    log_error "ffprobe validation failed for $temp_output"
    mark_temp_failed "$temp_output"
    release_clip_lock "$lock_dir"
    return 1
  fi

  release_clip_lock "$lock_dir"
  return 0
}

detect_ai_goggles_volume() {
  local volume="$1"

  if [[ -f "$volume/$MARKER_NAME" ]]; then
    log "Detected by marker: $volume"
    return 0
  fi

  if find "$volume" -maxdepth 1 -type f -name 'clip_[0-9][0-9][0-9][0-9].mjpeg' -print -quit 2>/dev/null | grep -q .; then
    log "Detected by legacy clip structure: $volume"
    return 0
  fi

  if find "$volume" -maxdepth 1 -type d -name 'clip_[0-9][0-9][0-9][0-9]' -exec test -f '{}/frame_0001.jpg' ';' -print -quit 2>/dev/null | grep -q .; then
    log "Detected by legacy clip structure: $volume"
    return 0
  fi

  log "Skipping unrelated volume: $volume"
  return 1
}

process_volume() {
  local volume="$1"
  local volume_name volume_prefix converted_before converted_after
  local mjpeg_file clip_dir

  if [[ ! -d "$volume" ]]; then
    log "Skipping non-directory volume path: $volume"
    return 0
  fi

  detect_ai_goggles_volume "$volume" || return 0

  volume_name="${volume:t}"
  volume_prefix="$(sanitize_name "$volume_name")"
  converted_before="$(find "$OUTPUT_DIR" -maxdepth 1 -type f -name "${volume_prefix}_sd_clip_*.mp4" | wc -l | tr -d ' ')"

  for mjpeg_file in "$volume"/clip_[0-9][0-9][0-9][0-9].mjpeg(N.); do
    convert_mjpeg "$volume" "$volume_prefix" "$mjpeg_file" || true
  done

  for clip_dir in "$volume"/clip_[0-9][0-9][0-9][0-9](N/); do
    convert_jpeg_sequence "$volume" "$volume_prefix" "$clip_dir" || true
  done

  converted_after="$(find "$OUTPUT_DIR" -maxdepth 1 -type f -name "${volume_prefix}_sd_clip_*.mp4" | wc -l | tr -d ' ')"
  if [[ "$converted_before" == "$converted_after" ]]; then
    log "No new clips found for $volume"
  fi
}

main() {
  local volumes=()
  local volume

  log "StartOnMount trigger received"
  sleep 2

  if (( $# > 0 )); then
    volumes=("$@")
    log "Scanning specified volume path(s): $*"
  else
    volumes=(/Volumes/*(N/))
    log "Scanning /Volumes"
  fi

  if (( ${#volumes[@]} == 0 )); then
    log "No volumes found to scan."
    return 0
  fi

  for volume in "${volumes[@]}"; do
    process_volume "$volume"
  done
}

main "$@"
