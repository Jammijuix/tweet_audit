import json , html
from pathlib import Path
from typing import Any, Generator
from scr.models import Tweet 

def strips_js_prefix(file_path: Path) -> str:
    """
    Read a JSON file and remove the JavaScript prefix if present.

    Args:
        file_path (Path): Path to the JSON file.

    Returns:
        str: The content of the file with the JavaScript prefix removed.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read().strip()

        array_start = content.find("[")
        if array_start == -1:
            raise ValueError(F"No JSON array found in the file {file_path}.")


    return content[array_start:]


def normalise_raw_tweet_data(raw_tweet: dict[str, Any]) -> dict:
    """
    Normalize raw tweet data to match the Tweet model structure.

    Args:
        raw_tweet (dict): Raw tweet data from the JSON file.

    Returns:
        dict: Normalized tweet data.
    """
    tweet_dict = raw_tweet.get("tweet", raw_tweet)


    #handle missing or none

    raw_tweet = tweet_dict.get("full_text") or ""
    clean_text = Tweet.unescape_html(raw_tweet) #
    fav_count = tweet_dict.get("favourites_count", 0)
    rt_count = tweet_dict.get("retweets_count", 0)
    reply_id = tweet_dict.get("in_reply_to_status_id_str")
    return {
        "id": tweet_dict.get("id"),
        "full_text": clean_text,
        "created_at": tweet_dict.get("created_at"),
        "favourites_count": int(fav_count) if fav_count is not None else 0,
        "retweets_count": int(rt_count) if rt_count is not None else 0,
        "in_reply_to_status_id_str": reply_id
    }







    
def parse_archive(file_path: Path) -> Generator[Tweet, None, None]:
    """
    Parse a JSON archive file containing tweets and yield Tweet objects.

    Args:
        file_path (Path): Path to the JSON archive file."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"The file {path} does not exist.")

    with open(path, 'r', encoding='utf-8') as f:
       content = f.read().strip()

    # Remove JavaScript prefix if present
    array_start = content.find("[") 
    if array_start == -1:
        raise ValueError(f"No JSON array found in the file {path}.")

    raw_data = json.loads(content[array_start:])

    # Iterate through each raw tweet in the JSON array
    for raw_tweet in raw_data:
      tweet_data = raw_tweet.get("tweet", raw_tweet)
      #map twitter data to our model

      normalized = {
          "id": tweet_data.get("id"),
          "full_text": html.unescape(tweet_data.get("full_text", "")),
          "favourites_count": tweet_data.get("favourites_count", 0),
          "retweets_count": tweet_data.get("retweets_count", 0),
          "in_reply_to_status_id_str": tweet_data.get("in_reply_to_status_id_str"),
          "created_at": tweet_data.get("created_at")
      }

      yield Tweet.model_validate(normalized)

    



