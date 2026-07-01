# V2 chip-down hardware

## Now present: the pre-layout system schematic (no PCB yet)

`ai_glasses_v2_chipdown.kicad_sch` is a **pre-PCB-layout, functional-block system
schematic** for the whole V2 design. It is generated from the master in
[../scripts/chipdown_bom.py](../scripts/chipdown_bom.py) and captures what is
knowable before layout: the power tree, the AON control plane, interface buses,
default-OFF enable pulls, current-sense points, and hidden `NET_META` signal
attributes on global labels. See [../docs/07_schematic_design.md](../docs/07_schematic_design.md).

| File | What |
|---|---|
| `ai_glasses_v2_chipdown.kicad_sch` | one system sheet, 96 blocks, 127 declared nets, **ERC clean** |
| `AI_Glasses_V2.kicad_sym` | generated box symbols |
| `ai_glasses_v2_chipdown.kicad_pro`, `sym-lib-table`, `fp-lib-table` | project + lib tables |

Regenerate from the repo root:

```bash
.venv/bin/python v2_chipdown/scripts/chipdown_bom.py
.venv/bin/python v2_chipdown/scripts/generate_chipdown_sch.py
.venv/bin/python v2_chipdown/scripts/generate_gate_docs.py
.venv/bin/python v2_chipdown/scripts/generate_bom_status.py
```

Then run ERC and exports per [../docs/07_schematic_design.md](../docs/07_schematic_design.md).
Review outputs (netlist / BOM / PDF / SVG / ERC) are in [../reports/](../reports/).
Generated gate docs are [08](../docs/08_signal_dictionary.md),
[09](../docs/09_power_domain_isolation_matrix.md),
[10](../docs/10_bom_status.md), [11](../docs/11_footprint_register.md) and
[12](../docs/12_layout_entry_gate_status.md).

## Still NOT here: PCB layout (by design)

No `.kicad_pcb`, no assigned footprints, no placement/copper. **PCB layout stays
gated behind Gate 0 and the HOLD closure matrix** — batteries proven to fit L/R
temples with swell/foam/FPC room, not stacked over RK3576/PMIC, antenna keep-out
respected, and NDP120/Wi-Fi/battery/camera/FPC data closed (see
[../docs/12_layout_entry_gate_status.md](../docs/12_layout_entry_gate_status.md)).
The Footprint field is intentionally empty; intended packages live in the
`Package` field only and are tracked in [../docs/11_footprint_register.md](../docs/11_footprint_register.md).

## Intended board split at layout (Phase 4)

One system schematic now; four physical boards at layout time (each component
already tagged with its `Board`):

```
front_sensor/   custom 1080p camera + PDM mic array + camera rails + ESD
rk3576_core/    RK3576 + LPDDR4X + eMMC + RK806S + 5V boost + Wi-Fi   (delta off Radxa ref)
aon_power/      nRF54L15 + nPM1300 + NDP120 + BMI270 + charge/gauge/protection   (BUILD FIRST)
power_tree/     Buck + load-switch islands + per-island current sense
```

Build order remains AON board first, then the RK3576 core — never the SoC first.
