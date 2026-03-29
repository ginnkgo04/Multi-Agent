import pytest

from app.agents.base import AgentProfile, WorkflowAgent
from app.agents.langchain_agents import LangChainLCELAgent, LangChainToolAgent
from app.models.schemas import AgentTaskContext, ProviderConfig, ProviderKind, Role


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


@pytest.mark.anyio
async def test_lcel_agent_accepts_plain_chat_provider_fallback() -> None:
    class FakeChatProvider:
        async def generate(self, *, system_prompt: str, user_prompt: str, metadata: dict) -> str:
            assert "Return ONLY one JSON object" in system_prompt
            assert "<REQUIREMENT>" in user_prompt
            assert metadata["role"] == "PC"
            return """
            {
              "requirement_brief": "Build a bear profile landing page",
              "acceptance_criteria": {
                "must_have": ["hero section", "habitat facts"]
              },
              "work_breakdown": ["draft content", "design layout"],
              "summary": "Requirement analysis complete",
              "handoff_notes": "Proceed with UI-first architecture",
              "confidence": 0.86
            }
            """

    context = AgentTaskContext(
        role=Role.PC,
        project_id="project-1",
        run_id="run-1",
        cycle_id="cycle-1",
        cycle_index=1,
        task_spec={},
        shared_plan={},
        provider_config=ProviderConfig(
            id="provider-1",
            name="deepseek",
            kind=ProviderKind.CHAT,
            provider="openai-compatible",
            model="deepseek-chat",
            base_url="https://api.deepseek.com/v1",
            api_key=None,
            is_default=True,
            settings={},
        ),
        original_requirement="生成一个小熊的介绍网页",
    )

    result = await LangChainLCELAgent(Role.PC).execute(
        context,
        chat_model=FakeChatProvider(),
        session=None,
        embedding_model=None,
        rag_service=None,
    )

    assert result.summary == "Requirement analysis complete"
    assert result.result_payload["requirement_brief"] == "Build a bear profile landing page"
    assert result.artifact_list[0]["name"] == "requirements/brief.md"


@pytest.mark.anyio
async def test_tool_agent_falls_back_to_legacy_provider_when_submit_missing() -> None:
    class FakeFallbackProvider:
        async def generate(self, *, system_prompt: str, user_prompt: str, metadata: dict) -> str:
            if "Do not include a content field in artifacts." in system_prompt:
                return """
                {
                  "summary": "Frontend implementation ready",
                  "confidence": 0.84,
                  "handoff_notes": "Frontend ready for integration.",
                  "result_payload": {
                    "implemented_features": ["landing page", "responsive layout"],
                    "frontend_routes": ["/"],
                    "integration_notes": ["Consumes static content only"]
                  },
                  "artifacts": [
                    {"path": "workspace/frontend/package.json", "artifact_type": "configuration", "content_type": "application/json", "summary": "package manifest"},
                    {"path": "workspace/frontend/app/page.tsx", "artifact_type": "source_code", "content_type": "text/x.typescript", "summary": "home page"},
                    {"path": "workspace/frontend/app/globals.css", "artifact_type": "stylesheet", "content_type": "text/css", "summary": "global styles"},
                    {"path": "workspace/frontend/components/FeatureExperience.tsx", "artifact_type": "source_code", "content_type": "text/x.typescript", "summary": "feature component"},
                    {"path": "workspace/frontend/lib/api.ts", "artifact_type": "source_code", "content_type": "text/x.typescript", "summary": "api helper"},
                    {"path": "implementation/frontend/notes.md", "artifact_type": "documentation", "content_type": "text/markdown", "summary": "implementation notes"}
                  ]
                }
                """
            target = user_prompt.split("<CURRENT_TARGET_FILE>\n", 1)[1].split("\n</CURRENT_TARGET_FILE>", 1)[0].strip()
            file_map = {
                "workspace/frontend/package.json": '{"name":"polar-bear-site","private":true}',
                "workspace/frontend/app/page.tsx": "export default function Page(){return <main>Polar Bear</main>}",
                "workspace/frontend/app/globals.css": "body { margin: 0; }",
                "workspace/frontend/components/FeatureExperience.tsx": "export function FeatureExperience(){return <section>Facts</section>}",
                "workspace/frontend/lib/api.ts": "export const getApiBase = () => '/api';",
                "implementation/frontend/notes.md": "# Frontend Notes",
            }
            return file_map[target]

    context = AgentTaskContext(
        role=Role.FD,
        project_id="project-1",
        run_id="run-1",
        cycle_id="cycle-1",
        cycle_index=1,
        task_spec={},
        shared_plan={"steps": ["design", "implement"]},
        provider_config=ProviderConfig(
            id="provider-1",
            name="deepseek",
            kind=ProviderKind.CHAT,
            provider="openai-compatible",
            model="deepseek-chat",
            base_url="https://api.deepseek.com/v1",
            api_key=None,
            is_default=True,
            settings={},
        ),
        original_requirement="生成一个北极熊介绍网页",
    )
    agent = LangChainToolAgent(Role.FD)

    async def no_submit(*args, **kwargs) -> None:
        return None

    agent._run_tool_agent = no_submit  # type: ignore[method-assign]
    result = await agent.execute(
        context,
        chat_model=object(),
        fallback_provider=FakeFallbackProvider(),
        session=None,
        embedding_model=None,
        rag_service=None,
    )

    assert result.summary == "Frontend implementation ready"
    assert result.result_payload["frontend_routes"] == ["/"]
    assert len(result.artifact_list) == 6
    assert any(artifact["name"] == "workspace/frontend/app/page.tsx" for artifact in result.artifact_list)
