# AI Glasses V2 (Chip-Down) - Power Budget & Battery Sizing

- **Generated:** 2026-07-01  |  Model: `v2_chipdown/config/power_budget_v2.yaml`
- **Battery options:** `v2_chipdown/config/battery_options.yaml`
- **Assumptions:** 1S Li-Po 3.7 V nominal; usable DoD 90%; subsystem mW are battery-side draw (conversion loss in the *_loss rows).
- **[!] ESTIMATE** from datasheet typicals - NOT bench-measured. Replace with per-island shunt values at Phase-2 EVT and re-run.

## 1. Per-state load vs design target

| Power state | Modelled load (mW) | Target band (mW) | In band? | Batt current (mA) |
|---|--:|--:|:--:|--:|
| Deep Off (AON only, RK3576 down) | **22** | 20-50 | YES | 6 |
| Quick Standby (DDR retention / light sleep) | **134** | 80-200 | YES | 36 |
| Phone-assisted safety ID (blended) | **362** | 250-450 | YES | 98 |
| Mixed motion use (blended) | **450** | <=500-800 | YES | 122 |
| Record Active (1080p, ISP+encode) | **1290** | 1000-1500 | YES | 349 |
| AI Burst (NPU + encode + Wi-Fi) | **2065** | 1500-2500 | YES | 558 |

## 2. Subsystem breakdown (mW, battery-side)

| Subsystem | Domain | deep_off | quick_standby | phone_assist | mixed_active | record | ai_record |
|---|---|--:|--:|--:|--:|--:|--:|
| BLE MCU (nRF-class, always-on) | AON | 2 | 3 | 8 | 6 | 5 | 8 |
| Audio DSP / wake-word (always listening) | AON | 12 | 12 | 15 | 15 | 15 | 20 |
| IMU BMI270 (low-power) | AON | 1 | 1 | 1 | 1 | 1 | 1 |
| MEMS mic array (wake mic always; array when active) | AON | 3 | 3 | 6 | 6 | 8 | 10 |
| Fuel gauge + NTC + protection | AON | 1 | 1 | 1 | 1 | 1 | 1 |
| AON Buck quiescent + regulation loss | AON | 3 | 4 | 6 | 6 | 10 | 15 |
| RK3576 SoC + LPDDR4X + eMMC + PMIC | COMPUTE | 0 | 90 | 150 | 250 | 850 | 1500 |
| Custom 1080p camera (sensor + ISP share) | CAMERA | 0 | 0 | 0 | 30 | 250 | 300 |
| Wi-Fi (on-demand) | RADIO | 0 | 0 | 150 | 100 | 80 | 120 |
| Audio amp + speaker (avg) | AUDIO | 0 | 0 | 15 | 15 | 30 | 30 |
| Compute-island load switches / PMIC loss | COMPUTE | 0 | 20 | 10 | 20 | 40 | 60 |
| **TOTAL** | | **22** | **134** | **362** | **450** | **1290** | **2065** |

## 3. Runtime per candidate battery

Runtime = pack mAh x 3.7 V x 90% DoD / load. Target-runtime column is the state's design goal.

| Power state | Target runtime | 300 mAh (LP451165_1P) | 600 mAh (LP451165_2P) | 500 mAh (generic_500_2P) | 650 mAh (generic_650_2P) | 800 mAh (generic_800_2P) |
|---|--:|--:|--:|--:|--:|--:|
| Deep Off (AON only, RK3576 down) | 12-24 h | 45 h | 91 h | 76 h | 98 h | 121 h |
| Quick Standby (DDR retention / light sleep) | 8-16 h | 7.5 h (447 min) | 15 h | 12 h | 16 h | 20 h |
| Phone-assisted safety ID (blended) | 3-5 h | 2.8 h (166 min) | 5.5 h (331 min) | 4.6 h (276 min) | 6.0 h (359 min) | 7.4 h (442 min) |
| Mixed motion use (blended) | 3-4 h | 2.2 h (133 min) | 4.4 h (266 min) | 3.7 h (222 min) | 4.8 h (289 min) | 5.9 h (355 min) |
| Record Active (1080p, ISP+encode) | 0.75-1.5 h | 0.8 h (46 min) | 1.5 h (93 min) | 1.3 h (77 min) | 1.7 h (101 min) | 2.1 h (124 min) |
| AI Burst (NPU + encode + Wi-Fi) | 0.5-1.0 h | 0.5 h (29 min) | 1.0 h (58 min) | 0.8 h (48 min) | 1.0 h (63 min) | 1.3 h (77 min) |

## 4. Capacity required to hit each target runtime

| Power state | Load (mW) | Target runtime | Required capacity (mAh) |
|---|--:|--:|--:|
| Deep Off (AON only, RK3576 down) | 22 | 12-24 h | 79 - 159 |
| Quick Standby (DDR retention / light sleep) | 134 | 8-16 h | 322 - 644 |
| Phone-assisted safety ID (blended) | 362 | 3-5 h | 326 - 544 |
| Mixed motion use (blended) | 450 | 3-4 h | 405 - 541 |
| Record Active (1080p, ISP+encode) | 1290 | 0.75-1.5 h | 291 - 581 |
| AI Burst (NPU + encode + Wi-Fi) | 2065 | 0.5-1.0 h | 310 - 620 |

## 5. All-day wear (duty-cycle blend)

Weighted-average power over a realistic day, and how long each pack lasts.

### All-day mixed wear

- Blend: deep_off 70%, quick_standby 10%, phone_assist 12%, mixed_active 4%, record 2%, ai_record 2%
- **Weighted-average draw: ~153 mW** (41 mA)

| Battery | All-day runtime |
|---|--:|
| LP451165 x1 (one temple only) (300 mAh) | 6.5 h (391 min) |
| LP451165 x2, 1S2P (RECOMMENDED) (600 mAh) | 13 h |
| Generic 250 mAh x2, 1S2P (500 mAh) | 11 h |
| Generic 325 mAh x2, 1S2P (650 mAh) | 14 h |
| Generic 400 mAh x2, 1S2P (800 mAh) | 17 h |

### Heavy usage day

- Blend: deep_off 50%, quick_standby 15%, phone_assist 15%, mixed_active 10%, record 6%, ai_record 4%
- **Weighted-average draw: ~290 mW** (78 mA)

| Battery | All-day runtime |
|---|--:|
| LP451165 x1 (one temple only) (300 mAh) | 3.4 h (206 min) |
| LP451165 x2, 1S2P (RECOMMENDED) (600 mAh) | 6.9 h (413 min) |
| Generic 250 mAh x2, 1S2P (500 mAh) | 5.7 h (344 min) |
| Generic 325 mAh x2, 1S2P (650 mAh) | 7.5 h (447 min) |
| Generic 400 mAh x2, 1S2P (800 mAh) | 9.2 h (550 min) |

## 6. Battery verdict

**Recommended: LP451165 x2, 1S2P (RECOMMENDED) - 600 mAh / 2.22 Wh (1S2P), ~12 g.**

| Power state | Target runtime | Recommended pack | Meets target? |
|---|--:|--:|:--:|
| Deep Off (AON only, RK3576 down) | 12-24 h | 91 h | YES |
| Quick Standby (DDR retention / light sleep) | 8-16 h | 15 h | YES |
| Phone-assisted safety ID (blended) | 3-5 h | 5.5 h (331 min) | YES |
| Mixed motion use (blended) | 3-4 h | 4.4 h (266 min) | YES |
| Record Active (1080p, ISP+encode) | 0.75-1.5 h | 1.5 h (93 min) | YES |
| AI Burst (NPU + encode + Wi-Fi) | 0.5-1.0 h | 1.0 h (58 min) | YES |

### Why not a single 300 mAh cell

- One LP451165 (300 mAh) at mixed use (450 mW) lasts **2.2 h (133 min)** - misses the 3-4 h target.
- Two in 1S2P (600 mAh) lasts **4.4 h (266 min)** - meets it. This is the '300 mAh cannot do 500-800 mW for 3-4 h' contradiction, resolved by (a) 600 mAh and (b) pulling mixed load down to ~450 mW.

### Mechanical / safety notes (Mechanical Gate)

- LP451165 = 4.5 x 11 x 65 mm per cell. Temple cavity must clear cell thickness + ~0.5-1 mm swell + foam + FPC (budget ~6-7 mm internal).
- One cell per temple keeps L/R weight balanced (~6 g each, ~12 g total; well under the <50 g budget).
- 1S2P: same model / capacity / batch cells only; per-branch fusing/protection; NTC at the cell; fuel gauge configured for the paralleled capacity; keep Power-Path so charge+run can coexist.
- Do NOT stack cells directly above RK3576/PMIC; keep antenna keep-out clear of the cell.
- Check 1S voltage droop under the AI-burst peak (PMIC/boost UVLO risk).

---
_Estimates from `v2_chipdown/config/*.yaml`. Replace with Phase-2 per-island shunt measurements (docs/03_workflow_phases.md Power Gate) and re-run `power_budget_v2.py`._
