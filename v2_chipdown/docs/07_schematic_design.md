# 07 — Pre-Layout System Schematic (design record)

This is the design record for the V2 chip-down **pre-PCB-layout** schematic. It
captures the three decision sets — **Phase-1 AON selection**, **AON power
budget**, **Phase-3 power tree** — as an actual, ERC-clean, netlist-verified
KiCad schematic, and states plainly what is intentionally **not** done yet
because it belongs to PCB layout.

## What was built (and how it is verified)

| Artifact | Path |
|---|---|
| Component + net master (source of truth) | `scripts/chipdown_bom.py` |
| Schematic generator | `scripts/generate_chipdown_sch.py` |
| KiCad schematic (one system sheet) | `hardware/ai_glasses_v2_chipdown.kicad_sch` |
| Symbol library / project / lib tables | `hardware/AI_Glasses_V2.kicad_sym`, `.kicad_pro`, `sym-lib-table`, `fp-lib-table` |
| ERC report | `reports/erc.report.txt` |
| Netlist (KiCad) | `reports/ai_glasses_v2.net` |
| BOM (fields: Reference, Value, BOM_ID, Board, Assembly, Priority, Package, Gate) | `reports/ai_glasses_v2_bom.csv` |
| Schematic PDF / SVG | `reports/output/ai_glasses_v2_chipdown_schematic.pdf`, `.svg` |

**Regenerate:**
```bash
.venv/bin/python v2_chipdown/scripts/chipdown_bom.py          # validate master
.venv/bin/python v2_chipdown/scripts/generate_chipdown_sch.py # emit schematic
KCLI=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli
"$KCLI" sch erc --severity-all --format report -o v2_chipdown/reports/erc.report.txt \
    v2_chipdown/hardware/ai_glasses_v2_chipdown.kicad_sch
```

**Status:** 96 components (58 Fit / 12 HOLD / 19 DNP / 7 TBD), 127 declared nets.
**ERC = 0 errors, 0 warnings, 0 violations** (KiCad 10.0.4).
The netlist was parsed back to confirm real connectivity (not just labels): e.g.
`SOC_SAFE_TO_OFF` joins RK3576 (U1) + nRF (U7) + hinge FPC (J4); `SOC_PWR_EN`
joins nRF (U7) + TPS61088 (U6) + default-off pull-down (R11); the pack path
runs cell branches through `RS2/RS3` into `BAT_P`, then `RS1` into nPM1300
`NPM_VBAT`; `VSYS→RS4→SOC_IN` feeds the SoC boost; `PDM_WAKE_CLK` joins the
wake mic (MK1) + NDP120 (U9) + front FPC (J3).

> **Honesty note.** This is a *functional-block* schematic: parts whose ball map
> / datasheet is not in hand (RK3576, RK806S, LPDDR4X, eMMC, NDP120, the custom
> IMX415 module, the Wi-Fi module) are drawn with only their architecturally
> defined interface pins. The RK806S→RK3576 rail names are the Radxa reference
> set and freeze only at G02/G03. The Footprint field is deliberately **empty** —
> footprints are a layout deliverable (see "Deferred to layout").

---

## 1. Phase-1 AON selection (frozen for EVT)

| Function | Part | Ref | Status | Why this, not the alternative |
|---|---|---|---|---|
| BLE MCU / state machine | **nRF54L15-QFN48** | U7 | Fit | vs nRF52840 (older platform) / nRF5340 (dual-core overkill — voice NN lives in the DSP). 1.5 MB NVM / 256 KB RAM headroom; QFN48 for a debuggable EVT, WLCSP shrink later. |
| AON charger/gauge/PMIC | **nPM1300** | U8 | HOLD | Integrates 1S charge + Power-Path + Fuel Gauge + 2×Buck + LDO/Load-Switch + Ship/Hibernate. Powers the **AON world only** — never the RK3576 peak path. |
| Always-on audio DSP | **NDP120** | U9 | HOLD | Ultra-low-power wake-word off RK3576. HOLD until full datasheet, rails/sequence, PDM/I²S detail, model tools, wake-word licensing, measured listening power, MOQ/lead. Bypass + DNP kept. |
| 6-axis IMU | **BMI270** | U10 | Fit | Low-power motion-interrupt wake for wearables. |

**Audio topology (no PDM-clock contention).** One dedicated **wake mic** (MK1) →
NDP120; NDP120 wakes nRF over `DSP_WAKE`. **Two array mics** (MK2/MK3) → RK3576
PDM for beamforming; **4th mic (MK4) is footprint-only/DNP** until array + wind
tests decide. nRF↔NDP120 carries `DSP_SPI_*` + `WAKE/READY/FAULT/RESET`. The
wake mic runs in the AON audio domain so Deep Off can capture without RK3576.

**Charger/gauge scope is explicit in the tree:** nPM1300 supplies nRF, NDP120,
IMU, gauge logic, part of the always-on mic domain, buttons/sensors. The RK3576
compute island has its **own** high-power path (TPS61088 → RK806S).

---

## 2. AON power budget (turn "20–50 mW" into a measurable budget)

| AON load | Design budget | Verify |
|---|--:|---|
| nRF54L15 (BLE conn + state machine) | 1–5 mW avg | measure adv / conn / notify / sleep separately |
| NDP120 + wake mic | 5–15 mW | measure real continuous listening (no datasheet typ.) |
| IMU low-power motion | <1 mW | motion-interrupt only, no continuous high ODR |
| nPM1300 self + conversion loss | <1 mW | at real load |
| Other sensors / pull-ups / leakage | 1–3 mW | incl. FPC + cross-domain IO leakage |
| BLE burst headroom | 5–10 mW | connect + TX transients |
| **AON normal average** | **10–25 mW target** | worn, normal |
| **AON design ceiling** | **50 mW** | must not be the normal average |

So **20–50 mW is the ceiling band; the real target is 10–25 mW average**, and
every mode is measured for **energy**, not just instantaneous current. On-board
verification uses shunt `RS1` (main) + `U25` (INA238) — in Deep Off the gated
islands are off, so the main path reads AON-only; the nPM1300 fuel gauge
cross-checks.

**Dev-board bring-up (before trusting the schematic):** nRF54L15 DK, nPM1300 EK
(configure via nPM PowerUP, export settings), NDP120 kit/module, real PDM mics,
BMI270 breakout, Otii Arc / Joulescope.

### Gate 1 (AON board) — must all pass
AON average ≤ 25 mW, worst ≤ 50 mW · voice/button/BLE/IMU all wake reliably ·
acceptable false-wake rate · **100** RK3576 on/off cycles with no lock-up ·
RK3576-off leakage at target · low-battery **blocks** RK3576 start · no reverse
feed into a powered-down RK3576 via GPIO.

---

## 3. Phase-3 power tree (Buck + Load-Switch, on the schematic)

```
2×LP451165 (1S2P) ─F1/F2─► BAT_P ─► nPM1300 (VBAT) ─► VSYS
                                        │  BUCK1 ─► AON_1V8   (always on: nRF IO/IMU/DSP/mics)
                                        │  BUCK2 ─► AON_3V3   (always on: nRF RF/DSP/mics)
 BATR/L ─F1/F2─RS2/RS3─► BAT_P ─RS1─► NPM_VBAT
 VSYS ─┬─[RS4]─► SOC_IN  ─► TPS61088 ─► SOC_5V ─► RK806S ─► RK3576/DDR/eMMC rails
       ├─[RS5]─► WIFI_IN ─► TPS62825 ─► WIFI_3V3 ─► TPS22917 ─► module
       ├─[RS6]─► AUDIO_IN ─► TPS22917 ─► AUDIO_PWR ─► MAX98360A
       ├────────► TPS62840 ─► CAM_1V1 ─RS7─► CAM_1V1_S
       └────────► TLV75529 ─► CAM_2V9 ─RS9─► CAM_2V9_S
 AON_1V8 ─► TPS22917 ─► CAM_1V8_SW ─RS8─► CAM_1V8_S
```

**Rules honoured:** camera/MCU/IMU/mics/radio run off 1S via Buck/Load-Switch —
**only the RK3576 island gets a boost**, and only if RK806S input truly needs
5 V (else drop the boost). Every expensive rail sits behind an nRF-controlled
load switch. AON Buck (nPM1300) is the low-Iq 24/7 dominator of Deep Off.

### Per-island regulators

| Island | Regulator | Ref | Status | Rail |
|---|---|---|---|---|
| RK3576 boost | TPS61088 (+L1) | U6/L1 | HOLD | SOC_5V |
| SoC PMIC | RK806S-5 | U2 | HOLD | CPU/GPU/NPU/LOGIC/DDR/DDRIO/1V8/3V3 |
| Camera 1.1 V | TPS62840 (+L3) | U15/L3 | Fit | CAM_1V1 |
| Camera 1.8 V | TPS22917 (from AON_1V8) | U17 | Fit | CAM_1V8_SW |
| Camera 2.9 V | TLV75529 | U16 | Fit | CAM_2V9 |
| Wi-Fi | TPS62825 (+L2) → TPS22917 | U12/L2/U13 | Fit | WIFI_3V3(_SW) |
| Audio | TPS22917 | U21 | Fit | AUDIO_PWR |

### Control lines on the schematic (nRF54L15 is master)

| Net | Direction | Purpose |
|---|---|---|
| `SOC_PWR_EN` | nRF → TPS61088 EN | power the compute island |
| `SOC_5V_PGOOD` | TPS61088 PG → nRF | boost good |
| `PMIC_PWRON` | nRF → RK806S | sequence RK3576 rails on |
| `SOC_SHUTDOWN_REQ` | RK3576 → nRF | SoC asks to power down |
| `SOC_SAFE_TO_OFF` | RK3576 → nRF | Linux synced, safe to cut |
| `SOC_ALIVE` / `SOC_FAULT` | RK3576 → nRF | liveness / fault |
| `CAM_1V1_EN`/`CAM_1V8_EN`/`CAM_2V9_EN` | nRF → regs/LS | camera island |
| `WIFI_BUCK_EN`/`WIFI_LS_EN`/`WIFI_CHIP_EN` | nRF → buck/LS/module | Wi-Fi on-demand |
| `AUDIO_LS_EN`/`AUDIO_AMP_SD` | nRF → LS/amp | audio gated + amp shutdown |
| `DSP_RESET_L`/`DSP_WAKE`/`DSP_READY`/`DSP_FAULT` | nRF ↔ NDP120 | wake handshake |

**Safe shutdown sequence (never cut Linux without warning):**
```
nRF asserts SOC_SHUTDOWN_REQ
 → Linux stops recording + sync()s the filesystem
 → RK3576 asserts SOC_SAFE_TO_OFF
 → nRF drops Wi-Fi + camera load switches
 → nRF deasserts SOC_PWR_EN (SOC_5V off)
```

### Per-island current sense (mandatory)

Series shunts feed INA238 monitors. **EVT-A:** all populated. **EVT-B /
production:** shunt pads kept (0 Ω), only the main `U25` optional, the rest DNP.

| Sense | Shunt | Value rule | INA |
|---|---|---|---|
| System / AON (Deep Off) | RS1 (BAT_P→NPM_VBAT) | 10 mΩ; production-kept sense path | U25 |
| Left cell branch | RS2 (BATL_F→BAT_P) | 10 mΩ; current-share check | U26 |
| Right cell branch | RS3 (BATR_F→BAT_P) | 10 mΩ; current-share check | U27 |
| RK3576 island | RS4 (VSYS→SOC_IN) | 5–20 mΩ (2 A×10 mΩ=20 mV; avoid boost UVLO) | U28 |
| Wi-Fi island | RS5 (VSYS→WIFI_IN) | 20–100 mΩ | U29 |
| Audio island | RS6 (VSYS→AUDIO_IN) | 20–100 mΩ | U30 |
| Camera DVDD | RS7 (CAM_1V1→CAM_1V1_S) | 100 mΩ Kelvin; DVDD ~250 mA | U31 |
| Camera IOVDD | RS8 (CAM_1V8_SW→CAM_1V8_S) | 100 mΩ Kelvin; IOVDD ~3 mA | U32 |
| Camera AVDD | RS9 (CAM_2V9→CAM_2V9_S) | 100 mΩ Kelvin; AVDD ~156 mA | U33 |

Record **peak + average + duration + energy-per-event** at each, and watch **1S
droop** at the RK3576 AI-burst peak (boost/PMIC UVLO risk).

### Passive specs locked pre-layout (V1 audit discipline)
USB-C CC1/CC2 = **5.1 kΩ 1%** (R1/R2). AON + camera + SoC-PMIC I²C pull-ups =
**2.2 kΩ 1%** (R3–R6, R9/R10) — confirm against each bus's total capacitance at
layout. High-power enables have **100 kΩ pull-downs** (R11–R20) so RK3576,
camera, Wi-Fi and audio default OFF before nRF firmware runs. Decoupling
X7R/X5R and ≥10 V-on-5 V rules apply when the manufacturing passive BOM is
expanded at G15.

---

## Deferred to PCB layout / still HOLD (intentionally NOT done)

Per the instruction to do only what precedes PCB layout, the following are **not**
in this schematic and must not be treated as done:

- **No `.kicad_pcb`** — placement, copper, diff-pair/impedance (MIPI 100 Ω, USB2
  90 Ω), stack-up, DRC. Gated behind **Gate 0 (mechanical)**: prove the two
  LP451165 cells fit L/R temples with swell/foam/FPC room, not stacked over
  RK3576/PMIC, antenna keep-out respected.
- **Phase 1.5 floorplan before routing** — create a no-route mechanical/electrical
  KiCad floorplan with board outlines, RK3576/LPDDR/RK806/eMMC/Wi-Fi/boost
  inductor/FPC connector placement envelopes, LP451165 3D/envelope blocks,
  speaker and antenna keep-outs. If it does not fit, change architecture before
  PCB layout. See [13_mechanical_electrical_floorplan.md](13_mechanical_electrical_floorplan.md).
- **No footprints assigned** (Footprint field empty; intended package in the
  `Package` field only). Real footprints are created at layout.
- **Ball-level nets** for RK3576/RK806S/LPDDR4X/eMMC/NDP120/IMX415-module/Wi-Fi
  module — start as a *delta off the Radxa reference* once G01/G02/G03/G05/G10
  documents are in hand.
- **HOLD parts stay HOLD:** NDP120 (datasheet+kit+power), Wi-Fi module (RK3576
  BSP), LP451165 + 1S2P pack (real datasheet + discharge curves + matching/NTC),
  TPS61088 (measured RK3576 peak), camera rail currents (custom IMX415 module),
  battery-bay dimensions (real cell + swell fit).
- **Manufacturing passive expansion** — the locked pre-layout pull-ups,
  pull-downs and sense shunts are present, but the full decoupling/passive MPN
  table still expands at G15.

See [08_signal_dictionary.md](08_signal_dictionary.md) for every net's signal
attributes, [09_power_domain_isolation_matrix.md](09_power_domain_isolation_matrix.md)
for reverse-feed review, [10_bom_status.md](10_bom_status.md) for Fit/HOLD/DNP/TBD,
[11_footprint_register.md](11_footprint_register.md) for package readiness and
[12_layout_entry_gate_status.md](12_layout_entry_gate_status.md) for the layout
go/no-go verdict.
