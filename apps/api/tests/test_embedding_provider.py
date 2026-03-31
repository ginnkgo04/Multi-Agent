import pytest

from app.providers.embedding import OpenAICompatibleEmbeddingProvider


@pytest.mark.anyio
async def test_openai_compatible_embedding_provider_sends_small_batches(monkeypatch: pytest.MonkeyPatch) -> None:
    requests: list[dict] = []

    class FakeResponse:
        def __init__(self, payload: dict) -> None:
            self._payload = payload

        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict:
            return self._payload

    class FakeAsyncClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def post(self, url: str, json: dict, headers: dict):
            requests.append({"url": url, "json": json, "headers": headers})
            text = json["input"][0]
            return FakeResponse({"data": [{"embedding": [float(len(text))]}]})

    monkeypatch.setattr("app.providers.embedding.httpx.AsyncClient", lambda timeout: FakeAsyncClient())

    provider = OpenAICompatibleEmbeddingProvider(
        base_url="https://example.com/v1",
        api_key="secret",
        model="text-embedding-test",
    )

    embeddings = await provider.embed_texts(["a", "bb", "ccc"])

    assert embeddings == [[1.0], [2.0], [3.0]]
    assert [request["json"]["input"] for request in requests] == [["a"], ["bb"], ["ccc"]]
