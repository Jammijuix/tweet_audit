from datetime import datetime, timezone
import pytest
from pydantic import ValidationError
from scr.models import Tweet, AuditResult


def test_tweet_date_parsing_success():
    """Verifies that Twitter date strings are correctly converted to datetime objects."""
    raw_date = "Wed Oct 10 20:19:24 +0000 2018"
    tweet = Tweet(
        id="12345",
        full_text="Test tweet content",
        created_at=raw_date,
        favourites_count=5,
        retweets_count=1,
    )
    assert isinstance(tweet.created_at, datetime)
    assert tweet.created_at.year == 2018
    assert tweet.created_at.month == 10
    assert tweet.created_at.day == 10


def test_tweet_date_passthrough_datetime():
    """Verifies that a pre-constructed datetime object passes validation cleanly."""
    dt = datetime(2023, 5, 1, 12, 0, 0, tzinfo=timezone.utc)
    tweet = Tweet(
        id="12345",
        full_text="Test tweet",
        created_at=dt,
    )
    assert tweet.created_at == dt


def test_tweet_date_parsing_invalid_format():
    """Verifies that malformed date strings raise a ValidationError."""
    with pytest.raises(ValidationError):
        Tweet(
            id="12345",
            full_text="Test tweet",
            created_at="Invalid Date 2024",
        )


def test_tweet_html_unescaping():
    """Verifies that HTML entities like &amp;, &lt;, &gt; are decoded properly."""
    tweet = Tweet(
        id="12345",
        full_text="Python &amp; FastAPI &gt; Flask &lt;3",
        created_at="Wed Oct 10 20:19:24 +0000 2018",
    )
    assert tweet.full_text == "Python & FastAPI > Flask <3"


def test_tweet_computed_fields():
    """Verifies is_retweet and is_reply computed properties."""
    # Retweet
    rt_tweet = Tweet(
        id="1",
        full_text="RT @username: Check this out!",
        created_at="Wed Oct 10 20:19:24 +0000 2018",
    )
    assert rt_tweet.is_retweet is True
    assert rt_tweet.is_reply is False

    # Reply
    reply_tweet = Tweet(
        id="2",
        full_text="Replying to someone",
        created_at="Wed Oct 10 20:19:24 +0000 2018",
        in_reply_to_status_id_str="99999",
    )
    assert reply_tweet.is_retweet is False
    assert reply_tweet.is_reply is True


def test_audit_result_model():
    """Verifies AuditResult validation."""
    result = AuditResult(
        flagged=True,
        confidence=0.95,
        category="toxic_argument",
        reason="Hostile language detected.",
    )
    assert result.flagged is True
    assert result.confidence == 0.95
    assert result.category == "toxic_argument"