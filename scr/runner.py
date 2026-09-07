import csv
import logging
import time
from pathlib import Path
from typing import Optional

from scr.evaluator import evaluate_tweet
from scr.parser import parse_archive
from scr.state import AuditStateManager


logging.basicConfig(
    level= logging.INFO,
    format = "%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

def export_flagged_tweets_to_csv(
    state_results: dict,
    output_file: Path = Path("Flagged_tweets.csv"),
    username: str = "i/web") -> int:
    """Export all Flagged tweets to a csv matching the requested specification."""

    try:
        flagged_rows = []
        for tweet_id, result in state_results.items():
            if result.get("flagged", False):
                tweet_url = f"https://x.com/{username}/status/{tweet_id}"
                flagged_rows.append({
                    "tweet_url": tweet_url,
                    "deleted": "False"
                })

        with open(output_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["tweet_url", "deleted"])
            writer.writeheader()
            writer.writerows(flagged_rows)

        logger.info(f"Sucessfully exported {len(flagged_rows)} flaged tweets to {output_file.resolve()}")

    except Exception as e:
        logger.error(f"Failde to export flagged tweets to csv: {e}")
        return 0


def run_audit(
    archive_path: Path,
    max_tweets: Optional[int]= None,
    delay_seconds: float = 6.0,
    username:  str = "i/web"

) -> None:
    """Main orchestration pipeline:
    Streams archive -> Checks state -> Audits with Gemini -> Saves state -> Exports CSV.
    """
    path = Path(archive_path)
    if not path.exists():
        logger.error(f"Archive file not found.")
        return


    state_manager = AuditStateManager()
    logger.info(f"Initial state: {state_manager.get_total_audited()} tweets processed so far")

    audited_in_session = 0

    try:
        for tweet in parse_archive(path):
            #1. Skip if already processing in prior run

            if state_manager.is_processed(tweet.id):
                continue

            #2. Skip retweets (keep focus on original posts)
            if tweet.is_retweet:
                continue
            logger.info(f"Auditing TweetId {tweet.id}  | Date: {tweet.created_at}")

            #call Gemini evaluator with error isolation
            try:
                result = evaluate_tweet(tweet)
                state_manager.save_result(tweet.id, tweet.full_text, result)

                status = "FLAGGED" if result.flagged else "PASSED"
                logger.info(f" -> [{status}] (Confidence: {result.confidence: .2f}) Reason: {result.reason}")

                audited_in_session +=1

            except Exception as e:
                logger.error(f"Failed to process Tweet Id {tweet.id}: {e}")
                continue


            #4. Stop if max_tweets threashold reached
            if max_tweets and audited_in_session >= max_tweets:
                logger.info(f"Reached specified limit of {max_tweets} tweet for this run.")
                break


            #5. PolitePause to avoid rate limits

            time.sleep(delay_seconds)

    except KeyboardInterrupt:
        logger.warning("Audit pipeline interrupted by user (Ctrl+C). Progress is safely saved.")
    except Exception as e:
        logger.exception(f"Unexpected error in pipeline run: {e}")

    finally:
        # Always generate / update the CSV even on early termination
        export_flagged_tweets_to_csv(state_manager.results, username=username)

        print("\n" + "=" * 40)
        print("          AUDIT RUN SUMMARY          ")
        print("=" * 40)
        print(f"Total Audited in System : {state_manager.get_total_audited()}")
        print(f"Total Flagged for Deletion: {state_manager.get_flagged_count()}")
        print(f"State Checkpoint Saved  : {state_manager.state_file.resolve()}")
        print(f"Deletion CSV Output     : {Path('flagged_tweets.csv').resolve()}")
        print("=" * 40 + "\n")


if __name__ == "__main__":
    # Test batch run on your archive file
    ARCHIVE_FILE = Path("data/tweets.js")
    run_audit(ARCHIVE_FILE, max_tweets=10)


