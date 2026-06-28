from scripts.audit_passive_bom_freeze import build_records, target_refs


def test_passive_bom_freeze_covers_every_target_ref():
    records, problems = build_records()
    assert not problems
    covered = {row["ref"] for row in records}
    assert covered == target_refs()


def test_passive_bom_freeze_has_orderable_or_deferred_status_for_every_ref():
    records, _ = build_records()
    allowed = {"LOCKED_CANDIDATE", "PROCUREMENT_VERIFY", "TUNE_OR_EVT_SELECT"}
    for row in records:
        assert row["mpn"]
        assert row["lcsc"]
        assert row["footprint"]
        assert row["procurement_status"] in allowed
