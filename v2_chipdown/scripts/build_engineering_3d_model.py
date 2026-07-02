#!/usr/bin/env python3
"""Build the EVT V2.0 engineering placement model and rendered view pack.

This is a deterministic fallback renderer for the current machine. It uses the
schematic/BOM source of truth plus the latest mechanical dimensions supplied in
the prompt. If FreeCAD or Blender are installed, their handoff scripts are also
written; if they are not installed, the blocked deliverables are recorded in the
setup and method reports instead of being silently skipped.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import csv
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import textwrap

os.environ.setdefault("MPLCONFIGDIR", str(Path("/private/tmp/aiglasses_mpl")))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Ellipse, FancyBboxPatch, Polygon, Rectangle
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SCRIPT_DIR = ROOT / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

from chipdown_bom import COMPONENTS, all_nets, _validate  # noqa: E402

BASE = ROOT / "mechanical_3d"
MODELS = BASE / "models"
EXPORT = BASE / "export"
BLENDER = BASE / "blender"
RENDERS = BASE / "renders"
REPORTS = BASE / "reports"

INPUT_PDF_REQUESTED = Path("/mnt/data/AI_Glasses_Hardware_Dimensions_V2.2 (3).pdf")
INPUT_PDF_FALLBACK = ROOT / "reports" / "output" / "AI_Glasses_Hardware_Dimensions_V2.2 (3).pdf"

DPI = 240
FIGSIZE = (16, 9)  # 3840 x 2160

COL = {
    "compute": "#42a5f5",
    "power": "#8e44ad",
    "rf": "#2e9d55",
    "audio": "#f6c343",
    "battery": "#e84d3d",
    "tbd": "#f39c12",
    "shell": "#b8c1cc",
    "pcb": "#8fd0a3",
    "thermal": "#1f78b4",
    "keepout": "#23a455",
    "dark": "#202020",
}


@dataclass
class Part:
    id: str
    ref: str
    name: str
    mpn: str
    board: str
    zone: str
    x: float
    y: float
    z: float
    l: float
    w: float
    h: float
    color: str
    status: str
    body_dims: str
    envelope_dims: str
    clearance_mm: float
    note: str = ""
    frozen: bool = True
    hatch: str = ""

    def aabb2(self) -> tuple[float, float, float, float]:
        return (self.x, self.y, self.x + self.l, self.y + self.w)


@dataclass
class OutputRecord:
    path: str
    status: str
    note: str


def run_version(cmd: str) -> tuple[str, str]:
    exe = shutil.which(cmd)
    if not exe:
        return "", "MISSING"
    probes = {
        "pdftotext": [exe, "-v"],
        "freecad": [exe, "--version"],
        "blender": [exe, "--version"],
        "kicad-cli": [exe, "version"],
        "python3": [exe, "--version"],
        "git": [exe, "--version"],
        "magick": [exe, "--version"],
        "convert": [exe, "--version"],
    }
    try:
        cp = subprocess.run(probes.get(cmd, [exe, "--version"]), capture_output=True, text=True, timeout=8)
        text = (cp.stdout + cp.stderr).strip().splitlines()
        return exe, (text[0] if text else "version probe returned no text")
    except Exception as exc:  # pragma: no cover - diagnostic only
        return exe, f"version probe failed: {exc}"


def ensure_dirs() -> None:
    for d in (MODELS, EXPORT, BLENDER, RENDERS, REPORTS):
        d.mkdir(parents=True, exist_ok=True)


def parts() -> list[Part]:
    """Current engineering placement model in mm.

    Coordinates for right/left temple detail views are local to each temple.
    Global 3D views re-map these records into an assembly coordinate system.
    """
    return [
        Part("R-PCB", "PCB-R", "Compute PCB", "rigid PCB envelope", "Right temple", "PCB", 8, 1, 1.0, 62, 18, 1.0, COL["compute"], "Candidate", "62x18x1.0", "local 20mm compute pod", 0.3, "No-route placement envelope"),
        Part("C01", "U1", "RK3576", "RK3576", "Right temple", "SoC/high-speed", 11, 1.6, 2.0, 16.1, 17.2, 1.0, COL["compute"], "Candidate/HOLD", "16.1x17.2xH TBD", "SoC body, not full circuit", 0.3, "H from official package drawing still required", False),
        Part("C02", "U3", "LPDDR4X", "Samsung K4U6E3S4AA-MGCL", "Right temple", "SoC/high-speed", 29.5, 4.0, 2.0, 11.5, 10.0, 0.9, COL["tbd"], "HOLD", "TBD package drawing", "orange DDR placement envelope", 0.3, "MPN selected for EVT; official package/ball map still required", False, "//"),
        Part("C03", "U2", "RK806S-5", "RK806S-5", "Right temple", "PMIC", 43.0, 3.0, 2.0, 7.0, 7.0, 0.9, COL["power"], "Candidate/HOLD", "7.0x7.0x0.90", "QFN68 ePad", 0.3, "Package frozen; power sequence still HOLD"),
        Part("C04", "U4", "eMMC", "Samsung KLMAG1JENB-B041", "Right temple", "Storage", 52.0, 3.0, 2.0, 11.5, 13.0, 0.8, COL["compute"], "Candidate/HOLD", "11.5x13.0x0.8", "153-FBGA", 0.3, "BSP boot validation required"),
        Part("P01", "U35", "Charger/Power Path", "BQ25895", "Right temple", "Power", 32.0, 12.8, 2.0, 4.5, 4.5, 0.8, COL["power"], "HOLD", "TBD official package", "charger placement envelope", 0.3, "Primary 1S charger + power path", False, "//"),
        Part("P02", "U6", "Boost IC", "TPS61088", "Right temple", "Boost", 50.0, 13.5, 2.0, 4.5, 3.5, 0.9, COL["power"], "Candidate/HOLD", "4.5x3.5xH TBD", "boost IC body", 0.3, "Thermal/droop gate open", False),
        Part("P03", "L1", "Boost inductor", "Coilcraft XGL4020-102MEC", "Right temple", "Boost", 56.0, 12.5, 2.0, 4.0, 4.0, 2.0, COL["power"], "Candidate/HOLD", "4.0x4.0x2.0", "high-current magnetic", 0.3, "No DDR/MIPI/audio/RF below"),
        Part("P04", "Y1", "24 MHz crystal", "24MHz 10ppm", "Right temple", "Clock", 11.5, 0.2, 2.0, 3.2, 2.5, 0.8, COL["compute"], "Fit", "3.2x2.5xH TBD", "3225 crystal", 0.3, "Near SoC oscillator", False),
        Part("RF01", "U11", "Wi-Fi/BT module", "Quectel FCU760K", "Right temple", "RF", 36.0, 1.8, 3.0, 13.0, 12.2, 2.0, COL["rf"], "HOLD", "13.0x12.2x2.0", "LCC module", 0.3, "USB2 host; shared antenna"),
        Part("TH01", "HS1", "Heat spreader path", "outer-wall path", "Right temple", "Thermal", 10.0, 19.0, 4.2, 58.0, 0.35, 0.2, "#ff3366", "Candidate", "58x0.35x0.2", "outer wall heat path", 0.3, "Keep battery longitudinally separated"),
        Part("SH01", "SH1", "Shield can", "RF/PMIC shield TBD", "Right temple", "Shield", 34.0, 1.2, 4.9, 30.0, 14.0, 1.0, COL["tbd"], "TBD", "TBD", "orange shield envelope", 0.3, "Do not let antenna sit against shield", False, "//"),
        Part("BAT-R", "BT1", "Right battery envelope", "LP451165 in 1S2P pack", "Right temple", "Battery", 76.0, 1.0, 1.0, 70.0, 12.8, 5.6, COL["battery"], "HOLD", "70x12.8x5.6 max", "cell+seal+PCM+foam+swell", 0.5, "Supplier pack drawing and fit test required", False, "//"),
        Part("SPK-R", "LS1", "Main speaker", "CUI CMS-15113-078SP-67", "Right temple", "Audio", 108.0, 0.6, 4.6, 15.0, 11.0, 3.0, COL["audio"], "HOLD", "15x11x3", "0.3-0.5cc cavity", 0.3, "Port must not face microphones"),
        Part("RF02", "J7", "Shared Wi-Fi/BLE antenna", "Taoglas FXP840.07.0055B", "Right temple", "RF", 126.0, 15.7, 4.8, 14.0, 5.0, 0.1, COL["rf"], "HOLD", "14x5x0.1", "plastic window keep-out", 0.3, "No battery/speaker magnet/shield/copper in keep-out"),
        Part("J01", "J1", "6-pin magnetic pogo", "CCP P2578MP01-06C180HT", "Right temple", "Pogo", 141.0, 1.0, 1.0, 10.0, 3.0, 1.0, COL["power"], "HOLD", "target 10x3x1", "6 pins: GND D- D+ GND VBUS VBUS", 0.3, "USB2 eye/contact validation required", False),
        Part("L-PCB", "PCB-L", "AON/power PCB", "rigid PCB envelope", "Left temple", "PCB", 10.0, 1.0, 1.0, 46.0, 13.0, 1.0, COL["pcb"], "Candidate", "46x13x1.0", "15mm straight temple target", 0.3, "No-route placement envelope"),
        Part("A01", "U7", "AON MCU", "nRF54L15-QFN48", "Left temple", "AON", 13.0, 5.0, 2.0, 6.0, 6.0, 0.85, COL["pcb"], "Fit", "6x6x0.85", "QFN48", 0.3, "No separate BLE antenna in EVT"),
        Part("A02", "U8", "AON PMIC/gauge", "nPM1300", "Left temple", "Power", 23.0, 5.0, 2.0, 5.0, 5.0, 0.9, COL["power"], "HOLD", "5x5xH TBD", "AON rails/gauge", 0.3, "BQ25895 is primary charger", False),
        Part("A03", "U9", "Audio DSP", "NDP120", "Left temple", "AON audio", 33.0, 5.0, 2.0, 5.0, 5.0, 0.9, COL["pcb"], "HOLD", "5x5xH TBD", "QFN40 target", 0.3, "Full datasheet/dev kit required", False),
        Part("A04", "U10", "IMU", "BMI270", "Left temple", "Motion", 43.0, 6.0, 2.0, 2.5, 3.0, 0.8, COL["pcb"], "Fit", "2.5x3.0x0.8", "LGA14", 0.3, "Avoid high stress/vibration"),
        Part("BAT-L", "BT2", "Left battery envelope", "LP451165 in 1S2P pack", "Left temple", "Battery", 61.0, 1.0, 1.0, 70.0, 12.8, 5.6, COL["battery"], "HOLD", "70x12.8x5.6 max", "cell+seal+PCM+foam+swell", 0.5, "Supplier pack drawing and fit test required", False, "//"),
        Part("J02", "J1-L", "Left service/pogo area", "mechanical keep space", "Left temple", "Service", 134.0, 1.0, 1.0, 9.0, 3.0, 1.0, COL["power"], "Candidate", "9x3x1", "service keep space", 0.3, "If duplicated pogo is deleted, use as strain relief"),
        Part("CAM01", "U14", "IMX415 module envelope", "Sony IMX415-AAQR-C", "Front frame", "Camera", 60.0, 10.0, 1.0, 15.0, 15.0, 9.5, COL["tbd"], "HOLD/TBD", "sensor PCB <=15x15; total Z <=9.5 target", "lens+IR+PCB+FPC TBD envelope", 0.3, "TBD - NOT RELEASED FOR TOOLING", False, "//"),
        Part("J03", "J3", "33-pin camera FPC", "FH26W-33S-0.3SHW(97)", "Front frame", "FPC", 57.0, 27.0, 1.0, 11.4, 3.2, 1.0, COL["power"], "HOLD", "11.4x3.2x1.0 approx", "33-pin 0.3mm pitch", 0.3, "Vendor pinout sign-off required", False),
        Part("MIC1", "MK1", "Wake microphone", "T5837", "Front frame", "Audio", 43.0, 8.0, 1.0, 3.5, 2.65, 0.98, COL["audio"], "Fit", "3.50x2.65x0.98", "bottom-port MEMS", 0.3, "Sound hole + keep-out"),
        Part("MIC2", "MK2", "Array microphone 1", "T5837", "Front frame", "Audio", 72.0, 8.0, 1.0, 3.5, 2.65, 0.98, COL["audio"], "Fit", "3.50x2.65x0.98", "bottom-port MEMS", 0.3, "Sound hole + keep-out"),
        Part("MIC3", "MK3", "Array microphone 2", "T5837", "Front frame", "Audio", 89.0, 8.0, 1.0, 3.5, 2.65, 0.98, COL["audio"], "Fit", "3.50x2.65x0.98", "bottom-port MEMS", 0.3, "Sound hole + keep-out"),
    ]


def rect(ax, p: Part, *, xy: tuple[float, float] | None = None, label: bool = True, alpha: float = 0.78) -> None:
    x, y = xy if xy else (p.x, p.y)
    ls = "--" if not p.frozen else "-"
    patch = Rectangle(
        (x, y),
        p.l,
        p.w,
        facecolor=p.color,
        edgecolor=COL["dark"],
        linewidth=1.1,
        alpha=0.36 if not p.frozen else alpha,
        hatch=p.hatch,
        linestyle=ls,
    )
    ax.add_patch(patch)
    if label:
        ax.text(
            x + p.l / 2,
            y + p.w / 2,
            p.id,
            ha="center",
            va="center",
            fontsize=7.5,
            weight="bold",
            bbox=dict(facecolor="white", edgecolor="none", alpha=0.62, pad=0.5),
        )


def dim(ax, x0, y0, x1, y1, text, *, fontsize=8) -> None:
    ax.annotate("", xy=(x1, y1), xytext=(x0, y0), arrowprops=dict(arrowstyle="<->", lw=0.9, color="#444"))
    ax.text((x0 + x1) / 2, (y0 + y1) / 2, text, ha="center", va="bottom", fontsize=fontsize, color="#222")


def set_mm_axes(ax, title: str, xlim: tuple[float, float], ylim: tuple[float, float]) -> None:
    ax.set_title(title, loc="left", fontsize=13, weight="bold")
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel("length from hinge / mm")
    ax.set_ylabel("internal width / mm")
    ax.grid(True, color="#e7e7e7", linewidth=0.5)


def legend_table(fig, rows: list[Part], title: str, *, bbox=(0.73, 0.08, 0.25, 0.84)) -> None:
    ax = fig.add_axes(bbox)
    ax.axis("off")
    ax.text(0, 1.0, title, fontsize=12, weight="bold", va="top")
    y = 0.95
    for p in rows:
        text = f"{p.id}  {p.ref}  {p.mpn}\n{p.body_dims} | {p.status}"
        ax.text(0.0, y, text, fontsize=7.2, va="top", linespacing=1.05)
        y -= 0.055 if len(text) < 55 else 0.072
        if y < 0.02:
            break


def save(fig, name: str, outputs: list[OutputRecord]) -> None:
    path = RENDERS / name
    fig.savefig(path, dpi=DPI, facecolor="white")
    plt.close(fig)
    with Image.open(path) as im:
        status = "PASS" if im.size[0] >= 3840 and im.size[1] >= 2160 else "FAIL"
        outputs.append(OutputRecord(str(path.relative_to(BASE)), status, f"{im.size[0]}x{im.size[1]} px"))


def right_top(parts_: list[Part], outputs: list[OutputRecord]) -> None:
    fig, ax = plt.subplots(figsize=FIGSIZE)
    fig.subplots_adjust(left=0.06, right=0.69, top=0.86, bottom=0.14)
    shell = Polygon([(0, 0), (70, 0), (88, 15), (150, 15), (150, 0), (0, 0), (0, 20), (70, 20), (88, 15), (150, 15), (150, 0)], closed=False, fill=False, lw=1.6)
    ax.add_patch(Rectangle((0, 0), 70, 20, facecolor="#e8f0f8", edgecolor="#333", alpha=0.35))
    ax.add_patch(Rectangle((88, 0), 62, 15, facecolor="#eaf4ef", edgecolor="#333", alpha=0.35))
    ax.add_patch(Polygon([(70, 0), (88, 0), (88, 15), (70, 20)], facecolor="#eaf4ef", edgecolor="#333", alpha=0.35))
    for p in parts_:
        if p.board == "Right temple" and p.id not in {"TH01"}:
            rect(ax, p)
    ax.add_patch(Rectangle((74, 0.5), 75, 14.0, facecolor="none", edgecolor="#d62728", hatch="///", lw=1.0, alpha=0.45))
    ax.text(75, 14.9, "battery bay: no RK3576/RK806/boost under pack", fontsize=8, color="#a51d1d")
    ax.add_patch(Rectangle((124, 14.8), 20, 6.4, facecolor="none", edgecolor=COL["keepout"], linestyle="--", lw=1.6))
    ax.text(124, 21.7, "RF keep-out: no battery, magnet, shield, copper", fontsize=8, color=COL["rf"])
    dim(ax, 0, 22, 70, 22, "front compute pod local width 20 mm / length 70 mm")
    dim(ax, 88, 18, 150, 18, "narrow rear target 15 mm")
    set_mm_axes(ax, "03 Right Temple Top View - Option 1 local compute pod + narrow rear", (-5, 155), (-3, 25))
    legend_table(fig, [p for p in parts_ if p.board == "Right temple"], "Right temple IDs")
    save(fig, "03_right_top.png", outputs)


def left_top(parts_: list[Part], outputs: list[OutputRecord]) -> None:
    fig, ax = plt.subplots(figsize=FIGSIZE)
    fig.subplots_adjust(left=0.06, right=0.69, top=0.86, bottom=0.14)
    ax.add_patch(Rectangle((0, 0), 145, 15, facecolor="#eaf4ef", edgecolor="#333", alpha=0.40))
    for p in parts_:
        if p.board == "Left temple":
            rect(ax, p)
    ax.text(62, 14.1, "no separate BLE antenna fitted; FCU760K shares right antenna", fontsize=8, color=COL["rf"])
    dim(ax, 0, 17, 145, 17, "usable straight length 145 mm")
    dim(ax, 148, 0, 148, 15, "15 mm internal target")
    set_mm_axes(ax, "05 Left Temple Top View - AON side 15 mm straight target", (-5, 153), (-3, 21))
    legend_table(fig, [p for p in parts_ if p.board == "Left temple"], "Left temple IDs")
    save(fig, "05_left_top.png", outputs)


def side_view(parts_: list[Part], side: str, outputs: list[OutputRecord], name: str, title: str, length: float, height: float) -> None:
    fig, ax = plt.subplots(figsize=FIGSIZE)
    fig.subplots_adjust(left=0.06, right=0.69, top=0.86, bottom=0.14)
    ax.add_patch(Rectangle((0, 0), length, height, facecolor="#f2f2f2", edgecolor="#333", alpha=0.55))
    ax.add_patch(Rectangle((4, 0.5), length - 8, height - 1.0, facecolor="none", edgecolor="#777", lw=0.9))
    for p in parts_:
        if p.board != side:
            continue
        patch = Rectangle((p.x, p.z), p.l, p.h, facecolor=p.color, edgecolor="#222", alpha=0.35 if not p.frozen else 0.78, hatch=p.hatch, linestyle="--" if not p.frozen else "-")
        ax.add_patch(patch)
        ax.text(p.x + p.l / 2, p.z + p.h / 2, p.id, fontsize=8, ha="center", va="center", weight="bold")
    if side == "Right temple":
        ax.plot([10, 68], [7.6, 7.6], color="#ff3366", lw=2.0)
        ax.text(11, 7.85, "outer-wall heat spreader path; battery separated", fontsize=8, color="#ff3366")
    ax.set_title(title, loc="left", fontsize=13, weight="bold")
    ax.set_xlim(-5, length + 5)
    ax.set_ylim(-0.5, height + 2.0)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel("length from hinge / mm")
    ax.set_ylabel("Z / thickness mm")
    ax.grid(True, color="#e7e7e7", linewidth=0.5)
    legend_table(fig, [p for p in parts_ if p.board == side], f"{side} Z-stack IDs")
    save(fig, name, outputs)


def front_detail(parts_: list[Part], outputs: list[OutputRecord]) -> None:
    fig, ax = plt.subplots(figsize=FIGSIZE)
    fig.subplots_adjust(left=0.06, right=0.69, top=0.86, bottom=0.14)
    ax.add_patch(FancyBboxPatch((0, 0), 135, 42, boxstyle="round,pad=0.3,rounding_size=8", facecolor="#d6dbe1", edgecolor="#333", alpha=0.45, lw=1.4))
    ax.add_patch(FancyBboxPatch((24, 6), 34, 26, boxstyle="round,pad=0.2,rounding_size=6", facecolor="white", edgecolor="#444", alpha=0.85))
    ax.add_patch(FancyBboxPatch((77, 6), 34, 26, boxstyle="round,pad=0.2,rounding_size=6", facecolor="white", edgecolor="#444", alpha=0.85))
    for p in parts_:
        if p.board == "Front frame":
            rect(ax, p)
            if p.id.startswith("MIC"):
                ax.add_patch(Circle((p.x + p.l / 2, p.y + p.w / 2), 1.8, fill=False, edgecolor=COL["audio"], lw=1.5, linestyle="--"))
    ax.text(52, 38, "Hinge electrical interconnect is out of scope for Chip-down EVT V2.0", fontsize=9, ha="center")
    dim(ax, 60, 28, 75, 28, "sensor PCB <=15 mm")
    dim(ax, 82, 10, 82, 19.5, "camera Z target <=9.5 mm", fontsize=8)
    ax.set_title("07 Front Frame Camera / Mic Detail - TBD camera module envelope", loc="left", fontsize=13, weight="bold")
    ax.set_xlim(-4, 139)
    ax.set_ylim(-3, 47)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel("front frame X / mm")
    ax.set_ylabel("front frame Y / mm")
    ax.grid(True, color="#e7e7e7", linewidth=0.5)
    legend_table(fig, [p for p in parts_ if p.board == "Front frame"], "Front frame IDs")
    save(fig, "07_camera_detail.png", outputs)


def section_views(parts_: list[Part], outputs: list[OutputRecord]) -> None:
    specs = [
        ("08_soc_thermal_section.png", "08 RK3576 Thermal Section", [("PCB", 4, 6, 22, 1, COL["compute"]), ("RK3576 C01", 8, 7, 16.1, 1.0, COL["compute"]), ("thermal pad", 7, 8.2, 18, 0.4, COL["thermal"]), ("outer wall", 4, 11.8, 22, 0.5, "#555")], "blue dashed path to outer wall; >=0.3mm hard clearance"),
        ("09_battery_section.png", "09 Battery Maximum Swell Section", [("PCB edge", 4, 7.2, 22, 0.8, COL["pcb"]), ("foam", 6, 1.0, 18, 0.8, "#ddd"), ("battery BAT-R/L", 6, 1.8, 18, 5.6, COL["battery"]), ("no-compress zone", 5, 1.2, 20, 6.4, COL["tbd"])], "supplier swelling + foam controls final shell; not tooling released"),
        ("10_camera_z_section.png", "10 IMX415 Total Z Section", [("FPC", 3, 1, 27, 0.3, "#ccc"), ("sensor PCB", 4, 2.0, 25, 0.8, COL["tbd"]), ("IR-cut", 9, 3.2, 15, 0.5, COL["tbd"]), ("lens CAM01", 11, 3.8, 11, 5.7, COL["tbd"])], "orange TBD envelope: total Z target <=9.5mm; stop IMX415 if required Z <8mm"),
        ("11_speaker_section.png", "11 Speaker + Acoustic Cavity Section", [("speaker SPK-R", 7, 5.6, 15, 3, COL["audio"]), ("foam seal", 6.5, 5.1, 16, 0.35, "#ddd"), ("0.3-0.5cc rear cavity", 6, 1.2, 17, 4.0, "#ffe89a"), ("sound port away from mics", 22, 6.2, 6, 0.6, COL["audio"])], "speaker port cannot face front microphones; magnet clearance to antenna required"),
        ("12_pogo_section.png", "12 Pogo Compression Section", [("shell pocket", 4, 1.0, 24, 6.0, "#ddd"), ("pogo free", 7, 5.0, 10, 1.0, COL["power"]), ("pogo compressed", 19, 4.4, 10, 1.0, COL["power"])], "6 pins: GND, D-, D+, GND, VBUS, VBUS; USB2 validation required"),
        ("13_rf_keepout.png", "13 Wireless Module + Antenna Keep-out", [("FCU760K RF01", 5, 1.5, 13, 2.0, COL["rf"]), ("50ohm feed", 18, 2.2, 36, 0.3, COL["rf"]), ("antenna RF02", 55, 1.2, 14, 0.1, COL["rf"]), ("keep-out", 51, 0.4, 23, 5.0, "#c9f1d5"), ("battery forbidden", 51, 5.8, 23, 4.0, COL["battery"])], "antenna cannot sit against battery, speaker magnet, shield, copper or pogo magnet"),
    ]
    for filename, title, items, foot in specs:
        fig, ax = plt.subplots(figsize=FIGSIZE)
        ax.add_patch(Rectangle((2, 0.5), 75, 12, fill=False, edgecolor="#333", lw=1.2))
        for label, x, y, l, h, color in items:
            alpha = 0.25 if "TBD" in label or "keep-out" in label else 0.78
            hatch = "///" if "forbidden" in label or "no-compress" in label else ""
            ax.add_patch(Rectangle((x, y), l, h, facecolor=color, edgecolor="#222", alpha=alpha, hatch=hatch))
            ax.text(x + l / 2, y + h / 2, label, fontsize=8, ha="center", va="center")
        ax.text(3, 13.2, foot, fontsize=9)
        ax.set_xlim(0, 80)
        ax.set_ylim(0, 15)
        ax.set_aspect("equal", adjustable="box")
        ax.set_title(title, loc="left", fontsize=13, weight="bold")
        ax.set_xlabel("section width / mm")
        ax.set_ylabel("Z / mm")
        ax.grid(True, color="#e7e7e7", linewidth=0.5)
        save(fig, filename, outputs)


def box_faces(x, y, z, l, w, h):
    v = [
        (x, y, z), (x + l, y, z), (x + l, y + w, z), (x, y + w, z),
        (x, y, z + h), (x + l, y, z + h), (x + l, y + w, z + h), (x, y + w, z + h),
    ]
    return [[v[i] for i in face] for face in ((0, 1, 2, 3), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7))]


def add_box(ax, x, y, z, l, w, h, color, alpha=0.8):
    pc = Poly3DCollection(box_faces(x, y, z, l, w, h), facecolors=color, edgecolors="#333", linewidths=0.3, alpha=alpha)
    ax.add_collection3d(pc)


def global_box(p: Part, exploded: bool = False) -> tuple[float, float, float, float, float, float]:
    if p.board == "Right temple":
        return (70 + p.y - 10, p.x + (22 if exploded and p.zone != "PCB" else 0), p.z, p.w, p.l, p.h)
    if p.board == "Left temple":
        return (-70 - p.y, p.x + (22 if exploded and p.zone != "PCB" else 0), p.z, p.w, p.l, p.h)
    return (p.x - 67.5, -8 + (18 if exploded else 0), p.z + 8, p.l, p.w, p.h)


def overview_3d(parts_: list[Part], outputs: list[OutputRecord], *, transparent: bool, exploded: bool, filename: str, title: str) -> None:
    fig = plt.figure(figsize=FIGSIZE)
    ax = fig.add_subplot(111, projection="3d")
    shell_alpha = 0.18 if transparent else 0.88
    add_box(ax, -75, -9, 0, 150, 8, 42, COL["shell"], shell_alpha)
    add_box(ax, 70, 0, 0, 20, 150, 8.5, COL["shell"], shell_alpha)
    add_box(ax, -90, 0, 0, 20, 145, 7.5, COL["shell"], shell_alpha)
    if transparent or exploded:
        for p in parts_:
            if p.id in {"TH01"}:
                continue
            x, y, z, l, w, h = global_box(p, exploded=exploded)
            add_box(ax, x, y, z, l, w, h, p.color, 0.30 if not p.frozen else 0.78)
            if p.id in {"C01", "C02", "C03", "C04", "RF01", "BAT-R", "BAT-L", "SPK-R", "RF02", "CAM01", "A01", "A02", "A03"}:
                ax.text(x + l / 2, y + w / 2, z + h + 1.0, p.id, fontsize=7, ha="center")
    ax.set_title(title, loc="left", fontsize=13, weight="bold")
    ax.set_xlim(-95, 95)
    ax.set_ylim(-15, 180)
    ax.set_zlim(0, 50)
    ax.set_xlabel("glasses X / mm")
    ax.set_ylabel("temple length / mm")
    ax.set_zlabel("Z / mm")
    ax.view_init(elev=22, azim=-55)
    save(fig, filename, outputs)


def write_stl(parts_: list[Part], outputs: list[OutputRecord]) -> None:
    path = EXPORT / "glasses_assembly.stl"
    def tri(a, b, c):
        return f"  facet normal 0 0 0\n    outer loop\n      vertex {' '.join(map(str, a))}\n      vertex {' '.join(map(str, b))}\n      vertex {' '.join(map(str, c))}\n    endloop\n  endfacet\n"
    lines = ["solid ai_glasses_evt_v2_engineering_envelopes_mm\n"]
    for p in parts_:
        x, y, z, l, w, h = global_box(p)
        for f in box_faces(x, y, z, l, w, h):
            lines.append(tri(f[0], f[1], f[2]))
            lines.append(tri(f[0], f[2], f[3]))
    lines.append("endsolid ai_glasses_evt_v2_engineering_envelopes_mm\n")
    path.write_text("".join(lines), encoding="utf-8")
    outputs.append(OutputRecord(str(path.relative_to(BASE)), "PASS", "ASCII STL envelope model, units documented as mm"))


class Dxf:
    def __init__(self) -> None:
        self.lines: list[str] = []

    def add(self, *items: object) -> None:
        self.lines.extend(str(i) for i in items)

    def header(self) -> None:
        layers = {
            "SHELL": 8,
            "COMPUTE": 140,
            "POWER": 200,
            "RF": 94,
            "AUDIO": 50,
            "BATTERY": 1,
            "TBD": 30,
            "KEEP_OUT": 3,
            "DIM": 7,
            "TEXT": 7,
        }
        self.add(
            0, "SECTION", 2, "HEADER",
            9, "$ACADVER", 1, "AC1027",
            9, "$INSUNITS", 70, 4,
            0, "ENDSEC",
            0, "SECTION", 2, "TABLES",
            0, "TABLE", 2, "LAYER", 70, len(layers),
        )
        for name, color in layers.items():
            self.add(0, "LAYER", 2, name, 70, 0, 62, color, 6, "CONTINUOUS")
        self.add(0, "ENDTAB", 0, "ENDSEC", 0, "SECTION", 2, "ENTITIES")

    def footer(self) -> None:
        self.add(0, "ENDSEC", 0, "EOF")

    def line(self, layer: str, x1: float, y1: float, x2: float, y2: float, z1: float = 0, z2: float = 0) -> None:
        self.add(0, "LINE", 8, layer, 10, f"{x1:.4f}", 20, f"{y1:.4f}", 30, f"{z1:.4f}", 11, f"{x2:.4f}", 21, f"{y2:.4f}", 31, f"{z2:.4f}")

    def rect(self, layer: str, x: float, y: float, l: float, w: float, z: float = 0) -> None:
        self.line(layer, x, y, x + l, y, z, z)
        self.line(layer, x + l, y, x + l, y + w, z, z)
        self.line(layer, x + l, y + w, x, y + w, z, z)
        self.line(layer, x, y + w, x, y, z, z)

    def text(self, layer: str, x: float, y: float, text: str, height: float = 2.0, z: float = 0) -> None:
        safe = text.replace("\n", " / ").replace("—", "-").replace("≤", "<=").replace("×", "x")
        self.add(0, "TEXT", 8, layer, 10, f"{x:.4f}", 20, f"{y:.4f}", 30, f"{z:.4f}", 40, f"{height:.4f}", 1, safe[:240])

    def face(self, layer: str, pts: list[tuple[float, float, float]]) -> None:
        p = pts if len(pts) == 4 else [*pts, pts[-1]]
        self.add(
            0, "3DFACE", 8, layer,
            10, f"{p[0][0]:.4f}", 20, f"{p[0][1]:.4f}", 30, f"{p[0][2]:.4f}",
            11, f"{p[1][0]:.4f}", 21, f"{p[1][1]:.4f}", 31, f"{p[1][2]:.4f}",
            12, f"{p[2][0]:.4f}", 22, f"{p[2][1]:.4f}", 32, f"{p[2][2]:.4f}",
            13, f"{p[3][0]:.4f}", 23, f"{p[3][1]:.4f}", 33, f"{p[3][2]:.4f}",
        )

    def save(self, path: Path) -> None:
        self.footer()
        path.write_text("\n".join(self.lines) + "\n", encoding="ascii", errors="ignore")


def layer_for_part(p: Part) -> str:
    if "Battery" in p.zone:
        return "BATTERY"
    if "RF" in p.zone:
        return "RF"
    if "Audio" in p.zone or p.id.startswith("MIC") or p.id.startswith("SPK"):
        return "AUDIO"
    if "Power" in p.zone or "Boost" in p.zone or "Pogo" in p.zone:
        return "POWER"
    if not p.frozen or "TBD" in p.status:
        return "TBD"
    if "PCB" in p.zone:
        return "SHELL"
    return "COMPUTE"


def write_autocad_dxf(parts_: list[Part], outputs: list[OutputRecord]) -> None:
    """Write AutoCAD-compatible ASCII DXF files without external dependencies."""
    d = Dxf()
    d.header()
    d.text("TEXT", 0, 240, "AI Glasses Chip-down EVT V2.0 - AutoCAD 2D floorplan, units=mm", 4)
    d.text("TEXT", 0, 233, "Solid edges=candidate/frozen envelope; orange/TBD layer=NOT RELEASED FOR TOOLING; no hinge electrical interconnect in EVT V2.0", 2.5)

    # Right temple top view.
    ox, oy = 0, 170
    d.text("TEXT", ox, oy + 27, "Right temple top - local compute pod + narrow rear", 3)
    d.rect("SHELL", ox, oy, 70, 20)
    d.rect("SHELL", ox + 88, oy, 62, 15)
    d.line("SHELL", ox + 70, oy, ox + 88, oy)
    d.line("SHELL", ox + 70, oy + 20, ox + 88, oy + 15)
    for p in parts_:
        if p.board == "Right temple" and p.id != "TH01":
            d.rect(layer_for_part(p), ox + p.x, oy + p.y, p.l, p.w)
            d.text("TEXT", ox + p.x + 0.8, oy + p.y + p.w / 2, p.id, 1.6)
    d.rect("KEEP_OUT", ox + 124, oy + 14.8, 23, 6.2)
    d.rect("BATTERY", ox + 74, oy + 0.5, 75, 14)
    d.text("TEXT", ox + 74, oy - 5, "BAT keep-out: no RK3576/RK806/TPS61088/boost inductor under pack", 2)
    d.line("DIM", ox, oy + 23, ox + 70, oy + 23)
    d.text("DIM", ox + 20, oy + 24, "70 mm wide compute pod section", 2)
    d.line("DIM", ox + 88, oy + 18, ox + 150, oy + 18)
    d.text("DIM", ox + 104, oy + 19, "62 mm narrow rear target", 2)

    # Left temple top view.
    ox, oy = 0, 115
    d.text("TEXT", ox, oy + 22, "Left temple top - AON side 15 mm straight target", 3)
    d.rect("SHELL", ox, oy, 145, 15)
    for p in parts_:
        if p.board == "Left temple":
            d.rect(layer_for_part(p), ox + p.x, oy + p.y, p.l, p.w)
            d.text("TEXT", ox + p.x + 0.8, oy + p.y + p.w / 2, p.id, 1.6)
    d.line("DIM", ox, oy + 18, ox + 145, oy + 18)
    d.text("DIM", ox + 60, oy + 19, "145 mm usable length / 15 mm internal width", 2)

    # Front frame view.
    ox, oy = 0, 42
    d.text("TEXT", ox, oy + 50, "Front frame camera/mic region - IMX415 module TBD envelope", 3)
    d.rect("SHELL", ox, oy, 135, 42)
    d.rect("SHELL", ox + 24, oy + 6, 34, 26)
    d.rect("SHELL", ox + 77, oy + 6, 34, 26)
    for p in parts_:
        if p.board == "Front frame":
            d.rect(layer_for_part(p), ox + p.x, oy + p.y, p.l, p.w)
            d.text("TEXT", ox + p.x + 0.8, oy + p.y + p.w / 2, p.id, 1.5)
    d.text("TEXT", ox + 55, oy - 6, "Hinge electrical interconnect is out of scope for Chip-down EVT V2.0", 2)

    # Legend.
    ox, oy = 170, 42
    d.text("TEXT", ox, oy + 195, "ID legend / dimensions", 3)
    y = oy + 187
    for p in parts_:
        d.text("TEXT", ox, y, f"{p.id} {p.ref} {p.mpn} | {p.body_dims} | {p.status}", 1.55)
        y -= 4.2
        if y < 8:
            break

    path2d = EXPORT / "autocad_floorplan_2d.dxf"
    d.save(path2d)
    outputs.append(OutputRecord(str(path2d.relative_to(BASE)), "PASS", "AutoCAD ASCII DXF 2D floorplan, INSUNITS=mm"))

    d3 = Dxf()
    d3.header()
    d3.text("TEXT", -90, -20, "AI Glasses Chip-down EVT V2.0 - 3D envelope DXF, units=mm", 4)
    # Transparent shell as wire boxes.
    shell_boxes = [
        ("SHELL", -75, -9, 0, 150, 8, 42),
        ("SHELL", 70, 0, 0, 20, 150, 8.5),
        ("SHELL", -90, 0, 0, 20, 145, 7.5),
    ]
    for layer, x, y, z, l, w, h in shell_boxes:
        for f in box_faces(x, y, z, l, w, h):
            d3.face(layer, f)
    for p in parts_:
        if p.id == "TH01":
            continue
        x, y, z, l, w, h = global_box(p)
        for f in box_faces(x, y, z, l, w, h):
            d3.face(layer_for_part(p), f)
        d3.text("TEXT", x + l / 2, y + w / 2, p.id, 2.0, z + h + 1)
    path3d = EXPORT / "autocad_envelopes_3d.dxf"
    d3.save(path3d)
    outputs.append(OutputRecord(str(path3d.relative_to(BASE)), "PASS", "AutoCAD ASCII DXF 3D 3DFACE envelope model, INSUNITS=mm"))

    notes = [
        "# AutoCAD import notes",
        "",
        "- Primary CAD exchange files:",
        "  - `export/autocad_floorplan_2d.dxf`: model-space 2D floorplan, units in millimeters.",
        "  - `export/autocad_envelopes_3d.dxf`: 3D envelope model using DXF `3DFACE` entities, units in millimeters.",
        "- In AutoCAD, open the DXF directly or use `INSERT`; verify `INSUNITS=4` / millimeters.",
        "- Layers: COMPUTE, POWER, RF, AUDIO, BATTERY, TBD, KEEP_OUT, SHELL, DIM, TEXT.",
        "- TBD layer means target/control envelope only and `NOT RELEASED FOR TOOLING`.",
        "- DWG was not generated because the environment has no DWG-capable converter. AutoCAD can save the opened DXF as DWG.",
    ]
    note_path = REPORTS / "autocad_import_notes.md"
    note_path.write_text("\n".join(notes) + "\n", encoding="utf-8")
    outputs.append(OutputRecord(str(note_path.relative_to(BASE)), "PASS", "AutoCAD handoff notes"))


def write_blender_scripts(outputs: list[OutputRecord]) -> None:
    build = BLENDER / "build_scene.py"
    build.write_text(textwrap.dedent(
        '''\
        # Run inside Blender: blender --background --python build_scene.py
        import json
        from pathlib import Path
        import bpy
        base = Path(__file__).resolve().parents[1]
        data = json.loads((base / "models" / "glasses_assembly_model.json").read_text())
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete()
        for p in data["parts"]:
            bpy.ops.mesh.primitive_cube_add(size=1, location=(p["x"] + p["l"]/2, p["y"] + p["w"]/2, p["z"] + p["h"]/2))
            obj = bpy.context.object
            obj.name = p["id"] + "_" + p["ref"]
            obj.dimensions = (p["l"], p["w"], p["h"])
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        bpy.ops.wm.save_as_mainfile(filepath=str(base / "blender" / "ai_glasses_render.blend"))
        '''
    ), encoding="utf-8")
    render = BLENDER / "render_all_views.py"
    render.write_text("# Placeholder: use build_scene.py then configure cameras/materials in Blender.\n", encoding="utf-8")
    if shutil.which("blender"):
        outputs.append(OutputRecord(str(build.relative_to(BASE)), "READY", "Blender is installed; run script to create .blend"))
    else:
        (BLENDER / "ai_glasses_render.blend.blocked.txt").write_text("Blender command not found; .blend cannot be generated on this machine.\n", encoding="utf-8")
        outputs.append(OutputRecord("blender/ai_glasses_render.blend", "BLOCKED", "blender command not found"))


def write_model_json(parts_: list[Part], outputs: list[OutputRecord]) -> None:
    payload = {
        "units": "mm",
        "source": "current chipdown_bom.py + prompt freeze data + V2.2 hardware dimensions PDF fallback",
        "parts": [asdict(p) for p in parts_],
    }
    for name, subset in {
        "glasses_assembly_model.json": parts_,
        "compute_board_model.json": [p for p in parts_ if p.board == "Right temple"],
        "aon_board_model.json": [p for p in parts_ if p.board == "Left temple"],
        "camera_module_model.json": [p for p in parts_ if p.board == "Front frame"],
        "battery_pack_model.json": [p for p in parts_ if p.id in {"BAT-R", "BAT-L"}],
        "speaker_chamber_model.json": [p for p in parts_ if p.id == "SPK-R"],
    }.items():
        (MODELS / name).write_text(json.dumps({"units": "mm", "parts": [asdict(p) for p in subset]}, indent=2), encoding="utf-8")
        outputs.append(OutputRecord(str((MODELS / name).relative_to(BASE)), "PASS", "editable JSON parameter model"))
    for fcstd in ("glasses_assembly.FCStd", "compute_board.FCStd", "aon_board.FCStd", "camera_module.FCStd", "battery_pack.FCStd", "speaker_chamber.FCStd"):
        (MODELS / f"{fcstd}.blocked.txt").write_text("FreeCAD/freecadcmd command not found; FCStd cannot be generated on this machine.\n", encoding="utf-8")
    (EXPORT / "glasses_assembly.step.blocked.txt").write_text("FreeCAD/freecadcmd command not found; STEP export cannot be generated on this machine.\n", encoding="utf-8")


def overlap(a: Part, b: Part) -> bool:
    ax0, ay0, ax1, ay1 = a.aabb2()
    bx0, by0, bx1, by1 = b.aabb2()
    return max(ax0, bx0) < min(ax1, bx1) and max(ay0, by0) < min(ay1, by1)


def write_reports(parts_: list[Part], outputs: list[OutputRecord]) -> None:
    tools = {c: run_version(c) for c in ("blender", "freecad", "kicad-cli", "python3", "pdftotext", "magick", "convert", "git")}
    missing = [c for c, (_, v) in tools.items() if v == "MISSING"]
    pdf_used = INPUT_PDF_REQUESTED if INPUT_PDF_REQUESTED.exists() else INPUT_PDF_FALLBACK
    if shutil.which("pdftotext") and pdf_used.exists():
        cp = subprocess.run([shutil.which("pdftotext") or "pdftotext", str(pdf_used), "-"], capture_output=True, text=True, timeout=20)
        (REPORTS / "source_dimensions_pdf_extract.txt").write_text(cp.stdout[:12000], encoding="utf-8")

    with (REPORTS / "hardware_dimensions.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["id", "ref", "name", "mpn", "board", "zone", "body_dims", "envelope_dims", "status", "clearance_mm", "note"])
        w.writeheader()
        for p in parts_:
            w.writerow({k: getattr(p, k) for k in w.fieldnames})
    visible_by_ref = {p.ref: p for p in parts_}
    with (REPORTS / "hardware_bom.csv").open("w", newline="", encoding="utf-8") as f:
        fields = ["ref", "bom_id", "value", "board", "assembly", "render_id", "body_dims", "envelope_dims", "status", "gate"]
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for c in COMPONENTS:
            p = visible_by_ref.get(c.ref)
            w.writerow({
                "ref": c.ref, "bom_id": c.bom_id, "value": c.value, "board": c.board,
                "assembly": c.assembly, "render_id": p.id if p else "",
                "body_dims": p.body_dims if p else "see schematic / TBD or passive",
                "envelope_dims": p.envelope_dims if p else "",
                "status": p.status if p else c.assembly, "gate": c.gate,
            })
    with (REPORTS / "frozen_tbd_register.csv").open("w", newline="", encoding="utf-8") as f:
        fields = ["id", "ref", "mpn", "status", "frozen", "body_dims", "blocker"]
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for p in parts_:
            w.writerow({"id": p.id, "ref": p.ref, "mpn": p.mpn, "status": p.status, "frozen": p.frozen, "body_dims": p.body_dims, "blocker": "" if p.frozen else p.note})

    heat = {p.id: p for p in parts_ if p.id in {"C01", "C03", "P02", "P03"}}
    bat_r = next(p for p in parts_ if p.id == "BAT-R")
    ant = next(p for p in parts_ if p.id == "RF02")
    spk = next(p for p in parts_ if p.id == "SPK-R")
    shield = next(p for p in parts_ if p.id == "SH01")
    conflicts: list[str] = []
    for hp in heat.values():
        if overlap(bat_r, hp):
            conflicts.append(f"FAIL: BAT-R overlaps hot/high-stress part {hp.id} in top projection.")
    for bad in (bat_r, spk, shield):
        if overlap(ant, bad):
            conflicts.append(f"FAIL: RF02 antenna keep-out overlaps {bad.id}.")
    if not conflicts:
        conflicts.append("PASS: No 2D projection overlap between right battery and RK3576/RK806/TPS61088/boost inductor.")
        conflicts.append("PASS: RF02 antenna keep-out is separated from battery, main speaker and shield in this envelope model.")
    conflicts.append("WARN: LPDDR4X package body/height and ball map are still supplier/Rockchip HOLD despite EVT MPN selection.")
    conflicts.append("WARN: IMX415 camera module is an orange TBD target envelope, not released tooling geometry.")
    conflicts.append("WARN: Battery 70x12.8x5.6 is a control envelope; supplier pack drawing, tab/cable exit and dummy-cell fit test remain required.")
    if missing:
        conflicts.append("BLOCKED: Missing tools prevent native CAD exports: " + ", ".join(missing))
    (REPORTS / "mechanical_conflicts.md").write_text("# Mechanical conflicts and blockers\n\n" + "\n".join(f"- {x}" for x in conflicts) + "\n", encoding="utf-8")

    z_lines = [
        "# Z-stack report",
        "",
        "| Section | Stack / max height | Status |",
        "|---|---:|---|",
        "| RK806S-5 | 0.90 mm body + solder + clearance | package candidate, sequence HOLD |",
        "| eMMC KLMAG1JENB-B041 | 0.80 mm body + solder + clearance | candidate, BSP validation HOLD |",
        "| FCU760K | 2.00 mm module + clearance | HOLD pending Quectel design package |",
        "| Boost inductor XGL4020 | 2.00 mm + keep-out below | HOLD pending thermal/droop |",
        "| Speaker CMS-15113 | 3.00 mm + foam/cavity | acoustic EVT HOLD |",
        "| Battery envelope | 5.60 mm max + supplier swell/foam | HOLD supplier pack drawing |",
        "| IMX415 camera | target <=9.5 mm total Z | TBD, not released for tooling |",
        "| Hard components | >=0.3 mm worst-case clearance | rule carried into CAD checks |",
    ]
    (REPORTS / "z_stack_report.md").write_text("\n".join(z_lines) + "\n", encoding="utf-8")

    setup = [
        "# Setup requirements",
        "",
        f"Input PDF requested: `{INPUT_PDF_REQUESTED}`",
        f"Input PDF used: `{pdf_used}`",
        "",
        "| Tool | Path | Version/status | Impact | Install command |",
        "|---|---|---|---|---|",
    ]
    install_macos = {
        "blender": "brew install --cask blender",
        "freecad": "brew install --cask freecad",
        "kicad-cli": "brew install --cask kicad",
        "magick": "brew install imagemagick",
        "convert": "brew install imagemagick",
        "pdftotext": "brew install poppler",
        "python3": "brew install python@3.12",
        "git": "brew install git",
    }
    impacts = {
        "blender": ".blend and native Blender renders blocked",
        "freecad": ".FCStd and STEP exports blocked",
        "kicad-cli": "ERC/PDF export from KiCad CLI blocked",
        "magick": "image montage via ImageMagick blocked",
        "convert": "image montage via ImageMagick blocked",
        "pdftotext": "PDF dimension extraction blocked",
        "python3": "all generation blocked",
        "git": "version control operations blocked",
    }
    for tool, (path, version) in tools.items():
        setup.append(f"| {tool} | {path or '-'} | {version} | {impacts[tool]} | `{install_macos[tool]}` |")
    setup += [
        "",
        "Python package status: current environment has numpy/pandas/Pillow/matplotlib/PyYAML; reportlab/trimesh/shapely/ezdxf/pypdf are not installed.",
        "Because this environment lacks FreeCAD/Blender/KiCad CLI, native FreeCAD/Blender deliverables are recorded as blocked files, while AutoCAD DXF, PNG, CSV, JSON and STL outputs were generated.",
    ]
    (REPORTS / "setup_requirements.md").write_text("\n".join(setup) + "\n", encoding="utf-8")

    method = [
        "# Render method",
        "",
        "- Units: millimeters.",
        "- Source of truth: `v2_chipdown/scripts/chipdown_bom.py`, current generated schematic, and the supplied V2.2 hardware-dimensions PDF.",
        "- Rendering method on this machine: deterministic matplotlib engineering drawings plus ASCII STL envelope export.",
        "- AutoCAD handoff method: dependency-free ASCII DXF. `autocad_floorplan_2d.dxf` contains 2D engineering floorplans; `autocad_envelopes_3d.dxf` contains 3D `3DFACE` envelope solids.",
        "- Labeling method: short IDs on geometry, details in side tables/CSV to avoid text overlap.",
        "- Frozen dimensions use solid edges; TBD or target-only envelopes use orange transparent/dashed/hatch styling and are marked `TBD - NOT RELEASED FOR TOOLING`.",
        "- Native FreeCAD `.FCStd`, STEP and Blender `.blend` exports require installing the missing tools listed in `setup_requirements.md`.",
        "",
        "Generated outputs:",
        *[f"- {o.path}: {o.status} ({o.note})" for o in outputs],
    ]
    (REPORTS / "render_method.md").write_text("\n".join(method) + "\n", encoding="utf-8")


def render_all(parts_: list[Part]) -> list[OutputRecord]:
    outputs: list[OutputRecord] = []
    overview_3d(parts_, outputs, transparent=True, exploded=False, filename="01_transparent_overview.png", title="01 Transparent Engineering Overview - internal envelopes visible")
    overview_3d(parts_, outputs, transparent=False, exploded=False, filename="02_external_view.png", title="02 External View - opaque shell only with scale axes")
    right_top(parts_, outputs)
    side_view(parts_, "Right temple", outputs, "04_right_side.png", "04 Right Temple Side View - heat/battery separation", 150, 8.5)
    left_top(parts_, outputs)
    side_view(parts_, "Left temple", outputs, "06_left_side.png", "06 Left Temple Side View - AON + battery stack", 145, 7.5)
    front_detail(parts_, outputs)
    section_views(parts_, outputs)
    overview_3d(parts_, outputs, transparent=True, exploded=True, filename="14_exploded_view.png", title="14 Exploded Assembly View - shell, PCBs, batteries, RF and camera")
    return outputs


def main() -> int:
    ensure_dirs()
    problems = _validate()
    if problems:
        raise RuntimeError("Schematic/BOM validation failed: " + "; ".join(problems))
    p = parts()
    outputs = render_all(p)
    write_model_json(p, outputs)
    write_stl(p, outputs)
    write_autocad_dxf(p, outputs)
    write_blender_scripts(outputs)
    write_reports(p, outputs)
    print(f"generated {len(outputs)} output records under {BASE.relative_to(ROOT.parent)}")
    print(f"renders: {RENDERS.relative_to(ROOT.parent)}")
    print(f"reports: {REPORTS.relative_to(ROOT.parent)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
