#!/usr/bin/env python3
"""XLSX -> CSV/JSON half of the ai_context build pipeline.

Per project convention:
  - native XLSX in data/ is the authoritative source (never edited by AI)
  - this script emits lossless AI-readable CSV/JSON into ai_context/
It also dumps the verified pin assignment (scripts/cm4_pinmap.py) to
ai_context/ so the pin map can be diffed/analysed without opening Excel.

Run via tools/build_ai_context.sh (do not edit ai_context/ by hand).
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
AI_DIR = ROOT / "ai_context"
SCRIPTS = ROOT / "scripts"


def dump_xlsx(path: Path) -> list[str]:
    """Dump every non-empty sheet of an xlsx to lossless CSV + JSON (rows as lists)."""
    import openpyxl

    out: list[str] = []
    wb = openpyxl.load_workbook(path, data_only=True)
    for ws in wb.worksheets:
        rows = [
            ["" if c is None else c for c in row]
            for row in ws.iter_rows(values_only=True)
        ]
        rows = [r for r in rows if any(str(c).strip() for c in r)]
        if not rows:
            continue
        stem = f"{path.stem}__{ws.title}" if len(wb.worksheets) > 1 else path.stem
        csv_path = AI_DIR / f"{stem}.csv"
        json_path = AI_DIR / f"{stem}.json"
        with csv_path.open("w", newline="", encoding="utf-8") as fh:
            csv.writer(fh).writerows(rows)
        json_path.write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
        out.extend([csv_path.name, json_path.name])
    return out


def dump_pin_assignment() -> list[str]:
    """Dump the verified pin map (scripts/cm4_pinmap.py) to CSV + JSON."""
    sys.path.insert(0, str(SCRIPTS))
    import cm4_pinmap  # noqa: E402

    rows = cm4_pinmap.ASSIGNMENTS
    cols = ["function", "signal", "connector", "pin", "cm4_net", "cm4_func",
            "voltage_domain", "pinmux_conflict", "board_connects_to",
            "device_tree_status", "priority", "source_verified"]
    csv_path = AI_DIR / "pin_assignment.csv"
    json_path = AI_DIR / "pin_assignment.json"
    with csv_path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    json_path.write_text(
        json.dumps(
            {"metadata": cm4_pinmap.METADATA, "assignments": rows,
             "open_tbd": cm4_pinmap.OPEN_TBD},
            ensure_ascii=False, indent=1),
        encoding="utf-8",
    )
    return [csv_path.name, json_path.name]


def main() -> int:
    AI_DIR.mkdir(exist_ok=True)
    written: list[str] = []
    for xlsx in sorted(DATA_DIR.glob("*.xlsx")):
        try:
            written += dump_xlsx(xlsx)
        except Exception as exc:  # rule 10: report path + error explicitly
            print(f"ERROR parsing {xlsx}: {type(exc).__name__}: {exc}", file=sys.stderr)
            return 1
    try:
        written += dump_pin_assignment()
    except Exception as exc:
        print(f"ERROR dumping pin assignment: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1
    for name in written:
        print(f"  wrote ai_context/{name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
