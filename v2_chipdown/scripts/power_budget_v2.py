#!/usr/bin/env python3
"""AI Glasses V2 (chip-down) power budget + battery sizing.

Reads:
  v2_chipdown/config/power_budget_v2.yaml   (subsystem x power-state model)
  v2_chipdown/config/battery_options.yaml   (candidate 1S packs incl. LP451165)

Computes, per power state:
  - total battery-side load (mW), and whether it lands in the design target band
  - runtime for every candidate pack (usable DoD applied)
  - capacity (mAh) needed to hit the state's target runtime
Plus a day-mix (duty-cycle blend) all-day-wear check, and a battery verdict.

All inputs are ENGINEERING ESTIMATES until Phase-2 bench EVT (per-island shunt)
replaces them. Writes Markdown to reports/POWER_BUDGET_V2.md; render with kidoc.
"""
from __future__ import annotations

from datetime import date
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent          # v2_chipdown/
MODEL = ROOT / "config" / "power_budget_v2.yaml"
BATT = ROOT / "config" / "battery_options.yaml"
OUT = ROOT / "reports" / "POWER_BUDGET_V2.md"


def sanitize(s: str) -> str:
    rep = {"→": "->", "≈": "~", "±": "+/-", "×": "x",
           "–": "-", "—": "-", "≥": ">=", "≤": "<=",
           "Ω": "ohm", "“": '"', "”": '"', "◄": "<-"}
    for a, b in rep.items():
        s = s.replace(a, b)
    return "".join(c if ord(c) < 256 else "" for c in s)


def main() -> int:
    model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))
    batt = yaml.safe_load(BATT.read_text(encoding="utf-8"))

    c = model["constants"]
    v, dod = c["v_batt_nominal_V"], c["usable_dod"]
    states = model["states"]
    subs = model["subsystems"]
    mixes = model["day_mixes"]
    packs = batt["packs"]
    recommended = batt.get("recommended")

    keys = [s["key"] for s in states]
    label = {s["key"]: s["label"] for s in states}

    # per-state total battery-side load (mW)
    total_mW = {k: sum(sub["mW"][k] for sub in subs) for k in keys}

    def batt_mA(mW):            # battery-side current at nominal V
        return mW / v

    def usable_mWh(mAh):        # energy actually usable
        return mAh * v * dod

    def runtime_h(mAh, mW):
        return usable_mWh(mAh) / mW if mW > 0 else float("inf")

    def req_mAh(mW, t_h):       # capacity to sustain mW for t_h at usable DoD
        return mW * t_h / (v * dod)

    def fmt_hm(h):
        if h >= 10:
            return f"{h:.0f} h"
        return f"{h:.1f} h ({h*60:.0f} min)"

    md: list[str] = []
    def w(line: str = ""):
        md.append(sanitize(line))

    w("# AI Glasses V2 (Chip-Down) - Power Budget & Battery Sizing")
    w("")
    w(f"- **Generated:** {date.today().isoformat()}  |  Model: `v2_chipdown/config/power_budget_v2.yaml`")
    w(f"- **Battery options:** `v2_chipdown/config/battery_options.yaml`")
    w(f"- **Assumptions:** 1S Li-Po {v} V nominal; usable DoD {dod:.0%}; "
      "subsystem mW are battery-side draw (conversion loss in the *_loss rows).")
    w("- **[!] ESTIMATE** from datasheet typicals - NOT bench-measured. Replace with "
      "per-island shunt values at Phase-2 EVT and re-run.")
    w("")

    # ---- 1. Per-state totals vs target band ----
    w("## 1. Per-state load vs design target")
    w("")
    w("| Power state | Modelled load (mW) | Target band (mW) | In band? | Batt current (mA) |")
    w("|---|--:|--:|:--:|--:|")
    for s in states:
        k = s["key"]
        lo, hi = s["target_mW"]
        target_display = s.get("target_display", f"{lo}-{hi}")
        tot = total_mW[k]
        ok = "YES" if lo <= tot <= hi else ("HIGH" if tot > hi else "LOW")
        w(f"| {label[k]} | **{tot}** | {target_display} | {ok} | {batt_mA(tot):.0f} |")
    w("")

    # ---- 2. Subsystem breakdown ----
    w("## 2. Subsystem breakdown (mW, battery-side)")
    w("")
    hdr = "| Subsystem | Domain |" + "".join(f" {k} |" for k in keys)
    sep = "|---|---|" + "".join("--:|" for _ in keys)
    w(hdr); w(sep)
    for sub in subs:
        row = f"| {sub['name']} | {sub['domain']} |" + "".join(
            f" {sub['mW'][k]} |" for k in keys)
        w(row)
    w("| **TOTAL** | |" + "".join(f" **{total_mW[k]}** |" for k in keys))
    w("")

    # ---- 3. Runtime per candidate pack ----
    w("## 3. Runtime per candidate battery")
    w("")
    w(f"Runtime = pack mAh x {v} V x {dod:.0%} DoD / load. "
      "Target-runtime column is the state's design goal.")
    w("")
    hdr = "| Power state | Target runtime |" + "".join(
        f" {p['mAh']} mAh ({p['id'].replace('_1S','_')}) |" for p in packs)
    sep = "|---|--:|" + "".join("--:|" for _ in packs)
    w(hdr); w(sep)
    for s in states:
        k = s["key"]
        tlo, thi = s["target_runtime_h"]
        row = f"| {label[k]} | {tlo}-{thi} h |"
        for p in packs:
            row += f" {fmt_hm(runtime_h(p['mAh'], total_mW[k]))} |"
        w(row)
    w("")

    # ---- 4. Required capacity for each state's target ----
    w("## 4. Capacity required to hit each target runtime")
    w("")
    w("| Power state | Load (mW) | Target runtime | Required capacity (mAh) |")
    w("|---|--:|--:|--:|")
    for s in states:
        k = s["key"]
        tlo, thi = s["target_runtime_h"]
        lo = req_mAh(total_mW[k], tlo)
        hi = req_mAh(total_mW[k], thi)
        w(f"| {label[k]} | {total_mW[k]} | {tlo}-{thi} h | {lo:.0f} - {hi:.0f} |")
    w("")

    # ---- 5. Day-mix all-day-wear check ----
    w("## 5. All-day wear (duty-cycle blend)")
    w("")
    w("Weighted-average power over a realistic day, and how long each pack lasts.")
    w("")
    for mix in mixes:
        fr = mix["fractions"]
        ssum = sum(fr.values())
        avg = sum(fr[k] * total_mW[k] for k in keys) / ssum
        w(f"### {mix['name']}")
        w("")
        w("- Blend: " + ", ".join(f"{k} {fr[k]*100:.0f}%" for k in keys))
        w(f"- **Weighted-average draw: ~{avg:.0f} mW** ({batt_mA(avg):.0f} mA)")
        w("")
        w("| Battery | All-day runtime |")
        w("|---|--:|")
        for p in packs:
            w(f"| {p['label']} ({p['mAh']} mAh) | {fmt_hm(runtime_h(p['mAh'], avg))} |")
        w("")

    # ---- 6. Verdict on recommended pack ----
    rec = next((p for p in packs if p["id"] == recommended), None)
    w("## 6. Battery verdict")
    w("")
    if rec:
        pack_topology = f"{rec['series']}S{rec['parallel']}P"
        w(f"**Recommended: {rec['label']} - {rec['mAh']} mAh / {rec['Wh']} Wh "
          f"({pack_topology}), ~{rec['weight_g_est']} g.**")
        w("")
        w("| Power state | Target runtime | Recommended pack | Meets target? |")
        w("|---|--:|--:|:--:|")
        for s in states:
            k = s["key"]
            tlo, thi = s["target_runtime_h"]
            rt = runtime_h(rec["mAh"], total_mW[k])
            verdict = "YES" if rt >= tlo else "NO"
            w(f"| {label[k]} | {tlo}-{thi} h | {fmt_hm(rt)} | {verdict} |")
        w("")
        # contradiction resolution: single-cell 300 mAh
        single = next((p for p in packs if p["id"] == "LP451165_1S1P"), None)
        if single:
            k = "mixed_active"
            rt1 = runtime_h(single["mAh"], total_mW[k])
            rt2 = runtime_h(rec["mAh"], total_mW[k])
            w("### Why not a single 300 mAh cell")
            w("")
            w(f"- One LP451165 (300 mAh) at mixed use ({total_mW[k]} mW) lasts "
              f"**{fmt_hm(rt1)}** - misses the 3-4 h target.")
            w(f"- Two in 1S2P (600 mAh) lasts **{fmt_hm(rt2)}** - meets it. "
              "This is the '300 mAh cannot do 500-800 mW for 3-4 h' contradiction, resolved "
              "by (a) 600 mAh and (b) pulling mixed load down to ~450 mW.")
            w("")

    w("### Mechanical / safety notes (Mechanical Gate)")
    w("")
    w("- LP451165 = 4.5 x 11 x 65 mm per cell. Temple cavity must clear cell thickness "
      "+ ~0.5-1 mm swell + foam + FPC (budget ~6-7 mm internal).")
    w("- One cell per temple keeps L/R weight balanced (~6 g each, ~12 g total; well under the <50 g budget).")
    w("- 1S2P: same model / capacity / batch cells only; per-branch fusing/protection; NTC at the cell; "
      "fuel gauge configured for the paralleled capacity; keep Power-Path so charge+run can coexist.")
    w("- Do NOT stack cells directly above RK3576/PMIC; keep antenna keep-out clear of the cell.")
    w("- Check 1S voltage droop under the AI-burst peak (PMIC/boost UVLO risk).")
    w("")
    w("---")
    w("_Estimates from `v2_chipdown/config/*.yaml`. Replace with Phase-2 per-island shunt "
      "measurements (docs/03_workflow_phases.md Power Gate) and re-run `power_budget_v2.py`._")

    OUT.write_text("\n".join(md) + "\n", encoding="utf-8")

    # ---- console summary ----
    print(f"wrote {OUT.relative_to(ROOT.parent)}")
    for s in states:
        k = s["key"]
        lo, hi = s["target_mW"]
        tot = total_mW[k]
        flag = "ok" if lo <= tot <= hi else "OUT-OF-BAND"
        print(f"  {k:14} {tot:5} mW  (target {lo}-{hi})  {flag}")
    if rec:
        print(f"  recommended: {rec['label']} = {rec['mAh']} mAh / {rec['Wh']} Wh")
        for s in states:
            k = s["key"]
            print(f"    {k:14} -> {runtime_h(rec['mAh'], total_mW[k]):.2f} h")
        for mix in mixes:
            fr = mix["fractions"]
            avg = sum(fr[k] * total_mW[k] for k in keys) / sum(fr.values())
            print(f"    day-mix '{mix['name']}': {avg:.0f} mW avg -> "
                  f"{runtime_h(rec['mAh'], avg):.1f} h on {rec['mAh']} mAh")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
