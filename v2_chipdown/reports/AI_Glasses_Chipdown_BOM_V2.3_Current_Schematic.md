# AI Glasses RK3576 Chip-down BOM V2.3
## Current schematic-aligned BOM, power, and layout-gate report

- Generated: 2026-07-01
- Source of truth: `v2_chipdown/scripts/chipdown_bom.py` and `v2_chipdown/config/power_budget_v2.yaml`
- Schematic: `v2_chipdown/hardware/ai_glasses_v2_chipdown.kicad_sch`
- Exported BOM/netlist/PDF: `v2_chipdown/reports/*`
- This report is schematic-aligned. If an older PDF disagrees with this document, use this document.

## 1. Read this first

| Item | Current value |
|---|---|
| Schematic scope | Pre-PCB-layout functional-block schematic |
| Components / nets | 93 components / 133 nets |
| Assembly states | DNP=16, Fit=57, HOLD=18, TBD=2 |
| Board split | R-Temple Compute Board=33, L-Temple AON/Power Board=9, Temple Rears (batt/spkr/ant)=19, Front Sensor Board=24, EVT Debug Tail=8 |
| ERC | Report includes: Errors, Warnings, Exclusions; ** ERC messages: 0  Errors 0  Warnings 0 |
| PCB layout release | NOT released; Gate 0/G00F/G05/G07/G08/G10/G12 still block layout |
| Phase 1.5 | Required mechanical/electrical floorplan before formal PCB layout |
| First EVT hinge stance | Hinge electrical interconnect is out of scope for Chip-down EVT V2.0; J4 hinge FPC has been removed from the schematic source |

Status legend: Fit = populate first build; DNP = land only; HOLD = candidate blocked by a gate; TBD = MPN/spec undecided.
Power numbers are project budget estimates until EVT shunt measurements replace them.

## 2. System power boundary

| Power state | Current load (mW) | Target band (mW) | Battery current @3.7 V | Runtime on LP451165 x2 1S2P |
|---|--:|--:|--:|--:|
| Deep Off (AON only, RK3576 down) | 22 | 20-50 | 6 mA | 91 h |
| Quick Standby (DDR retention / light sleep) | 134 | 80-200 | 36 mA | 15 h |
| Phone-assisted safety ID (blended) | 362 | 250-450 | 98 mA | 5.5 h (331 min) |
| Mixed motion use (blended) | 450 | <=500-800 | 122 mA | 4.4 h (266 min) |
| Record Active (1080p, ISP+encode) | 1290 | 1000-1500 | 349 mA | 1.5 h (93 min) |
| AI Burst (NPU + encode + Wi-Fi) | 2065 | 1500-2500 | 558 mA | 1.0 h (58 min) |

Recommended pack: LP451165 x2, 1S2P, 600 mAh / 2.22 Wh nominal, one cell per temple.
Baseline current model uses 1290 mW for continuous 1080p record and 2065 mW for AI burst.

## 3. Subsystem power model

| Subsystem | Domain | deep_off | quick_standby | phone_assist | mixed_active | record | ai_record |
|---|---|--:|--:|--:|--:|--:|--:|
| BLE MCU (nRF-class, always-on) | AON | 2 | 3 | 8 | 6 | 5 | 8 |
| Audio DSP / wake-word (always listening) | AON | 12 | 12 | 15 | 15 | 15 | 20 |
| IMU BMI270 (low-power) | AON | 1 | 1 | 1 | 1 | 1 | 1 |
| MEMS mic array (wake mic always; array when active) | AON | 3 | 3 | 6 | 6 | 8 | 10 |
| Fuel gauge + NTC + protection | AON | 1 | 1 | 1 | 1 | 1 | 1 |
| AON Buck quiescent + regulation loss | AON | 3 | 4 | 6 | 6 | 10 | 15 |
| RK3576 SoC + LPDDR4X + eMMC + PMIC | COMPUTE | 0 | 90 | 150 | 250 | 850 | 1500 |
| Custom 1080p camera (sensor + ISP share) | CAMERA | 0 | 0 | 0 | 30 | 250 | 300 |
| Wi-Fi (on-demand) | RADIO | 0 | 0 | 150 | 100 | 80 | 120 |
| Audio amp + speaker (avg) | AUDIO | 0 | 0 | 15 | 15 | 30 | 30 |
| Compute-island load switches / PMIC loss | COMPUTE | 0 | 20 | 10 | 20 | 40 | 60 |
| **TOTAL** | | **22** | **134** | **362** | **450** | **1290** | **2065** |

## 4. What changed from the attached PDF

- The Wi-Fi module is the current schematic part `U11 / C015 = FCU760KAAMD`, status HOLD.
- BQ25895 is now explicit as the primary charger + Power Path block; nPM1300 remains the AON low-power PMIC/gauge/rail manager.
- J4 hinge FPC has been removed: no hinge FPC footprint, no cross-hinge battery, MIPI, USB or audio wiring in EVT V2.0.
- J3 is the proposed 33-pin FH26W camera FPC connector; IMX415 is now drawn as a 4-lane target while its mechanical module remains HOLD/TBD.
- Wi-Fi/BLE share the main dual-band FPC antenna; the second FCU760K RF port is DNP/test only.
- The IMU is `U10 / C012 = BMI270`, status Fit.
- The current baseline power totals are 22 / 134 / 362 / 450 / 1290 / 2065 mW.
- The current BOM is not only C001-C045; it is 93 schematic components with expanded shunts, INA238 monitors, passives, load switches, charger/input protection, and C046 default-off pull-downs.
- C044 is expanded into RS1-RS9 plus U25-U33 current monitors; C045/C046 passives are explicit pre-layout controls.
- PCB layout is still not released; unresolved mechanical/battery/FPC/RF/camera/AON gates remain.
- A new Phase 1.5 floorplan is required between ERC-clean schematic and formal PCB layout.

## 5. Board and mechanical partition

| Region | Current schematic contents | EVT note |
|---|---|---|
| Front Sensor Board | IMX415 custom FPC module, 3 fitted T5837 mics, 4th mic DNP, camera rails, MIPI ESD, front FPC | Final module pinout/lens/lane count remains G10 HOLD |
| R-Temple Compute Board | RK3576, RK806S, LPDDR4X, eMMC, TPS61088, FCU760K Wi-Fi, Wi-Fi buck/load switch, MAX98360A audio | Heat and boost droop gates remain open |
| L-Temple AON/Power Board | nRF54L15, nPM1300, NDP120, BMI270, optional protection, main shunt/INA | AON average <=25 mW and ceiling <=50 mW must be measured |
| Temple Rears | LP451165 x2 pack envelopes, branch fuses/shunts, main speaker, shared Wi-Fi/BLE antenna, pogo, DNP RF/debug options | First EVT is fixed-temple electrically; no hinge FPC/cross-hinge harness in the released schematic |
| EVT Debug Tail | USB-C, ESD, CC resistors, SWD/UART pads, power/reset/recovery buttons | Bring-up only; production can hide/remove |

## 5.5. Phase 1.5 mechanical/electrical floorplan

Before formal PCB placement/routing, create a no-route fit floorplan. This is a CAD + EE deliverable, not a routed board.

| Required output | Contents |
|---|---|
| Right-temple top/side view | usable length/width/height; Compute PCB; RK3576/LPDDR/RK806/eMMC/Wi-Fi/BQ25895/boost-inductor zones; battery; speaker; shared Wi-Fi/BLE antenna keep-out; pogo; front FPC corridor; shell/foam/swell allowance |
| Left-temple top/side view | usable length/width/height; AON/power PCB; nRF/nPM/NDP/BMI270 zones; battery; no separate BLE antenna fitted; pogo/service clearance; shell/foam/swell allowance |
| KiCad no-route floorplan | board frames plus RK3576, LPDDR, RK806, eMMC, Wi-Fi, boost inductor, FPC connectors, battery 3D/envelope blocks, speaker and antenna keep-outs |
| Pass/fail decision | prove the current schematic architecture fits before routing; if not, change battery/partition/connectors/DNP features/local temple width |

Formal routing starts only after this floorplan passes. If it fails, do not route; change the architecture first.

## 6. Current BOM by board

### R-Temple Compute Board

| Ref | BOM ID | Value | Status | Pri | Package / footprint placeholder | Gate |
|---|---|---|:--:|:--:|---|---|
| U1 | C001 | RK3576 | Fit | P0 | AI_Glasses_V2:VERIFY_FCCSP698L_16x17 | G01 (RK3576 datasheet/HDG/ballmap/DDR guide) |
| U2 | C002 | RK806S-5 QFN68 7x7x0.90mm | HOLD | P0 | AI_Glasses_V2:VERIFY_QFN68_7x7_EP5.49_P0.35 | G03 (official RK806S-5 datasheet, OTP/default rails, sequence, layout guide) |
| U3 | C003 | Samsung K4U6E3S4AA-MGCL | HOLD | P0 | AI_Glasses_V2:VERIFY_FBGA200_0.65 | G02 (Samsung datasheet/ball map/IBIS + Rockchip DDR AVL/init + length report) |
| U4 | C004 | Samsung KLMAG1JENB-B041 | HOLD | P0 | AI_Glasses_V2:VERIFY_BGA153 | G04 (official Samsung datasheet/package + BSP boot/HS200 then HS400 validation) |
| Y1 | C005 | 24 MHz 10 ppm XTAL | Fit | P0 | AI_Glasses_V2:Crystal_SMD_3225 | G01 (reuse reference CL/ESR + placement distance per HDG) |
| U5 | C006 | MX25U6432F | DNP | P1 | AI_Glasses_V2:USON-8 | Boot flow decides whether production needs it |
| U6 | C007 | TPS61088 | HOLD | P0 | AI_Glasses_V2:VQFN-22_4.5x3.5 | G06/G09 (measured RK3576 boot+AI peak, soft-start, droop, thermal) |
| L1 | C008 | Coilcraft XGL4020-102MEC 1.0uH | HOLD | P0 | AI_Glasses_V2:VERIFY_L_4x4x2_XGL4020 | G06/G13 (Isat/DCR/thermal pass for 5.1V 3A continuous / 4A peak boost) |
| U11 | C015 | FCU760KAAMD | HOLD | P0 | AI_Glasses_V2:VERIFY_LCC_13x12.2_Quectel | G05 (Quectel HW Design + RK3576 BSP driver/firmware/enum) + official LCC land pattern |
| U12 | C016 | TPS62825 | Fit | P0 | AI_Glasses_V2:QFN_1.5x1.5 | G05/G06 (inductor/caps per module 353mA TX peak + ripple) |
| L2 | C016c | Wi-Fi buck inductor (TBD) | Fit | P0 | AI_Glasses_V2:VERIFY_L_2x2 | Per TPS62825 peak+ripple |
| U13 | C016b | TPS22917DBVR | Fit | P0 | Package_TO_SOT_SMD:SOT-23-5 | G05 (turn-on sequence w/ module) |
| C1 | C015-C | 47uF 6.3V X5R | Fit | P0 | AI_Glasses_V2:C_0805 | Local bulk per Quectel HW Design |
| RT3 | C043 | 10k NTC B=3435 | Fit | P0 | AI_Glasses_V2:R_0402 | Probe position per thermal sim |
| U35 | C010b | BQ25895 | HOLD | P0 | AI_Glasses_V2:VERIFY_WQFN_24_BQ25895 | Charger/power-path config, TS thresholds, 1S2P charge profile, thermal/current validation |
| U36 | C034b | 5V input eFuse/OVP (MPN TBD) | HOLD | P0 | AI_Glasses_V2:VERIFY_EFUSE_OVP | Select MPN for pogo/USB VBUS surge, reverse, OVP, current limit and thermal fault |
| U20 | C024 | MAX98360A | Fit | P0 | AI_Glasses_V2:VERIFY_WLP_QFN | Verify Z/cavity/EMI/peak power |
| U21 | C024b | TPS22917DBVR | Fit | P0 | Package_TO_SOT_SMD:SOT-23-5 | Amp must be fully power-downable (V1 lesson) |
| RS4 | C044-RSOC | 10 mohm 1% | Fit | P0 | AI_Glasses_V2:R_0805_shunt | 5-20 mohm (2A x 10m=20mV; avoid boost UVLO) |
| RS5 | C044-RWIFI | 50 mohm 1% | Fit | P0 | AI_Glasses_V2:R_0603_shunt | 20-100 mohm |
| RS6 | C044-RAUD | 50 mohm 1% | Fit | P0 | AI_Glasses_V2:R_0603_shunt | 20-100 mohm |
| U28 | C044c | INA238 (I_SOC_5V) | DNP | P1 | AI_Glasses_V2:VSSOP-10 | Power Gate - EVT-A only |
| U29 | C044e | INA238 (I_WIFI) | DNP | P1 | AI_Glasses_V2:VSSOP-10 | Power Gate - EVT-A only |
| U30 | C044f | INA238 (I_AUDIO) | DNP | P1 | AI_Glasses_V2:VSSOP-10 | Power Gate - EVT-A only |
| R11 | C046a | 100k | Fit | P0 | AI_Glasses_V2:R_0402 | Default OFF (section 4) |
| R12 | C046b | 100k | Fit | P0 | AI_Glasses_V2:R_0402 | Default OFF (section 4) |
| R16 | C046f | 100k | Fit | P0 | AI_Glasses_V2:R_0402 | Default OFF (section 4) |
| R17 | C046g | 100k | Fit | P0 | AI_Glasses_V2:R_0402 | Default OFF (section 4) |
| R18 | C046h | 100k | Fit | P0 | AI_Glasses_V2:R_0402 | Default OFF (section 4/section 9: FCU760K CHIP_EN default low) |
| R19 | C046i | 100k | Fit | P0 | AI_Glasses_V2:R_0402 | Default OFF (section 4) |
| R20 | C046j | 100k | Fit | P0 | AI_Glasses_V2:R_0402 | Default OFF (section 4) |
| R9 | C045e | 2.2k 1% | Fit | P0 | AI_Glasses_V2:R_0402 | Confirm vs SoC PMIC bus |
| R10 | C045f | 2.2k 1% | Fit | P0 | AI_Glasses_V2:R_0402 | Confirm vs SoC PMIC bus |

### L-Temple AON/Power Board

| Ref | BOM ID | Value | Status | Pri | Package / footprint placeholder | Gate |
|---|---|---|:--:|:--:|---|---|
| U7 | C009 | nRF54L15-QFN48 | Fit | P0 | AI_Glasses_V2:QFN-48_6x6 | EVT-frozen (RF layout/SDK/package to freeze early) |
| U8 | C010 | nPM1300 | HOLD | P0 | AI_Glasses_V2:QFN_5x5 | G08 (AON <=25/50mW) - configure via nPM PowerUP on EK before board |
| U9 | C011 | NDP120 | HOLD | P0 | AI_Glasses_V2:VERIFY_QFN_5x5 | Full datasheet + dev kit + measured listening power + NDA/licensing |
| U10 | C012 | BMI270 | Fit | P0 | Package_LGA:LGA-14_2.5x3mm_P0.5mm | Evaluate false-trigger under real frame vibration |
| U22 | C027 | DRV2605L | DNP | P1 | Package_SO:MSOP-10_3x3mm_P0.5mm | Vibration P1 - may DNP on first board (IMU/mic coupling) |
| RS1 | C044-RBAT | 10 mohm 1% 1W | Fit | P0 | AI_Glasses_V2:R_1206_shunt | I_BAT_TOTAL; the one production-kept sense path |
| U25 | C044a | INA238 (I_BAT_TOTAL) | DNP | P1 | AI_Glasses_V2:VSSOP-10 | Power Gate - EVT-A; production may keep this one |
| R3 | C045a | 2.2k 1% | Fit | P0 | AI_Glasses_V2:R_0402 | Confirm vs total AON bus capacitance |
| R4 | C045b | 2.2k 1% | Fit | P0 | AI_Glasses_V2:R_0402 | Confirm vs total AON bus capacitance |

### Temple Rears (batt/spkr/ant)

| Ref | BOM ID | Value | Status | Pri | Package / footprint placeholder | Gate |
|---|---|---|:--:|:--:|---|---|
| J6 | C018 | FCU760K ANT_BT DNP test pad | DNP | P0 | AI_Glasses_V2:VERIFY_ANT | Only populate if Quectel FAE + coexistence test requires the second RF port |
| J7 | C017 | Taoglas FXP840.07.0055B | HOLD | P0 | AI_Glasses_V2:VERIFY_FPC_ANT_14x5 | G14 (worn-state tune + antenna keep-out in full shell with battery/speaker) |
| LS1 | C025 | CUI CMS-15113-078SP-67 | HOLD | P0 | AI_Glasses_V2:VERIFY_SPK_15x11x3 | Acoustic EVT: 0.3-0.5cc cavity, port/foam seal, magnet-to-antenna clearance, leak test |
| LS2 | C026 | 2nd speaker pad | DNP | P1 | AI_Glasses_V2:VERIFY_SPK | Decide dual-speaker at EVT-B |
| M1 | C028 | LRA/ERM motor | DNP | P1 | AI_Glasses_V2:VERIFY_LRA | Vibration P1 |
| BT1 | C029 | LP451165 300mAh (R) | HOLD | P0 | AI_Glasses_V2:VERIFY_CELL_4.5x11x65 | G07 (full datasheet, >=2C, IR, cycles, cert) |
| BT2 | C030 | LP451165 300mAh (L) | HOLD | P0 | AI_Glasses_V2:VERIFY_CELL_70x12.8x5.6_maxenv | G07 |
| F1 | C031a | PTC/fuse (R branch) | TBD | P0 | AI_Glasses_V2:VERIFY_FUSE | Rating from peak-current calc (> branch peak, < FPC rating) |
| F2 | C031b | PTC/fuse (L branch) | TBD | P0 | AI_Glasses_V2:VERIFY_FUSE | Rating from peak-current calc |
| RS2 | C044-RCL | 10 mohm 1% | Fit | P0 | AI_Glasses_V2:R_0805_shunt | Branch current-share (section 7/section 29) |
| RS3 | C044-RCR | 10 mohm 1% | Fit | P0 | AI_Glasses_V2:R_0805_shunt | Branch current-share (section 7/section 29) |
| PCM1 | C032 | Supplier 1S2P pack PCM + protection FETs | HOLD | P0 | AI_Glasses_V2:PACK_INTERNAL_NO_BOARD_FOOTPRINT | Pack supplier drawing: OVP/UVP/OCP/SCP thresholds, FET Rds(on), current rating, NTC placement, UN38.3/MSDS/IEC62133 |
| RT1 | C033a | 10k NTC B=3435 1% (R cell) | Fit | P0 | AI_Glasses_V2:R_0402 | NTC curve/package/placement matched to pack supplier + BQ25895/nPM1300 config |
| RT2 | C033b | 10k NTC B=3435 1% (L cell) | Fit | P0 | AI_Glasses_V2:R_0402 | NTC curve/package/placement matched to pack supplier + ADC/config |
| TP2 | C033-TP | Battery test points | Fit | P0 | AI_Glasses_V2:TestPad_Set | Cell/pack voltage + NTC probe access (section 21) |
| J1 | C034 | CCP P2578MP01-06C180HT | HOLD | P0 | AI_Glasses_V2:VERIFY_POGO_6P_1.8MM | USB2 eye/contact validation, current/fault/ESD, mating STEP, corrosion/cycle life |
| J5 | C040 | U.FL / I-PEX MHF RF test connector | DNP | P0 | Connector_Coaxial:U.FL_Hirose_U.FL-R-SMT-1_Vertical | EVT RF debug only; production prefers direct coax or soldered antenna pigtail |
| U26 | C044-ICL | INA238 (I_CELL_L) | DNP | P1 | AI_Glasses_V2:VSSOP-10 | Power Gate - EVT-A only (current-share) |
| U27 | C044-ICR | INA238 (I_CELL_R) | DNP | P1 | AI_Glasses_V2:VSSOP-10 | Power Gate - EVT-A only (current-share) |

### Front Sensor Board

| Ref | BOM ID | Value | Status | Pri | Package / footprint placeholder | Gate |
|---|---|---|:--:|:--:|---|---|
| U14 | C019 | Sony IMX415-AAQR-C custom module | HOLD | P0 | AI_Glasses_V2:VERIFY_CAM_MODULE | G10 (module lens/FOV/FPC pinout/lane/supply/timing from vendor) |
| U15 | C020 | TPS62840 | Fit | P0 | AI_Glasses_V2:VERIFY_WSON | Output current/noise per final module (DVDD ~250mA max + margin) |
| L3 | C020b | Cam 1V1 buck inductor (TBD) | Fit | P0 | AI_Glasses_V2:VERIFY_L_1.6x0.8 | Per TPS62840 design |
| U16 | C021 | TLV75529PDRVR | Fit | P0 | AI_Glasses_V2:WSON-6_2x2 | Verify vs IMX415 AVDD peak (156mA) + PSRR |
| U17 | C022 | TPS22917DBVR | Fit | P0 | Package_TO_SOT_SMD:SOT-23-5 | Check reverse block, ramp, QOD, logic level |
| U18 | C023a | TPD4E05U06 | Fit | P0 | AI_Glasses_V2:USON | Low-cap array near FPC entry |
| U19 | C023b | TPD4E05U06 | Fit | P0 | AI_Glasses_V2:USON | Low-cap array near FPC entry |
| U34 | C023c | TPD4E05U06 | Fit | P0 | AI_Glasses_V2:USON | Low-cap array near FPC entry for 4-lane CSI |
| MK1 | C013a | T5837 (wake mic) | Fit | P0 | AI_Glasses_V2:LGA-5_3.5x2.65 | G11 (mic coords/ports/wind/wake + AEC/beamforming) |
| MK2 | C013b | T5837 (array mic 1) | Fit | P0 | AI_Glasses_V2:LGA-5_3.5x2.65 | G11 |
| MK3 | C013c | T5837 (array mic 2) | Fit | P0 | AI_Glasses_V2:LGA-5_3.5x2.65 | G11 |
| MK4 | C014 | T5837 (4th mic) | DNP | P1 | AI_Glasses_V2:LGA-5_3.5x2.65 | G11 (populate only if array sim/proto needs it) |
| J3 | C038 | Hirose FH26W-33S-0.3SHW(97) | HOLD | P0 | AI_Glasses_V2:VERIFY_FH26W_33S_0.3SHW | G10/G12 (camera module vendor signs 33-pin pinout, contact orientation, impedance) |
| RS7 | C044-RC1 | 100 mohm 1% | Fit | P0 | AI_Glasses_V2:R_0603_shunt | Per-rail Kelvin (section 23/section 29); DVDD ~250mA |
| RS8 | C044-RC8 | 100 mohm 1% | Fit | P0 | AI_Glasses_V2:R_0402_shunt | Per-rail Kelvin (section 23/section 29); IOVDD ~3mA |
| RS9 | C044-RC29 | 100 mohm 1% | Fit | P0 | AI_Glasses_V2:R_0603_shunt | Per-rail Kelvin (section 23/section 29); AVDD ~156mA |
| U31 | C044-IC1 | INA238 (I_CAM_1V1) | DNP | P1 | AI_Glasses_V2:VSSOP-10 | Power Gate - EVT-A only |
| U32 | C044-IC8 | INA238 (I_CAM_1V8) | DNP | P1 | AI_Glasses_V2:VSSOP-10 | Power Gate - EVT-A only |
| U33 | C044-IC29 | INA238 (I_CAM_2V9) | DNP | P1 | AI_Glasses_V2:VSSOP-10 | Power Gate - EVT-A only |
| R13 | C046c | 100k | Fit | P0 | AI_Glasses_V2:R_0402 | Default OFF (section 4) |
| R14 | C046d | 100k | Fit | P0 | AI_Glasses_V2:R_0402 | Default OFF (section 4) |
| R15 | C046e | 100k | Fit | P0 | AI_Glasses_V2:R_0402 | Default OFF (section 4) |
| R5 | C045c | 2.2k 1% | Fit | P0 | AI_Glasses_V2:R_0402 | Confirm vs camera bus capacitance |
| R6 | C045d | 2.2k 1% | Fit | P0 | AI_Glasses_V2:R_0402 | Confirm vs camera bus capacitance |

### EVT Debug Tail

| Ref | BOM ID | Value | Status | Pri | Package / footprint placeholder | Gate |
|---|---|---|:--:|:--:|---|---|
| J2 | C035 | USB-C 16p USB2-only | Fit | P0 | AI_Glasses_V2:USB_C_16P_MidMount | Connector height + shell opening co-freeze |
| U24 | C036 | TPD2E001 | Fit | P0 | Package_TO_SOT_SMD:SOT-23-3 | Keep ~90 ohm diff + continuous ref gnd |
| R1 | C037a | 5.1k 1% | Fit | P0 | AI_Glasses_V2:R_0402 | USB-C spec |
| R2 | C037b | 5.1k 1% | Fit | P0 | AI_Glasses_V2:R_0402 | USB-C spec |
| TP1 | C041 | UART/SWD pogo pads | Fit | P0 | AI_Glasses_V2:TestPad_Set | Voltage domain clearly labelled (no 3.3V into 1.8V IO) |
| SW1 | C042a | Power/PWRKEY | Fit | P0 | Button_Switch_SMD:SW_Push_1P1T_NO_CK_KMR2 | First chip-down must recover from boot failure |
| SW2 | C042b | Reset | Fit | P0 | Button_Switch_SMD:SW_Push_1P1T_NO_CK_KMR2 | Bring-up |
| SW3 | C042c | MaskROM/Recovery | Fit | P0 | Button_Switch_SMD:SW_Push_1P1T_NO_CK_KMR2 | Bring-up (recover from bad boot) |

## 7. Per-component power allocation

Values below are battery-side project-budget mW and sum exactly to the current subsystem totals. A zero means DNP, passive/source, or already included in its owning domain; it does not mean zero parasitic physics.

| Ref | BOM ID | Value | Status | deep_off | quick_standby | phone_assist | mixed_active | record | ai_record | Basis |
|---|---|---|:--:|--:|--:|--:|--:|--:|--:|---|
| U1 | C001 | RK3576 | Fit | 0 | 20 | 80 | 150 | 600 | 1150 | RK3576 project allocation inside compute core row |
| U2 | C002 | RK806S-5 QFN68 7x7x0.90mm | HOLD | 0 | 10 | 15 | 25 | 70 | 100 | RK806S/PMIC rail-management allocation |
| U3 | C003 | Samsung K4U6E3S4AA-MGCL | HOLD | 0 | 55 | 45 | 60 | 130 | 180 | LPDDR4X retention/activity allocation |
| U4 | C004 | Samsung KLMAG1JENB-B041 | HOLD | 0 | 5 | 10 | 15 | 50 | 70 | eMMC standby/write allocation |
| Y1 | C005 | 24 MHz 10 ppm XTAL | Fit | 0 | 0 | 0 | 0 | 0 | 0 | 0 direct load, DNP, passive, source, or included in owning domain |
| U5 | C006 | MX25U6432F | DNP | 0 | 0 | 0 | 0 | 0 | 0 | 0 direct load, DNP, passive, source, or included in owning domain |
| U6 | C007 | TPS61088 | HOLD | 0 | 20 | 10 | 20 | 40 | 60 | compute-island boost/load-switch/PMIC loss row |
| L1 | C008 | Coilcraft XGL4020-102MEC 1.0uH | HOLD | 0 | 0 | 0 | 0 | 0 | 0 | 0 direct load, DNP, passive, source, or included in owning domain |
| U11 | C015 | FCU760KAAMD | HOLD | 0 | 0 | 145 | 95 | 75 | 115 | FCU760K on-demand Wi-Fi activity average |
| U12 | C016 | TPS62825 | Fit | 0 | 0 | 5 | 5 | 5 | 5 | Wi-Fi buck conversion-loss allocation |
| L2 | C016c | Wi-Fi buck inductor (TBD) | Fit | 0 | 0 | 0 | 0 | 0 | 0 | 0 direct load, DNP, passive, source, or included in owning domain |
| U13 | C016b | TPS22917DBVR | Fit | 0 | 0 | 0 | 0 | 0 | 0 | 0 direct load, DNP, passive, source, or included in owning domain |
| C1 | C015-C | 47uF 6.3V X5R | Fit | 0 | 0 | 0 | 0 | 0 | 0 | 0 direct load, DNP, passive, source, or included in owning domain |
| RT3 | C043 | 10k NTC B=3435 | Fit | 0 | 0 | 0 | 0 | 0 | 0 | 0 direct load, DNP, passive, source, or included in owning domain |
| U35 | C010b | BQ25895 | HOLD | 0 | 0 | 0 | 0 | 0 | 0 | 0 direct load, DNP, passive, source, or included in owning domain |
| U36 | C034b | 5V input eFuse/OVP (MPN TBD) | HOLD | 0 | 0 | 0 | 0 | 0 | 0 | 0 direct load, DNP, passive, source, or included in owning domain |
| U7 | C009 | nRF54L15-QFN48 | Fit | 2 | 3 | 8 | 6 | 5 | 8 | nRF-class BLE MCU/current-state-machine average |
| U8 | C010 | nPM1300 | HOLD | 3 | 4 | 6 | 6 | 10 | 15 | nPM1300 AON buck quiescent + regulation loss |
| U9 | C011 | NDP120 | HOLD | 12 | 12 | 15 | 15 | 15 | 20 | NDP120-class wake-word/listening budget |
| U10 | C012 | BMI270 | Fit | 1 | 1 | 1 | 1 | 1 | 1 | BMI270 low-power motion budget |
| J6 | C018 | FCU760K ANT_BT DNP test pad | DNP | 0 | 0 | 0 | 0 | 0 | 0 | 0 direct load, DNP, passive, source, or included in owning domain |
| J7 | C017 | Taoglas FXP840.07.0055B | HOLD | 0 | 0 | 0 | 0 | 0 | 0 | 0 direct load, DNP, passive, source, or included in owning domain |
| U14 | C019 | Sony IMX415-AAQR-C custom module | HOLD | 0 | 0 | 0 | 25 | 220 | 265 | custom 1080p camera module baseline allocation |
| U15 | C020 | TPS62840 | Fit | 0 | 0 | 0 | 2 | 15 | 18 | camera 1.1 V buck loss allocation |
| L3 | C020b | Cam 1V1 buck inductor (TBD) | Fit | 0 | 0 | 0 | 0 | 0 | 0 | 0 direct load, DNP, passive, source, or included in owning domain |
| U16 | C021 | TLV75529PDRVR | Fit | 0 | 0 | 0 | 3 | 14 | 16 | camera 2.9 V LDO loss allocation |
| U17 | C022 | TPS22917DBVR | Fit | 0 | 0 | 0 | 0 | 1 | 1 | camera 1.8 V load-switch loss allocation |
| U18 | C023a | TPD4E05U06 | Fit | 0 | 0 | 0 | 0 | 0 | 0 | 0 direct load, DNP, passive, source, or included in owning domain |
| U19 | C023b | TPD4E05U06 | Fit | 0 | 0 | 0 | 0 | 0 | 0 | 0 direct load, DNP, passive, source, or included in owning domain |
| U34 | C023c | TPD4E05U06 | Fit | 0 | 0 | 0 | 0 | 0 | 0 | 0 direct load, DNP, passive, source, or included in owning domain |
| MK1 | C013a | T5837 (wake mic) | Fit | 3 | 3 | 3 | 3 | 3 | 3 | wake mic always-on share of MEMS mic row |
| MK2 | C013b | T5837 (array mic 1) | Fit | 0 | 0 | 1.5 | 1.5 | 2.5 | 3.5 | array mic share of MEMS mic row |
| MK3 | C013c | T5837 (array mic 2) | Fit | 0 | 0 | 1.5 | 1.5 | 2.5 | 3.5 | array mic share of MEMS mic row |
| MK4 | C014 | T5837 (4th mic) | DNP | 0 | 0 | 0 | 0 | 0 | 0 | 0 direct load, DNP, passive, source, or included in owning domain |
| U20 | C024 | MAX98360A | Fit | 0 | 0 | 2 | 2 | 3 | 3 | MAX98360A small-signal/idle audio allocation |
| U21 | C024b | TPS22917DBVR | Fit | 0 | 0 | 0 | 0 | 0 | 0 | 0 direct load, DNP, passive, source, or included in owning domain |
| LS1 | C025 | CUI CMS-15113-078SP-67 | HOLD | 0 | 0 | 13 | 13 | 27 | 27 | single speaker acoustic-output average |
| LS2 | C026 | 2nd speaker pad | DNP | 0 | 0 | 0 | 0 | 0 | 0 | 0 direct load, DNP, passive, source, or included in owning domain |
| U22 | C027 | DRV2605L | DNP | 0 | 0 | 0 | 0 | 0 | 0 | 0 direct load, DNP, passive, source, or included in owning domain |
| M1 | C028 | LRA/ERM motor | DNP | 0 | 0 | 0 | 0 | 0 | 0 | 0 direct load, DNP, passive, source, or included in owning domain |
| BT1 | C029 | LP451165 300mAh (R) | HOLD | 0 | 0 | 0 | 0 | 0 | 0 | 0 direct load, DNP, passive, source, or included in owning domain |
| BT2 | C030 | LP451165 300mAh (L) | HOLD | 0 | 0 | 0 | 0 | 0 | 0 | 0 direct load, DNP, passive, source, or included in owning domain |
| F1 | C031a | PTC/fuse (R branch) | TBD | 0 | 0 | 0 | 0 | 0 | 0 | 0 direct load, DNP, passive, source, or included in owning domain |
| F2 | C031b | PTC/fuse (L branch) | TBD | 0 | 0 | 0 | 0 | 0 | 0 | 0 direct load, DNP, passive, source, or included in owning domain |
| RS2 | C044-RCL | 10 mohm 1% | Fit | 0 | 0 | 0 | 0 | 0 | 0 | 0 direct load, DNP, passive, source, or included in owning domain |
| RS3 | C044-RCR | 10 mohm 1% | Fit | 0 | 0 | 0 | 0 | 0 | 0 | 0 direct load, DNP, passive, source, or included in owning domain |
| RS1 | C044-RBAT | 10 mohm 1% 1W | Fit | 0 | 0 | 0 | 0 | 0 | 0 | 0 direct load, DNP, passive, source, or included in owning domain |
| PCM1 | C032 | Supplier 1S2P pack PCM + protection FETs | HOLD | 0 | 0 | 0 | 0 | 0 | 0 | 0 direct load, DNP, passive, source, or included in owning domain |
| RT1 | C033a | 10k NTC B=3435 1% (R cell) | Fit | 0.5 | 0.5 | 0.5 | 0.5 | 0.5 | 0.5 | fuel-gauge/NTC/protection monitor allocation |
| RT2 | C033b | 10k NTC B=3435 1% (L cell) | Fit | 0.5 | 0.5 | 0.5 | 0.5 | 0.5 | 0.5 | fuel-gauge/NTC/protection monitor allocation |
| TP2 | C033-TP | Battery test points | Fit | 0 | 0 | 0 | 0 | 0 | 0 | 0 direct load, DNP, passive, source, or included in owning domain |
| J1 | C034 | CCP P2578MP01-06C180HT | HOLD | 0 | 0 | 0 | 0 | 0 | 0 | 0 direct load, DNP, passive, source, or included in owning domain |
| J2 | C035 | USB-C 16p USB2-only | Fit | 0 | 0 | 0 | 0 | 0 | 0 | 0 direct load, DNP, passive, source, or included in owning domain |
| U24 | C036 | TPD2E001 | Fit | 0 | 0 | 0 | 0 | 0 | 0 | 0 direct load, DNP, passive, source, or included in owning domain |
| R1 | C037a | 5.1k 1% | Fit | 0 | 0 | 0 | 0 | 0 | 0 | 0 direct load, DNP, passive, source, or included in owning domain |
| R2 | C037b | 5.1k 1% | Fit | 0 | 0 | 0 | 0 | 0 | 0 | 0 direct load, DNP, passive, source, or included in owning domain |
| J3 | C038 | Hirose FH26W-33S-0.3SHW(97) | HOLD | 0 | 0 | 0 | 0 | 0 | 0 | 0 direct load, DNP, passive, source, or included in owning domain |
| J5 | C040 | U.FL / I-PEX MHF RF test connector | DNP | 0 | 0 | 0 | 0 | 0 | 0 | 0 direct load, DNP, passive, source, or included in owning domain |
| TP1 | C041 | UART/SWD pogo pads | Fit | 0 | 0 | 0 | 0 | 0 | 0 | 0 direct load, DNP, passive, source, or included in owning domain |
| SW1 | C042a | Power/PWRKEY | Fit | 0 | 0 | 0 | 0 | 0 | 0 | 0 direct load, DNP, passive, source, or included in owning domain |
| SW2 | C042b | Reset | Fit | 0 | 0 | 0 | 0 | 0 | 0 | 0 direct load, DNP, passive, source, or included in owning domain |
| SW3 | C042c | MaskROM/Recovery | Fit | 0 | 0 | 0 | 0 | 0 | 0 | 0 direct load, DNP, passive, source, or included in owning domain |
| RS4 | C044-RSOC | 10 mohm 1% | Fit | 0 | 0 | 0 | 0 | 0 | 0 | 0 direct load, DNP, passive, source, or included in owning domain |
| RS5 | C044-RWIFI | 50 mohm 1% | Fit | 0 | 0 | 0 | 0 | 0 | 0 | 0 direct load, DNP, passive, source, or included in owning domain |
| RS6 | C044-RAUD | 50 mohm 1% | Fit | 0 | 0 | 0 | 0 | 0 | 0 | 0 direct load, DNP, passive, source, or included in owning domain |
| RS7 | C044-RC1 | 100 mohm 1% | Fit | 0 | 0 | 0 | 0 | 0 | 0 | 0 direct load, DNP, passive, source, or included in owning domain |
| RS8 | C044-RC8 | 100 mohm 1% | Fit | 0 | 0 | 0 | 0 | 0 | 0 | 0 direct load, DNP, passive, source, or included in owning domain |
| RS9 | C044-RC29 | 100 mohm 1% | Fit | 0 | 0 | 0 | 0 | 0 | 0 | 0 direct load, DNP, passive, source, or included in owning domain |
| U25 | C044a | INA238 (I_BAT_TOTAL) | DNP | 0 | 0 | 0 | 0 | 0 | 0 | 0 direct load, DNP, passive, source, or included in owning domain |
| U26 | C044-ICL | INA238 (I_CELL_L) | DNP | 0 | 0 | 0 | 0 | 0 | 0 | 0 direct load, DNP, passive, source, or included in owning domain |
| U27 | C044-ICR | INA238 (I_CELL_R) | DNP | 0 | 0 | 0 | 0 | 0 | 0 | 0 direct load, DNP, passive, source, or included in owning domain |
| U28 | C044c | INA238 (I_SOC_5V) | DNP | 0 | 0 | 0 | 0 | 0 | 0 | 0 direct load, DNP, passive, source, or included in owning domain |
| U29 | C044e | INA238 (I_WIFI) | DNP | 0 | 0 | 0 | 0 | 0 | 0 | 0 direct load, DNP, passive, source, or included in owning domain |
| U30 | C044f | INA238 (I_AUDIO) | DNP | 0 | 0 | 0 | 0 | 0 | 0 | 0 direct load, DNP, passive, source, or included in owning domain |
| U31 | C044-IC1 | INA238 (I_CAM_1V1) | DNP | 0 | 0 | 0 | 0 | 0 | 0 | 0 direct load, DNP, passive, source, or included in owning domain |
| U32 | C044-IC8 | INA238 (I_CAM_1V8) | DNP | 0 | 0 | 0 | 0 | 0 | 0 | 0 direct load, DNP, passive, source, or included in owning domain |
| U33 | C044-IC29 | INA238 (I_CAM_2V9) | DNP | 0 | 0 | 0 | 0 | 0 | 0 | 0 direct load, DNP, passive, source, or included in owning domain |
| R11 | C046a | 100k | Fit | 0 | 0 | 0 | 0 | 0 | 0 | 0 direct load, DNP, passive, source, or included in owning domain |
| R12 | C046b | 100k | Fit | 0 | 0 | 0 | 0 | 0 | 0 | 0 direct load, DNP, passive, source, or included in owning domain |
| R13 | C046c | 100k | Fit | 0 | 0 | 0 | 0 | 0 | 0 | 0 direct load, DNP, passive, source, or included in owning domain |
| R14 | C046d | 100k | Fit | 0 | 0 | 0 | 0 | 0 | 0 | 0 direct load, DNP, passive, source, or included in owning domain |
| R15 | C046e | 100k | Fit | 0 | 0 | 0 | 0 | 0 | 0 | 0 direct load, DNP, passive, source, or included in owning domain |
| R16 | C046f | 100k | Fit | 0 | 0 | 0 | 0 | 0 | 0 | 0 direct load, DNP, passive, source, or included in owning domain |
| R17 | C046g | 100k | Fit | 0 | 0 | 0 | 0 | 0 | 0 | 0 direct load, DNP, passive, source, or included in owning domain |
| R18 | C046h | 100k | Fit | 0 | 0 | 0 | 0 | 0 | 0 | 0 direct load, DNP, passive, source, or included in owning domain |
| R19 | C046i | 100k | Fit | 0 | 0 | 0 | 0 | 0 | 0 | 0 direct load, DNP, passive, source, or included in owning domain |
| R20 | C046j | 100k | Fit | 0 | 0 | 0 | 0 | 0 | 0 | 0 direct load, DNP, passive, source, or included in owning domain |
| R3 | C045a | 2.2k 1% | Fit | 0 | 0 | 0 | 0 | 0 | 0 | 0 direct load, DNP, passive, source, or included in owning domain |
| R4 | C045b | 2.2k 1% | Fit | 0 | 0 | 0 | 0 | 0 | 0 | 0 direct load, DNP, passive, source, or included in owning domain |
| R5 | C045c | 2.2k 1% | Fit | 0 | 0 | 0 | 0 | 0 | 0 | 0 direct load, DNP, passive, source, or included in owning domain |
| R6 | C045d | 2.2k 1% | Fit | 0 | 0 | 0 | 0 | 0 | 0 | 0 direct load, DNP, passive, source, or included in owning domain |
| R9 | C045e | 2.2k 1% | Fit | 0 | 0 | 0 | 0 | 0 | 0 | 0 direct load, DNP, passive, source, or included in owning domain |
| R10 | C045f | 2.2k 1% | Fit | 0 | 0 | 0 | 0 | 0 | 0 | 0 direct load, DNP, passive, source, or included in owning domain |
| **TOTAL** | | | | **22** | **134** | **362** | **450** | **1290** | **2065** | Current model total |

## 8. Power domains and shutdown policy

| Domain | Rails / source | Main loads | Default state | Owner / control |
|---|---|---|---|---|
| Battery / pack | LP451165 1S2P pack PCM -> F1/F2 -> RS2/RS3 -> BAT_P -> RS1 -> NPM_VBAT | Entire system source | Live | Pack PCM + BQ25895 charger/power path |
| AON | AON_1V8, AON_3V3, AON_LSW2 from nPM1300 | nRF54L15, NDP120, BMI270, wake mic, fuel/NTC | On in normal standby | nPM1300 / nRF54L15 |
| RK3576 compute | VSYS -> RS4 -> TPS61088 -> SOC_5V -> RK806S rails | RK3576, LPDDR4X, eMMC | Off until `SOC_PWR_EN` + `PMIC_PWRON` | nRF54L15 master; Linux safe-off handshake |
| Camera | TPS62840 CAM_1V1, TPS22917 CAM_1V8, TLV75529 CAM_2V9 | IMX415 custom FPC module | Off until camera session | nRF54L15 / RK3576 |
| Wi-Fi | VSYS -> RS5 -> TPS62825 -> TPS22917 -> FCU760K | FCU760K and antenna path | Off until transfer/preview | nRF54L15 enables buck, switch, and module |
| Audio | VSYS -> RS6 -> TPS22917 -> MAX98360A -> LS1 | Single 8 ohm speaker | Off/muted | nRF54L15 / RK3576 |

Default-off controls use 100k pull-downs R11-R20 so compute, camera, Wi-Fi, and audio remain off if firmware is absent or reset.

## 9. Layout-entry gates

| Gate | Topic | Current status | Close condition |
|---|---|:--:|---|
| G00 | Mechanical/battery | HOLD | Real cell fit, swell room, FPC corridor, antenna keep-out, no battery over RK3576/PMIC |
| G00F | Phase 1.5 floorplan | HOLD | Dimensioned top/side floorplan + no-route KiCad placement envelopes prove fit before routing |
| G01 | RK3576 identity + HDG | OPEN | Full datasheet, HDG, ball map, package drawing, reference delta |
| G02 | LPDDR4X | OPEN | MPN, topology, placement, length report, DDR review |
| G03 | RK806S PMIC | OPEN | Exact MPN, rails, inductors/caps, sequencing, timing |
| G04 | eMMC/boot | OPEN | MPN, bootloader/BSP support, cold boot and power-loss recovery |
| G05 | Wi-Fi FCU760K | HOLD | Hardware design, land pattern/3D, antenna SKU, BSP driver/firmware enumeration |
| G06 | High-power transient sizing | OPEN | RK3576 boot/AI peak, boost soft-start, 1S droop, Wi-Fi/camera/audio peaks |
| G07 | LP451165 + 1S2P pack | HOLD | Formal datasheet, discharge curves, IR/cycle/cert, pairing/fusing/NTC/current-share |
| G08 | AON power | HOLD | nPM1300 EK config, NDP120 kit, measured AON <=25 mW avg / <=50 mW ceiling |
| G09 | Thermal/boost droop | OPEN | RK3576 burst thermal path, TPS61088/RK806 droop and UVLO margin |
| G10 | Camera module | HOLD | Final IMX415 module FPC pinout, lens/FOV, lane count, rail current/timing |
| G11 | Mic/audio topology | OPEN | Mic coordinates, ports, wind/AEC/beamforming, NDP120 wake path |
| G12 | Camera/front FPC interconnect | HOLD | FH26W-33S pinout, contact orientation, impedance and module vendor sign-off; hinge electrical interconnect is out of scope for EVT V2.0 |
| G13 | Magnetics/passives height | OPEN | Inductor Isat/DCR/height, cap derating, wearable Z limits |
| G14 | RF/worn tune | OPEN | Antenna SKU, keep-out, matching in shell and worn condition |
| G15 | Passive/manufacturing BOM | OPEN | Expanded R/C/L MPNs, derating, lifecycle and alternates |

## 10. Detailed schematic cards

### U1 / C001 - RK3576

- Board/status: R-Temple Compute Board / Fit / P0
- Package field: AI_Glasses_V2:VERIFY_FCCSP698L_16x17
- Gate: G01 (RK3576 datasheet/HDG/ballmap/DDR guide)
- Description: Main SoC - 8-core, 6 TOPS NPU, ISP, MIPI CSI, H.264/265. Demand-started compute island (NOT always-on). Functional block: interface pins only.
- Note: FCCSP698L 16.1x17.2mm 0.6mm. Ball map not yet released -> only architecturally-defined interface pins are drawn. Start as a delta off the Radxa reference (Phase 2).
- Schematic nets: VDD_CPU->VDD_CPU, VDD_GPU->VDD_GPU, VDD_NPU->VDD_NPU, VDD_LOGIC->VDD_LOGIC, VDD_DDR->VDD_DDR, VCC_DDRIO->VCC_DDRIO, VCCIO_1V8->VCCIO_1V8, VCC_3V3->VCC_3V3, GND->GND, XIN->SOC_XIN, XOUT->SOC_XOUT, PMIC_SLEEP->PMIC_SLEEP, SHUTDOWN_REQ->SOC_SHUTDOWN_REQ, SAFE_TO_OFF->SOC_SAFE_TO_OFF, ALIVE->SOC_ALIVE, FAULT->SOC_FAULT, AON_UART_RX->AON_UART_TX, AON_UART_TX->AON_UART_RX, DDR_BUS->DDR_BUS, EMMC_BUS->EMMC_BUS, FSPI_BUS->FSPI_BUS, CSI_CLK_P->CSI_CLK_P, CSI_CLK_N->CSI_CLK_N, CSI_D0_P->CSI_D0_P, CSI_D0_N->CSI_D0_N, CSI_D1_P->CSI_D1_P, CSI_D1_N->CSI_D1_N, CSI_D2_P->CSI_D2_P, CSI_D2_N->CSI_D2_N, CSI_D3_P->CSI_D3_P, CSI_D3_N->CSI_D3_N, CAM_I2C_SCL->CAM_I2C_SCL, CAM_I2C_SDA->CAM_I2C_SDA, CAM_RST_L->CAM_RST_L, CAM_PWDN_L->CAM_PWDN_L, CAM_MCLK->CAM_MCLK, PDM_ARR_CLK->PDM_ARRAY_CLK, PDM_ARR_D0->PDM_ARRAY_D0, PDM_ARR_D1->PDM_ARRAY_D1, I2S_BCLK->I2S_BCLK, I2S_LRCLK->I2S_LRCLK, I2S_DIN->I2S_DIN, SARADC_NTC->SOC_NTC, USB2_WIFI_DP->WIFI_USB_DP, USB2_WIFI_DM->WIFI_USB_DM, PCM_CLK->WIFI_PCM_CLK, PCM_SYNC->WIFI_PCM_SYNC, PCM_DIN->WIFI_PCM_DIN, PCM_DOUT->WIFI_PCM_DOUT, WIFI_WAKE_L->WIFI_WAKE_L, USB2_DP->USB2_DP, USB2_DM->USB2_DM, DBG_UART_TX->SOC_DBG_TX, DBG_UART_RX->SOC_DBG_RX, MASKROM_n->SOC_MASKROM_L, RESET_n->SOC_RESET_L, PWRKEY->SOC_PWRKEY

### U2 / C002 - RK806S-5 QFN68 7x7x0.90mm

- Board/status: R-Temple Compute Board / HOLD / P0
- Package field: AI_Glasses_V2:VERIFY_QFN68_7x7_EP5.49_P0.35
- Gate: G03 (official RK806S-5 datasheet, OTP/default rails, sequence, layout guide)
- Description: SoC PMIC - generates CPU/GPU/NPU/DDR/IO rails + power sequencing for RK3576. Reuse verified RK3576 power architecture; NOT for AON.
- Note: Package envelope can be used for placement: QFN68 + exposed thermal pad, body 7.0x7.0mm, max height 0.90mm, 0.35mm pitch, ePad about 5.49x5.49mm, MSL3. Power sequence, OTP/default voltage table and compensation parts remain HOLD until complete Rockchip/Radxa reference collateral is reviewed.
- Schematic nets: VIN->SOC_5V, GND->GND, PWRON->PMIC_PWRON, SLEEP->PMIC_SLEEP, I2C_SCL->SOC_PMIC_SCL, I2C_SDA->SOC_PMIC_SDA, RESET_n->SOC_RESET_L, VDD_CPU->VDD_CPU, VDD_GPU->VDD_GPU, VDD_NPU->VDD_NPU, VDD_LOGIC->VDD_LOGIC, VDD_DDR->VDD_DDR, VCC_DDRIO->VCC_DDRIO, VCCIO_1V8->VCCIO_1V8, VCC_3V3->VCC_3V3

### U3 / C003 - Samsung K4U6E3S4AA-MGCL

- Board/status: R-Temple Compute Board / HOLD / P0
- Package field: AI_Glasses_V2:VERIFY_FBGA200_0.65
- Gate: G02 (Samsung datasheet/ball map/IBIS + Rockchip DDR AVL/init + length report)
- Description: EVT system memory baseline - Samsung K4U6E3S4AA-MGCL, 16Gb / 2GB, x32, 200-ball FBGA 0.65mm, LPDDR4X-4266 class. Use this Radxa reference MPN for first chip-down boot risk reduction; 4GB is a later BOM variant only.
- Note: Do not substitute the 32Gb/4GB K4UBE3D4AB-MGCL unless Rockchip confirms DDR AVL, training binary/init parameters, rank/capacity config and ball assignment compatibility.
- Schematic nets: VDD_DDR->VDD_DDR, VDDQ->VCC_DDRIO, GND->GND, DDR_BUS->DDR_BUS

### U4 / C004 - Samsung KLMAG1JENB-B041

- Board/status: R-Temple Compute Board / HOLD / P0
- Package field: AI_Glasses_V2:VERIFY_BGA153
- Gate: G04 (official Samsung datasheet/package + BSP boot/HS200 then HS400 validation)
- Description: EVT system storage baseline - Samsung KLMAG1JENB-B041, 16GB eMMC 5.1, 153-FBGA, 11.5x13.0x0.8mm, 0.5mm pitch, 8-bit, HS400 capable. VCC 2.7-3.6V, VCCQ uses 1.8V in this project. 32GB upgrade is a later BSP/supply variant.
- Schematic nets: VCC->VCC_3V3, VCCQ->VCCIO_1V8, GND->GND, EMMC_BUS->EMMC_BUS

### Y1 / C005 - 24 MHz 10 ppm XTAL

- Board/status: R-Temple Compute Board / Fit / P0
- Package field: AI_Glasses_V2:Crystal_SMD_3225
- Gate: G01 (reuse reference CL/ESR + placement distance per HDG)
- Description: Main clock - 24 MHz, 10 ppm; load per Rockchip reference layout.
- Schematic nets: XIN->SOC_XIN, XOUT->SOC_XOUT, GND->GND

### U5 / C006 - MX25U6432F

- Board/status: R-Temple Compute Board / DNP / P1
- Package field: AI_Glasses_V2:USON-8
- Gate: Boot flow decides whether production needs it
- Description: Backup boot flash - 64 Mbit 1.8 V serial NOR on FSPI. Reserved for recovery / factory test / alt-boot; not populated on first EVT.
- Schematic nets: VCC->VCCIO_1V8, GND->GND, FSPI_BUS->FSPI_BUS

### U6 / C007 - TPS61088

- Board/status: R-Temple Compute Board / HOLD / P0
- Package field: AI_Glasses_V2:VQFN-22_4.5x3.5
- Gate: G06/G09 (measured RK3576 boot+AI peak, soft-start, droop, thermal)
- Description: Main SoC 5 V boost - 1S -> SOC_5V for the compute island. High-current sync boost; EN from nRF54L15, PG back to nRF. Candidate/HOLD until peak measured.
- Note: Only the RK3576 island gets a boost (Phase-3 rule). Verify RK806 input range before committing the boost; if RK806 takes 1S directly, drop it.
- Schematic nets: VIN->SOC_IN, SW->SOC_BOOST_SW, GND->GND, EN->SOC_PWR_EN, PG->SOC_5V_PGOOD, VOUT->SOC_5V

### L1 / C008 - Coilcraft XGL4020-102MEC 1.0uH

- Board/status: R-Temple Compute Board / HOLD / P0
- Package field: AI_Glasses_V2:VERIFY_L_4x4x2_XGL4020
- Gate: G06/G13 (Isat/DCR/thermal pass for 5.1V 3A continuous / 4A peak boost)
- Description: Boost inductor for TPS61088 - Coilcraft XGL4020-102MEC candidate, 1.0uH, 4.0x4.0x2.0mm, low DCR, high-current shielded inductor. Keep SW copper small; do not route DDR/MIPI/audio/RF under the inductor.
- Schematic nets: A->SOC_IN, B->SOC_BOOST_SW

### U11 / C015 - FCU760KAAMD

- Board/status: R-Temple Compute Board / HOLD / P0
- Package field: AI_Glasses_V2:VERIFY_LCC_13x12.2_Quectel
- Gate: G05 (Quectel HW Design + RK3576 BSP driver/firmware/enum) + official LCC land pattern
- Description: Wi-Fi 6 + BT 5.4 module - Quectel FCU760K, LCC 13.0x12.2x2.0mm. USB2 to RK3576 host; PCM for BT audio; VBAT 3.0-3.6V (typ 3.3V), max TX 353 mA. On-demand, load-switched off.
- Note: CONFIRMED on Radxa CM4 V1.20 p20; interface = USB2 (NOT SDIO). Single-antenna SKU FCU760KAAMD shares Wi-Fi/BT on ANT_WIFI_BT. Optional ANT_BT is kept only as a DNP test/matching node until Quectel FAE confirms its use. Exact LCC pinout/land pattern + Linux driver/firmware stay HOLD pending Quectel Hardware Design.
- Schematic nets: VBAT->WIFI_VBAT_3V3, GND->GND, USB_DP->WIFI_USB_DP, USB_DM->WIFI_USB_DM, CHIP_EN->WIFI_CHIP_EN, PCM_CLK->WIFI_PCM_CLK, PCM_SYNC->WIFI_PCM_SYNC, PCM_IN->WIFI_PCM_DOUT, PCM_OUT->WIFI_PCM_DIN, WAKE->WIFI_WAKE_L, ANT_WIFI_BT->WIFI_ANT, ANT_BT_DNP->BLE_ANT

### U12 / C016 - TPS62825

- Board/status: R-Temple Compute Board / Fit / P0
- Package field: AI_Glasses_V2:QFN_1.5x1.5
- Gate: G05/G06 (inductor/caps per module 353mA TX peak + ripple)
- Description: Wi-Fi dedicated 3.3 V buck - feeds FCU760K VBAT; >=500 mA capability for the 353 mA TX peak (pack note). EN by AON MCU. Avoids routing the radio through 5 V (Phase-3 rule).
- Schematic nets: VIN->WIFI_IN, SW->WIFI_BUCK_SW, GND->GND, EN->WIFI_BUCK_EN, VOUT->WIFI_3V3

### L2 / C016c - Wi-Fi buck inductor (TBD)

- Board/status: R-Temple Compute Board / Fit / P0
- Package field: AI_Glasses_V2:VERIFY_L_2x2
- Gate: Per TPS62825 peak+ripple
- Description: Wi-Fi buck inductor - SW->3V3, value per TPS62825 design.
- Schematic nets: A->WIFI_BUCK_SW, B->WIFI_3V3

### U13 / C016b - TPS22917DBVR

- Board/status: R-Temple Compute Board / Fit / P0
- Package field: Package_TO_SOT_SMD:SOT-23-5
- Gate: G05 (turn-on sequence w/ module)
- Description: Wi-Fi load switch - gates WIFI_3V3 -> FCU760K VBAT with QOD + reverse block. EN by AON MCU.
- Schematic nets: VIN->WIFI_3V3, VOUT->WIFI_VBAT_3V3, EN->WIFI_LS_EN, GND->GND

### C1 / C015-C - 47uF 6.3V X5R

- Board/status: R-Temple Compute Board / Fit / P0
- Package field: AI_Glasses_V2:C_0805
- Gate: Local bulk per Quectel HW Design
- Description: FCU760K VBAT bulk storage - 47 uF local reservoir next to the module (pack: 47uF + 1uF + 100nF). Rides the 353 mA TX burst.
- Schematic nets: A->WIFI_VBAT_3V3, B->GND

### RT3 / C043 - 10k NTC B=3435

- Board/status: R-Temple Compute Board / Fit / P0
- Package field: AI_Glasses_V2:R_0402
- Gate: Probe position per thermal sim
- Description: SoC/enclosure temp monitor - 10k NTC on SoC heat-spreader + skin side. Wearable must watch both die and skin temp.
- Schematic nets: A->SOC_NTC, B->GND

### U35 / C010b - BQ25895

- Board/status: R-Temple Compute Board / HOLD / P0
- Package field: AI_Glasses_V2:VERIFY_WQFN_24_BQ25895
- Gate: Charger/power-path config, TS thresholds, 1S2P charge profile, thermal/current validation
- Description: Primary 1S charger + Power Path - protected 5V input to SYS/VSYS and 1S2P pack. Use with pack-internal PCM, BQ25895 TS temperature protection, input current limit, and software charge-profile control. First bring-up must prove low-battery boost droop and charge/boost coexistence.
- Note: This is the board-level charger/power-path block for EVT V2.0. nPM1300 remains the AON buck/fuel-gauge/low-power PMIC; do not also populate board-level BQ2970 protection when the pack includes PCM.
- Schematic nets: VBUS->USB_5V, SYS->VSYS, BAT->NPM_VBAT, GND->GND, SCL->I2C_AON_SCL, SDA->I2C_AON_SDA, TS->NTC_R, INT_L->CHG_INT_L, CE_L->CHG_CE_L, PG_L->CHG_PG_L

### U36 / C034b - 5V input eFuse/OVP (MPN TBD)

- Board/status: R-Temple Compute Board / HOLD / P0
- Package field: AI_Glasses_V2:VERIFY_EFUSE_OVP
- Gate: Select MPN for pogo/USB VBUS surge, reverse, OVP, current limit and thermal fault
- Description: 5V input protection between magnetic pogo/EVT USB-C and charger input. Required: VBUS TVS/OVP/eFuse/current limit, fault indication and layout close to the connector path.
- Schematic nets: IN->VBUS_RAW, OUT->USB_5V, GND->GND, FLT_L->VBUS_FAULT_L

### U7 / C009 - nRF54L15-QFN48

- Board/status: L-Temple AON/Power Board / Fit / P0
- Package field: AI_Glasses_V2:QFN-48_6x6
- Gate: EVT-frozen (RF layout/SDK/package to freeze early)
- Description: Low-power BLE MCU - ALWAYS ON. Owns the system state machine; controls RK3576/camera/Wi-Fi/audio power ENs; talks IMU/buttons/gauge; UART to RK3576, SPI to NDP120. Turns RK3576 from an always-on host into a demand accelerator.
- Note: nRF54L15 (not nRF52/53): 1.5MB NVM / 256KB RAM headroom, long-life platform, later WLCSP shrink. QFN48 for the debuggable EVT board. EVT V2.0 does not fit a separate nRF BLE antenna; phone/BLE data path is assigned to FCU760K shared RF unless RF coexistence testing reopens the DNP ANT_BT option.
- Schematic nets: VDD_1V8->AON_1V8, VDD_3V3->AON_3V3, GND->GND, ANT_DNP->NC, SOC_PWR_EN->SOC_PWR_EN, SOC_5V_PGOOD->SOC_5V_PGOOD, PMIC_PWRON->PMIC_PWRON, CAM_1V1_EN->CAM_1V1_EN, CAM_1V8_EN->CAM_1V8_EN, CAM_2V9_EN->CAM_2V9_EN, WIFI_BUCK_EN->WIFI_BUCK_EN, WIFI_LS_EN->WIFI_LS_EN, WIFI_CHIP_EN->WIFI_CHIP_EN, AUDIO_LS_EN->AUDIO_LS_EN, AMP_SD->AUDIO_AMP_SD, SOC_SHDN_REQ->SOC_SHUTDOWN_REQ, SOC_SAFE_OFF->SOC_SAFE_TO_OFF, SOC_ALIVE->SOC_ALIVE, SOC_FAULT->SOC_FAULT, AON_UART_TX->AON_UART_TX, AON_UART_RX->AON_UART_RX, I2C_SCL->I2C_AON_SCL, I2C_SDA->I2C_AON_SDA, PMIC_INT_L->PMIC_INT_L, PMIC_SHPHLD->PMIC_SHPHLD, CHG_INT_L->CHG_INT_L, CHG_CE_L->CHG_CE_L, CHG_PG_L->CHG_PG_L, VBUS_FAULT_L->VBUS_FAULT_L, IMU_INT1->IMU_INT1, IMU_INT2->IMU_INT2, DSP_SCK->DSP_SPI_SCK, DSP_MOSI->DSP_SPI_MOSI, DSP_MISO->DSP_SPI_MISO, DSP_CS_n->DSP_SPI_CS_n, DSP_WAKE->DSP_WAKE, DSP_READY->DSP_READY, DSP_FAULT->DSP_FAULT, DSP_RST_n->DSP_RESET_L, HAPTIC_EN->HAPTIC_EN, SWDIO->NRF_SWDIO, SWDCLK->NRF_SWDCLK

### U8 / C010 - nPM1300

- Board/status: L-Temple AON/Power Board / HOLD / P0
- Package field: AI_Glasses_V2:QFN_5x5
- Gate: G08 (AON <=25/50mW) - configure via nPM PowerUP on EK before board
- Description: AON PMIC / low-power rail manager - fuel-gauge support, dual Buck, LDO/Load-Switch and Ship/Hibernate for the small AON world ONLY; NOT the RK3576 peak path.
- Note: BQ25895 is the primary charger + power-path block in EVT V2.0. nPM1300 stays in the AON domain for low-Iq rails/gauge/support functions and must be configured for the supplier-built 1S2P pack, not a single 300mAh cell.
- Schematic nets: VBAT->NPM_VBAT, VBUS->USB_5V, VSYS->VSYS, GND->GND, BUCK1->AON_1V8, BUCK2->AON_3V3, LSW2->AON_LSW2, NTC_R->NTC_R, NTC_L->NTC_L, I2C_SCL->I2C_AON_SCL, I2C_SDA->I2C_AON_SDA, INT->PMIC_INT_L, SHPHLD->PMIC_SHPHLD

### U9 / C011 - NDP120

- Board/status: L-Temple AON/Power Board / HOLD / P0
- Package field: AI_Glasses_V2:VERIFY_QFN_5x5
- Gate: Full datasheet + dev kit + measured listening power + NDA/licensing
- Description: Always-on Audio DSP - ultra-low-power wake-word + audio front-end; wakes the MCU over GPIO. Moves voice listening off RK3576. Keep bypass + DNP capability.
- Note: HOLD until hardware datasheet, rails/sequence, PDM/I2S detail, firmware/model tools, wake-word licensing, real listening power, MOQ/lead all in hand.
- Schematic nets: VDD_1V8->AON_1V8, VDD_3V3->AON_3V3, GND->GND, PDM_CLK->PDM_WAKE_CLK, PDM_DATA->PDM_WAKE_DATA, HOST_SCK->DSP_SPI_SCK, HOST_MOSI->DSP_SPI_MOSI, HOST_MISO->DSP_SPI_MISO, HOST_CS_n->DSP_SPI_CS_n, WAKE->DSP_WAKE, READY->DSP_READY, FAULT->DSP_FAULT, RESET_n->DSP_RESET_L

### U10 / C012 - BMI270

- Board/status: L-Temple AON/Power Board / Fit / P0
- Package field: Package_LGA:LGA-14_2.5x3mm_P0.5mm
- Gate: Evaluate false-trigger under real frame vibration
- Description: 6-axis IMU - low-power motion detect; motion-interrupt wakes the MCU. Cycling/running state ID for wearables.
- Schematic nets: VDD->AON_1V8, VDDIO->AON_1V8, GND->GND, SCL->I2C_AON_SCL, SDA->I2C_AON_SDA, INT1->IMU_INT1, INT2->IMU_INT2

### J6 / C018 - FCU760K ANT_BT DNP test pad

- Board/status: Temple Rears (batt/spkr/ant) / DNP / P0
- Package field: AI_Glasses_V2:VERIFY_ANT
- Gate: Only populate if Quectel FAE + coexistence test requires the second RF port
- Description: Optional second RF feed for FCU760K ANT_BT - DNP/test only. EVT V2.0 does not fit a separate BLE antenna; Wi-Fi/BLE share the main dual-band FPC antenna on WIFI_ANT.
- Schematic nets: ANT->BLE_ANT, GND->GND

### J7 / C017 - Taoglas FXP840.07.0055B

- Board/status: Temple Rears (batt/spkr/ant) / HOLD / P0
- Package field: AI_Glasses_V2:VERIFY_FPC_ANT_14x5
- Gate: G14 (worn-state tune + antenna keep-out in full shell with battery/speaker)
- Description: Shared Wi-Fi/BLE dual-band FPC antenna candidate - Taoglas FXP840.07.0055B, about 14x5x0.1mm with 55mm coax/MHF-style termination. Place at temple end or non-metal window; keep away from battery, speaker magnet, pogo magnet, shields and copper.
- Schematic nets: ANT->WIFI_ANT, GND->GND

### U14 / C019 - Sony IMX415-AAQR-C custom module

- Board/status: Front Sensor Board / HOLD / P0
- Package field: AI_Glasses_V2:VERIFY_CAM_MODULE
- Gate: G10 (module lens/FOV/FPC pinout/lane/supply/timing from vendor)
- Description: Main camera module target - Sony IMX415-AAQR-C, 8.46 MP, 3840x2160 30fps baseline, RAW10 first, 4-lane MIPI CSI-2. Custom small sensor+lens rigid island + FPC (NOT a dev module). Sensor PCB target <=15x15mm, total camera Z target <=9.5mm. Sensor rails (Sony datasheet): AVDD 2.9V 128/156mA, IOVDD 1.8V 3mA, DVDD 1.1V 187/250mA (~0.58W typ, ~0.77W max).
- Note: IMX415 mechanical stack is still TBD: lens MPN, IR-cut, PCB, glue, FPC exit, mount, TTL/BFL/CRA/MTF/distortion/relative illumination and module STEP must come from the module vendor. Use orange TBD mechanical envelope; not released for tooling.
- Schematic nets: DVDD_1V1->CAM_1V1_S, IOVDD_1V8->CAM_1V8_S, AVDD_2V9->CAM_2V9_S, GND->GND, CSI_CLK_P->CSI_CLK_P, CSI_CLK_N->CSI_CLK_N, CSI_D0_P->CSI_D0_P, CSI_D0_N->CSI_D0_N, CSI_D1_P->CSI_D1_P, CSI_D1_N->CSI_D1_N, CSI_D2_P->CSI_D2_P, CSI_D2_N->CSI_D2_N, CSI_D3_P->CSI_D3_P, CSI_D3_N->CSI_D3_N, SCL->CAM_I2C_SCL, SDA->CAM_I2C_SDA, XCLR_L->CAM_RST_L, PWDN_L->CAM_PWDN_L, INCK->CAM_MCLK, MODULE_ID->CAM_MODULE_ID

### U15 / C020 - TPS62840

- Board/status: Front Sensor Board / Fit / P0
- Package field: AI_Glasses_V2:VERIFY_WSON
- Gate: Output current/noise per final module (DVDD ~250mA max + margin)
- Description: Camera DVDD 1.1 V buck - ultra-low-Iq (~60 nA) buck for the sensor core (DVDD 187/250mA), up to ~750 mA. EN by AON MCU / SoC. True power-down when camera off.
- Schematic nets: VIN->VSYS, SW->CAM_1V1_SW, GND->GND, EN->CAM_1V1_EN, VOUT->CAM_1V1

### L3 / C020b - Cam 1V1 buck inductor (TBD)

- Board/status: Front Sensor Board / Fit / P0
- Package field: AI_Glasses_V2:VERIFY_L_1.6x0.8
- Gate: Per TPS62840 design
- Description: Camera 1.1 V buck inductor - SW->1V1.
- Schematic nets: A->CAM_1V1_SW, B->CAM_1V1

### U16 / C021 - TLV75529PDRVR

- Board/status: Front Sensor Board / Fit / P0
- Package field: AI_Glasses_V2:WSON-6_2x2
- Gate: Verify vs IMX415 AVDD peak (156mA) + PSRR
- Description: Camera AVDD 2.9 V LDO - 500 mA low-noise analog supply (AVDD 128/156mA). Low-noise LDO, NOT a series resistor off 3.3V (pack section 23).
- Schematic nets: VIN->VSYS, EN->CAM_2V9_EN, GND->GND, VOUT->CAM_2V9

### U17 / C022 - TPS22917DBVR

- Board/status: Front Sensor Board / Fit / P0
- Package field: Package_TO_SOT_SMD:SOT-23-5
- Gate: Check reverse block, ramp, QOD, logic level
- Description: Camera IOVDD 1.8 V load switch / isolation - low-leak switch from AON_1V8 for camera I/O (IOVDD ~3mA); Quick-Output-Discharge kills reverse feed when camera off (section 24).
- Schematic nets: VIN->AON_1V8, VOUT->CAM_1V8_SW, EN->CAM_1V8_EN, GND->GND

### U18 / C023a - TPD4E05U06

- Board/status: Front Sensor Board / Fit / P0
- Package field: AI_Glasses_V2:USON
- Gate: Low-cap array near FPC entry
- Description: MIPI/FPC ESD (clk + D0) - ultra-low-cap 4-ch ESD at the FPC entry.
- Schematic nets: CLK_P->CSI_CLK_P, CLK_N->CSI_CLK_N, D0_P->CSI_D0_P, D0_N->CSI_D0_N, GND->GND

### U19 / C023b - TPD4E05U06

- Board/status: Front Sensor Board / Fit / P0
- Package field: AI_Glasses_V2:USON
- Gate: Low-cap array near FPC entry
- Description: MIPI/FPC ESD (D1 + control) - ultra-low-cap ESD for the second lane pair and critical control.
- Schematic nets: D1_P->CSI_D1_P, D1_N->CSI_D1_N, RST->CAM_RST_L, MCLK->CAM_MCLK, GND->GND

### U34 / C023c - TPD4E05U06

- Board/status: Front Sensor Board / Fit / P0
- Package field: AI_Glasses_V2:USON
- Gate: Low-cap array near FPC entry for 4-lane CSI
- Description: MIPI/FPC ESD (D2 + D3) - adds the two lane pairs required by the 4-lane IMX415 EVT target.
- Schematic nets: D2_P->CSI_D2_P, D2_N->CSI_D2_N, D3_P->CSI_D3_P, D3_N->CSI_D3_N, GND->GND

### MK1 / C013a - T5837 (wake mic)

- Board/status: Front Sensor Board / Fit / P0
- Package field: AI_Glasses_V2:LGA-5_3.5x2.65
- Gate: G11 (mic coords/ports/wind/wake + AEC/beamforming)
- Description: PDM wake mic - dedicated always-on wake channel into NDP120 (AON audio domain). Deep Off must capture without RK3576.
- Schematic nets: VDD->AON_3V3, GND->GND, CLK->PDM_WAKE_CLK, DATA->PDM_WAKE_DATA

### MK2 / C013b - T5837 (array mic 1)

- Board/status: Front Sensor Board / Fit / P0
- Package field: AI_Glasses_V2:LGA-5_3.5x2.65
- Gate: G11
- Description: PDM array mic 1 - into RK3576 PDM for beamforming during vision/voice tasks.
- Schematic nets: VDD->AON_3V3, GND->GND, CLK->PDM_ARRAY_CLK, DATA->PDM_ARRAY_D0

### MK3 / C013c - T5837 (array mic 2)

- Board/status: Front Sensor Board / Fit / P0
- Package field: AI_Glasses_V2:LGA-5_3.5x2.65
- Gate: G11
- Description: PDM array mic 2 - second array channel (L/R stereo on shared PDM clock).
- Schematic nets: VDD->AON_3V3, GND->GND, CLK->PDM_ARRAY_CLK, DATA->PDM_ARRAY_D1

### MK4 / C014 - T5837 (4th mic)

- Board/status: Front Sensor Board / DNP / P1
- Package field: AI_Glasses_V2:LGA-5_3.5x2.65
- Gate: G11 (populate only if array sim/proto needs it)
- Description: 4th array mic - footprint only; on the switchable AON_LSW2 rail (nPM1300 load switch, section 14 'spare mic') so it can be fully powered down. Not populated until array/wind tests.
- Schematic nets: VDD->AON_LSW2, GND->GND, CLK->PDM_ARRAY_CLK, DATA->PDM_ARRAY_D1

### U20 / C024 - MAX98360A

- Board/status: R-Temple Compute Board / Fit / P0
- Package field: AI_Glasses_V2:VERIFY_WLP_QFN
- Gate: Verify Z/cavity/EMI/peak power
- Description: Digital Class-D amp - I2S in, mono, low-power shutdown. Direct digital audio chain, no analog codec. Fully power-downable via load switch.
- Schematic nets: VDD->AUDIO_PWR, GND->GND, BCLK->I2S_BCLK, LRCLK->I2S_LRCLK, DIN->I2S_DIN, SD_MODE->AUDIO_AMP_SD, OUT_P->SPK_P, OUT_N->SPK_N

### U21 / C024b - TPS22917DBVR

- Board/status: R-Temple Compute Board / Fit / P0
- Package field: Package_TO_SOT_SMD:SOT-23-5
- Gate: Amp must be fully power-downable (V1 lesson)
- Description: Audio load switch - gates AUDIO_PWR to the amp; EN by AON MCU / SoC.
- Schematic nets: VIN->AUDIO_IN, VOUT->AUDIO_PWR, EN->AUDIO_LS_EN, GND->GND

### LS1 / C025 - CUI CMS-15113-078SP-67

- Board/status: Temple Rears (batt/spkr/ant) / HOLD / P0
- Package field: AI_Glasses_V2:VERIFY_SPK_15x11x3
- Gate: Acoustic EVT: 0.3-0.5cc cavity, port/foam seal, magnet-to-antenna clearance, leak test
- Description: Main speaker EVT baseline - CUI CMS-15113-078SP-67, 15x11x3mm, 8 ohm, 0.7W rated / 1W max, about 91dB sensitivity, front IP67. Drive as mono differential speaker from the digital Class-D amp; limit first firmware to 0.5-0.7W RMS.
- Schematic nets: P->SPK_P, N->SPK_N

### LS2 / C026 - 2nd speaker pad

- Board/status: Temple Rears (batt/spkr/ant) / DNP / P1
- Package field: AI_Glasses_V2:VERIFY_SPK
- Gate: Decide dual-speaker at EVT-B
- Description: Second speaker land - reserved for productization; not populated first version.
- Schematic nets: P->NC, N->NC

### U22 / C027 - DRV2605L

- Board/status: L-Temple AON/Power Board / DNP / P1
- Package field: Package_SO:MSOP-10_3x3mm_P0.5mm
- Gate: Vibration P1 - may DNP on first board (IMU/mic coupling)
- Description: Haptic driver - LRA/ERM driver, I2C, waveform library. Silent safety reminder path.
- Schematic nets: VDD->VSYS, GND->GND, SCL->I2C_AON_SCL, SDA->I2C_AON_SDA, EN->HAPTIC_EN, OUT_P->HAPTIC_P, OUT_N->HAPTIC_N

### M1 / C028 - LRA/ERM motor

- Board/status: Temple Rears (batt/spkr/ant) / DNP / P1
- Package field: AI_Glasses_V2:VERIFY_LRA
- Gate: Vibration P1
- Description: LRA/ERM motor - short haptic alerts; can be replaced by phone vibration first version.
- Schematic nets: P->HAPTIC_P, N->HAPTIC_N

### BT1 / C029 - LP451165 300mAh (R)

- Board/status: Temple Rears (batt/spkr/ant) / HOLD / P0
- Package field: AI_Glasses_V2:VERIFY_CELL_4.5x11x65
- Gate: G07 (full datasheet, >=2C, IR, cycles, cert)
- Description: Right-side element of the supplier-built 1S2P pack - LP451165 nominal cell candidate, one per temple. Mechanical control envelope per side is 70x12.8x5.6mm including tabs, PCM/insulation allowance, foam and swelling space.
- Note: Do not parallel two independent protected cells on the PCB. G07 must close with one pack supplier building a matched 1S2P pack, common PCM, branch fusing/fusible links, two NTCs, official 2D/STEP, tab/cable exit, UN38.3/MSDS/IEC62133-equivalent data.
- Schematic nets: +->BATR_P, -->CELL_NEG

### BT2 / C030 - LP451165 300mAh (L)

- Board/status: Temple Rears (batt/spkr/ant) / HOLD / P0
- Package field: AI_Glasses_V2:VERIFY_CELL_70x12.8x5.6_maxenv
- Gate: G07
- Description: Left-side element of the supplier-built 1S2P pack - same batch/capacity/IR-matched to the right side. Use the same 70x12.8x5.6mm mechanical control envelope and pack supplier cable/tab/PCM drawing.
- Schematic nets: +->BATL_P, -->CELL_NEG

### F1 / C031a - PTC/fuse (R branch)

- Board/status: Temple Rears (batt/spkr/ant) / TBD / P0
- Package field: AI_Glasses_V2:VERIFY_FUSE
- Gate: Rating from peak-current calc (> branch peak, < FPC rating)
- Description: Right branch protection - resettable PTC / fusible link in the right cell branch. Limits a single-cell / FPC short (section 7).
- Schematic nets: A->BATR_P, B->BATR_F

### F2 / C031b - PTC/fuse (L branch)

- Board/status: Temple Rears (batt/spkr/ant) / TBD / P0
- Package field: AI_Glasses_V2:VERIFY_FUSE
- Gate: Rating from peak-current calc
- Description: Left branch protection - resettable PTC / fusible link in the left cell branch.
- Schematic nets: A->BATL_P, B->BATL_F

### RS2 / C044-RCL - 10 mohm 1%

- Board/status: Temple Rears (batt/spkr/ant) / Fit / P0
- Package field: AI_Glasses_V2:R_0805_shunt
- Gate: Branch current-share (section 7/section 29)
- Description: Left branch shunt - BATL_F -> BAT_P; I_CELL_L for current-share monitoring.
- Schematic nets: A->BATL_F, B->BAT_P

### RS3 / C044-RCR - 10 mohm 1%

- Board/status: Temple Rears (batt/spkr/ant) / Fit / P0
- Package field: AI_Glasses_V2:R_0805_shunt
- Gate: Branch current-share (section 7/section 29)
- Description: Right branch shunt - BATR_F -> BAT_P; I_CELL_R for current-share monitoring.
- Schematic nets: A->BATR_F, B->BAT_P

### RS1 / C044-RBAT - 10 mohm 1% 1W

- Board/status: L-Temple AON/Power Board / Fit / P0
- Package field: AI_Glasses_V2:R_1206_shunt
- Gate: I_BAT_TOTAL; the one production-kept sense path
- Description: Pack total shunt - BAT_P -> nPM1300 VBAT. Whole-device current (charge + discharge).
- Schematic nets: A->BAT_P, B->NPM_VBAT

### PCM1 / C032 - Supplier 1S2P pack PCM + protection FETs

- Board/status: Temple Rears (batt/spkr/ant) / HOLD / P0
- Package field: AI_Glasses_V2:PACK_INTERNAL_NO_BOARD_FOOTPRINT
- Gate: Pack supplier drawing: OVP/UVP/OCP/SCP thresholds, FET Rds(on), current rating, NTC placement, UN38.3/MSDS/IEC62133
- Description: Pack-internal protection baseline - the supplier builds both matched LP451165 cells as one complete 1S2P pack with common PCM, branch fusing/fusible links, over-charge, over-discharge, over-current, short-circuit and FET cutoff. The main PCB does NOT populate a second BQ2970 + dual-MOSFET protection stage.
- Note: Board-level battery protection is intentionally limited to BQ25895 charger/power-path, 5V input eFuse/OVP, software low-battery shutdown and test access. Battery exits via fixed harness/direct solder pads near the power board; no battery wiring crosses a hinge.
- Schematic nets: PACK_PLUS->BAT_P, PACK_MINUS->GND, CELL_MINUS->CELL_NEG, NTC1->NTC_R, NTC2_OR_ID->NTC_L

### RT1 / C033a - 10k NTC B=3435 1% (R cell)

- Board/status: Temple Rears (batt/spkr/ant) / Fit / P0
- Package field: AI_Glasses_V2:R_0402
- Gate: NTC curve/package/placement matched to pack supplier + BQ25895/nPM1300 config
- Description: Right cell temperature - 10k NTC at 25C, B=3435K, 1% or better, bonded to the cell large face near center, not to the PCM. Route with ESD/filtering and battery-sense ground.
- Schematic nets: A->NTC_R, B->GND

### RT2 / C033b - 10k NTC B=3435 1% (L cell)

- Board/status: Temple Rears (batt/spkr/ant) / Fit / P0
- Package field: AI_Glasses_V2:R_0402
- Gate: NTC curve/package/placement matched to pack supplier + ADC/config
- Description: Left cell temperature - second per-cell NTC for software/safety monitoring; firmware must stop charging if either cell is out of the supplier temperature window.
- Schematic nets: A->NTC_L, B->GND

### TP2 / C033-TP - Battery test points

- Board/status: Temple Rears (batt/spkr/ant) / Fit / P0
- Package field: AI_Glasses_V2:TestPad_Set
- Gate: Cell/pack voltage + NTC probe access (section 21)
- Description: Battery Kelvin test points - Cell-L+, Cell-R+, Pack+, Cell-neg, both NTCs for pairing / current-share / temperature verification.
- Schematic nets: CELL_L->BATL_P, CELL_R->BATR_P, PACK_P->BAT_P, CELL_NEG->CELL_NEG, NTC_L->NTC_L, NTC_R->NTC_R

### J1 / C034 - CCP P2578MP01-06C180HT

- Board/status: Temple Rears (batt/spkr/ant) / HOLD / P0
- Package field: AI_Glasses_V2:VERIFY_POGO_6P_1.8MM
- Gate: USB2 eye/contact validation, current/fault/ESD, mating STEP, corrosion/cycle life
- Description: 6-pin magnetic pogo EVT candidate - 1.8mm pitch, working height about 1.0mm, target outline about 10x3mm. Pins carry 5V charge input, USB2 D+/D-, and dual GND/VBUS contacts for lower resistance. Add VBUS TVS/eFuse/OVP, D+/D- low-cap ESD, USB CMC DNP, VBUS insert detect and MaskROM/UART fallback pads.
- Schematic nets: GND1->GND, USB_DN->USB2_DM, USB_DP->USB2_DP, GND2->GND, VBUS1->VBUS_RAW, VBUS2->VBUS_RAW

### J2 / C035 - USB-C 16p USB2-only

- Board/status: EVT Debug Tail / Fit / P0
- Package field: AI_Glasses_V2:USB_C_16P_MidMount
- Gate: Connector height + shell opening co-freeze
- Description: EVT USB-C - 5 V sink + USB2 OTG (no USB3/DP). For MaskROM/ADB/firmware/lab supply.
- Schematic nets: VBUS->VBUS_RAW, GND->GND, DP->USB2_DP, DM->USB2_DM, CC1->USB_CC1, CC2->USB_CC2

### U24 / C036 - TPD2E001

- Board/status: EVT Debug Tail / Fit / P0
- Package field: Package_TO_SOT_SMD:SOT-23-3
- Gate: Keep ~90 ohm diff + continuous ref gnd
- Description: USB2 ESD - low-cap ESD on D+/D- near the connector.
- Schematic nets: DP->USB2_DP, DM->USB2_DM, GND->GND

### R1 / C037a - 5.1k 1%

- Board/status: EVT Debug Tail / Fit / P0
- Package field: AI_Glasses_V2:R_0402
- Gate: USB-C spec
- Description: USB-C CC1 Rd - 5.1k 1% sink pulldown. LOCK value + 1% (V1 audit rule).
- Schematic nets: A->USB_CC1, B->GND

### R2 / C037b - 5.1k 1%

- Board/status: EVT Debug Tail / Fit / P0
- Package field: AI_Glasses_V2:R_0402
- Gate: USB-C spec
- Description: USB-C CC2 Rd - 5.1k 1% sink pulldown.
- Schematic nets: A->USB_CC2, B->GND

### J3 / C038 - Hirose FH26W-33S-0.3SHW(97)

- Board/status: Front Sensor Board / HOLD / P0
- Package field: AI_Glasses_V2:VERIFY_FH26W_33S_0.3SHW
- Gate: G10/G12 (camera module vendor signs 33-pin pinout, contact orientation, impedance)
- Description: 33-pin camera FPC connector - Hirose FH26W-33S-0.3SHW(97), 0.3mm pitch, bottom contact, horizontal, about 1.0mm height, for 0.2mm FPC. Carries IMX415 4-lane CSI, rails, I2C, reset/powerdown and module ID. Assembly/service connector only, not a user-cycle connector.
- Note: Pinout below follows the current project proposal and must be signed by the camera module vendor. Hinge electrical interconnect is out of scope for Chip-down EVT V2.0.
- Schematic nets: 1_GND->GND, 2_DVDD->CAM_1V1_S, 3_GND->GND, 4_AVDD->CAM_2V9_S, 5_GND->GND, 6_IOVDD->CAM_1V8_S, 7_GND->GND, 8_MCLK->CAM_MCLK, 9_GND->GND, 10_I2C_SCL->CAM_I2C_SCL, 11_I2C_SDA->CAM_I2C_SDA, 12_RESET_N->CAM_RST_L, 13_PWDN->CAM_PWDN_L, 14_FSYNC_NC->NC, 15_GND->GND, 16_MIPI_CLK_N->CSI_CLK_N, 17_MIPI_CLK_P->CSI_CLK_P, 18_GND->GND, 19_MIPI_D0_N->CSI_D0_N, 20_MIPI_D0_P->CSI_D0_P, 21_GND->GND, 22_MIPI_D1_N->CSI_D1_N, 23_MIPI_D1_P->CSI_D1_P, 24_GND->GND, 25_MIPI_D2_N->CSI_D2_N, 26_MIPI_D2_P->CSI_D2_P, 27_GND->GND, 28_MIPI_D3_N->CSI_D3_N, 29_MIPI_D3_P->CSI_D3_P, 30_GND->GND, 31_MODULE_ID->CAM_MODULE_ID, 32_NC->NC, 33_GND->GND

### J5 / C040 - U.FL / I-PEX MHF RF test connector

- Board/status: Temple Rears (batt/spkr/ant) / DNP / P0
- Package field: Connector_Coaxial:U.FL_Hirose_U.FL-R-SMT-1_Vertical
- Gate: EVT RF debug only; production prefers direct coax or soldered antenna pigtail
- Description: Micro RF connector - DNP RF debug/attach option on the shared Wi-Fi/BLE antenna feed. Do not consume production Z-height unless RF bring-up requires it.
- Schematic nets: SIG->WIFI_ANT, GND->GND

### TP1 / C041 - UART/SWD pogo pads

- Board/status: EVT Debug Tail / Fit / P0
- Package field: AI_Glasses_V2:TestPad_Set
- Gate: Voltage domain clearly labelled (no 3.3V into 1.8V IO)
- Description: UART/SWD test pads - RK3576 UART0 + nRF SWD + GND/VREF for bring-up (no connector height).
- Schematic nets: SOC_TX->SOC_DBG_TX, SOC_RX->SOC_DBG_RX, SWDIO->NRF_SWDIO, SWDCLK->NRF_SWDCLK, GND->GND

### SW1 / C042a - Power/PWRKEY

- Board/status: EVT Debug Tail / Fit / P0
- Package field: Button_Switch_SMD:SW_Push_1P1T_NO_CK_KMR2
- Gate: First chip-down must recover from boot failure
- Description: Power key - RK3576 PWRON via AON/PMIC.
- Schematic nets: A->SOC_PWRKEY, B->GND

### SW2 / C042b - Reset

- Board/status: EVT Debug Tail / Fit / P0
- Package field: Button_Switch_SMD:SW_Push_1P1T_NO_CK_KMR2
- Gate: Bring-up
- Description: Reset key - RK3576 RESET_n.
- Schematic nets: A->SOC_RESET_L, B->GND

### SW3 / C042c - MaskROM/Recovery

- Board/status: EVT Debug Tail / Fit / P0
- Package field: Button_Switch_SMD:SW_Push_1P1T_NO_CK_KMR2
- Gate: Bring-up (recover from bad boot)
- Description: MaskROM/recovery key - force USB recovery boot.
- Schematic nets: A->SOC_MASKROM_L, B->GND

### RS4 / C044-RSOC - 10 mohm 1%

- Board/status: R-Temple Compute Board / Fit / P0
- Package field: AI_Glasses_V2:R_0805_shunt
- Gate: 5-20 mohm (2A x 10m=20mV; avoid boost UVLO)
- Description: RK3576 island shunt - VSYS -> SOC_IN (I_SOC_5V).
- Schematic nets: A->VSYS, B->SOC_IN

### RS5 / C044-RWIFI - 50 mohm 1%

- Board/status: R-Temple Compute Board / Fit / P0
- Package field: AI_Glasses_V2:R_0603_shunt
- Gate: 20-100 mohm
- Description: Wi-Fi island shunt - VSYS -> WIFI_IN (I_WIFI).
- Schematic nets: A->VSYS, B->WIFI_IN

### RS6 / C044-RAUD - 50 mohm 1%

- Board/status: R-Temple Compute Board / Fit / P0
- Package field: AI_Glasses_V2:R_0603_shunt
- Gate: 20-100 mohm
- Description: Audio island shunt - VSYS -> AUDIO_IN (I_AUDIO).
- Schematic nets: A->VSYS, B->AUDIO_IN

### RS7 / C044-RC1 - 100 mohm 1%

- Board/status: Front Sensor Board / Fit / P0
- Package field: AI_Glasses_V2:R_0603_shunt
- Gate: Per-rail Kelvin (section 23/section 29); DVDD ~250mA
- Description: Camera DVDD shunt - CAM_1V1 -> CAM_1V1_S (I_CAM_1V1).
- Schematic nets: A->CAM_1V1, B->CAM_1V1_S

### RS8 / C044-RC8 - 100 mohm 1%

- Board/status: Front Sensor Board / Fit / P0
- Package field: AI_Glasses_V2:R_0402_shunt
- Gate: Per-rail Kelvin (section 23/section 29); IOVDD ~3mA
- Description: Camera IOVDD shunt - CAM_1V8_SW -> CAM_1V8_S (I_CAM_1V8).
- Schematic nets: A->CAM_1V8_SW, B->CAM_1V8_S

### RS9 / C044-RC29 - 100 mohm 1%

- Board/status: Front Sensor Board / Fit / P0
- Package field: AI_Glasses_V2:R_0603_shunt
- Gate: Per-rail Kelvin (section 23/section 29); AVDD ~156mA
- Description: Camera AVDD shunt - CAM_2V9 -> CAM_2V9_S (I_CAM_2V9).
- Schematic nets: A->CAM_2V9, B->CAM_2V9_S

### U25 / C044a - INA238 (I_BAT_TOTAL)

- Board/status: L-Temple AON/Power Board / DNP / P1
- Package field: AI_Glasses_V2:VSSOP-10
- Gate: Power Gate - EVT-A; production may keep this one
- Description: Whole-device current across RS1 (BAT_P->VBAT). Deep Off total = AON only, so it also backs the AON 20-50 mW check; nPM1300 fuel gauge cross-checks.
- Schematic nets: IN_P->BAT_P, IN_N->NPM_VBAT, SCL->I2C_AON_SCL, SDA->I2C_AON_SDA, GND->GND

### U26 / C044-ICL - INA238 (I_CELL_L)

- Board/status: Temple Rears (batt/spkr/ant) / DNP / P1
- Package field: AI_Glasses_V2:VSSOP-10
- Gate: Power Gate - EVT-A only (current-share)
- Description: Left branch current across RS2 - cell current-share vs SOC/temp.
- Schematic nets: IN_P->BATL_F, IN_N->BAT_P, SCL->I2C_AON_SCL, SDA->I2C_AON_SDA, GND->GND

### U27 / C044-ICR - INA238 (I_CELL_R)

- Board/status: Temple Rears (batt/spkr/ant) / DNP / P1
- Package field: AI_Glasses_V2:VSSOP-10
- Gate: Power Gate - EVT-A only (current-share)
- Description: Right branch current across RS3 - cell current-share vs SOC/temp.
- Schematic nets: IN_P->BATR_F, IN_N->BAT_P, SCL->I2C_AON_SCL, SDA->I2C_AON_SDA, GND->GND

### U28 / C044c - INA238 (I_SOC_5V)

- Board/status: R-Temple Compute Board / DNP / P1
- Package field: AI_Glasses_V2:VSSOP-10
- Gate: Power Gate - EVT-A only
- Description: RK3576 island monitor across RS4 - record/AI curves + wake energy.
- Schematic nets: IN_P->VSYS, IN_N->SOC_IN, SCL->I2C_AON_SCL, SDA->I2C_AON_SDA, GND->GND

### U29 / C044e - INA238 (I_WIFI)

- Board/status: R-Temple Compute Board / DNP / P1
- Package field: AI_Glasses_V2:VSSOP-10
- Gate: Power Gate - EVT-A only
- Description: Wi-Fi island monitor across RS5 - FCU760K TX avg vs 353mA peak.
- Schematic nets: IN_P->VSYS, IN_N->WIFI_IN, SCL->I2C_AON_SCL, SDA->I2C_AON_SDA, GND->GND

### U30 / C044f - INA238 (I_AUDIO)

- Board/status: R-Temple Compute Board / DNP / P1
- Package field: AI_Glasses_V2:VSSOP-10
- Gate: Power Gate - EVT-A only
- Description: Audio island monitor across RS6 - speech avg vs music peak.
- Schematic nets: IN_P->VSYS, IN_N->AUDIO_IN, SCL->I2C_AON_SCL, SDA->I2C_AON_SDA, GND->GND

### U31 / C044-IC1 - INA238 (I_CAM_1V1)

- Board/status: Front Sensor Board / DNP / P1
- Package field: AI_Glasses_V2:VSSOP-10
- Gate: Power Gate - EVT-A only
- Description: Camera DVDD monitor across RS7 - sensor core draw + off-leakage.
- Schematic nets: IN_P->CAM_1V1, IN_N->CAM_1V1_S, SCL->I2C_AON_SCL, SDA->I2C_AON_SDA, GND->GND

### U32 / C044-IC8 - INA238 (I_CAM_1V8)

- Board/status: Front Sensor Board / DNP / P1
- Package field: AI_Glasses_V2:VSSOP-10
- Gate: Power Gate - EVT-A only
- Description: Camera IOVDD monitor across RS8 - I/O draw + off-leakage.
- Schematic nets: IN_P->CAM_1V8_SW, IN_N->CAM_1V8_S, SCL->I2C_AON_SCL, SDA->I2C_AON_SDA, GND->GND

### U33 / C044-IC29 - INA238 (I_CAM_2V9)

- Board/status: Front Sensor Board / DNP / P1
- Package field: AI_Glasses_V2:VSSOP-10
- Gate: Power Gate - EVT-A only
- Description: Camera AVDD monitor across RS9 - analog draw + off-leakage.
- Schematic nets: IN_P->CAM_2V9, IN_N->CAM_2V9_S, SCL->I2C_AON_SCL, SDA->I2C_AON_SDA, GND->GND

### R11 / C046a - 100k

- Board/status: R-Temple Compute Board / Fit / P0
- Package field: AI_Glasses_V2:R_0402
- Gate: Default OFF (section 4)
- Description: SOC_PWR_EN pull-down - RK3576 boost default OFF (main SoC off at boot).
- Schematic nets: A->SOC_PWR_EN, B->GND

### R12 / C046b - 100k

- Board/status: R-Temple Compute Board / Fit / P0
- Package field: AI_Glasses_V2:R_0402
- Gate: Default OFF (section 4)
- Description: PMIC_PWRON pull-down - RK806 stays off until AON MCU sequences it.
- Schematic nets: A->PMIC_PWRON, B->GND

### R13 / C046c - 100k

- Board/status: Front Sensor Board / Fit / P0
- Package field: AI_Glasses_V2:R_0402
- Gate: Default OFF (section 4)
- Description: CAM_1V1_EN pull-down - camera core buck default OFF.
- Schematic nets: A->CAM_1V1_EN, B->GND

### R14 / C046d - 100k

- Board/status: Front Sensor Board / Fit / P0
- Package field: AI_Glasses_V2:R_0402
- Gate: Default OFF (section 4)
- Description: CAM_1V8_EN pull-down - camera I/O load switch default OFF.
- Schematic nets: A->CAM_1V8_EN, B->GND

### R15 / C046e - 100k

- Board/status: Front Sensor Board / Fit / P0
- Package field: AI_Glasses_V2:R_0402
- Gate: Default OFF (section 4)
- Description: CAM_2V9_EN pull-down - camera analog LDO default OFF.
- Schematic nets: A->CAM_2V9_EN, B->GND

### R16 / C046f - 100k

- Board/status: R-Temple Compute Board / Fit / P0
- Package field: AI_Glasses_V2:R_0402
- Gate: Default OFF (section 4)
- Description: WIFI_BUCK_EN pull-down - Wi-Fi buck default OFF.
- Schematic nets: A->WIFI_BUCK_EN, B->GND

### R17 / C046g - 100k

- Board/status: R-Temple Compute Board / Fit / P0
- Package field: AI_Glasses_V2:R_0402
- Gate: Default OFF (section 4)
- Description: WIFI_LS_EN pull-down - Wi-Fi load switch default OFF.
- Schematic nets: A->WIFI_LS_EN, B->GND

### R18 / C046h - 100k

- Board/status: R-Temple Compute Board / Fit / P0
- Package field: AI_Glasses_V2:R_0402
- Gate: Default OFF (section 4/section 9: FCU760K CHIP_EN default low)
- Description: WIFI_CHIP_EN pull-down - FCU760K held off until AON MCU enables it (pack section 9).
- Schematic nets: A->WIFI_CHIP_EN, B->GND

### R19 / C046i - 100k

- Board/status: R-Temple Compute Board / Fit / P0
- Package field: AI_Glasses_V2:R_0402
- Gate: Default OFF (section 4)
- Description: AUDIO_LS_EN pull-down - audio amp load switch default OFF.
- Schematic nets: A->AUDIO_LS_EN, B->GND

### R20 / C046j - 100k

- Board/status: R-Temple Compute Board / Fit / P0
- Package field: AI_Glasses_V2:R_0402
- Gate: Default OFF (section 4)
- Description: AUDIO_AMP_SD pull-down - MAX98360A shutdown default (amp muted at boot).
- Schematic nets: A->AUDIO_AMP_SD, B->GND

### R3 / C045a - 2.2k 1%

- Board/status: L-Temple AON/Power Board / Fit / P0
- Package field: AI_Glasses_V2:R_0402
- Gate: Confirm vs total AON bus capacitance
- Description: AON I2C SCL pull-up to AON_1V8 (nPM1300/BMI270/INA238 bus).
- Schematic nets: A->AON_1V8, B->I2C_AON_SCL

### R4 / C045b - 2.2k 1%

- Board/status: L-Temple AON/Power Board / Fit / P0
- Package field: AI_Glasses_V2:R_0402
- Gate: Confirm vs total AON bus capacitance
- Description: AON I2C SDA pull-up to AON_1V8.
- Schematic nets: A->AON_1V8, B->I2C_AON_SDA

### R5 / C045c - 2.2k 1%

- Board/status: Front Sensor Board / Fit / P0
- Package field: AI_Glasses_V2:R_0402
- Gate: Confirm vs camera bus capacitance
- Description: Camera I2C SCL pull-up to CAM_1V8_SW.
- Schematic nets: A->CAM_1V8_SW, B->CAM_I2C_SCL

### R6 / C045d - 2.2k 1%

- Board/status: Front Sensor Board / Fit / P0
- Package field: AI_Glasses_V2:R_0402
- Gate: Confirm vs camera bus capacitance
- Description: Camera I2C SDA pull-up to CAM_1V8_SW.
- Schematic nets: A->CAM_1V8_SW, B->CAM_I2C_SDA

### R9 / C045e - 2.2k 1%

- Board/status: R-Temple Compute Board / Fit / P0
- Package field: AI_Glasses_V2:R_0402
- Gate: Confirm vs SoC PMIC bus
- Description: SoC-PMIC I2C SCL pull-up to VCCIO_1V8 (RK3576<->RK806).
- Schematic nets: A->VCCIO_1V8, B->SOC_PMIC_SCL

### R10 / C045f - 2.2k 1%

- Board/status: R-Temple Compute Board / Fit / P0
- Package field: AI_Glasses_V2:R_0402
- Gate: Confirm vs SoC PMIC bus
- Description: SoC-PMIC I2C SDA pull-up to VCCIO_1V8.
- Schematic nets: A->VCCIO_1V8, B->SOC_PMIC_SDA

---
Regeneration:
`python3 v2_chipdown/scripts/generate_current_schematic_report.py`
Then render with kidoc to PDF. Do not hand-edit the PDF; update the schematic master or YAML and regenerate.
