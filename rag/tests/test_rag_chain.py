from unittest.mock import MagicMock, patch
import rag_chain


def test_answer_retorna_mensagem_quando_nao_ha_chunks():
    with patch("rag_chain.search_similar_chunks", return_value=[]):
        result = rag_chain.answer("doc-123", "Qual é o tema?")

    assert "não encontrei" in result.lower()


def test_answer_chama_llm_com_contexto_e_pergunta():
    chunks = ["Trecho A sobre o assunto.", "Trecho B com mais detalhes."]
    mock_chain = MagicMock()
    mock_chain.invoke.return_value = "Resposta gerada."

    with patch("rag_chain.search_similar_chunks", return_value=chunks), \
         patch.object(rag_chain, "_chain", mock_chain):
        result = rag_chain.answer("doc-123", "O que diz o documento?")

    assert result == "Resposta gerada."

    call_kwargs = mock_chain.invoke.call_args[0][0]
    assert call_kwargs["question"] == "O que diz o documento?"
    assert "Trecho A sobre o assunto." in call_kwargs["context"]
    assert "Trecho B com mais detalhes." in call_kwargs["context"]


def test_answer_remove_espacos_da_resposta():
    mock_chain = MagicMock()
    mock_chain.invoke.return_value = "  Resposta com espaços.  \n"

    with patch("rag_chain.search_similar_chunks", return_value=["chunk"]), \
         patch.object(rag_chain, "_chain", mock_chain):
        result = rag_chain.answer("doc-123", "Pergunta?")

    assert result == "Resposta com espaços."


def test_answer_separa_chunks_com_divisor():
    chunks = ["Parte 1", "Parte 2", "Parte 3"]
    mock_chain = MagicMock()
    mock_chain.invoke.return_value = "ok"

    with patch("rag_chain.search_similar_chunks", return_value=chunks), \
         patch.object(rag_chain, "_chain", mock_chain):
        rag_chain.answer("doc-123", "Pergunta?")

    context = mock_chain.invoke.call_args[0][0]["context"]
    assert "---" in context
    assert "Parte 1" in context
    assert "Parte 3" in context
