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
3. [Project Structure](#project-structure)
4. [Configuration](#configuration)
5. [Using PostgreSQL](#using-postgresql)
6. [API Reference](#api-reference)
7. [System Diagram](#system-diagram)
8. [Security Notes](#security-notes)
9. [Roadmap](#roadmap)
10. [Contributing](#contributing)
11. [License](#license)

---

## Features
- **FastAPI** with automatic interactive docs at `/docs`.
- **SQLite** out-of-the-box, optional **PostgreSQL** support.
- Periodic RSS fetcher script (cron-friendly).
- Simple daily digest endpoint.
- Modular routers (`/sources`, `/articles`).
- Typed models with **Pydantic**.
- One-command setup (see below).

---

## Quick Start

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
├── config.ini
└── requirements.txt
```

---

## Configuration

| Key              | Default                 | Description                           |
| ---------------- | ----------------------- | ------------------------------------- |
| `DB_URL`         | `sqlite:///rssgpt.db`   | SQLAlchemy URL                        |
| `FETCH_INTERVAL` | *None*                  | If set, the fetcher loops every N sec |
| `OPENAI_API_KEY` | *env* var / `.env` file | For downstream AI usage               |

> **Tip:** Copy `config.ini.example` to `config.ini` and tweak as needed.

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
