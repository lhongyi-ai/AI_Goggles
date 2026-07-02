#!/usr/bin/env python3
"""Generate the Chinese current-schematic aligned BOM/power PDF.

The engineering identifiers (MPN, refdes, BOM ID, net names) intentionally stay
in English so they match KiCad and the generated netlist exactly. Narrative,
section titles, status legends, gate notes and power interpretation are in
Chinese.
"""
from __future__ import annotations

from datetime import date
from pathlib import Path
import re
import sys
from xml.sax.saxutils import escape

try:
    import yaml
except ModuleNotFoundError:
    # kidoc's report-generation venv may not include PyYAML, while the main
    # project/system Python does. Add the common local site-packages path only as
    # a read-only fallback; no package installation or environment mutation.
    for candidate in (
        "/opt/anaconda3/lib/python3.12/site-packages",
        "/opt/anaconda3/lib/python3.11/site-packages",
    ):
        if Path(candidate).exists() and candidate not in sys.path:
            sys.path.append(candidate)
    import yaml

ROOT = Path(__file__).resolve().parent.parent
SCRIPT_DIR = ROOT / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

from chipdown_bom import COMPONENTS, all_nets, _validate  # noqa: E402
from generate_current_schematic_report import (  # noqa: E402
    POWER_MODEL,
    BATTERY_MODEL,
    OUT as EN_OUT,
    component_power,
    erc_summary,
    fmt_power,
    fmt_runtime,
    refs_by_board,
    status_counts,
)

MD_OUT = ROOT / "reports" / "AI_Glasses_Chipdown_BOM_V2.3_Current_Schematic_ZH.md"
PDF_OUT = ROOT / "reports" / "output" / "AI_Glasses_Chipdown_BOM_V2.3_Current_Schematic_ZH.pdf"


BOARD_CN = {
    "R-Temple Compute Board": "右镜腿 Compute Board",
    "L-Temple AON/Power Board": "左镜腿 AON/Power Board",
    "Temple Rears (batt/spkr/ant)": "镜腿后端电池/扬声器/天线区",
    "Front Sensor Board": "前框 Sensor Board",
    "EVT Debug Tail": "EVT 调试尾板",
}

STATUS_CN = {
    "Fit": "Fit / 首版贴装",
    "DNP": "DNP / 只留焊盘不贴",
    "HOLD": "HOLD / 候选件但门禁未关闭",
    "TBD": "TBD / 型号或规格待定",
}

STATE_CN = {
    "deep_off": "深度待机(AON only, RK3576 off)",
    "quick_standby": "快速待机(DDR retention / light sleep)",
    "phone_assist": "手机协作识别(blended)",
    "mixed_active": "混合运动使用(blended)",
    "record": "连续 1080p 录像",
    "ai_record": "录像 + 本地 AI Burst",
}


def load_models() -> tuple[dict, dict]:
    return (
        yaml.safe_load(POWER_MODEL.read_text(encoding="utf-8")),
        yaml.safe_load(BATTERY_MODEL.read_text(encoding="utf-8")),
    )


def power_totals(model: dict) -> tuple[list[str], dict[str, str], dict[str, float]]:
    keys = [state["key"] for state in model["states"]]
    labels = {key: STATE_CN.get(key, key) for key in keys}
    totals = {key: sum(sub["mW"][key] for sub in model["subsystems"]) for key in keys}
    return keys, labels, totals


def cn_board(board: str) -> str:
    return BOARD_CN.get(board, board)


def cn_status(status: str) -> str:
    return STATUS_CN.get(status, status)


def cell(text: object) -> str:
    s = "" if text is None else str(text)
    return s.replace("\n", " ").strip()


def pins_text(comp) -> str:
    return ", ".join(f"{pin}->{net}" for pin, net in comp.pins)


def basis_zh(ref: str, basis: str) -> str:
    mapping = {
        "RK3576 project allocation inside compute core row": "RK3576 在计算核心功耗行中的项目预算分摊",
        "RK806S/PMIC rail-management allocation": "RK806S/PMIC 多路 rail 管理损耗分摊",
        "LPDDR4X retention/activity allocation": "LPDDR4X 保持/活动功耗分摊",
        "eMMC standby/write allocation": "eMMC 待机与写入功耗分摊",
        "compute-island boost/load-switch/PMIC loss row": "计算岛 Boost/开关/PMIC 损耗",
        "nRF-class BLE MCU/current-state-machine average": "nRF BLE MCU 与常开状态机平均功耗",
        "nPM1300 AON buck quiescent + regulation loss": "nPM1300 AON Buck 静态与转换损耗",
        "NDP120-class wake-word/listening budget": "NDP120 类唤醒词/监听预算",
        "BMI270 low-power motion budget": "BMI270 低功耗运动检测预算",
        "wake mic always-on share of MEMS mic row": "常开唤醒麦克风分摊",
        "array mic share of MEMS mic row": "阵列麦克风分摊",
        "fuel-gauge/NTC/protection monitor allocation": "电量计/NTC/保护监测分摊",
        "custom 1080p camera module baseline allocation": "当前 1080p camera baseline 分摊",
        "camera 1.1 V buck loss allocation": "Camera 1.1 V Buck 损耗分摊",
        "camera 2.9 V LDO loss allocation": "Camera 2.9 V LDO 损耗分摊",
        "camera 1.8 V load-switch loss allocation": "Camera 1.8 V load switch 损耗分摊",
        "FCU760K on-demand Wi-Fi activity average": "FCU760K 按需 Wi-Fi 活动平均功耗",
        "Wi-Fi buck conversion-loss allocation": "Wi-Fi Buck 转换损耗",
        "MAX98360A small-signal/idle audio allocation": "MAX98360A 小信号/空闲分摊",
        "single speaker acoustic-output average": "单扬声器平均声学输出功耗",
        "0 direct load, DNP, passive, source, or included in owning domain": "0 表示 DNP/被动/电源源头，或已计入所属功耗域",
    }
    return mapping.get(basis, basis)


def summary_zh(comp) -> str:
    """Compact Chinese summary without translating engineering identifiers."""
    status = cn_status(comp.assembly)
    board = cn_board(comp.board)
    if comp.assembly == "DNP":
        return f"{comp.value}，位于{board}，当前为 {status}；第一版不贴装或只作为预留。"
    if comp.assembly == "HOLD":
        return f"{comp.value}，位于{board}，当前为 {status}；必须完成对应 gate 后才能作为 layout/fab 冻结依据。"
    if comp.assembly == "TBD":
        return f"{comp.value}，位于{board}，当前为 {status}；具体 MPN/额定值仍需供应商资料或实测关闭。"
    return f"{comp.value}，位于{board}，当前为 {status}；按当前 schematic 进入 EVT 首版装配。"


def write_markdown() -> tuple[list[str], dict]:
    problems = _validate()
    if problems:
        raise RuntimeError("BOM validation failed: " + "; ".join(problems))

    model, battery = load_models()
    keys, labels, totals = power_totals(model)
    by_board, by_status = status_counts()
    powers = component_power(keys, totals)
    states = model["states"]
    v_batt = model["constants"]["v_batt_nominal_V"]
    dod = model["constants"]["usable_dod"]
    pack = next(p for p in battery["packs"] if p["id"] == battery["recommended"])
    pack_mwh = pack["mAh"] * v_batt * dod

    md: list[str] = []

    def w(line: str = "") -> None:
        md.append(line)

    w("# AI Glasses RK3576 Chip-down BOM V2.3 中文版")
    w("## 与当前 schematic 对齐的 BOM、功耗和 layout gate 报告")
    w("")
    w(f"- 生成日期：{date.today().isoformat()}")
    w("- Source of truth：`v2_chipdown/scripts/chipdown_bom.py` 与 `v2_chipdown/config/power_budget_v2.yaml`")
    w("- Schematic：`v2_chipdown/hardware/ai_glasses_v2_chipdown.kicad_sch`")
    w("- 导出 BOM/netlist/PDF：`v2_chipdown/reports/*`")
    w("- 如果旧 PDF 和本文件冲突，以本文件和当前 schematic 为准。")
    w("- 注意：MPN、refdes、BOM ID、net name 保留英文，避免和 KiCad/schematic 不一致。")
    w("")

    w("## 1. 优先阅读")
    w("")
    w("| 项目 | 当前值 |")
    w("|---|---|")
    w("| schematic 范围 | PCB layout 之前的 functional-block schematic |")
    w(f"| 元件 / 网络 | {len(COMPONENTS)} components / {len(all_nets())} nets |")
    w("| 装配状态 | " + ", ".join(f"{k}={v}" for k, v in sorted(by_status.items())) + " |")
    w("| 板卡分区 | " + ", ".join(f"{cn_board(k)}={v}" for k, v in by_board.items()) + " |")
    w(f"| ERC | {erc_summary()} |")
    w("| PCB layout release | 还没有 release；Gate 0/G00F/G05/G07/G08/G10/G12 仍阻塞 layout |")
    w("| Phase 1.5 | 正式 PCB layout 前必须完成 Mechanical/Electrical Floorplan |")
    w("| 第一版铰链口径 | Chip-down EVT V2.0 不包含铰链电气连接；J4 hinge FPC 已从 schematic source 删除 |")
    w("")
    w("状态定义：Fit=首版贴装；DNP=只留焊盘不贴；HOLD=候选件但门禁未关闭；TBD=型号/规格待定。")
    w("功耗数字是项目预算模型，还不是 EVT bench 实测；后续必须用分域 shunt 数据替换。")
    w("")

    w("## 2. 系统功耗边界")
    w("")
    w("| 工作状态 | 当前负载 (mW) | 目标区间 (mW) | 3.7V 电池电流 | LP451165 x2 1S2P 续航 |")
    w("|---|--:|--:|--:|--:|")
    for state in states:
        key = state["key"]
        target = state.get("target_display") or f"{state['target_mW'][0]}-{state['target_mW'][1]}"
        current_ma = totals[key] / v_batt
        runtime_h = pack_mwh / totals[key]
        w(f"| {labels[key]} | {totals[key]:.0f} | {target} | {current_ma:.0f} mA | {fmt_runtime(runtime_h)} |")
    w("")
    w("推荐电池包：LP451165 x2，1S2P，600 mAh / 2.22 Wh nominal，左右镜腿各一颗。")
    w("当前 baseline 模型：连续 1080p 录像为 1290 mW，AI Burst 为 2065 mW。")
    w("")

    w("## 3. 子系统功耗模型")
    w("")
    w("| 子系统 | 功耗域 | " + " | ".join(labels[key] for key in keys) + " |")
    w("|---|---|" + "|".join(["--:"] * len(keys)) + "|")
    for sub in model["subsystems"]:
        w("| " + sub["name"] + " | " + sub["domain"] + " | " + " | ".join(str(sub["mW"][key]) for key in keys) + " |")
    w("| **TOTAL** | | " + " | ".join(f"**{totals[key]:.0f}**" for key in keys) + " |")
    w("")

    w("## 4. 相对旧 PDF 的修正")
    w("")
    w("- Wi-Fi 模块以当前 schematic 为准：`U11 / C015 = FCU760KAAMD`，状态 HOLD。")
    w("- BQ25895 已作为主充电与 Power Path block 加入；nPM1300 保留为 AON 低功耗 PMIC/gauge/rail manager。")
    w("- J4 hinge FPC 已删除：EVT V2.0 不放 hinge FPC footprint，也不画跨铰链 battery、MIPI、USB 或 audio 线。")
    w("- J3 是建议的 33-pin FH26W camera FPC；IMX415 已按 4-lane 目标画入，但机械模组仍为 HOLD/TBD。")
    w("- Wi-Fi/BLE 共用一根双频 FPC 天线；FCU760K 第二 RF port 仅保留 DNP/test。")
    w("- IMU 以当前 schematic 为准：`U10 / C012 = BMI270`，状态 Fit。")
    w("- 当前 baseline 功耗总表为：22 / 134 / 362 / 450 / 1290 / 2065 mW。")
    w(f"- 当前 BOM 不只是 C001-C045；已经展开为 {len(COMPONENTS)} 个 schematic components。")
    w("- C044 已展开为 RS1-RS9 与 U25-U33；C045/C046 的关键被动件和 default-off 下拉也已显式列出。")
    w("- PCB layout 仍未 release；机械、电池、FPC、RF、camera、AON 功耗等 gate 仍需关闭。")
    w("- 新增 Phase 1.5：在 ERC-clean schematic 和正式 PCB layout 之间，必须先完成机械/电气 floorplan。")
    w("")

    w("## 5. 板卡与机械分区")
    w("")
    w("| 区域 | 当前 schematic 内容 | EVT 说明 |")
    w("|---|---|---|")
    w("| 前框 Sensor Board | IMX415 custom FPC module、3 颗 fitted T5837 mic、第 4 颗 mic DNP、camera rails、MIPI ESD、front FPC | 最终 module pinout/lens/lane count 仍是 G10 HOLD |")
    w("| 右镜腿 Compute Board | RK3576、RK806S、LPDDR4X、eMMC、BQ25895、TPS61088、FCU760K Wi-Fi、Wi-Fi buck/load switch、MAX98360A audio | 热、充电/boost droop gate 仍未关闭 |")
    w("| 左镜腿 AON/Power Board | nRF54L15、nPM1300、NDP120、BMI270、可选保护、main shunt/INA | AON 平均 <=25 mW、上限 <=50 mW 必须实测 |")
    w("| 镜腿后端 | LP451165 x2 pack envelopes、branch fuses/shunts、speaker、shared Wi-Fi/BLE antenna、pogo、DNP RF/debug options | 第一版电气上 fixed-temple；当前 released schematic 不含 hinge FPC/cross-hinge harness |")
    w("| EVT 调试尾板 | USB-C、ESD、CC resistors、SWD/UART pads、power/reset/recovery buttons | 只用于 bring-up；量产可隐藏或移除 |")
    w("")

    w("## 5.5. Phase 1.5 Mechanical/Electrical Floorplan")
    w("")
    w("正式 PCB placement/routing 之前，先做 no-route fit floorplan。这是 CAD + EE 的交付物，不是 routed PCB。")
    w("")
    w("| 必需输出 | 内容 |")
    w("|---|---|")
    w("| 右镜腿俯视/侧视 | usable length/width/height；Compute PCB；RK3576/LPDDR/RK806/eMMC/Wi-Fi/BQ25895/boost-inductor zones；battery；speaker；shared Wi-Fi/BLE antenna keep-out；pogo；front FPC corridor；shell/foam/swell allowance |")
    w("| 左镜腿俯视/侧视 | usable length/width/height；AON/power PCB；nRF/nPM/NDP/BMI270 zones；battery；不单放 BLE antenna；pogo/service clearance；shell/foam/swell allowance |")
    w("| KiCad no-route floorplan | board frames；RK3576、LPDDR、RK806、eMMC、Wi-Fi、boost inductor、FPC connectors、battery 3D/envelope blocks、speaker、antenna keep-outs |")
    w("| Pass/fail decision | 先证明当前 schematic 架构放得下；如果放不下，先改 battery/partition/connectors/DNP/local temple width，不进入 routing |")
    w("")
    w("只有 floorplan 通过后，才允许开始正式 routing。")
    w("")

    w("## 6. 当前 BOM（按板卡）")
    w("")
    for board, comps in refs_by_board().items():
        w(f"### {cn_board(board)}")
        w("")
        w("| Ref | BOM ID | Value | 状态 | Pri | Package / footprint placeholder | 关闭门禁 |")
        w("|---|---|---|:--:|:--:|---|---|")
        for comp in comps:
            w(f"| {comp.ref} | {comp.bom_id} | {comp.value} | {cn_status(comp.assembly)} | {comp.pri} | {comp.footprint or 'TBD'} | {comp.gate or '-'} |")
        w("")

    w("## 7. 逐元件功耗分摊")
    w("")
    w("下表为 battery-side 项目预算 mW，所有行加总必须等于当前 subsystem total。0 表示 DNP、被动件、电源源头，或损耗已计入所属功耗域，并不表示物理上没有寄生损耗。")
    w("")
    w("| Ref | BOM ID | Value | 状态 | " + " | ".join(labels[key] for key in keys) + " | 依据 |")
    w("|---|---|---|:--:|" + "|".join(["--:"] * len(keys)) + "|---|")
    for comp in COMPONENTS:
        row = powers[comp.ref]
        values = " | ".join(fmt_power(row["mW"][key]) for key in keys)
        w(f"| {comp.ref} | {comp.bom_id} | {comp.value} | {cn_status(comp.assembly)} | {values} | {basis_zh(comp.ref, row['basis'])} |")
    w("| **TOTAL** | | | | " + " | ".join(f"**{fmt_power(totals[key])}**" for key in keys) + " | 当前模型总功耗 |")
    w("")

    w("## 8. 电源域与关断策略")
    w("")
    w("| 电源域 | Rail / source | 主要负载 | 默认状态 | 控制者 |")
    w("|---|---|---|---|---|")
    w("| Battery / pack | LP451165 1S2P pack PCM -> F1/F2 -> RS2/RS3 -> BAT_P -> RS1 -> NPM_VBAT | 全系统源头 | live | Pack PCM + BQ25895 charger/power path |")
    w("| AON | AON_1V8, AON_3V3, AON_LSW2 from nPM1300 | nRF54L15, NDP120, BMI270, wake mic, fuel/NTC | normal standby 常开 | nPM1300 / nRF54L15 |")
    w("| RK3576 compute | VSYS -> RS4 -> TPS61088 -> SOC_5V -> RK806S rails | RK3576, LPDDR4X, eMMC | 默认 off | nRF54L15 master + Linux safe-off handshake |")
    w("| Camera | TPS62840 CAM_1V1, TPS22917 CAM_1V8, TLV75529 CAM_2V9 | IMX415 custom FPC module | 默认 off | nRF54L15 / RK3576 |")
    w("| Wi-Fi | VSYS -> RS5 -> TPS62825 -> TPS22917 -> FCU760K | FCU760K and antenna path | 默认 off | nRF54L15 enables buck, switch, module |")
    w("| Audio | VSYS -> RS6 -> TPS22917 -> MAX98360A -> LS1 | 单 8 ohm speaker | 默认 off/muted | nRF54L15 / RK3576 |")
    w("")
    w("R11-R20 为 100k default-off pull-down，保证 firmware 不在场或 reset 时，compute、camera、Wi-Fi、audio 都保持关闭。")
    w("")

    w("## 9. Layout-entry gates")
    w("")
    w("| Gate | 主题 | 当前状态 | 关闭条件 |")
    w("|---|---|:--:|---|")
    w("| G00 | 机械/电池 layout gate | HOLD | 真实电芯 fit、膨胀空间、固定线束/极耳出口、天线 keep-out、电池不叠在 RK3576/PMIC/boost 上 |")
    w("| G00F | Phase 1.5 floorplan | HOLD | 带尺寸的俯视/侧视 floorplan + KiCad no-route placement envelope 证明能放下 |")
    w("| G01 | RK3576 identity + HDG | OPEN | Full datasheet、HDG、ball map、package drawing、reference delta |")
    w("| G02 | LPDDR4X | OPEN | MPN、topology、placement、length report、DDR review |")
    w("| G03 | RK806S PMIC | OPEN | exact MPN、rails、inductors/caps、sequence/timing |")
    w("| G04 | eMMC/boot | OPEN | MPN、bootloader/BSP support、cold boot、power-loss recovery |")
    w("| G05 | Wi-Fi FCU760K | HOLD | Hardware Design、land pattern/3D、antenna SKU、BSP driver/firmware enumeration |")
    w("| G06 | 高功率瞬态 | OPEN | RK3576 boot/AI peak、boost soft-start、1S droop、Wi-Fi/camera/audio peaks |")
    w("| G07 | LP451165 + 1S2P pack | HOLD | 正式 datasheet、放电曲线、IR/cycle/cert、pairing/fusing/NTC/current-share |")
    w("| G08 | AON 功耗 | HOLD | nPM1300 EK config、NDP120 kit、AON <=25 mW avg / <=50 mW ceiling 实测 |")
    w("| G09 | 热/boost droop | OPEN | RK3576 burst thermal path、TPS61088/RK806 droop、UVLO margin |")
    w("| G10 | Camera module | HOLD | final IMX415 module FPC pinout、lens/FOV、lane count、rail current/timing |")
    w("| G11 | Mic/audio topology | OPEN | mic coordinates、ports、wind/AEC/beamforming、NDP120 wake path |")
    w("| G12 | Camera/front FPC interconnect | HOLD | FH26W-33S pinout、contact orientation、impedance、camera module vendor sign-off；铰链电气连接不属于 EVT V2.0 范围 |")
    w("| G13 | Magnetics/passives height | OPEN | inductor Isat/DCR/height、cap derating、wearable Z limits |")
    w("| G14 | RF/worn tune | OPEN | antenna SKU、keep-out、matching in shell and worn condition |")
    w("| G15 | Passive/manufacturing BOM | OPEN | 展开 R/C/L MPN、derating、lifecycle、alternates |")
    w("")

    w("## 10. 详细 schematic cards")
    w("")
    for comp in COMPONENTS:
        w(f"### {comp.ref} / {comp.bom_id} - {comp.value}")
        w("")
        w(f"- 板卡/状态：{cn_board(comp.board)} / {cn_status(comp.assembly)} / {comp.pri}")
        w(f"- Package field：{comp.footprint or 'TBD'}")
        w(f"- 关闭门禁：{comp.gate or '-'}")
        w(f"- 中文摘要：{summary_zh(comp)}")
        w(f"- 原始 source-of-truth 说明：{comp.desc}")
        if comp.note:
            w(f"- 原始 note：{comp.note}")
        w(f"- Schematic nets：{pins_text(comp)}")
        w("")

    w("---")
    w("再生成命令：")
    w("`reports/.venv/bin/python v2_chipdown/scripts/generate_current_schematic_report_zh.py`")
    w("不要手工改 PDF；请修改 schematic master 或 YAML 后重新生成。")

    MD_OUT.write_text("\n".join(md) + "\n", encoding="utf-8")
    return md, {"keys": keys, "totals": totals}


def strip_inline(s: str) -> str:
    s = re.sub(r"`([^`]*)`", r"\1", s)
    s = s.replace("**", "")
    return s


def para(text: str, style):
    from reportlab.platypus import Paragraph

    return Paragraph(escape(strip_inline(text)), style)


def markdown_table_to_data(lines: list[str]) -> list[list[str]]:
    data: list[list[str]] = []
    for i, line in enumerate(lines):
        if i == 1 and re.match(r"^\|?\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)+\|?$", line):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        data.append(cells)
    return data


def col_widths(headers: list[str], page_width: float) -> list[float]:
    n = len(headers)
    joined = " ".join(headers)
    if n >= 11:
        return [34, 48, 130, 58] + [34] * 6 + [page_width - (34 + 48 + 130 + 58 + 34 * 6)]
    if n == 7 and "Package" in joined:
        return [42, 48, 145, 62, 32, 150, page_width - 479]
    if n == 7 and "依据" in joined:
        return [38, 46, 130, 60] + [38] * 6 + [page_width - (38 + 46 + 130 + 60 + 38 * 6)]
    if n == 5:
        return [page_width * 0.22, page_width * 0.18, page_width * 0.18, page_width * 0.18, page_width * 0.24]
    return [page_width / n] * n


def build_pdf(markdown_lines: list[str]) -> None:
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER
    from reportlab.lib.pagesizes import letter, landscape
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import inch
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.platypus import (
        PageBreak,
        Paragraph,
        SimpleDocTemplate,
        Spacer,
        Table,
        TableStyle,
    )

    font_path = Path("/System/Library/Fonts/Supplemental/Arial Unicode.ttf")
    if not font_path.exists():
        font_path = Path("/Library/Fonts/Arial Unicode.ttf")
    pdfmetrics.registerFont(TTFont("CJK", str(font_path)))

    page_size = landscape(letter)
    margin = 0.45 * inch
    doc = SimpleDocTemplate(
        str(PDF_OUT),
        pagesize=page_size,
        leftMargin=margin,
        rightMargin=margin,
        topMargin=margin,
        bottomMargin=margin,
        title="AI Glasses RK3576 Chip-down BOM V2.3 中文版",
        subject="Current schematic-aligned Chinese BOM and power report",
    )
    page_width = page_size[0] - doc.leftMargin - doc.rightMargin

    base = getSampleStyleSheet()
    styles = {
        "Title": ParagraphStyle("TitleCN", parent=base["Title"], fontName="CJK", fontSize=20, leading=25, alignment=TA_CENTER, spaceAfter=12),
        "H2": ParagraphStyle("H2CN", parent=base["Heading2"], fontName="CJK", fontSize=13, leading=17, spaceBefore=12, spaceAfter=6),
        "H3": ParagraphStyle("H3CN", parent=base["Heading3"], fontName="CJK", fontSize=10.5, leading=14, spaceBefore=8, spaceAfter=4),
        "Body": ParagraphStyle("BodyCN", parent=base["BodyText"], fontName="CJK", fontSize=8.8, leading=12.5, spaceAfter=4),
        "Bullet": ParagraphStyle("BulletCN", parent=base["BodyText"], fontName="CJK", fontSize=8.5, leading=12, leftIndent=12, firstLineIndent=-8, spaceAfter=3),
        "Table": ParagraphStyle("TableCN", parent=base["BodyText"], fontName="CJK", fontSize=6.3, leading=8.2),
    }

    story = []
    i = 0
    while i < len(markdown_lines):
        line = markdown_lines[i]
        if not line.strip():
            story.append(Spacer(1, 4))
            i += 1
            continue
        if line.startswith("# "):
            story.append(Paragraph(escape(strip_inline(line[2:])), styles["Title"]))
            i += 1
            continue
        if line.startswith("## "):
            if line.startswith("## 10. "):
                story.append(PageBreak())
            story.append(Paragraph(escape(strip_inline(line[3:])), styles["H2"]))
            i += 1
            continue
        if line.startswith("### "):
            story.append(Paragraph(escape(strip_inline(line[4:])), styles["H3"]))
            i += 1
            continue
        if line.startswith("|"):
            block = []
            while i < len(markdown_lines) and markdown_lines[i].startswith("|"):
                block.append(markdown_lines[i])
                i += 1
            raw_data = markdown_table_to_data(block)
            if not raw_data:
                continue
            data = [[para(c, styles["Table"]) for c in row] for row in raw_data]
            widths = col_widths(raw_data[0], page_width)
            if len(widths) != len(raw_data[0]):
                widths = [page_width / len(raw_data[0])] * len(raw_data[0])
            table = Table(data, colWidths=widths, repeatRows=1, splitByRow=1)
            table.setStyle(TableStyle([
                ("FONTNAME", (0, 0), (-1, -1), "CJK"),
                ("FONTSIZE", (0, 0), (-1, -1), 6.3),
                ("LEADING", (0, 0), (-1, -1), 8),
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e8eef7")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#1f2937")),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#b8c2cc")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 2.5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 2.5),
                ("TOPPADDING", (0, 0), (-1, -1), 2),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
            ]))
            story.append(table)
            story.append(Spacer(1, 6))
            continue
        if line.startswith("- "):
            story.append(Paragraph("• " + escape(strip_inline(line[2:])), styles["Bullet"]))
            i += 1
            continue
        if line.startswith("`") and line.endswith("`"):
            story.append(Paragraph(escape(strip_inline(line)), styles["Body"]))
            i += 1
            continue
        story.append(Paragraph(escape(strip_inline(line)), styles["Body"]))
        i += 1

    PDF_OUT.parent.mkdir(parents=True, exist_ok=True)
    doc.build(story)


def main() -> int:
    md, info = write_markdown()
    build_pdf(md)
    keys = info["keys"]
    totals = info["totals"]
    print(f"wrote {MD_OUT.relative_to(ROOT.parent)}")
    print(f"wrote {PDF_OUT.relative_to(ROOT.parent)}")
    print(f"{len(COMPONENTS)} components, {len(all_nets())} nets")
    print("power totals: " + ", ".join(f"{key}={totals[key]:.0f}mW" for key in keys))
    print(f"english source remains: {EN_OUT.relative_to(ROOT.parent)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
