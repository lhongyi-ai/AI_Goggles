# AI Glasses Carrier V1 - Power Budget & Battery Sizing

- **Generated:** 2026-06-30  |  Source: `config/power_budget.yaml`
- **Assumptions:** 1S Li-Po 3.7 V nominal; boost eff 90%; usable DoD 90%.
- **[!] ESTIMATE** from datasheet typicals - NOT bench-measured. Fill measured current (R3 0R/shunt on +5V) during bring-up and re-run.

## 1. Per-subsystem load power (mW)

| Subsystem | Idle | Typical | Full | Note |
|---|--:|--:|--:|---|
| CM4 (RK3576 SoC + LPDDR4X + eMMC) | 450 | 2000 | 2900 | Dominant load; NPU AI + camera ISP + H.265 encode drive the peaks |
| Wi-Fi / BT radio (on CM4) | 50 | 200 | 750 | TX bursts; radio is on the CM4 module |
| Camera IMX415 (4-lane MIPI) | 0 | 400 | 450 | Off in idle; streaming otherwise |
| Audio amp + speaker (avg) | 0 | 150 | 300 | Class-D average for speech; short music peaks to ~3W not in the average |
| PDM mics x2 | 10 | 20 | 20 |  |
| GNSS MAX-M10S | 20 | 80 | 80 | ~25 mA @3.3V during acquisition/tracking |
| IMU ICM-42688-P | 1 | 1 | 2 | Low-power 6-axis |
| Haptic DRV2605L (avg) | 0 | 0 | 100 | Only during a vibration pulse |
| Status LEDs | 20 | 30 | 30 |  |
| LDO quiescent + regulation loss margin | 100 | 150 | 200 | 3V3/1V8 LDO drop + headroom |
| **TOTAL load** | **651** | **3031** | **4832** | mW |

## 2. Battery-side current & runtime

Battery current = load / (3.7 V x 90% boost). Runtime uses 90% usable DoD.

| Scenario | Load (W) | Batt current (mA) | Draw/hour (mAh) | V1 bench 103450 (2000 mAh) | Glasses pack (2-3 cells) (650 mAh) |
|---|--:|--:|--:|--:|--:|
| Idle | 0.65 | 195 | 195 | 9.2 h | 3.0 h |
| Typical | 3.03 | 910 | 910 | 2.0 h | 0.6 h |
| Full | 4.83 | 1451 | 1451 | 1.2 h | 0.4 h |

## 3. Battery capacity required for a target runtime

Capacity (mAh) needed to sustain each scenario for the target time (1S 3.7 V, 90% DoD, boost 90%):

| Scenario | Load (W) | 1 h | 2 h | 3 h | 4 h |
|---|--:|--:|--:|--:|--:|
| Idle | 0.65 | 217 mAh | 434 mAh | 652 mAh | 869 mAh |
| Typical | 3.03 | 1011 mAh | 2023 mAh | 3034 mAh | 4045 mAh |
| Full | 4.83 | 1612 mAh | 3225 mAh | 4837 mAh | 6449 mAh |

## 4. Bottom line

- **Typical use ~3.0 W** -> battery draws **~910 mA**, i.e. **~1011 mAh per hour**.
- Hitting the **3-4 h** target at typical load needs **~3034-4045 mAh**.
- **V1 bench 103450 (2000 mAh)** -> ~2.0 h typical, ~1.2 h full, ~9.2 h idle.
- **Glasses pack (2-3 cells) (650 mAh)** -> ~0.6 h typical, ~0.4 h full, ~3.0 h idle.
- The glasses pack cannot reach 3-4 h at a steady ~3 W; that target needs **AI duty-cycling** (wake-on-demand, gate the NPU/camera/encode), not just a bigger cell.

---
_Estimates from `config/power_budget.yaml`. Replace with R3-shunt bench measurements during bring-up and re-run `scripts/power_budget.py`._
