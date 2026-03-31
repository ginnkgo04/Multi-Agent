import inspect

import pytest

from app.agents.base import AgentProfile, WorkflowAgent
from app.agents.langchain_agents import LangChainLCELAgent, LangChainToolAgent
from app.models.schemas import AgentTaskContext, ProviderConfig, ProviderKind, Role


def make_agent(role: Role) -> WorkflowAgent:
    return WorkflowAgent(AgentProfile(role=role, system_prompt="", artifact_prefix="test"))


def make_context(
    role: Role,
    *,
    shared_plan: dict | None = None,
    template_context: dict | None = None,
) -> AgentTaskContext:
    return AgentTaskContext(
        role=role,
        project_id="project-1",
        run_id="run-1",
        cycle_id="cycle-1",
        cycle_index=1,
        task_spec={},
        shared_plan=shared_plan or {},
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
        template_context=template_context or {},
    )


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


def test_fd_manifest_prompt_prefers_ca_execution_contract_over_template_defaults() -> None:
    agent = make_agent(Role.FD)
    context = make_context(
        Role.FD,
        shared_plan={
            "execution_contract": {
                "frontend": {
                    "stack_id": "react-vite",
                    "required_paths": [
                        "workspace/frontend/package.json",
                        "workspace/frontend/src/main.tsx",
                        "workspace/frontend/src/App.tsx",
                        "implementation/frontend/notes.md",
                    ],
                    "constraints": ["Use React with Vite entrypoints."],
                }
            }
        },
        template_context={"stack": "next-fastapi"},
    )

    prompt = agent._build_manifest_system_prompt(context)

    assert "workspace/frontend/src/main.tsx" in prompt
    assert "workspace/frontend/src/App.tsx" in prompt
    assert "workspace/frontend/app/page.tsx" not in prompt


def test_fd_manifest_prompt_falls_back_to_default_template_when_ca_contract_missing() -> None:
    agent = make_agent(Role.FD)
    context = make_context(Role.FD, template_context={"stack": "next-fastapi"})

    prompt = agent._build_manifest_system_prompt(context)

    assert "workspace/frontend/app/page.tsx" in prompt
    assert "workspace/frontend/components/FeatureExperience.tsx" in prompt


def test_fd_manifest_prompt_falls_back_when_ca_execution_contract_escapes_allowed_roots() -> None:
    agent = make_agent(Role.FD)
    context = make_context(
        Role.FD,
        shared_plan={
            "execution_contract": {
                "frontend": {
                    "stack_id": "react-vite",
                    "required_paths": ["workspace/backend/app/main.py"],
                    "constraints": [],
                }
            }
        },
        template_context={"stack": "next-fastapi"},
    )

    prompt = agent._build_manifest_system_prompt(context)

    assert "workspace/frontend/app/page.tsx" in prompt
    assert "fallback after invalid CA execution contract" in prompt
    assert "workspace/backend/app/main.py" in prompt


def test_tool_agent_system_prompt_mentions_execution_contract_priority() -> None:
    agent = LangChainToolAgent(Role.FD)
    context = make_context(
        Role.FD,
        shared_plan={
            "execution_contract": {
                "frontend": {
                    "stack_id": "react-vite",
                    "required_paths": [
                        "workspace/frontend/package.json",
                        "workspace/frontend/src/main.tsx",
                        "implementation/frontend/notes.md",
                    ],
                    "constraints": ["Prefer CA-defined stack."],
                }
            }
        },
    )

    prompt = agent._system_prompt(context)

    assert "execution_contract" in prompt
    assert "template is only a fallback" in prompt
    assert "react-vite" in prompt


def test_ca_system_prompt_requires_execution_contract_keys() -> None:
    prompt = LangChainLCELAgent(Role.CA)._system_prompt()

    assert "execution_contract.frontend.stack_id" in prompt
    assert "execution_contract.backend.required_paths" in prompt


def test_ca_system_prompt_includes_execution_contract_path_rules() -> None:
    prompt = LangChainLCELAgent(Role.CA)._system_prompt()

    assert "workspace/frontend/" in prompt
    assert "implementation/frontend/" in prompt
    assert "workspace/backend/" in prompt
    assert "implementation/backend/" in prompt


def test_fd_manifest_prompt_falls_back_to_template_when_ca_execution_contract_paths_are_invalid() -> None:
    agent = make_agent(Role.FD)
    context = make_context(
        Role.FD,
        shared_plan={
            "execution_contract": {
                "frontend": {
                    "stack_id": "static-html",
                    "required_paths": ["index.html", "styles.css"],
                    "constraints": ["Plain static website."],
                }
            }
        },
        template_context={"stack": "next-fastapi"},
    )

    prompt = agent._build_manifest_system_prompt(context)

    assert "workspace/frontend/app/page.tsx" in prompt
    assert "fallback after invalid CA execution contract" in prompt
    assert "Plain static website." not in prompt


def test_tool_agent_submit_payload_is_normalized_by_role() -> None:
    agent = LangChainToolAgent(Role.QT)

    normalized = agent.legacy._normalize_result_payload(
        {
            "status": "PASS",
            "defect_list": [
                {
                    "id": "QT-001",
                    "description": "missing validation",
                    "severity": "high",
                    "location": "workspace/backend/app/routes.py",
                    "suggestion": "add request validation",
                }
            ],
            "retest_scope": "retry api flow",
        }
    )

    assert normalized["status"] == "FAIL"
    assert normalized["defect_list"] == [
        {
            "id": "QT-001",
            "description": "missing validation",
            "severity": "high",
            "location": "workspace/backend/app/routes.py",
            "suggestion": "add request validation",
        }
    ]
    assert normalized["retest_scope"] == ["retry api flow"]


def test_tool_agent_submit_payload_normalizes_legacy_defect_strings() -> None:
    agent = LangChainToolAgent(Role.QT)

    normalized = agent.legacy._normalize_result_payload(
        {
            "status": "PASS",
            "defect_list": [
                "description: missing alt text | id: QT-002 | severity: minor | location: workspace/frontend/app/page.tsx",
                "missing contact form",
            ],
        }
    )

    assert normalized["status"] == "PASS"
    assert normalized["defect_list"] == [
        {
            "id": "QT-002",
            "description": "missing alt text",
            "severity": "low",
            "location": "workspace/frontend/app/page.tsx",
            "suggestion": "",
        },
        {
            "id": "",
            "description": "missing contact form",
            "severity": "medium",
            "location": "",
            "suggestion": "",
        },
    ]


def test_tool_agent_run_path_uses_langchain_v1_api_only() -> None:
    source = inspect.getsource(LangChainToolAgent._run_tool_agent)
    legacy_api_symbols = ("Agent" "Executor", "create_tool" "_calling_" "_agent")

    assert "create_agent" in source
    assert all(symbol not in source for symbol in legacy_api_symbols)


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
async def test_legacy_fallback_uses_ca_execution_contract_required_paths() -> None:
    class FakeFallbackProvider:
        async def generate(self, *, system_prompt: str, user_prompt: str, metadata: dict) -> str:
            if "Do not include a content field in artifacts." in system_prompt:
                assert "workspace/frontend/src/main.tsx" in system_prompt
                assert "workspace/frontend/app/page.tsx" not in system_prompt
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
                    {"path": "workspace/frontend/src/main.tsx", "artifact_type": "source_code", "content_type": "text/x.typescript", "summary": "entrypoint"},
                    {"path": "workspace/frontend/src/App.tsx", "artifact_type": "source_code", "content_type": "text/x.typescript", "summary": "app shell"},
                    {"path": "implementation/frontend/notes.md", "artifact_type": "documentation", "content_type": "text/markdown", "summary": "implementation notes"}
                  ]
                }
                """
            required_paths_json = user_prompt.split("<ALL_REQUIRED_PATHS_JSON>\n", 1)[1].split("\n</ALL_REQUIRED_PATHS_JSON>", 1)[0]
            assert "workspace/frontend/src/main.tsx" in required_paths_json
            assert "workspace/frontend/app/page.tsx" not in required_paths_json
            target = user_prompt.split("<CURRENT_TARGET_FILE>\n", 1)[1].split("\n</CURRENT_TARGET_FILE>", 1)[0].strip()
            file_map = {
                "workspace/frontend/package.json": '{"name":"polar-bear-site","private":true}',
                "workspace/frontend/src/main.tsx": "import { createRoot } from 'react-dom/client';",
                "workspace/frontend/src/App.tsx": "export function App(){return <main>Polar Bear</main>}",
                "implementation/frontend/notes.md": "# Frontend Notes",
            }
            return file_map[target]

    context = make_context(
        Role.FD,
        shared_plan={
            "execution_contract": {
                "frontend": {
                    "stack_id": "react-vite",
                    "required_paths": [
                        "workspace/frontend/package.json",
                        "workspace/frontend/src/main.tsx",
                        "workspace/frontend/src/App.tsx",
                        "implementation/frontend/notes.md",
                    ],
                    "constraints": ["Use React with Vite entrypoints."],
                }
            }
        },
        template_context={"stack": "next-fastapi"},
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

    assert len(result.artifact_list) == 4
    assert {artifact["name"] for artifact in result.artifact_list} == {
        "workspace/frontend/package.json",
        "workspace/frontend/src/main.tsx",
        "workspace/frontend/src/App.tsx",
        "implementation/frontend/notes.md",
    }


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
