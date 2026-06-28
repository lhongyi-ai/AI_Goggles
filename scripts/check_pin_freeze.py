#!/usr/bin/env python3
"""Pin-assignment freeze gate checker (requirements doc v1.1, Section 3.3).

Project rule: KiCad PCB Layout may not begin until cm4_v1_pin_assignment is
FROZEN. This script verifies the gate and refuses to pass while any P0 row is
incomplete. It does NOT pretend success — an unresolved table fails loudly.
"""
from __future__ import annotations

from pathlib import Path

import yaml

try:
    from .kicad_tools import PROJECT_ROOT, status
except ImportError:
    from kicad_tools import PROJECT_ROOT, status


PIN_ASSIGNMENT_FILE = PROJECT_ROOT / "config" / "cm4_v1_pin_assignment.yaml"

# Fields every assignment row must define (Section 3.3 table).
REQUIRED_FIELDS = (
    "function",
    "signal",
    "connector",
    "pin",
    "voltage_domain",
    "pinmux_conflict",
    "board_connects_to",
    "device_tree_status",
)


def load_pin_assignment() -> dict:
    if not PIN_ASSIGNMENT_FILE.exists():
        raise SystemExit(
            status("ERROR", f"Pin assignment file not found: {PIN_ASSIGNMENT_FILE}")
        )
    with PIN_ASSIGNMENT_FILE.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def row_is_p0(row: dict) -> bool:
    # Rows are P0 unless explicitly marked priority: P1/P2.
    return str(row.get("priority", "P0")).upper() == "P0"


def check_row(row: dict) -> list[str]:
    problems: list[str] = []
    label = f"{row.get('function', '?')}/{row.get('signal', '?')}"

    for field in REQUIRED_FIELDS:
        if field not in row or row[field] in (None, ""):
            problems.append(f"{label}: missing field '{field}'")

    pin = row.get("pin")
    if isinstance(pin, str) and pin.strip().upper() == "TBD":
        problems.append(f"{label}: pin is still TBD")

    if row.get("source_verified") is not True:
        problems.append(f"{label}: source_verified is not true (verify vs CM4 V1.20)")

    return problems


def main() -> int:
    data = load_pin_assignment()

    overall_status = str(data.get("status", "DRAFT")).upper()
    assignments = data.get("assignments", []) or []
    open_tbd = data.get("open_tbd", []) or []

    print(status("INFO", f"Pin assignment status: {overall_status}"))
    print(status("INFO", f"Total assignment rows: {len(assignments)}"))

    p0_problems: list[str] = []
    p1_incomplete = 0
    for row in assignments:
        problems = check_row(row)
        if row_is_p0(row):
            p0_problems.extend(problems)
        elif problems:
            p1_incomplete += 1

    unresolved_tbd = [t for t in open_tbd if not t.get("resolved", False)]

    if p0_problems:
        print(status("ERROR", f"{len(p0_problems)} P0 assignment issue(s) found:"))
        for problem in p0_problems:
            print(status("ERROR", f"  - {problem}"))

    if unresolved_tbd:
        print(status("WARN", f"{len(unresolved_tbd)} unresolved TBD item(s) (Section 8.3):"))
        for tbd in unresolved_tbd:
            print(status("WARN", f"  - {tbd.get('id')}: {tbd.get('must_confirm')}"))

    if p1_incomplete:
        print(status("INFO", f"{p1_incomplete} P1 row(s) still incomplete (allowed pre-freeze)."))

    gate_ok = (
        overall_status == "FROZEN"
        and not p0_problems
        and not unresolved_tbd
    )

    print()
    if gate_ok:
        print(status("OK", "GATE PASSED — pin assignment is FROZEN. PCB Layout may begin."))
        return 0

    print(status("ERROR", "GATE BLOCKED — PCB Layout must NOT begin yet."))
    print(status("INFO", "Resolve all P0 rows + TBD items, set status: FROZEN, then re-run."))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
