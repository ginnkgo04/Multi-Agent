from datetime import datetime, timezone

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.routes import get_run_quality_gate
from app.api.serializers import to_cycle_summary
from app.db import Base
from app.models.records import CycleRecord, NodeExecutionRecord, ProjectRecord, RunRecord


def make_session() -> Session:
    engine = create_engine(
        "sqlite://",
        future=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    testing_session_local = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
        class_=Session,
    )
    return testing_session_local()


def seed_run(session: Session) -> None:
    created_at = datetime.now(timezone.utc)
    session.add(ProjectRecord(id="project-1", name="Demo", description="Demo", created_at=created_at))
    session.add(
        RunRecord(
            id="run-1",
            project_id="project-1",
            requirement="Build a sakura page",
            status="RUNNING",
            current_cycle=2,
            max_cycles=3,
            provider_name="openai",
            embedding_provider_name="Qwen",
            manual_approval=False,
            template_context={},
            template_context_origin="explicit",
            created_at=created_at,
            updated_at=created_at,
        )
    )


def test_to_cycle_summary_hides_quality_report_until_qt_completes() -> None:
    session = make_session()
    seed_run(session)
    created_at = datetime.now(timezone.utc)
    cycle = CycleRecord(
        id="cycle-2",
        run_id="run-1",
        cycle_index=2,
        status="RUNNING",
        quality_report={
            "status": "FAIL",
            "defect_list": [],
            "root_cause_guess": "",
            "retest_scope": [],
            "remediation_requirement": "",
        },
        created_at=created_at,
        updated_at=created_at,
    )
    session.add(cycle)
    session.add(
        NodeExecutionRecord(
            id="node-qt",
            run_id="run-1",
            cycle_id="cycle-2",
            role="QT",
            batch_index=3,
            status="RUNNING",
            retry_count=0,
            task_spec={},
        )
    )
    session.commit()

    summary = to_cycle_summary(session, cycle)

    assert summary.quality_report is None


def test_get_run_quality_gate_prefers_latest_completed_qt_report() -> None:
    session = make_session()
    seed_run(session)
    created_at = datetime.now(timezone.utc)
    previous_cycle = CycleRecord(
        id="cycle-1",
        run_id="run-1",
        cycle_index=1,
        status="FAILED",
        quality_report={
            "status": "FAIL",
            "defect_list": [
                {
                    "id": "QT-001",
                    "description": "Missing responsive footer",
                    "severity": "high",
                    "location": "workspace/frontend/index.html",
                    "suggestion": "Add footer layout rules.",
                }
            ],
            "root_cause_guess": "Footer contract was skipped in implementation.",
            "retest_scope": ["footer", "mobile layout"],
            "remediation_requirement": "Fix the footer before delivery.",
        },
        created_at=created_at,
        updated_at=created_at,
    )
    active_cycle = CycleRecord(
        id="cycle-2",
        run_id="run-1",
        cycle_index=2,
        status="RUNNING",
        quality_report={
            "status": "FAIL",
            "defect_list": [],
        },
        created_at=created_at,
        updated_at=created_at,
    )
    session.add_all([previous_cycle, active_cycle])
    session.add(
        NodeExecutionRecord(
            id="node-qt-cycle-1",
            run_id="run-1",
            cycle_id="cycle-1",
            role="QT",
            batch_index=3,
            status="COMPLETED",
            retry_count=0,
            task_spec={},
        )
    )
    session.add(
        NodeExecutionRecord(
            id="node-qt-cycle-2",
            run_id="run-1",
            cycle_id="cycle-2",
            role="QT",
            batch_index=3,
            status="RUNNING",
            retry_count=0,
            task_spec={},
        )
    )
    session.commit()

    response = get_run_quality_gate("run-1", session=session)

    assert response.cycle_id == "cycle-1"
    assert response.report is not None
    assert response.report.root_cause_guess == "Footer contract was skipped in implementation."
    assert response.report.retest_scope == ["footer", "mobile layout"]
