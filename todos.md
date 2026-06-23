# Document Copilot — implementation checklist

Work top to bottom. Each phase unlocks the next. Check items off as you go.

## Current status snapshot (2026-06-17)

- Supabase local stack is running via Docker (`supabase start`)
- Local DB URL is active (`postgresql://postgres:postgres@127.0.0.1:54322/postgres`)
- Alembic revision is applied at head (`dd1a1c1dda28`)
- Backend health endpoint is returning `200` on `GET /health`

## Where to start: backend, frontend, or both?

**Start with foundation, then backend-led vertical slices.**

| Order | Why |
| ----- | --- |
| 1. Supabase local stack + sample data | Everything persists here; you need local infra and a corpus to test against. |
| 2. Backend schema + migrations | Auth, chat, retrieval, and citations all depend on the data model. |
| 3. Thin vertical slices | Wire auth, then a stubbed chat stream, then real RAG — each slice touches frontend + backend together. |
| 4. Frontend in parallel (lightly) | Scaffold the SPA early, but don't build citation UI or chat polish until the backend can return real grounded answers. |

The critical path is **data model → ingestion → retrieval → LLM → citations**. The frontend is mostly a streaming chat shell with auth and citation display — it shouldn't get far ahead of working APIs.

---

## Phase 0 — Prerequisites & foundation

- [x] Install toolchain: Python 3.12+, `uv`, Node 20+, `pnpm` (see [README](README.md))
- [x] Initialize Supabase local stack (`supabase init` + `supabase start`) and collect local credentials ([supabase-setup](docs/guides/supabase-setup.md))
- [x] Create Gemini API key (Google Gen AI) (needed from Phase 4 onward)
- [x] Set `USER_AGENT` in `data/download.py` and download sample 10-K corpus:
  ```bash
  uv run data/download.py
  ```
- [x] Confirm `data/downloads/manifest.json` lists AAPL, MSFT, NVDA, AMZN, GOOGL filings (2021–2025)

---

## Phase 1 — Backend scaffold & database

Goal: a running FastAPI service with a migrated Supabase schema (local stack in dev).

- [x] Init backend deps and project layout ([backend-setup](docs/guides/backend-setup.md))
- [x] `app/config.py` — settings module, fail fast on missing env vars
- [x] `app/main.py` — FastAPI app, CORS, health check (`GET /health`)
- [x] SQLAlchemy models in `app/database/models/`:
  - [x] `users`
  - [x] `source_documents`
  - [x] `document_chunks` (embedding + generated `tsvector`)
  - [x] `chat_threads`
  - [x] `chat_messages`
  - [x] `message_citations`
- [x] Alembic init + first migration:
  - [x] `create extension if not exists vector`
  - [x] embedding column with dimension matching the selected Gemini embedding model
  - [x] generated `tsvector` column on chunks
  - [x] HNSW index (vector) + GIN index (full-text)
  - [x] RLS policies (users see only their own chats)
- [x] `uv run alembic upgrade head` against local Supabase DB (`127.0.0.1:54322`)
- [x] `app/database/supabase.py` — user-scoped and service-role clients
- [x] Verify: `uv run uvicorn app.main:app --reload` → health check returns 200

---

## Phase 2 — Auth (full stack)

Goal: analysts can sign in with email; backend rejects unauthenticated requests.

**Backend**

- [x] `app/auth/dependencies.py` — verify `Authorization: Bearer <supabase_jwt>`, expose `get_current_user`
- [x] Reject missing/expired tokens with `401` before any chat or retrieval work

**Frontend**

- [x] Scaffold Vite + React + TypeScript + Tailwind + shadcn ([frontend-setup](docs/guides/frontend-setup.md))
- [x] `src/lib/env.ts` — validate `VITE_API_BASE_URL`, `VITE_SUPABASE_URL`, `VITE_SUPABASE_ANON_KEY`
- [x] `src/lib/supabase.ts` — browser Supabase client
- [x] `src/lib/http.ts` + `src/lib/api.ts` — fetch wrapper with automatic bearer token
- [x] Sign-in / sign-up pages (email only, no SSO)
- [x] Protected routes — redirect unauthenticated users to login
- [x] Verify: sign up, sign in, token reaches backend on a test authenticated endpoint

---

## Phase 3 — Chat shell (vertical slice, stubbed)

Goal: end-to-end chat UI streaming from FastAPI, no real retrieval yet.

**Backend**

- [x] Chat thread CRUD: list threads, create thread, load message history
- [x] `POST /chat/stream` — accepts AI SDK message format, streams a stubbed assistant reply
- [x] Persist user + assistant messages to `chat_messages` after stream completes
- [x] `403` when user accesses another user's thread

**Frontend**

- [x] React Router: login, chat list, chat thread routes
- [x] AI SDK chat primitives pointed at `POST /chat/stream` with Supabase bearer token
- [x] Thread sidebar (past conversations)
- [x] Basic message list + input + streaming indicator
- [x] Verify: create thread, send message, see streamed stub response, reload and see history

---

## Phase 4 — Ingestion pipeline

Goal: SEC filings in the corpus are parsed, chunked, embedded, and stored in Supabase.

- [x] `ingest/` scripts (or CLI entrypoint) for one-off corpus loading
- [x] HTML → normalized Markdown extraction (preserve page/section metadata)
- [x] Chunking strategy (size + overlap; store chunk index, page, section, ticker, filing type, year)
- [x] Write `source_documents` rows with filing metadata from `manifest.json`
- [x] Write `document_chunks` rows with text + metadata
- [x] Gemini embeddings generation (Google Gen AI) → store vectors with the model's configured dimension
- [x] Generated `tsvector` populated for full-text search
- [x] Idempotent re-run (skip already-ingested documents)
- [x] Unit tests: chunking logic, metadata extraction
- [x] Run ingestion on full sample corpus (25 filings × 5 companies)
- [x] Verify: chunks exist in Supabase; spot-check a known passage (e.g. Apple revenue mix table)

---

## Phase 5 — Retrieval

Goal: a user question returns ranked, relevant source passages.

- [ ] `retrieval/queries.py` — pgvector semantic search over `document_chunks`
- [ ] `retrieval/queries.py` — Postgres full-text search over `search_vector`
- [ ] `retrieval/fusion.py` — Reciprocal Rank Fusion in Python
- [ ] `retrieval/retriever.py` — query → fused ranked passages + neighbor chunks
- [ ] Unit tests: fusion ranking, query assembly (mock DB)
- [ ] Integration test (optional, `@pytest.mark.integration`): real query against ingested corpus
- [ ] Verify: test queries from [client-brief](docs/client-brief.md) return relevant chunks (manual or scripted)

---

## Phase 6 — LLM agent & grounding

Goal: grounded answers with enforced citations — the core product contract.

- [ ] `assistant/instructions.md` — product contract (cite everything, refuse to invent, no stock picks)
- [ ] PydanticAI agent with typed deps (`DocumentAgentDeps`) and output (`GroundedAnswer`)
- [ ] Agent tools: `search_filings`, `read_chunk`, `read_surrounding_chunks`
- [ ] `chat/orchestrator.py` — one turn: retrieve → agent → validate → stream → persist
- [ ] `grounding/validator.py` — every citation maps to a retrieved passage; fail closed on violation
- [ ] `chat/streaming.py` — AI SDK-compatible stream (text deltas + citation metadata parts)
- [ ] Persist `message_citations` linked to assistant messages
- [ ] Unit tests: citation validation, grounding enforcement, message conversion
- [ ] Verify against [client-brief example questions](docs/client-brief.md#example-analyst-questions):
  - [ ] Answers cite specific filings and pages
  - [ ] Under-specified questions get "not enough evidence" responses
  - [ ] Question 10 (generative AI margins) refuses to infer beyond filings

---

## Phase 7 — Trust UI (citations & source passages)

Goal: analysts can verify every claim in one click — this is what makes the product usable.

- [ ] Citation chips/links on assistant messages (company, filing type, date, page/section)
- [ ] Source passage panel — show underlying excerpt for selected citation
- [ ] Empty states (no threads, no corpus match)
- [ ] Error states (auth expired, retrieval failure, grounding failure, network/CORS)
- [ ] Loading/streaming status during assistant run
- [ ] Verify: click a citation → see the exact passage from the filing

---

## Phase 8 — Pilot readiness

Goal: 5 senior analysts can use it for a week and report ≥3 hours saved per analyst per week.

- [ ] README "Running locally" section — copy-paste commands for backend + frontend + env vars
- [ ] Seed or document how to ingest/update the corpus
- [ ] Smoke-test all 10 example questions from the client brief
- [ ] Confirm chat history persists across sessions
- [ ] Confirm ~40-user scale assumptions (no hardcoded single-user shortcuts)
- [ ] Basic structured logging on backend (`structlog`) for debugging failed turns
- [ ] Review latency: streaming starts within a few seconds for typical queries

---

## Phase 9 — Deployment (Railway)

- [ ] Railway: backend service (Uvicorn, env vars, `ALLOWED_ORIGINS`)
- [ ] Railway: frontend service (Vite build, `VITE_*` env vars at build time)
- [ ] Supabase: re-enable email confirmation for production if disabled during dev
- [ ] Run `alembic upgrade head` against production Supabase (direct connection)
- [ ] Run ingestion against production database
- [ ] End-to-end test on deployed URLs with a real Driftwood-style email account

---

## Quick reference

| Doc | Purpose |
| --- | ------- |
| [docs/client-brief.md](docs/client-brief.md) | What Driftwood needs and example questions |
| [docs/architecture.md](docs/architecture.md) | System design, data model, streaming contract |
| [docs/guides/supabase-setup.md](docs/guides/supabase-setup.md) | Supabase local stack (Docker) + env wiring |
| [docs/guides/backend-setup.md](docs/guides/backend-setup.md) | FastAPI + Alembic commands |
| [docs/guides/frontend-setup.md](docs/guides/frontend-setup.md) | Vite + React scaffold commands |

