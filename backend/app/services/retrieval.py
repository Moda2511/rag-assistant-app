from __future__ import annotations

from pathlib import Path
from typing import Any

import chromadb
from sentence_transformers import SentenceTransformer


class RetrievalService:
    def __init__(
        self,
        vector_store_dir: Path,
        collection_name: str,
        embedding_model_name: str,
        top_k: int = 5,
    ) -> None:
        self.vector_store_dir = Path(vector_store_dir)
        self.collection_name = collection_name
        self.embedding_model_name = embedding_model_name
        self.top_k = top_k

        if not self.vector_store_dir.exists():
            raise FileNotFoundError(
                f"Vector store directory not found: "
                f"{self.vector_store_dir}"
            )

        self.embedding_model = SentenceTransformer(
            self.embedding_model_name
        )

        actual_dim = (
            self.embedding_model.get_embedding_dimension()
        )

        if actual_dim is None:
            raise RuntimeError(
                "Could not determine embedding dimension."
            )

        self.embedding_dim = int(actual_dim)

        self.client = chromadb.PersistentClient(
            path=str(self.vector_store_dir)
        )

        self.collection = self.client.get_collection(
            name=self.collection_name
        )

    def retrieve(
        self,
        question: str,
        document_id: str,
        top_k: int | None = None,
    ) -> list[dict[str, Any]]:
        k = top_k or self.top_k

        if k <= 0:
            raise ValueError(
                "top_k must be greater than zero."
            )

        document_id = document_id.strip()

        if not document_id:
            raise ValueError(
                "document_id cannot be empty."
            )

        query_embedding = self.embedding_model.encode(
            [question]
        ).tolist()

        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=k,
            where={
                "document_id": document_id
            },
            include=[
                "documents",
                "metadatas",
                "distances",
            ],
        )

        documents = results.get(
            "documents",
            [[]],
        )[0]

        metadatas = results.get(
            "metadatas",
            [[]],
        )[0]

        distances = results.get(
            "distances",
            [[]],
        )[0]

        ids = results.get(
            "ids",
            [[]],
        )[0]

        hits: list[dict[str, Any]] = []

        for index, document in enumerate(documents):
            metadata = (
                metadatas[index]
                if index < len(metadatas)
                else {}
            )

            distance = (
                distances[index]
                if index < len(distances)
                else None
            )

            chunk_id = (
                ids[index]
                if index < len(ids)
                else None
            )

            hits.append(
                {
                    "chunk_id": chunk_id,
                    "chunk_text": document,
                    "distance": distance,
                    "document_id": metadata.get(
                        "document_id"
                    ),
                    "filename": metadata.get(
                        "filename"
                    ),
                    "source_path": metadata.get(
                        "source_path"
                    ),
                    "contract_type": metadata.get(
                        "contract_type"
                    ),
                    "page_start": metadata.get(
                        "page_start"
                    ),
                    "page_end": metadata.get(
                        "page_end"
                    ),
                }
            )

        return hits