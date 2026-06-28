#!/usr/bin/env python3
"""Generate the J2 FH35C-31S-0.3SHW(50) footprint from the Hirose drawing record."""
from __future__ import annotations

from pathlib import Path
from uuid import uuid4

import yaml

try:
    from .kicad_tools import HARDWARE_DIR, PROJECT_ROOT, status
except ImportError:
    from kicad_tools import HARDWARE_DIR, PROJECT_ROOT, status


CONFIG = PROJECT_ROOT / "config" / "j2_fh35c_footprint.yaml"
FOOTPRINT = HARDWARE_DIR / "AI_Glasses.pretty" / "FH35C-31S-0.3SHW_50.kicad_mod"
CHECK_PCB = HARDWARE_DIR / "j2_fh35c_1to1_check.kicad_pcb"
CHECK_PRO = HARDWARE_DIR / "j2_fh35c_1to1_check.kicad_pro"


def uid() -> str:
    return str(uuid4())


def load_config() -> dict:
    with CONFIG.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def prop(name: str, value: str) -> str:
    return f'''  (property "{name}" "{value}" (at 0 0 0) (layer "F.Fab") hide
    (effects (font (size 1 1) (thickness 0.15)))
  )'''


def pad(num: str, x: float, y: float, w: float, h: float, *, rr: float = 0.25) -> str:
    return (
        f'  (pad "{num}" smd roundrect (at {x:.3f} {y:.3f}) '
        f'(size {w:.3f} {h:.3f}) (layers "F.Cu" "F.Paste" "F.Mask") '
        f'(roundrect_rratio {rr:.3f}))'
    )


def fp_line(layer: str, x1: float, y1: float, x2: float, y2: float, width: float) -> str:
    return (
        f'  (fp_line (start {x1:.3f} {y1:.3f}) (end {x2:.3f} {y2:.3f})\n'
        f'    (stroke (width {width:.3f}) (type solid)) (layer "{layer}"))'
    )


def rect(layer: str, x: float, y: float, width: float, height: float, stroke: float) -> str:
    x0 = -width / 2 + x
    x1 = width / 2 + x
    y0 = -height / 2 + y
    y1 = height / 2 + y
    return "\n".join(
        [
            fp_line(layer, x0, y0, x1, y0, stroke),
            fp_line(layer, x1, y0, x1, y1, stroke),
            fp_line(layer, x1, y1, x0, y1, stroke),
            fp_line(layer, x0, y1, x0, y0, stroke),
        ]
    )


def footprint_text(data: dict, *, board_instance: bool = False, at: tuple[float, float] | None = None) -> str:
    part = data["part"]
    dims = data["dimension_table_mm"]
    pattern = data["pcb_mounting_pattern_mm"]
    odd = pattern["contact_no1_odd_pad"]
    even = pattern["contact_no2_even_pad"]
    upper_mp = pattern["metal_fitting_pads"]["upper"]
    lower_mp = pattern["metal_fitting_pads"]["lower"]
    n = int(part["contacts"])

    header = [
        f'(footprint "FH35C-31S-0.3SHW_50"',
        '  (version 20240108)',
        '  (generator "ai-glasses-python")',
        '  (layer "F.Cu")',
    ]
    if board_instance and at:
        header.append(f'  (at {at[0]:.3f} {at[1]:.3f})')

    body = [
        f'  (descr "Hirose {part["mpn"]}, 31-pin 0.3mm FPC, generated from {data["source_drawing"]["drawing_no"]}; physical 1:1 check required.")',
        '  (tags "Hirose FH35C 31P 0.3mm FPC Radxa Camera 4K IMX415")',
        prop("Manufacturer", part["manufacturer"]),
        prop("MPN", part["mpn"]),
        prop("CodeNumber", part["code_number"]),
        prop("SourceDrawing", data["source_drawing"]["drawing_no"]),
        prop("Verification", "DRAWING_DIMENSIONS_APPLIED__PHYSICAL_1TO1_CHECK_REQUIRED"),
        '  (attr smd)',
        '  (fp_text reference "J2" (at 0 -3.100 0) (layer "F.SilkS")',
        '    (effects (font (size 0.8 0.8) (thickness 0.12)))',
        '  )',
        f'  (fp_text value "{part["mpn"]}" (at 0 3.200 0) (layer "F.Fab")',
        '    (effects (font (size 0.75 0.75) (thickness 0.1)))',
        '  )',
        '  (fp_text user "PIN 1 = GND" (at -5.350 1.850 0) (layer "F.SilkS")',
        '    (effects (font (size 0.55 0.55) (thickness 0.08)) (justify left))',
        '  )',
        '  (fp_text user "FPC INSERT ->" (at 0 2.450 0) (layer "F.SilkS")',
        '    (effects (font (size 0.65 0.65) (thickness 0.1)))',
        '  )',
        '  (fp_text user "1:1 CHECK REQUIRED" (at 0 1.750 0) (layer "F.Fab")',
        '    (effects (font (size 0.55 0.55) (thickness 0.08)))',
        '  )',
        '  (fp_text user "${REFERENCE}" (at 0 0 0) (layer "F.Fab")',
        '    (effects (font (size 0.8 0.8) (thickness 0.1)))',
        '  )',
        rect("F.Fab", 0, 0, dims["A"], 3.35, 0.1),
        rect("F.CrtYd", 0, 0, dims["A"] + 0.6, 4.4, 0.05),
        fp_line("F.SilkS", -5.35, 1.55, -4.95, 1.95, 0.12),
        fp_line("F.SilkS", -4.95, 1.95, -4.55, 1.55, 0.12),
        fp_line("F.SilkS", -4.55, 1.55, -5.35, 1.55, 0.12),
    ]

    # Odd pins/contact No.1: lower row, 16 pads, 0.6mm pitch, C=9.0mm span.
    odd_start = -float(dims["C"]) / 2
    even_start = -float(dims["B"]) / 2
    for pin_no in range(1, n + 1, 2):
        k = (pin_no - 1) // 2
        body.append(pad(str(pin_no), odd_start + k * pattern["same_row_pitch"], odd["center_y"], odd["width_x"], odd["length_y"]))
    for pin_no in range(2, n + 1, 2):
        k = (pin_no - 2) // 2
        body.append(pad(str(pin_no), even_start + k * pattern["same_row_pitch"], even["center_y"], even["width_x"], even["length_y"]))

    # End metal fitting pads from the mounting-pattern drawing.
    body.extend(
        [
            pad("MP1", -upper_mp["center_x_abs"], upper_mp["center_y"], upper_mp["width_x"], upper_mp["length_y"], rr=0.05),
            pad("MP2", upper_mp["center_x_abs"], upper_mp["center_y"], upper_mp["width_x"], upper_mp["length_y"], rr=0.05),
            pad("MP3", -lower_mp["center_x_abs"], lower_mp["center_y"], lower_mp["width_x"], lower_mp["length_y"], rr=0.05),
            pad("MP4", lower_mp["center_x_abs"], lower_mp["center_y"], lower_mp["width_x"], lower_mp["length_y"], rr=0.05),
            '  (embedded_fonts no)',
        ]
    )
    return "\n".join([*header, *body, ")"]) + "\n"


def check_board_text(data: dict) -> str:
    fp = footprint_text(data, board_instance=True, at=(25.0, 15.0))
    return f'''(kicad_pcb
  (version 20240108)
  (generator "ai-glasses-python")
  (general (thickness 1.6))
  (paper "A4")
  (title_block
    (title "J2 FH35C-31S-0.3SHW(50) 1:1 Footprint Check")
    (comment 1 "Print at 100%; place real FH35C connector on pads.")
    (comment 2 "Do not fabricate as a board; this is a paper/assembly check fixture.")
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
  (gr_rect (start 0 0) (end 50 30)
    (stroke (width 0.100) (type default)) (fill none) (layer "Edge.Cuts") (uuid "{uid()}"))
  (gr_text "PRINT 1:1 / 100% ONLY" (at 25 5 0) (layer "F.SilkS") (uuid "{uid()}")
    (effects (font (size 1.2 1.2) (thickness 0.15))))
  (gr_text "FH35C-31S-0.3SHW(50)  Pad1=GND  FPC insert ->" (at 25 24 0) (layer "F.Fab") (uuid "{uid()}")
    (effects (font (size 0.9 0.9) (thickness 0.12))))
{fp}
)
'''


def write_files() -> tuple[Path, Path]:
    data = load_config()
    FOOTPRINT.parent.mkdir(parents=True, exist_ok=True)
    FOOTPRINT.write_text(footprint_text(data), encoding="utf-8")
    CHECK_PCB.write_text(check_board_text(data), encoding="utf-8")
    CHECK_PRO.write_text(
        '{\n  "meta": {"filename": "j2_fh35c_1to1_check.kicad_pro", "version": 1},\n'
        '  "project": {"name": "j2_fh35c_1to1_check", "note": "Paper 1:1 footprint check fixture"}\n}\n',
        encoding="utf-8",
    )
    return FOOTPRINT, CHECK_PCB


def main() -> int:
    fp, pcb = write_files()
    print(status("OK", f"Wrote J2 footprint: {fp}"))
    print(status("OK", f"Wrote 1:1 check PCB: {pcb}"))
    print(status("INFO", "Export PDF with: kicad-cli pcb export pdf --layers F.Cu,F.SilkS,F.Fab,Edge.Cuts"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
