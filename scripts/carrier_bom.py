#!/usr/bin/env python3
"""Single source of truth for the ai_glasses_carrier_v1 component list (BOM).

Both the schematic generator (scripts/generate_carrier_board.py) and the
Chinese design report (scripts/generate_report.py) read COMPONENTS from here so
the drawn schematic and the written BOM can never drift apart.

IMPORTANT — these part numbers and values are *engineering candidates* for an
EVT board, not a frozen BOM.  Per the requirements doc (Section 1.1) AI output
is auxiliary: every part, value and especially every CM4 pin number must be
human-verified against the official Radxa CM4 Schematic V1.20 before release.
Passive values below are typical starting values (decoupling / pull-ups / etc.)
and must be confirmed against each chosen IC's datasheet.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml


@dataclass
class Component:
    ref: str                       # schematic reference designator (unique)
    value: str                     # IC part number OR passive value (e.g. "5.1k")
    desc: str                      # human description for the BOM report
    group: str                     # functional group for grouping in the report
    # pins: ordered list of (pin_name, net_name). The schematic generator splits
    # the list in half: first half on the left edge, second half on the right.
    pins: list[tuple[str, str]] = field(default_factory=list)
    pri: str = "P0"                # P0 (must) / P1 (should)
    note: str = ""
    mpn: str = ""                  # manufacturer part number (when frozen)
    lcsc: str = ""                 # LCSC / JLC part number (for SMT)
    footprint: str = ""            # KiCad footprint library id, when known


PROJECT_ROOT = Path(__file__).resolve().parent.parent
PASSIVE_FREEZE_FILE = PROJECT_ROOT / "config" / "passive_bom_freeze.yaml"


def _load_passive_footprints() -> dict[str, str]:
    if not PASSIVE_FREEZE_FILE.exists():
        return {}
    with PASSIVE_FREEZE_FILE.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    footprints: dict[str, str] = {}
    for family in (data.get("families") or {}).values():
        footprint = family.get("footprint")
        if not footprint:
            continue
        for ref in family.get("refs") or []:
            footprints[str(ref)] = str(footprint)
    return footprints


PASSIVE_FOOTPRINTS = _load_passive_footprints()


def _fp(ref: str, fallback: str = "") -> str:
    return PASSIVE_FOOTPRINTS.get(ref, fallback)


FALLBACK_FOOTPRINTS = {
    # CM4 B2B connectors: schematic/logical refs; replace with verified Hirose DF40 footprint before layout.
    "J31": "AI_Glasses:VERIFY_B2B_J31_LOGICAL",
    "J32": "AI_Glasses:VERIFY_B2B_J32_LOGICAL",
    "J1": "AI_Glasses:VERIFY_B2B_J1_LOGICAL",

    # Debug header footprint is low-risk and useful during bring-up.
    "J7": "Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical",
}


def _fallback_footprint(comp: Component) -> str:
    ref = comp.ref
    if ref.startswith("TP") and ref[2:].isdigit():
        return "AI_Glasses:VERIFY_TP_1P"
    explicit = FALLBACK_FOOTPRINTS.get(ref)
    if explicit:
        return explicit
    return f"AI_Glasses:VERIFY_{max(len(comp.pins), 1)}P"


# ─────────────────────────────────────────────────────────────────────────────
# CM4 module, represented as its three 100-pin board-to-board connectors.
# Only the signals the carrier actually uses are pinned out.  The physical CM4
# pin numbers are TBD (except +5V on J3A) until verified vs CM4 Schematic V1.20;
# the symbol pin *numbers* below are just symbol-local indices, NOT CM4 pins.
# ─────────────────────────────────────────────────────────────────────────────
# Pin numbers below are the REAL Radxa CM4 pins (verified vs radxa_cm4_pinout_v1.20
# + Schematic V1.20). Authoritative map: scripts/cm4_pinmap.py. Names show "P<pin>".
_B2B = "DF40C-100DS-0.4V(51)"   # carrier-side receptacle; mates module DF40C-100DP-0.4V(51)

CM4 = [
    Component(
        ref="J31", value=_B2B,
        desc="CM4 J3A (low-speed): power, debug/GNSS UART, I2C, control GPIO",
        group="CM4 模块 / B2B 连接器", pri="P0",
        note="KiCad refdes J31 represents Radxa CM4 connector J3A. Carrier-side receptacle; "
             "pins verified vs CM4 V1.20. GPIO bank @1.8V (VREF=P78).",
        pins=[
            ("P77-87 +5V", "+5V_SYS"), ("P78 VREF→1V8", "+1V8"), ("GND", "GND"),
            ("P55 DBG_TX", "UART_DBG_TX"), ("P51 DBG_RX", "UART_DBG_RX"),
            ("P47 GNSS_TX", "GNSS_UART_TX"), ("P45 GNSS_RX", "GNSS_UART_RX"),
            ("P40 GNSS_PPS", "GNSS_PPS"), ("P44 GNSS_RST", "GNSS_RST_n"),
            ("P80 CAM_SCL", "CAM_I2C_SCL"), ("P82 CAM_SDA", "CAM_I2C_SDA"),
            ("P56 IMU_SCL", "IMU_I2C_SCL"), ("P58 IMU_SDA", "IMU_I2C_SDA"),
            ("P35 FUEL_SCL", "FUEL_I2C_SCL"), ("P36 FUEL_SDA", "FUEL_I2C_SDA"),
            ("P30 IMU_INT", "IMU_INT1"), ("P48 VIB_PWM", "VIB_PWM"), ("P34 VIB_EN", "VIB_EN"),
            ("P37 CHG_INT", "CHG_INT_n"), ("P39 LBAT_INT", "LOW_BAT_INT_n"),
            ("P95 LED_PWR", "LED_PWR_n"), ("P21 LED_STAT", "LED_STATUS_n"),
            ("P93 RECOVERY", "RECOVERY_n"), ("P92 RESET", "RESET_n"), ("P99 PWR_KEY", "POWER_KEY"),
            ("P89 WL_DIS", "WL_nDIS"), ("P91 BT_DIS", "BT_nDIS"),
        ],
    ),
    Component(
        ref="J32", value=_B2B,
        desc="CM4 J3B (high-speed): MIPI-CSI3 4-lane camera, USB2-OTG0, PDM1 mics",
        group="CM4 模块 / B2B 连接器", pri="P0",
        note="KiCad refdes J32 represents Radxa CM4 connector J3B. MIPI CSI3 100Ω diff, "
             "USB 90Ω diff. Pins verified vs CM4 V1.20.",
        pins=[
            ("P129 CSI3_CLKP", "MIPI_CSI3_CLK_P"), ("P127 CSI3_CLKN", "MIPI_CSI3_CLK_N"),
            ("P117 CSI3_D0P", "MIPI_CSI3_D0_P"), ("P115 CSI3_D0N", "MIPI_CSI3_D0_N"),
            ("P123 CSI3_D1P", "MIPI_CSI3_D1_P"), ("P121 CSI3_D1N", "MIPI_CSI3_D1_N"),
            ("P135 CSI3_D2P", "MIPI_CSI3_D2_P"), ("P133 CSI3_D2N", "MIPI_CSI3_D2_N"),
            ("P141 CSI3_D3P", "MIPI_CSI3_D3_P"), ("P139 CSI3_D3N", "MIPI_CSI3_D3_N"),
            ("P143 CAM3_GPIO", "CAM_RST_n"),
            ("P105 USB_DP", "USB_DP"), ("P103 USB_DM", "USB_DM"),
            ("P96 PDM_CLK", "PDM1_CLK"), ("P94 PDM_D0", "PDM1_DATA0"),
            ("P111 PDM_D1", "PDM1_DATA1"), ("GND", "GND"),
        ],
    ),
    Component(
        ref="J1", value=_B2B,
        desc="CM4 J1 (I/O): SAI1 audio, CSI3 camera MCLK, speaker enable",
        group="CM4 模块 / B2B 连接器", pri="P0",
        note="SAI1 audio out + CAM_CLK2_OUT_M0 for Radxa Camera 4K. Pins verified vs CM4 V1.20. "
             "Radxa Camera 4K 31-pin FPC has active-low RESET but no PWDN pin. "
             "SAI1_MCLK is unused for MAX98357A and marked no-connect at the CM4 B2B.",
        pins=[
            ("P25 SAI_BCLK", "SAI1_BCLK"), ("P19 SAI_LRCK", "SAI1_LRCK"),
            ("P29 SAI_SDO", "SAI1_SDO"), ("P23 SAI_MCLK_UNUSED", "NC"),
            ("P59 CAM3_MCLK", "CAM_MCLK"),
            ("P96 SPK_EN", "SPKR_EN_n"), ("+1V8 (P88/90)", "+1V8"), ("GND", "GND"),
        ],
    ),
]

# ─────────────────────────────────────────────────────────────────────────────
# Camera (P0)
# ─────────────────────────────────────────────────────────────────────────────
CAMERA = [
    Component(
        ref="J2", value="FH35C-31S-0.3SHW(50)",
        desc="Camera FPC — Radxa Camera 4K / Sony IMX415-AAQR-C, 31-pin 0.3mm, 4-lane MIPI",
        group="摄像头 Camera (P0)", pri="P0",
        note="SCHEMATIC_ELECTRICAL_LOCKED for Radxa Camera 4K using Radxa AC006 31P 0.3mm "
             "opposite-side FPC. Pad 1 = GND. J2 pins 1-31, CSI3 4-lane, P/N, I2C/MCLK/RESET, "
             "voltage domains, power and NC are checked by scripts/audit_csi3_camera.py. "
             "DEFERRED_TO_PRE_LAYOUT: AC006 physical validation, FPC contact side, insertion direction, "
             "Pin 1 physical check, 1:1 print, coupon test, and FPC bend/enclosure path. "
             "Pinout source: CM4_IMX415_design_files/Radxa_Camera_4K_31pin_pinout.csv.",
        mpn="FH35C-31S-0.3SHW(50)",
        lcsc="C424662",
        footprint="AI_Glasses:FH35C-31S-0.3SHW_50",
        pins=[
            ("1 GND", "GND"), ("2 MDN4", "MIPI_CSI3_D3_N"), ("3 MDP4", "MIPI_CSI3_D3_P"),
            ("4 GND", "GND"), ("5 MDN3", "MIPI_CSI3_D2_N"), ("6 MDP3", "MIPI_CSI3_D2_P"),
            ("7 GND", "GND"), ("8 NC", "NC"), ("9 NC", "NC"),
            ("10 GND", "GND"), ("11 MDN2", "MIPI_CSI3_D1_N"), ("12 MDP2", "MIPI_CSI3_D1_P"),
            ("13 GND", "GND"), ("14 MDN1", "MIPI_CSI3_D0_N"), ("15 MDP1", "MIPI_CSI3_D0_P"),
            ("16 GND", "GND"), ("17 MCN", "MIPI_CSI3_CLK_N"), ("18 MCP", "MIPI_CSI3_CLK_P"),
            ("19 GND", "GND"), ("20 MCLK", "CAM_MCLK"), ("21 GND", "GND"),
            ("22 NC", "NC"), ("23 NC", "NC"), ("24 SCL", "CAM_I2C_SCL"),
            ("25 SDA", "CAM_I2C_SDA"), ("26 NC", "NC"), ("27 RESET_N", "CAM_RST_n"),
            ("28 VCC3.3V", "+CAM_3V3"), ("29 VCC3.3V", "+CAM_3V3"),
            ("30 VCC5V", "+5V_SYS"), ("31 VCC5V", "+5V_SYS"),
        ],
    ),
    Component(
        ref="U2", value="TPD4E05U06",
        desc="MIPI-CSI low-capacitance ESD array for CSI3 clock + data lanes 0/1 (<0.4pF/line)",
        group="摄像头 Camera (P0)", pri="P0",
        pins=[
            ("CLK_P", "MIPI_CSI3_CLK_P"), ("CLK_N", "MIPI_CSI3_CLK_N"),
            ("D0_P", "MIPI_CSI3_D0_P"), ("D0_N", "MIPI_CSI3_D0_N"),
            ("D1_P", "MIPI_CSI3_D1_P"), ("D1_N", "MIPI_CSI3_D1_N"), ("GND", "GND"),
        ],
    ),
    Component(
        ref="U16", value="TPD4E05U06",
        desc="MIPI-CSI low-capacitance ESD array for CSI3 data lanes 2/3 (<0.4pF/line)",
        group="摄像头 Camera (P0)", pri="P0",
        pins=[
            ("D2_P", "MIPI_CSI3_D2_P"), ("D2_N", "MIPI_CSI3_D2_N"),
            ("D3_P", "MIPI_CSI3_D3_P"), ("D3_N", "MIPI_CSI3_D3_N"), ("GND", "GND"),
        ],
    ),
    Component(
        ref="U3", value="LP5907-3.3 (low-noise LDO)",
        desc="Camera 3.3V low-noise supply for Radxa Camera 4K, EN-gated",
        group="摄像头 Camera (P0)", pri="P0",
        pins=[("VIN", "+5V_SYS"), ("EN", "CAM_PWR_EN"), ("GND", "GND"), ("VOUT", "+CAM_3V3")],
    ),
    Component(ref="R7", value="2.2k", desc="Camera I2C SCL pull-up to +1V8 (cam OVDD=1.8V confirmed)",
              group="摄像头 Camera (P0)", pri="P0", pins=[("1", "+1V8"), ("2", "CAM_I2C_SCL")]),
    Component(ref="R8", value="2.2k", desc="Camera I2C SDA pull-up to +1V8 (cam OVDD=1.8V confirmed)",
              group="摄像头 Camera (P0)", pri="P0", pins=[("1", "+1V8"), ("2", "CAM_I2C_SDA")]),
    Component(ref="C8", value="10µF", desc="Camera +3V3 bulk decoupling",
              group="摄像头 Camera (P0)", pri="P0", pins=[("1", "+CAM_3V3"), ("2", "GND")]),
    Component(ref="C9", value="1µF", desc="Camera +3V3 decoupling",
              group="摄像头 Camera (P0)", pri="P0", pins=[("1", "+CAM_3V3"), ("2", "GND")]),
    Component(ref="C10", value="100nF", desc="Camera +3V3 HF decoupling",
              group="摄像头 Camera (P0)", pri="P0", pins=[("1", "+CAM_3V3"), ("2", "GND")]),
    Component(ref="C29", value="10µF", desc="Camera +5V bulk decoupling for Radxa Camera 4K",
              group="摄像头 Camera (P0)", pri="P0", pins=[("1", "+5V_SYS"), ("2", "GND")]),
    Component(ref="C30", value="100nF", desc="Camera +5V HF decoupling for Radxa Camera 4K",
              group="摄像头 Camera (P0)", pri="P0", pins=[("1", "+5V_SYS"), ("2", "GND")]),
]

# ─────────────────────────────────────────────────────────────────────────────
# Microphones + audio out (P0)
# ─────────────────────────────────────────────────────────────────────────────
AUDIO = [
    Component(ref="MK1", value="SPH0641LU4H-1", desc="PDM MEMS mic (L, SEL=GND)",
              group="音频 Audio (P0)", pri="P0",
              pins=[("VDD", "+1V8"), ("CLK", "PDM1_CLK"), ("DATA", "PDM1_DATA0"),
                    ("SEL", "GND"), ("GND", "GND")]),
    Component(ref="MK2", value="SPH0641LU4H-1", desc="PDM MEMS mic (R, SEL=VDD)",
              group="音频 Audio (P0)", pri="P0",
              pins=[("VDD", "+1V8"), ("CLK", "PDM1_CLK"), ("DATA", "PDM1_DATA1"),
                    ("SEL", "+1V8"), ("GND", "GND")]),
    Component(ref="U4", value="MAX98357AETE+T", desc="Class-D I2S/SAI mono amp (TQFN-16, no MCLK)",
              group="音频 Audio (P0)", pri="P0", mpn="MAX98357AETE+T", lcsc="C910544",
              note="GAIN=GND → low gain (3-6dB) for 8Ω/1W spkr; SW volume-limit at bring-up.",
              pins=[("VDD", "+5V_SYS"), ("GND", "GND"), ("BCLK", "SAI1_BCLK"),
                    ("LRC", "SAI1_LRCK"), ("DIN", "SAI1_SDO"), ("SD", "SPKR_EN_n"),
                    ("GAIN", "GND"), ("OUT+", "SPK_OUT_P"), ("OUT-", "SPK_OUT_N")]),
    Component(ref="FB1", value="Ferrite 600Ω@100MHz", desc="Class-D speaker EMI bead (OUT+)",
              group="音频 Audio (P0)", pri="P0", pins=[("1", "SPK_OUT_P"), ("2", "SPK_P_F")]),
    Component(ref="FB2", value="Ferrite 600Ω@100MHz", desc="Class-D speaker EMI bead (OUT-)",
              group="音频 Audio (P0)", pri="P0", pins=[("1", "SPK_OUT_N"), ("2", "SPK_N_F")]),
    Component(ref="C23", value="1nF", desc="Class-D EMI cap (OUT+ to GND)",
              group="音频 Audio (P0)", pri="P0", pins=[("1", "SPK_P_F"), ("2", "GND")]),
    Component(ref="C24", value="1nF", desc="Class-D EMI cap (OUT- to GND)",
              group="音频 Audio (P0)", pri="P0", pins=[("1", "SPK_N_F"), ("2", "GND")]),
    Component(ref="J3", value="JST-SH 2p (spkr)", desc="Speaker connector (post-EMI); 2 wire-leads",
              group="音频 Audio (P0)", pri="P0",
              note="Speaker = Ole Wolff OWS-091630W50A-8 (8Ω 1W, 16×9×3mm, LCSC C5840086), wire-leads.",
              pins=[("SPK+", "SPK_P_F"), ("SPK-", "SPK_N_F")]),
    Component(ref="C13", value="100nF", desc="Amp VDD decoupling",
              group="音频 Audio (P0)", pri="P0", pins=[("1", "+5V_SYS"), ("2", "GND")]),
]

# ─────────────────────────────────────────────────────────────────────────────
# USB-C (P0)
# ─────────────────────────────────────────────────────────────────────────────
USB = [
    Component(ref="J4", value="GCT USB4085 (USB2)", desc="USB-C receptacle (USB2 + 5V sink)",
              group="USB-C (P0)", pri="P0",
              pins=[("VBUS", "USB_VBUS"), ("GND", "GND"), ("DP", "USB_DP"),
                    ("DM", "USB_DM"), ("CC1", "USB_CC1"), ("CC2", "USB_CC2"),
                    ("SHLD", "GND")]),
    Component(ref="U5", value="TPD2E009", desc="USB2 D+/D- ESD clamp",
              group="USB-C (P0)", pri="P0",
              pins=[("DP", "USB_DP"), ("DM", "USB_DM"), ("GND", "GND")]),
    Component(ref="R1", value="5.1k", desc="USB-C CC1 pull-down (Sink role)",
              group="USB-C (P0)", pri="P0", pins=[("1", "USB_CC1"), ("2", "GND")]),
    Component(ref="R2", value="5.1k", desc="USB-C CC2 pull-down (Sink role)",
              group="USB-C (P0)", pri="P0", pins=[("1", "USB_CC2"), ("2", "GND")]),
    Component(ref="D3", value="SMAJ5.0A (TVS)", desc="USB VBUS ESD/TVS clamp (5V standoff)",
              group="USB-C (P0)", pri="P0", pins=[("1", "USB_VBUS"), ("2", "GND")]),
    Component(ref="U15", value="TPS25940 (e-fuse, opt)",
              desc="VBUS e-fuse: OVP/OCP/reverse-block (DNP-able; bypass via R3 if unused)",
              group="USB-C (P0)", pri="P0",
              pins=[("IN", "USB_VBUS"), ("EN", "USB_VBUS"), ("GND", "GND"), ("OUT", "VBUS_PROT")]),
    Component(ref="R3", value="0R / shunt", desc="VBUS_PROT→5V series 0R/shunt (current log)",
              group="USB-C (P0)", pri="P0", pins=[("1", "VBUS_PROT"), ("2", "+5V_SYS")]),
    Component(ref="C11", value="1µF", desc="VBUS input cap",
              group="USB-C (P0)", pri="P0", pins=[("1", "USB_VBUS"), ("2", "GND")]),
]

# ─────────────────────────────────────────────────────────────────────────────
# Power rails (P0 + P1)
# ─────────────────────────────────────────────────────────────────────────────
POWER = [
    Component(ref="U12", value="TLV75733 (LDO)", desc="3.3V rail regulator",
              group="电源 Power (P0)", pri="P0",
              pins=[("VIN", "+5V_SYS"), ("GND", "GND"), ("VOUT", "+3V3")]),
    Component(ref="U13", value="TLV75718 (LDO)", desc="1.8V VCCIO rail regulator",
              group="电源 Power (P0)", pri="P0",
              pins=[("VIN", "+3V3"), ("GND", "GND"), ("VOUT", "+1V8")]),
    Component(ref="C1", value="10µF", desc="+5V bulk decoupling",
              group="电源 Power (P0)", pri="P0", pins=[("1", "+5V_SYS"), ("2", "GND")]),
    Component(ref="C2", value="100nF", desc="+5V HF decoupling",
              group="电源 Power (P0)", pri="P0", pins=[("1", "+5V_SYS"), ("2", "GND")]),
    Component(ref="C3", value="10µF", desc="+3V3 bulk decoupling",
              group="电源 Power (P0)", pri="P0", pins=[("1", "+3V3"), ("2", "GND")]),
    Component(ref="C4", value="100nF", desc="+3V3 HF decoupling",
              group="电源 Power (P0)", pri="P0", pins=[("1", "+3V3"), ("2", "GND")]),
    Component(ref="C5", value="10µF", desc="+1V8 bulk decoupling",
              group="电源 Power (P0)", pri="P0", pins=[("1", "+1V8"), ("2", "GND")]),
    Component(ref="C6", value="100nF", desc="+1V8 HF decoupling",
              group="电源 Power (P0)", pri="P0", pins=[("1", "+1V8"), ("2", "GND")]),
]

# ─────────────────────────────────────────────────────────────────────────────
# Battery system (P1)
# ─────────────────────────────────────────────────────────────────────────────
BATTERY = [
    Component(ref="U6", value="TPS61022 (Boost)", desc="1S Li-Po → 5V boost converter",
              group="电池系统 Battery (P1)", pri="P1",
              pins=[("VIN", "+VBAT"), ("SW", "BOOST_SW"), ("EN", "BOOST_EN"),
                    ("FB", "+5V_SYS"), ("GND", "GND")]),
    Component(ref="R20", value="100k", desc="Boost EN pull-up to +VBAT; default boost enabled for bench bring-up",
              group="电池系统 Battery (P1)", pri="P1", pins=[("1", "+VBAT"), ("2", "BOOST_EN")]),
    Component(ref="L1", value="4.7µH", desc="Boost inductor",
              group="电池系统 Battery (P1)", pri="P1",
              pins=[("1", "+VBAT"), ("2", "BOOST_SW")]),
    Component(ref="U7", value="BQ25180", desc="1S Li-Po charger w/ power-path (I2C)",
              group="电池系统 Battery (P1)", pri="P1",
              pins=[("IN", "USB_VBUS"), ("SYS", "+VBAT"), ("BAT", "VBAT_P"),
                    ("TS", "BAT_NTC"), ("SCL", "FUEL_I2C_SCL"), ("SDA", "FUEL_I2C_SDA"),
                    ("INT", "CHG_INT_n"), ("GND", "GND")]),
    Component(ref="U8", value="BQ29700", desc="Single-cell battery protection (OVP/UVP/OCP)",
              group="电池系统 Battery (P1)", pri="P1",
              pins=[("VDD", "VBAT_P"), ("VM", "VBAT_N"), ("OUT", "+VBAT")]),
    Component(ref="U9", value="MAX17048", desc="I2C fuel gauge (SOC, low-batt IRQ)",
              group="电池系统 Battery (P1)", pri="P1",
              pins=[("VDD", "+VBAT"), ("CELL", "+VBAT"), ("SCL", "FUEL_I2C_SCL"),
                    ("SDA", "FUEL_I2C_SDA"), ("ALRT", "LOW_BAT_INT_n"), ("GND", "GND")]),
    Component(ref="J5", value="JST-PH 3p", desc="Battery connector (BAT+/BAT-/NTC)",
              group="电池系统 Battery (P1)", pri="P1",
              note="V1 BENCH cell = 1S 103450 ~2000mAh w/ PCM (~2.5h @3W). Glasses form = 2-3× "
                   "35×18×4mm (~500-750mAh, ~30-50min @3W → needs AI duty-cycling). "
                   "ASSEMBLY: if cell has NO NTC, populate R11 as fixed divider to a valid temp "
                   "(or disable BQ25180 TS) — else charger faults. Measure current via R3 shunt.",
              pins=[("BAT+", "VBAT_P"), ("BAT-", "VBAT_N"), ("NTC", "BAT_NTC")]),
    Component(ref="C7", value="22µF", desc="+VBAT bulk decoupling",
              group="电池系统 Battery (P1)", pri="P1", pins=[("1", "+VBAT"), ("2", "GND")]),
    Component(ref="R11", value="10k", desc="Battery NTC bias (placeholder)",
              group="电池系统 Battery (P1)", pri="P1", pins=[("1", "BAT_NTC"), ("2", "GND")]),
]

# ─────────────────────────────────────────────────────────────────────────────
# IMU + vibration (P1)
# ─────────────────────────────────────────────────────────────────────────────
SENSORS = [
    Component(ref="U10", value="ICM-42688-P", desc="6-axis IMU (accel+gyro, I2C)",
              group="传感器 IMU/Haptic (P1)", pri="P1",
              pins=[("VDD", "+1V8"), ("GND", "GND"), ("SCL", "IMU_I2C_SCL"),
                    ("SDA", "IMU_I2C_SDA"), ("INT1", "IMU_INT1")]),
    Component(ref="R9", value="2.2k", desc="IMU I2C SCL pull-up to +1V8",
              group="传感器 IMU/Haptic (P1)", pri="P1", pins=[("1", "+1V8"), ("2", "IMU_I2C_SCL")]),
    Component(ref="R10", value="2.2k", desc="IMU I2C SDA pull-up to +1V8",
              group="传感器 IMU/Haptic (P1)", pri="P1", pins=[("1", "+1V8"), ("2", "IMU_I2C_SDA")]),
    Component(ref="U11", value="DRV2605L", desc="LRA/ERM haptic driver",
              group="传感器 IMU/Haptic (P1)", pri="P1",
              pins=[("VDD", "+5V_SYS"), ("GND", "GND"), ("IN", "VIB_PWM"),
                    ("EN", "VIB_EN"), ("OUT+", "VIB_OUT_P"), ("OUT-", "VIB_OUT_N")]),
    Component(ref="J6", value="JST-SH 2p", desc="Vibration motor connector",
              group="传感器 IMU/Haptic (P1)", pri="P1",
              pins=[("M+", "VIB_OUT_P"), ("M-", "VIB_OUT_N")]),
]

# ─────────────────────────────────────────────────────────────────────────────
# GNSS / GPS (P0) — external module on UART (RK3576 has no on-chip GNSS)
# ─────────────────────────────────────────────────────────────────────────────
GNSS = [
    Component(ref="U14", value="MAX-M10S-00B-01", desc="u-blox GNSS (GPS/GLO/GAL/BDS), UART, VIO=1.8V",
              group="GNSS / 定位 (P0)", pri="P0", mpn="MAX-M10S-00B-01",
              note="VCC=3.3V, V_IO=1.8V (matches CM4 UART7 @1.8V), 50Ω RF, U.FL external active antenna.",
              pins=[("VCC", "+3V3"), ("V_IO", "+1V8"), ("V_BCKP", "+3V3"), ("GND", "GND"),
                    ("TXD", "GNSS_UART_RX"), ("RXD", "GNSS_UART_TX"),
                    ("TIMEPULSE", "GNSS_PPS"), ("RESET_N", "GNSS_RST_n"), ("RF_IN", "GNSS_RFIN")]),
    # RF front-end: DC-block/π-match (tune at bring-up) + active-antenna bias-tee (DNP if passive)
    Component(ref="C27", value="DC-block (series,tune)", desc="GNSS RF series match / DC block",
              group="GNSS / 定位 (P0)", pri="P0", pins=[("1", "GNSS_RFIN"), ("2", "GNSS_ANT")]),
    Component(ref="C25", value="π shunt (DNP,tune)", desc="GNSS π-match shunt, module side (DNP)",
              group="GNSS / 定位 (P0)", pri="P0", pins=[("1", "GNSS_RFIN"), ("2", "GND")]),
    Component(ref="C26", value="π shunt (DNP,tune)", desc="GNSS π-match shunt, antenna side (DNP)",
              group="GNSS / 定位 (P0)", pri="P0", pins=[("1", "GNSS_ANT"), ("2", "GND")]),
    Component(ref="L2", value="RF choke (active-ant)", desc="Bias-tee choke (DNP if passive antenna)",
              group="GNSS / 定位 (P0)", pri="P0", pins=[("1", "GNSS_ANT"), ("2", "V_ANT_BIAS")]),
    Component(ref="R17", value="10Ω (active-ant)", desc="Active-antenna bias feed from +3V3 (DNP if passive)",
              group="GNSS / 定位 (P0)", pri="P0", pins=[("1", "+3V3"), ("2", "V_ANT_BIAS")]),
    Component(ref="C28", value="100nF (active-ant)", desc="Antenna bias decoupling (DNP if passive)",
              group="GNSS / 定位 (P0)", pri="P0", pins=[("1", "V_ANT_BIAS"), ("2", "GND")]),
    Component(ref="J8", value="U.FL / IPEX", desc="GNSS antenna connector (50Ω; external active/passive)",
              group="GNSS / 定位 (P0)", pri="P0", pins=[("ANT", "GNSS_ANT"), ("GND", "GND")]),
    Component(ref="C14", value="100nF", desc="GNSS VCC decoupling",
              group="GNSS / 定位 (P0)", pri="P0", pins=[("1", "+3V3"), ("2", "GND")]),
    Component(ref="C15", value="10µF", desc="GNSS VCC bulk decoupling",
              group="GNSS / 定位 (P0)", pri="P0", pins=[("1", "+3V3"), ("2", "GND")]),
]

# ─────────────────────────────────────────────────────────────────────────────
# Indicators + debug
# ─────────────────────────────────────────────────────────────────────────────
DEBUG = [
    Component(ref="D1", value="LED Green", desc="Power LED (active-low GPIO sink)",
              group="指示 / 调试 Debug", pri="P0",
              pins=[("A", "LED_PWR_A"), ("K", "LED_PWR_n")]),
    Component(ref="R4", value="1k", desc="Power LED current limit",
              group="指示 / 调试 Debug", pri="P0", pins=[("1", "+3V3"), ("2", "LED_PWR_A")]),
    Component(ref="D2", value="LED Blue", desc="Status LED (active-low GPIO sink)",
              group="指示 / 调试 Debug", pri="P0",
              pins=[("A", "LED_STAT_A"), ("K", "LED_STATUS_n")]),
    Component(ref="R5", value="1k", desc="Status LED current limit",
              group="指示 / 调试 Debug", pri="P0", pins=[("1", "+3V3"), ("2", "LED_STAT_A")]),
    Component(ref="J7", value="Header 1x4 2.54mm", desc="UART debug header (TX/RX/GND/VREF)",
              group="指示 / 调试 Debug", pri="P0",
              pins=[("TX", "UART_DBG_TX"), ("RX", "UART_DBG_RX"),
                    ("GND", "GND"), ("VREF", "+3V3")]),
]


# ─────────────────────────────────────────────────────────────────────────────
# Test points (bring-up probe access) — single-pad TPs on key nets
# ─────────────────────────────────────────────────────────────────────────────
_TP_NETS = [
    ("VBAT", "+VBAT"), ("5V", "+5V_SYS"), ("3V3", "+3V3"), ("1V8", "+1V8"), ("GND", "GND"),
    ("UART_TX", "UART_DBG_TX"), ("UART_RX", "UART_DBG_RX"),
    ("CAM_SCL", "CAM_I2C_SCL"), ("CAM_SDA", "CAM_I2C_SDA"),
    ("IMU_SCL", "IMU_I2C_SCL"), ("IMU_SDA", "IMU_I2C_SDA"),
    ("FUEL_SCL", "FUEL_I2C_SCL"), ("FUEL_SDA", "FUEL_I2C_SDA"),
    ("RESET", "RESET_n"), ("RECOVERY", "RECOVERY_n"), ("CAM_EN", "CAM_PWR_EN"),
]
TESTPOINTS = [
    Component(ref=f"TP{i + 1}", value="TestPoint 1.0mm", desc=f"Test point: {lbl}",
              group="测试点 Test Points", pri="P0", pins=[("1", net)])
    for i, (lbl, net) in enumerate(_TP_NETS)
]

# ─────────────────────────────────────────────────────────────────────────────
# Manual buttons (recovery / reset / power) + pull-ups to +1V8 (active-low)
# ─────────────────────────────────────────────────────────────────────────────
BUTTONS = [
    Component(ref="SW1", value="Tact SW SMD", desc="RECOVERY / maskrom button (to GND)",
              group="按键 Buttons", pri="P0", pins=[("1", "RECOVERY_n"), ("2", "GND")]),
    Component(ref="SW2", value="Tact SW SMD", desc="RESET button (to GND)",
              group="按键 Buttons", pri="P0", pins=[("1", "RESET_n"), ("2", "GND")]),
    Component(ref="SW3", value="Tact SW SMD", desc="POWER button (to GND)",
              group="按键 Buttons", pri="P0", pins=[("1", "POWER_KEY"), ("2", "GND")]),
    Component(ref="R14", value="10k", desc="RECOVERY pull-up to +1V8",
              group="按键 Buttons", pri="P0", pins=[("1", "+1V8"), ("2", "RECOVERY_n")]),
    Component(ref="R15", value="10k", desc="RESET pull-up to +1V8",
              group="按键 Buttons", pri="P0", pins=[("1", "+1V8"), ("2", "RESET_n")]),
    Component(ref="R16", value="10k", desc="POWER_KEY pull-up to +1V8",
              group="按键 Buttons", pri="P0", pins=[("1", "+1V8"), ("2", "POWER_KEY")]),
    Component(ref="R18", value="100k", desc="WL_nDIS pull-up to +1V8; default Wi-Fi enabled",
              group="按键 Buttons", pri="P0", pins=[("1", "+1V8"), ("2", "WL_nDIS")]),
    Component(ref="R19", value="100k", desc="BT_nDIS pull-up to +1V8; default Bluetooth enabled",
              group="按键 Buttons", pri="P0", pins=[("1", "+1V8"), ("2", "BT_nDIS")]),
]

# ─────────────────────────────────────────────────────────────────────────────
# Added: I2C6 pull-ups, per-IC 100nF decoupling, GNSS antenna ESD
# ─────────────────────────────────────────────────────────────────────────────
EXTRA = [
    Component(ref="R12", value="2.2k", desc="Charger/Fuel I2C6 SCL pull-up to +1V8",
              group="电池系统 Battery (P1)", pri="P1", pins=[("1", "+1V8"), ("2", "FUEL_I2C_SCL")]),
    Component(ref="R13", value="2.2k", desc="Charger/Fuel I2C6 SDA pull-up to +1V8",
              group="电池系统 Battery (P1)", pri="P1", pins=[("1", "+1V8"), ("2", "FUEL_I2C_SDA")]),
    Component(ref="C16", value="100nF", desc="IMU U10 VDD decoupling",
              group="传感器 IMU/Haptic (P1)", pri="P1", pins=[("1", "+1V8"), ("2", "GND")]),
    Component(ref="C17", value="100nF", desc="Charger U7 VBUS decoupling",
              group="电池系统 Battery (P1)", pri="P1", pins=[("1", "USB_VBUS"), ("2", "GND")]),
    Component(ref="C18", value="100nF", desc="Fuel gauge U9 VDD decoupling",
              group="电池系统 Battery (P1)", pri="P1", pins=[("1", "+VBAT"), ("2", "GND")]),
    Component(ref="C19", value="100nF", desc="Boost U6 VIN decoupling",
              group="电池系统 Battery (P1)", pri="P1", pins=[("1", "+VBAT"), ("2", "GND")]),
    Component(ref="C20", value="100nF", desc="Haptic U11 VDD decoupling",
              group="传感器 IMU/Haptic (P1)", pri="P1", pins=[("1", "+5V_SYS"), ("2", "GND")]),
    Component(ref="C21", value="100nF", desc="LDO U12 +3V3 output decoupling",
              group="电源 Power (P0)", pri="P0", pins=[("1", "+3V3"), ("2", "GND")]),
    Component(ref="C22", value="100nF", desc="LDO U13 +1V8 output decoupling",
              group="电源 Power (P0)", pri="P0", pins=[("1", "+1V8"), ("2", "GND")]),
    Component(ref="D4", value="ESD low-cap RF 0.3pF", desc="GNSS antenna ESD clamp",
              group="GNSS / 定位 (P0)", pri="P0", pins=[("1", "GNSS_ANT"), ("2", "GND")]),
]

COMPONENTS: list[Component] = (
    CM4 + CAMERA + AUDIO + USB + POWER + BATTERY + SENSORS + GNSS + DEBUG
    + TESTPOINTS + BUTTONS + EXTRA
)


def _apply_footprints() -> None:
    for comp in COMPONENTS:
        if not comp.footprint:
            comp.footprint = _fp(comp.ref, _fallback_footprint(comp))


_apply_footprints()


def by_group() -> dict[str, list[Component]]:
    """Return components grouped in declaration order (for the report)."""
    groups: dict[str, list[Component]] = {}
    for comp in COMPONENTS:
        groups.setdefault(comp.group, []).append(comp)
    return groups


if __name__ == "__main__":
    # Quick sanity check: no duplicate refs.
    refs = [c.ref for c in COMPONENTS]
    dupes = {r for r in refs if refs.count(r) > 1}
    assert not dupes, f"Duplicate refs: {dupes}"
    print(f"{len(COMPONENTS)} components, {len(set(refs))} unique refs — OK")
