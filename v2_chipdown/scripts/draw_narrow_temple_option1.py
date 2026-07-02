#!/usr/bin/env python3
"""Draw Phase 1.5 narrow-temple option 1.

This is a placement-envelope sketch, not released CAD or PCB geometry.
Option 1 keeps the RK3576 compute zone locally wide and narrows the rear
battery/RF/speaker zone so the whole temple does not visually read as 20 mm.
"""
from __future__ import annotations

import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/private/tmp/ai_glasses_v2_mplcache")

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import patches


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "v2_chipdown" / "reports" / "output" / "mechanical_options"

COLORS = {
    "outline": "#202020",
    "current": "#f1f3f5",
    "option": "#eef8f2",
    "compute": "#8ecae6",
    "compute_hot": "#48cae4",
    "aon": "#b7e4c7",
    "battery": "#ffe066",
    "speaker": "#f4a261",
    "rf": "#cdb4db",
    "fpc": "#adb5bd",
    "heat": "#ef476f",
    "keep": "#dee2e6",
    "dimension": "#343a40",
}


def add_box(ax, x, y, w, h, label, color, *, hatch=None, alpha=0.95, fontsize=7):
    rect = patches.Rectangle(
        (x, y),
        w,
        h,
        facecolor=color,
        edgecolor=COLORS["outline"],
        linewidth=1.0,
        hatch=hatch,
        alpha=alpha,
    )
    ax.add_patch(rect)
    if label:
        ax.text(x + w / 2, y + h / 2, label, ha="center", va="center", fontsize=fontsize, linespacing=1.05)
    return rect


def add_poly(ax, pts, label, color):
    poly = patches.Polygon(pts, closed=True, facecolor=color, edgecolor=COLORS["outline"], linewidth=1.4)
    ax.add_patch(poly)
    if label:
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        ax.text((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, label, ha="center", va="center", fontsize=8)
    return poly


def add_dim(ax, x0, y0, x1, y1, text, *, fontsize=7):
    ax.annotate(
        "",
        xy=(x1, y1),
        xytext=(x0, y0),
        arrowprops=dict(arrowstyle="<->", lw=0.8, color=COLORS["dimension"]),
    )
    ax.text((x0 + x1) / 2, (y0 + y1) / 2, text, fontsize=fontsize, ha="center", va="bottom")


def setup(ax, title, ylim):
    ax.set_title(title, loc="left", fontsize=12, fontweight="bold")
    ax.set_xlim(-5, 158)
    ax.set_ylim(*ylim)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel("length from hinge / mm", fontsize=8)
    ax.set_ylabel("internal width / mm", fontsize=8)
    ax.grid(True, color="#d9d9d9", linewidth=0.3)
    ax.tick_params(labelsize=7)


def draw_current_right(ax):
    setup(ax, "Current reference: straight right-temple envelope", (-3, 24))
    add_box(ax, 0, 0, 150, 20, "", COLORS["current"])
    ax.text(3, 19.0, "current envelope: 150 x 20 mm internal", fontsize=8, va="top")
    add_box(ax, 0, 0, 8, 20, "FPC", COLORS["fpc"], fontsize=6)
    add_box(ax, 8, 1, 62, 18, "compute PCB\n62 x 18", COLORS["compute"], fontsize=7)
    add_box(ax, 11, 1.4, 22, 17.2, "RK3576\nlocal width driver", COLORS["compute_hot"], fontsize=6)
    add_box(ax, 34, 2, 29, 16.5, "RK806 / LPDDR\n/eMMC / boost", "#bde0fe", fontsize=6)
    add_box(ax, 55, 3.9, 13, 12.2, "FCU760K\n13 x 12.2", "#caf0f8", fontsize=6)
    add_box(ax, 74, 4, 70, 12.8, "LP451165\nmax bay 70 x 12.8", COLORS["battery"], fontsize=7)
    add_box(ax, 108, 0.4, 16, 3, "speaker\nslot", COLORS["speaker"], fontsize=6)
    add_box(ax, 126, 17.1, 22, 2.4, "Wi-Fi ant.\nkeep-out", COLORS["rf"], hatch="//", fontsize=5.5)
    add_dim(ax, 151.4, 0, 151.4, 20, "20 mm")
    add_dim(ax, 0, 21.5, 150, 21.5, "150 mm")


def draw_option1_right(ax):
    setup(ax, "Option 1: local compute pod + narrow rear temple", (-3, 24))
    # Hinge/FPC and front compute pod stay wide; rear zone tapers down.
    pts = [
        (0, 0),
        (0, 20),
        (70, 20),
        (88, 15),
        (150, 15),
        (150, 0),
        (88, 0),
        (70, 0),
    ]
    add_poly(ax, pts, "", COLORS["option"])
    ax.text(3, 19.0, "front local pod: 20 mm only where RK3576 board needs it", fontsize=8, va="top")
    ax.text(90, 14.2, "rear visual width target: 15 mm internal", fontsize=8, va="top")
    add_box(ax, 0, 0, 8, 20, "FPC", COLORS["fpc"], fontsize=6)
    add_box(ax, 8, 1, 62, 18, "compute PCB\n62 x 18\nUNCHANGED", COLORS["compute"], fontsize=7)
    add_box(ax, 11, 1.4, 22, 17.2, "RK3576\ncannot fit\n15 mm", COLORS["compute_hot"], fontsize=6)
    add_box(ax, 34, 2, 29, 16.5, "RK806 / LPDDR\n/eMMC / boost", "#bde0fe", fontsize=6)
    add_box(ax, 55, 3.9, 13, 12.2, "FCU760K", "#caf0f8", fontsize=6)
    add_box(ax, 82, 1.1, 64, 12.8, "LP451165 bay\nuse 64-70 mm length\n12.8 mm max width", COLORS["battery"], fontsize=6.6)
    add_box(ax, 108, 0.3, 14, 2.6, "speaker\nside port", COLORS["speaker"], fontsize=5.7)
    add_box(ax, 126, 12.5, 22, 2.0, "Wi-Fi ant.\nplastic window", COLORS["rf"], hatch="//", fontsize=5.4)
    ax.plot([70, 88], [20, 15], color=COLORS["outline"], linewidth=1.0)
    ax.plot([70, 88], [0, 0], color=COLORS["outline"], linewidth=1.0)
    ax.plot([8, 70], [20.7, 20.7], color=COLORS["heat"], linewidth=2.4)
    ax.text(12, 21.0, "outer-wall heat spreader over compute pod", fontsize=6.4, color=COLORS["heat"], va="bottom")
    add_dim(ax, 151.4, 0, 151.4, 15, "15 mm rear")
    add_dim(ax, 68.5, 0, 68.5, 20, "20 mm pod")
    add_dim(ax, 0, 21.9, 70, 21.9, "wide section ~70 mm")
    add_dim(ax, 88, 16.8, 150, 16.8, "narrow rear ~62 mm")


def draw_left_option(ax):
    setup(ax, "Left temple pairing: AON side can target 15 mm straight", (-3, 20))
    add_box(ax, 0, 0, 145, 15, "", COLORS["option"])
    ax.text(3, 14.2, "left temple option: reduce from 16 mm to 15 mm internal if AON PCB is tightened", fontsize=8, va="top")
    add_box(ax, 0, 0, 8, 15, "FPC", COLORS["fpc"], fontsize=6)
    add_box(ax, 8, 1, 46, 13, "AON/power PCB\n46 x 13 target", COLORS["aon"], fontsize=7)
    add_box(ax, 11, 8, 8, 5.5, "nRF54", "#95d5b2", fontsize=6)
    add_box(ax, 21, 8, 8, 5.5, "nPM", "#95d5b2", fontsize=6)
    add_box(ax, 31, 8, 8, 5.5, "NDP120\nHOLD", "#95d5b2", fontsize=5.4)
    add_box(ax, 60, 1, 70, 12.8, "LP451165 bay\n70 x 12.8 max", COLORS["battery"], fontsize=7)
    add_box(ax, 123, 12.8, 20, 1.7, "BLE ant.\nkeep-out", COLORS["rf"], hatch="//", fontsize=5.2)
    add_dim(ax, 146.2, 0, 146.2, 15, "15 mm")
    add_dim(ax, 0, 16.8, 145, 16.8, "145 mm")


def draw_section(ax):
    ax.set_title("What Option 1 buys and what it does not buy", loc="left", fontsize=12, fontweight="bold")
    ax.axis("off")
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    rows = [
        ("Current right temple", "20 mm internal width along most of temple", "#f1f3f5"),
        ("Option 1 right temple", "20 mm only at compute pod; rear target 15 mm", "#eef8f2"),
        ("Left temple", "15 mm internal target is plausible; needs AON PCB re-pack", "#eef8f2"),
        ("Hard limit", "RK3576 + memory zone is still a 18-20 mm local pod", "#ffe3e3"),
        ("Gate before PCB", "CAD must check taper, shell wall, antenna window, heat path, battery swell", "#fff3bf"),
    ]
    y = 86
    for name, text, color in rows:
        add_box(ax, 4, y - 8, 25, 9, name, color, fontsize=7)
        ax.text(34, y - 3.5, text, fontsize=9, va="center")
        y -= 15
    ax.text(
        4,
        8,
        "This option preserves the current schematic/BOM. It is a mechanical floorplan option only; no KiCad routing release implied.",
        fontsize=8,
        color="#343a40",
    )


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    fig = plt.figure(figsize=(16, 13), dpi=180)
    gs = fig.add_gridspec(4, 1, height_ratios=[1, 1, 0.85, 0.8], hspace=0.48)
    draw_current_right(fig.add_subplot(gs[0, 0]))
    draw_option1_right(fig.add_subplot(gs[1, 0]))
    draw_left_option(fig.add_subplot(gs[2, 0]))
    draw_section(fig.add_subplot(gs[3, 0]))
    fig.suptitle(
        "AI Glasses V2 Narrow Temple Option 1 - local compute pod, slim rear",
        x=0.02,
        y=0.985,
        ha="left",
        fontsize=16,
        fontweight="bold",
    )
    fig.text(
        0.02,
        0.012,
        "Basis: current V2 schematic/BOM: RK3576 chip-down compute remains in right temple; LP451165 one cell per temple; Wi-Fi/BLE antenna keep-outs still HOLD.",
        fontsize=8,
        color="#343a40",
    )
    for ext in ("svg", "png", "pdf"):
        fig.savefig(OUT / f"AI_Glasses_V2_Narrow_Temple_Option1.{ext}", bbox_inches="tight")
    plt.close(fig)
    print(OUT / "AI_Glasses_V2_Narrow_Temple_Option1.png")


if __name__ == "__main__":
    main()
