-- Habilita a extensão pgvector (idempotente)
CREATE EXTENSION IF NOT EXISTS vector;

-- Tabela de chunks com embeddings (gerenciada pelo Python/LangChain)
CREATE TABLE document_chunks (
  id           SERIAL PRIMARY KEY,
  document_id  TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
  content      TEXT NOT NULL,
  chunk_index  INT  NOT NULL,
  embedding    vector(384)
);

-- Índice para busca por similaridade (cosine distance)
CREATE INDEX document_chunks_embedding_idx
  ON document_chunks
  USING ivfflat (embedding vector_cosine_ops)
  WITH (lists = 100);
