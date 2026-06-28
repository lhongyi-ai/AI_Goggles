#!/usr/bin/env python3
from __future__ import annotations

import importlib
import subprocess
from dataclasses import dataclass

try:
    from .kicad_tools import available_ipc_modules, is_macos, status
except ImportError:
    from kicad_tools import available_ipc_modules, is_macos, status


@dataclass
class ProcessCheck:
    running: bool
    details: str


def pcb_editor_process() -> ProcessCheck:
    if is_macos():
        result = subprocess.run(
            ["pgrep", "-fl", "KiCad|pcbnew"],
            text=True,
            capture_output=True,
            check=False,
        )
        output = (result.stdout or result.stderr).strip()
        if result.returncode == 0 and output:
            return ProcessCheck(True, output)
        return ProcessCheck(False, "No KiCad or PCB Editor process was found by pgrep.")

    result = subprocess.run(
        ["ps", "aux"],
        text=True,
        capture_output=True,
        check=False,
    )
    output = result.stdout.lower()
    if "kicad" in output or "pcbnew" in output:
        return ProcessCheck(True, "A KiCad-like process appears to be running.")
    return ProcessCheck(False, "No KiCad or PCB Editor process was found.")


def describe_module(module_name: str) -> str:
    module = importlib.import_module(module_name)
    version = getattr(module, "__version__", None)
    path = getattr(module, "__file__", None)
    pieces = [module_name]
    if version:
        pieces.append(f"version={version}")
    if path:
        pieces.append(f"path={path}")
    return ", ".join(pieces)


def main() -> int:
    modules = available_ipc_modules()
    if not modules:
        print(status("ERROR", "KiCad IPC bindings are not importable in this Python environment."))
        print(status("INFO", "Run scripts/check_environment.py and scripts/setup_environment.sh first."))
        print(status("INFO", "Fallback file generation remains available via scripts/generate_test_board.py."))
        return 2

    print(status("OK", "KiCad IPC bindings imported: " + "; ".join(describe_module(name) for name in modules)))

    process = pcb_editor_process()
    if process.running:
        print(status("OK", "KiCad or PCB Editor process detected."))
        print(status("INFO", process.details))
    else:
        print(status("ERROR", process.details))
        print(status("INFO", "Start KiCad, open PCB Editor, and open hardware/ai_glasses_carrier.kicad_pcb."))
        return 3

    print(status("ERROR", "No compatible IPC client adapter is implemented for the detected Python module."))
    print(status("INFO", "This script refuses to report a successful IPC connection without a verified board read."))
    print(status("INFO", "Likely causes: IPC server disabled, unsupported KiCad version, or incompatible bindings."))
    return 4


if __name__ == "__main__":
    raise SystemExit(main())
