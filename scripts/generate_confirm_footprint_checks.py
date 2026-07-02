#!/usr/bin/env python3
"""Build a 1:1 print-and-verify check PCB for the two 'confirm' footprints that
now use KiCad's TI-official library land patterns:

  - U2/U16  TPD4E05U06   -> Package_SON:USON-10_2.5x1.0mm_P0.5mm   (TI DQA0010A)
  - U6      TPS61022     -> Package_DFN_QFN:Texas_RWU0007A_VQFN-7_2x2mm_P0.5mm

We did NOT hand-redraw these: KiCad ships the TI land patterns (the RWU0007A file
even references tps61022.pdf). This fixture embeds those exact footprints so you
can print at 100% and lay the physical part on the pads to confirm, mirroring the
existing j2_fh35c_1to1_check.kicad_pcb flow. It is a verification fixture, not a
fabricable board.
"""
from __future__ import annotations

from pathlib import Path
from uuid import uuid4

try:
    from .kicad_tools import HARDWARE_DIR, status
except ImportError:
    from kicad_tools import HARDWARE_DIR, status

KICAD_FP = Path("/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints")
SOURCES = {
    "USON-10 (TPD4E05U06 / U2,U16)":
        KICAD_FP / "Package_SON.pretty" / "USON-10_2.5x1.0mm_P0.5mm.kicad_mod",
    "VQFN-7 RWU0007A (TPS61022 / U6)":
        KICAD_FP / "Package_DFN_QFN.pretty" / "Texas_RWU0007A_VQFN-7_2x2mm_P0.5mm.kicad_mod",
}
CHECK_PCB = HARDWARE_DIR / "confirm_fp_1to1_check.kicad_pcb"
CHECK_PRO = HARDWARE_DIR / "confirm_fp_1to1_check.kicad_pro"


def uid() -> str:
    return str(uuid4())


def embed(mod_text: str, x: float, y: float) -> str:
    """Turn a standalone .kicad_mod into a placed footprint inside a board."""
    marker = '(layer "F.Cu")'
    idx = mod_text.index(marker) + len(marker)
    inject = f'\n\t(at {x:.3f} {y:.3f})\n\t(uuid "{uid()}")'
    return mod_text[:idx] + inject + mod_text[idx:]


def build() -> str:
    placements = [
        ("USON-10 (TPD4E05U06 / U2,U16)", 14.0, 12.0),
        ("USON-10 (TPD4E05U06 / U2,U16)", 14.0, 20.0),
        ("VQFN-7 RWU0007A (TPS61022 / U6)", 34.0, 12.0),
    ]
    blocks = []
    for label, x, y in placements:
        text = SOURCES[label].read_text(encoding="utf-8").rstrip()
        blocks.append(embed(text, x, y))
    labels = [
        ('gr_text "U2/U16 USON-10 2.5x1.0 (TPD4E05U06)" (at 14 7 0)'),
        ('gr_text "U6 VQFN-7 RWU0007A (TPS61022)" (at 34 7 0)'),
    ]
    label_lines = "\n".join(
        f'  ({t} (layer "F.SilkS") (uuid "{uid()}") '
        f'(effects (font (size 0.7 0.7) (thickness 0.1))))'
        for t in labels
    )
    fps = "\n".join(blocks)
    return f'''(kicad_pcb
  (version 20240108)
  (generator "ai-glasses-python")
  (general (thickness 1.6))
  (paper "A4")
  (title_block
    (title "Confirm-footprint 1:1 check (USON-10 + VQFN-7 RWU0007A)")
    (comment 1 "Print at 100% / 1:1; lay the physical part on the pads to verify.")
    (comment 2 "Verification fixture only - not a fabricable board.")
    (comment 3 "Footprints are KiCad TI-official library land patterns.")
  )
  (layers
    (0 "F.Cu" signal)
    (31 "B.Cu" signal)
    (36 "B.SilkS" user)
    (37 "F.SilkS" user)
    (38 "B.Mask" user)
    (39 "F.Mask" user)
    (44 "Edge.Cuts" user)
    (47 "F.CrtYd" user)
    (48 "B.Fab" user)
    (49 "F.Fab" user)
  )
  (setup (pad_to_mask_clearance 0.050))
  (net 0 "")
  (gr_rect (start 0 0) (end 50 28)
    (stroke (width 0.100) (type default)) (fill none) (layer "Edge.Cuts") (uuid "{uid()}"))
  (gr_text "PRINT 1:1 / 100% ONLY" (at 25 3 0) (layer "F.SilkS") (uuid "{uid()}")
    (effects (font (size 1.1 1.1) (thickness 0.15))))
{label_lines}
{fps}
)
'''


def write_files() -> Path:
    CHECK_PCB.write_text(build(), encoding="utf-8")
    CHECK_PRO.write_text(
        '{\n  "meta": {"filename": "confirm_fp_1to1_check.kicad_pro", "version": 1},\n'
        '  "project": {"name": "confirm_fp_1to1_check", "note": "1:1 footprint check fixture"}\n}\n',
        encoding="utf-8",
    )
    return CHECK_PCB


def main() -> int:
    for label, path in SOURCES.items():
        if not path.exists():
            print(status("ERROR", f"Missing KiCad library footprint: {path}"))
            return 1
    pcb = write_files()
    print(status("OK", f"Wrote 1:1 check PCB: {pcb}"))
    print(status("INFO", "Export PDF: kicad-cli pcb export pdf --layers F.Cu,F.Paste,F.SilkS,F.Fab,Edge.Cuts"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
