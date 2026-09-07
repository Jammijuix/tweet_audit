# Implementation Trade-offs & Design Decisions

### 1. Architecture Choices: Modular Pipeline with Clean Separation of Concerns
The application follows a modular, single-responsibility pipeline (`parser` -> `evaluator` -> `state` -> `runner`). 
* **Why this pattern?** It decouples data ingestion, LLM inference, and persistence. The parsing layer isolates messy Twitter archive data structures from the evaluation engine. This makes individual components independently testable using mocks without requiring network calls or real archive dumps.

### 2. Concurrency Strategy: Sequential Execution with Configurable Delay
* **Decision:** Sequential evaluation loop using Python generators (`yield`) paired with a deterministic delay (`time.sleep`).
* **Why not full async/batching?** The primary operational constraint is external: free-tier Gemini API rate limits (5–15 RPM). High-concurrency async pipelines (`asyncio`/`aiohttp`) add complexity around semaphores, backpressure, and burst handling without providing throughput benefits under hard RPM caps. Sequential streaming provides deterministic rate-limiting and a minimal memory footprint regardless of archive size.

### 3. Error Handling Approach: Resilient Fallback and Log & Continue
* **Strategy:** Fail-safe isolation per tweet.
* **Why?** An audit over thousands of historical tweets should not abort mid-run due to an individual malformed record or an intermittent API error.
  * **API Errors:** Caught gracefully and assigned an unflagged fallback `AuditResult` (`category="api_error"`).
  * **Corrupted Archive Rows:** Logged and skipped during parsing.
  * **Atomic State Persistence:** State writes use atomic file operations (`.tmp` write followed by `os.replace`) to eliminate state file corruption during unexpected termination.

### 4. Performance vs. Safety Trade-offs
* **Strict Schema Decoding over Raw Text Speed:** Enforcing Gemini structured outputs via Pydantic schemas adds minor token overhead compared to unstructured output. However, it eliminates brittle regex parsing and JSON decoding errors.
* **Immediate Checkpointing over Batched Disk Writes:** Persisting state to disk after every processed tweet trades minor I/O performance for guaranteed crash recovery and idempotent restarts.

### 5. Language & Framework Choices
* **Python 3.10+:** Industry standard for AI integration, providing first-class SDK support for Google GenAI.
* **Pydantic v2:** Provides robust data validation, automatic type casting, and native JSON schema generation for structured LLM outputs.
* **Standard Library Priority:** Used built-in modules (`json`, `csv`, `pathlib`, `logging`, `html`) to minimize external dependency bloat and ensure high maintainability.