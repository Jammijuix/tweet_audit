# TweetAudit

Audit, filter, and sanitize your historical Twitter/X posts using Gemini structured outputs, customizable audit personas, and zero data persistence.

---

## Overview

Exporting your personal Twitter/X archive bundles gigabytes of media files, making direct full-archive analysis slow, resource-heavy, and bandwidth-expensive.

**TweetAudit** solves this by targeting only the lightweight `data/tweets.js` file (typically under 1MB). It streams archive tweets in-memory, checks each post against a chosen personal-brand standard (an *audit persona*) using Gemini structured JSON outputs, and generates an actionable cleanup CSV of posts that need deletion.

---

## Features

- **In-Memory Streaming Parser**: Reads `data/tweets.js` directly from uploaded bytes using custom delimiters, without persisting raw posts to disk.
- **Custom Audit Personas**: Choose from 5 tailored auditing profiles:

  | Persona | Description |
  |---|---|
  | `corporate` | Recruiter-ready. Flags workplace attacks, vulgarity, and unprofessional rants. |
  | `anti_cringe` | Flags teenage melodrama, oversharing, and edge-lord posts. |
  | `naija_street` | Tailored to Nigerian digital discourse. Safeguards local Pidgin banter, satire, and slang while strictly flagging scams, ethnic bigotry, and harassment. |
  | `sfw` | Strict filtering for NSFW or explicit language. |
  | `clumsy_takes` | Detects aged hot takes, poorly aged opinions, and flawed arguments. |

- **Structured JSON Audits**: Enforces strict Pydantic schemas (`flagged`, `confidence`, `category`, `reason`) using Gemini structured outputs.
- **Stateful Resumption and Error Handling**: Checkpoints audit progress locally (`audit_state.json`) so interrupted runs resume safely without re-evaluating duplicate tweets.
- **Clean CSV Export**: Outputs flagged tweets as a CSV (`tweet_url`, `deleted`) ready for downstream cleanup scripts or manual review.
- **Web Dashboard**: A FastAPI backend paired with a Next.js frontend for uploading and auditing archives directly through the browser.

---

## Project Structure

```text
tweet_audit/
├── scr/
│   ├── config.py          # Settings and environment configuration
│   ├── evaluator.py       # Gemini prompt logic and dynamic persona execution
│   ├── models.py          # Pydantic schemas (Tweet, AuditResult)
│   ├── parser.py          # Streaming parser for tweets.js archive files
│   ├── personas.py        # System instructions and Enum for audit personas
│   ├── runner.py          # Core pipeline orchestration and CSV export
│   ├── state.py           # Audit state manager and progress tracking
│   └── main.py            # FastAPI stateless backend routes
├── frontend/               # Next.js web application
│   ├── app/                # App Router pages, layout, and global styles
│   ├── package.json        # Frontend dependencies and scripts
│   └── next.config.ts      # Next.js configuration
├── tests/
│   ├── test_evaluator.py  # Tests for persona selection and API mocking
│   ├── test_models.py     # Tests for tweet date parsing and schemas
│   ├── test_parser.py     # Tests for archive parsing and stream extraction
│   ├── test_runner.py     # Tests for CSV export and pipeline execution
│   └── test_state.py      # Tests for state persistence and recovery
├── data/
│   └── tweets.js          # (Optional) Local Twitter archive file for CLI tests
├── requirements.txt
├── pytest.ini
└── README.md
```

---

## Getting Started

### 1. Prerequisites

- Python 3.10+
- Node.js 18+ (for running the frontend)
- A Google Gemini API key

### 2. Installation

Clone the repository and set up a virtual environment:

```bash
# Clone the repository
git clone https://github.com/jammijuix/tweet_audit.git
cd tweet_audit

# Create and activate virtual environment
python -m venv .venv

# On Windows
.venv\Scripts\activate

# On Linux/macOS
# source .venv/bin/activate

# Install backend dependencies
pip install -r requirements.txt
```

### 3. Environment Variables

Create a `.env` file in the root directory:

```env
GEMINI_API_KEY="your-gemini-api-key-here"
GEMINI_MODEL="gemini-1.5-flash"
MOCK_AUDIT="false"
```

> Never commit your `.env` file. Ensure it is listed in `.gitignore`.

---

## Running Tests

Ensure all unit tests pass before running or deploying:

```powershell
# Set Python path to current root directory
$env:PYTHONPATH = "."

# Run full test suite
python -m pytest -v
```

To run individual test modules:

```powershell
python -m pytest -v tests/test_evaluator.py
python -m pytest -v tests/test_runner.py
```

---

## Usage

### CLI Execution

You can test the auditing pipeline directly from your terminal:

1. Unzip your Twitter archive and place `data/tweets.js` inside the `data/` folder.
2. Execute the runner module:

   ```powershell
   $env:PYTHONPATH = "."
   python -m scr.runner
   ```

3. Choose your audit persona from the interactive prompt:

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

### Web Dashboard Execution

To launch the web interface:

1. Start the FastAPI backend:

   ```powershell
   uvicorn scr.main:app --reload --port 8000
   ```

2. In a separate terminal, launch the Next.js frontend:

   ```bash
   cd frontend
   npm install
   npm run dev
   ```

3. Open `http://localhost:3000` to upload `tweets.js` directly through the browser.

---

## Output Format

`flagged_tweets.csv` contains one row per flagged tweet:

| Column | Description |
|---|---|
| `tweet_url` | Direct link to the flagged tweet on Twitter/X |
| `category` | The policy or tone rule triggered by the persona |
| `reason` | Short explanatory justification generated by the model |
| `deleted` | Boolean tracking whether the post has been removed (for downstream scripts) |

---

## Privacy Architecture

- Only `data/tweets.js` is processed; media files (images, videos, direct messages) are ignored completely.
- Archives are read and parsed directly from memory byte streams without saving copies to disk or remote servers.
- The only local artifacts created are progress tracking files (`audit_state.json`) and the flagged results CSV.
