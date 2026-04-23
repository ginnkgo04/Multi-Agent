from __future__ import annotations

import asyncio
import json
from typing import Any, Protocol

import httpx


TRANSPORT_ENVELOPE_OBJECTS = {
    "chat.completion",
    "chat.completion.chunk",
    "response",
    "response.output_text",
}

RETRYABLE_UPSTREAM_ERROR_MARKERS = (
    "upstream stream ended without a terminal response event",
    "server disconnected without sending a response",
)

RETRYABLE_HTTP_STATUSES = {408, 409, 425, 429, 500, 502, 503, 504}


class ChatProvider(Protocol):
    async def generate(self, *, system_prompt: str, user_prompt: str, metadata: dict[str, Any]) -> str:
        ...


class OpenAICompatibleChatProvider:
    def __init__(self, *, base_url: str, api_key: str, model: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model

    async def generate(self, *, system_prompt: str, user_prompt: str, metadata: dict[str, Any]) -> str:
        url = f"{self.base_url}/chat/completions"
        timeout_seconds = metadata.get("timeout", 120)
        max_attempts = max(1, int(metadata.get("network_retry_attempts", 3)))
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": metadata.get("temperature", 0.2),
        }
        if metadata.get("max_tokens"):
            payload["max_tokens"] = metadata["max_tokens"]
        if metadata.get("response_format"):
            payload["response_format"] = metadata["response_format"]
        headers = {"Authorization": f"Bearer {self.api_key}"}

        async def _send_request() -> httpx.Response:
            async with httpx.AsyncClient(timeout=timeout_seconds) as client:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                return response

        last_empty_envelope: Any = None
        for attempt in range(1, max_attempts + 1):
            try:
                response = await self._send_with_retries(
                    _send_request,
                    timeout_seconds=timeout_seconds,
                    max_attempts=max_attempts,
                )
            except asyncio.TimeoutError as exc:
                raise TimeoutError(f"LLM request exceeded the configured timeout after {timeout_seconds} seconds.") from exc

            try:
                data = response.json()
            except json.JSONDecodeError as exc:
                recovered, envelope = self._recover_content_from_raw_body(getattr(response, "text", ""))
                if recovered is not None:
                    return recovered
                if envelope is not None:
                    last_empty_envelope = envelope
                    if attempt < max_attempts:
                        await asyncio.sleep(min(0.5 * attempt, 1.5))
                        continue
                    raise ValueError(self._empty_envelope_message(envelope)) from exc
                snippet = self._response_body_snippet(getattr(response, "text", ""))
                raise ValueError(
                    f"LLM endpoint returned a non-JSON response body (status={getattr(response, 'status_code', 'unknown')}): {snippet}"
                ) from exc

            content = self._extract_content(data)
            if content is not None:
                return content
            if self._is_empty_transport_envelope(data):
                last_empty_envelope = data
                if attempt < max_attempts:
                    await asyncio.sleep(min(0.5 * attempt, 1.5))
                    continue
                raise ValueError(self._empty_envelope_message(data))
            retryable_error = self._retryable_upstream_error_message(data)
            if retryable_error is not None:
                if attempt < max_attempts:
                    await asyncio.sleep(min(0.5 * attempt, 1.5))
                    continue
                raise ValueError(self._retryable_upstream_error_exhausted_message(retryable_error))
            raise ValueError(self._unexpected_response_message(data))

        if last_empty_envelope is not None:
            raise ValueError(self._empty_envelope_message(last_empty_envelope))
        raise RuntimeError("LLM request retry loop exited without content or error.")

    async def _send_with_retries(
        self,
        send_request,
        *,
        timeout_seconds: float,
        max_attempts: int,
    ) -> httpx.Response:
        last_error: Exception | None = None
        for attempt in range(1, max_attempts + 1):
            try:
                return await asyncio.wait_for(send_request(), timeout=timeout_seconds)
            except asyncio.TimeoutError:
                raise
            except httpx.HTTPStatusError as exc:
                if not self._is_retryable_http_status(exc) or attempt >= max_attempts:
                    raise
                last_error = exc
                await asyncio.sleep(min(0.5 * attempt, 1.5))
            except Exception as exc:
                if not self._is_retryable_transport_error(exc) or attempt >= max_attempts:
                    raise
                last_error = exc
                await asyncio.sleep(min(0.5 * attempt, 1.5))
        if last_error is not None:
            raise last_error
        raise RuntimeError("LLM request retry loop exited without a response or error.")

    @staticmethod
    def _is_retryable_transport_error(exc: Exception) -> bool:
        return isinstance(
            exc,
            (
                httpx.RemoteProtocolError,
                httpx.ReadError,
                httpx.WriteError,
                httpx.ConnectError,
                httpx.ConnectTimeout,
                httpx.ReadTimeout,
                httpx.WriteTimeout,
                httpx.PoolTimeout,
                httpx.CloseError,
                httpx.NetworkError,
                httpx.ProtocolError,
            ),
        )

    @staticmethod
    def _is_retryable_http_status(exc: httpx.HTTPStatusError) -> bool:
        return exc.response.status_code in RETRYABLE_HTTP_STATUSES

    @classmethod
    def _extract_content(cls, payload: Any) -> str | None:
        if not isinstance(payload, dict):
            return None

        choices = payload.get("choices")
        if isinstance(choices, list) and choices:
            first_choice = choices[0] if isinstance(choices[0], dict) else {}
            message = first_choice.get("message") if isinstance(first_choice, dict) else {}
            if isinstance(message, dict):
                content = cls._normalize_content(message.get("content"))
                if content:
                    return content
            content = cls._normalize_content(first_choice.get("text"))
            if content:
                return content

        output_text = cls._normalize_content(payload.get("output_text"))
        if output_text:
            return output_text

        output = payload.get("output")
        if isinstance(output, list):
            parts: list[str] = []
            for item in output:
                if not isinstance(item, dict):
                    continue
                content = cls._normalize_content(item.get("content"))
                if content:
                    parts.append(content)
            if parts:
                return "".join(parts)

        content = cls._normalize_content(payload.get("content"))
        return content or None

    @classmethod
    def _normalize_content(cls, value: Any) -> str:
        if isinstance(value, str):
            return value
        if isinstance(value, dict):
            text = value.get("text")
            if isinstance(text, str):
                return text
            if isinstance(text, dict):
                nested = text.get("value")
                if isinstance(nested, str):
                    return nested
            return ""
        if isinstance(value, list):
            parts: list[str] = []
            for item in value:
                normalized = cls._normalize_content(item)
                if normalized:
                    parts.append(normalized)
            return "".join(parts)
        return ""

    @staticmethod
    def _unexpected_response_message(payload: Any) -> str:
        if isinstance(payload, dict):
            error = payload.get("error")
            if isinstance(error, dict):
                message = error.get("message")
                if isinstance(message, str) and message.strip():
                    return f"LLM response did not contain content: {message.strip()}"
            snippet = json.dumps(payload, ensure_ascii=False)[:400]
            return f"LLM response did not contain chat content. payload={snippet}"
        return "LLM response did not contain chat content."

    @classmethod
    def _empty_envelope_message(cls, payload: Any) -> str:
        snippet = json.dumps(payload, ensure_ascii=False)[:400] if isinstance(payload, dict) else str(payload)[:400]
        return f"LLM endpoint returned a transport envelope without chat content after retries. payload={snippet}"

    @classmethod
    def _retryable_upstream_error_message(cls, payload: Any) -> str | None:
        if not isinstance(payload, dict):
            return None
        error = payload.get("error")
        if not isinstance(error, dict):
            return None
        message = error.get("message")
        if not isinstance(message, str) or not message.strip():
            return None
        normalized = message.strip().lower()
        if any(marker in normalized for marker in RETRYABLE_UPSTREAM_ERROR_MARKERS):
            return message.strip()
        return None

    @staticmethod
    def _retryable_upstream_error_exhausted_message(message: str) -> str:
        return f"LLM endpoint returned a retryable upstream error after retries: {message}"

    @classmethod
    def _recover_content_from_raw_body(cls, body: str) -> tuple[str | None, dict[str, Any] | None]:
        snippet = body.strip()
        if not snippet:
            return None, None
        try:
            extracted = cls._extract_json_object(snippet)
            parsed = json.loads(extracted)
        except (ValueError, json.JSONDecodeError):
            return None, None
        content = cls._extract_content(parsed)
        if content:
            return content, None
        if cls._is_empty_transport_envelope(parsed):
            return None, parsed
        if isinstance(parsed, dict):
            return extracted, None
        return None, None

    @classmethod
    def _is_empty_transport_envelope(cls, payload: Any) -> bool:
        if not isinstance(payload, dict):
            return False
        object_type = str(payload.get("object", "")).strip().lower()
        if object_type not in TRANSPORT_ENVELOPE_OBJECTS:
            return False
        return cls._extract_content(payload) is None

    @staticmethod
    def _response_body_snippet(body: str, limit: int = 240) -> str:
        normalized = " ".join(body.strip().split())
        if not normalized:
            return "<empty>"
        return normalized[:limit]

    @staticmethod
    def _extract_json_object(text: str) -> str:
        fenced = text.strip()
        if fenced.startswith("```"):
            lines = fenced.splitlines()
            if len(lines) >= 3:
                fenced = "\n".join(lines[1:-1]).strip()
        start = fenced.find("{")
        if start == -1:
            raise ValueError("No JSON object found in response body.")
        depth = 0
        in_string = False
        escape = False
        for index in range(start, len(fenced)):
            char = fenced[index]
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
                    return fenced[start : index + 1]
        raise ValueError("Incomplete JSON object in response body.")
