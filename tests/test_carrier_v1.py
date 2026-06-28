from pathlib import Path

from scripts.generate_carrier_board import collect_nets, write_files
from scripts.check_pin_freeze import load_pin_assignment, check_row, row_is_p0
from scripts.audit_csi3_camera import build_report
from scripts.carrier_bom import COMPONENTS
from scripts.generate_j2_footprint import write_files as write_j2_footprint_files
import re


def test_carrier_skeleton_generates_six_layer_pcb():
    pcb_path, sch_path = write_files()
    assert pcb_path.exists() and sch_path.exists()
    text = pcb_path.read_text(encoding="utf-8")
    # 6-layer stack must declare the inner copper layers.
    assert '"In1.Cu"' in text
    assert '"In4.Cu"' in text
    assert "Edge.Cuts" in text


def test_carrier_declares_core_v1_nets():
    write_files()
    text = Path("hardware/ai_glasses_carrier.kicad_pcb").read_text(encoding="utf-8")
    for net in ("GND", "+5V_SYS", "MIPI_CSI3_CLK_P", "USB_DP", "PDM1_CLK", "SAI1_BCLK"):
        assert net in text, f"missing net {net}"


def test_carrier_skeleton_is_marked_do_not_fab():
    write_files()
    text = Path("hardware/ai_glasses_carrier.kicad_pcb").read_text(encoding="utf-8")
    assert "DO NOT FAB" in text
    assert "SKELETON" in text


def test_net_collection_has_no_duplicates():
    nets = collect_nets()
    assert len(nets) == len(set(nets))
    assert "GND" in nets


def test_all_schematic_references_are_kicad_annotation_safe():
    bad = [comp.ref for comp in COMPONENTS if not re.match(r"^[A-Za-z]+[0-9]+$", comp.ref)]
    assert not bad, f"KiCad reference designators must end in digits: {bad}"


def test_camera_j2_uses_project_footprint_and_no_connect_markers():
    write_files()
    text = Path("hardware/ai_glasses_carrier.kicad_sch").read_text(encoding="utf-8")
    assert 'AI_Glasses:FH35C-31S-0.3SHW_50' in text
    assert '27 RESET_N' in text
    assert "J2_NC" not in text
    assert text.count("(no_connect") >= 6


def test_all_components_have_footprints_for_update_pcb_from_schematic():
    missing = [comp.ref for comp in COMPONENTS if not comp.footprint]
    assert not missing, f"Update PCB requires Footprint fields for every symbol: {missing}"


def test_generated_schematic_has_no_empty_footprint_fields():
    write_files()
    sch = Path("hardware/ai_glasses_carrier.kicad_sch").read_text(encoding="utf-8")
    sym = Path("hardware/AI_Glasses.kicad_sym").read_text(encoding="utf-8")
    assert 'property "Footprint" ""' not in sch
    assert 'property "Footprint" ""' not in sym
    assert 'Resistor_SMD:R_0603_1608Metric' in sch
    assert 'Capacitor_SMD:C_0805_2012Metric' in sch
    assert 'AI_Glasses:VERIFY_B2B_J31_LOGICAL' in sch


def test_project_symbol_library_is_configured_for_generated_symbols():
    write_files()
    assert Path("hardware/sym-lib-table").exists()
    assert Path("hardware/fp-lib-table").exists()
    assert Path("hardware/AI_Glasses.kicad_sym").exists()
    assert Path("hardware/AI_Glasses.pretty/FH35C-31S-0.3SHW_50.kicad_mod").exists()
    assert Path("hardware/AI_Glasses.pretty/VERIFY_B2B_J31_LOGICAL.kicad_mod").exists()
    assert Path("hardware/AI_Glasses.pretty/VERIFY_TP_1P.kicad_mod").exists()
    table = Path("hardware/sym-lib-table").read_text(encoding="utf-8")
    fp_table = Path("hardware/fp-lib-table").read_text(encoding="utf-8")
    lib = Path("hardware/AI_Glasses.kicad_sym").read_text(encoding="utf-8")
    assert '(name "aiglasses")' in table
    assert '(name "AI_Glasses")' in fp_table
    assert '${KIPRJMOD}/AI_Glasses.pretty' in fp_table
    assert '(symbol "J2"' in lib


def test_j2_fh35c_footprint_uses_official_two_row_pattern():
    fp, check_pcb = write_j2_footprint_files()
    text = fp.read_text(encoding="utf-8")
    assert check_pcb.exists()
    assert '(pad "1" smd roundrect (at -4.500 1.075)' in text
    assert '(pad "2" smd roundrect (at -4.200 -1.150)' in text
    assert '(pad "31" smd roundrect (at 4.500 1.075)' in text
    assert '(size 0.200 0.800)' in text
    assert '(size 0.200 0.650)' in text
    assert text.count('(pad "') == 35


def test_csi3_imx415_audit_passes():
    report, problems = build_report()
    assert not problems, report
    assert "J2 Pin 1-31 Electrical Check" in report
    assert "| 31 | `VCC5V` | `VCC5V` | `+5V_SYS`" in report
    assert "CSI3/CSI4 mux alias" in report
    assert "DEFERRED_TO_PRE_LAYOUT" in report


def test_pin_freeze_gate_not_frozen_until_procurement_resolved():
    """Pins are now verified, but the gate must still block until FROZEN.

    After filling real CM4 pins (vs official pinout) every P0 row is complete
    (no TBD pin, source_verified=true), so the remaining blocker is the Section
    8.3 procurement TBDs + the FROZEN sign-off — not the pin data.
    """
    data = load_pin_assignment()
    assert data["status"] != "FROZEN", "must not be FROZEN until procurement signs off"

    # P0 pin data should now be complete (no per-row problems).
    p0_problems = []
    for row in data["assignments"]:
        if row_is_p0(row):
            p0_problems.extend(check_row(row))
    assert not p0_problems, f"P0 pin rows should be complete, got: {p0_problems[:3]}"

    # The gate stays blocked because procurement TBDs remain unresolved.
    unresolved = [t for t in data.get("open_tbd", []) if not t.get("resolved")]
    assert unresolved, "expected unresolved procurement TBDs keeping the gate blocked"


def test_pin_freeze_required_fields_defined_for_every_row():
    """Every row must at least carry the Section 3.3 field keys."""
    data = load_pin_assignment()
    required = {"function", "signal", "connector", "pin", "voltage_domain"}
    for row in data["assignments"]:
        assert required.issubset(row.keys())
