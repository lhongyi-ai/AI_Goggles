# macOS SD Auto Convert

This workflow converts AI Goggles SD recordings to H.264 MP4 automatically when the SD card is mounted.

```text
SD card inserted
  -> macOS LaunchAgent StartOnMount
  -> scripts/auto_convert_clips.sh
  -> scan AI Goggles volumes only
  -> convert new clips
  -> write MP4 files to ~/Movies/AI_Goggles/SD_Recordings/
```

The script does not delete MJPEG files, JPEG frames, or metadata on the SD card.

## First-Time Install

Run once from the repository:

```bash
chmod +x scripts/*.sh
./scripts/install_auto_convert_launch_agent.sh
```

The installer writes:

```text
~/Library/LaunchAgents/com.stanley.ai-glasses.auto-convert.plist
```

The repository only stores a template at:

```text
macos/com.stanley.ai-glasses.auto-convert.plist.template
```

## First-Time SD Card Preparation

Run once per AI Goggles SD card:

```bash
./scripts/prepare_ai_goggles_sd.sh "/Volumes/SD_CARD_NAME"
```

This creates:

```text
/Volumes/SD_CARD_NAME/AI_GOGGLES.marker
```

with:

```text
AI_GOGGLES_SD_V1
```

It does not format the SD card and does not delete existing files.

## Normal Use

1. Record on the XIAO ESP32S3 Sense.
2. Remove the SD card.
3. Insert it into the Mac.
4. Wait for the background conversion.
5. Open:

```text
~/Movies/AI_Goggles/SD_Recordings/
```

Normal use does not require opening Terminal.

## Output Names

MP4 files are written to the Mac, not back to the SD card:

```text
~/Movies/AI_Goggles/SD_Recordings/VOLUME_sd_clip_0004.mp4
```

The volume label is included to avoid collisions between cards with the same clip number.

Examples:

```text
AI_GOGGLES_sd_clip_0004.mp4
NO_NAME_sd_clip_0004.mp4
```

Temporary files are written as hidden partial MP4s and renamed only after ffprobe validation passes:

```text
.AI_GOGGLES_sd_clip_0004.partial.mp4
```

## SD Card Detection

`StartOnMount` can fire for any disk, USB drive, DMG, or SD card. The script only processes volumes that match one of these rules:

- Preferred: root contains `AI_GOGGLES.marker`
- Legacy fallback: root contains `clip_XXXX.mjpeg`
- Legacy fallback: root contains `clip_XXXX/frame_0001.jpg`

Unrelated volumes are logged and skipped.

## Check Status

```bash
./scripts/check_auto_convert_status.sh
```

It reports whether the LaunchAgent is installed and loaded, whether ffmpeg/ffprobe are installed, and shows recent logs.

## Logs

Main conversion log:

```bash
tail -f ~/Library/Logs/AI_Goggles/auto_convert.log
```

Error log:

```bash
tail -f ~/Library/Logs/AI_Goggles/auto_convert_error.log
```

LaunchAgent stdout/stderr:

```text
~/Library/Logs/AI_Goggles/auto_convert.launchd.out.log
~/Library/Logs/AI_Goggles/auto_convert.launchd.err.log
```

## Manual Debug

Scan all mounted volumes:

```bash
./scripts/auto_convert_clips.sh
```

Scan one volume, including names with spaces:

```bash
./scripts/auto_convert_clips.sh "/Volumes/NO NAME"
```

Manually trigger launchd:

```bash
launchctl kickstart -k gui/$(id -u)/com.stanley.ai-glasses.auto-convert
```

Manual commands are for debugging. Normal use is insert SD card and wait.

## Uninstall

```bash
./scripts/uninstall_auto_convert_launch_agent.sh
```

This removes the LaunchAgent plist. It does not delete recordings, MP4 files, or logs.

## Reliability Notes

- A global lock prevents overlapping launchd runs.
- Each clip also has its own lock.
- Existing valid MP4 files are skipped.
- Existing invalid MP4 files are renamed to `*.invalid_TIMESTAMP.mp4` and regenerated.
- If conversion fails, no final MP4 is created.
- If the SD card is removed during conversion, ffmpeg should fail and the next insert can retry.
- Do not intentionally pull the SD card during conversion unless you are using disposable test data.

## Requirements

- Mac user must be logged in because this is a per-user LaunchAgent.
- Mac must not be asleep when the SD card is inserted.
- `ffmpeg` and `ffprobe` are required.
- The SD card needs `AI_GOGGLES.marker` or a strict legacy clip layout.
