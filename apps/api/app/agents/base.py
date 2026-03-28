from __future__ import annotations

import json
from dataclasses import dataclass
from textwrap import dedent
from typing import Any

from app.models.schemas import AgentTaskContext, AgentTaskResult, Role
from app.providers.chat import ChatProvider


ROLE_SPECS: dict[Role, dict[str, Any]] = {
    Role.PC: {
        "title": "Product Coordinator",
        "goal": "Break the requirement into a concrete execution brief and acceptance criteria.",
        "required_prefixes": ["requirements/"],
        "required_paths": [
            "requirements/brief.md",
            "requirements/acceptance_criteria.json",
        ],
        "payload_contract": "result_payload must include requirement_brief, acceptance_criteria, and work_breakdown.",
    },
    Role.CA: {
        "title": "Chief Architect",
        "goal": "Define the architecture, interfaces, and implementation plan for the generated solution.",
        "generation_mode": "manifest_then_files",
        "required_prefixes": ["architecture/"],
        "required_paths": [
            "architecture/solution.md",
            "architecture/contracts.json",
            "architecture/task_graph.json",
        ],
        "payload_contract": "result_payload must include shared_plan, interfaces, and architecture_decisions.",
    },
    Role.FD: {
        "title": "Frontend Developer",
        "goal": "Generate real frontend source files for the task workspace using Next.js App Router conventions.",
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
        "goal": "Generate real backend source files for the task workspace using FastAPI conventions.",
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
        "goal": "Assemble the generated solution into a task workspace manifest and delivery summary.",
        "generation_mode": "manifest_then_files",
        "required_prefixes": ["delivery/"],
        "required_paths": [
            "delivery/integration_report.md",
            "delivery/run_manifest.json",
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
            "quality/report.md",
            "quality/test_plan.md",
        ],
        "payload_contract": "result_payload must include status (PASS or FAIL), defect_list, retest_scope, and remediation_requirement.",
    },
}


@dataclass(slots=True)
class AgentProfile:
    role: Role
    system_prompt: str
    artifact_prefix: str


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
            },
        )
        payload = self._parse_model_response(raw_response)
        artifacts = self._normalize_artifacts(context, payload.get("artifacts", []))
        self._validate_artifacts(artifacts)
        result_payload = self._normalize_result_payload(payload.get("result_payload", {}))
        return AgentTaskResult(
            summary=str(payload.get("summary", "Generated implementation artifacts.")),
            artifact_list=artifacts,
            result_payload=result_payload,
            confidence=float(payload.get("confidence", 0.72)),
            handoff_notes=str(payload.get("handoff_notes", "Proceed to the next stage with the generated artifacts.")),
        )

    async def _execute_manifest_then_files(self, context: AgentTaskContext, provider: ChatProvider) -> AgentTaskResult:
        spec = ROLE_SPECS[self.profile.role]
        manifest_response = await provider.generate(
            system_prompt=self._build_manifest_system_prompt(),
            user_prompt=self._build_manifest_user_prompt(context),
            metadata={
                "role": self.profile.role.value,
                "cycle_index": context.cycle_index,
                "requirement": context.original_requirement,
                "temperature": 0.1,
                "max_tokens": 3500,
                "timeout": 180,
            },
        )
        payload = self._parse_model_response(manifest_response)
        manifest_artifacts = self._normalize_artifacts(context, payload.get("artifacts", []))
        self._validate_artifacts(manifest_artifacts)

        generated_artifacts: list[dict[str, Any]] = []
        for artifact in manifest_artifacts:
            content = await provider.generate(
                system_prompt=self._build_file_system_prompt(artifact),
                user_prompt=self._build_file_user_prompt(context, payload.get("result_payload", {}), artifact, spec["required_paths"]),
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

        return AgentTaskResult(
            summary=str(payload.get("summary", "Generated implementation artifacts.")),
            artifact_list=generated_artifacts,
            result_payload=self._normalize_result_payload(payload.get("result_payload", {})),
            confidence=float(payload.get("confidence", 0.72)),
            handoff_notes=str(payload.get("handoff_notes", "Proceed to the next stage with the generated artifacts.")),
        )

    def _build_system_prompt(self, context: AgentTaskContext) -> str:
        spec = ROLE_SPECS[self.profile.role]
        required_paths = "\n".join(f"- {path}" for path in spec["required_paths"])
        return dedent(
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

    def _build_manifest_system_prompt(self) -> str:
        spec = ROLE_SPECS[self.profile.role]
        required_paths = "\n".join(f"- {path}" for path in spec["required_paths"])
        return dedent(
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
              ]
            }}

            Rules:
            - Do not include a content field in artifacts.
            - Do not wrap JSON in markdown fences.
            - Every artifact path must be relative and must not contain '..'.
            - Use the following required paths as your minimum deliverable set:
            {required_paths}
            - {spec['payload_contract']}
            """
        ).strip()

    def _build_user_prompt(self, context: AgentTaskContext) -> str:
        if self.profile.role is Role.DE:
            max_artifacts = 8
            preview_limit = 220
        elif self.profile.role is Role.QT:
            max_artifacts = 8
            preview_limit = 320
        elif self.profile.role is Role.CA:
            max_artifacts = 4
            preview_limit = 360
        else:
            max_artifacts = 6
            preview_limit = 500
        upstream_sections = []
        for artifact in context.upstream_artifacts[:max_artifacts]:
            preview = self._normalize_prompt_text(artifact.metadata.get("content_preview", ""), limit=preview_limit)
            upstream_sections.append(
                f"- {artifact.name}\n  summary: {artifact.summary}\n  preview:\n{preview}"
            )
        if len(context.upstream_artifacts) > max_artifacts:
            upstream_sections.append(f"- ... {len(context.upstream_artifacts) - max_artifacts} more artifacts omitted for brevity")
        upstream = "\n".join(upstream_sections) or "- none"
        retrieved = "\n".join(
            f"- {self._normalize_prompt_text(item.get('source', 'knowledge'), limit=60)} "
            f"(score={self._normalize_prompt_text(item.get('score', 'n/a'), limit=20)}): "
            f"{self._normalize_prompt_text(item.get('content', ''), limit=240)}"
            for item in context.retrieved_context
        ) or "- none"
        memories = "\n".join(f"- {self._normalize_prompt_text(item, limit=240)}" for item in context.memories) or "- none"
        sections = [
            self._format_prompt_section("ROLE", self.profile.role.value),
            self._format_prompt_section("REQUIREMENT", context.original_requirement),
            self._format_prompt_section("SHARED_PLAN_JSON", json.dumps(context.shared_plan, ensure_ascii=False, indent=2)),
            self._format_prompt_section("CURRENT_CYCLE", str(context.cycle_index)),
            self._format_prompt_section("TASK_SPEC_JSON", json.dumps(context.task_spec, ensure_ascii=False, indent=2)),
            self._format_prompt_section("UPSTREAM_ARTIFACTS", upstream),
            self._format_prompt_section("RETRIEVED_CONTEXT", retrieved),
            self._format_prompt_section("MEMORIES", memories),
        ]
        if context.template_context:
            sections.append(
                self._format_prompt_section(
                    "TEMPLATE_CONTEXT_JSON",
                    json.dumps(context.template_context, ensure_ascii=False, indent=2),
                )
            )
        return "\n\n".join(sections)

    def _build_manifest_user_prompt(self, context: AgentTaskContext) -> str:
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
        return "\n\n".join(sections)

    def _parse_model_response(self, raw_response: str) -> dict[str, Any]:
        try:
            parsed = json.loads(raw_response)
        except json.JSONDecodeError:
            parsed = json.loads(self._extract_json_object(raw_response))
        if not isinstance(parsed, dict):
            raise ValueError("Model response must be a JSON object.")
        return parsed

    def _normalize_artifacts(self, context: AgentTaskContext, artifacts: list[dict[str, Any]]) -> list[dict[str, Any]]:
        normalized: list[dict[str, Any]] = []
        for artifact in artifacts:
            relative_path = self._normalize_relative_path(artifact.get("path") or artifact.get("name") or "")
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
        if not normalized:
            raise ValueError(f"{self.profile.role.value} returned no artifacts.")
        return normalized

    def _validate_artifacts(self, artifacts: list[dict[str, Any]]) -> None:
        required_prefixes = ROLE_SPECS[self.profile.role]["required_prefixes"]
        names = [artifact["name"] for artifact in artifacts]
        for prefix in required_prefixes:
            if not any(name.startswith(prefix) for name in names):
                raise ValueError(f"{self.profile.role.value} must produce at least one artifact under '{prefix}'.")
        for artifact in artifacts:
            if not artifact["name"] or ".." in artifact["name"].split("/"):
                raise ValueError(f"{self.profile.role.value} produced an invalid artifact path: {artifact['name']}")

    @staticmethod
    def _normalize_qt_payload(payload: dict[str, Any]) -> dict[str, Any]:
        status = str(payload.get("status", "FAIL")).upper()
        if status not in {"PASS", "FAIL"}:
            status = "FAIL"
        return {
            "status": status,
            "defect_list": WorkflowAgent._normalize_string_list(payload.get("defect_list", [])),
            "root_cause_guess": WorkflowAgent._stringify_value(payload.get("root_cause_guess", "")),
            "retest_scope": WorkflowAgent._normalize_string_list(payload.get("retest_scope", [])),
            "remediation_requirement": payload.get("remediation_requirement", "Investigate the failed quality gate and regenerate the affected implementation files."),
        }

    def _normalize_result_payload(self, payload: Any) -> dict[str, Any]:
        normalized_payload = payload if isinstance(payload, dict) else {"raw_payload": self._stringify_value(payload)}
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

    @staticmethod
    def _normalize_pc_payload(payload: dict[str, Any]) -> dict[str, Any]:
        return {
            "requirement_brief": WorkflowAgent._stringify_value(payload.get("requirement_brief", "")),
            "acceptance_criteria": WorkflowAgent._normalize_acceptance_criteria(payload.get("acceptance_criteria", {})),
            "work_breakdown": WorkflowAgent._normalize_string_list(payload.get("work_breakdown", [])),
        }

    @staticmethod
    def _normalize_ca_payload(payload: dict[str, Any]) -> dict[str, Any]:
        return {
            "shared_plan": WorkflowAgent._normalize_mapping(payload.get("shared_plan", payload)),
            "interfaces": WorkflowAgent._normalize_list_of_mappings(payload.get("interfaces", [])),
            "architecture_decisions": WorkflowAgent._normalize_string_list(payload.get("architecture_decisions", [])),
        }

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
