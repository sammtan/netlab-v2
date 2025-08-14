# NetLab Universal Parametric Cyber Range Builder
# Makefile for development and operations

.PHONY: help dev.setup dev.test images.build test itest.minilab clean

# Default target
help: ## Show this help message
	@echo "NetLab - Universal Parametric Cyber Range Builder"
	@echo "================================================="
	@echo
	@echo "Available targets:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# Development Environment Setup
dev.setup: ## Set up isolated development environment (IDEV)
	@echo "🔧 Setting up NetLab isolated development environment..."
	@if command -v docker >/dev/null 2>&1; then \
		echo "✅ Docker found, building development container..."; \
		docker build -f docker/Dockerfile.dev -t netlab-dev .; \
		docker run --rm -v $(PWD):/workspace netlab-dev python -m pip install -e .; \
	else \
		echo "⚠️  Docker not found, setting up local Python environment..."; \
		python3 -m venv venv; \
		. venv/bin/activate && pip install -r requirements-dev.txt; \
		. venv/bin/activate && pip install -e .; \
	fi
	@echo "✅ Development environment ready!"

dev.test: ## Run unit and integration tests in IDEV
	@echo "🧪 Running tests in isolated development environment..."
	@if command -v docker >/dev/null 2>&1; then \
		docker run --rm -v $(PWD):/workspace netlab-dev pytest tests/; \
	else \
		. venv/bin/activate && pytest tests/; \
	fi

images.build: ## Build base VM images with Packer
	@echo "📦 Building base VM images..."
	@if [ -d "packer/" ]; then \
		cd packer && packer build -parallel-builds=2 base-images.pkr.hcl; \
	else \
		echo "⚠️  Packer directory not found, skipping image build"; \
	fi

# Testing
test: ## Run unit tests
	@echo "🧪 Running unit tests..."
	python -m pytest tests/unit/ -v

itest.minilab: ## Run integration test with mini lab
	@echo "🔬 Running integration test with mini lab..."
	python -m pytest tests/integration/ -v --mini-lab

# Host Environment
host.check: ## Check host capabilities for NetLab deployment
	@echo "🔍 Checking host capabilities..."
	@python scripts/host_detect.py --json

sources.sync: ## Download and verify device base images
	@echo "📥 Syncing device source images..."
	@python scripts/download.py --manifest manifests/sources.yaml --verify

# Lab Operations (requires uvdnl to be installed)
lab.plan: ## Plan a lab deployment (usage: make lab.plan LAB=examples/small-office.yaml)
	@if [ -z "$(LAB)" ]; then \
		echo "❌ Please specify LAB file: make lab.plan LAB=examples/small-office.yaml"; \
		exit 1; \
	fi
	@uvdnl plan $(LAB)

lab.up: ## Deploy a lab (usage: make lab.up LAB=examples/small-office.yaml)
	@if [ -z "$(LAB)" ]; then \
		echo "❌ Please specify LAB file: make lab.up LAB=examples/small-office.yaml"; \
		exit 1; \
	fi
	@uvdnl lab up $(LAB)

lab.down: ## Destroy a lab (usage: make lab.down LAB=examples/small-office.yaml)
	@if [ -z "$(LAB)" ]; then \
		echo "❌ Please specify LAB file: make lab.down LAB=examples/small-office.yaml"; \
		exit 1; \
	fi
	@uvdnl lab down $(LAB)

# Development utilities
lint: ## Run code linting
	@echo "🔍 Running code linting..."
	@python -m flake8 cli/ core/ scripts/
	@python -m black --check cli/ core/ scripts/
	@python -m mypy cli/ core/ scripts/

format: ## Format code
	@echo "🎨 Formatting code..."
	@python -m black cli/ core/ scripts/
	@python -m isort cli/ core/ scripts/

# Documentation
docs.build: ## Build documentation
	@echo "📚 Building documentation..."
	@if command -v sphinx-build >/dev/null 2>&1; then \
		sphinx-build -b html docs/ docs/_build/html/; \
	else \
		echo "⚠️  Sphinx not installed, skipping documentation build"; \
	fi

docs.serve: ## Serve documentation locally
	@echo "🌐 Serving documentation at http://localhost:8000..."
	@cd docs/_build/html && python -m http.server 8000

# Cleanup
clean: ## Clean up generated files and caches
	@echo "🧹 Cleaning up..."
	@rm -rf build/ dist/ *.egg-info/
	@rm -rf .pytest_cache/ __pycache__/ */__pycache__/
	@rm -rf images/cache/.partial/
	@find . -name "*.pyc" -delete
	@find . -name "*.pyo" -delete

clean.all: clean ## Clean everything including downloaded images
	@echo "🧹 Deep cleaning (including images)..."
	@rm -rf images/cache/*
	@rm -rf images/base/*
	@rm -rf venv/

# Package and distribution
build: ## Build distribution packages
	@echo "📦 Building distribution packages..."
	@python -m build

install: ## Install NetLab locally
	@echo "📦 Installing NetLab..."
	@pip install -e .

# Development workflow helpers
dev.workflow: ## Show common development workflow
	@echo "🔄 Common NetLab Development Workflow:"
	@echo "======================================"
	@echo "1. make dev.setup          # Set up development environment"
	@echo "2. make host.check         # Verify your host can run NetLab"
	@echo "3. make sources.sync       # Download base device images"
	@echo "4. make test              # Run unit tests"
	@echo "5. make lab.plan LAB=examples/small-office.yaml"
	@echo "6. make lab.up LAB=examples/small-office.yaml"
	@echo "7. make lab.down LAB=examples/small-office.yaml"

# Quick development cycle
dev.cycle: lint test ## Run quick development cycle (lint + test)
	@echo "✅ Development cycle complete!"

# CI/CD simulation
ci: lint test itest.minilab ## Run full CI pipeline
	@echo "✅ CI pipeline complete!"