#!/usr/bin/env python3
"""Generate V2 pre-layout gate documents from chipdown_bom.py.

Outputs:
  docs/08_signal_dictionary.md
  docs/09_power_domain_isolation_matrix.md
  docs/11_footprint_register.md
  docs/12_layout_entry_gate_status.md
"""
from __future__ import annotations

import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
sys.path.insert(0, str(Path(__file__).resolve().parent))

from chipdown_bom import COMPONENTS, all_nets, net_endpoints, net_meta  # noqa: E402


def esc(text: object) -> str:
    return str(text).replace("\n", " ").replace("|", "\\|")


def bom_key(c):
    digits = "".join(ch for ch in c.bom_id if ch.isdigit()) or "0"
    return (int(digits), c.bom_id, c.ref)


def refs_for_gate(gate_id: str) -> str:
    refs = [c.ref for c in COMPONENTS if gate_id in c.gate]
    return ", ".join(refs[:18]) + (" ..." if len(refs) > 18 else "") if refs else "-"


def gate_ids(text: str) -> list[str]:
    return sorted(set(re.findall(r"G\d{2}", text)))


def endpoint_refs(net: str) -> str:
    return "; ".join(f"{ep['ref']}.{ep['pin']}" for ep in net_endpoints(net))


def endpoint_boards(net: str) -> str:
    boards = []
    for ep in net_endpoints(net):
        if ep["board"] not in boards:
            boards.append(ep["board"])
    return " -> ".join(boards)


def component_counts() -> str:
    counts: dict[str, int] = {}
    for c in COMPONENTS:
        counts[c.assembly] = counts.get(c.assembly, 0) + 1
    return " · ".join(f"{counts.get(k, 0)} {k}" for k in ("Fit", "HOLD", "DNP", "TBD"))


def write_signal_dictionary() -> None:
    rows = [(net, net_meta(net)) for net in all_nets()]
    by_kind: dict[str, list[tuple[str, dict[str, str]]]] = {}
    for row in rows:
        by_kind.setdefault(row[1]["kind"], []).append(row)

    md: list[str] = []
    w = md.append
    w("# 08 — Signal dictionary (generated)")
    w("")
    w(f"> Generated {date.today().isoformat()} from `scripts/chipdown_bom.py`. "
      "Do not hand-edit. Every row is a net-level `NET_META` record normalized by `net_meta()`.")
    w("")
    w(f"**{len(rows)} nets**. Signal attributes cover name, source, destination, direction, "
      "voltage domain, default state, pulls, powered-off behavior, debug series parts, ESD, "
      "differential pairing, pinmux, device-tree/driver owner, and isolation notes.")
    w("")
    w("## Rules")
    w("")
    w("- `_L` means active low. `EN` and `PGOOD` are active high.")
    w("- Any row with `Cross-domain = yes` must pass reverse-feed/off-leakage review before layout.")
    w("- Defaults marked `low (OFF)` are backed by physical pull-downs where listed in `11/12`.")
    w("- `TBD` attributes are allowed only while the owning gate remains open.")
    w("")

    order = ["power", "control", "bus", "diff", "analog", "signal"]
    for kind in order:
        kind_rows = by_kind.get(kind, [])
        if not kind_rows:
            continue
        w(f"## {kind.title()} nets ({len(kind_rows)})")
        w("")
        w("| Net | Full name | From | To | Direction | Domain | Default | Pull | Off-high allowed | Series / ESD / Diff | Pinmux / DT / Driver | Notes |")
        w("|---|---|---|---|---|---|---|---|---|---|---|---|")
        for net, m in kind_rows:
            software = f"{m['pinmux']} / {m['dt']} / {m['driver']}"
            physical = f"{m['series']} / {m['esd']} / {m['diff_pair']}"
            w(f"| `{esc(net)}` | {esc(m['name'])} | {esc(m['source'])} | {esc(m['dest'])} | "
              f"{esc(m['direction'])} | {esc(m['dom'])} | {esc(m['default'])} | "
              f"{esc(m['pull'])} | {esc(m['off_high'])} | {esc(physical)} | "
              f"{esc(software)} | {esc(m['note'])} |")
        w("")

    (DOCS / "08_signal_dictionary.md").write_text("\n".join(md) + "\n", encoding="utf-8")


def write_isolation_matrix() -> None:
    xdom = [(net, net_meta(net)) for net in all_nets() if net_meta(net)["xdom"] == "yes"]
    default_off = [c for c in COMPONENTS if c.bom_id.startswith("C046")]

    domains = [
        ("Battery / pack", "BATR_P, BATL_P, BATR_F, BATL_F, BAT_P, NPM_VBAT, CELL_NEG", "LP451165 1S2P + F1/F2/RS1-RS3", "live", "G07 pack + protection closure"),
        ("AON", "AON_1V8, AON_3V3, AON_LSW2", "nPM1300 BUCK1/BUCK2/LSW2", "on in normal standby", "G08 AON <=25/50 mW"),
        ("RK3576 compute", "SOC_IN, SOC_5V, VDD_*, VCC_*", "RS4 -> TPS61088 -> RK806S", "off until SOC_PWR_EN + PMIC_PWRON", "G01/G02/G03/G06/G09"),
        ("Wi-Fi", "WIFI_IN, WIFI_3V3, WIFI_VBAT_3V3", "RS5 -> TPS62825 -> TPS22917", "off until WIFI_*_EN + CHIP_EN", "G05/G06"),
        ("Camera", "CAM_1V1, CAM_1V8_SW, CAM_2V9 and *_S", "front-board buck/LDO/load switch + RS7-RS9", "off until CAM_*_EN", "G10/G12"),
        ("Audio", "AUDIO_IN, AUDIO_PWR", "RS6 -> TPS22917 -> MAX98360A", "off/muted until AUDIO_* asserted", "speaker/acoustic gate"),
        ("RF", "WIFI_ANT, BLE_ANT", "antenna feeds", "passive", "worn-state tune + keep-out"),
        ("Debug / charge", "USB_5V, USB2_DP/DM, USB_CC1/2, SWD/UART pads", "EVT tail / pogo", "lab-use only", "connector/mechanical gate"),
    ]

    md: list[str] = []
    w = md.append
    w("# 09 — Power-domain isolation matrix (generated)")
    w("")
    w(f"> Generated {date.today().isoformat()} from `scripts/chipdown_bom.py`. "
      "This is the pre-layout reverse-feed checklist.")
    w("")
    w("## Domain map")
    w("")
    w("| Domain | Rails / nets | Owner | Default state | Closure gate |")
    w("|---|---|---|---|---|")
    for row in domains:
        w("| " + " | ".join(esc(x) for x in row) + " |")
    w("")
    w("## Cross-domain signals")
    w("")
    w("| Net | Kind | Domain | Board crossing | Default | Off-high allowed | Isolation / leakage rule | Endpoints |")
    w("|---|---|---|---|---|---|---|---|")
    for net, m in xdom:
        w(f"| `{esc(net)}` | {esc(m['kind'])} | {esc(m['dom'])} | {esc(endpoint_boards(net))} | "
          f"{esc(m['default'])} | {esc(m['off_high'])} | {esc(m['isolation'])} | {esc(endpoint_refs(net))} |")
    w("")
    w("## Hardware default-OFF proof")
    w("")
    w("| Ref | Net | Value | Board | Effect |")
    w("|---|---|---|---|---|")
    for c in sorted(default_off, key=bom_key):
        net = c.pins[0][1]
        w(f"| {c.ref} | `{net}` | {esc(c.value)} | {esc(c.board)} | {esc(c.desc)} |")
    w("")
    w("## Layout-entry requirements")
    w("")
    w("- RK3576, camera, Wi-Fi and audio domains must remain off with nRF reset or firmware hung.")
    w("- Any signal into a powered-down RK3576/camera/Wi-Fi domain needs measured leakage or isolation.")
    w("- Load switches with quick-output-discharge must prove the off-domain rail collapses fast enough.")
    w("- FPC crossings need the same default-state review as board-local crossings.")

    (DOCS / "09_power_domain_isolation_matrix.md").write_text("\n".join(md) + "\n", encoding="utf-8")


def footprint_status(footprint: str) -> str:
    if not footprint:
        return "MISSING"
    if "VERIFY" in footprint:
        return "VERIFY placeholder; not layout/fab ready"
    if footprint.startswith(("Package_", "Connector_", "Button_")):
        return "KiCad-library candidate; verify against MPN package drawing"
    if any(tag in footprint for tag in (":R_", ":C_", ":L_")):
        return "generic passive placeholder; freeze after passive MPN/derating"
    return "candidate; verify official land pattern + 3D/height"


def write_footprint_register() -> None:
    placeholder = sum(1 for c in COMPONENTS if "VERIFY" in c.footprint)
    md: list[str] = []
    w = md.append
    w("# 11 — Footprint register (generated)")
    w("")
    w(f"> Generated {date.today().isoformat()} from `scripts/chipdown_bom.py`. "
      "The KiCad `Footprint` field in the generated schematic intentionally remains empty; "
      "the `Package` property below is the intended package/footprint register for layout entry.")
    w("")
    w(f"**{len(COMPONENTS)} components** — {component_counts()}. "
      f"**{placeholder}** entries still use `VERIFY` placeholder package names.")
    w("")
    w("## Freeze rule")
    w("")
    w("A P0 component may enter PCB layout only after exact manufacturer, MPN, package variant, "
      "datasheet revision/date, package drawing, official recommended land pattern, max height, "
      "temperature range, lifecycle/MOQ/supply status, schematic symbol, footprint and 3D model all match.")
    w("")
    w("| BOM ID | Ref | Value | Board | Status | Package / intended footprint | Footprint readiness | Gate |")
    w("|---|---|---|---|:--:|---|---|---|")
    for c in sorted(COMPONENTS, key=bom_key):
        w(f"| {esc(c.bom_id)} | {esc(c.ref)} | {esc(c.value)} | {esc(c.board)} | {esc(c.assembly)} | "
          f"`{esc(c.footprint or '-')}` | {esc(footprint_status(c.footprint))} | {esc(c.gate or '-')} |")
    w("")
    w("## Layout implication")
    w("")
    w("- `VERIFY_*` entries are deliberate blockers, not approved generic footprints.")
    w("- HOLD parts keep their package names only as placement-envelope candidates until official drawings land.")
    w("- DNP footprints may be placed for EVT flexibility, but their pads must not compromise impedance, RF, acoustic ports or battery clearance.")

    (DOCS / "11_footprint_register.md").write_text("\n".join(md) + "\n", encoding="utf-8")


GATES = [
    ("G00", "Mechanical/battery layout gate", "HOLD", "real cell fit, swell room, hinge FPC, antenna keep-out, no battery over RK3576/PMIC"),
    ("G01", "RK3576 identity + HDG", "OPEN", "full datasheet/HDG/ball map, package drawing, reference-design delta plan"),
    ("G02", "LPDDR4X", "OPEN", "verified MPN, topology, placement, length report, DDR review"),
    ("G03", "RK806S PMIC", "OPEN", "exact MPN, rails, inductors/caps, sequence/timing with RK3576"),
    ("G04", "eMMC/boot", "OPEN", "MPN, BSP/bootloader, cold boot and power-loss recovery plan"),
    ("G05", "Wi-Fi module", "HOLD", "Quectel FCU760K Hardware Design, official LCC land pattern, RK3576 BSP/firmware enumeration"),
    ("G06", "High-power transient sizing", "OPEN", "RK3576 boot/AI peak, boost soft-start, 1S droop, Wi-Fi/camera/audio peaks"),
    ("G07", "LP451165 + 1S2P pack", "HOLD", "formal datasheet, discharge curve, IR/cycle/cert, pairing/fuse/NTC/current-share tests"),
    ("G08", "AON power", "HOLD", "nPM1300 EK config, NDP120 kit, measured AON <=25 mW avg / <=50 mW ceiling"),
    ("G09", "Thermal/boost droop", "OPEN", "RK3576 burst thermal path, TPS61088/RK806 droop and UVLO margin"),
    ("G10", "Camera module", "HOLD", "final IMX415 module FPC pinout, lens/FOV, lane count, rail current/timing"),
    ("G11", "Mic/audio topology", "OPEN", "mic coordinates, ports, wind/AEC/beamforming, NDP120 wake path"),
    ("G12", "FPC/hinge", "HOLD", "front FPC pin count, impedance, bend radius, hinge life and interference"),
    ("G13", "Magnetics/passives height", "OPEN", "inductor Isat/DCR/height, cap derating, wearable Z limits"),
    ("G14", "RF/worn tune", "OPEN", "antenna SKU, keep-out, matching in shell and worn condition"),
    ("G15", "Passive/manufacturing BOM", "OPEN", "expanded R/C/L MPNs, derating, lifecycle and alternates"),
]

HOLD_CLOSURE = [
    ("NDP120", "HOLD", "Full datasheet, package drawing/land pattern, rail map, reset/strap sequence, dev kit, model toolchain/licensing, measured listening power", "AI_Glasses_HOLD_Closure_Pack/01_NDP120", "Blocks U9 and wake-audio freeze"),
    ("Wi-Fi FCU760K", "HOLD", "Quectel Hardware Design, official LCC land pattern/3D/height, antenna SKU, RK3576 BSP driver + firmware enumeration", "AI_Glasses_HOLD_Closure_Pack/02_WiFi_FCU760K", "Blocks U11/J7 RF and USB2/PCM freeze"),
    ("LP451165 cell", "HOLD", "Formal supplier datasheet, discharge curves, IR, cycle life, high-rate limit, certification, swell envelope", "AI_Glasses_HOLD_Closure_Pack/03_Battery_LP451165_1S2P", "Blocks BT1/BT2 and mechanical Gate 0"),
    ("1S2P pack", "HOLD", "Pairing rules, fusing, NTC placement, current-share shunts, protection scheme, charge/gauge profiling", "AI_Glasses_HOLD_Closure_Pack/03_Battery_LP451165_1S2P", "Blocks G07/G08/G00"),
    ("Camera power current", "HOLD", "Custom IMX415 module rail currents/timing/FPC pinout beyond bare sensor datasheet", "AI_Glasses_HOLD_Closure_Pack/04_IMX415", "Blocks U14, CAM rails and G10"),
    ("Battery bay dimensions", "HOLD", "Real dummy-cell assembly, foam/swell allowance, hinge FPC path, antenna and speaker interference", "AI_Glasses_HOLD_Closure_Pack/06_Mechanical_Fit_Check", "Blocks PCB layout start"),
]


def write_layout_gate_status() -> None:
    hold_refs = [c for c in COMPONENTS if c.assembly == "HOLD"]
    md: list[str] = []
    w = md.append
    w("# 12 — Layout-entry gate status and HOLD closure")
    w("")
    w(f"> Generated {date.today().isoformat()} from `scripts/chipdown_bom.py`. "
      "This is the go/no-go record for entering PCB layout.")
    w("")
    w("## Verdict")
    w("")
    w("**PCB layout is NOT released.** The schematic is ERC-clean and useful for review, "
      "procurement and bench planning, but Gate 0/G05/G07/G08/G10/G12 remain HOLD.")
    w("")
    w(f"Current BOM state: **{len(COMPONENTS)} components** — {component_counts()}; "
      f"**{len(hold_refs)} HOLD** components.")
    w("")
    w("## Gate table")
    w("")
    w("| Gate | Topic | Status | Close condition | Components currently referencing it |")
    w("|---|---|:--:|---|---|")
    for gid, topic, status, close in GATES:
        w(f"| {gid} | {esc(topic)} | {status} | {esc(close)} | {esc(refs_for_gate(gid))} |")
    w("")
    w("## HOLD closure pack status")
    w("")
    w("| Item | Status | Close condition | Source folder | Blocks |")
    w("|---|:--:|---|---|---|")
    for row in HOLD_CLOSURE:
        w("| " + " | ".join(esc(x) for x in row) + " |")
    w("")
    w("## HOLD components")
    w("")
    w("| Ref | BOM ID | Value | Gate |")
    w("|---|---|---|---|")
    for c in sorted(hold_refs, key=bom_key):
        w(f"| {c.ref} | {c.bom_id} | {esc(c.value)} | {esc(c.gate)} |")
    w("")
    w("## Allowed next work before layout release")
    w("")
    w("- Keep the functional schematic and generated docs current.")
    w("- Procure missing datasheets/dev kits and run the AON/power bench tests.")
    w("- Build only small validation fixtures or dev-kit harnesses; do not start production PCB placement/copper.")

    (DOCS / "12_layout_entry_gate_status.md").write_text("\n".join(md) + "\n", encoding="utf-8")


def main() -> int:
    DOCS.mkdir(parents=True, exist_ok=True)
    write_signal_dictionary()
    write_isolation_matrix()
    write_footprint_register()
    write_layout_gate_status()
    print("wrote docs/08_signal_dictionary.md")
    print("wrote docs/09_power_domain_isolation_matrix.md")
    print("wrote docs/11_footprint_register.md")
    print("wrote docs/12_layout_entry_gate_status.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
