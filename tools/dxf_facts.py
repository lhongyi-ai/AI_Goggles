#!/usr/bin/env python3
"""Extract authoritative mechanical facts from official Radxa mechanical DXFs.

Native source: mechanical/radxa_cm4_2d_dxf_v1.20/*.dxf (do not edit).
Native source: mechanical/radxa_cm4_io_2d_dxf_v1.10/*.dxf (do not edit).
Emits ai_context/cm4_mechanical.json (derived; do not hand-edit).

Only facts that can be extracted *reliably* are emitted — currently the CM4
module board outline and the official CM4 IO Board outline from the
BOARD_OUTLINE_00 layer. Precise B2B connector origins must be obtained by
importing the DXF into KiCad as a reference layer and aligning footprints there
(repo CLAUDE.md rule 7), NOT by text-mining this hybrid mechanical+symbol
export.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DXF_DIR = ROOT / "mechanical" / "radxa_cm4_2d_dxf_v1.20"
IO_DXF_DIR = ROOT / "mechanical" / "radxa_cm4_io_2d_dxf_v1.10"
OUT = ROOT / "ai_context" / "cm4_mechanical.json"


def outline_bbox(path: Path):
    import ezdxf

    doc = ezdxf.readfile(str(path))
    msp = doc.modelspace()
    xs: list[float] = []
    ys: list[float] = []

    def add(pt):
        xs.append(pt[0])
        ys.append(pt[1])

    def handle(e):
        if e.dxf.layer != "BOARD_OUTLINE_00":
            return
        t = e.dxftype()
        if t == "LINE":
            add(e.dxf.start)
            add(e.dxf.end)
        elif t == "LWPOLYLINE":
            for v in e.get_points("xy"):
                add(v)
        elif t == "POLYLINE":
            for vertex in e.vertices:
                add(vertex.dxf.location)
        elif t in ("CIRCLE", "ARC"):
            add(e.dxf.center)

    def scan(ent):
        for e in ent.virtual_entities():
            if e.dxftype() == "INSERT":
                scan(e)
            else:
                handle(e)

    for e in msp:
        if e.dxftype() == "INSERT":
            scan(e)
        else:
            handle(e)
    if not xs:
        return None
    return {
        "width_mm": round(max(xs) - min(xs), 2),
        "height_mm": round(max(ys) - min(ys), 2),
        "min_x_mm": round(min(xs), 3),
        "min_y_mm": round(min(ys), 3),
        "max_x_mm": round(max(xs), 3),
        "max_y_mm": round(max(ys), 3),
    }


def text_labels(path: Path, wanted: tuple[str, ...]) -> list[dict[str, object]]:
    import ezdxf

    doc = ezdxf.readfile(str(path))
    labels: list[dict[str, object]] = []
    for e in doc.modelspace():
        if e.dxftype() != "TEXT":
            continue
        text = e.dxf.text
        if not any(token in text for token in wanted):
            continue
        insert = e.dxf.insert
        labels.append({
            "text": text,
            "x_mm": round(float(insert.x), 3),
            "y_mm": round(float(insert.y), 3),
            "note": "Text insertion point only; not a connector footprint origin.",
        })
    return labels


def main() -> int:
    OUT.parent.mkdir(exist_ok=True)
    facts = {
        "source": "Radxa CM4 V1.20 official 2D DXF (mechanical/radxa_cm4_2d_dxf_v1.20)",
        "source_io_board": "Radxa CM4 IO Board V1.10 official 2D DXF "
                           "(mechanical/radxa_cm4_io_2d_dxf_v1.10)",
        "note": "Authoritative CM4 MODULE outline and official CM4 IO Board reference outline. "
                "Carrier outline = project decision. B2B connector origins: align in KiCad via "
                "DXF/STEP import, do not text-mine.",
        "cm4_module_outline": None,
        "cm4_io_board_outline": None,
        "files": {},
        "io_board_files": {},
        "io_board_reference_labels": [],
    }
    errors = []
    for tag in ("TOP", "BOT"):
        p = DXF_DIR / f"Radxa CM4 V1.20 {tag}.dxf"
        if not p.exists():
            errors.append(f"missing: {p}")
            continue
        try:
            bb = outline_bbox(p)
            facts["files"][tag] = {"path": str(p.relative_to(ROOT)), "outline": bb}
            if bb and facts["cm4_module_outline"] is None:
                facts["cm4_module_outline"] = bb
        except Exception as exc:  # rule 10
            errors.append(f"{p}: {type(exc).__name__}: {exc}")
    io_top = IO_DXF_DIR / "RC126_V1.10_20250526_TOP.dxf"
    io_bot = IO_DXF_DIR / "RC126_V1.10_20250526_BOT.dxf"
    for tag, p in (("TOP", io_top), ("BOT", io_bot)):
        if not p.exists():
            errors.append(f"missing: {p}")
            continue
        try:
            bb = outline_bbox(p)
            facts["io_board_files"][tag] = {"path": str(p.relative_to(ROOT)), "outline": bb}
            if bb and facts["cm4_io_board_outline"] is None:
                facts["cm4_io_board_outline"] = bb
            if tag == "TOP":
                facts["io_board_reference_labels"] = text_labels(p, ("Connector_", "J12"))
        except Exception as exc:  # rule 10
            errors.append(f"{p}: {type(exc).__name__}: {exc}")
    if errors:
        facts["errors"] = errors
    OUT.write_text(json.dumps(facts, ensure_ascii=False, indent=2), encoding="utf-8")
    bb = facts["cm4_module_outline"]
    print(f"  wrote ai_context/{OUT.name}: CM4 module outline = "
          f"{bb['width_mm']}x{bb['height_mm']} mm" if bb else
          f"  wrote ai_context/{OUT.name} (no outline extracted)")
    io_bb = facts["cm4_io_board_outline"]
    if io_bb:
        print(f"  wrote ai_context/{OUT.name}: CM4 IO Board outline = "
              f"{io_bb['width_mm']}x{io_bb['height_mm']} mm")
    for e in errors:
        print("  WARN:", e)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
