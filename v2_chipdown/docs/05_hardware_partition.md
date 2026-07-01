# 05 — Hardware Partition (4 distributed boards)

Instead of one big carrier holding compute + battery + charging + audio, split into four physical regions. This is what actually lets you balance heat, weight, and battery volume across the frame.

```
                          FRONT FRAME
                    Camera + Mic Array
                            │ FPC
                            ▼
        ┌───────────────────┴───────────────────┐
   RIGHT TEMPLE (front)                   LEFT TEMPLE (front)
   RK3576 Compute                    AON MCU + DSP + Power
        │                                   │
   R battery + Speaker                 L battery + Speaker
        │                                   │
   Wi-Fi antenna                       BLE antenna / charging
```

## 1. Front-frame sensor board
- Small **custom 1080p camera** (lens + sensor only)
- **2–4 MEMS mics** (see Phase 5 — lay out 4, populate 2–3 on EVT)
- Camera-local LDO / Buck
- Ambient-light or status LED
- Connects to temples by **FPC**

> Replace the IMX415 dev module with lens + sensor on a **tiny rigid or rigid-flex board + custom FPC**, no dev-board connector, no redundant regulators.

## 2. Right-temple compute board
- RK3576
- LPDDR4X
- PMIC (RK806S-5)
- eMMC
- **Primary heat structure** (routes heat to temple outer wall, not skin side)
- **Not** stacked directly above/below the battery

## 3. Left-temple always-on / power board
- BLE MCU
- Audio DSP / wake-word
- Charger
- Fuel gauge
- Power-path
- Battery protection
- **Main-SoC power switch control**

## 4. Temple rears (both sides)
- Battery (one cell per temple — see [06_battery_strategy.md](06_battery_strategy.md))
- Speaker (single now, **layout reserves dual**)
- Antenna (BLE left, Wi-Fi right)
- Charging pogo pins

## Interconnect

- Front frame → temples: **FPC through the hinge** (must survive hinge flex — a Mechanical-Gate item).
- Left ↔ right temple: control/power link across the frame; keep high-speed (MIPI, RK3576 signals) on the right, low-speed (BLE control, I²C, UART) on the left.
- **Antenna keep-out:** no battery, copper pour, screws, or speaker magnet in the antenna region.
