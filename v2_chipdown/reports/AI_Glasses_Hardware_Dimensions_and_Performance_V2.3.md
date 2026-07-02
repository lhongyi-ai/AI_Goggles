# AI Glasses Hardware Dimensions and Performance V2.3

Generated: 2026-07-01

This report is generated from the current schematic/BOM plus the single mechanical database. Current schematic wins over older PDFs. Numbers without official package drawings remain HOLD/TBD/PROVISIONAL.

## Executive Summary

- Normal thin optical frames do not fit this RK3576 chip-down architecture.
- Thick smart-glasses / sports-sunglasses temples can conditionally fit if Phase 1.5 envelopes are met.
- AON and compute boards intentionally contain multiple ICs: they are real PCB assemblies, not overlapping solid objects.
- Current PCB layout is not released. KiCad currently has no V2 `.kicad_pcb`; DRC is not applicable yet.
- The biggest risks before PCB layout are battery/FPC current safety, DDR/HDI routability, antenna keep-out, camera module choice, and Z-height tolerance stack.

## Current Power States

| State | Current model | Target / use case |
|---|---:|---|
| Deep Off / AON only | 22 mW | target 20-50 mW |
| Quick Standby | 134 mW | DDR/light standby model |
| Phone-assisted safety ID | 362 mW | 3-5 h blended target |
| Mixed motion use | 450 mW | target <=500-800 mW |
| Continuous 1080p record | 1290 mW | 45-90 min product target |
| AI + record burst | 2065 mW | 30-60 min / short burst target |

## Frozen / Open Dimension Summary

| Ref | MPN / item | Board | Dims | Status | Source | Next action |
|---|---|---|---|---|---|---|
| U1 | RK3576 | R-Temple Compute Board | 16.1 x 17.2 x TBD mm | HOLD | RK3576 Brief Datasheet file | G01 (RK3576 datasheet/HDG/ballmap/DDR guide) |
| U2 | RK806S-5 | R-Temple Compute Board | TBD | HOLD | AI Glasses Hardware Dimensions V2.3 | G03 (RK806S MPN/inductors/caps/timing per Radxa/Rockchip FAE) |
| U3 | LPDDR4X 4 GB MPN TBD | R-Temple Compute Board | TBD | HOLD | AI Glasses Hardware Dimensions V2.3 | G02 (LPDDR4X MPN/topology/placement, DDR review + length report) |
| U4 | 32 GB eMMC 5.1 MPN TBD | R-Temple Compute Board | TBD | HOLD | AI Glasses Hardware Dimensions V2.3 | G04 (eMMC MPN + BSP/bootloader; cold-boot + power-loss recovery) |
| U11 | FCU760KAAMD | R-Temple Compute Board | 13.0 x 12.2 x 2.0 mm | HOLD | Quectel FCU760K Short Specification | G05 (Quectel HW Design + RK3576 BSP driver/firmware/enum) + official LCC land pattern |
| U6 | TPS61088 | R-Temple Compute Board | 4.5 x 3.5 x TBD mm | HOLD | AI Glasses Hardware Dimensions V2.3 | G06/G09 (measured RK3576 boot+AI peak, soft-start, droop, thermal) |
| L1 | shielded low-DCR power inductor TBD | R-Temple Compute Board | 5.0 x 5.0 x 2.0 mm | TBD | AI Glasses Hardware Dimensions V2.3 | G06/G13 (Isat covers boot+AI peak; height <=2mm; thermal) |
| U12 | TPS62825 | R-Temple Compute Board | 1.5 x 1.5 x TBD mm | PROVISIONAL | AI Glasses Hardware Dimensions V2.3 | G05/G06 (inductor/caps per module 353mA TX peak + ripple) |
| U20 | MAX98360A | R-Temple Compute Board | TBD | PROVISIONAL | AI Glasses Hardware Dimensions V2.3 | Verify Z/cavity/EMI/peak power |
| Y1 | 24 MHz 10 ppm crystal TBD | R-Temple Compute Board | 3.2 x 2.5 x TBD mm | PROVISIONAL | AI Glasses Hardware Dimensions V2.3 | G01 (reuse reference CL/ESR + placement distance per HDG) |
| U5 | MX25U6432F | R-Temple Compute Board | TBD | DNP | AI Glasses Hardware Dimensions V2.3 | Boot flow decides whether production needs it |
| BT1 | LP451165 300 mAh | Temple Rears (batt/spkr/ant) | 70.0 x 12.8 x 5.6 mm | HOLD | LP451165 Battery Bay Fit Check | G07 (full datasheet, >=2C, IR, cycles, cert) |
| LS1 | 8 ohm 0.5-1 W micro speaker TBD | Temple Rears (batt/spkr/ant) | TBD | TBD | Current V2 generated schematic/BOM master | MPN after acoustic cavity/volume/leak test |
| J1 | magnetic pogo 4-6 pin TBD | Temple Rears (batt/spkr/ant) | 10.0 x 3.0 x TBD mm | TBD | AI Glasses Hardware Dimensions V2.3 | Magnet direction, sweat corrosion, short, cycle life |
| J3 | FH26W series pin count TBD | Front Sensor Board | 12.0 x 3.5 x 1.0 mm | HOLD | AI Glasses Hardware Dimensions V2.3 | G12 (pin count from final cam lane/mic/power split) |
| J4 | custom 6-10 mm FPC / rigid-flex TBD | Temple Rears (batt/spkr/ant) | TBD x 6-10 x 0.10-0.18 mm | HOLD | AI Glasses Hardware Dimensions V2.3 | G12 (impedance, bend radius, life, hinge interference) |
| U7 | nRF54L15 QFN48 candidate | L-Temple AON/Power Board | 6.0 x 6.0 x 0.85 mm | PROVISIONAL | AI Glasses Hardware Dimensions V2.3 | EVT-frozen (RF layout/SDK/package to freeze early) |
| U8 | nPM1300 | L-Temple AON/Power Board | 5.0 x 5.0 x TBD mm | HOLD | AI Glasses Hardware Dimensions V2.3 | G08 (AON <=25/50mW) — configure via nPM PowerUP on EK before board |
| U9 | NDP120 QFN40 candidate | L-Temple AON/Power Board | 5.0 x 5.0 x TBD mm | HOLD | Syntiant NDP120 Product Brief | Full datasheet + dev kit + measured listening power + NDA/licensing |
| U10 | BMI270 | L-Temple AON/Power Board | 2.5 x 3.0 x 0.8 mm | PROVISIONAL | AI Glasses Hardware Dimensions V2.3 | Evaluate false-trigger under real frame vibration |
| U23 | BQ2970/BQ297xx suffix TBD | L-Temple AON/Power Board | 1.5 x 1.5 x 0.75 mm | DNP | TI BQ297xx Datasheet SLUSBU9I | Keep ONE protection scheme; confirm suffix OVP/UVP/OCP vs nPM1300/boost UVLO (§17) |
| Q1 | dual back-to-back N-MOSFET TBD | L-Temple AON/Power Board | TBD | DNP | Current V2 generated schematic/BOM master | Vds/RDSon/Vgs/peak per BQ2970 app (§17) |
| RS1 | 10 milliohm 1% 1 W shunt TBD | L-Temple AON/Power Board | TBD | PROVISIONAL | Current V2 generated schematic/BOM master | I_BAT_TOTAL; the one production-kept sense path |
| U25 | INA238 | L-Temple AON/Power Board | 3.0 x 4.9 x TBD mm | DNP | AI Glasses Hardware Dimensions V2.3 | Power Gate — EVT-A; production may keep this one |
| RT1 | 10k NTC curve TBD | Temple Rears (batt/spkr/ant) | TBD | PROVISIONAL | AI Glasses Hardware Dimensions V2.3 | NTC curve matched to nPM1300 charger config |
| BT2 | LP451165 300 mAh | Temple Rears (batt/spkr/ant) | 70.0 x 12.8 x 5.6 mm | HOLD | LP451165 Battery Bay Fit Check | G07 |
| J6 | 2.4 GHz FPC/PCB antenna TBD | Temple Rears (batt/spkr/ant) | TBD | TBD | Current V2 generated schematic/BOM master | Worn-state tuning; clear of battery/metal |
| U14 | IMX415-AAQR custom FPC module; Radxa Camera 4K AS001 is only a candidate mechanical baseline | Front Sensor Board | TBD | HOLD | Sony IMX415-AAQR-C Datasheet E19504 | G10 (module lens/FOV/FPC pinout/lane/supply/timing from vendor) |
| CAM_LENS | Radxa Camera 4K AS001 lens candidate | Virtual mechanical item | 32.5 x 32.5 x 18.0 mm | HOLD | AI Glasses Hardware Dimensions V2.3 | close gate/source data before PCB layout |
| MK1 | T5837 | Front Sensor Board | 3.5 x 2.65 x 0.98 mm | PROVISIONAL | AI Glasses Hardware Dimensions V2.3 | G11 (mic coords/ports/wind/wake + AEC/beamforming) |
| MK2 | T5837 | Front Sensor Board | 3.5 x 2.65 x 0.98 mm | PROVISIONAL | AI Glasses Hardware Dimensions V2.3 | G11 |
| MK3 | T5837 | Front Sensor Board | 3.5 x 2.65 x 0.98 mm | PROVISIONAL | AI Glasses Hardware Dimensions V2.3 | G11 |
| U15 | TPS62840 | Front Sensor Board | TBD | PROVISIONAL | AI Glasses Hardware Dimensions V2.3 | Output current/noise per final module (DVDD ~250mA max + margin) |
| U16 | TLV75529PDRVR | Front Sensor Board | 2.0 x 2.0 x TBD mm | PROVISIONAL | AI Glasses Hardware Dimensions V2.3 | Verify vs IMX415 AVDD peak (156mA) + PSRR |
| U17 | TPS22917DBVR | Front Sensor Board | 2.9 x 2.8 x TBD mm | PROVISIONAL | AI Glasses Hardware Dimensions V2.3 | Check reverse block, ramp, QOD, logic level |
| U18 | TPD4E05U06 | Front Sensor Board | 2.5 x 1.0 x TBD mm | PROVISIONAL | AI Glasses Hardware Dimensions V2.3 | Low-cap array near FPC entry |
| CAM_FPC | custom camera FPC TBD | Virtual mechanical item | TBD | HOLD | Current V2 generated schematic/BOM master | close gate/source data before PCB layout |

## Component Cards

### U1 - RK3576

- What it is: Main SoC — 8-core, 6 TOPS NPU, ISP, MIPI CSI, H.264/265. Demand-started compute island (NOT always-on). Functional block: interface pins only..
- What it does: 运行 Linux/AI/编码/ISP 等高负载任务。
- Why needed: 需要本地 AI、摄像头 ISP 和视频编码时才启动。
- Connects to: RK806S、LPDDR4X、eMMC、camera MIPI、Wi-Fi USB、audio I2S、AON UART。
- Voltage: RK806S rails from SOC_5V.
- Power: typical included in compute model; peak part of AI-burst compute row.
- Body size: 16.1 x 17.2 x TBD mm.
- Extra area: 还要去耦、fanout、DDR corridor、热扩散和测试点。
- Placement: R-Temple Compute Board; Body outline known from project BOM/PDF; full datasheet, HDG, ball map, max height, DDR guide and official land pattern still required.
- Keep away from: 天线 keep-out、电池膨胀区、高热源和不可维修的硬压位置。
- Freeze status: HOLD; footprint: NOT_FOR_FAB placeholder; not release-ready.
- Missing data: G01 (RK3576 datasheet/HDG/ballmap/DDR guide)
- Source: RK3576 Brief Datasheet file (V1.2, 2024-03-11; PDF metadata title mismatch noted), pp. 1-3, `AI_Glasses_HOLD_Closure_Pack/05_Project_References/RK3576 Brief Datasheet V1.2-20240311.pdf`.

### U2 - RK806S-5

- What it is: SoC PMIC — generates CPU/GPU/NPU/DDR/IO rails + power sequencing for RK3576. Reuse verified RK3576 power architecture; NOT for AON..
- What it does: 运行 Linux/AI/编码/ISP 等高负载任务。
- Why needed: 当前架构需要它来完成对应电源、信号、传感、射频、声学或调试功能。
- Connects to: 见 current schematic nets and board partition。
- Voltage: SOC_5V input; generates RK3576/DDR rails.
- Power: typical regulation loss included in compute model; peak TBD after rail-current budget.
- Body size: TBD.
- Extra area: 还要去耦、fanout、DDR corridor、热扩散和测试点。
- Placement: R-Temple Compute Board; Exact package, height, land pattern and rail sequence are not frozen.
- Keep away from: 天线 keep-out、电池膨胀区、高热源和不可维修的硬压位置。
- Freeze status: HOLD; footprint: NOT_FOR_FAB placeholder; not release-ready.
- Missing data: G03 (RK806S MPN/inductors/caps/timing per Radxa/Rockchip FAE)
- Source: AI Glasses Hardware Dimensions V2.3 (2026-07-01), pp. 1-10, `/Users/stanley/Downloads/AI_Glasses_Hardware_Dimensions_V2.3.pdf`.

### U3 - LPDDR4X 4 GB MPN TBD

- What it is: System memory — 4 GB LPDDR4X x32, placed adjacent to RK3576. Reuse a Rockchip/Radxa-verified MPN to lower first chip-down risk vs LPDDR5..
- What it does: 完成该功能模块在系统中的专用任务。
- Why needed: 当前架构需要它来完成对应电源、信号、传感、射频、声学或调试功能。
- Connects to: 见 current schematic nets and board partition。
- Voltage: RK806 DDR rails.
- Power: typical included in compute model; peak TBD by selected MPN.
- Body size: TBD.
- Extra area: 还要去耦、fanout、DDR corridor、热扩散和测试点。
- Placement: R-Temple Compute Board; Needs exact AVL MPN, package drawing, ball map and DDR length/escape review.
- Keep away from: 天线 keep-out、电池膨胀区、高热源和不可维修的硬压位置。
- Freeze status: HOLD; footprint: NOT_FOR_FAB placeholder; not release-ready.
- Missing data: G02 (LPDDR4X MPN/topology/placement, DDR review + length report)
- Source: AI Glasses Hardware Dimensions V2.3 (2026-07-01), pp. 1-10, `/Users/stanley/Downloads/AI_Glasses_Hardware_Dimensions_V2.3.pdf`.

### U4 - 32 GB eMMC 5.1 MPN TBD

- What it is: System storage — 32 GB eMMC 5.1 (HS200/HS400 per BSP). Small + reliable; no microSD. Holds OS, models, event clips..
- What it does: 完成该功能模块在系统中的专用任务。
- Why needed: 当前架构需要它来完成对应电源、信号、传感、射频、声学或调试功能。
- Connects to: 见 current schematic nets and board partition。
- Voltage: VCC/VCCQ from RK806 rails.
- Power: typical included in compute model; peak TBD by selected MPN.
- Body size: TBD.
- Extra area: 还要去耦、连接器、测试点、keep-out 和装配公差。
- Placement: R-Temple Compute Board; Common eMMC sizes are not freeze data; final MPN and package drawing required.
- Keep away from: 天线 keep-out、电池膨胀区、高热源和不可维修的硬压位置。
- Freeze status: HOLD; footprint: NOT_FOR_FAB placeholder; not release-ready.
- Missing data: G04 (eMMC MPN + BSP/bootloader; cold-boot + power-loss recovery)
- Source: AI Glasses Hardware Dimensions V2.3 (2026-07-01), pp. 1-10, `/Users/stanley/Downloads/AI_Glasses_Hardware_Dimensions_V2.3.pdf`.

### U11 - FCU760KAAMD

- What it is: Wi-Fi 6 + BT 5.4 module — Quectel FCU760K, LCC 13.0x12.2x2.0mm. USB2 to RK3576 host; PCM for BT audio; VBAT 3.0-3.6V (typ 3.3V), max TX 353 mA. On-demand, load-switched off..
- What it does: 完成该功能模块在系统中的专用任务。
- Why needed: 当前架构需要它来完成对应电源、信号、传感、射频、声学或调试功能。
- Connects to: WIFI_3V3、USB2 to RK3576、PCM/audio、Wi-Fi antenna。
- Voltage: VBAT 3.0-3.6 V, typ 3.3 V.
- Power: typical radio average: 80-150 mW in current model; peak 353 mA @ 3.3 V max Tx current in short spec.
- Body size: 13.0 x 12.2 x 2.0 mm.
- Extra area: 还要去耦、连接器、测试点、keep-out 和装配公差。
- Placement: R-Temple Compute Board; Module outline is known. Official hardware design guide, land pattern/3D and RK3576 driver enumeration still close G05.
- Keep away from: 天线 keep-out、电池膨胀区、高热源和不可维修的硬压位置。
- Freeze status: HOLD; footprint: NOT_FOR_FAB placeholder; not release-ready.
- Missing data: G05 (Quectel HW Design + RK3576 BSP driver/firmware/enum) + official LCC land pattern
- Source: Quectel FCU760K Short Specification (V1.1, Released, 2024), pp. 1-3, `AI_Glasses_HOLD_Closure_Pack/02_WiFi_FCU760K/Quectel_FCU760K_Short_Spec_V1.1.pdf`.

### U6 - TPS61088

- What it is: Main SoC 5 V boost — 1S -> SOC_5V for the compute island. High-current sync boost; EN from nRF54L15, PG back to nRF. Candidate/HOLD until peak measured..
- What it does: 运行 Linux/AI/编码/ISP 等高负载任务。
- Why needed: 当前架构需要它来完成对应电源、信号、传感、射频、声学或调试功能。
- Connects to: 见 current schematic nets and board partition。
- Voltage: VSYS in, SOC_5V out.
- Power: typical conversion loss in compute-island loss row; peak TBD from RK3576 boot/AI current.
- Body size: 4.5 x 3.5 x TBD mm.
- Extra area: 还要电感、输入/输出电容、反馈、热铜和高电流回路空间。
- Placement: R-Temple Compute Board; Chip size alone is insufficient; L1, input/output caps, current loop and thermal rise are the real footprint.
- Keep away from: antenna、IMU、mic、skin-side hot spot 和电池。
- Freeze status: HOLD; footprint: candidate; verify official drawing/land pattern/height before layout.
- Missing data: G06/G09 (measured RK3576 boot+AI peak, soft-start, droop, thermal)
- Source: AI Glasses Hardware Dimensions V2.3 (2026-07-01), pp. 1-10, `/Users/stanley/Downloads/AI_Glasses_Hardware_Dimensions_V2.3.pdf`.

### L1 - shielded low-DCR power inductor TBD

- What it is: Boost inductor for TPS61088 — low-DCR shielded, value per TPS61088 design. Do not freeze before transient sim/measurement..
- What it does: 完成该功能模块在系统中的专用任务。
- Why needed: 当前架构需要它来完成对应电源、信号、传感、射频、声学或调试功能。
- Connects to: 见 current schematic nets and board partition。
- Voltage: SOC_5V boost switch node.
- Power: typical loss TBD by DCR/RMS current; peak Isat must cover boot/AI peak.
- Body size: 5.0 x 5.0 x 2.0 mm.
- Extra area: 还要电感、输入/输出电容、反馈、热铜和高电流回路空间。
- Placement: R-Temple Compute Board; Target envelope only. Final MPN may grow after Isat/DCR/temperature validation.
- Keep away from: antenna、IMU、mic、skin-side hot spot 和电池。
- Freeze status: TBD; footprint: NOT_FOR_FAB placeholder; not release-ready.
- Missing data: G06/G13 (Isat covers boot+AI peak; height <=2mm; thermal)
- Source: AI Glasses Hardware Dimensions V2.3 (2026-07-01), pp. 1-10, `/Users/stanley/Downloads/AI_Glasses_Hardware_Dimensions_V2.3.pdf`.

### U12 - TPS62825

- What it is: Wi-Fi dedicated 3.3 V buck — feeds FCU760K VBAT; >=500 mA capability for the 353 mA TX peak (pack note). EN by AON MCU. Avoids routing the radio through 5 V (Phase-3 rule)..
- What it does: 完成该功能模块在系统中的专用任务。
- Why needed: 当前架构需要它来完成对应电源、信号、传感、射频、声学或调试功能。
- Connects to: 见 current schematic nets and board partition。
- Voltage: VSYS to WIFI_3V3.
- Power: typical ~5 mW loss allocation; peak sized for FCU760K Tx current.
- Body size: 1.5 x 1.5 x TBD mm.
- Extra area: 还要去耦、连接器、测试点、keep-out 和装配公差。
- Placement: R-Temple Compute Board; Needs final inductor/cap derating and land-pattern check.
- Keep away from: 天线 keep-out、电池膨胀区、高热源和不可维修的硬压位置。
- Freeze status: PROVISIONAL; footprint: candidate; verify official drawing/land pattern/height before layout.
- Missing data: G05/G06 (inductor/caps per module 353mA TX peak + ripple)
- Source: AI Glasses Hardware Dimensions V2.3 (2026-07-01), pp. 1-10, `/Users/stanley/Downloads/AI_Glasses_Hardware_Dimensions_V2.3.pdf`.

### U20 - MAX98360A

- What it is: Digital Class-D amp — I2S in, mono, low-power shutdown. Direct digital audio chain, no analog codec. Fully power-downable via load switch..
- What it does: 输出提示音或语音。
- Why needed: 当前架构需要它来完成对应电源、信号、传感、射频、声学或调试功能。
- Connects to: 见 current schematic nets and board partition。
- Voltage: AUDIO_PWR / I2S control.
- Power: typical audio average 2-3 mW electronics plus speaker output; peak depends on speaker impedance and acoustic target.
- Body size: TBD.
- Extra area: 还要去耦、连接器、测试点、keep-out 和装配公差。
- Placement: R-Temple Compute Board; Exact package and EMI/thermal/acoustic layout still need closure.
- Keep away from: 天线 keep-out、电池膨胀区、高热源和不可维修的硬压位置。
- Freeze status: PROVISIONAL; footprint: NOT_FOR_FAB placeholder; not release-ready.
- Missing data: Verify Z/cavity/EMI/peak power
- Source: AI Glasses Hardware Dimensions V2.3 (2026-07-01), pp. 1-10, `/Users/stanley/Downloads/AI_Glasses_Hardware_Dimensions_V2.3.pdf`.

### Y1 - 24 MHz 10 ppm crystal TBD

- What it is: Main clock — 24 MHz, 10 ppm; load per Rockchip reference layout..
- What it does: 完成该功能模块在系统中的专用任务。
- Why needed: 当前架构需要它来完成对应电源、信号、传感、射频、声学或调试功能。
- Connects to: 见 current schematic nets and board partition。
- Voltage: oscillator pins on RK3576.
- Power: typical passive; peak passive.
- Body size: 3.2 x 2.5 x TBD mm.
- Extra area: 还要去耦、连接器、测试点、keep-out 和装配公差。
- Placement: R-Temple Compute Board; Reference load capacitance/ESR/placement must follow RK3576 HDG.
- Keep away from: 天线 keep-out、电池膨胀区、高热源和不可维修的硬压位置。
- Freeze status: PROVISIONAL; footprint: candidate; verify official drawing/land pattern/height before layout.
- Missing data: G01 (reuse reference CL/ESR + placement distance per HDG)
- Source: AI Glasses Hardware Dimensions V2.3 (2026-07-01), pp. 1-10, `/Users/stanley/Downloads/AI_Glasses_Hardware_Dimensions_V2.3.pdf`.

### U5 - MX25U6432F

- What it is: Backup boot flash — 64 Mbit 1.8 V serial NOR on FSPI. Reserved for recovery / factory test / alt-boot; not populated on first EVT..
- What it does: 完成该功能模块在系统中的专用任务。
- Why needed: 当前架构需要它来完成对应电源、信号、传感、射频、声学或调试功能。
- Connects to: 见 current schematic nets and board partition。
- Voltage: 1.8 V SPI/QSPI.
- Power: typical DNP; peak DNP.
- Body size: TBD.
- Extra area: 还要去耦、连接器、测试点、keep-out 和装配公差。
- Placement: R-Temple Compute Board; Footprint kept only if boot flow needs external NOR.
- Keep away from: 天线 keep-out、电池膨胀区、高热源和不可维修的硬压位置。
- Freeze status: DNP; footprint: DNP; do not treat as release BOM.
- Missing data: Boot flow decides whether production needs it
- Source: AI Glasses Hardware Dimensions V2.3 (2026-07-01), pp. 1-10, `/Users/stanley/Downloads/AI_Glasses_Hardware_Dimensions_V2.3.pdf`.

### BT1 - LP451165 300 mAh

- What it is: Right cell — 3.7 V 300 mAh, 4.5x11x65 mm, high-rate custom. Right-temple weight..
- What it does: 提供整机电源和续航。
- Why needed: 右侧电池提供容量并平衡整机重量。
- Connects to: F1/RS3 branch path into BAT_P and J4/AON power path。
- Voltage: 1S Li-Po nominal 3.7 V.
- Power: typical source; peak branch current TBD by 1S2P validation.
- Body size: 70.0 x 12.8 x 5.6 mm.
- Extra area: 还要极耳/线材、NTC、泡棉、膨胀、绝缘和维修余量。
- Placement: Temple Rears (batt/spkr/ant); Use 70 x 12.8 x 5.6 mm CAD clearance envelope, not nominal 65 x 11 x 4.5 mm. Supplier drawing still required.
- Keep away from: RK3576、PMIC、boost、电感、尖锐边、螺丝、热扩散片和强压点。
- Freeze status: HOLD; footprint: NOT_FOR_FAB placeholder; not release-ready.
- Missing data: G07 (full datasheet, >=2C, IR, cycles, cert)
- Source: LP451165 Battery Bay Fit Check (project fit-check, 2026-07-01), dimensions.csv + fit-check md, `AI_Glasses_HOLD_Closure_Pack/06_Mechanical_Fit_Check/`.

### LS1 - 8 ohm 0.5-1 W micro speaker TBD

- What it is: Main speaker — first version single speaker; open acoustic unit set by temple cavity..
- What it does: 输出提示音或语音。
- Why needed: 当前架构需要它来完成对应电源、信号、传感、射频、声学或调试功能。
- Connects to: 见 current schematic nets and board partition。
- Voltage: driven by MAX98360A.
- Power: typical 13-27 mW average in model; peak 0.5-1 W acoustic part class.
- Body size: TBD.
- Extra area: 还要去耦、连接器、测试点、keep-out 和装配公差。
- Placement: Temple Rears (batt/spkr/ant); Must choose speaker MPN, magnet size, port, cavity, leak path and antenna exclusion.
- Keep away from: 天线 keep-out、电池膨胀区、高热源和不可维修的硬压位置。
- Freeze status: TBD; footprint: NOT_FOR_FAB placeholder; not release-ready.
- Missing data: MPN after acoustic cavity/volume/leak test
- Source: Current V2 generated schematic/BOM master (generated 2026-07-01), scripts/chipdown_bom.py, `v2_chipdown/scripts/chipdown_bom.py`.

### J1 - magnetic pogo 4-6 pin TBD

- What it is: Charge/data interface — magnetic pogo (5 V charge, optional USB2). Thinner + more waterproof than a temple USB-C..
- What it does: 连接板卡、电源、信号或充电/调试接口。
- Why needed: 当前架构需要它来完成对应电源、信号、传感、射频、声学或调试功能。
- Connects to: 见 current schematic nets and board partition。
- Voltage: USB_5V, GND, optional USB2/ID.
- Power: typical passive; contact I2R loss; peak charge/fault current rating TBD.
- Body size: 10.0 x 3.0 x TBD mm.
- Extra area: 还要去耦、连接器、测试点、keep-out 和装配公差。
- Placement: Temple Rears (batt/spkr/ant); Needs pin count, contact resistance, magnet polarity, corrosion, short and mating-life data.
- Keep away from: 天线 keep-out、电池膨胀区、高热源和不可维修的硬压位置。
- Freeze status: TBD; footprint: NOT_FOR_FAB placeholder; not release-ready.
- Missing data: Magnet direction, sweat corrosion, short, cycle life
- Source: AI Glasses Hardware Dimensions V2.3 (2026-07-01), pp. 1-10, `/Users/stanley/Downloads/AI_Glasses_Hardware_Dimensions_V2.3.pdf`.

### J3 - FH26W series pin count TBD

- What it is: Front<->temple high-speed FPC — carries MIPI CSI + PDM + I2C + control + camera power + GND across to the compute/AON boards. Documents the hinge-FPC pin list..
- What it does: 连接板卡、电源、信号或充电/调试接口。
- Why needed: 当前架构需要它来完成对应电源、信号、传感、射频、声学或调试功能。
- Connects to: 见 current schematic nets and board partition。
- Voltage: MIPI/PDM/I2C/CAM rails/GND.
- Power: typical passive; peak pin-current TBD.
- Body size: 12.0 x 3.5 x 1.0 mm.
- Extra area: 还要去耦、连接器、测试点、keep-out 和装配公差。
- Placement: Front Sensor Board; 35-pin length is only an example. Final pin count and contact orientation are G12 blockers.
- Keep away from: 天线 keep-out、电池膨胀区、高热源和不可维修的硬压位置。
- Freeze status: HOLD; footprint: NOT_FOR_FAB placeholder; not release-ready.
- Missing data: G12 (pin count from final cam lane/mic/power split)
- Source: AI Glasses Hardware Dimensions V2.3 (2026-07-01), pp. 1-10, `/Users/stanley/Downloads/AI_Glasses_Hardware_Dimensions_V2.3.pdf`.

### J4 - custom 6-10 mm FPC / rigid-flex TBD

- What it is: Hinge FPC (L<->R) — carries battery power path, AON UART, control lines and GND between the two temples. Enables the split-and-fold structure..
- What it does: 连接板卡、电源、信号或充电/调试接口。
- Why needed: 当前架构需要它来完成对应电源、信号、传感、射频、声学或调试功能。
- Connects to: left AON/power side and right compute/battery side。
- Voltage: BAT_P/VSYS, GND, AON UART, EN/PGOOD/fault/status.
- Power: typical passive; I2R loss; peak must carry peak and fault current safely.
- Body size: TBD x 6-10 x 0.10-0.18 mm.
- Extra area: 还要去耦、连接器、测试点、keep-out 和装配公差。
- Placement: Temple Rears (batt/spkr/ant); EVT-A can be fixed-temple cable/FPC. Folding hinge life, bend radius, stack-up and pin count remain open.
- Keep away from: 天线 keep-out、电池膨胀区、高热源和不可维修的硬压位置。
- Freeze status: HOLD; footprint: NOT_FOR_FAB placeholder; not release-ready.
- Missing data: G12 (impedance, bend radius, life, hinge interference)
- Source: AI Glasses Hardware Dimensions V2.3 (2026-07-01), pp. 1-10, `/Users/stanley/Downloads/AI_Glasses_Hardware_Dimensions_V2.3.pdf`.

### U7 - nRF54L15 QFN48 candidate

- What it is: Low-power BLE MCU — ALWAYS ON. Owns the system state machine; controls RK3576/camera/Wi-Fi/audio power ENs; talks IMU/buttons/gauge; UART to RK3576, SPI to NDP120. Turns RK3576 from an always-on host into a demand accelerator..
- What it does: 在主 SoC 断电时保持 BLE、IMU、唤醒和电源控制。
- Why needed: 它是低功耗常开大脑，负责让主 SoC 彻底断电。
- Connects to: nPM1300、NDP120、BMI270、AON I2C、J4 interconnect 和各路 enable/PGOOD。
- Voltage: AON_1V8/AON_3V3.
- Power: typical 2-8 mW allocation depending state; peak radio peak TBD.
- Body size: 6.0 x 6.0 x 0.85 mm.
- Extra area: 还要去耦、连接器、测试点、keep-out 和装配公差。
- Placement: L-Temple AON/Power Board; EVT QFN chosen for bring-up. RF layout, SDK and official package drawing still must be checked before fab.
- Keep away from: 天线 keep-out、电池膨胀区、高热源和不可维修的硬压位置。
- Freeze status: PROVISIONAL; footprint: candidate; verify official drawing/land pattern/height before layout.
- Missing data: EVT-frozen (RF layout/SDK/package to freeze early)
- Source: AI Glasses Hardware Dimensions V2.3 (2026-07-01), pp. 1-10, `/Users/stanley/Downloads/AI_Glasses_Hardware_Dimensions_V2.3.pdf`.

### U8 - nPM1300

- What it is: AON PMIC — 1S charger + Power-Path + Fuel Gauge + dual Buck + LDO/Load-Switch + Ship/Hibernate. Powers the small AON world ONLY; NOT the RK3576 peak path..
- What it does: 在主 SoC 断电时保持 BLE、IMU、唤醒和电源控制。
- Why needed: 当前架构需要它来完成对应电源、信号、传感、射频、声学或调试功能。
- Connects to: 见 current schematic nets and board partition。
- Voltage: BAT_P/USB_5V in; AON_1V8/AON_3V3 out.
- Power: typical 3-15 mW AON buck/quiescent allocation; peak charge/PMIC thermal TBD.
- Body size: 5.0 x 5.0 x TBD mm.
- Extra area: 还要去耦、连接器、测试点、keep-out 和装配公差。
- Placement: L-Temple AON/Power Board; nPM PowerUP config and measured AON <=25/50 mW target must close G08.
- Keep away from: 天线 keep-out、电池膨胀区、高热源和不可维修的硬压位置。
- Freeze status: HOLD; footprint: candidate; verify official drawing/land pattern/height before layout.
- Missing data: G08 (AON <=25/50mW) — configure via nPM PowerUP on EK before board
- Source: AI Glasses Hardware Dimensions V2.3 (2026-07-01), pp. 1-10, `/Users/stanley/Downloads/AI_Glasses_Hardware_Dimensions_V2.3.pdf`.

### U9 - NDP120 QFN40 candidate

- What it is: Always-on Audio DSP — ultra-low-power wake-word + audio front-end; wakes the MCU over GPIO. Moves voice listening off RK3576. Keep bypass + DNP capability..
- What it does: 完成该功能模块在系统中的专用任务。
- Why needed: 让语音唤醒不需要一直开 RK3576。
- Connects to: 见 current schematic nets and board partition。
- Voltage: AON rails, reset/wake to nRF54L15.
- Power: typical 12-20 mW project listening allocation; peak TBD by dev kit measurement.
- Body size: 5.0 x 5.0 x TBD mm.
- Extra area: 还要去耦、连接器、测试点、keep-out 和装配公差。
- Placement: L-Temple AON/Power Board; Product brief confirms packages and capability; full datasheet, rail map, reset straps, SDK/licensing and measured listening current still needed.
- Keep away from: 天线 keep-out、电池膨胀区、高热源和不可维修的硬压位置。
- Freeze status: HOLD; footprint: NOT_FOR_FAB placeholder; not release-ready.
- Missing data: Full datasheet + dev kit + measured listening power + NDA/licensing
- Source: Syntiant NDP120 Product Brief (V1, 2023), pp. 1-2, `AI_Glasses_HOLD_Closure_Pack/01_NDP120/NDP120_Product_Brief.pdf`.

### U10 - BMI270

- What it is: 6-axis IMU — low-power motion detect; motion-interrupt wakes the MCU. Cycling/running state ID for wearables..
- What it does: 完成该功能模块在系统中的专用任务。
- Why needed: 检测运动、姿态和佩戴状态。
- Connects to: 见 current schematic nets and board partition。
- Voltage: AON_1V8/AON_3V3.
- Power: typical 1 mW low-power motion budget; peak TBD by IMU mode.
- Body size: 2.5 x 3.0 x 0.8 mm.
- Extra area: 还要去耦、连接器、测试点、keep-out 和装配公差。
- Placement: L-Temple AON/Power Board; Current schematic uses BMI270. Placement must avoid speaker/motor vibration and high-stress zones.
- Keep away from: speaker、马达、高应力壳体筋位和剧烈振动源。
- Freeze status: PROVISIONAL; footprint: candidate; verify official drawing/land pattern/height before layout.
- Missing data: Evaluate false-trigger under real frame vibration
- Source: AI Glasses Hardware Dimensions V2.3 (2026-07-01), pp. 1-10, `/Users/stanley/Downloads/AI_Glasses_Hardware_Dimensions_V2.3.pdf`.

### U23 - BQ2970/BQ297xx suffix TBD

- What it is: 1S protection IC (fallback) — OV/UV/OC/short via two low-side back-to-back NMOS. DNP if the supplier pack integrates protection (avoid double-protection conflict, §17)..
- What it does: 提供整机电源和续航。
- Why needed: 当前架构需要它来完成对应电源、信号、传感、射频、声学或调试功能。
- Connects to: 见 current schematic nets and board partition。
- Voltage: single-cell Li-ion protection.
- Power: typical 4 uA normal, 100 nA shutdown class; peak external FET path handles current.
- Body size: 1.5 x 1.5 x 0.75 mm.
- Extra area: 还要极耳/线材、NTC、泡棉、膨胀、绝缘和维修余量。
- Placement: L-Temple AON/Power Board; DNP if supplier pack has qualified PCM. Exact suffix thresholds must match cell and nPM1300 charger.
- Keep away from: RK3576、PMIC、boost、电感、尖锐边、螺丝、热扩散片和强压点。
- Freeze status: DNP; footprint: DNP; do not treat as release BOM.
- Missing data: Keep ONE protection scheme; confirm suffix OVP/UVP/OCP vs nPM1300/boost UVLO (§17)
- Source: TI BQ297xx Datasheet SLUSBU9I (March 2014, revised August 2024), pp. 1, 3, package outline, `AI_Glasses_HOLD_Closure_Pack/03_Battery_LP451165_1S2P/TI_BQ2970_1S_Protection_Datasheet.pdf`.

### Q1 - dual back-to-back N-MOSFET TBD

- What it is: Back-to-back protection NMOS — discharge + charge FETs between CELL_NEG and pack GND; gates driven by BQ2970 DO/CO. DNP with U23..
- What it does: 提供整机电源和续航。
- Why needed: 当前架构需要它来完成对应电源、信号、传感、射频、声学或调试功能。
- Connects to: 见 current schematic nets and board partition。
- Voltage: cell negative protection path.
- Power: typical DNP; peak RDS(on), VDS and pulse current TBD.
- Body size: TBD.
- Extra area: 还要极耳/线材、NTC、泡棉、膨胀、绝缘和维修余量。
- Placement: L-Temple AON/Power Board; Only used with BQ2970 fallback. Must not be populated together with incompatible pack PCM path.
- Keep away from: RK3576、PMIC、boost、电感、尖锐边、螺丝、热扩散片和强压点。
- Freeze status: DNP; footprint: NOT_FOR_FAB placeholder; not release-ready.
- Missing data: Vds/RDSon/Vgs/peak per BQ2970 app (§17)
- Source: Current V2 generated schematic/BOM master (generated 2026-07-01), scripts/chipdown_bom.py, `v2_chipdown/scripts/chipdown_bom.py`.

### RS1 - 10 milliohm 1% 1 W shunt TBD

- What it is: Pack total shunt — BAT_P -> nPM1300 VBAT. Whole-device current (charge + discharge)..
- What it does: 完成该功能模块在系统中的专用任务。
- Why needed: 当前架构需要它来完成对应电源、信号、传感、射频、声学或调试功能。
- Connects to: 见 current schematic nets and board partition。
- Voltage: BAT_P/NPM_VBAT Kelvin sense.
- Power: typical I^2R loss; peak sized for pack current.
- Body size: TBD.
- Extra area: 还要去耦、连接器、测试点、keep-out 和装配公差。
- Placement: L-Temple AON/Power Board; Production-kept sense path; MPN, TCR, surge and pad geometry still need freeze.
- Keep away from: 天线 keep-out、电池膨胀区、高热源和不可维修的硬压位置。
- Freeze status: PROVISIONAL; footprint: candidate; verify official drawing/land pattern/height before layout.
- Missing data: I_BAT_TOTAL; the one production-kept sense path
- Source: Current V2 generated schematic/BOM master (generated 2026-07-01), scripts/chipdown_bom.py, `v2_chipdown/scripts/chipdown_bom.py`.

### U25 - INA238

- What it is: Whole-device current across RS1 (BAT_P->VBAT). Deep Off total = AON only, so it also backs the AON 20-50 mW check; nPM1300 fuel gauge cross-checks..
- What it does: 完成该功能模块在系统中的专用任务。
- Why needed: 当前架构需要它来完成对应电源、信号、传感、射频、声学或调试功能。
- Connects to: 见 current schematic nets and board partition。
- Voltage: AON I2C / shunt monitor.
- Power: typical 640 uA class when populated; peak 5 uA shutdown max class.
- Body size: 3.0 x 4.9 x TBD mm.
- Extra area: 还要去耦、连接器、测试点、keep-out 和装配公差。
- Placement: L-Temple AON/Power Board; EVT-A only unless power telemetry stays in production.
- Keep away from: 天线 keep-out、电池膨胀区、高热源和不可维修的硬压位置。
- Freeze status: DNP; footprint: DNP; do not treat as release BOM.
- Missing data: Power Gate — EVT-A; production may keep this one
- Source: AI Glasses Hardware Dimensions V2.3 (2026-07-01), pp. 1-10, `/Users/stanley/Downloads/AI_Glasses_Hardware_Dimensions_V2.3.pdf`.

### RT1 - 10k NTC curve TBD

- What it is: Right cell temperature — 10k NTC at the cell into nPM1300 NTC/AON ADC. Per-cell NTC (§15)..
- What it does: 完成该功能模块在系统中的专用任务。
- Why needed: 当前架构需要它来完成对应电源、信号、传感、射频、声学或调试功能。
- Connects to: 见 current schematic nets and board partition。
- Voltage: AON analog / nPM1300 temperature input.
- Power: typical uW class divider; peak uW class.
- Body size: TBD.
- Extra area: 还要去耦、连接器、测试点、keep-out 和装配公差。
- Placement: Temple Rears (batt/spkr/ant); Location matters more than package: place against cell body, not charger IC.
- Keep away from: 天线 keep-out、电池膨胀区、高热源和不可维修的硬压位置。
- Freeze status: PROVISIONAL; footprint: candidate; verify official drawing/land pattern/height before layout.
- Missing data: NTC curve matched to nPM1300 charger config
- Source: AI Glasses Hardware Dimensions V2.3 (2026-07-01), pp. 1-10, `/Users/stanley/Downloads/AI_Glasses_Hardware_Dimensions_V2.3.pdf`.

### BT2 - LP451165 300 mAh

- What it is: Left cell — same batch/capacity/IR-matched to the right cell. Left-temple weight. 1S2P parallel only after supplier pairing (OCV<=20mV, cap<=3%, DCIR<=10%, same lot, §20)..
- What it does: 提供整机电源和续航。
- Why needed: 左侧电池与右侧并联形成 1S2P。
- Connects to: F2/RS2 branch path into BAT_P and nPM1300。
- Voltage: 1S Li-Po nominal 3.7 V.
- Power: typical source; peak branch current TBD by 1S2P validation.
- Body size: 70.0 x 12.8 x 5.6 mm.
- Extra area: 还要极耳/线材、NTC、泡棉、膨胀、绝缘和维修余量。
- Placement: Temple Rears (batt/spkr/ant); Must be lot/capacity/DCIR matched to BT1; one cell per temple, 1S2P.
- Keep away from: RK3576、PMIC、boost、电感、尖锐边、螺丝、热扩散片和强压点。
- Freeze status: HOLD; footprint: NOT_FOR_FAB placeholder; not release-ready.
- Missing data: G07
- Source: LP451165 Battery Bay Fit Check (project fit-check, 2026-07-01), dimensions.csv + fit-check md, `AI_Glasses_HOLD_Closure_Pack/06_Mechanical_Fit_Check/`.

### J6 - 2.4 GHz FPC/PCB antenna TBD

- What it is: BLE antenna — 50 ohm, always-on. Physically separate from the Wi-Fi antenna..
- What it does: 把无线芯片的 RF 信号发射/接收出去。
- Why needed: 当前架构需要它来完成对应电源、信号、传感、射频、声学或调试功能。
- Connects to: 见 current schematic nets and board partition。
- Voltage: RF passive, 50 ohm.
- Power: typical passive; peak radio-dependent.
- Body size: TBD.
- Extra area: 还要 no-copper keep-out、塑胶窗口和 matching network。
- Placement: Temple Rears (batt/spkr/ant); Requires left-temple tail keep-out, matching and worn-state tune. Must clear battery/copper/screws/magnets.
- Keep away from: 电池、铜皮、螺丝、speaker 磁体、pogo 磁体、高电流环路。
- Freeze status: TBD; footprint: NOT_FOR_FAB placeholder; not release-ready.
- Missing data: Worn-state tuning; clear of battery/metal
- Source: Current V2 generated schematic/BOM master (generated 2026-07-01), scripts/chipdown_bom.py, `v2_chipdown/scripts/chipdown_bom.py`.

### U14 - IMX415-AAQR custom FPC module; Radxa Camera 4K AS001 is only a candidate mechanical baseline

- What it is: Main camera module — 8.46 MP, first target 1080p30/60, MIPI CSI. Custom small sensor+lens rigid island + FPC (NOT the dev module). Sensor rails (Sony datasheet): AVDD 2.9V 128/156mA, IOVDD 1.8V 3mA, DVDD 1.1V 187/250mA (~0.58W typ, ~0.77W max)..
- What it does: 采集画面或给相机供电/保护。
- Why needed: 当前架构需要它来完成对应电源、信号、传感、射频、声学或调试功能。
- Connects to: J3 FPC、CAM rails、MIPI CSI、CAM I2C/MCLK/RST/PWDN。
- Voltage: CAM_1V1, CAM_1V8_SW, CAM_2V9.
- Power: typical 250-300 mW camera row in current model; peak bare-sensor/module rail currents TBD.
- Body size: TBD.
- Extra area: 还要镜头、固定孔、FPC、ESD、供电小板和 Z-stack。
- Placement: Front Sensor Board; Current schematic says custom FPC module. The external V2.3 dimensions PDF freezes Radxa AS001 at 32.5 x 32.5 x 18.0 mm, but that is not yet schematic-aligned.
- Keep away from: 高温 regulator、电池硬压、过紧 FPC 弯折和污染源。
- Freeze status: HOLD; footprint: NOT_FOR_FAB placeholder; not release-ready.
- Missing data: G10 (module lens/FOV/FPC pinout/lane/supply/timing from vendor)
- Source: Sony IMX415-AAQR-C Datasheet E19504 (Official edition, 2019-05-21), pp. 1, 3, 97, `AI_Glasses_HOLD_Closure_Pack/04_IMX415/IMX415-AAQR-C_Datasheet_E19504.pdf`.

### CAM_LENS - Radxa Camera 4K AS001 lens candidate

- What it is: camera lens stack.
- What it does: 采集画面或给相机供电/保护。
- Why needed: 当前架构需要它来完成对应电源、信号、传感、射频、声学或调试功能。
- Connects to: 见 current schematic nets and board partition。
- Voltage: mechanical/optical.
- Power: typical passive; peak passive.
- Body size: 32.5 x 32.5 x 18.0 mm.
- Extra area: 还要镜头、固定孔、FPC、ESD、供电小板和 Z-stack。
- Placement: Virtual mechanical item; Virtual mechanical item, not in schematic. Must not replace U14 custom module unless EE/CAD approve that architecture.
- Keep away from: 高温 regulator、电池硬压、过紧 FPC 弯折和污染源。
- Freeze status: HOLD; footprint: virtual; no KiCad footprint.
- Missing data: close gate/source data before PCB layout
- Source: AI Glasses Hardware Dimensions V2.3 (2026-07-01), pp. 1-10, `/Users/stanley/Downloads/AI_Glasses_Hardware_Dimensions_V2.3.pdf`.

### MK1 - T5837

- What it is: PDM wake mic — dedicated always-on wake channel into NDP120 (AON audio domain). Deep Off must capture without RK3576..
- What it does: 完成该功能模块在系统中的专用任务。
- Why needed: 当前架构需要它来完成对应电源、信号、传感、射频、声学或调试功能。
- Connects to: 见 current schematic nets and board partition。
- Voltage: AON microphone rail/PDM.
- Power: typical 3 mW wake-mic budget; peak TBD by mode.
- Body size: 3.5 x 2.65 x 0.98 mm.
- Extra area: 还要去耦、连接器、测试点、keep-out 和装配公差。
- Placement: Front Sensor Board; Requires sound port, acoustic keep-out and wind/AEC placement review.
- Keep away from: 天线 keep-out、电池膨胀区、高热源和不可维修的硬压位置。
- Freeze status: PROVISIONAL; footprint: candidate; verify official drawing/land pattern/height before layout.
- Missing data: G11 (mic coords/ports/wind/wake + AEC/beamforming)
- Source: AI Glasses Hardware Dimensions V2.3 (2026-07-01), pp. 1-10, `/Users/stanley/Downloads/AI_Glasses_Hardware_Dimensions_V2.3.pdf`.

### MK2 - T5837

- What it is: PDM array mic 1 — into RK3576 PDM for beamforming during vision/voice tasks..
- What it does: 完成该功能模块在系统中的专用任务。
- Why needed: 当前架构需要它来完成对应电源、信号、传感、射频、声学或调试功能。
- Connects to: 见 current schematic nets and board partition。
- Voltage: camera/compute audio PDM rail.
- Power: typical array mic share in active states; peak TBD by mode.
- Body size: 3.5 x 2.65 x 0.98 mm.
- Extra area: 还要去耦、连接器、测试点、keep-out 和装配公差。
- Placement: Front Sensor Board; Mic coordinate spacing and port path remain G11.
- Keep away from: 天线 keep-out、电池膨胀区、高热源和不可维修的硬压位置。
- Freeze status: PROVISIONAL; footprint: candidate; verify official drawing/land pattern/height before layout.
- Missing data: G11
- Source: AI Glasses Hardware Dimensions V2.3 (2026-07-01), pp. 1-10, `/Users/stanley/Downloads/AI_Glasses_Hardware_Dimensions_V2.3.pdf`.

### MK3 - T5837

- What it is: PDM array mic 2 — second array channel (L/R stereo on shared PDM clock)..
- What it does: 完成该功能模块在系统中的专用任务。
- Why needed: 当前架构需要它来完成对应电源、信号、传感、射频、声学或调试功能。
- Connects to: 见 current schematic nets and board partition。
- Voltage: camera/compute audio PDM rail.
- Power: typical array mic share in active states; peak TBD by mode.
- Body size: 3.5 x 2.65 x 0.98 mm.
- Extra area: 还要去耦、连接器、测试点、keep-out 和装配公差。
- Placement: Front Sensor Board; Mic coordinate spacing and port path remain G11.
- Keep away from: 天线 keep-out、电池膨胀区、高热源和不可维修的硬压位置。
- Freeze status: PROVISIONAL; footprint: candidate; verify official drawing/land pattern/height before layout.
- Missing data: G11
- Source: AI Glasses Hardware Dimensions V2.3 (2026-07-01), pp. 1-10, `/Users/stanley/Downloads/AI_Glasses_Hardware_Dimensions_V2.3.pdf`.

### U15 - TPS62840

- What it is: Camera DVDD 1.1 V buck — ultra-low-Iq (~60 nA) buck for the sensor core (DVDD 187/250mA), up to ~750 mA. EN by AON MCU / SoC. True power-down when camera off..
- What it does: 采集画面或给相机供电/保护。
- Why needed: 当前架构需要它来完成对应电源、信号、传感、射频、声学或调试功能。
- Connects to: 见 current schematic nets and board partition。
- Voltage: CAM_1V1.
- Power: typical 15-18 mW loss allocation when camera active; peak DVDD current plus margin.
- Body size: TBD.
- Extra area: 还要镜头、固定孔、FPC、ESD、供电小板和 Z-stack。
- Placement: Front Sensor Board; Exact package and inductor/cap choices still need freeze.
- Keep away from: 高温 regulator、电池硬压、过紧 FPC 弯折和污染源。
- Freeze status: PROVISIONAL; footprint: NOT_FOR_FAB placeholder; not release-ready.
- Missing data: Output current/noise per final module (DVDD ~250mA max + margin)
- Source: AI Glasses Hardware Dimensions V2.3 (2026-07-01), pp. 1-10, `/Users/stanley/Downloads/AI_Glasses_Hardware_Dimensions_V2.3.pdf`.

### U16 - TLV75529PDRVR

- What it is: Camera AVDD 2.9 V LDO — 500 mA low-noise analog supply (AVDD 128/156mA). Low-noise LDO, NOT a series resistor off 3.3V (pack §23)..
- What it does: 采集画面或给相机供电/保护。
- Why needed: 当前架构需要它来完成对应电源、信号、传感、射频、声学或调试功能。
- Connects to: 见 current schematic nets and board partition。
- Voltage: CAM_2V9.
- Power: typical 14-16 mW loss allocation when camera active; peak IMX415 AVDD current plus thermal.
- Body size: 2.0 x 2.0 x TBD mm.
- Extra area: 还要镜头、固定孔、FPC、ESD、供电小板和 Z-stack。
- Placement: Front Sensor Board; Verify package suffix and PSRR/noise versus final camera module.
- Keep away from: 高温 regulator、电池硬压、过紧 FPC 弯折和污染源。
- Freeze status: PROVISIONAL; footprint: candidate; verify official drawing/land pattern/height before layout.
- Missing data: Verify vs IMX415 AVDD peak (156mA) + PSRR
- Source: AI Glasses Hardware Dimensions V2.3 (2026-07-01), pp. 1-10, `/Users/stanley/Downloads/AI_Glasses_Hardware_Dimensions_V2.3.pdf`.

### U17 - TPS22917DBVR

- What it is: Camera IOVDD 1.8 V load switch / isolation — low-leak switch from AON_1V8 for camera I/O (IOVDD ~3mA); Quick-Output-Discharge kills reverse feed when camera off (§24)..
- What it does: 采集画面或给相机供电/保护。
- Why needed: 当前架构需要它来完成对应电源、信号、传感、射频、声学或调试功能。
- Connects to: 见 current schematic nets and board partition。
- Voltage: AON_1V8 to CAM_1V8_SW.
- Power: typical ~1 mW loss allocation; peak IOVDD current, reverse-block/QOD check.
- Body size: 2.9 x 2.8 x TBD mm.
- Extra area: 还要镜头、固定孔、FPC、ESD、供电小板和 Z-stack。
- Placement: Front Sensor Board; Confirm QOD/reverse feed when camera off.
- Keep away from: 高温 regulator、电池硬压、过紧 FPC 弯折和污染源。
- Freeze status: PROVISIONAL; footprint: candidate; verify official drawing/land pattern/height before layout.
- Missing data: Check reverse block, ramp, QOD, logic level
- Source: AI Glasses Hardware Dimensions V2.3 (2026-07-01), pp. 1-10, `/Users/stanley/Downloads/AI_Glasses_Hardware_Dimensions_V2.3.pdf`.

### U18 - TPD4E05U06

- What it is: MIPI/FPC ESD (clk + D0) — ultra-low-cap 4-ch ESD at the FPC entry..
- What it does: 连接板卡、电源、信号或充电/调试接口。
- Why needed: 当前架构需要它来完成对应电源、信号、传感、射频、声学或调试功能。
- Connects to: 见 current schematic nets and board partition。
- Voltage: MIPI/low-cap ESD.
- Power: typical leakage only; peak ESD clamp.
- Body size: 2.5 x 1.0 x TBD mm.
- Extra area: 还要去耦、连接器、测试点、keep-out 和装配公差。
- Placement: Front Sensor Board; Must be close to FPC entry and not stub MIPI lines.
- Keep away from: 天线 keep-out、电池膨胀区、高热源和不可维修的硬压位置。
- Freeze status: PROVISIONAL; footprint: candidate; verify official drawing/land pattern/height before layout.
- Missing data: Low-cap array near FPC entry
- Source: AI Glasses Hardware Dimensions V2.3 (2026-07-01), pp. 1-10, `/Users/stanley/Downloads/AI_Glasses_Hardware_Dimensions_V2.3.pdf`.

### CAM_FPC - custom camera FPC TBD

- What it is: camera FPC tail.
- What it does: 采集画面或给相机供电/保护。
- Why needed: 当前架构需要它来完成对应电源、信号、传感、射频、声学或调试功能。
- Connects to: 见 current schematic nets and board partition。
- Voltage: MIPI CSI, I2C, rails, GND.
- Power: typical passive; I2R/insertion loss; peak pin-current TBD.
- Body size: TBD.
- Extra area: 还要镜头、固定孔、FPC、ESD、供电小板和 Z-stack。
- Placement: Virtual mechanical item; Virtual mechanical item; final exit direction, stiffener, contact side and bend radius required.
- Keep away from: 高温 regulator、电池硬压、过紧 FPC 弯折和污染源。
- Freeze status: HOLD; footprint: virtual; no KiCad footprint.
- Missing data: close gate/source data before PCB layout
- Source: Current V2 generated schematic/BOM master (generated 2026-07-01), scripts/chipdown_bom.py, `v2_chipdown/scripts/chipdown_bom.py`.

## Source Register

| ID | Title | Revision | Page | Local file / URL | Confidence |
|---|---|---|---|---|---|
| S0 | Current V2 generated schematic/BOM master | generated 2026-07-01 | scripts/chipdown_bom.py | v2_chipdown/scripts/chipdown_bom.py | high for current project intent; not a package drawing |
| S1 | AI Glasses Hardware Dimensions V2.2 | 2026-07-01 | pp. 1-10 | /Users/stanley/Downloads/AI_Glasses_Hardware_Dimensions_V2.2 (3).pdf | medium; project extraction from BOM PDFs |
| S2 | AI Glasses Hardware Dimensions V2.3 | 2026-07-01 | pp. 1-10 | /Users/stanley/Downloads/AI_Glasses_Hardware_Dimensions_V2.3.pdf | medium; project extraction from BOM PDFs |
| S3 | Quectel FCU760K Short Specification | V1.1, Released, 2024 | pp. 1-3 | AI_Glasses_HOLD_Closure_Pack/02_WiFi_FCU760K/Quectel_FCU760K_Short_Spec_V1.1.pdf | high for module outline and basic electrical data; land pattern still missing |
| S4 | Syntiant NDP120 Product Brief | V1, 2023 | pp. 1-2 | AI_Glasses_HOLD_Closure_Pack/01_NDP120/NDP120_Product_Brief.pdf | medium; product brief, not full datasheet/package drawing |
| S5 | Sony IMX415-AAQR-C Datasheet E19504 | Official edition, 2019-05-21 | pp. 1, 3, 97 | AI_Glasses_HOLD_Closure_Pack/04_IMX415/IMX415-AAQR-C_Datasheet_E19504.pdf | high for bare sensor; low for final module mechanics |
| S6 | TI BQ297xx Datasheet SLUSBU9I | March 2014, revised August 2024 | pp. 1, 3, package outline | AI_Glasses_HOLD_Closure_Pack/03_Battery_LP451165_1S2P/TI_BQ2970_1S_Protection_Datasheet.pdf | high for IC; exact suffix still TBD |
| S7 | LP451165 Battery Bay Fit Check | project fit-check, 2026-07-01 | dimensions.csv + fit-check md | AI_Glasses_HOLD_Closure_Pack/06_Mechanical_Fit_Check/ | medium; CAD clearance envelope, not supplier pack drawing |
| S8 | RK3576 Brief Datasheet file | V1.2, 2024-03-11; PDF metadata title mismatch noted | pp. 1-3 | AI_Glasses_HOLD_Closure_Pack/05_Project_References/RK3576 Brief Datasheet V1.2-20240311.pdf | medium; package/HDG/ball map still required |

## Release Checklist

- Left/right temple top, side and section views: generated as Phase 1 evidence; still HOLD until CAD validates.
- Every major hardware-list item has a component card and freeze status.
- Every dimension has a source register entry or is marked TBD/HOLD.
- KiCad footprint edits: not performed in Phase 1.
- Symbol/footprint mapping and interconnect matrix: generated from current schematic source.
- ERC: existing report clean; not rerun because `kicad-cli` was unavailable.
- DRC/3D collision: not complete because V2 has no PCB/STEP assembly yet.
- Final PASS/HOLD/FAIL: overall **HOLD** before PCB layout.
