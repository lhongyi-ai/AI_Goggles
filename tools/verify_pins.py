#!/usr/bin/env python3
"""Cross-verify scripts/cm4_pinmap.py against the OFFICIAL Radxa pinout xlsx.

For every assignment row with a concrete CM4 pin, look up the authoritative
net name at that exact connector+pin in data/radxa_cm4_pinout_v1.20.xlsx and
confirm our recorded cm4_net matches (or our cm4_func is a documented mux
option on that pin). Reports MATCH / MISMATCH / can't-check per row.

Connector→pin-range mapping in the xlsx (one continuous sheet):
  J3A = first table pins 1..100
  J3B = first table pins 101..200
  J1  = second table pins 1..100
Exit code 0 only if there are no MISMATCHes.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
XLSX = ROOT / "data" / "radxa_cm4_pinout_v1.20.xlsx"
sys.path.insert(0, str(ROOT / "scripts"))


def load_official():
    import openpyxl

    wb = openpyxl.load_workbook(XLSX, data_only=True)
    ws = wb["Sheet1"]
    ordered = []  # (pin:int, net:str, funcs:str) in file order
    for row in ws.iter_rows(values_only=True):
        net = "" if row[0] is None else str(row[0]).strip()
        num = row[1]
        if isinstance(num, (int, float)) and float(num).is_integer():
            funcs = " | ".join(str(c).strip() for c in row[2:] if c)
            ordered.append((int(num), net, funcs))
    # split first table (1..200) from second table (J1, restarts at 1)
    j1_start = None
    for i in range(1, len(ordered)):
        if ordered[i][0] == 1 and ordered[i - 1][0] > 1:
            j1_start = i
            break
    first = {p: (net, f) for p, net, f in ordered[:j1_start]}
    j1 = {p: (net, f) for p, net, f in ordered[j1_start:]}
    return first, j1


def norm(s: str) -> str:
    return re.sub(r"[^A-Z0-9]", "", s.upper())


def main() -> int:
    if not XLSX.exists():
        print(f"ERROR: official pinout not found: {XLSX}")
        return 2
    first, j1 = load_official()
    print(f"official pinout: first-table pins={len(first)} (J3A 1-100, J3B 101-200), "
          f"J1 pins={len(j1)}")

    import cm4_pinmap

    def lookup(conn, pin):
        if conn == "J3A":
            return first.get(pin)
        if conn == "J3B":
            return first.get(pin)
        if conn == "J1":
            return j1.get(pin)
        return None

    ok = mism = skipped = 0
    mismatches = []
    for r in cm4_pinmap.ASSIGNMENTS:
        conn = r["connector"]
        pin = r["pin"]
        my_net = r.get("cm4_net", "")
        my_func = r.get("cm4_func", "")
        sig = r["signal"]
        # skip aggregate / multi-pin / non-numeric pins
        if not isinstance(pin, int):
            skipped += 1
            continue
        off = lookup(conn, pin)
        if off is None:
            mism += 1
            mismatches.append(f"{sig:24} {conn} p{pin}: pin not found in official table")
            continue
        off_net, off_funcs = off
        # match if our cm4_net equals official net, OR our func/net appears in the
        # official mux-function list for that pin.
        cand = norm(off_net)
        mine = {norm(my_net), norm(my_func.split(" (")[0])}
        funcset = {norm(x) for x in re.split(r"[|()]", off_funcs)}
        if cand in mine or (mine & funcset) or norm(off_net) in {norm(my_func)}:
            ok += 1
        else:
            mism += 1
            mismatches.append(
                f"{sig:24} {conn} p{pin}: I say net='{my_net}' func='{my_func}' "
                f"| OFFICIAL net='{off_net}' funcs='{off_funcs[:60]}'")

    print(f"\nchecked {ok+mism} numeric-pin rows: {ok} MATCH, {mism} MISMATCH "
          f"({skipped} skipped: GND/multi-pin/VREF)")
    if mismatches:
        print("\n=== MISMATCHES ===")
        for m in mismatches:
            print(" ", m)
        return 1
    print("\nAll concrete-pin assignments verified against the official pinout. ✓")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
