# AI Glasses RK3576 Chip-down BOM V2.3 中文版
## 与当前 schematic 对齐的 BOM、功耗和 layout gate 报告

- 生成日期：2026-07-01
- Source of truth：`v2_chipdown/scripts/chipdown_bom.py` 与 `v2_chipdown/config/power_budget_v2.yaml`
- Schematic：`v2_chipdown/hardware/ai_glasses_v2_chipdown.kicad_sch`
- 导出 BOM/netlist/PDF：`v2_chipdown/reports/*`
- 如果旧 PDF 和本文件冲突，以本文件和当前 schematic 为准。
- 注意：MPN、refdes、BOM ID、net name 保留英文，避免和 KiCad/schematic 不一致。

## 1. 优先阅读

| 项目 | 当前值 |
|---|---|
| schematic 范围 | PCB layout 之前的 functional-block schematic |
| 元件 / 网络 | 98 components / 137 nets |
| 装配状态 | DNP=21, Fit=58, HOLD=17, TBD=2 |
| 板卡分区 | 右镜腿 Compute Board=33, 左镜腿 AON/Power Board=15, 镜腿后端电池/扬声器/天线区=18, 前框 Sensor Board=24, EVT 调试尾板=8 |
| ERC | Report includes: Errors, Warnings, Exclusions; ** ERC messages: 0  Errors 0  Warnings 0 |
| PCB layout release | 还没有 release；Gate 0/G00F/G05/G07/G08/G10/G12 仍阻塞 layout |
| Phase 1.5 | 正式 PCB layout 前必须完成 Mechanical/Electrical Floorplan |
| 第一版铰链口径 | Chip-down EVT V2.0 不包含铰链电气连接；J4 hinge FPC 已从 schematic source 删除 |

状态定义：Fit=首版贴装；DNP=只留焊盘不贴；HOLD=候选件但门禁未关闭；TBD=型号/规格待定。
功耗数字是项目预算模型，还不是 EVT bench 实测；后续必须用分域 shunt 数据替换。

## 2. 系统功耗边界

| 工作状态 | 当前负载 (mW) | 目标区间 (mW) | 3.7V 电池电流 | LP451165 x2 1S2P 续航 |
|---|--:|--:|--:|--:|
| 深度待机(AON only, RK3576 off) | 22 | 20-50 | 6 mA | 91 h |
| 快速待机(DDR retention / light sleep) | 134 | 80-200 | 36 mA | 15 h |
| 手机协作识别(blended) | 362 | 250-450 | 98 mA | 5.5 h (331 min) |
| 混合运动使用(blended) | 450 | <=500-800 | 122 mA | 4.4 h (266 min) |
| 连续 1080p 录像 | 1290 | 1000-1500 | 349 mA | 1.5 h (93 min) |
| 录像 + 本地 AI Burst | 2065 | 1500-2500 | 558 mA | 1.0 h (58 min) |

推荐电池包：LP451165 x2，1S2P，600 mAh / 2.22 Wh nominal，左右镜腿各一颗。
当前 baseline 模型：连续 1080p 录像为 1290 mW，AI Burst 为 2065 mW。

## 3. 子系统功耗模型

| 子系统 | 功耗域 | 深度待机(AON only, RK3576 off) | 快速待机(DDR retention / light sleep) | 手机协作识别(blended) | 混合运动使用(blended) | 连续 1080p 录像 | 录像 + 本地 AI Burst |
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

## 4. 相对旧 PDF 的修正

- Wi-Fi 模块以当前 schematic 为准：`U11 / C015 = FCU760KAAMD`，状态 HOLD。
- BQ25895 已作为主充电与 Power Path block 加入；nPM1300 保留为 AON 低功耗 PMIC/gauge/rail manager。
- J4 hinge FPC 已删除：EVT V2.0 不放 hinge FPC footprint，也不画跨铰链 battery、MIPI、USB 或 audio 线。
- J3 是建议的 33-pin FH26W camera FPC；IMX415 已按 4-lane 目标画入，但机械模组仍为 HOLD/TBD。
- Wi-Fi/BLE 共用一根双频 FPC 天线；FCU760K 第二 RF port 仅保留 DNP/test。
- IMU 以当前 schematic 为准：`U10 / C012 = BMI270`，状态 Fit。
- 当前 baseline 功耗总表为：22 / 134 / 362 / 450 / 1290 / 2065 mW。
- 当前 BOM 不只是 C001-C045；已经展开为 98 个 schematic components。
- C044 已展开为 RS1-RS9 与 U25-U33；C045/C046 的关键被动件和 default-off 下拉也已显式列出。
- PCB layout 仍未 release；机械、电池、FPC、RF、camera、AON 功耗等 gate 仍需关闭。
- 新增 Phase 1.5：在 ERC-clean schematic 和正式 PCB layout 之间，必须先完成机械/电气 floorplan。

## 5. 板卡与机械分区

| 区域 | 当前 schematic 内容 | EVT 说明 |
|---|---|---|
| 前框 Sensor Board | IMX415 custom FPC module、3 颗 fitted T5837 mic、第 4 颗 mic DNP、camera rails、MIPI ESD、front FPC | 最终 module pinout/lens/lane count 仍是 G10 HOLD |
| 右镜腿 Compute Board | RK3576、RK806S、LPDDR4X、eMMC、BQ25895、TPS61088、FCU760K Wi-Fi、Wi-Fi buck/load switch、MAX98360A audio | 热、充电/boost droop gate 仍未关闭 |
| 左镜腿 AON/Power Board | nRF54L15、nPM1300、NDP120、BMI270、可选保护、main shunt/INA | AON 平均 <=25 mW、上限 <=50 mW 必须实测 |
| 镜腿后端 | LP451165 x2 pack envelopes、branch fuses/shunts、speaker、shared Wi-Fi/BLE antenna、pogo、DNP RF/debug options | 第一版电气上 fixed-temple；当前 released schematic 不含 hinge FPC/cross-hinge harness |
| EVT 调试尾板 | USB-C、ESD、CC resistors、SWD/UART pads、power/reset/recovery buttons | 只用于 bring-up；量产可隐藏或移除 |

## 5.5. Phase 1.5 Mechanical/Electrical Floorplan

正式 PCB placement/routing 之前，先做 no-route fit floorplan。这是 CAD + EE 的交付物，不是 routed PCB。

| 必需输出 | 内容 |
|---|---|
| 右镜腿俯视/侧视 | usable length/width/height；Compute PCB；RK3576/LPDDR/RK806/eMMC/Wi-Fi/BQ25895/boost-inductor zones；battery；speaker；shared Wi-Fi/BLE antenna keep-out；pogo；front FPC corridor；shell/foam/swell allowance |
| 左镜腿俯视/侧视 | usable length/width/height；AON/power PCB；nRF/nPM/NDP/BMI270 zones；battery；不单放 BLE antenna；pogo/service clearance；shell/foam/swell allowance |
| KiCad no-route floorplan | board frames；RK3576、LPDDR、RK806、eMMC、Wi-Fi、boost inductor、FPC connectors、battery 3D/envelope blocks、speaker、antenna keep-outs |
| Pass/fail decision | 先证明当前 schematic 架构放得下；如果放不下，先改 battery/partition/connectors/DNP/local temple width，不进入 routing |

只有 floorplan 通过后，才允许开始正式 routing。

## 6. 当前 BOM（按板卡）

### 右镜腿 Compute Board

| Ref | BOM ID | Value | 状态 | Pri | Package / footprint placeholder | 关闭门禁 |
|---|---|---|:--:|:--:|---|---|
| U1 | C001 | RK3576 | Fit / 首版贴装 | P0 | AI_Glasses_V2:VERIFY_FCCSP698L_16x17 | G01 (RK3576 datasheet/HDG/ballmap/DDR guide) |
| U2 | C002 | RK806S-5 QFN68 7x7x0.90mm | HOLD / 候选件但门禁未关闭 | P0 | AI_Glasses_V2:VERIFY_QFN68_7x7_EP5.49_P0.35 | G03 (official RK806S-5 datasheet, OTP/default rails, sequence, layout guide) |
| U3 | C003 | Samsung K4U6E3S4AA-MGCL | HOLD / 候选件但门禁未关闭 | P0 | AI_Glasses_V2:VERIFY_FBGA200_0.65 | G02 (Samsung datasheet/ball map/IBIS + Rockchip DDR AVL/init + length report) |
| U4 | C004 | Samsung KLMAG1JENB-B041 | HOLD / 候选件但门禁未关闭 | P0 | AI_Glasses_V2:VERIFY_BGA153 | G04 (official Samsung datasheet/package + BSP boot/HS200 then HS400 validation) |
| Y1 | C005 | 24 MHz 10 ppm XTAL | Fit / 首版贴装 | P0 | AI_Glasses_V2:Crystal_SMD_3225 | G01 (reuse reference CL/ESR + placement distance per HDG) |
| U5 | C006 | MX25U6432F | DNP / 只留焊盘不贴 | P1 | AI_Glasses_V2:USON-8 | Boot flow decides whether production needs it |
| U6 | C007 | TPS61088 | HOLD / 候选件但门禁未关闭 | P0 | AI_Glasses_V2:VQFN-22_4.5x3.5 | G06/G09 (measured RK3576 boot+AI peak, soft-start, droop, thermal) |
| L1 | C008 | Coilcraft XGL4020-102MEC 1.0uH | HOLD / 候选件但门禁未关闭 | P0 | AI_Glasses_V2:VERIFY_L_4x4x2_XGL4020 | G06/G13 (Isat/DCR/thermal pass for 5.1V 3A continuous / 4A peak boost) |
| U11 | C015 | FCU760KAAMD | HOLD / 候选件但门禁未关闭 | P0 | AI_Glasses_V2:VERIFY_LCC_13x12.2_Quectel | G05 (Quectel HW Design + RK3576 BSP driver/firmware/enum) + official LCC land pattern |
| U12 | C016 | TPS62825 | Fit / 首版贴装 | P0 | AI_Glasses_V2:QFN_1.5x1.5 | G05/G06 (inductor/caps per module 353mA TX peak + ripple) |
| L2 | C016c | Wi-Fi buck inductor (TBD) | Fit / 首版贴装 | P0 | AI_Glasses_V2:VERIFY_L_2x2 | Per TPS62825 peak+ripple |
| U13 | C016b | TPS22917DBVR | Fit / 首版贴装 | P0 | Package_TO_SOT_SMD:SOT-23-5 | G05 (turn-on sequence w/ module) |
| C1 | C015-C | 47uF 6.3V X5R | Fit / 首版贴装 | P0 | AI_Glasses_V2:C_0805 | Local bulk per Quectel HW Design |
| RT3 | C043 | 10k NTC B=3435 | Fit / 首版贴装 | P0 | AI_Glasses_V2:R_0402 | Probe position per thermal sim |
| U35 | C010b | BQ25895 | HOLD / 候选件但门禁未关闭 | P0 | AI_Glasses_V2:VERIFY_WQFN_24_BQ25895 | Charger/power-path config, TS thresholds, 1S2P charge profile, thermal/current validation |
| U36 | C034b | 5V input eFuse/OVP (MPN TBD) | HOLD / 候选件但门禁未关闭 | P0 | AI_Glasses_V2:VERIFY_EFUSE_OVP | Select MPN for pogo/USB VBUS surge, reverse, OVP, current limit and thermal fault |
| U20 | C024 | MAX98360A | Fit / 首版贴装 | P0 | AI_Glasses_V2:VERIFY_WLP_QFN | Verify Z/cavity/EMI/peak power |
| U21 | C024b | TPS22917DBVR | Fit / 首版贴装 | P0 | Package_TO_SOT_SMD:SOT-23-5 | Amp must be fully power-downable (V1 lesson) |
| RS4 | C044-RSOC | 10 mohm 1% | Fit / 首版贴装 | P0 | AI_Glasses_V2:R_0805_shunt | 5-20 mohm (2A x 10m=20mV; avoid boost UVLO) |
| RS5 | C044-RWIFI | 50 mohm 1% | Fit / 首版贴装 | P0 | AI_Glasses_V2:R_0603_shunt | 20-100 mohm |
| RS6 | C044-RAUD | 50 mohm 1% | Fit / 首版贴装 | P0 | AI_Glasses_V2:R_0603_shunt | 20-100 mohm |
| U28 | C044c | INA238 (I_SOC_5V) | DNP / 只留焊盘不贴 | P1 | AI_Glasses_V2:VSSOP-10 | Power Gate — EVT-A only |
| U29 | C044e | INA238 (I_WIFI) | DNP / 只留焊盘不贴 | P1 | AI_Glasses_V2:VSSOP-10 | Power Gate — EVT-A only |
| U30 | C044f | INA238 (I_AUDIO) | DNP / 只留焊盘不贴 | P1 | AI_Glasses_V2:VSSOP-10 | Power Gate — EVT-A only |
| R11 | C046a | 100k | Fit / 首版贴装 | P0 | AI_Glasses_V2:R_0402 | Default OFF (§4) |
| R12 | C046b | 100k | Fit / 首版贴装 | P0 | AI_Glasses_V2:R_0402 | Default OFF (§4) |
| R16 | C046f | 100k | Fit / 首版贴装 | P0 | AI_Glasses_V2:R_0402 | Default OFF (§4) |
| R17 | C046g | 100k | Fit / 首版贴装 | P0 | AI_Glasses_V2:R_0402 | Default OFF (§4) |
| R18 | C046h | 100k | Fit / 首版贴装 | P0 | AI_Glasses_V2:R_0402 | Default OFF (§4/§9: FCU760K CHIP_EN default low) |
| R19 | C046i | 100k | Fit / 首版贴装 | P0 | AI_Glasses_V2:R_0402 | Default OFF (§4) |
| R20 | C046j | 100k | Fit / 首版贴装 | P0 | AI_Glasses_V2:R_0402 | Default OFF (§4) |
| R9 | C045e | 2.2k 1% | Fit / 首版贴装 | P0 | AI_Glasses_V2:R_0402 | Confirm vs SoC PMIC bus |
| R10 | C045f | 2.2k 1% | Fit / 首版贴装 | P0 | AI_Glasses_V2:R_0402 | Confirm vs SoC PMIC bus |

### 左镜腿 AON/Power Board

| Ref | BOM ID | Value | 状态 | Pri | Package / footprint placeholder | 关闭门禁 |
|---|---|---|:--:|:--:|---|---|
| U7 | C009 | nRF54L15-QFN48 | Fit / 首版贴装 | P0 | AI_Glasses_V2:QFN-48_6x6 | EVT-frozen (RF layout/SDK/package to freeze early) |
| U8 | C010 | nPM1300 | HOLD / 候选件但门禁未关闭 | P0 | AI_Glasses_V2:QFN_5x5 | G08 (AON <=25/50mW) — configure via nPM PowerUP on EK before board |
| U9 | C011 | NDP120 | HOLD / 候选件但门禁未关闭 | P0 | AI_Glasses_V2:VERIFY_QFN_5x5 | Full datasheet + dev kit + measured listening power + NDA/licensing |
| U10 | C012 | BMI270 | Fit / 首版贴装 | P0 | Package_LGA:LGA-14_2.5x3mm_P0.5mm | Evaluate false-trigger under real frame vibration |
| U22 | C027 | DRV2605L | DNP / 只留焊盘不贴 | P1 | Package_SO:MSOP-10_3x3mm_P0.5mm | Vibration P1 — may DNP on first board (IMU/mic coupling) |
| RS1 | C044-RBAT | 10 mohm 1% 1W | Fit / 首版贴装 | P0 | AI_Glasses_V2:R_1206_shunt | I_BAT_TOTAL; the one production-kept sense path |
| R21 | C032-BYP | 0R (pack-PCM baseline) | Fit / 首版贴装 | P0 | AI_Glasses_V2:R_0805 | Populate 0R OR discrete protection, never both (§17) |
| U23 | C032 | BQ2970 | DNP / 只留焊盘不贴 | P0 | Package_TO_SOT_SMD:SOT-23-5 | Keep ONE protection scheme; confirm suffix OVP/UVP/OCP vs nPM1300/boost UVLO (§17) |
| Q1 | C032-Q | Dual N-MOSFET (b2b) | DNP / 只留焊盘不贴 | P0 | AI_Glasses_V2:VERIFY_DFN_2FET | Vds/RDSon/Vgs/peak per BQ2970 app (§17) |
| R22 | C032-Rv | 330R | DNP / 只留焊盘不贴 | P0 | AI_Glasses_V2:R_0402 | Per BQ2970 app |
| C2 | C032-Cv | 0.1uF | DNP / 只留焊盘不贴 | P0 | AI_Glasses_V2:C_0402 | Per BQ2970 app |
| R23 | C032-Rm | 2k | DNP / 只留焊盘不贴 | P0 | AI_Glasses_V2:R_0402 | Per BQ2970 app (V- sense) |
| U25 | C044a | INA238 (I_BAT_TOTAL) | DNP / 只留焊盘不贴 | P1 | AI_Glasses_V2:VSSOP-10 | Power Gate — EVT-A; production may keep this one |
| R3 | C045a | 2.2k 1% | Fit / 首版贴装 | P0 | AI_Glasses_V2:R_0402 | Confirm vs total AON bus capacitance |
| R4 | C045b | 2.2k 1% | Fit / 首版贴装 | P0 | AI_Glasses_V2:R_0402 | Confirm vs total AON bus capacitance |

### 镜腿后端电池/扬声器/天线区

| Ref | BOM ID | Value | 状态 | Pri | Package / footprint placeholder | 关闭门禁 |
|---|---|---|:--:|:--:|---|---|
| J6 | C018 | FCU760K ANT_BT DNP test pad | DNP / 只留焊盘不贴 | P0 | AI_Glasses_V2:VERIFY_ANT | Only populate if Quectel FAE + coexistence test requires the second RF port |
| J7 | C017 | Taoglas FXP840.07.0055B | HOLD / 候选件但门禁未关闭 | P0 | AI_Glasses_V2:VERIFY_FPC_ANT_14x5 | G14 (worn-state tune + antenna keep-out in full shell with battery/speaker) |
| LS1 | C025 | CUI CMS-15113-078SP-67 | HOLD / 候选件但门禁未关闭 | P0 | AI_Glasses_V2:VERIFY_SPK_15x11x3 | Acoustic EVT: 0.3-0.5cc cavity, port/foam seal, magnet-to-antenna clearance, leak test |
| LS2 | C026 | 2nd speaker pad | DNP / 只留焊盘不贴 | P1 | AI_Glasses_V2:VERIFY_SPK | Decide dual-speaker at EVT-B |
| M1 | C028 | LRA/ERM motor | DNP / 只留焊盘不贴 | P1 | AI_Glasses_V2:VERIFY_LRA | Vibration P1 |
| BT1 | C029 | LP451165 300mAh (R) | HOLD / 候选件但门禁未关闭 | P0 | AI_Glasses_V2:VERIFY_CELL_4.5x11x65 | G07 (full datasheet, >=2C, IR, cycles, cert) |
| BT2 | C030 | LP451165 300mAh (L) | HOLD / 候选件但门禁未关闭 | P0 | AI_Glasses_V2:VERIFY_CELL_70x12.8x5.6_maxenv | G07 |
| F1 | C031a | PTC/fuse (R branch) | TBD / 型号或规格待定 | P0 | AI_Glasses_V2:VERIFY_FUSE | Rating from peak-current calc (> branch peak, < FPC rating) |
| F2 | C031b | PTC/fuse (L branch) | TBD / 型号或规格待定 | P0 | AI_Glasses_V2:VERIFY_FUSE | Rating from peak-current calc |
| RS2 | C044-RCL | 10 mohm 1% | Fit / 首版贴装 | P0 | AI_Glasses_V2:R_0805_shunt | Branch current-share (§7/§29) |
| RS3 | C044-RCR | 10 mohm 1% | Fit / 首版贴装 | P0 | AI_Glasses_V2:R_0805_shunt | Branch current-share (§7/§29) |
| RT1 | C033a | 10k NTC B=3435 1% (R cell) | Fit / 首版贴装 | P0 | AI_Glasses_V2:R_0402 | NTC curve/package/placement matched to pack supplier + BQ25895/nPM1300 config |
| RT2 | C033b | 10k NTC B=3435 1% (L cell) | Fit / 首版贴装 | P0 | AI_Glasses_V2:R_0402 | NTC curve/package/placement matched to pack supplier + ADC/config |
| TP2 | C033-TP | Battery test points | Fit / 首版贴装 | P0 | AI_Glasses_V2:TestPad_Set | Cell/pack voltage + NTC probe access (§21) |
| J1 | C034 | CCP P2578MP01-06C180HT | HOLD / 候选件但门禁未关闭 | P0 | AI_Glasses_V2:VERIFY_POGO_6P_1.8MM | USB2 eye/contact validation, current/fault/ESD, mating STEP, corrosion/cycle life |
| J5 | C040 | U.FL / I-PEX MHF RF test connector | DNP / 只留焊盘不贴 | P0 | Connector_Coaxial:U.FL_Hirose_U.FL-R-SMT-1_Vertical | EVT RF debug only; production prefers direct coax or soldered antenna pigtail |
| U26 | C044-ICL | INA238 (I_CELL_L) | DNP / 只留焊盘不贴 | P1 | AI_Glasses_V2:VSSOP-10 | Power Gate — EVT-A only (current-share) |
| U27 | C044-ICR | INA238 (I_CELL_R) | DNP / 只留焊盘不贴 | P1 | AI_Glasses_V2:VSSOP-10 | Power Gate — EVT-A only (current-share) |

### 前框 Sensor Board

| Ref | BOM ID | Value | 状态 | Pri | Package / footprint placeholder | 关闭门禁 |
|---|---|---|:--:|:--:|---|---|
| U14 | C019 | Sony IMX415-AAQR-C custom module | HOLD / 候选件但门禁未关闭 | P0 | AI_Glasses_V2:VERIFY_CAM_MODULE | G10 (module lens/FOV/FPC pinout/lane/supply/timing from vendor) |
| U15 | C020 | TPS62840 | Fit / 首版贴装 | P0 | AI_Glasses_V2:VERIFY_WSON | Output current/noise per final module (DVDD ~250mA max + margin) |
| L3 | C020b | Cam 1V1 buck inductor (TBD) | Fit / 首版贴装 | P0 | AI_Glasses_V2:VERIFY_L_1.6x0.8 | Per TPS62840 design |
| U16 | C021 | TLV75529PDRVR | Fit / 首版贴装 | P0 | AI_Glasses_V2:WSON-6_2x2 | Verify vs IMX415 AVDD peak (156mA) + PSRR |
| U17 | C022 | TPS22917DBVR | Fit / 首版贴装 | P0 | Package_TO_SOT_SMD:SOT-23-5 | Check reverse block, ramp, QOD, logic level |
| U18 | C023a | TPD4E05U06 | Fit / 首版贴装 | P0 | AI_Glasses_V2:USON | Low-cap array near FPC entry |
| U19 | C023b | TPD4E05U06 | Fit / 首版贴装 | P0 | AI_Glasses_V2:USON | Low-cap array near FPC entry |
| U34 | C023c | TPD4E05U06 | Fit / 首版贴装 | P0 | AI_Glasses_V2:USON | Low-cap array near FPC entry for 4-lane CSI |
| MK1 | C013a | T5837 (wake mic) | Fit / 首版贴装 | P0 | AI_Glasses_V2:LGA-5_3.5x2.65 | G11 (mic coords/ports/wind/wake + AEC/beamforming) |
| MK2 | C013b | T5837 (array mic 1) | Fit / 首版贴装 | P0 | AI_Glasses_V2:LGA-5_3.5x2.65 | G11 |
| MK3 | C013c | T5837 (array mic 2) | Fit / 首版贴装 | P0 | AI_Glasses_V2:LGA-5_3.5x2.65 | G11 |
| MK4 | C014 | T5837 (4th mic) | DNP / 只留焊盘不贴 | P1 | AI_Glasses_V2:LGA-5_3.5x2.65 | G11 (populate only if array sim/proto needs it) |
| J3 | C038 | Hirose FH26W-33S-0.3SHW(97) | HOLD / 候选件但门禁未关闭 | P0 | AI_Glasses_V2:VERIFY_FH26W_33S_0.3SHW | G10/G12 (camera module vendor signs 33-pin pinout, contact orientation, impedance) |
| RS7 | C044-RC1 | 100 mohm 1% | Fit / 首版贴装 | P0 | AI_Glasses_V2:R_0603_shunt | Per-rail Kelvin (§23/§29); DVDD ~250mA |
| RS8 | C044-RC8 | 100 mohm 1% | Fit / 首版贴装 | P0 | AI_Glasses_V2:R_0402_shunt | Per-rail Kelvin (§23/§29); IOVDD ~3mA |
| RS9 | C044-RC29 | 100 mohm 1% | Fit / 首版贴装 | P0 | AI_Glasses_V2:R_0603_shunt | Per-rail Kelvin (§23/§29); AVDD ~156mA |
| U31 | C044-IC1 | INA238 (I_CAM_1V1) | DNP / 只留焊盘不贴 | P1 | AI_Glasses_V2:VSSOP-10 | Power Gate — EVT-A only |
| U32 | C044-IC8 | INA238 (I_CAM_1V8) | DNP / 只留焊盘不贴 | P1 | AI_Glasses_V2:VSSOP-10 | Power Gate — EVT-A only |
| U33 | C044-IC29 | INA238 (I_CAM_2V9) | DNP / 只留焊盘不贴 | P1 | AI_Glasses_V2:VSSOP-10 | Power Gate — EVT-A only |
| R13 | C046c | 100k | Fit / 首版贴装 | P0 | AI_Glasses_V2:R_0402 | Default OFF (§4) |
| R14 | C046d | 100k | Fit / 首版贴装 | P0 | AI_Glasses_V2:R_0402 | Default OFF (§4) |
| R15 | C046e | 100k | Fit / 首版贴装 | P0 | AI_Glasses_V2:R_0402 | Default OFF (§4) |
| R5 | C045c | 2.2k 1% | Fit / 首版贴装 | P0 | AI_Glasses_V2:R_0402 | Confirm vs camera bus capacitance |
| R6 | C045d | 2.2k 1% | Fit / 首版贴装 | P0 | AI_Glasses_V2:R_0402 | Confirm vs camera bus capacitance |

### EVT 调试尾板

| Ref | BOM ID | Value | 状态 | Pri | Package / footprint placeholder | 关闭门禁 |
|---|---|---|:--:|:--:|---|---|
| J2 | C035 | USB-C 16p USB2-only | Fit / 首版贴装 | P0 | AI_Glasses_V2:USB_C_16P_MidMount | Connector height + shell opening co-freeze |
| U24 | C036 | TPD2E001 | Fit / 首版贴装 | P0 | Package_TO_SOT_SMD:SOT-23-3 | Keep ~90 ohm diff + continuous ref gnd |
| R1 | C037a | 5.1k 1% | Fit / 首版贴装 | P0 | AI_Glasses_V2:R_0402 | USB-C spec |
| R2 | C037b | 5.1k 1% | Fit / 首版贴装 | P0 | AI_Glasses_V2:R_0402 | USB-C spec |
| TP1 | C041 | UART/SWD pogo pads | Fit / 首版贴装 | P0 | AI_Glasses_V2:TestPad_Set | Voltage domain clearly labelled (no 3.3V into 1.8V IO) |
| SW1 | C042a | Power/PWRKEY | Fit / 首版贴装 | P0 | Button_Switch_SMD:SW_Push_1P1T_NO_CK_KMR2 | First chip-down must recover from boot failure |
| SW2 | C042b | Reset | Fit / 首版贴装 | P0 | Button_Switch_SMD:SW_Push_1P1T_NO_CK_KMR2 | Bring-up |
| SW3 | C042c | MaskROM/Recovery | Fit / 首版贴装 | P0 | Button_Switch_SMD:SW_Push_1P1T_NO_CK_KMR2 | Bring-up (recover from bad boot) |

## 7. 逐元件功耗分摊

下表为 battery-side 项目预算 mW，所有行加总必须等于当前 subsystem total。0 表示 DNP、被动件、电源源头，或损耗已计入所属功耗域，并不表示物理上没有寄生损耗。

| Ref | BOM ID | Value | 状态 | 深度待机(AON only, RK3576 off) | 快速待机(DDR retention / light sleep) | 手机协作识别(blended) | 混合运动使用(blended) | 连续 1080p 录像 | 录像 + 本地 AI Burst | 依据 |
|---|---|---|:--:|--:|--:|--:|--:|--:|--:|---|
| U1 | C001 | RK3576 | Fit / 首版贴装 | 0 | 20 | 80 | 150 | 600 | 1150 | RK3576 在计算核心功耗行中的项目预算分摊 |
| U2 | C002 | RK806S-5 QFN68 7x7x0.90mm | HOLD / 候选件但门禁未关闭 | 0 | 10 | 15 | 25 | 70 | 100 | RK806S/PMIC 多路 rail 管理损耗分摊 |
| U3 | C003 | Samsung K4U6E3S4AA-MGCL | HOLD / 候选件但门禁未关闭 | 0 | 55 | 45 | 60 | 130 | 180 | LPDDR4X 保持/活动功耗分摊 |
| U4 | C004 | Samsung KLMAG1JENB-B041 | HOLD / 候选件但门禁未关闭 | 0 | 5 | 10 | 15 | 50 | 70 | eMMC 待机与写入功耗分摊 |
| Y1 | C005 | 24 MHz 10 ppm XTAL | Fit / 首版贴装 | 0 | 0 | 0 | 0 | 0 | 0 | 0 表示 DNP/被动/电源源头，或已计入所属功耗域 |
| U5 | C006 | MX25U6432F | DNP / 只留焊盘不贴 | 0 | 0 | 0 | 0 | 0 | 0 | 0 表示 DNP/被动/电源源头，或已计入所属功耗域 |
| U6 | C007 | TPS61088 | HOLD / 候选件但门禁未关闭 | 0 | 20 | 10 | 20 | 40 | 60 | 计算岛 Boost/开关/PMIC 损耗 |
| L1 | C008 | Coilcraft XGL4020-102MEC 1.0uH | HOLD / 候选件但门禁未关闭 | 0 | 0 | 0 | 0 | 0 | 0 | 0 表示 DNP/被动/电源源头，或已计入所属功耗域 |
| U11 | C015 | FCU760KAAMD | HOLD / 候选件但门禁未关闭 | 0 | 0 | 145 | 95 | 75 | 115 | FCU760K 按需 Wi-Fi 活动平均功耗 |
| U12 | C016 | TPS62825 | Fit / 首版贴装 | 0 | 0 | 5 | 5 | 5 | 5 | Wi-Fi Buck 转换损耗 |
| L2 | C016c | Wi-Fi buck inductor (TBD) | Fit / 首版贴装 | 0 | 0 | 0 | 0 | 0 | 0 | 0 表示 DNP/被动/电源源头，或已计入所属功耗域 |
| U13 | C016b | TPS22917DBVR | Fit / 首版贴装 | 0 | 0 | 0 | 0 | 0 | 0 | 0 表示 DNP/被动/电源源头，或已计入所属功耗域 |
| C1 | C015-C | 47uF 6.3V X5R | Fit / 首版贴装 | 0 | 0 | 0 | 0 | 0 | 0 | 0 表示 DNP/被动/电源源头，或已计入所属功耗域 |
| RT3 | C043 | 10k NTC B=3435 | Fit / 首版贴装 | 0 | 0 | 0 | 0 | 0 | 0 | 0 表示 DNP/被动/电源源头，或已计入所属功耗域 |
| U35 | C010b | BQ25895 | HOLD / 候选件但门禁未关闭 | 0 | 0 | 0 | 0 | 0 | 0 | 0 表示 DNP/被动/电源源头，或已计入所属功耗域 |
| U36 | C034b | 5V input eFuse/OVP (MPN TBD) | HOLD / 候选件但门禁未关闭 | 0 | 0 | 0 | 0 | 0 | 0 | 0 表示 DNP/被动/电源源头，或已计入所属功耗域 |
| U7 | C009 | nRF54L15-QFN48 | Fit / 首版贴装 | 2 | 3 | 8 | 6 | 5 | 8 | nRF BLE MCU 与常开状态机平均功耗 |
| U8 | C010 | nPM1300 | HOLD / 候选件但门禁未关闭 | 3 | 4 | 6 | 6 | 10 | 15 | nPM1300 AON Buck 静态与转换损耗 |
| U9 | C011 | NDP120 | HOLD / 候选件但门禁未关闭 | 12 | 12 | 15 | 15 | 15 | 20 | NDP120 类唤醒词/监听预算 |
| U10 | C012 | BMI270 | Fit / 首版贴装 | 1 | 1 | 1 | 1 | 1 | 1 | BMI270 低功耗运动检测预算 |
| J6 | C018 | FCU760K ANT_BT DNP test pad | DNP / 只留焊盘不贴 | 0 | 0 | 0 | 0 | 0 | 0 | 0 表示 DNP/被动/电源源头，或已计入所属功耗域 |
| J7 | C017 | Taoglas FXP840.07.0055B | HOLD / 候选件但门禁未关闭 | 0 | 0 | 0 | 0 | 0 | 0 | 0 表示 DNP/被动/电源源头，或已计入所属功耗域 |
| U14 | C019 | Sony IMX415-AAQR-C custom module | HOLD / 候选件但门禁未关闭 | 0 | 0 | 0 | 25 | 220 | 265 | 当前 1080p camera baseline 分摊 |
| U15 | C020 | TPS62840 | Fit / 首版贴装 | 0 | 0 | 0 | 2 | 15 | 18 | Camera 1.1 V Buck 损耗分摊 |
| L3 | C020b | Cam 1V1 buck inductor (TBD) | Fit / 首版贴装 | 0 | 0 | 0 | 0 | 0 | 0 | 0 表示 DNP/被动/电源源头，或已计入所属功耗域 |
| U16 | C021 | TLV75529PDRVR | Fit / 首版贴装 | 0 | 0 | 0 | 3 | 14 | 16 | Camera 2.9 V LDO 损耗分摊 |
| U17 | C022 | TPS22917DBVR | Fit / 首版贴装 | 0 | 0 | 0 | 0 | 1 | 1 | Camera 1.8 V load switch 损耗分摊 |
| U18 | C023a | TPD4E05U06 | Fit / 首版贴装 | 0 | 0 | 0 | 0 | 0 | 0 | 0 表示 DNP/被动/电源源头，或已计入所属功耗域 |
| U19 | C023b | TPD4E05U06 | Fit / 首版贴装 | 0 | 0 | 0 | 0 | 0 | 0 | 0 表示 DNP/被动/电源源头，或已计入所属功耗域 |
| U34 | C023c | TPD4E05U06 | Fit / 首版贴装 | 0 | 0 | 0 | 0 | 0 | 0 | 0 表示 DNP/被动/电源源头，或已计入所属功耗域 |
| MK1 | C013a | T5837 (wake mic) | Fit / 首版贴装 | 3 | 3 | 3 | 3 | 3 | 3 | 常开唤醒麦克风分摊 |
| MK2 | C013b | T5837 (array mic 1) | Fit / 首版贴装 | 0 | 0 | 1.5 | 1.5 | 2.5 | 3.5 | 阵列麦克风分摊 |
| MK3 | C013c | T5837 (array mic 2) | Fit / 首版贴装 | 0 | 0 | 1.5 | 1.5 | 2.5 | 3.5 | 阵列麦克风分摊 |
| MK4 | C014 | T5837 (4th mic) | DNP / 只留焊盘不贴 | 0 | 0 | 0 | 0 | 0 | 0 | 0 表示 DNP/被动/电源源头，或已计入所属功耗域 |
| U20 | C024 | MAX98360A | Fit / 首版贴装 | 0 | 0 | 2 | 2 | 3 | 3 | MAX98360A 小信号/空闲分摊 |
| U21 | C024b | TPS22917DBVR | Fit / 首版贴装 | 0 | 0 | 0 | 0 | 0 | 0 | 0 表示 DNP/被动/电源源头，或已计入所属功耗域 |
| LS1 | C025 | CUI CMS-15113-078SP-67 | HOLD / 候选件但门禁未关闭 | 0 | 0 | 13 | 13 | 27 | 27 | 单扬声器平均声学输出功耗 |
| LS2 | C026 | 2nd speaker pad | DNP / 只留焊盘不贴 | 0 | 0 | 0 | 0 | 0 | 0 | 0 表示 DNP/被动/电源源头，或已计入所属功耗域 |
| U22 | C027 | DRV2605L | DNP / 只留焊盘不贴 | 0 | 0 | 0 | 0 | 0 | 0 | 0 表示 DNP/被动/电源源头，或已计入所属功耗域 |
| M1 | C028 | LRA/ERM motor | DNP / 只留焊盘不贴 | 0 | 0 | 0 | 0 | 0 | 0 | 0 表示 DNP/被动/电源源头，或已计入所属功耗域 |
| BT1 | C029 | LP451165 300mAh (R) | HOLD / 候选件但门禁未关闭 | 0 | 0 | 0 | 0 | 0 | 0 | 0 表示 DNP/被动/电源源头，或已计入所属功耗域 |
| BT2 | C030 | LP451165 300mAh (L) | HOLD / 候选件但门禁未关闭 | 0 | 0 | 0 | 0 | 0 | 0 | 0 表示 DNP/被动/电源源头，或已计入所属功耗域 |
| F1 | C031a | PTC/fuse (R branch) | TBD / 型号或规格待定 | 0 | 0 | 0 | 0 | 0 | 0 | 0 表示 DNP/被动/电源源头，或已计入所属功耗域 |
| F2 | C031b | PTC/fuse (L branch) | TBD / 型号或规格待定 | 0 | 0 | 0 | 0 | 0 | 0 | 0 表示 DNP/被动/电源源头，或已计入所属功耗域 |
| RS2 | C044-RCL | 10 mohm 1% | Fit / 首版贴装 | 0 | 0 | 0 | 0 | 0 | 0 | 0 表示 DNP/被动/电源源头，或已计入所属功耗域 |
| RS3 | C044-RCR | 10 mohm 1% | Fit / 首版贴装 | 0 | 0 | 0 | 0 | 0 | 0 | 0 表示 DNP/被动/电源源头，或已计入所属功耗域 |
| RS1 | C044-RBAT | 10 mohm 1% 1W | Fit / 首版贴装 | 0 | 0 | 0 | 0 | 0 | 0 | 0 表示 DNP/被动/电源源头，或已计入所属功耗域 |
| R21 | C032-BYP | 0R (pack-PCM baseline) | Fit / 首版贴装 | 0 | 0 | 0 | 0 | 0 | 0 | 0 表示 DNP/被动/电源源头，或已计入所属功耗域 |
| U23 | C032 | BQ2970 | DNP / 只留焊盘不贴 | 0 | 0 | 0 | 0 | 0 | 0 | 0 表示 DNP/被动/电源源头，或已计入所属功耗域 |
| Q1 | C032-Q | Dual N-MOSFET (b2b) | DNP / 只留焊盘不贴 | 0 | 0 | 0 | 0 | 0 | 0 | 0 表示 DNP/被动/电源源头，或已计入所属功耗域 |
| R22 | C032-Rv | 330R | DNP / 只留焊盘不贴 | 0 | 0 | 0 | 0 | 0 | 0 | 0 表示 DNP/被动/电源源头，或已计入所属功耗域 |
| C2 | C032-Cv | 0.1uF | DNP / 只留焊盘不贴 | 0 | 0 | 0 | 0 | 0 | 0 | 0 表示 DNP/被动/电源源头，或已计入所属功耗域 |
| R23 | C032-Rm | 2k | DNP / 只留焊盘不贴 | 0 | 0 | 0 | 0 | 0 | 0 | 0 表示 DNP/被动/电源源头，或已计入所属功耗域 |
| RT1 | C033a | 10k NTC B=3435 1% (R cell) | Fit / 首版贴装 | 0.5 | 0.5 | 0.5 | 0.5 | 0.5 | 0.5 | 电量计/NTC/保护监测分摊 |
| RT2 | C033b | 10k NTC B=3435 1% (L cell) | Fit / 首版贴装 | 0.5 | 0.5 | 0.5 | 0.5 | 0.5 | 0.5 | 电量计/NTC/保护监测分摊 |
| TP2 | C033-TP | Battery test points | Fit / 首版贴装 | 0 | 0 | 0 | 0 | 0 | 0 | 0 表示 DNP/被动/电源源头，或已计入所属功耗域 |
| J1 | C034 | CCP P2578MP01-06C180HT | HOLD / 候选件但门禁未关闭 | 0 | 0 | 0 | 0 | 0 | 0 | 0 表示 DNP/被动/电源源头，或已计入所属功耗域 |
| J2 | C035 | USB-C 16p USB2-only | Fit / 首版贴装 | 0 | 0 | 0 | 0 | 0 | 0 | 0 表示 DNP/被动/电源源头，或已计入所属功耗域 |
| U24 | C036 | TPD2E001 | Fit / 首版贴装 | 0 | 0 | 0 | 0 | 0 | 0 | 0 表示 DNP/被动/电源源头，或已计入所属功耗域 |
| R1 | C037a | 5.1k 1% | Fit / 首版贴装 | 0 | 0 | 0 | 0 | 0 | 0 | 0 表示 DNP/被动/电源源头，或已计入所属功耗域 |
| R2 | C037b | 5.1k 1% | Fit / 首版贴装 | 0 | 0 | 0 | 0 | 0 | 0 | 0 表示 DNP/被动/电源源头，或已计入所属功耗域 |
| J3 | C038 | Hirose FH26W-33S-0.3SHW(97) | HOLD / 候选件但门禁未关闭 | 0 | 0 | 0 | 0 | 0 | 0 | 0 表示 DNP/被动/电源源头，或已计入所属功耗域 |
| J5 | C040 | U.FL / I-PEX MHF RF test connector | DNP / 只留焊盘不贴 | 0 | 0 | 0 | 0 | 0 | 0 | 0 表示 DNP/被动/电源源头，或已计入所属功耗域 |
| TP1 | C041 | UART/SWD pogo pads | Fit / 首版贴装 | 0 | 0 | 0 | 0 | 0 | 0 | 0 表示 DNP/被动/电源源头，或已计入所属功耗域 |
| SW1 | C042a | Power/PWRKEY | Fit / 首版贴装 | 0 | 0 | 0 | 0 | 0 | 0 | 0 表示 DNP/被动/电源源头，或已计入所属功耗域 |
| SW2 | C042b | Reset | Fit / 首版贴装 | 0 | 0 | 0 | 0 | 0 | 0 | 0 表示 DNP/被动/电源源头，或已计入所属功耗域 |
| SW3 | C042c | MaskROM/Recovery | Fit / 首版贴装 | 0 | 0 | 0 | 0 | 0 | 0 | 0 表示 DNP/被动/电源源头，或已计入所属功耗域 |
| RS4 | C044-RSOC | 10 mohm 1% | Fit / 首版贴装 | 0 | 0 | 0 | 0 | 0 | 0 | 0 表示 DNP/被动/电源源头，或已计入所属功耗域 |
| RS5 | C044-RWIFI | 50 mohm 1% | Fit / 首版贴装 | 0 | 0 | 0 | 0 | 0 | 0 | 0 表示 DNP/被动/电源源头，或已计入所属功耗域 |
| RS6 | C044-RAUD | 50 mohm 1% | Fit / 首版贴装 | 0 | 0 | 0 | 0 | 0 | 0 | 0 表示 DNP/被动/电源源头，或已计入所属功耗域 |
| RS7 | C044-RC1 | 100 mohm 1% | Fit / 首版贴装 | 0 | 0 | 0 | 0 | 0 | 0 | 0 表示 DNP/被动/电源源头，或已计入所属功耗域 |
| RS8 | C044-RC8 | 100 mohm 1% | Fit / 首版贴装 | 0 | 0 | 0 | 0 | 0 | 0 | 0 表示 DNP/被动/电源源头，或已计入所属功耗域 |
| RS9 | C044-RC29 | 100 mohm 1% | Fit / 首版贴装 | 0 | 0 | 0 | 0 | 0 | 0 | 0 表示 DNP/被动/电源源头，或已计入所属功耗域 |
| U25 | C044a | INA238 (I_BAT_TOTAL) | DNP / 只留焊盘不贴 | 0 | 0 | 0 | 0 | 0 | 0 | 0 表示 DNP/被动/电源源头，或已计入所属功耗域 |
| U26 | C044-ICL | INA238 (I_CELL_L) | DNP / 只留焊盘不贴 | 0 | 0 | 0 | 0 | 0 | 0 | 0 表示 DNP/被动/电源源头，或已计入所属功耗域 |
| U27 | C044-ICR | INA238 (I_CELL_R) | DNP / 只留焊盘不贴 | 0 | 0 | 0 | 0 | 0 | 0 | 0 表示 DNP/被动/电源源头，或已计入所属功耗域 |
| U28 | C044c | INA238 (I_SOC_5V) | DNP / 只留焊盘不贴 | 0 | 0 | 0 | 0 | 0 | 0 | 0 表示 DNP/被动/电源源头，或已计入所属功耗域 |
| U29 | C044e | INA238 (I_WIFI) | DNP / 只留焊盘不贴 | 0 | 0 | 0 | 0 | 0 | 0 | 0 表示 DNP/被动/电源源头，或已计入所属功耗域 |
| U30 | C044f | INA238 (I_AUDIO) | DNP / 只留焊盘不贴 | 0 | 0 | 0 | 0 | 0 | 0 | 0 表示 DNP/被动/电源源头，或已计入所属功耗域 |
| U31 | C044-IC1 | INA238 (I_CAM_1V1) | DNP / 只留焊盘不贴 | 0 | 0 | 0 | 0 | 0 | 0 | 0 表示 DNP/被动/电源源头，或已计入所属功耗域 |
| U32 | C044-IC8 | INA238 (I_CAM_1V8) | DNP / 只留焊盘不贴 | 0 | 0 | 0 | 0 | 0 | 0 | 0 表示 DNP/被动/电源源头，或已计入所属功耗域 |
| U33 | C044-IC29 | INA238 (I_CAM_2V9) | DNP / 只留焊盘不贴 | 0 | 0 | 0 | 0 | 0 | 0 | 0 表示 DNP/被动/电源源头，或已计入所属功耗域 |
| R11 | C046a | 100k | Fit / 首版贴装 | 0 | 0 | 0 | 0 | 0 | 0 | 0 表示 DNP/被动/电源源头，或已计入所属功耗域 |
| R12 | C046b | 100k | Fit / 首版贴装 | 0 | 0 | 0 | 0 | 0 | 0 | 0 表示 DNP/被动/电源源头，或已计入所属功耗域 |
| R13 | C046c | 100k | Fit / 首版贴装 | 0 | 0 | 0 | 0 | 0 | 0 | 0 表示 DNP/被动/电源源头，或已计入所属功耗域 |
| R14 | C046d | 100k | Fit / 首版贴装 | 0 | 0 | 0 | 0 | 0 | 0 | 0 表示 DNP/被动/电源源头，或已计入所属功耗域 |
| R15 | C046e | 100k | Fit / 首版贴装 | 0 | 0 | 0 | 0 | 0 | 0 | 0 表示 DNP/被动/电源源头，或已计入所属功耗域 |
| R16 | C046f | 100k | Fit / 首版贴装 | 0 | 0 | 0 | 0 | 0 | 0 | 0 表示 DNP/被动/电源源头，或已计入所属功耗域 |
| R17 | C046g | 100k | Fit / 首版贴装 | 0 | 0 | 0 | 0 | 0 | 0 | 0 表示 DNP/被动/电源源头，或已计入所属功耗域 |
| R18 | C046h | 100k | Fit / 首版贴装 | 0 | 0 | 0 | 0 | 0 | 0 | 0 表示 DNP/被动/电源源头，或已计入所属功耗域 |
| R19 | C046i | 100k | Fit / 首版贴装 | 0 | 0 | 0 | 0 | 0 | 0 | 0 表示 DNP/被动/电源源头，或已计入所属功耗域 |
| R20 | C046j | 100k | Fit / 首版贴装 | 0 | 0 | 0 | 0 | 0 | 0 | 0 表示 DNP/被动/电源源头，或已计入所属功耗域 |
| R3 | C045a | 2.2k 1% | Fit / 首版贴装 | 0 | 0 | 0 | 0 | 0 | 0 | 0 表示 DNP/被动/电源源头，或已计入所属功耗域 |
| R4 | C045b | 2.2k 1% | Fit / 首版贴装 | 0 | 0 | 0 | 0 | 0 | 0 | 0 表示 DNP/被动/电源源头，或已计入所属功耗域 |
| R5 | C045c | 2.2k 1% | Fit / 首版贴装 | 0 | 0 | 0 | 0 | 0 | 0 | 0 表示 DNP/被动/电源源头，或已计入所属功耗域 |
| R6 | C045d | 2.2k 1% | Fit / 首版贴装 | 0 | 0 | 0 | 0 | 0 | 0 | 0 表示 DNP/被动/电源源头，或已计入所属功耗域 |
| R9 | C045e | 2.2k 1% | Fit / 首版贴装 | 0 | 0 | 0 | 0 | 0 | 0 | 0 表示 DNP/被动/电源源头，或已计入所属功耗域 |
| R10 | C045f | 2.2k 1% | Fit / 首版贴装 | 0 | 0 | 0 | 0 | 0 | 0 | 0 表示 DNP/被动/电源源头，或已计入所属功耗域 |
| **TOTAL** | | | | **22** | **134** | **362** | **450** | **1290** | **2065** | 当前模型总功耗 |

## 8. 电源域与关断策略

| 电源域 | Rail / source | 主要负载 | 默认状态 | 控制者 |
|---|---|---|---|---|
| Battery / pack | LP451165 1S2P pack PCM -> F1/F2 -> RS2/RS3 -> BAT_P -> RS1 -> NPM_VBAT | 全系统源头 | live | Pack PCM + BQ25895 charger/power path |
| AON | AON_1V8, AON_3V3, AON_LSW2 from nPM1300 | nRF54L15, NDP120, BMI270, wake mic, fuel/NTC | normal standby 常开 | nPM1300 / nRF54L15 |
| RK3576 compute | VSYS -> RS4 -> TPS61088 -> SOC_5V -> RK806S rails | RK3576, LPDDR4X, eMMC | 默认 off | nRF54L15 master + Linux safe-off handshake |
| Camera | TPS62840 CAM_1V1, TPS22917 CAM_1V8, TLV75529 CAM_2V9 | IMX415 custom FPC module | 默认 off | nRF54L15 / RK3576 |
| Wi-Fi | VSYS -> RS5 -> TPS62825 -> TPS22917 -> FCU760K | FCU760K and antenna path | 默认 off | nRF54L15 enables buck, switch, module |
| Audio | VSYS -> RS6 -> TPS22917 -> MAX98360A -> LS1 | 单 8 ohm speaker | 默认 off/muted | nRF54L15 / RK3576 |

R11-R20 为 100k default-off pull-down，保证 firmware 不在场或 reset 时，compute、camera、Wi-Fi、audio 都保持关闭。

## 9. Layout-entry gates

| Gate | 主题 | 当前状态 | 关闭条件 |
|---|---|:--:|---|
| G00 | 机械/电池 layout gate | HOLD | 真实电芯 fit、膨胀空间、固定线束/极耳出口、天线 keep-out、电池不叠在 RK3576/PMIC/boost 上 |
| G00F | Phase 1.5 floorplan | HOLD | 带尺寸的俯视/侧视 floorplan + KiCad no-route placement envelope 证明能放下 |
| G01 | RK3576 identity + HDG | OPEN | Full datasheet、HDG、ball map、package drawing、reference delta |
| G02 | LPDDR4X | OPEN | MPN、topology、placement、length report、DDR review |
| G03 | RK806S PMIC | OPEN | exact MPN、rails、inductors/caps、sequence/timing |
| G04 | eMMC/boot | OPEN | MPN、bootloader/BSP support、cold boot、power-loss recovery |
| G05 | Wi-Fi FCU760K | HOLD | Hardware Design、land pattern/3D、antenna SKU、BSP driver/firmware enumeration |
| G06 | 高功率瞬态 | OPEN | RK3576 boot/AI peak、boost soft-start、1S droop、Wi-Fi/camera/audio peaks |
| G07 | LP451165 + 1S2P pack | HOLD | 正式 datasheet、放电曲线、IR/cycle/cert、pairing/fusing/NTC/current-share |
| G08 | AON 功耗 | HOLD | nPM1300 EK config、NDP120 kit、AON <=25 mW avg / <=50 mW ceiling 实测 |
| G09 | 热/boost droop | OPEN | RK3576 burst thermal path、TPS61088/RK806 droop、UVLO margin |
| G10 | Camera module | HOLD | final IMX415 module FPC pinout、lens/FOV、lane count、rail current/timing |
| G11 | Mic/audio topology | OPEN | mic coordinates、ports、wind/AEC/beamforming、NDP120 wake path |
| G12 | Camera/front FPC interconnect | HOLD | FH26W-33S pinout、contact orientation、impedance、camera module vendor sign-off；铰链电气连接不属于 EVT V2.0 范围 |
| G13 | Magnetics/passives height | OPEN | inductor Isat/DCR/height、cap derating、wearable Z limits |
| G14 | RF/worn tune | OPEN | antenna SKU、keep-out、matching in shell and worn condition |
| G15 | Passive/manufacturing BOM | OPEN | 展开 R/C/L MPN、derating、lifecycle、alternates |

## 10. 详细 schematic cards

### U1 / C001 - RK3576

- 板卡/状态：右镜腿 Compute Board / Fit / 首版贴装 / P0
- Package field：AI_Glasses_V2:VERIFY_FCCSP698L_16x17
- 关闭门禁：G01 (RK3576 datasheet/HDG/ballmap/DDR guide)
- 中文摘要：RK3576，位于右镜腿 Compute Board，当前为 Fit / 首版贴装；按当前 schematic 进入 EVT 首版装配。
- 原始 source-of-truth 说明：Main SoC — 8-core, 6 TOPS NPU, ISP, MIPI CSI, H.264/265. Demand-started compute island (NOT always-on). Functional block: interface pins only.
- 原始 note：FCCSP698L 16.1x17.2mm 0.6mm. Ball map not yet released -> only architecturally-defined interface pins are drawn. Start as a delta off the Radxa reference (Phase 2).
- Schematic nets：VDD_CPU->VDD_CPU, VDD_GPU->VDD_GPU, VDD_NPU->VDD_NPU, VDD_LOGIC->VDD_LOGIC, VDD_DDR->VDD_DDR, VCC_DDRIO->VCC_DDRIO, VCCIO_1V8->VCCIO_1V8, VCC_3V3->VCC_3V3, GND->GND, XIN->SOC_XIN, XOUT->SOC_XOUT, PMIC_SLEEP->PMIC_SLEEP, SHUTDOWN_REQ->SOC_SHUTDOWN_REQ, SAFE_TO_OFF->SOC_SAFE_TO_OFF, ALIVE->SOC_ALIVE, FAULT->SOC_FAULT, AON_UART_RX->AON_UART_TX, AON_UART_TX->AON_UART_RX, DDR_BUS->DDR_BUS, EMMC_BUS->EMMC_BUS, FSPI_BUS->FSPI_BUS, CSI_CLK_P->CSI_CLK_P, CSI_CLK_N->CSI_CLK_N, CSI_D0_P->CSI_D0_P, CSI_D0_N->CSI_D0_N, CSI_D1_P->CSI_D1_P, CSI_D1_N->CSI_D1_N, CSI_D2_P->CSI_D2_P, CSI_D2_N->CSI_D2_N, CSI_D3_P->CSI_D3_P, CSI_D3_N->CSI_D3_N, CAM_I2C_SCL->CAM_I2C_SCL, CAM_I2C_SDA->CAM_I2C_SDA, CAM_RST_L->CAM_RST_L, CAM_PWDN_L->CAM_PWDN_L, CAM_MCLK->CAM_MCLK, PDM_ARR_CLK->PDM_ARRAY_CLK, PDM_ARR_D0->PDM_ARRAY_D0, PDM_ARR_D1->PDM_ARRAY_D1, I2S_BCLK->I2S_BCLK, I2S_LRCLK->I2S_LRCLK, I2S_DIN->I2S_DIN, SARADC_NTC->SOC_NTC, USB2_WIFI_DP->WIFI_USB_DP, USB2_WIFI_DM->WIFI_USB_DM, PCM_CLK->WIFI_PCM_CLK, PCM_SYNC->WIFI_PCM_SYNC, PCM_DIN->WIFI_PCM_DIN, PCM_DOUT->WIFI_PCM_DOUT, WIFI_WAKE_L->WIFI_WAKE_L, USB2_DP->USB2_DP, USB2_DM->USB2_DM, DBG_UART_TX->SOC_DBG_TX, DBG_UART_RX->SOC_DBG_RX, MASKROM_n->SOC_MASKROM_L, RESET_n->SOC_RESET_L, PWRKEY->SOC_PWRKEY

### U2 / C002 - RK806S-5 QFN68 7x7x0.90mm

- 板卡/状态：右镜腿 Compute Board / HOLD / 候选件但门禁未关闭 / P0
- Package field：AI_Glasses_V2:VERIFY_QFN68_7x7_EP5.49_P0.35
- 关闭门禁：G03 (official RK806S-5 datasheet, OTP/default rails, sequence, layout guide)
- 中文摘要：RK806S-5 QFN68 7x7x0.90mm，位于右镜腿 Compute Board，当前为 HOLD / 候选件但门禁未关闭；必须完成对应 gate 后才能作为 layout/fab 冻结依据。
- 原始 source-of-truth 说明：SoC PMIC — generates CPU/GPU/NPU/DDR/IO rails + power sequencing for RK3576. Reuse verified RK3576 power architecture; NOT for AON.
- 原始 note：Package envelope can be used for placement: QFN68 + exposed thermal pad, body 7.0x7.0mm, max height 0.90mm, 0.35mm pitch, ePad about 5.49x5.49mm, MSL3. Power sequence, OTP/default voltage table and compensation parts remain HOLD until complete Rockchip/Radxa reference collateral is reviewed.
- Schematic nets：VIN->SOC_5V, GND->GND, PWRON->PMIC_PWRON, SLEEP->PMIC_SLEEP, I2C_SCL->SOC_PMIC_SCL, I2C_SDA->SOC_PMIC_SDA, RESET_n->SOC_RESET_L, VDD_CPU->VDD_CPU, VDD_GPU->VDD_GPU, VDD_NPU->VDD_NPU, VDD_LOGIC->VDD_LOGIC, VDD_DDR->VDD_DDR, VCC_DDRIO->VCC_DDRIO, VCCIO_1V8->VCCIO_1V8, VCC_3V3->VCC_3V3

### U3 / C003 - Samsung K4U6E3S4AA-MGCL

- 板卡/状态：右镜腿 Compute Board / HOLD / 候选件但门禁未关闭 / P0
- Package field：AI_Glasses_V2:VERIFY_FBGA200_0.65
- 关闭门禁：G02 (Samsung datasheet/ball map/IBIS + Rockchip DDR AVL/init + length report)
- 中文摘要：Samsung K4U6E3S4AA-MGCL，位于右镜腿 Compute Board，当前为 HOLD / 候选件但门禁未关闭；必须完成对应 gate 后才能作为 layout/fab 冻结依据。
- 原始 source-of-truth 说明：EVT system memory baseline — Samsung K4U6E3S4AA-MGCL, 16Gb / 2GB, x32, 200-ball FBGA 0.65mm, LPDDR4X-4266 class. Use this Radxa reference MPN for first chip-down boot risk reduction; 4GB is a later BOM variant only.
- 原始 note：Do not substitute the 32Gb/4GB K4UBE3D4AB-MGCL unless Rockchip confirms DDR AVL, training binary/init parameters, rank/capacity config and ball assignment compatibility.
- Schematic nets：VDD_DDR->VDD_DDR, VDDQ->VCC_DDRIO, GND->GND, DDR_BUS->DDR_BUS

### U4 / C004 - Samsung KLMAG1JENB-B041

- 板卡/状态：右镜腿 Compute Board / HOLD / 候选件但门禁未关闭 / P0
- Package field：AI_Glasses_V2:VERIFY_BGA153
- 关闭门禁：G04 (official Samsung datasheet/package + BSP boot/HS200 then HS400 validation)
- 中文摘要：Samsung KLMAG1JENB-B041，位于右镜腿 Compute Board，当前为 HOLD / 候选件但门禁未关闭；必须完成对应 gate 后才能作为 layout/fab 冻结依据。
- 原始 source-of-truth 说明：EVT system storage baseline — Samsung KLMAG1JENB-B041, 16GB eMMC 5.1, 153-FBGA, 11.5x13.0x0.8mm, 0.5mm pitch, 8-bit, HS400 capable. VCC 2.7-3.6V, VCCQ uses 1.8V in this project. 32GB upgrade is a later BSP/supply variant.
- Schematic nets：VCC->VCC_3V3, VCCQ->VCCIO_1V8, GND->GND, EMMC_BUS->EMMC_BUS

### Y1 / C005 - 24 MHz 10 ppm XTAL

- 板卡/状态：右镜腿 Compute Board / Fit / 首版贴装 / P0
- Package field：AI_Glasses_V2:Crystal_SMD_3225
- 关闭门禁：G01 (reuse reference CL/ESR + placement distance per HDG)
- 中文摘要：24 MHz 10 ppm XTAL，位于右镜腿 Compute Board，当前为 Fit / 首版贴装；按当前 schematic 进入 EVT 首版装配。
- 原始 source-of-truth 说明：Main clock — 24 MHz, 10 ppm; load per Rockchip reference layout.
- Schematic nets：XIN->SOC_XIN, XOUT->SOC_XOUT, GND->GND

### U5 / C006 - MX25U6432F

- 板卡/状态：右镜腿 Compute Board / DNP / 只留焊盘不贴 / P1
- Package field：AI_Glasses_V2:USON-8
- 关闭门禁：Boot flow decides whether production needs it
- 中文摘要：MX25U6432F，位于右镜腿 Compute Board，当前为 DNP / 只留焊盘不贴；第一版不贴装或只作为预留。
- 原始 source-of-truth 说明：Backup boot flash — 64 Mbit 1.8 V serial NOR on FSPI. Reserved for recovery / factory test / alt-boot; not populated on first EVT.
- Schematic nets：VCC->VCCIO_1V8, GND->GND, FSPI_BUS->FSPI_BUS

### U6 / C007 - TPS61088

- 板卡/状态：右镜腿 Compute Board / HOLD / 候选件但门禁未关闭 / P0
- Package field：AI_Glasses_V2:VQFN-22_4.5x3.5
- 关闭门禁：G06/G09 (measured RK3576 boot+AI peak, soft-start, droop, thermal)
- 中文摘要：TPS61088，位于右镜腿 Compute Board，当前为 HOLD / 候选件但门禁未关闭；必须完成对应 gate 后才能作为 layout/fab 冻结依据。
- 原始 source-of-truth 说明：Main SoC 5 V boost — 1S -> SOC_5V for the compute island. High-current sync boost; EN from nRF54L15, PG back to nRF. Candidate/HOLD until peak measured.
- 原始 note：Only the RK3576 island gets a boost (Phase-3 rule). Verify RK806 input range before committing the boost; if RK806 takes 1S directly, drop it.
- Schematic nets：VIN->SOC_IN, SW->SOC_BOOST_SW, GND->GND, EN->SOC_PWR_EN, PG->SOC_5V_PGOOD, VOUT->SOC_5V

### L1 / C008 - Coilcraft XGL4020-102MEC 1.0uH

- 板卡/状态：右镜腿 Compute Board / HOLD / 候选件但门禁未关闭 / P0
- Package field：AI_Glasses_V2:VERIFY_L_4x4x2_XGL4020
- 关闭门禁：G06/G13 (Isat/DCR/thermal pass for 5.1V 3A continuous / 4A peak boost)
- 中文摘要：Coilcraft XGL4020-102MEC 1.0uH，位于右镜腿 Compute Board，当前为 HOLD / 候选件但门禁未关闭；必须完成对应 gate 后才能作为 layout/fab 冻结依据。
- 原始 source-of-truth 说明：Boost inductor for TPS61088 — Coilcraft XGL4020-102MEC candidate, 1.0uH, 4.0x4.0x2.0mm, low DCR, high-current shielded inductor. Keep SW copper small; do not route DDR/MIPI/audio/RF under the inductor.
- Schematic nets：A->SOC_IN, B->SOC_BOOST_SW

### U11 / C015 - FCU760KAAMD

- 板卡/状态：右镜腿 Compute Board / HOLD / 候选件但门禁未关闭 / P0
- Package field：AI_Glasses_V2:VERIFY_LCC_13x12.2_Quectel
- 关闭门禁：G05 (Quectel HW Design + RK3576 BSP driver/firmware/enum) + official LCC land pattern
- 中文摘要：FCU760KAAMD，位于右镜腿 Compute Board，当前为 HOLD / 候选件但门禁未关闭；必须完成对应 gate 后才能作为 layout/fab 冻结依据。
- 原始 source-of-truth 说明：Wi-Fi 6 + BT 5.4 module — Quectel FCU760K, LCC 13.0x12.2x2.0mm. USB2 to RK3576 host; PCM for BT audio; VBAT 3.0-3.6V (typ 3.3V), max TX 353 mA. On-demand, load-switched off.
- 原始 note：CONFIRMED on Radxa CM4 V1.20 p20; interface = USB2 (NOT SDIO). Single-antenna SKU FCU760KAAMD shares Wi-Fi/BT on ANT_WIFI_BT. Optional ANT_BT is kept only as a DNP test/matching node until Quectel FAE confirms its use. Exact LCC pinout/land pattern + Linux driver/firmware stay HOLD pending Quectel Hardware Design.
- Schematic nets：VBAT->WIFI_VBAT_3V3, GND->GND, USB_DP->WIFI_USB_DP, USB_DM->WIFI_USB_DM, CHIP_EN->WIFI_CHIP_EN, PCM_CLK->WIFI_PCM_CLK, PCM_SYNC->WIFI_PCM_SYNC, PCM_IN->WIFI_PCM_DOUT, PCM_OUT->WIFI_PCM_DIN, WAKE->WIFI_WAKE_L, ANT_WIFI_BT->WIFI_ANT, ANT_BT_DNP->BLE_ANT

### U12 / C016 - TPS62825

- 板卡/状态：右镜腿 Compute Board / Fit / 首版贴装 / P0
- Package field：AI_Glasses_V2:QFN_1.5x1.5
- 关闭门禁：G05/G06 (inductor/caps per module 353mA TX peak + ripple)
- 中文摘要：TPS62825，位于右镜腿 Compute Board，当前为 Fit / 首版贴装；按当前 schematic 进入 EVT 首版装配。
- 原始 source-of-truth 说明：Wi-Fi dedicated 3.3 V buck — feeds FCU760K VBAT; >=500 mA capability for the 353 mA TX peak (pack note). EN by AON MCU. Avoids routing the radio through 5 V (Phase-3 rule).
- Schematic nets：VIN->WIFI_IN, SW->WIFI_BUCK_SW, GND->GND, EN->WIFI_BUCK_EN, VOUT->WIFI_3V3

### L2 / C016c - Wi-Fi buck inductor (TBD)

- 板卡/状态：右镜腿 Compute Board / Fit / 首版贴装 / P0
- Package field：AI_Glasses_V2:VERIFY_L_2x2
- 关闭门禁：Per TPS62825 peak+ripple
- 中文摘要：Wi-Fi buck inductor (TBD)，位于右镜腿 Compute Board，当前为 Fit / 首版贴装；按当前 schematic 进入 EVT 首版装配。
- 原始 source-of-truth 说明：Wi-Fi buck inductor — SW->3V3, value per TPS62825 design.
- Schematic nets：A->WIFI_BUCK_SW, B->WIFI_3V3

### U13 / C016b - TPS22917DBVR

- 板卡/状态：右镜腿 Compute Board / Fit / 首版贴装 / P0
- Package field：Package_TO_SOT_SMD:SOT-23-5
- 关闭门禁：G05 (turn-on sequence w/ module)
- 中文摘要：TPS22917DBVR，位于右镜腿 Compute Board，当前为 Fit / 首版贴装；按当前 schematic 进入 EVT 首版装配。
- 原始 source-of-truth 说明：Wi-Fi load switch — gates WIFI_3V3 -> FCU760K VBAT with QOD + reverse block. EN by AON MCU.
- Schematic nets：VIN->WIFI_3V3, VOUT->WIFI_VBAT_3V3, EN->WIFI_LS_EN, GND->GND

### C1 / C015-C - 47uF 6.3V X5R

- 板卡/状态：右镜腿 Compute Board / Fit / 首版贴装 / P0
- Package field：AI_Glasses_V2:C_0805
- 关闭门禁：Local bulk per Quectel HW Design
- 中文摘要：47uF 6.3V X5R，位于右镜腿 Compute Board，当前为 Fit / 首版贴装；按当前 schematic 进入 EVT 首版装配。
- 原始 source-of-truth 说明：FCU760K VBAT bulk storage — 47 uF local reservoir next to the module (pack: 47uF + 1uF + 100nF). Rides the 353 mA TX burst.
- Schematic nets：A->WIFI_VBAT_3V3, B->GND

### RT3 / C043 - 10k NTC B=3435

- 板卡/状态：右镜腿 Compute Board / Fit / 首版贴装 / P0
- Package field：AI_Glasses_V2:R_0402
- 关闭门禁：Probe position per thermal sim
- 中文摘要：10k NTC B=3435，位于右镜腿 Compute Board，当前为 Fit / 首版贴装；按当前 schematic 进入 EVT 首版装配。
- 原始 source-of-truth 说明：SoC/enclosure temp monitor — 10k NTC on SoC heat-spreader + skin side. Wearable must watch both die and skin temp.
- Schematic nets：A->SOC_NTC, B->GND

### U35 / C010b - BQ25895

- 板卡/状态：右镜腿 Compute Board / HOLD / 候选件但门禁未关闭 / P0
- Package field：AI_Glasses_V2:VERIFY_WQFN_24_BQ25895
- 关闭门禁：Charger/power-path config, TS thresholds, 1S2P charge profile, thermal/current validation
- 中文摘要：BQ25895，位于右镜腿 Compute Board，当前为 HOLD / 候选件但门禁未关闭；必须完成对应 gate 后才能作为 layout/fab 冻结依据。
- 原始 source-of-truth 说明：Primary 1S charger + Power Path — protected 5V input to SYS/VSYS and 1S2P pack. Use with pack-internal PCM, BQ25895 TS temperature protection, input current limit, and software charge-profile control. First bring-up must prove low-battery boost droop and charge/boost coexistence.
- 原始 note：This is the board-level charger/power-path block for EVT V2.0. nPM1300 remains the AON buck/fuel-gauge/low-power PMIC; do not also populate board-level BQ2970 protection when the pack includes PCM.
- Schematic nets：VBUS->USB_5V, SYS->VSYS, BAT->NPM_VBAT, GND->GND, SCL->I2C_AON_SCL, SDA->I2C_AON_SDA, TS->NTC_R, INT_L->CHG_INT_L, CE_L->CHG_CE_L, PG_L->CHG_PG_L

### U36 / C034b - 5V input eFuse/OVP (MPN TBD)

- 板卡/状态：右镜腿 Compute Board / HOLD / 候选件但门禁未关闭 / P0
- Package field：AI_Glasses_V2:VERIFY_EFUSE_OVP
- 关闭门禁：Select MPN for pogo/USB VBUS surge, reverse, OVP, current limit and thermal fault
- 中文摘要：5V input eFuse/OVP (MPN TBD)，位于右镜腿 Compute Board，当前为 HOLD / 候选件但门禁未关闭；必须完成对应 gate 后才能作为 layout/fab 冻结依据。
- 原始 source-of-truth 说明：5V input protection between magnetic pogo/EVT USB-C and charger input. Required: VBUS TVS/OVP/eFuse/current limit, fault indication and layout close to the connector path.
- Schematic nets：IN->VBUS_RAW, OUT->USB_5V, GND->GND, FLT_L->VBUS_FAULT_L

### U7 / C009 - nRF54L15-QFN48

- 板卡/状态：左镜腿 AON/Power Board / Fit / 首版贴装 / P0
- Package field：AI_Glasses_V2:QFN-48_6x6
- 关闭门禁：EVT-frozen (RF layout/SDK/package to freeze early)
- 中文摘要：nRF54L15-QFN48，位于左镜腿 AON/Power Board，当前为 Fit / 首版贴装；按当前 schematic 进入 EVT 首版装配。
- 原始 source-of-truth 说明：Low-power BLE MCU — ALWAYS ON. Owns the system state machine; controls RK3576/camera/Wi-Fi/audio power ENs; talks IMU/buttons/gauge; UART to RK3576, SPI to NDP120. Turns RK3576 from an always-on host into a demand accelerator.
- 原始 note：nRF54L15 (not nRF52/53): 1.5MB NVM / 256KB RAM headroom, long-life platform, later WLCSP shrink. QFN48 for the debuggable EVT board. EVT V2.0 does not fit a separate nRF BLE antenna; phone/BLE data path is assigned to FCU760K shared RF unless RF coexistence testing reopens the DNP ANT_BT option.
- Schematic nets：VDD_1V8->AON_1V8, VDD_3V3->AON_3V3, GND->GND, ANT_DNP->NC, SOC_PWR_EN->SOC_PWR_EN, SOC_5V_PGOOD->SOC_5V_PGOOD, PMIC_PWRON->PMIC_PWRON, CAM_1V1_EN->CAM_1V1_EN, CAM_1V8_EN->CAM_1V8_EN, CAM_2V9_EN->CAM_2V9_EN, WIFI_BUCK_EN->WIFI_BUCK_EN, WIFI_LS_EN->WIFI_LS_EN, WIFI_CHIP_EN->WIFI_CHIP_EN, AUDIO_LS_EN->AUDIO_LS_EN, AMP_SD->AUDIO_AMP_SD, SOC_SHDN_REQ->SOC_SHUTDOWN_REQ, SOC_SAFE_OFF->SOC_SAFE_TO_OFF, SOC_ALIVE->SOC_ALIVE, SOC_FAULT->SOC_FAULT, AON_UART_TX->AON_UART_TX, AON_UART_RX->AON_UART_RX, I2C_SCL->I2C_AON_SCL, I2C_SDA->I2C_AON_SDA, PMIC_INT_L->PMIC_INT_L, PMIC_SHPHLD->PMIC_SHPHLD, CHG_INT_L->CHG_INT_L, CHG_CE_L->CHG_CE_L, CHG_PG_L->CHG_PG_L, VBUS_FAULT_L->VBUS_FAULT_L, IMU_INT1->IMU_INT1, IMU_INT2->IMU_INT2, DSP_SCK->DSP_SPI_SCK, DSP_MOSI->DSP_SPI_MOSI, DSP_MISO->DSP_SPI_MISO, DSP_CS_n->DSP_SPI_CS_n, DSP_WAKE->DSP_WAKE, DSP_READY->DSP_READY, DSP_FAULT->DSP_FAULT, DSP_RST_n->DSP_RESET_L, HAPTIC_EN->HAPTIC_EN, SWDIO->NRF_SWDIO, SWDCLK->NRF_SWDCLK

### U8 / C010 - nPM1300

- 板卡/状态：左镜腿 AON/Power Board / HOLD / 候选件但门禁未关闭 / P0
- Package field：AI_Glasses_V2:QFN_5x5
- 关闭门禁：G08 (AON <=25/50mW) — configure via nPM PowerUP on EK before board
- 中文摘要：nPM1300，位于左镜腿 AON/Power Board，当前为 HOLD / 候选件但门禁未关闭；必须完成对应 gate 后才能作为 layout/fab 冻结依据。
- 原始 source-of-truth 说明：AON PMIC / low-power rail manager — fuel-gauge support, dual Buck, LDO/Load-Switch and Ship/Hibernate for the small AON world ONLY; NOT the RK3576 peak path.
- 原始 note：BQ25895 is the primary charger + power-path block in EVT V2.0. nPM1300 stays in the AON domain for low-Iq rails/gauge/support functions and must be configured for the supplier-built 1S2P pack, not a single 300mAh cell.
- Schematic nets：VBAT->NPM_VBAT, VBUS->USB_5V, VSYS->VSYS, GND->GND, BUCK1->AON_1V8, BUCK2->AON_3V3, LSW2->AON_LSW2, NTC_R->NTC_R, NTC_L->NTC_L, I2C_SCL->I2C_AON_SCL, I2C_SDA->I2C_AON_SDA, INT->PMIC_INT_L, SHPHLD->PMIC_SHPHLD

### U9 / C011 - NDP120

- 板卡/状态：左镜腿 AON/Power Board / HOLD / 候选件但门禁未关闭 / P0
- Package field：AI_Glasses_V2:VERIFY_QFN_5x5
- 关闭门禁：Full datasheet + dev kit + measured listening power + NDA/licensing
- 中文摘要：NDP120，位于左镜腿 AON/Power Board，当前为 HOLD / 候选件但门禁未关闭；必须完成对应 gate 后才能作为 layout/fab 冻结依据。
- 原始 source-of-truth 说明：Always-on Audio DSP — ultra-low-power wake-word + audio front-end; wakes the MCU over GPIO. Moves voice listening off RK3576. Keep bypass + DNP capability.
- 原始 note：HOLD until hardware datasheet, rails/sequence, PDM/I2S detail, firmware/model tools, wake-word licensing, real listening power, MOQ/lead all in hand.
- Schematic nets：VDD_1V8->AON_1V8, VDD_3V3->AON_3V3, GND->GND, PDM_CLK->PDM_WAKE_CLK, PDM_DATA->PDM_WAKE_DATA, HOST_SCK->DSP_SPI_SCK, HOST_MOSI->DSP_SPI_MOSI, HOST_MISO->DSP_SPI_MISO, HOST_CS_n->DSP_SPI_CS_n, WAKE->DSP_WAKE, READY->DSP_READY, FAULT->DSP_FAULT, RESET_n->DSP_RESET_L

### U10 / C012 - BMI270

- 板卡/状态：左镜腿 AON/Power Board / Fit / 首版贴装 / P0
- Package field：Package_LGA:LGA-14_2.5x3mm_P0.5mm
- 关闭门禁：Evaluate false-trigger under real frame vibration
- 中文摘要：BMI270，位于左镜腿 AON/Power Board，当前为 Fit / 首版贴装；按当前 schematic 进入 EVT 首版装配。
- 原始 source-of-truth 说明：6-axis IMU — low-power motion detect; motion-interrupt wakes the MCU. Cycling/running state ID for wearables.
- Schematic nets：VDD->AON_1V8, VDDIO->AON_1V8, GND->GND, SCL->I2C_AON_SCL, SDA->I2C_AON_SDA, INT1->IMU_INT1, INT2->IMU_INT2

### J6 / C018 - FCU760K ANT_BT DNP test pad

- 板卡/状态：镜腿后端电池/扬声器/天线区 / DNP / 只留焊盘不贴 / P0
- Package field：AI_Glasses_V2:VERIFY_ANT
- 关闭门禁：Only populate if Quectel FAE + coexistence test requires the second RF port
- 中文摘要：FCU760K ANT_BT DNP test pad，位于镜腿后端电池/扬声器/天线区，当前为 DNP / 只留焊盘不贴；第一版不贴装或只作为预留。
- 原始 source-of-truth 说明：Optional second RF feed for FCU760K ANT_BT — DNP/test only. EVT V2.0 does not fit a separate BLE antenna; Wi-Fi/BLE share the main dual-band FPC antenna on WIFI_ANT.
- Schematic nets：ANT->BLE_ANT, GND->GND

### J7 / C017 - Taoglas FXP840.07.0055B

- 板卡/状态：镜腿后端电池/扬声器/天线区 / HOLD / 候选件但门禁未关闭 / P0
- Package field：AI_Glasses_V2:VERIFY_FPC_ANT_14x5
- 关闭门禁：G14 (worn-state tune + antenna keep-out in full shell with battery/speaker)
- 中文摘要：Taoglas FXP840.07.0055B，位于镜腿后端电池/扬声器/天线区，当前为 HOLD / 候选件但门禁未关闭；必须完成对应 gate 后才能作为 layout/fab 冻结依据。
- 原始 source-of-truth 说明：Shared Wi-Fi/BLE dual-band FPC antenna candidate — Taoglas FXP840.07.0055B, about 14x5x0.1mm with 55mm coax/MHF-style termination. Place at temple end or non-metal window; keep away from battery, speaker magnet, pogo magnet, shields and copper.
- Schematic nets：ANT->WIFI_ANT, GND->GND

### U14 / C019 - Sony IMX415-AAQR-C custom module

- 板卡/状态：前框 Sensor Board / HOLD / 候选件但门禁未关闭 / P0
- Package field：AI_Glasses_V2:VERIFY_CAM_MODULE
- 关闭门禁：G10 (module lens/FOV/FPC pinout/lane/supply/timing from vendor)
- 中文摘要：Sony IMX415-AAQR-C custom module，位于前框 Sensor Board，当前为 HOLD / 候选件但门禁未关闭；必须完成对应 gate 后才能作为 layout/fab 冻结依据。
- 原始 source-of-truth 说明：Main camera module target — Sony IMX415-AAQR-C, 8.46 MP, 3840x2160 30fps baseline, RAW10 first, 4-lane MIPI CSI-2. Custom small sensor+lens rigid island + FPC (NOT a dev module). Sensor PCB target <=15x15mm, total camera Z target <=9.5mm. Sensor rails (Sony datasheet): AVDD 2.9V 128/156mA, IOVDD 1.8V 3mA, DVDD 1.1V 187/250mA (~0.58W typ, ~0.77W max).
- 原始 note：IMX415 mechanical stack is still TBD: lens MPN, IR-cut, PCB, glue, FPC exit, mount, TTL/BFL/CRA/MTF/distortion/relative illumination and module STEP must come from the module vendor. Use orange TBD mechanical envelope; not released for tooling.
- Schematic nets：DVDD_1V1->CAM_1V1_S, IOVDD_1V8->CAM_1V8_S, AVDD_2V9->CAM_2V9_S, GND->GND, CSI_CLK_P->CSI_CLK_P, CSI_CLK_N->CSI_CLK_N, CSI_D0_P->CSI_D0_P, CSI_D0_N->CSI_D0_N, CSI_D1_P->CSI_D1_P, CSI_D1_N->CSI_D1_N, CSI_D2_P->CSI_D2_P, CSI_D2_N->CSI_D2_N, CSI_D3_P->CSI_D3_P, CSI_D3_N->CSI_D3_N, SCL->CAM_I2C_SCL, SDA->CAM_I2C_SDA, XCLR_L->CAM_RST_L, PWDN_L->CAM_PWDN_L, INCK->CAM_MCLK, MODULE_ID->CAM_MODULE_ID

### U15 / C020 - TPS62840

- 板卡/状态：前框 Sensor Board / Fit / 首版贴装 / P0
- Package field：AI_Glasses_V2:VERIFY_WSON
- 关闭门禁：Output current/noise per final module (DVDD ~250mA max + margin)
- 中文摘要：TPS62840，位于前框 Sensor Board，当前为 Fit / 首版贴装；按当前 schematic 进入 EVT 首版装配。
- 原始 source-of-truth 说明：Camera DVDD 1.1 V buck — ultra-low-Iq (~60 nA) buck for the sensor core (DVDD 187/250mA), up to ~750 mA. EN by AON MCU / SoC. True power-down when camera off.
- Schematic nets：VIN->VSYS, SW->CAM_1V1_SW, GND->GND, EN->CAM_1V1_EN, VOUT->CAM_1V1

### L3 / C020b - Cam 1V1 buck inductor (TBD)

- 板卡/状态：前框 Sensor Board / Fit / 首版贴装 / P0
- Package field：AI_Glasses_V2:VERIFY_L_1.6x0.8
- 关闭门禁：Per TPS62840 design
- 中文摘要：Cam 1V1 buck inductor (TBD)，位于前框 Sensor Board，当前为 Fit / 首版贴装；按当前 schematic 进入 EVT 首版装配。
- 原始 source-of-truth 说明：Camera 1.1 V buck inductor — SW->1V1.
- Schematic nets：A->CAM_1V1_SW, B->CAM_1V1

### U16 / C021 - TLV75529PDRVR

- 板卡/状态：前框 Sensor Board / Fit / 首版贴装 / P0
- Package field：AI_Glasses_V2:WSON-6_2x2
- 关闭门禁：Verify vs IMX415 AVDD peak (156mA) + PSRR
- 中文摘要：TLV75529PDRVR，位于前框 Sensor Board，当前为 Fit / 首版贴装；按当前 schematic 进入 EVT 首版装配。
- 原始 source-of-truth 说明：Camera AVDD 2.9 V LDO — 500 mA low-noise analog supply (AVDD 128/156mA). Low-noise LDO, NOT a series resistor off 3.3V (pack §23).
- Schematic nets：VIN->VSYS, EN->CAM_2V9_EN, GND->GND, VOUT->CAM_2V9

### U17 / C022 - TPS22917DBVR

- 板卡/状态：前框 Sensor Board / Fit / 首版贴装 / P0
- Package field：Package_TO_SOT_SMD:SOT-23-5
- 关闭门禁：Check reverse block, ramp, QOD, logic level
- 中文摘要：TPS22917DBVR，位于前框 Sensor Board，当前为 Fit / 首版贴装；按当前 schematic 进入 EVT 首版装配。
- 原始 source-of-truth 说明：Camera IOVDD 1.8 V load switch / isolation — low-leak switch from AON_1V8 for camera I/O (IOVDD ~3mA); Quick-Output-Discharge kills reverse feed when camera off (§24).
- Schematic nets：VIN->AON_1V8, VOUT->CAM_1V8_SW, EN->CAM_1V8_EN, GND->GND

### U18 / C023a - TPD4E05U06

- 板卡/状态：前框 Sensor Board / Fit / 首版贴装 / P0
- Package field：AI_Glasses_V2:USON
- 关闭门禁：Low-cap array near FPC entry
- 中文摘要：TPD4E05U06，位于前框 Sensor Board，当前为 Fit / 首版贴装；按当前 schematic 进入 EVT 首版装配。
- 原始 source-of-truth 说明：MIPI/FPC ESD (clk + D0) — ultra-low-cap 4-ch ESD at the FPC entry.
- Schematic nets：CLK_P->CSI_CLK_P, CLK_N->CSI_CLK_N, D0_P->CSI_D0_P, D0_N->CSI_D0_N, GND->GND

### U19 / C023b - TPD4E05U06

- 板卡/状态：前框 Sensor Board / Fit / 首版贴装 / P0
- Package field：AI_Glasses_V2:USON
- 关闭门禁：Low-cap array near FPC entry
- 中文摘要：TPD4E05U06，位于前框 Sensor Board，当前为 Fit / 首版贴装；按当前 schematic 进入 EVT 首版装配。
- 原始 source-of-truth 说明：MIPI/FPC ESD (D1 + control) — ultra-low-cap ESD for the second lane pair and critical control.
- Schematic nets：D1_P->CSI_D1_P, D1_N->CSI_D1_N, RST->CAM_RST_L, MCLK->CAM_MCLK, GND->GND

### U34 / C023c - TPD4E05U06

- 板卡/状态：前框 Sensor Board / Fit / 首版贴装 / P0
- Package field：AI_Glasses_V2:USON
- 关闭门禁：Low-cap array near FPC entry for 4-lane CSI
- 中文摘要：TPD4E05U06，位于前框 Sensor Board，当前为 Fit / 首版贴装；按当前 schematic 进入 EVT 首版装配。
- 原始 source-of-truth 说明：MIPI/FPC ESD (D2 + D3) — adds the two lane pairs required by the 4-lane IMX415 EVT target.
- Schematic nets：D2_P->CSI_D2_P, D2_N->CSI_D2_N, D3_P->CSI_D3_P, D3_N->CSI_D3_N, GND->GND

### MK1 / C013a - T5837 (wake mic)

- 板卡/状态：前框 Sensor Board / Fit / 首版贴装 / P0
- Package field：AI_Glasses_V2:LGA-5_3.5x2.65
- 关闭门禁：G11 (mic coords/ports/wind/wake + AEC/beamforming)
- 中文摘要：T5837 (wake mic)，位于前框 Sensor Board，当前为 Fit / 首版贴装；按当前 schematic 进入 EVT 首版装配。
- 原始 source-of-truth 说明：PDM wake mic — dedicated always-on wake channel into NDP120 (AON audio domain). Deep Off must capture without RK3576.
- Schematic nets：VDD->AON_3V3, GND->GND, CLK->PDM_WAKE_CLK, DATA->PDM_WAKE_DATA

### MK2 / C013b - T5837 (array mic 1)

- 板卡/状态：前框 Sensor Board / Fit / 首版贴装 / P0
- Package field：AI_Glasses_V2:LGA-5_3.5x2.65
- 关闭门禁：G11
- 中文摘要：T5837 (array mic 1)，位于前框 Sensor Board，当前为 Fit / 首版贴装；按当前 schematic 进入 EVT 首版装配。
- 原始 source-of-truth 说明：PDM array mic 1 — into RK3576 PDM for beamforming during vision/voice tasks.
- Schematic nets：VDD->AON_3V3, GND->GND, CLK->PDM_ARRAY_CLK, DATA->PDM_ARRAY_D0

### MK3 / C013c - T5837 (array mic 2)

- 板卡/状态：前框 Sensor Board / Fit / 首版贴装 / P0
- Package field：AI_Glasses_V2:LGA-5_3.5x2.65
- 关闭门禁：G11
- 中文摘要：T5837 (array mic 2)，位于前框 Sensor Board，当前为 Fit / 首版贴装；按当前 schematic 进入 EVT 首版装配。
- 原始 source-of-truth 说明：PDM array mic 2 — second array channel (L/R stereo on shared PDM clock).
- Schematic nets：VDD->AON_3V3, GND->GND, CLK->PDM_ARRAY_CLK, DATA->PDM_ARRAY_D1

### MK4 / C014 - T5837 (4th mic)

- 板卡/状态：前框 Sensor Board / DNP / 只留焊盘不贴 / P1
- Package field：AI_Glasses_V2:LGA-5_3.5x2.65
- 关闭门禁：G11 (populate only if array sim/proto needs it)
- 中文摘要：T5837 (4th mic)，位于前框 Sensor Board，当前为 DNP / 只留焊盘不贴；第一版不贴装或只作为预留。
- 原始 source-of-truth 说明：4th array mic — footprint only; on the switchable AON_LSW2 rail (nPM1300 load switch, §14 'spare mic') so it can be fully powered down. Not populated until array/wind tests.
- Schematic nets：VDD->AON_LSW2, GND->GND, CLK->PDM_ARRAY_CLK, DATA->PDM_ARRAY_D1

### U20 / C024 - MAX98360A

- 板卡/状态：右镜腿 Compute Board / Fit / 首版贴装 / P0
- Package field：AI_Glasses_V2:VERIFY_WLP_QFN
- 关闭门禁：Verify Z/cavity/EMI/peak power
- 中文摘要：MAX98360A，位于右镜腿 Compute Board，当前为 Fit / 首版贴装；按当前 schematic 进入 EVT 首版装配。
- 原始 source-of-truth 说明：Digital Class-D amp — I2S in, mono, low-power shutdown. Direct digital audio chain, no analog codec. Fully power-downable via load switch.
- Schematic nets：VDD->AUDIO_PWR, GND->GND, BCLK->I2S_BCLK, LRCLK->I2S_LRCLK, DIN->I2S_DIN, SD_MODE->AUDIO_AMP_SD, OUT_P->SPK_P, OUT_N->SPK_N

### U21 / C024b - TPS22917DBVR

- 板卡/状态：右镜腿 Compute Board / Fit / 首版贴装 / P0
- Package field：Package_TO_SOT_SMD:SOT-23-5
- 关闭门禁：Amp must be fully power-downable (V1 lesson)
- 中文摘要：TPS22917DBVR，位于右镜腿 Compute Board，当前为 Fit / 首版贴装；按当前 schematic 进入 EVT 首版装配。
- 原始 source-of-truth 说明：Audio load switch — gates AUDIO_PWR to the amp; EN by AON MCU / SoC.
- Schematic nets：VIN->AUDIO_IN, VOUT->AUDIO_PWR, EN->AUDIO_LS_EN, GND->GND

### LS1 / C025 - CUI CMS-15113-078SP-67

- 板卡/状态：镜腿后端电池/扬声器/天线区 / HOLD / 候选件但门禁未关闭 / P0
- Package field：AI_Glasses_V2:VERIFY_SPK_15x11x3
- 关闭门禁：Acoustic EVT: 0.3-0.5cc cavity, port/foam seal, magnet-to-antenna clearance, leak test
- 中文摘要：CUI CMS-15113-078SP-67，位于镜腿后端电池/扬声器/天线区，当前为 HOLD / 候选件但门禁未关闭；必须完成对应 gate 后才能作为 layout/fab 冻结依据。
- 原始 source-of-truth 说明：Main speaker EVT baseline — CUI CMS-15113-078SP-67, 15x11x3mm, 8 ohm, 0.7W rated / 1W max, about 91dB sensitivity, front IP67. Drive as mono differential speaker from the digital Class-D amp; limit first firmware to 0.5-0.7W RMS.
- Schematic nets：P->SPK_P, N->SPK_N

### LS2 / C026 - 2nd speaker pad

- 板卡/状态：镜腿后端电池/扬声器/天线区 / DNP / 只留焊盘不贴 / P1
- Package field：AI_Glasses_V2:VERIFY_SPK
- 关闭门禁：Decide dual-speaker at EVT-B
- 中文摘要：2nd speaker pad，位于镜腿后端电池/扬声器/天线区，当前为 DNP / 只留焊盘不贴；第一版不贴装或只作为预留。
- 原始 source-of-truth 说明：Second speaker land — reserved for productization; not populated first version.
- Schematic nets：P->NC, N->NC

### U22 / C027 - DRV2605L

- 板卡/状态：左镜腿 AON/Power Board / DNP / 只留焊盘不贴 / P1
- Package field：Package_SO:MSOP-10_3x3mm_P0.5mm
- 关闭门禁：Vibration P1 — may DNP on first board (IMU/mic coupling)
- 中文摘要：DRV2605L，位于左镜腿 AON/Power Board，当前为 DNP / 只留焊盘不贴；第一版不贴装或只作为预留。
- 原始 source-of-truth 说明：Haptic driver — LRA/ERM driver, I2C, waveform library. Silent safety reminder path.
- Schematic nets：VDD->VSYS, GND->GND, SCL->I2C_AON_SCL, SDA->I2C_AON_SDA, EN->HAPTIC_EN, OUT_P->HAPTIC_P, OUT_N->HAPTIC_N

### M1 / C028 - LRA/ERM motor

- 板卡/状态：镜腿后端电池/扬声器/天线区 / DNP / 只留焊盘不贴 / P1
- Package field：AI_Glasses_V2:VERIFY_LRA
- 关闭门禁：Vibration P1
- 中文摘要：LRA/ERM motor，位于镜腿后端电池/扬声器/天线区，当前为 DNP / 只留焊盘不贴；第一版不贴装或只作为预留。
- 原始 source-of-truth 说明：LRA/ERM motor — short haptic alerts; can be replaced by phone vibration first version.
- Schematic nets：P->HAPTIC_P, N->HAPTIC_N

### BT1 / C029 - LP451165 300mAh (R)

- 板卡/状态：镜腿后端电池/扬声器/天线区 / HOLD / 候选件但门禁未关闭 / P0
- Package field：AI_Glasses_V2:VERIFY_CELL_4.5x11x65
- 关闭门禁：G07 (full datasheet, >=2C, IR, cycles, cert)
- 中文摘要：LP451165 300mAh (R)，位于镜腿后端电池/扬声器/天线区，当前为 HOLD / 候选件但门禁未关闭；必须完成对应 gate 后才能作为 layout/fab 冻结依据。
- 原始 source-of-truth 说明：Right-side element of the supplier-built 1S2P pack — LP451165 nominal cell candidate, one per temple. Mechanical control envelope per side is 70x12.8x5.6mm including tabs, PCM/insulation allowance, foam and swelling space.
- 原始 note：Do not parallel two independent protected cells on the PCB. G07 must close with one pack supplier building a matched 1S2P pack, common PCM, branch fusing/fusible links, two NTCs, official 2D/STEP, tab/cable exit, UN38.3/MSDS/IEC62133-equivalent data.
- Schematic nets：+->BATR_P, -->CELL_NEG

### BT2 / C030 - LP451165 300mAh (L)

- 板卡/状态：镜腿后端电池/扬声器/天线区 / HOLD / 候选件但门禁未关闭 / P0
- Package field：AI_Glasses_V2:VERIFY_CELL_70x12.8x5.6_maxenv
- 关闭门禁：G07
- 中文摘要：LP451165 300mAh (L)，位于镜腿后端电池/扬声器/天线区，当前为 HOLD / 候选件但门禁未关闭；必须完成对应 gate 后才能作为 layout/fab 冻结依据。
- 原始 source-of-truth 说明：Left-side element of the supplier-built 1S2P pack — same batch/capacity/IR-matched to the right side. Use the same 70x12.8x5.6mm mechanical control envelope and pack supplier cable/tab/PCM drawing.
- Schematic nets：+->BATL_P, -->CELL_NEG

### F1 / C031a - PTC/fuse (R branch)

- 板卡/状态：镜腿后端电池/扬声器/天线区 / TBD / 型号或规格待定 / P0
- Package field：AI_Glasses_V2:VERIFY_FUSE
- 关闭门禁：Rating from peak-current calc (> branch peak, < FPC rating)
- 中文摘要：PTC/fuse (R branch)，位于镜腿后端电池/扬声器/天线区，当前为 TBD / 型号或规格待定；具体 MPN/额定值仍需供应商资料或实测关闭。
- 原始 source-of-truth 说明：Right branch protection — resettable PTC / fusible link in the right cell branch. Limits a single-cell / FPC short (§7).
- Schematic nets：A->BATR_P, B->BATR_F

### F2 / C031b - PTC/fuse (L branch)

- 板卡/状态：镜腿后端电池/扬声器/天线区 / TBD / 型号或规格待定 / P0
- Package field：AI_Glasses_V2:VERIFY_FUSE
- 关闭门禁：Rating from peak-current calc
- 中文摘要：PTC/fuse (L branch)，位于镜腿后端电池/扬声器/天线区，当前为 TBD / 型号或规格待定；具体 MPN/额定值仍需供应商资料或实测关闭。
- 原始 source-of-truth 说明：Left branch protection — resettable PTC / fusible link in the left cell branch.
- Schematic nets：A->BATL_P, B->BATL_F

### RS2 / C044-RCL - 10 mohm 1%

- 板卡/状态：镜腿后端电池/扬声器/天线区 / Fit / 首版贴装 / P0
- Package field：AI_Glasses_V2:R_0805_shunt
- 关闭门禁：Branch current-share (§7/§29)
- 中文摘要：10 mohm 1%，位于镜腿后端电池/扬声器/天线区，当前为 Fit / 首版贴装；按当前 schematic 进入 EVT 首版装配。
- 原始 source-of-truth 说明：Left branch shunt — BATL_F -> BAT_P; I_CELL_L for current-share monitoring.
- Schematic nets：A->BATL_F, B->BAT_P

### RS3 / C044-RCR - 10 mohm 1%

- 板卡/状态：镜腿后端电池/扬声器/天线区 / Fit / 首版贴装 / P0
- Package field：AI_Glasses_V2:R_0805_shunt
- 关闭门禁：Branch current-share (§7/§29)
- 中文摘要：10 mohm 1%，位于镜腿后端电池/扬声器/天线区，当前为 Fit / 首版贴装；按当前 schematic 进入 EVT 首版装配。
- 原始 source-of-truth 说明：Right branch shunt — BATR_F -> BAT_P; I_CELL_R for current-share monitoring.
- Schematic nets：A->BATR_F, B->BAT_P

### RS1 / C044-RBAT - 10 mohm 1% 1W

- 板卡/状态：左镜腿 AON/Power Board / Fit / 首版贴装 / P0
- Package field：AI_Glasses_V2:R_1206_shunt
- 关闭门禁：I_BAT_TOTAL; the one production-kept sense path
- 中文摘要：10 mohm 1% 1W，位于左镜腿 AON/Power Board，当前为 Fit / 首版贴装；按当前 schematic 进入 EVT 首版装配。
- 原始 source-of-truth 说明：Pack total shunt — BAT_P -> nPM1300 VBAT. Whole-device current (charge + discharge).
- Schematic nets：A->BAT_P, B->NPM_VBAT

### R21 / C032-BYP - 0R (pack-PCM baseline)

- 板卡/状态：左镜腿 AON/Power Board / Fit / 首版贴装 / P0
- Package field：AI_Glasses_V2:R_0805
- 关闭门禁：Populate 0R OR discrete protection, never both (§17)
- 中文摘要：0R (pack-PCM baseline)，位于左镜腿 AON/Power Board，当前为 Fit / 首版贴装；按当前 schematic 进入 EVT 首版装配。
- 原始 source-of-truth 说明：Cell-negative bypass — ties CELL_NEG to pack GND when the supplier 1S2P pack already integrates its PCM. DNP this and populate U23+Q1 only if doing board-level protection.
- Schematic nets：A->CELL_NEG, B->GND

### U23 / C032 - BQ2970

- 板卡/状态：左镜腿 AON/Power Board / DNP / 只留焊盘不贴 / P0
- Package field：Package_TO_SOT_SMD:SOT-23-5
- 关闭门禁：Keep ONE protection scheme; confirm suffix OVP/UVP/OCP vs nPM1300/boost UVLO (§17)
- 中文摘要：BQ2970，位于左镜腿 AON/Power Board，当前为 DNP / 只留焊盘不贴；第一版不贴装或只作为预留。
- 原始 source-of-truth 说明：1S protection IC (fallback) — OV/UV/OC/short via two low-side back-to-back NMOS. DNP if the supplier pack integrates protection (avoid double-protection conflict, §17).
- 原始 note：Wired per TI BQ2970 typical app (pack 03_Battery TI datasheet): VDD via Rvdd from BAT_P with 0.1uF to VSS(=CELL_NEG); V- via Rvm to pack GND; DO/CO drive Q1.
- Schematic nets：VDD->PROT_VDD, VSS->CELL_NEG, V-->PROT_VM, DO->PROT_DO, CO->PROT_CO

### Q1 / C032-Q - Dual N-MOSFET (b2b)

- 板卡/状态：左镜腿 AON/Power Board / DNP / 只留焊盘不贴 / P0
- Package field：AI_Glasses_V2:VERIFY_DFN_2FET
- 关闭门禁：Vds/RDSon/Vgs/peak per BQ2970 app (§17)
- 中文摘要：Dual N-MOSFET (b2b)，位于左镜腿 AON/Power Board，当前为 DNP / 只留焊盘不贴；第一版不贴装或只作为预留。
- 原始 source-of-truth 说明：Back-to-back protection NMOS — discharge + charge FETs between CELL_NEG and pack GND; gates driven by BQ2970 DO/CO. DNP with U23.
- Schematic nets：D_CELL->CELL_NEG, G_DIS->PROT_DO, D_PACK->GND, G_CHG->PROT_CO

### R22 / C032-Rv - 330R

- 板卡/状态：左镜腿 AON/Power Board / DNP / 只留焊盘不贴 / P0
- Package field：AI_Glasses_V2:R_0402
- 关闭门禁：Per BQ2970 app
- 中文摘要：330R，位于左镜腿 AON/Power Board，当前为 DNP / 只留焊盘不贴；第一版不贴装或只作为预留。
- 原始 source-of-truth 说明：BQ2970 VDD series R — from BAT_P (DNP with protection).
- Schematic nets：A->BAT_P, B->PROT_VDD

### C2 / C032-Cv - 0.1uF

- 板卡/状态：左镜腿 AON/Power Board / DNP / 只留焊盘不贴 / P0
- Package field：AI_Glasses_V2:C_0402
- 关闭门禁：Per BQ2970 app
- 中文摘要：0.1uF，位于左镜腿 AON/Power Board，当前为 DNP / 只留焊盘不贴；第一版不贴装或只作为预留。
- 原始 source-of-truth 说明：BQ2970 VDD-VSS decoupling (DNP with protection).
- Schematic nets：A->PROT_VDD, B->CELL_NEG

### R23 / C032-Rm - 2k

- 板卡/状态：左镜腿 AON/Power Board / DNP / 只留焊盘不贴 / P0
- Package field：AI_Glasses_V2:R_0402
- 关闭门禁：Per BQ2970 app (V- sense)
- 中文摘要：2k，位于左镜腿 AON/Power Board，当前为 DNP / 只留焊盘不贴；第一版不贴装或只作为预留。
- 原始 source-of-truth 说明：BQ2970 V- sense R — to pack GND (DNP with protection).
- Schematic nets：A->GND, B->PROT_VM

### RT1 / C033a - 10k NTC B=3435 1% (R cell)

- 板卡/状态：镜腿后端电池/扬声器/天线区 / Fit / 首版贴装 / P0
- Package field：AI_Glasses_V2:R_0402
- 关闭门禁：NTC curve/package/placement matched to pack supplier + BQ25895/nPM1300 config
- 中文摘要：10k NTC B=3435 1% (R cell)，位于镜腿后端电池/扬声器/天线区，当前为 Fit / 首版贴装；按当前 schematic 进入 EVT 首版装配。
- 原始 source-of-truth 说明：Right cell temperature — 10k NTC at 25C, B=3435K, 1% or better, bonded to the cell large face near center, not to the PCM. Route with ESD/filtering and battery-sense ground.
- Schematic nets：A->NTC_R, B->GND

### RT2 / C033b - 10k NTC B=3435 1% (L cell)

- 板卡/状态：镜腿后端电池/扬声器/天线区 / Fit / 首版贴装 / P0
- Package field：AI_Glasses_V2:R_0402
- 关闭门禁：NTC curve/package/placement matched to pack supplier + ADC/config
- 中文摘要：10k NTC B=3435 1% (L cell)，位于镜腿后端电池/扬声器/天线区，当前为 Fit / 首版贴装；按当前 schematic 进入 EVT 首版装配。
- 原始 source-of-truth 说明：Left cell temperature — second per-cell NTC for software/safety monitoring; firmware must stop charging if either cell is out of the supplier temperature window.
- Schematic nets：A->NTC_L, B->GND

### TP2 / C033-TP - Battery test points

- 板卡/状态：镜腿后端电池/扬声器/天线区 / Fit / 首版贴装 / P0
- Package field：AI_Glasses_V2:TestPad_Set
- 关闭门禁：Cell/pack voltage + NTC probe access (§21)
- 中文摘要：Battery test points，位于镜腿后端电池/扬声器/天线区，当前为 Fit / 首版贴装；按当前 schematic 进入 EVT 首版装配。
- 原始 source-of-truth 说明：Battery Kelvin test points — Cell-L+, Cell-R+, Pack+, Cell-neg, both NTCs for pairing / current-share / temperature verification.
- Schematic nets：CELL_L->BATL_P, CELL_R->BATR_P, PACK_P->BAT_P, CELL_NEG->CELL_NEG, NTC_L->NTC_L, NTC_R->NTC_R

### J1 / C034 - CCP P2578MP01-06C180HT

- 板卡/状态：镜腿后端电池/扬声器/天线区 / HOLD / 候选件但门禁未关闭 / P0
- Package field：AI_Glasses_V2:VERIFY_POGO_6P_1.8MM
- 关闭门禁：USB2 eye/contact validation, current/fault/ESD, mating STEP, corrosion/cycle life
- 中文摘要：CCP P2578MP01-06C180HT，位于镜腿后端电池/扬声器/天线区，当前为 HOLD / 候选件但门禁未关闭；必须完成对应 gate 后才能作为 layout/fab 冻结依据。
- 原始 source-of-truth 说明：6-pin magnetic pogo EVT candidate — 1.8mm pitch, working height about 1.0mm, target outline about 10x3mm. Pins carry 5V charge input, USB2 D+/D-, and dual GND/VBUS contacts for lower resistance. Add VBUS TVS/eFuse/OVP, D+/D- low-cap ESD, USB CMC DNP, VBUS insert detect and MaskROM/UART fallback pads.
- Schematic nets：GND1->GND, USB_DN->USB2_DM, USB_DP->USB2_DP, GND2->GND, VBUS1->VBUS_RAW, VBUS2->VBUS_RAW

### J2 / C035 - USB-C 16p USB2-only

- 板卡/状态：EVT 调试尾板 / Fit / 首版贴装 / P0
- Package field：AI_Glasses_V2:USB_C_16P_MidMount
- 关闭门禁：Connector height + shell opening co-freeze
- 中文摘要：USB-C 16p USB2-only，位于EVT 调试尾板，当前为 Fit / 首版贴装；按当前 schematic 进入 EVT 首版装配。
- 原始 source-of-truth 说明：EVT USB-C — 5 V sink + USB2 OTG (no USB3/DP). For MaskROM/ADB/firmware/lab supply.
- Schematic nets：VBUS->VBUS_RAW, GND->GND, DP->USB2_DP, DM->USB2_DM, CC1->USB_CC1, CC2->USB_CC2

### U24 / C036 - TPD2E001

- 板卡/状态：EVT 调试尾板 / Fit / 首版贴装 / P0
- Package field：Package_TO_SOT_SMD:SOT-23-3
- 关闭门禁：Keep ~90 ohm diff + continuous ref gnd
- 中文摘要：TPD2E001，位于EVT 调试尾板，当前为 Fit / 首版贴装；按当前 schematic 进入 EVT 首版装配。
- 原始 source-of-truth 说明：USB2 ESD — low-cap ESD on D+/D- near the connector.
- Schematic nets：DP->USB2_DP, DM->USB2_DM, GND->GND

### R1 / C037a - 5.1k 1%

- 板卡/状态：EVT 调试尾板 / Fit / 首版贴装 / P0
- Package field：AI_Glasses_V2:R_0402
- 关闭门禁：USB-C spec
- 中文摘要：5.1k 1%，位于EVT 调试尾板，当前为 Fit / 首版贴装；按当前 schematic 进入 EVT 首版装配。
- 原始 source-of-truth 说明：USB-C CC1 Rd — 5.1k 1% sink pulldown. LOCK value + 1% (V1 audit rule).
- Schematic nets：A->USB_CC1, B->GND

### R2 / C037b - 5.1k 1%

- 板卡/状态：EVT 调试尾板 / Fit / 首版贴装 / P0
- Package field：AI_Glasses_V2:R_0402
- 关闭门禁：USB-C spec
- 中文摘要：5.1k 1%，位于EVT 调试尾板，当前为 Fit / 首版贴装；按当前 schematic 进入 EVT 首版装配。
- 原始 source-of-truth 说明：USB-C CC2 Rd — 5.1k 1% sink pulldown.
- Schematic nets：A->USB_CC2, B->GND

### J3 / C038 - Hirose FH26W-33S-0.3SHW(97)

- 板卡/状态：前框 Sensor Board / HOLD / 候选件但门禁未关闭 / P0
- Package field：AI_Glasses_V2:VERIFY_FH26W_33S_0.3SHW
- 关闭门禁：G10/G12 (camera module vendor signs 33-pin pinout, contact orientation, impedance)
- 中文摘要：Hirose FH26W-33S-0.3SHW(97)，位于前框 Sensor Board，当前为 HOLD / 候选件但门禁未关闭；必须完成对应 gate 后才能作为 layout/fab 冻结依据。
- 原始 source-of-truth 说明：33-pin camera FPC connector — Hirose FH26W-33S-0.3SHW(97), 0.3mm pitch, bottom contact, horizontal, about 1.0mm height, for 0.2mm FPC. Carries IMX415 4-lane CSI, rails, I2C, reset/powerdown and module ID. Assembly/service connector only, not a user-cycle connector.
- 原始 note：Pinout below follows the current project proposal and must be signed by the camera module vendor. Hinge electrical interconnect is out of scope for Chip-down EVT V2.0.
- Schematic nets：1_GND->GND, 2_DVDD->CAM_1V1_S, 3_GND->GND, 4_AVDD->CAM_2V9_S, 5_GND->GND, 6_IOVDD->CAM_1V8_S, 7_GND->GND, 8_MCLK->CAM_MCLK, 9_GND->GND, 10_I2C_SCL->CAM_I2C_SCL, 11_I2C_SDA->CAM_I2C_SDA, 12_RESET_N->CAM_RST_L, 13_PWDN->CAM_PWDN_L, 14_FSYNC_NC->NC, 15_GND->GND, 16_MIPI_CLK_N->CSI_CLK_N, 17_MIPI_CLK_P->CSI_CLK_P, 18_GND->GND, 19_MIPI_D0_N->CSI_D0_N, 20_MIPI_D0_P->CSI_D0_P, 21_GND->GND, 22_MIPI_D1_N->CSI_D1_N, 23_MIPI_D1_P->CSI_D1_P, 24_GND->GND, 25_MIPI_D2_N->CSI_D2_N, 26_MIPI_D2_P->CSI_D2_P, 27_GND->GND, 28_MIPI_D3_N->CSI_D3_N, 29_MIPI_D3_P->CSI_D3_P, 30_GND->GND, 31_MODULE_ID->CAM_MODULE_ID, 32_NC->NC, 33_GND->GND

### J5 / C040 - U.FL / I-PEX MHF RF test connector

- 板卡/状态：镜腿后端电池/扬声器/天线区 / DNP / 只留焊盘不贴 / P0
- Package field：Connector_Coaxial:U.FL_Hirose_U.FL-R-SMT-1_Vertical
- 关闭门禁：EVT RF debug only; production prefers direct coax or soldered antenna pigtail
- 中文摘要：U.FL / I-PEX MHF RF test connector，位于镜腿后端电池/扬声器/天线区，当前为 DNP / 只留焊盘不贴；第一版不贴装或只作为预留。
- 原始 source-of-truth 说明：Micro RF connector — DNP RF debug/attach option on the shared Wi-Fi/BLE antenna feed. Do not consume production Z-height unless RF bring-up requires it.
- Schematic nets：SIG->WIFI_ANT, GND->GND

### TP1 / C041 - UART/SWD pogo pads

- 板卡/状态：EVT 调试尾板 / Fit / 首版贴装 / P0
- Package field：AI_Glasses_V2:TestPad_Set
- 关闭门禁：Voltage domain clearly labelled (no 3.3V into 1.8V IO)
- 中文摘要：UART/SWD pogo pads，位于EVT 调试尾板，当前为 Fit / 首版贴装；按当前 schematic 进入 EVT 首版装配。
- 原始 source-of-truth 说明：UART/SWD test pads — RK3576 UART0 + nRF SWD + GND/VREF for bring-up (no connector height).
- Schematic nets：SOC_TX->SOC_DBG_TX, SOC_RX->SOC_DBG_RX, SWDIO->NRF_SWDIO, SWDCLK->NRF_SWDCLK, GND->GND

### SW1 / C042a - Power/PWRKEY

- 板卡/状态：EVT 调试尾板 / Fit / 首版贴装 / P0
- Package field：Button_Switch_SMD:SW_Push_1P1T_NO_CK_KMR2
- 关闭门禁：First chip-down must recover from boot failure
- 中文摘要：Power/PWRKEY，位于EVT 调试尾板，当前为 Fit / 首版贴装；按当前 schematic 进入 EVT 首版装配。
- 原始 source-of-truth 说明：Power key — RK3576 PWRON via AON/PMIC.
- Schematic nets：A->SOC_PWRKEY, B->GND

### SW2 / C042b - Reset

- 板卡/状态：EVT 调试尾板 / Fit / 首版贴装 / P0
- Package field：Button_Switch_SMD:SW_Push_1P1T_NO_CK_KMR2
- 关闭门禁：Bring-up
- 中文摘要：Reset，位于EVT 调试尾板，当前为 Fit / 首版贴装；按当前 schematic 进入 EVT 首版装配。
- 原始 source-of-truth 说明：Reset key — RK3576 RESET_n.
- Schematic nets：A->SOC_RESET_L, B->GND

### SW3 / C042c - MaskROM/Recovery

- 板卡/状态：EVT 调试尾板 / Fit / 首版贴装 / P0
- Package field：Button_Switch_SMD:SW_Push_1P1T_NO_CK_KMR2
- 关闭门禁：Bring-up (recover from bad boot)
- 中文摘要：MaskROM/Recovery，位于EVT 调试尾板，当前为 Fit / 首版贴装；按当前 schematic 进入 EVT 首版装配。
- 原始 source-of-truth 说明：MaskROM/recovery key — force USB recovery boot.
- Schematic nets：A->SOC_MASKROM_L, B->GND

### RS4 / C044-RSOC - 10 mohm 1%

- 板卡/状态：右镜腿 Compute Board / Fit / 首版贴装 / P0
- Package field：AI_Glasses_V2:R_0805_shunt
- 关闭门禁：5-20 mohm (2A x 10m=20mV; avoid boost UVLO)
- 中文摘要：10 mohm 1%，位于右镜腿 Compute Board，当前为 Fit / 首版贴装；按当前 schematic 进入 EVT 首版装配。
- 原始 source-of-truth 说明：RK3576 island shunt — VSYS -> SOC_IN (I_SOC_5V).
- Schematic nets：A->VSYS, B->SOC_IN

### RS5 / C044-RWIFI - 50 mohm 1%

- 板卡/状态：右镜腿 Compute Board / Fit / 首版贴装 / P0
- Package field：AI_Glasses_V2:R_0603_shunt
- 关闭门禁：20-100 mohm
- 中文摘要：50 mohm 1%，位于右镜腿 Compute Board，当前为 Fit / 首版贴装；按当前 schematic 进入 EVT 首版装配。
- 原始 source-of-truth 说明：Wi-Fi island shunt — VSYS -> WIFI_IN (I_WIFI).
- Schematic nets：A->VSYS, B->WIFI_IN

### RS6 / C044-RAUD - 50 mohm 1%

- 板卡/状态：右镜腿 Compute Board / Fit / 首版贴装 / P0
- Package field：AI_Glasses_V2:R_0603_shunt
- 关闭门禁：20-100 mohm
- 中文摘要：50 mohm 1%，位于右镜腿 Compute Board，当前为 Fit / 首版贴装；按当前 schematic 进入 EVT 首版装配。
- 原始 source-of-truth 说明：Audio island shunt — VSYS -> AUDIO_IN (I_AUDIO).
- Schematic nets：A->VSYS, B->AUDIO_IN

### RS7 / C044-RC1 - 100 mohm 1%

- 板卡/状态：前框 Sensor Board / Fit / 首版贴装 / P0
- Package field：AI_Glasses_V2:R_0603_shunt
- 关闭门禁：Per-rail Kelvin (§23/§29); DVDD ~250mA
- 中文摘要：100 mohm 1%，位于前框 Sensor Board，当前为 Fit / 首版贴装；按当前 schematic 进入 EVT 首版装配。
- 原始 source-of-truth 说明：Camera DVDD shunt — CAM_1V1 -> CAM_1V1_S (I_CAM_1V1).
- Schematic nets：A->CAM_1V1, B->CAM_1V1_S

### RS8 / C044-RC8 - 100 mohm 1%

- 板卡/状态：前框 Sensor Board / Fit / 首版贴装 / P0
- Package field：AI_Glasses_V2:R_0402_shunt
- 关闭门禁：Per-rail Kelvin (§23/§29); IOVDD ~3mA
- 中文摘要：100 mohm 1%，位于前框 Sensor Board，当前为 Fit / 首版贴装；按当前 schematic 进入 EVT 首版装配。
- 原始 source-of-truth 说明：Camera IOVDD shunt — CAM_1V8_SW -> CAM_1V8_S (I_CAM_1V8).
- Schematic nets：A->CAM_1V8_SW, B->CAM_1V8_S

### RS9 / C044-RC29 - 100 mohm 1%

- 板卡/状态：前框 Sensor Board / Fit / 首版贴装 / P0
- Package field：AI_Glasses_V2:R_0603_shunt
- 关闭门禁：Per-rail Kelvin (§23/§29); AVDD ~156mA
- 中文摘要：100 mohm 1%，位于前框 Sensor Board，当前为 Fit / 首版贴装；按当前 schematic 进入 EVT 首版装配。
- 原始 source-of-truth 说明：Camera AVDD shunt — CAM_2V9 -> CAM_2V9_S (I_CAM_2V9).
- Schematic nets：A->CAM_2V9, B->CAM_2V9_S

### U25 / C044a - INA238 (I_BAT_TOTAL)

- 板卡/状态：左镜腿 AON/Power Board / DNP / 只留焊盘不贴 / P1
- Package field：AI_Glasses_V2:VSSOP-10
- 关闭门禁：Power Gate — EVT-A; production may keep this one
- 中文摘要：INA238 (I_BAT_TOTAL)，位于左镜腿 AON/Power Board，当前为 DNP / 只留焊盘不贴；第一版不贴装或只作为预留。
- 原始 source-of-truth 说明：Whole-device current across RS1 (BAT_P->VBAT). Deep Off total = AON only, so it also backs the AON 20-50 mW check; nPM1300 fuel gauge cross-checks.
- Schematic nets：IN_P->BAT_P, IN_N->NPM_VBAT, SCL->I2C_AON_SCL, SDA->I2C_AON_SDA, GND->GND

### U26 / C044-ICL - INA238 (I_CELL_L)

- 板卡/状态：镜腿后端电池/扬声器/天线区 / DNP / 只留焊盘不贴 / P1
- Package field：AI_Glasses_V2:VSSOP-10
- 关闭门禁：Power Gate — EVT-A only (current-share)
- 中文摘要：INA238 (I_CELL_L)，位于镜腿后端电池/扬声器/天线区，当前为 DNP / 只留焊盘不贴；第一版不贴装或只作为预留。
- 原始 source-of-truth 说明：Left branch current across RS2 — cell current-share vs SOC/temp.
- Schematic nets：IN_P->BATL_F, IN_N->BAT_P, SCL->I2C_AON_SCL, SDA->I2C_AON_SDA, GND->GND

### U27 / C044-ICR - INA238 (I_CELL_R)

- 板卡/状态：镜腿后端电池/扬声器/天线区 / DNP / 只留焊盘不贴 / P1
- Package field：AI_Glasses_V2:VSSOP-10
- 关闭门禁：Power Gate — EVT-A only (current-share)
- 中文摘要：INA238 (I_CELL_R)，位于镜腿后端电池/扬声器/天线区，当前为 DNP / 只留焊盘不贴；第一版不贴装或只作为预留。
- 原始 source-of-truth 说明：Right branch current across RS3 — cell current-share vs SOC/temp.
- Schematic nets：IN_P->BATR_F, IN_N->BAT_P, SCL->I2C_AON_SCL, SDA->I2C_AON_SDA, GND->GND

### U28 / C044c - INA238 (I_SOC_5V)

- 板卡/状态：右镜腿 Compute Board / DNP / 只留焊盘不贴 / P1
- Package field：AI_Glasses_V2:VSSOP-10
- 关闭门禁：Power Gate — EVT-A only
- 中文摘要：INA238 (I_SOC_5V)，位于右镜腿 Compute Board，当前为 DNP / 只留焊盘不贴；第一版不贴装或只作为预留。
- 原始 source-of-truth 说明：RK3576 island monitor across RS4 — record/AI curves + wake energy.
- Schematic nets：IN_P->VSYS, IN_N->SOC_IN, SCL->I2C_AON_SCL, SDA->I2C_AON_SDA, GND->GND

### U29 / C044e - INA238 (I_WIFI)

- 板卡/状态：右镜腿 Compute Board / DNP / 只留焊盘不贴 / P1
- Package field：AI_Glasses_V2:VSSOP-10
- 关闭门禁：Power Gate — EVT-A only
- 中文摘要：INA238 (I_WIFI)，位于右镜腿 Compute Board，当前为 DNP / 只留焊盘不贴；第一版不贴装或只作为预留。
- 原始 source-of-truth 说明：Wi-Fi island monitor across RS5 — FCU760K TX avg vs 353mA peak.
- Schematic nets：IN_P->VSYS, IN_N->WIFI_IN, SCL->I2C_AON_SCL, SDA->I2C_AON_SDA, GND->GND

### U30 / C044f - INA238 (I_AUDIO)

- 板卡/状态：右镜腿 Compute Board / DNP / 只留焊盘不贴 / P1
- Package field：AI_Glasses_V2:VSSOP-10
- 关闭门禁：Power Gate — EVT-A only
- 中文摘要：INA238 (I_AUDIO)，位于右镜腿 Compute Board，当前为 DNP / 只留焊盘不贴；第一版不贴装或只作为预留。
- 原始 source-of-truth 说明：Audio island monitor across RS6 — speech avg vs music peak.
- Schematic nets：IN_P->VSYS, IN_N->AUDIO_IN, SCL->I2C_AON_SCL, SDA->I2C_AON_SDA, GND->GND

### U31 / C044-IC1 - INA238 (I_CAM_1V1)

- 板卡/状态：前框 Sensor Board / DNP / 只留焊盘不贴 / P1
- Package field：AI_Glasses_V2:VSSOP-10
- 关闭门禁：Power Gate — EVT-A only
- 中文摘要：INA238 (I_CAM_1V1)，位于前框 Sensor Board，当前为 DNP / 只留焊盘不贴；第一版不贴装或只作为预留。
- 原始 source-of-truth 说明：Camera DVDD monitor across RS7 — sensor core draw + off-leakage.
- Schematic nets：IN_P->CAM_1V1, IN_N->CAM_1V1_S, SCL->I2C_AON_SCL, SDA->I2C_AON_SDA, GND->GND

### U32 / C044-IC8 - INA238 (I_CAM_1V8)

- 板卡/状态：前框 Sensor Board / DNP / 只留焊盘不贴 / P1
- Package field：AI_Glasses_V2:VSSOP-10
- 关闭门禁：Power Gate — EVT-A only
- 中文摘要：INA238 (I_CAM_1V8)，位于前框 Sensor Board，当前为 DNP / 只留焊盘不贴；第一版不贴装或只作为预留。
- 原始 source-of-truth 说明：Camera IOVDD monitor across RS8 — I/O draw + off-leakage.
- Schematic nets：IN_P->CAM_1V8_SW, IN_N->CAM_1V8_S, SCL->I2C_AON_SCL, SDA->I2C_AON_SDA, GND->GND

### U33 / C044-IC29 - INA238 (I_CAM_2V9)

- 板卡/状态：前框 Sensor Board / DNP / 只留焊盘不贴 / P1
- Package field：AI_Glasses_V2:VSSOP-10
- 关闭门禁：Power Gate — EVT-A only
- 中文摘要：INA238 (I_CAM_2V9)，位于前框 Sensor Board，当前为 DNP / 只留焊盘不贴；第一版不贴装或只作为预留。
- 原始 source-of-truth 说明：Camera AVDD monitor across RS9 — analog draw + off-leakage.
- Schematic nets：IN_P->CAM_2V9, IN_N->CAM_2V9_S, SCL->I2C_AON_SCL, SDA->I2C_AON_SDA, GND->GND

### R11 / C046a - 100k

- 板卡/状态：右镜腿 Compute Board / Fit / 首版贴装 / P0
- Package field：AI_Glasses_V2:R_0402
- 关闭门禁：Default OFF (§4)
- 中文摘要：100k，位于右镜腿 Compute Board，当前为 Fit / 首版贴装；按当前 schematic 进入 EVT 首版装配。
- 原始 source-of-truth 说明：SOC_PWR_EN pull-down — RK3576 boost default OFF (main SoC off at boot).
- Schematic nets：A->SOC_PWR_EN, B->GND

### R12 / C046b - 100k

- 板卡/状态：右镜腿 Compute Board / Fit / 首版贴装 / P0
- Package field：AI_Glasses_V2:R_0402
- 关闭门禁：Default OFF (§4)
- 中文摘要：100k，位于右镜腿 Compute Board，当前为 Fit / 首版贴装；按当前 schematic 进入 EVT 首版装配。
- 原始 source-of-truth 说明：PMIC_PWRON pull-down — RK806 stays off until AON MCU sequences it.
- Schematic nets：A->PMIC_PWRON, B->GND

### R13 / C046c - 100k

- 板卡/状态：前框 Sensor Board / Fit / 首版贴装 / P0
- Package field：AI_Glasses_V2:R_0402
- 关闭门禁：Default OFF (§4)
- 中文摘要：100k，位于前框 Sensor Board，当前为 Fit / 首版贴装；按当前 schematic 进入 EVT 首版装配。
- 原始 source-of-truth 说明：CAM_1V1_EN pull-down — camera core buck default OFF.
- Schematic nets：A->CAM_1V1_EN, B->GND

### R14 / C046d - 100k

- 板卡/状态：前框 Sensor Board / Fit / 首版贴装 / P0
- Package field：AI_Glasses_V2:R_0402
- 关闭门禁：Default OFF (§4)
- 中文摘要：100k，位于前框 Sensor Board，当前为 Fit / 首版贴装；按当前 schematic 进入 EVT 首版装配。
- 原始 source-of-truth 说明：CAM_1V8_EN pull-down — camera I/O load switch default OFF.
- Schematic nets：A->CAM_1V8_EN, B->GND

### R15 / C046e - 100k

- 板卡/状态：前框 Sensor Board / Fit / 首版贴装 / P0
- Package field：AI_Glasses_V2:R_0402
- 关闭门禁：Default OFF (§4)
- 中文摘要：100k，位于前框 Sensor Board，当前为 Fit / 首版贴装；按当前 schematic 进入 EVT 首版装配。
- 原始 source-of-truth 说明：CAM_2V9_EN pull-down — camera analog LDO default OFF.
- Schematic nets：A->CAM_2V9_EN, B->GND

### R16 / C046f - 100k

- 板卡/状态：右镜腿 Compute Board / Fit / 首版贴装 / P0
- Package field：AI_Glasses_V2:R_0402
- 关闭门禁：Default OFF (§4)
- 中文摘要：100k，位于右镜腿 Compute Board，当前为 Fit / 首版贴装；按当前 schematic 进入 EVT 首版装配。
- 原始 source-of-truth 说明：WIFI_BUCK_EN pull-down — Wi-Fi buck default OFF.
- Schematic nets：A->WIFI_BUCK_EN, B->GND

### R17 / C046g - 100k

- 板卡/状态：右镜腿 Compute Board / Fit / 首版贴装 / P0
- Package field：AI_Glasses_V2:R_0402
- 关闭门禁：Default OFF (§4)
- 中文摘要：100k，位于右镜腿 Compute Board，当前为 Fit / 首版贴装；按当前 schematic 进入 EVT 首版装配。
- 原始 source-of-truth 说明：WIFI_LS_EN pull-down — Wi-Fi load switch default OFF.
- Schematic nets：A->WIFI_LS_EN, B->GND

### R18 / C046h - 100k

- 板卡/状态：右镜腿 Compute Board / Fit / 首版贴装 / P0
- Package field：AI_Glasses_V2:R_0402
- 关闭门禁：Default OFF (§4/§9: FCU760K CHIP_EN default low)
- 中文摘要：100k，位于右镜腿 Compute Board，当前为 Fit / 首版贴装；按当前 schematic 进入 EVT 首版装配。
- 原始 source-of-truth 说明：WIFI_CHIP_EN pull-down — FCU760K held off until AON MCU enables it (pack §9).
- Schematic nets：A->WIFI_CHIP_EN, B->GND

### R19 / C046i - 100k

- 板卡/状态：右镜腿 Compute Board / Fit / 首版贴装 / P0
- Package field：AI_Glasses_V2:R_0402
- 关闭门禁：Default OFF (§4)
- 中文摘要：100k，位于右镜腿 Compute Board，当前为 Fit / 首版贴装；按当前 schematic 进入 EVT 首版装配。
- 原始 source-of-truth 说明：AUDIO_LS_EN pull-down — audio amp load switch default OFF.
- Schematic nets：A->AUDIO_LS_EN, B->GND

### R20 / C046j - 100k

- 板卡/状态：右镜腿 Compute Board / Fit / 首版贴装 / P0
- Package field：AI_Glasses_V2:R_0402
- 关闭门禁：Default OFF (§4)
- 中文摘要：100k，位于右镜腿 Compute Board，当前为 Fit / 首版贴装；按当前 schematic 进入 EVT 首版装配。
- 原始 source-of-truth 说明：AUDIO_AMP_SD pull-down — MAX98360A shutdown default (amp muted at boot).
- Schematic nets：A->AUDIO_AMP_SD, B->GND

### R3 / C045a - 2.2k 1%

- 板卡/状态：左镜腿 AON/Power Board / Fit / 首版贴装 / P0
- Package field：AI_Glasses_V2:R_0402
- 关闭门禁：Confirm vs total AON bus capacitance
- 中文摘要：2.2k 1%，位于左镜腿 AON/Power Board，当前为 Fit / 首版贴装；按当前 schematic 进入 EVT 首版装配。
- 原始 source-of-truth 说明：AON I2C SCL pull-up to AON_1V8 (nPM1300/BMI270/INA238 bus).
- Schematic nets：A->AON_1V8, B->I2C_AON_SCL

### R4 / C045b - 2.2k 1%

- 板卡/状态：左镜腿 AON/Power Board / Fit / 首版贴装 / P0
- Package field：AI_Glasses_V2:R_0402
- 关闭门禁：Confirm vs total AON bus capacitance
- 中文摘要：2.2k 1%，位于左镜腿 AON/Power Board，当前为 Fit / 首版贴装；按当前 schematic 进入 EVT 首版装配。
- 原始 source-of-truth 说明：AON I2C SDA pull-up to AON_1V8.
- Schematic nets：A->AON_1V8, B->I2C_AON_SDA

### R5 / C045c - 2.2k 1%

- 板卡/状态：前框 Sensor Board / Fit / 首版贴装 / P0
- Package field：AI_Glasses_V2:R_0402
- 关闭门禁：Confirm vs camera bus capacitance
- 中文摘要：2.2k 1%，位于前框 Sensor Board，当前为 Fit / 首版贴装；按当前 schematic 进入 EVT 首版装配。
- 原始 source-of-truth 说明：Camera I2C SCL pull-up to CAM_1V8_SW.
- Schematic nets：A->CAM_1V8_SW, B->CAM_I2C_SCL

### R6 / C045d - 2.2k 1%

- 板卡/状态：前框 Sensor Board / Fit / 首版贴装 / P0
- Package field：AI_Glasses_V2:R_0402
- 关闭门禁：Confirm vs camera bus capacitance
- 中文摘要：2.2k 1%，位于前框 Sensor Board，当前为 Fit / 首版贴装；按当前 schematic 进入 EVT 首版装配。
- 原始 source-of-truth 说明：Camera I2C SDA pull-up to CAM_1V8_SW.
- Schematic nets：A->CAM_1V8_SW, B->CAM_I2C_SDA

### R9 / C045e - 2.2k 1%

- 板卡/状态：右镜腿 Compute Board / Fit / 首版贴装 / P0
- Package field：AI_Glasses_V2:R_0402
- 关闭门禁：Confirm vs SoC PMIC bus
- 中文摘要：2.2k 1%，位于右镜腿 Compute Board，当前为 Fit / 首版贴装；按当前 schematic 进入 EVT 首版装配。
- 原始 source-of-truth 说明：SoC-PMIC I2C SCL pull-up to VCCIO_1V8 (RK3576<->RK806).
- Schematic nets：A->VCCIO_1V8, B->SOC_PMIC_SCL

### R10 / C045f - 2.2k 1%

- 板卡/状态：右镜腿 Compute Board / Fit / 首版贴装 / P0
- Package field：AI_Glasses_V2:R_0402
- 关闭门禁：Confirm vs SoC PMIC bus
- 中文摘要：2.2k 1%，位于右镜腿 Compute Board，当前为 Fit / 首版贴装；按当前 schematic 进入 EVT 首版装配。
- 原始 source-of-truth 说明：SoC-PMIC I2C SDA pull-up to VCCIO_1V8.
- Schematic nets：A->VCCIO_1V8, B->SOC_PMIC_SDA

---
再生成命令：
`reports/.venv/bin/python v2_chipdown/scripts/generate_current_schematic_report_zh.py`
不要手工改 PDF；请修改 schematic master 或 YAML 后重新生成。
