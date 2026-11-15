
"""Retrieval-Augmented Generation pipeline for FlameBound."""

import httpx

from ai.retrieval.search import semantic_search


OLLAMA_URL = "http://localhost:11434/api/chat"
GENERATION_MODEL = "llama3.2"


SYSTEM_PROMPT = """
You are FlameBound, a scientific research assistant specializing
in solid-fuel combustion and fire behaviour under microgravity.

Your task is to answer questions using ONLY the experimental
evidence and research passages supplied to you.

Follow these rules strictly:

1. Base factual claims on the supplied evidence.
2. Do not invent experimental results, measurements, or findings.
3. Distinguish documented findings from your own interpretation.
4. If the evidence is insufficient, explicitly acknowledge it.
5. Cite supporting passages using their source filename and page.
6. Do not present general scientific knowledge as though it
   were a finding from the supplied NASA documents.
7. Be precise, scientific, and concise.

Use citations in this format:
[Source: filename, Page: number]
"""


def generate_answer(question, retrieved_chunks):
    """Generate an evidence-grounded answer using Ollama."""

    if not retrieved_chunks:
        return (
            "Insufficient evidence: no relevant research passages "
            "were retrieved for this question."
        )

    evidence = []

    for index, chunk in enumerate(retrieved_chunks, start=1):
        metadata = chunk["metadata"]

        evidence.append(
            f"""
EVIDENCE {index}
Source: {metadata['source']}
Page: {metadata['page']}
Similarity: {chunk['similarity']:.4f}

Content:
{chunk['text']}
"""
        )

    context = "\n".join(evidence)

    user_prompt = f"""
SCIENTIFIC QUESTION:
{question}

RETRIEVED RESEARCH EVIDENCE:
{context}

Answer the scientific question using the supplied evidence.
Include source citations for the claims you make.
If the evidence does not adequately answer the question,
state its limitations instead of guessing.
"""

    response = httpx.post(
        OLLAMA_URL,
        json={
            "model": GENERATION_MODEL,
            "messages": [
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
            "stream": False,
            "options": {
                "temperature": 0.1,
            },
        },
        timeout=180.0,
    )

    response.raise_for_status()

    data = response.json()

    return data["message"]["content"]


def answer_question(question, embedded_chunks, top_k=3):
    """
    Retrieve relevant research and generate an evidence-grounded answer.

    Returns the answer, supporting sources, and retrieved passages.
    """

    if not isinstance(question, str) or not question.strip():
        raise ValueError("Question must be a non-empty string")

    retrieved_chunks = semantic_search(
        question,
        embedded_chunks,
        top_k=top_k,
    )

    answer = generate_answer(
        question,
        retrieved_chunks,
    )

    sources = []

    for chunk in retrieved_chunks:
        metadata = chunk["metadata"]

        source = {
            "source": metadata["source"],
            "page": metadata["page"],
            "similarity": chunk["similarity"],
        }

        if source not in sources:
            sources.append(source)

    return {
        "question": question,
        "answer": answer,
        "sources": sources,
        "retrieved_chunks": retrieved_chunks,
    }
