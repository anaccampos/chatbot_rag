-- Habilita a extensão pgvector (idempotente)
CREATE EXTENSION IF NOT EXISTS vector;

-- Tabela de chunks com embeddings (gerenciada pelo Python/LangChain)
-- nomic-embed-text gera vetores de 768 dimensões
CREATE TABLE document_chunks (
  id           SERIAL PRIMARY KEY,
  document_id  TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
  content      TEXT NOT NULL,
  chunk_index  INT  NOT NULL,
  embedding    vector(768)
);
