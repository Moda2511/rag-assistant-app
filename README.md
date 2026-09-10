# RAG Contract Assistant

A Retrieval-Augmented Generation (RAG) application for intelligent question answering over legal contracts.

The system allows users to ask questions about commercial contracts and receive grounded answers based on the retrieved contract content.

The project combines semantic search, vector databases, local LLM inference, a FastAPI backend, and a Streamlit frontend.

---

## Overview

This project implements an end-to-end RAG pipeline for legal contract analysis.

Instead of asking an LLM to answer questions using only its internal knowledge, the system:

1. Loads legal contract documents.
2. Extracts text from the documents.
3. Splits the text into manageable chunks.
4. Converts chunks into vector embeddings.
5. Stores the embeddings in ChromaDB.
6. Retrieves the most relevant chunks for a user's question.
7. Sends the retrieved context to a local LLM.
8. Generates a grounded answer based on the retrieved contract content.
9. Displays the answer through a Streamlit web interface.

The application is designed for educational and research purposes and should not be considered a substitute for professional legal advice.

---

## Architecture

```text
                    ┌──────────────────────┐
                    │      User            │
                    │  Legal Question      │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │  Streamlit Frontend  │
                    │      Port 8501       │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │    FastAPI Backend   │
                    │      Port 8000       │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │      Retriever       │
                    │    ChromaDB Search   │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ Relevant Contract    │
                    │      Chunks           │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │   Ollama + Qwen      │
                    │      2.5 7B           │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ Grounded Answer      │
                    │ + Source Information │
                    └──────────────────────┘
```

---

## RAG Pipeline

```text
Contract PDFs
     │
     ▼
PDF Text Extraction
     │
     ▼
Text Cleaning
     │
     ▼
Chunking
     │
     ▼
Embeddings
(all-MiniLM-L6-v2)
     │
     ▼
ChromaDB
Vector Store
     │
     │
     │ User Question
     ▼
Semantic Retrieval
     │
     ▼
Relevant Context
     │
     ▼
Qwen 2.5 7B
via Ollama
     │
     ▼
Grounded Answer
```

---

## Tech Stack

### Programming

* Python 3.13
* Jupyter Notebook

### Data Processing

* Pandas
* NumPy
* PyPDF

### RAG / Vector Search

* ChromaDB
* Sentence Transformers
* `all-MiniLM-L6-v2`

### LLM

* Ollama
* Qwen 2.5 7B

### Backend

* FastAPI
* Uvicorn

### Frontend

* Streamlit

### Version Control

* Git
* GitHub

---

## Dataset

This project uses the **CUAD — Contract Understanding Atticus Dataset**.

CUAD is a dataset containing commercial legal contracts annotated for contract review tasks.

The dataset includes contracts and annotations covering multiple contract clause categories.

Examples include:

* Governing Law
* Confidentiality
* Termination
* Assignment
* Change of Control
* Indemnification
* Limitation of Liability
* Non-Compete
* Renewal
* Effective Date
* Payment Terms

The dataset is used to build a legal-domain RAG system capable of retrieving relevant contract information and answering questions about it.

---

## Dataset Download

The CUAD dataset was downloaded from Hugging Face using:

```bash
hf download theatticusproject/cuad --repo-type dataset --local-dir data/CUAD
```

The raw contract corpus is intentionally excluded from GitHub because of its size and repository management considerations.

To reproduce the project, download the dataset using the command above.

---

## Embedding Model

The project uses:

```text
sentence-transformers/all-MiniLM-L6-v2
```

The model converts contract chunks and user questions into numerical vector representations.

These vectors are stored in ChromaDB and used for semantic similarity search.

---

## Project Structure

```text
rag-assistant-project/
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── ...
│   │
│   ├── requirements.txt
│   └── ...
│
├── frontend/
│   ├── app.py
│   └── api_client.py
│
├── data/
│   └── CUAD/
│       └── CUAD_v1/
│           ├── master_clauses.csv
│           ├── master_clauses.xlsx
│           └── ...
│
├── notebooks/
│   └── ...
│
├── chroma_db/
│   └── ...
│
├── .gitignore
├── README.md
└── ...
```

> Note: Large raw datasets and generated vector stores are excluded from GitHub through `.gitignore`.

---

# Installation

## 1. Clone the Repository

```bash
git clone https://github.com/Moda2511/rag-assistant-app.git
```

Then:

```bash
cd rag-assistant-app
```

---

## 2. Create a Virtual Environment

Windows:

```cmd
python -m venv .venv
```

Activate it:

```cmd
.venv\Scripts\activate
```

---

## 3. Install Dependencies

Install the backend requirements:

```cmd
pip install -r backend\requirements.txt
```

If additional notebook dependencies are required:

```cmd
pip install pandas numpy chromadb sentence-transformers pypdf ollama python-dotenv
```

---

# Ollama Setup

Install Ollama on your machine.

Verify the installation:

```cmd
ollama version
```

Pull the required model:

```cmd
ollama pull qwen2.5:7b
```

Verify that the model is available:

```cmd
ollama list
```

The project uses Ollama for local LLM inference.

---

# Environment Variables

Create a `.env` file in the project root if your implementation requires environment configuration.

Example:

```env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:7b
CHROMA_PATH=chroma_db
```

| Variable          | Description             | Example                  |
| ----------------- | ----------------------- | ------------------------ |
| `OLLAMA_BASE_URL` | Ollama server URL       | `http://localhost:11434` |
| `OLLAMA_MODEL`    | LLM used for generation | `qwen2.5:7b`             |
| `CHROMA_PATH`     | ChromaDB storage path   | `chroma_db`              |

Do not commit `.env` to GitHub.

---

# Preparing the Dataset

Download CUAD:

```bash
hf download theatticusproject/cuad --repo-type dataset --local-dir data/CUAD
```

The raw PDF and TXT corpus is intentionally ignored by Git.

After downloading the dataset, follow the project notebook/pipeline to:

1. Load the contracts.
2. Extract the text.
3. Clean the text.
4. Split documents into chunks.
5. Generate embeddings.
6. Store the embeddings in ChromaDB.

---

# Running the Backend

Open a terminal.

Navigate to the project:

```cmd
cd C:\Users\Lenovo\rag-assistant-project
```

Activate the environment:

```cmd
.venv\Scripts\activate
```

Go to the backend:

```cmd
cd backend
```

Start FastAPI:

```cmd
uvicorn app.main:app --reload
```

The backend will normally be available at:

```text
http://127.0.0.1:8000
```

---

## FastAPI Documentation

FastAPI automatically provides interactive API documentation.

Open:

```text
http://127.0.0.1:8000/docs
```

You can use Swagger UI to test the available API endpoints.

---

## Health Check

The health endpoint can be accessed at:

```text
http://127.0.0.1:8000/health
```

Example response:

```json
{
  "status": "ok"
}
```

---

# Running the Frontend

Keep the backend running.

Open a second terminal.

Navigate to the project:

```cmd
cd C:\Users\Lenovo\rag-assistant-project
```

Activate the environment:

```cmd
.venv\Scripts\activate
```

Run Streamlit:

```cmd
streamlit run frontend/app.py
```

The frontend will normally be available at:

```text
http://localhost:8501
```

Open the address in your browser.

---

# API Reference

The backend exposes an API for querying the RAG system.

The exact endpoints are documented automatically through FastAPI Swagger UI:

```text
http://127.0.0.1:8000/docs
```

---

## Example API Request

Example using `curl`:

```bash
curl -X POST "http://127.0.0.1:8000/query" ^
  -H "Content-Type: application/json" ^
  -d "{\"question\":\"What is the governing law of this agreement?\"}"
```

Depending on the backend implementation, the request body may contain additional parameters such as:

* `question`
* `top_k`
* document or contract identifiers

Use the Swagger documentation to confirm the currently available request schema.

---

# Example Questions

The system can answer questions such as:

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

### Assignment

```text
Does this agreement contain any restrictions on assignment?
Explain the relevant provision.
```

### Change of Control

```text
Does the agreement contain a change of control provision?
```

---

# Grounded Generation

The system is designed to reduce hallucinations by providing retrieved contract context to the LLM.

The generation process follows:

```text
User Question
      │
      ▼
Semantic Retrieval
      │
      ▼
Relevant Contract Chunks
      │
      ▼
Prompt + Retrieved Context
      │
      ▼
Qwen 2.5 7B
      │
      ▼
Grounded Answer
```

The LLM is instructed to base its response on the retrieved contract information rather than relying only on general knowledge.

---

# Why RAG?

Large Language Models can generate fluent answers, but they may not contain the specific information required to answer questions about private or specialized documents.

RAG addresses this by retrieving relevant information from a document collection before generating the answer.

For this project:

```text
Legal Contracts
      ↓
Vector Database
      ↓
Relevant Contract Sections
      ↓
LLM
      ↓
Contract-Specific Answer
```

This makes the system more suitable for document-based question answering.

---

# Testing

The project includes tests for the backend and/or RAG components depending on the current implementation.

Run available tests with:

```cmd
pytest
```

For more detailed output:

```cmd
pytest -v
```

---

# Docker

The project can also be containerized using Docker.

A typical project setup may contain:

```text
Dockerfile
```

The Docker configuration can be used to package the application and simplify deployment.

For local development, running the backend and frontend directly through the Python virtual environment is recommended.

---

# GitHub

The project is maintained using Git.

Initialize the repository:

```bash
git init
```

Add files:

```bash
git add .
```

Create a commit:

```bash
git commit -m "RAG assistant: notebook, FastAPI backend, frontend"
```

Connect the GitHub repository:

```bash
git remote add origin https://github.com/Moda2511/rag-assistant-app.git
```

Set the main branch:

```bash
git branch -M main
```

Push:

```bash
git push -u origin main
```

Repository:

https://github.com/Moda2511/rag-assistant-app

---

# .gitignore

The project excludes files that should not be committed to GitHub, including:

```text
.venv/
__pycache__/
.env
*.log
large CUAD raw corpus
vector stores
temporary files
model caches
```

The raw CUAD corpus can be downloaded again using the Hugging Face command described above.

---

# Limitations

This project is an educational RAG implementation and has several limitations.

### Legal Disclaimer

The generated answers should not be considered professional legal advice.

### Retrieval Quality

The quality of the final answer depends heavily on the quality of the retrieved chunks.

### Local LLM

The application relies on a locally running Ollama model, so response quality may vary depending on the selected model and available hardware.

### Dataset

The application is currently designed around the CUAD legal-contract domain.

### Large Corpus

The complete raw dataset is not stored in the GitHub repository.

---

# Future Improvements

Possible future improvements include:

* Hybrid search
* Reranking
* Better chunking strategies
* Metadata-aware retrieval
* Citation improvements
* Multi-document comparison
* Contract clause extraction
* Evaluation with automated RAG metrics
* Improved hallucination detection
* Authentication
* Cloud deployment
* Production database
* Larger or more capable LLMs
* Streaming responses
* Conversation memory

---

# Project Status

The project currently includes:

* [x] CUAD legal contract dataset
* [x] Document processing pipeline
* [x] Text chunking
* [x] Sentence Transformer embeddings
* [x] ChromaDB vector search
* [x] Local Ollama LLM
* [x] RAG question answering
* [x] FastAPI backend
* [x] Streamlit frontend
* [x] Git/GitHub integration
* [x] `.gitignore`
* [x] Project documentation

---

# Author

**Mahmoud Abd Elghani**

Computer Science & Artificial Intelligence Student

Damietta University, Egypt

GitHub:

https://github.com/Moda2511

LinkedIn:

https://www.linkedin.com/in/mahmoud-abdelghani-ghanem

---

# License and Dataset Usage

This project is intended for educational and research purposes.

The CUAD dataset is provided by The Atticus Project. Users should review and comply with the dataset's own license and usage terms when downloading or redistributing the data.

The raw dataset is not included in this repository.

---

# Acknowledgements

* The Atticus Project for CUAD
* Hugging Face for dataset hosting
* Sentence Transformers
* ChromaDB
* Ollama
* Qwen
* FastAPI
* Streamlit

---

## Repository

https://github.com/Moda2511/rag-assistant-app
