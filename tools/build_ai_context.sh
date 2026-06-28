#!/usr/bin/env bash
# Regenerate ai_context/ (AI-readable derived views) from the native sources.
#
#   hardware/*.kicad_sch ─┐                        ┌─ schematic.pdf / .svg
#   hardware/*.kicad_pcb ─┼─ kicad-cli ───────────►├─ netlist.net / bom.csv
#                         │                        ├─ erc.report.txt / .json
#                         │                        └─ drc.report.txt / .json
#   data/*.xlsx ──────────┴─ openpyxl ────────────►  *.csv / *.json
#   scripts/cm4_pinmap.py ── (verified pin map) ──►  pin_assignment.csv / .json
#   config/passive_bom_freeze.yaml ───────────────►  passive_bom_freeze.csv / .json
#
# This script is EXPORT-ONLY: it never edits the native KiCad/XLSX sources.
# It prints every command + exit code (rule 6) and tees a BUILD_LOG.txt.
# Do not hand-edit anything under ai_context/ (rule 9).
set -u

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT" || exit 2

KCLI="${KICAD_CLI:-/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli}"
PY="${PYTHON:-$ROOT/.venv/bin/python}"
SCH="hardware/ai_glasses_carrier.kicad_sch"
PCB="hardware/ai_glasses_carrier.kicad_pcb"
OUT="ai_context"
LOG="$OUT/BUILD_LOG.txt"

mkdir -p "$OUT"
: > "$LOG"
rc_overall=0

# run "<label>" cmd args... : echo, run, capture exit code, tee to log.
run() {
  local label="$1"; shift
  echo "── $label"
  echo "   \$ $*"
  "$@" >>"$LOG" 2>&1
  local rc=$?
  echo "   exit=$rc"
  { echo "## $label"; echo "\$ $*"; echo "exit=$rc"; echo; } >> "$LOG"
  [ $rc -ne 0 ] && rc_overall=1
  return $rc
}

if [ ! -x "$KCLI" ]; then
  echo "ERROR: kicad-cli not found/executable at: $KCLI" | tee -a "$LOG"
  echo "       set KICAD_CLI=/path/to/kicad-cli and retry." | tee -a "$LOG"
  exit 2
fi

echo "=== build_ai_context: $(date) ===" | tee -a "$LOG"
"$KCLI" version | tee -a "$LOG"
echo

# ── Schematic exports ───────────────────────────────────────────────────────
if [ -f "$SCH" ]; then
  rm -f "$OUT/erc.report.txt" "$OUT/erc.json"
  run "sch: PDF"     "$KCLI" sch export pdf     --output "$OUT/schematic.pdf"  "$SCH"
  run "sch: SVG"     "$KCLI" sch export svg     --output "$OUT/schematic-svg"  "$SCH"
  run "sch: netlist" "$KCLI" sch export netlist --output "$OUT/netlist.net"    "$SCH"
  run "sch: BOM"     "$KCLI" sch export bom     --output "$OUT/bom.csv" \
        --fields "Reference,Value,Footprint,QUANTITY,DNP" --group-by Value "$SCH"
  run "sch: ERC (report)" "$KCLI" sch erc --severity-all --format report \
        --output "$OUT/erc.report.txt" "$SCH"
  run "sch: ERC (json)"   "$KCLI" sch erc --severity-all --format json \
        --output "$OUT/erc.json" "$SCH"
else
  echo "WARN: $SCH not found — skipping schematic exports" | tee -a "$LOG"
fi

# ── PCB exports ─────────────────────────────────────────────────────────────
if [ -f "$PCB" ]; then
  rm -f "$OUT/drc.report.txt" "$OUT/drc.json"
  run "pcb: SVG" "$KCLI" pcb export svg --output "$OUT/pcb.svg" \
        --layers "Edge.Cuts,F.Cu,B.Cu,F.Silkscreen,F.Fab" --page-size-mode 2 "$PCB"
  run "pcb: DRC (report)" "$KCLI" pcb drc --severity-all --format report \
        --output "$OUT/drc.report.txt" "$PCB"
  run "pcb: DRC (json)"   "$KCLI" pcb drc --severity-all --format json \
        --output "$OUT/drc.json" "$PCB"
else
  echo "WARN: $PCB not found — skipping PCB exports" | tee -a "$LOG"
fi

# ── XLSX -> CSV/JSON + verified pin assignment ──────────────────────────────
run "xlsx+pinmap -> csv/json" "$PY" tools/xlsx_to_ai_context.py
run "passive BOM freeze -> csv/json" "$PY" scripts/audit_passive_bom_freeze.py --write --ai-context

# ── Mechanical DXF -> facts JSON (CM4 module outline) ───────────────────────
if ls mechanical/radxa_cm4_2d_dxf_v1.20/*.dxf >/dev/null 2>&1; then
  run "dxf -> cm4_mechanical.json" "$PY" tools/dxf_facts.py
fi

# ── ERC/DRC headline counts (parsed from the JSON reports) ──────────────────
echo
echo "=== ERC / DRC summary ==="
"$PY" - "$OUT" <<'PYEOF' | tee -a "$LOG"
import json, sys
from pathlib import Path
out = Path(sys.argv[1])
for kind, f in (("ERC", out/"erc.json"), ("DRC", out/"drc.json")):
    if not f.exists():
        print(f"{kind}: (no json report)"); continue
    try:
        d = json.loads(f.read_text())
    except Exception as e:
        print(f"{kind}: ERROR parsing {f}: {e}"); continue
    viol = d.get("violations")
    if viol is None:  # some versions nest per-sheet/unit
        viol = [v for s in d.get("sheets", d.get("items", [])) for v in s.get("violations", [])]
    sev = {}
    for v in viol or []:
        s = v.get("severity", "?"); sev[s] = sev.get(s, 0) + 1
    total = len(viol or [])
    detail = ", ".join(f"{k}={v}" for k, v in sorted(sev.items())) or "none"
    print(f"{kind}: {total} violation(s) [{detail}]")
PYEOF

echo
if [ $rc_overall -eq 0 ]; then
  echo "build_ai_context: OK (all export commands exit 0). Log: $LOG"
else
  echo "build_ai_context: completed WITH ERRORS (see exit codes above). Log: $LOG"
fi
exit $rc_overall
