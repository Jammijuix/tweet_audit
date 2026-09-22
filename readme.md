# TweetAudit 🔍

Audit, filter, and sanitize your historical Twitter/X posts using Gemini structured outputs, customizable audit personas, and zero data persistence.

---

## 📌 Overview

Exporting your personal Twitter/X archive bundles gigabytes of media files, making direct full-archive analysis slow, resource-heavy, and bandwidth-expensive.

**TweetAudit** solves this by targeting only the lightweight `data/tweets.js` file (< 1MB). It streams archive tweets in-memory, checks each post against a chosen personal-brand standard (an *audit persona*) using Gemini structured JSON outputs, and generates an actionable cleanup CSV of posts that need deletion.

---

## ✨ Features

- **In-Memory Streaming Parser**: Reads `data/tweets.js` directly from uploaded bytes using `ijson` and custom delimiters, without persisting raw posts to disk.
- **Custom Audit Personas**: Choose from 5 tailored auditing profiles:

  | Persona | What it does |
  |---|---|
  | `corporate` | Recruiter-ready. Flags workplace attacks, vulgarity, and unprofessional rants. |
  | `anti_cringe` | Flags teenage melodrama, oversharing, and edge-lord posts. |
  | `naija_street` | Tailored to Nigerian digital discourse. Safeguards local Pidgin banter, satire, and slang while strictly flagging scams, ethnic bigotry, and harassment. |
  | `sfw` | Strict filtering for NSFW or explicit language. |
  | `clumsy_takes` | Detects aged hot takes, poorly aged opinions, and bad arguments. |

- **Structured JSON Audits**: Enforces strict Pydantic schemas (`flagged`, `confidence`, `category`, `reason`) using Gemini structured outputs.
- **Stateful Resumption & Error Handling**: Checkpoints audit progress locally (`audit_state.json`) so interrupted runs resume safely without re-evaluating duplicate tweets.
- **Clean CSV Export**: Outputs flagged tweets as a CSV (`tweet_url`, `deleted`) ready for downstream cleanup scripts or manual review.

---

## 📁 Project Structure

```text
tweet_audit/
├── scr/
│   ├── config.py          # Settings and environment configuration
│   ├── evaluator.py       # Gemini prompt logic & dynamic persona execution
│   ├── models.py          # Pydantic schemas (Tweet, AuditResult)
│   ├── parser.py          # Streaming parser for tweets.js archive files
│   ├── personas.py        # System instructions for audit personas
│   ├── runner.py          # Core pipeline orchestration & CSV export
│   └── state.py           # Audit state manager & progress tracking
├── tests/
│   ├── test_evaluator.py  # Tests for persona selection and API mocking
│   ├── test_models.py     # Tests for tweet date parsing and schemas
│   ├── test_parser.py     # Tests for archive parsing & stream extraction
│   ├── test_runner.py     # Tests for CSV export & pipeline execution
│   └── test_state.py      # Tests for state persistence and recovery
├── data/
│   └── tweets.js          # (Optional) Local Twitter archive file for CLI tests
├── requirements.txt
├── pytest.ini
└── README.md
```

---

## 🚀 Getting Started

### 1. Prerequisites

- Python 3.10+
- A [Google Gemini API key](https://aistudio.google.com/app/apikey)

### 2. Installation

Clone the repository and set up a virtual environment:

```powershell
# Clone the repository
git clone https://github.com/jammijuix/tweet_audit.git
cd tweet_audit

# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate      # On Windows
# source .venv/bin/activate # On Linux/macOS

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Variables

Create a `.env` file in the root directory:

```env
GEMINI_API_KEY="your-gemini-api-key-here"
GEMINI_MODEL="gemini-3.5-flash"
```

> ⚠️ Never commit your `.env` file. Make sure it's listed in `.gitignore`.

---

## 🧪 Running Tests

Ensure all unit tests pass before running or deploying:

```powershell
# Set Python path to current root directory
$env:PYTHONPATH = "."

# Run full test suite
py -m pytest -v
```

To run individual test modules:

```powershell
py -m pytest -v tests/test_evaluator.py
py -m pytest -v tests/test_runner.py
```

---

## 💻 CLI Usage

You can test the auditing pipeline directly from your terminal before running the web backend.

1. Unzip your Twitter archive and copy `data/tweets.js` into the `data/` directory.
2. Run the audit runner:

   ```powershell
   $env:PYTHONPATH = "."
   python -m scr.runner
   ```

3. Choose your audit persona from the prompt:

   ```text
   --- Select Audit Persona ---
   [1] Corporate & Recruiter Ready
   [2] Anti-Cringe & Teen Drama
   [3] Naija Banter vs. Real Hate
   [4] Safe For Work (SFW)
   [5] Clumsy & Bad Takes

   Select a persona (1-5) [Default: 1]: 1
   ```

Flagged tweets are saved automatically to `flagged_tweets.csv`.

---

## 📄 Output Format

`flagged_tweets.csv` contains one row per flagged tweet:

| Column | Description |
|---|---|
| `tweet_url` | Direct link to the flagged tweet |
| `deleted` | Tracks whether the tweet has been removed (for downstream cleanup scripts or manual review) |

---

## 🔒 Privacy

- Only `data/tweets.js` is used. Media files from your archive are never needed.
- Tweets are streamed and processed in-memory; raw posts are not persisted to disk.
- The only local artifacts are the progress checkpoint (`audit_state.json`) and the flagged-tweets CSV.
