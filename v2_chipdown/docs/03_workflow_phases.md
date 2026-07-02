# 03 — Development Workflow (reordered)

The old order was "finish the RK3576 board, then worry about power." V2 reverses it: **freeze battery volume + power state machine first, then draw the RK3576 chip-down.**

## Phase 0 — Freeze battery + usage modes (before any chip-down schematic)

**0.1 Five standard test scenarios** (see [02_power_states.md](02_power_states.md) for the full table): standby 20–50 mW / 12–24 h; phone-assist ID 250–450 mW / 3–5 h; mixed ≤500–800 mW target with current model at 450 mW / 3–4 h; record 1.0–1.5 W / 45–90 min; 1080p+AI 1.5–2.5 W / 30–60 min.

**0.2 Three battery tiers:**

| Total capacity | Product result |
|---|---|
| 300–400 mAh | thin temples; phone-assist oriented; short high-perf time |
| **500–650 mAh** | **recommended engineering target**; L/R temple split |
| 700–900 mAh | closer to 3–4 h heavy mixed, but temples visibly thicker/heavier |

### Gate 0 (mechanical, blocks all circuit design)
Mechanical CAD must prove, before schematic: batteries physically fit L/R temples; room for swell + foam + FPC + shell; batteries **not** stacked directly above RK3576/PMIC; L/R weight balanced; antenna keep-out respected; whole device still near <50 g.

## Phase 1 — Always-on low-power board FIRST (not RK3576)

Standalone small validation board: BLE MCU, Audio DSP/wake-word, IMU, buttons, fuel gauge, NTC, charge status, **RK3576 power-enable, camera power-enable, Wi-Fi power-enable**, UART to RK3576, Wake/Ready/Fault GPIO.

Validate: BLE-connected power; IMU motion-interrupt power; continuous wake-word listening power; MCU can reliably power the main SoC on/off; no reverse leakage when SoC is off; low-battery can *block* RK3576 start; false-wake rate; whether 12–24 h standby holds.

### Gate 1
AON total ≤ **50 mW**; no meaningful compute-island leakage when RK3576 is off; BLE/button/IMU/voice all produce reliable wake; **100 consecutive** SoC on/off cycles with no lock-up.

## Phase 1.5 — Mechanical/Electrical Floorplan (after schematic, before PCB layout)

This is the required bridge between an ERC-clean schematic and formal PCB layout.
The output is **not** a routed board. It is a dimensioned floorplan with top/side
views, board outlines, placement envelopes, height envelopes, keep-outs and FPC
corridors.

Minimum deliverables:

| Area | Required dimensions / checks |
|---|---|
| Right temple | usable internal length/width/height; Compute PCB outline; RK3576/LPDDR/RK806/eMMC/Wi-Fi/boost-inductor zones; battery envelope; speaker envelope; antenna keep-out; pogo/service area; shell/foam/swell allowance |
| Left temple | usable internal length/width/height; AON/power PCB outline; nRF/nPM/NDP/BMI270 zones; battery envelope; BLE antenna keep-out; pogo/FPC corridor; shell/foam/swell allowance |
| KiCad no-route floorplan | board frames plus RK3576, LPDDR, RK806, eMMC, Wi-Fi, boost inductor, FPC connectors, battery 3D/envelope blocks, speaker and antenna keep-outs |

**Do not route.** Only prove the product volume can physically contain the
current schematic architecture. If it does not fit, change the architecture now:
shorter battery, different board split, delete DNP features, move Wi-Fi, widen a
local temple pod, reduce connectors, or split into multiple rigid boards plus
FPC. Do not discover this during routing.

See [13_mechanical_electrical_floorplan.md](13_mechanical_electrical_floorplan.md)
for the floorplan template and pass/fail checklist.

## Phase 2 — Truly-powerdownable RK3576 minimum core

**Keep:** RK3576; 4 GB LPDDR4X; 32 GB eMMC; RK806S-5 PMIC; 24 MHz clock; USB2 MaskROM; UART debug; **one** MIPI CSI; PDM/SAI; Wi-Fi/BT (module or discrete); AON-MCU comms link; SoC master power switch; **per-domain current-sense points**.

**Delete:** HDMI, eDP, Ethernet, PCIe, SATA, UFS, USB3, microSD, 40-pin GPIO header, fan, dual-cam, display, non-essential peripherals.

> Start the first chip-down as a **delta off the Radxa reference** (LPDDR/PMIC/eMMC/camera/radio), not a from-scratch power+DDR redesign.

### Gate 2
MCU can cold-boot RK3576 fully; software can request MCU safe power-down; eMMC filesystem survives power-down; **20/20** cold boots succeed; Wi-Fi off = *rail* off (not just software sleep); camera off = sensor rails at 0; capture real power curves for record / AI / radio.

## Phase 3 — Redesign the power tree

`1S → 5V boost → everything` becomes a Buck + Load-Switch tree. Full detail in [04_power_tree.md](04_power_tree.md). Core rule: **do not boost everything to 5 V then step back down.** Only the RK3576 island gets a dedicated 5 V boost, and only if RK806 input truly needs it.

## Phase 4 — Split the one big carrier into 4 distributed boards

Detail in [05_hardware_partition.md](05_hardware_partition.md): front sensor board (custom 1080p cam + 2–4 mics + local LDO/Buck + status LED), right-temple compute board (RK3576 + LPDDR + PMIC + eMMC + heatsink), left-temple AON/power board (BLE MCU + DSP + charger + gauge + power-path + protection + SoC switch), and the rears (battery + speaker + antenna + charging pogo). **The IMX415 dev module is replaced by lens+sensor on a tiny rigid/rigid-flex board with a custom FPC** — no dev-board connectors or extra regulators.

## Phase 5 — Freeze the mic array before choosing count

"2 → 3–4 mics" is not just adding parts. Before schematic freeze, fix: mic coordinates, L/R spacing, front/back orientation, port locations, whether there's a dedicated wake mic, beamforming yes/no, wind-noise handling, speaker echo handling, which DSP/SoC runs AEC/denoise. **Lay out 4, populate 2–3 on EVT, decide production count after wind-tunnel + cycling wind + AEC tests.** The wake mic must live in the AON audio domain — Deep Off cannot rely on RK3576 to capture.

## Phase 6 — Event-driven software state machine

```
AON boot → BLE connect + IMU LP detect + wake-word listen + read buttons/fuel
         (RK3576 stays OFF)
   │
   ▼ cycling / voice / button / hazard event
 classify task:
   simple reminder → MCU handles directly
   GNSS need       → read from phone
   cloud voice     → phone handles
   vision task     → START RK3576 → camera on → ISP+NPU → encode clip →
                     Wi-Fi if needed → send → close Wi-Fi+camera → save → RK3576 sleep/off
```

## Full reordered flow

```
1 freeze usage modes + runtime defs
2 back-calculate required Wh + battery volume
3 finish L/R temple battery + board mechanical layout   ◄ Gate 0
4 design AON MCU + Audio DSP prototype
5 verify 20–50 mW standby + SoC power control           ◄ Gate 1
6 design RK3576 minimum chip-down core / system schematic
7 Phase 1.5 no-route mechanical/electrical floorplan     ◄ Floorplan Gate
8 build AON / camera / Wi-Fi / audio / SoC power islands
9 bench EVT: Linux + power measurement on external supply ◄ Gate 2
10 re-compute battery capacity from measured data
11 design split rigid PCBs + hinge FPC
12 add real battery, charging, fuel gauge, pogo pins
13 worn-condition runtime / thermal / RF / wind validation
14 decide whether to shrink battery or narrow temples further
```

## Gates for every revision

**Power Gate** — must submit measured: AON standby (MCU+DSP+BLE+IMU); RK3576-off leakage; Quick Standby power; camera-only (sensor+ISP+encode); AI-only (NPU inference power + duration); Wi-Fi TX avg+peak; full peak (cam+NPU+encode+Wi-Fi+speaker); **wake energy (mWh per start)**; return-to-sleep time. Record **peak + average + duration + energy-per-event**, not just "current now."

**Mechanical Gate** — real supplier battery dims; swell room; FPC through hinge; manufacturable camera + mic ports; antenna region clear of battery/copper/screws/speaker magnet; SoC heat routed to temple outside; **no SoC heat-spreader on the skin side.**
