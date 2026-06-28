# Radxa CM4 Carrier Board 门禁资料与 FPC 解决方案

更新日期：2026-06-28

## 1. Camera / FPC

### 锁定器件
- 相机模块：Radxa Camera 4K
- Sensor：Sony IMX415-AAQR-C
- 载板 J2 FPC 连接器：Hirose FH35C-31S-0.3SHW(50)
- LCSC：C424662
- FPC：Radxa AC006，31P 0.3 mm → 31P 0.3 mm，Opposite Side
- 不使用 AC008；AC008 是 31P → 15P 转接线。

### 官方资料
- Camera 4K 页面与 31-pin pinout:
  https://docs.radxa.com/en/accessories/camera/camera-4k
- Camera 4K Product Brief:
  https://dl.radxa.com/accessories/camera-4k/radxa_camera_4k_product_brief_Revision_1.0.pdf
- IMX415 datasheet:
  https://dl.radxa.com/accessories/camera-4k/IMX415-AAQR-C_Datasheet_E19504.pdf
- Radxa 对 FH35C-31S-0.3SHW(50) 的明确型号说明:
  https://docs.radxa.com/en/rock4/rock4d/hardware-use/mipi-csi
- LCSC FH35C 页面:
  https://www.lcsc.com/product-detail/C424662.html
- Radxa AC006 FPC:
  https://radxa.com/products/accessories/fpc-cable-ac006/

### Schematic 电气门禁
- J2 symbol 为 31-pin。
- J2 pad 1 对应 Camera 4K pin 1 = GND。
- J2 pin 1–31 已逐脚对照 Radxa Camera 4K 31-pin pinout。
- CSI3 4-lane、P/N polarity、I2C、MCLK、RESET、电压域、供电和 NC 已由 `scripts/audit_csi3_camera.py` 审计。
- RESET 使用项目 net `CAM_RST_n`，active-low；Radxa Camera 4K 31-pin pinout 无 PWDN。
- 当前目标：KiCad ERC 0 violation；若出现 warning 必须逐项解释。

### DEFERRED_TO_PRE_LAYOUT
- AC006 实物验证。
- FPC 接触面。
- 插入方向。
- Pin 1 实体核对。
- 1:1 打印。
- Coupon 测试。
- FPC 弯折和外壳路径。

### Pre-layout / Fab 前门禁
- Footprint 按 Hirose 2D drawing 建立并人工核对。
- Pin 1 丝印三角与 Fab 标记明确。
- 做 1:1 PDF 打印，将实物连接器放在打印图上核对。
- 购买至少 5 个连接器和 2 条 AC006，做实物插拔和导通验证。

## 2. B2B Fit-Check

### 锁定器件
- CM4 模块端 Plug：DF40C-100DP-0.4V(51)
- 载板端 Receptacle：DF40C-100DS-0.4V(51)
- 配合高度：1.5 mm

### 官方资料
- Plug:
  https://www.hirose.com/product/p/CL0684-4032-1-51
- Receptacle:
  https://www.hirose.com/product/p/CL0684-4033-4-51
- Radxa CM4 资源页:
  https://docs.radxa.com/en/som/cm/cm4/download
- CM4 2D DXF:
  https://dl.radxa.com/cm4/docs/hw/radxa_cm4_2d_dxf_v1.20.zip
- CM4 3D STEP:
  https://dl.radxa.com/cm4/docs/hw/radxa_cm4_3d_stp_v1.20.zip
- CM4 Placement Map:
  https://dl.radxa.com/cm4/docs/hw/radxa_cm4_components_placement_map_v1.20.pdf
- IO Board dimensions:
  https://dl.radxa.com/cm4/cm4-io-board/docs/hw/radxa_cm4_io_dimensions_drawing.pdf

### Fit-check 板要求
- 2 层板。
- 仅放 3 个 DF40C-100DS、板框、Pin 1 和中心线。
- 不放电源和功能元件。
- 先用 CM4 DXF 获取三连接器 XY 和角度。
- 实物验证三只连接器能同时压入，模块无翘起和偏转。

## 3. Board Outline

### 输入资料
- CM4 2D DXF / 3D STEP / Placement Map
- CM4 IO Board 2D DXF / 3D STEP / Dimensions Drawing

### 仍需项目决定
官方文件只能提供 CM4 和连接器几何位置，不能替项目决定定制载板外形。需冻结：
- 板长、板宽、圆角半径
- USB-C、Camera FPC、电池、调试口出线方向
- 安装孔/定位柱
- 电池与 CM4 的相对位置

## 4. POWER_5V

### 参考资料
- CM4 Schematic V1.20
- CM4 Pinout V1.20
- CM4 IO Board Schematic V1.10
- 项目 Power Budget 与台架测量记录

### 临时冻结建议
- 台架输入：5 V / 4 A 以上。
- Boost 不按平均电流选，按峰值和瞬态选。
- 预留分流电阻、输入/输出测试点、Boost EN/PG、扩展电容位。
- EVT 运行 Camera 4K + NPU + Video Encode + Wi-Fi TX + Speaker，测启动峰值和稳态峰值。

## 5. Wi-Fi / Bluetooth Antenna

### 已知
- Wi-Fi/BT 在 CM4 模块上。
- CM4 使用外接天线接口。
- Carrier 不新增 Wi-Fi/BT RF 芯片和 50-ohm 天线走线。

### Layout 门禁
- CM4 天线接头上方和出线方向不得被载板元件挡住。
- FPC 天线远离电池、金属铰链、扬声器磁体、开关电感和大面积金属。
- 最终天线型号、线长和粘贴位置需要整机 RF 测试后关闭。

## 更新后的门禁状态

| 门禁 | 状态 |
|---|---|
| Camera electrical pinout | Resolved |
| Camera connector MPN | Resolved: FH35C-31S-0.3SHW(50) |
| Camera cable | Resolved: AC006 |
| Camera schematic electrical gate | Resolved: J2 1–31 / CSI3 / P-N / control / power / NC |
| Camera pre-layout physical gate | DEFERRED_TO_PRE_LAYOUT: AC006, contact side, insertion, Pin 1 physical, 1:1 print, coupon, FPC bend/path |
| B2B source files | Resolved |
| B2B physical fit-check | Open |
| Board outline source geometry | Resolved |
| Board outline final decision | Open |
| POWER_5V provisional design | Can freeze provisionally |
| POWER_5V measured peak | Open until EVT |
| Antenna carrier schematic | Resolved: no extra RF circuit |
| Antenna placement/RF validation | Open until layout/EVT |
