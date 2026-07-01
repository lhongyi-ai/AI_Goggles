# 06 — Battery Strategy & Recommendation

> Numbers below are produced by `scripts/power_budget_v2.py` from
> `config/power_budget_v2.yaml` + `config/battery_options.yaml`. Re-run after any edit.

## The contradiction to kill first

The V1/shell-brief plan (≈3×100 mAh ≈ 300 mAh ≈ 1.11 Wh, usable ~0.85–0.95 Wh) **cannot** simultaneously satisfy:

1. only 300 mAh, **and**
2. mixed average 500–800 mW, **and**
3. mixed use 3–4 h.

Pick at least one change: push mixed average below the **≤500–800 mW** external target, raise the battery to **~500–800 mAh**, or lean on the phone/compute-box so RK3576 duty cycle drops. V2 does **two** of these: it models mixed use at **450 mW** (see [02_power_states.md](02_power_states.md)) *and* raises capacity to 600 mAh.

## Recommendation — LP451165 × 2, 1S2P

| | |
|---|---|
| Cell | **LP451165** — 3.7 V, 300 mAh, 1.11 Wh, **4.5 × 11 × 65 mm**, 10 kΩ NTC option |
| Pack | **1S2P, one cell per temple** = **600 mAh / 2.22 Wh** |
| Weight | ~6 g/cell, **~12 g total** (well under the <50 g budget) |
| Usable | 600 mAh × 3.7 V × 90 % DoD ≈ **2.0 Wh usable** |

This is the **500–650 mAh recommended engineering tier**, distributed L/R exactly as the architecture wants. The cell is already a slim wearable-camera form factor, so it drops into a temple.

## Does 600 mAh meet the targets? (model output)

| Power state | Modelled load | Target runtime | **600 mAh runtime** | Meets? |
|---|--:|--:|--:|:--:|
| Deep Off (standby) | 22 mW | 12–24 h | **~90 h** | ✅ |
| Quick Standby | 134 mW | 8–16 h | ~15 h | ✅ |
| Phone-assist safety ID | 362 mW | 3–5 h | ~5.5 h | ✅ |
| Mixed motion use | 450 mW | 3–4 h | ~4.4 h | ✅ |
| Continuous 1080p record | 1290 mW | 45–90 min | ~93 min | ✅ |
| 1080p + local AI | 2065 mW | 30–60 min | ~58 min | ✅ |

**All targets met.** Realistic all-day blends: "all-day mixed wear" ≈ 153 mW avg → **~13 h**; "heavy usage day" ≈ 290 mW avg → **~7 h**.

## Why not one 300 mAh cell

One LP451165 (300 mAh) at mixed use (450 mW) lasts only **~2.2 h** — misses 3–4 h. Two in 1S2P (600 mAh) reach **~4.4 h**. That's the contradiction resolved.

## Capacity tiers (for the trade discussion)

| Tier | Example pack | Mixed-use runtime | Notes |
|---|---|--:|---|
| 300–400 mAh | LP451165 ×1 (300) | ~2.2 h | thin temples, phone-assist only |
| **500–650 mAh** | **LP451165 ×2 (600)** | **~4.4 h** | **recommended** |
| 700–900 mAh | 400 ×2 (800) | ~5.9 h | closer to heavy 3–4 h, temples thicker/heavier |

## Pack architecture rules (1S2P)

- **Same model / capacity / batch** cells only — never parallel mixed-age/mixed-state pouches.
- Per-branch fuse or controlled protection on each long temple-to-temple battery run.
- NTC at the cell; fuel gauge configured for the **paralleled** capacity (600 mAh, not 300).
- **Power-Path** so charging + system run can happen together.
- Check **battery voltage droop** during the AI-burst peak (PMIC/boost UVLO risk on 1S sag).

## Mechanical checklist (Gate 0)

- Temple internal cavity ≥ ~6–7 mm to clear 4.5 mm cell + ~0.5–1 mm swell + foam + FPC.
- One cell per temple → L/R balanced.
- **No cell stacked directly above RK3576/PMIC**; keep the antenna region clear of the cell.
- Real supplier dims + swell room confirmed in CAD before schematic.

## Re-sizing after bench

After Phase-2 EVT gives measured per-island current, edit `config/power_budget_v2.yaml`, re-run the script, and re-decide capacity. If measured mixed load lands above ~500 mW, either tighten duty-cycling or step to the 700–900 mAh tier.
