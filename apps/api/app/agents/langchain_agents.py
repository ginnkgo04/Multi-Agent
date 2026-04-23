from __future__ import annotations

import asyncio
import json
from textwrap import dedent
from typing import Any, Awaitable, Callable

from sqlalchemy.orm import Session

from app.agents.base import AgentProfile, ROLE_SPECS, WorkflowAgent
from app.agents.runtime_types import ExecutionBuffer
from app.config import get_settings
from app.models.schemas import (
    AgentTaskContext,
    AgentTaskResult,
    EditOperation,
    Role,
)
from app.services.workflow_graph_builder import role_dependencies_for_cycle

ToolLogger = Callable[[str, str, dict[str, Any] | None], Awaitable[None]]


def _legacy_agent(role: Role) -> WorkflowAgent:
    return WorkflowAgent(AgentProfile(role=role, system_prompt="", artifact_prefix=f"{role.value.lower()}-langchain"))


def _json_blob(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2)

class LangChainLCELAgent:
    def __init__(self, role: Role) -> None:
        self.role = role
        self.legacy = _legacy_agent(role)

    async def execute(
        self,
        context: AgentTaskContext,
        *,
        chat_model,
        fallback_provider=None,
        session: Session,
        embedding_model,
        rag_service,
        tool_logger: ToolLogger | None = None,
    ) -> AgentTaskResult:
        del fallback_provider, session, embedding_model, rag_service, tool_logger
        raw_text = await self._invoke_model(context, chat_model)
        payload = self.legacy._parse_model_response(str(raw_text))
        summary = self.legacy._normalize_prompt_text(
            payload.get("summary") or f"{self.role.value} produced structured planning output.",
            limit=400,
        )
        handoff_notes = self.legacy._normalize_prompt_text(
            payload.get("handoff_notes")
            or f"Proceed to the next role after reviewing the {self.role.value} outputs.",
            limit=800,
        )
        confidence = float(payload.get("confidence", 0.72))
        result_payload = self.legacy._normalize_result_payload(payload)
        artifacts = self._build_artifacts(context, result_payload)
        self.legacy._validate_artifacts(context, artifacts)
        return AgentTaskResult(
            summary=summary,
            artifact_list=artifacts,
            result_payload=result_payload,
            confidence=confidence,
            handoff_notes=handoff_notes,
        )

    async def _invoke_model(self, context: AgentTaskContext, chat_model) -> Any:
        prompt_text = self._human_prompt(context)
        if hasattr(chat_model, "generate"):
            return await chat_model.generate(
                system_prompt=self._system_prompt(),
                user_prompt=prompt_text,
                metadata={
                    "role": self.role.value,
                    "cycle_index": context.cycle_index,
                    "requirement": context.original_requirement,
                    "temperature": 0.1,
                    "max_tokens": 3500,
                    "timeout": 180,
                    "response_format": {"type": "json_object"},
                },
            )

        try:
            from langchain_core.prompts import ChatPromptTemplate
            from langchain_core.runnables import RunnableLambda
        except ImportError as exc:  # pragma: no cover - depends on optional packages
            raise RuntimeError("LangChain core is not installed. Install langchain/langchain-core to run LCEL agents.") from exc

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", self._system_prompt()),
                ("human", "{context_block}"),
            ]
        )
        chain = (
            RunnableLambda(
                lambda _: {
                    "context_block": prompt_text,
                }
            )
            | prompt
            | chat_model
        )
        response = await chain.ainvoke({})
        return getattr(response, "content", response)

    def _system_prompt(self) -> str:
        spec = ROLE_SPECS[self.role]
        if self.role is Role.PC:
            return dedent(
                f"""
                You are the {spec['title']} in a LangChain-driven multi-agent delivery workflow.
                Produce structured intent analysis and requirement normalization only.
                Return ONLY one JSON object. Do not use markdown fences and do not add commentary.
                Required keys:
                - intent: object with
                  - scope: frontend | backend | fullstack
                  - app_type: short web-application category such as landing_page, dashboard, admin, forum, ecommerce, tool
                  - confidence: float between 0 and 1
                  - needs_clarification: boolean
                  - clarifying_questions: array of unresolved questions
                  - key_entities: array of important domain entities or features
                  - constraints: array of important delivery constraints
                - requirement_brief: concise but implementation-ready summary
                - acceptance_criteria: object with must_have, should_have, could_have arrays
                - work_breakdown: ordered array of execution tasks
                - requirement_fidelity: object with
                  - semantic_coverage_score: float between 0 and 1
                  - constraint_retention_score: float between 0 and 1
                  - unmapped_items: array of requirement details not yet grounded
                  - assumed_defaults: array of defaults inferred by PC
                  - clarification_needed: boolean
                - summary: short stage summary
                - handoff_notes: concise next-step notes
                - confidence: float between 0 and 1
                """
            ).strip()
        return dedent(
            f"""
            You are the {spec['title']} in a LangChain-driven multi-agent delivery workflow.
            Produce structured architecture output only.
            Return ONLY one JSON object. Do not use markdown fences and do not add commentary.
            Required keys:
            - shared_plan: structured implementation plan object
              - shared_plan.execution_contract.frontend.stack_id
              - shared_plan.execution_contract.frontend.required_paths
              - shared_plan.execution_contract.frontend.allowed_paths
              - shared_plan.execution_contract.frontend.constraints
              - shared_plan.execution_contract.backend.stack_id
              - shared_plan.execution_contract.backend.required_paths
              - shared_plan.execution_contract.backend.allowed_paths
              - shared_plan.execution_contract.backend.constraints
            - interfaces: array of contracts or APIs
            - architecture_decisions: array of key technical decisions
            - remediation_plan: object describing incremental fixes when CA is responding to QT failures
            - approval_status: pending | approved | rejected | not_required
            - summary: short stage summary
            - handoff_notes: concise next-step notes
            - confidence: float between 0 and 1
            Execution contract path rules:
            - shared_plan.execution_contract.frontend.required_paths must include at least one path under workspace/frontend/
            - shared_plan.execution_contract.backend.required_paths must include at least one path under workspace/backend/
            - implementation/frontend/notes.md is the only allowed implementation/ path in shared_plan.execution_contract.frontend.required_paths
            - implementation/backend/notes.md is the only allowed implementation/ path in shared_plan.execution_contract.backend.required_paths
            - Never emit repo-root paths like index.html, styles.css, app.py, or README.md in execution_contract.required_paths
            - required_paths must be the complete minimal runnable file set for the chosen stack, not only business source files
            - Include package or dependency manifests, configuration, bootstrap, routing, entry, and service files needed to install, build, and start locally
            - Do not omit framework entrypoints or runtime configuration files because they look like boilerplate
            - Put install/build/start commands and port assumptions in constraints when they are known
            """
        ).strip()

    def _human_prompt(self, context: AgentTaskContext) -> str:
        return self.legacy._build_user_prompt(context) + "\n\nReturn one valid JSON object only."

    def _build_artifacts(self, context: AgentTaskContext, payload: dict[str, Any]) -> list[dict[str, Any]]:
        if self.role is Role.PC:
            intent = payload.get("intent", {})
            acceptance = payload.get("acceptance_criteria", {})
            return [
                self._artifact(
                    context,
                    path="requirements/intent_spec.json",
                    summary="Intent specification",
                    content=_json_blob(intent),
                    content_type="application/json",
                ),
                self._artifact(
                    context,
                    path="requirements/brief.md",
                    summary="Requirement brief",
                    content=self._pc_brief_content(payload),
                ),
                self._artifact(
                    context,
                    path="requirements/acceptance_criteria.json",
                    summary="Acceptance criteria",
                    content=_json_blob(acceptance),
                    content_type="application/json",
                ),
                self._artifact(
                    context,
                    path="requirements/requirement_diff_report.json",
                    summary="Requirement fidelity and diff report",
                    content=_json_blob(payload.get("requirement_fidelity", {})),
                    content_type="application/json",
                ),
            ]

        shared_plan = payload.get("shared_plan", {})
        execution_contract = shared_plan.get("execution_contract", {}) if isinstance(shared_plan, dict) else {}
        return [
            self._artifact(
                context,
                path="architecture/shared_plan.json",
                summary="Shared implementation plan",
                content=_json_blob(shared_plan),
                content_type="application/json",
            ),
            self._artifact(
                context,
                path="architecture/execution_contract.json",
                summary="Execution contract",
                content=_json_blob(execution_contract),
                content_type="application/json",
            ),
            self._artifact(
                context,
                path="architecture/interface_contracts.json",
                summary="Interfaces and contracts",
                content=_json_blob(payload.get("interfaces", [])),
                content_type="application/json",
            ),
            self._artifact(
                context,
                path="architecture/approval_packet.md",
                summary="Approval packet",
                content=self._ca_approval_packet_content(context, payload),
            ),
        ]

    def _pc_brief_content(self, payload: dict[str, Any]) -> str:
        brief = payload.get("requirement_brief", "").strip()
        intent = payload.get("intent", {}) if isinstance(payload.get("intent", {}), dict) else {}
        lines = ["# Requirement Brief", ""]
        if brief:
            lines.extend([brief, ""])
        if intent:
            lines.extend(
                [
                    "## Intent",
                    "",
                    f"- Scope: {intent.get('scope', '') or 'unspecified'}",
                    f"- App type: {intent.get('app_type', '') or 'unspecified'}",
                    f"- Confidence: {intent.get('confidence', 0.0)}",
                    f"- Needs clarification: {'yes' if intent.get('needs_clarification') else 'no'}",
                ]
            )
        return "\n".join(lines).rstrip() + "\n"

    def _ca_approval_packet_content(self, context: AgentTaskContext, payload: dict[str, Any]) -> str:
        approval_status = str(payload.get("approval_status", "pending")).strip() or "pending"
        decisions = payload.get("architecture_decisions", [])
        remediation_plan = payload.get("remediation_plan", {})
        task_graph = {
            "cycle_index": context.cycle_index,
            "roles": [role.value for role in role_dependencies_for_cycle(context.cycle_index).keys()],
            "dependencies": {
                role.value: [dependency.value for dependency in dependencies]
                for role, dependencies in role_dependencies_for_cycle(context.cycle_index).items()
            },
        }
        lines = [
            "# Approval Packet",
            "",
            f"- Approval status: {approval_status}",
            f"- Cycle index: {context.cycle_index}",
            "",
            "## Architecture Decisions",
        ]
        if decisions:
            lines.extend(f"- {item}" for item in decisions)
        else:
            lines.append("- none")
        lines.extend([
            "",
            "## Remediation Plan",
            _json_blob(remediation_plan),
            "",
            "## Task Graph",
            _json_blob(task_graph),
        ])
        return "\n".join(lines).rstrip() + "\n"

    def _artifact(
        self,
        context: AgentTaskContext,
        *,
        path: str,
        summary: str,
        content: str,
        content_type: str | None = None,
    ) -> dict[str, Any]:
        return {
            "name": path,
            "artifact_type": self.legacy._default_artifact_type(path),
            "content_type": content_type or self.legacy._default_content_type(path),
            "summary": summary,
            "content": content,
            "metadata": {
                "role": self.role.value,
                "cycle": context.cycle_index,
                "generated_by": "langchain-lcel",
            },
        }


class LangChainToolAgent:
    def __init__(self, role: Role) -> None:
        self.role = role
        self.legacy = _legacy_agent(role)
        self.settings = get_settings()

    async def execute(
        self,
        context: AgentTaskContext,
        *,
        chat_model,
        fallback_provider=None,
        session: Session,
        embedding_model,
        rag_service,
        tool_logger: ToolLogger | None = None,
    ) -> AgentTaskResult:
        try:
            from langchain_core.tools import tool
        except ImportError as exc:  # pragma: no cover - depends on optional packages
            raise RuntimeError(f"LangChain tool dependencies are unavailable: {exc}") from exc

        buffer = ExecutionBuffer()

        async def log_tool(tool_name: str, status: str, payload: dict[str, Any] | None = None) -> None:
            entry = {"tool_name": tool_name, "status": status, "payload": payload or {}}
            buffer.tool_trace.append(entry)
            if tool_logger is not None:
                await tool_logger(tool_name, status, payload)

        @tool
        async def get_requirement() -> str:
            """Return the original user requirement for the current run."""
            await log_tool("get_requirement", "ok")
            return context.original_requirement

        @tool
        async def get_shared_plan() -> str:
            """Return the current shared plan as JSON text."""
            shared_plan_id, plan = rag_service.get_shared_plan(session, context.run_id)
            await log_tool("get_shared_plan", "ok", {"shared_plan_id": shared_plan_id or context.shared_plan_id})
            return _json_blob(plan or context.shared_plan)

        @tool
        async def list_upstream_artifacts() -> str:
            """Return upstream artifact summaries and previews for the current node."""
            previews = []
            for artifact in context.upstream_artifacts:
                previews.append(
                    {
                        "name": artifact.name,
                        "summary": artifact.summary,
                        "preview": artifact.metadata.get("content_preview", "")[:400],
                    }
                )
            await log_tool("list_upstream_artifacts", "ok", {"count": len(previews)})
            return _json_blob(previews)

        @tool
        async def retrieve_context(query: str, top_k: int = 4, source_types: list[str] | None = None) -> str:
            """Retrieve extra project context using the platform RAG service."""
            items = await rag_service.retrieve(
                session,
                context.project_id,
                query,
                embedding_model,
                run_id=context.run_id,
                top_k=top_k,
                source_types=source_types,
            )
            await log_tool(
                "retrieve_context",
                "ok",
                {"query": query, "count": len(items), "top_k": top_k, "source_types": source_types or []},
            )
            return _json_blob(items)

        @tool
        async def get_context_sources() -> str:
            """Return the ordered context sources already assembled for the current node."""
            items = [source.model_dump(mode="json") for source in context.context_sources]
            await log_tool("get_context_sources", "ok", {"count": len(items)})
            return _json_blob(items)

        @tool
        async def list_workspace_files() -> str:
            """Return the current run workspace manifest for the active role."""
            await log_tool("list_workspace_files", "ok", {"count": len(context.workspace_manifest)})
            return _json_blob(context.workspace_manifest)

        @tool
        async def read_workspace_file(path: str) -> str:
            """Return the current contents of one workspace file from the assembled baseline."""
            normalized_path = self.legacy._normalize_relative_path(path)
            snapshot = next((item for item in context.workspace_snapshots if item.path == normalized_path), None)
            if snapshot is None:
                raise ValueError(f"Workspace file not available in context: {path}")
            await log_tool("read_workspace_file", "ok", {"path": normalized_path, "size_bytes": snapshot.size_bytes})
            return snapshot.content

        @tool
        async def emit_edit_operation(
            path: str,
            operation: str,
            strategy: str,
            summary: str,
            content: str = "",
            old_text: str = "",
            new_text: str = "",
            anchors: list[str] | None = None,
            unified_diff: str = "",
        ) -> str:
            """Buffer one workspace edit operation for the current role."""
            edit_operation = self.legacy._normalize_edit_operation(
                EditOperation(
                    path=path,
                    operation=operation,
                    strategy=strategy,
                    summary=summary,
                    content=content,
                    old_text=old_text,
                    new_text=new_text,
                    anchors=anchors or [],
                    unified_diff=unified_diff,
                )
            )
            buffer.emit_edit_operation(edit_operation)
            await log_tool(
                "emit_edit_operation",
                "ok",
                {
                    "path": edit_operation.path,
                    "operation": edit_operation.operation,
                    "strategy": edit_operation.strategy,
                },
            )
            return f"Buffered edit operation for {edit_operation.path}"

        @tool
        async def emit_artifact(path: str, artifact_type: str, content_type: str, summary: str, content: str) -> str:
            """Buffer an artifact that belongs to the current role."""
            normalized_path = self.legacy._normalize_relative_path(path)
            if not normalized_path:
                raise ValueError("emit_artifact received an invalid relative path.")
            buffer.emit_artifact(
                path=normalized_path,
                artifact_type=artifact_type,
                content_type=content_type,
                summary=summary,
                content=content,
                metadata={
                    "role": self.role.value,
                    "cycle": context.cycle_index,
                    "generated_by": "langchain-tool-agent",
                },
            )
            await log_tool("emit_artifact", "ok", {"path": normalized_path, "artifact_type": artifact_type})
            return f"Buffered artifact {normalized_path}"

        @tool(return_direct=True)
        async def submit_result(summary: str, handoff_notes: str, result_payload: dict[str, Any], confidence: float = 0.72) -> str:
            """Finalize the current role after all artifacts have been emitted."""
            normalized_payload = self.legacy._normalize_result_payload(result_payload)
            normalized_summary = self.legacy._normalize_prompt_text(summary, limit=400)
            normalized_handoff = self.legacy._normalize_prompt_text(handoff_notes, limit=800)
            normalized_confidence = max(0.0, min(1.0, float(confidence)))
            buffer.submit(
                summary=normalized_summary,
                handoff_notes=normalized_handoff,
                result_payload=normalized_payload,
                confidence=normalized_confidence,
            )
            await log_tool(
                "submit_result",
                "ok",
                {"artifact_count": len(buffer.artifacts), "edit_operation_count": len(buffer.edit_operations)},
            )
            return "Result submitted"

        tools = [
            get_requirement,
            get_shared_plan,
            list_upstream_artifacts,
            retrieve_context,
            get_context_sources,
            list_workspace_files,
            read_workspace_file,
            emit_edit_operation,
            emit_artifact,
            submit_result,
        ]
        try:
            await self._run_tool_agent(chat_model, tools, context)

            if not buffer.submitted:
                raise ValueError(f"{self.role.value} must call submit_result before finishing.")

            edit_operations = [self.legacy._normalize_edit_operation(item) for item in buffer.edit_operations]
            self.legacy._validate_artifacts(context, buffer.artifacts, edit_operations=edit_operations)
            result_payload = self.legacy._normalize_result_payload(buffer.result_payload)
            return AgentTaskResult(
                summary=buffer.summary,
                artifact_list=buffer.artifacts,
                edit_operations=edit_operations,
                result_payload=result_payload,
                confidence=buffer.confidence,
                handoff_notes=buffer.handoff_notes,
            )
        except Exception as exc:
            if fallback_provider is None:
                raise
            await log_tool(
                "legacy_fallback",
                "ok",
                {
                    "reason": str(exc),
                    "buffered_artifact_count": len(buffer.artifacts),
                    "submitted": buffer.submitted,
                },
            )
            return await self.legacy.execute(context, fallback_provider)

    async def _run_tool_agent(self, chat_model, tools: list[Any], context: AgentTaskContext) -> None:
        prompt_text = self._human_prompt(context)
        system_prompt = self._system_prompt(context)
        try:
            from langchain.agents import create_agent
        except ImportError as exc:  # pragma: no cover - depends on optional packages
            raise RuntimeError(
                "LangChain v1 agent API is unavailable in the current runtime. "
                f"Import failed: {exc}."
            ) from exc

        agent = create_agent(
            model=chat_model,
            tools=tools,
            system_prompt=system_prompt,
            name=f"{self.role.value.lower()}-tool-agent",
        )
        await asyncio.wait_for(
            agent.ainvoke({"messages": [{"role": "user", "content": prompt_text}]}),
            timeout=self.settings.multi_agent_task_timeout_seconds,
        )

    def _system_prompt(self, context: AgentTaskContext) -> str:
        spec = ROLE_SPECS[self.role]
        required_paths = "\n".join(f"- {path}" for path in self.legacy._required_paths_for_context(context))
        dynamic_note = ""
        if context.template_context:
            dynamic_note = f"\nTemplate context is available in the prompt and may be used when relevant.\n"
        prompt = dedent(
            f"""
            You are the {spec['title']} in a LangGraph + LangChain multi-agent delivery workflow.
            Use tools to inspect the requirement, shared plan, upstream artifacts, and optional retrieved context.
            You must emit concrete artifacts and finish with submit_result.

            Rules:
            - Always use emit_artifact for every output file.
            - When modifying workspace code for FD or BD, use emit_edit_operation for create, update, and delete actions under workspace/*.
            - Use list_workspace_files and read_workspace_file before editing existing workspace files.
            - Always call submit_result exactly once after artifact emission is complete.
            - Produce real implementation content, not pseudo-code.
            - Keep all tool arguments plain strings or JSON-compatible objects.
            - Artifact paths must be relative, use forward slashes, and must not contain '..'.
            - Required minimum artifact paths:
            {required_paths}
            - {spec['payload_contract']}
            {dynamic_note}
            """
        ).strip()
        execution_guidance = self.legacy._execution_guidance_block(context)
        if execution_guidance:
            prompt = f"{prompt}\n{execution_guidance}"
        if self.role in {Role.FD, Role.BD}:
            prompt = (
                f"{prompt}\n"
                "Workspace edit guardrails:\n"
                "- Use emit_edit_operation for workspace changes and emit_artifact for implementation notes.\n"
                "- Prefer replace, insert_before, insert_after, or patch for existing files.\n"
                "- Delete obsolete files explicitly.\n"
                "- Do not overwrite an existing workspace file with a full rewritten file body.\n"
            )
        return prompt

    def _human_prompt(self, context: AgentTaskContext) -> str:
        return self.legacy._build_user_prompt(context)
