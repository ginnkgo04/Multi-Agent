import pytest
import httpx

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


@pytest.mark.anyio
async def test_openai_compatible_embedding_provider_requests_float_encoding(monkeypatch: pytest.MonkeyPatch) -> None:
    requests: list[dict] = []

    class FakeResponse:
        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict:
            return {"data": [{"embedding": [1.0]}]}

    class FakeAsyncClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def post(self, url: str, json: dict, headers: dict):
            requests.append({"url": url, "json": json, "headers": headers})
            return FakeResponse()

    monkeypatch.setattr("app.providers.embedding.httpx.AsyncClient", lambda timeout: FakeAsyncClient())

    provider = OpenAICompatibleEmbeddingProvider(
        base_url="https://example.com/v1",
        api_key="secret",
        model="text-embedding-test",
    )

    await provider.embed_texts(["hello world"])

    assert requests[0]["json"]["encoding_format"] == "float"


@pytest.mark.anyio
async def test_openai_compatible_embedding_provider_retries_transient_disconnect(monkeypatch: pytest.MonkeyPatch) -> None:
    attempts = {"count": 0}

    class FakeResponse:
        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict:
            return {"data": [{"embedding": [1.0]}]}

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

    monkeypatch.setattr("app.providers.embedding.httpx.AsyncClient", lambda timeout: FakeAsyncClient())

    provider = OpenAICompatibleEmbeddingProvider(
        base_url="https://example.com/v1",
        api_key="secret",
        model="text-embedding-test",
    )

    embeddings = await provider.embed_texts(["hello world"])

    assert attempts["count"] == 2
    assert embeddings == [[1.0]]
