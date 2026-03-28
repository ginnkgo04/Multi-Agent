from __future__ import annotations

from typing import Protocol

import httpx


class EmbeddingProvider(Protocol):
    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        ...


class OpenAICompatibleEmbeddingProvider:
    def __init__(self, *, base_url: str, api_key: str, model: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        url = f"{self.base_url}/embeddings"
        payload = {"model": self.model, "input": texts}
        headers = {"Authorization": f"Bearer {self.api_key}"}
        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
        data = response.json()
        return [item["embedding"] for item in data["data"]]
