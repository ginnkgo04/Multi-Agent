from types import SimpleNamespace

import pytest

from app.models.schemas import RunStatus
from app.services.retry_recovery_manager import RetryRecoveryManager


def test_prepare_resume_rejects_completed_run() -> None:
    manager = RetryRecoveryManager()
    run = SimpleNamespace(status=RunStatus.COMPLETED.value)

    with pytest.raises(ValueError, match="Only blocked or running runs can be restarted."):
        manager.prepare_resume(None, run)  # type: ignore[arg-type]
