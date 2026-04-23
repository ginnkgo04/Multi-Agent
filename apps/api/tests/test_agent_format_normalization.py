import asyncio
import inspect
import json

import pytest

from app.agents.base import AgentProfile, WorkflowAgent
from app.agents.langchain_agents import LangChainLCELAgent, LangChainToolAgent
from app.models.schemas import AgentTaskContext, ProviderConfig, ProviderKind, Role, WorkspaceFileSnapshot


def make_agent(role: Role) -> WorkflowAgent:
    return WorkflowAgent(AgentProfile(role=role, system_prompt="", artifact_prefix="test"))


def make_context(
    role: Role,
    *,
    shared_plan: dict | None = None,
    template_context: dict | None = None,
    workspace_manifest: list[str] | None = None,
    workspace_snapshots: list[WorkspaceFileSnapshot] | None = None,
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
        workspace_manifest=workspace_manifest or [],
        workspace_snapshots=workspace_snapshots or [],
    )


def test_extract_json_object_accepts_fenced_payload() -> None:
    agent = make_agent(Role.PC)

    payload = agent._parse_model_response(
        """```json
        {
          "intent": {"scope": "fullstack", "app_type": "dashboard"},
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
    assert payload["intent"]["scope"] == "fullstack"
    assert payload["acceptance_criteria"]["must_have"] == ["list runs"]


@pytest.mark.parametrize("role", [Role.PC, Role.CA, Role.FD, Role.BD, Role.QT, Role.DE])
def test_all_roles_reject_upstream_transport_envelope_payload(role: Role) -> None:
    agent = make_agent(role)

    with pytest.raises(ValueError, match="transport envelope"):
        agent._normalize_result_payload(
            {
                "id": "",
                "object": "chat.completion.chunk",
                "created": "0",
                "model": "gpt-5.3-codex",
                "choices": [],
                "usage": {"completion_tokens": "0"},
            }
        )


@pytest.mark.parametrize("role", [Role.PC, Role.CA, Role.FD, Role.BD, Role.QT, Role.DE])
def test_all_roles_reject_payload_without_role_specific_fields(role: Role) -> None:
    agent = make_agent(role)

    with pytest.raises(ValueError, match="missing role-specific fields"):
        agent._normalize_result_payload({"foo": "bar"})


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


def test_fd_user_prompt_includes_workspace_manifest_and_edit_constraints() -> None:
    agent = make_agent(Role.FD)
    context = make_context(
        Role.FD,
        shared_plan={"remediation_plan": {"frontend": ["update hero copy"]}},
        template_context={"stack": "next-fastapi"},
        workspace_manifest=["workspace/frontend/app/page.tsx"],
        workspace_snapshots=[
            WorkspaceFileSnapshot(
                path="workspace/frontend/app/page.tsx",
                content="export default function Page() { return <main>Polar Bear</main>; }",
            )
        ],
    )

    prompt = agent._build_user_prompt(context)

    assert "<WORKSPACE_MANIFEST_JSON>" in prompt
    assert "<WORKSPACE_SNAPSHOTS_JSON>" in prompt
    assert "<EDIT_CONSTRAINTS>" in prompt
    assert "existing workspace files must use edit_operations" in prompt
    assert "do not overwrite an existing file with a full rewritten file body" in prompt.lower()


def test_fd_manifest_prompt_requires_edit_operations_for_existing_files() -> None:
    agent = make_agent(Role.FD)
    context = make_context(
        Role.FD,
        workspace_manifest=["workspace/frontend/app/page.tsx"],
        workspace_snapshots=[
            WorkspaceFileSnapshot(
                path="workspace/frontend/app/page.tsx",
                content="export default function Page() { return <main>Polar Bear</main>; }",
            )
        ],
    )

    prompt = agent._build_manifest_system_prompt(context)

    assert '"edit_operations"' in prompt
    assert "existing workspace files must be changed with edit operations" in prompt
    assert "Do not return a whole rewritten file body for an existing workspace file" in prompt


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
        workspace_manifest=["workspace/frontend/app/page.tsx"],
        workspace_snapshots=[
            WorkspaceFileSnapshot(
                path="workspace/frontend/app/page.tsx",
                content="export default function Page() { return <main>Polar Bear</main>; }",
            )
        ],
    )

    prompt = agent._system_prompt(context)

    assert "execution_contract" in prompt
    assert "template is only a fallback" in prompt
    assert "react-vite" in prompt
    assert "emit_edit_operation" in prompt
    assert "full rewritten file body" in prompt
    assert "list_workspace_files" in prompt
    assert "read_workspace_file" in prompt


def test_ca_system_prompt_requires_execution_contract_keys() -> None:
    prompt = LangChainLCELAgent(Role.CA)._system_prompt()

    assert "execution_contract.frontend.stack_id" in prompt
    assert "execution_contract.backend.required_paths" in prompt
    assert "approval_status" in prompt
    assert "allowed_paths" in prompt


def test_ca_system_prompt_includes_execution_contract_path_rules() -> None:
    prompt = LangChainLCELAgent(Role.CA)._system_prompt()

    assert "workspace/frontend/" in prompt
    assert "implementation/frontend/notes.md" in prompt
    assert "workspace/backend/" in prompt
    assert "implementation/backend/notes.md" in prompt
    assert "must include at least one path under workspace/frontend/" in prompt
    assert "must include at least one path under workspace/backend/" in prompt
    assert "remediation_plan" in prompt


def test_ca_system_prompt_requires_stack_agnostic_runnable_file_contract() -> None:
    prompt = LangChainLCELAgent(Role.CA)._system_prompt()

    assert "complete minimal runnable file set" in prompt
    assert "chosen stack" in prompt
    assert "install, build, and start" in prompt
    assert "Do not omit framework entrypoints" in prompt
    assert "Vite" not in prompt
    assert "Express" not in prompt


def test_pc_system_prompt_requires_requirement_fidelity_output() -> None:
    prompt = LangChainLCELAgent(Role.PC)._system_prompt()

    assert "requirement_fidelity" in prompt
    assert "semantic_coverage_score" in prompt
    assert "constraint_retention_score" in prompt
    assert "assumed_defaults" in prompt


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


def test_bd_manifest_prompt_falls_back_when_ca_execution_contract_uses_implementation_code_paths() -> None:
    agent = make_agent(Role.BD)
    context = make_context(
        Role.BD,
        shared_plan={
            "execution_contract": {
                "backend": {
                    "stack_id": "node-express",
                    "required_paths": [
                        "implementation/backend/src/server.js",
                        "implementation/backend/notes.md",
                    ],
                    "constraints": ["Use Express with lightweight persistence."],
                }
            }
        },
        template_context={"stack": "next-fastapi"},
    )

    prompt = agent._build_manifest_system_prompt(context)

    assert "workspace/backend/app/main.py" in prompt
    assert "fallback after invalid CA execution contract" in prompt
    assert "implementation/backend/src/server.js" in prompt
    assert "Use Express with lightweight persistence." not in prompt


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
            "owner_role": "",
            "location": "workspace/backend/app/routes.py",
            "suggestion": "add request validation",
            "expected_behavior": "",
            "actual_behavior": "",
            "fix_guidance": "",
            "requires_plan_update": False,
        }
    ]
    assert normalized["retest_scope"] == ["retry api flow"]


def test_legacy_fd_execute_extracts_edit_operations_from_model_response() -> None:
    agent = make_agent(Role.FD)
    context = make_context(
        Role.FD,
        template_context={"stack": "next-fastapi"},
        workspace_manifest=[
            "workspace/frontend/package.json",
            "workspace/frontend/app/page.tsx",
            "workspace/frontend/app/globals.css",
            "workspace/frontend/components/FeatureExperience.tsx",
            "workspace/frontend/lib/api.ts",
        ],
        workspace_snapshots=[
            WorkspaceFileSnapshot(
                path="workspace/frontend/app/page.tsx",
                content="export default function Page() { return <main>Polar Bear</main>; }\n",
            )
        ],
    )

    class FakeProvider:
        async def generate(self, **_: object) -> str:
            return json.dumps(
                {
                    "summary": "Updated the frontend in place.",
                    "confidence": 0.8,
                    "handoff_notes": "QT can validate the updated hero copy.",
                    "result_payload": {"implemented_features": ["hero copy refresh"]},
                    "edit_operations": [
                        {
                            "path": "workspace/frontend/app/page.tsx",
                            "operation": "update",
                            "strategy": "replace",
                            "summary": "Update the hero heading",
                            "old_text": "Polar Bear",
                            "new_text": "Arctic Fox",
                        }
                    ],
                    "artifacts": [
                        {
                            "path": "implementation/frontend/notes.md",
                            "artifact_type": "documentation",
                            "content_type": "text/markdown",
                            "summary": "Frontend implementation notes",
                        }
                    ],
                }
            )

    result = asyncio.run(agent.execute(context, FakeProvider()))

    assert result.edit_operations[0].path == "workspace/frontend/app/page.tsx"
    assert result.edit_operations[0].strategy == "replace"
    assert result.artifact_list[0]["name"] == "implementation/frontend/notes.md"


@pytest.mark.anyio
async def test_tool_agent_exposes_workspace_edit_tools_and_returns_edit_operations() -> None:
    agent = LangChainToolAgent(Role.FD)
    context = make_context(
        Role.FD,
        shared_plan={
            "execution_contract": {
                "frontend": {
                    "stack_id": "next-fastapi",
                    "required_paths": ["workspace/frontend/app/page.tsx"],
                    "constraints": ["Update the existing page incrementally."],
                }
            }
        },
        workspace_manifest=["workspace/frontend/app/page.tsx"],
        workspace_snapshots=[
            WorkspaceFileSnapshot(
                path="workspace/frontend/app/page.tsx",
                content="export default function Page(){return <main>Polar Bear</main>}",
            )
        ],
    )

    async def fake_run_tool_agent(chat_model, tools, context_arg) -> None:
        assert context_arg is context
        tool_map = {tool.name: tool for tool in tools}

        listing = await tool_map["list_workspace_files"].ainvoke({})
        assert "workspace/frontend/app/page.tsx" in listing

        snapshot = await tool_map["read_workspace_file"].ainvoke({"path": "workspace/frontend/app/page.tsx"})
        assert "Polar Bear" in snapshot

        await tool_map["emit_edit_operation"].ainvoke(
            {
                "path": "workspace/frontend/app/page.tsx",
                "operation": "update",
                "strategy": "replace",
                "summary": "Swap the featured animal",
                "content": "",
                "old_text": "Polar Bear",
                "new_text": "Arctic Fox",
                "anchors": [],
                "unified_diff": "",
            }
        )
        await tool_map["submit_result"].ainvoke(
            {
                "summary": "Frontend copy updated",
                "handoff_notes": "Ready for review",
                "result_payload": {
                    "implemented_features": ["updated hero copy"],
                    "frontend_routes": ["/"],
                    "integration_notes": ["Kept existing page structure"],
                },
                "confidence": 0.79,
            }
        )

    agent._run_tool_agent = fake_run_tool_agent  # type: ignore[method-assign]

    result = await agent.execute(
        context,
        chat_model=object(),
        fallback_provider=None,
        session=None,
        embedding_model=None,
        rag_service=object(),
    )

    assert result.summary == "Frontend copy updated"
    assert result.artifact_list == []
    assert len(result.edit_operations) == 1
    assert result.edit_operations[0].path == "workspace/frontend/app/page.tsx"
    assert result.edit_operations[0].new_text == "Arctic Fox"


def test_qt_payload_preserves_approval_and_owner_metadata() -> None:
    agent = LangChainToolAgent(Role.QT)

    normalized = agent.legacy._normalize_result_payload(
        {
            "status": "FAIL",
            "approval_recommended": True,
            "defect_list": [
                {
                    "id": "QT-009",
                    "description": "frontend and backend contract drift",
                    "severity": "high",
                    "owner_role": "CA",
                    "location": "architecture/interface_contracts.json",
                    "expected_behavior": "Shared contract matches implementation",
                    "actual_behavior": "Field names diverge",
                    "fix_guidance": "Regenerate the remediation plan before coding",
                    "requires_plan_update": True,
                }
            ],
        }
    )

    assert normalized["approval_recommended"] is True
    assert normalized["defect_list"][0]["owner_role"] == "CA"
    assert normalized["defect_list"][0]["requires_plan_update"] is True
    assert normalized["defect_list"][0]["expected_behavior"] == "Shared contract matches implementation"


def test_de_required_paths_focus_on_post_qt_delivery_bundle() -> None:
    agent = make_agent(Role.DE)
    context = make_context(Role.DE)

    required_paths = agent._required_paths_for_context(context)

    assert required_paths == [
        "delivery/delivery_manifest.json",
        "delivery/integration_report.md",
        "delivery/runbook.md",
        "delivery/architecture_guide.md",
        "delivery/checklist.md",
    ]


def test_pc_ca_qt_required_paths_match_vnext_contract() -> None:
    assert make_agent(Role.PC)._required_paths_for_context(make_context(Role.PC)) == [
        "requirements/intent_spec.json",
        "requirements/brief.md",
        "requirements/acceptance_criteria.json",
        "requirements/requirement_diff_report.json",
    ]
    assert make_agent(Role.CA)._required_paths_for_context(make_context(Role.CA)) == [
        "architecture/shared_plan.json",
        "architecture/execution_contract.json",
        "architecture/interface_contracts.json",
        "architecture/approval_packet.md",
    ]
    assert make_agent(Role.QT)._required_paths_for_context(make_context(Role.QT)) == [
        "quality/quality_gate.json",
        "quality/test_cases.json",
        "quality/defect_report.json",
        "quality/report.md",
    ]


def test_fd_artifact_validation_rejects_outputs_outside_allowed_roots() -> None:
    agent = make_agent(Role.FD)
    context = make_context(Role.FD)
    artifacts = [
        {
            "name": "workspace/frontend/package.json",
            "artifact_type": "source-code",
            "content_type": "application/json",
            "summary": "package",
            "content": "{}",
        },
        {
            "name": "workspace/frontend/app/page.tsx",
            "artifact_type": "source-code",
            "content_type": "text/x.typescript",
            "summary": "page",
            "content": "export default function Page(){return null}",
        },
        {
            "name": "workspace/frontend/app/globals.css",
            "artifact_type": "source-code",
            "content_type": "text/css",
            "summary": "css",
            "content": "body{}",
        },
        {
            "name": "workspace/frontend/components/FeatureExperience.tsx",
            "artifact_type": "source-code",
            "content_type": "text/x.typescript",
            "summary": "component",
            "content": "export function FeatureExperience(){return null}",
        },
        {
            "name": "workspace/frontend/lib/api.ts",
            "artifact_type": "source-code",
            "content_type": "text/x.typescript",
            "summary": "api",
            "content": "export const api = {}",
        },
        {
            "name": "implementation/frontend/notes.md",
            "artifact_type": "report",
            "content_type": "text/markdown",
            "summary": "notes",
            "content": "# Notes",
        },
        {
            "name": "delivery/runbook.md",
            "artifact_type": "delivery",
            "content_type": "text/markdown",
            "summary": "invalid extra output",
            "content": "# Should not be allowed",
        },
    ]

    with pytest.raises(ValueError, match="outside the allowed roots"):
        agent._validate_artifacts(context, artifacts)


def test_lcel_pc_and_ca_artifacts_follow_vnext_paths() -> None:
    pc_artifacts = LangChainLCELAgent(Role.PC)._build_artifacts(
        make_context(Role.PC),
        {
            "intent": {"scope": "frontend"},
            "requirement_brief": "Build a landing page",
            "acceptance_criteria": {"must_have": ["hero"]},
            "work_breakdown": ["brief"],
            "requirement_fidelity": {
                "semantic_coverage_score": 0.95,
                "constraint_retention_score": 0.96,
                "unmapped_items": [],
                "assumed_defaults": [],
                "clarification_needed": False,
            },
        },
    )
    ca_artifacts = LangChainLCELAgent(Role.CA)._build_artifacts(
        make_context(Role.CA),
        {
            "shared_plan": {"execution_contract": {}},
            "interfaces": [{"name": "createLead"}],
            "architecture_decisions": ["Use FastAPI"],
            "approval_status": "pending",
            "remediation_plan": {},
        },
    )

    assert {artifact["name"] for artifact in pc_artifacts} == {
        "requirements/intent_spec.json",
        "requirements/brief.md",
        "requirements/acceptance_criteria.json",
        "requirements/requirement_diff_report.json",
    }
    assert {artifact["name"] for artifact in ca_artifacts} == {
        "architecture/shared_plan.json",
        "architecture/execution_contract.json",
        "architecture/interface_contracts.json",
        "architecture/approval_packet.md",
    }


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
            "owner_role": "",
            "location": "workspace/frontend/app/page.tsx",
            "suggestion": "",
            "expected_behavior": "",
            "actual_behavior": "",
            "fix_guidance": "",
            "requires_plan_update": False,
        },
        {
            "id": "",
            "description": "missing contact form",
            "severity": "medium",
            "owner_role": "",
            "location": "",
            "suggestion": "",
            "expected_behavior": "",
            "actual_behavior": "",
            "fix_guidance": "",
            "requires_plan_update": False,
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
              "intent": {
                "scope": "frontend",
                "app_type": "landing_page",
                "confidence": 0.9,
                "needs_clarification": false,
                "key_entities": ["bear", "habitat"],
                "constraints": ["responsive"],
                "clarifying_questions": []
              },
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
    assert result.result_payload["intent"]["app_type"] == "landing_page"
    assert result.result_payload["requirement_brief"] == "Build a bear profile landing page"
    assert {artifact["name"] for artifact in result.artifact_list} >= {
        "requirements/intent_spec.json",
        "requirements/brief.md",
        "requirements/requirement_diff_report.json",
    }


@pytest.mark.anyio
async def test_lcel_agent_normalizes_list_handoff_notes_in_ca_payload() -> None:
    class FakeChatProvider:
        async def generate(self, *, system_prompt: str, user_prompt: str, metadata: dict) -> str:
            assert metadata["role"] == "CA"
            return """
            {
              "shared_plan": {
                "execution_contract": {
                  "frontend": {
                    "stack_id": "next-fastapi",
                    "required_paths": [
                      "workspace/frontend/app/page.tsx",
                      "implementation/frontend/notes.md"
                    ],
                    "allowed_paths": ["workspace/frontend/", "implementation/frontend/"],
                    "constraints": []
                  },
                  "backend": {
                    "stack_id": "next-fastapi",
                    "required_paths": [
                      "workspace/backend/app/main.py",
                      "implementation/backend/notes.md"
                    ],
                    "allowed_paths": ["workspace/backend/", "implementation/backend/"],
                    "constraints": []
                  }
                }
              },
              "interfaces": [{"name": "createLead"}],
              "architecture_decisions": ["Use template defaults"],
              "remediation_plan": {},
              "approval_status": "pending",
              "summary": "Architecture plan ready",
              "handoff_notes": ["Review the execution contract", "Proceed to implementation"],
              "confidence": 0.81
            }
            """

    result = await LangChainLCELAgent(Role.CA).execute(
        make_context(Role.CA),
        chat_model=FakeChatProvider(),
        session=None,
        embedding_model=None,
        rag_service=None,
    )

    assert result.summary == "Architecture plan ready"
    assert result.handoff_notes == "Review the execution contract; Proceed to implementation"
    assert {artifact["name"] for artifact in result.artifact_list} == {
        "architecture/shared_plan.json",
        "architecture/execution_contract.json",
        "architecture/interface_contracts.json",
        "architecture/approval_packet.md",
    }


@pytest.mark.anyio
async def test_lcel_agent_rejects_ca_execution_contract_with_implementation_code_paths_for_workspace_roles() -> None:
    class FakeChatProvider:
        async def generate(self, *, system_prompt: str, user_prompt: str, metadata: dict) -> str:
            assert metadata["role"] == "CA"
            return """
            {
              "shared_plan": {
                "execution_contract": {
                  "frontend": {
                    "stack_id": "react-vite-ts",
                    "required_paths": [
                      "implementation/frontend/src/main.tsx",
                      "implementation/frontend/notes.md"
                    ],
                    "allowed_paths": ["workspace/frontend/", "implementation/frontend/"],
                    "constraints": []
                  },
                  "backend": {
                    "stack_id": "nodejs-express-sqlite",
                    "required_paths": [
                      "implementation/backend/src/server.js",
                      "implementation/backend/notes.md"
                    ],
                    "allowed_paths": ["workspace/backend/", "implementation/backend/"],
                    "constraints": []
                  }
                }
              },
              "interfaces": [{"name": "GetLandingContent"}],
              "architecture_decisions": ["Use a lightweight fullstack landing page."],
              "remediation_plan": {},
              "approval_status": "pending",
              "summary": "Architecture plan ready",
              "handoff_notes": "Proceed to implementation.",
              "confidence": 0.81
            }
            """

    with pytest.raises(ValueError, match="implementation/frontend/src/main.tsx"):
        await LangChainLCELAgent(Role.CA).execute(
            make_context(Role.CA),
            chat_model=FakeChatProvider(),
            session=None,
            embedding_model=None,
            rag_service=None,
        )


@pytest.mark.anyio
async def test_lcel_agent_rejects_transport_envelope_for_ca() -> None:
    class FakeChatProvider:
        async def generate(self, *, system_prompt: str, user_prompt: str, metadata: dict) -> str:
            assert metadata["role"] == "CA"
            return """
            {
              "id": "",
              "object": "chat.completion.chunk",
              "created": "0",
              "model": "gpt-5.3-codex",
              "choices": [],
              "usage": {
                "prompt_tokens": "3880",
                "completion_tokens": "0"
              }
            }
            """

    with pytest.raises(ValueError, match="transport envelope"):
        await LangChainLCELAgent(Role.CA).execute(
            make_context(Role.CA),
            chat_model=FakeChatProvider(),
            session=None,
            embedding_model=None,
            rag_service=None,
        )


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


@pytest.mark.anyio
async def test_legacy_fallback_normalizes_frontend_notes_artifact_alias() -> None:
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
                    {"path": "workspace/frontend/src/main.tsx", "artifact_type": "source_code", "content_type": "text/x.typescript", "summary": "entrypoint"},
                    {"path": "workspace/frontend/src/App.tsx", "artifact_type": "source_code", "content_type": "text/x.typescript", "summary": "app shell"},
                    {"path": "implementation/frontend-implementation-notes.md", "artifact_type": "documentation", "content_type": "text/markdown", "summary": "implementation notes"}
                  ]
                }
                """
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

    assert {artifact["name"] for artifact in result.artifact_list} == {
        "workspace/frontend/package.json",
        "workspace/frontend/src/main.tsx",
        "workspace/frontend/src/App.tsx",
        "implementation/frontend/notes.md",
    }


@pytest.mark.anyio
async def test_legacy_fallback_promotes_frontend_notes_edit_alias_to_notes_artifact() -> None:
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
                  "artifacts": [],
                  "edit_operations": [
                    {
                      "path": "workspace/frontend/src/App.tsx",
                      "operation": "update",
                      "strategy": "replace",
                      "summary": "Update hero copy",
                      "old_text": "Polar Bear",
                      "new_text": "Sha County Snacks"
                    },
                    {
                      "path": "implementation/frontend-implementation-notes.md",
                      "operation": "update",
                      "strategy": "replace",
                      "summary": "Implementation notes",
                      "old_text": "",
                      "new_text": "# Frontend Notes\\n\\nUpdated the hero copy."
                    }
                  ]
                }
                """
            target = user_prompt.split("<CURRENT_TARGET_FILE>\n", 1)[1].split("\n</CURRENT_TARGET_FILE>", 1)[0].strip()
            assert target == "implementation/frontend/notes.md"
            return "# Frontend Notes\n\nUpdated the hero copy."

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
        workspace_manifest=[
            "workspace/frontend/package.json",
            "workspace/frontend/src/main.tsx",
            "workspace/frontend/src/App.tsx",
        ],
        workspace_snapshots=[
            WorkspaceFileSnapshot(
                path="workspace/frontend/src/App.tsx",
                content="export function App(){return <main>Polar Bear</main>}",
            )
        ],
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

    assert len(result.edit_operations) == 1
    assert result.edit_operations[0].path == "workspace/frontend/src/App.tsx"
    assert {artifact["name"] for artifact in result.artifact_list} == {"implementation/frontend/notes.md"}


@pytest.mark.anyio
async def test_legacy_fallback_synthesizes_frontend_notes_when_only_edit_operations_are_returned() -> None:
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
                  "artifacts": [],
                  "edit_operations": [
                    {
                      "path": "workspace/frontend/src/App.tsx",
                      "operation": "update",
                      "strategy": "replace",
                      "summary": "Update hero copy",
                      "old_text": "Polar Bear",
                      "new_text": "Sha County Snacks"
                    }
                  ]
                }
                """
            target = user_prompt.split("<CURRENT_TARGET_FILE>\n", 1)[1].split("\n</CURRENT_TARGET_FILE>", 1)[0].strip()
            assert target == "implementation/frontend/notes.md"
            return "# Frontend Notes\n\nUpdated the hero copy."

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
        workspace_manifest=[
            "workspace/frontend/package.json",
            "workspace/frontend/src/main.tsx",
            "workspace/frontend/src/App.tsx",
        ],
        workspace_snapshots=[
            WorkspaceFileSnapshot(
                path="workspace/frontend/src/App.tsx",
                content="export function App(){return <main>Polar Bear</main>}",
            )
        ],
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

    assert len(result.edit_operations) == 1
    assert result.edit_operations[0].path == "workspace/frontend/src/App.tsx"
    assert {artifact["name"] for artifact in result.artifact_list} == {"implementation/frontend/notes.md"}


@pytest.mark.anyio
async def test_manifest_then_files_recovers_backend_required_paths_when_manifest_has_no_artifacts() -> None:
    class FakeProvider:
        def __init__(self) -> None:
            self._manifest_calls = 0

        async def generate(self, *, system_prompt: str, user_prompt: str, metadata: dict) -> str:
            if "Do not include a content field in artifacts." in system_prompt:
                self._manifest_calls += 1
                return """
                {
                  "summary": "Backend manifest draft",
                  "confidence": 0.66,
                  "handoff_notes": "Continue with backend generation.",
                  "result_payload": {
                    "implemented_endpoints": ["/api/dishes", "/api/messages"],
                    "data_models": ["Message"],
                    "integration_notes": ["Use JSON file persistence."]
                  },
                  "artifacts": []
                }
                """

            target = user_prompt.split("<CURRENT_TARGET_FILE>\n", 1)[1].split("\n</CURRENT_TARGET_FILE>", 1)[0].strip()
            file_map = {
                "workspace/backend/src/server.js": "export const server = true;\n",
                "workspace/backend/src/routes/dishes.js": "export const dishesRoute = true;\n",
                "workspace/backend/src/routes/messages.js": "export const messagesRoute = true;\n",
                "workspace/backend/src/storage/messages.json": "[]\n",
                "implementation/backend/notes.md": "# Backend Notes\n",
            }
            return file_map[target]

    context = make_context(
        Role.BD,
        shared_plan={
            "execution_contract": {
                "backend": {
                    "stack_id": "nodejs-express-json-file",
                    "required_paths": [
                        "workspace/backend/src/server.js",
                        "workspace/backend/src/routes/dishes.js",
                        "workspace/backend/src/routes/messages.js",
                        "workspace/backend/src/storage/messages.json",
                        "implementation/backend/notes.md",
                    ],
                    "constraints": ["Use lightweight JSON persistence."],
                }
            }
        },
    )

    result = await make_agent(Role.BD).execute(context, FakeProvider())

    assert {artifact["name"] for artifact in result.artifact_list} == {
        "workspace/backend/src/server.js",
        "workspace/backend/src/routes/dishes.js",
        "workspace/backend/src/routes/messages.js",
        "workspace/backend/src/storage/messages.json",
        "implementation/backend/notes.md",
    }
    assert result.result_payload["implemented_endpoints"] == ["/api/dishes", "/api/messages"]


@pytest.mark.anyio
async def test_manifest_then_files_recovers_backend_required_paths_when_manifest_is_not_json() -> None:
    class FakeProvider:
        async def generate(self, *, system_prompt: str, user_prompt: str, metadata: dict) -> str:
            if "Do not include a content field in artifacts." in system_prompt:
                return "backend manifest draft without valid json"

            target = user_prompt.split("<CURRENT_TARGET_FILE>\n", 1)[1].split("\n</CURRENT_TARGET_FILE>", 1)[0].strip()
            file_map = {
                "workspace/backend/src/server.js": "export const server = true;\n",
                "workspace/backend/src/routes/dishes.js": "export const dishesRoute = true;\n",
                "workspace/backend/src/routes/messages.js": "export const messagesRoute = true;\n",
                "workspace/backend/src/storage/messages.json": "[]\n",
                "implementation/backend/notes.md": "# Backend Notes\n",
            }
            return file_map[target]

    context = make_context(
        Role.BD,
        shared_plan={
            "execution_contract": {
                "backend": {
                    "stack_id": "nodejs-express-json-file",
                    "required_paths": [
                        "workspace/backend/src/server.js",
                        "workspace/backend/src/routes/dishes.js",
                        "workspace/backend/src/routes/messages.js",
                        "workspace/backend/src/storage/messages.json",
                        "implementation/backend/notes.md",
                    ],
                    "constraints": ["Use lightweight JSON persistence."],
                }
            }
        },
    )

    result = await make_agent(Role.BD).execute(context, FakeProvider())

    assert {artifact["name"] for artifact in result.artifact_list} == {
        "workspace/backend/src/server.js",
        "workspace/backend/src/routes/dishes.js",
        "workspace/backend/src/routes/messages.js",
        "workspace/backend/src/storage/messages.json",
        "implementation/backend/notes.md",
    }
    assert result.result_payload["integration_notes"]
