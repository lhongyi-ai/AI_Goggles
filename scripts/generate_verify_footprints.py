#!/usr/bin/env python3
"""Generate explicit VERIFY placeholder footprints for pre-layout sync.

These footprints exist only so KiCad's "Update PCB from Schematic" can place
all schematic symbols without "no footprint assigned" errors. They are not
manufacturing footprints and must be replaced with datasheet-verified footprints
before layout/fabrication.
"""
from __future__ import annotations

import math
from pathlib import Path

try:
    from .carrier_bom import COMPONENTS
    from .kicad_tools import HARDWARE_DIR
except ImportError:
    from carrier_bom import COMPONENTS
    from kicad_tools import HARDWARE_DIR


PRETTY_DIR = HARDWARE_DIR / "AI_Glasses.pretty"


def _project_verify_footprints() -> dict[str, int]:
    footprints: dict[str, int] = {}
    for comp in COMPONENTS:
        footprint = comp.footprint
        if not footprint.startswith("AI_Glasses:"):
            continue
        name = footprint.split(":", 1)[1]
        if "VERIFY" not in name:
            continue
        pad_count = max(len(comp.pins), 1)
        previous = footprints.get(name)
        footprints[name] = max(previous or 0, pad_count)
    return footprints


def _line(start: tuple[float, float], end: tuple[float, float], layer: str, width: float = 0.05) -> str:
    return (
        f'  (fp_line (start {start[0]:.3f} {start[1]:.3f}) (end {end[0]:.3f} {end[1]:.3f})\n'
        f'    (stroke (width {width:.3f}) (type solid)) (layer "{layer}"))'
    )


def _pad_grid(pad_count: int) -> tuple[list[str], float, float]:
    if pad_count == 1:
        return [
            '  (pad "1" smd circle (at 0.000 0.000) (size 1.000 1.000) '
            '(layers "F.Cu" "F.Paste" "F.Mask"))'
        ], 3.0, 3.0

    cols = min(10, pad_count)
    rows = math.ceil(pad_count / cols)
    pitch = 1.27
    pads: list[str] = []
    for pad_num in range(1, pad_count + 1):
        row = (pad_num - 1) // cols
        col = (pad_num - 1) % cols
        x = (col - (cols - 1) / 2) * pitch
        y = (row - (rows - 1) / 2) * pitch
        pads.append(
            f'  (pad "{pad_num}" smd roundrect (at {x:.3f} {y:.3f}) '
            f'(size 0.800 0.800) (layers "F.Cu" "F.Paste" "F.Mask") '
            f'(roundrect_rratio 0.200))'
        )

    width = max((cols - 1) * pitch + 2.5, 3.0)
    height = max((rows - 1) * pitch + 2.5, 3.0)
    return pads, width, height


def footprint_text(name: str, pad_count: int) -> str:
    pads, width, height = _pad_grid(pad_count)
    x = width / 2
    y = height / 2
    outline = "\n".join(
        [
            _line((-x, -y), (x, -y), "F.Fab"),
            _line((x, -y), (x, y), "F.Fab"),
            _line((x, y), (-x, y), "F.Fab"),
            _line((-x, y), (-x, -y), "F.Fab"),
            _line((-x - 0.25, -y - 0.25), (x + 0.25, -y - 0.25), "F.CrtYd"),
            _line((x + 0.25, -y - 0.25), (x + 0.25, y + 0.25), "F.CrtYd"),
            _line((x + 0.25, y + 0.25), (-x - 0.25, y + 0.25), "F.CrtYd"),
            _line((-x - 0.25, y + 0.25), (-x - 0.25, -y - 0.25), "F.CrtYd"),
        ]
    )

    return f'''(footprint "{name}"
  (version 20240108)
  (generator "ai-glasses-python")
  (layer "F.Cu")
  (descr "VERIFY placeholder footprint for pre-layout schematic-to-PCB sync; replace before layout/fab.")
  (tags "VERIFY PLACEHOLDER DO_NOT_FAB")
  (property "Verification" "PLACEHOLDER_NOT_FOR_FAB" (at 0 0 0) (layer "F.Fab") hide
    (effects (font (size 1 1) (thickness 0.15)))
  )
  (attr smd exclude_from_pos_files)
  (fp_text reference "REF**" (at 0 {-y - 1.000:.3f} 0) (layer "F.SilkS")
    (effects (font (size 0.800 0.800) (thickness 0.120)))
  )
  (fp_text value "{name}" (at 0 {y + 1.000:.3f} 0) (layer "F.Fab")
    (effects (font (size 0.700 0.700) (thickness 0.100)))
  )
  (fp_text user "VERIFY - REPLACE BEFORE LAYOUT" (at 0 0 0) (layer "F.Fab")
    (effects (font (size 0.600 0.600) (thickness 0.080)))
  )
{outline}
{chr(10).join(pads)}
  (embedded_fonts no)
)
'''


def write_verify_footprints() -> list[Path]:
    PRETTY_DIR.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for name, pad_count in sorted(_project_verify_footprints().items()):
        path = PRETTY_DIR / f"{name}.kicad_mod"
        path.write_text(footprint_text(name, pad_count), encoding="utf-8")
        written.append(path)
    return written


def main() -> int:
    written = write_verify_footprints()
    print(f"Generated {len(written)} VERIFY placeholder footprints in {PRETTY_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
