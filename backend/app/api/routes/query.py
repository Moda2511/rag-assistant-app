from fastapi import APIRouter, HTTPException, Request, status

from app.schemas.query import QueryRequest, QueryResponse


router = APIRouter()


@router.get("/health")
async def health(request: Request):
    app_state = request.app.state

    retrieval_service = getattr(
        app_state,
        "retrieval_service",
        None,
    )

    generation_service = getattr(
        app_state,
        "generation_service",
        None,
    )

    if retrieval_service is None:
        vector_store_status = "unavailable"
    else:
        vector_store_status = "loaded"

    if generation_service is None:
        ollama_status = "unavailable"
        ollama_model = None
    else:
        ollama_status = (
            "available"
            if generation_service.check_availability()
            else "unavailable"
        )
        ollama_model = generation_service.ollama_model

    overall_status = (
        "ok"
        if (
            vector_store_status == "loaded"
            and ollama_status == "available"
        )
        else "degraded"
    )

    return {
        "status": overall_status,
        "vector_store": vector_store_status,
        "collection": (
            retrieval_service.collection_name
            if retrieval_service
            else None
        ),
        "embedding_model": (
            retrieval_service.embedding_model_name
            if retrieval_service
            else None
        ),
        "embedding_dim": (
            retrieval_service.embedding_dim
            if retrieval_service
            else None
        ),
        "ollama": ollama_status,
        "ollama_model": ollama_model,
    }


@router.post(
    "/query",
    response_model=QueryResponse,
    status_code=status.HTTP_200_OK,
)
async def query_contract(
    request: Request,
    payload: QueryRequest,
) -> QueryResponse:
    retrieval_service = getattr(
        request.app.state,
        "retrieval_service",
        None,
    )

    generation_service = getattr(
        request.app.state,
        "generation_service",
        None,
    )

    if retrieval_service is None:
        raise HTTPException(
            status_code=503,
            detail="Retrieval service is unavailable.",
        )

    if generation_service is None:
        raise HTTPException(
            status_code=503,
            detail="Generation service is unavailable.",
        )

    try:
        chunks = retrieval_service.retrieve(
            question=payload.question,
            document_id=payload.document_id,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Retrieval failed: {exc}",
        ) from exc

    try:
        answer = generation_service.generate_answer(
            question=payload.question,
            chunks=chunks,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Generation failed: {exc}",
        ) from exc

    sources: list[str] = []

    for chunk in chunks:
        filename = chunk.get("filename") or "unknown"
        chunk_id = chunk.get("chunk_id") or "unknown"
        page_start = chunk.get("page_start")
        page_end = chunk.get("page_end")

        source = (
            f"[Source: {filename} | "
            f"Chunk: {chunk_id} | "
            f"Pages: {page_start}-{page_end}]"
        )

        if source not in sources:
            sources.append(source)

    return QueryResponse(
        answer=answer,
        sources=sources,
    )