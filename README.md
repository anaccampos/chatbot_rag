# Chatbot RAG

Assistente conversacional baseado em **RAG (Retrieval-Augmented Generation)**. Permite fazer upload de documentos PDF e realizar perguntas sobre o conteúdo, com respostas geradas por um modelo de linguagem local.

## Como funciona

1. Usuário faz upload de um PDF pela interface
2. O sistema extrai o texto, divide em chunks e gera embeddings
3. Os embeddings são armazenados no banco vetorial (pgvector)
4. Ao receber uma pergunta, o sistema busca os trechos mais relevantes e os envia como contexto ao modelo de linguagem
5. O modelo gera uma resposta baseada no conteúdo do documento

## Tecnologias

| Camada | Tecnologia |
|---|---|
| API CRUD | Node.js 20+, TypeScript, Express, Prisma |
| RAG + UI | Python 3.11+, LangChain, Streamlit |
| Banco de dados | PostgreSQL 17 + pgvector |
| Modelo de linguagem | Ollama (llama3.2) — local, gratuito |
| Embeddings | Ollama (nomic-embed-text) — local, gratuito |

## Pré-requisitos

- [Node.js 20+](https://nodejs.org)
- [Python 3.11+](https://python.org)
- [Homebrew](https://brew.sh) (macOS)
- [Ollama](https://ollama.com)

## Instalação

### 1. Clone o repositório

```bash
git clone <url-do-repositorio>
cd chatbot_rag
```

### 2. PostgreSQL + pgvector

```bash
brew install postgresql@17 pgvector
brew services start postgresql@17

# Adicione ao PATH (ou inclua no ~/.zshrc)
export PATH="/opt/homebrew/opt/postgresql@17/bin:$PATH"

# Crie o banco
psql -U $USER -d postgres -c "CREATE DATABASE chatbot_rag;"
psql -U $USER -d chatbot_rag -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

### 3. Variáveis de ambiente

Copie o `.env` de exemplo e ajuste se necessário:

```bash
cp .env .env.local
```

Conteúdo padrão do `.env`:

```env
DATABASE_URL="postgresql://<seu-usuario>@localhost:5432/chatbot_rag"
PORT=3000
API_BASE_URL="http://localhost:3000"
OLLAMA_BASE_URL="http://localhost:11434"
OLLAMA_MODEL="llama3.2"
OLLAMA_EMBED_MODEL="nomic-embed-text"
```

### 4. API Node.js

```bash
cd api
cp ../.env .env
npm install
npx prisma migrate dev
```

### 5. Python (RAG + UI)

```bash
cd rag
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 6. Ollama + modelos

```bash
# Instalar Ollama
brew install ollama

# Iniciar o serviço
ollama serve

# Em outro terminal, baixar os modelos
ollama pull llama3.2
ollama pull nomic-embed-text
```

## Rodando o projeto

Em terminais separados:

```bash
# Terminal 1 — API Node.js
cd api && npm run dev

# Terminal 2 — Interface Streamlit
cd rag && source .venv/bin/activate && streamlit run app.py
```

Acesse a interface em `http://localhost:8501`
