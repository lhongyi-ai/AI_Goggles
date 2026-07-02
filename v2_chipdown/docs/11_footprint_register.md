# 11 — Footprint register (generated)

> Generated 2026-07-01 from `scripts/chipdown_bom.py`. The KiCad `Footprint` field in the generated schematic intentionally remains empty; the `Package` property below is the intended package/footprint register for layout entry.

**93 components** — 57 Fit · 18 HOLD · 16 DNP · 2 TBD. **25** entries still use `VERIFY` placeholder package names.

## Freeze rule

A P0 component may enter PCB layout only after exact manufacturer, MPN, package variant, datasheet revision/date, package drawing, official recommended land pattern, max height, temperature range, lifecycle/MOQ/supply status, schematic symbol, footprint and 3D model all match.

| BOM ID | Ref | Value | Board | Status | Package / intended footprint | Footprint readiness | Gate |
|---|---|---|---|:--:|---|---|---|
| C001 | U1 | RK3576 | R-Temple Compute Board | Fit | `AI_Glasses_V2:VERIFY_FCCSP698L_16x17` | VERIFY placeholder; not layout/fab ready | G01 (RK3576 datasheet/HDG/ballmap/DDR guide) |
| C002 | U2 | RK806S-5 QFN68 7x7x0.90mm | R-Temple Compute Board | HOLD | `AI_Glasses_V2:VERIFY_QFN68_7x7_EP5.49_P0.35` | VERIFY placeholder; not layout/fab ready | G03 (official RK806S-5 datasheet, OTP/default rails, sequence, layout guide) |
| C003 | U3 | Samsung K4U6E3S4AA-MGCL | R-Temple Compute Board | HOLD | `AI_Glasses_V2:VERIFY_FBGA200_0.65` | VERIFY placeholder; not layout/fab ready | G02 (Samsung datasheet/ball map/IBIS + Rockchip DDR AVL/init + length report) |
| C004 | U4 | Samsung KLMAG1JENB-B041 | R-Temple Compute Board | HOLD | `AI_Glasses_V2:VERIFY_BGA153` | VERIFY placeholder; not layout/fab ready | G04 (official Samsung datasheet/package + BSP boot/HS200 then HS400 validation) |
| C005 | Y1 | 24 MHz 10 ppm XTAL | R-Temple Compute Board | Fit | `AI_Glasses_V2:Crystal_SMD_3225` | candidate; verify official land pattern + 3D/height | G01 (reuse reference CL/ESR + placement distance per HDG) |
| C006 | U5 | MX25U6432F | R-Temple Compute Board | DNP | `AI_Glasses_V2:USON-8` | candidate; verify official land pattern + 3D/height | Boot flow decides whether production needs it |
| C007 | U6 | TPS61088 | R-Temple Compute Board | HOLD | `AI_Glasses_V2:VQFN-22_4.5x3.5` | candidate; verify official land pattern + 3D/height | G06/G09 (measured RK3576 boot+AI peak, soft-start, droop, thermal) |
| C008 | L1 | Coilcraft XGL4020-102MEC 1.0uH | R-Temple Compute Board | HOLD | `AI_Glasses_V2:VERIFY_L_4x4x2_XGL4020` | VERIFY placeholder; not layout/fab ready | G06/G13 (Isat/DCR/thermal pass for 5.1V 3A continuous / 4A peak boost) |
| C009 | U7 | nRF54L15-QFN48 | L-Temple AON/Power Board | Fit | `AI_Glasses_V2:QFN-48_6x6` | candidate; verify official land pattern + 3D/height | EVT-frozen (RF layout/SDK/package to freeze early) |
| C010 | U8 | nPM1300 | L-Temple AON/Power Board | HOLD | `AI_Glasses_V2:QFN_5x5` | candidate; verify official land pattern + 3D/height | G08 (AON <=25/50mW) — configure via nPM PowerUP on EK before board |
| C010b | U35 | BQ25895 | R-Temple Compute Board | HOLD | `AI_Glasses_V2:VERIFY_WQFN_24_BQ25895` | VERIFY placeholder; not layout/fab ready | Charger/power-path config, TS thresholds, 1S2P charge profile, thermal/current validation |
| C011 | U9 | NDP120 | L-Temple AON/Power Board | HOLD | `AI_Glasses_V2:VERIFY_QFN_5x5` | VERIFY placeholder; not layout/fab ready | Full datasheet + dev kit + measured listening power + NDA/licensing |
| C012 | U10 | BMI270 | L-Temple AON/Power Board | Fit | `Package_LGA:LGA-14_2.5x3mm_P0.5mm` | KiCad-library candidate; verify against MPN package drawing | Evaluate false-trigger under real frame vibration |
| C013a | MK1 | T5837 (wake mic) | Front Sensor Board | Fit | `AI_Glasses_V2:LGA-5_3.5x2.65` | candidate; verify official land pattern + 3D/height | G11 (mic coords/ports/wind/wake + AEC/beamforming) |
| C013b | MK2 | T5837 (array mic 1) | Front Sensor Board | Fit | `AI_Glasses_V2:LGA-5_3.5x2.65` | candidate; verify official land pattern + 3D/height | G11 |
| C013c | MK3 | T5837 (array mic 2) | Front Sensor Board | Fit | `AI_Glasses_V2:LGA-5_3.5x2.65` | candidate; verify official land pattern + 3D/height | G11 |
| C014 | MK4 | T5837 (4th mic) | Front Sensor Board | DNP | `AI_Glasses_V2:LGA-5_3.5x2.65` | candidate; verify official land pattern + 3D/height | G11 (populate only if array sim/proto needs it) |
| C015 | U11 | FCU760KAAMD | R-Temple Compute Board | HOLD | `AI_Glasses_V2:VERIFY_LCC_13x12.2_Quectel` | VERIFY placeholder; not layout/fab ready | G05 (Quectel HW Design + RK3576 BSP driver/firmware/enum) + official LCC land pattern |
| C015-C | C1 | 47uF 6.3V X5R | R-Temple Compute Board | Fit | `AI_Glasses_V2:C_0805` | generic passive placeholder; freeze after passive MPN/derating | Local bulk per Quectel HW Design |
| C016 | U12 | TPS62825 | R-Temple Compute Board | Fit | `AI_Glasses_V2:QFN_1.5x1.5` | candidate; verify official land pattern + 3D/height | G05/G06 (inductor/caps per module 353mA TX peak + ripple) |
| C016b | U13 | TPS22917DBVR | R-Temple Compute Board | Fit | `Package_TO_SOT_SMD:SOT-23-5` | KiCad-library candidate; verify against MPN package drawing | G05 (turn-on sequence w/ module) |
| C016c | L2 | Wi-Fi buck inductor (TBD) | R-Temple Compute Board | Fit | `AI_Glasses_V2:VERIFY_L_2x2` | VERIFY placeholder; not layout/fab ready | Per TPS62825 peak+ripple |
| C017 | J7 | Taoglas FXP840.07.0055B | Temple Rears (batt/spkr/ant) | HOLD | `AI_Glasses_V2:VERIFY_FPC_ANT_14x5` | VERIFY placeholder; not layout/fab ready | G14 (worn-state tune + antenna keep-out in full shell with battery/speaker) |
| C018 | J6 | FCU760K ANT_BT DNP test pad | Temple Rears (batt/spkr/ant) | DNP | `AI_Glasses_V2:VERIFY_ANT` | VERIFY placeholder; not layout/fab ready | Only populate if Quectel FAE + coexistence test requires the second RF port |
| C019 | U14 | Sony IMX415-AAQR-C custom module | Front Sensor Board | HOLD | `AI_Glasses_V2:VERIFY_CAM_MODULE` | VERIFY placeholder; not layout/fab ready | G10 (module lens/FOV/FPC pinout/lane/supply/timing from vendor) |
| C020 | U15 | TPS62840 | Front Sensor Board | Fit | `AI_Glasses_V2:VERIFY_WSON` | VERIFY placeholder; not layout/fab ready | Output current/noise per final module (DVDD ~250mA max + margin) |
| C020b | L3 | Cam 1V1 buck inductor (TBD) | Front Sensor Board | Fit | `AI_Glasses_V2:VERIFY_L_1.6x0.8` | VERIFY placeholder; not layout/fab ready | Per TPS62840 design |
| C021 | U16 | TLV75529PDRVR | Front Sensor Board | Fit | `AI_Glasses_V2:WSON-6_2x2` | candidate; verify official land pattern + 3D/height | Verify vs IMX415 AVDD peak (156mA) + PSRR |
| C022 | U17 | TPS22917DBVR | Front Sensor Board | Fit | `Package_TO_SOT_SMD:SOT-23-5` | KiCad-library candidate; verify against MPN package drawing | Check reverse block, ramp, QOD, logic level |
| C023a | U18 | TPD4E05U06 | Front Sensor Board | Fit | `AI_Glasses_V2:USON` | candidate; verify official land pattern + 3D/height | Low-cap array near FPC entry |
| C023b | U19 | TPD4E05U06 | Front Sensor Board | Fit | `AI_Glasses_V2:USON` | candidate; verify official land pattern + 3D/height | Low-cap array near FPC entry |
| C023c | U34 | TPD4E05U06 | Front Sensor Board | Fit | `AI_Glasses_V2:USON` | candidate; verify official land pattern + 3D/height | Low-cap array near FPC entry for 4-lane CSI |
| C024 | U20 | MAX98360A | R-Temple Compute Board | Fit | `AI_Glasses_V2:VERIFY_WLP_QFN` | VERIFY placeholder; not layout/fab ready | Verify Z/cavity/EMI/peak power |
| C024b | U21 | TPS22917DBVR | R-Temple Compute Board | Fit | `Package_TO_SOT_SMD:SOT-23-5` | KiCad-library candidate; verify against MPN package drawing | Amp must be fully power-downable (V1 lesson) |
| C025 | LS1 | CUI CMS-15113-078SP-67 | Temple Rears (batt/spkr/ant) | HOLD | `AI_Glasses_V2:VERIFY_SPK_15x11x3` | VERIFY placeholder; not layout/fab ready | Acoustic EVT: 0.3-0.5cc cavity, port/foam seal, magnet-to-antenna clearance, leak test |
| C026 | LS2 | 2nd speaker pad | Temple Rears (batt/spkr/ant) | DNP | `AI_Glasses_V2:VERIFY_SPK` | VERIFY placeholder; not layout/fab ready | Decide dual-speaker at EVT-B |
| C027 | U22 | DRV2605L | L-Temple AON/Power Board | DNP | `Package_SO:MSOP-10_3x3mm_P0.5mm` | KiCad-library candidate; verify against MPN package drawing | Vibration P1 — may DNP on first board (IMU/mic coupling) |
| C028 | M1 | LRA/ERM motor | Temple Rears (batt/spkr/ant) | DNP | `AI_Glasses_V2:VERIFY_LRA` | VERIFY placeholder; not layout/fab ready | Vibration P1 |
| C029 | BT1 | LP451165 300mAh (R) | Temple Rears (batt/spkr/ant) | HOLD | `AI_Glasses_V2:VERIFY_CELL_4.5x11x65` | VERIFY placeholder; not layout/fab ready | G07 (full datasheet, >=2C, IR, cycles, cert) |
| C030 | BT2 | LP451165 300mAh (L) | Temple Rears (batt/spkr/ant) | HOLD | `AI_Glasses_V2:VERIFY_CELL_70x12.8x5.6_maxenv` | VERIFY placeholder; not layout/fab ready | G07 |
| C031a | F1 | PTC/fuse (R branch) | Temple Rears (batt/spkr/ant) | TBD | `AI_Glasses_V2:VERIFY_FUSE` | VERIFY placeholder; not layout/fab ready | Rating from peak-current calc (> branch peak, < FPC rating) |
| C031b | F2 | PTC/fuse (L branch) | Temple Rears (batt/spkr/ant) | TBD | `AI_Glasses_V2:VERIFY_FUSE` | VERIFY placeholder; not layout/fab ready | Rating from peak-current calc |
| C032 | PCM1 | Supplier 1S2P pack PCM + protection FETs | Temple Rears (batt/spkr/ant) | HOLD | `AI_Glasses_V2:PACK_INTERNAL_NO_BOARD_FOOTPRINT` | pack-internal / harness block; no PCB land pattern to place | Pack supplier drawing: OVP/UVP/OCP/SCP thresholds, FET Rds(on), current rating, NTC placement, UN38.3/MSDS/IEC62133 |
| C033-TP | TP2 | Battery test points | Temple Rears (batt/spkr/ant) | Fit | `AI_Glasses_V2:TestPad_Set` | candidate; verify official land pattern + 3D/height | Cell/pack voltage + NTC probe access (§21) |
| C033a | RT1 | 10k NTC B=3435 1% (R cell) | Temple Rears (batt/spkr/ant) | Fit | `AI_Glasses_V2:R_0402` | generic passive placeholder; freeze after passive MPN/derating | NTC curve/package/placement matched to pack supplier + BQ25895/nPM1300 config |
| C033b | RT2 | 10k NTC B=3435 1% (L cell) | Temple Rears (batt/spkr/ant) | Fit | `AI_Glasses_V2:R_0402` | generic passive placeholder; freeze after passive MPN/derating | NTC curve/package/placement matched to pack supplier + ADC/config |
| C034 | J1 | CCP P2578MP01-06C180HT | Temple Rears (batt/spkr/ant) | HOLD | `AI_Glasses_V2:VERIFY_POGO_6P_1.8MM` | VERIFY placeholder; not layout/fab ready | USB2 eye/contact validation, current/fault/ESD, mating STEP, corrosion/cycle life |
| C034b | U36 | 5V input eFuse/OVP (MPN TBD) | R-Temple Compute Board | HOLD | `AI_Glasses_V2:VERIFY_EFUSE_OVP` | VERIFY placeholder; not layout/fab ready | Select MPN for pogo/USB VBUS surge, reverse, OVP, current limit and thermal fault |
| C035 | J2 | USB-C 16p USB2-only | EVT Debug Tail | Fit | `AI_Glasses_V2:USB_C_16P_MidMount` | candidate; verify official land pattern + 3D/height | Connector height + shell opening co-freeze |
| C036 | U24 | TPD2E001 | EVT Debug Tail | Fit | `Package_TO_SOT_SMD:SOT-23-3` | KiCad-library candidate; verify against MPN package drawing | Keep ~90 ohm diff + continuous ref gnd |
| C037a | R1 | 5.1k 1% | EVT Debug Tail | Fit | `AI_Glasses_V2:R_0402` | generic passive placeholder; freeze after passive MPN/derating | USB-C spec |
| C037b | R2 | 5.1k 1% | EVT Debug Tail | Fit | `AI_Glasses_V2:R_0402` | generic passive placeholder; freeze after passive MPN/derating | USB-C spec |
| C038 | J3 | Hirose FH26W-33S-0.3SHW(97) | Front Sensor Board | HOLD | `AI_Glasses_V2:VERIFY_FH26W_33S_0.3SHW` | VERIFY placeholder; not layout/fab ready | G10/G12 (camera module vendor signs 33-pin pinout, contact orientation, impedance) |
| C040 | J5 | U.FL / I-PEX MHF RF test connector | Temple Rears (batt/spkr/ant) | DNP | `Connector_Coaxial:U.FL_Hirose_U.FL-R-SMT-1_Vertical` | KiCad-library candidate; verify against MPN package drawing | EVT RF debug only; production prefers direct coax or soldered antenna pigtail |
| C041 | TP1 | UART/SWD pogo pads | EVT Debug Tail | Fit | `AI_Glasses_V2:TestPad_Set` | candidate; verify official land pattern + 3D/height | Voltage domain clearly labelled (no 3.3V into 1.8V IO) |
| C042a | SW1 | Power/PWRKEY | EVT Debug Tail | Fit | `Button_Switch_SMD:SW_Push_1P1T_NO_CK_KMR2` | KiCad-library candidate; verify against MPN package drawing | First chip-down must recover from boot failure |
| C042b | SW2 | Reset | EVT Debug Tail | Fit | `Button_Switch_SMD:SW_Push_1P1T_NO_CK_KMR2` | KiCad-library candidate; verify against MPN package drawing | Bring-up |
| C042c | SW3 | MaskROM/Recovery | EVT Debug Tail | Fit | `Button_Switch_SMD:SW_Push_1P1T_NO_CK_KMR2` | KiCad-library candidate; verify against MPN package drawing | Bring-up (recover from bad boot) |
| C043 | RT3 | 10k NTC B=3435 | R-Temple Compute Board | Fit | `AI_Glasses_V2:R_0402` | generic passive placeholder; freeze after passive MPN/derating | Probe position per thermal sim |
| C044-ICL | U26 | INA238 (I_CELL_L) | Temple Rears (batt/spkr/ant) | DNP | `AI_Glasses_V2:VSSOP-10` | candidate; verify official land pattern + 3D/height | Power Gate — EVT-A only (current-share) |
| C044-ICR | U27 | INA238 (I_CELL_R) | Temple Rears (batt/spkr/ant) | DNP | `AI_Glasses_V2:VSSOP-10` | candidate; verify official land pattern + 3D/height | Power Gate — EVT-A only (current-share) |
| C044-RAUD | RS6 | 50 mohm 1% | R-Temple Compute Board | Fit | `AI_Glasses_V2:R_0603_shunt` | generic passive placeholder; freeze after passive MPN/derating | 20-100 mohm |
| C044-RBAT | RS1 | 10 mohm 1% 1W | L-Temple AON/Power Board | Fit | `AI_Glasses_V2:R_1206_shunt` | generic passive placeholder; freeze after passive MPN/derating | I_BAT_TOTAL; the one production-kept sense path |
| C044-RCL | RS2 | 10 mohm 1% | Temple Rears (batt/spkr/ant) | Fit | `AI_Glasses_V2:R_0805_shunt` | generic passive placeholder; freeze after passive MPN/derating | Branch current-share (§7/§29) |
| C044-RCR | RS3 | 10 mohm 1% | Temple Rears (batt/spkr/ant) | Fit | `AI_Glasses_V2:R_0805_shunt` | generic passive placeholder; freeze after passive MPN/derating | Branch current-share (§7/§29) |
| C044-RSOC | RS4 | 10 mohm 1% | R-Temple Compute Board | Fit | `AI_Glasses_V2:R_0805_shunt` | generic passive placeholder; freeze after passive MPN/derating | 5-20 mohm (2A x 10m=20mV; avoid boost UVLO) |
| C044-RWIFI | RS5 | 50 mohm 1% | R-Temple Compute Board | Fit | `AI_Glasses_V2:R_0603_shunt` | generic passive placeholder; freeze after passive MPN/derating | 20-100 mohm |
| C044a | U25 | INA238 (I_BAT_TOTAL) | L-Temple AON/Power Board | DNP | `AI_Glasses_V2:VSSOP-10` | candidate; verify official land pattern + 3D/height | Power Gate — EVT-A; production may keep this one |
| C044c | U28 | INA238 (I_SOC_5V) | R-Temple Compute Board | DNP | `AI_Glasses_V2:VSSOP-10` | candidate; verify official land pattern + 3D/height | Power Gate — EVT-A only |
| C044e | U29 | INA238 (I_WIFI) | R-Temple Compute Board | DNP | `AI_Glasses_V2:VSSOP-10` | candidate; verify official land pattern + 3D/height | Power Gate — EVT-A only |
| C044f | U30 | INA238 (I_AUDIO) | R-Temple Compute Board | DNP | `AI_Glasses_V2:VSSOP-10` | candidate; verify official land pattern + 3D/height | Power Gate — EVT-A only |
| C045a | R3 | 2.2k 1% | L-Temple AON/Power Board | Fit | `AI_Glasses_V2:R_0402` | generic passive placeholder; freeze after passive MPN/derating | Confirm vs total AON bus capacitance |
| C045b | R4 | 2.2k 1% | L-Temple AON/Power Board | Fit | `AI_Glasses_V2:R_0402` | generic passive placeholder; freeze after passive MPN/derating | Confirm vs total AON bus capacitance |
| C045c | R5 | 2.2k 1% | Front Sensor Board | Fit | `AI_Glasses_V2:R_0402` | generic passive placeholder; freeze after passive MPN/derating | Confirm vs camera bus capacitance |
| C045d | R6 | 2.2k 1% | Front Sensor Board | Fit | `AI_Glasses_V2:R_0402` | generic passive placeholder; freeze after passive MPN/derating | Confirm vs camera bus capacitance |
| C045e | R9 | 2.2k 1% | R-Temple Compute Board | Fit | `AI_Glasses_V2:R_0402` | generic passive placeholder; freeze after passive MPN/derating | Confirm vs SoC PMIC bus |
| C045f | R10 | 2.2k 1% | R-Temple Compute Board | Fit | `AI_Glasses_V2:R_0402` | generic passive placeholder; freeze after passive MPN/derating | Confirm vs SoC PMIC bus |
| C046a | R11 | 100k | R-Temple Compute Board | Fit | `AI_Glasses_V2:R_0402` | generic passive placeholder; freeze after passive MPN/derating | Default OFF (§4) |
| C046b | R12 | 100k | R-Temple Compute Board | Fit | `AI_Glasses_V2:R_0402` | generic passive placeholder; freeze after passive MPN/derating | Default OFF (§4) |
| C046c | R13 | 100k | Front Sensor Board | Fit | `AI_Glasses_V2:R_0402` | generic passive placeholder; freeze after passive MPN/derating | Default OFF (§4) |
| C046d | R14 | 100k | Front Sensor Board | Fit | `AI_Glasses_V2:R_0402` | generic passive placeholder; freeze after passive MPN/derating | Default OFF (§4) |
| C046e | R15 | 100k | Front Sensor Board | Fit | `AI_Glasses_V2:R_0402` | generic passive placeholder; freeze after passive MPN/derating | Default OFF (§4) |
| C046f | R16 | 100k | R-Temple Compute Board | Fit | `AI_Glasses_V2:R_0402` | generic passive placeholder; freeze after passive MPN/derating | Default OFF (§4) |
| C046g | R17 | 100k | R-Temple Compute Board | Fit | `AI_Glasses_V2:R_0402` | generic passive placeholder; freeze after passive MPN/derating | Default OFF (§4) |
| C046h | R18 | 100k | R-Temple Compute Board | Fit | `AI_Glasses_V2:R_0402` | generic passive placeholder; freeze after passive MPN/derating | Default OFF (§4/§9: FCU760K CHIP_EN default low) |
| C046i | R19 | 100k | R-Temple Compute Board | Fit | `AI_Glasses_V2:R_0402` | generic passive placeholder; freeze after passive MPN/derating | Default OFF (§4) |
| C046j | R20 | 100k | R-Temple Compute Board | Fit | `AI_Glasses_V2:R_0402` | generic passive placeholder; freeze after passive MPN/derating | Default OFF (§4) |
| C044-IC1 | U31 | INA238 (I_CAM_1V1) | Front Sensor Board | DNP | `AI_Glasses_V2:VSSOP-10` | candidate; verify official land pattern + 3D/height | Power Gate — EVT-A only |
| C044-RC1 | RS7 | 100 mohm 1% | Front Sensor Board | Fit | `AI_Glasses_V2:R_0603_shunt` | generic passive placeholder; freeze after passive MPN/derating | Per-rail Kelvin (§23/§29); DVDD ~250mA |
| C044-IC8 | U32 | INA238 (I_CAM_1V8) | Front Sensor Board | DNP | `AI_Glasses_V2:VSSOP-10` | candidate; verify official land pattern + 3D/height | Power Gate — EVT-A only |
| C044-RC8 | RS8 | 100 mohm 1% | Front Sensor Board | Fit | `AI_Glasses_V2:R_0402_shunt` | generic passive placeholder; freeze after passive MPN/derating | Per-rail Kelvin (§23/§29); IOVDD ~3mA |
| C044-IC29 | U33 | INA238 (I_CAM_2V9) | Front Sensor Board | DNP | `AI_Glasses_V2:VSSOP-10` | candidate; verify official land pattern + 3D/height | Power Gate — EVT-A only |
| C044-RC29 | RS9 | 100 mohm 1% | Front Sensor Board | Fit | `AI_Glasses_V2:R_0603_shunt` | generic passive placeholder; freeze after passive MPN/derating | Per-rail Kelvin (§23/§29); AVDD ~156mA |

## Layout implication

- `VERIFY_*` entries are deliberate blockers, not approved generic footprints.
- HOLD parts keep their package names only as placement-envelope candidates until official drawings land.
- DNP footprints may be placed for EVT flexibility, but their pads must not compromise impedance, RF, acoustic ports or battery clearance.
