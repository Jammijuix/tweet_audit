from google import genai
from google.genai import types
from scr.config import settings
from scr.models import Tweet, AuditResult
import logging
from google.genai.errors import APIError
from pydantic import ValidationError
from scr.persona import AUDIT_PERSONAS 
import time


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

def select_personal_brand_category() -> str:
    """Prompt the users in the terminal to select a personality brand category for the audit."""
    persona_keys = list(AUDIT_PERSONAS.keys())

    print("\n -- Choose a Personal Brand Category for the Audit --")
    for index, key in enumerate(persona_keys, start=1):
        label= AUDIT_PERSONAS.get("label", key)
        print(f"{index}. {label} ({key})")
    while True:
        try:
            choice = int (input("\nEnter choice (1-5)[Default: 1]").strip())
            if not choice:
                return persona_keys[0]
            if choice < 1 or choice > len(persona_keys):
                print(f"Invalid choice. Please enter a number between 1 and {len(persona_keys)}.")
            else:
                inx = int(choice) - 1
                if 0 <= inx < len(persona_keys):
                    selected = persona_keys[inx]
                    print(f"Selected Personal Brand Category: {AUDIT_PERSONAS[selected]['label']} ({selected})")
                    return selected
        except ValueError as e:
            print(f"Invalid choice. Please enter a number between 1 and 5.")



    

def evaluate_tweet(tweet: Tweet, persona: str = "corporate", max_retries: int = 3) -> AuditResult:
    """Evaluates a tweet against the persona selected by the user."""
    selected = AUDIT_PERSONAS[persona]
    system_instruction = selected["system_instruction"]

    """Evaluates a single tweet using gemini Structured Outputs."""

    prompt = f'Tweet Content: \n"""{tweet.full_text}"""'
    for attempt in range(max_retries):
        
        try:
            response = client.models.generate_content(
                model=settings.gemini_model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    response_mime_type="application/json",
                    response_schema=AuditResult,
                    temperature=0.1
                ),
            )
            if not response.text:
                raise ValueError("Empty response from Gemini API.")
            return AuditResult.model_validate_json(response.text)

        
        except APIError as e:
            if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                wait_time = 25 * (attempt + 1)
                logger.warning(f"Rate limit hit. Waiting for {wait_time} seconds before retrying...")
                time.sleep(wait_time)

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
    return AuditResult(
        flagged=False,
        confidence=0.0,
        category="max_retries_exceeded",
        reason="Maximum retry attempts exceeded without a successful evaluation."
    )