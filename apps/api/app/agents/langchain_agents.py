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
    Role,
)
from app.services.workflow_graph_builder import role_dependencies_for_cycle

ToolLogger = Callable[[str, str, dict[str, Any] | None], Awaitable[None]]


def _legacy_agent(role: Role) -> WorkflowAgent:
    return WorkflowAgent(AgentProfile(role=role, system_prompt="", artifact_prefix=f"{role.value.lower()}-langchain"))


def _json_blob(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2)


def _assert_required_paths(role: Role, artifacts: list[dict[str, Any]]) -> None:
    names = {artifact["name"] for artifact in artifacts}
    missing = [path for path in ROLE_SPECS[role]["required_paths"] if path not in names]
    if missing:
        raise ValueError(f"{role.value} is missing required artifact paths: {', '.join(missing)}")


class LangChainLCELAgent:
    def __init__(self, role: Role) -> None:
        self.role = role
        self.legacy = _legacy_agent(role)

    async def execute(
        self,
        context: AgentTaskContext,
        *,
        chat_model,
        session: Session,
        embedding_model,
        rag_service,
        tool_logger: ToolLogger | None = None,
    ) -> AgentTaskResult:
        del session, embedding_model, rag_service, tool_logger
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
                    "context_block": self._human_prompt(context),
                }
            )
            | prompt
            | chat_model
        )
        response = await chain.ainvoke({})
        raw_text = getattr(response, "content", response)
        payload = self.legacy._parse_model_response(str(raw_text))
        summary = payload.get("summary") or f"{self.role.value} produced structured planning output."
        handoff_notes = payload.get("handoff_notes") or f"Proceed to the next role after reviewing the {self.role.value} outputs."
        confidence = float(payload.get("confidence", 0.72))
        result_payload = self.legacy._normalize_result_payload(payload)
        artifacts = self._build_artifacts(context, result_payload)
        self.legacy._validate_artifacts(artifacts)
        _assert_required_paths(self.role, artifacts)
        return AgentTaskResult(
            summary=summary,
            artifact_list=artifacts,
            result_payload=result_payload,
            confidence=confidence,
            handoff_notes=handoff_notes,
        )

    def _system_prompt(self) -> str:
        spec = ROLE_SPECS[self.role]
        if self.role is Role.PC:
            return dedent(
                f"""
                You are the {spec['title']} in a LangChain-driven multi-agent delivery workflow.
                Produce structured requirement analysis only.
                Return ONLY one JSON object. Do not use markdown fences and do not add commentary.
                Required keys:
                - requirement_brief: concise but implementation-ready summary
                - acceptance_criteria: object with must_have, should_have, could_have arrays
                - work_breakdown: ordered array of execution tasks
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
            - interfaces: array of contracts or APIs
            - architecture_decisions: array of key technical decisions
            - summary: short stage summary
            - handoff_notes: concise next-step notes
            - confidence: float between 0 and 1
            """
        ).strip()

    def _human_prompt(self, context: AgentTaskContext) -> str:
        return self.legacy._build_user_prompt(context) + "\n\nReturn one valid JSON object only."

    def _build_artifacts(self, context: AgentTaskContext, payload: dict[str, Any]) -> list[dict[str, Any]]:
        if self.role is Role.PC:
            acceptance = payload.get("acceptance_criteria", {})
            work_breakdown = payload.get("work_breakdown", [])
            return [
                self._artifact(
                    context,
                    path="requirements/brief.md",
                    summary="Requirement brief",
                    content="# Requirement Brief\n\n" + payload.get("requirement_brief", "").strip() + "\n",
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
                    path="requirements/work_breakdown.md",
                    summary="Work breakdown",
                    content="# Work Breakdown\n\n" + "\n".join(f"- {item}" for item in work_breakdown),
                ),
            ]

        task_graph = {
            "cycle_index": context.cycle_index,
            "roles": [role.value for role in role_dependencies_for_cycle(context.cycle_index).keys()],
            "dependencies": {
                role.value: [dependency.value for dependency in dependencies]
                for role, dependencies in role_dependencies_for_cycle(context.cycle_index).items()
            },
        }
        solution_lines = ["# Solution Outline", "", "## Shared Plan", _json_blob(payload.get("shared_plan", {}))]
        decisions = payload.get("architecture_decisions", [])
        if decisions:
            solution_lines.extend(["", "## Key Decisions", *[f"- {item}" for item in decisions]])
        return [
            self._artifact(
                context,
                path="architecture/solution.md",
                summary="Architecture solution document",
                content="\n".join(solution_lines).strip() + "\n",
            ),
            self._artifact(
                context,
                path="architecture/contracts.json",
                summary="Interfaces and contracts",
                content=_json_blob(payload.get("interfaces", [])),
                content_type="application/json",
            ),
            self._artifact(
                context,
                path="architecture/task_graph.json",
                summary="Execution task graph",
                content=_json_blob(task_graph),
                content_type="application/json",
            ),
        ]

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
            await log_tool("get_shared_plan", "ok", {"shared_plan_id": context.shared_plan_id})
            return _json_blob(context.shared_plan)

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
        async def retrieve_context(query: str, top_k: int = 4) -> str:
            """Retrieve extra project context using the platform RAG service."""
            items = await rag_service.retrieve(
                session,
                context.project_id,
                query,
                embedding_model,
                top_k=top_k,
            )
            await log_tool("retrieve_context", "ok", {"query": query, "count": len(items), "top_k": top_k})
            return _json_blob(items)

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
            await log_tool("submit_result", "ok", {"artifact_count": len(buffer.artifacts)})
            return "Result submitted"

        tools = [
            get_requirement,
            get_shared_plan,
            list_upstream_artifacts,
            retrieve_context,
            emit_artifact,
            submit_result,
        ]
        await self._run_tool_agent(chat_model, tools, context)

        if not buffer.submitted:
            raise ValueError(f"{self.role.value} must call submit_result before finishing.")

        self.legacy._validate_artifacts(buffer.artifacts)
        _assert_required_paths(self.role, buffer.artifacts)
        result_payload = self.legacy._normalize_result_payload(buffer.result_payload)
        return AgentTaskResult(
            summary=buffer.summary,
            artifact_list=buffer.artifacts,
            result_payload=result_payload,
            confidence=buffer.confidence,
            handoff_notes=buffer.handoff_notes,
        )

    async def _run_tool_agent(self, chat_model, tools: list[Any], context: AgentTaskContext) -> None:
        prompt_text = self._human_prompt(context)
        system_prompt = self._system_prompt(context)
        try:
            from langchain.agents import AgentExecutor, create_tool_calling_agent
            from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
        except ImportError as old_api_exc:
            try:
                from langchain.agents import create_agent
            except ImportError as new_api_exc:  # pragma: no cover - depends on optional packages
                raise RuntimeError(
                    "LangChain agent API is unavailable in the current runtime. "
                    f"Legacy import failed: {old_api_exc}. New API import failed: {new_api_exc}."
                ) from new_api_exc

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
            return

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                ("human", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )
        agent = create_tool_calling_agent(chat_model, tools, prompt)
        executor = AgentExecutor(
            agent=agent,
            tools=tools,
            return_intermediate_steps=True,
            verbose=False,
            max_iterations=20,
        )
        await asyncio.wait_for(
            executor.ainvoke({"input": prompt_text}),
            timeout=self.settings.multi_agent_task_timeout_seconds,
        )

    def _system_prompt(self, context: AgentTaskContext) -> str:
        spec = ROLE_SPECS[self.role]
        required_paths = "\n".join(f"- {path}" for path in spec["required_paths"])
        dynamic_note = ""
        if context.template_context:
            dynamic_note = f"\nTemplate context is available in the prompt and may be used when relevant.\n"
        return dedent(
            f"""
            You are the {spec['title']} in a LangGraph + LangChain multi-agent delivery workflow.
            Use tools to inspect the requirement, shared plan, upstream artifacts, and optional retrieved context.
            You must emit concrete artifacts and finish with submit_result.

            Rules:
            - Always use emit_artifact for every output file.
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

    def _human_prompt(self, context: AgentTaskContext) -> str:
        return self.legacy._build_user_prompt(context)
