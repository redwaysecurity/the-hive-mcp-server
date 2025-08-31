.PHONY: run run-sse run-stdio build publish lint format test install help docker-build docker-run docker-clean lint-comprehensive lint-fix lint-black lint-isort lint-flake8 lint-mypy lint-pylint

# Python environment detection
VENV_PYTHON = .venv/bin/python
SYSTEM_PYTHON = python3

# Use venv python if available, otherwise system python
PYTHON = $(if $(wildcard $(VENV_PYTHON)),$(VENV_PYTHON),$(SYSTEM_PYTHON))

# Check if uv is available
UV_AVAILABLE = $(shell which uv 2>/dev/null)
ifeq ($(UV_AVAILABLE),)
    UV_CMD = $(PYTHON) -m uv
else
    UV_CMD = uv
endif

# Docker configuration
DOCKER_IMAGE = thehive-mcp-server
DOCKER_TAG = latest
DOCKER_FULL_NAME = $(DOCKER_IMAGE):$(DOCKER_TAG)

PARAMS=

# Help target
help:
	@echo "Available targets:"
	@echo "  run          - Run MCP server with stdio transport"
	@echo "  run-sse      - Run MCP server with SSE transport"
	@echo "  run-stdio    - Run MCP server with stdio transport (alias for run)"
	@echo "  install      - Install dependencies"
	@echo "  build        - Build the package"
	@echo "  publish      - Publish to PyPI"
	@echo "  lint         - Run linting with ruff (quick)"
	@echo "  lint-comprehensive - Run comprehensive linting (black, isort, flake8, mypy, pylint)"
	@echo "  lint-fix     - Run comprehensive linting with auto-fix"
	@echo "  lint-black   - Run black code formatting check"
	@echo "  lint-isort   - Run isort import sorting check"
	@echo "  lint-flake8  - Run flake8 style checking"
	@echo "  lint-mypy    - Run mypy type checking"
	@echo "  lint-pylint  - Run pylint code analysis"
	@echo "  format       - Format code with ruff"
	@echo "  test         - Run tests"
	@echo "  docker-build - Build Docker image"
	@echo "  docker-run   - Run Docker container"
	@echo "  docker-clean - Clean Docker images"

# Install dependencies
install:
	@if [ -f "$(VENV_PYTHON)" ]; then \
		echo "Using virtual environment..."; \
		$(VENV_PYTHON) -m pip install -e ".[dev]"; \
	else \
		echo "Creating virtual environment..."; \
		python3 -m venv .venv; \
		$(VENV_PYTHON) -m pip install --upgrade pip; \
		$(VENV_PYTHON) -m pip install -e ".[dev]"; \
	fi

# Run with stdio transport (default for MCP)
run:
	@echo "Starting TheHive MCP Server with stdio transport..."
	$(PYTHON) -m thehive_mcp --transport stdio $(PARAMS)

run-stdio:
	@echo "Starting TheHive MCP Server with stdio transport..."
	$(PYTHON) -m thehive_mcp --transport stdio $(PARAMS)

# Run with SSE transport
run-sse:
	@echo "Starting TheHive MCP Server with SSE transport..."
	$(PYTHON) -m thehive_mcp --transport sse $(PARAMS)

# Test the server
test:
	$(PYTHON) -m pytest tests/ -v

# Build package
build:
	@if [ -n "$(UV_AVAILABLE)" ]; then \
		$(UV_CMD) build; \
	else \
		$(PYTHON) -m build; \
	fi

# Publish package
publish:
	@if [ -n "$(UV_AVAILABLE)" ]; then \
		$(UV_CMD) publish; \
	else \
		$(PYTHON) -m twine upload dist/*; \
	fi

# Lint code
lint:
	$(PYTHON) -m ruff check . --fix

# Comprehensive linting with multiple tools
lint-comprehensive:
	@echo "🔍 Running comprehensive linting..."
	$(PYTHON) dev-tools/lint.py

# Comprehensive linting with auto-fix
lint-fix:
	@echo "🔧 Running comprehensive linting with auto-fix..."
	$(PYTHON) dev-tools/lint.py --fix

# Individual linting tools
lint-black:
	@echo "🔍 Running black formatting check..."
	$(PYTHON) dev-tools/lint.py --tool black

lint-isort:
	@echo "🔍 Running isort import sorting check..."
	$(PYTHON) dev-tools/lint.py --tool isort

lint-flake8:
	@echo "🔍 Running flake8 style checking..."
	$(PYTHON) dev-tools/lint.py --tool flake8

lint-mypy:
	@echo "🔍 Running mypy type checking..."
	$(PYTHON) dev-tools/lint.py --tool mypy

lint-pylint:
	@echo "🔍 Running pylint code analysis..."
	$(PYTHON) dev-tools/lint.py --tool pylint

# Format code
format:
	$(PYTHON) -m ruff format .

# Docker targets
docker-build:
	@echo "Building Docker image $(DOCKER_FULL_NAME)..."
	docker build -t $(DOCKER_FULL_NAME) .
	@echo "✅ Docker image built successfully"

docker-run: docker-build
	@echo "Running Docker container..."
	docker run --rm -it \
		--env HIVE_URL=${HIVE_URL:-http://host.docker.internal:9000} \
		--env HIVE_API_KEY=${HIVE_API_KEY:-your-api-key-here} \
		-p 8000:8000 \
		$(DOCKER_FULL_NAME)

docker-run-stdio: docker-build
	@echo "Running Docker container with stdio transport..."
	docker run --rm -i \
		--env HIVE_URL=${HIVE_URL:-http://host.docker.internal:9000} \
		--env HIVE_API_KEY=${HIVE_API_KEY:-your-api-key-here} \
		$(DOCKER_FULL_NAME) \
		python -m thehive_mcp --transport stdio

docker-clean:
	@echo "Cleaning Docker images..."
	docker rmi $(DOCKER_FULL_NAME) 2>/dev/null || true
	docker system prune -f
	@echo "✅ Docker cleanup complete"