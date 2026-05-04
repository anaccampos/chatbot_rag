# Chatbot RAG

Assistente conversacional baseado em **RAG (Retrieval-Augmented Generation)** desenvolvido como projeto de pós-graduação (UFG). Em vez de responder apenas com base no treinamento geral do modelo, o sistema busca informações em um documento PDF enviado pelo usuário e formula respostas fundamentadas nesse conteúdo.

> Projeto desenvolvido com auxílio do **GitHub Copilot** (modelo Claude Sonnet 4.6).

---

## Como funciona

```
Upload PDF → Extração de texto → Chunking → Embeddings → pgvector
                                                              ↓
Pergunta → Busca semântica (top-k chunks) → Contexto → Ollama → Resposta
```

1. Usuário faz upload de um PDF pela interface Streamlit
2. O texto é extraído e dividido em chunks de ~500 tokens
3. Cada chunk é transformado em um vetor de embeddings (768 dimensões)
4. Os vetores são armazenados no PostgreSQL com a extensão pgvector
5. Ao receber uma pergunta, o sistema busca os chunks mais similares por distância cosseno
6. Os chunks relevantes são enviados como contexto ao modelo de linguagem local (Ollama)
7. O modelo gera uma resposta baseada exclusivamente no conteúdo do documento
8. A conversa (pergunta + resposta) é salva via API Node.js

---

## Tecnologias

| Camada | Tecnologia | Versão |
|---|---|---|
| API CRUD | Node.js, TypeScript, Express, Prisma, Multer | Node 20+ / TS 5+ |
| RAG | Python, LangChain, LangChain-Ollama | Python 3.11+ |
| Interface | Streamlit | 1.45+ |
| Banco de dados | PostgreSQL + pgvector | PostgreSQL 17 / pgvector 0.8 |
| LLM (respostas) | Ollama — llama3.2 | local, gratuito |
| Embeddings | Ollama — nomic-embed-text | local, gratuito, 768 dim |
| Testes (API) | Jest + ts-jest | 29+ |
| Testes (Python) | pytest + pytest-mock | 8+ |

### Modelo de IA

O projeto utiliza modelos **100% locais e gratuitos** via [Ollama](https://ollama.com), sem necessidade de chaves de API externas:

- **llama3.2** — modelo de linguagem para geração de respostas (~2GB)
- **nomic-embed-text** — modelo de embeddings para busca semântica (~274MB)

### Assistente de código

Este projeto foi desenvolvido com o auxílio do **GitHub Copilot** como assistente de programação, utilizando o modelo **Claude** (Anthropic). O Copilot auxiliou no planejamento da arquitetura, geração de código, resolução de problemas de configuração e criação dos testes unitários.

---

## Estrutura do projeto

```
chatbot_rag/
├── api/                              # Node.js/TypeScript — API CRUD
│   ├── src/
│   │   ├── controllers/
│   │   │   ├── document.controller.ts    # Lógica de documentos
│   │   │   └── conversation.controller.ts# Lógica de conversas
│   │   ├── routes/
│   │   │   ├── document.routes.ts        # GET/POST/PATCH/DELETE /api/documents
│   │   │   └── conversation.routes.ts    # GET/POST/DELETE /api/conversations
│   │   ├── middlewares/
│   │   │   └── upload.middleware.ts      # Multer (aceita PDF, máx 20MB)
│   │   ├── app.ts                        # Express + CORS + rotas
│   │   └── server.ts                     # Inicialização do servidor
│   ├── prisma/
│   │   ├── schema.prisma                 # Modelos Document e Conversation
│   │   └── migrations/                   # Migrations (inclui pgvector SQL raw)
│   ├── src/__tests__/                    # Testes Jest (16 testes)
│   ├── uploads/                          # PDFs enviados (ignorado pelo git)
│   ├── package.json
│   └── tsconfig.json
│
├── rag/                              # Python — RAG + Interface
│   ├── app.py                            # Streamlit UI (upload + chat)
│   ├── pdf_processor.py                  # Extração de texto + chunking
│   ├── vector_store.py                   # Embeddings + operações pgvector
│   ├── rag_chain.py                      # Pipeline LangChain + Ollama
│   ├── tests/                            # Testes pytest (13 testes)
│   │   ├── conftest.py
│   │   ├── test_pdf_processor.py
│   │   ├── test_vector_store.py
│   │   └── test_rag_chain.py
│   └── requirements.txt
│
├── .env                              # Variáveis de ambiente (não commitado)
├── .gitignore
└── README.md
```

### Banco de dados

| Tabela | Gerenciada por | Descrição |
|---|---|---|
| `documents` | Prisma (Node.js) | Metadata dos PDFs enviados |
| `conversations` | Prisma (Node.js) | Histórico de perguntas e respostas |
| `document_chunks` | SQL raw + Python | Chunks de texto com embeddings vetoriais (vector(768)) |

---

## Pré-requisitos

- [Node.js 20+](https://nodejs.org)
- [Python 3.11+](https://python.org)
- [Homebrew](https://brew.sh) (macOS)
- [Ollama](https://ollama.com)

---

## Instalação

### 1. Clone o repositório

```bash
git clone https://github.com/anaccampos/chatbot_rag.git
cd chatbot_rag
```

### 2. Variáveis de ambiente

Crie o arquivo `.env` na raiz do projeto:

```env
DATABASE_URL="postgresql://<seu-usuario>@localhost:5432/chatbot_rag"
PORT=3000
API_BASE_URL="http://localhost:3000"
OLLAMA_BASE_URL="http://localhost:11434"
OLLAMA_MODEL="llama3.2"
OLLAMA_EMBED_MODEL="nomic-embed-text"
```

> Substitua `<seu-usuario>` pelo seu usuário do sistema (`whoami`).

### 3. PostgreSQL + pgvector

```bash
brew install postgresql@17 pgvector
brew services start postgresql@17

# Adicione ao PATH (ou inclua no ~/.zshrc)
export PATH="/opt/homebrew/opt/postgresql@17/bin:$PATH"

# Crie o banco e habilite a extensão
psql -U $USER -d postgres -c "CREATE DATABASE chatbot_rag;"
psql -U $USER -d chatbot_rag -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

### 4. Ollama + modelos

```bash
brew install ollama
ollama serve  # manter este terminal aberto

# Em outro terminal — baixar os modelos (pode demorar, ~2.3GB no total)
ollama pull llama3.2
ollama pull nomic-embed-text
```

### 5. Dependências + banco de dados

Com o arquivo `.env` criado, rode o setup completo com um único comando:

```bash
make setup
```

Esse comando instala as dependências da API e do Python e executa as migrations do Prisma. Para ver todos os comandos disponíveis:

```bash
make help
```

<details>
<summary>Instalação manual (sem Make)</summary>

```bash
# API Node.js
cd api && cp ../.env .env && npm install && npx prisma migrate dev

# Python — RAG + Interface
cd rag && python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
```

</details>

---

## Rodando o projeto

Abra **3 terminais** e execute um comando em cada:

```bash
# Terminal 1 — Ollama
ollama serve

# Terminal 2 — API Node.js
make dev-api

# Terminal 3 — Interface Streamlit
make dev-rag
```

Acesse a interface em **http://localhost:8501**

---

## Exemplos de uso

### Upload e consulta via interface

1. Acesse `http://localhost:8501`
2. Na barra lateral, clique em **"Enviar PDF"** e selecione um arquivo
3. Clique em **"Processar documento"** e aguarde a indexação
4. No campo de chat, faça perguntas sobre o conteúdo do documento

**Exemplos de perguntas:**
```
"Qual é o tema principal do documento?"
"Quais são as conclusões do autor?"
"O que é dito sobre o capítulo 3?"
"Resuma os principais pontos abordados."
```

### Consulta direta à API REST

```bash
# Listar todos os documentos
curl http://localhost:3000/api/documents

# Listar conversas de um documento específico
curl "http://localhost:3000/api/conversations?documentId=<id>"

# Deletar um documento (remove também chunks e conversas em cascata)
curl -X DELETE http://localhost:3000/api/documents/<id>
```

---

## Testes

```bash
make test        # todos os testes (API + RAG)
make test-api    # Jest — API Node.js (16 testes)
make test-rag    # pytest — RAG Python (13 testes)
```

---

## Próximos passos

Melhorias planejadas para versões futuras:

- [ ] **Exibir trechos-fonte** — mostrar na interface quais partes do PDF embasaram cada resposta
- [ ] **Suporte a múltiplos formatos** — aceitar `.txt` e `.docx` além de PDF
- [ ] **Memória conversacional** — manter o contexto das últimas N perguntas na mesma sessão
- [ ] **Autenticação** — login com JWT para múltiplos usuários com documentos isolados
- [ ] **Deploy com Docker** — `docker-compose.yml` para subir todos os serviços com um único comando
- [ ] **Indicador de confiança** — exibir o score de similaridade junto com cada resposta
- [ ] **Múltiplos documentos simultâneos** — permitir perguntas que cruzem informações de diferentes PDFs
- [ ] **Modelos alternativos** — suporte a OpenAI GPT-4o e Google Gemini além do Ollama
- [ ] **Troca de modelo via interface** — selecionar o modelo LLM diretamente pela UI do Streamlit

---

## Licença

Distribuído sob a licença MIT. Consulte o arquivo [LICENSE](LICENSE) para mais detalhes.
