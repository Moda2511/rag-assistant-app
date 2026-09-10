from fastapi.testclient import TestClient

from app.main import app


def test_query_happy_path():
    class FakeRetrievalService:
        def retrieve(
            self,
            question: str,
            document_id: str,
        ):
            assert document_id == "CUAD_000001"

            return [
                {
                    "chunk_id": "CUAD_000001_chunk_0001",
                    "chunk_text": (
                        "The agreement may be assigned "
                        "with consent."
                    ),
                    "distance": 0.1,
                    "document_id": "CUAD_000001",
                    "filename": "sample.pdf",
                    "source_path": "sample.pdf",
                    "contract_type": "Commercial Agreement",
                    "page_start": 1,
                    "page_end": 2,
                }
            ]

    class FakeGenerationService:
        ollama_model = "qwen2.5:7b"

        def generate_answer(self, question, chunks):
            return (
                "The agreement may be assigned with consent. "
                "[Source: sample.pdf | "
                "Chunk: CUAD_000001_chunk_0001 | Pages: 1-2]"
            )

        def check_availability(self):
            return True

    original_retrieval = getattr(
        app.state,
        "retrieval_service",
        None,
    )

    original_generation = getattr(
        app.state,
        "generation_service",
        None,
    )

    app.state.retrieval_service = FakeRetrievalService()
    app.state.generation_service = FakeGenerationService()

    try:
        with TestClient(app) as client:
            response = client.post(
                "/query",
                json={
                    "question": (
                        "Can the agreement be assigned "
                        "to another party?"
                    ),
                    "document_id": "CUAD_000001",
                },
            )

        assert response.status_code == 200

        data = response.json()

        assert "answer" in data
        assert "sources" in data
        assert len(data["answer"]) > 0
        assert len(data["sources"]) > 0

    finally:
        app.state.retrieval_service = original_retrieval
        app.state.generation_service = original_generation


def test_query_invalid_empty_question():
    with TestClient(app) as client:
        response = client.post(
            "/query",
            json={
                "question": "",
                "document_id": "CUAD_000001",
            },
        )

    assert response.status_code == 422


def test_query_invalid_whitespace_question():
    with TestClient(app) as client:
        response = client.post(
            "/query",
            json={
                "question": "   ",
                "document_id": "CUAD_000001",
            },
        )

    assert response.status_code == 422


def test_query_invalid_missing_document_id():
    with TestClient(app) as client:
        response = client.post(
            "/query",
            json={
                "question": "What is the governing law?"
            },
        )

    assert response.status_code == 422


def test_query_invalid_empty_document_id():
    with TestClient(app) as client:
        response = client.post(
            "/query",
            json={
                "question": "What is the governing law?",
                "document_id": "",
            },
        )

    assert response.status_code == 422