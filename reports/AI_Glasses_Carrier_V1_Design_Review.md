# AI Glasses Carrier V1 - PCB Design Review

- **Board:** ai_glasses_carrier_v1  |  **CM4 SKU:** RM126-D4E32J0R35W28 (RK3576, 4GB LPDDR4X, 32GB eMMC, Wi-Fi6+BT5.x)
- **Pin-assignment status:** `REVIEW` (verified vs official pinout; not yet FROZEN)
- **Generated:** 2026-06-30  (from working sources; see footer)
- **Components:** 102 (81 P0)  |  **Passive families:** 22 (LOCKED 11 / VERIFY 6 / TUNE 5)
- **ERC:** 0  |  **DRC:** 0 violations  |  **Footprints:** 101/102 real (1 VERIFY), 0 placed  |  **MPN set:** 27/102

> [!] **Stage:** schematic / pin-freeze. The PCB is intentionally an empty skeleton (outline + 6-layer stack + mounting holes + nets, **no footprints placed**). Per repo rule 7 this report makes **no** claim about layout/copper/clearance correctness - that is confirmed only in KiCad/3D after placement. Part values & specs are EVT candidates pending human review.

---
## 1. Project status

| Item | State |
|---|---|
| Pin assignment | [OK] 56 rows, all verified vs `radxa_cm4_pinout_v1.20.xlsx` |
| Freeze gate | [BLOCKED] `REVIEW` - blocked by 3 procurement/mechanical TBDs (not pins) |
| Schematic | [OK] element-level draft, net-connectivity verified |
| PCB layout | [ ] not started (skeleton only) |
| ERC / DRC | 0 / 0 violations (see §2/§3) |

## 2. Schematic status (ERC)

Schematic is generated from the BOM master (`scripts/carrier_bom.py`) as box symbols with global net labels; every net was checked with `kicad-cli sch export netlist`. The CM4 module is drawn as its three B2B connectors (J31=J3A, J32=J3B, J1) carrying the real CM4 pins.

**ERC: 0 errors, 0 warnings - clean** (`ai_context/erc.report.txt`: "ERC messages: 0  Errors 0  Warnings 0"). Confirms 102 symbols + 321 net labels with no unconnected-critical-pin, duplicate-net, or power-driver violations.

## 3. PCB status (DRC)

PCB = pre-layout skeleton: 70×55 mm outline (placeholder - carrier outline still a TBD), 6-layer stack (F.Cu / In1.GND / In2.PWR / In3.sig / In4.GND / B.Cu), 4× M2 mounting holes, declared nets, **no component footprints**. `Update PCB from Schematic` will populate it once footprints are assigned and the gate is FROZEN.

**DRC: 0 errors, 0 warnings** on the skeleton (`ai_context/drc.report.txt`). Meaningful DRC (clearances, diff-pair, copper) only applies after footprints are placed.

## 4. Footprint status

"Footprint" means three different things at three stages - they are NOT the same, and conflating them is what makes the status look contradictory:

| Layer | Meaning | Status |
|---|---|---|
| (1) Footprint field (pointer) | Each symbol names *which* footprint to use | **102/102** assigned |
| (2) Real footprint exists/usable | That name maps to a real KiCad library footprint | **101/102** real, **1** still `VERIFY` placeholder |
| (3) Placed on the PCB | Physical footprint dropped into `.kicad_pcb` | **0** (pre-layout skeleton) |

So: every symbol has a footprint *pointer* (needed for `Update PCB from Schematic`), **101** of those now point at real, datasheet-checked footprints from the installed KiCad 10 libraries (all passives + most connectors/ICs/test points), **1** are still placeholders, and **nothing is placed on the board yet**.

### 4.1 The 1 remaining placeholders - proposed real footprints

Each was researched against the installed KiCad libraries / the part datasheet. `custom` = must be drawn in `AI_Glasses.pretty` (no stock footprint); `confirm` = std-lib family identified, verify exact pads/EP vs the ordered part.

| Ref | Part / package | Proposed footprint | Action |
|---|---|---|---|
| L1 | Boost inductor 4.7uH, >=10A sat | `Inductor_SMD: 4x4mm class per chosen part` | confirm |

> All parts now use **authoritative KiCad-library footprints**, including the TI-official land patterns for the small packages: B2B = `Connector_Hirose_DF40:Hirose_DF40C-100DS-0.4V_2x50_P0.4mm`, GNSS = `RF_GPS:ublox_MAX`, IMU = `Package_LGA:LGA-14_3x2.5mm`, TPD4E05U06 = `Package_SON:USON-10_2.5x1.0mm_P0.5mm`, TPS61022 = `Package_DFN_QFN:Texas_RWU0007A_VQFN-7_2x2mm`. A 1:1 print-and-verify fixture for the two small packages is in `hardware/confirm_fp_1to1_check.kicad_pcb` (PDF: `reports/output/Confirm_FP_1to1_Check.pdf`). The only remaining placeholder is **L1** (boost inductor) - its footprint is selected once the boost peak current sets the inductor part. The B2B footprint geometry is authoritative, but the locked 3-connector PLACEMENT still needs the mechanical fit-check (official CM4 STEP + 2-layer coupon, see §8).

## 5. Component list (by function)

### CM4 Module / B2B Connectors (3)

| Ref | Value | MPN | LCSC | Footprint | Function |
|---|---|---|---|---|---|
| J1 | DF40C-100DS-0.4V(51) | DF40C-100DS-0.4V(51) | - | `Connector_Hirose_DF40:Hirose_DF40C-100DS-0.4V_2x50_P0.4mm` | CM4 J1 (I/O): SAI1 audio, CSI3 camera MCLK, speaker enable |
| J31 | DF40C-100DS-0.4V(51) | DF40C-100DS-0.4V(51) | - | `Connector_Hirose_DF40:Hirose_DF40C-100DS-0.4V_2x50_P0.4mm` | CM4 J3A (low-speed): power, debug/GNSS UART, I2C, control GPIO |
| J32 | DF40C-100DS-0.4V(51) | DF40C-100DS-0.4V(51) | - | `Connector_Hirose_DF40:Hirose_DF40C-100DS-0.4V_2x50_P0.4mm` | CM4 J3B (high-speed): MIPI-CSI3 4-lane camera, USB2-OTG0, PDM1 mics |

### Camera (P0) (11)

| Ref | Value | MPN | LCSC | Footprint | Function |
|---|---|---|---|---|---|
| C8 | 10µF | - | - | `Capacitor_SMD:C_0805_2012Metric` | Camera +3V3 bulk decoupling |
| C9 | 1µF | - | - | `Capacitor_SMD:C_0603_1608Metric` | Camera +3V3 decoupling |
| C10 | 100nF | - | - | `Capacitor_SMD:C_0603_1608Metric` | Camera +3V3 HF decoupling |
| C29 | 10µF | - | - | `Capacitor_SMD:C_0805_2012Metric` | Camera +5V bulk decoupling for Radxa Camera 4K |
| C30 | 100nF | - | - | `Capacitor_SMD:C_0603_1608Metric` | Camera +5V HF decoupling for Radxa Camera 4K |
| J2 | FH35C-31S-0.3SHW(50) | FH35C-31S-0.3SHW(50) | C424662 | `AI_Glasses:FH35C-31S-0.3SHW_50` | Camera FPC - Radxa Camera 4K / Sony IMX415-AAQR-C, 31-pin 0.3mm, 4-lane MIPI |
| R7 | 2.2k | - | - | `Resistor_SMD:R_0603_1608Metric` | Camera I2C SCL pull-up to +1V8 (cam OVDD=1.8V confirmed) |
| R8 | 2.2k | - | - | `Resistor_SMD:R_0603_1608Metric` | Camera I2C SDA pull-up to +1V8 (cam OVDD=1.8V confirmed) |
| U2 | TPD4E05U06 | TPD4E05U06 | - | `Package_SON:USON-10_2.5x1.0mm_P0.5mm` | MIPI-CSI low-capacitance ESD array for CSI3 clock + data lanes 0/1 (<0.4pF/line) |
| U3 | LP5907-3.3 (low-noise LDO) | LP5907MFX-3.3 | - | `Package_TO_SOT_SMD:SOT-23-5` | Camera 3.3V low-noise supply for Radxa Camera 4K, EN-gated |
| U16 | TPD4E05U06 | TPD4E05U06 | - | `Package_SON:USON-10_2.5x1.0mm_P0.5mm` | MIPI-CSI low-capacitance ESD array for CSI3 data lanes 2/3 (<0.4pF/line) |

### Audio (P0) (9)

| Ref | Value | MPN | LCSC | Footprint | Function |
|---|---|---|---|---|---|
| C13 | 100nF | - | - | `Capacitor_SMD:C_0603_1608Metric` | Amp VDD decoupling |
| C23 | 1nF | - | - | `Capacitor_SMD:C_0603_1608Metric` | Class-D EMI cap (OUT+ to GND) |
| C24 | 1nF | - | - | `Capacitor_SMD:C_0603_1608Metric` | Class-D EMI cap (OUT- to GND) |
| FB1 | Ferrite 600ohm@100MHz | - | - | `Inductor_SMD:L_0603_1608Metric` | Class-D speaker EMI bead (OUT+) |
| FB2 | Ferrite 600ohm@100MHz | - | - | `Inductor_SMD:L_0603_1608Metric` | Class-D speaker EMI bead (OUT-) |
| J3 | JST-SH 2p (spkr) | SM02B-SRSS-TB | - | `Connector_JST:JST_SH_BM02B-SRSS-TB_1x02-1MP_P1.00mm_Vertical` | Speaker connector (post-EMI); 2 wire-leads |
| MK1 | SPH0641LU4H-1 | SPH0641LU4H-1 | - | `Sensor_Audio:Knowles_LGA-5_3.5x2.65mm` | PDM MEMS mic (L, SEL=GND) |
| MK2 | SPH0641LU4H-1 | SPH0641LU4H-1 | - | `Sensor_Audio:Knowles_LGA-5_3.5x2.65mm` | PDM MEMS mic (R, SEL=VDD) |
| U4 | MAX98357AETE+T | MAX98357AETE+T | C910544 | `Package_DFN_QFN:QFN-16-1EP_3x3mm_P0.5mm_EP1.45x1.45mm` | Class-D I2S/SAI mono amp (TQFN-16, no MCLK) |

### USB-C (P0) (8)

| Ref | Value | MPN | LCSC | Footprint | Function |
|---|---|---|---|---|---|
| C11 | 1µF | - | - | `Capacitor_SMD:C_0603_1608Metric` | VBUS input cap |
| D3 | SMAJ5.0A (TVS) | SMAJ5.0A | - | `Diode_SMD:D_SMA` | USB VBUS ESD/TVS clamp (5V standoff) |
| J4 | GCT USB4085 (USB2) | USB4085-GF-A | - | `Connector_USB:USB_C_Receptacle_GCT_USB4085` | USB-C receptacle (USB2 + 5V sink) |
| R1 | 5.1k | - | - | `Resistor_SMD:R_0603_1608Metric` | USB-C CC1 pull-down (Sink role) |
| R2 | 5.1k | - | - | `Resistor_SMD:R_0603_1608Metric` | USB-C CC2 pull-down (Sink role) |
| R3 | 0R / shunt | - | - | `Resistor_SMD:R_2512_6332Metric` | VBUS_PROT->5V series 0R/shunt (current log) |
| U5 | TPD2E009 | TPD2E009 | - | `Package_TO_SOT_SMD:SOT-553` | USB2 D+/D- ESD clamp |
| U15 | TPS25940 (e-fuse, opt) | TPS25940 | - | `Package_DFN_QFN:Texas_RGP0020H_VQFN-20-1EP_4x4mm_P0.5mm_EP2.4x2.4mm` | VBUS e-fuse: OVP/OCP/reverse-block (DNP-able; bypass via R3 if unused) |

### Power (P0) (10)

| Ref | Value | MPN | LCSC | Footprint | Function |
|---|---|---|---|---|---|
| C1 | 10µF | - | - | `Capacitor_SMD:C_0805_2012Metric` | +5V bulk decoupling |
| C2 | 100nF | - | - | `Capacitor_SMD:C_0603_1608Metric` | +5V HF decoupling |
| C3 | 10µF | - | - | `Capacitor_SMD:C_0805_2012Metric` | +3V3 bulk decoupling |
| C4 | 100nF | - | - | `Capacitor_SMD:C_0603_1608Metric` | +3V3 HF decoupling |
| C5 | 10µF | - | - | `Capacitor_SMD:C_0805_2012Metric` | +1V8 bulk decoupling |
| C6 | 100nF | - | - | `Capacitor_SMD:C_0603_1608Metric` | +1V8 HF decoupling |
| C21 | 100nF | - | - | `Capacitor_SMD:C_0603_1608Metric` | LDO U12 +3V3 output decoupling |
| C22 | 100nF | - | - | `Capacitor_SMD:C_0603_1608Metric` | LDO U13 +1V8 output decoupling |
| U12 | TLV75733 (LDO) | TLV75733 | - | `Package_TO_SOT_SMD:SOT-23-5` | 3.3V rail regulator |
| U13 | TLV75718 (LDO) | TLV75718 | - | `Package_TO_SOT_SMD:SOT-23-5` | 1.8V VCCIO rail regulator |

### Battery (P1) (14)

| Ref | Value | MPN | LCSC | Footprint | Function |
|---|---|---|---|---|---|
| C7 | 22µF | - | - | `Capacitor_SMD:C_0805_2012Metric` | +VBAT bulk decoupling |
| C17 | 100nF | - | - | `Capacitor_SMD:C_0603_1608Metric` | Charger U7 VBUS decoupling |
| C18 | 100nF | - | - | `Capacitor_SMD:C_0603_1608Metric` | Fuel gauge U9 VDD decoupling |
| C19 | 100nF | - | - | `Capacitor_SMD:C_0603_1608Metric` | Boost U6 VIN decoupling |
| J5 | JST-PH 3p | S3B-PH-SM4-TB | - | `Connector_JST:JST_PH_S3B-PH-SM4-TB_1x03-1MP_P2.00mm_Horizontal` | Battery connector (BAT+/BAT-/NTC) |
| L1 | 4.7µH | - | - | `AI_Glasses:POWER_INDUCTOR_7X7_VERIFY` | Boost inductor |
| R11 | 10k | - | - | `Resistor_SMD:R_0603_1608Metric` | Battery NTC bias (placeholder) |
| R12 | 2.2k | - | - | `Resistor_SMD:R_0603_1608Metric` | Charger/Fuel I2C6 SCL pull-up to +1V8 |
| R13 | 2.2k | - | - | `Resistor_SMD:R_0603_1608Metric` | Charger/Fuel I2C6 SDA pull-up to +1V8 |
| R20 | 100k | - | - | `Resistor_SMD:R_0603_1608Metric` | Boost EN pull-up to +VBAT; default boost enabled for bench bring-up |
| U6 | TPS61022 (Boost) | TPS61022 | - | `Package_DFN_QFN:Texas_RWU0007A_VQFN-7_2x2mm_P0.5mm` | 1S Li-Po -> 5V boost converter |
| U7 | BQ25180 | BQ25180 | - | `Package_BGA:Texas_DSBGA-12_1.36x1.86mm_Layout3x4_P0.5mm` | 1S Li-Po charger w/ power-path (I2C) |
| U8 | BQ29700 | BQ29700 | - | `Package_TO_SOT_SMD:SOT-23-5` | Single-cell battery protection (OVP/UVP/OCP) |
| U9 | MAX17048 | MAX17048 | - | `Package_DFN_QFN:DFN-8-1EP_2x3mm_P0.5mm_EP0.61x2.2mm` | I2C fuel gauge (SOC, low-batt IRQ) |

### IMU / Haptic (P1) (7)

| Ref | Value | MPN | LCSC | Footprint | Function |
|---|---|---|---|---|---|
| C16 | 100nF | - | - | `Capacitor_SMD:C_0603_1608Metric` | IMU U10 VDD decoupling |
| C20 | 100nF | - | - | `Capacitor_SMD:C_0603_1608Metric` | Haptic U11 VDD decoupling |
| J6 | JST-SH 2p | SM02B-SRSS-TB | - | `Connector_JST:JST_SH_BM02B-SRSS-TB_1x02-1MP_P1.00mm_Vertical` | Vibration motor connector |
| R9 | 2.2k | - | - | `Resistor_SMD:R_0603_1608Metric` | IMU I2C SCL pull-up to +1V8 |
| R10 | 2.2k | - | - | `Resistor_SMD:R_0603_1608Metric` | IMU I2C SDA pull-up to +1V8 |
| U10 | ICM-42688-P | ICM-42688-P | - | `Package_LGA:LGA-14_3x2.5mm_P0.5mm_LayoutBorder3x4y` | 6-axis IMU (accel+gyro, I2C) |
| U11 | DRV2605L | DRV2605L | - | `Package_SO:MSOP-10_3x3mm_P0.5mm` | LRA/ERM haptic driver |

### GNSS / Positioning (P0) (11)

| Ref | Value | MPN | LCSC | Footprint | Function |
|---|---|---|---|---|---|
| C14 | 100nF | - | - | `Capacitor_SMD:C_0603_1608Metric` | GNSS VCC decoupling |
| C15 | 10µF | - | - | `Capacitor_SMD:C_0805_2012Metric` | GNSS VCC bulk decoupling |
| C25 |  shunt (DNP,tune) | - | - | `Capacitor_SMD:C_0402_1005Metric` | GNSS -match shunt, module side (DNP) |
| C26 |  shunt (DNP,tune) | - | - | `Capacitor_SMD:C_0402_1005Metric` | GNSS -match shunt, antenna side (DNP) |
| C27 | DC-block (series,tune) | - | - | `Capacitor_SMD:C_0402_1005Metric` | GNSS RF series match / DC block |
| C28 | 100nF (active-ant) | - | - | `Capacitor_SMD:C_0603_1608Metric` | Antenna bias decoupling (DNP if passive) |
| D4 | ESD low-cap RF 0.3pF | - | - | `Diode_SMD:D_SOD-882` | GNSS antenna ESD clamp |
| J8 | U.FL / IPEX | U.FL-R-SMT-1 | - | `Connector_Coaxial:U.FL_Hirose_U.FL-R-SMT-1_Vertical` | GNSS antenna connector (50ohm; external active/passive) |
| L2 | RF choke (active-ant) | - | - | `Inductor_SMD:L_0402_1005Metric` | Bias-tee choke (DNP if passive antenna) |
| R17 | 10ohm (active-ant) | - | - | `Resistor_SMD:R_0603_1608Metric` | Active-antenna bias feed from +3V3 (DNP if passive) |
| U14 | MAX-M10S-00B-01 | MAX-M10S-00B-01 | - | `RF_GPS:ublox_MAX` | u-blox GNSS (GPS/GLO/GAL/BDS), UART, VIO=1.8V |

### Indicators / Debug (5)

| Ref | Value | MPN | LCSC | Footprint | Function |
|---|---|---|---|---|---|
| D1 | LED Green | - | - | `LED_SMD:LED_0603_1608Metric` | Power LED (active-low GPIO sink) |
| D2 | LED Blue | - | - | `LED_SMD:LED_0603_1608Metric` | Status LED (active-low GPIO sink) |
| J7 | Header 1x4 2.54mm | - | - | `Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical` | UART debug header (TX/RX/GND/VREF) |
| R4 | 1k | - | - | `Resistor_SMD:R_0603_1608Metric` | Power LED current limit |
| R5 | 1k | - | - | `Resistor_SMD:R_0603_1608Metric` | Status LED current limit |

### Test Points (16)

| Ref | Value | MPN | LCSC | Footprint | Function |
|---|---|---|---|---|---|
| TP1 | TestPoint 1.0mm | - | - | `TestPoint:TestPoint_Pad_D1.5mm` | Test point: VBAT |
| TP2 | TestPoint 1.0mm | - | - | `TestPoint:TestPoint_Pad_D1.5mm` | Test point: 5V |
| TP3 | TestPoint 1.0mm | - | - | `TestPoint:TestPoint_Pad_D1.5mm` | Test point: 3V3 |
| TP4 | TestPoint 1.0mm | - | - | `TestPoint:TestPoint_Pad_D1.5mm` | Test point: 1V8 |
| TP5 | TestPoint 1.0mm | - | - | `TestPoint:TestPoint_Pad_D1.5mm` | Test point: GND |
| TP6 | TestPoint 1.0mm | - | - | `TestPoint:TestPoint_Pad_D1.5mm` | Test point: UART_TX |
| TP7 | TestPoint 1.0mm | - | - | `TestPoint:TestPoint_Pad_D1.5mm` | Test point: UART_RX |
| TP8 | TestPoint 1.0mm | - | - | `TestPoint:TestPoint_Pad_D1.5mm` | Test point: CAM_SCL |
| TP9 | TestPoint 1.0mm | - | - | `TestPoint:TestPoint_Pad_D1.5mm` | Test point: CAM_SDA |
| TP10 | TestPoint 1.0mm | - | - | `TestPoint:TestPoint_Pad_D1.5mm` | Test point: IMU_SCL |
| TP11 | TestPoint 1.0mm | - | - | `TestPoint:TestPoint_Pad_D1.5mm` | Test point: IMU_SDA |
| TP12 | TestPoint 1.0mm | - | - | `TestPoint:TestPoint_Pad_D1.5mm` | Test point: FUEL_SCL |
| TP13 | TestPoint 1.0mm | - | - | `TestPoint:TestPoint_Pad_D1.5mm` | Test point: FUEL_SDA |
| TP14 | TestPoint 1.0mm | - | - | `TestPoint:TestPoint_Pad_D1.5mm` | Test point: RESET |
| TP15 | TestPoint 1.0mm | - | - | `TestPoint:TestPoint_Pad_D1.5mm` | Test point: RECOVERY |
| TP16 | TestPoint 1.0mm | - | - | `TestPoint:TestPoint_Pad_D1.5mm` | Test point: CAM_EN |

### Buttons (8)

| Ref | Value | MPN | LCSC | Footprint | Function |
|---|---|---|---|---|---|
| R14 | 10k | - | - | `Resistor_SMD:R_0603_1608Metric` | RECOVERY pull-up to +1V8 |
| R15 | 10k | - | - | `Resistor_SMD:R_0603_1608Metric` | RESET pull-up to +1V8 |
| R16 | 10k | - | - | `Resistor_SMD:R_0603_1608Metric` | POWER_KEY pull-up to +1V8 |
| R18 | 100k | - | - | `Resistor_SMD:R_0603_1608Metric` | WL_nDIS pull-up to +1V8; default Wi-Fi enabled |
| R19 | 100k | - | - | `Resistor_SMD:R_0603_1608Metric` | BT_nDIS pull-up to +1V8; default Bluetooth enabled |
| SW1 | Tact SW SMD | - | - | `Button_Switch_SMD:SW_Push_1P1T_NO_CK_KMR2` | RECOVERY / maskrom button (to GND) |
| SW2 | Tact SW SMD | - | - | `Button_Switch_SMD:SW_Push_1P1T_NO_CK_KMR2` | RESET button (to GND) |
| SW3 | Tact SW SMD | - | - | `Button_Switch_SMD:SW_Push_1P1T_NO_CK_KMR2` | POWER button (to GND) |

## 6. CM4 pin assignment (verified vs official pinout)

| Function | Signal | Conn | Pin | CM4 net | Voltage |
|---|---|---|---|---|---|
| Power | +5V_IN | J3A | 77 | 5V_DCIN | 5V |
| Power | +5V_IN | J3A | 79 | 5V_DCIN | 5V |
| Power | +5V_IN | J3A | 81 | 5V_DCIN | 5V |
| Power | +5V_IN | J3A | 83 | 5V_DCIN | 5V |
| Power | +5V_IN | J3A | 85 | 5V_DCIN | 5V |
| Power | +5V_IN | J3A | 87 | 5V_DCIN | 5V |
| Power | GND | J3A/J3B/J1 | ALL_GND | GND | GND |
| Power | +3V3_OUT(CM4) | J3A | 84,86 | VCCIO6 | 3.3V |
| Power | +1V8_OUT(CM4) | J3A | 88,90 | VCC_1V8_S0 | 1.8V |
| Power | GPIO_VREF | J3A | 78 | GPIO_VREF | set=1.8V |
| Camera | MIPI_DPHY_CSI3_RX_CLKP | J3B | 129 | MIPI_DPHY_CSI3_RX_CLKP | diff_1V8 (100ohm) |
| Camera | MIPI_DPHY_CSI3_RX_CLKN | J3B | 127 | MIPI_DPHY_CSI3_RX_CLKN | diff_1V8 (100ohm) |
| Camera | MIPI_DPHY_CSI3_RX_D0P | J3B | 117 | MIPI_DPHY_CSI3_RX_D0P | diff_1V8 (100ohm) |
| Camera | MIPI_DPHY_CSI3_RX_D0N | J3B | 115 | MIPI_DPHY_CSI3_RX_D0N | diff_1V8 (100ohm) |
| Camera | MIPI_DPHY_CSI3_RX_D1P | J3B | 123 | MIPI_DPHY_CSI3_RX_D1P | diff_1V8 (100ohm) |
| Camera | MIPI_DPHY_CSI3_RX_D1N | J3B | 121 | MIPI_DPHY_CSI3_RX_D1N | diff_1V8 (100ohm) |
| Camera | MIPI_DPHY_CSI3_RX_D2P | J3B | 135 | MIPI_DPHY_CSI3_RX_D2P | diff_1V8 (100ohm) |
| Camera | MIPI_DPHY_CSI3_RX_D2N | J3B | 133 | MIPI_DPHY_CSI3_RX_D2N | diff_1V8 (100ohm) |
| Camera | MIPI_DPHY_CSI3_RX_D3P | J3B | 141 | MIPI_DPHY_CSI3_RX_D3P | diff_1V8 (100ohm) |
| Camera | MIPI_DPHY_CSI3_RX_D3N | J3B | 139 | MIPI_DPHY_CSI3_RX_D3N | diff_1V8 (100ohm) |
| Camera | I2C_CAM_SCL | J3A | 80 | I2C0_SCL_M1_TP | 1.8V (PMUIO1) |
| Camera | I2C_CAM_SDA | J3A | 82 | I2C0_SDA_M1_TP | 1.8V (PMUIO1) |
| Camera | CAM_RST_n | J3B | 143 | MIPI_CAM3_PDN_1V8 | 1.8V |
| Camera | CAM_MCLK | J1 | 59 | MIPI_CSI3_CAM_CLKOUT_1V8 | 1.8V |
| PDM | PDM1_CLK1_M1 | J3B | 96 | PDM1_CLK1_M1 | 1.8V (VCCIO_AUDIO) |
| PDM | PDM1_SDI1_M1 | J3B | 94 | PDM1_SDI1_M1 | 1.8V (VCCIO_AUDIO) |
| PDM | PDM1_SDI2_M1 | J3B | 111 | PDM1_SDI2_M1 | 1.8V (VCCIO_AUDIO) |
| SAI | SAI1_SCLK | J1 | 25 | SAI1_SCLK_M0 | 1.8V (VCCIO_AUDIO) |
| SAI | SAI1_LRCK | J1 | 19 | SAI1_LRCK_M0 | 1.8V (VCCIO_AUDIO) |
| SAI | SAI1_SDO0 | J1 | 29 | SAI1_SDO0_M0 | 1.8V (VCCIO_AUDIO) |
| SAI | SAI1_MCLK | J1 | 23 | SAI1_MCLK_M0 | 1.8V (VCCIO_AUDIO) |
| Control | GPIO_SPKR_EN | J1 | 96 | SPK_CTL_H | 1.8V (VCCIO6) |
| USB | USB2_OTG0_DP | J3B | 105 | USB2_OTG0_DP | USB 3.3V analog (90ohm) |
| USB | USB2_OTG0_DM | J3B | 103 | USB2_OTG0_DM | USB 3.3V analog (90ohm) |
| UART | UART0_TX_M0_DEBUG | J3A | 55 | UART0_TX_M0_DEBUG | 1.8V (VCCIO6) |
| UART | UART0_RX_M0_DEBUG | J3A | 51 | UART0_RX_M0_DEBUG | 1.8V (VCCIO6) |
| GNSS | GNSS_UART_TX | J3A | 47 | UART7_TX_M0 | 1.8V (VCCIO6) |
| GNSS | GNSS_UART_RX | J3A | 45 | UART7_RX_M0 | 1.8V (VCCIO6) |
| GNSS | GNSS_PPS | J3A | 40 | SPI1_MISO_M0 | 1.8V (VCCIO6) |
| GNSS | GNSS_RST_n | J3A | 44 | SPI1_MOSI_M0 | 1.8V (VCCIO6) |
| Control | RECOVERY_n | J3A | 93 | MASKROM | 1.8V |
| Control | RESET_n | J3A | 92 | RESET_L | 1.8V |
| Control | POWER_KEY | J3A | 99 | PWRON_L | 1.8V |
| Control | WL_nDIS | J3A | 89 | WL_NDIS | 1.8V |
| Control | BT_nDIS | J3A | 91 | BT_NDIS | 1.8V |
| Control | LED_PWR_n | J3A | 95 | NPWR_LED | 1.8V (VCCIO6) |
| Control | LED_STATUS_n | J3A | 21 | PI_NLED_ACTIVITY | 1.8V (VCCIO6) |
| I2C | I2C_IMU_SCL | J3A | 56 | I2C8_SCL_M1 | 1.8V (VCCIO6) |
| I2C | I2C_IMU_SDA | J3A | 58 | I2C8_SDA_M1 | 1.8V (VCCIO6) |
| Control | IMU_INT1 | J3A | 30 | GPIO1_C1 | 1.8V (VCCIO6) |
| Control | VIB_PWM | J3A | 48 | PWM1_CH0_M2 | 1.8V (VCCIO6) |
| Control | VIB_EN | J3A | 34 | CAN1_TX_M3 | 1.8V (VCCIO6) |
| I2C | FUEL_I2C_SCL | J3A | 35 | I2C6_SCL_M3 | 1.8V (VCCIO6) |
| I2C | FUEL_I2C_SDA | J3A | 36 | I2C6_SDA_M3 | 1.8V (VCCIO6) |
| Control | CHG_INT_n | J3A | 37 | SPI1_CSN1_M0 | 1.8V (VCCIO6) |
| Control | LOW_BAT_INT_n | J3A | 39 | SPI1_CSN0_M0 | 1.8V (VCCIO6) |

## 7. Passive component spec audit

Specs from `config/passive_bom_freeze.yaml`. **Verdict** checks good-practice compliance (MLCC voltage derating / DC-bias headroom, tolerance for critical positions). Status: LOCKED_CANDIDATE = ready for schematic-stage freeze (LCSC checked); PROCUREMENT_VERIFY = spec OK, confirm stock; TUNE_OR_EVT_SELECT = footprint/min-spec frozen, value/MPN by RF tuning or bench measurement.

### 7.1 Resistors - value, tolerance, package, tempco, power

| Refs | Value | Role | Tol | Package | Tempco | Power | Temp °C | MPN | LCSC | Status |
|---|---|---|---|---|---|---|---|---|---|---|
| R7, R8, R9, R10, R12, R13 | 2.2k | 1.8V I2C pull-up | 1% | 0603 / 1608 metric | 100 ppm/C | 0.1W | -55..155 | RC0603FR-072K2L | C4190 | LOCKED_CANDIDATE |
| R1, R2 | 5.1k | USB-C sink CC pull-down | 1% | 0603 / 1608 metric | 100 ppm/C | 0.1W | -55..155 | RC0603FR-075K1L | C23186 | LOCKED_CANDIDATE |
| R4, R5 | 1k | LED current limit | 1% | 0603 / 1608 metric | 100 ppm/C | 0.1W | -55..155 | RC0603FR-071KL | C21190 | LOCKED_CANDIDATE |
| R11, R14, R15, R16 | 10k | Reset/recovery/power pull-up and battery NTC placeholder bias | 1% | 0603 / 1608 metric | 100 ppm/C | 0.1W | -55..155 | RC0603FR-0710KL | C25804 | LOCKED_CANDIDATE |
| R18, R19, R20 | 100k | Wireless disable defaults and boost EN default | 1% | 0603 / 1608 metric | 100 ppm/C | 0.1W | -55..155 | RC0603FR-07100KL | C25803 | LOCKED_CANDIDATE |
| R17 | 10R | Active GNSS antenna bias feed, DNP if passive antenna | 1% | 0603 / 1608 metric | 100 ppm/C | 0.1W | -55..155 | RC0603FR-0710RL | C22859 | LOCKED_CANDIDATE |
| R3 | 0R / current shunt | Bring-up current measurement in +5V_SYS path | 1% if populated as shunt; jumper option allowed for no-measure builds | 2512 shunt footprint preferred; Kelvin sense pads recommended |  | 1.0W | -55..155 | TUNE_OR_EVT_SELECT | TUNE_OR_EVT_SELECT | TUNE_OR_EVT_SELECT |

**Resistor verdicts:**
- [OK] **R7, R8, R9, R10, R12, R13** (2.2k): I2C pull-up; 2.2k valid for ~100-400 pF bus at <=400 kHz - confirm vs actual bus capacitance after layout.
- [OK] **R1, R2** (5.1k): USB-C CC sink pull-down - 1% locked (correct per spec).
- [OK] **R4, R5** (1k): LED current-limit - 1% fine (5% also OK).
- [OK] **R11, R14, R15, R16** (10k): Reset/recovery/power pull-up and battery NTC placeholder bias - tolerance 1%.
- [OK] **R18, R19, R20** (100k): Wireless disable defaults and boost EN default - tolerance 1%.
- [OK] **R17** (10R): Active GNSS antenna bias feed, DNP if passive antenna - tolerance 1%.
- [!] **R3** (0R / current shunt): 0ohm/shunt in the 5V high-current path - do NOT use a tiny 0603; select a real mohm shunt (0.005-0.02ohm, 2512, Kelvin) or a 1% jumper.

### 7.2 Capacitors - value, voltage, dielectric, package, temp

| Refs | Value | Role | Dielectric | Voltage | Tol | Package | Temp °C | MPN | LCSC | Status |
|---|---|---|---|---|---|---|---|---|---|---|
| C2, C4, C6, C10, C13, C14, C16, C17, C18, C19, C20, C21, C22, C28, C30 | 100nF | Local HF decoupling and antenna-bias decoupling | X7R | 50V | 10% | 0603 / 1608 metric | -55..125 | CC0603KRX7R9BB104 | C14663 | LOCKED_CANDIDATE |
| C9, C11 | 1uF | Input/local decoupling | X7R | 16V | 10% | 0603 / 1608 metric | -55..125 | CL10B105KO8NNNC | C15849 | LOCKED_CANDIDATE |
| C1, C3, C5, C8, C15, C29 | 10uF | Rail bulk decoupling | X5R | 25V | 10% | 0805 / 2012 metric | -55..85 | CL21A106KAYNNNE | C15850 | LOCKED_CANDIDATE |
| C7 | 22uF | VBAT bulk decoupling | X5R | 25V | 20% | 0805 / 2012 metric | -55..85 | CL21A226MAQNNNE | C45783 | LOCKED_CANDIDATE |
| C23, C24 | 1nF | Class-D speaker EMI shunt | X7R | 50V | 10% | 0603 / 1608 metric | -55..125 | CC0603KRX7R9BB102 | C1669 | LOCKED_CANDIDATE |
| C27 | 100pF initial / tune | GNSS RF DC block or series match | C0G/NP0 | 25V(min) | 5% or better | 0402 / 1005 metric | -55..125 | TUNE_OR_EVT_SELECT | TUNE_OR_EVT_SELECT | TUNE_OR_EVT_SELECT |
| C25, C26 | DNP / tune | GNSS pi-match shunt pads | C0G/NP0 | 25V(min) | 5% or better | 0402 / 1005 metric | -55..125 | DNP_TUNE_KIT | DNP_TUNE_KIT | TUNE_OR_EVT_SELECT |

**Capacitor verdicts (DC-bias / derating vs rail):**
- **C2, C4, C6, C10, C13, C14, C16, C17, C18, C19, C20, C21, C22, C28, C30** (100nF, X7R): [OK] 50V on +5V_SYS (5.0V) -> 10.0× margin, good DC-bias headroom
- **C9, C11** (1uF, X7R): [OK] 16V on USB_VBUS (5.0V) -> 3.2× margin, good DC-bias headroom
- **C1, C3, C5, C8, C15, C29** (10uF, X5R): [OK] 25V on +5V_SYS (5.0V) -> 5.0× margin, good DC-bias headroom - bulk MLCC: confirm effective C after DC bias (consider 0805/larger).
- **C7** (22uF, X5R): [OK] 25V on +VBAT (4.2V) -> 6.0× margin, good DC-bias headroom - bulk MLCC: confirm effective C after DC bias (consider 0805/larger).
- **C23, C24** (1nF, X7R): [OK] spec OK (no power rail mapped / EMI position).
- **C27** (100pF initial / tune, C0G/NP0): [OK] RF/timing position - C0G/NP0, 25V min; value RF-tuned.
- **C25, C26** (DNP / tune, C0G/NP0): [OK] RF/timing position - C0G/NP0, 25V min; value RF-tuned.

### 7.3 Magnetics, protection, indicators

| Refs | Category | Value | Role | Package | Key ratings | MPN | LCSC | Status |
|---|---|---|---|---|---|---|---|---|
| L1 | inductor | 4.7uH | TPS61022-class 1S to 5V boost inductor | Shielded power inductor, about 7x7mm class | saturation_current_A_min=10; rms_current_A_min=6; dcr_mohm_max=25 | TUNE_OR_EVT_SELECT | TUNE_OR_EVT_SELECT | TUNE_OR_EVT_SELECT |
| FB1, FB2 | ferrite_bead | 600R@100MHz | Class-D speaker output EMI bead | 0603 / 1608 metric | impedance_ohm_at_100MHz=600; current_rating_A_min=1 | BLM18AG601SN1D | PROCUREMENT_VERIFY | PROCUREMENT_VERIFY |
| L2 | rf_inductor | RF choke / active antenna bias | GNSS active antenna bias tee, DNP if passive antenna | 0402 / 1005 metric | inductance_initial=47nH initial / tune; q_requirement=High-Q at GNSS L1 | TUNE_OR_EVT_SELECT | TUNE_OR_EVT_SELECT | TUNE_OR_EVT_SELECT |
| D3 | tvs | SMAJ5.0A | USB VBUS surge/ESD clamp | SMA / DO-214AC | peak_pulse_power_W_min=400; vrwm_V=5 | SMAJ5.0A | PROCUREMENT_VERIFY | PROCUREMENT_VERIFY |
| D4 | esd | low-cap RF ESD, <=0.3pF | GNSS antenna RF ESD clamp | SOD-882 (DFN1006-2) low-cap RF ESD | vrwm_V_min=5; capacitance_pF_max=0.3 | PROCUREMENT_VERIFY_LOW_CAP_RF_ESD | PROCUREMENT_VERIFY | PROCUREMENT_VERIFY |
| U2, U16 | esd_array | TPD4E05U06 | MIPI CSI3 low-capacitance ESD arrays | USON-10 (DQA) 2.5x1.0mm, 0.5mm pitch (TI DQA0010A) | vrwm_V_min=5; capacitance_pF_max=0.4; channels=4 | TPD4E05U06 | PROCUREMENT_VERIFY | PROCUREMENT_VERIFY |
| U5 | esd_array | TPD2E009 | USB2 D+/D- ESD clamp | SOT-553 (DRL); confirm pad map vs symbol when real symbol added | vrwm_V_min=5; capacitance_pF_max=1.5; channels=2 | TPD2E009 | PROCUREMENT_VERIFY | PROCUREMENT_VERIFY |
| D1, D2 | led | 0603 LED, green/blue | Power/status indicators | 0603 / 1608 metric | current_mA_nominal=1 | PROCUREMENT_VERIFY_LED_COLOR | PROCUREMENT_VERIFY | PROCUREMENT_VERIFY |

## 8. What's missing - open TBDs (freeze gate, §8.3)

| ID | Resolved | Must confirm |
|---|---|---|
| `CM4_SKU` | [OK] | CONFIRMED RM126-D4E32J0R35W28: RK3576 / 4GB LPDDR4X / 32GB eMMC / Wi-Fi6+BT5.x. Antenna form tracked under ANTENNA. |
| `CAMERA_ELECTRICAL_PINOUT` | [OK] | RESOLVED: camera module is Radxa Camera 4K / Sony IMX415-AAQR-C; 31-pin FPC pinout captured in CM4_IMX415_design_files/Radxa_Camera_4K_31pin_pinout.csv and cross-referenced in docs/p0_p1_decisions_2026-06-28.md. |
| `CAMERA_CONNECTOR_MPN` | [OK] | RESOLVED: carrier J2 connector is Hirose FH35C-31S-0.3SHW(50), LCSC C424662. Footprint has been generated from the Hirose 2D drawing. |
| `CAMERA_CABLE` | [OK] | RESOLVED: use Radxa AC006, 31P 0.3mm to 31P 0.3mm, opposite-side FPC. Do not use AC008; AC008 is 31P to 15P. |
| `CAMERA_SCHEMATIC_GATE` | [OK] | RESOLVED for schematic stage: J2 pins 1-31, CSI3 4-lane mapping, P/N polarity, I2C/MCLK/RESET, voltage domains, power pins and NC pins are checked by scripts/audit_csi3_camera.py. RESET is active-low on project net CAM_RST_n; no PWDN pin is present in the Radxa Camera 4K 31-pin pinout. |
| `CAMERA_KICAD_IMPLEMENTATION` | [X] | PARTIAL: schematic source now uses 31-pin FH35C/Radxa Cam4K pinout on CM4 CSI3 4-lane, and the FH35C footprint has been regenerated from the Hirose 2D drawing. DEFERRED_TO_PRE_LAYOUT: AC006 physical validation, FPC contact side, FPC insertion direction, J2 Pin 1 physical check, 1:1 print, coupon test, and FPC bend/enclosure path. Official CM4 IO overlay radxa-cm4-io-radxa-camera-4k.dtbo is confirmed. Bring-up logs (dmesg/media/v4l2) remain open for EVT. |
| `AUDIO_PARTS` | [OK] | CONFIRMED: 2×SPH0641LU4H-1 mic, MAX98357AETE+T (C910544) amp, Ole Wolff OWS-091630W50A-8 8ohm/1W (C5840086) speaker |
| `GNSS_MODULE` | [OK] | CONFIRMED u-blox MAX-M10S-00B-01: UART, VCC=3.3V/VIO=1.8V, 50ohm U.FL, external active antenna (-match + bias-tee, DNP for passive) |
| `BATTERY` | [OK] | Reverse-calc: 1S 2-3×(35×18×4mm ~250mAh)=500-750mAh/1.85-2.8Wh. V1 bench use ~1.5-2Ah. >3-4h target needs AI duty-cycling (system-power issue, see report) |
| `POWER_5V` | [OK] | CONSERVATIVE FREEZE: keep TPS61022-class 1S->5V boost and design +5V_SYS for >=4A bench/boost margin. R3 remains the bring-up shunt/0R measurement point; final peak/thermal validation is deferred to bench testing. |
| `ANTENNA` | [OK] | CONSERVATIVE FREEZE: Wi-Fi/BT stays on the CM4 module/U.FL path; carrier does not add 2.4/5GHz RF routing. Layout must reserve the CM4 antenna keep-out and keep battery, metal hinge/screws, speaker magnet, and copper away from the antenna zone. |
| `BOARD_OUTLINE` | [X] | SOURCE GEOMETRY RESOLVED: CM4 module outline = 40.02x54.98mm from official DXF; CM4/IO Board DXF, STEP, placement map and dimensions drawing are the mechanical inputs. OPEN: project must freeze board length/width/radius, USB-C/camera/battery/debug exit direction, mounting holes, and battery-vs-CM4 position. |
| `B2B_CONNECTOR` | [X] | SOURCE FILES RESOLVED: carrier receptacle DF40C-100DS-0.4V(51), module plug DF40C-100DP-0.4V(51), 1.5mm mated height. OPEN: build 2-layer connector-only fit-check board and verify all three connectors press in together with no module lift/skew. |
| `PINMUX` | [OK] | PDM/SAI/I2C/UART/GPIO conflict map + Device Tree |

Plus schematic-stage structural gaps: **no footprints placed on PCB** (skeleton), `VERIFY` placeholder footprints (§4), and the carrier board outline + B2B connector XY (needs official CM4 DXF/STEP aligned in KiCad).

## 9. Key recommendations

1. **USB-C CC (R1/R2, 5.1k):** locked at 1% [OK] - keep. Sink-role pull-downs to GND.
2. **I2C pull-ups (2.2k, R7-R13):** validate against measured bus capacitance after layout; 2.2k suits <=400 kHz / <=~400 pF. Camera I2C0, IMU I2C8, charger/fuel I2C6 are separate buses.
3. **5V-rail MLCC:** 10µF is 25V X5R / 1µF is 16V / 100nF is 50V -> all >=2× the 5V rail, good DC-bias margin. Still confirm **effective** capacitance of 10µF/0805 after DC bias on +5V_SYS.
4. **VBAT bulk (C7, 22µF/25V):** fine for 4.2V; high glasses-cell C-rate means keep/expand bulk near the boost input.
5. **R3 current shunt:** replace the 0ohm placeholder with a defined mohm shunt (2512, Kelvin) before measuring 5V power, or populate a 1% jumper for no-measure builds.
6. **GNSS RF (C25/C26/C27, L2):** C0G/NP0, values RF-tuned with the chosen antenna; C25/C26 stay DNP unless tuning needs shunt C; bias-tee (L2/R17/C28) DNP for a passive antenna.
7. **Boost inductor (L1):** select a >=10A-saturation shielded part sized to the measured 5V peak; footprint is a `VERIFY` placeholder.
8. **Replace all `VERIFY` footprints** (B2B, ESD arrays, RF ESD, inductor) with purchasable, library-verified footprints before layout.

---
## Appendix A - full pin -> net connections

| Ref | Pin | Net |
|---|---|---|
| J31 | P77-87 +5V | +5V_SYS |
| J31 | P78 VREF->1V8 | +1V8 |
| J31 | GND | GND |
| J31 | P55 DBG_TX | UART_DBG_TX |
| J31 | P51 DBG_RX | UART_DBG_RX |
| J31 | P47 GNSS_TX | GNSS_UART_TX |
| J31 | P45 GNSS_RX | GNSS_UART_RX |
| J31 | P40 GNSS_PPS | GNSS_PPS |
| J31 | P44 GNSS_RST | GNSS_RST_n |
| J31 | P80 CAM_SCL | CAM_I2C_SCL |
| J31 | P82 CAM_SDA | CAM_I2C_SDA |
| J31 | P56 IMU_SCL | IMU_I2C_SCL |
| J31 | P58 IMU_SDA | IMU_I2C_SDA |
| J31 | P35 FUEL_SCL | FUEL_I2C_SCL |
| J31 | P36 FUEL_SDA | FUEL_I2C_SDA |
| J31 | P30 IMU_INT | IMU_INT1 |
| J31 | P48 VIB_PWM | VIB_PWM |
| J31 | P34 VIB_EN | VIB_EN |
| J31 | P37 CHG_INT | CHG_INT_n |
| J31 | P39 LBAT_INT | LOW_BAT_INT_n |
| J31 | P95 LED_PWR | LED_PWR_n |
| J31 | P21 LED_STAT | LED_STATUS_n |
| J31 | P93 RECOVERY | RECOVERY_n |
| J31 | P92 RESET | RESET_n |
| J31 | P99 PWR_KEY | POWER_KEY |
| J31 | P89 WL_DIS | WL_nDIS |
| J31 | P91 BT_DIS | BT_nDIS |
| J32 | P129 CSI3_CLKP | MIPI_CSI3_CLK_P |
| J32 | P127 CSI3_CLKN | MIPI_CSI3_CLK_N |
| J32 | P117 CSI3_D0P | MIPI_CSI3_D0_P |
| J32 | P115 CSI3_D0N | MIPI_CSI3_D0_N |
| J32 | P123 CSI3_D1P | MIPI_CSI3_D1_P |
| J32 | P121 CSI3_D1N | MIPI_CSI3_D1_N |
| J32 | P135 CSI3_D2P | MIPI_CSI3_D2_P |
| J32 | P133 CSI3_D2N | MIPI_CSI3_D2_N |
| J32 | P141 CSI3_D3P | MIPI_CSI3_D3_P |
| J32 | P139 CSI3_D3N | MIPI_CSI3_D3_N |
| J32 | P143 CAM3_GPIO | CAM_RST_n |
| J32 | P105 USB_DP | USB_DP |
| J32 | P103 USB_DM | USB_DM |
| J32 | P96 PDM_CLK | PDM1_CLK |
| J32 | P94 PDM_D0 | PDM1_DATA0 |
| J32 | P111 PDM_D1 | PDM1_DATA1 |
| J32 | GND | GND |
| J1 | P25 SAI_BCLK | SAI1_BCLK |
| J1 | P19 SAI_LRCK | SAI1_LRCK |
| J1 | P29 SAI_SDO | SAI1_SDO |
| J1 | P23 SAI_MCLK_UNUSED | NC |
| J1 | P59 CAM3_MCLK | CAM_MCLK |
| J1 | P96 SPK_EN | SPKR_EN_n |
| J1 | +1V8 (P88/90) | +1V8 |
| J1 | GND | GND |
| J2 | 1 GND | GND |
| J2 | 2 MDN4 | MIPI_CSI3_D3_N |
| J2 | 3 MDP4 | MIPI_CSI3_D3_P |
| J2 | 4 GND | GND |
| J2 | 5 MDN3 | MIPI_CSI3_D2_N |
| J2 | 6 MDP3 | MIPI_CSI3_D2_P |
| J2 | 7 GND | GND |
| J2 | 8 NC | NC |
| J2 | 9 NC | NC |
| J2 | 10 GND | GND |
| J2 | 11 MDN2 | MIPI_CSI3_D1_N |
| J2 | 12 MDP2 | MIPI_CSI3_D1_P |
| J2 | 13 GND | GND |
| J2 | 14 MDN1 | MIPI_CSI3_D0_N |
| J2 | 15 MDP1 | MIPI_CSI3_D0_P |
| J2 | 16 GND | GND |
| J2 | 17 MCN | MIPI_CSI3_CLK_N |
| J2 | 18 MCP | MIPI_CSI3_CLK_P |
| J2 | 19 GND | GND |
| J2 | 20 MCLK | CAM_MCLK |
| J2 | 21 GND | GND |
| J2 | 22 NC | NC |
| J2 | 23 NC | NC |
| J2 | 24 SCL | CAM_I2C_SCL |
| J2 | 25 SDA | CAM_I2C_SDA |
| J2 | 26 NC | NC |
| J2 | 27 RESET_N | CAM_RST_n |
| J2 | 28 VCC3.3V | +CAM_3V3 |
| J2 | 29 VCC3.3V | +CAM_3V3 |
| J2 | 30 VCC5V | +5V_SYS |
| J2 | 31 VCC5V | +5V_SYS |
| U2 | CLK_P | MIPI_CSI3_CLK_P |
| U2 | CLK_N | MIPI_CSI3_CLK_N |
| U2 | D0_P | MIPI_CSI3_D0_P |
| U2 | D0_N | MIPI_CSI3_D0_N |
| U2 | D1_P | MIPI_CSI3_D1_P |
| U2 | D1_N | MIPI_CSI3_D1_N |
| U2 | GND | GND |
| U16 | D2_P | MIPI_CSI3_D2_P |
| U16 | D2_N | MIPI_CSI3_D2_N |
| U16 | D3_P | MIPI_CSI3_D3_P |
| U16 | D3_N | MIPI_CSI3_D3_N |
| U16 | GND | GND |
| U3 | VIN | +5V_SYS |
| U3 | EN | CAM_PWR_EN |
| U3 | GND | GND |
| U3 | VOUT | +CAM_3V3 |
| R7 | 1 | +1V8 |
| R7 | 2 | CAM_I2C_SCL |
| R8 | 1 | +1V8 |
| R8 | 2 | CAM_I2C_SDA |
| C8 | 1 | +CAM_3V3 |
| C8 | 2 | GND |
| C9 | 1 | +CAM_3V3 |
| C9 | 2 | GND |
| C10 | 1 | +CAM_3V3 |
| C10 | 2 | GND |
| C29 | 1 | +5V_SYS |
| C29 | 2 | GND |
| C30 | 1 | +5V_SYS |
| C30 | 2 | GND |
| MK1 | VDD | +1V8 |
| MK1 | CLK | PDM1_CLK |
| MK1 | DATA | PDM1_DATA0 |
| MK1 | SEL | GND |
| MK1 | GND | GND |
| MK2 | VDD | +1V8 |
| MK2 | CLK | PDM1_CLK |
| MK2 | DATA | PDM1_DATA1 |
| MK2 | SEL | +1V8 |
| MK2 | GND | GND |
| U4 | VDD | +5V_SYS |
| U4 | GND | GND |
| U4 | BCLK | SAI1_BCLK |
| U4 | LRC | SAI1_LRCK |
| U4 | DIN | SAI1_SDO |
| U4 | SD | SPKR_EN_n |
| U4 | GAIN | GND |
| U4 | OUT+ | SPK_OUT_P |
| U4 | OUT- | SPK_OUT_N |
| FB1 | 1 | SPK_OUT_P |
| FB1 | 2 | SPK_P_F |
| FB2 | 1 | SPK_OUT_N |
| FB2 | 2 | SPK_N_F |
| C23 | 1 | SPK_P_F |
| C23 | 2 | GND |
| C24 | 1 | SPK_N_F |
| C24 | 2 | GND |
| J3 | SPK+ | SPK_P_F |
| J3 | SPK- | SPK_N_F |
| C13 | 1 | +5V_SYS |
| C13 | 2 | GND |
| J4 | VBUS | USB_VBUS |
| J4 | GND | GND |
| J4 | DP | USB_DP |
| J4 | DM | USB_DM |
| J4 | CC1 | USB_CC1 |
| J4 | CC2 | USB_CC2 |
| J4 | SHLD | GND |
| U5 | DP | USB_DP |
| U5 | DM | USB_DM |
| U5 | GND | GND |
| R1 | 1 | USB_CC1 |
| R1 | 2 | GND |
| R2 | 1 | USB_CC2 |
| R2 | 2 | GND |
| D3 | 1 | USB_VBUS |
| D3 | 2 | GND |
| U15 | IN | USB_VBUS |
| U15 | EN | USB_VBUS |
| U15 | GND | GND |
| U15 | OUT | VBUS_PROT |
| R3 | 1 | VBUS_PROT |
| R3 | 2 | +5V_SYS |
| C11 | 1 | USB_VBUS |
| C11 | 2 | GND |
| U12 | VIN | +5V_SYS |
| U12 | GND | GND |
| U12 | VOUT | +3V3 |
| U13 | VIN | +3V3 |
| U13 | GND | GND |
| U13 | VOUT | +1V8 |
| C1 | 1 | +5V_SYS |
| C1 | 2 | GND |
| C2 | 1 | +5V_SYS |
| C2 | 2 | GND |
| C3 | 1 | +3V3 |
| C3 | 2 | GND |
| C4 | 1 | +3V3 |
| C4 | 2 | GND |
| C5 | 1 | +1V8 |
| C5 | 2 | GND |
| C6 | 1 | +1V8 |
| C6 | 2 | GND |
| U6 | VIN | +VBAT |
| U6 | SW | BOOST_SW |
| U6 | EN | BOOST_EN |
| U6 | FB | +5V_SYS |
| U6 | GND | GND |
| R20 | 1 | +VBAT |
| R20 | 2 | BOOST_EN |
| L1 | 1 | +VBAT |
| L1 | 2 | BOOST_SW |
| U7 | IN | USB_VBUS |
| U7 | SYS | +VBAT |
| U7 | BAT | VBAT_P |
| U7 | TS | BAT_NTC |
| U7 | SCL | FUEL_I2C_SCL |
| U7 | SDA | FUEL_I2C_SDA |
| U7 | INT | CHG_INT_n |
| U7 | GND | GND |
| U8 | VDD | VBAT_P |
| U8 | VM | VBAT_N |
| U8 | OUT | +VBAT |
| U9 | VDD | +VBAT |
| U9 | CELL | +VBAT |
| U9 | SCL | FUEL_I2C_SCL |
| U9 | SDA | FUEL_I2C_SDA |
| U9 | ALRT | LOW_BAT_INT_n |
| U9 | GND | GND |
| J5 | BAT+ | VBAT_P |
| J5 | BAT- | VBAT_N |
| J5 | NTC | BAT_NTC |
| C7 | 1 | +VBAT |
| C7 | 2 | GND |
| R11 | 1 | BAT_NTC |
| R11 | 2 | GND |
| U10 | VDD | +1V8 |
| U10 | GND | GND |
| U10 | SCL | IMU_I2C_SCL |
| U10 | SDA | IMU_I2C_SDA |
| U10 | INT1 | IMU_INT1 |
| R9 | 1 | +1V8 |
| R9 | 2 | IMU_I2C_SCL |
| R10 | 1 | +1V8 |
| R10 | 2 | IMU_I2C_SDA |
| U11 | VDD | +5V_SYS |
| U11 | GND | GND |
| U11 | IN | VIB_PWM |
| U11 | EN | VIB_EN |
| U11 | OUT+ | VIB_OUT_P |
| U11 | OUT- | VIB_OUT_N |
| J6 | M+ | VIB_OUT_P |
| J6 | M- | VIB_OUT_N |
| U14 | VCC | +3V3 |
| U14 | V_IO | +1V8 |
| U14 | V_BCKP | +3V3 |
| U14 | GND | GND |
| U14 | TXD | GNSS_UART_RX |
| U14 | RXD | GNSS_UART_TX |
| U14 | TIMEPULSE | GNSS_PPS |
| U14 | RESET_N | GNSS_RST_n |
| U14 | RF_IN | GNSS_RFIN |
| C27 | 1 | GNSS_RFIN |
| C27 | 2 | GNSS_ANT |
| C25 | 1 | GNSS_RFIN |
| C25 | 2 | GND |
| C26 | 1 | GNSS_ANT |
| C26 | 2 | GND |
| L2 | 1 | GNSS_ANT |
| L2 | 2 | V_ANT_BIAS |
| R17 | 1 | +3V3 |
| R17 | 2 | V_ANT_BIAS |
| C28 | 1 | V_ANT_BIAS |
| C28 | 2 | GND |
| J8 | ANT | GNSS_ANT |
| J8 | GND | GND |
| C14 | 1 | +3V3 |
| C14 | 2 | GND |
| C15 | 1 | +3V3 |
| C15 | 2 | GND |
| D1 | A | LED_PWR_A |
| D1 | K | LED_PWR_n |
| R4 | 1 | +3V3 |
| R4 | 2 | LED_PWR_A |
| D2 | A | LED_STAT_A |
| D2 | K | LED_STATUS_n |
| R5 | 1 | +3V3 |
| R5 | 2 | LED_STAT_A |
| J7 | TX | UART_DBG_TX |
| J7 | RX | UART_DBG_RX |
| J7 | GND | GND |
| J7 | VREF | +3V3 |
| TP1 | 1 | +VBAT |
| TP2 | 1 | +5V_SYS |
| TP3 | 1 | +3V3 |
| TP4 | 1 | +1V8 |
| TP5 | 1 | GND |
| TP6 | 1 | UART_DBG_TX |
| TP7 | 1 | UART_DBG_RX |
| TP8 | 1 | CAM_I2C_SCL |
| TP9 | 1 | CAM_I2C_SDA |
| TP10 | 1 | IMU_I2C_SCL |
| TP11 | 1 | IMU_I2C_SDA |
| TP12 | 1 | FUEL_I2C_SCL |
| TP13 | 1 | FUEL_I2C_SDA |
| TP14 | 1 | RESET_n |
| TP15 | 1 | RECOVERY_n |
| TP16 | 1 | CAM_PWR_EN |
| SW1 | 1 | RECOVERY_n |
| SW1 | 2 | GND |
| SW2 | 1 | RESET_n |
| SW2 | 2 | GND |
| SW3 | 1 | POWER_KEY |
| SW3 | 2 | GND |
| R14 | 1 | +1V8 |
| R14 | 2 | RECOVERY_n |
| R15 | 1 | +1V8 |
| R15 | 2 | RESET_n |
| R16 | 1 | +1V8 |
| R16 | 2 | POWER_KEY |
| R18 | 1 | +1V8 |
| R18 | 2 | WL_nDIS |
| R19 | 1 | +1V8 |
| R19 | 2 | BT_nDIS |
| R12 | 1 | +1V8 |
| R12 | 2 | FUEL_I2C_SCL |
| R13 | 1 | +1V8 |
| R13 | 2 | FUEL_I2C_SDA |
| C16 | 1 | +1V8 |
| C16 | 2 | GND |
| C17 | 1 | USB_VBUS |
| C17 | 2 | GND |
| C18 | 1 | +VBAT |
| C18 | 2 | GND |
| C19 | 1 | +VBAT |
| C19 | 2 | GND |
| C20 | 1 | +5V_SYS |
| C20 | 2 | GND |
| C21 | 1 | +3V3 |
| C21 | 2 | GND |
| C22 | 1 | +1V8 |
| C22 | 2 | GND |
| D4 | 1 | GNSS_ANT |
| D4 | 2 | GND |

---
_Generated by `scripts/generate_design_review.py` from working sources (`carrier_bom.py`, `cm4_pinmap.py`, `config/passive_bom_freeze.yaml`, `ai_context/*.json`). Native KiCad/XLSX remain the source of truth (repo CLAUDE.md)._
