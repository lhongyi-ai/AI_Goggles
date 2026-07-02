#!/usr/bin/env python3
"""Compute the AI Glasses Carrier V1 power budget + required battery capacity.

Reads config/power_budget.yaml (per-subsystem estimated load power per scenario),
sums each scenario, converts to battery-side current (incl. boost efficiency),
and reports runtime for the candidate packs + the capacity needed to hit target
run-times. Writes a Markdown report; render to PDF with kidoc like the others.

These are ENGINEERING ESTIMATES. Replace with bench values (R3 0R/shunt on +5V)
during bring-up, then re-run.
"""
from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
CFG = ROOT / "config" / "power_budget.yaml"
OUT = ROOT / "reports" / "AI_Glasses_Carrier_V1_Power_Budget.md"


def sanitize(s: str) -> str:
    rep = {"→": "->", "≈": "~", "±": "+/-", "×": "x", "–": "-", "—": "-",
           "≥": ">=", "≤": "<=", "Ω": "ohm", "“": '"', "”": '"'}
    for a, b in rep.items():
        s = s.replace(a, b)
    return "".join(c if ord(c) < 256 else "" for c in s)


def main() -> int:
    cfg = yaml.safe_load(CFG.read_text(encoding="utf-8"))
    c = cfg["constants"]
    v, eta, dod = c["v_batt_nominal_V"], c["boost_efficiency"], c["usable_dod"]
    scen = cfg["scenarios"]
    subs = cfg["subsystems"]
    packs = cfg["packs"]
    targets = cfg["target_runtimes_h"]

    # scenario load totals (W)
    total_W = {s: sum(sub["mW"][s] for sub in subs) / 1000.0 for s in scen}

    def batt_mA(load_W):          # battery-side current at nominal V, incl. boost loss
        return load_W / (v * eta) * 1000.0

    def runtime_h(mAh, load_W):   # usable energy / battery power
        usable_Wh = mAh / 1000.0 * v * dod
        return usable_Wh / (load_W / eta)

    def req_mAh(load_W, t_h):     # capacity to sustain load_W for t_h (with DoD)
        return (load_W / eta) * t_h / (v * dod) * 1000.0

    md: list[str] = []
    def w(line: str = ""): md.append(sanitize(line))

    w("# AI Glasses Carrier V1 - Power Budget & Battery Sizing")
    w("")
    w(f"- **Generated:** {date.today().isoformat()}  |  Source: `config/power_budget.yaml`")
    w(f"- **Assumptions:** 1S Li-Po {v} V nominal; boost eff {eta:.0%}; usable DoD {dod:.0%}.")
    w("- **[!] ESTIMATE** from datasheet typicals - NOT bench-measured. Fill measured "
      "current (R3 0R/shunt on +5V) during bring-up and re-run.")
    w("")
    w("## 1. Per-subsystem load power (mW)")
    w("")
    w("| Subsystem | Idle | Typical | Full | Note |")
    w("|---|--:|--:|--:|---|")
    for sub in subs:
        m = sub["mW"]
        w(f"| {sub['name']} | {m['idle']} | {m['typical']} | {m['full']} | {sub.get('note','')} |")
    w(f"| **TOTAL load** | **{total_W['idle']*1000:.0f}** | **{total_W['typical']*1000:.0f}** "
      f"| **{total_W['full']*1000:.0f}** | mW |")
    w("")

    w("## 2. Battery-side current & runtime")
    w("")
    w(f"Battery current = load / ({v} V x {eta:.0%} boost). Runtime uses {dod:.0%} usable DoD.")
    w("")
    hdr = "| Scenario | Load (W) | Batt current (mA) | Draw/hour (mAh) |"
    sep = "|---|--:|--:|--:|"
    for p in packs:
        hdr += f" {p['name']} ({p['mAh']} mAh) |"
        sep += "--:|"
    w(hdr); w(sep)
    for s in scen:
        lw = total_W[s]
        row = f"| {s.capitalize()} | {lw:.2f} | {batt_mA(lw):.0f} | {batt_mA(lw):.0f} |"
        for p in packs:
            row += f" {runtime_h(p['mAh'], lw):.1f} h |"
        w(row)
    w("")

    w("## 3. Battery capacity required for a target runtime")
    w("")
    w("Capacity (mAh) needed to sustain each scenario for the target time "
      f"(1S {v} V, {dod:.0%} DoD, boost {eta:.0%}):")
    w("")
    hdr = "| Scenario | Load (W) |" + "".join(f" {t} h |" for t in targets)
    sep = "|---|--:|" + "".join("--:|" for _ in targets)
    w(hdr); w(sep)
    for s in scen:
        lw = total_W[s]
        row = f"| {s.capitalize()} | {lw:.2f} |" + "".join(
            f" {req_mAh(lw, t):.0f} mAh |" for t in targets)
        w(row)
    w("")

    # headline numbers
    typ = total_W["typical"]
    w("## 4. Bottom line")
    w("")
    w(f"- **Typical use ~{typ:.1f} W** -> battery draws **~{batt_mA(typ):.0f} mA**, "
      f"i.e. **~{req_mAh(typ,1):.0f} mAh per hour**.")
    w(f"- Hitting the **3-4 h** target at typical load needs "
      f"**~{req_mAh(typ,3):.0f}-{req_mAh(typ,4):.0f} mAh**.")
    for p in packs:
        w(f"- **{p['name']} ({p['mAh']} mAh)** -> ~{runtime_h(p['mAh'], typ):.1f} h typical, "
          f"~{runtime_h(p['mAh'], total_W['full']):.1f} h full, "
          f"~{runtime_h(p['mAh'], total_W['idle']):.1f} h idle.")
    w("- The glasses pack cannot reach 3-4 h at a steady ~3 W; that target needs "
      "**AI duty-cycling** (wake-on-demand, gate the NPU/camera/encode), not just a bigger cell.")
    w("")
    w("---")
    w("_Estimates from `config/power_budget.yaml`. Replace with R3-shunt bench "
      "measurements during bring-up and re-run `scripts/power_budget.py`._")

    OUT.write_text("\n".join(md) + "\n", encoding="utf-8")

    # console summary
    print(f"wrote {OUT.relative_to(ROOT)}")
    for s in scen:
        lw = total_W[s]
        print(f"  {s:8} load {lw:.2f} W -> batt {batt_mA(lw):.0f} mA -> {req_mAh(lw,1):.0f} mAh/h")
    print(f"  target 3-4h @typical: {req_mAh(typ,3):.0f}-{req_mAh(typ,4):.0f} mAh")
    for p in packs:
        print(f"  {p['name']} {p['mAh']}mAh -> {runtime_h(p['mAh'],typ):.1f}h typ")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
