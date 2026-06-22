#!/usr/bin/env python3
"""Analyze AI_Goggles clip timing CSV files using only the Python standard library."""

from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path
from statistics import mean


def read_info(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}

    with path.open(newline="") as handle:
        reader = csv.reader(handle)
        rows = list(reader)

    if rows and rows[0] == ["key", "value"]:
        rows = rows[1:]

    return {row[0]: row[1] for row in rows if len(row) >= 2}


def read_timing(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(path)

    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def to_float(value: str | None, default: float = 0.0) -> float:
    if value is None or value == "":
        return default
    return float(value)


def to_int(value: str | None, default: int = 0) -> int:
    if value is None or value == "":
        return default
    return int(float(value))


def percentile(values: list[float], pct: float) -> float:
    if not values:
        return 0.0

    ordered = sorted(values)
    rank = (pct / 100.0) * (len(ordered) - 1)
    lower = math.floor(rank)
    upper = math.ceil(rank)

    if lower == upper:
        return ordered[int(rank)]

    weight = rank - lower
    return ordered[lower] * (1.0 - weight) + ordered[upper] * weight


def describe(name: str, values: list[float]) -> list[tuple[str, float]]:
    if not values:
        return [
            (f"{name}_avg", 0.0),
            (f"{name}_p50", 0.0),
            (f"{name}_p95", 0.0),
            (f"{name}_p99", 0.0),
            (f"{name}_min", 0.0),
            (f"{name}_max", 0.0),
        ]

    avg = mean(values)
    variance = mean([(value - avg) ** 2 for value in values])

    return [
        (f"{name}_avg", avg),
        (f"{name}_stddev", math.sqrt(variance)),
        (f"{name}_p50", percentile(values, 50)),
        (f"{name}_p95", percentile(values, 95)),
        (f"{name}_p99", percentile(values, 99)),
        (f"{name}_min", min(values)),
        (f"{name}_max", max(values)),
    ]


def find_default_files(path: Path) -> tuple[Path, Path]:
    if path.is_dir():
        return path / "clip_info.csv", path / "frame_timing.csv"

    if path.name.endswith("_info.csv"):
        stem = path.name.removesuffix("_info.csv")
        return path, path.with_name(f"{stem}_timing.csv")

    raise ValueError("Pass a clip directory or a *_info.csv file")


def analyze(path: Path) -> list[tuple[str, str]]:
    info_path, timing_path = find_default_files(path)
    info = read_info(info_path)
    rows = read_timing(timing_path)

    successful = [row for row in rows if row.get("write_success") == "1"]
    intervals = [to_float(row.get("frame_interval_us")) for row in rows if to_float(row.get("frame_interval_us")) > 0]
    capture = [to_float(row.get("capture_duration_us")) for row in rows if to_float(row.get("capture_duration_us")) > 0]
    sd_write = [to_float(row.get("sd_write_duration_us")) for row in rows if to_float(row.get("sd_write_duration_us")) > 0]
    sd_open = [to_float(row.get("sd_open_duration_us")) for row in rows if to_float(row.get("sd_open_duration_us")) > 0]
    sd_close = [to_float(row.get("sd_close_duration_us")) for row in rows if to_float(row.get("sd_close_duration_us")) > 0]
    preview_send = [to_float(row.get("preview_send_duration_us")) for row in rows if to_float(row.get("preview_send_duration_us")) > 0]
    jpeg_sizes = [to_float(row.get("jpeg_size_bytes")) for row in successful if to_float(row.get("jpeg_size_bytes")) > 0]

    elapsed_seconds = 0.0
    if info.get("recording_start_us") and info.get("recording_end_us"):
        elapsed_seconds = (to_float(info["recording_end_us"]) - to_float(info["recording_start_us"])) / 1_000_000.0

    actual_fps = len(successful) / elapsed_seconds if elapsed_seconds > 0 else to_float(info.get("actual_average_fps"))
    total_bytes = sum(jpeg_sizes)
    throughput = total_bytes / 1024.0 / elapsed_seconds if elapsed_seconds > 0 else 0.0

    result: list[tuple[str, str]] = [
        ("info_file", str(info_path)),
        ("timing_file", str(timing_path)),
        ("profile", info.get("profile", "")),
        ("storage_mode", info.get("storage_mode", "")),
        ("resolution", f"{info.get('width', '')}x{info.get('height', '')}"),
        ("jpeg_quality", info.get("jpeg_quality", "")),
        ("target_fps", info.get("target_fps", "")),
        ("actual_fps", f"{actual_fps:.3f}"),
        ("elapsed_seconds", f"{elapsed_seconds:.3f}"),
        ("capture_attempts", str(len(rows))),
        ("successful_frames", str(len(successful))),
        ("failed_frames", str(len(rows) - len(successful))),
        ("missed_deadlines", str(sum(1 for row in rows if row.get("deadline_missed") == "1"))),
        ("preview_frames_sent", info.get("preview_frames_sent", str(sum(1 for row in rows if row.get("preview_sent") == "1")))),
        ("preview_frames_dropped", info.get("preview_frames_dropped", str(sum(1 for row in rows if row.get("preview_dropped") == "1")))),
        ("preview_disconnects", info.get("preview_disconnects", "")),
        ("longest_stall_us", f"{max(intervals) if intervals else 0:.1f}"),
        ("total_bytes", f"{total_bytes:.0f}"),
        ("throughput_kb_s", f"{throughput:.3f}"),
    ]

    for key, value in describe("interval_us", intervals):
        result.append((key, f"{value:.3f}"))
    for key, value in describe("capture_us", capture):
        result.append((key, f"{value:.3f}"))
    for key, value in describe("sd_open_us", sd_open):
        result.append((key, f"{value:.3f}"))
    for key, value in describe("sd_write_us", sd_write):
        result.append((key, f"{value:.3f}"))
    for key, value in describe("sd_close_us", sd_close):
        result.append((key, f"{value:.3f}"))
    for key, value in describe("preview_send_us", preview_send):
        result.append((key, f"{value:.3f}"))
    for key, value in describe("jpeg_size_bytes", jpeg_sizes):
        result.append((key, f"{value:.3f}"))

    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("clip", type=Path, help="Clip directory or *_info.csv file")
    parser.add_argument("--csv", type=Path, help="Optional output CSV summary path")
    args = parser.parse_args()

    result = analyze(args.clip)

    width = max(len(key) for key, _ in result)
    for key, value in result:
        print(f"{key:<{width}}  {value}")

    if args.csv:
        with args.csv.open("w", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow(["metric", "value"])
            writer.writerows(result)


if __name__ == "__main__":
    main()
