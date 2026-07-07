# 更低成本 / 更小空间 / 更低功耗方案调研 · 🔴 待接手
- **从 → 给**: Zizheng → l.hongyi / hardware teammate
- **日期**: 2026-07-07
- **涉及域 / 要读**: `v2_chipdown/reports/AI_Glasses_Chipdown_BOM_V2.3_Current_Schematic_ZH.md`, `v2_chipdown/reports/POWER_BUDGET_V2.md`, `v2_chipdown/reports/AI_Glasses_Hardware_Dimensions_and_Performance_V2.3.md`, `v2_chipdown/reports/AI_Glasses_V2_Phase1_5_Floorplan_ZH.md`, `v2_chipdown/reports/AI_Glasses_V2_Phase1_5_Floorplan.md`, `v2_chipdown/docs/01_architecture.md`, `v2_chipdown/docs/05_hardware_partition.md`

**交接什么**: 请独立调研一轮比当前 RK3576 chip-down baseline 更便宜、更省空间、更低功耗、且更容易塞进运动眼镜外形的硬件方案，并给出可落地的替代架构建议。

## 当前 baseline 必须先看清楚

当前方案不是量产 release，只是 no-route placement + schematic/KiCad export baseline。下面尺寸、功耗、续航、价格都不能当成 EVT 实测或供应商正式 quote。

## 1. 整副眼镜 / 镜腿外形尺寸

先不要只看 PCB，要先看整机能不能戴。当前有两个口径：

| 口径 | 当前数值 | 说明 |
|---|---:|---|
| 外观目标前框宽度 | 138-142 mm | 运动墨镜 / 包裹式前框目标 |
| 外观目标镜腿长度 | 143-147 mm | 常规运动眼镜目标，约 145 mm |
| 外观目标整机重量 | <50 g | 舒适佩戴硬指标 |
| 外观目标镜腿最大厚度 T | <=6 mm | 横向厚度，贴头到外侧 |
| 外观目标镜腿最大高度 H | <=28 mm | 竖向刀锋高度；当前刀锋段目标约 26 mm |
| 当前 RK3576 方案右镜腿 usable length | >=150 mm，最好 ~160+ mm | 为了放 62 mm compute PCB + 70 mm 电池 + speaker/pogo + Wi-Fi antenna keep-out |
| 当前 RK3576 方案左镜腿 usable length | >=145 mm | AON 板 + 70 mm 电池 + BLE keep-out + service 区 |
| 右侧前段 compute pod 内部净空 | >=72 x 20 x 8.5 mm | 62 x 18 mm compute PCB 加 FPC/散热/壳体余量 |
| 右侧 compute pod 外形估计 | 高 22-24 mm，厚 10-11 mm | 这已经明显厚于普通眼镜镜腿 |
| 后段电池/RF/声学 pod 外形估计 | 高 17-18 mm，厚 8.5-9.5 mm | 仍是厚智能眼镜/运动墨镜口径 |
| 前框 sensor brow 内部净空 | >=32 x 8 x 5 mm | camera power/ESD/mic/FPC；camera module 本身仍 HOLD |

**关键矛盾**: 外观目标镜腿约 143-147 mm，但当前 RK3576 右侧工程 fit 需要 >=150 mm，最好 160+ mm。你调研替代方案时，不要只说芯片小了；必须说明它能否把右镜腿从 150-160 mm 需求拉回 143-147 mm 外观目标，或者能否明显降低 22-24 mm 高 / 10-11 mm 厚的 compute pod。

## 2. 当前板级 / 部件占用

| 区域 | 当前 baseline | 备注 |
|---|---:|---|
| 右镜腿 Compute PCB | 62 x 18 x 1.0 mm | RK3576 + PMIC + LPDDR4X + eMMC + Wi-Fi + charger/boost/audio；formal routing 未 release |
| 左镜腿 AON/Power PCB | 46 x 13 x 1.0 mm | nRF54L15 + nPM1300 + NDP120 + BMI270 + sense/power |
| 前框 sensor/FPC target | 32 x 8 mm target | camera module/FPC vendor drawing 未关闭前不能定版 |
| EVT debug tail | 30 x 12 mm | 只给实验室 bring-up；量产应删除或隐藏 |
| 单颗电池控制 envelope | 70 x 12.8 x 5.6 mm | LP451165 300 mAh；左右各一颗 |
| 推荐电池包 | 1S2P, 600 mAh / 2.22 Wh nominal, 约 12 g | 左右镜腿各一颗；pack drawing 和 fit test 仍 HOLD |

## 3. 当前功耗与续航

功耗来自项目预算模型，不是 EVT bench 实测。续航按推荐 LP451165 x2、1S2P、600 mAh、3.7 V nominal、90% usable DoD 计算。

| 状态 | 当前估算总功耗 | 电池电流 | 推荐 600 mAh 续航 |
|---|---:|---:|---:|
| 深度待机 | 22 mW | 6 mA | 91 h |
| 快速待机 | 134 mW | 36 mA | 15 h |
| 手机协作识别 | 362 mW | 98 mA | 5.5 h (331 min) |
| 混合运动使用 | 450 mW | 122 mA | 4.4 h (266 min) |
| 连续 1080p 录像 | 1290 mW | 349 mA | 1.5 h (93 min) |
| 录像 + 本地 AI Burst | 2065 mW | 558 mA | 1.0 h (58 min) |

日常混合模型：

| 使用模型 | 平均功耗 | 推荐 600 mAh 续航 |
|---|---:|---:|
| All-day mixed wear | ~153 mW | 13 h |
| Heavy usage day | ~290 mW | 6.9 h |

对比提醒：如果只用单颗 300 mAh，混合运动使用只有 2.2 h，连续录像约 46 min，AI Burst 约 29 min。因此替代方案如果想减少电池体积，必须同时显著降低 active/record/AI burst 功耗，否则续航会直接不够。

主要功耗池：RK3576 SoC + LPDDR4X + eMMC + PMIC、camera、Wi-Fi active time。AON 侧需要重点确认 NDP120 always-listening 是否真的值得保留。

## 4. 当前预估价格

价格是工程估算，不是实时采购报价，也不是供应商正式 quote。

| 场景 | 1 套 | 5 套 | 20 套 | 100 套 | 1000 套 |
|---|---:|---:|---:|---:|---:|
| 只做裸 PCB/FPC 板组 | $155-460 / ¥1052-3121 | $95-260 / ¥645-1764 | $55-150 / ¥373-1018 | $28-75 / ¥190-509 | $14-40 / ¥95-271 |
| 电子样机/EVT PCBA | $1000-2000 / ¥6785-13571 | $650-1100 / ¥4411-7464 | $420-750 / ¥2850-5089 | $220-420 / ¥1493-2850 | $100-230 / ¥679-1561 |

当前贵的核心原因：右侧 RK3576 compute 架构、8-10 层 HDI 候选、小批量 SMT/NRE、BGA/DDR、定制相机、RF/电池/声学集成风险。

## 5. 你需要做什么

- [ ] 先读上面列出的 baseline 文件，确认你理解当前 architecture：AON island 常开，RK3576 compute island 按需启动。
- [ ] 找 3-5 个替代方案，不限于换主控，也可以是架构变化：phone-assist 更彻底、删/替 NDP120、换低功耗 vision SoC、用模块替代 chip-down、降低 camera/AI spec、把部分计算挪到手机/线控盒等。
- [ ] 每个方案都必须填完整对比表：整机前框宽度、镜腿长度、镜腿最大高度/厚度、PCB/模块尺寸、电池尺寸/容量、待机功耗、录像功耗、AI burst 功耗、续航、BOM/PCBA 成本、软件移植难度、供应链风险、量产/认证风险。
- [ ] 明确这个方案能不能解决当前尺寸矛盾：右镜腿是否还能保持 143-147 mm？compute pod 是否能低于 22-24 mm 高、10-11 mm 厚？电池是否还能保证 4 h 混合使用和约 1 h AI burst？
- [ ] 明确哪些能力会降级：本地 STT/TTS、YOLO/NPU、1080p 编码、always-listening、Wi-Fi 上传、手机依赖程度。
- [ ] 给出你推荐的 1-2 个方案，并说明为什么比当前 baseline 更适合下一版 EVT。
- [ ] 只写 proposal，不直接改 `.kicad_sch` 或 `.kicad_pcb`。

## 6. 建议输出格式

请新增一个 proposal 文件：

`v2_chipdown/reports/alternative_architecture_cost_power_space_research.md`

里面至少包含：

1. 当前 baseline 摘要：整机尺寸、部件尺寸、功耗、续航、成本五张表。
2. 候选方案对比矩阵。
3. 每个候选方案的证据来源：datasheet/package drawing、开发板实测或公开功耗、供应商报价/价格截图、最小起订量、软件 SDK 状态。
4. 推荐方案和不推荐方案。
5. 需要 Zizheng/团队决定的问题。

## 7. 不要踩的坑

- 不要只比较芯片单价。小批量 PCBA 里，HDI、BGA、DDR、SMT/NRE、X-ray、调试风险会吃掉单颗便宜芯片的优势。
- 不要只写 PCB 尺寸。必须写整副眼镜大概多宽、镜腿多长、镜腿最厚/最高、前框/镜腿内部净空够不够。
- 不要只写功耗。必须把功耗换算成 600 mAh / 500 mAh / 300 mAh 等候选电池下的续航。
- 不要把营销 TOPS 当成可用 AI 能力。要看模型支持、NPU toolchain、camera/ISP/encode、Linux/BSP 成熟度。
- 不要默认删 NDP120。可以提出 DNP/phone-assist variant，但要写清楚对 always-listening 体验和待机功耗的影响。
- 不要用未确认尺寸替代当前 envelope。必须写 package/body size、外围器件、DDR/flash/PMIC/antenna/camera connector 后的总占用。
- 不要改 KiCad 文件；先把结论写成 proposal，等团队批准后再进入 schematic 变更。

## 待你回答 / 决定

- 你能否在本周内给出 3-5 个候选方案的第一版对比矩阵？
- 你更倾向从哪条线开始：低功耗 AON、替代 RK3576 compute、phone-assist 架构、camera/Wi-Fi/encoder 降配、还是有线/口袋计算盒？
- 你需要我补哪类约束：目标续航、目标镜腿宽度/高度、目标售价、必须保留的本地 AI 能力？
