from pathlib import Path
from scr.models import AuditResult
from scr.state import AuditStateManager


def test_state_init_empty(tmp_path: Path):
    """Verifies clean initialization when no state file exists."""
    state_file = tmp_path / "audit_state.json"
    manager = AuditStateManager(state_file=state_file)

    assert manager.get_total_audited() == 0
    assert manager.get_flagged_count() == 0
    assert manager.is_processed("101") is False


def test_state_save_and_reload(tmp_path: Path):
    """Verifies that saving results writes correctly to disk and reloads on new instance."""
    state_file = tmp_path / "audit_state.json"
    manager = AuditStateManager(state_file=state_file)

    audit_res = AuditResult(
        flagged=True,
        confidence=0.85,
        category="cynical_rant",
        reason="Unconstructive rant.",
    )

    manager.save_result(tweet_id="101", tweet_text="I hate everything", result=audit_res)

    assert manager.is_processed("101") is True
    assert manager.get_total_audited() == 1
    assert manager.get_flagged_count() == 1
    assert state_file.exists()

    # Create new instance pointing to same file to verify reload
    reloaded_manager = AuditStateManager(state_file=state_file)
    assert reloaded_manager.is_processed("101") is True
    assert reloaded_manager.get_total_audited() == 1
    assert reloaded_manager.get_flagged_count() == 1


def test_state_corrupted_file_recovery(tmp_path: Path):
    """Verifies graceful reset when reading an unparseable state file."""
    state_file = tmp_path / "corrupted_state.json"
    state_file.write_text("INVALID_JSON_CONTENT{{{", encoding="utf-8")

    manager = AuditStateManager(state_file=state_file)
    assert manager.get_total_audited() == 0
    assert manager.results == {}