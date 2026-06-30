# VENV_DIR = .venv
# PYTHON_BIN = $(VENV_DIR)/Scripts/python.exe
# FLASK_BIN = $(VENV_DIR)/Scripts/flask.exe
# FLASK_APP = app.py

# .PHONY: help setup run clean-cache db-update

# help:
# 	@echo "Comandos disponiveis:"
# 	@echo "   make setup       - Cria a venv (se nao existir) e instala dependencias"
# 	@echo "   make run         - Inicia o servidor Flask usando a VENV (Modo Debug)"
# 	@echo "   make clean-cache - Limpa arquivos temporarios do Python"
# 	@echo "   make db-update   - Inicializa ou atualiza o banco de dados usando a VENV"

# setup:
# 	@if [ ! -d "$(VENV_DIR)" ]; then \
# 		echo "Criando ambiente virtual '$(VENV_DIR)'..."; \
# 		python -m venv $(VENV_DIR); \
# 	else \
# 		echo "Ambiente '$(VENV_DIR)' ja existe. Pulando criacao..."; \
# 	fi
# 	@echo "Atualizando o pip..."
# 	@$(PYTHON_BIN) -m pip install --upgrade pip
# 	@echo "Instalando dependencias do requirements.txt..."
# 	@$(PYTHON_BIN) -m pip install -r requirements.txt
# 	@echo "Tudo pronto!"

# run:
# 	@echo "Iniciando o servidor Flask..."
# 	$(PYTHON_BIN) -m flask --app $(FLASK_APP) run --debug

# clean:
# 	@echo "Limpando arquivos de cache..."
# 	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
# 	find . -type f -name "*.pyc" -delete 2>/dev/null || true
# 	@echo "Cache limpo!"

# db-update:
# 	@echo "Atualizando as tabelas do banco de dados..."
# 	$(PYTHON_BIN) -c "from models.character import CharacterModel; from models.mesa import MesaModel; CharacterModel.init_db(); MesaModel.init_db();"
# 	@echo "Banco de dados atualizado!"

VENV_DIR = .venv
PYTHON_BIN = $(VENV_DIR)/bin/python
FLASK_APP = app.py

.PHONY: help setup run clean db-update

help:
	@echo "Comandos disponíveis:"
	@echo "  make setup      - Cria a venv e instala dependências"
	@echo "  make run        - Inicia o servidor Flask em modo debug"
	@echo "  make clean      - Remove arquivos de cache do Python"
	@echo "  make db-update  - Inicializa ou atualiza o banco de dados"

setup:
	@if [ ! -d "$(VENV_DIR)" ]; then \
		echo "Criando ambiente virtual..."; \
		python3 -m venv $(VENV_DIR); \
	else \
		echo "Ambiente virtual já existe."; \
	fi
	@echo "Atualizando pip..."
	@$(PYTHON_BIN) -m pip install --upgrade pip
	@echo "Instalando dependências..."
	@$(PYTHON_BIN) -m pip install -r requirements.txt
	@echo "Setup concluído!"

run:
	@echo "Iniciando servidor Flask..."
	@$(PYTHON_BIN) -m flask --app $(FLASK_APP) run --debug

clean:
	@echo "Removendo caches..."
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -type f -name "*.pyc" -delete
	@echo "Limpeza concluída!"

db-update:
	@echo "Atualizando banco de dados..."
	@$(PYTHON_BIN) -c "from models.character import CharacterModel; from models.mesa import MesaModel; CharacterModel.init_db(); MesaModel.init_db();"
	@echo "Banco de dados atualizado!"