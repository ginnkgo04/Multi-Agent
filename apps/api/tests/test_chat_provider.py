import asyncio
import json

import httpx
import pytest

from app.agents.base import AgentProfile, WorkflowAgent
from app.agents.langchain_agents import LangChainLCELAgent
from app.models.schemas import AgentTaskContext, ProviderConfig, ProviderKind, Role
from app.providers.chat import OpenAICompatibleChatProvider


def make_context(role: Role) -> AgentTaskContext:
    return AgentTaskContext(
        role=role,
        project_id="project-1",
        run_id="run-1",
        cycle_id="cycle-1",
        cycle_index=1,
        task_spec={},
        shared_plan={},
        provider_config=ProviderConfig(
            id="provider-1",
            name="openai",
            kind=ProviderKind.CHAT,
            provider="openai-compatible",
            model="gpt-5.3-codex",
            base_url="https://example.com/v1",
            api_key=None,
            is_default=True,
            settings={},
        ),
        original_requirement="生成一个沙县小吃宣传网页",
        template_context={},
    )


@pytest.mark.anyio
async def test_openai_compatible_chat_provider_accepts_responses_style_output(monkeypatch: pytest.MonkeyPatch) -> None:
    class FakeResponse:
        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict:
            return {
                "id": "resp-1",
                "output": [
                    {
                        "type": "message",
                        "content": [
                            {
                                "type": "output_text",
                                "text": "{\"ok\":true}",
                            }
                        ],
                    }
                ],
            }

    class FakeAsyncClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def post(self, url: str, json: dict, headers: dict):
            return FakeResponse()

    monkeypatch.setattr("app.providers.chat.httpx.AsyncClient", lambda timeout: FakeAsyncClient())

    provider = OpenAICompatibleChatProvider(
        base_url="https://example.com/v1",
        api_key="secret",
        model="gpt-5.3-codex",
    )

    content = await provider.generate(
        system_prompt="Return JSON only.",
        user_prompt="Return {\"ok\":true}.",
        metadata={"temperature": 0},
    )

    assert content == "{\"ok\":true}"


@pytest.mark.anyio
async def test_openai_compatible_chat_provider_raises_helpful_error_for_non_choice_payload(monkeypatch: pytest.MonkeyPatch) -> None:
    class FakeResponse:
        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict:
            return {"error": {"message": "upstream busy"}}

    class FakeAsyncClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def post(self, url: str, json: dict, headers: dict):
            return FakeResponse()

    monkeypatch.setattr("app.providers.chat.httpx.AsyncClient", lambda timeout: FakeAsyncClient())

    provider = OpenAICompatibleChatProvider(
        base_url="https://example.com/v1",
        api_key="secret",
        model="gpt-5.3-codex",
    )

    with pytest.raises(ValueError, match="upstream busy"):
        await provider.generate(
            system_prompt="Return JSON only.",
            user_prompt="Return {\"ok\":true}.",
            metadata={"temperature": 0},
        )


@pytest.mark.anyio
async def test_openai_compatible_chat_provider_enforces_wall_clock_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    class FakeAsyncClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def post(self, url: str, json: dict, headers: dict):
            await asyncio.sleep(0.05)
            raise AssertionError("post should have been cancelled before completing")

    monkeypatch.setattr("app.providers.chat.httpx.AsyncClient", lambda timeout: FakeAsyncClient())

    provider = OpenAICompatibleChatProvider(
        base_url="https://example.com/v1",
        api_key="secret",
        model="gpt-5.3-codex",
    )

    with pytest.raises(TimeoutError, match="exceeded the configured timeout"):
        await provider.generate(
            system_prompt="Return JSON only.",
            user_prompt="Return {\"ok\":true}.",
            metadata={"temperature": 0, "timeout": 0.01},
        )


@pytest.mark.anyio
async def test_openai_compatible_chat_provider_recovers_direct_json_body_when_response_json_is_invalid(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    raw_body = """
    {
      "summary": "ok",
      "confidence": 0.8,
      "handoff_notes": "next",
      "result_payload": {
        "intent": {"scope": "fullstack", "app_type": "landing_page"},
        "requirement_brief": "Build a Sha County Snacks page",
        "acceptance_criteria": {"must_have": ["hero"]},
        "work_breakdown": ["PC brief"],
        "requirement_fidelity": {
          "semantic_coverage_score": 0.9,
          "constraint_retention_score": 0.9,
          "unmapped_items": [],
          "assumed_defaults": [],
          "clarification_needed": false
        }
      },
      "artifacts": []
    }
    """.strip()

    class FakeResponse:
        status_code = 200
        text = raw_body

        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict:
            raise json.JSONDecodeError("Expecting value", self.text, 2)

    class FakeAsyncClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def post(self, url: str, json: dict, headers: dict):
            return FakeResponse()

    monkeypatch.setattr("app.providers.chat.httpx.AsyncClient", lambda timeout: FakeAsyncClient())

    provider = OpenAICompatibleChatProvider(
        base_url="https://example.com/v1",
        api_key="secret",
        model="gpt-5.3-codex",
    )

    content = await provider.generate(
        system_prompt="Return JSON only.",
        user_prompt="Return a workflow payload.",
        metadata={"temperature": 0},
    )

    assert json.loads(content)["summary"] == "ok"


@pytest.mark.anyio
async def test_openai_compatible_chat_provider_raises_helpful_error_for_non_json_http_body(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakeResponse:
        status_code = 200
        text = "upstream temporarily unavailable"

        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict:
            raise json.JSONDecodeError("Expecting value", self.text, 0)

    class FakeAsyncClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def post(self, url: str, json: dict, headers: dict):
            return FakeResponse()

    monkeypatch.setattr("app.providers.chat.httpx.AsyncClient", lambda timeout: FakeAsyncClient())

    provider = OpenAICompatibleChatProvider(
        base_url="https://example.com/v1",
        api_key="secret",
        model="gpt-5.3-codex",
    )

    with pytest.raises(ValueError, match="non-JSON response body"):
        await provider.generate(
            system_prompt="Return JSON only.",
            user_prompt="Return a workflow payload.",
            metadata={"temperature": 0},
        )


@pytest.mark.anyio
async def test_openai_compatible_chat_provider_retries_transient_transport_disconnect(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    attempts = {"count": 0}

    class FakeResponse:
        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict:
            return {
                "choices": [
                    {
                        "message": {
                            "content": "{\"ok\":true}",
                        }
                    }
                ]
            }

    class FakeAsyncClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def post(self, url: str, json: dict, headers: dict):
            attempts["count"] += 1
            if attempts["count"] == 1:
                raise httpx.RemoteProtocolError("Server disconnected without sending a response.")
            return FakeResponse()

    monkeypatch.setattr("app.providers.chat.httpx.AsyncClient", lambda timeout: FakeAsyncClient())

    provider = OpenAICompatibleChatProvider(
        base_url="https://example.com/v1",
        api_key="secret",
        model="gpt-5.3-codex",
    )

    content = await provider.generate(
        system_prompt="Return JSON only.",
        user_prompt="Return {\"ok\":true}.",
        metadata={"temperature": 0, "network_retry_attempts": 2},
    )

    assert attempts["count"] == 2
    assert content == "{\"ok\":true}"


@pytest.mark.anyio
async def test_openai_compatible_chat_provider_retries_transient_http_503(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    attempts = {"count": 0}
    request = httpx.Request("POST", "https://example.com/v1/chat/completions")

    class ServiceUnavailableResponse:
        def raise_for_status(self) -> None:
            response = httpx.Response(503, request=request)
            raise httpx.HTTPStatusError("503 Service Unavailable", request=request, response=response)

    class ContentResponse:
        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict:
            return {
                "choices": [
                    {
                        "message": {
                            "content": "{\"ok\":true}",
                        }
                    }
                ]
            }

    class FakeAsyncClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def post(self, url: str, json: dict, headers: dict):
            attempts["count"] += 1
            if attempts["count"] == 1:
                return ServiceUnavailableResponse()
            return ContentResponse()

    monkeypatch.setattr("app.providers.chat.httpx.AsyncClient", lambda timeout: FakeAsyncClient())

    provider = OpenAICompatibleChatProvider(
        base_url="https://example.com/v1",
        api_key="secret",
        model="gpt-5.3-codex",
    )

    content = await provider.generate(
        system_prompt="Return JSON only.",
        user_prompt="Return {\"ok\":true}.",
        metadata={"temperature": 0, "network_retry_attempts": 2},
    )

    assert attempts["count"] == 2
    assert content == "{\"ok\":true}"


@pytest.mark.anyio
async def test_openai_compatible_chat_provider_retries_empty_transport_envelope_body(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    attempts = {"count": 0}

    class EmptyEnvelopeResponse:
        status_code = 200
        text = 'data: {"id":"chunk-1","object":"chat.completion.chunk","choices":[]}'

        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict:
            raise json.JSONDecodeError("Expecting value", self.text, 0)

    class ContentResponse:
        status_code = 200
        text = '{"choices":[{"message":{"content":"{\\"ok\\":true}"}}]}'

        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict:
            return {
                "choices": [
                    {
                        "message": {
                            "content": "{\"ok\":true}",
                        }
                    }
                ]
            }

    class FakeAsyncClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def post(self, url: str, json: dict, headers: dict):
            attempts["count"] += 1
            if attempts["count"] == 1:
                return EmptyEnvelopeResponse()
            return ContentResponse()

    monkeypatch.setattr("app.providers.chat.httpx.AsyncClient", lambda timeout: FakeAsyncClient())

    provider = OpenAICompatibleChatProvider(
        base_url="https://example.com/v1",
        api_key="secret",
        model="gpt-5.3-codex",
    )

    content = await provider.generate(
        system_prompt="Return JSON only.",
        user_prompt="Return {\"ok\":true}.",
        metadata={"temperature": 0, "network_retry_attempts": 2},
    )

    assert attempts["count"] == 2
    assert content == "{\"ok\":true}"


@pytest.mark.anyio
async def test_openai_compatible_chat_provider_retries_transient_upstream_terminal_event_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    attempts = {"count": 0}

    class UpstreamErrorResponse:
        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict:
            return {
                "error": {
                    "message": "Upstream stream ended without a terminal response event",
                }
            }

    class ContentResponse:
        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict:
            return {
                "choices": [
                    {
                        "message": {
                            "content": "{\"ok\":true}",
                        }
                    }
                ]
            }

    class FakeAsyncClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def post(self, url: str, json: dict, headers: dict):
            attempts["count"] += 1
            if attempts["count"] == 1:
                return UpstreamErrorResponse()
            return ContentResponse()

    monkeypatch.setattr("app.providers.chat.httpx.AsyncClient", lambda timeout: FakeAsyncClient())

    provider = OpenAICompatibleChatProvider(
        base_url="https://example.com/v1",
        api_key="secret",
        model="gpt-5.3-codex",
    )

    content = await provider.generate(
        system_prompt="Return JSON only.",
        user_prompt="Return {\"ok\":true}.",
        metadata={"temperature": 0, "network_retry_attempts": 2},
    )

    assert attempts["count"] == 2
    assert content == "{\"ok\":true}"


@pytest.mark.anyio
async def test_workflow_agent_requests_json_object_response_format() -> None:
    agent = WorkflowAgent(AgentProfile(role=Role.PC, system_prompt="", artifact_prefix="test"))
    context = make_context(Role.PC)

    class FakeProvider:
        async def generate(self, *, system_prompt: str, user_prompt: str, metadata: dict) -> str:
            assert metadata["response_format"] == {"type": "json_object"}
            return """
            {
              "summary": "ok",
              "confidence": 0.8,
              "handoff_notes": "next",
              "result_payload": {
                "intent": {"scope": "fullstack", "app_type": "landing_page"},
                "requirement_brief": "Build a Sha County Snacks page",
                "acceptance_criteria": {"must_have": ["hero"]},
                "work_breakdown": ["PC brief"],
                "requirement_fidelity": {
                  "semantic_coverage_score": 0.9,
                  "constraint_retention_score": 0.9,
                  "unmapped_items": [],
                  "assumed_defaults": [],
                  "clarification_needed": false
                }
              },
              "artifacts": [
                {
                  "path": "requirements/intent_spec.json",
                  "artifact_type": "requirements",
                  "content_type": "application/json",
                  "summary": "intent",
                  "content": "{}"
                },
                {
                  "path": "requirements/brief.md",
                  "artifact_type": "requirements",
                  "content_type": "text/markdown",
                  "summary": "brief",
                  "content": "# Brief"
                },
                {
                  "path": "requirements/acceptance_criteria.json",
                  "artifact_type": "requirements",
                  "content_type": "application/json",
                  "summary": "criteria",
                  "content": "{}"
                },
                {
                  "path": "requirements/requirement_diff_report.json",
                  "artifact_type": "requirements",
                  "content_type": "application/json",
                  "summary": "diff",
                  "content": "{}"
                }
              ]
            }
            """

    result = await agent.execute(context, FakeProvider())

    assert result.summary == "ok"


@pytest.mark.anyio
async def test_lcel_agent_requests_json_object_response_format() -> None:
    agent = LangChainLCELAgent(Role.PC)
    context = make_context(Role.PC)

    class FakeProvider:
        async def generate(self, *, system_prompt: str, user_prompt: str, metadata: dict) -> str:
            assert metadata["response_format"] == {"type": "json_object"}
            return """
            {
              "intent": {
                "scope": "fullstack",
                "app_type": "landing_page",
                "confidence": 0.9,
                "needs_clarification": false,
                "clarifying_questions": [],
                "key_entities": ["menu"],
                "constraints": ["simple backend"]
              },
              "requirement_brief": "Build a Sha County Snacks page",
              "acceptance_criteria": {"must_have": ["hero"]},
              "work_breakdown": ["PC brief"],
              "requirement_fidelity": {
                "semantic_coverage_score": 0.9,
                "constraint_retention_score": 0.9,
                "unmapped_items": [],
                "assumed_defaults": [],
                "clarification_needed": false
              },
              "summary": "ok",
              "handoff_notes": "next",
              "confidence": 0.8
            }
            """

    result = await agent.execute(
        context,
        chat_model=FakeProvider(),
        fallback_provider=None,
        session=None,
        embedding_model=None,
        rag_service=None,
    )

    assert result.summary == "ok"
