#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
from uuid import uuid4

try:
    from .kicad_tools import PCB_FILE, TEST_NETS, ensure_output_dirs, load_board_config, status
except ImportError:
    from kicad_tools import PCB_FILE, TEST_NETS, ensure_output_dirs, load_board_config, status


def uid() -> str:
    return str(uuid4())


def line(start: tuple[float, float], end: tuple[float, float]) -> str:
    return (
        f'  (gr_line (start {start[0]:.3f} {start[1]:.3f}) '
        f'(end {end[0]:.3f} {end[1]:.3f})\n'
        f'    (stroke (width 0.100) (type default)) (layer "Edge.Cuts") (tstamp {uid()}))'
    )


def pad(number: int, x: float, net_index: int, net_name: str) -> str:
    shape = "rect" if number == 1 else "circle"
    return (
        f'    (pad "{number}" thru_hole {shape} (at {x:.2f} 0) (size 1.70 1.70) '
        f'(drill 1.00) (layers "*.Cu" "*.Mask") (net {net_index} "{net_name}") '
        f'(pinfunction "Pin_{number}") (pintype "passive") (tstamp {uid()}))'
    )


def generate_pcb_text() -> str:
    config = load_board_config()
    width = config.board.width_mm
    height = config.board.height_mm
    nets = "\n".join(f'  (net {index} "{name}")' for index, name in enumerate(["", *TEST_NETS]))
    edge_lines = "\n".join(
        [
            line((0, 0), (width, 0)),
            line((width, 0), (width, height)),
            line((width, height), (0, height)),
            line((0, height), (0, 0)),
        ]
    )
    connector_pads = "\n".join(
        pad(number, 0.0, number, net_name)
        for number, net_name in enumerate(TEST_NETS, start=1)
    )

    return f'''(kicad_pcb
  (version 20221018)
  (generator "ai-glasses-python")
  (general
    (thickness 1.6)
  )
  (paper "A4")
  (title_block
    (title "AI Glasses Carrier Test")
    (rev "{config.project.revision}")
  )
  (layers
    (0 "F.Cu" signal)
    (31 "B.Cu" signal)
    (32 "B.Adhes" user)
    (33 "F.Adhes" user)
    (34 "B.Paste" user)
    (35 "F.Paste" user)
    (36 "B.SilkS" user)
    (37 "F.SilkS" user)
    (38 "B.Mask" user)
    (39 "F.Mask" user)
    (44 "Edge.Cuts" user)
    (45 "Margin" user)
    (46 "B.CrtYd" user)
    (47 "F.CrtYd" user)
    (48 "B.Fab" user)
    (49 "F.Fab" user)
  )
  (setup
    (pad_to_mask_clearance 0.050)
  )
{nets}
{edge_lines}
  (gr_text "AI Glasses Carrier Test" (at {width / 2:.3f} {height / 2:.3f} 0) (layer "F.SilkS") (tstamp {uid()})
    (effects (font (size 1.500 1.500) (thickness 0.150)))
  )
  (footprint "Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical" (layer "F.Cu")
    (tstamp {uid()})
    (at {width / 2 - 3.81:.3f} {height - 5:.3f})
    (descr "Generated 1x4 test connector for automation validation")
    (property "Reference" "J1" (at 3.81 -2.33 0) (layer "F.SilkS") (tstamp {uid()})
      (effects (font (size 1.000 1.000) (thickness 0.150)))
    )
    (property "Value" "TEST_I2C_PWR" (at 3.81 2.33 0) (layer "F.Fab") (tstamp {uid()})
      (effects (font (size 1.000 1.000) (thickness 0.150)))
    )
    (fp_text reference "J1" (at 3.81 -2.33 0) (layer "F.SilkS") (tstamp {uid()})
      (effects (font (size 1.000 1.000) (thickness 0.150)))
    )
    (fp_text value "TEST_I2C_PWR" (at 3.81 2.33 0) (layer "F.Fab") (tstamp {uid()})
      (effects (font (size 1.000 1.000) (thickness 0.150)))
    )
{connector_pads}
  )
  (footprint "MountingHole:MountingHole_2.2mm_M2" (layer "F.Cu")
    (tstamp {uid()})
    (at 5.000 5.000)
    (descr "Generated M2 mounting hole")
    (property "Reference" "H1" (at 0 -3.200 0) (layer "F.SilkS") (tstamp {uid()})
      (effects (font (size 1.000 1.000) (thickness 0.150)))
    )
    (property "Value" "MountingHole" (at 0 3.200 0) (layer "F.Fab") (tstamp {uid()})
      (effects (font (size 1.000 1.000) (thickness 0.150)))
    )
    (pad "" np_thru_hole circle (at 0 0) (size 2.200 2.200) (drill 2.200) (layers "*.Cu" "*.Mask") (tstamp {uid()}))
  )
  (footprint "MountingHole:MountingHole_2.2mm_M2" (layer "F.Cu")
    (tstamp {uid()})
    (at {width - 5:.3f} {height - 5:.3f})
    (descr "Generated M2 mounting hole")
    (property "Reference" "H2" (at 0 -3.200 0) (layer "F.SilkS") (tstamp {uid()})
      (effects (font (size 1.000 1.000) (thickness 0.150)))
    )
    (property "Value" "MountingHole" (at 0 3.200 0) (layer "F.Fab") (tstamp {uid()})
      (effects (font (size 1.000 1.000) (thickness 0.150)))
    )
    (pad "" np_thru_hole circle (at 0 0) (size 2.200 2.200) (drill 2.200) (layers "*.Cu" "*.Mask") (tstamp {uid()}))
  )
)
'''


def write_board(path: Path = PCB_FILE) -> Path:
    ensure_output_dirs()
    text = generate_pcb_text()
    path.write_text(text, encoding="utf-8")
    return path


def main() -> int:
    board_path = write_board()
    print(status("OK", f"Generated test PCB: {board_path}"))

    try:
        try:
            from .run_drc import run_drc
        except ImportError:
            from run_drc import run_drc

        drc_code = run_drc(allow_missing_cli=True)
        if drc_code == 0:
            print(status("OK", "DRC completed."))
        else:
            print(status("WARN", f"DRC did not complete cleanly; exit code {drc_code}."))
    except Exception as exc:
        print(status("WARN", f"DRC step skipped after board generation: {exc}"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
