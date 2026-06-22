#!/usr/bin/env python3
"""Validate AI_Goggles recording artifacts with optional ffprobe support."""

from __future__ import annotations

import argparse
import csv
import json
import shutil
import subprocess
from pathlib import Path


def read_info(path: Path) -> dict[str, str]:
    if path.is_dir():
        info = path / "clip_info.csv"
    elif path.name.endswith("_info.csv"):
        info = path
    else:
        info = path.with_name(f"{path.stem}_info.csv")

    if not info.exists():
        return {}

    with info.open(newline="") as handle:
        rows = list(csv.reader(handle))
    if rows and rows[0] == ["key", "value"]:
        rows = rows[1:]
    return {row[0]: row[1] for row in rows if len(row) >= 2}


def ffprobe(path: Path) -> dict[str, object] | None:
    if shutil.which("ffprobe") is None:
        return None
    command = [
        "ffprobe",
        "-v",
        "error",
        "-count_frames",
        "-select_streams",
        "v:0",
        "-show_entries",
        "stream=nb_read_frames,duration,avg_frame_rate,width,height",
        "-of",
        "json",
        str(path),
    ]
    result = subprocess.run(command, check=False, capture_output=True, text=True)
    if result.returncode != 0:
        return {"error": result.stderr.strip()}
    return json.loads(result.stdout)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("artifact", type=Path, help="Clip directory, *_info.csv, MJPEG, or MP4 file")
    args = parser.parse_args()

    artifact = args.artifact
    print(f"artifact={artifact}")
    print(f"exists={artifact.exists()}")

    info = read_info(artifact)
    for key in [
        "profile",
        "storage_mode",
        "output_path",
        "target_fps",
        "actual_average_fps",
        "successful_frames",
        "failed_frames",
        "preview_frames_sent",
        "preview_frames_dropped",
        "preview_disconnects",
    ]:
        if key in info:
            print(f"{key}={info[key]}")

    if artifact.suffix.lower() == ".mp4":
        probe = ffprobe(artifact)
        print(f"ffprobe={json.dumps(probe, indent=2) if probe is not None else 'not available'}")


if __name__ == "__main__":
    main()
