# RAG Assistant for Legal Contract Review

An end-to-end Retrieval-Augmented Generation (RAG) application for querying and analyzing commercial legal contracts.

The system allows users to ask natural-language questions about contracts and receive answers grounded in relevant contract passages retrieved from a vector database.

The project combines semantic search, vector retrieval, and local Large Language Model (LLM) generation through a FastAPI backend and Streamlit frontend.

---

## Overview

This project implements a complete RAG pipeline for legal contract question answering using the **Contract Understanding Atticus Dataset (CUAD)**.

The application provides:

* Semantic retrieval of relevant contract passages.
* Local vector storage using ChromaDB.
* Sentence Transformer embeddings.
* Local LLM-based answer generation using Ollama.
* FastAPI backend for the RAG API.
* Streamlit frontend for user interaction.
* Automated backend tests.
* Docker support for the backend.
* A reproducible notebook for the RAG pipeline.

The main goal is to build an explainable legal-document assistant that retrieves relevant contractual evidence before generating an answer.

> **Disclaimer:** This project is for educational and research purposes. It is not a substitute for professional legal advice.

---

# Architecture

```text
                         User
                           │
                           ▼
                 ┌───────────────────┐
                 │ Streamlit         │
                 │ Frontend          │
                 └─────────┬─────────┘
                           │ HTTP
                           ▼
                 ┌───────────────────┐
                 │ FastAPI           │
                 │ Backend           │
                 └─────────┬─────────┘
                           │
                    User Question
                           │
                           ▼
                 ┌───────────────────┐
                 │ Query Embedding   │
                 │ all-MiniLM-L6-v2  │
                 └─────────┬─────────┘
                           │
                           ▼
                 ┌───────────────────┐
                 │ ChromaDB          │
                 │ Vector Retrieval  │
                 └─────────┬─────────┘
                           │
                    Retrieved Context
                           │
                           ▼
                 ┌───────────────────┐
                 │ Ollama             │
                 │ Qwen 2.5 7B       │
                 └─────────┬─────────┘
                           │
                           ▼
                    Grounded Answer
                           │
                           ▼
                 ┌───────────────────┐
                 │ Streamlit         │
                 │ Frontend          │
                 └───────────────────┘
```

---

# RAG Pipeline

The RAG pipeline follows these steps:

1. Load CUAD contract documents.
2. Extract text from the documents.
3. Split documents into meaningful chunks.
4. Generate embeddings using `all-MiniLM-L6-v2`.
5. Store embeddings in ChromaDB.
6. Convert the user's question into an embedding.
7. Retrieve the most relevant contract chunks.
8. Pass the retrieved context to the LLM.
9. Generate a grounded answer using Qwen 2.5 7B through Ollama.
10. Return the answer and relevant source information to the frontend.

```text
CUAD Documents
      │
      ▼
Text Extraction
      │
      ▼
Document Chunking
      │
      ▼
all-MiniLM-L6-v2
      │
      ▼
ChromaDB
      │
      │
      │ User Query
      ▼
Semantic Retrieval
      │
      ▼
Relevant Contract Context
      │
      ▼
Qwen 2.5 7B
      │
      ▼
Grounded Answer
```

---

# Tech Stack

| Component            | Technology            |
| -------------------- | --------------------- |
| Programming Language | Python 3.13           |
| RAG Framework        | Custom RAG Pipeline   |
| Embeddings           | Sentence Transformers |
| Embedding Model      | `all-MiniLM-L6-v2`    |
| Vector Database      | ChromaDB              |
| LLM Runtime          | Ollama                |
| Language Model       | Qwen 2.5 7B           |
| Backend              | FastAPI               |
| API Server           | Uvicorn               |
| Frontend             | Streamlit             |
| PDF Processing       | pypdf                 |
| Data Processing      | Pandas / NumPy        |
| Testing              | Pytest                |
| Containerization     | Docker                |
| Dataset              | CUAD                  |

---

# Dataset

## Contract Understanding Atticus Dataset (CUAD)

This project uses the **Contract Understanding Atticus Dataset (CUAD)** for legal contract understanding and question answering.

CUAD contains commercial contracts with annotations covering multiple contractual clause categories.

Examples include:

* Governing Law
* Confidentiality
* Termination
* Assignment
* Change of Control
* Indemnification
* Insurance
* Renewal Terms
* Non-Compete

---

# Dataset Download

The CUAD dataset was downloaded from the Hugging Face dataset repository using the Hugging Face CLI.

```bash
hf download theatticusproject/cuad --repo-type dataset --local-dir data/CUAD
```

If the Hugging Face CLI is not installed:

```bash
pip install -U "huggingface_hub[cli]"
```

Then download the dataset:

```bash
hf download theatticusproject/cuad --repo-type dataset --local-dir data/CUAD
```

The expected local location is:

```text
data/
└── CUAD/
```

### Important

The raw CUAD contract corpus is intentionally **not included in this GitHub repository** because of its size.

The following directories are excluded through `.gitignore`:

```text
data/CUAD/CUAD_v1/full_contract_pdf/
data/CUAD/CUAD_v1/full_contract_txt/
data/CUAD/CUAD_v1/label_group_xlsx/
```

The large `CUAD_v1.json` file is also excluded.

The dataset should therefore be downloaded locally before reproducing the complete RAG pipeline.

---

# Embedding Model

The project uses the Sentence Transformers model:

```text
all-MiniLM-L6-v2
```

The model converts both contract chunks and user queries into vector representations.

These embeddings are used for semantic similarity search in ChromaDB.

### Embedding Flow

```text
Contract Chunk
      │
      ▼
all-MiniLM-L6-v2
      │
      ▼
Vector Representation
      │
      ▼
ChromaDB
```

For a user query:

```text
User Question
      │
      ▼
all-MiniLM-L6-v2
      │
      ▼
Query Vector
      │
      ▼
Similarity Search
      │
      ▼
Relevant Contract Chunks
```

---

# Project Structure

```text
rag-assistant-project/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── routes/
│   │   │       └── query.py
│   │   │
│   │   ├── core/
│   │   │   └── config.py
│   │   │
│   │   ├── schemas/
│   │   │   └── query.py
│   │   │
│   │   ├── services/
│   │   │   ├── generation.py
│   │   │   └── retrieval.py
│   │   │
│   │   ├── utils/
│   │   │   └── logging_config.py
│   │   │
│   │   └── main.py
│   │
│   ├── tests/
│   │   └── test_query.py
│   │
│   ├── Dockerfile
│   ├── pytest.ini
│   └── requirements.txt
│
├── frontend/
│   ├── api_client.py
│   ├── app.py
│   └── requirements.txt
│
├── notebooks/
│   └── rag_pipeline.ipynb
│
├── data/
│   └── CUAD/
│       ├── CUAD_v1/
│       └── README.md
│
├── .env.example
├── .gitignore
├── README.md
└── requirements.txt
```

---

# Requirements

Before running the project, install:

* Python 3.10 or newer
* Git
* Ollama
* Hugging Face CLI

Python 3.13 was used during development.

---

# Installation

## 1. Clone the Repository

```bash
git clone https://github.com/Moda2511/rag-assistant-app.git
```

Enter the project directory:

```bash
cd rag-assistant-app
```

---

## 2. Create a Virtual Environment

On Windows:

```cmd
python -m venv .venv
```

Activate it:

```cmd
.venv\Scripts\activate
```

---

## 3. Install Dependencies

Install the main dependencies:

```cmd
pip install -r requirements.txt
```

Install backend dependencies:

```cmd
pip install -r backend\requirements.txt
```

Install frontend dependencies:

```cmd
pip install -r frontend\requirements.txt
```

---

# Ollama Setup

The project uses Ollama for local LLM inference.

Install Ollama and make sure the Ollama service is running.

Pull the required model:

```cmd
ollama pull qwen2.5:7b
```

Verify the installed model:

```cmd
ollama list
```

The application expects Ollama to be available locally.

Default Ollama address:

```text
http://localhost:11434
```

---

# Environment Variables

Create the environment file from the example:

```cmd
copy .env.example .env
```

If required by the backend:

```cmd
copy backend\.env.example backend\.env
```

Example environment configuration:

| Variable          | Description             | Example                  |
| ----------------- | ----------------------- | ------------------------ |
| `OLLAMA_BASE_URL` | Ollama server URL       | `http://localhost:11434` |
| `OLLAMA_MODEL`    | LLM used for generation | `qwen2.5:7b`             |
| `CHROMA_PATH`     | ChromaDB storage path   | `./chroma_db`            |

> Do not commit `.env` files, API keys, passwords, or other secrets to GitHub.

---

# Running the RAG Pipeline

The main RAG pipeline is available in:

```text
notebooks/rag_pipeline.ipynb
```

Run the notebook to reproduce the data preparation and vector-store creation process.

The notebook covers:

1. Dataset loading.
2. Document processing.
3. Text extraction.
4. Chunking.
5. Embedding generation.
6. Vector-store creation.
7. Retrieval.
8. RAG querying.
9. Evaluation.

The generated vector store is excluded from GitHub when it is large.

---

# Running the Backend

Open a terminal in the project directory.

```cmd
cd C:\Users\Lenovo\rag-assistant-project
```

Activate the virtual environment:

```cmd
.venv\Scripts\activate
```

Enter the backend directory:

```cmd
cd backend
```

Start FastAPI:

```cmd
uvicorn app.main:app --reload
```

The backend will run at:

```text
http://127.0.0.1:8000
```

---

# Backend Health Check

Open:

```text
http://127.0.0.1:8000/health
```

A successful response should indicate that the backend is running.

---

# Swagger API Documentation

FastAPI provides an interactive API documentation interface.

Open:

```text
http://127.0.0.1:8000/docs
```

The Swagger interface allows you to inspect and test the available API endpoints.

---

# Running the Frontend

Keep the backend terminal running.

Open a second terminal.

```cmd
cd C:\Users\Lenovo\rag-assistant-project
```

Activate the virtual environment:

```cmd
.venv\Scripts\activate
```

Start Streamlit:

```cmd
streamlit run frontend/app.py
```

The frontend will normally be available at:

```text
http://localhost:8501
```

Open the URL in your browser.

---

# API Reference

## POST `/query`

The `/query` endpoint accepts a natural-language question and returns an answer generated from retrieved contract context.

### Example Request

```bash
curl -X POST "http://127.0.0.1:8000/query" ^
  -H "Content-Type: application/json" ^
  -d "{\"question\":\"What is the governing law of this agreement?\"}"
```

### Example Question

```text
What is the governing law of this agreement?
```

The backend:

1. Receives the question.
2. Generates the query embedding.
3. Searches ChromaDB.
4. Retrieves relevant contract passages.
5. Sends the retrieved context to Qwen 2.5 7B.
6. Returns the generated answer.

---

# Example Questions

The application can be used for questions such as:

### Governing Law

```text
What is the governing law of this agreement?
```

### Confidentiality

```text
Does this contract contain a confidentiality clause?
If so, what obligations does it impose on the parties?
```

### Termination

```text
Can either party terminate this agreement?
If yes, under what conditions?
```

### Assignment and Change of Control

```text
Does this agreement contain any restrictions on assignment or change of control?
Explain the relevant provision.
```

---

# Evaluation

The RAG system was evaluated as part of the project evaluation process.

## Phase 2.6 Results

The final evaluation results should be reported here based on the actual Phase 2.6 evaluation output.

| Metric                   |         Result |
| ------------------------ | -------------: |
| Retrieval Evaluation     | **ADD RESULT** |
| Answer Quality           | **ADD RESULT** |
| Context Relevance        | **ADD RESULT** |
| Faithfulness / Grounding | **ADD RESULT** |

> The values above should be replaced with the actual metrics produced during Phase 2.6. No evaluation values are fabricated in this README.

---

# Screenshots

Screenshots of the running application should be added to the repository.

Recommended structure:

```text
docs/
└── screenshots/
    ├── frontend.png
    └── backend-swagger.png
```

## Frontend

Add a screenshot showing the Streamlit RAG Assistant interface.

```markdown
![RAG Assistant Frontend](docs/screenshots/frontend.png)
```

## Backend

Add a screenshot showing the FastAPI Swagger documentation.

```markdown
![FastAPI Swagger](docs/screenshots/backend-swagger.png)
```

---

# Demo Workflow

The complete application workflow is:

```text
User
 │
 ▼
Streamlit Frontend
 │
 ▼
FastAPI Backend
 │
 ▼
Query Embedding
 │
 ▼
ChromaDB Retrieval
 │
 ▼
Relevant Contract Context
 │
 ▼
Qwen 2.5 7B via Ollama
 │
 ▼
Grounded Answer
 │
 ▼
Streamlit Frontend
```

---

# Testing

Backend tests can be executed using:

```cmd
cd backend
pytest
```

The test suite covers the backend query functionality.

---

# Docker

The backend includes a Dockerfile.

Build the backend image:

```bash
docker build -t rag-assistant-backend ./backend
```

Run the container:

```bash
docker run -p 8000:8000 rag-assistant-backend
```

For a complete RAG deployment, the application also requires access to the vector store and Ollama model.

---

# GitHub and Version Control

The project uses Git for version control.

The repository excludes:

* Python virtual environments.
* Environment files containing secrets.
* Logs.
* Raw CUAD PDF corpus.
* Raw CUAD TXT corpus.
* CUAD label-group files.
* Large dataset files.
* Large vector stores.
* Generated temporary files.

This keeps the repository lightweight while allowing another developer to reproduce the dataset locally using the documented Hugging Face download command.

---

# Limitations

* The application currently depends on a locally running Ollama instance.
* The raw CUAD contract corpus is not included in the repository.
* Large vector stores are not committed to GitHub.
* Retrieval quality depends on document chunking and embedding quality.
* Generation quality depends on the retrieved context and language model.
* Legal answers should be verified against the original contract.
* This project is an educational/research system and does not provide professional legal advice.

---

# Future Improvements

Possible future improvements include:

* Hybrid keyword and semantic retrieval.
* Cross-encoder reranking.
* Improved document chunking.
* Better page-level citation handling.
* More advanced RAG evaluation.
* Hallucination detection.
* Query rewriting.
* Multi-document comparison.
* User authentication.
* Cloud deployment.
* Support for additional legal document formats.
* Improved legal clause classification.
* Production monitoring and logging.

---

# Project Status

The project currently includes:

* [x] CUAD dataset integration
* [x] Document processing
* [x] Semantic embeddings
* [x] ChromaDB vector retrieval
* [x] Local LLM generation
* [x] RAG pipeline notebook
* [x] FastAPI backend
* [x] Streamlit frontend
* [x] Backend tests
* [x] Dockerfile
* [x] GitHub repository
* [ ] Final Phase 2.6 evaluation values
* [ ] Final project screenshots

---

# Repository

GitHub:

https://github.com/Moda2511/rag-assistant-app

---

# License and Dataset Usage

This project is intended for educational and portfolio purposes.

The CUAD dataset is a third-party dataset. Users should review and comply with the dataset's original license, terms of use, and attribution requirements when downloading and using it.

The project code and the CUAD dataset are separate components and may be subject to different licensing terms.
