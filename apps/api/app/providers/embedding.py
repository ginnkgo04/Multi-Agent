from __future__ import annotations

from typing import Protocol

import httpx


class EmbeddingProvider(Protocol):
    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        ...


class OpenAICompatibleEmbeddingProvider:
    def __init__(self, *, base_url: str, api_key: str, model: str, batch_size: int = 1) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self.batch_size = max(1, int(batch_size))

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        url = f"{self.base_url}/embeddings"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        embeddings: list[list[float]] = []
        async with httpx.AsyncClient(timeout=120) as client:
            for index in range(0, len(texts), self.batch_size):
                batch = texts[index : index + self.batch_size]
                response = await client.post(
                    url,
                    json={"model": self.model, "input": batch},
                    headers=headers,
                )
                response.raise_for_status()
                data = response.json()
                embeddings.extend(item["embedding"] for item in data["data"])
        return embeddings
