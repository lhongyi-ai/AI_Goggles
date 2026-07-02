#!/usr/bin/env python3
"""WORKING MASTER for the AI Glasses V2 (RK3576 chip-down) schematic.

This is the single source of truth for the V2 pre-layout schematic. It mirrors
the idiom of the V1 master (scripts/carrier_bom.py): every component is a
``Component`` with an ordered ``pins`` list of ``(pin_name, net_name)`` tuples.
The generator (generate_chipdown_sch.py) draws each as a box symbol and attaches
a global label per net, so same-named nets are electrically joined across the
one system sheet. Deriving the schematic and the BOM from ONE list keeps the
drawn nets and the written BOM from ever drifting apart.

SCOPE — this is deliberately the *pre-PCB-layout* system schematic only:
  * power domains + power tree topology (which rail comes from which regulator)
  * the AON control plane (every EN / PG / PWRON / WAKE / READY / FAULT / RESET
    handshake between nRF54L15, nPM1300, RK3576, NDP120 and the load switches)
  * the interface buses that are already knowable (MIPI CSI 4-lane, PDM, I2S,
    USB2 x2 [external + FCU760K], PCM, AON I2C/SPI/UART, SWD, current-sense I2C)
It is NOT a ball-level netlist. Parts whose datasheet / ball-map is not yet in
hand (RK3576, RK806S, LPDDR4X, eMMC, NDP120, the custom IMX415 module, the
Wi-Fi module) are drawn as FUNCTIONAL BLOCKS with only their architecturally
defined interface pins. The RK806->RK3576 rail names are the Radxa RK806S
reference set (Phase-2 "delta off Radxa reference") and are frozen only when
G02 (DDR) / G03 (PMIC) close.

Assembly status uses the BOM legend: Fit / DNP / HOLD / TBD.
Board region uses the 4-board partition from docs/05_hardware_partition.md.

Data source: AI_Glasses_Chipdown_BOM_V2.0 (BOM IDs C001-C045) plus the Phase-1
AON selection, AON power budget and Phase-3 power-tree decisions recorded in
docs/07_schematic_design.md. Every MPN here is an ENGINEERING CANDIDATE for
EVT, not a frozen production BOM (see the per-part gate column).
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Component:
    ref: str                        # KiCad reference designator (unique)
    bom_id: str                     # C0xx id from the V2 key-component table
    value: str                      # MPN or passive value
    desc: str                       # human description for the BOM report
    board: str                      # 4-board partition region
    # pins: ordered (pin_name, net_name). The generator splits the list in half:
    # first half on the left edge, second half on the right edge of the box.
    pins: list[tuple[str, str]] = field(default_factory=list)
    assembly: str = "Fit"           # Fit / DNP / HOLD / TBD
    pri: str = "P0"                 # P0 (must) / P1 (should)
    gate: str = ""                  # design gate that must close before freeze
    note: str = ""
    footprint: str = ""             # KiCad footprint id, when a package is known


# Board region short names (docs/05_hardware_partition.md)
FRONT = "Front Sensor Board"
COMPUTE = "R-Temple Compute Board"
AON = "L-Temple AON/Power Board"
REAR = "Temple Rears (batt/spkr/ant)"
EVT = "EVT Debug Tail"

# ─────────────────────────────────────────────────────────────────────────────
# NET NAMING (documented so the whole design is legible from this file alone)
#
# Power path / rails:
#   BATR_P, BATL_P  raw cell + terminals (right / left temple)
#   BAT_P           supplier-pack protected 1S2P pack +, into BQ25895/nPM1300
#   VSYS            nPM1300 power-path system node — main distribution rail
#   VBUS_RAW       VBUS from USB-C / pogo before input protection/eFuse
#   USB_5V          protected 5 V into BQ25895 / charger input
#   AON_1V8         nPM1300 BUCK1  (always on)
#   AON_3V3         nPM1300 BUCK2  (always on / mode)
#   SOC_5V          TPS61088 boost out -> RK806S input
#   CAM_1V1         TPS62840 buck out (sensor core)
#   CAM_1V8_SW      TPS22917 out (from AON_1V8) — camera I/O, gated
#   CAM_2V9         TLV75529 LDO out (sensor analog)
#   WIFI_3V3        TPS62825 buck out
#   WIFI_3V3_SW     wifi load-switch out -> module
#   AUDIO_PWR       audio load-switch out -> Class-D amp
#   VDD_CPU/GPU/NPU/LOGIC/DDR, VCC_DDRIO, VCCIO_1V8, VCC_3V3
#                   RK806S reference rails -> RK3576 / DDR / eMMC (G02/G03)
#
# AON control plane (nRF54L15 is master; direction in the note):
#   SOC_PWR_EN, SOC_5V_PGOOD, PMIC_PWRON, SOC_SHUTDOWN_REQ, SOC_SAFE_TO_OFF,
#   SOC_ALIVE, SOC_FAULT, WIFI_BUCK_EN, WIFI_LS_EN, WIFI_CHIP_EN, CAM_1V1_EN,
#   CAM_1V8_EN, CAM_2V9_EN, AUDIO_LS_EN, AUDIO_AMP_SD, DSP_RESET_L, DSP_WAKE,
#   DSP_READY, DSP_FAULT
#
# AON buses:
#   I2C_AON_SCL/SDA (nPM1300, BMI270, INA238s), PMIC_INT_L, PMIC_SHPHLD,
#   IMU_INT1/2, DSP_SPI_SCK/MOSI/MISO/CS_n, AON_UART_TX/RX (nRF<->RK3576),
#   NTC_R, NTC_L
#
# Interfaces:
#   MIPI  CSI_CLK_P/N, CSI_D0/1/2/3_P/N (4-lane IMX415 target) + CAM_I2C_SCL/SDA,
#         CAM_RST_L, CAM_PWDN_L, CAM_MCLK
#   Audio PDM_WAKE_CLK/DATA (wake mic->DSP), PDM_ARRAY_CLK/D0/D1 (array->RK3576),
#         I2S_BCLK/LRCLK/DIN (RK3576->amp)
#   Radio FCU760K over USB2: WIFI_USB_DP/DM, WIFI_PCM_CLK/SYNC/DIN/DOUT,
#         WIFI_CHIP_EN, WIFI_WAKE_L, WIFI_ANT, BLE_ANT_DNP
#   USB2  USB2_DP/DM (external), CC1, CC2
#   Debug SOC_DBG_TX/RX, NRF_SWDIO/SWDCLK, SOC_MASKROM_L, SOC_RESET_L, SOC_PWRKEY
# Active level is in the name: _L = active low, EN/PGOOD = active high.
# ─────────────────────────────────────────────────────────────────────────────


# ── Signal attributes (§2): for the signal dictionary + power-domain review. ──
# Keyed by net. The explicit entries below cover high-risk rails, control nets,
# buses and high-speed interfaces; net_meta() then normalizes every net into the
# full required attribute set for docs and schematic label fields:
#
#   name, source, dest, direction, dom, kind, default, pull, off_high, series,
#   esd, diff_pair, pinmux, dt, driver, xdom, isolation, layout, note
#
# "xdom" means the signal crosses a powered-domain boundary and therefore needs
# a reverse-feed/off-leakage check before layout entry.
NET_META: dict[str, dict] = {
    # power rails
    "BAT_P":       dict(dom="Vbat", kind="power", default="live", note="protected 1S2P pack +"),
    "VSYS":        dict(dom="Vbat", kind="power", default="live", note="nPM1300 power-path system node"),
    "VBUS_RAW":    dict(dom="5V",   kind="power", default="ext",  note="raw pogo/USB-C VBUS before eFuse/OVP"),
    "USB_5V":      dict(dom="5V",   kind="power", default="ext",  note="protected VBUS into BQ25895/nPM1300 sense"),
    "AON_1V8":     dict(dom="1.8V", kind="power", default="on",   note="always-on nPM1300 BUCK1"),
    "AON_3V3":     dict(dom="3.3V", kind="power", default="on",   note="always-on nPM1300 BUCK2"),
    "SOC_5V":      dict(dom="5V",   kind="power", default="off",  note="TPS61088 boost, gated"),
    "WIFI_3V3":    dict(dom="3.3V", kind="power", default="off",  note="TPS62825 buck, gated"),
    "WIFI_VBAT_3V3": dict(dom="3.3V", kind="power", default="off", note="FCU760K VBAT, load-switched"),
    "CAM_1V1":     dict(dom="1.1V", kind="power", default="off",  note="IMX415 DVDD"),
    "CAM_1V8_SW":  dict(dom="1.8V", kind="power", default="off",  note="IMX415 IOVDD"),
    "CAM_2V9":     dict(dom="2.9V", kind="power", default="off",  note="IMX415 AVDD"),
    "AUDIO_PWR":   dict(dom="Vbat", kind="power", default="off",  note="Class-D amp, gated"),
    # high-power enables (default OFF, crash-safe, §4)
    "SOC_PWR_EN":  dict(dom="1.8V", kind="control", direction="nRF->boost", default="low (OFF)", note="100k pulldown"),
    "SOC_5V_PGOOD":dict(dom="1.8V", kind="control", direction="boost->nRF", default="low", note="power-good in"),
    "PMIC_PWRON":  dict(dom="1.8V", kind="control", direction="nRF->RK806", default="low (OFF)", xdom=True, note="100k pulldown; into SoC domain"),
    "SOC_RESET_L": dict(dom="1.8V", kind="control", direction="nRF/btn->RK3576", default="low (reset)", xdom=True, note="active low"),
    "SOC_SHUTDOWN_REQ": dict(dom="1.8V", kind="control", direction="nRF->RK3576", default="low", xdom=True, note="request Linux shutdown"),
    "SOC_SAFE_TO_OFF":  dict(dom="1.8V", kind="control", direction="RK3576->nRF", default="low", xdom=True, note="synced, safe to cut SOC_5V"),
    "SOC_ALIVE":   dict(dom="1.8V", kind="control", direction="RK3576->nRF", default="low", xdom=True, note="liveness"),
    "SOC_FAULT":   dict(dom="1.8V", kind="control", direction="RK3576->nRF", default="low", xdom=True, note="fault"),
    "CAM_1V1_EN":  dict(dom="1.8V", kind="control", direction="nRF->buck", default="low (OFF)", note="100k pulldown"),
    "CAM_1V8_EN":  dict(dom="1.8V", kind="control", direction="nRF->LSW",  default="low (OFF)", note="100k pulldown"),
    "CAM_2V9_EN":  dict(dom="1.8V", kind="control", direction="nRF->LDO",  default="low (OFF)", note="100k pulldown"),
    "WIFI_BUCK_EN":dict(dom="1.8V", kind="control", direction="nRF->buck", default="low (OFF)", note="100k pulldown"),
    "WIFI_LS_EN":  dict(dom="1.8V", kind="control", direction="nRF->LSW",  default="low (OFF)", note="100k pulldown"),
    "WIFI_CHIP_EN":dict(dom="3.3V", kind="control", direction="nRF->FCU760K", default="low (OFF)", xdom=True, note="100k pulldown; module off default (pack §9)"),
    "AUDIO_LS_EN": dict(dom="1.8V", kind="control", direction="nRF->LSW",  default="low (OFF)", note="100k pulldown"),
    "AUDIO_AMP_SD":dict(dom="Vbat", kind="control", direction="nRF->amp",  default="low (muted)", note="100k pulldown"),
    "DSP_WAKE":    dict(dom="1.8V", kind="control", direction="NDP120->nRF", default="low", note="wake IRQ"),
    "DSP_READY":   dict(dom="1.8V", kind="control", direction="NDP120->nRF", default="low"),
    "DSP_FAULT":   dict(dom="1.8V", kind="control", direction="NDP120->nRF", default="low"),
    "DSP_RESET_L": dict(dom="1.8V", kind="control", direction="nRF->NDP120", default="low (reset)", note="active low"),
    # AON buses
    "I2C_AON_SCL": dict(dom="1.8V", kind="bus", default="pull-up 2.2k", note="nPM1300/BMI270/INA238"),
    "I2C_AON_SDA": dict(dom="1.8V", kind="bus", default="pull-up 2.2k"),
    "AON_UART_TX": dict(dom="1.8V", kind="bus", direction="nRF->RK3576", default="idle high", xdom=True, note="series 0R/33R + reverse-feed check when SoC off"),
    "AON_UART_RX": dict(dom="1.8V", kind="bus", direction="RK3576->nRF", default="idle high", xdom=True),
    # interfaces
    "CSI_CLK_P":   dict(dom="1.2V", kind="diff", default="hi-Z", note="MIPI 100R diff, ultra-low-cap ESD, no stub"),
    "CSI_CLK_N":   dict(dom="1.2V", kind="diff", default="hi-Z", note="MIPI 100R diff"),
    "CSI_D0_P":    dict(dom="1.2V", kind="diff", default="hi-Z", note="MIPI 100R diff"),
    "CSI_D1_P":    dict(dom="1.2V", kind="diff", default="hi-Z", note="MIPI 100R diff"),
    "USB2_DP":     dict(dom="3.3V", kind="diff", default="hi-Z", note="USB2 90R diff, ESD at connector"),
    "USB2_DM":     dict(dom="3.3V", kind="diff", default="hi-Z", note="USB2 90R diff"),
    "WIFI_USB_DP": dict(dom="3.3V", kind="diff", default="hi-Z", note="FCU760K USB2 90R diff (internal)"),
    "WIFI_USB_DM": dict(dom="3.3V", kind="diff", default="hi-Z", note="FCU760K USB2 90R diff (internal)"),
    "CAM_RST_L":   dict(dom="1.8V", kind="control", direction="RK3576->cam", default="low (XCLR held)", xdom=True, note="active low; hold low until rails+clock up (§24)"),
    "CAM_PWDN_L":  dict(dom="1.8V", kind="control", direction="RK3576->cam", default="low", xdom=True),
    "CAM_MCLK":    dict(dom="1.8V", kind="control", direction="RK3576->cam", default="off", note="INCK; enable only after rails stable (§24)"),
    "PDM_WAKE_CLK":dict(dom="AON",  kind="bus", direction="NDP120->mic", default="off", note="wake mic PDM; 0R/22R debug pos; single master"),
    "PDM_ARRAY_CLK":dict(dom="AON", kind="bus", direction="RK3576->mic", default="off", note="array PDM; 0R to select NDP120/RK3576 path"),
    "WIFI_ANT":    dict(dom="RF",   kind="analog", default="-", note="50R; pi-match; shared Wi-Fi/BLE FPC antenna; keep out from battery/magnet/shield/copper"),
    "BLE_ANT":     dict(dom="RF",   kind="analog", default="-", note="DNP optional FCU760K ANT_BT test/matching node; no separate BLE antenna fitted in EVT V2.0"),
    # battery / protection
    "CELL_NEG":    dict(dom="Vbat", kind="power", default="live", note="internal cell negative into supplier pack PCM; no board BQ2970"),
    "NPM_VBAT":    dict(dom="Vbat", kind="power", default="live", note="nPM1300 VBAT (after RS1 total shunt)"),
    "NTC_R":       dict(dom="analog", kind="analog", default="-", note="per-cell NTC (§15)"),
    "NTC_L":       dict(dom="analog", kind="analog", default="-", note="per-cell NTC (§15)"),
}

SIGNAL_META_FIELDS = (
    "name", "source", "dest", "direction", "dom", "kind", "default", "pull",
    "off_high", "series", "esd", "diff_pair", "pinmux", "dt", "driver",
    "xdom", "isolation", "layout", "note",
)


POWER_SOURCE_HINTS = {
    "BAT_P": "RS2/RS3 branch shunts from LP451165 1S2P pack",
    "BATR_P": "right LP451165 cell",
    "BATL_P": "left LP451165 cell",
    "BATR_F": "F1 branch fuse",
    "BATL_F": "F2 branch fuse",
    "NPM_VBAT": "RS1 pack-total shunt",
    "VSYS": "nPM1300 power-path output",
    "USB_5V": "USB-C or magnetic pogo VBUS",
    "VBUS_RAW": "USB-C or magnetic pogo before input protection",
    "AON_1V8": "nPM1300 BUCK1",
    "AON_3V3": "nPM1300 BUCK2",
    "AON_LSW2": "nPM1300 load switch 2",
    "SOC_IN": "RS4 from VSYS",
    "SOC_5V": "TPS61088 boost output",
    "WIFI_IN": "RS5 from VSYS",
    "WIFI_3V3": "TPS62825 output",
    "WIFI_VBAT_3V3": "TPS22917 Wi-Fi load-switch output",
    "AUDIO_IN": "RS6 from VSYS",
    "AUDIO_PWR": "TPS22917 audio load-switch output",
    "CAM_1V1": "TPS62840 output",
    "CAM_1V1_S": "RS7 Kelvin sense output to camera DVDD",
    "CAM_1V8_SW": "TPS22917 camera I/O load-switch output",
    "CAM_1V8_S": "RS8 Kelvin sense output to camera IOVDD",
    "CAM_2V9": "TLV75529 output",
    "CAM_2V9_S": "RS9 Kelvin sense output to camera AVDD",
    "VDD_CPU": "RK806S rail",
    "VDD_GPU": "RK806S rail",
    "VDD_NPU": "RK806S rail",
    "VDD_LOGIC": "RK806S rail",
    "VDD_DDR": "RK806S rail",
    "VCC_DDRIO": "RK806S rail",
    "VCCIO_1V8": "RK806S rail",
    "VCC_3V3": "RK806S rail",
}

_DIFF_PAIR_MATES = {
    "CSI_CLK_P": "CSI_CLK_N", "CSI_CLK_N": "CSI_CLK_P",
    "CSI_D0_P": "CSI_D0_N", "CSI_D0_N": "CSI_D0_P",
    "CSI_D1_P": "CSI_D1_N", "CSI_D1_N": "CSI_D1_P",
    "CSI_D2_P": "CSI_D2_N", "CSI_D2_N": "CSI_D2_P",
    "CSI_D3_P": "CSI_D3_N", "CSI_D3_N": "CSI_D3_P",
    "USB2_DP": "USB2_DM", "USB2_DM": "USB2_DP",
    "WIFI_USB_DP": "WIFI_USB_DM", "WIFI_USB_DM": "WIFI_USB_DP",
    "SPK_P": "SPK_N", "SPK_N": "SPK_P",
    "HAPTIC_P": "HAPTIC_N", "HAPTIC_N": "HAPTIC_P",
}

_FULL_NAMES = {
    "SOC_PWR_EN": "SoC 5V boost enable, active high",
    "SOC_5V_PGOOD": "SoC 5V boost power-good, active high",
    "PMIC_PWRON": "RK806 PMIC power-on request",
    "SOC_RESET_L": "RK3576 reset, active low",
    "SOC_SHUTDOWN_REQ": "Linux shutdown request handshake",
    "SOC_SAFE_TO_OFF": "Linux safe-to-remove-power handshake",
    "SOC_ALIVE": "RK3576 liveness heartbeat",
    "SOC_FAULT": "RK3576 fault indication",
    "WIFI_CHIP_EN": "FCU760K chip enable, active high",
    "DSP_WAKE": "NDP120 wake interrupt to nRF",
    "DSP_READY": "NDP120 ready indication",
    "DSP_FAULT": "NDP120 fault indication",
    "DSP_RESET_L": "NDP120 reset, active low",
    "PDM_WAKE_CLK": "Dedicated wake-mic PDM clock",
    "PDM_WAKE_DATA": "Dedicated wake-mic PDM data",
    "PDM_ARRAY_CLK": "Array-mic PDM clock",
    "PDM_ARRAY_D0": "Array-mic PDM data 0",
    "PDM_ARRAY_D1": "Array-mic PDM data 1",
    "WIFI_ANT": "Wi-Fi/BT shared RF antenna feed",
    "BLE_ANT": "Optional FCU760K ANT_BT DNP RF test feed",
}


def _is_truthy(v: object) -> bool:
    if isinstance(v, str):
        return v.strip().lower() in {"1", "true", "yes", "y"}
    return bool(v)


def _endpoint_label(ep: dict[str, str]) -> str:
    return f"{ep['ref']}.{ep['pin']} ({ep['board']})"


def net_endpoints(net: str) -> list[dict[str, str]]:
    """Return all schematic endpoints for a net."""
    out: list[dict[str, str]] = []
    target = net.strip()
    for comp in COMPONENTS:
        for pin, pin_net in comp.pins:
            if pin_net.strip() == target:
                out.append({
                    "ref": comp.ref,
                    "pin": pin,
                    "value": comp.value,
                    "board": comp.board,
                    "bom_id": comp.bom_id,
                })
    return out


def _infer_kind(net: str, explicit: str | None) -> str:
    if explicit:
        return explicit
    n = net.upper()
    if n == "GND" or n.startswith(("VDD", "VCC")) or n in POWER_SOURCE_HINTS:
        return "power"
    if n.endswith(("_P", "_N", "_DP", "_DM")) and n in _DIFF_PAIR_MATES:
        return "diff"
    if "ANT" in n or n.startswith(("NTC", "SOC_NTC")):
        return "analog"
    if any(s in n for s in ("I2C", "SPI", "UART", "PDM", "I2S", "PCM", "DDR", "EMMC", "FSPI", "SWD", "USB_CC")):
        return "bus"
    if n.endswith(("_EN", "_PGOOD", "_RESET_L", "_RST_L", "_PWDN_L", "_WAKE_L", "_INT_L", "_SHPHLD")):
        return "control"
    if any(s in n for s in ("PWR", "ALIVE", "FAULT", "READY", "WAKE", "MASKROM", "PWRKEY", "SLEEP")):
        return "control"
    return "signal"


def _infer_domain(net: str, kind: str, explicit: str | None) -> str:
    if explicit:
        return explicit
    n = net.upper()
    if n == "GND":
        return "0V"
    if n in {"USB_5V", "SOC_5V"}:
        return "5V"
    if "1V1" in n:
        return "1.1V"
    if "1V8" in n or n in {"VCCIO_1V8", "VCC_DDRIO"}:
        return "1.8V"
    if "2V9" in n:
        return "2.9V"
    if "3V3" in n or n == "VCC_3V3":
        return "3.3V"
    if n.startswith(("VDD_CPU", "VDD_GPU", "VDD_NPU", "VDD_LOGIC", "VDD_DDR")):
        return "RK806 rail (TBD)"
    if n.startswith(("BAT", "CELL", "NPM", "VSYS", "SOC_IN", "WIFI_IN", "AUDIO_IN")):
        return "Vbat"
    if "CSI_" in n:
        return "MIPI D-PHY"
    if "ANT" in n:
        return "RF"
    if kind in {"control", "bus"}:
        return "1.8V unless final pinmux says otherwise"
    return "TBD"


def _infer_default(net: str, kind: str, explicit: str | None) -> str:
    if explicit:
        return explicit
    n = net.upper()
    if n == "GND":
        return "0V"
    if kind == "power":
        if n.startswith(("AON_", "BAT", "NPM", "VSYS", "CELL")):
            return "on/live in AON mode"
        return "off until owning regulator is enabled"
    if n.endswith("_EN"):
        return "low (OFF)"
    if n.endswith(("_RESET_L", "_RST_L", "_PWDN_L", "_MASKROM_L")):
        return "low or pulled to safe state until firmware owns it"
    if "I2C" in n:
        return "pulled high"
    if "UART" in n:
        return "idle high"
    if kind == "diff":
        return "hi-Z when source domain is off"
    if kind == "analog":
        return "passive / sensed"
    return "TBD at pinmux freeze"


def _infer_pull(net: str, default: str) -> str:
    n = net.upper()
    if n in {"USB_CC1", "USB_CC2"}:
        return "5.1k Rd to GND"
    if "I2C_AON" in n:
        return "2.2k to AON_1V8 (R3/R4)"
    if "CAM_I2C" in n:
        return "2.2k to CAM_1V8_SW (R5/R6)"
    if "SOC_PMIC" in n:
        return "2.2k to VCCIO_1V8 (R9/R10)"
    if n in {
        "SOC_PWR_EN", "PMIC_PWRON", "CAM_1V1_EN", "CAM_1V8_EN", "CAM_2V9_EN",
        "WIFI_BUCK_EN", "WIFI_LS_EN", "WIFI_CHIP_EN", "AUDIO_LS_EN", "AUDIO_AMP_SD",
    }:
        return "100k pulldown (R11-R20)"
    if "pulled high" in default:
        return "pull-up required"
    return "none / TBD"


def _infer_direction(net: str, kind: str, explicit: str | None) -> str:
    if explicit:
        return explicit
    n = net.upper()
    if kind == "power":
        return "source->loads"
    if n.endswith("_SCL"):
        return "controller->targets"
    if n.endswith("_SDA"):
        return "bidirectional open-drain"
    if "UART_TX" in n or n.endswith("_MOSI") or n.endswith("_SCK") or n.endswith("_CS_N"):
        return "owner->peer"
    if "UART_RX" in n or n.endswith("_MISO"):
        return "peer->owner"
    if "CSI_" in n:
        return "camera->RK3576"
    if "USB" in n:
        return "bidirectional"
    if n.startswith("PDM_WAKE_CLK"):
        return "NDP120->wake mic"
    if n.startswith("PDM_WAKE_DATA"):
        return "wake mic->NDP120"
    if n.startswith("PDM_ARRAY_CLK"):
        return "RK3576->array mics"
    if n.startswith("PDM_ARRAY_D"):
        return "array mics->RK3576"
    if n.startswith("I2S_"):
        return "RK3576->amp"
    return "see endpoints"


def _infer_software(net: str) -> tuple[str, str, str]:
    n = net.upper()
    if any(s in n for s in ("CSI_", "CAM_I2C", "CAM_RST", "CAM_PWDN", "CAM_MCLK")):
        return ("RK3576 camera pinmux; G10 module pinout", "camera node + CSI/ISP graph", "imx415 + rkisp")
    if n.startswith("WIFI_USB") or n.startswith("WIFI_PCM") or n in {"WIFI_CHIP_EN", "WIFI_WAKE_L"}:
        return ("RK3576 USB2/PCM + nRF GPIO for CHIP_EN", "usb host + optional bt-audio PCM", "usbcore + Quectel firmware")
    if n.startswith("USB2") or n.startswith("USB_CC"):
        return ("RK3576 USB2 OTG/host", "usb2 port / connector", "dwc2/xhci + Type-C sink policy")
    if n.startswith(("PDM_ARRAY", "I2S_")):
        return ("RK3576 audio pinmux", "sound card / PDM / I2S nodes", "ALSA SoC audio")
    if n.startswith(("PDM_WAKE", "DSP_")):
        return ("nRF SPI/GPIO + NDP120 host interface", "nRF firmware config", "Syntiant SDK / nRF app")
    if n.startswith(("I2C_AON", "IMU_", "PMIC_INT", "PMIC_SHPHLD", "HAPTIC")):
        return ("nRF AON I2C/GPIO", "nRF firmware config", "nPM1300/BMI270/INA238/DRV2605L app drivers")
    if n.startswith(("SOC_", "PMIC_PWRON", "AON_UART")):
        return ("nRF GPIO/UART + RK3576 GPIO/UART DT", "power-state handshake + uart node", "nRF app + Linux GPIO/UART")
    if n.startswith("SOC_PMIC"):
        return ("RK3576 PMIC I2C", "rk806 regulator node", "rk806/regulator")
    if n.startswith(("DDR", "EMMC", "FSPI")):
        return ("RK3576 fixed-function bus", "bootloader + storage nodes", "Rockchip BSP")
    if n.startswith("NRF_SWD"):
        return ("debug only", "none", "SWD probe")
    return ("none / TBD", "none / TBD", "none / TBD")


def _infer_layout(net: str, kind: str) -> str:
    n = net.upper()
    if n.startswith("CSI_"):
        return "100 ohm diff, length match, continuous ground, no stubs, ESD at FPC"
    if n in {"USB2_DP", "USB2_DM", "WIFI_USB_DP", "WIFI_USB_DM"}:
        return "90 ohm diff, pair route, no stubs, continuous ground"
    if "ANT" in n:
        return "50 ohm controlled impedance, pi-match, antenna keep-out"
    if n.startswith("PDM"):
        return "short clock, continuous ground; keep out of boost/SW/RF zones"
    if kind == "power":
        return "wide/short copper; local decoupling; current-sense Kelvin where named"
    if kind == "control":
        return "keep away from SW nodes; verify default pull before MCU boot"
    return "standard layout; verify at pinmux/placement"


def _infer_esd(net: str, kind: str) -> str:
    n = net.upper()
    if n.startswith("CSI_"):
        return "yes, low-cap at FPC entry (U18/U19)"
    if n in {"USB2_DP", "USB2_DM"}:
        return "yes, low-cap at connector (U24)"
    if n.startswith("WIFI_USB"):
        return "module-internal side; add only if HW Design requires"
    if "ANT" in n:
        return "RF-approved only if required"
    if kind == "power" and n == "USB_5V":
        return "VBUS ESD/OV strategy required"
    return "no / TBD"


def net_meta(net: str) -> dict[str, str]:
    """Full signal-attribute record for one net, explicit NET_META plus inference."""
    raw = NET_META.get(net, {})
    kind = _infer_kind(net, raw.get("kind"))
    dom = _infer_domain(net, kind, raw.get("dom"))
    default = _infer_default(net, kind, raw.get("default"))
    direction = _infer_direction(net, kind, raw.get("direction"))
    endpoints = net_endpoints(net)
    boards = {ep["board"] for ep in endpoints}
    xdom = _is_truthy(raw.get("xdom", False)) or (len(boards) > 1 and kind in {"control", "bus", "diff", "analog"})
    pinmux, dt, driver = _infer_software(net)

    source = raw.get("source")
    dest = raw.get("dest")
    if not source:
        source = POWER_SOURCE_HINTS.get(net)
    if not source and "->" in direction and "<->" not in direction:
        source = direction.split("->", 1)[0]
    if not source:
        source = _endpoint_label(endpoints[0]) if endpoints else "TBD"
    if not dest:
        if "->" in direction and "<->" not in direction:
            dest = direction.split("->", 1)[1]
        else:
            dest_eps = endpoints[1:] if len(endpoints) > 1 else endpoints
            dest = "; ".join(_endpoint_label(ep) for ep in dest_eps) if dest_eps else "TBD"

    meta = {
        "name": raw.get("name", _FULL_NAMES.get(net, net.replace("_", " "))),
        "source": str(source),
        "dest": str(dest),
        "direction": direction,
        "dom": dom,
        "kind": kind,
        "default": default,
        "pull": raw.get("pull", _infer_pull(net, default)),
        "off_high": raw.get(
            "off_high",
            "No; prove no reverse-feed or add isolation" if xdom else ("N/A" if kind == "power" else "same-domain only"),
        ),
        "series": raw.get(
            "series",
            "0R/22-33R recommended" if net.startswith(("PDM_", "AON_UART")) else ("optional 0R debug" if kind in {"control", "bus"} else "none"),
        ),
        "esd": raw.get("esd", _infer_esd(net, kind)),
        "diff_pair": raw.get("diff_pair", _DIFF_PAIR_MATES.get(net, "no")),
        "pinmux": raw.get("pinmux", pinmux),
        "dt": raw.get("dt", dt),
        "driver": raw.get("driver", driver),
        "xdom": "yes" if xdom else "no",
        "isolation": raw.get(
            "isolation",
            "required: default-safe pull + leakage/reverse-feed check" if xdom else "not a power-domain crossing",
        ),
        "layout": raw.get("layout", _infer_layout(net, kind)),
        "note": raw.get("note", "derived from endpoints; verify at the owning gate"),
    }
    return {k: str(meta.get(k, "")) for k in SIGNAL_META_FIELDS}


def C(**kw) -> Component:
    return Component(**kw)


# ── C001–C008, C015–C016: R-Temple Compute Board (RK3576 island) ─────────────
COMPUTE_BOARD = [
    C(ref="U1", bom_id="C001", value="RK3576", board=COMPUTE, assembly="Fit",
      gate="G01 (RK3576 datasheet/HDG/ballmap/DDR guide)",
      footprint="AI_Glasses_V2:VERIFY_FCCSP698L_16x17",
      desc="Main SoC — 8-core, 6 TOPS NPU, ISP, MIPI CSI, H.264/265. Demand-started "
           "compute island (NOT always-on). Functional block: interface pins only.",
      note="FCCSP698L 16.1x17.2mm 0.6mm. Ball map not yet released -> only "
           "architecturally-defined interface pins are drawn. Start as a delta off "
           "the Radxa reference (Phase 2).",
      pins=[
          # power in (RK806 rails)
          ("VDD_CPU", "VDD_CPU"), ("VDD_GPU", "VDD_GPU"), ("VDD_NPU", "VDD_NPU"),
          ("VDD_LOGIC", "VDD_LOGIC"), ("VDD_DDR", "VDD_DDR"), ("VCC_DDRIO", "VCC_DDRIO"),
          ("VCCIO_1V8", "VCCIO_1V8"), ("VCC_3V3", "VCC_3V3"), ("GND", "GND"),
          ("XIN", "SOC_XIN"), ("XOUT", "SOC_XOUT"),
          # AON handshake
          ("PMIC_SLEEP", "PMIC_SLEEP"), ("SHUTDOWN_REQ", "SOC_SHUTDOWN_REQ"),
          ("SAFE_TO_OFF", "SOC_SAFE_TO_OFF"), ("ALIVE", "SOC_ALIVE"), ("FAULT", "SOC_FAULT"),
          ("AON_UART_RX", "AON_UART_TX"), ("AON_UART_TX", "AON_UART_RX"),
          # DDR / eMMC buses (to blocks)
          ("DDR_BUS", "DDR_BUS"), ("EMMC_BUS", "EMMC_BUS"), ("FSPI_BUS", "FSPI_BUS"),
          # camera MIPI CSI (2-lane 1080p) + control
          ("CSI_CLK_P", "CSI_CLK_P"), ("CSI_CLK_N", "CSI_CLK_N"),
          ("CSI_D0_P", "CSI_D0_P"), ("CSI_D0_N", "CSI_D0_N"),
          ("CSI_D1_P", "CSI_D1_P"), ("CSI_D1_N", "CSI_D1_N"),
          ("CSI_D2_P", "CSI_D2_P"), ("CSI_D2_N", "CSI_D2_N"),
          ("CSI_D3_P", "CSI_D3_P"), ("CSI_D3_N", "CSI_D3_N"),
          ("CAM_I2C_SCL", "CAM_I2C_SCL"), ("CAM_I2C_SDA", "CAM_I2C_SDA"),
          ("CAM_RST_L", "CAM_RST_L"), ("CAM_PWDN_L", "CAM_PWDN_L"), ("CAM_MCLK", "CAM_MCLK"),
          # audio
          ("PDM_ARR_CLK", "PDM_ARRAY_CLK"), ("PDM_ARR_D0", "PDM_ARRAY_D0"),
          ("PDM_ARR_D1", "PDM_ARRAY_D1"),
          ("I2S_BCLK", "I2S_BCLK"), ("I2S_LRCLK", "I2S_LRCLK"), ("I2S_DIN", "I2S_DIN"),
          ("SARADC_NTC", "SOC_NTC"),
          # radio: FCU760K over a 2nd USB2 host + PCM (BT audio), per Radxa CM4 v1.20 p20
          ("USB2_WIFI_DP", "WIFI_USB_DP"), ("USB2_WIFI_DM", "WIFI_USB_DM"),
          ("PCM_CLK", "WIFI_PCM_CLK"), ("PCM_SYNC", "WIFI_PCM_SYNC"),
          ("PCM_DIN", "WIFI_PCM_DIN"), ("PCM_DOUT", "WIFI_PCM_DOUT"),
          ("WIFI_WAKE_L", "WIFI_WAKE_L"),
          # usb2 (external) + debug
          ("USB2_DP", "USB2_DP"), ("USB2_DM", "USB2_DM"),
          ("DBG_UART_TX", "SOC_DBG_TX"), ("DBG_UART_RX", "SOC_DBG_RX"),
          ("MASKROM_n", "SOC_MASKROM_L"), ("RESET_n", "SOC_RESET_L"), ("PWRKEY", "SOC_PWRKEY"),
      ]),
    C(ref="U2", bom_id="C002", value="RK806S-5 QFN68 7x7x0.90mm", board=COMPUTE, assembly="HOLD",
      gate="G03 (official RK806S-5 datasheet, OTP/default rails, sequence, layout guide)",
      footprint="AI_Glasses_V2:VERIFY_QFN68_7x7_EP5.49_P0.35",
      desc="SoC PMIC — generates CPU/GPU/NPU/DDR/IO rails + power sequencing for RK3576. "
           "Reuse verified RK3576 power architecture; NOT for AON.",
      note="Package envelope can be used for placement: QFN68 + exposed thermal pad, body "
           "7.0x7.0mm, max height 0.90mm, 0.35mm pitch, ePad about 5.49x5.49mm, MSL3. "
           "Power sequence, OTP/default voltage table and compensation parts remain HOLD "
           "until complete Rockchip/Radxa reference collateral is reviewed.",
      pins=[
          ("VIN", "SOC_5V"), ("GND", "GND"),
          ("PWRON", "PMIC_PWRON"), ("SLEEP", "PMIC_SLEEP"),
          ("I2C_SCL", "SOC_PMIC_SCL"), ("I2C_SDA", "SOC_PMIC_SDA"),
          ("RESET_n", "SOC_RESET_L"),
          ("VDD_CPU", "VDD_CPU"), ("VDD_GPU", "VDD_GPU"), ("VDD_NPU", "VDD_NPU"),
          ("VDD_LOGIC", "VDD_LOGIC"), ("VDD_DDR", "VDD_DDR"), ("VCC_DDRIO", "VCC_DDRIO"),
          ("VCCIO_1V8", "VCCIO_1V8"), ("VCC_3V3", "VCC_3V3"),
      ]),
    C(ref="U3", bom_id="C003", value="Samsung K4U6E3S4AA-MGCL", board=COMPUTE, assembly="HOLD",
      gate="G02 (Samsung datasheet/ball map/IBIS + Rockchip DDR AVL/init + length report)",
      footprint="AI_Glasses_V2:VERIFY_FBGA200_0.65",
      desc="EVT system memory baseline — Samsung K4U6E3S4AA-MGCL, 16Gb / 2GB, x32, "
           "200-ball FBGA 0.65mm, LPDDR4X-4266 class. Use this Radxa reference MPN for "
           "first chip-down boot risk reduction; 4GB is a later BOM variant only.",
      note="Do not substitute the 32Gb/4GB K4UBE3D4AB-MGCL unless Rockchip confirms DDR AVL, "
           "training binary/init parameters, rank/capacity config and ball assignment compatibility.",
      pins=[("VDD_DDR", "VDD_DDR"), ("VDDQ", "VCC_DDRIO"), ("GND", "GND"),
            ("DDR_BUS", "DDR_BUS")]),
    C(ref="U4", bom_id="C004", value="Samsung KLMAG1JENB-B041", board=COMPUTE, assembly="HOLD",
      gate="G04 (official Samsung datasheet/package + BSP boot/HS200 then HS400 validation)",
      footprint="AI_Glasses_V2:VERIFY_BGA153",
      desc="EVT system storage baseline — Samsung KLMAG1JENB-B041, 16GB eMMC 5.1, "
           "153-FBGA, 11.5x13.0x0.8mm, 0.5mm pitch, 8-bit, HS400 capable. VCC 2.7-3.6V, "
           "VCCQ uses 1.8V in this project. 32GB upgrade is a later BSP/supply variant.",
      pins=[("VCC", "VCC_3V3"), ("VCCQ", "VCCIO_1V8"), ("GND", "GND"),
            ("EMMC_BUS", "EMMC_BUS")]),
    C(ref="Y1", bom_id="C005", value="24 MHz 10 ppm XTAL", board=COMPUTE, assembly="Fit",
      gate="G01 (reuse reference CL/ESR + placement distance per HDG)",
      footprint="AI_Glasses_V2:Crystal_SMD_3225",
      desc="Main clock — 24 MHz, 10 ppm; load per Rockchip reference layout.",
      pins=[("XIN", "SOC_XIN"), ("XOUT", "SOC_XOUT"), ("GND", "GND")]),
    C(ref="U5", bom_id="C006", value="MX25U6432F", board=COMPUTE, assembly="DNP", pri="P1",
      gate="Boot flow decides whether production needs it",
      footprint="AI_Glasses_V2:USON-8",
      desc="Backup boot flash — 64 Mbit 1.8 V serial NOR on FSPI. Reserved for "
           "recovery / factory test / alt-boot; not populated on first EVT.",
      pins=[("VCC", "VCCIO_1V8"), ("GND", "GND"), ("FSPI_BUS", "FSPI_BUS")]),
    C(ref="U6", bom_id="C007", value="TPS61088", board=COMPUTE, assembly="HOLD",
      gate="G06/G09 (measured RK3576 boot+AI peak, soft-start, droop, thermal)",
      footprint="AI_Glasses_V2:VQFN-22_4.5x3.5",
      desc="Main SoC 5 V boost — 1S -> SOC_5V for the compute island. High-current "
           "sync boost; EN from nRF54L15, PG back to nRF. Candidate/HOLD until peak measured.",
      note="Only the RK3576 island gets a boost (Phase-3 rule). Verify RK806 input range "
           "before committing the boost; if RK806 takes 1S directly, drop it.",
      pins=[("VIN", "SOC_IN"), ("SW", "SOC_BOOST_SW"), ("GND", "GND"),
            ("EN", "SOC_PWR_EN"), ("PG", "SOC_5V_PGOOD"),
            ("VOUT", "SOC_5V")]),
    C(ref="L1", bom_id="C008", value="Coilcraft XGL4020-102MEC 1.0uH", board=COMPUTE, assembly="HOLD",
      gate="G06/G13 (Isat/DCR/thermal pass for 5.1V 3A continuous / 4A peak boost)",
      footprint="AI_Glasses_V2:VERIFY_L_4x4x2_XGL4020",
      desc="Boost inductor for TPS61088 — Coilcraft XGL4020-102MEC candidate, 1.0uH, "
           "4.0x4.0x2.0mm, low DCR, high-current shielded inductor. Keep SW copper small; "
           "do not route DDR/MIPI/audio/RF under the inductor.",
      pins=[("A", "SOC_IN"), ("B", "SOC_BOOST_SW")]),
    C(ref="U11", bom_id="C015", value="FCU760KAAMD", board=COMPUTE, assembly="HOLD",
      gate="G05 (Quectel HW Design + RK3576 BSP driver/firmware/enum) + official LCC land pattern",
      footprint="AI_Glasses_V2:VERIFY_LCC_13x12.2_Quectel",
      desc="Wi-Fi 6 + BT 5.4 module — Quectel FCU760K, LCC 13.0x12.2x2.0mm. USB2 to RK3576 host; "
           "PCM for BT audio; VBAT 3.0-3.6V (typ 3.3V), max TX 353 mA. On-demand, load-switched off.",
      note="CONFIRMED on Radxa CM4 V1.20 p20; interface = USB2 (NOT SDIO). Single-antenna SKU "
           "FCU760KAAMD shares Wi-Fi/BT on ANT_WIFI_BT. Optional ANT_BT is kept only as a DNP "
           "test/matching node until Quectel FAE confirms its use. Exact LCC pinout/land pattern "
           "+ Linux driver/firmware stay HOLD pending Quectel Hardware Design.",
      pins=[("VBAT", "WIFI_VBAT_3V3"), ("GND", "GND"),
            ("USB_DP", "WIFI_USB_DP"), ("USB_DM", "WIFI_USB_DM"),
            ("CHIP_EN", "WIFI_CHIP_EN"),
            ("PCM_CLK", "WIFI_PCM_CLK"), ("PCM_SYNC", "WIFI_PCM_SYNC"),
            ("PCM_IN", "WIFI_PCM_DOUT"), ("PCM_OUT", "WIFI_PCM_DIN"),
            ("WAKE", "WIFI_WAKE_L"), ("ANT_WIFI_BT", "WIFI_ANT"), ("ANT_BT_DNP", "BLE_ANT")]),
    C(ref="U12", bom_id="C016", value="TPS62825", board=COMPUTE, assembly="Fit",
      gate="G05/G06 (inductor/caps per module 353mA TX peak + ripple)",
      footprint="AI_Glasses_V2:QFN_1.5x1.5",
      desc="Wi-Fi dedicated 3.3 V buck — feeds FCU760K VBAT; >=500 mA capability for the 353 mA "
           "TX peak (pack note). EN by AON MCU. Avoids routing the radio through 5 V (Phase-3 rule).",
      pins=[("VIN", "WIFI_IN"), ("SW", "WIFI_BUCK_SW"), ("GND", "GND"),
            ("EN", "WIFI_BUCK_EN"), ("VOUT", "WIFI_3V3")]),
    C(ref="L2", bom_id="C016c", value="Wi-Fi buck inductor (TBD)", board=COMPUTE, assembly="Fit",
      gate="Per TPS62825 peak+ripple",
      footprint="AI_Glasses_V2:VERIFY_L_2x2",
      desc="Wi-Fi buck inductor — SW->3V3, value per TPS62825 design.",
      pins=[("A", "WIFI_BUCK_SW"), ("B", "WIFI_3V3")]),
    C(ref="U13", bom_id="C016b", value="TPS22917DBVR", board=COMPUTE, assembly="Fit",
      gate="G05 (turn-on sequence w/ module)",
      footprint="Package_TO_SOT_SMD:SOT-23-5",
      desc="Wi-Fi load switch — gates WIFI_3V3 -> FCU760K VBAT with QOD + reverse block. EN by AON MCU.",
      pins=[("VIN", "WIFI_3V3"), ("VOUT", "WIFI_VBAT_3V3"), ("EN", "WIFI_LS_EN"),
            ("GND", "GND")]),
    C(ref="C1", bom_id="C015-C", value="47uF 6.3V X5R", board=COMPUTE, assembly="Fit",
      gate="Local bulk per Quectel HW Design",
      footprint="AI_Glasses_V2:C_0805",
      desc="FCU760K VBAT bulk storage — 47 uF local reservoir next to the module (pack: 47uF + "
           "1uF + 100nF). Rides the 353 mA TX burst.",
      pins=[("A", "WIFI_VBAT_3V3"), ("B", "GND")]),
    C(ref="RT3", bom_id="C043", value="10k NTC B=3435", board=COMPUTE, assembly="Fit",
      gate="Probe position per thermal sim",
      footprint="AI_Glasses_V2:R_0402",
      desc="SoC/enclosure temp monitor — 10k NTC on SoC heat-spreader + skin side. "
           "Wearable must watch both die and skin temp.",
      pins=[("A", "SOC_NTC"), ("B", "GND")]),
    C(ref="U35", bom_id="C010b", value="BQ25895", board=COMPUTE, assembly="HOLD",
      gate="Charger/power-path config, TS thresholds, 1S2P charge profile, thermal/current validation",
      footprint="AI_Glasses_V2:VERIFY_WQFN_24_BQ25895",
      desc="Primary 1S charger + Power Path — protected 5V input to SYS/VSYS and 1S2P pack. "
           "Use with pack-internal PCM, BQ25895 TS temperature protection, input current limit, "
           "and software charge-profile control. First bring-up must prove low-battery boost droop "
           "and charge/boost coexistence.",
      note="This is the board-level charger/power-path block for EVT V2.0. nPM1300 remains the "
           "AON buck/fuel-gauge/low-power PMIC; do not also populate board-level BQ2970 protection "
           "when the pack includes PCM.",
      pins=[("VBUS", "USB_5V"), ("SYS", "VSYS"), ("BAT", "NPM_VBAT"), ("GND", "GND"),
            ("SCL", "I2C_AON_SCL"), ("SDA", "I2C_AON_SDA"),
            ("TS", "NTC_R"), ("INT_L", "CHG_INT_L"), ("CE_L", "CHG_CE_L"), ("PG_L", "CHG_PG_L")]),
    C(ref="U36", bom_id="C034b", value="5V input eFuse/OVP (MPN TBD)", board=COMPUTE, assembly="HOLD",
      gate="Select MPN for pogo/USB VBUS surge, reverse, OVP, current limit and thermal fault",
      footprint="AI_Glasses_V2:VERIFY_EFUSE_OVP",
      desc="5V input protection between magnetic pogo/EVT USB-C and charger input. Required: "
           "VBUS TVS/OVP/eFuse/current limit, fault indication and layout close to the connector path.",
      pins=[("IN", "VBUS_RAW"), ("OUT", "USB_5V"), ("GND", "GND"), ("FLT_L", "VBUS_FAULT_L")]),
]

# ── C009–C012, C010, C017–C018: L-Temple AON/Power Board ─────────────────────
AON_BOARD = [
    C(ref="U7", bom_id="C009", value="nRF54L15-QFN48", board=AON, assembly="Fit",
      gate="EVT-frozen (RF layout/SDK/package to freeze early)",
      footprint="AI_Glasses_V2:QFN-48_6x6",
      desc="Low-power BLE MCU — ALWAYS ON. Owns the system state machine; controls "
           "RK3576/camera/Wi-Fi/audio power ENs; talks IMU/buttons/gauge; UART to RK3576, "
           "SPI to NDP120. Turns RK3576 from an always-on host into a demand accelerator.",
      note="nRF54L15 (not nRF52/53): 1.5MB NVM / 256KB RAM headroom, long-life platform, "
           "later WLCSP shrink. QFN48 for the debuggable EVT board. EVT V2.0 does not fit a "
           "separate nRF BLE antenna; phone/BLE data path is assigned to FCU760K shared RF unless "
           "RF coexistence testing reopens the DNP ANT_BT option.",
      pins=[
          ("VDD_1V8", "AON_1V8"), ("VDD_3V3", "AON_3V3"), ("GND", "GND"),
          ("ANT_DNP", "NC"),
          # power control (outputs)
          ("SOC_PWR_EN", "SOC_PWR_EN"), ("SOC_5V_PGOOD", "SOC_5V_PGOOD"),
          ("PMIC_PWRON", "PMIC_PWRON"),
          ("CAM_1V1_EN", "CAM_1V1_EN"), ("CAM_1V8_EN", "CAM_1V8_EN"), ("CAM_2V9_EN", "CAM_2V9_EN"),
          ("WIFI_BUCK_EN", "WIFI_BUCK_EN"), ("WIFI_LS_EN", "WIFI_LS_EN"), ("WIFI_CHIP_EN", "WIFI_CHIP_EN"),
          ("AUDIO_LS_EN", "AUDIO_LS_EN"), ("AMP_SD", "AUDIO_AMP_SD"),
          # SoC handshake (inputs)
          ("SOC_SHDN_REQ", "SOC_SHUTDOWN_REQ"), ("SOC_SAFE_OFF", "SOC_SAFE_TO_OFF"),
          ("SOC_ALIVE", "SOC_ALIVE"), ("SOC_FAULT", "SOC_FAULT"),
          ("AON_UART_TX", "AON_UART_TX"), ("AON_UART_RX", "AON_UART_RX"),
          # AON buses
          ("I2C_SCL", "I2C_AON_SCL"), ("I2C_SDA", "I2C_AON_SDA"),
          ("PMIC_INT_L", "PMIC_INT_L"), ("PMIC_SHPHLD", "PMIC_SHPHLD"),
          ("CHG_INT_L", "CHG_INT_L"), ("CHG_CE_L", "CHG_CE_L"),
          ("CHG_PG_L", "CHG_PG_L"), ("VBUS_FAULT_L", "VBUS_FAULT_L"),
          ("IMU_INT1", "IMU_INT1"), ("IMU_INT2", "IMU_INT2"),
          # NDP120 link
          ("DSP_SCK", "DSP_SPI_SCK"), ("DSP_MOSI", "DSP_SPI_MOSI"), ("DSP_MISO", "DSP_SPI_MISO"),
          ("DSP_CS_n", "DSP_SPI_CS_n"), ("DSP_WAKE", "DSP_WAKE"), ("DSP_READY", "DSP_READY"),
          ("DSP_FAULT", "DSP_FAULT"), ("DSP_RST_n", "DSP_RESET_L"),
          # haptics + debug
          ("HAPTIC_EN", "HAPTIC_EN"), ("SWDIO", "NRF_SWDIO"), ("SWDCLK", "NRF_SWDCLK"),
      ]),
    C(ref="U8", bom_id="C010", value="nPM1300", board=AON, assembly="HOLD",
      gate="G08 (AON <=25/50mW) — configure via nPM PowerUP on EK before board",
      footprint="AI_Glasses_V2:QFN_5x5",
      desc="AON PMIC / low-power rail manager — fuel-gauge support, dual Buck, LDO/Load-Switch "
           "and Ship/Hibernate for the small AON world ONLY; NOT the RK3576 peak path.",
      note="BQ25895 is the primary charger + power-path block in EVT V2.0. nPM1300 stays in the "
           "AON domain for low-Iq rails/gauge/support functions and must be configured for the "
           "supplier-built 1S2P pack, not a single 300mAh cell.",
      pins=[
          ("VBAT", "NPM_VBAT"), ("VBUS", "USB_5V"), ("VSYS", "VSYS"), ("GND", "GND"),
          ("BUCK1", "AON_1V8"), ("BUCK2", "AON_3V3"),
          ("LSW2", "AON_LSW2"),
          ("NTC_R", "NTC_R"), ("NTC_L", "NTC_L"),
          ("I2C_SCL", "I2C_AON_SCL"), ("I2C_SDA", "I2C_AON_SDA"),
          ("INT", "PMIC_INT_L"), ("SHPHLD", "PMIC_SHPHLD"),
      ]),
    C(ref="U9", bom_id="C011", value="NDP120", board=AON, assembly="HOLD",
      gate="Full datasheet + dev kit + measured listening power + NDA/licensing",
      footprint="AI_Glasses_V2:VERIFY_QFN_5x5",
      desc="Always-on Audio DSP — ultra-low-power wake-word + audio front-end; wakes the MCU "
           "over GPIO. Moves voice listening off RK3576. Keep bypass + DNP capability.",
      note="HOLD until hardware datasheet, rails/sequence, PDM/I2S detail, firmware/model "
           "tools, wake-word licensing, real listening power, MOQ/lead all in hand.",
      pins=[
          ("VDD_1V8", "AON_1V8"), ("VDD_3V3", "AON_3V3"), ("GND", "GND"),
          ("PDM_CLK", "PDM_WAKE_CLK"), ("PDM_DATA", "PDM_WAKE_DATA"),
          ("HOST_SCK", "DSP_SPI_SCK"), ("HOST_MOSI", "DSP_SPI_MOSI"),
          ("HOST_MISO", "DSP_SPI_MISO"), ("HOST_CS_n", "DSP_SPI_CS_n"),
          ("WAKE", "DSP_WAKE"), ("READY", "DSP_READY"), ("FAULT", "DSP_FAULT"),
          ("RESET_n", "DSP_RESET_L"),
      ]),
    C(ref="U10", bom_id="C012", value="BMI270", board=AON, assembly="Fit",
      gate="Evaluate false-trigger under real frame vibration",
      footprint="Package_LGA:LGA-14_2.5x3mm_P0.5mm",
      desc="6-axis IMU — low-power motion detect; motion-interrupt wakes the MCU. "
           "Cycling/running state ID for wearables.",
      pins=[("VDD", "AON_1V8"), ("VDDIO", "AON_1V8"), ("GND", "GND"),
            ("SCL", "I2C_AON_SCL"), ("SDA", "I2C_AON_SDA"),
            ("INT1", "IMU_INT1"), ("INT2", "IMU_INT2")]),
    C(ref="J6", bom_id="C018", value="FCU760K ANT_BT DNP test pad", board=REAR, assembly="DNP",
      gate="Only populate if Quectel FAE + coexistence test requires the second RF port",
      footprint="AI_Glasses_V2:VERIFY_ANT",
      desc="Optional second RF feed for FCU760K ANT_BT — DNP/test only. EVT V2.0 does not fit a "
           "separate BLE antenna; Wi-Fi/BLE share the main dual-band FPC antenna on WIFI_ANT.",
      pins=[("ANT", "BLE_ANT"), ("GND", "GND")]),
    C(ref="J7", bom_id="C017", value="Taoglas FXP840.07.0055B", board=REAR, assembly="HOLD",
      gate="G14 (worn-state tune + antenna keep-out in full shell with battery/speaker)",
      footprint="AI_Glasses_V2:VERIFY_FPC_ANT_14x5",
      desc="Shared Wi-Fi/BLE dual-band FPC antenna candidate — Taoglas FXP840.07.0055B, "
           "about 14x5x0.1mm with 55mm coax/MHF-style termination. Place at temple end or "
           "non-metal window; keep away from battery, speaker magnet, pogo magnet, shields and copper.",
      pins=[("ANT", "WIFI_ANT"), ("GND", "GND")]),
]

# ── C013–C014, C019–C023: Front Sensor Board ─────────────────────────────────
FRONT_BOARD = [
    C(ref="U14", bom_id="C019", value="Sony IMX415-AAQR-C custom module", board=FRONT, assembly="HOLD",
      gate="G10 (module lens/FOV/FPC pinout/lane/supply/timing from vendor)",
      footprint="AI_Glasses_V2:VERIFY_CAM_MODULE",
      desc="Main camera module target — Sony IMX415-AAQR-C, 8.46 MP, 3840x2160 30fps baseline, "
           "RAW10 first, 4-lane MIPI CSI-2. Custom small sensor+lens rigid island + FPC "
           "(NOT a dev module). Sensor PCB target <=15x15mm, total camera Z target <=9.5mm. "
           "Sensor rails (Sony datasheet): "
           "AVDD 2.9V 128/156mA, IOVDD 1.8V 3mA, DVDD 1.1V 187/250mA (~0.58W typ, ~0.77W max).",
      note="IMX415 mechanical stack is still TBD: lens MPN, IR-cut, PCB, glue, FPC exit, mount, "
           "TTL/BFL/CRA/MTF/distortion/relative illumination and module STEP must come from the "
           "module vendor. Use orange TBD mechanical envelope; not released for tooling.",
      pins=[
          ("DVDD_1V1", "CAM_1V1_S"), ("IOVDD_1V8", "CAM_1V8_S"), ("AVDD_2V9", "CAM_2V9_S"), ("GND", "GND"),
          ("CSI_CLK_P", "CSI_CLK_P"), ("CSI_CLK_N", "CSI_CLK_N"),
          ("CSI_D0_P", "CSI_D0_P"), ("CSI_D0_N", "CSI_D0_N"),
          ("CSI_D1_P", "CSI_D1_P"), ("CSI_D1_N", "CSI_D1_N"),
          ("CSI_D2_P", "CSI_D2_P"), ("CSI_D2_N", "CSI_D2_N"),
          ("CSI_D3_P", "CSI_D3_P"), ("CSI_D3_N", "CSI_D3_N"),
          ("SCL", "CAM_I2C_SCL"), ("SDA", "CAM_I2C_SDA"),
          ("XCLR_L", "CAM_RST_L"), ("PWDN_L", "CAM_PWDN_L"), ("INCK", "CAM_MCLK"),
          ("MODULE_ID", "CAM_MODULE_ID"),
      ]),
    C(ref="U15", bom_id="C020", value="TPS62840", board=FRONT, assembly="Fit",
      gate="Output current/noise per final module (DVDD ~250mA max + margin)",
      footprint="AI_Glasses_V2:VERIFY_WSON",
      desc="Camera DVDD 1.1 V buck — ultra-low-Iq (~60 nA) buck for the sensor core (DVDD 187/"
           "250mA), up to ~750 mA. EN by AON MCU / SoC. True power-down when camera off.",
      pins=[("VIN", "VSYS"), ("SW", "CAM_1V1_SW"), ("GND", "GND"),
            ("EN", "CAM_1V1_EN"), ("VOUT", "CAM_1V1")]),
    C(ref="L3", bom_id="C020b", value="Cam 1V1 buck inductor (TBD)", board=FRONT, assembly="Fit",
      gate="Per TPS62840 design",
      footprint="AI_Glasses_V2:VERIFY_L_1.6x0.8",
      desc="Camera 1.1 V buck inductor — SW->1V1.",
      pins=[("A", "CAM_1V1_SW"), ("B", "CAM_1V1")]),
    C(ref="U16", bom_id="C021", value="TLV75529PDRVR", board=FRONT, assembly="Fit",
      gate="Verify vs IMX415 AVDD peak (156mA) + PSRR",
      footprint="AI_Glasses_V2:WSON-6_2x2",
      desc="Camera AVDD 2.9 V LDO — 500 mA low-noise analog supply (AVDD 128/156mA). Low-noise "
           "LDO, NOT a series resistor off 3.3V (pack §23).",
      pins=[("VIN", "VSYS"), ("EN", "CAM_2V9_EN"), ("GND", "GND"), ("VOUT", "CAM_2V9")]),
    C(ref="U17", bom_id="C022", value="TPS22917DBVR", board=FRONT, assembly="Fit",
      gate="Check reverse block, ramp, QOD, logic level",
      footprint="Package_TO_SOT_SMD:SOT-23-5",
      desc="Camera IOVDD 1.8 V load switch / isolation — low-leak switch from AON_1V8 for camera "
           "I/O (IOVDD ~3mA); Quick-Output-Discharge kills reverse feed when camera off (§24).",
      pins=[("VIN", "AON_1V8"), ("VOUT", "CAM_1V8_SW"), ("EN", "CAM_1V8_EN"), ("GND", "GND")]),
    C(ref="U18", bom_id="C023a", value="TPD4E05U06", board=FRONT, assembly="Fit",
      gate="Low-cap array near FPC entry",
      footprint="AI_Glasses_V2:USON",
      desc="MIPI/FPC ESD (clk + D0) — ultra-low-cap 4-ch ESD at the FPC entry.",
      pins=[("CLK_P", "CSI_CLK_P"), ("CLK_N", "CSI_CLK_N"),
            ("D0_P", "CSI_D0_P"), ("D0_N", "CSI_D0_N"), ("GND", "GND")]),
    C(ref="U19", bom_id="C023b", value="TPD4E05U06", board=FRONT, assembly="Fit",
      gate="Low-cap array near FPC entry",
      footprint="AI_Glasses_V2:USON",
      desc="MIPI/FPC ESD (D1 + control) — ultra-low-cap ESD for the second lane pair and critical control.",
      pins=[("D1_P", "CSI_D1_P"), ("D1_N", "CSI_D1_N"),
            ("RST", "CAM_RST_L"), ("MCLK", "CAM_MCLK"), ("GND", "GND")]),
    C(ref="U34", bom_id="C023c", value="TPD4E05U06", board=FRONT, assembly="Fit",
      gate="Low-cap array near FPC entry for 4-lane CSI",
      footprint="AI_Glasses_V2:USON",
      desc="MIPI/FPC ESD (D2 + D3) — adds the two lane pairs required by the 4-lane IMX415 EVT target.",
      pins=[("D2_P", "CSI_D2_P"), ("D2_N", "CSI_D2_N"),
            ("D3_P", "CSI_D3_P"), ("D3_N", "CSI_D3_N"), ("GND", "GND")]),
    C(ref="MK1", bom_id="C013a", value="T5837 (wake mic)", board=FRONT, assembly="Fit",
      gate="G11 (mic coords/ports/wind/wake + AEC/beamforming)",
      footprint="AI_Glasses_V2:LGA-5_3.5x2.65",
      desc="PDM wake mic — dedicated always-on wake channel into NDP120 (AON audio domain). "
           "Deep Off must capture without RK3576.",
      pins=[("VDD", "AON_3V3"), ("GND", "GND"),
            ("CLK", "PDM_WAKE_CLK"), ("DATA", "PDM_WAKE_DATA")]),
    C(ref="MK2", bom_id="C013b", value="T5837 (array mic 1)", board=FRONT, assembly="Fit",
      gate="G11",
      footprint="AI_Glasses_V2:LGA-5_3.5x2.65",
      desc="PDM array mic 1 — into RK3576 PDM for beamforming during vision/voice tasks.",
      pins=[("VDD", "AON_3V3"), ("GND", "GND"),
            ("CLK", "PDM_ARRAY_CLK"), ("DATA", "PDM_ARRAY_D0")]),
    C(ref="MK3", bom_id="C013c", value="T5837 (array mic 2)", board=FRONT, assembly="Fit",
      gate="G11",
      footprint="AI_Glasses_V2:LGA-5_3.5x2.65",
      desc="PDM array mic 2 — second array channel (L/R stereo on shared PDM clock).",
      pins=[("VDD", "AON_3V3"), ("GND", "GND"),
            ("CLK", "PDM_ARRAY_CLK"), ("DATA", "PDM_ARRAY_D1")]),
    C(ref="MK4", bom_id="C014", value="T5837 (4th mic)", board=FRONT, assembly="DNP", pri="P1",
      gate="G11 (populate only if array sim/proto needs it)",
      footprint="AI_Glasses_V2:LGA-5_3.5x2.65",
      desc="4th array mic — footprint only; on the switchable AON_LSW2 rail (nPM1300 load switch, "
           "§14 'spare mic') so it can be fully powered down. Not populated until array/wind tests.",
      pins=[("VDD", "AON_LSW2"), ("GND", "GND"),
            ("CLK", "PDM_ARRAY_CLK"), ("DATA", "PDM_ARRAY_D1")]),
]

# ── C024–C028: Audio + haptics (R/L temple rears) ────────────────────────────
AUDIO_BOARD = [
    C(ref="U20", bom_id="C024", value="MAX98360A", board=COMPUTE, assembly="Fit",
      gate="Verify Z/cavity/EMI/peak power",
      footprint="AI_Glasses_V2:VERIFY_WLP_QFN",
      desc="Digital Class-D amp — I2S in, mono, low-power shutdown. Direct digital audio chain, "
           "no analog codec. Fully power-downable via load switch.",
      pins=[("VDD", "AUDIO_PWR"), ("GND", "GND"),
            ("BCLK", "I2S_BCLK"), ("LRCLK", "I2S_LRCLK"), ("DIN", "I2S_DIN"),
            ("SD_MODE", "AUDIO_AMP_SD"),
            ("OUT_P", "SPK_P"), ("OUT_N", "SPK_N")]),
    C(ref="U21", bom_id="C024b", value="TPS22917DBVR", board=COMPUTE, assembly="Fit",
      gate="Amp must be fully power-downable (V1 lesson)",
      footprint="Package_TO_SOT_SMD:SOT-23-5",
      desc="Audio load switch — gates AUDIO_PWR to the amp; EN by AON MCU / SoC.",
      pins=[("VIN", "AUDIO_IN"), ("VOUT", "AUDIO_PWR"), ("EN", "AUDIO_LS_EN"), ("GND", "GND")]),
    C(ref="LS1", bom_id="C025", value="CUI CMS-15113-078SP-67", board=REAR, assembly="HOLD",
      gate="Acoustic EVT: 0.3-0.5cc cavity, port/foam seal, magnet-to-antenna clearance, leak test",
      footprint="AI_Glasses_V2:VERIFY_SPK_15x11x3",
      desc="Main speaker EVT baseline — CUI CMS-15113-078SP-67, 15x11x3mm, 8 ohm, "
           "0.7W rated / 1W max, about 91dB sensitivity, front IP67. Drive as mono differential "
           "speaker from the digital Class-D amp; limit first firmware to 0.5-0.7W RMS.",
      pins=[("P", "SPK_P"), ("N", "SPK_N")]),
    C(ref="LS2", bom_id="C026", value="2nd speaker pad", board=REAR, assembly="DNP", pri="P1",
      gate="Decide dual-speaker at EVT-B",
      footprint="AI_Glasses_V2:VERIFY_SPK",
      desc="Second speaker land — reserved for productization; not populated first version.",
      pins=[("P", "NC"), ("N", "NC")]),
    C(ref="U22", bom_id="C027", value="DRV2605L", board=AON, assembly="DNP", pri="P1",
      gate="Vibration P1 — may DNP on first board (IMU/mic coupling)",
      footprint="Package_SO:MSOP-10_3x3mm_P0.5mm",
      desc="Haptic driver — LRA/ERM driver, I2C, waveform library. Silent safety reminder path.",
      pins=[("VDD", "VSYS"), ("GND", "GND"),
            ("SCL", "I2C_AON_SCL"), ("SDA", "I2C_AON_SDA"), ("EN", "HAPTIC_EN"),
            ("OUT_P", "HAPTIC_P"), ("OUT_N", "HAPTIC_N")]),
    C(ref="M1", bom_id="C028", value="LRA/ERM motor", board=REAR, assembly="DNP", pri="P1",
      gate="Vibration P1",
      footprint="AI_Glasses_V2:VERIFY_LRA",
      desc="LRA/ERM motor — short haptic alerts; can be replaced by phone vibration first version.",
      pins=[("P", "HAPTIC_P"), ("N", "HAPTIC_N")]),
]

# ── C029–C033: Battery pack, supplier PCM + temperature ──────────────────────
BATTERY = [
    C(ref="BT1", bom_id="C029", value="LP451165 300mAh (R)", board=REAR, assembly="HOLD",
      gate="G07 (full datasheet, >=2C, IR, cycles, cert)",
      footprint="AI_Glasses_V2:VERIFY_CELL_4.5x11x65",
      desc="Right-side element of the supplier-built 1S2P pack — LP451165 nominal cell candidate, "
           "one per temple. Mechanical control envelope per side is 70x12.8x5.6mm including tabs, "
           "PCM/insulation allowance, foam and swelling space.",
      note="Do not parallel two independent protected cells on the PCB. G07 must close with one "
           "pack supplier building a matched 1S2P pack, common PCM, branch fusing/fusible links, "
           "two NTCs, official 2D/STEP, tab/cable exit, UN38.3/MSDS/IEC62133-equivalent data.",
      pins=[("+", "BATR_P"), ("-", "CELL_NEG")]),
    C(ref="BT2", bom_id="C030", value="LP451165 300mAh (L)", board=REAR, assembly="HOLD",
      gate="G07",
      footprint="AI_Glasses_V2:VERIFY_CELL_70x12.8x5.6_maxenv",
      desc="Left-side element of the supplier-built 1S2P pack — same batch/capacity/IR-matched "
           "to the right side. Use the same 70x12.8x5.6mm mechanical control envelope and pack "
           "supplier cable/tab/PCM drawing.",
      pins=[("+", "BATL_P"), ("-", "CELL_NEG")]),
    C(ref="F1", bom_id="C031a", value="PTC/fuse (R branch)", board=REAR, assembly="TBD",
      gate="Rating from peak-current calc (> branch peak, < FPC rating)",
      footprint="AI_Glasses_V2:VERIFY_FUSE",
      desc="Right branch protection — resettable PTC / fusible link in the right cell branch. "
           "Limits a single-cell / FPC short (§7).",
      pins=[("A", "BATR_P"), ("B", "BATR_F")]),
    C(ref="F2", bom_id="C031b", value="PTC/fuse (L branch)", board=REAR, assembly="TBD",
      gate="Rating from peak-current calc",
      footprint="AI_Glasses_V2:VERIFY_FUSE",
      desc="Left branch protection — resettable PTC / fusible link in the left cell branch.",
      pins=[("A", "BATL_P"), ("B", "BATL_F")]),
    # per-branch current-sense shunts (I_CELL_R / I_CELL_L, for current-share check)
    C(ref="RS2", bom_id="C044-RCL", value="10 mohm 1%", board=REAR, assembly="Fit",
      gate="Branch current-share (§7/§29)", footprint="AI_Glasses_V2:R_0805_shunt",
      desc="Left branch shunt — BATL_F -> BAT_P; I_CELL_L for current-share monitoring.",
      pins=[("A", "BATL_F"), ("B", "BAT_P")]),
    C(ref="RS3", bom_id="C044-RCR", value="10 mohm 1%", board=REAR, assembly="Fit",
      gate="Branch current-share (§7/§29)", footprint="AI_Glasses_V2:R_0805_shunt",
      desc="Right branch shunt — BATR_F -> BAT_P; I_CELL_R for current-share monitoring.",
      pins=[("A", "BATR_F"), ("B", "BAT_P")]),
    C(ref="RS1", bom_id="C044-RBAT", value="10 mohm 1% 1W", board=AON, assembly="Fit",
      gate="I_BAT_TOTAL; the one production-kept sense path", footprint="AI_Glasses_V2:R_1206_shunt",
      desc="Pack total shunt — BAT_P -> nPM1300 VBAT. Whole-device current (charge + discharge).",
      pins=[("A", "BAT_P"), ("B", "NPM_VBAT")]),
    C(ref="PCM1", bom_id="C032", value="Supplier 1S2P pack PCM + protection FETs", board=REAR, assembly="HOLD",
      gate="Pack supplier drawing: OVP/UVP/OCP/SCP thresholds, FET Rds(on), current rating, NTC placement, UN38.3/MSDS/IEC62133",
      footprint="AI_Glasses_V2:PACK_INTERNAL_NO_BOARD_FOOTPRINT",
      desc="Pack-internal protection baseline — the supplier builds both matched LP451165 cells "
           "as one complete 1S2P pack with common PCM, branch fusing/fusible links, over-charge, "
           "over-discharge, over-current, short-circuit and FET cutoff. The main PCB does NOT "
           "populate a second BQ2970 + dual-MOSFET protection stage.",
      note="Board-level battery protection is intentionally limited to BQ25895 charger/power-path, "
           "5V input eFuse/OVP, software low-battery shutdown and test access. Battery exits via "
           "fixed harness/direct solder pads near the power board; no battery wiring crosses a hinge.",
      pins=[("PACK_PLUS", "BAT_P"), ("PACK_MINUS", "GND"), ("CELL_MINUS", "CELL_NEG"),
            ("NTC1", "NTC_R"), ("NTC2_OR_ID", "NTC_L")]),
    C(ref="RT1", bom_id="C033a", value="10k NTC B=3435 1% (R cell)", board=REAR, assembly="Fit",
      gate="NTC curve/package/placement matched to pack supplier + BQ25895/nPM1300 config",
      footprint="AI_Glasses_V2:R_0402",
      desc="Right cell temperature — 10k NTC at 25C, B=3435K, 1% or better, bonded to the cell "
           "large face near center, not to the PCM. Route with ESD/filtering and battery-sense ground.",
      pins=[("A", "NTC_R"), ("B", "GND")]),
    C(ref="RT2", bom_id="C033b", value="10k NTC B=3435 1% (L cell)", board=REAR, assembly="Fit",
      gate="NTC curve/package/placement matched to pack supplier + ADC/config",
      footprint="AI_Glasses_V2:R_0402",
      desc="Left cell temperature — second per-cell NTC for software/safety monitoring; firmware "
           "must stop charging if either cell is out of the supplier temperature window.",
      pins=[("A", "NTC_L"), ("B", "GND")]),
    C(ref="TP2", bom_id="C033-TP", value="Battery test points", board=REAR, assembly="Fit",
      gate="Cell/pack voltage + NTC probe access (§21)",
      footprint="AI_Glasses_V2:TestPad_Set",
      desc="Battery Kelvin test points — Cell-L+, Cell-R+, Pack+, Cell-neg, both NTCs for pairing "
           "/ current-share / temperature verification.",
      pins=[("CELL_L", "BATL_P"), ("CELL_R", "BATR_P"), ("PACK_P", "BAT_P"),
            ("CELL_NEG", "CELL_NEG"), ("NTC_L", "NTC_L"), ("NTC_R", "NTC_R")]),
]

# ── C034–C042: Charge/data interface, USB2, debug, buttons ───────────────────
INTERFACE = [
    C(ref="J1", bom_id="C034", value="CCP P2578MP01-06C180HT", board=REAR, assembly="HOLD",
      gate="USB2 eye/contact validation, current/fault/ESD, mating STEP, corrosion/cycle life",
      footprint="AI_Glasses_V2:VERIFY_POGO_6P_1.8MM",
      desc="6-pin magnetic pogo EVT candidate — 1.8mm pitch, working height about 1.0mm, "
           "target outline about 10x3mm. Pins carry 5V charge input, USB2 D+/D-, and dual GND/VBUS "
           "contacts for lower resistance. Add VBUS TVS/eFuse/OVP, D+/D- low-cap ESD, USB CMC DNP, "
           "VBUS insert detect and MaskROM/UART fallback pads.",
      pins=[("GND1", "GND"), ("USB_DN", "USB2_DM"), ("USB_DP", "USB2_DP"),
            ("GND2", "GND"), ("VBUS1", "VBUS_RAW"), ("VBUS2", "VBUS_RAW")]),
    C(ref="J2", bom_id="C035", value="USB-C 16p USB2-only", board=EVT, assembly="Fit",
      gate="Connector height + shell opening co-freeze",
      footprint="AI_Glasses_V2:USB_C_16P_MidMount",
      desc="EVT USB-C — 5 V sink + USB2 OTG (no USB3/DP). For MaskROM/ADB/firmware/lab supply.",
      pins=[("VBUS", "VBUS_RAW"), ("GND", "GND"),
            ("DP", "USB2_DP"), ("DM", "USB2_DM"), ("CC1", "USB_CC1"), ("CC2", "USB_CC2")]),
    C(ref="U24", bom_id="C036", value="TPD2E001", board=EVT, assembly="Fit",
      gate="Keep ~90 ohm diff + continuous ref gnd",
      footprint="Package_TO_SOT_SMD:SOT-23-3",
      desc="USB2 ESD — low-cap ESD on D+/D- near the connector.",
      pins=[("DP", "USB2_DP"), ("DM", "USB2_DM"), ("GND", "GND")]),
    C(ref="R1", bom_id="C037a", value="5.1k 1%", board=EVT, assembly="Fit",
      gate="USB-C spec",
      footprint="AI_Glasses_V2:R_0402",
      desc="USB-C CC1 Rd — 5.1k 1% sink pulldown. LOCK value + 1% (V1 audit rule).",
      pins=[("A", "USB_CC1"), ("B", "GND")]),
    C(ref="R2", bom_id="C037b", value="5.1k 1%", board=EVT, assembly="Fit",
      gate="USB-C spec",
      footprint="AI_Glasses_V2:R_0402",
      desc="USB-C CC2 Rd — 5.1k 1% sink pulldown.",
      pins=[("A", "USB_CC2"), ("B", "GND")]),
    C(ref="J3", bom_id="C038", value="Hirose FH26W-33S-0.3SHW(97)", board=FRONT, assembly="HOLD",
      gate="G10/G12 (camera module vendor signs 33-pin pinout, contact orientation, impedance)",
      footprint="AI_Glasses_V2:VERIFY_FH26W_33S_0.3SHW",
      desc="33-pin camera FPC connector — Hirose FH26W-33S-0.3SHW(97), 0.3mm pitch, "
           "bottom contact, horizontal, about 1.0mm height, for 0.2mm FPC. Carries IMX415 "
           "4-lane CSI, rails, I2C, reset/powerdown and module ID. Assembly/service connector only, "
           "not a user-cycle connector.",
      note="Pinout below follows the current project proposal and must be signed by the camera "
           "module vendor. Hinge electrical interconnect is out of scope for Chip-down EVT V2.0.",
      pins=[
          ("1_GND", "GND"), ("2_DVDD", "CAM_1V1_S"), ("3_GND", "GND"),
          ("4_AVDD", "CAM_2V9_S"), ("5_GND", "GND"), ("6_IOVDD", "CAM_1V8_S"),
          ("7_GND", "GND"), ("8_MCLK", "CAM_MCLK"), ("9_GND", "GND"),
          ("10_I2C_SCL", "CAM_I2C_SCL"), ("11_I2C_SDA", "CAM_I2C_SDA"),
          ("12_RESET_N", "CAM_RST_L"), ("13_PWDN", "CAM_PWDN_L"), ("14_FSYNC_NC", "NC"),
          ("15_GND", "GND"), ("16_MIPI_CLK_N", "CSI_CLK_N"), ("17_MIPI_CLK_P", "CSI_CLK_P"),
          ("18_GND", "GND"), ("19_MIPI_D0_N", "CSI_D0_N"), ("20_MIPI_D0_P", "CSI_D0_P"),
          ("21_GND", "GND"), ("22_MIPI_D1_N", "CSI_D1_N"), ("23_MIPI_D1_P", "CSI_D1_P"),
          ("24_GND", "GND"), ("25_MIPI_D2_N", "CSI_D2_N"), ("26_MIPI_D2_P", "CSI_D2_P"),
          ("27_GND", "GND"), ("28_MIPI_D3_N", "CSI_D3_N"), ("29_MIPI_D3_P", "CSI_D3_P"),
          ("30_GND", "GND"), ("31_MODULE_ID", "CAM_MODULE_ID"), ("32_NC", "NC"), ("33_GND", "GND"),
      ]),
    C(ref="J5", bom_id="C040", value="U.FL / I-PEX MHF RF test connector", board=REAR, assembly="DNP",
      gate="EVT RF debug only; production prefers direct coax or soldered antenna pigtail",
      footprint="Connector_Coaxial:U.FL_Hirose_U.FL-R-SMT-1_Vertical",
      desc="Micro RF connector — DNP RF debug/attach option on the shared Wi-Fi/BLE antenna feed. "
           "Do not consume production Z-height unless RF bring-up requires it.",
      pins=[("SIG", "WIFI_ANT"), ("GND", "GND")]),
    C(ref="TP1", bom_id="C041", value="UART/SWD pogo pads", board=EVT, assembly="Fit",
      gate="Voltage domain clearly labelled (no 3.3V into 1.8V IO)",
      footprint="AI_Glasses_V2:TestPad_Set",
      desc="UART/SWD test pads — RK3576 UART0 + nRF SWD + GND/VREF for bring-up (no connector height).",
      pins=[("SOC_TX", "SOC_DBG_TX"), ("SOC_RX", "SOC_DBG_RX"),
            ("SWDIO", "NRF_SWDIO"), ("SWDCLK", "NRF_SWDCLK"), ("GND", "GND")]),
    C(ref="SW1", bom_id="C042a", value="Power/PWRKEY", board=EVT, assembly="Fit",
      gate="First chip-down must recover from boot failure",
      footprint="Button_Switch_SMD:SW_Push_1P1T_NO_CK_KMR2",
      desc="Power key — RK3576 PWRON via AON/PMIC.",
      pins=[("A", "SOC_PWRKEY"), ("B", "GND")]),
    C(ref="SW2", bom_id="C042b", value="Reset", board=EVT, assembly="Fit",
      gate="Bring-up",
      footprint="Button_Switch_SMD:SW_Push_1P1T_NO_CK_KMR2",
      desc="Reset key — RK3576 RESET_n.",
      pins=[("A", "SOC_RESET_L"), ("B", "GND")]),
    C(ref="SW3", bom_id="C042c", value="MaskROM/Recovery", board=EVT, assembly="Fit",
      gate="Bring-up (recover from bad boot)",
      footprint="Button_Switch_SMD:SW_Push_1P1T_NO_CK_KMR2",
      desc="MaskROM/recovery key — force USB recovery boot.",
      pins=[("A", "SOC_MASKROM_L"), ("B", "GND")]),
]

# ── C044: EVT current-sense — the canonical 10 measurement points (§29) ──────
# Battery shunts (RS1 total, RS2/RS3 branches) live in the BATTERY section (at
# the cells). Here: island-input shunts off VSYS + per-camera-rail Kelvin shunts,
# and all INA238 monitors. Every INA238 is DNP: EVT-A populates all; EVT-B /
# production keeps the shunt pads (0R) and DNPs the INAs except the RS1 main path.
# Shunt values follow docs/04 (Vdrop = Ipeak x Rshunt; SoC small to avoid UVLO).
# I_AON is NOT a separate shunt: nPM1300 integrates the AON bucks, so AON current
# = nPM1300 fuel gauge + the Deep-Off RS1 total (gated islands off).
CURRENT_SENSE = [
    C(ref="RS4", bom_id="C044-RSOC", value="10 mohm 1%", board=COMPUTE, assembly="Fit",
      gate="5-20 mohm (2A x 10m=20mV; avoid boost UVLO)", footprint="AI_Glasses_V2:R_0805_shunt",
      desc="RK3576 island shunt — VSYS -> SOC_IN (I_SOC_5V).", pins=[("A", "VSYS"), ("B", "SOC_IN")]),
    C(ref="RS5", bom_id="C044-RWIFI", value="50 mohm 1%", board=COMPUTE, assembly="Fit",
      gate="20-100 mohm", footprint="AI_Glasses_V2:R_0603_shunt",
      desc="Wi-Fi island shunt — VSYS -> WIFI_IN (I_WIFI).", pins=[("A", "VSYS"), ("B", "WIFI_IN")]),
    C(ref="RS6", bom_id="C044-RAUD", value="50 mohm 1%", board=COMPUTE, assembly="Fit",
      gate="20-100 mohm", footprint="AI_Glasses_V2:R_0603_shunt",
      desc="Audio island shunt — VSYS -> AUDIO_IN (I_AUDIO).", pins=[("A", "VSYS"), ("B", "AUDIO_IN")]),
    C(ref="RS7", bom_id="C044-RC1", value="100 mohm 1%", board=FRONT, assembly="Fit",
      gate="Per-rail Kelvin (§23/§29); DVDD ~250mA", footprint="AI_Glasses_V2:R_0603_shunt",
      desc="Camera DVDD shunt — CAM_1V1 -> CAM_1V1_S (I_CAM_1V1).", pins=[("A", "CAM_1V1"), ("B", "CAM_1V1_S")]),
    C(ref="RS8", bom_id="C044-RC8", value="100 mohm 1%", board=FRONT, assembly="Fit",
      gate="Per-rail Kelvin (§23/§29); IOVDD ~3mA", footprint="AI_Glasses_V2:R_0402_shunt",
      desc="Camera IOVDD shunt — CAM_1V8_SW -> CAM_1V8_S (I_CAM_1V8).", pins=[("A", "CAM_1V8_SW"), ("B", "CAM_1V8_S")]),
    C(ref="RS9", bom_id="C044-RC29", value="100 mohm 1%", board=FRONT, assembly="Fit",
      gate="Per-rail Kelvin (§23/§29); AVDD ~156mA", footprint="AI_Glasses_V2:R_0603_shunt",
      desc="Camera AVDD shunt — CAM_2V9 -> CAM_2V9_S (I_CAM_2V9).", pins=[("A", "CAM_2V9"), ("B", "CAM_2V9_S")]),
    C(ref="U25", bom_id="C044a", value="INA238 (I_BAT_TOTAL)", board=AON, assembly="DNP", pri="P1",
      gate="Power Gate — EVT-A; production may keep this one", footprint="AI_Glasses_V2:VSSOP-10",
      desc="Whole-device current across RS1 (BAT_P->VBAT). Deep Off total = AON only, so it also "
           "backs the AON 20-50 mW check; nPM1300 fuel gauge cross-checks.",
      pins=[("IN_P", "BAT_P"), ("IN_N", "NPM_VBAT"), ("SCL", "I2C_AON_SCL"), ("SDA", "I2C_AON_SDA"), ("GND", "GND")]),
    C(ref="U26", bom_id="C044-ICL", value="INA238 (I_CELL_L)", board=REAR, assembly="DNP", pri="P1",
      gate="Power Gate — EVT-A only (current-share)", footprint="AI_Glasses_V2:VSSOP-10",
      desc="Left branch current across RS2 — cell current-share vs SOC/temp.",
      pins=[("IN_P", "BATL_F"), ("IN_N", "BAT_P"), ("SCL", "I2C_AON_SCL"), ("SDA", "I2C_AON_SDA"), ("GND", "GND")]),
    C(ref="U27", bom_id="C044-ICR", value="INA238 (I_CELL_R)", board=REAR, assembly="DNP", pri="P1",
      gate="Power Gate — EVT-A only (current-share)", footprint="AI_Glasses_V2:VSSOP-10",
      desc="Right branch current across RS3 — cell current-share vs SOC/temp.",
      pins=[("IN_P", "BATR_F"), ("IN_N", "BAT_P"), ("SCL", "I2C_AON_SCL"), ("SDA", "I2C_AON_SDA"), ("GND", "GND")]),
    C(ref="U28", bom_id="C044c", value="INA238 (I_SOC_5V)", board=COMPUTE, assembly="DNP", pri="P1",
      gate="Power Gate — EVT-A only", footprint="AI_Glasses_V2:VSSOP-10",
      desc="RK3576 island monitor across RS4 — record/AI curves + wake energy.",
      pins=[("IN_P", "VSYS"), ("IN_N", "SOC_IN"), ("SCL", "I2C_AON_SCL"), ("SDA", "I2C_AON_SDA"), ("GND", "GND")]),
    C(ref="U29", bom_id="C044e", value="INA238 (I_WIFI)", board=COMPUTE, assembly="DNP", pri="P1",
      gate="Power Gate — EVT-A only", footprint="AI_Glasses_V2:VSSOP-10",
      desc="Wi-Fi island monitor across RS5 — FCU760K TX avg vs 353mA peak.",
      pins=[("IN_P", "VSYS"), ("IN_N", "WIFI_IN"), ("SCL", "I2C_AON_SCL"), ("SDA", "I2C_AON_SDA"), ("GND", "GND")]),
    C(ref="U30", bom_id="C044f", value="INA238 (I_AUDIO)", board=COMPUTE, assembly="DNP", pri="P1",
      gate="Power Gate — EVT-A only", footprint="AI_Glasses_V2:VSSOP-10",
      desc="Audio island monitor across RS6 — speech avg vs music peak.",
      pins=[("IN_P", "VSYS"), ("IN_N", "AUDIO_IN"), ("SCL", "I2C_AON_SCL"), ("SDA", "I2C_AON_SDA"), ("GND", "GND")]),
    C(ref="U31", bom_id="C044-IC1", value="INA238 (I_CAM_1V1)", board=FRONT, assembly="DNP", pri="P1",
      gate="Power Gate — EVT-A only", footprint="AI_Glasses_V2:VSSOP-10",
      desc="Camera DVDD monitor across RS7 — sensor core draw + off-leakage.",
      pins=[("IN_P", "CAM_1V1"), ("IN_N", "CAM_1V1_S"), ("SCL", "I2C_AON_SCL"), ("SDA", "I2C_AON_SDA"), ("GND", "GND")]),
    C(ref="U32", bom_id="C044-IC8", value="INA238 (I_CAM_1V8)", board=FRONT, assembly="DNP", pri="P1",
      gate="Power Gate — EVT-A only", footprint="AI_Glasses_V2:VSSOP-10",
      desc="Camera IOVDD monitor across RS8 — I/O draw + off-leakage.",
      pins=[("IN_P", "CAM_1V8_SW"), ("IN_N", "CAM_1V8_S"), ("SCL", "I2C_AON_SCL"), ("SDA", "I2C_AON_SDA"), ("GND", "GND")]),
    C(ref="U33", bom_id="C044-IC29", value="INA238 (I_CAM_2V9)", board=FRONT, assembly="DNP", pri="P1",
      gate="Power Gate — EVT-A only", footprint="AI_Glasses_V2:VSSOP-10",
      desc="Camera AVDD monitor across RS9 — analog draw + off-leakage.",
      pins=[("IN_P", "CAM_2V9"), ("IN_N", "CAM_2V9_S"), ("SCL", "I2C_AON_SCL"), ("SDA", "I2C_AON_SDA"), ("GND", "GND")]),
]

# ── AON I2C pull-ups (passive spec locked pre-layout, V1 audit discipline) ────
PASSIVES = [
    C(ref="R3", bom_id="C045a", value="2.2k 1%", board=AON, assembly="Fit",
      gate="Confirm vs total AON bus capacitance",
      footprint="AI_Glasses_V2:R_0402",
      desc="AON I2C SCL pull-up to AON_1V8 (nPM1300/BMI270/INA238 bus).",
      pins=[("A", "AON_1V8"), ("B", "I2C_AON_SCL")]),
    C(ref="R4", bom_id="C045b", value="2.2k 1%", board=AON, assembly="Fit",
      gate="Confirm vs total AON bus capacitance",
      footprint="AI_Glasses_V2:R_0402",
      desc="AON I2C SDA pull-up to AON_1V8.",
      pins=[("A", "AON_1V8"), ("B", "I2C_AON_SDA")]),
    C(ref="R5", bom_id="C045c", value="2.2k 1%", board=FRONT, assembly="Fit",
      gate="Confirm vs camera bus capacitance",
      footprint="AI_Glasses_V2:R_0402",
      desc="Camera I2C SCL pull-up to CAM_1V8_SW.",
      pins=[("A", "CAM_1V8_SW"), ("B", "CAM_I2C_SCL")]),
    C(ref="R6", bom_id="C045d", value="2.2k 1%", board=FRONT, assembly="Fit",
      gate="Confirm vs camera bus capacitance",
      footprint="AI_Glasses_V2:R_0402",
      desc="Camera I2C SDA pull-up to CAM_1V8_SW.",
      pins=[("A", "CAM_1V8_SW"), ("B", "CAM_I2C_SDA")]),
    C(ref="R9", bom_id="C045e", value="2.2k 1%", board=COMPUTE, assembly="Fit",
      gate="Confirm vs SoC PMIC bus",
      footprint="AI_Glasses_V2:R_0402",
      desc="SoC-PMIC I2C SCL pull-up to VCCIO_1V8 (RK3576<->RK806).",
      pins=[("A", "VCCIO_1V8"), ("B", "SOC_PMIC_SCL")]),
    C(ref="R10", bom_id="C045f", value="2.2k 1%", board=COMPUTE, assembly="Fit",
      gate="Confirm vs SoC PMIC bus",
      footprint="AI_Glasses_V2:R_0402",
      desc="SoC-PMIC I2C SDA pull-up to VCCIO_1V8.",
      pins=[("A", "VCCIO_1V8"), ("B", "SOC_PMIC_SDA")]),
]

# ── EN default-state pull-downs (§4: default OFF; crash-safe) ─────────────────
# Every high-power rail enable has a hardware default = OFF so that at power-on,
# and if the MCU resets or its firmware hangs, the SoC / camera / Wi-Fi / audio
# do NOT come up. The nRF54L15 must actively assert each EN to turn a rail on.
EN_DEFAULTS = [
    C(ref="R11", bom_id="C046a", value="100k", board=COMPUTE, assembly="Fit",
      gate="Default OFF (§4)", footprint="AI_Glasses_V2:R_0402",
      desc="SOC_PWR_EN pull-down — RK3576 boost default OFF (main SoC off at boot).",
      pins=[("A", "SOC_PWR_EN"), ("B", "GND")]),
    C(ref="R12", bom_id="C046b", value="100k", board=COMPUTE, assembly="Fit",
      gate="Default OFF (§4)", footprint="AI_Glasses_V2:R_0402",
      desc="PMIC_PWRON pull-down — RK806 stays off until AON MCU sequences it.",
      pins=[("A", "PMIC_PWRON"), ("B", "GND")]),
    C(ref="R13", bom_id="C046c", value="100k", board=FRONT, assembly="Fit",
      gate="Default OFF (§4)", footprint="AI_Glasses_V2:R_0402",
      desc="CAM_1V1_EN pull-down — camera core buck default OFF.",
      pins=[("A", "CAM_1V1_EN"), ("B", "GND")]),
    C(ref="R14", bom_id="C046d", value="100k", board=FRONT, assembly="Fit",
      gate="Default OFF (§4)", footprint="AI_Glasses_V2:R_0402",
      desc="CAM_1V8_EN pull-down — camera I/O load switch default OFF.",
      pins=[("A", "CAM_1V8_EN"), ("B", "GND")]),
    C(ref="R15", bom_id="C046e", value="100k", board=FRONT, assembly="Fit",
      gate="Default OFF (§4)", footprint="AI_Glasses_V2:R_0402",
      desc="CAM_2V9_EN pull-down — camera analog LDO default OFF.",
      pins=[("A", "CAM_2V9_EN"), ("B", "GND")]),
    C(ref="R16", bom_id="C046f", value="100k", board=COMPUTE, assembly="Fit",
      gate="Default OFF (§4)", footprint="AI_Glasses_V2:R_0402",
      desc="WIFI_BUCK_EN pull-down — Wi-Fi buck default OFF.",
      pins=[("A", "WIFI_BUCK_EN"), ("B", "GND")]),
    C(ref="R17", bom_id="C046g", value="100k", board=COMPUTE, assembly="Fit",
      gate="Default OFF (§4)", footprint="AI_Glasses_V2:R_0402",
      desc="WIFI_LS_EN pull-down — Wi-Fi load switch default OFF.",
      pins=[("A", "WIFI_LS_EN"), ("B", "GND")]),
    C(ref="R18", bom_id="C046h", value="100k", board=COMPUTE, assembly="Fit",
      gate="Default OFF (§4/§9: FCU760K CHIP_EN default low)", footprint="AI_Glasses_V2:R_0402",
      desc="WIFI_CHIP_EN pull-down — FCU760K held off until AON MCU enables it (pack §9).",
      pins=[("A", "WIFI_CHIP_EN"), ("B", "GND")]),
    C(ref="R19", bom_id="C046i", value="100k", board=COMPUTE, assembly="Fit",
      gate="Default OFF (§4)", footprint="AI_Glasses_V2:R_0402",
      desc="AUDIO_LS_EN pull-down — audio amp load switch default OFF.",
      pins=[("A", "AUDIO_LS_EN"), ("B", "GND")]),
    C(ref="R20", bom_id="C046j", value="100k", board=COMPUTE, assembly="Fit",
      gate="Default OFF (§4)", footprint="AI_Glasses_V2:R_0402",
      desc="AUDIO_AMP_SD pull-down — MAX98360A shutdown default (amp muted at boot).",
      pins=[("A", "AUDIO_AMP_SD"), ("B", "GND")]),
]

# Full ordered component list (drives both schematic + BOM report).
COMPONENTS: list[Component] = [
    *COMPUTE_BOARD,
    *AON_BOARD,
    *FRONT_BOARD,
    *AUDIO_BOARD,
    *BATTERY,
    *INTERFACE,
    *CURRENT_SENSE,
    *EN_DEFAULTS,
    *PASSIVES,
]


def all_nets() -> list[str]:
    """Ordered unique net list (GND first), for the netlist / PCB net table."""
    nets: list[str] = ["GND"]
    for comp in COMPONENTS:
        for _, net in comp.pins:
            n = net.strip()
            if n and n.upper() not in {"NC", "DNP"} and n not in nets:
                nets.append(n)
    return nets


def _validate() -> list[str]:
    problems: list[str] = []
    seen: dict[str, str] = {}
    for comp in COMPONENTS:
        if comp.ref in seen:
            problems.append(f"duplicate refdes {comp.ref} (bom {comp.bom_id} and {seen[comp.ref]})")
        seen[comp.ref] = comp.bom_id
        if not comp.pins:
            problems.append(f"{comp.ref} ({comp.bom_id}) has no pins")
    # every net should have >=2 endpoints, else it is an isolated stub (ERC noise)
    endpoints: dict[str, int] = {}
    for comp in COMPONENTS:
        for _, net in comp.pins:
            n = net.strip()
            if n and n.upper() not in {"NC", "DNP"}:
                endpoints[n] = endpoints.get(n, 0) + 1
    for net, count in sorted(endpoints.items()):
        if count < 2:
            problems.append(f"single-endpoint net '{net}' (add a load/source or mark NC)")
    for net in all_nets():
        meta = net_meta(net)
        missing = [k for k in SIGNAL_META_FIELDS if not meta.get(k)]
        if missing:
            problems.append(f"NET_META incomplete for '{net}': missing {', '.join(missing)}")
    return problems


if __name__ == "__main__":
    problems = _validate()
    n_by_board: dict[str, int] = {}
    n_by_status: dict[str, int] = {}
    for comp in COMPONENTS:
        n_by_board[comp.board] = n_by_board.get(comp.board, 0) + 1
        n_by_status[comp.assembly] = n_by_status.get(comp.assembly, 0) + 1
    print(f"{len(COMPONENTS)} components, {len(all_nets())} nets")
    print("by board:  " + ", ".join(f"{k}={v}" for k, v in n_by_board.items()))
    print("by status: " + ", ".join(f"{k}={v}" for k, v in n_by_status.items()))
    if problems:
        print(f"\n{len(problems)} issue(s):")
        for p in problems:
            print(f"  - {p}")
        raise SystemExit(1)
    print("validation OK — no duplicate refdes, no single-endpoint nets")
