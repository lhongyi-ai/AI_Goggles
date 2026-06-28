# AI Glasses Carrier — repo conventions

This repo holds **native engineering sources** and **AI-readable derived files**.
Treat them differently.

## Source of truth (authoritative — only edit these for engineering changes)
- `hardware/*.kicad_sch`, `hardware/*.kicad_pcb`, `hardware/*.kicad_pro` — KiCad project
- `data/*.xlsx` — input data (e.g. `data/radxa_cm4_pinout_v1.20.xlsx`, the official Radxa pinout)
- `mechanical/**` — official mechanical refs (`mechanical/radxa_cm4_2d_dxf_v1.20/*.dxf`; later: STEP). CM4 module outline = 40.02 × 54.98 mm. Connector placement: import DXF into KiCad as a reference layer (see rule 7), don't text-mine.
- `scripts/cm4_pinmap.py` — verified CM4 pin assignment working master (Python; documents its source)

## Derived / AI-readable (generated — never hand-edit)
- `ai_context/*.pdf .svg .csv .json .net .txt` — schematic/PCB views, netlist, BOM, ERC, DRC, pinout & pin-assignment dumps
- `config/cm4_v1_pin_assignment.yaml`, `generated/reports/cm4_v1_pin_assignment.{csv,xlsx}` — generated from `scripts/cm4_pinmap.py` via `scripts/build_pin_assignment.py`

## Pipeline
```
hardware/*.kicad_{sch,pcb} ─ kicad-cli ─► ai_context/ {pdf, svg, netlist.net, bom.csv, erc.*, drc.*}
data/*.xlsx                ─ openpyxl  ─► ai_context/ {*.csv, *.json}
scripts/cm4_pinmap.py      ─ (pin map) ─► ai_context/ {pin_assignment.csv/json}
```
Regenerate everything with: **`./tools/build_ai_context.sh`** (export-only; never edits native sources).

## Division of labor
- **Claude:** analyse nets/components, cross-check pin assignment vs `data/` pinout, check BOM, run ERC/DRC, edit native sources or helper scripts, write review reports.
- **KiCad (human):** open the project, schematic graphics, PCB placement/copper/diff-pairs, 3D assembly, manufacturing files.

## Rules
1. Use `ai_context/` to understand schematic, PCB, BOM, pin assignment, ERC, DRC.
2. Native KiCad + XLSX files are authoritative.
3. Never treat a PDF/CSV/JSON/SVG as the editable source of truth.
4. Any engineering change goes into the native source file (or its generator: `scripts/cm4_pinmap.py`, `scripts/carrier_bom.py`, `scripts/generate_carrier_board.py`).
5. After every change run `./tools/build_ai_context.sh`.
6. Run ERC/DRC and report the exact command, exit code, and result.
7. Do not claim a graphical layout is correct from parsing `.kicad_pcb` text alone — only KiCad/3D confirms placement, copper, clearances.
8. Do not overwrite verified pin assignments without documenting the source + reason (`scripts/cm4_pinmap.py` records both).
9. Do not hand-edit generated files inside `ai_context/`.
10. If a file cannot be parsed, report the exact path, command attempted, and error message.

## ERC/DRC commands (KiCad 10.0.4; kicad-cli not on PATH — full path below)
```
KCLI=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli
"$KCLI" sch erc --severity-all --format report -o ai_context/erc.report.txt hardware/ai_glasses_carrier.kicad_sch
"$KCLI" pcb drc --severity-all --format report -o ai_context/drc.report.txt hardware/ai_glasses_carrier.kicad_pcb
```
Known-benign at the current pre-layout stage: ERC `lib_symbol_issues` / `isolated_pin_label` (auto-generated placeholder box symbols, single-node nets); DRC `lib_footprint_mismatch` (generated mounting holes). These clear once real library symbols/footprints replace the generated placeholders.

## Pin-freeze gate (requirements §3.3)
`scripts/check_pin_freeze.py` reads `config/cm4_v1_pin_assignment.yaml`. PCB layout may not begin until `status: FROZEN`. Pins are filled & verified (status `REVIEW`); the gate is currently blocked only by the §8.3 procurement TBDs in `scripts/cm4_pinmap.py:OPEN_TBD`.

## Environment
Python venv at `.venv` (has PyYAML, pydantic, pytest, openpyxl). Run scripts as `.venv/bin/python scripts/...`.
