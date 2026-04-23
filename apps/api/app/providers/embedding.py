from __future__ import annotations

import asyncio
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
                response = await self._post_with_retries(
                    client,
                    url,
                    payload={"model": self.model, "input": batch, "encoding_format": "float"},
                    headers=headers,
                )
                data = response.json()
                embeddings.extend(item["embedding"] for item in data["data"])
        return embeddings

    async def _post_with_retries(
        self,
        client: httpx.AsyncClient,
        url: str,
        *,
        payload: dict,
        headers: dict,
        max_attempts: int = 3,
    ) -> httpx.Response:
        last_error: Exception | None = None
        for attempt in range(1, max_attempts + 1):
            try:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                return response
            except httpx.HTTPStatusError:
                raise
            except Exception as exc:
                if not self._is_retryable_transport_error(exc) or attempt >= max_attempts:
                    raise
                last_error = exc
                await asyncio.sleep(min(0.5 * attempt, 1.5))
        if last_error is not None:
            raise last_error
        raise RuntimeError("Embedding request retry loop exited without a response or error.")

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
