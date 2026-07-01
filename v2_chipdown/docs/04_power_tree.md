# 04 — Power Tree (Buck + Load-Switch, not "boost everything")

## Old (V1, dev-board style)

```
1S battery ──► 5V Boost ──► everything (then LDO down to 1.8/3.3)
```

Every rail paid a boost-up then a step-down. Fine for a dev board, wasteful for glasses.

## New (V2)

```
1S battery system
   │
   ├─ high-eff, low-Iq Buck ─────► AON 1.8V / 3.3V
   │                               BLE MCU / DSP / IMU / fuel gauge   (ALWAYS ON)
   │
   ├─ Load Switch ───────────────► Camera 1.2V / 1.8V / 2.8V         (gated)
   │
   ├─ Load Switch or own Buck ───► Audio amp                          (gated)
   │
   ├─ Load Switch ───────────────► Wi-Fi                              (gated, on-demand)
   │
   └─ dedicated high-power path ─► RK3576 PMIC (RK806)               (gated)
                                    boost to 5V ONLY if RK806 input requires it
```

## Rules

1. **Do not** boost the whole system to 5 V and step back down. Camera, MCU, IMU, mics and part of the radio run **directly off the 1S cell** via high-efficiency Buck or Load Switch.
2. Only the **RK3576 compute island** gets a dedicated 5 V boost, and only if RK806's input range genuinely needs it. If RK806 accepts 1S directly, drop the boost.
3. The AON Buck must be **low quiescent current** — it runs 24/7 and dominates Deep Off. Its Iq is a Phase-1 acceptance number.
4. Every expensive rail is behind a **load switch the AON MCU controls**, with a defined off-leakage budget (Gate 1 / Gate 2).

## Per-island current sense (mandatory, upgraded from V1)

V1 already asked for a shunt / current sense / transient droop / safe-shutdown provision on power. In V2 this becomes **mandatory on every island**:

| Island | Sense point | Why |
|---|---|---|
| AON Buck output | shunt / INA | verify 20–50 mW Deep Off target |
| RK3576 island input | shunt / INA | record/AI curves + wake energy |
| Camera rail | shunt / INA | sensor+ISP draw, off-leakage |
| Wi-Fi rail | shunt / INA | TX avg vs peak |
| Audio amp | shunt / INA | speech avg vs music peak |

Record **peak, average, duration, and energy-per-event** at each — not a single "current now" reading. Check **battery voltage droop** during RK3576 peak (1S sag under burst load is a real risk for the boost / PMIC UVLO).
