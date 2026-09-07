from pydantic import BaseModel, field_validator, computed_field, Field
from typing import Optional
from datetime import datetime
import html
from typing import Optional


class Tweet(BaseModel):
    id: str
    full_text: str
    created_at: datetime
    favourites_count: int = 0
    retweets_count: int = 0
    in_reply_to_status_id_str: Optional[str] = None 

    @field_validator("created_at", mode="before")
    @classmethod
    def parse_twitter_date(cls, v):
        """Parse Twitter date string or pass-through datetime object."""
        if isinstance(v, datetime):
            return v
        if isinstance(v, str):
            # Twitter date format: 'Wed Oct 10 20:19:24 +0000 2018'
            return datetime.strptime(v, "%a %b %d %H:%M:%S %z %Y")
        raise ValueError(f"Invalid date format or type: {v}")
    @field_validator('full_text', mode="before")
    @classmethod
    def unescape_html(cls, full_text: str) -> str:
        """
        Unescape HTML entities in the full_text of the tweet.
        """
        if isinstance(full_text, str):   
            full_text = html.unescape(full_text)
        return full_text
    @computed_field
    @property
    def is_retweet(self) -> bool:
        """
        Check if the tweet is a retweet.
        A retweet typically starts with 'RT @'.
        """
        return self.full_text.startswith("RT @")
    @computed_field
    @property
    def is_reply(self) -> bool:
        """
        Check if the tweet is a reply.
        A reply has a non-null in_reply_to_status_id_str.
        """
        return self.in_reply_to_status_id_str is not None

#audit model
class AuditResult(BaseModel):
    flagged: bool = Field(
        description ="True if the tweet violates professional alignment or contains unwanted content, False otherwise."
    )
    confidence: float = Field(
        description="Confidence score between 0.0 and 1.0 regarding the audit decision."
    )
    category: Optional[str] = Field(
        default=None,
        description="Category of concern (e.g., 'toxic_argument', 'cynical_rant','unprofessional_tone', 'personal_disclosure')."
    )
    reason: str = Field(
        description="Concise rationale explaining why the tweet was flagged or allowed."
    )





    



    