from pathlib import Path

from scripts.generate_test_board import write_board
from scripts.kicad_tools import TEST_NETS, load_board_config
from scripts import run_drc


def test_generated_pcb_file_exists_and_is_not_empty(tmp_path):
    path = write_board(tmp_path / "test_board.kicad_pcb")
    assert path.exists()
    assert path.stat().st_size > 0


def test_generated_pcb_contains_edge_cuts_and_test_networks(tmp_path):
    path = write_board(tmp_path / "test_board.kicad_pcb")
    text = path.read_text(encoding="utf-8")
    assert "Edge.Cuts" in text
    for net in TEST_NETS:
        assert net in text


def test_fallback_generation_runs_without_ipc(tmp_path):
    path = write_board(tmp_path / "test_board.kicad_pcb")
    text = Path(path).read_text(encoding="utf-8")
    assert "(kicad_pcb" in text


def test_generated_pcb_contains_expected_board_outline_size(tmp_path):
    path = write_board(tmp_path / "test_board.kicad_pcb")
    text = path.read_text(encoding="utf-8")
    config = load_board_config()
    w, h = config.board.width_mm, config.board.height_mm
    assert f'(start 0.000 0.000) (end {w:.3f} 0.000)' in text
    assert f'(start {w:.3f} 0.000) (end {w:.3f} {h:.3f})' in text


def test_generated_pcb_contains_two_mounting_holes_and_connector(tmp_path):
    path = write_board(tmp_path / "test_board.kicad_pcb")
    text = path.read_text(encoding="utf-8")
    assert text.count('MountingHole:MountingHole_2.2mm_M2') == 2
    assert 'Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical' in text


def test_drc_missing_cli_writes_report_without_hiding_error(monkeypatch, tmp_path):
    pcb = write_board(tmp_path / "test_board.kicad_pcb")
    reports = tmp_path / "reports"
    monkeypatch.setattr(run_drc, "find_kicad_cli", lambda: None)
    monkeypatch.setattr(run_drc, "PCB_FILE", pcb)
    monkeypatch.setattr(run_drc, "REPORTS_DIR", reports)
    assert run_drc.run_drc(allow_missing_cli=True) == 127
    report = reports / "drc-report.txt"
    assert report.exists()
    assert "kicad-cli was not found" in report.read_text(encoding="utf-8")
