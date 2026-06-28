#!/usr/bin/env python3
from __future__ import annotations

import platform
import sys
from pathlib import Path

try:
    from .kicad_tools import (
        PROJECT_ROOT,
        available_ipc_modules,
        common_kicad_paths,
        find_kicad_app,
        find_kicad_cli,
        find_kicad_python,
        get_kicad_version,
        legacy_pcbnew_available,
        pcbnew_available_via_kicad_python,
        python_summary,
        status,
    )
except ImportError:
    from kicad_tools import (
        PROJECT_ROOT,
        available_ipc_modules,
        common_kicad_paths,
        find_kicad_app,
        find_kicad_cli,
        find_kicad_python,
        get_kicad_version,
        legacy_pcbnew_available,
        pcbnew_available_via_kicad_python,
        python_summary,
        status,
    )


def main() -> int:
    print(status("OK", f"Python: {python_summary()}"))
    print(status("OK", f"Python executable: {sys.executable}"))
    print(status("OK", f"Platform: {platform.system()} {platform.release()}"))

    print(status("INFO", "Checking common macOS KiCad locations:"))
    for path in common_kicad_paths():
        state = "exists" if Path(path).exists() else "missing"
        print(status("INFO", f"{path}: {state}"))

    kicad_app = find_kicad_app()
    if kicad_app:
        print(status("OK", f"KiCad app: {kicad_app}"))
    else:
        print(status("WARN", "KiCad app was not found under /Applications."))

    kicad_cli = find_kicad_cli()
    if kicad_cli:
        print(status("OK", f"KiCad CLI: {kicad_cli}"))
    else:
        print(status("WARN", "KiCad CLI was not found in PATH or /Applications."))

    version, error = get_kicad_version(kicad_cli)
    if version:
        print(status("OK", f"KiCad version: {version}"))
    else:
        print(status("WARN", f"KiCad version unavailable: {error}"))

    ipc_modules = available_ipc_modules()
    print(
        status(
            "INFO",
            "IPC API package (system Python): "
            + ("yes (" + ", ".join(ipc_modules) + ")" if ipc_modules else "no"),
        )
    )
    print(
        status(
            "INFO",
            "Legacy pcbnew (system Python): " + ("yes" if legacy_pcbnew_available() else "no"),
        )
    )

    kicad_py = find_kicad_python()
    if kicad_py:
        print(status("OK", f"KiCad bundled Python 3.9: {kicad_py}"))
        if pcbnew_available_via_kicad_python():
            print(status("OK", "pcbnew importable via KiCad Python — board scripting is available"))
            print(status("INFO", f"To use pcbnew: {kicad_py} <your_script.py>"))
        else:
            print(status("WARN", "pcbnew import failed even with KiCad Python — check KiCad installation"))
    else:
        print(status("WARN", "KiCad bundled Python 3.9 not found — pcbnew scripting unavailable"))

    print(status("OK", f"Project path: {PROJECT_ROOT}"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
