#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

try:
    from .kicad_tools import PCB_FILE, REPORTS_DIR, ensure_output_dirs, find_kicad_cli, help_text, run_command, status
except ImportError:
    from kicad_tools import PCB_FILE, REPORTS_DIR, ensure_output_dirs, find_kicad_cli, help_text, run_command, status


def build_drc_command(kicad_cli: Path, pcb_file: Path, report_file: Path) -> list[str]:
    drc_help = help_text([str(kicad_cli), "pcb", "drc", "--help"])
    command = [str(kicad_cli), "pcb", "drc"]
    if "--output" in drc_help:
        command.extend(["--output", str(report_file)])
    elif " -o," in drc_help or "\n  -o" in drc_help:
        command.extend(["-o", str(report_file)])
    if "--format" in drc_help:
        command.extend(["--format", "report"])
    command.append(str(pcb_file))
    return command


def run_drc(allow_missing_cli: bool = False) -> int:
    ensure_output_dirs()
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    report_file = REPORTS_DIR / "drc-report.txt"
    kicad_cli = find_kicad_cli()
    if not kicad_cli:
        message = "kicad-cli was not found; cannot run DRC."
        report_file.write_text(f"[WARN] {message}\n", encoding="utf-8")
        print(status("WARN" if allow_missing_cli else "ERROR", message))
        return 127

    if not PCB_FILE.exists():
        message = f"PCB file does not exist: {PCB_FILE}"
        report_file.write_text(f"[ERROR] {message}\n", encoding="utf-8")
        print(status("ERROR", message))
        return 2

    command = build_drc_command(kicad_cli, PCB_FILE, report_file)
    print(status("INFO", "Running: " + " ".join(command)))
    result = run_command(command, timeout=120)
    combined = "\n".join(part for part in [result.stdout, result.stderr] if part)
    if not report_file.exists() or report_file.stat().st_size == 0:
        report_file.write_text(combined or "[INFO] kicad-cli produced no report output.\n", encoding="utf-8")

    if result.returncode == 0:
        print(status("OK", f"DRC report: {report_file}"))
    else:
        print(status("ERROR", f"DRC failed with exit code {result.returncode}. See {report_file}"))
    return result.returncode


def main() -> int:
    return run_drc(allow_missing_cli=False)


if __name__ == "__main__":
    raise SystemExit(main())
