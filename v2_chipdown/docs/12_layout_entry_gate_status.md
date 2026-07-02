# 12 — Layout-entry gate status and HOLD closure

> Generated 2026-07-01 from `scripts/chipdown_bom.py`. This is the go/no-go record for entering PCB layout.

## Verdict

**PCB layout is NOT released.** The schematic is ERC-clean and useful for review, procurement and bench planning, but Gate 0/G00F/G05/G07/G08/G10/G12 remain HOLD.

Current BOM state: **93 components** — 57 Fit · 18 HOLD · 16 DNP · 2 TBD; **18 HOLD** components.

## Gate table

| Gate | Topic | Status | Close condition | Components currently referencing it |
|---|---|:--:|---|---|
| G00 | Mechanical/battery layout gate | HOLD | real cell fit, swell room, fixed-temple cable/tab exits, antenna keep-out, no battery over RK3576/PMIC/boost | - |
| G00F | Phase 1.5 mechanical/electrical floorplan | HOLD | dimensioned top/side floorplan + no-route KiCad placement envelopes prove all critical parts fit before routing | - |
| G01 | RK3576 identity + HDG | OPEN | full datasheet/HDG/ball map, package drawing, reference-design delta plan | U1, Y1 |
| G02 | LPDDR4X | OPEN | verified MPN, topology, placement, length report, DDR review | U3 |
| G03 | RK806S PMIC | OPEN | exact MPN, rails, inductors/caps, sequence/timing with RK3576 | U2 |
| G04 | eMMC/boot | OPEN | MPN, BSP/bootloader, cold boot and power-loss recovery plan | U4 |
| G05 | Wi-Fi module | HOLD | Quectel FCU760K Hardware Design, official LCC land pattern, RK3576 BSP/firmware enumeration | U11, U12, U13 |
| G06 | High-power transient sizing | OPEN | RK3576 boot/AI peak, boost soft-start, 1S droop, Wi-Fi/camera/audio peaks | U6, L1, U12 |
| G07 | LP451165 + 1S2P pack | HOLD | formal datasheet, discharge curve, IR/cycle/cert, pairing/fuse/NTC/current-share tests | BT1, BT2 |
| G08 | AON power | HOLD | nPM1300 EK config, NDP120 kit, measured AON <=25 mW avg / <=50 mW ceiling | U8 |
| G09 | Thermal/boost droop | OPEN | RK3576 burst thermal path, TPS61088/RK806 droop and UVLO margin | U6 |
| G10 | Camera module | HOLD | final IMX415 module FPC pinout, lens/FOV, lane count, rail current/timing | U14, J3 |
| G11 | Mic/audio topology | OPEN | mic coordinates, ports, wind/AEC/beamforming, NDP120 wake path | MK1, MK2, MK3, MK4 |
| G12 | Camera/front FPC interconnect | HOLD | FH26W-33S pin count/contact orientation, camera FPC impedance, module vendor sign-off; hinge electrical interconnect is out of scope | J3 |
| G13 | Magnetics/passives height | OPEN | inductor Isat/DCR/height, cap derating, wearable Z limits | L1 |
| G14 | RF/worn tune | OPEN | antenna SKU, keep-out, matching in shell and worn condition | J7 |
| G15 | Passive/manufacturing BOM | OPEN | expanded R/C/L MPNs, derating, lifecycle and alternates | - |

## HOLD closure pack status

| Item | Status | Close condition | Source folder | Blocks |
|---|:--:|---|---|---|
| NDP120 | HOLD | Full datasheet, package drawing/land pattern, rail map, reset/strap sequence, dev kit, model toolchain/licensing, measured listening power | AI_Glasses_HOLD_Closure_Pack/01_NDP120 | Blocks U9 and wake-audio freeze |
| Wi-Fi FCU760K | HOLD | Quectel Hardware Design, official LCC land pattern/3D/height, antenna SKU, RK3576 BSP driver + firmware enumeration | AI_Glasses_HOLD_Closure_Pack/02_WiFi_FCU760K | Blocks U11/J7 RF and USB2/PCM freeze |
| LP451165 cell | HOLD | Formal supplier datasheet, discharge curves, IR, cycle life, high-rate limit, certification, swell envelope | AI_Glasses_HOLD_Closure_Pack/03_Battery_LP451165_1S2P | Blocks BT1/BT2 and mechanical Gate 0 |
| 1S2P pack | HOLD | Pairing rules, fusing, NTC placement, current-share shunts, protection scheme, charge/gauge profiling | AI_Glasses_HOLD_Closure_Pack/03_Battery_LP451165_1S2P | Blocks G07/G08/G00 |
| Camera power current | HOLD | Custom IMX415 module rail currents/timing/FPC pinout beyond bare sensor datasheet | AI_Glasses_HOLD_Closure_Pack/04_IMX415 | Blocks U14, CAM rails and G10 |
| Battery bay dimensions | HOLD | Real dummy-cell assembly, foam/swell allowance, tab/cable exit, antenna and speaker interference | AI_Glasses_HOLD_Closure_Pack/06_Mechanical_Fit_Check | Blocks PCB layout start |
| Phase 1.5 floorplan | HOLD | Right/left temple dimension tables, no-route KiCad floorplan, antenna/speaker/FPC/pogo/thermal keep-outs, pass/fail decision | v2_chipdown/docs/13_mechanical_electrical_floorplan.md | Blocks formal PCB placement/routing |

## HOLD components

| Ref | BOM ID | Value | Gate |
|---|---|---|---|
| U2 | C002 | RK806S-5 QFN68 7x7x0.90mm | G03 (official RK806S-5 datasheet, OTP/default rails, sequence, layout guide) |
| U3 | C003 | Samsung K4U6E3S4AA-MGCL | G02 (Samsung datasheet/ball map/IBIS + Rockchip DDR AVL/init + length report) |
| U4 | C004 | Samsung KLMAG1JENB-B041 | G04 (official Samsung datasheet/package + BSP boot/HS200 then HS400 validation) |
| U6 | C007 | TPS61088 | G06/G09 (measured RK3576 boot+AI peak, soft-start, droop, thermal) |
| L1 | C008 | Coilcraft XGL4020-102MEC 1.0uH | G06/G13 (Isat/DCR/thermal pass for 5.1V 3A continuous / 4A peak boost) |
| U8 | C010 | nPM1300 | G08 (AON <=25/50mW) — configure via nPM PowerUP on EK before board |
| U35 | C010b | BQ25895 | Charger/power-path config, TS thresholds, 1S2P charge profile, thermal/current validation |
| U9 | C011 | NDP120 | Full datasheet + dev kit + measured listening power + NDA/licensing |
| U11 | C015 | FCU760KAAMD | G05 (Quectel HW Design + RK3576 BSP driver/firmware/enum) + official LCC land pattern |
| J7 | C017 | Taoglas FXP840.07.0055B | G14 (worn-state tune + antenna keep-out in full shell with battery/speaker) |
| U14 | C019 | Sony IMX415-AAQR-C custom module | G10 (module lens/FOV/FPC pinout/lane/supply/timing from vendor) |
| LS1 | C025 | CUI CMS-15113-078SP-67 | Acoustic EVT: 0.3-0.5cc cavity, port/foam seal, magnet-to-antenna clearance, leak test |
| BT1 | C029 | LP451165 300mAh (R) | G07 (full datasheet, >=2C, IR, cycles, cert) |
| BT2 | C030 | LP451165 300mAh (L) | G07 |
| PCM1 | C032 | Supplier 1S2P pack PCM + protection FETs | Pack supplier drawing: OVP/UVP/OCP/SCP thresholds, FET Rds(on), current rating, NTC placement, UN38.3/MSDS/IEC62133 |
| J1 | C034 | CCP P2578MP01-06C180HT | USB2 eye/contact validation, current/fault/ESD, mating STEP, corrosion/cycle life |
| U36 | C034b | 5V input eFuse/OVP (MPN TBD) | Select MPN for pogo/USB VBUS surge, reverse, OVP, current limit and thermal fault |
| J3 | C038 | Hirose FH26W-33S-0.3SHW(97) | G10/G12 (camera module vendor signs 33-pin pinout, contact orientation, impedance) |

## Allowed next work before layout release

- Keep the functional schematic and generated docs current.
- Complete Phase 1.5: dimensioned mechanical/electrical floorplan + no-route KiCad placement-envelope check.
- Procure missing datasheets/dev kits and run the AON/power bench tests.
- Build only small validation fixtures or dev-kit harnesses; do not start production PCB placement/copper.
