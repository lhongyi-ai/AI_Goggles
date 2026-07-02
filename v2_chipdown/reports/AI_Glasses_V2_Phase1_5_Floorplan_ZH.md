# AI Glasses V2 Phase 1.5 机械/电气 Floorplan 中文交付版

这份文件按当前 V2 schematic/BOM 说话，用来给 CAD、结构、PCB layout 团队判断：现有这些部件能不能放进眼镜、需要什么框架、分别放哪里、PCB 要不要叠、各模块怎么连接。

## 结论

- 普通细镜腿光学眼镜 **放不下** 这一版 V2 RK3576 chip-down 架构。
- 厚镜腿 smart glasses / 运动墨镜式框架 **有条件放得下**，前提是内部空间达到下面的最小包络。
- 这不是正式 PCB layout 放行。G00/G00F/G07/G10/G12/G14 仍然需要真实 CAD、假电芯、天线、FPC、扬声器、相机模组和封装图纸验证。
- 任何真实 3D 包络、器件 courtyard、电池膨胀区、speaker cavity 或 RF antenna keep-out 重叠都算 **fail**。只有 CAD/EE 明确证明它们处在不同 Z 高度，并且 clearance、隔离、热和 RF 都通过，才可以接受。

## 最小内部尺寸

| 区域 | 最小内部尺寸 | 说明 |
|---|---:|---|
| 右镜腿可用长度 | >=150 mm，推荐 ~160+ mm | RK3576 计算板 + 70 mm 电池 + speaker/pogo + Wi-Fi antenna keep-out |
| 右前 compute pod | >=72 x 20 x 8.5 mm | 62 x 18 mm compute PCB + FPC 缓冲 + 热路径 |
| 右后电池/RF/声学区 | >=78 x 16 x 8.5 mm | LP451165 最大包络 70 x 12.8 x 5.6 mm + 泡棉/膨胀 + LS1 声学槽 + pogo + RF 窗口 |
| 左镜腿可用长度 | >=145 mm | AON 板 + 70 mm 电池 + BLE keep-out + pogo |
| 左前 AON pod | >=54 x 16 x 7.5 mm | 46 x 14 mm AON/power PCB + FPC + 壳体余量 |
| 左后电池/RF区 | >=82 x 16 x 7.5 mm | LP451165 最大包络 + BLE antenna 区 + 充电/维修区 |
| 前框 sensor brow | >=32 x 8 x 5 mm | IMX415 custom module、camera power、ESD、mic footprints、FPC exit |

## 推荐眼镜框架

第一版应按 fixed-temple EVT 处理，不强行做量产折叠铰链。结构上建议：

- 厚 acetate / TR / PC 类 smart-glasses 框架，不用普通细金属镜腿。
- 右前镜腿做局部加厚 compute pod，外部高度大约 22-24 mm，外部厚度大约 10-11 mm。
- 左前镜腿略薄，外部高度大约 18-20 mm，外部厚度大约 8.5-9.5 mm。
- 两侧后端电池 pod 可以逐渐变薄，但内部要保留 70 x 12.8 x 5.6 mm 电池最大包络和膨胀/泡棉余量。
- RF antenna 区需要塑胶窗口，不能被电池、铜皮、螺丝、speaker 磁体或高电流 boost 环路压住。

## 部件放置

| 位置 | 放置部件 | 避免事项 |
|---|---|---|
| 前框 / brow | U14 IMX415 custom camera module、MK1-MK4 T5837 mic footprints、U18/U19 MIPI ESD、J3 front FPC | 不放 RK3576、电池、高温 regulator |
| 右镜腿前端 | U1 RK3576、U3 LPDDR4X、U2 RK806S、U4 eMMC、Y1 24 MHz crystal、U6 TPS61088、L1、U11 FCU760KAAMD、U20/U21 audio electronics | 电池不能叠在 RK3576/PMIC/boost 上；Wi-Fi antenna 下方不能铺铜或放电池 |
| 右镜腿后端 | BT1 LP451165、LS1 speaker/acoustic slot、J7 Wi-Fi antenna keep-out、J1 pogo、J5 RF debug connector | speaker 磁体不能进入天线 keep-out；电池膨胀不能挤压 FPC |
| 左镜腿前端 | U7 nRF54L15、U8 nPM1300、U9 NDP120、U10 BMI270、RS1、可选保护/current-sense | 不放 RK3576 高电流 boost 环路 |
| 左镜腿后端 | BT2 LP451165、J6 BLE antenna keep-out、pogo/charge/service、RT1/RT2 NTC/test pads | BLE antenna 下方不要有电池、铜皮、螺丝或磁体 |

## PCB 是否要叠起来

不要做 board-on-board 叠板来硬塞体积。推荐做“分区刚性板 + FPC/线缆连接”：

- 右 compute PCB：一块双面贴装 8-10 layer HDI rigid board。RK3576 和 LPDDR4X 同面邻近放置；PMIC/eMMC/load switch 可以按高度放到另一面。
- 左 AON PCB：先按 4 layer rigid board；如果 RF、噪声、电流检测或地分割需要，再升到 6 layer。
- 前框 sensor board / FPC：如果 MIPI CSI 留在前框，按 4 layer controlled-impedance rigid-flex。
- 电池不能叠在 RK3576、RK806S、TPS61088、boost inductor 或 Wi-Fi/BLE antenna keep-out 上。
- 如果真实 CAD 长度不够，优先把 PCB 分成多个 rigid island 加 FPC，而不是把热源叠到电池上。

## 模块连接关系

| 连接 | 承载内容 | 当前 schematic 对应 |
|---|---|---|
| BT1/BT2 -> AON power path | 1S2P 电池、branch fuse、branch shunt、NTC | BT1/BT2 -> F1/F2 -> RS2/RS3 -> BAT_P -> RS1 -> U8 nPM1300/NPM_VBAT |
| 左 AON -> 右 compute | VSYS/BAT_P、AON UART、SOC/Wi-Fi/camera/audio enable、PGOOD/status、GND | J4/C039 hinge/interconnect placeholder；EVT-A 可做 fixed-temple FPC/cable |
| nPM1300 -> AON loads | AON_1V8、AON_3V3、AON_LSW2、I2C | U8 -> U7/U9/U10/current-sense |
| 右 compute power | VSYS -> SOC_IN -> SOC_5V -> RK806 rails | RS4、U6 TPS61088、U2 RK806S、U1/U3/U4 |
| 前框 camera -> 右 compute | MIPI CSI、CAM I2C、CAM MCLK/RST/PWDN、CAM_1V1/CAM_1V8/CAM_2V9、GND | J3/C038；U14/U15/U16/U17/U18/U19 -> U1 |
| 前框 audio -> AON/compute | wake mic PDM、array PDM、I2S speaker path | MK1 -> U9；MK2/MK3 -> U1；U20 -> LS1 |
| RF | Wi-Fi/BLE antenna feed 和 EVT debug coax | U11 -> J7/J5；U7 -> J6/J5；最终 antenna SKU/tune 仍是 G14 |

## 给 CAD 组的直接口径

请先做一版不布线的 Mechanical/Electrical Floorplan，只放板框和关键 3D 包络：

- 右镜腿：RK3576、LPDDR4X、RK806S、eMMC、TPS61088、boost inductor、FCU760KAAMD、BT1、LS1、Wi-Fi antenna keep-out、pogo、J3/J4 FPC corridor。
- 左镜腿：nRF54L15、nPM1300、NDP120、BMI270、BT2、BLE antenna keep-out、pogo、J4 interconnect corridor。
- 前框：IMX415 custom camera module、T5837 mic footprints、MIPI ESD、J3 FPC。

先不要 routing。只有证明上述尺寸和 keep-out 都能共存，才进入正式 PCB placement/routing。

## 渲染图输出

- SVG: `v2_chipdown/reports/output/AI_Glasses_V2_Phase1_5_Floorplan.svg`
- PNG: `v2_chipdown/reports/output/AI_Glasses_V2_Phase1_5_Floorplan.png`
- PDF: `v2_chipdown/reports/output/AI_Glasses_V2_Phase1_5_Floorplan.pdf`

## 当前 schematic 一致性

- SoC：U1 / C001 / RK3576。
- Wi-Fi：U11 / C015 / FCU760KAAMD。
- IMU：U10 / C012 / BMI270。
- Speaker：LS1 / C025 / 8 ohm 0.5-1 W speaker。
- Battery：BT1/BT2 / LP451165 300 mAh；机械最大包络使用 70 x 12.8 x 5.6 mm。
