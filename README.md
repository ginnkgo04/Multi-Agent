# Multi-Agent Orchestration Platform

A full-stack platform for multi-agent software delivery workflows. It combines FastAPI, LangGraph-inspired orchestration, RAG, persistent artifacts, and a Next.js dashboard with real-time SSE updates.

## Workspace layout

- `apps/api`: FastAPI backend, orchestration runtime, providers, persistence, tests
- `apps/web`: Next.js dashboard for live run monitoring
- `data/`: local database and seeded runtime state
- `tasks/`: generated task workspaces, organized by run and cycle

## Core workflow

`PC -> CA -> FD + BD -> DE -> QT`

If QT fails, the orchestrator generates a remediation requirement and restarts from `CA`. Each run supports up to three cycles.

## Quick start

### Conda

```bash
cd /Users/apple/Agent/Multi-Agent
conda env create -f environment.yml
conda activate Multi-Agent
```

### Backend

```bash
cd /Users/apple/Agent/Multi-Agent/apps/api
uvicorn app.main:app --reload
```

### Frontend

```bash
cd /Users/apple/Agent/Multi-Agent/apps/web
npm install
npm run dev
```

### Tests

```bash
cd /Users/apple/Agent/Multi-Agent/apps/api
PYTHONPATH=. pytest tests
```

### Full stack with Docker

```bash
docker compose up --build
```

## Demo flow

1. In `apps/api`, start FastAPI and make sure `apps/api/.env` contains the backend settings you want to use.
2. In `apps/web`, start Next.js and open the dashboard in the browser.
3. Create a project from the dashboard or via `POST /api/projects`.
4. Start a run with a feature request.
5. Watch the DAG, live event stream, task artifacts, and cycle history update in real time.
6. Inspect generated implementation files under `tasks/<run_id>/cycles/cycle-xx/`.
7. Resume blocked runs via `POST /api/runs/{id}/resume`.

## Notable implementation details

- SQLAlchemy-backed persistence works with SQLite by default and PostgreSQL in Docker.
- Provider adapters support live OpenAI-compatible chat and embedding APIs, including OpenAI and DeepSeek-style endpoints configured through `apps/api/.env`.
- RAG retrieval is vector-based, with embeddings stored in the database and artifact files persisted under `tasks/<run_id>/cycles/cycle-xx/`.
- The runtime emits structured events for every state transition, enabling replay and live streaming.
