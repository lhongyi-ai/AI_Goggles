#!/usr/bin/env python3
"""Draw a readable complete placement atlas for narrow-temple option 1.

The drawing uses zone IDs plus an inventory table so every current hardware
item is represented without forcing 96+ reference designators into tiny boxes.
It is a Phase 1.5 mechanical/electrical floorplan, not released CAD/PCB.
"""
from __future__ import annotations

import os
import sys
import textwrap
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/private/tmp/ai_glasses_v2_mplcache")

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import patches


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "v2_chipdown" / "reports" / "output" / "mechanical_options"
sys.path.insert(0, str(ROOT / "v2_chipdown" / "scripts"))
from chipdown_bom import COMPONENTS  # noqa: E402


COLORS = {
    "outline": "#202020",
    "shell": "#eef8f2",
    "shell_current": "#f1f3f5",
    "compute": "#8ecae6",
    "compute_hot": "#48cae4",
    "aon": "#b7e4c7",
    "battery": "#ffe066",
    "audio": "#f4a261",
    "rf": "#cdb4db",
    "fpc": "#adb5bd",
    "front": "#f5f5f0",
    "camera": "#ffb4a2",
    "debug": "#dee2e6",
    "power": "#90be6d",
    "heat": "#ef476f",
    "table": "#ffffff",
    "warn": "#fff3bf",
    "bad": "#ffe3e3",
}


def refs_for_board(board: str) -> list[str]:
    return [c.ref + ("*" if c.assembly == "DNP" else "") for c in COMPONENTS if c.board == board]


BOARD_REFS = {
    "R_ALL": refs_for_board("R-Temple Compute Board"),
    "L_ALL": refs_for_board("L-Temple AON/Power Board"),
    "REAR_ALL": refs_for_board("Temple Rears (batt/spkr/ant)"),
    "F_ALL": refs_for_board("Front Sensor Board") + ["CAM_FPC", "CAM_LENS"],
    "D_ALL": refs_for_board("EVT Debug Tail"),
}


ZONES = [
    ("R01", "Right compute SoC/memory/power PCB", "U1 U2 U3 U4 U5 U6 U11 U12 U13 U20 U21 U28 U29 U30 L1 L2 C1 RT3 Y1 R9-R12 R16-R20 RS4-RS6"),
    ("R02", "Right rear battery/power safety", "BT1 F1 RS3 RT1 TP2 U27 plus BAT/VSYS corridor"),
    ("R03", "Right audio/acoustic", "LS1 LS2* U20 U21 RS6 U30 R19 R20. Speaker slot shown as side-wall feature, not battery overlap."),
    ("R04", "Right RF / service / interconnect", "J7 Wi-Fi antenna, J5 RF debug, J1 pogo, J4 L-R/FPC, antenna keep-out"),
    ("L01", "Left AON/power PCB", "U7 U8 U9 U10 U22 U23* U25* Q1* C2 R3 R4 R21-R23 RS1"),
    ("L02", "Left rear battery/power safety", "BT2 F2 RS2 RT2 TP2 U26 plus shared BAT/VSYS corridor"),
    ("L03", "Left BLE/RF/haptic", "J6 BLE antenna, M1 haptic motor, matching/keep-out"),
    ("F01", "Front sensor board", "U14 U15 U16 U17 U18 U19 U31 U32 U33 L3 R5 R6 R13-R15 RS7-RS9 J3"),
    ("F02", "Front camera/lens stack", "U14 CAM_LENS CAM_FPC; total Z is HOLD until module drawing"),
    ("F03", "Microphones", "MK1 MK2 MK3 MK4"),
    ("D01", "EVT debug tail", "J2 U24 R1 R2 TP1 SW1 SW2 SW3; lab/bring-up only"),
]


def add_box(ax, x, y, w, h, label, color, *, hatch=None, alpha=0.96, fontsize=7, lw=1.0, ls="-"):
    rect = patches.Rectangle(
        (x, y),
        w,
        h,
        facecolor=color,
        edgecolor=COLORS["outline"],
        linewidth=lw,
        linestyle=ls,
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
            fontweight="bold",
            linespacing=1.05,
        )
    return rect


def add_poly(ax, pts, color):
    poly = patches.Polygon(pts, closed=True, facecolor=color, edgecolor=COLORS["outline"], linewidth=1.4)
    ax.add_patch(poly)
    return poly


def add_dim(ax, x0, y0, x1, y1, text, *, fontsize=7):
    ax.annotate(
        "",
        xy=(x1, y1),
        xytext=(x0, y0),
        arrowprops=dict(arrowstyle="<->", lw=0.8, color="#343a40"),
    )
    ax.text((x0 + x1) / 2, (y0 + y1) / 2, text, fontsize=fontsize, ha="center", va="bottom")


def setup_temple_axis(ax, title, ylim):
    ax.set_title(title, loc="left", fontsize=13, fontweight="bold")
    ax.set_xlim(-4, 156)
    ax.set_ylim(*ylim)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel("length from hinge / mm", fontsize=8)
    ax.set_ylabel("internal width / mm", fontsize=8)
    ax.grid(True, color="#d9d9d9", linewidth=0.3)
    ax.tick_params(labelsize=7)


def draw_right_option(ax):
    setup_temple_axis(ax, "Right temple option 1: 20 mm compute pod, 15 mm rear", (-3, 24))
    shell = [(0, 0), (0, 20), (70, 20), (88, 15), (150, 15), (150, 0), (88, 0), (70, 0)]
    add_poly(ax, shell, COLORS["shell"])
    add_box(ax, 0, 0, 8, 20, "J4\nFPC", COLORS["fpc"], fontsize=6)
    add_box(ax, 8, 1, 62, 18, "R01", COLORS["compute"], fontsize=13)
    add_box(ax, 11, 1.5, 22, 17.0, "U1", COLORS["compute_hot"], fontsize=10)
    add_box(ax, 35, 2.2, 12, 7, "U3", "#bde0fe", fontsize=8)
    add_box(ax, 48, 2.2, 10, 7, "U4", "#bde0fe", fontsize=8)
    add_box(ax, 35, 10.4, 18, 7.4, "U2", "#bde0fe", fontsize=8)
    add_box(ax, 55, 10.4, 10, 7.4, "U6/L1", "#bde0fe", fontsize=7)
    add_box(ax, 55.5, 2.4, 13, 7.2, "U11", "#caf0f8", fontsize=8)
    add_box(ax, 82, 1.0, 64, 12.8, "R02\nBT1 bay", COLORS["battery"], fontsize=9)
    add_box(ax, 108, -1.8, 16, 1.6, "R03\nspeaker slot", COLORS["audio"], fontsize=6, lw=1.0, ls="--")
    add_box(ax, 124, 14.1, 23, 0.75, "R04 Wi-Fi window", COLORS["rf"], hatch="//", fontsize=5.7)
    add_box(ax, 141.2, 0.5, 7.5, 3.1, "J1", COLORS["power"], fontsize=7)
    add_box(ax, 133.5, 0.5, 6.2, 3.1, "J5", COLORS["debug"], fontsize=7)
    ax.plot([8, 70], [20.6, 20.6], color=COLORS["heat"], linewidth=2.5)
    ax.text(10, 21.0, "heat spreader over compute pod", fontsize=6.8, color=COLORS["heat"], va="bottom")
    add_dim(ax, 0, 22.0, 70, 22.0, "wide section approx 70 mm")
    add_dim(ax, 88, 17.1, 150, 17.1, "narrow rear approx 62 mm")
    add_dim(ax, 69, 0, 69, 20, "20 mm pod")
    add_dim(ax, 151.5, 0, 151.5, 15, "15 mm rear")
    ax.text(
        2,
        -2.5,
        "No solid overlap intended: ICs sit on R01 PCB; R03 is a side-wall acoustic slot; R04 is plastic/RF keep-out above copper/battery.",
        fontsize=6.8,
        color="#343a40",
    )


def draw_left_option(ax):
    setup_temple_axis(ax, "Left temple option 1: 15 mm AON/battery temple", (-3, 20))
    add_box(ax, 0, 0, 145, 15, "", COLORS["shell"])
    add_box(ax, 0, 0, 8, 15, "J4\nFPC", COLORS["fpc"], fontsize=6)
    add_box(ax, 8, 1, 46, 13, "L01", COLORS["aon"], fontsize=13)
    add_box(ax, 11, 8, 8, 5.4, "U7", "#95d5b2", fontsize=7)
    add_box(ax, 21, 8, 8, 5.4, "U8", "#95d5b2", fontsize=7)
    add_box(ax, 31, 8, 8, 5.4, "U9", "#95d5b2", fontsize=7)
    add_box(ax, 40.5, 8, 5.5, 5.4, "U10", "#95d5b2", fontsize=6)
    add_box(ax, 60, 1.0, 70, 12.8, "L02\nBT2 bay", COLORS["battery"], fontsize=9)
    add_box(ax, 123, 14.1, 20, 0.75, "L03 BLE window", COLORS["rf"], hatch="//", fontsize=5.7)
    add_box(ax, 50.5, 1.2, 5.5, 3.0, "M1", COLORS["audio"], fontsize=6)
    add_box(ax, 137, 0.5, 6.5, 3.1, "J1", COLORS["power"], fontsize=7)
    add_dim(ax, 0, 16.8, 145, 16.8, "145 mm")
    add_dim(ax, 146.5, 0, 146.5, 15, "15 mm")
    ax.text(
        2,
        -2.5,
        "Left side can target 15 mm only if AON PCB, BLE antenna, haptic, pogo and battery tab exits are co-designed in CAD.",
        fontsize=6.8,
        color="#343a40",
    )


def draw_front_render(ax):
    ax.set_title("Front frame render: sensor board, camera, mics, FPC", loc="left", fontsize=13, fontweight="bold")
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlim(-12, 158)
    ax.set_ylim(-22, 60)
    ax.axis("off")
    frame = patches.FancyBboxPatch(
        (0, 0),
        140,
        42,
        boxstyle="round,pad=0.0,rounding_size=10",
        facecolor=COLORS["front"],
        edgecolor=COLORS["outline"],
        linewidth=1.5,
    )
    ax.add_patch(frame)
    for x in (14, 80):
        lens = patches.FancyBboxPatch(
            (x, 7),
            45,
            28,
            boxstyle="round,pad=0.0,rounding_size=9",
            facecolor="#ffffff",
            edgecolor=COLORS["outline"],
            linewidth=1.2,
        )
        ax.add_patch(lens)
    add_box(ax, 49, 35, 42, 8, "F01", COLORS["camera"], fontsize=9)
    add_box(ax, 59, 45, 22, 10, "F02", "#ffcad4", fontsize=9)
    mic_positions = [(18, 39), (44, 39), (96, 39), (122, 39)]
    for i, (x, y) in enumerate(mic_positions, start=1):
        ax.add_patch(patches.Circle((x, y), 1.8, facecolor="#222222", edgecolor="#000000"))
        ax.text(x, y + 4.2, f"MK{i}", ha="center", va="center", fontsize=6)
    ax.text(5, 50, "F03 microphones", fontsize=7)
    add_box(ax, 61, -8, 18, 4, "F04", COLORS["fpc"], fontsize=8)
    ax.annotate(
        "",
        xy=(70, -6),
        xytext=(90, -16),
        arrowprops=dict(arrowstyle="->", lw=0.8),
    )
    add_box(ax, 145, 6, 10, 30, "D01\nEVT\nTail", COLORS["debug"], fontsize=7)
    ax.text(7, -18, "Front Z stack remains HOLD until module/lens/FPC/mounting drawings are approved.", fontsize=7)


def write_table(ax, title, rows, *, x=0.0, y=1.0, line_h=0.055, fontsize=7.5):
    ax.text(x, y, title, fontsize=12, fontweight="bold", va="top")
    y -= line_h * 0.95
    for code, name, refs in rows:
        wrapped = textwrap.wrap(f"{code}  {name}: {refs}", width=88)
        for j, line in enumerate(wrapped):
            ax.text(x, y, line, fontsize=fontsize, va="top", family="monospace" if j == 0 else None)
            y -= line_h * 0.62
        y -= line_h * 0.25
    return y


def draw_inventory(ax):
    ax.set_title("Complete hardware inventory represented by zones", loc="left", fontsize=13, fontweight="bold")
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    write_table(ax, "Zone inventory (* = DNP in current schematic/BOM)", ZONES, y=0.98, line_h=0.058, fontsize=6.7)
    ax.text(
        0.0,
        0.03,
        "Full per-board reference list is exported as AI_Glasses_V2_Narrow_Temple_Option1_Inventory.*",
        fontsize=7,
        color="#343a40",
    )


def draw_inventory_sheet() -> None:
    fig = plt.figure(figsize=(18, 11), dpi=180)
    ax = fig.add_subplot(111)
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.text(0.02, 0.97, "AI Glasses V2 Option 1 - complete hardware reference inventory", fontsize=17, fontweight="bold", va="top")
    ax.text(0.02, 0.93, "* = DNP in current schematic/BOM. CAM_FPC and CAM_LENS are virtual mechanical items from the hardware table.", fontsize=8, va="top")

    columns = [
        ("R-Temple Compute Board", BOARD_REFS["R_ALL"]),
        ("L-Temple AON/Power Board", BOARD_REFS["L_ALL"]),
        ("Temple Rears", BOARD_REFS["REAR_ALL"]),
        ("Front Sensor Board", BOARD_REFS["F_ALL"]),
        ("EVT Debug Tail", BOARD_REFS["D_ALL"]),
    ]
    x_positions = [0.02, 0.36, 0.68, 0.02, 0.52]
    y_positions = [0.86, 0.86, 0.86, 0.43, 0.43]
    widths = [42, 40, 38, 58, 38]
    for (title, refs), x, y, width in zip(columns, x_positions, y_positions, widths):
        ax.text(x, y, f"{title} ({len(refs)})", fontsize=11, fontweight="bold", va="top")
        y -= 0.035
        wrapped = textwrap.wrap(", ".join(refs), width=width)
        for line in wrapped:
            ax.text(x, y, line, fontsize=8.2, family="monospace", va="top")
            y -= 0.025

    ax.text(
        0.02,
        0.06,
        "Completeness rule: every current schematic/BOM hardware reference appears in one of these five board/region groups; front CAM_FPC/CAM_LENS are mechanical placeholders, not schematic parts.",
        fontsize=8,
        color="#343a40",
    )
    for ext in ("svg", "png", "pdf"):
        fig.savefig(OUT / f"AI_Glasses_V2_Narrow_Temple_Option1_Inventory.{ext}", bbox_inches="tight")
    plt.close(fig)


def draw_overlap_notes(ax):
    ax.set_title("Overlap rule for this drawing", loc="left", fontsize=13, fontweight="bold")
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    notes = [
        ("OK", "A small IC rectangle inside a PCB rectangle means the IC is mounted on that PCB. This is expected."),
        ("OK", "A keep-out or heat-spreader line can cross an envelope if it marks a wall/plastic/copper restriction, not a solid object."),
        ("NOT OK", "Battery solid overlapping RK3576/PMIC/boost/speaker magnet in the same Z layer would be a real mechanical conflict."),
        ("NOT OK", "Antenna keep-out overlapping copper, battery metal pouch, speaker magnet, screws, or ground return needs CAD/RF correction."),
        ("HOLD", "Speaker cavity, battery tabs, FPC bend radius, connector mating heights and exact package heights still require supplier drawings."),
    ]
    y = 0.86
    for label, text in notes:
        color = COLORS["aon"] if label == "OK" else COLORS["bad"] if label == "NOT OK" else COLORS["warn"]
        add_box(ax, 0.02, y - 0.055, 0.16, 0.06, label, color, fontsize=7)
        ax.text(0.22, y - 0.025, text, fontsize=8, va="center")
        y -= 0.15


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    fig = plt.figure(figsize=(24, 17), dpi=180)
    gs = fig.add_gridspec(
        3,
        2,
        width_ratios=[1.62, 1.0],
        height_ratios=[1.0, 0.88, 0.95],
        wspace=0.18,
        hspace=0.42,
    )
    draw_right_option(fig.add_subplot(gs[0, 0]))
    draw_left_option(fig.add_subplot(gs[1, 0]))
    draw_front_render(fig.add_subplot(gs[2, 0]))
    draw_inventory(fig.add_subplot(gs[0:2, 1]))
    draw_overlap_notes(fig.add_subplot(gs[2, 1]))
    fig.suptitle(
        "AI Glasses V2 Narrow Temple Option 1 - complete readable placement atlas",
        x=0.015,
        y=0.992,
        ha="left",
        fontsize=18,
        fontweight="bold",
    )
    fig.text(
        0.015,
        0.012,
        "Basis: current v2_chipdown schematic/BOM + hardware mechanical database. This is a Phase 1.5 placement envelope; routing/fab release stays HOLD.",
        fontsize=8,
        color="#343a40",
    )
    fig.subplots_adjust(top=0.94, bottom=0.045, left=0.035, right=0.985)
    for ext in ("svg", "png", "pdf"):
        fig.savefig(OUT / f"AI_Glasses_V2_Narrow_Temple_Option1_Complete.{ext}", bbox_inches="tight")
    plt.close(fig)
    draw_inventory_sheet()
    print(OUT / "AI_Glasses_V2_Narrow_Temple_Option1_Complete.png")


if __name__ == "__main__":
    main()
