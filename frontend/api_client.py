from __future__ import annotations

import os
from typing import Any

import requests
from dotenv import load_dotenv


load_dotenv()

API_BASE_URL = os.getenv("API_BASE_URL", "").strip().rstrip("/")

if not API_BASE_URL:
    raise RuntimeError(
        "API_BASE_URL is not configured. "
        "Please add it to frontend/.env"
    )


def query_contract(
    question: str,
    document_id: str,
    timeout: int = 120,
) -> dict[str, Any]:
    """
    Send a contract question to the FastAPI backend.
    """

    question = question.strip()
    document_id = document_id.strip()

    if not question:
        raise ValueError("Question cannot be empty.")

    if not document_id:
        raise ValueError("Document ID cannot be empty.")

    endpoint = f"{API_BASE_URL}/query"

    payload = {
        "question": question,
        "document_id": document_id,
    }

    try:
        response = requests.post(
            endpoint,
            json=payload,
            timeout=timeout,
        )

        response.raise_for_status()

    except requests.exceptions.ConnectionError as exc:
        raise RuntimeError(
            "Unable to connect to the RAG backend. "
            "Please make sure the backend is running on port 8000."
        ) from exc

    except requests.exceptions.Timeout as exc:
        raise RuntimeError(
            "The backend took too long to respond. "
            "Please try again."
        ) from exc

    except requests.exceptions.HTTPError as exc:
        try:
            error_data = response.json()
            detail = error_data.get("detail", "Unknown backend error.")
        except Exception:
            detail = response.text or "Unknown backend error."

        raise RuntimeError(
            f"Backend request failed ({response.status_code}): {detail}"
        ) from exc

    except requests.exceptions.RequestException as exc:
        raise RuntimeError(
            f"Request failed: {exc}"
        ) from exc

    try:
        data = response.json()
    except ValueError as exc:
        raise RuntimeError(
            "The backend returned an invalid response."
        ) from exc

    if "answer" not in data:
        raise RuntimeError(
            "The backend response does not contain an answer."
        )

    if "sources" not in data:
        data["sources"] = []

    return data


def check_backend_health(
    timeout: int = 10,
) -> dict[str, Any]:
    """
    Check whether the FastAPI backend is available.
    """

    endpoint = f"{API_BASE_URL}/health"

    try:
        response = requests.get(
            endpoint,
            timeout=timeout,
        )

        response.raise_for_status()

        return response.json()

    except requests.exceptions.RequestException as exc:
        raise RuntimeError(
            "Backend is unavailable."
        ) from exc

    except ValueError as exc:
        raise RuntimeError(
            "Backend returned an invalid health response."
        ) from exc