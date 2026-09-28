import html
import json
from pathlib import Path
from typing import Any, Generator
from scr.models import Tweet


def strips_js_prefix(content: str) -> str:
    """Strips JavaScript assignment prefix from text, returning JSON starting at '['."""
    array_start = content.find("[")
    if array_start == -1:
        raise ValueError("No JSON array found in archive content.")
    return content[array_start:]


def normalise_raw_tweet_data(raw_tweet: dict[str, Any]) -> dict:
    """Normalizes raw tweet data to match the Tweet model structure."""
    tweet_dict = raw_tweet.get("tweet", raw_tweet)

    raw_text = tweet_dict.get("full_text") or ""
    clean_text = Tweet.unescape_html(raw_text)
    fav_count = tweet_dict.get("favourites_count", 0)
    rt_count = tweet_dict.get("retweets_count", 0)
    reply_id = tweet_dict.get("in_reply_to_status_id_str")

    return {
        "id": tweet_dict.get("id"),
        "full_text": clean_text,
        "favourites_count": int(fav_count) if fav_count is not None else 0,
        "retweets_count": int(rt_count) if rt_count is not None else 0,
        "in_reply_to_status_id_str": reply_id,
        "created_at": tweet_dict.get("created_at"),
    }


def parse_archive(file_path: Path) -> Generator[Tweet, None, None]:
    """Parses a JSON archive file from local disk (used by CLI / runner.py)."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"The file {path} does not exist.")

    with open(path, "r", encoding="utf-8") as f:
        content = f.read().strip()

    clean_json = strips_js_prefix(content)
    raw_data = json.loads(clean_json)

    for raw_tweet in raw_data:
        normalized = normalise_raw_tweet_data(raw_tweet)
        yield Tweet.model_validate(normalized)


def parse_archive_bytes(file_bytes: bytes) -> Generator[Tweet, None, None]:
    """Parses an archive file directly from uploaded memory bytes (used by FastAPI)."""
    text_content = file_bytes.decode("utf-8", errors="replace").strip()
    clean_json = strips_js_prefix(text_content)
    raw_data = json.loads(clean_json)

    for raw_tweet in raw_data:
        normalized = normalise_raw_tweet_data(raw_tweet)
        yield Tweet.model_validate(normalized)