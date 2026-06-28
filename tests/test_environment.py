from scripts import check_environment


def test_environment_check_does_not_crash_when_kicad_is_missing():
    assert check_environment.main() == 0
