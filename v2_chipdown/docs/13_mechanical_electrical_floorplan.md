# 13 — Phase 1.5 Mechanical/Electrical Floorplan

This phase sits between an ERC-clean schematic and formal PCB layout.

It is **not** a routed PCB. It is a dimensioned placement feasibility check:
top view, side view, board-outline envelopes, component height envelopes, cable/FPC
corridors, keep-outs and thermal/acoustic/RF conflict review.

## Verdict rule

**Formal PCB placement/routing must not start until this floorplan passes.**

If the floorplan does not fit, go back and change the product architecture:
shorter battery, wider local temple pod, different board split, fewer DNP
features, moved Wi-Fi, fewer connectors, or rigid-board-plus-FPC segmentation.

Do not discover "there is nowhere to put it" during routing.

## Current V2 placement concept

Generated current-state artifacts:

| Artifact | Path |
|---|---|
| Phase 1.5 fit report | [../reports/AI_Glasses_V2_Phase1_5_Floorplan.md](../reports/AI_Glasses_V2_Phase1_5_Floorplan.md) |
| Phase 1.5 Chinese CAD handoff | [../reports/AI_Glasses_V2_Phase1_5_Floorplan_ZH.md](../reports/AI_Glasses_V2_Phase1_5_Floorplan_ZH.md) |
| Multi-view render SVG | [../reports/output/AI_Glasses_V2_Phase1_5_Floorplan.svg](../reports/output/AI_Glasses_V2_Phase1_5_Floorplan.svg) |
| Multi-view render PNG | [../reports/output/AI_Glasses_V2_Phase1_5_Floorplan.png](../reports/output/AI_Glasses_V2_Phase1_5_Floorplan.png) |
| Multi-view render PDF | [../reports/output/AI_Glasses_V2_Phase1_5_Floorplan.pdf](../reports/output/AI_Glasses_V2_Phase1_5_Floorplan.pdf) |

Current verdict:

- A normal thin optical frame does **not** fit the V2 RK3576 chip-down
  architecture.
- A thick smart-glasses / sport-sunglasses frame can **conditionally fit** the
  current schematic if it provides the envelope below.
- This is not a PCB-layout release. G00/G00F/G07/G10/G12/G14 remain open/HOLD
  until real CAD, battery, RF, FPC, speaker, camera, and package drawings are
  verified.

Minimum frame envelope for the current schematic:

| Region | Minimum internal envelope | Why |
|---|---:|---|
| Right temple usable length | >=150 mm, with ~160+ mm preferred for clean antenna/battery separation | RK3576 board + 70 mm cell + speaker/pogo + Wi-Fi antenna keep-out |
| Right front compute pod | >=72 x 20 x 8.5 mm | 62 x 18 mm compute PCB plus FPC strain relief and thermal stack |
| Right rear battery/RF/acoustic pod | >=78 x 16 x 8.5 mm | LP451165 max envelope 70 x 12.8 x 5.6 mm plus foam/swell, LS1 acoustic slot, pogo, RF window |
| Left temple usable length | >=145 mm | AON board + 70 mm cell + BLE keep-out + pogo |
| Left front AON pod | >=54 x 16 x 7.5 mm | 46 x 14 mm AON/power PCB plus FPC and shell clearance |
| Left rear battery/RF pod | >=82 x 16 x 7.5 mm | LP451165 max envelope plus BLE antenna region and service/charge area |
| Front sensor brow | >=32 x 8 x 5 mm | Custom IMX415 module, camera power, ESD, mic footprints and FPC exit |

PCB stack recommendation:

- Right compute PCB: one double-sided 8-10 layer HDI rigid island, not a
  board-on-board stack.
- Left AON PCB: start with 4 layers; move to 6 only if RF/noise/current-sense
  review requires it.
- Front sensor/FPC: 4-layer controlled-impedance rigid-flex if MIPI stays in the
  front frame.
- Do not stack the battery over RK3576, RK806S, TPS61088, the boost inductor, or
  the Wi-Fi antenna keep-out.

## Required outputs

| Output | Owner | Required content |
|---|---|---|
| Right-temple top view | CAD + EE | board outlines, RK3576/DDR/PMIC/eMMC/Wi-Fi/boost-inductor, battery, speaker, antenna keep-out, pogo/FPC paths |
| Right-temple side view | CAD + EE | PCB thickness, max component height, battery envelope, speaker height, shell wall, foam/swell allowance |
| Left-temple top view | CAD + EE | AON/power PCB, nRF/nPM/NDP/IMU, battery, BLE antenna, FPC/pogo/mechanical corridors |
| Left-temple side view | CAD + EE | PCB thickness, max component height, battery envelope, shell wall, foam/swell allowance |
| KiCad no-route floorplan | EE/layout | board frames, placement blocks, courtyard/keep-out geometry, component height notes; **no routing** |
| Fit decision table | PM + CAD + EE | pass/fail for battery, compute board, antenna, speaker, FPC, pogo, heat path |

## Dimension table template

Fill every blank with measured CAD/supplier numbers before layout release.

### Right temple

| Item | Required value | Current / candidate value | Pass? | Notes |
|---|---:|---:|:--:|---|
| Right-temple usable internal length | ___ mm | ___ mm | TBD | after hinge/pogo/screw losses |
| Right-temple usable internal width | ___ mm | ___ mm | TBD | include wall thickness |
| Right-temple usable internal height | ___ mm | ___ mm | TBD | side-view clearance |
| Compute PCB outline | ___ x ___ x ___ mm | ___ x ___ x ___ mm | TBD | length x width x thickness |
| RK3576 keep-out/courtyard | ___ x ___ x ___ mm | ___ x ___ x ___ mm | TBD | include fanout + thermal path |
| LPDDR4X + DDR escape zone | ___ x ___ mm | ___ x ___ mm | TBD | length-match corridor |
| RK806S PMIC zone | ___ x ___ x ___ mm | ___ x ___ x ___ mm | TBD | inductors/caps included |
| eMMC zone | ___ x ___ x ___ mm | ___ x ___ x ___ mm | TBD | near RK3576 |
| TPS61088 + boost inductor zone | ___ x ___ x ___ mm | ___ x ___ x ___ mm | TBD | high-current loop, thermal |
| Wi-Fi module zone | ___ x ___ x ___ mm | FCU760K 13.0 x 12.2 x 2.0 mm + keep-out | TBD | final land pattern still HOLD |
| Wi-Fi antenna keep-out | ___ x ___ mm | ___ x ___ mm | TBD | no battery/copper/screw/speaker magnet |
| Right battery envelope | ___ x ___ x ___ mm | LP451165 max envelope target 70 x 12.8 x 5.6 mm | TBD | includes swell, tabs, foam, FPC |
| Speaker envelope | ___ x ___ x ___ mm | ___ x ___ x ___ mm | TBD | after acoustic cavity choice |
| Pogo / charge area | ___ mm length | ___ mm | TBD | sweat/corrosion/service path |
| FPC / harness corridor | ___ x ___ mm | ___ x ___ mm | TBD | no pinch at hinge or screws |
| Shell + foam + swell allowance | ___ mm | ___ mm | TBD | minimum around battery |
| Skin-side thermal stack | ___ mm | ___ mm | TBD | no hot spreader on skin side |

### Left temple

| Item | Required value | Current / candidate value | Pass? | Notes |
|---|---:|---:|:--:|---|
| Left-temple usable internal length | ___ mm | ___ mm | TBD | after hinge/pogo/screw losses |
| Left-temple usable internal width | ___ mm | ___ mm | TBD | include wall thickness |
| Left-temple usable internal height | ___ mm | ___ mm | TBD | side-view clearance |
| AON/power PCB outline | ___ x ___ x ___ mm | ___ x ___ x ___ mm | TBD | length x width x thickness |
| nRF54L15 zone | ___ x ___ x ___ mm | QFN48 6 x 6 mm + RF keep-out | TBD | RF/antenna routing |
| nPM1300 zone | ___ x ___ x ___ mm | QFN 5 x 5 mm + passives | TBD | charger heat and battery proximity |
| NDP120 zone | ___ x ___ x ___ mm | ___ x ___ x ___ mm | TBD | package still HOLD |
| BMI270 zone | ___ x ___ x ___ mm | LGA 2.5 x 3.0 mm | TBD | mechanical vibration coupling |
| Left battery envelope | ___ x ___ x ___ mm | LP451165 max envelope target 70 x 12.8 x 5.6 mm | TBD | includes swell, tabs, foam, FPC |
| BLE antenna keep-out | ___ x ___ mm | ___ x ___ mm | TBD | no battery/copper/screw/magnet |
| Pogo / charge area | ___ mm length | ___ mm | TBD | if shared with right/rear area |
| FPC / harness corridor | ___ x ___ mm | ___ x ___ mm | TBD | fixed-temple EVT or future hinge |
| Shell + foam + swell allowance | ___ mm | ___ mm | TBD | minimum around battery |

## KiCad floorplan contents

Create a no-route KiCad floorplan project or board file with only:

| Place / draw | Purpose |
|---|---|
| Board outlines | prove each rigid PCB fits the CAD envelope |
| RK3576 | compute hot spot and fanout/courtyard reference |
| LPDDR4X | DDR adjacency and length-match escape corridor |
| RK806S | PMIC + inductor/cap placement envelope |
| eMMC | boot storage placement envelope |
| Wi-Fi module | FCU760K LCC + antenna/keep-out relation |
| Boost inductor | height and high-current thermal loop |
| FPC connectors | front sensor and inter-board corridors |
| Battery 3D/envelope blocks | LP451165 nominal and max/swell envelope |
| Speaker | acoustic cavity and magnet keep-out |
| Antenna keep-outs | RF no-copper/no-battery/no-screw/no-magnet zones |
| Pogo/charge region | charging service and sealing interface |

Do **not** route. Do **not** optimize trace escape. The pass/fail question is:
can the real parts, keep-outs and height envelopes coexist in the product volume?

## Pass/fail checklist

| Check | Pass condition | Status |
|---|---|:--:|
| Battery fit | both LP451165 envelopes fit with swell + foam + tabs + FPC room | TBD |
| Compute fit | RK3576/LPDDR/RK806/eMMC/TPS61088/Wi-Fi placement envelopes fit in right temple | TBD |
| AON fit | nRF/nPM/NDP/BMI270/protection/current-sense envelopes fit in left temple | TBD |
| Antenna keep-out | BLE/Wi-Fi regions clear battery, copper, screws, speaker magnet and high-current loops | TBD |
| Speaker/acoustic | LS1 and cavity fit without blocking antenna or FPC corridor | TBD |
| FPC/interconnect | front sensor FPC and L/R interconnect corridor fit without pinch or impossible bend | TBD |
| Pogo/service | charge/debug/service region fits and remains mechanically accessible | TBD |
| Thermal | RK3576/PMIC/boost heat path goes to outer temple, not skin side or battery | TBD |
| DNP features | LS2/M1/U22 and extra INA pads do not consume critical fit/keep-out space | TBD |

## If it fails

Allowed architecture changes before routing:

- switch to a shorter or lower-capacity cell;
- widen only the local compute pod or battery pod;
- move Wi-Fi/antenna further from compute and speaker magnet;
- split one rigid board into multiple rigid islands connected by FPC;
- delete or postpone DNP features that consume mechanical volume;
- reduce connector count or replace connectors with soldered FPC/coax where appropriate;
- reassign functions between left/right temple boards;
- change from future foldable hinge assumptions to fixed-temple EVT.

## Handoff note for CAD

For EVT-A, fixed temples are acceptable. Reserve an FPC/interconnect corridor for
future hinge or service routing, but do not force a production foldable hinge
until the electronics, battery, RF, thermal and acoustic placement can pass this
floorplan.
