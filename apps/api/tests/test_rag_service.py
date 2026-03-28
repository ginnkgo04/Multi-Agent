import asyncio

from app.services.rag_service import RagService


def test_chunk_text_returns_segments() -> None:
    service = RagService()
    chunks = service._chunk_text("a" * 700, size=320)

    assert len(chunks) == 3
    assert all(chunks)


def test_cosine_similarity_handles_empty_vectors() -> None:
    assert RagService._cosine_similarity([], []) == 0.0


class FakeLangChainEmbeddings:
    async def aembed_documents(self, texts: list[str]) -> list[list[float]]:
        return [[float(len(text))] for text in texts]

    async def aembed_query(self, query: str) -> list[float]:
        return [float(len(query))]


def test_langchain_embedding_adapter_methods_are_supported() -> None:
    service = RagService()
    provider = FakeLangChainEmbeddings()

    documents = asyncio.run(service._embed_many(provider, ["abc", "hello"]))
    query = asyncio.run(service._embed_query(provider, "tool query"))

    assert documents == [[3.0], [5.0]]
    assert query == [10.0]
