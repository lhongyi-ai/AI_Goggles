#!/usr/bin/env python3
"""Generate the V2 Phase 1.5 mechanical/electrical floorplan artifacts.

This is an engineering placement-envelope render, not industrial design.
It keeps dimensions tied to the current V2 schematic/BOM source of truth and
records where real CAD/supplier data must still close the gate.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "v2_chipdown" / "reports"
OUT_IMG = OUT / "output"

os.environ.setdefault("MPLCONFIGDIR", "/private/tmp/ai_glasses_v2_mplcache")

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import patches

sys.path.insert(0, str(ROOT / "v2_chipdown" / "scripts"))
from chipdown_bom import COMPONENTS  # noqa: E402


COLORS = {
    "frame": "#f2f2ef",
    "pcb_compute": "#8ecae6",
    "pcb_aon": "#b7e4c7",
    "sensor": "#ffb4a2",
    "battery": "#ffe066",
    "rf": "#cdb4db",
    "speaker": "#f4a261",
    "fpc": "#adb5bd",
    "power": "#90be6d",
    "heat": "#ef476f",
    "keepout": "#dee2e6",
    "outline": "#242424",
}


def comp(ref: str):
    return next(c for c in COMPONENTS if c.ref == ref)


PARTS = {
    "soc": comp("U1"),
    "pmic": comp("U2"),
    "lpddr": comp("U3"),
    "emmc": comp("U4"),
    "wifi": comp("U11"),
    "imu": comp("U10"),
    "bat_r": comp("BT1"),
    "bat_l": comp("BT2"),
    "speaker": comp("LS1"),
    "camera": comp("U14"),
    "ndp": comp("U9"),
    "mcu": comp("U7"),
    "charger": comp("U8"),
}


FIT_LIMITS = {
    "right_usable_length_mm": 150.0,
    "right_front_internal_height_mm": 20.0,
    "right_internal_thickness_mm": 8.5,
    "left_usable_length_mm": 145.0,
    "left_front_internal_height_mm": 16.0,
    "left_internal_thickness_mm": 7.5,
    "battery_max_envelope_mm": (70.0, 12.8, 5.6),
    "front_sensor_envelope_mm": (32.0, 8.0, 5.0),
}


def add_box(ax, x, y, w, h, label, color, *, hatch=None, lw=1.1, alpha=0.92, fontsize=7):
    rect = patches.Rectangle(
        (x, y),
        w,
        h,
        facecolor=color,
        edgecolor=COLORS["outline"],
        linewidth=lw,
        hatch=hatch,
        alpha=alpha,
    )
    ax.add_patch(rect)
    if label:
        ax.text(
            x + w / 2,
            y + h / 2,
            label,
            ha="center",
            va="center",
            fontsize=fontsize,
            color="#111111",
            linespacing=1.05,
        )
    return rect


def add_dim(ax, x0, y0, x1, y1, text, *, fontsize=7):
    ax.annotate(
        "",
        xy=(x1, y1),
        xytext=(x0, y0),
        arrowprops=dict(arrowstyle="<->", lw=0.8, color="#333333"),
    )
    ax.text((x0 + x1) / 2, (y0 + y1) / 2, text, fontsize=fontsize, ha="center", va="bottom")


def style_mm_axis(ax, title):
    ax.set_title(title, loc="left", fontsize=11, fontweight="bold")
    ax.set_aspect("equal", adjustable="box")
    ax.grid(True, linewidth=0.25, color="#d0d0d0")
    ax.tick_params(labelsize=7)


def draw_right_temple(ax):
    style_mm_axis(ax, "Right temple top view - compute + Wi-Fi + battery")
    ax.set_xlim(-3, 153)
    ax.set_ylim(-3, 23)
    ax.set_xlabel("length from hinge / mm", fontsize=8)
    ax.set_ylabel("internal height / mm", fontsize=8)

    add_box(ax, 0, 0, 150, 20, "", COLORS["frame"], lw=1.4, fontsize=8)
    ax.text(2, 19.2, "Right temple internal envelope: 150 x 20 mm top view", fontsize=7.8, va="top")
    add_box(ax, 0, 0, 8, 20, "FPC\n8", COLORS["fpc"], fontsize=6)
    add_box(ax, 8, 1, 62, 18, "Compute PCB\n62 x 18", COLORS["pcb_compute"], fontsize=7)
    add_box(ax, 11, 1.4, 22, 17.2, "U1\nRK3576\n22x17.2", "#48cae4", fontsize=6.2)
    add_box(ax, 34.0, 2.0, 12, 10, "U3\nLPDDR", "#90dbf4", fontsize=6)
    add_box(ax, 47.0, 2.0, 12, 9, "U4\neMMC", "#90dbf4", fontsize=6)
    add_box(ax, 34.0, 12.0, 18, 6.5, "U2 RK806\n+ passives", "#74c0fc", fontsize=5.9)
    add_box(ax, 52.5, 12.0, 10.5, 6.5, "U6/L1\nboost", "#74c0fc", fontsize=5.7)
    add_box(ax, 55.5, 3.9, 13.0, 12.2, "U11\nFCU760K\n13x12.2", "#bde0fe", fontsize=6)
    add_box(ax, 74, 4.0, 70, 12.8, "BT1 LP451165\n70 x 12.8 x 5.6", COLORS["battery"], fontsize=7)
    add_box(ax, 108, 0.4, 16, 3.0, "LS1\nslot", COLORS["speaker"], fontsize=6)
    add_box(ax, 136, 0.8, 9, 3.2, "pogo", COLORS["power"], fontsize=6)
    add_box(ax, 126, 17.1, 22, 2.4, "Wi-Fi ant.\nkeep-out\nG14", COLORS["rf"], hatch="//", fontsize=5.4)
    ax.plot([6, 74, 144], [0.35, 0.35, 0.35], color="#495057", linewidth=2)
    ax.text(78, -2.0, "fixed-temple EVT can use cable/FPC corridor along inner lower edge", fontsize=6.5)
    add_dim(ax, 0, 21.5, 150, 21.5, "required usable length >=150 mm (clean RF no-overlap wants ~160+ mm)")
    add_dim(ax, 151.2, 0, 151.2, 20, ">=20 mm")


def draw_left_temple(ax):
    style_mm_axis(ax, "Left temple top view - AON/power + battery")
    ax.set_xlim(-3, 148)
    ax.set_ylim(-3, 20)
    ax.set_xlabel("length from hinge / mm", fontsize=8)
    ax.set_ylabel("internal height / mm", fontsize=8)

    add_box(ax, 0, 0, 145, 16, "", COLORS["frame"], lw=1.4, fontsize=8)
    ax.text(2, 15.2, "Left temple internal envelope: 145 x 16 mm top view", fontsize=7.8, va="top")
    add_box(ax, 0, 0, 8, 16, "FPC\n8", COLORS["fpc"], fontsize=6)
    add_box(ax, 8, 1, 46, 14, "AON/Power PCB\n46 x 14", COLORS["pcb_aon"], fontsize=7)
    add_box(ax, 11, 8, 8, 6, "nRF54\n6x6", "#95d5b2", fontsize=6)
    add_box(ax, 21, 8, 8, 6, "nPM1300\n5x5", "#95d5b2", fontsize=6)
    add_box(ax, 31, 8, 8, 6, "NDP120\n5x5 HOLD", "#95d5b2", fontsize=5.6)
    add_box(ax, 41, 8, 4.5, 4, "BMI270\n2.5x3", "#95d5b2", fontsize=5.2)
    add_box(ax, 12, 2, 18, 4.5, "shunts/prot.\nINA DNP pads", "#d8f3dc", fontsize=5.8)
    add_box(ax, 60, 1.0, 70, 12.8, "BT2 LP451165\n70 x 12.8 x 5.6", COLORS["battery"], fontsize=7)
    add_box(ax, 122, 14.1, 21, 1.7, "BLE ant.\nkeep-out\nG14", COLORS["rf"], hatch="//", fontsize=5.2)
    add_box(ax, 134, 0.6, 8.5, 3, "pogo", COLORS["power"], fontsize=6)
    ax.plot([6, 60, 130], [0.35, 0.35, 0.35], color="#495057", linewidth=2)
    add_dim(ax, 0, 17.7, 145, 17.7, "required usable length >=145 mm")
    add_dim(ax, 146.2, 0, 146.2, 16, ">=16 mm")


def draw_side_and_stack(ax):
    style_mm_axis(ax, "Right side section - thickness stack, no battery under RK3576")
    ax.set_xlim(-3, 153)
    ax.set_ylim(-0.8, 10.2)
    ax.set_xlabel("length from hinge / mm", fontsize=8)
    ax.set_ylabel("thickness / mm", fontsize=8)

    add_box(ax, 0, 0, 150, 8.5, "", COLORS["frame"], lw=1.4, fontsize=8)
    ax.text(2, 8.1, "Right temple internal thickness target >=8.5 mm", fontsize=7.8, va="top")
    add_box(ax, 8, 5.2, 62, 1.0, "compute PCB", COLORS["pcb_compute"], fontsize=6)
    add_box(ax, 11, 6.2, 22, 1.6, "RK3576\nouter-side heat", "#48cae4", fontsize=5.8)
    add_box(ax, 34, 6.2, 29, 1.6, "DDR/PMIC/eMMC", "#74c0fc", fontsize=5.7)
    add_box(ax, 74, 1.0, 70, 5.6, "battery 5.6 max + foam/swell", COLORS["battery"], fontsize=7)
    add_box(ax, 108, 6.6, 16, 1.7, "speaker port\ninner/ear side", COLORS["speaker"], fontsize=6)
    add_box(ax, 126, 7.1, 22, 1.0, "RF plastic window", COLORS["rf"], hatch="//", fontsize=6)
    ax.plot([8, 70], [8.2, 8.2], color=COLORS["heat"], linewidth=2.4)
    ax.text(15, 8.55, "heat spreader to OUTER wall, not skin side and not battery", fontsize=6.5, color=COLORS["heat"])
    add_dim(ax, 151, 0, 151, 8.5, ">=8.5 mm")


def draw_overall(ax):
    ax.set_title("Overall allocation - current schematic driven placement concept", loc="left", fontsize=11, fontweight="bold")
    ax.set_aspect("auto")
    ax.axis("off")
    ax.set_xlim(-170, 310)
    ax.set_ylim(-45, 72)

    # Front frame and lenses.
    front = patches.FancyBboxPatch((0, 0), 135, 34, boxstyle="round,pad=0.02,rounding_size=8", facecolor=COLORS["frame"], edgecolor=COLORS["outline"], linewidth=1.2)
    ax.add_patch(front)
    ax.add_patch(patches.FancyBboxPatch((8, 5), 52, 24, boxstyle="round,pad=0.02,rounding_size=7", facecolor="#ffffff", edgecolor=COLORS["outline"], linewidth=0.8))
    ax.add_patch(patches.FancyBboxPatch((75, 5), 52, 24, boxstyle="round,pad=0.02,rounding_size=7", facecolor="#ffffff", edgecolor=COLORS["outline"], linewidth=0.8))
    add_box(ax, 54, 30, 28, 7, "front sensor PCB\ncamera + mics\n32x8x5 env.", COLORS["sensor"], fontsize=6)
    for x in (18, 48, 88, 118):
        ax.add_patch(patches.Circle((x, 33), 1.4, facecolor="#222222"))
    ax.text(16, 38, "T5837 mic footprints along brow", fontsize=6.4)

    # Temples as simplified bars.
    add_box(ax, 135, 18, 150, 20, "RIGHT TEMPLE", "#e7f5ff", fontsize=8)
    add_box(ax, -145, 18, 145, 16, "LEFT TEMPLE", "#ebfbee", fontsize=8)
    add_box(ax, 143, 21, 62, 14, "compute", COLORS["pcb_compute"], fontsize=6)
    add_box(ax, 209, 21, 70, 12, "BT1", COLORS["battery"], fontsize=6)
    add_box(ax, 262, 33, 20, 4, "Wi-Fi ant.", COLORS["rf"], hatch="//", fontsize=5.6)
    add_box(ax, -136, 20, 46, 12, "AON/power", COLORS["pcb_aon"], fontsize=6)
    add_box(ax, -84, 20, 70, 12, "BT2", COLORS["battery"], fontsize=6)
    add_box(ax, -30, 31, 20, 3.5, "BLE ant.", COLORS["rf"], hatch="//", fontsize=5.6)

    # Interconnect arrows.
    ax.annotate("J3 front FPC: MIPI CSI, camera rails, PDM/I2C/GND", xy=(132, 33), xytext=(92, 58), arrowprops=dict(arrowstyle="->", lw=0.9), fontsize=7)
    ax.annotate("J4 L<->R interconnect: BAT_P/VSYS, AON UART, EN/PGOOD, GND", xy=(0, 22), xytext=(-50, -28), arrowprops=dict(arrowstyle="->", lw=0.9), fontsize=7)
    ax.annotate("1S2P cells: one LP451165 per temple", xy=(210, 24), xytext=(154, -28), arrowprops=dict(arrowstyle="->", lw=0.9), fontsize=7)


def draw_render():
    OUT_IMG.mkdir(parents=True, exist_ok=True)
    fig = plt.figure(figsize=(17.0, 14.0), dpi=180)
    gs = fig.add_gridspec(4, 1, height_ratios=[0.95, 0.9, 0.78, 0.7], hspace=0.45)
    ax0 = fig.add_subplot(gs[0, 0])
    ax1 = fig.add_subplot(gs[1, 0])
    ax2 = fig.add_subplot(gs[2, 0])
    ax3 = fig.add_subplot(gs[3, 0])

    draw_overall(ax0)
    draw_right_temple(ax1)
    draw_left_temple(ax2)
    draw_side_and_stack(ax3)

    fig.suptitle(
        "AI Glasses V2 Phase 1.5 Floorplan Render - placement envelopes in mm",
        x=0.02,
        y=0.985,
        ha="left",
        fontsize=15,
        fontweight="bold",
    )
    fig.text(
        0.02,
        0.012,
        "Schematic source: v2_chipdown/scripts/chipdown_bom.py. This is a conditional fit concept; official CAD, antenna, speaker, camera, battery, and package drawings still close G00/G00F/G07/G10/G12/G14.",
        fontsize=8,
        color="#333333",
    )
    svg = OUT_IMG / "AI_Glasses_V2_Phase1_5_Floorplan.svg"
    png = OUT_IMG / "AI_Glasses_V2_Phase1_5_Floorplan.png"
    pdf = OUT_IMG / "AI_Glasses_V2_Phase1_5_Floorplan.pdf"
    fig.savefig(svg, bbox_inches="tight")
    fig.savefig(png, bbox_inches="tight")
    fig.savefig(pdf, bbox_inches="tight")
    plt.close(fig)
    return svg, png, pdf


def write_report(render_paths: tuple[Path, Path, Path]):
    OUT.mkdir(parents=True, exist_ok=True)
    svg, png, pdf = render_paths
    report = OUT / "AI_Glasses_V2_Phase1_5_Floorplan.md"
    lines = [
        "# AI Glasses V2 Phase 1.5 Floorplan Fit Check",
        "",
        "This report is generated from the current V2 schematic/BOM source of truth. It answers the mechanical placement question before formal PCB routing.",
        "",
        "## Verdict",
        "",
        "- A normal thin optical frame does **not** fit this V2 RK3576 chip-down architecture.",
        "- A thick smart-glasses / sport-sunglasses frame can **conditionally fit** the current schematic if the frame provides the envelope below.",
        "- The fit is not released for PCB layout yet: G00/G00F/G07/G10/G12/G14 remain open or HOLD until real CAD, battery, RF, FPC, speaker, camera, and package drawings are verified.",
        "- Any real 3D envelope, component courtyard, battery swell zone, speaker cavity, or RF antenna keep-out overlap is a **fail**, unless CAD/EE explicitly proves it is a different Z-height feature with clearance, isolation, and thermal/RF sign-off.",
        "",
        "## Minimum frame envelope for the current schematic",
        "",
        "| Region | Minimum internal envelope | Why |",
        "|---|---:|---|",
        "| Right temple usable length | >=150 mm, with ~160+ mm preferred for a clean antenna/battery separation | RK3576 board + 70 mm cell + speaker/pogo + Wi-Fi antenna keep-out |",
        "| Right front compute pod | >=72 x 20 x 8.5 mm | 62 x 18 mm compute PCB plus FPC strain relief and thermal stack |",
        "| Right rear battery/RF/acoustic pod | >=78 x 16 x 8.5 mm | LP451165 max envelope 70 x 12.8 x 5.6 mm plus foam/swell, LS1 acoustic slot, pogo, RF window |",
        "| Left temple usable length | >=145 mm | AON board + 70 mm cell + BLE keep-out + pogo |",
        "| Left front AON pod | >=54 x 16 x 7.5 mm | 46 x 14 mm AON/power PCB plus FPC and shell clearance |",
        "| Left rear battery/RF pod | >=82 x 16 x 7.5 mm | LP451165 max envelope plus BLE antenna region and service/charge area |",
        "| Front sensor brow | >=32 x 8 x 5 mm | Custom IMX415 module, camera power, ESD, mic footprints and FPC exit |",
        "",
        "## Frame style that can fit",
        "",
        "Use a thick acetate/plastic smart-glasses frame, closer to Rokid/Xiaomi-style electronics temples than a normal thin prescription frame. The right temple needs a tall front compute pod, roughly 22-24 mm external vertical height and 10-11 mm external thickness after shell walls. The rear battery pods can taper but should still keep roughly 17-18 mm external vertical height and 8.5-9.5 mm external thickness.",
        "",
        "A fixed-temple EVT frame is acceptable. Do not force a production folding hinge for EVT-A; keep the FPC/interconnect corridor and reserve bend/strain space for a later hinge version.",
        "",
        "## Placement",
        "",
        "| Location | Place here | Do not place here |",
        "|---|---|---|",
        "| Front brow / frame | U14 IMX415 custom module, MK1-MK4 mic footprints, camera ESD, J3 front FPC | RK3576, battery, hot regulators |",
        "| Right temple front | U1 RK3576, U3 LPDDR4X, U2 RK806S, U4 eMMC, Y1 crystal, U6 TPS61088, L1, U11 FCU760K, U20/U21 audio electronics | Battery directly above/below RK3576/PMIC; antenna under copper or battery |",
        "| Right temple rear | BT1 LP451165, LS1 speaker/acoustic slot, J7 Wi-Fi antenna keep-out/window, J1 pogo, J5 RF debug connector if EVT needs it | Speaker magnet inside antenna keep-out; battery swelling into FPC |",
        "| Left temple front | U7 nRF54L15, U8 nPM1300, U9 NDP120, U10 BMI270, RS1, protection/current-sense options | High-current RK3576 boost loops |",
        "| Left temple rear | BT2 LP451165, J6 BLE antenna keep-out/window, pogo/charge/service contacts, NTC/test pads | Battery/copper directly under BLE radiator |",
        "",
        "## PCB stack recommendation",
        "",
        "- Right compute PCB: one double-sided 8-10 layer HDI rigid island, not a board-on-board stack. Use the outer wall for RK3576 heat spreading.",
        "- LPDDR4X must stay adjacent to RK3576; eMMC/PMIC/load switches can use the opposite side if height clears.",
        "- Do not stack the battery over RK3576, RK806S, TPS61088, or the boost inductor.",
        "- Left AON PCB: 4-layer rigid board is the starting point; use 6 layers only if RF/current-sense/noise review needs it.",
        "- Front sensor board/FPC: 4-layer controlled-impedance rigid-flex for MIPI if the final camera module keeps CSI in the front frame.",
        "- If the real CAD envelope is shorter than the table above, split into multiple rigid islands joined by FPC before routing instead of stacking hot boards over the battery.",
        "",
        "## Interconnect map",
        "",
        "| Link | Carries | Current schematic refs / nets |",
        "|---|---|---|",
        "| BT1/BT2 -> AON power path | 1S2P battery power, fuses, shunts, NTC | BT1/BT2 -> F1/F2 -> RS2/RS3 -> BAT_P -> RS1 -> U8 nPM1300/NPM_VBAT |",
        "| Left AON -> right compute | VSYS/BAT_P distribution, AON UART, SOC/Wi-Fi/camera/audio enables, PGOOD/status, GND | J4/C039 hinge/interconnect placeholder; can be fixed-temple FPC/cable in EVT |",
        "| nPM1300 -> AON loads | AON_1V8, AON_3V3, AON load-switch rail, I2C | U8 to U7/U9/U10 and current-sense options |",
        "| Right compute power | VSYS -> SOC_IN -> SOC_5V -> RK806 rails | RS4, U6 TPS61088, U2 RK806S, U1/U3/U4 |",
        "| Front camera -> right compute | MIPI CSI, CAM I2C, CAM MCLK/RST/PWDN, CAM_1V1/CAM_1V8/CAM_2V9, GND | J3/C038; U14/U15/U16/U17/U18/U19 to U1 |",
        "| Front audio -> AON/compute | wake mic PDM to NDP120, array PDM to RK3576, I2S to amp | MK1 -> U9; MK2/MK3 -> U1; U20 -> LS1 |",
        "| RF | Wi-Fi/BLE antenna feeds and debug coax | U11 -> J7/J5, U7 -> J6/J5; final antenna SKU/tune remains G14 |",
        "",
        "## Render artifacts",
        "",
        f"- SVG: `{svg.relative_to(ROOT)}`",
        f"- PNG: `{png.relative_to(ROOT)}`",
        f"- PDF: `{pdf.relative_to(ROOT)}`",
        "",
        "## Open gates before PCB layout",
        "",
        "- G00/G00F: real CAD top/side envelope and no-route KiCad placement pass.",
        "- G07: LP451165 datasheet, discharge curve, swelling, tabs, NTC, fusing, pairing/current-share proof.",
        "- G10: custom IMX415 module dimensions, lens stack height, FPC pinout and rail current.",
        "- G12: fixed-temple interconnect or folding hinge FPC pin count, impedance, bend radius and strain relief.",
        "- G14: Wi-Fi/BLE antenna SKU, keep-out, matching, worn-state tuning and SAR/thermal interaction.",
        "- Speaker/acoustic: final LS1 MPN, cavity size, magnet keep-out and leakage path.",
        "",
        "## Source-of-truth sanity",
        "",
        f"- Current SoC: {PARTS['soc'].ref} / {PARTS['soc'].bom_id} / {PARTS['soc'].value} / {PARTS['soc'].footprint}.",
        f"- Current Wi-Fi: {PARTS['wifi'].ref} / {PARTS['wifi'].bom_id} / {PARTS['wifi'].value}.",
        f"- Current IMU: {PARTS['imu'].ref} / {PARTS['imu'].bom_id} / {PARTS['imu'].value}.",
        f"- Current speaker: {PARTS['speaker'].ref} / {PARTS['speaker'].bom_id} / {PARTS['speaker'].value}.",
        f"- Current battery: {PARTS['bat_r'].value} and {PARTS['bat_l'].value}; mechanical max envelope uses 70 x 12.8 x 5.6 mm, not nominal pouch size.",
        "",
    ]
    report.write_text("\n".join(lines), encoding="utf-8")
    return report


def main():
    paths = draw_render()
    report = write_report(paths)
    print(f"wrote {report.relative_to(ROOT)}")
    for path in paths:
        print(f"wrote {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
