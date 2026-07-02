# AI Glasses Carrier V1 - Parts Specification

- **Generated:** 2026-06-30  |  **Board:** ai_glasses_carrier_v1
- **Scope:** key devices with manufacturer part number + headline datasheet parameters, by subsystem (compute + Wi-Fi/BT, camera, audio + speaker, GNSS, sensors, power, battery, USB-C, protection, connectors).
- MPN + footprint are pulled live from the BOM (`scripts/carrier_bom.py`); the electrical/mechanical specs are curated from the manufacturer datasheets.

> [!] **Headline figures only.** Verify exact numbers and the full orderable suffix (reel/package/grade) against the latest manufacturer datasheet before procurement. Wi-Fi/Bluetooth are integrated in the CM4 SKU (this is a SoM carrier, not chip-down).

---
## 1. Compute module + wireless (Wi-Fi / Bluetooth)

The SoC, RAM, eMMC and the Wi-Fi/BT radio all live ON the Radxa CM4 module (this is a SoM carrier, not chip-down). They reach the carrier only through the three DF40 B2B connectors. Bluetooth/Wi-Fi are therefore part of the CM4 SKU, not separate carrier components.

| Ref | Part / MPN | Mfr | Package | Key parameters | Interface / Rail |
|---|---|---|---|---|---|
| - | Radxa CM4 (RM126-D4E32J0R35W28) | Radxa | SoM, 3x 100-pin DF40 B2B | SoC Rockchip RK3576 (4x Cortex-A72 + 4x A53, NPU ~6 TOPS); RAM 4GB LPDDR4X; eMMC 32GB; supply 5V DCIN; GPIO bank 1.8V (GPIO_VREF) | B2B J31/J32/J1 |
| - | Wi-Fi (on CM4 module) | on-module | in CM4 SKU | 802.11ax (Wi-Fi 6), 2.4 + 5 GHz; antenna on-module / per SKU | SDIO/PCIe in CM4 |
| - | Bluetooth (on CM4 module) | on-module | in CM4 SKU | Bluetooth 5.x (BLE + classic); shares CM4 wireless front-end; antenna per SKU | UART/PCM in CM4 |

## 2. Camera

Sony IMX415 (Radxa Camera 4K) on CM4 CSI3, 4-lane MIPI, via a 31-pin 0.3mm FFC.

| Ref | Part / MPN | Mfr | Package | Key parameters | Interface / Rail |
|---|---|---|---|---|---|
| - | IMX415-AAQR-C (Radxa Camera 4K) | Sony | module (off-board, via J2 FFC) | 1/2.8in 8.29 MP (3864x2192) CMOS; 4-lane MIPI CSI-2; up to 90 fps; rails IO 1.8V / analog 2.9V / core 1.1V (on module); I2C control | CSI3 4-lane, I2C0 |
| J2 | FH35C-31S-0.3SHW(50) | Hirose | `AI_Glasses:FH35C-31S-0.3SHW_50` | 31-pos 0.3mm-pitch FFC/FPC connector, bottom-contact; camera flex | CSI3 FFC |

## 3. Audio (amplifier, microphones, speaker)

Class-D speaker path + dual PDM MEMS mics. Speaker is off-board via J3.

| Ref | Part / MPN | Mfr | Package | Key parameters | Interface / Rail |
|---|---|---|---|---|---|
| U4 | MAX98357AETE+T | Analog Devices (Maxim) | `Package_DFN_QFN:QFN-16-1EP_3x3mm_P0.5mm_EP1.45x1.45mm` | Mono class-D amp; I2S/SAI (Left/Right/(L+R)/2); ~3.2W into 4ohm @5V (~92% eff); no MCLK needed; gain 3/6/9/12/15 dB; supply 2.5-5.5V | SAI1 (BCLK/LRCK/DIN) |
| MK1 | SPH0641LU4H-1 | Knowles | `Sensor_Audio:Knowles_LGA-5_3.5x2.65mm` | PDM digital MEMS mic, bottom port; SNR 64.3 dB(A); AOP 120 dBSPL; sens -26 dBFS; supply 1.6-3.6V; ultrasonic-capable | PDM1 (L, SEL=GND) |
| MK2 | SPH0641LU4H-1 | Knowles | `Sensor_Audio:Knowles_LGA-5_3.5x2.65mm` | Same as MK1; right channel | PDM1 (R, SEL=VDD) |
| - | OWS-091630W50A-8 (speaker) | OWS / generic | 9x16x3.0 mm (off-board via J3) | 8 ohm; rated ~1 W (peak higher); micro rectangular speaker; SPL/Fo per datasheet | amp OUT+/OUT- (post FB1/FB2) |
| FB1 | Ferrite 600ohm@100MHz | Murata/TDK class | `Inductor_SMD:L_0603_1608Metric` | Class-D EMI bead on OUT+; with C23 1nF | speaker EMI |
| FB2 | Ferrite 600ohm@100MHz | Murata/TDK class | `Inductor_SMD:L_0603_1608Metric` | Class-D EMI bead on OUT-; with C24 1nF | speaker EMI |

## 4. GNSS (positioning)

u-blox MAX-M10S over UART; external active antenna via U.FL.

| Ref | Part / MPN | Mfr | Package | Key parameters | Interface / Rail |
|---|---|---|---|---|---|
| U14 | MAX-M10S-00B-01 | u-blox | `RF_GPS:ublox_MAX` | GNSS receiver GPS/GLONASS/Galileo/BeiDou/QZSS; tracking sens -167 dBm; ~25 mA continuous; VCC 2.7-3.6V, VIO 1.8V; UART/I2C | UART7, U.FL (J8) |
| J8 | U.FL-R-SMT-1 | Hirose | `Connector_Coaxial:U.FL_Hirose_U.FL-R-SMT-1_Vertical` | 50 ohm U.FL/IPEX coax RF connector; external active GNSS antenna | RF 50 ohm |
| D4 | low-cap RF ESD (<=0.3pF) | TBD (Nexperia/Littelfuse class) | `Diode_SMD:D_SOD-882` | RF ESD clamp on antenna feed; capacitance <=0.3 pF; Vrwm >=5V | antenna ESD |

## 5. Sensors (IMU, haptics)

| Ref | Part / MPN | Mfr | Package | Key parameters | Interface / Rail |
|---|---|---|---|---|---|
| U10 | ICM-42688-P | TDK InvenSense | `Package_LGA:LGA-14_3x2.5mm_P0.5mm_LayoutBorder3x4y` | 6-axis IMU; accel +/-2/4/8/16 g; gyro up to +/-2000 dps; gyro noise ~2.8 mdps/rtHz; I2C/SPI; supply 1.71-3.6V | I2C8, INT1 |
| U11 | DRV2605L | Texas Instruments | `Package_SO:MSOP-10_3x3mm_P0.5mm` | Haptic driver for LRA/ERM; I2C; 123-effect waveform ROM (TI/Immersion); supply 2-5.2V | I2C + PWM (vib motor J6) |

## 6. Power (boost, charger, fuel gauge, protection, LDOs)

1S Li-Po -> 5V system via boost; per-rail LDOs; charge + gauge + cell protection.

| Ref | Part / MPN | Mfr | Package | Key parameters | Interface / Rail |
|---|---|---|---|---|---|
| U6 | TPS61022 | Texas Instruments | `Package_DFN_QFN:Texas_RWU0007A_VQFN-7_2x2mm_P0.5mm` | Sync boost; Vin 0.5-5.5V; Vout up to 5.5V; 8A switch; up to 96% eff; ~1 MHz | VBAT -> +5V_SYS |
| L1 | Boost inductor 4.7uH | TBD (Cyntec/Wurth class) | `AI_Glasses:POWER_INDUCTOR_7X7_VERIFY` | 4.7 uH; saturation >=10 A; low DCR; shielded; size per measured peak current | boost SW node |
| U7 | BQ25180 | Texas Instruments | `Package_BGA:Texas_DSBGA-12_1.36x1.86mm_Layout3x4_P0.5mm` | 1S Li-ion charger w/ power path; up to 1A charge; input 3.5-5.5V; I2C; ship mode | I2C6, USB-C 5V in |
| U8 | BQ29700 | Texas Instruments | `Package_TO_SOT_SMD:SOT-23-5` | Single-cell protection: OVP/UVP/OCP/SCP; ultra-low IQ | battery protection |
| U9 | MAX17048 | Analog Devices (Maxim) | `Package_DFN_QFN:DFN-8-1EP_2x3mm_P0.5mm_EP0.61x2.2mm` | ModelGauge fuel gauge (SOC); I2C; ~3 uA hibernate; low-batt alert | I2C6 |
| U3 | LP5907MFX-3.3 | Texas Instruments | `Package_TO_SOT_SMD:SOT-23-5` | 250 mA ultra-low-noise LDO; 6.5 uVrms; PSRR ~82 dB; -> camera 3.3V | +CAM_3V3 |
| U12 | TLV75733 | Texas Instruments | `Package_TO_SOT_SMD:SOT-23-5` | 1A LDO; low IQ; -> 3.3V system rail | +3V3 |
| U13 | TLV75718 | Texas Instruments | `Package_TO_SOT_SMD:SOT-23-5` | 1A LDO; low IQ; -> 1.8V VCCIO rail | +1V8 |
| U15 | TPS25940 | Texas Instruments | `Package_DFN_QFN:Texas_RGP0020H_VQFN-20-1EP_4x4mm_P0.5mm_EP2.4x2.4mm` | eFuse: OVP/OCP/reverse-block/inrush; Vin 2.7-18V; optional, DNP by default | VBUS in |

## 7. Battery

1S Li-Po. V1 bench cell locked; glasses build uses thin temple cells.

| Ref | Part / MPN | Mfr | Package | Key parameters | Interface / Rail |
|---|---|---|---|---|---|
| J5 | S3B-PH-SM4-TB | JST | `Connector_JST:JST_PH_S3B-PH-SM4-TB_1x03-1MP_P2.00mm_Horizontal` | Battery connector BAT+/BAT-/NTC; 2.0mm pitch | battery |
| - | V1 bench cell (103450) | generic 1S Li-Po | 10x34x50 mm | 1S 3.7V nominal; ~2000 mAh; with PCM; NTC recommended | via J5 |
| - | Glasses pack (target) | custom 1S | ~35x18x4 mm cells | 2-3 cells, ~250 mAh each (~500-750 mAh); >3-4h needs AI duty-cycling | via J5 |

## 8. USB-C + protection

| Ref | Part / MPN | Mfr | Package | Key parameters | Interface / Rail |
|---|---|---|---|---|---|
| J4 | USB4085-GF-A | GCT | `Connector_USB:USB_C_Receptacle_GCT_USB4085` | USB-C receptacle; USB2 + 5V sink; 16-pos | USB2, 5V in |
| U5 | TPD2E009 | Texas Instruments | `Package_TO_SOT_SMD:SOT-553` | 2-ch ESD clamp for USB2 D+/D-; low cap ~1.5 pF; Vrwm >=5V | USB D+/D- |
| D3 | SMAJ5.0A | Littelfuse/Bourns class | `Diode_SMD:D_SMA` | Uni TVS for VBUS; 5V standoff; 400W peak pulse | VBUS surge/ESD |
| R1 | 5.1k 1% | Yageo class | `Resistor_SMD:R_0603_1608Metric` | USB-C CC1 sink pull-down (locked 1%) | CC1 |
| R2 | 5.1k 1% | Yageo class | `Resistor_SMD:R_0603_1608Metric` | USB-C CC2 sink pull-down (locked 1%) | CC2 |

## 9. MIPI / camera ESD

| Ref | Part / MPN | Mfr | Package | Key parameters | Interface / Rail |
|---|---|---|---|---|---|
| U2 | TPD4E05U06 | Texas Instruments | `Package_SON:USON-10_2.5x1.0mm_P0.5mm` | 4-ch ultra-low-cap (0.4 pF) ESD array for MIPI CSI lanes; Vrwm >=5V | CSI3 lanes |
| U16 | TPD4E05U06 | Texas Instruments | `Package_SON:USON-10_2.5x1.0mm_P0.5mm` | Second 4-ch low-cap ESD array (remaining CSI lanes) | CSI3 lanes |

## 10. CM4 board-to-board connectors

Carrier-side receptacles; mate the CM4's DF40C-100DP plugs; 1.5mm board gap. Footprint geometry is the KiCad library part; the locked 3-connector PLACEMENT still needs the mechanical fit-check (official CM4 STEP + 2-layer coupon).

| Ref | Part / MPN | Mfr | Package | Key parameters | Interface / Rail |
|---|---|---|---|---|---|
| J31 | DF40C-100DS-0.4V(51) | Hirose | `Connector_Hirose_DF40:Hirose_DF40C-100DS-0.4V_2x50_P0.4mm` | 100-pin, 0.4mm pitch B2B receptacle; CM4 J3A (low-speed) | CM4 J3A |
| J32 | DF40C-100DS-0.4V(51) | Hirose | `Connector_Hirose_DF40:Hirose_DF40C-100DS-0.4V_2x50_P0.4mm` | 100-pin, 0.4mm pitch B2B receptacle; CM4 J3B (high-speed: MIPI/USB) | CM4 J3B |
| J1 | DF40C-100DS-0.4V(51) | Hirose | `Connector_Hirose_DF40:Hirose_DF40C-100DS-0.4V_2x50_P0.4mm` | 100-pin, 0.4mm pitch B2B receptacle; CM4 J1 (I/O: SAI, MCLK) | CM4 J1 |

## 11. Other connectors + indicators

| Ref | Part / MPN | Mfr | Package | Key parameters | Interface / Rail |
|---|---|---|---|---|---|
| J3 | SM02B-SRSS-TB | JST | `Connector_JST:JST_SH_BM02B-SRSS-TB_1x02-1MP_P1.00mm_Vertical` | Speaker connector (post-EMI); 1.0mm pitch | speaker |
| J6 | SM02B-SRSS-TB | JST | `Connector_JST:JST_SH_BM02B-SRSS-TB_1x02-1MP_P1.00mm_Vertical` | Vibration motor connector; 1.0mm pitch | haptic |
| J7 | Header 1x4 2.54mm | generic | `Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical` | UART debug (TX/RX/GND/VREF) | UART0 |
| D1 | LED Green | generic | `LED_SMD:LED_0603_1608Metric` | Power LED; active-low GPIO sink; via R4 1k | status |
| D2 | LED Blue | generic | `LED_SMD:LED_0603_1608Metric` | Status LED; active-low GPIO sink; via R5 1k | status |

## 12. Passives (summary)

Full per-family passive audit (value / tolerance / dielectric / voltage / DC-bias verdicts) is in **AI_Glasses_Carrier_V1_Design_Review.pdf §7**. Headline:

| Family | Refs (examples) | Spec |
|---|---|---|
| I2C pull-ups | R7-R13 | 2.2k 1% 0603 |
| USB-C CC | R1, R2 | 5.1k 1% 0603 (locked) |
| Decoupling | C2,C4,C6,C10,C13... | 100nF X7R 50V 0603 |
| Bulk MLCC | C1,C3,C5,C8,C15,C29 | 10uF X5R 25V 0805 |
| VBAT bulk | C7 | 22uF X5R 25V 0805 |
| Class-D EMI | C23, C24 | 1nF X7R 50V 0603 |
| Current shunt | R3 | mohm 2512 (select for 5V measure) |

---
_Generated by `scripts/generate_parts_spec.py`. MPN/footprint live from the BOM; headline specs curated from manufacturer datasheets - verify before procurement._
