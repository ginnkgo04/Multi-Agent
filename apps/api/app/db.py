from collections.abc import Generator

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import get_settings

settings = get_settings()
connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(settings.database_url, future=True, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False, class_=Session)


class Base(DeclarativeBase):
    pass


def get_session() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def init_db() -> None:
    from app.models import records  # noqa: F401

    Base.metadata.create_all(bind=engine)
    _ensure_schema_compatibility()


def _ensure_schema_compatibility() -> None:
    inspector = inspect(engine)
    if "node_executions" in inspector.get_table_names():
        _ensure_column("node_executions", "context_snapshot", "JSON")
    if "runs" in inspector.get_table_names():
        _ensure_column("runs", "template_context_origin", "VARCHAR(32) DEFAULT 'explicit'")
    if "memory_summaries" in inspector.get_table_names():
        _ensure_column("memory_summaries", "project_id", "VARCHAR(64)")
    if "shared_plans" in inspector.get_table_names():
        _ensure_column("shared_plans", "plan_kind", "VARCHAR(32) DEFAULT 'initial'")
        _ensure_column("shared_plans", "approval_state", "VARCHAR(32) DEFAULT 'pending'")
        _ensure_column("shared_plans", "parent_plan_id", "VARCHAR(64)")


def _ensure_column(table_name: str, column_name: str, column_sql: str) -> None:
    inspector = inspect(engine)
    columns = {column["name"] for column in inspector.get_columns(table_name)}
    if column_name in columns:
        return
    with engine.begin() as connection:
        connection.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_sql}"))
