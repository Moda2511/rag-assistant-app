from __future__ import annotations

import html

import streamlit as st

from api_client import (
    check_backend_health,
    query_contract,
)


# ============================================================
# HTML HELPERS
#
# ROOT CAUSE OF THE "RAW HTML VISIBLE AS TEXT" BUG:
#
# Python-Markdown (the library Streamlit uses under st.markdown)
# treats ANY line indented by 4 or more spaces as a preformatted
# code block, per the CommonMark/Markdown spec. This happens
# BEFORE `unsafe_allow_html` is even considered - that flag only
# controls whether *parsed* HTML is sanitized, it does not stop
# Markdown from deciding a block is "code" in the first place.
#
# The previous version of this file built HTML strings that were
# indented to match the surrounding Python code (8, 12, 16+
# spaces), e.g.:
#
#     st.markdown("""
#         <div class="hero-icon">
#             ...
#         </div>
#     """, unsafe_allow_html=True)
#
# Because every line inside that triple-quoted string starts with
# 8+ spaces, Markdown treated the whole block as a code block and
# rendered the tags literally as visible text instead of parsing
# them as HTML. Blank lines inside those blocks made this worse by
# splitting one HTML block into several fragments.
#
# THE FIX: every HTML string passed to st.markdown must have its
# tags start at column 0 (no leading whitespace) and must not
# contain blank lines in the middle of the block. The helpers
# below build compact, flush-left HTML strings so this can never
# regress, and they HTML-escape any dynamic values (backend
# health info, source text) so odd characters in that data can't
# break the layout or inject markup.
# ============================================================


def esc(value: object, default: str = "N/A") -> str:
    """HTML-escape a dynamic value for safe interpolation."""
    if value is None or value == "":
        return default
    return html.escape(str(value))


def render_status_card(rows: list[tuple[str, str]]) -> str:
    """Build a flush-left status card with label/value rows."""
    parts = ['<div class="status-card">']
    for i, (label, value) in enumerate(rows):
        if i > 0:
            parts.append("<br>")
        parts.append(f'<div class="status-label">{esc(label)}</div>')
        parts.append(f'<div class="status-value">{esc(value)}</div>')
    parts.append("</div>")
    return "".join(parts)


def render_source_card(source: object) -> str:
    """
    Build a flush-left source/citation card.

    Only ever displays information the backend actually returned.
    Supports both plain-string sources and dict-shaped sources
    (e.g. {"source": ..., "page": ..., "excerpt": ...}) without
    inventing any fields that are not present.
    """
    if isinstance(source, dict):
        doc = source.get("source") or source.get("document") or source.get("filename")
        page = source.get("page") or source.get("page_number")
        excerpt = source.get("excerpt") or source.get("text") or source.get("content")

        lines = []
        if doc:
            lines.append(f'<div class="source-doc">📄 {esc(doc)}</div>')
        if page is not None:
            lines.append(f'<div class="source-page">Page {esc(page)}</div>')
        if excerpt:
            lines.append(f'<div class="source-excerpt">{esc(excerpt)}</div>')

        if not lines:
            # Dict shape we don't recognize - fall back to a safe
            # string representation rather than showing nothing.
            lines.append(f'<div class="source-excerpt">{esc(source)}</div>')

        return '<div class="source-card">' + "".join(lines) + "</div>"

    return f'<div class="source-card">{esc(source)}</div>'


def render_sources(sources: list) -> None:
    """Render the sources header + all source cards for a response."""
    st.markdown(
        '<div class="sources-header">📚 Sources</div>',
        unsafe_allow_html=True,
    )
    for source in sources:
        st.markdown(render_source_card(source), unsafe_allow_html=True)


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="CUAD Legal Contract Review Assistant",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

.stApp {
    background:
        radial-gradient(
            circle at top left,
            rgba(37, 99, 235, 0.06),
            transparent 35%
        ),
        #EAF4FF;
}

.main {
    padding-top: 1rem;
}

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

header[data-testid="stHeader"] {
    background: transparent;
}


/* ==========================================================
   HERO
   ========================================================== */

.hero {
    padding: 2.4rem 2.6rem;
    border-radius: 24px;
    background:
        linear-gradient(
            135deg,
            #173B63 0%,
            #1E4A7A 55%,
            #2563EB 100%
        );
    box-shadow:
        0 20px 50px rgba(23, 59, 99, 0.25);
    margin-bottom: 1.5rem;
    color: #FFFFFF;
    position: relative;
    overflow: hidden;
}

.hero::after {
    content: "";
    position: absolute;
    top: -60%;
    right: -10%;
    width: 320px;
    height: 320px;
    background: radial-gradient(circle, rgba(255, 255, 255, 0.18), transparent 70%);
    border-radius: 50%;
    pointer-events: none;
}

.hero-badge {
    display: inline-block;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #FFFFFF;
    background: rgba(255, 255, 255, 0.14);
    border: 1px solid rgba(255, 255, 255, 0.35);
    border-radius: 999px;
    padding: 0.3rem 0.75rem;
    margin-bottom: 0.9rem;
}

.hero-icon {
    font-size: 2.6rem;
    margin-bottom: 0.4rem;
}

.hero-title {
    font-size: 2.15rem;
    font-weight: 800;
    letter-spacing: -0.03em;
    margin-bottom: 0.4rem;
    color: #FFFFFF;
}

.hero-subtitle {
    font-size: 1rem;
    color: #DCEEFF;
    line-height: 1.65;
    max-width: 760px;
}


/* ==========================================================
   WELCOME CARD
   ========================================================== */

.welcome-card {
    background: #FFFFFF;
    border: 1px solid #C7DDF5;
    border-radius: 22px;
    padding: 2.6rem 2.4rem;
    text-align: center;
    box-shadow:
        0 10px 30px rgba(16, 42, 67, 0.06);
    margin: 1rem 0 1.5rem 0;
}

.welcome-icon {
    font-size: 3rem;
    margin-bottom: 0.7rem;
}

.welcome-title {
    font-size: 1.65rem;
    font-weight: 750;
    color: #173B63;
    margin-bottom: 0.6rem;
}

.welcome-text {
    color: #486581;
    font-size: 1rem;
    line-height: 1.7;
    max-width: 700px;
    margin: auto;
}


/* ==========================================================
   FEATURE CARDS
   ========================================================== */

.feature-card {
    background: #FFFFFF;
    border: 1px solid #C7DDF5;
    border-radius: 18px;
    padding: 1.3rem 1.2rem;
    height: 100%;
    box-shadow:
        0 8px 25px rgba(16, 42, 67, 0.04);
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.feature-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 14px 30px rgba(16, 42, 67, 0.08);
}

.feature-icon {
    font-size: 1.5rem;
    margin-bottom: 0.5rem;
}

.feature-title {
    font-weight: 700;
    color: #173B63;
    margin-bottom: 0.35rem;
}

.feature-text {
    color: #486581;
    font-size: 0.88rem;
    line-height: 1.55;
}


/* ==========================================================
   SOURCES
   ========================================================== */

.sources-header {
    color: #173B63;
    font-weight: 700;
    font-size: 0.92rem;
    margin-top: 0.9rem;
    margin-bottom: 0.5rem;
}

.source-card {
    background: #F4F9FF;
    border: 1px solid #C7DDF5;
    border-left: 4px solid #2563EB;
    border-radius: 12px;
    padding: 0.8rem 1rem;
    margin-bottom: 0.55rem;
    font-size: 0.85rem;
    color: #102A43;
    line-height: 1.55;
}

.source-doc {
    font-weight: 700;
    color: #173B63;
    margin-bottom: 0.15rem;
}

.source-page {
    font-size: 0.75rem;
    color: #486581;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.03em;
    margin-bottom: 0.3rem;
}

.source-excerpt {
    color: #102A43;
}


/* ==========================================================
   SIDEBAR
   ========================================================== */

section[data-testid="stSidebar"] {
    background: #E1F0FF;
    border-right: 1px solid #C7DDF5;
}

section[data-testid="stSidebar"] * {
    color: #102A43;
}

.sidebar-brand {
    padding: 0.5rem 0 1.2rem 0;
}

.sidebar-logo {
    font-size: 2rem;
    margin-bottom: 0.2rem;
}

.sidebar-title {
    font-size: 1.1rem;
    font-weight: 750;
    color: #173B63;
}

.sidebar-description {
    color: #486581;
    font-size: 0.82rem;
    line-height: 1.5;
    margin-top: 0.25rem;
}

section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] h4 {
    color: #173B63 !important;
}

section[data-testid="stSidebar"] hr {
    border-color: #C7DDF5;
}

section[data-testid="stSidebar"] input {
    background: #FFFFFF !important;
    color: #102A43 !important;
    border: 1px solid #C7DDF5 !important;
}

.status-card {
    background: #FFFFFF;
    border: 1px solid #C7DDF5;
    border-radius: 14px;
    padding: 0.9rem;
    margin-top: 0.5rem;
}

.status-label {
    font-size: 0.75rem;
    color: #486581;
    margin-bottom: 0.2rem;
}

.status-value {
    font-weight: 650;
    color: #102A43;
    word-break: break-word;
}


/* ==========================================================
   CHAT MESSAGES
   ========================================================== */

[data-testid="stChatMessage"] {
    border-radius: 18px;
    margin-bottom: 0.8rem;
    padding: 0.4rem 0.6rem;
    background: #FFFFFF;
    border: 1px solid #C7DDF5;
}

/* Assistant answer: white background, dark readable text */
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) {
    background: #FFFFFF;
    border: 1px solid #C7DDF5;
}

/* User message: light-blue background, dark readable text */
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
    background: #DCEEFF;
    border: 1px solid #C7DDF5;
}

/* Force readable dark text for every Markdown element inside a chat
   message, so an answer can never render as light-on-light text. */
[data-testid="stChatMessage"] p,
[data-testid="stChatMessage"] li,
[data-testid="stChatMessage"] span,
[data-testid="stChatMessage"] div,
[data-testid="stChatMessage"] strong,
[data-testid="stChatMessage"] em,
[data-testid="stChatMessage"] label {
    color: #102A43 !important;
}

[data-testid="stChatMessage"] h1,
[data-testid="stChatMessage"] h2,
[data-testid="stChatMessage"] h3,
[data-testid="stChatMessage"] h4 {
    color: #173B63 !important;
}

[data-testid="stChatMessage"] a {
    color: #2563EB !important;
}

[data-testid="stChatMessage"] code {
    background: #F4F9FF;
    color: #102A43 !important;
    padding: 0.15rem 0.4rem;
    border-radius: 4px;
    font-size: 0.9em;
}

[data-testid="stChatMessage"] pre {
    background: #F4F9FF;
    border: 1px solid #C7DDF5;
    border-radius: 8px;
    padding: 0.8rem;
}

[data-testid="stChatMessage"] pre code {
    background: transparent;
    color: #102A43 !important;
    padding: 0;
}


/* ==========================================================
   BUTTONS
   ========================================================== */

.stButton > button {
    border-radius: 10px;
    font-weight: 600;
    border: 1px solid #173B63;
    background: #173B63;
    color: #FFFFFF;
    transition: background 0.15s ease, border-color 0.15s ease;
}

.stButton > button:hover {
    background: #2563EB;
    border-color: #2563EB;
    color: #FFFFFF;
}

.stButton > button:active {
    background: #1E4A7A;
    border-color: #1E4A7A;
    color: #FFFFFF;
}

.stButton > button p {
    color: #FFFFFF !important;
}


/* ==========================================================
   CHAT INPUT
   Fixes the "text hard/impossible to see" issue: Streamlit
   nests the actual <textarea> inside a BaseWeb wrapper div, and
   both layers need the background + text color set explicitly
   or the browser/theme default (often white-on-white or
   white-on-light) can win.
   ========================================================== */

[data-testid="stChatInput"] {
    border-radius: 16px;
    border: 1px solid #A9CBEF !important;
    background: #DCEEFF !important;
}

[data-testid="stChatInput"] > div {
    background: #DCEEFF !important;
}

[data-testid="stChatInput"] div[data-baseweb="textarea"] {
    background: #DCEEFF !important;
    border-color: #A9CBEF !important;
}

[data-testid="stChatInput"] textarea,
[data-testid="stChatInput"] input {
    background: #DCEEFF !important;
    color: #102A43 !important;
    caret-color: #102A43 !important;
    -webkit-text-fill-color: #102A43 !important;
}

[data-testid="stChatInput"] textarea::placeholder,
[data-testid="stChatInput"] input::placeholder {
    color: #486581 !important;
    opacity: 1 !important;
    -webkit-text-fill-color: #486581 !important;
}

[data-testid="stChatInput"] button {
    color: #173B63 !important;
}

[data-testid="stChatInput"] svg {
    fill: #173B63 !important;
}


/* ==========================================================
   DIVIDER
   ========================================================== */

.soft-divider {
    height: 1px;
    background: #C7DDF5;
    margin: 1rem 0;
}

.suggestion-line {
    text-align: center;
    color: #486581;
    font-size: 0.9rem;
    margin-bottom: 1rem;
}


/* ==========================================================
   FOOTER
   ========================================================== */

.app-footer {
    text-align: center;
    color: #486581;
    font-size: 0.75rem;
    padding: 2rem 0 1rem 0;
}

</style>


""",
    unsafe_allow_html=True,
)


# ============================================================
# SESSION STATE
# ============================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "document_id" not in st.session_state:
    st.session_state.document_id = "CUAD_000460"

if "previous_document_id" not in st.session_state:
    st.session_state.previous_document_id = (
        st.session_state.document_id
    )

if "check_health" not in st.session_state:
    st.session_state.check_health = True


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        '<div class="sidebar-brand">'
        '<div class="sidebar-logo">⚖️</div>'
        '<div class="sidebar-title">CUAD Contract AI</div>'
        '<div class="sidebar-description">Intelligent contract analysis '
        'powered by Retrieval-Augmented Generation.</div>'
        "</div>",
        unsafe_allow_html=True,
    )

    st.markdown("---")

    st.markdown("### 📄 Contract")

    document_id = st.text_input(
        "Document ID",
        value=st.session_state.document_id,
        placeholder="CUAD_000460",
        help="Enter the CUAD document ID you want to analyze.",
    ).strip()

    if document_id != st.session_state.previous_document_id:

        st.session_state.document_id = document_id
        st.session_state.previous_document_id = document_id
        st.session_state.messages = []

        st.rerun()

    st.session_state.document_id = document_id

    st.markdown("---")

    st.markdown("### 🔌 System Status")

    if st.button(
        "Check Backend",
        use_container_width=True,
    ):
        st.session_state.check_health = True

    if st.session_state.check_health:

        try:

            health = check_backend_health()

            if health.get("status") == "ok":

                st.success(
                    "Backend Connected",
                    icon="🟢",
                )

                st.markdown(
                    render_status_card(
                        [
                            ("Collection", health.get("collection")),
                            ("Embedding Model", health.get("embedding_model")),
                            ("Embedding Dimension", health.get("embedding_dim")),
                            ("LLM", health.get("ollama_model")),
                        ]
                    ),
                    unsafe_allow_html=True,
                )

            else:

                st.warning(
                    "Backend is running in degraded mode.",
                    icon="🟡",
                )

        except RuntimeError:

            st.error(
                "Backend Unavailable",
                icon="🔴",
            )

            st.caption(
                "Make sure the FastAPI backend is running "
                "on port 8000."
            )

        except Exception as exc:

            st.error(
                "Could not check backend.",
                icon="⚠️",
            )

            st.caption(str(exc))

    st.markdown("---")

    st.markdown("### 🧠 AI Configuration")

    st.markdown(
        render_status_card(
            [
                ("Language Model", "Qwen 2.5 — 7B"),
                ("Embeddings", "all-MiniLM-L6-v2"),
                ("Retrieval", "ChromaDB"),
            ]
        ),
        unsafe_allow_html=True,
    )

    st.markdown("---")

    if st.button(
        "🗑️ Clear Conversation",
        use_container_width=True,
    ):
        st.session_state.messages = []
        st.rerun()


# ============================================================
# MAIN HERO
# ============================================================

st.markdown(
    '<div class="hero">'
    '<div class="hero-badge">CUAD · Contract Understanding AI</div>'
    '<div class="hero-icon">⚖️</div>'
    '<div class="hero-title">CUAD Legal Contract Review Assistant</div>'
    '<div class="hero-subtitle">Ask intelligent questions about commercial '
    "contracts and receive grounded answers supported by the original "
    "contract context and source citations.</div>"
    "</div>",
    unsafe_allow_html=True,
)


# ============================================================
# EMPTY STATE
# ============================================================

if not st.session_state.messages:

    st.markdown(
        '<div class="welcome-card">'
        '<div class="welcome-icon">⚖️</div>'
        '<div class="welcome-title">Contract Intelligence, Simplified</div>'
        '<div class="welcome-text">Select a CUAD contract using its document ID, '
        "then ask questions about its clauses, obligations, terms, and "
        "conditions. The AI answers using retrieved contract context and "
        "provides citations for transparency.</div>"
        "</div>",
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.markdown(
            '<div class="feature-card">'
            '<div class="feature-icon">🔎</div>'
            '<div class="feature-title">Grounded Retrieval</div>'
            '<div class="feature-text">Relevant contract sections are '
            "retrieved from the selected document before generating an "
            "answer.</div>"
            "</div>",
            unsafe_allow_html=True,
        )

    with col2:

        st.markdown(
            '<div class="feature-card">'
            '<div class="feature-icon">🤖</div>'
            '<div class="feature-title">AI Analysis</div>'
            '<div class="feature-text">Qwen 2.5 7B generates answers based '
            "on the retrieved contract context.</div>"
            "</div>",
            unsafe_allow_html=True,
        )

    with col3:

        st.markdown(
            '<div class="feature-card">'
            '<div class="feature-icon">📚</div>'
            '<div class="feature-title">Source Citations</div>'
            '<div class="feature-text">Every response includes the source '
            "chunks and page information returned by the backend.</div>"
            "</div>",
            unsafe_allow_html=True,
        )

    st.markdown(
        '<div class="soft-divider"></div>'
        '<div class="suggestion-line">Try asking: '
        "<strong>What is the governing law of the agreement?</strong></div>",
        unsafe_allow_html=True,
    )


# ============================================================
# DISPLAY CHAT HISTORY
# ============================================================

for message in st.session_state.messages:

    role = message["role"]

    with st.chat_message(
        role,
        avatar="👤" if role == "user" else "⚖️",
    ):

        st.markdown(message["content"])

        if role == "assistant":

            sources = message.get(
                "sources",
                [],
            )

            if sources:
                render_sources(sources)


# ============================================================
# CHAT INPUT
# ============================================================

question = st.chat_input(
    "Ask a question about the selected contract..."
)


if question:

    question = question.strip()

    if not question:

        st.warning(
            "Please enter a question."
        )

        st.stop()

    if not st.session_state.document_id:

        st.warning(
            "Please enter a Document ID before asking a question."
        )

        st.stop()


    # --------------------------------------------------------
    # USER MESSAGE
    # --------------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "user",
            "content": question,
        }
    )

    with st.chat_message(
        "user",
        avatar="👤",
    ):

        st.markdown(question)


    # --------------------------------------------------------
    # ASSISTANT RESPONSE
    # --------------------------------------------------------

    with st.chat_message(
        "assistant",
        avatar="⚖️",
    ):

        with st.spinner(
            "Searching the contract and generating an answer..."
        ):

            try:

                result = query_contract(
                    question=question,
                    document_id=st.session_state.document_id,
                )

                answer = result.get(
                    "answer",
                    "",
                )

                sources = result.get(
                    "sources",
                    [],
                )

                if not answer:

                    answer = (
                        "The backend returned an empty answer."
                    )

                st.markdown(answer)

                if sources:
                    render_sources(sources)
                else:

                    st.caption(
                        "No source information was returned."
                    )

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": answer,
                        "sources": sources,
                    }
                )

            except ValueError as exc:

                st.error(
                    str(exc),
                    icon="⚠️",
                )

            except RuntimeError as exc:

                st.error(
                    str(exc),
                    icon="🔴",
                )

            except Exception as exc:

                st.error(
                    "Something went wrong while processing "
                    "your question. Please try again.",
                    icon="⚠️",
                )

                st.caption(str(exc))


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    '<div class="app-footer">CUAD Legal Contract Review Assistant '
    "· RAG-powered contract intelligence</div>",
    unsafe_allow_html=True,
)
