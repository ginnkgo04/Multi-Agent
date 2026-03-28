# Multi-Agent API

FastAPI backend for orchestrating the PC/CA/FD/BD/DE/QT workflow with persistence, SSE, artifacts, and cycle recovery.

## Run locally

```bash
cd /Users/apple/Agent/Multi-Agent/apps/api
conda activate Multi-Agent
uvicorn app.main:app --reload
```

`apps/api/.env` is read when you start the backend from this directory.
