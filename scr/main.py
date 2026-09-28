import logging
from fastapi import  FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from scr.parser import parse_archive_bytes
from scr.evaluator import evaluate_tweet

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="TweetAudit App")

#allowed Next.js to communicate with backend

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["8"]
)

@app.get("/")
async def root():
    return{"status": "online",
           "message": "TweetAudit API is ready"}


@app.post("/api/audit")
async def audit_tweets(
        file: UploadFile = File(...),
        persona: str = Form("corporate"),
        limit: int = Form(10),

):
    if not file.filename.endswith((".js", "json")):
        raise HTTPException(
            status_code=400,
            detail="Invalid file format. Please upload your extracted tweet.js file.",
        )
    try:
        file_byte = await file.read()
        flagged_tweets = []
        audit_count = 0

        for tweet in parse_archive_bytes(file_byte):
            if tweet.is_retweet:
                continue
            if limit and audit_count >= limit:
                break
            result = evaluate_tweet(tweet, persona=persona)
            audit_count +=1

            if result.flagged:
                flagged_tweets.append(
                    {
                        "id": tweet.id,
                        "text": tweet.full_text,
                        "created_at": str(tweet.created_at),
                        "category": result.category,
                        "confidence": result.confidence,
                        "reason": result.reason,
                        "tweet_url": f"https://x.com/i/web/status/{tweet.id}",
                    }
        
                )


            logger.info(
                f"Audit finished: {audit_count} scanned, {len(flagged_tweets)} flagged using '{persona}' persona."
            )
            return {
                "status": "success",
                "total_scanned": audit_count,
                "total_flagged": len(flagged_tweets),
                "flagged_tweets": flagged_tweets,
            }
    except Exception as e:
        logger.error(f"Error during audit run: {e}")
        raise HTTPException(
            status_code=500,
            detail= f"An error occurred during the audit process. {str(e)}",
        )

if __name__ == "__main__":
    pass