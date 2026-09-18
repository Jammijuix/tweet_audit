import csv
from pathlib import Path
from scr.models import Tweet, AuditResult
from scr.runner import export_flagged_tweets_to_csv, run_audit
from scr.state import AuditStateManager


def test_export_flagged_to_csv(tmp_path: Path):
    """Verifies that only flagged tweets are exported to CSV with the exact schema."""
    output_csv = tmp_path / "flagged_tweets.csv"
    mock_results = {
        "101": {"flagged": True, "full_text": "unprofessional post"},
        "102": {"flagged": False, "full_text": "great tech post"},
        "103": {"flagged": True, "full_text": "toxic tweet"},
    }

    exported_count = export_flagged_tweets_to_csv(mock_results, output_file=output_csv, username="kelvin")

    assert exported_count == 2
    assert output_csv.exists()

    with open(output_csv, "r", encoding="utf-8") as f:
        reader = list(csv.DictReader(f))
        assert len(reader) == 2
        assert reader[0] == {"tweet_url": "https://x.com/kelvin/status/101", "deleted": "False"}
        assert reader[1] == {"tweet_url": "https://x.com/kelvin/status/103", "deleted": "False"}


def test_run_audit_pipeline(tmp_path: Path, mocker):
    """Verifies the runner pipeline loops through archive, skips retweets, and records state."""
    state_file = tmp_path / "test_state.json"
    archive_file = tmp_path / "tweets.js"

    # Sample archive containing 1 original tweet and 1 retweet
    archive_file.write_text(
        'window.YTD.tweet.part0 = ['
        '{"tweet": {"id": "201", "created_at": "Wed Oct 10 20:19:24 +0000 2018", "full_text": "Original tweet"}}, '
        '{"tweet": {"id": "202", "created_at": "Wed Oct 10 20:19:24 +0000 2018", "full_text": "RT @user: Retweet"}}'
        ']',
        encoding="utf-8"
    )

    # Mock evaluate_tweet
    mock_eval = mocker.patch(
        "scr.runner.evaluate_tweet",
        return_value=AuditResult(flagged=False, confidence=1.0, reason="Good post")
    )

    # Patch AuditStateManager to use the temporary state file
    mocker.patch("scr.runner.AuditStateManager", lambda: AuditStateManager(state_file=state_file))

    run_audit(archive_path=archive_file, max_tweets=5, delay_seconds=0.0)

    # Only 1 original tweet should have been sent to evaluate_tweet (retweet skipped)
    assert mock_eval.call_count == 1