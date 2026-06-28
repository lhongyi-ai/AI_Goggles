# AI 运动眼镜载板 V1 — 设计报告（中文版）

- **项目**：ai_glasses_carrier_v1
- **版本**：v1.0-draft
- **核心模组**：Radxa CM4（RK3576）
- **板卡尺寸**：70.0 × 55.0 mm，6 层
- **生成日期**：2026-06-28
- **元件总数**：102（P0 必需 81 项，P1 建议 21 项）

> ⚠️ **重要声明**：本报告由脚本依据 `scripts/carrier_bom.py` 自动生成。其中的元件型号与数值均为 **EVT 阶段工程候选**，不是冻结 BOM。所有 CM4 引脚号、所有高速/射频/电源/电池相关器件，必须人工对照 **Radxa CM4 Schematic V1.20** 与各芯片 datasheet 核对后才能投板。（需求文档 1.1 节：AI 输出仅作辅助。）

---

## 1. 方案概述

本载板是 AI 运动眼镜的功能验证板（EVT），承载 Radxa CM4（RK3576）模组，通过三个 100-pin 板对板（B2B）连接器与模组对接。功能划分：

- **P0（必需）**：摄像头 MIPI-CSI（Radxa Camera 4K / IMX415 31-pin + CM4 CSI3 4-lane；J2 schematic 电气已锁，实物/FPC 路径项转入 `DEFERRED_TO_PRE_LAYOUT`）、2× PDM 数字麦克风、I2S/SAI Class-D 音频输出、USB-C（仅 USB2 + 5V 取电）、CM4 板载 Wi-Fi6/BT5.4、**GNSS/GPS（UART 外接模块）**、调试/恢复接口。
- **P1（建议）**：1S 锂电 + 充电 + 电量计、6 轴 IMU、振动马达。

> 🔋 **续航目标**：当前 1 小时仅为验证级；最终版本目标 **>3–4 小时**。这要求在 Phase 0 完成功率预算（Idle / 摄像头 / 摄像头+AI / +H.265 / +Wi-Fi / 满载），据实测峰值与平均功耗反推电池容量与 boost（TPS61022）选型——本载板已预留 0Ω 分流位（R3）用于电流测量。

## 2. 元件清单（BOM）

被动元件（电阻 / 电容 / 电感）均已给出具体数值；IC / 连接器给出候选型号。

### CM4 模块 / B2B 连接器

| 位号 | 型号 / 数值 | 说明 | 优先级 |
| --- | --- | --- | --- |
| J31 | DF40C-100DS-0.4V(51) | CM4 J3A (low-speed): power, debug/GNSS UART, I2C, control GPIO — KiCad refdes J31 represents Radxa CM4 connector J3A. Carrier-side receptacle; pins verified vs CM4 V1.20. GPIO bank @1.8V (VREF=P78). | P0 |
| J32 | DF40C-100DS-0.4V(51) | CM4 J3B (high-speed): MIPI-CSI3 4-lane camera, USB2-OTG0, PDM1 mics — KiCad refdes J32 represents Radxa CM4 connector J3B. MIPI CSI3 100Ω diff, USB 90Ω diff. Pins verified vs CM4 V1.20. | P0 |
| J1 | DF40C-100DS-0.4V(51) | CM4 J1 (I/O): SAI1 audio, CSI3 camera MCLK, speaker enable — SAI1 audio out + CAM_CLK2_OUT_M0 for Radxa Camera 4K. Pins verified vs CM4 V1.20. Radxa Camera 4K 31-pin FPC has active-low RESET but no PWDN pin. SAI1_MCLK is unused for MAX98357A and marked no-connect at the CM4 B2B. | P0 |

### 摄像头 Camera (P0)

| 位号 | 型号 / 数值 | 说明 | 优先级 |
| --- | --- | --- | --- |
| J2 | FH35C-31S-0.3SHW(50) | Camera FPC — Radxa Camera 4K / Sony IMX415-AAQR-C, 31-pin 0.3mm, 4-lane MIPI — SCHEMATIC_ELECTRICAL_LOCKED for Radxa Camera 4K using Radxa AC006 31P 0.3mm opposite-side FPC. Pad 1 = GND. J2 pins 1-31, CSI3 4-lane, P/N, I2C/MCLK/RESET, voltage domains, power and NC are checked by scripts/audit_csi3_camera.py. DEFERRED_TO_PRE_LAYOUT: AC006 physical validation, FPC contact side, insertion direction, Pin 1 physical check, 1:1 print, coupon test, and FPC bend/enclosure path. Pinout source: CM4_IMX415_design_files/Radxa_Camera_4K_31pin_pinout.csv. | P0 |
| U2 | TPD4E05U06 | MIPI-CSI low-capacitance ESD array for CSI3 clock + data lanes 0/1 (<0.4pF/line) | P0 |
| U16 | TPD4E05U06 | MIPI-CSI low-capacitance ESD array for CSI3 data lanes 2/3 (<0.4pF/line) | P0 |
| U3 | LP5907-3.3 (low-noise LDO) | Camera 3.3V low-noise supply for Radxa Camera 4K, EN-gated | P0 |
| R7 | 2.2k | Camera I2C SCL pull-up to +1V8 (cam OVDD=1.8V confirmed) | P0 |
| R8 | 2.2k | Camera I2C SDA pull-up to +1V8 (cam OVDD=1.8V confirmed) | P0 |
| C8 | 10µF | Camera +3V3 bulk decoupling | P0 |
| C9 | 1µF | Camera +3V3 decoupling | P0 |
| C10 | 100nF | Camera +3V3 HF decoupling | P0 |
| C29 | 10µF | Camera +5V bulk decoupling for Radxa Camera 4K | P0 |
| C30 | 100nF | Camera +5V HF decoupling for Radxa Camera 4K | P0 |

### 音频 Audio (P0)

| 位号 | 型号 / 数值 | 说明 | 优先级 |
| --- | --- | --- | --- |
| MK1 | SPH0641LU4H-1 | PDM MEMS mic (L, SEL=GND) | P0 |
| MK2 | SPH0641LU4H-1 | PDM MEMS mic (R, SEL=VDD) | P0 |
| U4 | MAX98357AETE+T | Class-D I2S/SAI mono amp (TQFN-16, no MCLK) — GAIN=GND → low gain (3-6dB) for 8Ω/1W spkr; SW volume-limit at bring-up. | P0 |
| FB1 | Ferrite 600Ω@100MHz | Class-D speaker EMI bead (OUT+) | P0 |
| FB2 | Ferrite 600Ω@100MHz | Class-D speaker EMI bead (OUT-) | P0 |
| C23 | 1nF | Class-D EMI cap (OUT+ to GND) | P0 |
| C24 | 1nF | Class-D EMI cap (OUT- to GND) | P0 |
| J3 | JST-SH 2p (spkr) | Speaker connector (post-EMI); 2 wire-leads — Speaker = Ole Wolff OWS-091630W50A-8 (8Ω 1W, 16×9×3mm, LCSC C5840086), wire-leads. | P0 |
| C13 | 100nF | Amp VDD decoupling | P0 |

### USB-C (P0)

| 位号 | 型号 / 数值 | 说明 | 优先级 |
| --- | --- | --- | --- |
| J4 | GCT USB4085 (USB2) | USB-C receptacle (USB2 + 5V sink) | P0 |
| U5 | TPD2E009 | USB2 D+/D- ESD clamp | P0 |
| R1 | 5.1k | USB-C CC1 pull-down (Sink role) | P0 |
| R2 | 5.1k | USB-C CC2 pull-down (Sink role) | P0 |
| D3 | SMAJ5.0A (TVS) | USB VBUS ESD/TVS clamp (5V standoff) | P0 |
| U15 | TPS25940 (e-fuse, opt) | VBUS e-fuse: OVP/OCP/reverse-block (DNP-able; bypass via R3 if unused) | P0 |
| R3 | 0R / shunt | VBUS_PROT→5V series 0R/shunt (current log) | P0 |
| C11 | 1µF | VBUS input cap | P0 |

### 电源 Power (P0)

| 位号 | 型号 / 数值 | 说明 | 优先级 |
| --- | --- | --- | --- |
| U12 | TLV75733 (LDO) | 3.3V rail regulator | P0 |
| U13 | TLV75718 (LDO) | 1.8V VCCIO rail regulator | P0 |
| C1 | 10µF | +5V bulk decoupling | P0 |
| C2 | 100nF | +5V HF decoupling | P0 |
| C3 | 10µF | +3V3 bulk decoupling | P0 |
| C4 | 100nF | +3V3 HF decoupling | P0 |
| C5 | 10µF | +1V8 bulk decoupling | P0 |
| C6 | 100nF | +1V8 HF decoupling | P0 |
| C21 | 100nF | LDO U12 +3V3 output decoupling | P0 |
| C22 | 100nF | LDO U13 +1V8 output decoupling | P0 |

### 电池系统 Battery (P1)

| 位号 | 型号 / 数值 | 说明 | 优先级 |
| --- | --- | --- | --- |
| U6 | TPS61022 (Boost) | 1S Li-Po → 5V boost converter | P1 |
| R20 | 100k | Boost EN pull-up to +VBAT; default boost enabled for bench bring-up | P1 |
| L1 | 4.7µH | Boost inductor | P1 |
| U7 | BQ25180 | 1S Li-Po charger w/ power-path (I2C) | P1 |
| U8 | BQ29700 | Single-cell battery protection (OVP/UVP/OCP) | P1 |
| U9 | MAX17048 | I2C fuel gauge (SOC, low-batt IRQ) | P1 |
| J5 | JST-PH 3p | Battery connector (BAT+/BAT-/NTC) — V1 BENCH cell = 1S 103450 ~2000mAh w/ PCM (~2.5h @3W). Glasses form = 2-3× 35×18×4mm (~500-750mAh, ~30-50min @3W → needs AI duty-cycling). ASSEMBLY: if cell has NO NTC, populate R11 as fixed divider to a valid temp (or disable BQ25180 TS) — else charger faults. Measure current via R3 shunt. | P1 |
| C7 | 22µF | +VBAT bulk decoupling | P1 |
| R11 | 10k | Battery NTC bias (placeholder) | P1 |
| R12 | 2.2k | Charger/Fuel I2C6 SCL pull-up to +1V8 | P1 |
| R13 | 2.2k | Charger/Fuel I2C6 SDA pull-up to +1V8 | P1 |
| C17 | 100nF | Charger U7 VBUS decoupling | P1 |
| C18 | 100nF | Fuel gauge U9 VDD decoupling | P1 |
| C19 | 100nF | Boost U6 VIN decoupling | P1 |

### 传感器 IMU/Haptic (P1)

| 位号 | 型号 / 数值 | 说明 | 优先级 |
| --- | --- | --- | --- |
| U10 | ICM-42688-P | 6-axis IMU (accel+gyro, I2C) | P1 |
| R9 | 2.2k | IMU I2C SCL pull-up to +1V8 | P1 |
| R10 | 2.2k | IMU I2C SDA pull-up to +1V8 | P1 |
| U11 | DRV2605L | LRA/ERM haptic driver | P1 |
| J6 | JST-SH 2p | Vibration motor connector | P1 |
| C16 | 100nF | IMU U10 VDD decoupling | P1 |
| C20 | 100nF | Haptic U11 VDD decoupling | P1 |

### GNSS / 定位 (P0)

| 位号 | 型号 / 数值 | 说明 | 优先级 |
| --- | --- | --- | --- |
| U14 | MAX-M10S-00B-01 | u-blox GNSS (GPS/GLO/GAL/BDS), UART, VIO=1.8V — VCC=3.3V, V_IO=1.8V (matches CM4 UART7 @1.8V), 50Ω RF, U.FL external active antenna. | P0 |
| C27 | DC-block (series,tune) | GNSS RF series match / DC block | P0 |
| C25 | π shunt (DNP,tune) | GNSS π-match shunt, module side (DNP) | P0 |
| C26 | π shunt (DNP,tune) | GNSS π-match shunt, antenna side (DNP) | P0 |
| L2 | RF choke (active-ant) | Bias-tee choke (DNP if passive antenna) | P0 |
| R17 | 10Ω (active-ant) | Active-antenna bias feed from +3V3 (DNP if passive) | P0 |
| C28 | 100nF (active-ant) | Antenna bias decoupling (DNP if passive) | P0 |
| J8 | U.FL / IPEX | GNSS antenna connector (50Ω; external active/passive) | P0 |
| C14 | 100nF | GNSS VCC decoupling | P0 |
| C15 | 10µF | GNSS VCC bulk decoupling | P0 |
| D4 | ESD low-cap RF 0.3pF | GNSS antenna ESD clamp | P0 |

### 指示 / 调试 Debug

| 位号 | 型号 / 数值 | 说明 | 优先级 |
| --- | --- | --- | --- |
| D1 | LED Green | Power LED (active-low GPIO sink) | P0 |
| R4 | 1k | Power LED current limit | P0 |
| D2 | LED Blue | Status LED (active-low GPIO sink) | P0 |
| R5 | 1k | Status LED current limit | P0 |
| J7 | Header 1x4 2.54mm | UART debug header (TX/RX/GND/VREF) | P0 |

### 测试点 Test Points

| 位号 | 型号 / 数值 | 说明 | 优先级 |
| --- | --- | --- | --- |
| TP1 | TestPoint 1.0mm | Test point: VBAT | P0 |
| TP2 | TestPoint 1.0mm | Test point: 5V | P0 |
| TP3 | TestPoint 1.0mm | Test point: 3V3 | P0 |
| TP4 | TestPoint 1.0mm | Test point: 1V8 | P0 |
| TP5 | TestPoint 1.0mm | Test point: GND | P0 |
| TP6 | TestPoint 1.0mm | Test point: UART_TX | P0 |
| TP7 | TestPoint 1.0mm | Test point: UART_RX | P0 |
| TP8 | TestPoint 1.0mm | Test point: CAM_SCL | P0 |
| TP9 | TestPoint 1.0mm | Test point: CAM_SDA | P0 |
| TP10 | TestPoint 1.0mm | Test point: IMU_SCL | P0 |
| TP11 | TestPoint 1.0mm | Test point: IMU_SDA | P0 |
| TP12 | TestPoint 1.0mm | Test point: FUEL_SCL | P0 |
| TP13 | TestPoint 1.0mm | Test point: FUEL_SDA | P0 |
| TP14 | TestPoint 1.0mm | Test point: RESET | P0 |
| TP15 | TestPoint 1.0mm | Test point: RECOVERY | P0 |
| TP16 | TestPoint 1.0mm | Test point: CAM_EN | P0 |

### 按键 Buttons

| 位号 | 型号 / 数值 | 说明 | 优先级 |
| --- | --- | --- | --- |
| SW1 | Tact SW SMD | RECOVERY / maskrom button (to GND) | P0 |
| SW2 | Tact SW SMD | RESET button (to GND) | P0 |
| SW3 | Tact SW SMD | POWER button (to GND) | P0 |
| R14 | 10k | RECOVERY pull-up to +1V8 | P0 |
| R15 | 10k | RESET pull-up to +1V8 | P0 |
| R16 | 10k | POWER_KEY pull-up to +1V8 | P0 |
| R18 | 100k | WL_nDIS pull-up to +1V8; default Wi-Fi enabled | P0 |
| R19 | 100k | BT_nDIS pull-up to +1V8; default Bluetooth enabled | P0 |

## 3. 关键被动元件数值说明

| 类别 | 数值 | 用途 | 备注 |
| --- | --- | --- | --- |
| USB-C CC 下拉 | 5.1kΩ ×2 | 配置为 Sink（取电）角色 | USB-C 规范固定值 |
| VBUS 串联 | 0Ω / 分流电阻 | 5V 取电 + 电流测量预留 | EVT 用 0Ω，量产换分流 |
| I2C 上拉 | 2.2kΩ | 摄像头 / IMU I2C 上拉 | 视总线电容微调 1–4.7k |
| LED 限流 | 1kΩ | 电源 / 状态指示灯 | 视 LED 亮度调整 |
| 电源去耦 | 10µF + 100nF | 各电源轨就近去耦 | 每颗 IC 电源脚补 100nF |
| VBAT 储能 | 22µF | 电池轨大电流缓冲 | 配合 boost 输入 |
| Boost 电感 | 4.7µH | TPS61022 升压电感 | 按峰值电流与 datasheet 选型 |
| 摄像头去耦 | 100nF ×3 | 2.8/1.8/1.2V 每轨 | 配合 LDO datasheet |

> 被动件 pre-layout freeze 已建立：`config/passive_bom_freeze.yaml`。审计输出见 `docs/passive_bom_freeze_2026-06-28.md` 和 `generated/reports/passive_bom_freeze.csv`。`LOCKED_CANDIDATE` 为已给出候选 MPN/LCSC；`PROCUREMENT_VERIFY` 需采购前确认库存/后缀；`TUNE_OR_EVT_SELECT` 为 RF 调谐或台架实测后定值。

## 4. 引脚冻结门禁（需求文档 3.3 节）

- **当前状态**：`REVIEW`（引脚已填，等待采购冻结）。
- ✅ **引脚已全部填写并核对**：全部 56 行已对照官方 `radxa_cm4_pinout_v1.20.xlsx` + Schematic V1.20 填入真实 CM4 引脚号，`source_verified: true`，无 `TBD` 引脚、无单脚冲突。
- 工作主表：`scripts/cm4_pinmap.py`；交付件：`generated/reports/cm4_v1_pin_assignment.xlsx`。
- ⛔ full-layout 门禁仍 **阻塞** 的原因不再是引脚，也不是相机 schematic 电气，而是 8.3 节的 **pre-layout/机械类 TBD**（J2 实物/FPC 路径、B2B 装配核对、载板外形/三连接器 XY 等）。这些解决并 `status: FROZEN` 后方可布线。
- 关键工程决定：`GPIO_VREF`(J3A P78) 接 **1.8V** → J3A GPIO 全部 1.8V；摄像头目标为 **Radxa Camera 4K / IMX415 + CSI3 4-lane**，J2 使用 **Hirose FH35C-31S-0.3SHW(50)** + Radxa **AC006**；PDM1 麦克风、SAI1 音频、UART0 调试、UART7 GNSS；摄像头/IMU/电量计分别用 **I2C0 / I2C8 / I2C6** 三条独立总线。

**待解决的 TBD 项（8.3 节，共 3 项）：**

| 项目 | 需确认内容 | 状态 |
| --- | --- | --- |
| `CM4_SKU` | CONFIRMED RM126-D4E32J0R35W28: RK3576 / 4GB LPDDR4X / 32GB eMMC / Wi-Fi6+BT5.x. Antenna form tracked under ANTENNA. | ✅ 已解决 |
| `CAMERA_ELECTRICAL_PINOUT` | RESOLVED: camera module is Radxa Camera 4K / Sony IMX415-AAQR-C; 31-pin FPC pinout captured in CM4_IMX415_design_files/Radxa_Camera_4K_31pin_pinout.csv and cross-referenced in docs/p0_p1_decisions_2026-06-28.md. | ✅ 已解决 |
| `CAMERA_CONNECTOR_MPN` | RESOLVED: carrier J2 connector is Hirose FH35C-31S-0.3SHW(50), LCSC C424662. Footprint has been generated from the Hirose 2D drawing. | ✅ 已解决 |
| `CAMERA_CABLE` | RESOLVED: use Radxa AC006, 31P 0.3mm to 31P 0.3mm, opposite-side FPC. Do not use AC008; AC008 is 31P to 15P. | ✅ 已解决 |
| `CAMERA_SCHEMATIC_GATE` | RESOLVED for schematic stage: J2 pins 1-31, CSI3 4-lane mapping, P/N polarity, I2C/MCLK/RESET, voltage domains, power pins and NC pins are checked by scripts/audit_csi3_camera.py. RESET is active-low on project net CAM_RST_n; no PWDN pin is present in the Radxa Camera 4K 31-pin pinout. | ✅ 已解决 |
| `CAMERA_KICAD_IMPLEMENTATION` | PARTIAL: schematic source now uses 31-pin FH35C/Radxa Cam4K pinout on CM4 CSI3 4-lane, and the FH35C footprint has been regenerated from the Hirose 2D drawing. DEFERRED_TO_PRE_LAYOUT: AC006 physical validation, FPC contact side, FPC insertion direction, J2 Pin 1 physical check, 1:1 print, coupon test, and FPC bend/enclosure path. Official CM4 IO overlay radxa-cm4-io-radxa-camera-4k.dtbo is confirmed. Bring-up logs (dmesg/media/v4l2) remain open for EVT. | ❌ 未解决 |
| `AUDIO_PARTS` | CONFIRMED: 2×SPH0641LU4H-1 mic, MAX98357AETE+T (C910544) amp, Ole Wolff OWS-091630W50A-8 8Ω/1W (C5840086) speaker | ✅ 已解决 |
| `GNSS_MODULE` | CONFIRMED u-blox MAX-M10S-00B-01: UART, VCC=3.3V/VIO=1.8V, 50Ω U.FL, external active antenna (π-match + bias-tee, DNP for passive) | ✅ 已解决 |
| `BATTERY` | Reverse-calc: 1S 2-3×(35×18×4mm ~250mAh)=500-750mAh/1.85-2.8Wh. V1 bench use ~1.5-2Ah. >3-4h target needs AI duty-cycling (system-power issue, see report) | ✅ 已解决 |
| `POWER_5V` | CONSERVATIVE FREEZE: keep TPS61022-class 1S->5V boost and design +5V_SYS for >=4A bench/boost margin. R3 remains the bring-up shunt/0R measurement point; final peak/thermal validation is deferred to bench testing. | ✅ 已解决 |
| `ANTENNA` | CONSERVATIVE FREEZE: Wi-Fi/BT stays on the CM4 module/U.FL path; carrier does not add 2.4/5GHz RF routing. Layout must reserve the CM4 antenna keep-out and keep battery, metal hinge/screws, speaker magnet, and copper away from the antenna zone. | ✅ 已解决 |
| `BOARD_OUTLINE` | SOURCE GEOMETRY RESOLVED: CM4 module outline = 40.02x54.98mm from official DXF; CM4/IO Board DXF, STEP, placement map and dimensions drawing are the mechanical inputs. OPEN: project must freeze board length/width/radius, USB-C/camera/battery/debug exit direction, mounting holes, and battery-vs-CM4 position. | ❌ 未解决 |
| `B2B_CONNECTOR` | SOURCE FILES RESOLVED: carrier receptacle DF40C-100DS-0.4V(51), module plug DF40C-100DP-0.4V(51), 1.5mm mated height. OPEN: build 2-layer connector-only fit-check board and verify all three connectors press in together with no module lift/skew. | ❌ 未解决 |
| `PINMUX` | PDM/SAI/I2C/UART/GPIO conflict map + Device Tree | ✅ 已解决 |

## 5. 五项当前收敛决定（2026-06-28）

| 优先级 | 项目 | 当前决定 | 状态 |
| --- | --- | --- | --- |
| P0 | 相机实现 | 目标锁定 Radxa Camera 4K / IMX415-AAQR-C；J2 pins 1-31、CSI3 4-lane、P/N、I2C/MCLK/RESET、电压域、供电和 NC 已由 `scripts/audit_csi3_camera.py` 审计 | 🟢 schematic 电气已锁；实体/FPC 路径 `DEFERRED_TO_PRE_LAYOUT` |
| P0 | B2B Fit-Check | 做 2 层只焊三只 DF40C-100DS-0.4V(51) 的验证板，用官方 CM4 STEP + DXF 核对 1.5mm 压合、Pin1、XY、旋转和净空 | 🔴 阻塞：缺 STEP 装配核对 |
| P0 | 载板外形 | CM4 官方 DXF 外形 40.02 × 54.98mm；当前 70 × 55mm 仅作 EVT 草案，三连接器 XY 必须在 KiCad 中导入官方 DXF/STEP 对齐 | 🔴 阻塞：不可从 PDF/文本猜 XY |
| P1 | POWER_5V | 保守冻结 TPS61022-class 1S→5V，+5V_SYS 按 >=4A 裕量，R3 保留 0R/分流实测位 | 🟡 可先冻结，bring-up 实测收尾 |
| P1 | Wi-Fi/BT 天线 | 保守冻结为 CM4 模块板载/U.FL 天线路径，载板不新增 2.4/5GHz RF 走线 | 🟡 可先冻结，layout 阶段执行净空 |

## 6. 下一步行动

1. **相机 J2 schematic gate**：J2 schematic 已切换到 Radxa Camera 4K 31-pin + CM4 CSI3 4-lane；`scripts/audit_csi3_camera.py` 逐脚检查 J2 pin 1-31、MIPI lane、P/N、I2C/MCLK/RESET、电压域、供电和 NC。AC006 实物验证、FPC 接触面、插入方向、Pin1 实体核对、1:1 打印、Coupon 测试、FPC 弯折和外壳路径均为 `DEFERRED_TO_PRE_LAYOUT`。
2. **B2B 连接器（已基本确认，待机械冻结）**：载板侧 3× **Hirose DF40C-100DS-0.4V(51)**（CL No. CL0684-4033-4-51，0.4mm pitch，100-pin，插座），与 Radxa CM4 模块侧 **DF40C-100DP-0.4V(51)** 配对，标称 PCB 板间距 **1.5mm**（厂商 mated height，非两件本体高度相加）。冻结条件：官方 CM4 STEP 装配 + 2 层 Fit-Check 验证板确认三连接器坐标/方向/模块净空/1.5mm 间距。三连接器须作为整体放置并锁定，Pin1 与朝向明确标注，不可单独拖动。
3. **载板外形 / 连接器 XY**：保持 70 × 55mm 作为 EVT 草案；进入 layout 前，在 KiCad/机械 CAD 中导入官方 CM4 DXF/STEP 对齐三连接器，不用 PDF/图片/text-mining 当坐标来源。
4. **POWER_5V 与 Wi-Fi/BT 天线**：按保守决策先冻结；R3 台架实测和 antenna keep-out 在 layout/bring-up 收尾。
5. **冻结引脚表**：以上完成后将门禁置为 `FROZEN`，运行 `scripts/check_pin_freeze.py` 通过，才能进入 PCB 布局。

## 7. 工作流阶段进度（对照 10-Phase 工作流）

| 阶段 | 内容 | 状态 |
| --- | --- | --- |
| Phase 0 | 需求冻结 / 系统框图 / 接口清单 | 🟡 进行中（P1 电源/天线已有保守冻结） |
| Phase 1 | 资料 & Pin Assignment（B2B 引脚 / 电压域 / Pinmux） | 🟡 相机 schematic 电气已锁；pre-layout 仍待 J2 实物/FPC、B2B/外形机械门禁 |
| Phase 2 | 器件选型（MPN / datasheet / 采购） | 🟡 相机目标已锁 IMX415/Radxa Cam4K，J2/AC006 已记录 |
| Phase 3 | 原理图设计（分页 / ERC / BOM） | 🟢 已出元件级原理图草稿（本文件） |
| Phase 4–7 | Floorplan / 布线 / 审查 / 生产文件 | ⚪ 未开始（受 Phase 1 门禁阻塞） |
| Phase 8–10 | Bring-up / Linux 驱动 / 系统测试 | ⚪ 未开始 |

> 当前 schematic 阶段，相机 31-pin J2 电气已经闭合；下一阶段关键阻塞点是 J2 `DEFERRED_TO_PRE_LAYOUT` 实体验证、B2B 2 层 fit-check、载板外形 + 三连接器 XY/STEP 装配。POWER_5V 和 Wi-Fi/BT 天线按保守决策可先冻结，后续 layout/bring-up 收尾。

---

## 附：原理图 / PCB 文件

- 原理图：`hardware/ai_glasses_carrier.kicad_sch`（已含上述全部元件符号 + 网络标签，可在 KiCad 中直接打开查看）
- PCB：`hardware/ai_glasses_carrier.kicad_pcb`（**仅** 板框 + 6 层叠层 + 4 个 M2 安装孔 + 55 个网络；按门禁规则，元件封装在引脚冻结前 **不** 摆放，故 PCB 上目前看不到器件——这是预期行为）
- 生成脚本：`scripts/generate_carrier_board.py`、`scripts/carrier_bom.py`（BOM 唯一来源）、`scripts/generate_report.py`

