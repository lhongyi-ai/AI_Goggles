# V2.3 Phase 1 Design Review

Generated: 2026-07-01

结论：当前 schematic 是 ERC-clean 的 pre-layout functional schematic，但机械/PCB layout 仍为 HOLD。现在图里的 IC 画在 PCB 上是允许的：它表示器件贴装在同一块 PCB 上，不是实体重叠；真正不允许的是 3D 包络、courtyard、电池膨胀、speaker cavity、RF keep-out 在同一 Z 高度互相冲突。

| # | 检查项 | 结论 | 原因 | 关闭条件 |
|---|---|---|---|---|
| 1 | 左镜腿为什么缺少 side view | HOLD | 当前 Phase 1.5 图只有左镜腿 top view，没有左侧厚度 stack 和 A-A/B-B 截面；不能证明 AON 板、电池、FPC、泡棉和壳体在 Z 方向合壳。 | 补左镜腿 side view、AON tallest-component 截面、电池截面，并绑定数据库尺寸。 |
| 2 | 右镜腿当前 thickness section 是否完整 | PASS WITH CONDITIONS | 已有右侧厚度 section，表达了电池不在 RK3576/PMIC/boost 下方；但未含真实最大器件高度、焊锡、导热垫、绝缘膜和公差链。 | 用真实 package height、热结构和壳体 CAD 替换目标值。 |
| 3 | nRF54L15/nPM1300/NDP120/BMI270 同在 AON PCB 是否合理 | PASS WITH CONDITIONS | 这四个都是 always-on/low-power domain，放同一 AON/Power PCB 架构合理，能让 nRF 控制主 SoC 电源并保持 BLE/IMU/语音唤醒。 | 必须隔离 nPM charger 热、nRF RF 匹配、NDP audio clock/decoupling、BMI270 机械振动；NDP/nPM 仍 HOLD。 |
| 4 | AON PCB 46 x 14 mm 是否包含完整外围 | HOLD | 当前是 placement envelope，不是证明完整外围已经能放下；nRF 匹配、nPM 电感/电容、NDP 去耦/Flash、连接器、测试点、保护/电流检测都未完成占位核算。 | 做 no-route KiCad floorplan 或 ECAD placement envelope。 |
| 5 | Compute PCB 62 x 18 mm 是否容纳全部右镜腿电路 | HOLD | 矩形能摆下不等于能布线。RK3576/LPDDR/RK806/eMMC/TPS61088/FCU760K/MAX98360A/晶振/去耦/测试点/热结构需要 HDI 逃线、DDR 约束和完整高度验证。 | 8-10 layer HDI 预评审，DDR escape 和热/boost/current loop review。 |
| 6 | RK3576 与 LPDDR 逃线和层数是否现实 | NEEDS SUPPLIER DATA | 只有 RK3576 body 和 LPDDR TBD，缺 ball map、DDR topology、stack-up、via-in-pad/microvia 规则和 length report。 | 获取 RK3576 HDG/ball map、LPDDR MPN/ball map；完成 DDR pre-layout review。 |
| 7 | 是否存在电池叠在 RK3576/PMIC/Boost 上方 | PASS WITH CONDITIONS | 当前 floorplan 把电池纵向错开，右侧 section 明确 no battery under RK3576；这是正确方向。 | 真实 CAD 中必须把电池膨胀包络、泡棉、FPC 和热片加入，任何热源/电池真实重叠为 FAIL。 |
| 8 | Wi-Fi/BLE antenna keep-out 是否冲突 | HOLD | 当前图保留尾部 keep-out，但天线 SKU、keep-out 尺寸、塑胶窗口、螺丝/铜/扬声器磁体位置都未冻结。 | 完成 G14 RF/worn-state tuning；speaker magnet 和 battery clearance 同步审查。 |
| 9 | 左右各一颗电池跨镜腿 1S2P 是否安全 | HOLD | 架构可行但风险最高：需要同批/容量/DCIR/OCV 匹配、支路 fuse、NTC、branch shunt、FPC 电流和单支路断开行为验证。 | 关闭 G07；执行 1S2P safety review 和供应商 pack 资格验证。 |
| 10 | J4 是否能承受峰值和故障电流 | NEEDS SUPPLIER DATA | J4 仍是 custom hinge/interconnect placeholder。pin 数、铜厚、线宽、接触电阻、温升、fault current、bend life 都未冻结。 | 冻结 FPC stack-up/pinout/current rating；高电流建议多 pin 并联并加支路保护。 |

## Immediate Gate Verdict

- Formal PCB placement/routing: **HOLD**.
- Left temple side/section: **missing**.
- Right temple side/section: **partial evidence only**.
- AON same-board architecture: **allowed with conditions**.
- Compute board 62 x 18 mm: **not proven routable**.
- Cross-temple 1S2P and J4 current path: **major system risk**.
