# Video Smoothness Benchmark

This project records camera output as JPEG frames or as a raw single-file MJPEG stream. The XIAO ESP32S3 Sense does not have an H.264 encoder, so MP4 files are produced on the Mac after recording.

## Firmware Commands

- `i`: print board, heap, PSRAM, SD, BLE, and profile information.
- `r`: record one clip with the recommended baseline profile.
- `b`: run the benchmark suite across all configured profiles.

The commands work over both USB Serial and BLE. BLE only returns short status strings; full benchmark data is printed over Serial and written to CSV on the SD card.

## Profiles

| Profile | Resolution | JPEG quality | Target FPS | SD SPI | Storage |
| --- | --- | ---: | ---: | ---: | --- |
| A | 320x240 | 15 | 10 | 10 MHz | Separate JPEG files |
| B | 320x240 | 15 | 15 | 20 MHz | Separate JPEG files |
| C | 320x240 | 20 | 20 | 20 MHz | Separate JPEG files |
| D | 640x480 | 15 | 10 | 20 MHz | Separate JPEG files |
| E | 320x240 | 15 | 10 | 20 MHz | Single-file MJPEG |

The firmware falls back to 10 MHz if SD initialization at a higher frequency fails. If write errors occur at a higher frequency, it remounts at 10 MHz for future operations.

## Output Files

Separate JPEG mode:

```text
/clip_0007/
  frame_0001.jpg
  frame_0002.jpg
  clip_info.csv
  frame_timing.csv
```

Single-file MJPEG mode:

```text
/clip_0010.mjpeg
/clip_0010_info.csv
/clip_0010_timing.csv
```

`frame_timing.csv` is written after the recording finishes, not during the recording loop, so the measurement system does not add per-frame SD writes.

## Metrics To Check

Use:

```bash
python3 scripts/analyze_clip_metrics.py /Volumes/UNTITLED\ 2/clip_0007
python3 scripts/analyze_clip_metrics.py /Volumes/UNTITLED\ 2/clip_0010_info.csv
```

Important fields:

- `actual_fps`
- `interval_us_p95`
- `capture_us_p95`
- `sd_write_us_p95`
- `jpeg_size_bytes_avg`
- `throughput_kb_s`
- `missed_deadlines`
- `longest_stall_us`

## MP4 Conversion Modes

### Constant Frame Rate

Use this for normal viewing. It distributes the captured frames evenly over time and usually looks smoother:

```bash
ffmpeg -framerate 10 -i frame_%04d.jpg -c:v libx264 -pix_fmt yuv420p clip_0007.mp4
```

For `.mjpeg`:

```bash
ffmpeg -framerate 10 -f mjpeg -i clip_0010.mjpeg -c:v libx264 -pix_fmt yuv420p clip_0010.mp4
```

The macOS auto-convert script uses this CFR approach and reads `actual_average_fps` from the clip CSV when it is available.

### Variable Frame Rate

Use this for timing analysis. Generate a concat manifest from `frame_timing.csv` where each frame duration matches the real capture interval, then run ffmpeg with concat demuxer. This preserves jitter instead of smoothing it.

```text
file 'frame_0001.jpg'
duration 0.101
file 'frame_0002.jpg'
duration 0.097
```

This is useful for debugging camera or SD stalls, not for normal viewing.

## Pass Criteria

Baseline QVGA 10 FPS should aim for:

- 30 seconds or longer stable recording
- Actual FPS at least 9.5
- Failed writes = 0
- Corrupt JPEGs = 0
- Continuous frame numbering
- P95 frame interval <= 120 ms
- Maximum stall preferably below 250 ms

Higher-FPS profiles should only be promoted if they meet the same correctness requirements and maintain at least 95% of their target FPS.
