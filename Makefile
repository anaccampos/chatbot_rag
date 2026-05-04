.PHONY: install install-api install-rag migrate test test-api test-rag dev-api dev-rag setup help

# ── Instalação ──────────────────────────────────────────────────────────────

install: install-api install-rag ## Instala todas as dependências

install-api: ## Instala dependências da API Node.js
	cd api && npm install

install-rag: ## Instala dependências Python no virtualenv
	cd rag && python3 -m venv .venv && .venv/bin/pip install -r requirements.txt

# ── Banco de dados ───────────────────────────────────────────────────────────

migrate: ## Executa as migrations do Prisma
	cd api && npx prisma migrate dev

# ── Testes ───────────────────────────────────────────────────────────────────

test: test-api test-rag ## Roda todos os testes

test-api: ## Testes Jest (API Node.js)
	cd api && npm test

test-rag: ## Testes pytest (RAG Python)
	cd rag && .venv/bin/pytest tests/ -v

# ── Execução ─────────────────────────────────────────────────────────────────

dev-api: ## Inicia a API Node.js em modo desenvolvimento
	cd api && npm run dev

dev-rag: ## Inicia a interface Streamlit
	cd rag && .venv/bin/streamlit run app.py

# ── Setup completo (primeira vez) ────────────────────────────────────────────

setup: install migrate ## Instala dependências e executa migrations
	@echo ""
	@echo "Setup concluído. Para rodar o projeto, abra 3 terminais:"
	@echo "  Terminal 1: ollama serve"
	@echo "  Terminal 2: make dev-api"
	@echo "  Terminal 3: make dev-rag"

# ── Ajuda ────────────────────────────────────────────────────────────────────

help: ## Exibe esta mensagem de ajuda
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help
