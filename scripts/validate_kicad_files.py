#!/usr/bin/env python3
"""Structural validation of the active KiCad PCB file.

Checks the generated carrier board has the expected structure (header, board
outline, 6-layer stack, core nets). This is a cheap sanity check that does not
require kicad-cli; run scripts/run_drc.py for the real DRC.
"""
from __future__ import annotations

try:
    from .kicad_tools import PCB_FILE, status
except ImportError:
    from kicad_tools import PCB_FILE, status


# Nets that must always be present on the V1 carrier (subset of the full list).
CORE_NETS = ["GND", "+5V_SYS", "MIPI_CSI3_CLK_P", "USB_DP", "PDM1_CLK", "SAI1_BCLK"]


def main() -> int:
    if not PCB_FILE.exists():
        print(status("ERROR", f"Missing PCB file: {PCB_FILE}"))
        return 2
    text = PCB_FILE.read_text(encoding="utf-8")
    checks = {
        "KiCad PCB header": "(kicad_pcb" in text,
        "Edge.Cuts outline": "Edge.Cuts" in text,
        "6-layer stack (In1.Cu)": '"In1.Cu"' in text,
        "6-layer stack (In4.Cu)": '"In4.Cu"' in text,
        "core V1 nets": all(net in text for net in CORE_NETS),
    }
    for name, passed in checks.items():
        print(status("OK" if passed else "ERROR", name))
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
