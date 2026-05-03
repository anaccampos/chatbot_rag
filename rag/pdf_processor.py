from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter


def extract_chunks(filepath: str) -> list[str]:
    reader = PdfReader(filepath)

    full_text = ""
    for page in reader.pages:
        text = page.extract_text()
        if text:
            full_text += text + "\n"

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n\n", "\n", ".", " ", ""],
    )

    chunks = splitter.split_text(full_text)
    return chunks
