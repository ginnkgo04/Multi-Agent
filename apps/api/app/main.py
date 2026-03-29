from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select

from app.api.routes import router
from app.config import get_settings
from app.db import SessionLocal, init_db
from app.models.records import ProjectRecord
from app.models.schemas import ProjectCreate
from app.services.container import get_container

settings = get_settings()
container = get_container()
app = FastAPI(title=settings.app_name)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.api_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router, prefix=settings.api_prefix)


@app.on_event("startup")
def on_startup() -> None:
    init_db()
    with SessionLocal() as session:
        container.memory_service.backfill_project_ids(session)
        container.context_document_service.bootstrap(session)
        container.provider_registry.seed_defaults(session)
        existing_project = session.scalar(select(ProjectRecord).limit(1))
        if existing_project is None:
            container.requirement_intake.create_project(
                session,
                ProjectCreate(
                    name="Primary Workspace",
                    description="Default workspace for real multi-agent implementation runs.",
                ),
            )


@app.on_event("shutdown")
async def on_shutdown() -> None:
    await container.runtime.shutdown()
