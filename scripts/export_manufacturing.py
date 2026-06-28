#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

try:
    from .kicad_tools import GERBERS_DIR, PCB_FILE, ensure_output_dirs, find_kicad_cli, help_text, run_command, status
except ImportError:
    from kicad_tools import GERBERS_DIR, PCB_FILE, ensure_output_dirs, find_kicad_cli, help_text, run_command, status


def command_with_output(kicad_cli: Path, command: list[str], output: Path, input_file: Path) -> list[str]:
    text = help_text([str(kicad_cli), *command, "--help"])
    full = [str(kicad_cli), *command]
    if "--output" in text:
        full.extend(["--output", str(output)])
    elif " -o," in text or "\n  -o" in text:
        full.extend(["-o", str(output)])
    full.append(str(input_file))
    return full


def run_export(command: list[str], label: str) -> int:
    print(status("INFO", f"Running {label}: " + " ".join(command)))
    result = run_command(command, timeout=180)
    if result.stdout:
        print(result.stdout.rstrip())
    if result.stderr:
        print(result.stderr.rstrip())
    if result.returncode == 0:
        print(status("OK", f"{label} export completed."))
    else:
        print(status("ERROR", f"{label} export failed with exit code {result.returncode}."))
    return result.returncode


def main() -> int:
    ensure_output_dirs()
    kicad_cli = find_kicad_cli()
    if not kicad_cli:
        print(status("ERROR", "kicad-cli was not found; cannot export manufacturing files."))
        return 127
    if not PCB_FILE.exists():
        print(status("ERROR", f"PCB file does not exist: {PCB_FILE}"))
        return 2

    GERBERS_DIR.mkdir(parents=True, exist_ok=True)
    commands = [
        (command_with_output(kicad_cli, ["pcb", "export", "gerbers"], GERBERS_DIR, PCB_FILE), "Gerber"),
        (command_with_output(kicad_cli, ["pcb", "export", "drill"], GERBERS_DIR, PCB_FILE), "Drill"),
    ]

    step_help = help_text([str(kicad_cli), "pcb", "export", "--help"])
    if "step" in step_help.lower():
        commands.append(
            (
                command_with_output(
                    kicad_cli,
                    ["pcb", "export", "step"],
                    GERBERS_DIR / "ai_glasses_carrier.step",
                    PCB_FILE,
                ),
                "STEP",
            )
        )

    exit_code = 0
    for command, label in commands:
        exit_code = run_export(command, label) or exit_code
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
