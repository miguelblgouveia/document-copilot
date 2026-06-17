# Supabase setup

We use Supabase for **Postgres** (users, chats, source documents, chunks, embeddings, and citations) and **Auth** (email sign-in only). For this project, local development is based on the Supabase local stack running in Docker.

## 1. Prerequisites

1. Install [Docker Desktop](https://www.docker.com/products/docker-desktop/) and make sure the Docker daemon is running.
2. Install [Supabase CLI](https://supabase.com/docs/guides/local-development/cli/getting-started).
3. Confirm both are available:

```bash
docker info
supabase --version
```

## 2. Start Supabase locally

From the repository root:

```bash
supabase init
supabase start
```

Then inspect local endpoints and keys:

```bash
supabase status
```

Typical local values are:

- Project URL: `http://127.0.0.1:54321`
- Database URL: `postgresql://postgres:postgres@127.0.0.1:54322/postgres`
- Studio: `http://127.0.0.1:54323`

## 3. Wire credentials into backend/frontend

Set values in `backend/.env`:

```bash
SUPABASE_URL=http://127.0.0.1:54321
SUPABASE_ANON_KEY=<value from supabase status>
SUPABASE_SERVICE_ROLE_KEY=<value from supabase status>
DATABASE_URL=postgresql://postgres:postgres@127.0.0.1:54322/postgres
```

For frontend env, use the same `SUPABASE_URL` and anon key (never use `service_role` in browser code).

## 4. Auth settings (email only)

The local stack already includes Supabase Auth. For local testing, email auth works without setting up third-party providers.

If you also use a hosted Supabase project later, configure Auth there as email-only:

1. Dashboard → **Authentication** → **Providers**.
2. Leave **Email** enabled.
3. Optionally disable email confirmation in dev-only environments.

## 5. Database schema management

Document Copilot uses Alembic from the Python backend to manage schema. Do not create app tables manually in Studio.

From `backend/`:

```bash
uv run alembic upgrade head
```

Alembic migrations in this project create and update:

- the `vector` extension for `pgvector`
- source document and chunk tables
- embedding columns
- generated full-text search columns
- HNSW and GIN indexes
- chat and citation tables
- row-level security policies

## 6. Useful local commands

```bash
supabase status   # print local URLs, keys, ports
supabase stop     # stop local stack
supabase start    # start existing stack again
supabase db reset # reset local DB and re-run local migrations/seed
```

## 7. Costs

Running Supabase locally with Docker has no Supabase cloud billing cost. You only use local machine resources (CPU, RAM, disk, and image downloads).

## Optional: hosted Supabase later

You can still use a hosted project for shared environments or production. In that case:

- Keep Alembic on the direct/session DB connection (not pooler) whenever possible.
- Store cloud keys in environment variables/secrets.
- Keep `service_role` out of frontend and out of git.

## Next steps

- [Backend setup](backend-setup.md) — Python service + Supabase client
- [Frontend setup](frontend-setup.md) — React app + `@supabase/supabase-js`
