from __future__ import annotations

from typing import Any, Protocol

import httpx


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
        async with httpx.AsyncClient(timeout=metadata.get("timeout", 120)) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
        data = response.json()
        content = data["choices"][0]["message"].get("content", "")
        if isinstance(content, list):
            return "".join(part.get("text", "") for part in content if isinstance(part, dict))
        return content
