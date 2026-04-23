from __future__ import annotations

import json
from dataclasses import dataclass
from textwrap import dedent
from typing import Any

from app.models.schemas import AgentTaskContext, AgentTaskResult, EditOperation, Role
from app.providers.chat import ChatProvider


ROLE_SPECS: dict[Role, dict[str, Any]] = {
    Role.PC: {
        "title": "Product Coordinator",
        "goal": "Identify the product intent, then normalize the requirement into a concrete execution brief and acceptance criteria.",
        "required_prefixes": ["requirements/"],
        "required_paths": [
            "requirements/intent_spec.json",
            "requirements/brief.md",
            "requirements/acceptance_criteria.json",
            "requirements/requirement_diff_report.json",
        ],
        "payload_contract": "result_payload must include intent, requirement_brief, acceptance_criteria, work_breakdown, and requirement_fidelity.",
    },
    Role.CA: {
        "title": "Chief Architect",
        "goal": "Define the architecture, interfaces, and implementation plan for the generated solution.",
        "generation_mode": "manifest_then_files",
        "required_prefixes": ["architecture/"],
        "required_paths": [
            "architecture/shared_plan.json",
            "architecture/execution_contract.json",
            "architecture/interface_contracts.json",
            "architecture/approval_packet.md",
        ],
        "payload_contract": "result_payload must include shared_plan, interfaces, architecture_decisions, remediation_plan, and approval_status.",
    },
    Role.FD: {
        "title": "Frontend Developer",
        "goal": "Generate real frontend source files for the task workspace using the resolved implementation contract for this run.",
        "generation_mode": "manifest_then_files",
        "required_prefixes": ["workspace/frontend/", "implementation/frontend/"],
        "required_paths": [
            "workspace/frontend/package.json",
            "workspace/frontend/app/page.tsx",
            "workspace/frontend/app/globals.css",
            "workspace/frontend/components/FeatureExperience.tsx",
            "workspace/frontend/lib/api.ts",
            "implementation/frontend/notes.md",
        ],
        "payload_contract": "result_payload must include implemented_features, frontend_routes, and integration_notes.",
    },
    Role.BD: {
        "title": "Backend Developer",
        "goal": "Generate real backend source files for the task workspace using the resolved implementation contract for this run.",
        "generation_mode": "manifest_then_files",
        "required_prefixes": ["workspace/backend/", "implementation/backend/"],
        "required_paths": [
            "workspace/backend/requirements.txt",
            "workspace/backend/app/main.py",
            "workspace/backend/app/schemas.py",
            "workspace/backend/app/services.py",
            "workspace/backend/app/routes.py",
            "implementation/backend/notes.md",
        ],
        "payload_contract": "result_payload must include implemented_endpoints, data_models, and integration_notes.",
    },
    Role.DE: {
        "title": "Delivery Engineer",
        "goal": "Assemble the validated solution into a post-QT delivery bundle with integration notes and operator documentation.",
        "generation_mode": "manifest_then_files",
        "required_prefixes": ["delivery/"],
        "required_paths": [
            "delivery/delivery_manifest.json",
            "delivery/integration_report.md",
            "delivery/runbook.md",
            "delivery/architecture_guide.md",
            "delivery/checklist.md",
        ],
        "payload_contract": "result_payload must include delivery_summary, ready_to_review, and verification_steps.",
    },
    Role.QT: {
        "title": "Quality Tester",
        "goal": "Review the generated implementation and decide PASS or FAIL with actionable remediation if needed.",
        "generation_mode": "manifest_then_files",
        "required_prefixes": ["quality/"],
        "required_paths": [
            "quality/quality_gate.json",
            "quality/test_cases.json",
            "quality/defect_report.json",
            "quality/report.md",
        ],
        "payload_contract": "result_payload must include status (PASS or FAIL), approval_recommended, defect_list as an array of objects with id, description, severity (low|medium|high), owner_role, location, suggestion, expected_behavior, actual_behavior, fix_guidance, requires_plan_update, plus retest_scope and remediation_requirement. Any high-severity defect requires remediation.",
    },
}

DEFAULT_TEMPLATE_STACK = "next-fastapi"

TEMPLATE_STACK_ALIASES: dict[str, str] = {
    "next-fastapi": DEFAULT_TEMPLATE_STACK,
    "next-fastapi-template": DEFAULT_TEMPLATE_STACK,
}

ROLE_EXECUTION_CONTRACT_KEYS: dict[Role, str] = {
    Role.FD: "frontend",
    Role.BD: "backend",
}

ROLE_ALLOWED_ROOTS: dict[Role, tuple[str, ...]] = {
    Role.FD: ("workspace/frontend/", "implementation/frontend/"),
    Role.BD: ("workspace/backend/", "implementation/backend/"),
    Role.QT: ("quality/",),
    Role.DE: ("delivery/",),
}

ROLE_WORKSPACE_EDIT_ROOTS: dict[Role, tuple[str, ...]] = {
    Role.FD: ("workspace/frontend/",),
    Role.BD: ("workspace/backend/",),
}

ROLE_RESULT_CONTENT_KEYS: dict[Role, tuple[str, ...]] = {
    Role.PC: ("intent", "requirement_brief", "acceptance_criteria", "work_breakdown", "requirement_fidelity"),
    Role.CA: ("shared_plan", "execution_contract", "interfaces", "architecture_decisions", "remediation_plan"),
    Role.FD: ("implemented_features", "frontend_routes", "integration_notes"),
    Role.BD: ("implemented_endpoints", "data_models", "integration_notes"),
    Role.DE: ("delivery_summary", "ready_to_review", "verification_steps"),
    Role.QT: ("status", "approval_recommended", "defect_list", "root_cause_guess", "retest_scope", "remediation_requirement"),
}

TRANSPORT_ENVELOPE_OBJECTS = {
    "chat.completion",
    "chat.completion.chunk",
    "response",
    "response.output_text",
}

DEFAULT_TEMPLATE_EXECUTION_PROFILES: dict[str, dict[Role, dict[str, Any]]] = {
    DEFAULT_TEMPLATE_STACK: {
        Role.FD: {
            "stack_id": "nextjs-app-router",
            "required_paths": list(ROLE_SPECS[Role.FD]["required_paths"]),
            "constraints": [
                "Use Next.js App Router conventions unless CA overrides them.",
            ],
        },
        Role.BD: {
            "stack_id": "fastapi",
            "required_paths": list(ROLE_SPECS[Role.BD]["required_paths"]),
            "constraints": [
                "Use FastAPI conventions unless CA overrides them.",
            ],
        },
    }
}


@dataclass(slots=True)
class AgentProfile:
    role: Role
    system_prompt: str
    artifact_prefix: str


@dataclass(slots=True)
class ExecutionProfile:
    stack_id: str
    required_paths: list[str]
    constraints: list[str]
    source: str


class WorkflowAgent:
    def __init__(self, profile: AgentProfile) -> None:
        self.profile = profile

    async def execute(self, context: AgentTaskContext, provider: ChatProvider) -> AgentTaskResult:
        if ROLE_SPECS[self.profile.role].get("generation_mode") == "manifest_then_files":
            return await self._execute_manifest_then_files(context, provider)

        system_prompt = self._build_system_prompt(context)
        user_prompt = self._build_user_prompt(context)
        raw_response = await provider.generate(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            metadata={
                "role": self.profile.role.value,
                "cycle_index": context.cycle_index,
                "requirement": context.original_requirement,
                "temperature": 0.15,
                "max_tokens": 7000,
                "timeout": 180,
                "response_format": {"type": "json_object"},
            },
        )
        payload = self._parse_model_response(raw_response)
        edit_operations = self._parse_edit_operations(payload)
        artifacts = self._normalize_artifacts(context, payload.get("artifacts", []))
        self._validate_artifacts(context, artifacts, edit_operations=edit_operations)
        result_payload = self._normalize_result_payload(payload.get("result_payload", {}))
        return AgentTaskResult(
            summary=str(payload.get("summary", "Generated implementation artifacts.")),
            artifact_list=artifacts,
            edit_operations=edit_operations,
            result_payload=result_payload,
            confidence=float(payload.get("confidence", 0.72)),
            handoff_notes=str(payload.get("handoff_notes", "Proceed to the next stage with the generated artifacts.")),
        )

    async def _execute_manifest_then_files(self, context: AgentTaskContext, provider: ChatProvider) -> AgentTaskResult:
        required_paths = self._required_paths_for_context(context)
        payload: dict[str, Any] | None = None
        try:
            manifest_response = await provider.generate(
                system_prompt=self._build_manifest_system_prompt(context),
                user_prompt=self._build_manifest_user_prompt(context),
                metadata={
                    "role": self.profile.role.value,
                    "cycle_index": context.cycle_index,
                    "requirement": context.original_requirement,
                    "temperature": 0.1,
                    "max_tokens": 3500,
                    "timeout": 180,
                    "response_format": {"type": "json_object"},
                },
            )
            payload = self._parse_model_response(manifest_response)
            payload = self._rewrite_misplaced_documentation_operations(payload)
            edit_operations = self._parse_edit_operations(payload)
            manifest_artifacts = self._normalize_artifacts(
                context,
                payload.get("artifacts", []),
                allow_empty=bool(edit_operations),
            )
            manifest_artifacts = self._ensure_required_documentation_artifacts(
                context,
                payload,
                manifest_artifacts,
                edit_operations=edit_operations,
            )
            manifest_artifacts = self._ensure_manifest_artifacts_cover_required_paths(
                context,
                manifest_artifacts,
                edit_operations=edit_operations,
            )
            self._validate_artifacts(context, manifest_artifacts, edit_operations=edit_operations)
        except (json.JSONDecodeError, ValueError) as exc:
            if self.profile.role not in ROLE_WORKSPACE_EDIT_ROOTS:
                raise
            recovery_note = self._normalize_prompt_text(str(exc), limit=240)
            recovered_payload = self._default_workspace_recovery_result_payload(recovery_note)
            if isinstance(payload, dict):
                candidate_payload = payload.get("result_payload", {})
                if isinstance(candidate_payload, dict):
                    try:
                        recovered_payload = self._normalize_result_payload(candidate_payload)
                    except ValueError:
                        recovered_payload = self._default_workspace_recovery_result_payload(recovery_note)
            payload = {
                "summary": self._normalize_prompt_text(
                    (payload or {}).get("summary") or "Recovered implementation manifest from required paths.",
                    limit=400,
                ),
                "confidence": 0.55,
                "handoff_notes": self._normalize_prompt_text(
                    (payload or {}).get("handoff_notes")
                    or (
                        "Manifest stage returned an unusable response; "
                        f"continued with execution-contract required paths. Cause: {recovery_note}"
                    ),
                    limit=800,
                ),
                "result_payload": recovered_payload,
                "artifacts": [],
                "edit_operations": [],
            }
            edit_operations = []
            manifest_artifacts = self._ensure_manifest_artifacts_cover_required_paths(
                context,
                [],
                edit_operations=edit_operations,
            )
            self._validate_artifacts(context, manifest_artifacts, edit_operations=edit_operations)

        generated_artifacts: list[dict[str, Any]] = []
        for artifact in manifest_artifacts:
            content = await provider.generate(
                system_prompt=self._build_file_system_prompt(artifact),
                user_prompt=self._build_file_user_prompt(context, payload.get("result_payload", {}), artifact, required_paths),
                metadata={
                    "role": self.profile.role.value,
                    "cycle_index": context.cycle_index,
                    "requirement": context.original_requirement,
                    "temperature": 0.05,
                    "max_tokens": 2200,
                    "timeout": 180,
                },
            )
            generated_artifacts.append({**artifact, "content": self._strip_code_fences(content)})
        self._validate_artifacts(context, generated_artifacts, edit_operations=edit_operations)

        return AgentTaskResult(
            summary=str(payload.get("summary", "Generated implementation artifacts.")),
            artifact_list=generated_artifacts,
            edit_operations=edit_operations,
            result_payload=self._normalize_result_payload(payload.get("result_payload", {})),
            confidence=float(payload.get("confidence", 0.72)),
            handoff_notes=str(payload.get("handoff_notes", "Proceed to the next stage with the generated artifacts.")),
        )

    def _build_system_prompt(self, context: AgentTaskContext) -> str:
        spec = ROLE_SPECS[self.profile.role]
        required_paths = "\n".join(f"- {path}" for path in self._required_paths_for_context(context))
        prompt = dedent(
            f"""
            You are the {spec['title']} in a multi-agent software delivery system.
            Your job is to {spec['goal']}

            Return ONLY valid JSON with this shape:
            {{
              "summary": "short summary",
              "confidence": 0.0,
              "handoff_notes": "notes for the next role",
              "result_payload": {{... role-specific structured data ...}},
              "artifacts": [
                {{
                  "path": "relative/path/inside/task/workspace",
                  "artifact_type": "source-code | report | contract | manifest | test-plan",
                  "content_type": "text/markdown | application/json | text/x-python | text/x.typescript | text/css | text/plain",
                  "summary": "one line summary",
                  "content": "full file content"
                }}
              ]
            }}

            Rules:
            - Do not wrap JSON in markdown fences.
            - Every artifact path must be relative and must not contain '..'.
            - Generate concrete implementation files, not pseudo-code.
            - When generating code, include imports and runnable scaffolding where applicable.
            - Use the following required paths as your minimum deliverable set:
            {required_paths}
            - {spec['payload_contract']}
            """
        ).strip()
        execution_guidance = self._execution_guidance_block(context)
        if execution_guidance:
            prompt = f"{prompt}\n{execution_guidance}"
        return prompt

    def _build_manifest_system_prompt(self, context: AgentTaskContext) -> str:
        spec = ROLE_SPECS[self.profile.role]
        required_paths = "\n".join(f"- {path}" for path in self._required_paths_for_context(context))
        edit_operations_shape = self._edit_operations_response_shape()
        prompt = dedent(
            f"""
            You are the {spec['title']} in a multi-agent software delivery system.
            Your job is to {spec['goal']}

            Return ONLY valid JSON with this shape:
            {{
              "summary": "short summary",
              "confidence": 0.0,
              "handoff_notes": "notes for the next role",
              "result_payload": {{... role-specific structured data ...}},
              "artifacts": [
                {{
                  "path": "relative/path/inside/task/workspace",
                  "artifact_type": "source-code | report | contract | manifest | test-plan",
                  "content_type": "text/markdown | application/json | text/x-python | text/x.typescript | text/css | text/plain",
                  "summary": "one line summary"
                }}
              ]{edit_operations_shape}
            }}

            Rules:
            - Do not include a content field in artifacts.
            - Do not wrap JSON in markdown fences.
            - Every artifact path must be relative and must not contain '..'.
            - existing workspace files must be changed with edit operations.
            - Do not return a whole rewritten file body for an existing workspace file.
            - Use the following required paths as your minimum deliverable set:
            {required_paths}
            - {spec['payload_contract']}
            """
        ).strip()
        execution_guidance = self._execution_guidance_block(context)
        if execution_guidance:
            prompt = f"{prompt}\n{execution_guidance}"
        return prompt

    def _build_user_prompt(self, context: AgentTaskContext) -> str:
        context_sources = getattr(context, "context_sources", []) or []
        rendered_context_sources = self._render_context_sources(context_sources)
        sections = [
            self._format_prompt_section("ROLE", self.profile.role.value),
            self._format_prompt_section("REQUIREMENT", context.original_requirement),
            self._format_prompt_section("REQUIREMENT_BASELINE", getattr(context, "requirement_baseline", context.original_requirement)),
            self._format_prompt_section("SHARED_PLAN_JSON", json.dumps(context.shared_plan, ensure_ascii=False, indent=2)),
            self._format_prompt_section("CURRENT_CYCLE", str(context.cycle_index)),
            self._format_prompt_section("TASK_SPEC_JSON", json.dumps(context.task_spec, ensure_ascii=False, indent=2)),
            self._format_prompt_section("CONTEXT_SOURCES", rendered_context_sources),
        ]
        sections.extend(self._workspace_prompt_sections(context))
        if getattr(context, "clarification_history", None):
            sections.append(
                self._format_prompt_section(
                    "CLARIFICATION_HISTORY_JSON",
                    json.dumps(context.clarification_history, ensure_ascii=False, indent=2),
                )
            )
        if getattr(context, "preference_profile", None):
            sections.append(
                self._format_prompt_section(
                    "PREFERENCE_PROFILE_JSON",
                    json.dumps(context.preference_profile, ensure_ascii=False, indent=2),
                )
            )
        if context.template_context:
            sections.append(
                self._format_prompt_section(
                    "TEMPLATE_CONTEXT_JSON",
                    json.dumps(context.template_context, ensure_ascii=False, indent=2),
                )
            )
        execution_payload = self._execution_prompt_payload(context)
        if execution_payload is not None:
            sections.append(
                self._format_prompt_section(
                    "RESOLVED_EXECUTION_CONFIG_JSON",
                    json.dumps(execution_payload, ensure_ascii=False, indent=2),
                )
            )
        return "\n\n".join(sections)

    def _render_context_sources(self, context_sources: list[Any]) -> str:
        if not context_sources:
            return "- none"
        lines = []
        for source in context_sources:
            source_type = getattr(source, "source_type", None)
            if source_type is not None and hasattr(source_type, "value"):
                source_type = source_type.value
            path = getattr(source, "path", None) or getattr(source, "source_id", "unknown")
            section = getattr(source, "section", None) or "context"
            score = getattr(source, "score", None)
            excerpt = self._normalize_prompt_text(getattr(source, "excerpt", ""), limit=320)
            score_text = f" score={score}" if score is not None else ""
            lines.append(f"- [{section}] {source_type or 'context'} {path}{score_text}: {excerpt}")
        return "\n".join(lines)

    def _build_manifest_user_prompt(self, context: AgentTaskContext) -> str:
        if self.profile.role in ROLE_WORKSPACE_EDIT_ROOTS:
            return (
                self._build_user_prompt(context)
                + "\n\nReturn cycle-scoped documentation artifacts only. Express workspace changes through edit_operations. Do not inline file contents."
            )
        return self._build_user_prompt(context) + "\n\nReturn the file manifest first. Do not inline file contents."

    def _build_file_system_prompt(self, artifact: dict[str, Any]) -> str:
        content_type = artifact.get("content_type", "text/plain")
        return dedent(
            f"""
            Generate the complete contents for one file.

            Target path: {artifact["name"]}
            Content type: {content_type}

            Rules:
            - Return ONLY the raw file contents.
            - Do not add markdown fences.
            - Do not add explanations before or after the file.
            - Ensure the file is internally consistent and runnable where applicable.
            """
        ).strip()

    def _build_file_user_prompt(
        self,
        context: AgentTaskContext,
        result_payload: dict[str, Any],
        artifact: dict[str, Any],
        required_paths: list[str],
    ) -> str:
        if self.profile.role is Role.DE:
            max_artifacts = 8
            preview_limit = 180
        elif self.profile.role is Role.QT:
            max_artifacts = 8
            preview_limit = 240
        elif self.profile.role is Role.CA:
            max_artifacts = 4
            preview_limit = 220
        else:
            max_artifacts = 6
            preview_limit = 240
        upstream_sections = []
        for upstream in context.upstream_artifacts[:max_artifacts]:
            preview = self._normalize_prompt_text(upstream.metadata.get("content_preview", ""), limit=preview_limit)
            upstream_sections.append(
                f"- {upstream.name}\n  summary: {upstream.summary}\n  preview:\n{preview}"
            )
        if len(context.upstream_artifacts) > max_artifacts:
            upstream_sections.append(f"- ... {len(context.upstream_artifacts) - max_artifacts} more artifacts omitted for brevity")
        upstream = "\n".join(upstream_sections) or "- none"
        retrieved = "\n".join(
            f"- {self._normalize_prompt_text(item.get('source', 'knowledge'), limit=60)}: "
            f"{self._normalize_prompt_text(item.get('content', ''), limit=180)}"
            for item in context.retrieved_context
        ) or "- none"
        sections = [
            self._format_prompt_section("REQUIREMENT", context.original_requirement),
            self._format_prompt_section("CURRENT_CYCLE", str(context.cycle_index)),
            self._format_prompt_section("SHARED_PLAN_JSON", json.dumps(context.shared_plan, ensure_ascii=False, indent=2)),
            self._format_prompt_section("RESULT_PAYLOAD_JSON", json.dumps(result_payload, ensure_ascii=False, indent=2)),
            self._format_prompt_section("ALL_REQUIRED_PATHS_JSON", json.dumps(required_paths, ensure_ascii=False, indent=2)),
            self._format_prompt_section("CURRENT_TARGET_FILE", artifact["name"]),
            self._format_prompt_section("FILE_SUMMARY", artifact.get("summary", "")),
            self._format_prompt_section("UPSTREAM_ARTIFACTS", upstream),
            self._format_prompt_section("RETRIEVED_CONTEXT", retrieved),
        ]
        execution_payload = self._execution_prompt_payload(context)
        if execution_payload is not None:
            sections.insert(
                5,
                self._format_prompt_section(
                    "RESOLVED_EXECUTION_CONFIG_JSON",
                    json.dumps(execution_payload, ensure_ascii=False, indent=2),
                ),
            )
        return "\n\n".join(sections)

    def _parse_model_response(self, raw_response: str) -> dict[str, Any]:
        try:
            parsed = json.loads(raw_response)
        except json.JSONDecodeError:
            parsed = json.loads(self._extract_json_object(raw_response))
        if not isinstance(parsed, dict):
            raise ValueError("Model response must be a JSON object.")
        return parsed

    def _parse_edit_operations(self, payload: dict[str, Any]) -> list[EditOperation]:
        raw_edit_operations = payload.get("edit_operations", [])
        if raw_edit_operations in (None, ""):
            return []
        if not isinstance(raw_edit_operations, list):
            raise ValueError("edit_operations must be an array when provided.")
        return [self._normalize_edit_operation(item) for item in raw_edit_operations]

    def _normalize_edit_operation(self, value: Any) -> EditOperation:
        operation = EditOperation.model_validate(value)
        normalized_path = self._normalize_relative_path(operation.path)
        normalized_path = self._canonicalize_role_specific_path(normalized_path)
        if not normalized_path:
            raise ValueError("edit_operations contains an invalid path.")
        allowed_roots = ROLE_WORKSPACE_EDIT_ROOTS.get(self.profile.role)
        if allowed_roots is None:
            raise ValueError(f"{self.profile.role.value} does not support edit_operations.")
        if not any(normalized_path.startswith(root) for root in allowed_roots):
            allowed_text = ", ".join(allowed_roots)
            raise ValueError(
                f"{self.profile.role.value} edit operation '{normalized_path}' must stay under the allowed workspace roots: {allowed_text}"
            )
        return operation.model_copy(update={"path": normalized_path})

    def _normalize_artifacts(
        self,
        context: AgentTaskContext,
        artifacts: list[dict[str, Any]],
        *,
        allow_empty: bool = False,
    ) -> list[dict[str, Any]]:
        normalized: list[dict[str, Any]] = []
        for artifact in artifacts:
            relative_path = self._normalize_relative_path(artifact.get("path") or artifact.get("name") or "")
            relative_path = self._canonicalize_role_specific_path(relative_path)
            if not relative_path:
                continue
            normalized.append(
                {
                    "name": relative_path,
                    "artifact_type": artifact.get("artifact_type", self._default_artifact_type(relative_path)),
                    "content_type": artifact.get("content_type", self._default_content_type(relative_path)),
                    "summary": artifact.get("summary", relative_path),
                    "content": artifact.get("content", ""),
                    "metadata": {
                        "role": self.profile.role.value,
                        "cycle": context.cycle_index,
                        "generated_by": "live-llm",
                    },
                }
            )
        if not normalized and not allow_empty:
            raise ValueError(f"{self.profile.role.value} returned no artifacts.")
        return normalized

    def _rewrite_misplaced_documentation_operations(self, payload: dict[str, Any]) -> dict[str, Any]:
        if self.profile.role not in ROLE_WORKSPACE_EDIT_ROOTS:
            return payload

        notes_path = self._implementation_notes_path()
        if notes_path is None:
            return payload

        raw_artifacts = payload.get("artifacts", [])
        artifacts = list(raw_artifacts) if isinstance(raw_artifacts, list) else []
        raw_edit_operations = payload.get("edit_operations", [])
        if not isinstance(raw_edit_operations, list):
            return payload

        rewritten_edit_operations: list[Any] = []
        has_notes_artifact = any(
            self._canonicalize_role_specific_path(
                self._normalize_relative_path(item.get("path") or item.get("name") or "")
            )
            == notes_path
            for item in artifacts
            if isinstance(item, dict)
        )

        for item in raw_edit_operations:
            if not isinstance(item, dict):
                rewritten_edit_operations.append(item)
                continue

            normalized_path = self._canonicalize_role_specific_path(
                self._normalize_relative_path(item.get("path") or "")
            )
            if normalized_path == notes_path:
                if not has_notes_artifact:
                    artifacts.append(
                        {
                            "path": notes_path,
                            "artifact_type": "documentation",
                            "content_type": "text/markdown",
                            "summary": item.get("summary") or self._default_notes_summary(),
                            "content": item.get("content") or item.get("new_text") or "",
                        }
                    )
                    has_notes_artifact = True
                continue

            rewritten_edit_operations.append(item)

        rewritten = dict(payload)
        rewritten["artifacts"] = artifacts
        rewritten["edit_operations"] = rewritten_edit_operations
        return rewritten

    def _ensure_required_documentation_artifacts(
        self,
        context: AgentTaskContext,
        payload: dict[str, Any],
        artifacts: list[dict[str, Any]],
        *,
        edit_operations: list[EditOperation],
    ) -> list[dict[str, Any]]:
        notes_path = self._implementation_notes_path()
        if notes_path is None:
            return artifacts
        if notes_path not in self._required_paths_for_context(context):
            return artifacts
        if any(artifact["name"] == notes_path for artifact in artifacts):
            return artifacts
        if not edit_operations:
            return artifacts

        synthesized = list(artifacts)
        synthesized.append(
            {
                "name": notes_path,
                "artifact_type": "documentation",
                "content_type": "text/markdown",
                "summary": self._default_notes_summary(),
                "content": self._default_notes_content(payload, edit_operations),
                "metadata": {
                    "role": self.profile.role.value,
                    "cycle": context.cycle_index,
                    "generated_by": "live-llm",
                },
            }
        )
        return synthesized

    def _ensure_manifest_artifacts_cover_required_paths(
        self,
        context: AgentTaskContext,
        artifacts: list[dict[str, Any]],
        *,
        edit_operations: list[EditOperation],
    ) -> list[dict[str, Any]]:
        required_paths = self._required_paths_for_context(context)
        delivered_names = {artifact["name"] for artifact in artifacts}
        if self.profile.role in ROLE_WORKSPACE_EDIT_ROOTS:
            delivered_names.update(context.workspace_manifest)
            for operation in edit_operations:
                if operation.operation == "delete":
                    delivered_names.discard(operation.path)
                else:
                    delivered_names.add(operation.path)

        synthesized = list(artifacts)
        for path in required_paths:
            if path in delivered_names:
                continue
            synthesized.append(
                {
                    "name": path,
                    "artifact_type": self._default_artifact_type(path),
                    "content_type": self._default_content_type(path),
                    "summary": f"Generated {path}",
                    "content": "",
                    "metadata": {
                        "role": self.profile.role.value,
                        "cycle": context.cycle_index,
                        "generated_by": "manifest-recovery",
                    },
                }
            )
            delivered_names.add(path)
        return synthesized

    def _default_workspace_recovery_result_payload(self, recovery_note: str) -> dict[str, Any]:
        note = (
            "Manifest stage fell back to execution-contract required paths."
            if not recovery_note
            else f"Manifest stage fell back to execution-contract required paths: {recovery_note}"
        )
        if self.profile.role is Role.FD:
            return {
                "implemented_features": [],
                "frontend_routes": [],
                "integration_notes": [note],
            }
        if self.profile.role is Role.BD:
            return {
                "implemented_endpoints": [],
                "data_models": [],
                "integration_notes": [note],
            }
        raise ValueError(f"{self.profile.role.value} does not support workspace manifest recovery.")

    @staticmethod
    def _implementation_notes_path_for_role(role: Role) -> str | None:
        if role is Role.FD:
            return "implementation/frontend/notes.md"
        if role is Role.BD:
            return "implementation/backend/notes.md"
        return None

    def _implementation_notes_path(self) -> str | None:
        return self._implementation_notes_path_for_role(self.profile.role)

    def _canonicalize_role_specific_path(self, path: str) -> str:
        if not path:
            return path
        notes_path = self._implementation_notes_path()
        if notes_path is None:
            return path
        lowered = path.lower()
        if path.startswith("implementation/") and "note" in lowered:
            if self.profile.role is Role.FD and "frontend" in lowered:
                return notes_path
            if self.profile.role is Role.BD and "backend" in lowered:
                return notes_path
        return path

    def _default_notes_summary(self) -> str:
        if self.profile.role is Role.FD:
            return "Frontend implementation notes"
        if self.profile.role is Role.BD:
            return "Backend implementation notes"
        return "Implementation notes"

    def _default_notes_content(self, payload: dict[str, Any], edit_operations: list[EditOperation]) -> str:
        lines = [f"# {self._default_notes_summary()}", ""]
        summary = self._stringify_value(payload.get("summary", "")).strip()
        if summary:
            lines.extend([summary, ""])
        handoff_notes = self._stringify_value(payload.get("handoff_notes", "")).strip()
        if handoff_notes:
            lines.extend(["## Handoff", "", handoff_notes, ""])
        lines.extend(["## Workspace Changes", ""])
        for operation in edit_operations:
            lines.append(f"- `{operation.path}`: {operation.summary}")
        return "\n".join(lines).rstrip() + "\n"

    def _validate_artifacts(
        self,
        context: AgentTaskContext,
        artifacts: list[dict[str, Any]],
        *,
        edit_operations: list[EditOperation] | None = None,
    ) -> None:
        required_prefixes = self._required_prefixes_for_context(context)
        required_paths = self._required_paths_for_context(context)
        allowed_roots = ROLE_ALLOWED_ROOTS.get(self.profile.role)
        artifact_names = [artifact["name"] for artifact in artifacts]
        delivered_names = set(artifact_names)
        if self.profile.role in ROLE_WORKSPACE_EDIT_ROOTS:
            delivered_names.update(context.workspace_manifest)
            for operation in edit_operations or []:
                if operation.operation == "delete":
                    delivered_names.discard(operation.path)
                    continue
                delivered_names.add(operation.path)
        for prefix in required_prefixes:
            if not any(name.startswith(prefix) for name in delivered_names):
                raise ValueError(f"{self.profile.role.value} must produce at least one artifact under '{prefix}'.")
        missing = [path for path in required_paths if path not in delivered_names]
        if missing:
            raise ValueError(f"{self.profile.role.value} is missing required artifact paths: {', '.join(missing)}")
        for artifact in artifacts:
            if not artifact["name"] or ".." in artifact["name"].split("/"):
                raise ValueError(f"{self.profile.role.value} produced an invalid artifact path: {artifact['name']}")
            if allowed_roots and not any(artifact["name"].startswith(root) for root in allowed_roots):
                allowed_text = ", ".join(allowed_roots)
                raise ValueError(
                    f"{self.profile.role.value} produced artifact '{artifact['name']}' outside the allowed roots: {allowed_text}"
                )

    @staticmethod
    def _normalize_qt_payload(payload: dict[str, Any]) -> dict[str, Any]:
        defects = WorkflowAgent._normalize_quality_defect_list(payload.get("defect_list", []))
        status = WorkflowAgent._normalize_quality_status(payload.get("status", "FAIL"), defects)
        approval_recommended = WorkflowAgent._normalize_bool(payload.get("approval_recommended", False))
        return {
            "status": status,
            "defect_list": defects,
            "root_cause_guess": WorkflowAgent._stringify_value(payload.get("root_cause_guess", "")),
            "retest_scope": WorkflowAgent._normalize_string_list(payload.get("retest_scope", [])),
            "remediation_requirement": WorkflowAgent._stringify_value(
                payload.get("remediation_requirement", "Investigate the failed quality gate and regenerate the affected implementation files.")
            ),
            "approval_recommended": approval_recommended,
        }

    def _normalize_result_payload(self, payload: Any) -> dict[str, Any]:
        if not isinstance(payload, dict):
            raise ValueError(f"{self.profile.role.value} result payload must be a JSON object.")
        self._validate_raw_result_payload(payload)
        normalized_payload = payload
        if self.profile.role is Role.PC:
            return self._normalize_pc_payload(normalized_payload)
        if self.profile.role is Role.CA:
            return self._normalize_ca_payload(normalized_payload)
        if self.profile.role is Role.FD:
            return self._normalize_fd_payload(normalized_payload)
        if self.profile.role is Role.BD:
            return self._normalize_bd_payload(normalized_payload)
        if self.profile.role is Role.DE:
            return self._normalize_de_payload(normalized_payload)
        if self.profile.role is Role.QT:
            return self._normalize_qt_payload(normalized_payload)
        return normalized_payload

    def _validate_raw_result_payload(self, payload: dict[str, Any]) -> None:
        if self._contains_transport_envelope(payload):
            raise ValueError(f"{self.profile.role.value} received an upstream transport envelope instead of a role payload.")

        content_keys = ROLE_RESULT_CONTENT_KEYS[self.profile.role]
        meaningful_values = [payload.get(key) for key in content_keys if key in payload]
        if any(self._contains_transport_envelope(value) for value in meaningful_values):
            raise ValueError(f"{self.profile.role.value} received an upstream transport envelope instead of a role payload.")
        if any(self._has_meaningful_value(value) for value in meaningful_values):
            return
        expected_keys = ", ".join(content_keys)
        raise ValueError(
            f"{self.profile.role.value} result payload is missing role-specific fields or only contains empty placeholders. "
            f"Expected substantive content in one of: {expected_keys}."
        )

    @classmethod
    def _contains_transport_envelope(cls, value: Any) -> bool:
        if not isinstance(value, dict):
            return False
        object_type = cls._stringify_value(value.get("object")).strip().lower()
        if object_type in TRANSPORT_ENVELOPE_OBJECTS:
            return True
        if "choices" in value and "model" in value and any(key in value for key in ("id", "usage", "created")):
            return True
        return False

    @classmethod
    def _has_meaningful_value(cls, value: Any) -> bool:
        if cls._contains_transport_envelope(value):
            return False
        if isinstance(value, str):
            return bool(value.strip())
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return value != 0
        if isinstance(value, list):
            return any(cls._has_meaningful_value(item) for item in value)
        if isinstance(value, dict):
            return any(cls._has_meaningful_value(item) for item in value.values())
        return value is not None

    @staticmethod
    def _normalize_pc_payload(payload: dict[str, Any]) -> dict[str, Any]:
        return {
            "intent": WorkflowAgent._normalize_intent_payload(payload.get("intent", {})),
            "requirement_brief": WorkflowAgent._stringify_value(payload.get("requirement_brief", "")),
            "acceptance_criteria": WorkflowAgent._normalize_acceptance_criteria(payload.get("acceptance_criteria", {})),
            "work_breakdown": WorkflowAgent._normalize_string_list(payload.get("work_breakdown", [])),
            "requirement_fidelity": WorkflowAgent._normalize_requirement_fidelity(payload.get("requirement_fidelity", {})),
        }

    def _normalize_ca_payload(self, payload: dict[str, Any]) -> dict[str, Any]:
        shared_plan = WorkflowAgent._normalize_mapping(payload.get("shared_plan", payload))
        top_level_execution_contract = payload.get("execution_contract")
        if top_level_execution_contract and "execution_contract" not in shared_plan:
            shared_plan["execution_contract"] = WorkflowAgent._normalize_mapping(top_level_execution_contract)
        self._validate_ca_execution_contract(shared_plan)
        return {
            "shared_plan": shared_plan,
            "interfaces": WorkflowAgent._normalize_list_of_mappings(payload.get("interfaces", [])),
            "architecture_decisions": WorkflowAgent._normalize_string_list(payload.get("architecture_decisions", [])),
            "remediation_plan": WorkflowAgent._normalize_mapping(payload.get("remediation_plan", {})),
            "approval_status": WorkflowAgent._stringify_value(payload.get("approval_status", "pending")).strip() or "pending",
        }

    def _validate_ca_execution_contract(self, shared_plan: dict[str, Any]) -> None:
        execution_contract = shared_plan.get("execution_contract")
        if not isinstance(execution_contract, dict):
            raise ValueError("CA shared_plan.execution_contract must be an object.")

        for contract_key, role in (("frontend", Role.FD), ("backend", Role.BD)):
            role_contract = execution_contract.get(contract_key)
            if role_contract is None:
                raise ValueError(f"CA shared_plan.execution_contract.{contract_key} must be present.")
            self._parse_execution_profile_for_role(role, contract_key, role_contract)

    def _required_paths_for_context(self, context: AgentTaskContext) -> list[str]:
        execution_profile = self._resolve_execution_profile(context)
        if execution_profile is not None:
            return list(execution_profile.required_paths)
        return list(ROLE_SPECS[self.profile.role]["required_paths"])

    def _required_prefixes_for_context(self, context: AgentTaskContext) -> list[str]:
        execution_profile = self._resolve_execution_profile(context)
        if execution_profile is None:
            return list(ROLE_SPECS[self.profile.role]["required_prefixes"])
        roots = ROLE_ALLOWED_ROOTS[self.profile.role]
        prefixes: list[str] = []
        for path in execution_profile.required_paths:
            for root in roots:
                if path.startswith(root) and root not in prefixes:
                    prefixes.append(root)
        return prefixes or list(ROLE_SPECS[self.profile.role]["required_prefixes"])

    def _execution_prompt_payload(self, context: AgentTaskContext) -> dict[str, Any] | None:
        execution_profile = self._resolve_execution_profile(context)
        if execution_profile is None:
            return None
        return {
            "source": execution_profile.source,
            "stack_id": execution_profile.stack_id,
            "required_paths": execution_profile.required_paths,
            "constraints": execution_profile.constraints,
        }

    def _execution_guidance_block(self, context: AgentTaskContext) -> str:
        execution_profile = self._resolve_execution_profile(context)
        if execution_profile is None:
            return ""
        lines = [
            "Execution contract rules:",
            "- Follow CA shared_plan.execution_contract first when it defines this role.",
            "- The project template is only a fallback when CA does not define an execution_contract for this role.",
            f"- Resolved stack_id for this run: {execution_profile.stack_id} (source: {execution_profile.source}).",
        ]
        if execution_profile.constraints:
            lines.append("- Resolved execution constraints:")
            lines.extend(f"  - {constraint}" for constraint in execution_profile.constraints)
        if self.profile.role in ROLE_WORKSPACE_EDIT_ROOTS:
            lines.extend(
                [
                    "- Workspace edit mode is active for this role.",
                    "- Emit workspace/frontend/* or workspace/backend/* changes through edit_operations, not artifacts.",
                    "- Reserve artifacts for cycle-scoped documentation such as implementation notes.",
                    "- do not overwrite an existing file with a full rewritten file body.",
                ]
            )
        return "\n".join(lines)

    def _resolve_execution_profile(self, context: AgentTaskContext) -> ExecutionProfile | None:
        contract_key = ROLE_EXECUTION_CONTRACT_KEYS.get(self.profile.role)
        if contract_key is None:
            return None

        shared_contract = context.shared_plan.get("execution_contract")
        if shared_contract not in (None, {}):
            try:
                if not isinstance(shared_contract, dict):
                    raise ValueError(
                        f"{self.profile.role.value} received an invalid CA execution contract: execution_contract must be an object."
                    )
                role_contract = shared_contract.get(contract_key)
                if role_contract is not None:
                    return self._parse_execution_profile_for_role(self.profile.role, contract_key, role_contract)
            except ValueError as exc:
                return self._template_execution_profile(
                    context,
                    invalid_contract_reason=str(exc),
                )

        return self._template_execution_profile(context)

    def _template_execution_profile(
        self,
        context: AgentTaskContext,
        *,
        invalid_contract_reason: str | None = None,
    ) -> ExecutionProfile:
        template_key, template_source = self._resolve_template_stack(context.template_context)
        role_profile = DEFAULT_TEMPLATE_EXECUTION_PROFILES[template_key][self.profile.role]
        source = template_source
        if invalid_contract_reason:
            source = f"{template_source} (fallback after invalid CA execution contract: {invalid_contract_reason})"
        return ExecutionProfile(
            stack_id=str(role_profile["stack_id"]),
            required_paths=list(role_profile["required_paths"]),
            constraints=list(role_profile.get("constraints", [])),
            source=source,
        )

    def _parse_execution_profile_for_role(self, role: Role, contract_key: str, role_contract: Any) -> ExecutionProfile:
        allowed_roots = ROLE_ALLOWED_ROOTS[role]
        workspace_roots = ROLE_WORKSPACE_EDIT_ROOTS.get(role)
        notes_path = self._implementation_notes_path_for_role(role)
        if not isinstance(role_contract, dict):
            raise ValueError(
                f"{role.value} received an invalid CA execution contract: execution_contract.{contract_key} must be an object."
            )

        stack_id = self._stringify_value(role_contract.get("stack_id")).strip()
        if not stack_id:
            raise ValueError(
                f"{role.value} received an invalid CA execution contract: execution_contract.{contract_key}.stack_id must be a non-empty string."
            )

        required_paths_raw = role_contract.get("required_paths")
        if not isinstance(required_paths_raw, list):
            raise ValueError(
                f"{role.value} received an invalid CA execution contract: execution_contract.{contract_key}.required_paths must be an array."
            )

        normalized_paths: list[str] = []
        has_workspace_path = False
        for item in required_paths_raw:
            normalized_path = self._normalize_relative_path(item)
            if not normalized_path:
                raise ValueError(
                    f"{role.value} received an invalid CA execution contract: execution_contract.{contract_key}.required_paths contains an invalid path."
                )
            if workspace_roots is not None:
                is_workspace_path = any(normalized_path.startswith(root) for root in workspace_roots)
                is_notes_path = notes_path is not None and normalized_path == notes_path
                if not is_workspace_path and not is_notes_path:
                    allowed_text = " or ".join(workspace_roots)
                    raise ValueError(
                        f"{role.value} received an invalid CA execution contract: path '{normalized_path}' must stay under {allowed_text} or equal {notes_path}."
                    )
                has_workspace_path = has_workspace_path or is_workspace_path
            elif not any(normalized_path.startswith(root) for root in allowed_roots):
                allowed_text = " or ".join(allowed_roots)
                raise ValueError(
                    f"{role.value} received an invalid CA execution contract: path '{normalized_path}' must stay under {allowed_text}."
                )
            if normalized_path not in normalized_paths:
                normalized_paths.append(normalized_path)
        if not normalized_paths:
            raise ValueError(
                f"{role.value} received an invalid CA execution contract: execution_contract.{contract_key}.required_paths must contain at least one path."
            )
        if workspace_roots is not None and not has_workspace_path:
            workspace_text = " or ".join(workspace_roots)
            raise ValueError(
                f"{role.value} received an invalid CA execution contract: execution_contract.{contract_key}.required_paths must include at least one path under {workspace_text}."
            )

        constraints_raw = role_contract.get("constraints", [])
        if constraints_raw is None:
            constraints = []
        elif not isinstance(constraints_raw, list):
            raise ValueError(
                f"{role.value} received an invalid CA execution contract: execution_contract.{contract_key}.constraints must be an array."
            )
        else:
            constraints = []
            for item in constraints_raw:
                text = self._stringify_value(item).strip()
                if text:
                    constraints.append(text)

        return ExecutionProfile(
            stack_id=stack_id,
            required_paths=normalized_paths,
            constraints=constraints,
            source=f"shared_plan.execution_contract.{contract_key}",
        )

    @staticmethod
    def _resolve_template_stack(template_context: dict[str, Any]) -> tuple[str, str]:
        for source, raw_value in (
            ("template_context.stack", template_context.get("stack")),
            ("template_context.project_template", template_context.get("project_template")),
        ):
            if raw_value is None:
                continue
            normalized = TEMPLATE_STACK_ALIASES.get(str(raw_value).strip().lower())
            if normalized:
                return normalized, source
        return DEFAULT_TEMPLATE_STACK, "default-template"

    @staticmethod
    def _normalize_fd_payload(payload: dict[str, Any]) -> dict[str, Any]:
        return {
            "implemented_features": WorkflowAgent._normalize_string_list(payload.get("implemented_features", [])),
            "frontend_routes": WorkflowAgent._normalize_string_list(payload.get("frontend_routes", [])),
            "integration_notes": WorkflowAgent._normalize_string_list(payload.get("integration_notes", [])),
        }

    @staticmethod
    def _normalize_bd_payload(payload: dict[str, Any]) -> dict[str, Any]:
        return {
            "implemented_endpoints": WorkflowAgent._normalize_string_list(payload.get("implemented_endpoints", [])),
            "data_models": WorkflowAgent._normalize_string_list(payload.get("data_models", [])),
            "integration_notes": WorkflowAgent._normalize_string_list(payload.get("integration_notes", [])),
        }

    def _workspace_prompt_sections(self, context: AgentTaskContext) -> list[str]:
        if self.profile.role not in ROLE_WORKSPACE_EDIT_ROOTS:
            return []
        snapshots = [snapshot.model_dump(mode="json") for snapshot in context.workspace_snapshots]
        return [
            self._format_prompt_section(
                "WORKSPACE_MANIFEST_JSON",
                json.dumps(context.workspace_manifest, ensure_ascii=False, indent=2),
            ),
            self._format_prompt_section(
                "WORKSPACE_SNAPSHOTS_JSON",
                json.dumps(snapshots, ensure_ascii=False, indent=2),
            ),
            self._format_prompt_section("EDIT_CONSTRAINTS", self._workspace_edit_constraints_text()),
        ]

    def _edit_operations_response_shape(self) -> str:
        if self.profile.role not in ROLE_WORKSPACE_EDIT_ROOTS:
            return ""
        return dedent(
            """
            ,
              "edit_operations": [
                {
                  "path": "workspace/.../file.ext",
                  "operation": "create | update | delete",
                  "strategy": "create | replace | insert_before | insert_after | patch | delete",
                  "summary": "one line summary",
                  "content": "full file content for create operations",
                  "old_text": "exact existing text for replace operations",
                  "new_text": "replacement or inserted text",
                  "anchors": ["anchor text for insert operations"],
                  "unified_diff": "unified diff for patch strategy"
                }
              ]
            """
        ).rstrip()

    @staticmethod
    def _workspace_edit_constraints_text() -> str:
        return "\n".join(
            [
                "- Modify existing files in place.",
                "- Use edit_operations for workspace code changes.",
                "- existing workspace files must use edit_operations.",
                "- Prefer the smallest valid edit operation: replace, insert_before, insert_after, or patch.",
                "- Delete obsolete files explicitly.",
                "- Do not regenerate a parallel directory structure.",
                "- do not overwrite an existing file with a full rewritten file body.",
            ]
        )

    @staticmethod
    def _normalize_de_payload(payload: dict[str, Any]) -> dict[str, Any]:
        ready_to_review = payload.get("ready_to_review", False)
        if isinstance(ready_to_review, str):
            ready_to_review = ready_to_review.strip().lower() in {"true", "1", "yes", "ready", "pass"}
        else:
            ready_to_review = bool(ready_to_review)
        return {
            "delivery_summary": WorkflowAgent._stringify_value(payload.get("delivery_summary", "")),
            "ready_to_review": ready_to_review,
            "verification_steps": WorkflowAgent._normalize_string_list(payload.get("verification_steps", [])),
        }

    @staticmethod
    def _normalize_acceptance_criteria(value: Any) -> dict[str, list[str]]:
        if isinstance(value, dict):
            return {
                "must_have": WorkflowAgent._normalize_string_list(value.get("must_have", [])),
                "should_have": WorkflowAgent._normalize_string_list(value.get("should_have", [])),
                "could_have": WorkflowAgent._normalize_string_list(value.get("could_have", [])),
            }
        normalized = WorkflowAgent._normalize_string_list(value)
        return {"must_have": normalized, "should_have": [], "could_have": []}

    @staticmethod
    def _normalize_requirement_fidelity(value: Any) -> dict[str, Any]:
        payload = value if isinstance(value, dict) else {}
        return {
            "semantic_coverage_score": WorkflowAgent._normalize_score(payload.get("semantic_coverage_score", 0.0)),
            "constraint_retention_score": WorkflowAgent._normalize_score(payload.get("constraint_retention_score", 0.0)),
            "unmapped_items": WorkflowAgent._normalize_string_list(payload.get("unmapped_items", [])),
            "assumed_defaults": WorkflowAgent._normalize_string_list(payload.get("assumed_defaults", [])),
            "clarification_needed": WorkflowAgent._normalize_bool(payload.get("clarification_needed", False)),
        }

    @staticmethod
    def _normalize_intent_payload(value: Any) -> dict[str, Any]:
        payload = value if isinstance(value, dict) else {}
        confidence = payload.get("confidence", 0.0)
        try:
            confidence = float(confidence)
        except (TypeError, ValueError):
            confidence = 0.0
        confidence = max(0.0, min(1.0, confidence))

        needs_clarification = payload.get("needs_clarification", False)
        if isinstance(needs_clarification, str):
            needs_clarification = needs_clarification.strip().lower() in {"true", "1", "yes", "y"}
        else:
            needs_clarification = bool(needs_clarification)

        return {
            "scope": WorkflowAgent._stringify_value(payload.get("scope", "")).strip(),
            "app_type": WorkflowAgent._stringify_value(payload.get("app_type", "")).strip(),
            "confidence": confidence,
            "needs_clarification": needs_clarification,
            "clarifying_questions": WorkflowAgent._normalize_string_list(payload.get("clarifying_questions", [])),
            "key_entities": WorkflowAgent._normalize_string_list(payload.get("key_entities", [])),
            "constraints": WorkflowAgent._normalize_string_list(payload.get("constraints", [])),
        }

    @staticmethod
    def _normalize_mapping(value: Any) -> dict[str, Any]:
        if isinstance(value, dict):
            normalized: dict[str, Any] = {}
            for key, item in value.items():
                if isinstance(item, dict):
                    normalized[str(key)] = WorkflowAgent._normalize_mapping(item)
                elif isinstance(item, list):
                    normalized[str(key)] = WorkflowAgent._normalize_generic_list(item)
                else:
                    normalized[str(key)] = WorkflowAgent._stringify_value(item)
            return normalized
        if isinstance(value, list):
            return {"items": WorkflowAgent._normalize_generic_list(value)}
        text = WorkflowAgent._stringify_value(value).strip()
        return {"summary": text} if text else {}

    @staticmethod
    def _normalize_list_of_mappings(value: Any) -> list[dict[str, Any]]:
        if isinstance(value, list):
            items: list[dict[str, Any]] = []
            for item in value:
                mapping = WorkflowAgent._normalize_mapping(item)
                if mapping:
                    items.append(mapping)
            return items
        mapping = WorkflowAgent._normalize_mapping(value)
        return [mapping] if mapping else []

    @staticmethod
    def _normalize_generic_list(value: list[Any]) -> list[Any]:
        normalized: list[Any] = []
        for item in value:
            if isinstance(item, dict):
                normalized.append(WorkflowAgent._normalize_mapping(item))
            elif isinstance(item, list):
                normalized.append(WorkflowAgent._normalize_generic_list(item))
            else:
                text = WorkflowAgent._stringify_value(item).strip()
                if text:
                    normalized.append(text)
        return normalized

    @staticmethod
    def _extract_json_object(text: str) -> str:
        fenced = text.strip()
        if fenced.startswith("```"):
            lines = fenced.splitlines()
            if len(lines) >= 3:
                fenced = "\n".join(lines[1:-1]).strip()
        text = fenced
        start = text.find("{")
        if start == -1:
            raise ValueError("No JSON object found in model response.")
        depth = 0
        in_string = False
        escape = False
        for index in range(start, len(text)):
            char = text[index]
            if in_string:
                if escape:
                    escape = False
                elif char == "\\":
                    escape = True
                elif char == '"':
                    in_string = False
                continue
            if char == '"':
                in_string = True
            elif char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
                if depth == 0:
                    return text[start : index + 1]
        raise ValueError("Incomplete JSON object in model response.")

    @staticmethod
    def _default_content_type(path: str) -> str:
        if path.endswith(".md"):
            return "text/markdown"
        if path.endswith(".json"):
            return "application/json"
        if path.endswith(".py"):
            return "text/x-python"
        if path.endswith(".tsx") or path.endswith(".ts"):
            return "text/x.typescript"
        if path.endswith(".css"):
            return "text/css"
        return "text/plain"

    @staticmethod
    def _default_artifact_type(path: str) -> str:
        if path.startswith("requirements/"):
            return "requirements"
        if path.startswith("architecture/"):
            return "architecture"
        if path.startswith("workspace/"):
            return "source-code"
        if path.startswith("delivery/"):
            return "delivery"
        if path.startswith("quality/"):
            return "quality"
        return "artifact"

    @staticmethod
    def _strip_code_fences(content: str) -> str:
        stripped = content.strip()
        if stripped.startswith("```") and stripped.endswith("```"):
            lines = stripped.splitlines()
            if len(lines) >= 2:
                return "\n".join(lines[1:-1]).strip()
        return stripped

    @staticmethod
    def _normalize_relative_path(path: Any) -> str:
        text = WorkflowAgent._stringify_value(path).replace("\\", "/").strip().lstrip("/")
        text = text.replace("\r", "").replace("\n", "")
        while "//" in text:
            text = text.replace("//", "/")
        parts = [part for part in text.split("/") if part not in {"", "."}]
        if any(part == ".." for part in parts):
            return ""
        return "/".join(parts)

    @staticmethod
    def _normalize_prompt_text(value: Any, *, limit: int) -> str:
        text = WorkflowAgent._stringify_value(value).replace("\r\n", "\n").replace("\r", "\n")
        text = text.replace("\t", "  ")
        lines = [line.rstrip() for line in text.split("\n")]
        collapsed = "\n".join(lines).strip()
        if not collapsed:
            return "none"
        if len(collapsed) > limit:
            return collapsed[: max(limit - 3, 1)].rstrip() + "..."
        return collapsed

    @staticmethod
    def _format_prompt_section(name: str, content: Any) -> str:
        normalized = WorkflowAgent._normalize_prompt_text(content, limit=12000)
        return f"<{name}>\n{normalized}\n</{name}>"

    @staticmethod
    def _normalize_string_list(value: Any) -> list[str]:
        if value is None:
            return []
        if isinstance(value, str):
            text = value.strip()
            return [text] if text else []
        if isinstance(value, list):
            normalized: list[str] = []
            for item in value:
                text = WorkflowAgent._stringify_value(item).strip()
                if text:
                    normalized.append(text)
            return normalized
        text = WorkflowAgent._stringify_value(value).strip()
        return [text] if text else []

    @staticmethod
    def _normalize_quality_status(status_value: Any, defects: list[dict[str, str]]) -> str:
        status = str(status_value or "FAIL").upper()
        if status not in {"PASS", "FAIL"}:
            status = "FAIL"
        if any(defect.get("severity") == "high" for defect in defects):
            return "FAIL"
        return status

    @staticmethod
    def _normalize_quality_defect_list(value: Any) -> list[dict[str, str]]:
        if value is None:
            return []
        if not isinstance(value, list):
            value = [value]
        defects: list[dict[str, str]] = []
        for item in value:
            defect = WorkflowAgent._normalize_quality_defect(item)
            if defect["description"]:
                defects.append(defect)
        return defects

    @staticmethod
    def _normalize_quality_defect(value: Any) -> dict[str, str]:
        parsed = WorkflowAgent._parse_quality_defect_mapping(value)
        description = WorkflowAgent._stringify_value(parsed.get("description", "")).strip()
        if not description:
            description = WorkflowAgent._stringify_value(value).strip()
        return {
            "id": WorkflowAgent._stringify_value(parsed.get("id", "")).strip(),
            "description": description,
            "severity": WorkflowAgent._normalize_quality_severity(parsed.get("severity")),
            "owner_role": WorkflowAgent._stringify_value(parsed.get("owner_role", "")).strip(),
            "location": WorkflowAgent._stringify_value(parsed.get("location", "")).strip(),
            "suggestion": WorkflowAgent._stringify_value(parsed.get("suggestion", "")).strip(),
            "expected_behavior": WorkflowAgent._stringify_value(parsed.get("expected_behavior", "")).strip(),
            "actual_behavior": WorkflowAgent._stringify_value(parsed.get("actual_behavior", "")).strip(),
            "fix_guidance": WorkflowAgent._stringify_value(parsed.get("fix_guidance", "")).strip(),
            "requires_plan_update": WorkflowAgent._normalize_bool(parsed.get("requires_plan_update", False)),
        }

    @staticmethod
    def _parse_quality_defect_mapping(value: Any) -> dict[str, Any]:
        if isinstance(value, dict):
            return value
        if not isinstance(value, str):
            return {}
        text = value.strip()
        if not text:
            return {}
        parsed: dict[str, str] = {}
        for chunk in text.split("|"):
            key, separator, raw_item = chunk.partition(":")
            if not separator:
                continue
            normalized_key = key.strip().lower().replace(" ", "_")
            item = raw_item.strip()
            if normalized_key and item:
                parsed[normalized_key] = item
        return parsed

    @staticmethod
    def _normalize_quality_severity(value: Any) -> str:
        normalized = WorkflowAgent._stringify_value(value).strip().lower()
        if normalized in {"high", "critical", "major", "severe", "blocker"}:
            return "high"
        if normalized in {"low", "minor", "trivial"}:
            return "low"
        return "medium"

    @staticmethod
    def _normalize_score(value: Any) -> float:
        try:
            score = float(value)
        except (TypeError, ValueError):
            return 0.0
        if score > 1.0:
            score = score / 100.0
        return max(0.0, min(1.0, score))

    @staticmethod
    def _normalize_bool(value: Any) -> bool:
        if isinstance(value, str):
            return value.strip().lower() in {"true", "1", "yes", "y"}
        return bool(value)

    @staticmethod
    def _stringify_value(value: Any) -> str:
        if value is None:
            return ""
        if isinstance(value, str):
            return value
        if isinstance(value, dict):
            preferred_keys = ("description", "summary", "message", "title", "id", "severity", "location", "suggestion")
            parts = []
            for key in preferred_keys:
                item = value.get(key)
                if item:
                    parts.append(f"{key}: {item}")
            if parts:
                return " | ".join(parts)
            return json.dumps(value, ensure_ascii=False)
        if isinstance(value, list):
            return "; ".join(WorkflowAgent._stringify_value(item) for item in value if WorkflowAgent._stringify_value(item).strip())
        return str(value)
