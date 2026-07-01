# 10 — BOM freeze status (generated)

> Generated 2026-07-01 from `scripts/chipdown_bom.py`. Do not hand-edit. Legend: **Fit** first-build populate · **DNP** land only · **HOLD** candidate, blocked on a gate · **TBD** MPN/spec undecided.

**96 components** — 58 Fit · 12 HOLD · 19 DNP · 7 TBD. 127 nets.

Related generated gates: [08 signal dictionary](08_signal_dictionary.md), [09 power-domain isolation](09_power_domain_isolation_matrix.md), [11 footprint register](11_footprint_register.md), [12 layout-entry status](12_layout_entry_gate_status.md).

## R-Temple Compute Board (31)

| BOM ID | Ref | Value | Pri | Status | Gate to close |
|---|---|---|---|:--:|---|
| C001 | U1 | RK3576 | P0 | Fit | G01 (RK3576 datasheet/HDG/ballmap/DDR guide) |
| C002 | U2 | RK806S-5 | P0 | HOLD | G03 (RK806S MPN/inductors/caps/timing per Radxa/Rockchip FAE) |
| C003 | U3 | LPDDR4X 4GB (MPN TBD) | P0 | HOLD | G02 (LPDDR4X MPN/topology/placement, DDR review + length report) |
| C004 | U4 | eMMC 5.1 32GB (MPN TBD) | P0 | HOLD | G04 (eMMC MPN + BSP/bootloader; cold-boot + power-loss recovery) |
| C005 | Y1 | 24 MHz 10 ppm XTAL | P0 | Fit | G01 (reuse reference CL/ESR + placement distance per HDG) |
| C006 | U5 | MX25U6432F | P1 | DNP | Boot flow decides whether production needs it |
| C007 | U6 | TPS61088 | P0 | HOLD | G06/G09 (measured RK3576 boot+AI peak, soft-start, droop, thermal) |
| C008 | L1 | Boost inductor (TBD) | P0 | TBD | G06/G13 (Isat covers boot+AI peak; height <=2mm; thermal) |
| C015 | U11 | FCU760KAAMD | P0 | HOLD | G05 (Quectel HW Design + RK3576 BSP driver/firmware/enum) + official LCC land pattern |
| C015-C | C1 | 47uF 6.3V X5R | P0 | Fit | Local bulk per Quectel HW Design |
| C016 | U12 | TPS62825 | P0 | Fit | G05/G06 (inductor/caps per module 353mA TX peak + ripple) |
| C016b | U13 | TPS22917DBVR | P0 | Fit | G05 (turn-on sequence w/ module) |
| C016c | L2 | Wi-Fi buck inductor (TBD) | P0 | Fit | Per TPS62825 peak+ripple |
| C024 | U20 | MAX98360A | P0 | Fit | Verify Z/cavity/EMI/peak power |
| C024b | U21 | TPS22917DBVR | P0 | Fit | Amp must be fully power-downable (V1 lesson) |
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

## L-Temple AON/Power Board (15)

| BOM ID | Ref | Value | Pri | Status | Gate to close |
|---|---|---|---|:--:|---|
| C009 | U7 | nRF54L15-QFN48 | P0 | Fit | EVT-frozen (RF layout/SDK/package to freeze early) |
| C010 | U8 | nPM1300 | P0 | HOLD | G08 (AON <=25/50mW) — configure via nPM PowerUP on EK before board |
| C011 | U9 | NDP120 | P0 | HOLD | Full datasheet + dev kit + measured listening power + NDA/licensing |
| C012 | U10 | BMI270 | P0 | Fit | Evaluate false-trigger under real frame vibration |
| C027 | U22 | DRV2605L | P1 | DNP | Vibration P1 — may DNP on first board (IMU/mic coupling) |
| C032 | U23 | BQ2970 | P0 | DNP | Keep ONE protection scheme; confirm suffix OVP/UVP/OCP vs nPM1300/boost UVLO (§17) |
| C032-BYP | R21 | 0R (pack-PCM baseline) | P0 | Fit | Populate 0R OR discrete protection, never both (§17) |
| C032-Cv | C2 | 0.1uF | P0 | DNP | Per BQ2970 app |
| C032-Q | Q1 | Dual N-MOSFET (b2b) | P0 | DNP | Vds/RDSon/Vgs/peak per BQ2970 app (§17) |
| C032-Rm | R23 | 2k | P0 | DNP | Per BQ2970 app (V- sense) |
| C032-Rv | R22 | 330R | P0 | DNP | Per BQ2970 app |
| C044-RBAT | RS1 | 10 mohm 1% 1W | P0 | Fit | I_BAT_TOTAL; the one production-kept sense path |
| C044a | U25 | INA238 (I_BAT_TOTAL) | P1 | DNP | Power Gate — EVT-A; production may keep this one |
| C045a | R3 | 2.2k 1% | P0 | Fit | Confirm vs total AON bus capacitance |
| C045b | R4 | 2.2k 1% | P0 | Fit | Confirm vs total AON bus capacitance |

## Front Sensor Board (23)

| BOM ID | Ref | Value | Pri | Status | Gate to close |
|---|---|---|---|:--:|---|
| C013a | MK1 | T5837 (wake mic) | P0 | Fit | G11 (mic coords/ports/wind/wake + AEC/beamforming) |
| C013b | MK2 | T5837 (array mic 1) | P0 | Fit | G11 |
| C013c | MK3 | T5837 (array mic 2) | P0 | Fit | G11 |
| C014 | MK4 | T5837 (4th mic) | P1 | DNP | G11 (populate only if array sim/proto needs it) |
| C019 | U14 | IMX415-AAQR module (custom FPC) | P0 | HOLD | G10 (module lens/FOV/FPC pinout/lane/supply/timing from vendor) |
| C020 | U15 | TPS62840 | P0 | Fit | Output current/noise per final module (DVDD ~250mA max + margin) |
| C020b | L3 | Cam 1V1 buck inductor (TBD) | P0 | Fit | Per TPS62840 design |
| C021 | U16 | TLV75529PDRVR | P0 | Fit | Verify vs IMX415 AVDD peak (156mA) + PSRR |
| C022 | U17 | TPS22917DBVR | P0 | Fit | Check reverse block, ramp, QOD, logic level |
| C023a | U18 | TPD4E05U06 | P0 | Fit | Low-cap array near FPC entry |
| C023b | U19 | TPD4E05U06 | P0 | Fit | Low-cap array near FPC entry |
| C038 | J3 | Hirose FH26W 0.3mm FPC | P0 | HOLD | G12 (pin count from final cam lane/mic/power split) |
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
| C017 | J7 | Wi-Fi 2.4/5 GHz FPC ant | P0 | TBD | Head-loaded RSSI/throughput/SAR; keep-out |
| C018 | J6 | BLE 2.4 GHz FPC/PCB ant | P0 | TBD | Worn-state tuning; clear of battery/metal |
| C025 | LS1 | 8 ohm 0.5-1 W speaker | P0 | TBD | MPN after acoustic cavity/volume/leak test |
| C026 | LS2 | 2nd speaker pad | P1 | DNP | Decide dual-speaker at EVT-B |
| C028 | M1 | LRA/ERM motor | P1 | DNP | Vibration P1 |
| C029 | BT1 | LP451165 300mAh (R) | P0 | HOLD | G07 (full datasheet, >=2C, IR, cycles, cert) |
| C030 | BT2 | LP451165 300mAh (L) | P0 | HOLD | G07 |
| C031a | F1 | PTC/fuse (R branch) | P0 | TBD | Rating from peak-current calc (> branch peak, < FPC rating) |
| C031b | F2 | PTC/fuse (L branch) | P0 | TBD | Rating from peak-current calc |
| C033-TP | TP2 | Battery test points | P0 | Fit | Cell/pack voltage + NTC probe access (§21) |
| C033a | RT1 | 10k NTC (R cell) | P0 | Fit | NTC curve matched to nPM1300 charger config |
| C033b | RT2 | 10k NTC (L cell) | P0 | Fit | NTC curve matched to nPM1300 charger config |
| C034 | J1 | Magnetic pogo 4-6p | P0 | TBD | Magnet direction, sweat corrosion, short, cycle life |
| C039 | J4 | Custom hinge FPC 6-10mm | P0 | HOLD | G12 (impedance, bend radius, life, hinge interference) |
| C040 | J5 | U.FL / I-PEX MHF | P0 | Fit | Connector height + mating life |
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

