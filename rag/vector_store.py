import os
import psycopg2
from langchain_ollama import OllamaEmbeddings
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../.env"))

_embeddings = OllamaEmbeddings(
    model=os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text"),
    base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
)


def _get_conn():
    return psycopg2.connect(os.getenv("DATABASE_URL"))


def save_chunks(document_id: str, chunks: list[str]) -> int:
    vectors = _embeddings.embed_documents(chunks)

    conn = _get_conn()
    try:
        with conn.cursor() as cur:
            for i, (chunk, vector) in enumerate(zip(chunks, vectors)):
                cur.execute(
                    """
                    INSERT INTO document_chunks (document_id, content, chunk_index, embedding)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (document_id, chunk, i, vector),
                )
        conn.commit()
    finally:
        conn.close()

    return len(chunks)


def search_similar_chunks(document_id: str, question: str, top_k: int = 4) -> list[str]:
    vector = _embeddings.embed_query(question)

    conn = _get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT content
                FROM document_chunks
                WHERE document_id = %s
                ORDER BY embedding <=> %s::vector
                LIMIT %s
                """,
                (document_id, vector, top_k),
            )
            rows = cur.fetchall()
    finally:
        conn.close()

    return [row[0] for row in rows]


def delete_chunks(document_id: str) -> None:
    conn = _get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM document_chunks WHERE document_id = %s",
                (document_id,),
            )
        conn.commit()
    finally:
        conn.close()
