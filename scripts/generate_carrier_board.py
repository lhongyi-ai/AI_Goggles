#!/usr/bin/env python3
"""Generate the ai_glasses_carrier_v1 PCB skeleton.

This is intentionally a *pre-layout skeleton*, not a finished board:
  - 6-layer stack (GND/power planes) per config/design_rules.yaml
  - Board outline at target dimensions (placeholder until official CM4 STEP)
  - All V1 nets declared from config/cm4_pins.yaml
  - 4 mounting holes, board ID text

It does NOT place B2B connectors, the camera FPC, USB-C, or any real footprint.
Per requirements doc v1.1 Section 3.3, real layout may not begin until the pin
assignment in config/cm4_v1_pin_assignment.yaml is FROZEN. This script checks
that gate and reports honestly instead of emitting an unverified placement.
"""
from __future__ import annotations

from pathlib import Path
from uuid import uuid4

import yaml

try:
    from .kicad_tools import (
        HARDWARE_DIR,
        PROJECT_ROOT,
        ensure_output_dirs,
        load_board_config,
        status,
    )
except ImportError:
    from kicad_tools import (
        HARDWARE_DIR,
        PROJECT_ROOT,
        ensure_output_dirs,
        load_board_config,
        status,
    )


PCB_FILE = HARDWARE_DIR / "ai_glasses_carrier.kicad_pcb"
SCH_FILE = HARDWARE_DIR / "ai_glasses_carrier.kicad_sch"
SYM_LIB_FILE = HARDWARE_DIR / "AI_Glasses.kicad_sym"
SYM_LIB_TABLE = HARDWARE_DIR / "sym-lib-table"
FP_LIB_TABLE = HARDWARE_DIR / "fp-lib-table"
CM4_PINS_FILE = PROJECT_ROOT / "config" / "cm4_pins.yaml"


# 6-layer stack (matches config/design_rules.yaml stackup).
LAYER_BLOCK = """  (layers
    (0 "F.Cu" signal)
    (1 "In1.Cu" power)
    (2 "In2.Cu" power)
    (3 "In3.Cu" signal)
    (4 "In4.Cu" power)
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
  )"""


def uid() -> str:
    return str(uuid4())


def line(start: tuple[float, float], end: tuple[float, float]) -> str:
    return (
        f'  (gr_line (start {start[0]:.3f} {start[1]:.3f}) '
        f'(end {end[0]:.3f} {end[1]:.3f})\n'
        f'    (stroke (width 0.100) (type default)) (layer "Edge.Cuts") (tstamp {uid()}))'
    )


def mounting_hole(ref: str, x: float, y: float) -> str:
    return f'''  (footprint "MountingHole:MountingHole_2.2mm_M2"
    (version 20240108)
    (generator "ai-glasses-python")
    (layer "F.Cu")
    (at {x:.3f} {y:.3f})
    (descr "Mounting Hole 2.2mm, M2, no annular")
    (tags "mountinghole M2")
    (property "Reference" "{ref}"
      (at 0 -3.150 0)
      (layer "F.SilkS")
      (effects (font (size 1.000 1.000) (thickness 0.150)))
    )
    (property "Value" "MountingHole_2.2mm_M2"
      (at 0 3.150 0)
      (layer "F.Fab")
      (effects (font (size 1.000 1.000) (thickness 0.150)))
    )
    (attr exclude_from_pos_files exclude_from_bom)
    (duplicate_pad_numbers_are_jumpers no)
    (fp_circle
      (center 0 0)
      (end 2.200 0)
      (stroke (width 0.150) (type solid))
      (fill no)
      (layer "Cmts.User")
    )
    (fp_circle
      (center 0 0)
      (end 2.450 0)
      (stroke (width 0.050) (type solid))
      (fill no)
      (layer "F.CrtYd")
    )
    (fp_text user "${{REFERENCE}}"
      (at 0 0 0)
      (layer "F.Fab")
      (effects (font (size 1.000 1.000) (thickness 0.150)))
    )
    (pad "" np_thru_hole circle
      (at 0 0)
      (size 2.200 2.200)
      (drill 2.200)
      (layers "*.Cu" "*.Mask")
    )
    (embedded_fonts no)
  )'''


def collect_nets() -> list[str]:
    """Build the full V1 net list from cm4_pins.yaml (board_net + carrier_only)."""
    with CM4_PINS_FILE.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)

    nets: list[str] = []

    def add(name: str | None) -> None:
        if name and name not in nets:
            nets.append(name)

    # Always have GND first after the empty net.
    add("GND")

    for group in (data.get("signals") or {}).values():
        for entry in group:
            add(entry.get("board_net"))

    carrier = data.get("carrier_only_nets") or {}
    for group in carrier.values():
        for item in group:
            # Some YAML rows are comma-joined inline lists; split defensively.
            for name in str(item).split(","):
                add(name.strip())

    return nets


def generate_pcb_text() -> str:
    config = load_board_config()
    width = config.board.width_mm
    height = config.board.height_mm

    net_names = ["", *collect_nets()]
    nets = "\n".join(f'  (net {i} "{name}")' for i, name in enumerate(net_names))

    edge = "\n".join(
        [
            line((0, 0), (width, 0)),
            line((width, 0), (width, height)),
            line((width, height), (0, height)),
            line((0, height), (0, 0)),
        ]
    )

    holes = "\n".join(
        [
            mounting_hole("H1", 4.0, 4.0),
            mounting_hole("H2", width - 4.0, 4.0),
            mounting_hole("H3", 4.0, height - 4.0),
            mounting_hole("H4", width - 4.0, height - 4.0),
        ]
    )

    title = "AI Glasses Carrier V1 (RK3576/CM4) - PRE-LAYOUT SKELETON"

    return f'''(kicad_pcb
  (version 20221018)
  (generator "ai-glasses-python")
  (general
    (thickness {config.board.thickness_mm if hasattr(config.board, "thickness_mm") else 1.6})
  )
  (paper "A4")
  (title_block
    (title "{title}")
    (rev "{config.project.revision}")
    (comment 1 "Outline is placeholder until official Radxa CM4 STEP is imported.")
    (comment 2 "No B2B/USB/camera footprints: pin assignment not FROZEN (Sec 3.3).")
  )
{LAYER_BLOCK}
  (setup
    (pad_to_mask_clearance 0.050)
  )
{nets}
{edge}
  (gr_text "{title}" (at {width / 2:.3f} {height / 2 - 3:.3f} 0) (layer "F.Fab") (tstamp {uid()})
    (effects (font (size 1.500 1.500) (thickness 0.150)))
  )
  (gr_text "rev {config.project.revision}  DO NOT FAB" (at {width / 2:.3f} {height / 2 + 3:.3f} 0) (layer "F.SilkS") (tstamp {uid()})
    (effects (font (size 1.000 1.000) (thickness 0.150)))
  )
{holes}
)
'''


# ── Schematic symbol geometry (mm) ──────────────────────────────────────────
PITCH = 2.54        # pin-to-pin spacing
PIN_LEN = 5.08      # pin stub length
HALF_W = 12.7       # half box width


def _esc(text: str) -> str:
    return text.replace("\\", "\\\\").replace('"', '\\"')


def _footprint(comp) -> str:
    return getattr(comp, "footprint", "") or ""


def _is_no_connect(net: str | None) -> bool:
    if net is None:
        return True
    normalized = net.strip().upper()
    return normalized in {"", "NC", "NO_CONNECT", "UNUSED", "DNP"} or normalized.startswith("NC:")


def _comp_geometry(n_pins: int) -> tuple[int, int, float]:
    """Return (n_left, n_right, half_height) for a component with n_pins."""
    n_left = (n_pins + 1) // 2
    n_right = n_pins - n_left
    rows = max(n_left, n_right, 1)
    half_h = ((rows - 1) * PITCH + 4 * PITCH) / 2
    return n_left, n_right, half_h


def _pin_def(x: float, y: float, ang: int, name: str, number: int) -> str:
    return (
        f'      (pin passive line (at {x:.3f} {y:.3f} {ang}) (length {PIN_LEN:.3f})\n'
        f'        (name "{_esc(name)}" (effects (font (size 1.000 1.000))))\n'
        f'        (number "{number}" (effects (font (size 1.000 1.000))))\n'
        f'      )'
    )


def _lib_symbol(comp, *, external: bool = False) -> str:
    """Build a generic box lib_symbol for one component."""
    n = len(comp.pins)
    n_left, n_right, half_h = _comp_geometry(n)
    prefix = "".join(ch for ch in comp.ref if not ch.isdigit()) or "U"

    rect = (
        f'      (rectangle (start {-HALF_W:.3f} {half_h:.3f}) '
        f'(end {HALF_W:.3f} {-half_h:.3f})\n'
        f'        (stroke (width 0.254) (type default)) (fill (type background)))'
    )

    pins: list[str] = []
    top_l = (n_left - 1) / 2 * PITCH
    for i in range(n_left):
        name, _ = comp.pins[i]
        pins.append(_pin_def(-HALF_W - PIN_LEN, top_l - i * PITCH, 0, name, i + 1))
    top_r = (n_right - 1) / 2 * PITCH
    for j in range(n_right):
        name, _ = comp.pins[n_left + j]
        pins.append(_pin_def(HALF_W + PIN_LEN, top_r - j * PITCH, 180, name, n_left + j + 1))

    symbol_id = comp.ref if external else f"aiglasses:{comp.ref}"
    indent = "  " if external else "    "
    body_indent = "    " if external else "      "
    return f'''{indent}(symbol "{symbol_id}"
      (pin_names (offset 1.016)) (in_bom yes) (on_board yes)
      (property "Reference" "{prefix}" (at 0 {half_h + 2.54:.3f} 0) (effects (font (size 1.270 1.270))))
      (property "Value" "{_esc(comp.value)}" (at 0 {-half_h - 2.54:.3f} 0) (effects (font (size 1.270 1.270))))
      (property "Footprint" "{_esc(_footprint(comp))}" (at 0 0 0) (effects (font (size 1.270 1.270)) hide))
      (property "Datasheet" "~" (at 0 0 0) (effects (font (size 1.270 1.270)) hide))
{body_indent}(symbol "{comp.ref}_0_1"
{rect}
{body_indent})
{body_indent}(symbol "{comp.ref}_1_1"
{chr(10).join(pins)}
{body_indent})
{indent})'''


def _glabel(net: str, x: float, y: float, ang: int) -> str:
    return (
        f'  (global_label "{_esc(net)}" (shape input) (at {x:.3f} {y:.3f} {ang})\n'
        f'    (effects (font (size 1.270 1.270)))\n'
        f'    (uuid "{uid()}")\n'
        f'  )'
    )


def _no_connect(x: float, y: float) -> str:
    return f'  (no_connect (at {x:.3f} {y:.3f}) (uuid "{uid()}"))'


def _place(comp, x: float, y: float, root_uuid: str) -> tuple[str, list[str], list[str]]:
    """Return (symbol instance, global labels, no-connect markers) at (x, y)."""
    n = len(comp.pins)
    n_left, n_right, half_h = _comp_geometry(n)

    pin_uuids = "\n".join(f'    (pin "{k + 1}" (uuid "{uid()}"))' for k in range(n))
    instance = f'''  (symbol (lib_id "aiglasses:{comp.ref}") (at {x:.3f} {y:.3f} 0) (unit 1)
    (in_bom yes) (on_board yes) (dnp no)
    (uuid "{uid()}")
    (property "Reference" "{comp.ref}" (at {x:.3f} {y - half_h - 2.54:.3f} 0) (effects (font (size 1.270 1.270))))
    (property "Value" "{_esc(comp.value)}" (at {x:.3f} {y + half_h + 2.54:.3f} 0) (effects (font (size 1.270 1.270))))
    (property "Footprint" "{_esc(_footprint(comp))}" (at {x:.3f} {y:.3f} 0) (effects (font (size 1.270 1.270)) hide))
    (property "Datasheet" "~" (at {x:.3f} {y:.3f} 0) (effects (font (size 1.270 1.270)) hide))
{pin_uuids}
    (instances (project "ai_glasses_carrier" (path "/{root_uuid}" (reference "{comp.ref}") (unit 1))))
  )'''

    labels: list[str] = []
    no_connects: list[str] = []
    top_l = (n_left - 1) / 2 * PITCH
    for i in range(n_left):
        _, net = comp.pins[i]
        px = x - HALF_W - PIN_LEN
        py = y - (top_l - i * PITCH)
        if _is_no_connect(net):
            no_connects.append(_no_connect(px, py))
        else:
            labels.append(_glabel(net, px, py, 180))
    top_r = (n_right - 1) / 2 * PITCH
    for j in range(n_right):
        _, net = comp.pins[n_left + j]
        px = x + HALF_W + PIN_LEN
        py = y - (top_r - j * PITCH)
        if _is_no_connect(net):
            no_connects.append(_no_connect(px, py))
        else:
            labels.append(_glabel(net, px, py, 0))
    return instance, labels, no_connects


def generate_sch_text() -> str:
    """Generate a KiCad schematic with real component symbols + net labels.

    Each component from scripts/carrier_bom.py is drawn as a box symbol with
    named pins; every pin carries a global_label of its net, so same-named nets
    are electrically connected across the sheet.  Components are packed into
    columns sized to a custom (User) page so everything fits.
    """
    try:
        from .carrier_bom import COMPONENTS
    except ImportError:
        from carrier_bom import COMPONENTS

    config = load_board_config()
    root_uuid = uid()

    # ── Layout: pack components into columns (shortest-column-first) ─────────
    n_cols = 4
    col_w = 145.0
    margin_x = 25.0
    margin_top = 45.0
    v_gap = 18.0
    label_pad = 6.0     # extra space above box for the reference designator

    def snap(v: float) -> float:
        # Snap to the 1.27mm grid so all pin/label endpoints land on-grid
        # (clears KiCad ERC "endpoint_off_grid" warnings).
        return round(v / 1.27) * 1.27

    col_y = [margin_top] * n_cols
    placed: list[tuple[object, float, float]] = []
    for comp in COMPONENTS:
        _, _, half_h = _comp_geometry(len(comp.pins))
        c = min(range(n_cols), key=lambda k: col_y[k])
        cx = snap(margin_x + col_w / 2 + c * col_w)
        cy = snap(col_y[c] + half_h + label_pad)
        placed.append((comp, cx, cy))
        col_y[c] = cy + half_h + label_pad + v_gap

    paper_w = margin_x * 2 + n_cols * col_w
    paper_h = max(col_y) + margin_top

    lib_defs: list[str] = []
    instances: list[str] = []
    labels: list[str] = []
    no_connects: list[str] = []
    for comp, cx, cy in placed:
        lib_defs.append(_lib_symbol(comp))
        inst, labs, ncs = _place(comp, cx, cy, root_uuid)
        instances.append(inst)
        labels.extend(labs)
        no_connects.extend(ncs)

    header = (
        f'  (text "AI Glasses Carrier V1 (RK3576/CM4) — EVT Schematic   |   '
        f'{len(COMPONENTS)} components   |   '
        f'CM4 pin assignment is REVIEW/verified; pre-layout gates remain '
        f'(see config/cm4_v1_pin_assignment.yaml)"\n'
        f'    (at {margin_x:.3f} 20.000 0)\n'
        f'    (effects (font (size 2.000 2.000) (bold yes)) (justify left))\n'
        f'    (uuid "{uid()}")\n'
        f'  )'
    )

    lib_block = "\n".join(lib_defs)
    body = "\n".join([header, *instances, *labels, *no_connects])

    return f'''(kicad_sch
  (version 20230121)
  (generator "ai-glasses-python")
  (uuid "{root_uuid}")
  (paper "User" {paper_w:.3f} {paper_h:.3f})
  (title_block
    (title "AI Glasses Carrier V1 (RK3576/CM4) — EVT")
    (rev "{config.project.revision}")
    (company "AI Glasses Project")
    (comment 1 "Radxa CM4 (RK3576) Carrier Board — EVT")
    (comment 2 "Components: scripts/carrier_bom.py | Pin table: config/cm4_v1_pin_assignment.yaml")
    (comment 3 "P0: Camera MIPI-CSI | PDM Mic x2 | I2S Audio | USB-C | Wi-Fi/BT | Debug")
    (comment 4 "P1: 1S Li-Po | Fuel Gauge | IMU | Vibration")
  )
  (lib_symbols
{lib_block}
  )
{body}
  (sheet_instances
    (path "/" (page "1"))
  )
)
'''


def generate_symbol_library_text() -> str:
    try:
        from .carrier_bom import COMPONENTS
    except ImportError:
        from carrier_bom import COMPONENTS

    symbols = "\n".join(_lib_symbol(comp, external=True) for comp in COMPONENTS)
    return f'''(kicad_symbol_lib
  (version 20231120)
  (generator "ai-glasses-python")
{symbols}
)
'''


def write_symbol_table() -> None:
    SYM_LIB_TABLE.write_text(
        '(sym_lib_table\n'
        '  (version 7)\n'
        '  (lib (name "aiglasses")(type "KiCad")(uri "${KIPRJMOD}/AI_Glasses.kicad_sym")(options "")'
        '(descr "Project-generated AI Glasses schematic symbols"))\n'
        ')\n',
        encoding="utf-8",
    )


def write_footprint_table() -> None:
    FP_LIB_TABLE.write_text(
        '(fp_lib_table\n'
        '  (version 7)\n'
        '  (lib (name "AI_Glasses")(type "KiCad")(uri "${KIPRJMOD}/AI_Glasses.pretty")(options "")'
        '(descr "Project footprints for AI Glasses carrier"))\n'
        ')\n',
        encoding="utf-8",
    )


def write_files() -> tuple[Path, Path]:
    ensure_output_dirs()
    PCB_FILE.write_text(generate_pcb_text(), encoding="utf-8")
    SYM_LIB_FILE.write_text(generate_symbol_library_text(), encoding="utf-8")
    write_symbol_table()
    write_footprint_table()
    try:
        from .generate_verify_footprints import write_verify_footprints
    except ImportError:
        from generate_verify_footprints import write_verify_footprints

    write_verify_footprints()
    SCH_FILE.write_text(generate_sch_text(), encoding="utf-8")
    return PCB_FILE, SCH_FILE


def main() -> int:
    pcb_path, sch_path = write_files()
    net_count = len(collect_nets())
    print(status("OK", f"Generated 6-layer carrier skeleton: {pcb_path}"))
    print(status("OK", f"Generated schematic skeleton: {sch_path}"))
    print(status("INFO", f"Declared {net_count} V1 nets from config/cm4_pins.yaml."))

    # Honest gate check: tell the user whether real layout may proceed.
    try:
        try:
            from .check_pin_freeze import main as gate_main
        except ImportError:
            from check_pin_freeze import main as gate_main

        print()
        print(status("INFO", "Checking pin-assignment freeze gate (Section 3.3)..."))
        gate_code = gate_main()
        if gate_code != 0:
            print(status("WARN", "Skeleton only. Add real footprints AFTER the gate passes."))
    except Exception as exc:
        print(status("WARN", f"Gate check skipped: {exc}"))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
