# Document Copilot

An internal AI chatbot that lets analysts query a corpus of documents in plain English and get sourced, citable answers.

## The client

**Driftwood Capital** — fictional independent investment research firm. Their analysts spend half their week reading 10-Ks and 10-Qs before they can produce any original analysis. Document Copilot eats that intake work so they can skip straight to insight.

Full brief: [docs/client-brief.md](docs/client-brief.md)

## Stack

| Layer              | Choice                                               |
| ------------------ | ---------------------------------------------------- |
| Backend            | Python + FastAPI                                     |
| Frontend           | Vite + React SPA + TypeScript                        |
| Database           | Supabase local stack (Docker) for dev + Postgres     |
| Migrations         | SQLAlchemy models + Alembic                          |
| Retrieval          | Supabase `pgvector` + Postgres full-text search      |
| Auth               | Supabase Auth (email only)                           |
| Hosting            | Railway                                              |
| LLM + embeddings   | Google Gen AI                                        |

## Repo layout

```text
document-copilot/
├── AGENTS.md           # agent instructions (read first)
├── README.md           # this file
├── data/               # local corpus + download script (payloads gitignored)
├── docs/
│   └── client-brief.md # the client one-pager
├── backend/            # FastAPI service
└── frontend/           # React SPA (Vite)
```

## Prerequisites

Install these before setting up `backend/` or `frontend/`:

| Tool | Version | Used for | Install |
| ---- | ------- | -------- | ------- |
| [Python](https://www.python.org/downloads/) | 3.12+ | Backend runtime | OS package manager or python.org |
| [uv](https://docs.astral.sh/uv/getting-started/installation/) | latest | Backend deps + `data/download.py` | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| [Node.js](https://nodejs.org/) | 20+ (LTS) | Frontend toolchain | nodejs.org or `nvm install --lts` |
| [pnpm](https://pnpm.io/installation) | latest | Frontend package manager | `corepack enable && corepack prepare pnpm@latest --activate` |
| [Docker Desktop](https://www.docker.com/products/docker-desktop/) | latest | Run local Supabase stack | docker.com |
| [Supabase CLI](https://supabase.com/docs/guides/local-development/cli/getting-started) | latest | Manage local Supabase stack | `npm install -g supabase` |

You also need external service keys once the app is wired up. Start with [docs/guides/supabase-setup.md](docs/guides/supabase-setup.md) (local stack), then create a [Google Gen AI API key](https://cloud.google.com/genai) when the LLM layer is wired up.

## Running locally

Start local dependencies first:

```bash
supabase start
```

Then follow setup guides:

- [Supabase](docs/guides/supabase-setup.md) — local Docker stack + env wiring
- [Backend](docs/guides/backend-setup.md)
- [Frontend](docs/guides/frontend-setup.md)

## Sample SEC data

Use the standalone downloader to fetch a small local 10-K sample from SEC EDGAR.
Edit the params at the top of `data/download.py`, especially `USER_AGENT`, then run:

```bash
uv run data/download.py
```

By default this downloads the latest 5 10-K filings for AAPL, MSFT, NVDA, AMZN, and GOOGL into year folders under `data/downloads/` and writes a `manifest.json`.
Downloaded files are gitignored; the `data/` folder itself stays in git for the script and notes.

## Para correr o ambiente virtual
(Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned) ; (& d:\dev\PythonProjects\document-copilot\backend\.venv\Scripts\Activate.ps1)

## Para correr o backend
uv run uvicorn app.main:app --reload

## Para aceder à Base de Dados
Primeiro iniciar o docker desktop, depois correr o comando `supabase start` no terminal, e depois aceder à interface do supabase em `http://127.0.0.1:54323/`