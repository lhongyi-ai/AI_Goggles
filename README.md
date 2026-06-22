# AI_Goggles

V0 firmware for a Seeed Studio XIAO ESP32S3 Sense wearable camera validation prototype.

## V0 Behavior

- Short press on D1: capture one JPEG photo.
- Long press on D1 for at least 1 second: start SD MJPEG recording. Press again or send `x` to stop.
- Red LED on D2 stays on while capturing.
- Files are saved to the Sense microSD card without overwriting old files.
- Wi-Fi live preview is available when `v0_camera_prototype/wifi_config.h` is configured.

## Wiring

- `D1 -> push button -> GND`
- `D2 -> 330 ohm resistor -> LED anode`
- `LED cathode -> GND`

The camera and microSD slot are on the Sense expansion board. Do not use D8, D9, or D10 for the button or LED because those pins are used by SD SPI.

## Board

Use:

```bash
esp32:esp32:XIAO_ESP32S3
```

Recommended options:

- USB CDC On Boot: Enabled
- PSRAM: OPI PSRAM
- Partition Scheme: Maximum APP
- Upload Speed: 921600, or lower if upload is unreliable

The equivalent compile FQBN is:

```bash
esp32:esp32:XIAO_ESP32S3:PSRAM=opi,PartitionScheme=max_app_8MB,CDCOnBoot=default
```

## Suggested Test Order

1. `tests/01_blink_led`
2. `tests/02_read_button`
3. `tests/03_button_controls_led`
4. `tests/04_sd_write_test`
5. `v0_camera_prototype`

Compile the main firmware:

```bash
arduino-cli compile \
  --fqbn esp32:esp32:XIAO_ESP32S3:PSRAM=opi,PartitionScheme=max_app_8MB,CDCOnBoot=default \
  v0_camera_prototype
```

List connected boards:

```bash
arduino-cli board list
```

Upload after replacing the port with your actual port:

```bash
arduino-cli upload \
  -p /dev/cu.usbmodemXXXX \
  --fqbn esp32:esp32:XIAO_ESP32S3:PSRAM=opi,PartitionScheme=max_app_8MB,CDCOnBoot=default \
  v0_camera_prototype
```

Serial Monitor:

```bash
arduino-cli monitor -p /dev/cu.usbmodemXXXX -c baudrate=115200
```

Serial commands in the main firmware:

- `p`: take one photo
- `r`: start SD MJPEG recording with Wi-Fi preview available
- `x`: stop current SD recording and write metadata
- `j`: start JPEG sequence debug recording
- `m`: start SD MJPEG recording
- `v`: enable or disable Wi-Fi preview server
- `w`: print Wi-Fi status, IP, and preview URLs
- `s`: print next file indexes
- `i`: print hardware, memory, SD, BLE, and active profile information
- `b`: run the video smoothness benchmark suite
- `h`: print help

## Wi-Fi Live Preview And Mac MP4

Copy and edit the Wi-Fi config:

```bash
cp v0_camera_prototype/wifi_config.example.h v0_camera_prototype/wifi_config.h
```

Then upload the firmware. In Serial Monitor, send:

```text
w
```

Open the printed preview page:

```text
http://XIAO_IP/
```

Record a live H.264 MP4 on the Mac:

```bash
./scripts/live_preview_record.sh XIAO_IP
```

Stop with Ctrl+C, or:

```bash
./scripts/stop_live_recording.sh
```

See [docs/live_preview_and_dual_recording.md](docs/live_preview_and_dual_recording.md) for the architecture, endpoints, and validation plan.

## BLE Phone Control

The firmware exposes a BLE control service so a phone can trigger the same commands as USB serial.

BLE identifiers:

```text
Device name: AI_Goggles
Service UUID: 7b8f0001-2f5d-4d5a-9e4f-7f6a8c8d0001
Control characteristic UUID: 7b8f0002-2f5d-4d5a-9e4f-7f6a8c8d0001
```

Phone test apps:

- iPhone: nRF Connect or LightBlue
- Android: nRF Connect

Phone steps:

1. Power the XIAO ESP32S3 Sense.
2. Open nRF Connect or LightBlue.
3. Scan for `AI_Goggles`.
4. Connect to the device.
5. Open the custom service UUID above.
6. Open the control characteristic UUID above.
7. Write one UTF-8/text command:
   - `p`: take one photo
   - `r`: start SD MJPEG recording
   - `x`: stop recording
   - `j`: start JPEG sequence debug recording
   - `m`: start SD MJPEG recording
   - `v`: toggle Wi-Fi preview server
   - `w`: print Wi-Fi status
   - `s`: update/read status
   - `i`: print hardware/profile info to Serial Monitor
   - `b`: run the benchmark suite
   - `h`: print help to Serial Monitor
8. Read the same characteristic to see a simple status string like `ready: recording done`.

Do not write a new `r` or `b` command while a recording is already running. The board is busy during capture.

## Output Files

Single photos:

```text
/photo_0001.jpg
/photo_0002.jpg
```

JPEG sequences:

```text
/clip_0001/frame_0001.jpg
/clip_0001/frame_0002.jpg
/clip_0001/clip_info.csv
/clip_0001/frame_timing.csv
```

Single-file MJPEG output:

```text
/clip_0005.mjpeg
/clip_0005_info.csv
/clip_0005_timing.csv
```

The XIAO ESP32S3 Sense does not have a hardware H.264 encoder, so it cannot directly create smooth MP4/MOV files on-device. Convert a clip folder to MP4 on your computer:

```bash
ffmpeg -framerate 10 -i frame_%04d.jpg -c:v libx264 -pix_fmt yuv420p clip_0001.mp4
```

This repo also includes a macOS LaunchAgent and shell script that can auto-convert SD card `clip_*` folders and `.mjpeg` files to `sd_clip_*.mp4` when the card is mounted. Live network recordings are saved separately as `recordings/live/live_*.mp4`.

## Video Smoothness Benchmark

The firmware records per-frame timing with `esp_timer_get_time()` and writes metrics after recording finishes. It does not print per-frame logs during capture.

Profile summary:

| Profile | Resolution | JPEG quality | Target FPS | SD SPI | Storage |
| --- | --- | ---: | ---: | ---: | --- |
| A | 320x240 | 15 | 10 | 10 MHz | Separate JPEG files |
| B | 320x240 | 15 | 15 | 20 MHz | Separate JPEG files |
| C | 320x240 | 20 | 20 | 20 MHz | Separate JPEG files |
| D | 640x480 | 15 | 10 | 20 MHz | Separate JPEG files |
| E | 320x240 | 15 | 10 | 20 MHz | Single-file MJPEG |

Analyze a clip:

```bash
python3 scripts/analyze_clip_metrics.py /Volumes/UNTITLED\ 2/clip_0001
python3 scripts/analyze_clip_metrics.py /Volumes/UNTITLED\ 2/clip_0005_info.csv
```

See [docs/video_smoothness_benchmark.md](docs/video_smoothness_benchmark.md) for the full benchmark workflow and CFR/VFR MP4 conversion notes.

## Bluetooth Audio Note

The XIAO ESP32S3 Sense cannot act like a normal phone Bluetooth speaker/headset because ESP32-S3 supports BLE but not Classic Bluetooth audio profiles such as A2DP or HFP. BLE is useful for low-bandwidth control commands, but not for ordinary phone audio streaming in this Arduino setup.

For phone audio, use a separate Bluetooth audio receiver module or a chip/board with Classic Bluetooth audio support, then connect its audio output to a speaker/amp path. For phone camera control, a BLE control service can be added separately.

## V0 Pass Criteria

- Camera initializes reliably.
- Button triggers once per press.
- LED is visible while capturing and off afterward.
- Single photos open on a computer.
- A 10-second recording saves at least 30 valid JPEG frames.
- Restarting the board does not overwrite old captures.
