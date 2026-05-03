import os
from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv
from vector_store import search_similar_chunks

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../.env"))

_llm = OllamaLLM(
    model=os.getenv("OLLAMA_MODEL", "llama3.2"),
    base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
    temperature=0.2,
)

_prompt = PromptTemplate(
    input_variables=["context", "question"],
    template="""Você é um assistente que responde perguntas com base exclusivamente no conteúdo fornecido abaixo.
Se a resposta não estiver no conteúdo, diga que não encontrou a informação no documento.

Conteúdo do documento:
{context}

Pergunta: {question}

Resposta:""",
)

_chain = _prompt | _llm


def answer(document_id: str, question: str) -> str:
    chunks = search_similar_chunks(document_id, question)

    if not chunks:
        return "Não encontrei trechos relevantes no documento para responder essa pergunta."

    context = "\n\n---\n\n".join(chunks)
    response = _chain.invoke({"context": context, "question": question})
    return response.strip()
