#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
from uuid import uuid4

import yaml

try:
    from .kicad_tools import HARDWARE_DIR, PROJECT_ROOT, status
except ImportError:
    from kicad_tools import HARDWARE_DIR, PROJECT_ROOT, status


CONFIG = PROJECT_ROOT / "config" / "b2b_fit_check.yaml"
PCB = HARDWARE_DIR / "b2b_fit_check.kicad_pcb"
PRO = HARDWARE_DIR / "b2b_fit_check.kicad_pro"


def uid() -> str:
    return str(uuid4())


def line(start: tuple[float, float], end: tuple[float, float]) -> str:
    return (
        f'  (gr_line (start {start[0]:.3f} {start[1]:.3f}) '
        f'(end {end[0]:.3f} {end[1]:.3f})\n'
        f'    (stroke (width 0.100) (type default)) (layer "Edge.Cuts") (tstamp {uid()}))'
    )


def text(label: str, at: tuple[float, float], layer: str = "F.SilkS", size: float = 1.0) -> str:
    return (
        f'  (gr_text "{label}" (at {at[0]:.3f} {at[1]:.3f} 0) (layer "{layer}") (tstamp {uid()})\n'
        f'    (effects (font (size {size:.3f} {size:.3f}) (thickness 0.150)))\n'
        f'  )'
    )


def load_config() -> dict:
    with CONFIG.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def unresolved_connectors(cfg: dict) -> list[str]:
    missing: list[str] = []
    for ref, item in (cfg.get("connectors") or {}).items():
        for key in ("x_mm", "y_mm", "rotation_deg", "pin1_orientation"):
            if item.get(key) in (None, ""):
                missing.append(f"{ref}.{key}")
    return missing


def connector_placeholder(ref: str, item: dict) -> str:
    x = float(item["x_mm"])
    y = float(item["y_mm"])
    rot = float(item["rotation_deg"])
    mpn = item["carrier_mpn"]
    return f'''  (footprint "MECH_ONLY:DF40C-100DS-0.4V51_MECH_PLACEHOLDER" (layer "F.Cu")
    (tstamp {uid()})
    (at {x:.3f} {y:.3f} {rot:.3f})
    (descr "Mechanical placeholder only. Replace with verified Hirose footprint before fab.")
    (property "Reference" "{ref}" (at 0 -3.000 {rot:.3f}) (layer "F.SilkS") (tstamp {uid()})
      (effects (font (size 1.000 1.000) (thickness 0.150)))
    )
    (property "Value" "{mpn}" (at 0 3.000 {rot:.3f}) (layer "F.Fab") (tstamp {uid()})
      (effects (font (size 1.000 1.000) (thickness 0.150)))
    )
    (fp_text reference "{ref}" (at 0 -3.000 {rot:.3f}) (layer "F.SilkS") (tstamp {uid()})
      (effects (font (size 1.000 1.000) (thickness 0.150)))
    )
    (fp_text value "{mpn}" (at 0 3.000 {rot:.3f}) (layer "F.Fab") (tstamp {uid()})
      (effects (font (size 1.000 1.000) (thickness 0.150)))
    )
    (fp_line (start -12.000 -2.000) (end 12.000 -2.000) (stroke (width 0.100) (type default)) (layer "F.Fab") (tstamp {uid()}))
    (fp_line (start 12.000 -2.000) (end 12.000 2.000) (stroke (width 0.100) (type default)) (layer "F.Fab") (tstamp {uid()}))
    (fp_line (start 12.000 2.000) (end -12.000 2.000) (stroke (width 0.100) (type default)) (layer "F.Fab") (tstamp {uid()}))
    (fp_line (start -12.000 2.000) (end -12.000 -2.000) (stroke (width 0.100) (type default)) (layer "F.Fab") (tstamp {uid()}))
    (fp_circle (center -13.000 -2.500) (end -12.500 -2.500) (stroke (width 0.150) (type default)) (fill none) (layer "F.SilkS") (tstamp {uid()}))
  )'''


def generate(cfg: dict) -> str:
    board = cfg["board"]
    w = float(board["width_mm"])
    h = float(board["height_mm"])
    edges = "\n".join([line((0, 0), (w, 0)), line((w, 0), (w, h)), line((w, h), (0, h)), line((0, h), (0, 0))])
    center = "\n".join(
        [
            line((w / 2, 0), (w / 2, h)).replace('"Edge.Cuts"', '"Dwgs.User"'),
            line((0, h / 2), (w, h / 2)).replace('"Edge.Cuts"', '"Dwgs.User"'),
        ]
    )
    footprints = "\n".join(
        connector_placeholder(ref, item)
        for ref, item in (cfg.get("connectors") or {}).items()
    )
    return f'''(kicad_pcb
  (version 20221018)
  (generator "ai-glasses-b2b-fit-check")
  (general (thickness {float(board["thickness_mm"]):.3f}))
  (paper "A4")
  (title_block
    (title "Radxa CM4 B2B Fit-Check Coupon")
    (rev "{cfg["project"]["revision"]}")
    (comment 1 "2-layer connector-only mechanical coupon.")
    (comment 2 "Do not fabricate until DF40C footprint and CM4 STEP assembly are verified.")
  )
  (layers
    (0 "F.Cu" signal)
    (31 "B.Cu" signal)
    (32 "B.Adhes" user)
    (33 "F.Adhes" user)
    (34 "B.Paste" user)
    (35 "F.Paste" user)
    (36 "B.SilkS" user)
    (37 "F.SilkS" user)
    (38 "B.Mask" user)
    (39 "F.Mask" user)
    (44 "Edge.Cuts" user)
    (45 "Margin" user)
    (46 "B.CrtYd" user)
    (47 "F.CrtYd" user)
    (48 "B.Fab" user)
    (49 "F.Fab" user)
    (50 "User.1" user)
    (51 "User.2" user)
    (52 "User.3" user)
    (53 "User.4" user)
    (54 "User.5" user)
    (55 "User.6" user)
    (56 "User.7" user)
    (57 "User.8" user)
    (58 "User.9" user)
  )
  (setup (pad_to_mask_clearance 0.050))
  (net 0 "")
{edges}
{center}
{text("MECH FIT CHECK ONLY - NO POWER", (w / 2, 5), size=1.2)}
{text("DF40C-100DS x3, 1.5mm mated height target", (w / 2, h - 5), layer="F.Fab")}
{footprints}
)
'''


def main() -> int:
    cfg = load_config()
    missing = unresolved_connectors(cfg)
    PRO.write_text(
        '{\n  "meta": {"filename": "b2b_fit_check.kicad_pro", "version": 1},\n'
        '  "project": {"name": "b2b_fit_check", "note": "Connector-only CM4 B2B fit-check coupon"}\n}\n',
        encoding="utf-8",
    )
    if missing:
        print(status("ERROR", "B2B connector XY/rotation is not resolved; refusing to generate a board with guessed placement."))
        for item in missing:
            print(status("ERROR", f"  - missing {item} in {CONFIG}"))
        print(status("INFO", "Import the official CM4 DXF/STEP into KiCad/mechanical CAD, place the verified DF40C footprints, then record XY/rotation in the YAML."))
        return 2
    PCB.write_text(generate(cfg), encoding="utf-8")
    print(status("OK", f"Generated B2B fit-check PCB: {PCB}"))
    print(status("WARN", "Uses a mechanical placeholder footprint; replace with verified Hirose footprint before fabrication."))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
