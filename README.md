# RSS-GPT <!-- omit in toc -->

<p align="center">
  <img src="https://img.shields.io/badge/FastAPI-0.110+-green?style=flat-square" alt="FastAPI">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square" alt="Python">
  <img src="https://img.shields.io/badge/License-MIT-lightgrey?style=flat-square" alt="License">
</p>

A lightweight **FastAPI** backend that aggregates RSS feeds, stores articles, and exposes a clean REST API—perfect for powering newsletters, dashboards, or AI-driven summarizers.

---

## Table of Contents <!-- omit in toc -->
1. [Features](#features)
2. [Quick Start](#quick-start)
3. [AI Summarization with OpenAI](#ai-summarization-with-openai)
4. [Project Structure](#project-structure)
5. [Configuration](#configuration)
6. [Using PostgreSQL](#using-postgresql)
7. [API Reference](#api-reference)
8. [System Diagram](#system-diagram)
9. [Security Notes](#security-notes)
10. [Roadmap](#roadmap)
11. [Contributing](#contributing)
12. [License](#license)

---

## Features
- **FastAPI** with automatic interactive docs at `/docs`.
- **SQLite** out-of-the-box, optional **PostgreSQL** support.
- Periodic RSS fetcher script (cron-friendly).
- **AI-powered article summarization and keyword extraction using OpenAI** (scheduled every 12 hours).
- Simple daily digest endpoint.
- Modular routers (`/sources`, `/articles`).
- Typed models with **Pydantic**.
- One-command setup (see below).

---

## Quick Start

---

## AI Summarization with OpenAI

This project supports automated article summarization and keyword extraction using OpenAI's GPT models. Every 12 hours, a batch job fetches new RSS articles, generates summaries and keywords, and stores them in the database.

### Setup

1. **Obtain an OpenAI API Key**
   Sign up at [OpenAI](https://platform.openai.com/account/api-keys) and create an API key.

2. **Set Environment Variables**
   Export your OpenAI API key (and optionally, model and language) in your shell or systemd/cron environment:
   ```sh
   export OPENAI_API_KEY=your_openai_api_key
   export OPENAI_MODEL=gpt-4.1-mini     # Optional, default: gpt-4.1-mini
   export SUMMARY_LANGUAGE=fr           # Optional, default: fr
   export SUMMARY_LENGTH=250            # Optional, default: 250
   export KEYWORD_COUNT=6               # Optional, default: 6
   ```

3. **Manual Run**
   To fetch and summarize articles manually:
   ```sh
   python3 fetch_articles.py
   ```

4. **Scheduled Run (Every 12 Hours)**
   Use the provided script and add this line to your crontab:
   ```sh
   0 */12 * * * /path/to/your/project/run_fetch_articles.sh
   ```
   Make sure to set environment variables in your crontab or source them in the script.

5. **How it Works**
   - The [`llm_summarizer.py`](llm_summarizer.py) module calls OpenAI to generate summaries and keywords for each new article.
   - The [`fetch_articles.py`](fetch_articles.py) script fetches RSS feeds, processes new articles, and stores the results in the database.
   - Summaries and keywords are available via the API.

6. **API Output**
   Article objects returned by the API include `summary`, `keywords`, and `language` fields.

---

## Project Structure

```bash
# 1 Clone
git clone https://github.com/your-username/RSS-GPT.git
cd RSS-GPT

# 2 Create a virtual env
python -m venv .venv && source .venv/bin/activate

# 3 Install deps
pip install -r requirements.txt

# 4 Init DB (SQLite)
python init_db.py

# 5 Run API
uvicorn app:app --reload       # http://127.0.0.1:8000

# 6 (Opt.) Fetch articles
python fetch_articles.py
```

---

## Project Structure

```
rss-gpt/
├── app.py               # FastAPI entry-point
├── routers/
│   ├── articles.py
│   └── sources.py
├── models.py            # SQLAlchemy ORM models
├── schemas.py           # Pydantic models
├── fetch_articles.py    # Cron-capable fetcher
├── init_db.py
└── requirements.txt
```

---

## Configuration

All configuration is handled via environment variables. Example:

```sh
export DB_URL=sqlite:///rssgpt.db
export OPENAI_API_KEY=your_openai_api_key
export OPENAI_MODEL=gpt-4.1-mini
export SUMMARY_LANGUAGE=fr
export SUMMARY_LENGTH=250
export KEYWORD_COUNT=6
```

- `DB_URL`: SQLAlchemy URL (default: `sqlite:///rssgpt.db`)
- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `OPENAI_MODEL`: OpenAI model to use (default: `gpt-4.1-mini`)
- `SUMMARY_LANGUAGE`: Language for summaries (default: `fr`)
- `SUMMARY_LENGTH`: Target summary length in words (default: `250`)
- `KEYWORD_COUNT`: Number of keywords to extract (default: `6`)

---

## Using PostgreSQL

1. Install the driver

   ```bash
   pip install psycopg2-binary
   ```

2. Update the connection string

   ```ini
   DB_URL = postgresql://user:pass@localhost:5432/rssgpt
   ```

3. Re-run `init_db.py` (or your Alembic migrations).

---

## API Reference

Once the server is up, visit **`/docs`** for the full OpenAPI spec.
Key endpoints:

| Method | Path            | Purpose                |
| ------ | --------------- | ---------------------- |
| GET    | `/`             | Health check           |
| GET    | `/sources/`     | List sources           |
| POST   | `/sources/`     | Add a source           |
| PUT    | `/sources/{id}` | Update a source        |
| DELETE | `/sources/{id}` | Delete a source        |
| GET    | `/articles/`    | List / filter articles |

Example: add a new RSS source

```bash
curl -X POST http://127.0.0.1:8000/sources/ \
  -H "Content-Type: application/json" \
  -d '{"name":"Example","url":"https://example.com/rss"}'
```

---

## System Diagram

```mermaid
graph TD
    Client[Client] -->|HTTP| API(FastAPI)
    API --> SourcesRouter
    API --> ArticlesRouter
    SourcesRouter --> DB[(SQLite/PostgreSQL)]
    ArticlesRouter --> DB
```

---

## Security Notes

* **Authentication**: *none* (PRs welcome!).
* **CORS**: disabled by default—enable per use-case.
* **Input validation**: handled via Pydantic, but custom URL checks recommended.
* **OpenAI API Key**:  
  Store your OpenAI API key in an environment variable named `OPENAI_API_KEY` (recommended), or in a `.env` file if using `python-dotenv`.  
  **Example:**
  ```bash
  export OPENAI_API_KEY=your-openai-api-key
  ```
  In Python:
  ```python
  import os
  openai_api_key = os.getenv("OPENAI_API_KEY")
  ```
  Never hardcode secrets in your codebase.

---

## Roadmap

* [ ] JWT / API-key auth
* [ ] Pagination & rate limiting
* [ ] Background task queue (Celery/RQ)
* [ ] Dockerfile & CI workflow
* [ ] Unit / integration tests

---

## Contributing

1. Fork the repo & create a feature branch.
2. Run `pre-commit install` (linting, formatting).
3. Open a PR—descriptive title & screenshot/gif if UI-related.

---

## License

MIT © 2025 Your Name
