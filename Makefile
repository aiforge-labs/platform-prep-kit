.PHONY: install install-all test lint serve clean help

# Default Python — override with: make install PYTHON=python3.12
PYTHON ?= python3

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install core + dev dependencies
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -e ".[dev]"

install-all: ## Install all extras (ui, pdf, web, dashboard, dev)
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -e ".[all,ui,dashboard,dev]"

test: ## Run test suite
	$(PYTHON) -m pytest tests/ -v --tb=short

test-cov: ## Run tests with coverage report
	$(PYTHON) -m pytest tests/ -v --cov=prep_agent --cov-report=term-missing

lint: ## Check for syntax errors and common issues
	$(PYTHON) -m py_compile prep_agent/cli.py
	$(PYTHON) -m py_compile prep_agent/web/app.py
	$(PYTHON) -m py_compile prep_agent/web/database.py
	$(PYTHON) -m py_compile prep_agent/web/migrate.py
	@echo "All files compile OK"

serve: ## Start the web UI (localhost:8080)
	$(PYTHON) -m prep_agent.web.server

serve-dev: ## Start web UI with auto-reload
	$(PYTHON) -m uvicorn prep_agent.web.app:create_app --factory --host 127.0.0.1 --port 8080 --reload

clean: ## Remove build artifacts and caches
	rm -rf build/ dist/ *.egg-info .pytest_cache htmlcov .coverage
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

check-secrets: ## Scan for accidentally committed secrets
	@echo "Checking for common secret patterns..."
	@! grep -rn "sk-[a-zA-Z0-9]\{20,\}" prep_agent/ --include="*.py" || true
	@! grep -rn "AKIA[A-Z0-9]\{16\}" prep_agent/ --include="*.py" || true
	@! grep -rn "password\s*=" prep_agent/ --include="*.py" --include="*.yml" | grep -v "# " || true
	@echo "No secrets found."

init-dev: ## Full development setup from scratch
	$(PYTHON) -m venv .venv
	.venv/bin/pip install --upgrade pip
	.venv/bin/pip install -e ".[all,ui,dashboard,dev]"
	@echo ""
	@echo "Development environment ready."
	@echo "Activate with: source .venv/bin/activate"
	@echo "Run tests:     make test"
	@echo "Start web UI:  make serve"
