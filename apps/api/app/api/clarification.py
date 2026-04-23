from __future__ import annotations

from typing import Any

from app.models.schemas import ClarificationContextRead


ACCEPT_DEFAULTS_MESSAGE = "User accepted the current default assumptions and requested execution to continue."


def build_clarification_context(state: dict[str, Any]) -> ClarificationContextRead:
    pc_output = _as_dict((state.get("node_outputs") or {}).get("PC"))
    intent = _as_dict(pc_output.get("intent"))
    requirement_fidelity = _as_dict(pc_output.get("requirement_fidelity"))

    return ClarificationContextRead(
        requirement_brief=_string_value(pc_output.get("requirement_brief")),
        clarifying_questions=_string_list(intent.get("clarifying_questions")),
        assumed_defaults=_string_list(requirement_fidelity.get("assumed_defaults")),
        acceptance_criteria=_as_dict(pc_output.get("acceptance_criteria")),
        work_breakdown=_string_list(pc_output.get("work_breakdown")),
        clarification_history=_history_list(state.get("clarification_history")),
    )


def normalize_clarification_message(decision: str, message: str) -> str:
    if decision == "accept_defaults":
        return ACCEPT_DEFAULTS_MESSAGE
    if decision == "reject_defaults":
        normalized = message.strip()
        if not normalized:
            raise ValueError("reject_defaults requires feedback in the clarification message.")
        return normalized
    raise ValueError(f"Unsupported clarification decision: {decision}")


def _as_dict(value: Any) -> dict[str, Any]:
    return dict(value) if isinstance(value, dict) else {}


def _string_value(value: Any) -> str:
    if isinstance(value, str):
        return value
    if value is None:
        return ""
    return str(value)


def _string_list(value: Any) -> list[str]:
    if isinstance(value, str):
        text = value.strip()
        return [text] if text else []
    if isinstance(value, list):
        items: list[str] = []
        for item in value:
            text = _string_value(item).strip()
            if text:
                items.append(text)
        return items
    return []


def _history_list(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    history: list[dict[str, Any]] = []
    for item in value:
        if isinstance(item, dict):
            history.append(dict(item))
    return history
