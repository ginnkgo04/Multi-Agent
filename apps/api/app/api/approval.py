from __future__ import annotations

from typing import Any

from app.models.schemas import ApprovalContextRead


def build_approval_context(record) -> ApprovalContextRead | None:
    if record is None:
        return None
    plan_payload = dict(record.plan_payload or {}) if isinstance(record.plan_payload, dict) else {}
    execution_contract = plan_payload.get("execution_contract", {})
    interfaces = plan_payload.get("interfaces", [])
    architecture_decisions = plan_payload.get("architecture_decisions", [])
    remediation_plan = plan_payload.get("remediation_plan", {})
    return ApprovalContextRead(
        summary=_stringify(record.summary),
        plan_kind=_stringify(record.plan_kind) or "initial",
        approval_state=_stringify(record.approval_state) or "pending",
        execution_contract=_as_dict(execution_contract),
        interfaces=_as_dict_list(interfaces),
        architecture_decisions=_as_string_list(architecture_decisions),
        remediation_plan=_as_dict(remediation_plan),
    )


def _stringify(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    return str(value)


def _as_dict(value: Any) -> dict[str, Any]:
    return dict(value) if isinstance(value, dict) else {}


def _as_dict_list(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [dict(item) for item in value if isinstance(item, dict)]


def _as_string_list(value: Any) -> list[str]:
    if isinstance(value, str):
        text = value.strip()
        return [text] if text else []
    if not isinstance(value, list):
        return []
    normalized: list[str] = []
    for item in value:
        text = _stringify(item).strip()
        if text:
            normalized.append(text)
    return normalized
