from google import genai
from google.genai import types
from scr.config import settings
from scr.models import Tweet, AuditResult
import logging
from google.genai.errors import APIError
from pydantic import ValidationError

logger = logging.getLogger(__name__)

#System Prompt defing your audit standards
SYSTEM_INSTRUCTION = """ 
You are an objective content auditor evaluating past social media posts.
Assess whether the tweet aligns with a constructive, professional, and mature personal brand.

FLAG (flagged=True) if the tweet contains:
- Hostile arguments, insults, or harassment.
- Cynical, non-constructive rants or negative hot-takes.
- Inappropriate, overly defensive, or unprofessional language.
- Sensitive or obsolete personal disclosures.

PASS (flagged=False) if the tweet contains:
- Constructive technical, coding, or learning discussions.
- Friendly banter, polite humor, or casual positive interactions.
- Industry insights, milestones, and neutral updates.
- Polite inquiries or factual statements.

Return a structured JSON evaluation matching the requested schema.
"""

#Initialise Gemini Client with settings
client = genai.Client(api_key=settings.gemini_api_key)

def evaluate_tweet(tweet: Tweet) -> AuditResult:
    """Evaluates a single tweet using gemini Structured Outputs."""
    prompt = f'Tweet Content: \n"""{tweet.full_text}"""'

    try:
        response = client.models.generate_content(
            model=settings.gemini_model,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                response_mime_type="application/json",
                response_schema=AuditResult,
                temperature=0.1
            ),
        )
        if not response.text:
            raise ValueError("Empty response from Gemini API.")
        return AuditResult.model_validate_json(response.text)

    
    except APIError as e:
        logger.error(f"Error occurred while evaluating tweet: {e}")
        return AuditResult(
            flagged=False,
            confidence=0.0,
            category="api_error",
            reason=str(e)
        )
    except ValidationError as ve:
            logger.error(f"Validation error while parsing Gemini response: {ve}")
            return AuditResult(
                flagged=False,
                confidence=0.0,
                category="validation_error",
                reason=str(ve)
            )
    except Exception as e:
        logger.error(f"Unexpected error while evaluating tweet: {e}")
        return AuditResult(
            flagged=False,
            confidence=0.0,
            category="unexpected_error",
            reason=str(e)
        )
