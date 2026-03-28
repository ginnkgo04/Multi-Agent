from app.services.rag_service import RagService


def test_chunk_text_returns_segments() -> None:
    service = RagService()
    chunks = service._chunk_text("a" * 700, size=320)

    assert len(chunks) == 3
    assert all(chunks)


def test_cosine_similarity_handles_empty_vectors() -> None:
    assert RagService._cosine_similarity([], []) == 0.0
