# Live Preview And Dual Recording

This firmware uses one camera capture path:

```text
esp_camera_fb_get()
  -> write the JPEG framebuffer to microSD when recording
  -> send the same JPEG framebuffer to the active Wi-Fi MJPEG preview client
esp_camera_fb_return()
```

The HTTP stream does not call `esp_camera_fb_get()` by itself. This keeps SD recording and live preview synchronized and avoids framebuffer contention.

## Wi-Fi Setup

Copy the example config:

```bash
cp v0_camera_prototype/wifi_config.example.h v0_camera_prototype/wifi_config.h
```

Edit `wifi_config.h`:

```cpp
#define WIFI_SSID "your_wifi_name"
#define WIFI_PASSWORD "your_wifi_password"
```

`wifi_config.h` is ignored by git.

## Serial And BLE Commands

- `p`: take one photo when not recording
- `r`: start the default SD MJPEG recording
- `x`: stop the current recording, flush/close the file, and write CSV metadata
- `j`: start JPEG sequence debug recording
- `m`: start SD MJPEG recording
- `v`: enable or disable the Wi-Fi preview server
- `w`: print Wi-Fi status, IP address, and URLs
- `s`: print local status
- `i`: print system/profile information
- `b`: run the blocking benchmark suite
- `h`: print help

## Browser Preview

After boot, open Serial Monitor and send:

```text
w
```

Use the printed page URL:

```text
http://XIAO_IP/
```

Endpoints:

- `/`: HTML page with `<img src="/stream">`
- `/stream`: MJPEG multipart stream
- `/status`: JSON status
- `/capture`: one JPEG when the camera pipeline is idle

The V0 firmware supports one `/stream` client at a time. Use either browser preview or the Mac live recording script preview mode unless later testing proves multiple clients are stable.

## Mac Live MP4

Start live recording:

```bash
./scripts/live_preview_record.sh 192.168.1.123
```

or:

```bash
./scripts/live_preview_record.sh http://192.168.1.123/stream
```

Output:

```text
recordings/live/live_2026-06-22_153000.mp4
recordings/live/live_2026-06-22_153000.txt
recordings/live/logs/live_2026-06-22_153000.log
```

Stop with Ctrl+C, or from another terminal:

```bash
./scripts/stop_live_recording.sh
```

Check status:

```bash
./scripts/check_live_recording.sh
```

The script uses one ESP32 `/stream` connection. If `ffplay` is installed, ffmpeg also pipes the same incoming MJPEG stream to ffplay for local preview. If `ffplay` is not available, open the browser preview page instead.

## SD Local Recording

Default `r`/`m` output:

```text
/clip_0001.mjpeg
/clip_0001_info.csv
/clip_0001_timing.csv
```

JPEG debug `j` output:

```text
/clip_0002/frame_0001.jpg
/clip_0002/frame_0002.jpg
/clip_0002/clip_info.csv
/clip_0002/frame_timing.csv
```

SD recording is the priority path. If Wi-Fi disconnects, the browser closes, or the Mac stops recording, SD recording continues until you send `x`.

## SD Auto Conversion

When the SD card is mounted on the Mac, `scripts/auto_convert_clips.sh` converts SD recordings into:

```text
~/Movies/AI_Goggles/SD_Recordings/VOLUME_sd_clip_0004.mp4
~/Movies/AI_Goggles/SD_Recordings/VOLUME_sd_clip_0005.mp4
```

These files are different from live network MP4s:

- `live_*.mp4`: recorded on the Mac from the Wi-Fi stream in real time
- `sd_clip_*.mp4`: converted later from the SD local recording

## Recommended V0 Settings

- Resolution: QVGA 320x240
- JPEG quality: 15
- SD FPS: 10
- Preview FPS: 10, with frame dropping allowed if the network is slow
- SD SPI frequency: 20 MHz with fallback to 10 MHz on errors
- Storage mode: single-file MJPEG for normal recording, JPEG sequence only for debugging

## Validation

Run at least:

1. SD only, 60 seconds, no preview client
2. Preview only, 60 seconds
3. SD plus browser preview, 60 seconds
4. SD plus Mac live MP4, 60 seconds

Record:

- actual FPS
- P50/P95/P99 frame interval
- maximum stall
- failed SD writes
- preview frames sent/dropped
- network disconnects
- heap and PSRAM before/after
- Mac MP4 duration and frame count

Do not treat the feature as stable until SD failed writes are zero, there are no watchdog resets, and SD recording continues after network disconnects.
