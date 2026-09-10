from __future__ import annotations

from typing import Any

from ollama import Client


GROUNDED_PROMPT_TEMPLATE = """
You are a Legal Contract Review Assistant.

Your task is to answer the user's question using ONLY the
retrieved contract context provided below.

STRICT RULES:

1. Use only the provided retrieved context.
2. Do not use outside knowledge to fill missing information.
3. Do not hallucinate or invent facts.
4. Do not fabricate citations.
5. Every factual claim about the contract must be supported
   by the retrieved context.
6. If the retrieved context is insufficient to answer the question,
   clearly state that the available contract context is insufficient.
7. Do not provide legal advice.
8. Do not make unsupported legal conclusions.
9. Preserve the meaning of the contract text.
10. Include source citations for claims based on the retrieved chunks.

Citation format:

[Source: <filename> | Chunk: <chunk_id> | Pages: <page_start>-<page_end>]

Retrieved contract context:

{context}

User question:

{question}

Answer:
"""


class GenerationService:
    def __init__(
        self,
        ollama_host: str,
        ollama_model: str,
    ) -> None:

        self.ollama_host = ollama_host
        self.ollama_model = ollama_model

        self.client = Client(
            host=self.ollama_host
        )

    @staticmethod
    def build_context(
        chunks: list[dict[str, Any]]
    ) -> str:

        if not chunks:
            return "No relevant contract context was retrieved."

        context_blocks: list[str] = []

        for chunk in chunks:

            filename = chunk.get("filename") or "unknown"
            chunk_id = chunk.get("chunk_id") or "unknown"
            page_start = chunk.get("page_start")
            page_end = chunk.get("page_end")

            citation = (
                f"[Source: {filename} | "
                f"Chunk: {chunk_id} | "
                f"Pages: {page_start}-{page_end}]"
            )

            text = chunk.get("chunk_text") or ""

            context_blocks.append(
                f"{citation}\n{text}"
            )

        return "\n\n".join(context_blocks)

    def build_prompt(
        self,
        question: str,
        chunks: list[dict[str, Any]],
    ) -> str:

        context = self.build_context(chunks)

        return GROUNDED_PROMPT_TEMPLATE.format(
            context=context,
            question=question,
        )

    def generate_answer(
        self,
        question: str,
        chunks: list[dict[str, Any]],
    ) -> str:

        if not chunks:
            return (
                "I could not find sufficient relevant contract "
                "context to answer this question."
            )

        prompt = self.build_prompt(
            question=question,
            chunks=chunks,
        )

        response = self.client.chat(
            model=self.ollama_model,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        )

        answer = response["message"]["content"].strip()

        return answer

    def check_availability(self) -> bool:
        """
        Check the SAME Ollama host used for generation.
        """

        try:
            self.client.list()
            return True

        except Exception:
            return False