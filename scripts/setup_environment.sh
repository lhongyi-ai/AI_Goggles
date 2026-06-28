#!/usr/bin/env bash
set -u

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_DIR="$PROJECT_ROOT/generated/logs"
LOG_FILE="$LOG_DIR/setup_environment.log"

mkdir -p "$LOG_DIR"

log() {
  printf '%s\n' "$*" | tee -a "$LOG_FILE"
}

cd "$PROJECT_ROOT" || exit 1
: > "$LOG_FILE"

if ! command -v python3 >/dev/null 2>&1; then
  log "[ERROR] python3 was not found."
  exit 1
fi

log "[OK] Python: $(python3 --version 2>&1)"
python3 -m venv .venv || exit 1

# shellcheck disable=SC1091
source .venv/bin/activate

python -m pip install --upgrade pip | tee -a "$LOG_FILE"
python -m pip install -r requirements.txt | tee -a "$LOG_FILE"

log "[INFO] Checking KiCad environment."
python scripts/check_environment.py | tee -a "$LOG_FILE"

if python - <<'PY' >/dev/null 2>&1
import importlib.util
raise SystemExit(0 if any(importlib.util.find_spec(name) for name in ("kicad", "kicad_python", "kicad_ipc", "kiapi")) else 1)
PY
then
  log "[OK] KiCad IPC Python bindings are already importable."
else
  log "[WARN] KiCad IPC Python bindings are not importable."
  log "[INFO] No stable official IPC package was inferred automatically on this machine."
  log "[INFO] Fallback file-generation workflow remains available."
fi

log "[OK] Environment setup complete."
