#!/usr/bin/env python3
"""Generate the AI Glasses V2 (RK3576 chip-down) pre-layout system schematic.

Self-contained (does not touch the V1 native sources). Reads the component +
net master in chipdown_bom.py and emits, into v2_chipdown/hardware/:

  ai_glasses_v2_chipdown.kicad_sch   one system sheet, box symbols + net labels
  AI_Glasses_V2.kicad_sym            generated symbol library
  ai_glasses_v2_chipdown.kicad_pro   minimal project so KiCad can open it
  sym-lib-table / fp-lib-table       library tables

Method mirrors the V1 generator (scripts/generate_carrier_board.py): each
component is a rectangle with named pins; every pin drops a global_label of its
net, so same-named nets are joined across the one sheet. This is the pre-PCB-
layout artifact only — NO .kicad_pcb is produced (layout is gated behind the
Gate 0 mechanical review; see docs/03_workflow_phases.md).

Each placed symbol also carries BOM_ID / Board / Assembly / Priority / Gate as
schematic fields so `kicad-cli sch export bom` yields a rich, traceable BOM.
"""
from __future__ import annotations

import sys
from pathlib import Path
from uuid import NAMESPACE_URL, uuid5

ROOT = Path(__file__).resolve().parent.parent          # v2_chipdown/
HW = ROOT / "hardware"
SCH_FILE = HW / "ai_glasses_v2_chipdown.kicad_sch"
SYM_FILE = HW / "AI_Glasses_V2.kicad_sym"
PRO_FILE = HW / "ai_glasses_v2_chipdown.kicad_pro"
SYM_LIB_TABLE = HW / "sym-lib-table"
FP_LIB_TABLE = HW / "fp-lib-table"
PROJECT = "ai_glasses_v2_chipdown"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from chipdown_bom import COMPONENTS, all_nets, net_meta  # noqa: E402


# ── geometry (mm) ────────────────────────────────────────────────────────────
PITCH = 2.54
PIN_LEN = 5.08
HALF_W = 13.97          # 11 * 1.27 — keep pin tips on the 1.27 mm connection grid


_UID_COUNTER = 0


def uid() -> str:
    global _UID_COUNTER
    _UID_COUNTER += 1
    return str(uuid5(NAMESPACE_URL, f"{PROJECT}:{_UID_COUNTER}"))


def _esc(text: str) -> str:
    return text.replace("\\", "\\\\").replace('"', '\\"')


def _is_nc(net: str | None) -> bool:
    if net is None:
        return True
    n = net.strip().upper()
    return n in {"", "NC", "NO_CONNECT", "UNUSED", "DNP"}


def _geom(n_pins: int) -> tuple[int, int, float]:
    n_left = (n_pins + 1) // 2
    n_right = n_pins - n_left
    rows = max(n_left, n_right, 1)
    half_h = ((rows - 1) * PITCH + 4 * PITCH) / 2
    return n_left, n_right, half_h


def _pin(x: float, y: float, ang: int, name: str, number: int) -> str:
    return (
        f'      (pin passive line (at {x:.3f} {y:.3f} {ang}) (length {PIN_LEN:.3f})\n'
        f'        (name "{_esc(name)}" (effects (font (size 1.000 1.000))))\n'
        f'        (number "{number}" (effects (font (size 1.000 1.000))))\n'
        f'      )'
    )


def _lib_symbol(comp, *, external: bool = False) -> str:
    n = len(comp.pins)
    n_left, n_right, half_h = _geom(n)
    prefix = "".join(ch for ch in comp.ref if not ch.isdigit()) or "U"
    rect = (
        f'      (rectangle (start {-HALF_W:.3f} {half_h:.3f}) (end {HALF_W:.3f} {-half_h:.3f})\n'
        f'        (stroke (width 0.254) (type default)) (fill (type background)))'
    )
    pins: list[str] = []
    top_l = (n_left - 1) / 2 * PITCH
    for i in range(n_left):
        name, _ = comp.pins[i]
        pins.append(_pin(-HALF_W - PIN_LEN, top_l - i * PITCH, 0, name, i + 1))
    top_r = (n_right - 1) / 2 * PITCH
    for j in range(n_right):
        name, _ = comp.pins[n_left + j]
        pins.append(_pin(HALF_W + PIN_LEN, top_r - j * PITCH, 180, name, n_left + j + 1))

    symbol_id = comp.ref if external else f"aiglassesv2:{comp.ref}"
    indent = "  " if external else "    "
    body = "    " if external else "      "
    return f'''{indent}(symbol "{symbol_id}"
      (pin_names (offset 1.016)) (in_bom yes) (on_board yes)
      (property "Reference" "{prefix}" (at 0 {half_h + 2.54:.3f} 0) (effects (font (size 1.270 1.270))))
      (property "Value" "{_esc(comp.value)}" (at 0 {-half_h - 2.54:.3f} 0) (effects (font (size 1.270 1.270))))
      (property "Footprint" "" (at 0 0 0) (effects (font (size 1.270 1.270)) hide))
      (property "Datasheet" "~" (at 0 0 0) (effects (font (size 1.270 1.270)) hide))
{body}(symbol "{comp.ref}_0_1"
{rect}
{body})
{body}(symbol "{comp.ref}_1_1"
{chr(10).join(pins)}
{body})
{indent})'''


LABEL_META_FIELDS = [
    ("SIG_NAME", "name"),
    ("SIG_DOMAIN", "dom"),
    ("SIG_KIND", "kind"),
    ("SIG_DIR", "direction"),
    ("SIG_DEFAULT", "default"),
    ("SIG_PULL", "pull"),
    ("SIG_XDOM", "xdom"),
    ("SIG_OFF_HIGH", "off_high"),
    ("SIG_SERIES", "series"),
    ("SIG_ESD", "esd"),
    ("SIG_DIFF_PAIR", "diff_pair"),
    ("SIG_PINMUX", "pinmux"),
    ("SIG_DT", "dt"),
    ("SIG_DRIVER", "driver"),
    ("SIG_ISOLATION", "isolation"),
]


def _label_props(net: str, x: float, y: float) -> str:
    meta = net_meta(net)
    props = []
    for prop_name, meta_key in LABEL_META_FIELDS:
        props.append(
            f'    (property "{prop_name}" "{_esc(meta[meta_key])}" (at {x:.3f} {y:.3f} 0) '
            f'(effects (font (size 0.800 0.800)) hide))'
        )
    return "\n".join(props)


def _glabel(net: str, x: float, y: float, ang: int) -> str:
    return (
        f'  (global_label "{_esc(net)}" (shape bidirectional) (at {x:.3f} {y:.3f} {ang})\n'
        f'    (effects (font (size 1.000 1.000)) (justify left))\n'
        f'{_label_props(net, x, y)}\n'
        f'    (uuid "{uid()}")\n'
        f'  )'
    )


def _nc(x: float, y: float) -> str:
    return f'  (no_connect (at {x:.3f} {y:.3f}) (uuid "{uid()}"))'


def _extra_props(comp, x: float, y: float, half_h: float) -> str:
    fields = [
        ("BOM_ID", comp.bom_id),
        ("Board", comp.board),
        ("Assembly", comp.assembly),
        ("Priority", comp.pri),
        ("Gate", comp.gate),
        # intended package only — the KiCad Footprint field is left empty on purpose:
        # footprints are a layout-phase deliverable, gated behind Gate 0 (docs/03).
        ("Package", comp.footprint),
    ]
    out = []
    for k, val in fields:
        out.append(
            f'    (property "{k}" "{_esc(val)}" (at {x:.3f} {y:.3f} 0) '
            f'(effects (font (size 1.000 1.000)) hide))'
        )
    return "\n".join(out)


def _place(comp, x: float, y: float, root_uuid: str) -> tuple[str, list[str], list[str]]:
    n = len(comp.pins)
    n_left, n_right, half_h = _geom(n)
    dnp = "yes" if comp.assembly.upper() == "DNP" else "no"
    pin_uuids = "\n".join(f'    (pin "{k + 1}" (uuid "{uid()}"))' for k in range(n))
    instance = f'''  (symbol (lib_id "aiglassesv2:{comp.ref}") (at {x:.3f} {y:.3f} 0) (unit 1)
    (in_bom yes) (on_board yes) (dnp {dnp})
    (uuid "{uid()}")
    (property "Reference" "{comp.ref}" (at {x:.3f} {y - half_h - 2.54:.3f} 0) (effects (font (size 1.270 1.270))))
    (property "Value" "{_esc(comp.value)}" (at {x:.3f} {y + half_h + 2.54:.3f} 0) (effects (font (size 1.270 1.270))))
    (property "Footprint" "" (at {x:.3f} {y:.3f} 0) (effects (font (size 1.270 1.270)) hide))
    (property "Datasheet" "~" (at {x:.3f} {y:.3f} 0) (effects (font (size 1.270 1.270)) hide))
{_extra_props(comp, x, y, half_h)}
{pin_uuids}
    (instances (project "{PROJECT}" (path "/{root_uuid}" (reference "{comp.ref}") (unit 1))))
  )'''

    labels: list[str] = []
    ncs: list[str] = []
    top_l = (n_left - 1) / 2 * PITCH
    for i in range(n_left):
        _, net = comp.pins[i]
        px, py = x - HALF_W - PIN_LEN, y - (top_l - i * PITCH)
        (ncs if _is_nc(net) else labels).append(
            _nc(px, py) if _is_nc(net) else _glabel(net, px, py, 180))
    top_r = (n_right - 1) / 2 * PITCH
    for j in range(n_right):
        _, net = comp.pins[n_left + j]
        px, py = x + HALF_W + PIN_LEN, y - (top_r - j * PITCH)
        (ncs if _is_nc(net) else labels).append(
            _nc(px, py) if _is_nc(net) else _glabel(net, px, py, 0))
    return instance, labels, ncs


def generate_sch_text() -> str:
    root_uuid = uid()
    n_cols = 5
    col_w = 165.0
    margin_x = 25.0
    margin_top = 55.0
    v_gap = 20.0
    label_pad = 8.0

    def snap(v: float) -> float:
        return round(v / 1.27) * 1.27

    col_y = [margin_top] * n_cols
    placed: list[tuple[object, float, float]] = []
    for comp in COMPONENTS:
        _, _, half_h = _geom(len(comp.pins))
        c = min(range(n_cols), key=lambda k: col_y[k])
        cx = snap(margin_x + col_w / 2 + c * col_w)
        cy = snap(col_y[c] + half_h + label_pad)
        placed.append((comp, cx, cy))
        col_y[c] = cy + half_h + label_pad + v_gap

    paper_w = margin_x * 2 + n_cols * col_w
    paper_h = max(col_y) + margin_top

    lib_defs, instances, labels, ncs = [], [], [], []
    for comp, cx, cy in placed:
        lib_defs.append(_lib_symbol(comp))
        inst, labs, nc = _place(comp, cx, cy, root_uuid)
        instances.append(inst)
        labels.extend(labs)
        ncs.extend(nc)

    n_fit = sum(1 for c in COMPONENTS if c.assembly == "Fit")
    n_hold = sum(1 for c in COMPONENTS if c.assembly == "HOLD")
    n_dnp = sum(1 for c in COMPONENTS if c.assembly == "DNP")
    n_tbd = sum(1 for c in COMPONENTS if c.assembly == "TBD")
    header = (
        f'  (text "AI Glasses V2 (RK3576 Chip-Down) — PRE-LAYOUT SYSTEM SCHEMATIC   |   '
        f'{len(COMPONENTS)} components ({n_fit} Fit / {n_hold} HOLD / {n_dnp} DNP / {n_tbd} TBD)   |   '
        f'{len(all_nets())} nets   |   Functional-block capture: power tree + AON control plane + '
        f'interface buses. Ball-level detail + PCB layout gated behind Gate 0/1/2 '
        f'(see docs/03_workflow_phases.md). Source: scripts/chipdown_bom.py"\n'
        f'    (at {margin_x:.3f} 22.000 0)\n'
        f'    (effects (font (size 2.200 2.200) (bold yes)) (justify left))\n'
        f'    (uuid "{uid()}")\n'
        f'  )'
    )

    lib_block = "\n".join(lib_defs)
    body = "\n".join([header, *instances, *labels, *ncs])
    return f'''(kicad_sch
  (version 20230121)
  (generator "ai-glasses-python")
  (uuid "{root_uuid}")
  (paper "User" {paper_w:.3f} {paper_h:.3f})
  (title_block
    (title "AI Glasses V2 (RK3576 Chip-Down) — Pre-Layout System Schematic")
    (rev "0.04")
    (company "AI Glasses Project")
    (comment 1 "AON-always-on + RK3576 demand-burst. Source of truth: scripts/chipdown_bom.py")
    (comment 2 "Power tree: Buck + Load-Switch (docs/04); AON control plane (docs/07)")
    (comment 3 "NO PCB yet: layout gated behind Gate 0 mechanical (docs/03)")
    (comment 4 "Fit / HOLD / DNP / TBD per-part; gates in the Gate field")
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
    symbols = "\n".join(_lib_symbol(c, external=True) for c in COMPONENTS)
    return f'''(kicad_symbol_lib
  (version 20231120)
  (generator "ai-glasses-python")
{symbols}
)
'''


def write_tables() -> None:
    SYM_LIB_TABLE.write_text(
        '(sym_lib_table\n  (version 7)\n'
        '  (lib (name "aiglassesv2")(type "KiCad")(uri "${KIPRJMOD}/AI_Glasses_V2.kicad_sym")'
        '(options "")(descr "AI Glasses V2 chip-down generated symbols"))\n)\n',
        encoding="utf-8")
    FP_LIB_TABLE.write_text(
        '(fp_lib_table\n  (version 7)\n'
        '  (lib (name "AI_Glasses_V2")(type "KiCad")(uri "${KIPRJMOD}/AI_Glasses_V2.pretty")'
        '(options "")(descr "AI Glasses V2 footprints (created at layout time)"))\n)\n',
        encoding="utf-8")


def write_project() -> None:
    PRO_FILE.write_text(
        '{\n'
        '  "board": {"design_settings": {}},\n'
        '  "meta": {"filename": "ai_glasses_v2_chipdown.kicad_pro", "version": 1},\n'
        '  "schematic": {},\n'
        '  "sheets": [],\n'
        '  "text_variables": {}\n'
        '}\n',
        encoding="utf-8")


def main() -> int:
    HW.mkdir(parents=True, exist_ok=True)
    SYM_FILE.write_text(generate_symbol_library_text(), encoding="utf-8")
    write_tables()
    write_project()
    SCH_FILE.write_text(generate_sch_text(), encoding="utf-8")
    print(f"[OK] wrote {SCH_FILE.relative_to(ROOT.parent)}")
    print(f"[OK] wrote {SYM_FILE.relative_to(ROOT.parent)}")
    print(f"[INFO] {len(COMPONENTS)} components, {len(all_nets())} nets")
    print("[INFO] No .kicad_pcb generated — PCB layout is gated behind Gate 0 (docs/03).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
