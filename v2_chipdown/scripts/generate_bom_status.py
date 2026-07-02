#!/usr/bin/env python3
"""Emit docs/10_bom_status.md from the schematic master (chipdown_bom.py).

Derived file — do not hand-edit; re-run after changing chipdown_bom.py.
"""
from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
from chipdown_bom import COMPONENTS, all_nets  # noqa: E402

OUT = ROOT / "docs" / "10_bom_status.md"

BOARDS = ["R-Temple Compute Board", "L-Temple AON/Power Board",
          "Front Sensor Board", "Temple Rears (batt/spkr/ant)", "EVT Debug Tail"]


def bom_key(c):
    # sort by the numeric part of the BOM id, keeping suffix letters stable
    digits = "".join(ch for ch in c.bom_id if ch.isdigit()) or "0"
    return (int(digits), c.bom_id)


def main() -> int:
    md: list[str] = []
    w = md.append
    n = len(COMPONENTS)
    counts = {s: sum(1 for c in COMPONENTS if c.assembly == s)
              for s in ("Fit", "HOLD", "DNP", "TBD")}
    w("# 10 — BOM freeze status (generated)")
    w("")
    w(f"> Generated {date.today().isoformat()} from `scripts/chipdown_bom.py`. "
      "Do not hand-edit. Legend: **Fit** first-build populate · **DNP** land only · "
      "**HOLD** candidate, blocked on a gate · **TBD** MPN/spec undecided.")
    w("")
    w(f"**{n} components** — {counts['Fit']} Fit · {counts['HOLD']} HOLD · "
      f"{counts['DNP']} DNP · {counts['TBD']} TBD. {len(all_nets())} nets.")
    w("")
    w("Related generated gates: [08 signal dictionary](08_signal_dictionary.md), "
      "[09 power-domain isolation](09_power_domain_isolation_matrix.md), "
      "[11 footprint register](11_footprint_register.md), "
      "[12 layout-entry status](12_layout_entry_gate_status.md), plus "
      "[13 Phase 1.5 floorplan](13_mechanical_electrical_floorplan.md).")
    w("")
    for board in BOARDS:
        rows = sorted((c for c in COMPONENTS if c.board == board), key=bom_key)
        if not rows:
            continue
        w(f"## {board} ({len(rows)})")
        w("")
        w("| BOM ID | Ref | Value | Pri | Status | Gate to close |")
        w("|---|---|---|---|:--:|---|")
        for c in rows:
            w(f"| {c.bom_id} | {c.ref} | {c.value} | {c.pri} | {c.assembly} | {c.gate or '-'} |")
        w("")
    OUT.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT.parent)} ({n} components)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
