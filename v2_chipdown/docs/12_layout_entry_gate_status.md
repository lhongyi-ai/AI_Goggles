# 12 — Layout-entry gate status and HOLD closure

> Generated 2026-07-01 from `scripts/chipdown_bom.py`. This is the go/no-go record for entering PCB layout.

## Verdict

**PCB layout is NOT released.** The schematic is ERC-clean and useful for review, procurement and bench planning, but Gate 0/G05/G07/G08/G10/G12 remain HOLD.

Current BOM state: **96 components** — 58 Fit · 12 HOLD · 19 DNP · 7 TBD; **12 HOLD** components.

## Gate table

| Gate | Topic | Status | Close condition | Components currently referencing it |
|---|---|:--:|---|---|
| G00 | Mechanical/battery layout gate | HOLD | real cell fit, swell room, hinge FPC, antenna keep-out, no battery over RK3576/PMIC | - |
| G01 | RK3576 identity + HDG | OPEN | full datasheet/HDG/ball map, package drawing, reference-design delta plan | U1, Y1 |
| G02 | LPDDR4X | OPEN | verified MPN, topology, placement, length report, DDR review | U3 |
| G03 | RK806S PMIC | OPEN | exact MPN, rails, inductors/caps, sequence/timing with RK3576 | U2 |
| G04 | eMMC/boot | OPEN | MPN, BSP/bootloader, cold boot and power-loss recovery plan | U4 |
| G05 | Wi-Fi module | HOLD | Quectel FCU760K Hardware Design, official LCC land pattern, RK3576 BSP/firmware enumeration | U11, U12, U13 |
| G06 | High-power transient sizing | OPEN | RK3576 boot/AI peak, boost soft-start, 1S droop, Wi-Fi/camera/audio peaks | U6, L1, U12 |
| G07 | LP451165 + 1S2P pack | HOLD | formal datasheet, discharge curve, IR/cycle/cert, pairing/fuse/NTC/current-share tests | BT1, BT2 |
| G08 | AON power | HOLD | nPM1300 EK config, NDP120 kit, measured AON <=25 mW avg / <=50 mW ceiling | U8 |
| G09 | Thermal/boost droop | OPEN | RK3576 burst thermal path, TPS61088/RK806 droop and UVLO margin | U6 |
| G10 | Camera module | HOLD | final IMX415 module FPC pinout, lens/FOV, lane count, rail current/timing | U14 |
| G11 | Mic/audio topology | OPEN | mic coordinates, ports, wind/AEC/beamforming, NDP120 wake path | MK1, MK2, MK3, MK4 |
| G12 | FPC/hinge | HOLD | front FPC pin count, impedance, bend radius, hinge life and interference | J3, J4 |
| G13 | Magnetics/passives height | OPEN | inductor Isat/DCR/height, cap derating, wearable Z limits | L1 |
| G14 | RF/worn tune | OPEN | antenna SKU, keep-out, matching in shell and worn condition | - |
| G15 | Passive/manufacturing BOM | OPEN | expanded R/C/L MPNs, derating, lifecycle and alternates | - |

## HOLD closure pack status

| Item | Status | Close condition | Source folder | Blocks |
|---|:--:|---|---|---|
| NDP120 | HOLD | Full datasheet, package drawing/land pattern, rail map, reset/strap sequence, dev kit, model toolchain/licensing, measured listening power | AI_Glasses_HOLD_Closure_Pack/01_NDP120 | Blocks U9 and wake-audio freeze |
| Wi-Fi FCU760K | HOLD | Quectel Hardware Design, official LCC land pattern/3D/height, antenna SKU, RK3576 BSP driver + firmware enumeration | AI_Glasses_HOLD_Closure_Pack/02_WiFi_FCU760K | Blocks U11/J7 RF and USB2/PCM freeze |
| LP451165 cell | HOLD | Formal supplier datasheet, discharge curves, IR, cycle life, high-rate limit, certification, swell envelope | AI_Glasses_HOLD_Closure_Pack/03_Battery_LP451165_1S2P | Blocks BT1/BT2 and mechanical Gate 0 |
| 1S2P pack | HOLD | Pairing rules, fusing, NTC placement, current-share shunts, protection scheme, charge/gauge profiling | AI_Glasses_HOLD_Closure_Pack/03_Battery_LP451165_1S2P | Blocks G07/G08/G00 |
| Camera power current | HOLD | Custom IMX415 module rail currents/timing/FPC pinout beyond bare sensor datasheet | AI_Glasses_HOLD_Closure_Pack/04_IMX415 | Blocks U14, CAM rails and G10 |
| Battery bay dimensions | HOLD | Real dummy-cell assembly, foam/swell allowance, hinge FPC path, antenna and speaker interference | AI_Glasses_HOLD_Closure_Pack/06_Mechanical_Fit_Check | Blocks PCB layout start |

## HOLD components

| Ref | BOM ID | Value | Gate |
|---|---|---|---|
| U2 | C002 | RK806S-5 | G03 (RK806S MPN/inductors/caps/timing per Radxa/Rockchip FAE) |
| U3 | C003 | LPDDR4X 4GB (MPN TBD) | G02 (LPDDR4X MPN/topology/placement, DDR review + length report) |
| U4 | C004 | eMMC 5.1 32GB (MPN TBD) | G04 (eMMC MPN + BSP/bootloader; cold-boot + power-loss recovery) |
| U6 | C007 | TPS61088 | G06/G09 (measured RK3576 boot+AI peak, soft-start, droop, thermal) |
| U8 | C010 | nPM1300 | G08 (AON <=25/50mW) — configure via nPM PowerUP on EK before board |
| U9 | C011 | NDP120 | Full datasheet + dev kit + measured listening power + NDA/licensing |
| U11 | C015 | FCU760KAAMD | G05 (Quectel HW Design + RK3576 BSP driver/firmware/enum) + official LCC land pattern |
| U14 | C019 | IMX415-AAQR module (custom FPC) | G10 (module lens/FOV/FPC pinout/lane/supply/timing from vendor) |
| BT1 | C029 | LP451165 300mAh (R) | G07 (full datasheet, >=2C, IR, cycles, cert) |
| BT2 | C030 | LP451165 300mAh (L) | G07 |
| J3 | C038 | Hirose FH26W 0.3mm FPC | G12 (pin count from final cam lane/mic/power split) |
| J4 | C039 | Custom hinge FPC 6-10mm | G12 (impedance, bend radius, life, hinge interference) |

## Allowed next work before layout release

- Keep the functional schematic and generated docs current.
- Procure missing datasheets/dev kits and run the AON/power bench tests.
- Build only small validation fixtures or dev-kit harnesses; do not start production PCB placement/copper.
