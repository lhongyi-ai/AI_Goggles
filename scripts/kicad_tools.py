from __future__ import annotations

import importlib.util
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Iterable

import yaml
from pydantic import BaseModel, Field, ValidationError, field_validator


PROJECT_ROOT = Path(__file__).resolve().parents[1]
HARDWARE_DIR = PROJECT_ROOT / "hardware"
GENERATED_DIR = PROJECT_ROOT / "generated"
REPORTS_DIR = GENERATED_DIR / "reports"
GERBERS_DIR = GENERATED_DIR / "gerbers"
LOGS_DIR = GENERATED_DIR / "logs"
PCB_FILE = HARDWARE_DIR / "ai_glasses_carrier.kicad_pcb"

TEST_NETS = ["+5V", "GND", "I2C_SCL", "I2C_SDA"]


class ProjectConfig(BaseModel):
    name: str
    revision: str


class BoardGeometry(BaseModel):
    width_mm: float = Field(gt=0)
    height_mm: float = Field(gt=0)
    layers: int = Field(ge=2)


class BoardFeatures(BaseModel):
    test_connector: bool
    mounting_holes: int = Field(ge=0)
    generate_board_text: bool


class I2CConfig(BaseModel):
    enabled: bool
    voltage: float = Field(gt=0)


class PowerInputConfig(BaseModel):
    voltage: float = Field(gt=0)


class InterfaceConfig(BaseModel):
    i2c: I2CConfig
    power_input: PowerInputConfig


class BoardConfig(BaseModel):
    project: ProjectConfig
    board: BoardGeometry
    features: BoardFeatures
    interfaces: InterfaceConfig

    @field_validator("project")
    @classmethod
    def project_name_required(cls, value: ProjectConfig) -> ProjectConfig:
        if not value.name.strip():
            raise ValueError("project.name must not be empty")
        return value


def status(kind: str, message: str) -> str:
    return f"[{kind}] {message}"


def run_command(command: list[str], timeout: int = 30) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        text=True,
        capture_output=True,
        timeout=timeout,
        check=False,
    )


KICAD_APP = Path("/Applications/KiCad/KiCad.app")
KICAD_BUNDLED_PYTHON = KICAD_APP / "Contents/Frameworks/Python.framework/Versions/3.9/bin/python3.9"
KICAD_PCBNEW_SITE = KICAD_APP / "Contents/Frameworks/Python.framework/Versions/3.9/lib/python3.9/site-packages"


def common_kicad_paths() -> list[Path]:
    return [
        KICAD_APP / "Contents/MacOS/kicad-cli",
        KICAD_APP,
        KICAD_APP / "Contents/Frameworks",
    ]


def find_kicad_python() -> Path | None:
    """Return the KiCad-bundled Python 3.9 interpreter, or None if not present."""
    if KICAD_BUNDLED_PYTHON.exists() and os.access(KICAD_BUNDLED_PYTHON, os.X_OK):
        return KICAD_BUNDLED_PYTHON
    return None


def pcbnew_available_via_kicad_python() -> bool:
    """Return True if pcbnew can be imported using KiCad's bundled Python."""
    kicad_py = find_kicad_python()
    if not kicad_py:
        return False
    result = subprocess.run(
        [str(kicad_py), "-c", f"import sys; sys.path.insert(0,'{KICAD_PCBNEW_SITE}'); import pcbnew; print(pcbnew.GetBuildVersion())"],
        text=True,
        capture_output=True,
        timeout=15,
        check=False,
    )
    return result.returncode == 0


def find_kicad_cli() -> Path | None:
    from_path = shutil.which("kicad-cli")
    if from_path:
        return Path(from_path).resolve()

    direct = Path("/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli")
    if direct.exists():
        return direct

    applications = Path("/Applications")
    if applications.exists():
        for candidate in applications.rglob("kicad-cli"):
            if candidate.is_file() and os.access(candidate, os.X_OK):
                return candidate
    return None


def find_kicad_app() -> Path | None:
    direct = Path("/Applications/KiCad/KiCad.app")
    if direct.exists():
        return direct

    applications = Path("/Applications")
    if applications.exists():
        for candidate in applications.rglob("KiCad.app"):
            if candidate.is_dir():
                return candidate
    return None


def get_kicad_version(kicad_cli: Path | None = None) -> tuple[str | None, str | None]:
    cli = kicad_cli or find_kicad_cli()
    if not cli:
        return None, "kicad-cli was not found in PATH or /Applications."

    result = run_command([str(cli), "version"])
    output = (result.stdout or result.stderr).strip()
    if result.returncode != 0:
        return None, output or "kicad-cli version returned a non-zero status."
    return output, None


def module_available(module_name: str) -> bool:
    return importlib.util.find_spec(module_name) is not None


def ipc_candidates() -> list[str]:
    return [
        "kicad",
        "kicad_python",
        "kicad_ipc",
        "kiapi",
    ]


def available_ipc_modules() -> list[str]:
    return [name for name in ipc_candidates() if module_available(name)]


def legacy_pcbnew_available() -> bool:
    return module_available("pcbnew")


def load_board_config(path: Path | None = None) -> BoardConfig:
    config_path = path or PROJECT_ROOT / "config" / "board.yaml"
    with config_path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    try:
        return BoardConfig.model_validate(data)
    except ValidationError as exc:
        raise SystemExit(f"Invalid board config {config_path}: {exc}") from exc


def ensure_output_dirs() -> None:
    for path in (HARDWARE_DIR, REPORTS_DIR, GERBERS_DIR, LOGS_DIR):
        path.mkdir(parents=True, exist_ok=True)


def help_text(command: Iterable[str]) -> str:
    result = run_command(list(command), timeout=15)
    return "\n".join(part for part in [result.stdout, result.stderr] if part)


def is_macos() -> bool:
    return platform.system().lower() == "darwin"


def python_summary() -> str:
    return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
