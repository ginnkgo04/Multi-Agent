from app.agents.base import AgentProfile, WorkflowAgent
from app.agents.langchain_agents import LangChainToolAgent
from app.models.schemas import Role


def make_agent(role: Role) -> WorkflowAgent:
    return WorkflowAgent(AgentProfile(role=role, system_prompt="", artifact_prefix="test"))


def test_extract_json_object_accepts_fenced_payload() -> None:
    agent = make_agent(Role.PC)

    payload = agent._parse_model_response(
        """```json
        {
          "requirement_brief": "Build a dashboard",
          "acceptance_criteria": {"must_have": ["list runs"]},
          "work_breakdown": ["define API"],
          "summary": "ok",
          "handoff_notes": "next",
          "confidence": 0.8
        }
        ```"""
    )

    assert payload["requirement_brief"] == "Build a dashboard"
    assert payload["acceptance_criteria"]["must_have"] == ["list runs"]


def test_normalize_relative_path_rejects_parent_segments() -> None:
    agent = make_agent(Role.FD)

    assert agent._normalize_relative_path("../bad.txt") == ""
    assert agent._normalize_relative_path("workspace//frontend\\app/page.tsx") == "workspace/frontend/app/page.tsx"


def test_build_user_prompt_uses_tagged_sections() -> None:
    agent = make_agent(Role.CA)
    context = type(
        "Context",
        (),
        {
            "role": Role.CA,
            "original_requirement": "Create a task board",
            "shared_plan": {"steps": ["api", "ui"]},
            "cycle_index": 1,
            "task_spec": {"focus": "architecture"},
            "upstream_artifacts": [],
            "retrieved_context": [],
            "memories": [],
            "template_context": {"stack": "next-fastapi"},
        },
    )()

    prompt = agent._build_user_prompt(context)

    assert "<REQUIREMENT>" in prompt
    assert "<SHARED_PLAN_JSON>" in prompt
    assert "<TEMPLATE_CONTEXT_JSON>" in prompt


def test_tool_agent_submit_payload_is_normalized_by_role() -> None:
    agent = LangChainToolAgent(Role.QT)

    normalized = agent.legacy._normalize_result_payload(
        {
            "status": "maybe",
            "defect_list": "missing validation",
            "retest_scope": "retry api flow",
        }
    )

    assert normalized["status"] == "FAIL"
    assert normalized["defect_list"] == ["missing validation"]
    assert normalized["retest_scope"] == ["retry api flow"]
