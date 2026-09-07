import json
import logging
from pathlib import Path
import os
from typing import Any, Dict
from scr.models import AuditResult


logger = logging.getLogger(__name__)

class AuditStateManager:
    """Manages the state of tweet audits persistence, track processed tweets and results"""

    def __init__(self, state_file: Path = Path("audit_state.json")):
        self.state_file = Path(state_file)
        self.processed_id: set[str] = set()
        self.results: Dict[str, Dict[str, Any]] = {}
        self.load_state()

    def load_state(self):
        """Load prevoius audit checkpoints from disks with error recovery."""
        if  not self.state_file.exists():
            logger.info(f"No existing state file found at {self.state_file}. Starting fresh.")
            return
        
        try:
            with open(self.state_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.results = data.get("results", {})
                self.processed_id = set(self.results.keys())
                logger.info(f"loaded {len(self.processed_id)} processed tweet IDs from {self.state_file}.")
        except (json.JSONDecodeError, IOError) as e:
            logger.warning(f"State file {self.state_file} corrupted ({e}). Initializing clean state.")            
            self.results = {}
            self.processed_id = set()
        except Exception as e:
            logger.error(f"Failed to load state from {self.state_file}: {e}")
            self.results = {}
            self.processed_id = set()

    def is_processed(self, tweet_id: str) -> bool:
        """Check if a tweet has already been processed."""
        return tweet_id in self.processed_id    

    def save_result(self, tweet_id: str, tweet_text: str, result: AuditResult) -> None:
        """Record an evaluation results and commit to disk."""
        str_id = str(tweet_id)
        self.processed_id.add(str_id)
        self.results[str_id] = {
            "full_text": tweet_text,
            "flagged": result.flagged,
            "confidence": result.confidence,
            "category": result.category,
            "reason": result.reason
        }
        self._persist()

    def _persist(self) -> None:
        """write state to disk safely using a temporary file pattern to avoid corruption."""
        temp_file = self.state_file.with_suffix(".tmp")
        try:

            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump({"results": self.results}, f, ensure_ascii=False, indent=4)
                #atomic rename prevents partial writes from corrupting the state file
            os.replace(temp_file, self.state_file)
        except Exception as e:
            logger.error(f"Failed to persist state to {self.state_file}: {e}")
            if temp_file.exists():
                try:
                    temp_file.unlink()
                except OSError as oe:
                    logger.error(f"Failed to remove temporary state file {temp_file}: {oe}")
                    pass

    def get_flagged_count(self) -> int:
        """Return the number of tweets flagged as inappropriate."""
        return sum(1 for result in self.results.values() if result.get("flagged", False))

    def get_total_audited(self) -> int:
        """Return the total number of tweets audited."""
        return len(self.processed_id)





