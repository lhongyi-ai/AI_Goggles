#!/usr/bin/env python3
"""Generate the current-schematic aligned BOM/power PDF source.

This report intentionally supersedes the externally edited V2.2 PDF for
engineering review. It is generated from the current schematic master
(`chipdown_bom.py`) and the current power model YAML, so names, assembly states,
power totals, and gates do not drift from the schematic.
"""
from __future__ import annotations

from datetime import date
from pathlib import Path
import sys

import yaml

ROOT = Path(__file__).resolve().parent.parent
SCRIPT_DIR = ROOT / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

from chipdown_bom import COMPONENTS, all_nets, _validate  # noqa: E402

POWER_MODEL = ROOT / "config" / "power_budget_v2.yaml"
BATTERY_MODEL = ROOT / "config" / "battery_options.yaml"
ERC_REPORT = ROOT / "reports" / "erc.report.txt"
OUT = ROOT / "reports" / "AI_Glasses_Chipdown_BOM_V2.3_Current_Schematic.md"


def clean(value: object) -> str:
    """Keep generated markdown PDF-friendly and mostly ASCII."""
    s = "" if value is None else str(value)
    replacements = {
        "→": "->",
        "←": "<-",
        "↔": "<->",
        "×": "x",
        "–": "-",
        "—": "-",
        "≤": "<=",
        "≥": ">=",
        "±": "+/-",
        "Ω": "ohm",
        "µ": "u",
        "§": "section ",
        "°": " deg ",
        "“": '"',
        "”": '"',
        "’": "'",
        "·": "-",
    }
    for old, new in replacements.items():
        s = s.replace(old, new)
    return "".join(ch if ord(ch) < 128 else "" for ch in s).strip()


def fmt_power(value: float) -> str:
    if abs(value - round(value)) < 1e-9:
        return str(int(round(value)))
    return f"{value:.1f}"


def fmt_runtime(hours: float) -> str:
    if hours >= 10:
        return f"{hours:.0f} h"
    return f"{hours:.1f} h ({hours * 60:.0f} min)"


def load_models() -> tuple[dict, dict]:
    return (
        yaml.safe_load(POWER_MODEL.read_text(encoding="utf-8")),
        yaml.safe_load(BATTERY_MODEL.read_text(encoding="utf-8")),
    )


def power_totals(model: dict) -> tuple[list[str], dict[str, str], dict[str, float]]:
    keys = [state["key"] for state in model["states"]]
    labels = {state["key"]: state["label"] for state in model["states"]}
    totals = {key: sum(sub["mW"][key] for sub in model["subsystems"]) for key in keys}
    return keys, labels, totals


def status_counts() -> tuple[dict[str, int], dict[str, int]]:
    by_board: dict[str, int] = {}
    by_status: dict[str, int] = {}
    for comp in COMPONENTS:
        by_board[comp.board] = by_board.get(comp.board, 0) + 1
        by_status[comp.assembly] = by_status.get(comp.assembly, 0) + 1
    return by_board, by_status


def component_power(keys: list[str], totals: dict[str, float]) -> dict[str, dict]:
    """Project-budget allocation by schematic ref.

    The current public power model is subsystem-level. This allocation breaks
    those rows down across schematic refs so the report can show each component
    without changing the official totals. It is a project budget allocation, not
    a per-datasheet guarantee.
    """
    zero = {key: 0.0 for key in keys}
    rows: dict[str, dict] = {
        comp.ref: {"mW": dict(zero), "basis": "0 direct load, DNP, passive, source, or included in owning domain"}
        for comp in COMPONENTS
    }

    def set_ref(ref: str, values: list[float], basis: str) -> None:
        rows[ref] = {"mW": dict(zip(keys, values, strict=True)), "basis": basis}

    # Compute row: RK3576 + RK806 + LPDDR4X + eMMC = current model compute core.
    set_ref("U1", [0, 20, 80, 150, 600, 1150], "RK3576 project allocation inside compute core row")
    set_ref("U2", [0, 10, 15, 25, 70, 100], "RK806S/PMIC rail-management allocation")
    set_ref("U3", [0, 55, 45, 60, 130, 180], "LPDDR4X retention/activity allocation")
    set_ref("U4", [0, 5, 10, 15, 50, 70], "eMMC standby/write allocation")
    set_ref("U6", [0, 20, 10, 20, 40, 60], "compute-island boost/load-switch/PMIC loss row")

    # Always-on row.
    set_ref("U7", [2, 3, 8, 6, 5, 8], "nRF-class BLE MCU/current-state-machine average")
    set_ref("U8", [3, 4, 6, 6, 10, 15], "nPM1300 AON buck quiescent + regulation loss")
    set_ref("U9", [12, 12, 15, 15, 15, 20], "NDP120-class wake-word/listening budget")
    set_ref("U10", [1, 1, 1, 1, 1, 1], "BMI270 low-power motion budget")
    set_ref("MK1", [3, 3, 3, 3, 3, 3], "wake mic always-on share of MEMS mic row")
    set_ref("MK2", [0, 0, 1.5, 1.5, 2.5, 3.5], "array mic share of MEMS mic row")
    set_ref("MK3", [0, 0, 1.5, 1.5, 2.5, 3.5], "array mic share of MEMS mic row")
    set_ref("RT1", [0.5, 0.5, 0.5, 0.5, 0.5, 0.5], "fuel-gauge/NTC/protection monitor allocation")
    set_ref("RT2", [0.5, 0.5, 0.5, 0.5, 0.5, 0.5], "fuel-gauge/NTC/protection monitor allocation")

    # Camera row: current baseline, not the old high-load sensitivity case.
    set_ref("U14", [0, 0, 0, 25, 220, 265], "custom 1080p camera module baseline allocation")
    set_ref("U15", [0, 0, 0, 2, 15, 18], "camera 1.1 V buck loss allocation")
    set_ref("U16", [0, 0, 0, 3, 14, 16], "camera 2.9 V LDO loss allocation")
    set_ref("U17", [0, 0, 0, 0, 1, 1], "camera 1.8 V load-switch loss allocation")

    # Radio and audio rows.
    set_ref("U11", [0, 0, 145, 95, 75, 115], "FCU760K on-demand Wi-Fi activity average")
    set_ref("U12", [0, 0, 5, 5, 5, 5], "Wi-Fi buck conversion-loss allocation")
    set_ref("U20", [0, 0, 2, 2, 3, 3], "MAX98360A small-signal/idle audio allocation")
    set_ref("LS1", [0, 0, 13, 13, 27, 27], "single speaker acoustic-output average")

    assigned = {key: sum(row["mW"][key] for row in rows.values()) for key in keys}
    mismatch = [
        f"{key}: assigned {assigned[key]} mW vs model {totals[key]} mW"
        for key in keys
        if abs(assigned[key] - totals[key]) > 1e-9
    ]
    if mismatch:
        raise RuntimeError("component allocation does not match model totals: " + "; ".join(mismatch))
    return rows


def refs_by_board() -> dict[str, list]:
    out: dict[str, list] = {}
    for comp in COMPONENTS:
        out.setdefault(comp.board, []).append(comp)
    return out


def erc_summary() -> str:
    if not ERC_REPORT.exists():
        return "ERC report not found"
    text = ERC_REPORT.read_text(encoding="utf-8", errors="replace")
    lines = [clean(line) for line in text.splitlines() if "Errors" in line or "Warnings" in line or "Violations" in line]
    return "; ".join(lines) if lines else "ERC report present"


def write_report() -> None:
    problems = _validate()
    if problems:
        raise RuntimeError("BOM validation failed: " + "; ".join(problems))

    model, battery = load_models()
    keys, labels, totals = power_totals(model)
    by_board, by_status = status_counts()
    powers = component_power(keys, totals)
    states = model["states"]
    v_batt = model["constants"]["v_batt_nominal_V"]
    dod = model["constants"]["usable_dod"]
    pack = next(p for p in battery["packs"] if p["id"] == battery["recommended"])
    pack_mwh = pack["mAh"] * v_batt * dod

    md: list[str] = []

    def w(line: str = "") -> None:
        md.append(clean(line))

    def raw(line: str = "") -> None:
        md.append(line)

    w("# AI Glasses RK3576 Chip-down BOM V2.3")
    w("## Current schematic-aligned BOM, power, and layout-gate report")
    w("")
    w(f"- Generated: {date.today().isoformat()}")
    w("- Source of truth: `v2_chipdown/scripts/chipdown_bom.py` and `v2_chipdown/config/power_budget_v2.yaml`")
    w("- Schematic: `v2_chipdown/hardware/ai_glasses_v2_chipdown.kicad_sch`")
    w("- Exported BOM/netlist/PDF: `v2_chipdown/reports/*`")
    w("- This report is schematic-aligned. If an older PDF disagrees with this document, use this document.")
    w("")

    w("## 1. Read this first")
    w("")
    w("| Item | Current value |")
    w("|---|---|")
    w(f"| Schematic scope | Pre-PCB-layout functional-block schematic |")
    w(f"| Components / nets | {len(COMPONENTS)} components / {len(all_nets())} nets |")
    w(f"| Assembly states | " + ", ".join(f"{k}={v}" for k, v in sorted(by_status.items())) + " |")
    w(f"| Board split | " + ", ".join(f"{k}={v}" for k, v in by_board.items()) + " |")
    w(f"| ERC | {erc_summary()} |")
    w("| PCB layout release | NOT released; Gate 0/G00F/G05/G07/G08/G10/G12 still block layout |")
    w("| Phase 1.5 | Required mechanical/electrical floorplan before formal PCB layout |")
    w("| First EVT hinge stance | Hinge electrical interconnect is out of scope for Chip-down EVT V2.0; J4 hinge FPC has been removed from the schematic source |")
    w("")
    w("Status legend: Fit = populate first build; DNP = land only; HOLD = candidate blocked by a gate; TBD = MPN/spec undecided.")
    w("Power numbers are project budget estimates until EVT shunt measurements replace them.")
    w("")

    w("## 2. System power boundary")
    w("")
    w("| Power state | Current load (mW) | Target band (mW) | Battery current @3.7 V | Runtime on LP451165 x2 1S2P |")
    w("|---|--:|--:|--:|--:|")
    for state in states:
        key = state["key"]
        target = state.get("target_display") or f"{state['target_mW'][0]}-{state['target_mW'][1]}"
        current_ma = totals[key] / v_batt
        runtime_h = pack_mwh / totals[key]
        w(f"| {labels[key]} | {totals[key]:.0f} | {target} | {current_ma:.0f} mA | {fmt_runtime(runtime_h)} |")
    w("")
    w("Recommended pack: LP451165 x2, 1S2P, 600 mAh / 2.22 Wh nominal, one cell per temple.")
    w("Baseline current model uses 1290 mW for continuous 1080p record and 2065 mW for AI burst.")
    w("")

    w("## 3. Subsystem power model")
    w("")
    raw("| Subsystem | Domain | " + " | ".join(keys) + " |")
    raw("|---|---|" + "|".join(["--:"] * len(keys)) + "|")
    for sub in model["subsystems"]:
        raw("| " + clean(sub["name"]) + " | " + clean(sub["domain"]) + " | " + " | ".join(str(sub["mW"][key]) for key in keys) + " |")
    raw("| **TOTAL** | | " + " | ".join(f"**{totals[key]:.0f}**" for key in keys) + " |")
    w("")

    w("## 4. What changed from the attached PDF")
    w("")
    w("- The Wi-Fi module is the current schematic part `U11 / C015 = FCU760KAAMD`, status HOLD.")
    w("- BQ25895 is now explicit as the primary charger + Power Path block; nPM1300 remains the AON low-power PMIC/gauge/rail manager.")
    w("- J4 hinge FPC has been removed: no hinge FPC footprint, no cross-hinge battery, MIPI, USB or audio wiring in EVT V2.0.")
    w("- J3 is the proposed 33-pin FH26W camera FPC connector; IMX415 is now drawn as a 4-lane target while its mechanical module remains HOLD/TBD.")
    w("- Wi-Fi/BLE share the main dual-band FPC antenna; the second FCU760K RF port is DNP/test only.")
    w("- The IMU is `U10 / C012 = BMI270`, status Fit.")
    w("- The current baseline power totals are 22 / 134 / 362 / 450 / 1290 / 2065 mW.")
    w(f"- The current BOM is not only C001-C045; it is {len(COMPONENTS)} schematic components with expanded shunts, INA238 monitors, passives, load switches, charger/input protection, and C046 default-off pull-downs.")
    w("- C044 is expanded into RS1-RS9 plus U25-U33 current monitors; C045/C046 passives are explicit pre-layout controls.")
    w("- PCB layout is still not released; unresolved mechanical/battery/FPC/RF/camera/AON gates remain.")
    w("- A new Phase 1.5 floorplan is required between ERC-clean schematic and formal PCB layout.")
    w("")

    w("## 5. Board and mechanical partition")
    w("")
    w("| Region | Current schematic contents | EVT note |")
    w("|---|---|---|")
    w("| Front Sensor Board | IMX415 custom FPC module, 3 fitted T5837 mics, 4th mic DNP, camera rails, MIPI ESD, front FPC | Final module pinout/lens/lane count remains G10 HOLD |")
    w("| R-Temple Compute Board | RK3576, RK806S, LPDDR4X, eMMC, TPS61088, FCU760K Wi-Fi, Wi-Fi buck/load switch, MAX98360A audio | Heat and boost droop gates remain open |")
    w("| L-Temple AON/Power Board | nRF54L15, nPM1300, NDP120, BMI270, optional protection, main shunt/INA | AON average <=25 mW and ceiling <=50 mW must be measured |")
    w("| Temple Rears | LP451165 x2 pack envelopes, branch fuses/shunts, main speaker, shared Wi-Fi/BLE antenna, pogo, DNP RF/debug options | First EVT is fixed-temple electrically; no hinge FPC/cross-hinge harness in the released schematic |")
    w("| EVT Debug Tail | USB-C, ESD, CC resistors, SWD/UART pads, power/reset/recovery buttons | Bring-up only; production can hide/remove |")
    w("")

    w("## 5.5. Phase 1.5 mechanical/electrical floorplan")
    w("")
    w("Before formal PCB placement/routing, create a no-route fit floorplan. This is a CAD + EE deliverable, not a routed board.")
    w("")
    w("| Required output | Contents |")
    w("|---|---|")
    w("| Right-temple top/side view | usable length/width/height; Compute PCB; RK3576/LPDDR/RK806/eMMC/Wi-Fi/BQ25895/boost-inductor zones; battery; speaker; shared Wi-Fi/BLE antenna keep-out; pogo; front FPC corridor; shell/foam/swell allowance |")
    w("| Left-temple top/side view | usable length/width/height; AON/power PCB; nRF/nPM/NDP/BMI270 zones; battery; no separate BLE antenna fitted; pogo/service clearance; shell/foam/swell allowance |")
    w("| KiCad no-route floorplan | board frames plus RK3576, LPDDR, RK806, eMMC, Wi-Fi, boost inductor, FPC connectors, battery 3D/envelope blocks, speaker and antenna keep-outs |")
    w("| Pass/fail decision | prove the current schematic architecture fits before routing; if not, change battery/partition/connectors/DNP features/local temple width |")
    w("")
    w("Formal routing starts only after this floorplan passes. If it fails, do not route; change the architecture first.")
    w("")

    w("## 6. Current BOM by board")
    w("")
    for board, comps in refs_by_board().items():
        w(f"### {board}")
        w("")
        w("| Ref | BOM ID | Value | Status | Pri | Package / footprint placeholder | Gate |")
        w("|---|---|---|:--:|:--:|---|---|")
        for comp in comps:
            w(f"| {comp.ref} | {comp.bom_id} | {comp.value} | {comp.assembly} | {comp.pri} | {comp.footprint or 'TBD'} | {comp.gate or '-'} |")
        w("")

    w("## 7. Per-component power allocation")
    w("")
    w("Values below are battery-side project-budget mW and sum exactly to the current subsystem totals. A zero means DNP, passive/source, or already included in its owning domain; it does not mean zero parasitic physics.")
    w("")
    raw("| Ref | BOM ID | Value | Status | " + " | ".join(keys) + " | Basis |")
    raw("|---|---|---|:--:|" + "|".join(["--:"] * len(keys)) + "|---|")
    for comp in COMPONENTS:
        row = powers[comp.ref]
        raw("| " + " | ".join([
            clean(comp.ref),
            clean(comp.bom_id),
            clean(comp.value),
            clean(comp.assembly),
            *[fmt_power(row["mW"][key]) for key in keys],
            clean(row["basis"]),
        ]) + " |")
    raw("| **TOTAL** | | | | " + " | ".join(f"**{fmt_power(totals[key])}**" for key in keys) + " | Current model total |")
    w("")

    w("## 8. Power domains and shutdown policy")
    w("")
    w("| Domain | Rails / source | Main loads | Default state | Owner / control |")
    w("|---|---|---|---|---|")
    w("| Battery / pack | LP451165 1S2P pack PCM -> F1/F2 -> RS2/RS3 -> BAT_P -> RS1 -> NPM_VBAT | Entire system source | Live | Pack PCM + BQ25895 charger/power path |")
    w("| AON | AON_1V8, AON_3V3, AON_LSW2 from nPM1300 | nRF54L15, NDP120, BMI270, wake mic, fuel/NTC | On in normal standby | nPM1300 / nRF54L15 |")
    w("| RK3576 compute | VSYS -> RS4 -> TPS61088 -> SOC_5V -> RK806S rails | RK3576, LPDDR4X, eMMC | Off until `SOC_PWR_EN` + `PMIC_PWRON` | nRF54L15 master; Linux safe-off handshake |")
    w("| Camera | TPS62840 CAM_1V1, TPS22917 CAM_1V8, TLV75529 CAM_2V9 | IMX415 custom FPC module | Off until camera session | nRF54L15 / RK3576 |")
    w("| Wi-Fi | VSYS -> RS5 -> TPS62825 -> TPS22917 -> FCU760K | FCU760K and antenna path | Off until transfer/preview | nRF54L15 enables buck, switch, and module |")
    w("| Audio | VSYS -> RS6 -> TPS22917 -> MAX98360A -> LS1 | Single 8 ohm speaker | Off/muted | nRF54L15 / RK3576 |")
    w("")
    w("Default-off controls use 100k pull-downs R11-R20 so compute, camera, Wi-Fi, and audio remain off if firmware is absent or reset.")
    w("")

    w("## 9. Layout-entry gates")
    w("")
    w("| Gate | Topic | Current status | Close condition |")
    w("|---|---|:--:|---|")
    w("| G00 | Mechanical/battery | HOLD | Real cell fit, swell room, FPC corridor, antenna keep-out, no battery over RK3576/PMIC |")
    w("| G00F | Phase 1.5 floorplan | HOLD | Dimensioned top/side floorplan + no-route KiCad placement envelopes prove fit before routing |")
    w("| G01 | RK3576 identity + HDG | OPEN | Full datasheet, HDG, ball map, package drawing, reference delta |")
    w("| G02 | LPDDR4X | OPEN | MPN, topology, placement, length report, DDR review |")
    w("| G03 | RK806S PMIC | OPEN | Exact MPN, rails, inductors/caps, sequencing, timing |")
    w("| G04 | eMMC/boot | OPEN | MPN, bootloader/BSP support, cold boot and power-loss recovery |")
    w("| G05 | Wi-Fi FCU760K | HOLD | Hardware design, land pattern/3D, antenna SKU, BSP driver/firmware enumeration |")
    w("| G06 | High-power transient sizing | OPEN | RK3576 boot/AI peak, boost soft-start, 1S droop, Wi-Fi/camera/audio peaks |")
    w("| G07 | LP451165 + 1S2P pack | HOLD | Formal datasheet, discharge curves, IR/cycle/cert, pairing/fusing/NTC/current-share |")
    w("| G08 | AON power | HOLD | nPM1300 EK config, NDP120 kit, measured AON <=25 mW avg / <=50 mW ceiling |")
    w("| G09 | Thermal/boost droop | OPEN | RK3576 burst thermal path, TPS61088/RK806 droop and UVLO margin |")
    w("| G10 | Camera module | HOLD | Final IMX415 module FPC pinout, lens/FOV, lane count, rail current/timing |")
    w("| G11 | Mic/audio topology | OPEN | Mic coordinates, ports, wind/AEC/beamforming, NDP120 wake path |")
    w("| G12 | Camera/front FPC interconnect | HOLD | FH26W-33S pinout, contact orientation, impedance and module vendor sign-off; hinge electrical interconnect is out of scope for EVT V2.0 |")
    w("| G13 | Magnetics/passives height | OPEN | Inductor Isat/DCR/height, cap derating, wearable Z limits |")
    w("| G14 | RF/worn tune | OPEN | Antenna SKU, keep-out, matching in shell and worn condition |")
    w("| G15 | Passive/manufacturing BOM | OPEN | Expanded R/C/L MPNs, derating, lifecycle and alternates |")
    w("")

    w("## 10. Detailed schematic cards")
    w("")
    for comp in COMPONENTS:
        pins = ", ".join(f"{pin}->{net}" for pin, net in comp.pins)
        w(f"### {comp.ref} / {comp.bom_id} - {comp.value}")
        w("")
        w(f"- Board/status: {comp.board} / {comp.assembly} / {comp.pri}")
        w(f"- Package field: {comp.footprint or 'TBD'}")
        w(f"- Gate: {comp.gate or '-'}")
        w(f"- Description: {comp.desc}")
        if comp.note:
            w(f"- Note: {comp.note}")
        w(f"- Schematic nets: {pins}")
        w("")

    w("---")
    w("Regeneration:")
    w("`python3 v2_chipdown/scripts/generate_current_schematic_report.py`")
    w("Then render with kidoc to PDF. Do not hand-edit the PDF; update the schematic master or YAML and regenerate.")

    OUT.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT.parent)}")
    print(f"{len(COMPONENTS)} components, {len(all_nets())} nets")
    print("power totals: " + ", ".join(f"{key}={totals[key]:.0f}mW" for key in keys))


if __name__ == "__main__":
    write_report()
