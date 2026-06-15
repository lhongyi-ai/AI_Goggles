# AI_Goggles

V0 firmware for a Seeed Studio XIAO ESP32S3 Sense wearable camera validation prototype.

## V0 Behavior

- Short press on D1: capture one JPEG photo.
- Long press on D1 for at least 1 second: capture JPEG frames for 10 seconds.
- Red LED on D2 stays on while capturing.
- Files are saved to the Sense microSD card without overwriting old files.
- Wi-Fi file transfer, Bluetooth audio, battery, AI, display, and custom PCB work are intentionally out of scope for this camera V0.

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
- `r`: record one 10-second JPEG sequence
- `s`: print next file indexes
- `h`: print help

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
```

The XIAO ESP32S3 Sense does not have a hardware H.264 encoder, so it cannot directly create smooth MP4/MOV files on-device. Convert a clip folder to MP4 on your computer:

```bash
ffmpeg -framerate 10 -i frame_%04d.jpg -c:v libx264 -pix_fmt yuv420p clip_0001.mp4
```

This repo also includes a macOS LaunchAgent and shell script that can auto-convert SD card `clip_*` folders to MP4 when the card is mounted.

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
