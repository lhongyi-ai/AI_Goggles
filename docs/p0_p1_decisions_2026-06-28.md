# P0/P1 收敛决定 — IMX415 / B2B / 外形 / 电源 / 天线

日期：2026-06-28

本文件是五个当前卡点的工程决策记录。可读资料可参考 `ai_context/`，但可编辑源文件仍是 `hardware/*.kicad_*`、`data/*.xlsx`、`config/*.yaml` 和 `scripts/*.py`。本轮没有手动编辑 `ai_context/`。

## 结论总表

| 优先级 | 项目 | 当前决定 | 状态 |
| --- | --- | --- | --- |
| P0 | 相机实现 | 目标锁定 Radxa Camera 4K / IMX415-AAQR-C；31-pin FPC pinout、J2 连接器 MPN、AC006 线材已解决；schematic source 已切到 Radxa Cam4K 31-pin + CM4 CSI3 4-lane；J2 pins 1-31、P/N、I2C/MCLK/RESET、电压域、供电和 NC 已由脚本审计 | schematic 电气已锁；实体/FPC 路径项 `DEFERRED_TO_PRE_LAYOUT` |
| P0 | B2B Fit-Check | 做 2 层、只焊 J3A/J3B/J1 三个 DF40C-100DS-0.4V(51) 的验证板；用官方 CM4 STEP + DXF 核对 1.5 mm 压合、高度和 XY | 阻塞机械验证 |
| P0 | 载板外形 | CM4 模块外形按官方 DXF：40.02 x 54.98 mm；当前载板草案 70 x 55 mm 仅作 EVT 骨架，三连接器 XY 必须从 KiCad 导入官方 DXF/STEP 对齐，不从 PDF/文本猜坐标 | 阻塞 layout |
| P1 | POWER_5V | 先冻结保守决定：TPS61022-class 1S -> 5 V boost，+5V_SYS 按 >=4 A bring-up/瞬态裕量设计，R3 保留 0R/分流实测位 | 可先冻结 |
| P1 | Wi-Fi/BT 天线 | 先冻结保守决定：使用 CM4 模块板载/U.FL 天线路径，载板不新增 2.4/5 GHz RF 走线；layout 阶段执行 CM4 天线净空 | 可先冻结 |

## 1. P0 相机实现：Radxa Camera 4K / IMX415

本地证据：

- 31-pin FPC pinout：`CM4_IMX415_design_files/Radxa_Camera_4K_31pin_pinout.csv`
- CM4 pinout 权威源：`data/radxa_cm4_pinout_v1.20.xlsx`
- 当前原生 KiCad 源：`hardware/ai_glasses_carrier.kicad_sch`

锁定器件：

- 相机模块：Radxa Camera 4K
- Sensor：Sony IMX415-AAQR-C
- 载板 J2 FPC 连接器：Hirose FH35C-31S-0.3SHW(50)
- LCSC：C424662
- FPC：Radxa AC006，31P 0.3 mm 到 31P 0.3 mm，Opposite Side
- 不使用 AC008；AC008 是 31P 到 15P 转接线。

Schematic 电气门禁：

- J2 symbol 为 31-pin。
- J2 pin 1–31 逐脚对照 `CM4_IMX415_design_files/Radxa_Camera_4K_31pin_pinout.csv`。
- CSI3 lane order 与 P/N polarity 已由 `scripts/audit_csi3_camera.py` 审计。
- I2C / MCLK / RESET 均为 1.8 V；`CAM_RST_n` 为 active-low。
- Pin 28/29 接 `+CAM_3V3`；Pin 30/31 接 `+5V_SYS`；Pin 8/9/22/23/26 为 intentional NC。
- 当前目标：KiCad ERC 0 violation；若出现 warning 必须解释。

Pre-layout 实体门禁：

- Footprint 已在 `hardware/AI_Glasses.pretty/FH35C-31S-0.3SHW_50.kicad_mod` 建立，含 Pin 1、Fab 和 FPC 插入方向标记。
- Footprint source config: `config/j2_fh35c_footprint.yaml`。
- Drawing 核对记录：`docs/j2_fh35c_footprint_check_2026-06-28.md`。
- 1:1 check PDF：`generated/reports/j2_fh35c_1to1_check.pdf`。
- 以下项目为 `DEFERRED_TO_PRE_LAYOUT`：AC006 实物验证、FPC 接触面、插入方向、Pin 1 实体核对、1:1 打印、Coupon 测试、FPC 弯折和外壳路径。

Radxa Camera 4K 31-pin FPC 已知信号：

| FPC pin | Signal | 连接建议 |
| --- | --- | --- |
| 2/3 | MDN4/MDP4 | CSI3 lane 3 N/P 候选 |
| 5/6 | MDN3/MDP3 | CSI3 lane 2 N/P 候选 |
| 11/12 | MDN2/MDP2 | CSI3 lane 1 N/P 候选 |
| 14/15 | MDN1/MDP1 | CSI3 lane 0 N/P 候选 |
| 17/18 | MCN/MCP | CSI3 clock N/P 候选 |
| 20 | MCLK | CAM_CLK2_OUT_M0 / `MIPI_CSI3_CAM_CLKOUT_1V8` 候选 |
| 24/25 | SCL/SDA | 继续用 I2C0 或改用相机专用 I2C，需 Device Tree 一起确认 |
| 27 | RESET_N | active-low；项目 net 为 `CAM_RST_n` |
| 28/29 | VCC3.3V | Camera 3.3 V rail |
| 30/31 | VCC5V | Camera 5 V rail |

CM4 CSI3 4-lane 映射，来自 `data/radxa_cm4_pinout_v1.20.xlsx`：

| Camera FPC | CM4 net | CM4 connector pin |
| --- | --- | --- |
| MCP | MIPI_DPHY_CSI3_RX_CLKP | 129 |
| MCN | MIPI_DPHY_CSI3_RX_CLKN | 127 |
| MDP1 | MIPI_DPHY_CSI3_RX_D0P | 117 |
| MDN1 | MIPI_DPHY_CSI3_RX_D0N | 115 |
| MDP2 | MIPI_DPHY_CSI3_RX_D1P | 123 |
| MDN2 | MIPI_DPHY_CSI3_RX_D1N | 121 |
| MDP3 | MIPI_DPHY_CSI3_RX_D2P | 135 |
| MDN3 | MIPI_DPHY_CSI3_RX_D2N | 133 |
| MDP4 | MIPI_DPHY_CSI3_RX_D3P | 141 |
| MDN4 | MIPI_DPHY_CSI3_RX_D3N | 139 |
| MCLK | MIPI_CSI3_CAM_CLKOUT_1V8 / CAM_CLK2_OUT_M0 | 59 |

注意：上表已进入 schematic source；J2 31-pin 电气门禁已由 `scripts/audit_csi3_camera.py` 逐脚审计。J2 footprint 与 Pin 1/Fab/插入方向标记已按 Hirose drawing 更新，但实物连接器/AC006/1:1/弯折路径均标记为 `DEFERRED_TO_PRE_LAYOUT`。

CSI3/CSI4 lane 与控制电压审计报告：`docs/csi3_imx415_audit_2026-06-28.md`。审计结论：I2C、MCLK、RESET 均按 1.8 V 处理；CM4 pins 133/135/139/141 在 pinout 中主名为 CSI4，但 function list 暴露 CSI3 D2/D3，需在 Device Tree 中保持同一 lane order。

Radxa 官方 ROCK 5 ITX CSI 教程可作为 IMX415 bring-up 参考：页面列出 Radxa Camera 4K 使用 IMX415，ROCK 5 ITX 有两个 4-lane CSI 接口，并通过 `rsetup` 启用 Radxa Camera 4K overlay 后使用 `/dev/video11` 做 GStreamer 测试。该教程不能直接证明 CM4 overlay 无需修改。

官方 CM4 IO overlay 已确认：

| Item | Value |
| --- | --- |
| Overlay | `radxa-cm4-io-radxa-camera-4k.dtbo` |
| rsetup title | `Enable Radxa Camera 4K` |
| Board target | `radxa,cm4-io` |
| Sensor | IMX415 |
| I2C address | `0x1a` |
| MIPI lanes | 4 |
| D-PHY | `csi2_dphy3` |

Bring-up 参考命令：

```bash
rsetup
gst-launch-1.0 v4l2src device=/dev/video11 io-mode=4 ! videoconvert ! video/x-raw,format=NV12,width=1920,height=1080 ! xvimagesink
```

CM4 上必须重新确认：I2C controller、GPIO reset、MCLK、CSI endpoint、`data-lanes` 顺序、RKISP/rkcif/media graph。

## 2. P0 B2B Fit-Check

验证板目标：

- 2 层 PCB。
- 只焊三只载板端连接器：J3A / J3B / J1。
- 连接器目标：Hirose DF40C-100DS-0.4V(51)。
- 对配模块端：DF40C-100DP-0.4V(51)。
- 目标压合高度：1.5 mm。

门禁：

- 必须拿到官方 CM4 STEP。
- KiCad 导入 CM4 2D DXF 对齐三连接器 XY，不从 PDF 图片或文本抽坐标。
- 机械组检查压入方向、Pin 1、旋转角、拆卸空间、屏蔽罩/器件净空。

官方资料状态：

- B2B source files resolved：DF40C plug/receptacle、CM4 2D DXF、CM4 3D STEP、CM4 placement map、IO Board dimensions drawing。
- B2B physical fit-check open：还需要实际 2 层 fit-check 板和 CM4 STEP 装配核对。

仓库实现方式：

- 门禁配置：`config/b2b_fit_check.yaml`
- 生成脚本：`scripts/generate_b2b_fit_check.py`
- 输出目标：`hardware/b2b_fit_check.kicad_pcb`

当前脚本会在 J3A/J3B/J1 的 `x_mm`、`y_mm`、`rotation_deg`、`pin1_orientation` 未录入时拒绝生成 PCB。下一步必须在 KiCad 或机械 CAD 中导入官方 CM4 DXF/STEP，放置/核对真实 DF40C-100DS footprint 后，把三连接器坐标写回 YAML。不要从 PDF 或 DXF 文本里猜连接器坐标。

补充：`mechanical/radxa_cm4_io_2d_dxf_v1.10/RC126_V1.10_20250526_TOP.dxf` 中有 `Connector_1`、`Connector_2`、`Connector_3` 文字标签，可帮助人工识别三组 B2B 区域；这些是文字插入点，不是 footprint origin，不能直接作为制造坐标。

## 3. P0 载板外形

已知：

- CM4 官方 DXF 外形：40.02 x 54.98 mm。
- CM4 IO Board 官方 DXF 外形：160.01 x 90.02 mm，仅作官方参考板几何输入。
- 当前 EVT 载板草案：70 x 55 mm。
- Board outline source geometry resolved：CM4 2D DXF / 3D STEP / Placement Map、CM4 IO Board 2D DXF / 3D STEP / Dimensions Drawing。

当前决定：

- 70 x 55 mm 可继续作为电气骨架和报告尺寸。
- 进入 layout 前必须用官方 CM4 DXF/STEP 在 KiCad 里做三连接器 XY 对齐。
- 不声称图形布局正确，除非已在 KiCad/机械 CAD 中打开并完成装配核对。
- 官方文件不能替项目决定定制载板外形；仍需冻结板长、板宽、圆角半径、USB-C/Camera FPC/电池/调试口出线方向、安装孔/定位柱、电池与 CM4 的相对位置。

## 4. P1 POWER_5V

保守冻结：

- 采用 TPS61022-class 1S Li-Po -> 5 V boost。
- +5V_SYS 设计电流按 >=4 A 裕量。
- R3 保留 0R/分流脚位，用于 bring-up 台架实测。

待实测收尾：

- Idle / camera / camera+AI / +H.265 / +Wi-Fi / full load 电流。
- Boost IC、inductor、输入输出电容温升。
- 最终峰值、电池容量和热设计。

## 5. P1 Wi-Fi/BT 天线

保守冻结：

- 使用 CM4 模块板载/U.FL 天线路径。
- 载板不新增 2.4/5 GHz RF 走线。

Layout 收尾：

- 保留 CM4 天线区净空。
- 天线附近避开电池、金属铰链、螺丝、大铜皮、屏蔽罩、扬声器磁体。
- 最终天线形态以采购到的 CM4 SKU 和实物装配为准。
