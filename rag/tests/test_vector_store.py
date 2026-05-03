from unittest.mock import MagicMock, patch, call
import vector_store


def _make_mock_conn():
    """Cria uma conexão psycopg2 mock com suporte a context manager."""
    mock_cursor = MagicMock()
    mock_conn = MagicMock()
    # conn.cursor() retorna context manager cujo __enter__ devolve mock_cursor
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mock_conn.cursor.return_value.__exit__.return_value = False
    return mock_conn, mock_cursor


def test_save_chunks_retorna_quantidade_de_chunks():
    mock_conn, _ = _make_mock_conn()
    chunks = ["chunk 1", "chunk 2", "chunk 3"]
    fake_vectors = [[0.1] * 768] * 3

    mock_embeddings = MagicMock()
    mock_embeddings.embed_documents.return_value = fake_vectors

    with patch.object(vector_store, "_embeddings", mock_embeddings), \
         patch("psycopg2.connect", return_value=mock_conn):
        result = vector_store.save_chunks("doc-123", chunks)

    assert result == 3
    mock_embeddings.embed_documents.assert_called_once_with(chunks)


def test_save_chunks_insere_todos_os_chunks_no_banco():
    mock_conn, mock_cursor = _make_mock_conn()
    chunks = ["a", "b"]
    fake_vectors = [[0.1] * 768, [0.2] * 768]

    mock_embeddings = MagicMock()
    mock_embeddings.embed_documents.return_value = fake_vectors

    with patch.object(vector_store, "_embeddings", mock_embeddings), \
         patch("psycopg2.connect", return_value=mock_conn):
        vector_store.save_chunks("doc-123", chunks)

    assert mock_cursor.execute.call_count == 2
    mock_conn.commit.assert_called_once()


def test_search_similar_chunks_retorna_conteudo_dos_chunks():
    mock_conn, mock_cursor = _make_mock_conn()
    mock_cursor.fetchall.return_value = [("chunk relevante",), ("outro chunk",)]

    mock_embeddings = MagicMock()
    mock_embeddings.embed_query.return_value = [0.1] * 768

    with patch.object(vector_store, "_embeddings", mock_embeddings), \
         patch("psycopg2.connect", return_value=mock_conn):
        results = vector_store.search_similar_chunks("doc-123", "minha pergunta")

    assert results == ["chunk relevante", "outro chunk"]
    mock_embeddings.embed_query.assert_called_once_with("minha pergunta")


def test_search_similar_chunks_usa_top_k():
    mock_conn, mock_cursor = _make_mock_conn()
    mock_cursor.fetchall.return_value = [("c1",), ("c2",)]

    mock_embeddings = MagicMock()
    mock_embeddings.embed_query.return_value = [0.0] * 768

    with patch.object(vector_store, "_embeddings", mock_embeddings), \
         patch("psycopg2.connect", return_value=mock_conn):
        vector_store.search_similar_chunks("doc-123", "pergunta", top_k=2)

    # Verifica que o LIMIT correto foi passado na query
    call_args = mock_cursor.execute.call_args
    assert 2 in call_args[0][1]  # top_k=2 deve estar nos parâmetros


def test_delete_chunks_executa_delete_no_banco():
    mock_conn, mock_cursor = _make_mock_conn()

    with patch("psycopg2.connect", return_value=mock_conn):
        vector_store.delete_chunks("doc-123")

    mock_cursor.execute.assert_called_once()
    call_sql = mock_cursor.execute.call_args[0][0]
    assert "DELETE" in call_sql.upper()
    mock_conn.commit.assert_called_once()
