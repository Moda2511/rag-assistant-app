from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.query import router as query_router
from app.core.config import (
    PHASE2_CONFIG_PATH,
    Settings,
    get_collection_name,
    get_embedding_model_name,
    get_ollama_model,
    get_top_k,
    load_phase2_config,
    VECTOR_STORE_DIR,
)
from app.services.generation import GenerationService
from app.services.retrieval import RetrievalService
from app.utils.logging_config import setup_logging


logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):

    settings = Settings()

    setup_logging(settings.log_level)

    logger.info("Starting Legal Contract RAG Backend...")

    logger.info(
        "Loading Phase 2 configuration from: %s",
        PHASE2_CONFIG_PATH,
    )

    phase2_config = load_phase2_config()

    embedding_model = get_embedding_model_name(
        phase2_config
    )

    collection_name = get_collection_name(
        phase2_config
    )

    top_k = get_top_k(
        settings,
        phase2_config,
    )

    ollama_model = get_ollama_model(
        settings,
        phase2_config,
    )

    logger.info(
        "Embedding model: %s",
        embedding_model,
    )

    logger.info(
        "Chroma collection: %s",
        collection_name,
    )

    logger.info(
        "Top K: %s",
        top_k,
    )

    logger.info(
        "Ollama model: %s",
        ollama_model,
    )

    # Load retrieval resources ONCE.
    retrieval_service = RetrievalService(
        vector_store_dir=VECTOR_STORE_DIR,
        collection_name=collection_name,
        embedding_model_name=embedding_model,
        top_k=top_k,
    )

    # Load Ollama client ONCE.
    generation_service = GenerationService(
        ollama_host=settings.ollama_host,
        ollama_model=ollama_model,
    )

    app.state.settings = settings
    app.state.phase2_config = phase2_config
    app.state.retrieval_service = retrieval_service
    app.state.generation_service = generation_service

    logger.info(
        "Vector store loaded successfully."
    )

    if generation_service.check_availability():
        logger.info(
            "Ollama is available at %s",
            settings.ollama_host,
        )
    else:
        logger.warning(
            "Ollama is not currently available at %s",
            settings.ollama_host,
        )

    logger.info(
        "Legal Contract RAG Backend started successfully."
    )

    yield

    logger.info(
        "Shutting down Legal Contract RAG Backend."
    )


app = FastAPI(
    title="CUAD Legal Contract Review Assistant",
    description=(
        "RAG-based commercial contract review assistant "
        "using CUAD, ChromaDB, Sentence Transformers, "
        "and Ollama."
    ),
    version="1.0.0",
    lifespan=lifespan,
)


settings_for_cors = Settings()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings_for_cors.cors_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(
    query_router,
)