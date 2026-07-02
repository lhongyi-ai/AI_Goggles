#!/usr/bin/env python3
"""Generate a Parts Specification report (型号 & 参数) for the AI Glasses Carrier V1.

Per-part manufacturer part number + headline datasheet parameters, grouped by
subsystem (compute + Wi-Fi/BT, camera, audio + speaker, GNSS, sensors, power,
battery, USB-C, protection, connectors, indicators, passives summary).

MPN + footprint are pulled live from scripts/carrier_bom.py so they stay in sync;
the electrical/mechanical headline specs are curated from the manufacturer
datasheets here. Headline figures only — verify exact numbers and the orderable
suffix against the latest datasheet before procurement.
"""
from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import carrier_bom as bom          # noqa: E402

OUT = ROOT / "reports" / "AI_Glasses_Carrier_V1_Parts_Spec.md"
BY_REF = {c.ref: c for c in bom.COMPONENTS}

_GLYPH = {
    "→": "->", "≥": ">=", "≤": "<=", "≈": "~", "Ω": "ohm", "±": "+/-",
    "–": "-", "—": "-", "•": "-", "…": "...", "“": '"', "”": '"', "’": "'", "×": "x",
    "✓": "[OK]", "⚠": "[!]",
}


def sanitize(s: str) -> str:
    for a, b in _GLYPH.items():
        s = s.replace(a, b)
    return "".join(ch if ord(ch) < 256 else "" for ch in s)


def E(ref, name, mfr, pkg, params, iface):
    """One spec row. If ref is given, MPN/footprint come from the BOM."""
    return {"ref": ref, "name": name, "mfr": mfr, "pkg": pkg, "params": params, "iface": iface}


# ── Curated spec rows by subsystem ──────────────────────────────────────────
SECTIONS: list[tuple[str, str, list[dict]]] = [
 ("1. Compute module + wireless (Wi-Fi / Bluetooth)",
  "The SoC, RAM, eMMC and the Wi-Fi/BT radio all live ON the Radxa CM4 module "
  "(this is a SoM carrier, not chip-down). They reach the carrier only through the "
  "three DF40 B2B connectors. Bluetooth/Wi-Fi are therefore part of the CM4 SKU, "
  "not separate carrier components.",
  [
   E(None, "Radxa CM4 (RM126-D4E32J0R35W28)", "Radxa", "SoM, 3x 100-pin DF40 B2B",
     "SoC Rockchip RK3576 (4x Cortex-A72 + 4x A53, NPU ~6 TOPS); RAM 4GB LPDDR4X; "
     "eMMC 32GB; supply 5V DCIN; GPIO bank 1.8V (GPIO_VREF)", "B2B J31/J32/J1"),
   E(None, "Wi-Fi (on CM4 module)", "on-module", "in CM4 SKU",
     "802.11ax (Wi-Fi 6), 2.4 + 5 GHz; antenna on-module / per SKU", "SDIO/PCIe in CM4"),
   E(None, "Bluetooth (on CM4 module)", "on-module", "in CM4 SKU",
     "Bluetooth 5.x (BLE + classic); shares CM4 wireless front-end; antenna per SKU",
     "UART/PCM in CM4"),
  ]),

 ("2. Camera",
  "Sony IMX415 (Radxa Camera 4K) on CM4 CSI3, 4-lane MIPI, via a 31-pin 0.3mm FFC.",
  [
   E(None, "IMX415-AAQR-C (Radxa Camera 4K)", "Sony", "module (off-board, via J2 FFC)",
     "1/2.8in 8.29 MP (3864x2192) CMOS; 4-lane MIPI CSI-2; up to 90 fps; "
     "rails IO 1.8V / analog 2.9V / core 1.1V (on module); I2C control", "CSI3 4-lane, I2C0"),
   E("J2", "FH35C-31S-0.3SHW(50)", "Hirose", None,
     "31-pos 0.3mm-pitch FFC/FPC connector, bottom-contact; camera flex", "CSI3 FFC"),
  ]),

 ("3. Audio (amplifier, microphones, speaker)",
  "Class-D speaker path + dual PDM MEMS mics. Speaker is off-board via J3.",
  [
   E("U4", "MAX98357AETE+T", "Analog Devices (Maxim)", None,
     "Mono class-D amp; I2S/SAI (Left/Right/(L+R)/2); ~3.2W into 4ohm @5V (~92% eff); "
     "no MCLK needed; gain 3/6/9/12/15 dB; supply 2.5-5.5V", "SAI1 (BCLK/LRCK/DIN)"),
   E("MK1", "SPH0641LU4H-1", "Knowles", None,
     "PDM digital MEMS mic, bottom port; SNR 64.3 dB(A); AOP 120 dBSPL; "
     "sens -26 dBFS; supply 1.6-3.6V; ultrasonic-capable", "PDM1 (L, SEL=GND)"),
   E("MK2", "SPH0641LU4H-1", "Knowles", None,
     "Same as MK1; right channel", "PDM1 (R, SEL=VDD)"),
   E(None, "OWS-091630W50A-8 (speaker)", "OWS / generic", "9x16x3.0 mm (off-board via J3)",
     "8 ohm; rated ~1 W (peak higher); micro rectangular speaker; SPL/Fo per datasheet",
     "amp OUT+/OUT- (post FB1/FB2)"),
   E("FB1", "Ferrite 600ohm@100MHz", "Murata/TDK class", None,
     "Class-D EMI bead on OUT+; with C23 1nF", "speaker EMI"),
   E("FB2", "Ferrite 600ohm@100MHz", "Murata/TDK class", None,
     "Class-D EMI bead on OUT-; with C24 1nF", "speaker EMI"),
  ]),

 ("4. GNSS (positioning)",
  "u-blox MAX-M10S over UART; external active antenna via U.FL.",
  [
   E("U14", "MAX-M10S-00B-01", "u-blox", None,
     "GNSS receiver GPS/GLONASS/Galileo/BeiDou/QZSS; tracking sens -167 dBm; "
     "~25 mA continuous; VCC 2.7-3.6V, VIO 1.8V; UART/I2C", "UART7, U.FL (J8)"),
   E("J8", "U.FL-R-SMT-1", "Hirose", None,
     "50 ohm U.FL/IPEX coax RF connector; external active GNSS antenna", "RF 50 ohm"),
   E("D4", "low-cap RF ESD (<=0.3pF)", "TBD (Nexperia/Littelfuse class)", None,
     "RF ESD clamp on antenna feed; capacitance <=0.3 pF; Vrwm >=5V", "antenna ESD"),
  ]),

 ("5. Sensors (IMU, haptics)",
  None,
  [
   E("U10", "ICM-42688-P", "TDK InvenSense", None,
     "6-axis IMU; accel +/-2/4/8/16 g; gyro up to +/-2000 dps; gyro noise "
     "~2.8 mdps/rtHz; I2C/SPI; supply 1.71-3.6V", "I2C8, INT1"),
   E("U11", "DRV2605L", "Texas Instruments", None,
     "Haptic driver for LRA/ERM; I2C; 123-effect waveform ROM (TI/Immersion); "
     "supply 2-5.2V", "I2C + PWM (vib motor J6)"),
  ]),

 ("6. Power (boost, charger, fuel gauge, protection, LDOs)",
  "1S Li-Po -> 5V system via boost; per-rail LDOs; charge + gauge + cell protection.",
  [
   E("U6", "TPS61022", "Texas Instruments", None,
     "Sync boost; Vin 0.5-5.5V; Vout up to 5.5V; 8A switch; up to 96% eff; ~1 MHz",
     "VBAT -> +5V_SYS"),
   E("L1", "Boost inductor 4.7uH", "TBD (Cyntec/Wurth class)", None,
     "4.7 uH; saturation >=10 A; low DCR; shielded; size per measured peak current",
     "boost SW node"),
   E("U7", "BQ25180", "Texas Instruments", None,
     "1S Li-ion charger w/ power path; up to 1A charge; input 3.5-5.5V; I2C; ship mode",
     "I2C6, USB-C 5V in"),
   E("U8", "BQ29700", "Texas Instruments", None,
     "Single-cell protection: OVP/UVP/OCP/SCP; ultra-low IQ", "battery protection"),
   E("U9", "MAX17048", "Analog Devices (Maxim)", None,
     "ModelGauge fuel gauge (SOC); I2C; ~3 uA hibernate; low-batt alert", "I2C6"),
   E("U3", "LP5907MFX-3.3", "Texas Instruments", None,
     "250 mA ultra-low-noise LDO; 6.5 uVrms; PSRR ~82 dB; -> camera 3.3V", "+CAM_3V3"),
   E("U12", "TLV75733", "Texas Instruments", None,
     "1A LDO; low IQ; -> 3.3V system rail", "+3V3"),
   E("U13", "TLV75718", "Texas Instruments", None,
     "1A LDO; low IQ; -> 1.8V VCCIO rail", "+1V8"),
   E("U15", "TPS25940 (DNP/opt)", "Texas Instruments", None,
     "eFuse: OVP/OCP/reverse-block/inrush; Vin 2.7-18V; optional, DNP by default", "VBUS in"),
  ]),

 ("7. Battery",
  "1S Li-Po. V1 bench cell locked; glasses build uses thin temple cells.",
  [
   E("J5", "JST-PH 3p", "JST", None,
     "Battery connector BAT+/BAT-/NTC; 2.0mm pitch", "battery"),
   E(None, "V1 bench cell (103450)", "generic 1S Li-Po", "10x34x50 mm",
     "1S 3.7V nominal; ~2000 mAh; with PCM; NTC recommended", "via J5"),
   E(None, "Glasses pack (target)", "custom 1S", "~35x18x4 mm cells",
     "2-3 cells, ~250 mAh each (~500-750 mAh); >3-4h needs AI duty-cycling", "via J5"),
  ]),

 ("8. USB-C + protection",
  None,
  [
   E("J4", "USB4085-GF-A", "GCT", None,
     "USB-C receptacle; USB2 + 5V sink; 16-pos", "USB2, 5V in"),
   E("U5", "TPD2E009", "Texas Instruments", None,
     "2-ch ESD clamp for USB2 D+/D-; low cap ~1.5 pF; Vrwm >=5V", "USB D+/D-"),
   E("D3", "SMAJ5.0A", "Littelfuse/Bourns class", None,
     "Uni TVS for VBUS; 5V standoff; 400W peak pulse", "VBUS surge/ESD"),
   E("R1", "5.1k 1%", "Yageo class", None,
     "USB-C CC1 sink pull-down (locked 1%)", "CC1"),
   E("R2", "5.1k 1%", "Yageo class", None,
     "USB-C CC2 sink pull-down (locked 1%)", "CC2"),
  ]),

 ("9. MIPI / camera ESD",
  None,
  [
   E("U2", "TPD4E05U06", "Texas Instruments", None,
     "4-ch ultra-low-cap (0.4 pF) ESD array for MIPI CSI lanes; Vrwm >=5V", "CSI3 lanes"),
   E("U16", "TPD4E05U06", "Texas Instruments", None,
     "Second 4-ch low-cap ESD array (remaining CSI lanes)", "CSI3 lanes"),
  ]),

 ("10. CM4 board-to-board connectors",
  "Carrier-side receptacles; mate the CM4's DF40C-100DP plugs; 1.5mm board gap. "
  "Footprint geometry is the KiCad library part; the locked 3-connector PLACEMENT "
  "still needs the mechanical fit-check (official CM4 STEP + 2-layer coupon).",
  [
   E("J31", "DF40C-100DS-0.4V(51)", "Hirose", None,
     "100-pin, 0.4mm pitch B2B receptacle; CM4 J3A (low-speed)", "CM4 J3A"),
   E("J32", "DF40C-100DS-0.4V(51)", "Hirose", None,
     "100-pin, 0.4mm pitch B2B receptacle; CM4 J3B (high-speed: MIPI/USB)", "CM4 J3B"),
   E("J1", "DF40C-100DS-0.4V(51)", "Hirose", None,
     "100-pin, 0.4mm pitch B2B receptacle; CM4 J1 (I/O: SAI, MCLK)", "CM4 J1"),
  ]),

 ("11. Other connectors + indicators",
  None,
  [
   E("J3", "JST-SH 2p", "JST", None, "Speaker connector (post-EMI); 1.0mm pitch", "speaker"),
   E("J6", "JST-SH 2p", "JST", None, "Vibration motor connector; 1.0mm pitch", "haptic"),
   E("J7", "Header 1x4 2.54mm", "generic", None, "UART debug (TX/RX/GND/VREF)", "UART0"),
   E("D1", "LED Green", "generic", None, "Power LED; active-low GPIO sink; via R4 1k", "status"),
   E("D2", "LED Blue", "generic", None, "Status LED; active-low GPIO sink; via R5 1k", "status"),
  ]),
]


def part_label(e: dict) -> str:
    """MPN: prefer the live BOM MPN for ref rows, else the curated name."""
    if e["ref"] and e["ref"] in BY_REF and BY_REF[e["ref"]].mpn:
        return BY_REF[e["ref"]].mpn
    return e["name"]


def pkg_label(e: dict) -> str:
    if e["pkg"]:
        return e["pkg"]
    if e["ref"] and e["ref"] in BY_REF:
        return f"`{BY_REF[e['ref']].footprint}`"
    return "-"


def main() -> int:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    md: list[str] = []

    def w(line: str = "") -> None:
        md.append(sanitize(line))

    n_ic = sum(1 for _, _, rows in SECTIONS for e in rows if e["ref"] and e["ref"].startswith("U"))
    w("# AI Glasses Carrier V1 - Parts Specification")
    w("")
    w(f"- **Generated:** {date.today().isoformat()}  |  **Board:** ai_glasses_carrier_v1")
    w("- **Scope:** key devices with manufacturer part number + headline datasheet parameters, "
      "by subsystem (compute + Wi-Fi/BT, camera, audio + speaker, GNSS, sensors, power, "
      "battery, USB-C, protection, connectors).")
    w("- MPN + footprint are pulled live from the BOM (`scripts/carrier_bom.py`); the electrical/"
      "mechanical specs are curated from the manufacturer datasheets.")
    w("")
    w("> [!] **Headline figures only.** Verify exact numbers and the full orderable suffix "
      "(reel/package/grade) against the latest manufacturer datasheet before procurement. "
      "Wi-Fi/Bluetooth are integrated in the CM4 SKU (this is a SoM carrier, not chip-down).")
    w("")
    w("---")

    for title, intro, rows in SECTIONS:
        w(f"## {title}")
        w("")
        if intro:
            w(intro)
            w("")
        w("| Ref | Part / MPN | Mfr | Package | Key parameters | Interface / Rail |")
        w("|---|---|---|---|---|---|")
        for e in rows:
            ref = e["ref"] or "-"
            w(f"| {ref} | {part_label(e)} | {e['mfr']} | {pkg_label(e)} | "
              f"{e['params']} | {e['iface']} |")
        w("")

    # Passives summary (full detail lives in the Design Review report §7)
    w("## 12. Passives (summary)")
    w("")
    w("Full per-family passive audit (value / tolerance / dielectric / voltage / DC-bias "
      "verdicts) is in **AI_Glasses_Carrier_V1_Design_Review.pdf §7**. Headline:")
    w("")
    w("| Family | Refs (examples) | Spec |")
    w("|---|---|---|")
    w("| I2C pull-ups | R7-R13 | 2.2k 1% 0603 |")
    w("| USB-C CC | R1, R2 | 5.1k 1% 0603 (locked) |")
    w("| Decoupling | C2,C4,C6,C10,C13... | 100nF X7R 50V 0603 |")
    w("| Bulk MLCC | C1,C3,C5,C8,C15,C29 | 10uF X5R 25V 0805 |")
    w("| VBAT bulk | C7 | 22uF X5R 25V 0805 |")
    w("| Class-D EMI | C23, C24 | 1nF X7R 50V 0603 |")
    w("| Current shunt | R3 | mohm 2512 (select for 5V measure) |")
    w("")
    w("---")
    w("_Generated by `scripts/generate_parts_spec.py`. MPN/footprint live from the BOM; "
      "headline specs curated from manufacturer datasheets - verify before procurement._")

    OUT.write_text("\n".join(md) + "\n", encoding="utf-8")
    rows_total = sum(len(r) for _, _, r in SECTIONS)
    print(f"wrote {OUT.relative_to(ROOT)} ({len(md)} lines, {rows_total} part rows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
