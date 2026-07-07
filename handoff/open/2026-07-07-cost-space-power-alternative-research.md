# 更低成本 / 更小空间 / 更低功耗方案调研 · 🔴 待接手
- **从 → 给**: Zizheng → l.hongyi / hardware teammate
- **日期**: 2026-07-07
- **涉及域 / 要读**: `v2_chipdown/reports/AI_Glasses_Chipdown_BOM_V2.3_Current_Schematic_ZH.md`, `v2_chipdown/reports/POWER_BUDGET_V2.md`, `v2_chipdown/reports/AI_Glasses_Hardware_Dimensions_and_Performance_V2.3.md`, `v2_chipdown/reports/AI_Glasses_V2_Phase1_5_Floorplan_ZH.md`, `v2_chipdown/docs/01_architecture.md`, `v2_chipdown/docs/05_hardware_partition.md`

**交接什么**: 请独立调研一轮比当前 RK3576 chip-down baseline 更便宜、更省空间、更低功耗的硬件方案，并给出可落地的替代架构建议。

## 当前 baseline 必须先看清楚

当前方案不是量产 release，只是 no-route placement + schematic/KiCad export baseline。不要把以下数字当成已实测或供应商正式 quote。

### 当前占用空间 / 机械 envelope

| 区域 | 当前 baseline | 备注 |
|---|---:|---|
| 右镜腿 Compute PCB | 62 x 18 x 1.0 mm | 右侧最紧张；RK3576 + PMIC + LPDDR4X + eMMC + Wi-Fi + charger/boost/audio |
| 左镜腿 AON/Power PCB | 46 x 13 x 1.0 mm | nRF54L15 + nPM1300 + NDP120 + BMI270 + sense/power |
| 前框 sensor/FPC target | 32 x 8 mm target | camera module/FPC vendor drawing 未关闭前不能定版 |
| EVT debug tail | 30 x 12 mm | 只给实验室 bring-up；量产应删除或隐藏 |
| 电池 envelope | 左右各 LP451165 300 mAh，1S2P 共 600 mAh / 2.22 Wh nominal | 左右镜腿各一颗；pack drawing 和 fit test 仍 HOLD |

### 当前功耗估算

功耗来自项目预算模型，不是 EVT bench 实测。后续必须用分域 shunt 数据替换。

| 状态 | 当前估算总功耗 |
|---|---:|
| 深度待机 | 22 mW |
| 快速待机 | 134 mW |
| 手机协作识别 | 362 mW |
| 混合运动使用 | 450 mW |
| 连续 1080p 录像 | 1290 mW |
| 录像 + 本地 AI Burst | 2065 mW |

主要功耗池：RK3576 SoC + LPDDR4X + eMMC + PMIC、camera、Wi-Fi active time。AON 侧需要重点确认 NDP120 always-listening 是否真的值得保留。

### 当前预估价格

价格是工程估算，不是实时采购报价，也不是供应商正式 quote。

| 场景 | 1 套 | 5 套 | 20 套 | 100 套 | 1000 套 |
|---|---:|---:|---:|---:|---:|
| 只做裸 PCB/FPC 板组 | $155-460 / ¥1052-3121 | $95-260 / ¥645-1764 | $55-150 / ¥373-1018 | $28-75 / ¥190-509 | $14-40 / ¥95-271 |
| 电子样机/EVT PCBA | $1000-2000 / ¥6785-13571 | $650-1100 / ¥4411-7464 | $420-750 / ¥2850-5089 | $220-420 / ¥1493-2850 | $100-230 / ¥679-1561 |

当前贵的核心原因：右侧 RK3576 compute 架构、8-10 层 HDI 候选、小批量 SMT/NRE、BGA/DDR、定制相机、RF/电池/声学集成风险。

## 你需要做什么

- [ ] 先读上面列出的 baseline 文件，确认你理解当前 architecture：AON island 常开，RK3576 compute island 按需启动。
- [ ] 找 3-5 个替代方案，不限于换主控，也可以是架构变化：phone-assist 更彻底、删/替 NDP120、换低功耗 vision SoC、用模块替代 chip-down、降低 camera/AI spec 等。
- [ ] 每个方案都要填对比表：BOM/PCBA 成本、PCB/模块尺寸、待机功耗、录像功耗、AI burst 功耗、软件移植难度、供应链风险、量产/认证风险。
- [ ] 明确哪些能力会降级：本地 STT/TTS、YOLO/NPU、1080p 编码、always-listening、Wi-Fi 上传、手机依赖程度。
- [ ] 给出你推荐的 1-2 个方案，并说明为什么比当前 baseline 更适合下一版 EVT。
- [ ] 只写 proposal，不直接改 `.kicad_sch` 或 `.kicad_pcb`。

## 建议输出格式

请新增一个 proposal 文件：

`v2_chipdown/reports/alternative_architecture_cost_power_space_research.md`

里面至少包含：

1. 当前 baseline 摘要：空间、功耗、成本三张表。
2. 候选方案对比矩阵。
3. 每个候选方案的证据来源：datasheet/package drawing、开发板实测或公开功耗、供应商报价/价格截图、最小起订量、软件 SDK 状态。
4. 推荐方案和不推荐方案。
5. 需要 Zizheng/团队决定的问题。

## 不要踩的坑

- 不要只比较芯片单价。小批量 PCBA 里，HDI、BGA、DDR、SMT/NRE、X-ray、调试风险会吃掉单颗便宜芯片的优势。
- 不要把营销 TOPS 当成可用 AI 能力。要看模型支持、NPU toolchain、camera/ISP/encode、Linux/BSP 成熟度。
- 不要默认删 NDP120。可以提出 DNP/phone-assist variant，但要写清楚对 always-listening 体验和待机功耗的影响。
- 不要用未确认尺寸替代当前 envelope。必须写 package/body size、外围器件、DDR/flash/PMIC/antenna/camera connector 后的总占用。
- 不要改 KiCad 文件；先把结论写成 proposal，等团队批准后再进入 schematic 变更。

## 待你回答 / 决定

- 你能否在本周内给出 3-5 个候选方案的第一版对比矩阵？
- 你更倾向从哪条线开始：低功耗 AON、替代 RK3576 compute、phone-assist 架构、还是 camera/Wi-Fi/encoder 降配？
- 你需要我补哪类约束：目标续航、目标镜腿宽度/高度、目标售价、必须保留的本地 AI 能力？
