# Radxa CM4 + IMX415 设计文件索引

本目录用于支持以下五项工作：

1. Radxa Camera 4K / IMX415 31-pin FPC 原理图连接
2. CM4 4-lane CSI 引脚切换与核对
3. CM4 三组 B2B 连接器 Fit-Check
4. 载板外形、连接器 XY 和 3D 装配
5. POWER_5V 与 Wi-Fi/BT 天线布局的后续验证

> 注意：目录中已放入项目现有的 CM4 与 CM4 IO Board 原理图。其余官方文件请运行 `fetch_official_files.sh` 下载，或使用下方链接手动下载。

---

## A. 相机：Radxa Camera 4K / IMX415

### A1. 官方相机页面（含完整 31-pin pinout）
https://docs.radxa.com/en/accessories/camera/camera-4k

### A2. Radxa Camera 4K Product Brief
https://dl.radxa.com/accessories/camera-4k/radxa_camera_4k_product_brief_Revision_1.0.pdf

用途：确认模组尺寸、4-lane MIPI CSI-2、镜头、FOV、排线长度。

### A3. Sony IMX415-AAQR-C Datasheet
https://dl.radxa.com/accessories/camera-4k/IMX415-AAQR-C_Datasheet_E19504.pdf

用途：确认传感器电源、电平、时钟、I2C、CSI-2、上电时序和寄存器。

### A4. 31-pin pinout
见同目录：`Radxa_Camera_4K_31pin_pinout.csv`

关键提醒：
- FPC 接触面、Pin 1 方向和连接器上下接触方式标记为 `DEFERRED_TO_PRE_LAYOUT`，不作为当前 schematic 电气门禁。
- 不能只按针数画连接器。
- 相机模块的 4 条数据 lane 标为 MD1~MD4；当前 schematic 已按 CSI3 D0~D3 审计，CM4 Device Tree `data-lanes` 仍必须保持同一 lane order。

### A5. IMX415 bring-up 参考
ROCK 5 ITX 官方教程：
https://docs.radxa.com/en/rock5/rock5itx/getting-started/interface-usage/camera

这只能作为 IMX415 驱动/overlay 和 GStreamer 测试方法的参考，不能证明其 overlay 可不修改地用于 CM4。

---

## B. CM4 4-lane CSI 与 Pin Assignment

### B1. CM4 Schematic V1.20
本目录已有：`radxa_cm4_schematic_v1.20.pdf`

重点页面：
- Page 11：RK3576 MIPI DSI/CSI
- Page 22：High Speed Connector J3B

### B2. CM4 Pinout Table V1.20
https://dl.radxa.com/cm4/docs/hw/radxa_cm4_pinout_v1.20.xlsx

用途：将相机 lane、clock、I2C、MCLK、RESET/PWDN 映射到准确的 J3B/J1 引脚与电压域。

### B3. CM4 IO Schematic V1.10
本目录已有：`radxa_cm4_io_schematic_v1.10.pdf`

重点页面：
- Page 9：High Speed Connector
- Page 10：IO Connector / camera control
- Page 17：MIPI CSI RX

命名提醒：项目里称“CSI3”时，必须确认它指的是 SoC 的 CSI3/4 组合 4-lane 通道，还是官方 IO Board 上标注的 4-lane camera port。不要仅根据名称自动替换网络。

---

## C. B2B Fit-Check 与载板外形

### C1. CM4 Components Placement Map V1.20
https://dl.radxa.com/cm4/docs/hw/radxa_cm4_components_placement_map_v1.20.pdf

### C2. CM4 2D DXF V1.20
https://dl.radxa.com/cm4/docs/hw/radxa_cm4_2d_dxf_v1.20.zip

这是建立载板外形和三组连接器 XY 的主要机械基准。

### C3. CM4 3D STEP V1.20
https://dl.radxa.com/cm4/docs/hw/radxa_cm4_3d_stp_v1.20.zip

这是进行 3D 装配、干涉、压合方向和高度检查的主要文件。

### C4. CM4 IO Board 参考机械文件
Placement Map:
https://dl.radxa.com/cm4/cm4-io-board/docs/hw/radxa_cm4_io_components_placement_map_v1.10.pdf

2D DXF:
https://dl.radxa.com/cm4/cm4-io-board/docs/hw/radxa_cm4_io_2d_dxf_v1.10.zip

本仓库已保存：
- `mechanical/radxa_cm4_io_2d_dxf_v1.10/RC126_V1.10_20250526_TOP.dxf`
- `mechanical/radxa_cm4_io_2d_dxf_v1.10/RC126_V1.10_20250526_BOT.dxf`

可可靠抽取的事实：官方 IO Board 板框约 160.01 x 90.02 mm。DXF 中的 `Connector_1/2/3` 是文字标签位置，不是可直接制造的 DF40C footprint origin。

3D STEP:
https://dl.radxa.com/cm4/cm4-io-board/docs/hw/radxa_cm4_io_3d_stp_v1.10.zip

官方工程仓库：
https://github.com/radxa/radxa-cm-projects/tree/main/cm4/radxa-cm4-io-board

### C5. Hirose DF40C 连接器官方文件
CM4 模块端 Plug：DF40C-100DP-0.4V(51)
https://www.hirose.com/product/p/CL0684-4032-1-51

载板端 Receptacle：DF40C-100DS-0.4V(51)
https://www.hirose.com/product/p/CL0684-4033-4-51

在产品页面下载：
- Drawing (2D)
- Specification Sheet
- Product Guidelines
- Drawing (3D) (STEP)

该 DP + DS 组合的标称 mating height 为 1.5 mm。Fit-Check 板应只焊三只载板端 DS 连接器，以验证 XY、Pin 1、旋转角、压合和拆卸。

---

## D. POWER_5V

目前不存在一份能替代实测的“CM4 + IMX415 + 音频 + GNSS 峰值功耗文件”。应结合：

- CM4 Schematic V1.20
- CM4 Pinout V1.20（确认全部 5 V 输入引脚）
- 项目需求文档中的峰值电流/效率/热设计门禁
- EVT 台架分流电阻与示波器实测

首版 boost 可以按保守峰值冻结，但 PCB 必须保留：
- 电流测量分流/测试点
- 足够输入输出电容位置
- EN 与电源良好信号测试点
- 电感、二极管/同步管和 IC 的热铜区

---

## E. Wi-Fi / Bluetooth 天线

无线芯片在 CM4 模块上。载板阶段需要的主要文件是：

- CM4 Placement Map
- CM4 2D DXF
- CM4 3D STEP
- 最终选用天线的厂商 datasheet / keep-out drawing

如果使用 CM4 的外接天线接口，载板通常无需自行画 2.4/5 GHz RF 走线，但仍要在 3D 装配里避开：
- 电池
- 金属铰链与螺丝
- 大面积铜和屏蔽罩
- 扬声器磁体
- 人头侧的高损耗材料

---

## 最小文件门禁

在允许切换到 IMX415 原理图与 PCB Layout 前，应至少保存以下文件到仓库：

- Radxa Camera 4K 官方页面或 pinout 导出
- Camera 4K Product Brief
- IMX415 Datasheet
- CM4 Schematic V1.20
- CM4 Pinout V1.20
- CM4 Placement Map V1.20
- CM4 2D DXF V1.20
- CM4 3D STEP V1.20
- DF40C Plug 与 Receptacle 的 2D drawing + STEP
- IMX415 CM4 Device Tree/driver 验证记录
