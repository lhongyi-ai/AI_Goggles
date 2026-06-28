from pathlib import Path

import yaml

from scripts.kicad_tools import TEST_NETS, load_board_config


def test_board_yaml_can_be_loaded():
    config_path = Path("config/board.yaml")
    with config_path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    assert data["project"]["name"] == "ai_glasses_carrier_v1"


def test_board_dimensions_are_positive():
    config = load_board_config()
    assert config.board.width_mm > 0
    assert config.board.height_mm > 0


def test_board_is_six_layer():
    config = load_board_config()
    assert config.board.layers == 6


def test_confirmed_5v_pins_present():
    """Requirements Section 3.2: J3A +5V input pins are authoritative."""
    config_path = Path("config/cm4_pins.yaml")
    with config_path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    pins = data["connectors"]["J3A"]["confirmed_pins"]["+5V_IN"]
    assert pins == [77, 79, 81, 83, 85, 87]


def test_network_names_are_not_empty():
    assert TEST_NETS
    assert all(name.strip() for name in TEST_NETS)
