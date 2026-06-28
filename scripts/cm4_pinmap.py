#!/usr/bin/env python3
"""WORKING MASTER for the CM4 V1 pin assignment (Claude-editable format).

Per project workflow: CSV/JSON/Python is the *working* format; Excel is the
*delivery* format.  This module is the single source of truth.  Run
scripts/build_pin_assignment.py to regenerate:
  - config/cm4_v1_pin_assignment.yaml   (read by the freeze-gate checker)
  - generated/reports/cm4_v1_pin_assignment.csv   (review/diff)
  - generated/reports/cm4_v1_pin_assignment.xlsx  (formal delivery)

ALL pin numbers below are taken from the OFFICIAL sources the user provided:
  - radxa_cm4_pinout_v1.20.xlsx  (Net Name + pin number + RK3576 mux functions)
  - Radxa CM4 Schematic V1.20    (sheets 21 J3A / 22 J3B / 23 J1)
so every row is source_verified: true.

KEY DESIGN DECISIONS (human-reviewable):
  * GPIO_VREF (J3A pin 78) tied to 1.8V  → all J3A GPIO bank signals are 1.8V.
    Camera control IO, PDM, SAI, IMU all operate at 1.8V, so VCCIO = 1.8V.
  * Camera target = Radxa Camera 4K / Sony IMX415-AAQR-C on CM4 CSI3 4-lane.
    J2 is the 31-pin Hirose FH35C connector used with Radxa AC006.
  * Camera control I2C = I2C0_M1 (J3A 80/82, the RPi-CM4 camera/HAT I2C).
  * PDM mics = PDM1 (CLK J3B-96, SDI1 J3B-94, SDI2 J3B-111) — already broken out.
  * Audio out = SAI1 (J1 19/23/25/29) — contiguous block on the IO connector.
  * Debug UART = UART0_M0 (J3A 55/51, the dedicated CM4 debug console).
  * GNSS UART = UART7_M0 (J3A 47/45) + PPS/RST on spare J3A GPIO.
  * IMU I2C = I2C8_M1 (J3A 56/58); Fuel-gauge I2C = I2C6_M3 (J3A 35/36)
    → camera / IMU / fuel gauge are on three DIFFERENT I2C controllers.
"""
from __future__ import annotations

METADATA = {
    "board": "ai_glasses_carrier_v1",
    "schematic_ref": "Radxa CM4 Schematic V1.20",
    "pinout_ref": "radxa_cm4_pinout_v1.20.xlsx",
    "soc_ref": "RK3576 Brief Datasheet V1.2",
    # status: DRAFT -> REVIEW -> FROZEN. Pins are verified, but procurement
    # TBDs (CM4 SKU, camera module, battery...) still block the full freeze.
    "status": "REVIEW",
    "gpio_vref": "1.8V (GPIO_VREF / J3A pin 78)",
    "cm4_sku": "RM126-D4E32J0R35W28 (RK3576, 4GB LPDDR4X, 32GB eMMC, Wi-Fi6+BT5.x)",
}

# Helper: one assignment row.
def _a(function, signal, connector, pin, cm4_net, cm4_func, vdom, conflict,
       connects, dt, pri="P0", verified=True):
    return dict(function=function, signal=signal, connector=connector, pin=pin,
                cm4_net=cm4_net, cm4_func=cm4_func, voltage_domain=vdom,
                pinmux_conflict=conflict, board_connects_to=connects,
                device_tree_status=dt, priority=pri, source_verified=verified)


ASSIGNMENTS = [
    # ── POWER (P0) — confirmed 5V input pins ────────────────────────────────
    *[_a("Power", "+5V_IN", "J3A", p, "5V_DCIN", "power", "5V", "none",
         "+5V_SYS rail (all 6 paralleled)", "n/a (power)")
      for p in (77, 79, 81, 83, 85, 87)],
    _a("Power", "GND", "J3A/J3B/J1", "ALL_GND", "GND", "power", "GND", "none",
       "GND plane (connect every GND pin)", "n/a (power)"),
    _a("Power", "+3V3_OUT(CM4)", "J3A", "84,86", "VCCIO6", "power", "3.3V", "none",
       "CM4 3V3 out (600mA) — reference only; carrier uses own LDO", "n/a", "P1"),
    _a("Power", "+1V8_OUT(CM4)", "J3A", "88,90", "VCC_1V8_S0", "power", "1.8V", "none",
       "CM4 1V8 out — VCCIO for mics/IMU if budget allows", "n/a", "P1"),
    _a("Power", "GPIO_VREF", "J3A", 78, "GPIO_VREF", "power",
       "set=1.8V", "none", "Tie to +1V8 (sets J3A GPIO bank to 1.8V)", "n/a (power)"),

    # ── CAMERA — Radxa Camera 4K / IMX415 (CSI3 4-lane) (P0) ────────────────
    _a("Camera", "MIPI_DPHY_CSI3_RX_CLKP", "J3B", 129, "MIPI_DPHY_CSI3_RX_CLKP",
       "MIPI_DPHY_CSI3_RX_CLKP", "diff_1V8 (100Ω)", "none (dedicated MIPI)",
       "Radxa Camera 4K FPC pin 18 MCP", "rkisp/csi3-dphy 4-lane endpoint"),
    _a("Camera", "MIPI_DPHY_CSI3_RX_CLKN", "J3B", 127, "MIPI_DPHY_CSI3_RX_CLKN",
       "MIPI_DPHY_CSI3_RX_CLKN", "diff_1V8 (100Ω)", "none",
       "Radxa Camera 4K FPC pin 17 MCN", "csi3-dphy"),
    _a("Camera", "MIPI_DPHY_CSI3_RX_D0P", "J3B", 117, "MIPI_DPHY_CSI3_RX_D0P",
       "MIPI_DPHY_CSI3_RX_D0P", "diff_1V8 (100Ω)", "none",
       "Radxa Camera 4K FPC pin 15 MDP1", "csi3-dphy data-lanes"),
    _a("Camera", "MIPI_DPHY_CSI3_RX_D0N", "J3B", 115, "MIPI_DPHY_CSI3_RX_D0N",
       "MIPI_DPHY_CSI3_RX_D0N", "diff_1V8 (100Ω)", "none",
       "Radxa Camera 4K FPC pin 14 MDN1", "csi3-dphy data-lanes"),
    _a("Camera", "MIPI_DPHY_CSI3_RX_D1P", "J3B", 123, "MIPI_DPHY_CSI3_RX_D1P",
       "MIPI_DPHY_CSI3_RX_D1P", "diff_1V8 (100Ω)", "none",
       "Radxa Camera 4K FPC pin 12 MDP2", "csi3-dphy data-lanes"),
    _a("Camera", "MIPI_DPHY_CSI3_RX_D1N", "J3B", 121, "MIPI_DPHY_CSI3_RX_D1N",
       "MIPI_DPHY_CSI3_RX_D1N", "diff_1V8 (100Ω)", "none",
       "Radxa Camera 4K FPC pin 11 MDN2", "csi3-dphy data-lanes"),
    _a("Camera", "MIPI_DPHY_CSI3_RX_D2P", "J3B", 135, "MIPI_DPHY_CSI3_RX_D2P",
       "MIPI_DPHY_CSI3_RX_D2P", "diff_1V8 (100Ω)", "none",
       "Radxa Camera 4K FPC pin 6 MDP3", "csi3-dphy data-lanes"),
    _a("Camera", "MIPI_DPHY_CSI3_RX_D2N", "J3B", 133, "MIPI_DPHY_CSI3_RX_D2N",
       "MIPI_DPHY_CSI3_RX_D2N", "diff_1V8 (100Ω)", "none",
       "Radxa Camera 4K FPC pin 5 MDN3", "csi3-dphy data-lanes"),
    _a("Camera", "MIPI_DPHY_CSI3_RX_D3P", "J3B", 141, "MIPI_DPHY_CSI3_RX_D3P",
       "MIPI_DPHY_CSI3_RX_D3P", "diff_1V8 (100Ω)", "none",
       "Radxa Camera 4K FPC pin 3 MDP4", "csi3-dphy data-lanes"),
    _a("Camera", "MIPI_DPHY_CSI3_RX_D3N", "J3B", 139, "MIPI_DPHY_CSI3_RX_D3N",
       "MIPI_DPHY_CSI3_RX_D3N", "diff_1V8 (100Ω)", "none",
       "Radxa Camera 4K FPC pin 2 MDN4", "csi3-dphy data-lanes"),
    _a("Camera", "I2C_CAM_SCL", "J3A", 80, "I2C0_SCL_M1_TP", "I2C0_SCL_M1",
       "1.8V (PMUIO1)", "I2C0 — distinct addr from any HAT EEPROM",
       "Radxa Camera 4K FPC pin 24 SCL", "i2c0 + imx415 subdev"),
    _a("Camera", "I2C_CAM_SDA", "J3A", 82, "I2C0_SDA_M1_TP", "I2C0_SDA_M1",
       "1.8V (PMUIO1)", "I2C0", "Radxa Camera 4K FPC pin 25 SDA", "i2c0 + imx415 subdev"),
    _a("Camera", "CAM_RST_n", "J3B", 143, "MIPI_CAM3_PDN_1V8", "GPIO3_C5",
       "1.8V", "none", "Radxa Camera 4K FPC pin 27 RESET_N; active-low reset",
       "reset-gpios in imx415 node, GPIO_ACTIVE_LOW"),
    # NOTE: Radxa Camera 4K 31-pin pinout has RESET but no PWDN pin.
    _a("Camera", "CAM_MCLK", "J1", 59, "MIPI_CSI3_CAM_CLKOUT_1V8", "CAM_CLK2_OUT_M0",
       "1.8V", "dedicated CAM_CLK2 for CSI3", "Radxa Camera 4K FPC pin 20 MCLK",
       "clocks=<&cru CLK_CAM2_OUT>"),

    # ── PDM MICROPHONES (PDM1) (P0) ─────────────────────────────────────────
    _a("PDM", "PDM1_CLK1_M1", "J3B", 96, "PDM1_CLK1_M1", "PDM1_CLK1_M1 (GPIO4_B0)",
       "1.8V (VCCIO_AUDIO)", "none (dedicated PDM1)", "Both MEMS mics CLK",
       "pdm controller + clk"),
    _a("PDM", "PDM1_SDI1_M1", "J3B", 94, "PDM1_SDI1_M1", "PDM1_SDI1_M1 (GPIO4_B2)",
       "1.8V (VCCIO_AUDIO)", "none", "Mic 0 (L) DATA", "pdm rx channel"),
    _a("PDM", "PDM1_SDI2_M1", "J3B", 111, "PDM1_SDI2_M1", "PDM1_SDI2_M1 (GPIO4_B1)",
       "1.8V (VCCIO_AUDIO)", "none", "Mic 1 (R) DATA", "pdm rx channel"),

    # ── SAI / I2S AUDIO OUT (SAI1) (P0) ─────────────────────────────────────
    _a("SAI", "SAI1_SCLK", "J1", 25, "SAI1_SCLK_M0", "SAI1_SCLK_M0 (GPIO4_A3)",
       "1.8V (VCCIO_AUDIO)", "none (dedicated SAI1)", "Class-D Amp BCLK",
       "sai1 / simple-audio-card"),
    _a("SAI", "SAI1_LRCK", "J1", 19, "SAI1_LRCK_M0", "SAI1_LRCK_M0 (GPIO4_A5)",
       "1.8V (VCCIO_AUDIO)", "none", "Class-D Amp LRCLK", "sai1"),
    _a("SAI", "SAI1_SDO0", "J1", 29, "SAI1_SDO0_M0", "SAI1_SDO0_M0 (GPIO4_A7)",
       "1.8V (VCCIO_AUDIO)", "none", "Class-D Amp DIN", "sai1 playback"),
    _a("SAI", "SAI1_MCLK", "J1", 23, "SAI1_MCLK_M0", "SAI1_MCLK_M0 (GPIO4_A2)",
       "1.8V (VCCIO_AUDIO)", "none", "Unused/DNP: MAX98357A does not require MCLK",
       "unused unless future codec needs mclk", "P1"),

    # ── AUDIO control (P0) ──────────────────────────────────────────────────
    _a("Control", "GPIO_SPKR_EN", "J1", 96, "SPK_CTL_H", "GPIO2_C6",
       "1.8V (VCCIO6)", "none (dedicated speaker ctl)", "Class-D Amp SD/EN",
       "gpio (amp enable)"),

    # ── USB 2.0 OTG0 (P0) ───────────────────────────────────────────────────
    _a("USB", "USB2_OTG0_DP", "J3B", 105, "USB2_OTG0_DP", "USB2_OTG0_DP",
       "USB 3.3V analog (90Ω)", "none", "USB-C D+ (via ESD)", "usb2 otg0 / dwc3"),
    _a("USB", "USB2_OTG0_DM", "J3B", 103, "USB2_OTG0_DM", "USB2_OTG0_DM",
       "USB 3.3V analog (90Ω)", "none", "USB-C D- (via ESD)", "usb2 otg0 / dwc3"),

    # ── DEBUG UART (UART0_M0) (P0) ──────────────────────────────────────────
    _a("UART", "UART0_TX_M0_DEBUG", "J3A", 55, "UART0_TX_M0_DEBUG", "UART0_TX_M0",
       "1.8V (VCCIO6)", "none (dedicated debug)", "Debug header TX", "console UART0"),
    _a("UART", "UART0_RX_M0_DEBUG", "J3A", 51, "UART0_RX_M0_DEBUG", "UART0_RX_M0",
       "1.8V (VCCIO6)", "none", "Debug header RX", "console UART0"),

    # ── GNSS UART (UART7_M0) + control (P0, new per workflow V1.0) ───────────
    _a("GNSS", "GNSS_UART_TX", "J3A", 47, "UART7_TX_M0", "UART7_TX_M0 (GPIO2_B6)",
       "1.8V (VCCIO6)", "none", "GNSS module RXD (CM4→GNSS)", "uart7 / gnss nmea"),
    _a("GNSS", "GNSS_UART_RX", "J3A", 45, "UART7_RX_M0", "UART7_RX_M0 (GPIO2_B7)",
       "1.8V (VCCIO6)", "none", "GNSS module TXD (GNSS→CM4)", "uart7 / gnss nmea"),
    _a("GNSS", "GNSS_PPS", "J3A", 40, "SPI1_MISO_M0", "GPIO1_B6",
       "1.8V (VCCIO6)", "none (used as GPIO)", "GNSS PPS to CM4 GPIO", "pps-gpio"),
    _a("GNSS", "GNSS_RST_n", "J3A", 44, "SPI1_MOSI_M0", "GPIO1_B5",
       "1.8V (VCCIO6)", "none (used as GPIO)", "GNSS RESET/EN (active-low)", "gpio"),

    # ── RECOVERY / RESET / POWER / WIRELESS (P0) ────────────────────────────
    _a("Control", "RECOVERY_n", "J3A", 93, "MASKROM", "nRPIBOOT / SARADC_IN0_BOOT",
       "1.8V", "none (dedicated)", "RECOVERY button to GND (force USB maskrom)",
       "boot select"),
    _a("Control", "RESET_n", "J3A", 92, "RESET_L", "NPOR",
       "1.8V", "none (dedicated)", "RESET button (open-drain to GND)", "soc reset"),
    _a("Control", "POWER_KEY", "J3A", 99, "PWRON_L", "PWRON",
       "1.8V", "none (dedicated)", "Power button (active-low)", "power key"),
    _a("Control", "WL_nDIS", "J3A", 89, "WL_NDIS", "WL_NDIS",
       "1.8V", "none (dedicated)", "Pull-up; default Wi-Fi enabled", "rfkill"),
    _a("Control", "BT_nDIS", "J3A", 91, "BT_NDIS", "GPIO2_C1",
       "1.8V", "none (dedicated)", "Pull-up; default BT enabled", "rfkill"),

    # ── INDICATOR LEDs (P0) — dedicated CM4 LED nets ────────────────────────
    _a("Control", "LED_PWR_n", "J3A", 95, "NPWR_LED", "GPIO2_C4",
       "1.8V (VCCIO6)", "none", "Power LED (active-low sink)", "gpio-leds"),
    _a("Control", "LED_STATUS_n", "J3A", 21, "PI_NLED_ACTIVITY", "GPIO2_D0",
       "1.8V (VCCIO6)", "none", "Status LED (active-low sink)", "gpio-leds"),

    # ── IMU (I2C8) (P1) ─────────────────────────────────────────────────────
    _a("I2C", "I2C_IMU_SCL", "J3A", 56, "I2C8_SCL_M1", "I2C8_SCL_M1 (GPIO1_C6)",
       "1.8V (VCCIO6)", "I2C8 (separate from camera I2C0)", "IMU SCL", "i2c8", "P1"),
    _a("I2C", "I2C_IMU_SDA", "J3A", 58, "I2C8_SDA_M1", "I2C8_SDA_M1 (GPIO1_C7)",
       "1.8V (VCCIO6)", "I2C8", "IMU SDA", "i2c8", "P1"),
    _a("Control", "IMU_INT1", "J3A", 30, "GPIO1_C1", "GPIO1_C1",
       "1.8V (VCCIO6)", "none", "IMU INT1", "interrupt-gpio", "P1"),

    # ── VIBRATION (P1) ──────────────────────────────────────────────────────
    _a("Control", "VIB_PWM", "J3A", 48, "PWM1_CH0_M2", "PWM1_CH0_M2 (GPIO2_C0)",
       "1.8V (VCCIO6)", "PWM-capable pin", "Vibration driver IN/PWM", "pwm", "P1"),
    _a("Control", "VIB_EN", "J3A", 34, "CAN1_TX_M3", "GPIO3_A2",
       "1.8V (VCCIO6)", "none", "Vibration driver EN", "gpio", "P1"),

    # ── BATTERY / CHARGER / FUEL GAUGE (I2C6) (P1) ──────────────────────────
    _a("I2C", "FUEL_I2C_SCL", "J3A", 35, "I2C6_SCL_M3", "I2C6_SCL_M3 (GPIO4_C6)",
       "1.8V (VCCIO6)", "I2C6 (separate from camera/IMU)", "Charger+Fuel gauge SCL",
       "i2c6", "P1"),
    _a("I2C", "FUEL_I2C_SDA", "J3A", 36, "I2C6_SDA_M3", "I2C6_SDA_M3 (GPIO4_C7)",
       "1.8V (VCCIO6)", "I2C6", "Charger+Fuel gauge SDA", "i2c6", "P1"),
    _a("Control", "CHG_INT_n", "J3A", 37, "SPI1_CSN1_M0", "GPIO1_C0",
       "1.8V (VCCIO6)", "none", "Charger interrupt", "interrupt-gpio", "P1"),
    _a("Control", "LOW_BAT_INT_n", "J3A", 39, "SPI1_CSN0_M0", "GPIO1_B7",
       "1.8V (VCCIO6)", "none", "Fuel-gauge low-batt alert", "interrupt-gpio", "P1"),
]

# Section 8.3 open items that still gate the FULL freeze (procurement decisions).
OPEN_TBD = [
    {"id": "CM4_SKU", "must_confirm": "CONFIRMED RM126-D4E32J0R35W28: RK3576 / 4GB LPDDR4X / 32GB "
     "eMMC / Wi-Fi6+BT5.x. Antenna form tracked under ANTENNA.",
     "resolved": True},
    {"id": "CAMERA_ELECTRICAL_PINOUT", "must_confirm": "RESOLVED: camera module is Radxa Camera 4K / "
     "Sony IMX415-AAQR-C; 31-pin FPC pinout captured in "
     "CM4_IMX415_design_files/Radxa_Camera_4K_31pin_pinout.csv and cross-referenced in "
     "docs/p0_p1_decisions_2026-06-28.md.",
     "resolved": True},
    {"id": "CAMERA_CONNECTOR_MPN", "must_confirm": "RESOLVED: carrier J2 connector is "
     "Hirose FH35C-31S-0.3SHW(50), LCSC C424662. Footprint has been generated from the Hirose 2D drawing.",
     "resolved": True},
    {"id": "CAMERA_CABLE", "must_confirm": "RESOLVED: use Radxa AC006, 31P 0.3mm to 31P 0.3mm, "
     "opposite-side FPC. Do not use AC008; AC008 is 31P to 15P.",
     "resolved": True},
    {"id": "CAMERA_SCHEMATIC_GATE", "must_confirm": "RESOLVED for schematic stage: J2 pins 1-31, "
     "CSI3 4-lane mapping, P/N polarity, I2C/MCLK/RESET, voltage domains, power pins and NC pins are "
     "checked by scripts/audit_csi3_camera.py. RESET is active-low on project net CAM_RST_n; no PWDN pin "
     "is present in the Radxa Camera 4K 31-pin pinout.",
     "resolved": True},
    {"id": "CAMERA_KICAD_IMPLEMENTATION", "must_confirm": "PARTIAL: schematic source now uses "
     "31-pin FH35C/Radxa Cam4K pinout on CM4 CSI3 4-lane, and the FH35C footprint has been regenerated "
     "from the Hirose 2D drawing. DEFERRED_TO_PRE_LAYOUT: AC006 physical validation, FPC contact side, "
     "FPC insertion direction, J2 Pin 1 physical check, 1:1 print, coupon test, and FPC bend/enclosure "
     "path. Official CM4 IO overlay radxa-cm4-io-radxa-camera-4k.dtbo is confirmed. Bring-up logs "
     "(dmesg/media/v4l2) remain open for EVT.",
     "resolved": False},
    {"id": "AUDIO_PARTS", "must_confirm": "CONFIRMED: 2×SPH0641LU4H-1 mic, MAX98357AETE+T (C910544) amp, "
     "Ole Wolff OWS-091630W50A-8 8Ω/1W (C5840086) speaker",
     "resolved": True},
    {"id": "GNSS_MODULE", "must_confirm": "CONFIRMED u-blox MAX-M10S-00B-01: UART, VCC=3.3V/VIO=1.8V, "
     "50Ω U.FL, external active antenna (π-match + bias-tee, DNP for passive)",
     "resolved": True},
    {"id": "BATTERY", "must_confirm": "Reverse-calc: 1S 2-3×(35×18×4mm ~250mAh)=500-750mAh/1.85-2.8Wh. "
     "V1 bench use ~1.5-2Ah. >3-4h target needs AI duty-cycling (system-power issue, see report)",
     "resolved": True},
    {"id": "POWER_5V", "must_confirm": "CONSERVATIVE FREEZE: keep TPS61022-class 1S->5V boost and "
     "design +5V_SYS for >=4A bench/boost margin. R3 remains the bring-up shunt/0R measurement point; "
     "final peak/thermal validation is deferred to bench testing.",
     "resolved": True},
    {"id": "ANTENNA", "must_confirm": "CONSERVATIVE FREEZE: Wi-Fi/BT stays on the CM4 module/U.FL path; "
     "carrier does not add 2.4/5GHz RF routing. Layout must reserve the CM4 antenna keep-out and keep "
     "battery, metal hinge/screws, speaker magnet, and copper away from the antenna zone.",
     "resolved": True},
    {"id": "BOARD_OUTLINE", "must_confirm": "SOURCE GEOMETRY RESOLVED: CM4 module outline = "
     "40.02x54.98mm from official DXF; CM4/IO Board DXF, STEP, placement map and dimensions drawing "
     "are the mechanical inputs. OPEN: project must freeze board length/width/radius, USB-C/camera/"
     "battery/debug exit direction, mounting holes, and battery-vs-CM4 position.",
     "resolved": False},
    {"id": "B2B_CONNECTOR", "must_confirm": "SOURCE FILES RESOLVED: carrier receptacle "
     "DF40C-100DS-0.4V(51), module plug DF40C-100DP-0.4V(51), 1.5mm mated height. OPEN: build "
     "2-layer connector-only fit-check board and verify all three connectors press in together with "
     "no module lift/skew.",
     "resolved": False},
    {"id": "PINMUX", "must_confirm": "PDM/SAI/I2C/UART/GPIO conflict map + Device Tree",
     "resolved": True},   # done: this file is the conflict-free pinmux plan
]


if __name__ == "__main__":
    pins_by_conn: dict[str, list] = {}
    for row in ASSIGNMENTS:
        pins_by_conn.setdefault(row["connector"], []).append(row["pin"])
    # conflict check (ignore multi-pin/ALL_GND aggregate entries)
    for conn, pins in pins_by_conn.items():
        singles = [p for p in pins if isinstance(p, int)]
        dupes = {p for p in singles if singles.count(p) > 1}
        assert not dupes, f"Duplicate pin on {conn}: {dupes}"
    n_p0 = sum(1 for r in ASSIGNMENTS if r["priority"] == "P0")
    print(f"{len(ASSIGNMENTS)} rows ({n_p0} P0), no single-pin conflicts — OK")
