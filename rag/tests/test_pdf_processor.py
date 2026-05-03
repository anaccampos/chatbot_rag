from unittest.mock import MagicMock, patch
from pdf_processor import extract_chunks


def _make_mock_reader(pages_text: list[str]):
    """Cria um PdfReader mock com páginas de texto definidas."""
    mock_pages = []
    for text in pages_text:
        page = MagicMock()
        page.extract_text.return_value = text
        mock_pages.append(page)

    mock_reader = MagicMock()
    mock_reader.pages = mock_pages
    return mock_reader


def test_extract_chunks_retorna_lista_de_strings():
    texto = "Este é um parágrafo sobre inteligência artificial. " * 20
    mock_reader = _make_mock_reader([texto])

    with patch("pdf_processor.PdfReader", return_value=mock_reader):
        chunks = extract_chunks("/fake/path.pdf")

    assert isinstance(chunks, list)
    assert len(chunks) > 0
    assert all(isinstance(c, str) for c in chunks)


def test_extract_chunks_divide_em_multiplos_chunks():
    # Texto longo o suficiente para gerar mais de 1 chunk (chunk_size=500)
    texto = "Palavra " * 300  # ~2400 caracteres
    mock_reader = _make_mock_reader([texto])

    with patch("pdf_processor.PdfReader", return_value=mock_reader):
        chunks = extract_chunks("/fake/path.pdf")

    assert len(chunks) > 1


def test_extract_chunks_ignora_paginas_sem_texto():
    mock_reader = _make_mock_reader(["Texto válido na página 1.", None, "Texto na página 3."])

    with patch("pdf_processor.PdfReader", return_value=mock_reader):
        chunks = extract_chunks("/fake/path.pdf")

    # Deve processar apenas as páginas com texto
    assert len(chunks) > 0
    full = " ".join(chunks)
    assert "Texto válido na página 1." in full


def test_extract_chunks_pdf_vazio_retorna_lista_vazia():
    mock_reader = _make_mock_reader([None, None])

    with patch("pdf_processor.PdfReader", return_value=mock_reader):
        chunks = extract_chunks("/fake/path.pdf")

    assert chunks == []
