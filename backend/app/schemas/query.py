from pydantic import BaseModel, Field, field_validator


class QueryRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
        description="Question about the selected commercial contract",
    )

    document_id: str = Field(
        ...,
        min_length=1,
        description="CUAD document ID to search within",
    )

    @field_validator("question")
    @classmethod
    def validate_question(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError(
                "Question cannot be empty or whitespace."
            )

        return value

    @field_validator("document_id")
    @classmethod
    def validate_document_id(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError(
                "Document ID cannot be empty or whitespace."
            )

        return value


class QueryResponse(BaseModel):
    answer: str
    sources: list[str]