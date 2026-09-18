# Tweet Audit

A Python tool that parses an X (Twitter) archive, evaluates past tweets using the Google Gemini API against professional alignment criteria, and exports flagged posts to a CSV file for cleanup.

---

## Features

* **Archive Streaming:** Reads large `tweets.js` or `.json` archives using generators to keep memory usage low.
* **Structured Gemini Evaluation:** Uses strict Pydantic schemas to categorize and score posts with confidence levels.
* **Checkpoint & Resume:** Tracks progress in `audit_state.json` so you can stop and restart without re-analyzing already processed tweets.
* **CSV Export:** Generates a `flagged_tweets.csv` file containing the URLs of flagged tweets (`tweet_url,deleted`).

---

## Project Structure

```text
tweet-audit/
├── README.md
├── TRADEOFFS.md
├── .gitignore
├── config.example.json
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── models.py
│   ├── parser.py
│   ├── evaluator.py
│   ├── state.py
│   └── runner.py
└── tests/
    ├── __init__.py
    ├── test_models.py
    ├── test_parser.py
    ├── test_evaluator.py
    ├── test_state.py
    └── test_runner.py

## Setup & Installation

### 1. Clone the Repository
```bash
git clone [https://github.com/Jammijuix/tweet_audit.git](https://github.com/Jammijuix/tweet_audit.git)
cd tweet_audit

