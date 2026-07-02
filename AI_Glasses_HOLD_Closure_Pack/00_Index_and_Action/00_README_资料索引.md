# AI 运动眼镜 HOLD 关闭资料包

版本：2026-07-01

本资料包围绕六项尚未冻结的设计风险整理：NDP120、FCU760K Wi-Fi、LP451165、1S2P 电池包、IMX415 相机功耗、电池仓机械装配。

## 结论先行

| 模块 | 已拿到的资料 | 当前结论 | 还缺什么才能关闭 HOLD |
|---|---|---|---|
| NDP120 | Syntiant NDP120 Product Brief | 可以开始架构评估，但不能据此直接画量产原理图 | 完整 Datasheet、Hardware Integration Guide、SDK/TDK、参考原理图、EVK、授权模型与实测功耗 |
| Wi-Fi 模块 | Radxa CM4 原理图确认 FCU760K；Quectel Short Spec | 模块硬件接口已识别，BSP 驱动尚未验证 | Quectel Linux driver/firmware、RK3576 BSP 编译与真机验证 |
| LP451165 | 供应商网页公开参数：3.7 V、300 mAh、4.5 x 11 x 65 mm、无 NTC | 只能作为机械候选，不能作为已冻结电芯 | 带版本日期的正式 PDF、放电曲线、DCIR、倍率、循环与膨胀数据、认证 |
| 1S2P Pack | nPM1300 评估/燃料计资料；BQ2970 单节保护资料 | 可以建立测试方法，但具体 Pack 仍未冻结 | 供应商出具 1S2P Pack Spec、配对规则、支路保护、双 NTC、样品测试 |
| IMX415 电流 | Sony 完整 Datasheet；FRAMOS 模组资料参考 | Sensor 本体典型约 0.582 W；高温最坏角约 0.774 W | 最终镜头/FPC/时钟/稳压器组成的定制模组实测 |
| 电池仓尺寸 | Shell Brief；LP451165 名义尺寸；本包内假电芯 STL | 净宽可行但裕量很小，14 mm 外宽不能凭名义尺寸直接冻结 | 正式机械图、厚度公差/膨胀值、真实样品、FPC/线束/卡扣联合装配 |

## 文件夹说明

- `01_NDP120/`：NDP120 产品资料与获取/测功耗计划。
- `02_WiFi_FCU760K/`：FCU760K 规格及 RK3576 BSP 验证计划。
- `03_Battery_LP451165_1S2P/`：电芯供应商索资清单、1S2P 资格验证规范、nPM1300 与保护资料。
- `04_IMX415/`：Sony Sensor Datasheet、模组参考资料与功耗预算。
- `05_Project_References/`：RK3576、Radxa CM4、外壳尺寸等项目依据。
- `06_Mechanical_Fit_Check/`：电池仓 Fit-check、名义电芯与推荐 clearance envelope 的 STL。

## 关键公开来源

- NDP120 产品页：https://www.syntiant.com/products/chips-and-hardware/ndp120/
- Avnet RASynBoard：https://www.avnet.com/apac/products/rasynboard/
- Quectel FCU760K：https://www.quectel.com/product/wi-fi-bluetooth-fcu760k/
- Quectel FCU760K 下载区：https://www.quectel.com/download-zone/
- LP451165 页面：https://www.lipolbattery.com/Lithium-ion-Polymer-Battery-300mAh-for-Wearable-Camera.html
- Sony IMX415 Flyer：https://www.sony-semicon.com/files/62/pdf/p-12_IMX415-AAQR_AAMR_Flyer.pdf
- Nordic nPM1300：https://www.nordicsemi.com/Products/nPM1300

## 使用原则

1. 公开网页与 Product Brief 只能用于候选筛选，不等同于量产冻结资料。
2. 所有电池参数必须以供应商签字/盖章或可追溯版本的 Pack Specification 为准。
3. 所有功耗必须在实际负载波形和最低电池电压下测量。
4. 所有 BSP 结论必须保留 kernel、DTS、firmware、driver commit、测试日志和复现步骤。
5. 机械冻结必须使用真实样品或供应商认可的最大包络，而不是名义裸电芯尺寸。
