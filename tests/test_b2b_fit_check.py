from scripts.generate_b2b_fit_check import load_config, unresolved_connectors


def test_b2b_fit_check_gate_blocks_until_connector_xy_is_recorded():
    cfg = load_config()
    missing = unresolved_connectors(cfg)
    assert "J3A.x_mm" in missing
    assert "J3B.x_mm" in missing
    assert "J1.x_mm" in missing


def test_b2b_fit_check_is_connector_only():
    cfg = load_config()
    assert cfg["board"]["layers"] == 2
    assert set(cfg["connectors"]) == {"J3A", "J3B", "J1"}
    for item in cfg["connectors"].values():
        assert item["carrier_mpn"] == "DF40C-100DS-0.4V(51)"
        assert item["mated_height_mm"] == 1.5
