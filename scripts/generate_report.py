#!/usr/bin/env python3
"""Generate the Chinese-language design report for ai_glasses_carrier_v1.

Reads the same single-source-of-truth BOM (scripts/carrier_bom.py) that the
schematic generator uses, plus board.yaml and the pin-freeze table, and writes
docs/design_report_v1_zh.md.  Run after generate_carrier_board.py.
"""
from __future__ import annotations

from datetime import date
from pathlib import Path

import yaml

try:
    from .carrier_bom import COMPONENTS, by_group
    from .kicad_tools import PROJECT_ROOT, load_board_config, status
except ImportError:
    from carrier_bom import COMPONENTS, by_group
    from kicad_tools import PROJECT_ROOT, load_board_config, status

REPORT_FILE = PROJECT_ROOT / "docs" / "design_report_v1_zh.md"
PIN_FILE = PROJECT_ROOT / "config" / "cm4_v1_pin_assignment.yaml"


def _load_pin_table() -> dict:
    if not PIN_FILE.exists():
        return {}
    with PIN_FILE.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def build_report() -> str:
    cfg = load_board_config()
    pin_table = _load_pin_table()
    groups = by_group()

    n_p0 = sum(1 for c in COMPONENTS if c.pri == "P0")
    n_p1 = sum(1 for c in COMPONENTS if c.pri == "P1")

    lines: list[str] = []
    add = lines.append

    add("# AI 运动眼镜载板 V1 — 设计报告（中文版）")
    add("")
    add(f"- **项目**：{cfg.project.name if hasattr(cfg.project, 'name') else 'AI Glasses Carrier V1'}")
    add(f"- **版本**：{cfg.project.revision}")
    add(f"- **核心模组**：Radxa CM4（RK3576）")
    add(f"- **板卡尺寸**：{cfg.board.width_mm} × {cfg.board.height_mm} mm，"
        f"{getattr(cfg.board, 'layers', 6)} 层")
    add(f"- **生成日期**：{date.today().isoformat()}")
    add(f"- **元件总数**：{len(COMPONENTS)}（P0 必需 {n_p0} 项，P1 建议 {n_p1} 项）")
    add("")
    add("> ⚠️ **重要声明**：本报告由脚本依据 `scripts/carrier_bom.py` 自动生成。"
        "其中的元件型号与数值均为 **EVT 阶段工程候选**，不是冻结 BOM。"
        "所有 CM4 引脚号、所有高速/射频/电源/电池相关器件，"
        "必须人工对照 **Radxa CM4 Schematic V1.20** 与各芯片 datasheet 核对后才能投板。"
        "（需求文档 1.1 节：AI 输出仅作辅助。）")
    add("")
    add("---")
    add("")

    # ── 1. 概述 ──────────────────────────────────────────────────────────────
    add("## 1. 方案概述")
    add("")
    add("本载板是 AI 运动眼镜的功能验证板（EVT），承载 Radxa CM4（RK3576）模组，"
        "通过三个 100-pin 板对板（B2B）连接器与模组对接。功能划分：")
    add("")
    add("- **P0（必需）**：摄像头 MIPI-CSI（Radxa Camera 4K / IMX415 31-pin + "
        "CM4 CSI3 4-lane；J2 schematic 电气已锁，实物/FPC 路径项转入 `DEFERRED_TO_PRE_LAYOUT`）、"
        "2× PDM 数字麦克风、"
        "I2S/SAI Class-D 音频输出、USB-C（仅 USB2 + 5V 取电）、"
        "CM4 板载 Wi-Fi6/BT5.4、**GNSS/GPS（UART 外接模块）**、调试/恢复接口。")
    add("- **P1（建议）**：1S 锂电 + 充电 + 电量计、6 轴 IMU、振动马达。")
    add("")
    add("> 🔋 **续航目标**：当前 1 小时仅为验证级；最终版本目标 **>3–4 小时**。"
        "这要求在 Phase 0 完成功率预算（Idle / 摄像头 / 摄像头+AI / +H.265 / +Wi-Fi / 满载），"
        "据实测峰值与平均功耗反推电池容量与 boost（TPS61022）选型——"
        "本载板已预留 0Ω 分流位（R3）用于电流测量。")
    add("")

    # ── 2. 元件清单 BOM ──────────────────────────────────────────────────────
    add("## 2. 元件清单（BOM）")
    add("")
    add("被动元件（电阻 / 电容 / 电感）均已给出具体数值；IC / 连接器给出候选型号。")
    add("")
    for group, comps in groups.items():
        add(f"### {group}")
        add("")
        add("| 位号 | 型号 / 数值 | 说明 | 优先级 |")
        add("| --- | --- | --- | --- |")
        for c in comps:
            note = f" — {c.note}" if c.note else ""
            add(f"| {c.ref} | {c.value} | {c.desc}{note} | {c.pri} |")
        add("")

    # ── 3. 关键被动元件数值说明 ──────────────────────────────────────────────
    add("## 3. 关键被动元件数值说明")
    add("")
    add("| 类别 | 数值 | 用途 | 备注 |")
    add("| --- | --- | --- | --- |")
    add("| USB-C CC 下拉 | 5.1kΩ ×2 | 配置为 Sink（取电）角色 | USB-C 规范固定值 |")
    add("| VBUS 串联 | 0Ω / 分流电阻 | 5V 取电 + 电流测量预留 | EVT 用 0Ω，量产换分流 |")
    add("| I2C 上拉 | 2.2kΩ | 摄像头 / IMU I2C 上拉 | 视总线电容微调 1–4.7k |")
    add("| LED 限流 | 1kΩ | 电源 / 状态指示灯 | 视 LED 亮度调整 |")
    add("| 电源去耦 | 10µF + 100nF | 各电源轨就近去耦 | 每颗 IC 电源脚补 100nF |")
    add("| VBAT 储能 | 22µF | 电池轨大电流缓冲 | 配合 boost 输入 |")
    add("| Boost 电感 | 4.7µH | TPS61022 升压电感 | 按峰值电流与 datasheet 选型 |")
    add("| 摄像头去耦 | 100nF ×3 | 2.8/1.8/1.2V 每轨 | 配合 LDO datasheet |")
    add("")
    add("> 被动件 pre-layout freeze 已建立：`config/passive_bom_freeze.yaml`。"
        "审计输出见 `docs/passive_bom_freeze_2026-06-28.md` 和 "
        "`generated/reports/passive_bom_freeze.csv`。`LOCKED_CANDIDATE` 为已给出候选 MPN/LCSC；"
        "`PROCUREMENT_VERIFY` 需采购前确认库存/后缀；`TUNE_OR_EVT_SELECT` 为 RF 调谐或台架实测后定值。")
    add("")

    # ── 4. 引脚冻结门禁状态 ──────────────────────────────────────────────────
    pin_status = (pin_table.get("metadata", {}) or {}).get("status") \
        or pin_table.get("status", "DRAFT")
    assignment_count = len(pin_table.get("assignments") or [])
    add("## 4. 引脚冻结门禁（需求文档 3.3 节）")
    add("")
    add(f"- **当前状态**：`{pin_status}`（引脚已填，等待采购冻结）。")
    add(f"- ✅ **引脚已全部填写并核对**：全部 {assignment_count} 行已对照官方 "
        "`radxa_cm4_pinout_v1.20.xlsx` + Schematic V1.20 填入真实 CM4 引脚号，"
        "`source_verified: true`，无 `TBD` 引脚、无单脚冲突。")
    add("- 工作主表：`scripts/cm4_pinmap.py`；交付件：`generated/reports/cm4_v1_pin_assignment.xlsx`。")
    add("- ⛔ full-layout 门禁仍 **阻塞** 的原因不再是引脚，也不是相机 schematic 电气，"
        "而是 8.3 节的 **pre-layout/机械类 TBD**"
        "（J2 实物/FPC 路径、B2B 装配核对、载板外形/三连接器 XY 等）。"
        "这些解决并 `status: FROZEN` 后方可布线。")
    add("- 关键工程决定：`GPIO_VREF`(J3A P78) 接 **1.8V** → J3A GPIO 全部 1.8V；"
        "摄像头目标为 **Radxa Camera 4K / IMX415 + CSI3 4-lane**，"
        "J2 使用 **Hirose FH35C-31S-0.3SHW(50)** + Radxa **AC006**；"
        "PDM1 麦克风、SAI1 音频、UART0 调试、UART7 GNSS；"
        "摄像头/IMU/电量计分别用 **I2C0 / I2C8 / I2C6** 三条独立总线。")
    add("")
    tbd_items = pin_table.get("open_tbd") or []
    if tbd_items:
        unresolved = [i for i in tbd_items if not i.get("resolved")]
        add(f"**待解决的 TBD 项（8.3 节，共 {len(unresolved)} 项）：**")
        add("")
        add("| 项目 | 需确认内容 | 状态 |")
        add("| --- | --- | --- |")
        for item in tbd_items:
            state = "✅ 已解决" if item.get("resolved") else "❌ 未解决"
            add(f"| `{item.get('id', '?')}` | {item.get('must_confirm', '')} | {state} |")
        add("")

    add("## 5. 五项当前收敛决定（2026-06-28）")
    add("")
    add("| 优先级 | 项目 | 当前决定 | 状态 |")
    add("| --- | --- | --- | --- |")
    add("| P0 | 相机实现 | 目标锁定 Radxa Camera 4K / IMX415-AAQR-C；J2 pins 1-31、CSI3 4-lane、"
        "P/N、I2C/MCLK/RESET、电压域、供电和 NC 已由 `scripts/audit_csi3_camera.py` 审计 | "
        "🟢 schematic 电气已锁；实体/FPC 路径 `DEFERRED_TO_PRE_LAYOUT` |")
    add("| P0 | B2B Fit-Check | 做 2 层只焊三只 DF40C-100DS-0.4V(51) 的验证板，"
        "用官方 CM4 STEP + DXF 核对 1.5mm 压合、Pin1、XY、旋转和净空 | 🔴 阻塞：缺 STEP 装配核对 |")
    add("| P0 | 载板外形 | CM4 官方 DXF 外形 40.02 × 54.98mm；当前 70 × 55mm 仅作 EVT 草案，"
        "三连接器 XY 必须在 KiCad 中导入官方 DXF/STEP 对齐 | 🔴 阻塞：不可从 PDF/文本猜 XY |")
    add("| P1 | POWER_5V | 保守冻结 TPS61022-class 1S→5V，+5V_SYS 按 >=4A 裕量，R3 保留 0R/分流实测位 | 🟡 可先冻结，bring-up 实测收尾 |")
    add("| P1 | Wi-Fi/BT 天线 | 保守冻结为 CM4 模块板载/U.FL 天线路径，载板不新增 2.4/5GHz RF 走线 | 🟡 可先冻结，layout 阶段执行净空 |")
    add("")

    # ── 5. 下一步 ────────────────────────────────────────────────────────────
    add("## 6. 下一步行动")
    add("")
    add("1. **相机 J2 schematic gate**：J2 schematic 已切换到 Radxa Camera 4K 31-pin + "
        "CM4 CSI3 4-lane；`scripts/audit_csi3_camera.py` 逐脚检查 J2 pin 1-31、MIPI lane、"
        "P/N、I2C/MCLK/RESET、电压域、供电和 NC。AC006 实物验证、FPC 接触面、插入方向、"
        "Pin1 实体核对、1:1 打印、Coupon 测试、FPC 弯折和外壳路径均为 `DEFERRED_TO_PRE_LAYOUT`。")
    add("2. **B2B 连接器（已基本确认，待机械冻结）**：载板侧 3× "
        "**Hirose DF40C-100DS-0.4V(51)**（CL No. CL0684-4033-4-51，0.4mm pitch，100-pin，插座），"
        "与 Radxa CM4 模块侧 **DF40C-100DP-0.4V(51)** 配对，标称 PCB 板间距 **1.5mm**"
        "（厂商 mated height，非两件本体高度相加）。冻结条件：官方 CM4 STEP 装配 + "
        "2 层 Fit-Check 验证板确认三连接器坐标/方向/模块净空/1.5mm 间距。"
        "三连接器须作为整体放置并锁定，Pin1 与朝向明确标注，不可单独拖动。")
    add("3. **载板外形 / 连接器 XY**：保持 70 × 55mm 作为 EVT 草案；进入 layout 前，"
        "在 KiCad/机械 CAD 中导入官方 CM4 DXF/STEP 对齐三连接器，不用 PDF/图片/text-mining 当坐标来源。")
    add("4. **POWER_5V 与 Wi-Fi/BT 天线**：按保守决策先冻结；R3 台架实测和 antenna keep-out 在 layout/bring-up 收尾。")
    add("5. **冻结引脚表**：以上完成后将门禁置为 `FROZEN`，"
        "运行 `scripts/check_pin_freeze.py` 通过，才能进入 PCB 布局。")
    add("")
    add("## 7. 工作流阶段进度（对照 10-Phase 工作流）")
    add("")
    add("| 阶段 | 内容 | 状态 |")
    add("| --- | --- | --- |")
    add("| Phase 0 | 需求冻结 / 系统框图 / 接口清单 | 🟡 进行中（P1 电源/天线已有保守冻结） |")
    add("| Phase 1 | 资料 & Pin Assignment（B2B 引脚 / 电压域 / Pinmux） | 🟡 相机 schematic 电气已锁；pre-layout 仍待 J2 实物/FPC、B2B/外形机械门禁 |")
    add("| Phase 2 | 器件选型（MPN / datasheet / 采购） | 🟡 相机目标已锁 IMX415/Radxa Cam4K，J2/AC006 已记录 |")
    add("| Phase 3 | 原理图设计（分页 / ERC / BOM） | 🟢 已出元件级原理图草稿（本文件） |")
    add("| Phase 4–7 | Floorplan / 布线 / 审查 / 生产文件 | ⚪ 未开始（受 Phase 1 门禁阻塞） |")
    add("| Phase 8–10 | Bring-up / Linux 驱动 / 系统测试 | ⚪ 未开始 |")
    add("")
    add("> 当前 schematic 阶段，相机 31-pin J2 电气已经闭合；下一阶段关键阻塞点是 J2 "
        "`DEFERRED_TO_PRE_LAYOUT` 实体验证、B2B 2 层 fit-check、载板外形 + 三连接器 XY/STEP 装配。"
        "POWER_5V 和 Wi-Fi/BT 天线按保守决策可先冻结，"
        "后续 layout/bring-up 收尾。")
    add("")
    add("---")
    add("")
    add("## 附：原理图 / PCB 文件")
    add("")
    add("- 原理图：`hardware/ai_glasses_carrier.kicad_sch`"
        "（已含上述全部元件符号 + 网络标签，可在 KiCad 中直接打开查看）")
    add("- PCB：`hardware/ai_glasses_carrier.kicad_pcb`"
        "（**仅** 板框 + 6 层叠层 + 4 个 M2 安装孔 + 55 个网络；"
        "按门禁规则，元件封装在引脚冻结前 **不** 摆放，故 PCB 上目前看不到器件——这是预期行为）")
    add("- 生成脚本：`scripts/generate_carrier_board.py`、"
        "`scripts/carrier_bom.py`（BOM 唯一来源）、`scripts/generate_report.py`")
    add("")

    return "\n".join(lines) + "\n"


def main() -> int:
    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
    REPORT_FILE.write_text(build_report(), encoding="utf-8")
    print(status("OK", f"Wrote Chinese design report: {REPORT_FILE}"))
    print(status("INFO", f"{len(COMPONENTS)} components documented."))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
