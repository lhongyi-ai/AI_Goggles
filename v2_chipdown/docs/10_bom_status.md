# 10 — BOM freeze status (generated)

> Generated 2026-07-01 from `scripts/chipdown_bom.py`. Do not hand-edit. Legend: **Fit** first-build populate · **DNP** land only · **HOLD** candidate, blocked on a gate · **TBD** MPN/spec undecided.

**93 components** — 57 Fit · 18 HOLD · 16 DNP · 2 TBD. 133 nets.

Related generated gates: [08 signal dictionary](08_signal_dictionary.md), [09 power-domain isolation](09_power_domain_isolation_matrix.md), [11 footprint register](11_footprint_register.md), [12 layout-entry status](12_layout_entry_gate_status.md), plus [13 Phase 1.5 floorplan](13_mechanical_electrical_floorplan.md).

## R-Temple Compute Board (33)

| BOM ID | Ref | Value | Pri | Status | Gate to close |
|---|---|---|---|:--:|---|
| C001 | U1 | RK3576 | P0 | Fit | G01 (RK3576 datasheet/HDG/ballmap/DDR guide) |
| C002 | U2 | RK806S-5 QFN68 7x7x0.90mm | P0 | HOLD | G03 (official RK806S-5 datasheet, OTP/default rails, sequence, layout guide) |
| C003 | U3 | Samsung K4U6E3S4AA-MGCL | P0 | HOLD | G02 (Samsung datasheet/ball map/IBIS + Rockchip DDR AVL/init + length report) |
| C004 | U4 | Samsung KLMAG1JENB-B041 | P0 | HOLD | G04 (official Samsung datasheet/package + BSP boot/HS200 then HS400 validation) |
| C005 | Y1 | 24 MHz 10 ppm XTAL | P0 | Fit | G01 (reuse reference CL/ESR + placement distance per HDG) |
| C006 | U5 | MX25U6432F | P1 | DNP | Boot flow decides whether production needs it |
| C007 | U6 | TPS61088 | P0 | HOLD | G06/G09 (measured RK3576 boot+AI peak, soft-start, droop, thermal) |
| C008 | L1 | Coilcraft XGL4020-102MEC 1.0uH | P0 | HOLD | G06/G13 (Isat/DCR/thermal pass for 5.1V 3A continuous / 4A peak boost) |
| C010b | U35 | BQ25895 | P0 | HOLD | Charger/power-path config, TS thresholds, 1S2P charge profile, thermal/current validation |
| C015 | U11 | FCU760KAAMD | P0 | HOLD | G05 (Quectel HW Design + RK3576 BSP driver/firmware/enum) + official LCC land pattern |
| C015-C | C1 | 47uF 6.3V X5R | P0 | Fit | Local bulk per Quectel HW Design |
| C016 | U12 | TPS62825 | P0 | Fit | G05/G06 (inductor/caps per module 353mA TX peak + ripple) |
| C016b | U13 | TPS22917DBVR | P0 | Fit | G05 (turn-on sequence w/ module) |
| C016c | L2 | Wi-Fi buck inductor (TBD) | P0 | Fit | Per TPS62825 peak+ripple |
| C024 | U20 | MAX98360A | P0 | Fit | Verify Z/cavity/EMI/peak power |
| C024b | U21 | TPS22917DBVR | P0 | Fit | Amp must be fully power-downable (V1 lesson) |
| C034b | U36 | 5V input eFuse/OVP (MPN TBD) | P0 | HOLD | Select MPN for pogo/USB VBUS surge, reverse, OVP, current limit and thermal fault |
| C043 | RT3 | 10k NTC B=3435 | P0 | Fit | Probe position per thermal sim |
| C044-RAUD | RS6 | 50 mohm 1% | P0 | Fit | 20-100 mohm |
| C044-RSOC | RS4 | 10 mohm 1% | P0 | Fit | 5-20 mohm (2A x 10m=20mV; avoid boost UVLO) |
| C044-RWIFI | RS5 | 50 mohm 1% | P0 | Fit | 20-100 mohm |
| C044c | U28 | INA238 (I_SOC_5V) | P1 | DNP | Power Gate — EVT-A only |
| C044e | U29 | INA238 (I_WIFI) | P1 | DNP | Power Gate — EVT-A only |
| C044f | U30 | INA238 (I_AUDIO) | P1 | DNP | Power Gate — EVT-A only |
| C045e | R9 | 2.2k 1% | P0 | Fit | Confirm vs SoC PMIC bus |
| C045f | R10 | 2.2k 1% | P0 | Fit | Confirm vs SoC PMIC bus |
| C046a | R11 | 100k | P0 | Fit | Default OFF (§4) |
| C046b | R12 | 100k | P0 | Fit | Default OFF (§4) |
| C046f | R16 | 100k | P0 | Fit | Default OFF (§4) |
| C046g | R17 | 100k | P0 | Fit | Default OFF (§4) |
| C046h | R18 | 100k | P0 | Fit | Default OFF (§4/§9: FCU760K CHIP_EN default low) |
| C046i | R19 | 100k | P0 | Fit | Default OFF (§4) |
| C046j | R20 | 100k | P0 | Fit | Default OFF (§4) |

## L-Temple AON/Power Board (9)

| BOM ID | Ref | Value | Pri | Status | Gate to close |
|---|---|---|---|:--:|---|
| C009 | U7 | nRF54L15-QFN48 | P0 | Fit | EVT-frozen (RF layout/SDK/package to freeze early) |
| C010 | U8 | nPM1300 | P0 | HOLD | G08 (AON <=25/50mW) — configure via nPM PowerUP on EK before board |
| C011 | U9 | NDP120 | P0 | HOLD | Full datasheet + dev kit + measured listening power + NDA/licensing |
| C012 | U10 | BMI270 | P0 | Fit | Evaluate false-trigger under real frame vibration |
| C027 | U22 | DRV2605L | P1 | DNP | Vibration P1 — may DNP on first board (IMU/mic coupling) |
| C044-RBAT | RS1 | 10 mohm 1% 1W | P0 | Fit | I_BAT_TOTAL; the one production-kept sense path |
| C044a | U25 | INA238 (I_BAT_TOTAL) | P1 | DNP | Power Gate — EVT-A; production may keep this one |
| C045a | R3 | 2.2k 1% | P0 | Fit | Confirm vs total AON bus capacitance |
| C045b | R4 | 2.2k 1% | P0 | Fit | Confirm vs total AON bus capacitance |

## Front Sensor Board (24)

| BOM ID | Ref | Value | Pri | Status | Gate to close |
|---|---|---|---|:--:|---|
| C013a | MK1 | T5837 (wake mic) | P0 | Fit | G11 (mic coords/ports/wind/wake + AEC/beamforming) |
| C013b | MK2 | T5837 (array mic 1) | P0 | Fit | G11 |
| C013c | MK3 | T5837 (array mic 2) | P0 | Fit | G11 |
| C014 | MK4 | T5837 (4th mic) | P1 | DNP | G11 (populate only if array sim/proto needs it) |
| C019 | U14 | Sony IMX415-AAQR-C custom module | P0 | HOLD | G10 (module lens/FOV/FPC pinout/lane/supply/timing from vendor) |
| C020 | U15 | TPS62840 | P0 | Fit | Output current/noise per final module (DVDD ~250mA max + margin) |
| C020b | L3 | Cam 1V1 buck inductor (TBD) | P0 | Fit | Per TPS62840 design |
| C021 | U16 | TLV75529PDRVR | P0 | Fit | Verify vs IMX415 AVDD peak (156mA) + PSRR |
| C022 | U17 | TPS22917DBVR | P0 | Fit | Check reverse block, ramp, QOD, logic level |
| C023a | U18 | TPD4E05U06 | P0 | Fit | Low-cap array near FPC entry |
| C023b | U19 | TPD4E05U06 | P0 | Fit | Low-cap array near FPC entry |
| C023c | U34 | TPD4E05U06 | P0 | Fit | Low-cap array near FPC entry for 4-lane CSI |
| C038 | J3 | Hirose FH26W-33S-0.3SHW(97) | P0 | HOLD | G10/G12 (camera module vendor signs 33-pin pinout, contact orientation, impedance) |
| C045c | R5 | 2.2k 1% | P0 | Fit | Confirm vs camera bus capacitance |
| C045d | R6 | 2.2k 1% | P0 | Fit | Confirm vs camera bus capacitance |
| C046c | R13 | 100k | P0 | Fit | Default OFF (§4) |
| C046d | R14 | 100k | P0 | Fit | Default OFF (§4) |
| C046e | R15 | 100k | P0 | Fit | Default OFF (§4) |
| C044-IC1 | U31 | INA238 (I_CAM_1V1) | P1 | DNP | Power Gate — EVT-A only |
| C044-RC1 | RS7 | 100 mohm 1% | P0 | Fit | Per-rail Kelvin (§23/§29); DVDD ~250mA |
| C044-IC8 | U32 | INA238 (I_CAM_1V8) | P1 | DNP | Power Gate — EVT-A only |
| C044-RC8 | RS8 | 100 mohm 1% | P0 | Fit | Per-rail Kelvin (§23/§29); IOVDD ~3mA |
| C044-IC29 | U33 | INA238 (I_CAM_2V9) | P1 | DNP | Power Gate — EVT-A only |
| C044-RC29 | RS9 | 100 mohm 1% | P0 | Fit | Per-rail Kelvin (§23/§29); AVDD ~156mA |

## Temple Rears (batt/spkr/ant) (19)

| BOM ID | Ref | Value | Pri | Status | Gate to close |
|---|---|---|---|:--:|---|
| C017 | J7 | Taoglas FXP840.07.0055B | P0 | HOLD | G14 (worn-state tune + antenna keep-out in full shell with battery/speaker) |
| C018 | J6 | FCU760K ANT_BT DNP test pad | P0 | DNP | Only populate if Quectel FAE + coexistence test requires the second RF port |
| C025 | LS1 | CUI CMS-15113-078SP-67 | P0 | HOLD | Acoustic EVT: 0.3-0.5cc cavity, port/foam seal, magnet-to-antenna clearance, leak test |
| C026 | LS2 | 2nd speaker pad | P1 | DNP | Decide dual-speaker at EVT-B |
| C028 | M1 | LRA/ERM motor | P1 | DNP | Vibration P1 |
| C029 | BT1 | LP451165 300mAh (R) | P0 | HOLD | G07 (full datasheet, >=2C, IR, cycles, cert) |
| C030 | BT2 | LP451165 300mAh (L) | P0 | HOLD | G07 |
| C031a | F1 | PTC/fuse (R branch) | P0 | TBD | Rating from peak-current calc (> branch peak, < FPC rating) |
| C031b | F2 | PTC/fuse (L branch) | P0 | TBD | Rating from peak-current calc |
| C032 | PCM1 | Supplier 1S2P pack PCM + protection FETs | P0 | HOLD | Pack supplier drawing: OVP/UVP/OCP/SCP thresholds, FET Rds(on), current rating, NTC placement, UN38.3/MSDS/IEC62133 |
| C033-TP | TP2 | Battery test points | P0 | Fit | Cell/pack voltage + NTC probe access (§21) |
| C033a | RT1 | 10k NTC B=3435 1% (R cell) | P0 | Fit | NTC curve/package/placement matched to pack supplier + BQ25895/nPM1300 config |
| C033b | RT2 | 10k NTC B=3435 1% (L cell) | P0 | Fit | NTC curve/package/placement matched to pack supplier + ADC/config |
| C034 | J1 | CCP P2578MP01-06C180HT | P0 | HOLD | USB2 eye/contact validation, current/fault/ESD, mating STEP, corrosion/cycle life |
| C040 | J5 | U.FL / I-PEX MHF RF test connector | P0 | DNP | EVT RF debug only; production prefers direct coax or soldered antenna pigtail |
| C044-ICL | U26 | INA238 (I_CELL_L) | P1 | DNP | Power Gate — EVT-A only (current-share) |
| C044-ICR | U27 | INA238 (I_CELL_R) | P1 | DNP | Power Gate — EVT-A only (current-share) |
| C044-RCL | RS2 | 10 mohm 1% | P0 | Fit | Branch current-share (§7/§29) |
| C044-RCR | RS3 | 10 mohm 1% | P0 | Fit | Branch current-share (§7/§29) |

## EVT Debug Tail (8)

| BOM ID | Ref | Value | Pri | Status | Gate to close |
|---|---|---|---|:--:|---|
| C035 | J2 | USB-C 16p USB2-only | P0 | Fit | Connector height + shell opening co-freeze |
| C036 | U24 | TPD2E001 | P0 | Fit | Keep ~90 ohm diff + continuous ref gnd |
| C037a | R1 | 5.1k 1% | P0 | Fit | USB-C spec |
| C037b | R2 | 5.1k 1% | P0 | Fit | USB-C spec |
| C041 | TP1 | UART/SWD pogo pads | P0 | Fit | Voltage domain clearly labelled (no 3.3V into 1.8V IO) |
| C042a | SW1 | Power/PWRKEY | P0 | Fit | First chip-down must recover from boot failure |
| C042b | SW2 | Reset | P0 | Fit | Bring-up |
| C042c | SW3 | MaskROM/Recovery | P0 | Fit | Bring-up (recover from bad boot) |

