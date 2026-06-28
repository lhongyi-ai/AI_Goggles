#!/usr/bin/env python3
"""Audit the pre-layout passive/protection BOM freeze table.

This checks that every passive/protection ref used by the schematic BOM is
covered by config/passive_bom_freeze.yaml and emits review artifacts.
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path

import yaml

try:
    from .carrier_bom import COMPONENTS
    from .kicad_tools import PROJECT_ROOT, status
except ImportError:
    from carrier_bom import COMPONENTS
    from kicad_tools import PROJECT_ROOT, status


CONFIG = PROJECT_ROOT / "config" / "passive_bom_freeze.yaml"
CSV_OUT = PROJECT_ROOT / "generated" / "reports" / "passive_bom_freeze.csv"
JSON_OUT = PROJECT_ROOT / "generated" / "reports" / "passive_bom_freeze.json"
DOC_OUT = PROJECT_ROOT / "docs" / "passive_bom_freeze_2026-06-28.md"
AI_CSV_OUT = PROJECT_ROOT / "ai_context" / "passive_bom_freeze.csv"
AI_JSON_OUT = PROJECT_ROOT / "ai_context" / "passive_bom_freeze.json"

PROTECTION_ARRAY_REFS = {"U2", "U16", "U5"}
TARGET_PREFIXES = ("R", "C", "L", "D", "FB")

COMMON_REQUIRED = {
    "refs",
    "category",
    "value",
    "role",
    "package",
    "footprint",
    "temp_range_C",
    "manufacturer",
    "mpn",
    "lcsc",
    "procurement_status",
}

CATEGORY_REQUIRED = {
    "resistor": {"tolerance", "power_rating_W_min"},
    "capacitor": {"dielectric", "tolerance"},
    "inductor": {"saturation_current_A_min", "rms_current_A_min", "dcr_mohm_max"},
    "ferrite_bead": {"impedance_ohm_at_100MHz", "current_rating_A_min"},
    "rf_inductor": {"inductance_initial", "q_requirement"},
    "tvs": {"vrwm_V"},
    "esd": {"capacitance_pF_max", "vrwm_V_min"},
    "esd_array": {"channels", "capacitance_pF_max", "vrwm_V_min"},
    "led": {"current_mA_nominal"},
}

CSV_COLUMNS = [
    "ref",
    "schematic_value",
    "schematic_group",
    "family",
    "category",
    "freeze_value",
    "role",
    "package",
    "footprint",
    "manufacturer",
    "mpn",
    "lcsc",
    "procurement_status",
    "rating_summary",
    "note",
]


def load_config() -> dict:
    with CONFIG.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def component_by_ref() -> dict[str, object]:
    return {comp.ref: comp for comp in COMPONENTS}


def is_target_ref(ref: str) -> bool:
    return ref in PROTECTION_ARRAY_REFS or ref.startswith(TARGET_PREFIXES)


def target_refs() -> set[str]:
    return {comp.ref for comp in COMPONENTS if is_target_ref(comp.ref)}


def rating_summary(family: dict) -> str:
    keys = [
        "tolerance",
        "tempco",
        "power_rating_W_min",
        "voltage_rating_V",
        "voltage_rating_V_min",
        "dielectric",
        "saturation_current_A_min",
        "rms_current_A_min",
        "dcr_mohm_max",
        "impedance_ohm_at_100MHz",
        "current_rating_A_min",
        "capacitance_pF_max",
        "vrwm_V",
        "vrwm_V_min",
        "peak_pulse_power_W_min",
    ]
    parts = []
    for key in keys:
        if key in family:
            parts.append(f"{key}={family[key]}")
    return "; ".join(parts)


def build_records() -> tuple[list[dict[str, object]], list[str]]:
    data = load_config()
    families = data.get("families") or {}
    comps = component_by_ref()
    wanted = target_refs()
    problems: list[str] = []
    records: list[dict[str, object]] = []
    seen: dict[str, str] = {}

    for family_id, family in families.items():
        missing = sorted(COMMON_REQUIRED - set(family))
        if missing:
            problems.append(f"{family_id}: missing required field(s): {', '.join(missing)}")
        category = family.get("category")
        category_missing = sorted(CATEGORY_REQUIRED.get(str(category), set()) - set(family))
        if category_missing and family.get("procurement_status") != "TUNE_OR_EVT_SELECT":
            problems.append(f"{family_id}: missing {category} field(s): {', '.join(category_missing)}")

        if family.get("procurement_status") == "LOCKED_CANDIDATE":
            for key in ("lcsc_url",):
                if key not in family:
                    problems.append(f"{family_id}: LOCKED_CANDIDATE missing {key}")

        for ref in family.get("refs") or []:
            ref = str(ref)
            if ref in seen:
                problems.append(f"{ref}: appears in both {seen[ref]} and {family_id}")
            seen[ref] = family_id
            if ref not in comps:
                problems.append(f"{family_id}: ref {ref} not found in scripts/carrier_bom.py")
                continue
            comp = comps[ref]
            records.append(
                {
                    "ref": ref,
                    "schematic_value": comp.value,
                    "schematic_group": comp.group,
                    "family": family_id,
                    "category": family.get("category", ""),
                    "freeze_value": family.get("value", ""),
                    "role": family.get("role", ""),
                    "package": family.get("package", ""),
                    "footprint": family.get("footprint", ""),
                    "manufacturer": family.get("manufacturer", ""),
                    "mpn": family.get("mpn", ""),
                    "lcsc": family.get("lcsc", ""),
                    "procurement_status": family.get("procurement_status", ""),
                    "rating_summary": rating_summary(family),
                    "note": family.get("note", ""),
                }
            )

    missing_refs = sorted(wanted - set(seen))
    extra_refs = sorted(set(seen) - wanted)
    if missing_refs:
        problems.append("Missing passive freeze coverage for: " + ", ".join(missing_refs))
    if extra_refs:
        problems.append("Freeze table includes non-target refs: " + ", ".join(extra_refs))

    records.sort(key=lambda row: row["ref"])
    return records, problems


def write_csv(path: Path, records: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_COLUMNS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(records)


def write_json(path: Path, records: list[dict[str, object]], problems: list[str]) -> None:
    data = load_config()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "metadata": data.get("metadata", {}),
                "policy": data.get("policy", {}),
                "records": records,
                "problems": problems,
            },
            ensure_ascii=False,
            indent=1,
            default=str,
        ),
        encoding="utf-8",
    )


def build_markdown(records: list[dict[str, object]], problems: list[str]) -> str:
    data = load_config()
    counts = Counter(str(row["procurement_status"]) for row in records)
    lines = [
        "# Passive BOM Freeze",
        "",
        "Date: 2026-06-28",
        "",
        f"Status: `{data.get('metadata', {}).get('status', 'UNKNOWN')}`",
        "",
        "Scope: all schematic R/C/L/FB/D passives plus MIPI/USB protection arrays `U2`, `U16`, `U5`.",
        "",
        "## Summary",
        "",
        f"- Covered refs: {len(records)}",
        *[f"- {key}: {value}" for key, value in sorted(counts.items())],
        "",
        "## Records",
        "",
        "| Ref | Family | Value | Package | MPN | LCSC | Status |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in records:
        lines.append(
            f"| `{row['ref']}` | `{row['family']}` | {row['freeze_value']} | "
            f"{row['package']} | `{row['mpn']}` | `{row['lcsc']}` | `{row['procurement_status']}` |"
        )

    if problems:
        lines.extend(["", "## Problems", "", *[f"- {p}" for p in problems]])
    else:
        lines.extend(
            [
                "",
                "## Gate Result",
                "",
                "PASS: every pre-layout passive/protection target has a package, footprint, rating policy, MPN field and LCSC field.",
                "",
                "Notes:",
                "",
                "- `LOCKED_CANDIDATE` rows have checked LCSC product-detail URLs in `config/passive_bom_freeze.yaml`.",
                "- `PROCUREMENT_VERIFY` rows need stock/order-code confirmation before purchase.",
                "- `TUNE_OR_EVT_SELECT` rows keep the footprint/minimum spec frozen but intentionally defer exact value/MPN to RF tuning or bench measurement.",
            ]
        )
    return "\n".join(lines) + "\n"


def write_outputs(records: list[dict[str, object]], problems: list[str], *, ai_context: bool) -> None:
    write_csv(CSV_OUT, records)
    write_json(JSON_OUT, records, problems)
    DOC_OUT.write_text(build_markdown(records, problems), encoding="utf-8")
    if ai_context:
        write_csv(AI_CSV_OUT, records)
        write_json(AI_JSON_OUT, records, problems)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="write CSV/JSON/Markdown reports")
    parser.add_argument("--ai-context", action="store_true", help="also write ai_context CSV/JSON")
    args = parser.parse_args()

    records, problems = build_records()
    if args.write:
        write_outputs(records, problems, ai_context=args.ai_context)
        print(status("OK", f"Wrote {CSV_OUT}"))
        print(status("OK", f"Wrote {JSON_OUT}"))
        print(status("OK", f"Wrote {DOC_OUT}"))
        if args.ai_context:
            print(status("OK", f"Wrote {AI_CSV_OUT}"))
            print(status("OK", f"Wrote {AI_JSON_OUT}"))

    if problems:
        print(status("FAIL", f"{len(problems)} passive BOM freeze problem(s) found."))
        for problem in problems:
            print(status("FAIL", f"  - {problem}"))
        return 1

    print(status("OK", f"Passive BOM freeze covers {len(records)} refs."))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
