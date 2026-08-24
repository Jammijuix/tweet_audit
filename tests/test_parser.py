from datetime import datetime, timezone
import json
import pytest
from pathlib import Path
from scr.parser import parse_archive, normalise_raw_tweet_data
from scr.models import Tweet


# Sample mock JS archive data matching Twitter's exact format
MOCK_ARCHIVE_CONTENT = """window.YTD.tweets.part0 = [
  {
    "tweet": {
      "id": "1001",
      "created_at": "Wed Jul 29 11:41:25 +0000 2026",
      "full_text": "Standard standalone tweet &amp; test.",
      "favourites_count": "5",
      "retweets_count": "2"
    }
  },
  {
    "tweet": {
      "id": "1002",
      "created_at": "Thu Jul 30 12:00:00 +0000 2026",
      "full_text": "@johndoe This is a reply tweet",
      "favourites_count": "0",
      "retweets_count": "0",
      "in_reply_to_status_id_str": "9999"
    }
  },
  {
    "tweet": {
      "id": "1003",
      "created_at": "Fri Jul 31 15:30:00 +0000 2026",
      "full_text": "RT @techguru: Important announcement!",
      "favourites_count": "0",
      "retweets_count": "10"
    }
  }
]"""


@pytest.fixture
def mock_archive_file(tmp_path: Path) -> Path:
    """Creates a temporary tweets.js file for testing."""
    file_path = tmp_path / "tweets.js"
    file_path.write_text(MOCK_ARCHIVE_CONTENT, encoding="utf-8")
    return file_path


def test_normalize_raw_tweet():
    """Tests dictionary normalization and HTML unescaping."""
    raw_item = {
        "tweet": {
            "id": "12345",
            "created_at": "Wed Jul 29 11:41:25 +0000 2026",
            "full_text": "Python &gt; Java &amp; C++",
            "favourites_count": "12",
            "retweets_count": "3",
            "in_reply_to_status_id_str": None,
        }
    }
    
    normalized = normalise_raw_tweet_data(raw_item)
    
    assert normalized["id"] == "12345"
    assert normalized["full_text"] == "Python > Java & C++"
    assert normalized["favourites_count"] == 12
    assert normalized["retweets_count"] == 3
    assert normalized["in_reply_to_status_id_str"] is None


def test_parse_archive_yields_valid_models(mock_archive_file: Path):
    """Tests that parse_archive correctly loads, parses, and validates Tweet instances."""
    tweets = list(parse_archive(mock_archive_file))
    
    assert len(tweets) == 3
    assert all(isinstance(t, Tweet) for t in tweets)


def test_parse_archive_properties(mock_archive_file: Path):
    """Tests calculated properties: is_reply and is_retweet."""
    tweets = list(parse_archive(mock_archive_file))
    
    # Tweet 1: Standalone
    assert tweets[0].id == "1001"
    assert tweets[0].is_reply is False
    assert tweets[0].is_retweet is False
    assert tweets[0].full_text == "Standard standalone tweet & test."

    # Tweet 2: Reply
    assert tweets[1].id == "1002"
    assert tweets[1].is_reply is True
    assert tweets[1].is_retweet is False
    assert tweets[1].in_reply_to_status_id_str == "9999"

    # Tweet 3: Retweet
    assert tweets[2].id == "1003"
    assert tweets[2].is_reply is False
    assert tweets[2].is_retweet is True


def test_parse_archive_missing_file():
    """Tests that parse_archive raises FileNotFoundError for non-existent paths."""
    with pytest.raises(FileNotFoundError):
        list(parse_archive(Path("non_existent_tweets.js")))