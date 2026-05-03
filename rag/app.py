import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
import requests
import tempfile
from dotenv import load_dotenv

from pdf_processor import extract_chunks
from vector_store import save_chunks, delete_chunks
from rag_chain import answer

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../.env"))

API_BASE = os.getenv("API_BASE_URL", "http://localhost:3000")

st.set_page_config(page_title="Chatbot RAG", page_icon="📄", layout="wide")
st.title("📄 Chatbot RAG")
st.caption("Faça upload de um PDF e faça perguntas sobre o conteúdo.")

# --- Estado da sessão ---
if "document_id" not in st.session_state:
    st.session_state.document_id = None
if "document_name" not in st.session_state:
    st.session_state.document_name = None
if "messages" not in st.session_state:
    st.session_state.messages = []


# --- Sidebar: upload e seleção de documento ---
with st.sidebar:
    st.header("Documento")

    uploaded = st.file_uploader("Enviar PDF", type=["pdf"])

    if uploaded and st.button("Processar documento"):
        with st.spinner("Enviando e processando..."):
            # 1. Salva o arquivo temporariamente para processar localmente
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(uploaded.getbuffer())
                tmp_path = tmp.name

            # 2. Registra na API Node.js
            files = {"file": (uploaded.name, open(tmp_path, "rb"), "application/pdf")}
            resp = requests.post(f"{API_BASE}/api/documents", files=files)

            if resp.status_code != 201:
                st.error(f"Erro ao registrar documento: {resp.text}")
            else:
                doc = resp.json()
                doc_id = doc["id"]

                # 3. Processa PDF e salva embeddings no pgvector
                chunks = extract_chunks(tmp_path)
                total = save_chunks(doc_id, chunks)

                # 4. Atualiza totalChunks na API
                requests.patch(
                    f"{API_BASE}/api/documents/{doc_id}",
                    json={"totalChunks": total},
                )

                st.session_state.document_id = doc_id
                st.session_state.document_name = uploaded.name
                st.session_state.messages = []

                os.unlink(tmp_path)
                st.success(f"Pronto! {total} chunks indexados.")

    st.divider()

    # Lista documentos existentes
    st.subheader("Documentos anteriores")
    docs_resp = requests.get(f"{API_BASE}/api/documents")
    if docs_resp.status_code == 200:
        docs = docs_resp.json()
        if docs:
            for doc in docs:
                col1, col2 = st.columns([4, 1])
                with col1:
                    if st.button(doc["filename"], key=f"sel_{doc['id']}"):
                        st.session_state.document_id = doc["id"]
                        st.session_state.document_name = doc["filename"]
                        st.session_state.messages = []
                        st.rerun()
                with col2:
                    if st.button("🗑", key=f"del_{doc['id']}"):
                        delete_chunks(doc["id"])
                        requests.delete(f"{API_BASE}/api/documents/{doc['id']}")
                        if st.session_state.document_id == doc["id"]:
                            st.session_state.document_id = None
                            st.session_state.document_name = None
                            st.session_state.messages = []
                        st.rerun()
        else:
            st.info("Nenhum documento ainda.")


# --- Área principal: chat ---
if not st.session_state.document_id:
    st.info("Envie um PDF na barra lateral para começar.")
else:
    st.subheader(f"Conversando sobre: **{st.session_state.document_name}**")

    # Exibe histórico de mensagens
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Input de pergunta
    question = st.chat_input("Faça uma pergunta sobre o documento...")

    if question:
        # Exibe pergunta
        st.session_state.messages.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)

        # Gera resposta
        with st.chat_message("assistant"):
            with st.spinner("Buscando no documento..."):
                response = answer(st.session_state.document_id, question)

            st.markdown(response)

        st.session_state.messages.append({"role": "assistant", "content": response})

        # Salva conversa na API
        requests.post(
            f"{API_BASE}/api/conversations",
            json={
                "documentId": st.session_state.document_id,
                "question": question,
                "answer": response,
            },
        )
