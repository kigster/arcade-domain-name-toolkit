# Makefile for Domain Monitor Toolkit
# Usage: make <target>

.PHONY: help install install-dev test test-verbose test-coverage clean lint format run run-simple setup check-env


# Default target
help: ## Show this help message
	@echo "Domain Monitor Toolkit - Available commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Installation targets
install: ## Install production dependencies
	pip install -r requirements.txt

install-dev: install ## Install development dependencies (includes testing tools)
	pip install -e ./domain_name_toolkit

setup: install-dev ## Complete setup - install deps and toolkit
	@echo "✅ Setup complete!"
	@echo "   - Production dependencies installed"
	@echo "   - Domain toolkit installed in development mode"
	@echo "   - Testing tools available"

# Testing targets
test: ## Run all tests
	@echo "🧪 Running unit tests..."
	cd domain_name_monitor && python -m pytest tests/ -v --tb=short

test-verbose: ## Run tests with verbose output
	@echo "🧪 Running tests with verbose output..."
	cd domain_name_monitor && python -m pytest tests/ -v --tb=long -s

test-coverage: ## Run tests with coverage report
	@echo "🧪 Running tests with coverage..."
	cd domain_name_monitor && python -m pytest tests/ -v --cov=domain_name_toolkit --cov=config_loader --cov=domain_monitor_app --cov-report=html --cov-report=term-missing

test-quick: ## Run tests without coverage (faster)
	@echo "🧪 Running quick tests..."
	cd domain_name_monitor && python -m pytest tests/ -x --tb=short

test-specific: ## Run specific test file (use TEST=filename)
	@echo "🧪 Running specific test: $(TEST)"
	cd domain_name_monitor && python -m pytest tests/test_$(TEST).py -v

# Code quality targets
lint: ## Run code linting
	@echo "🔍 Checking code style..."
	@if command -v ruff >/dev/null 2>&1; then \
		ruff check . ; \
	else \
		echo "⚠️  ruff not installed - install with: pip install ruff"; \
	fi

format: ## Format code
	@echo "🎨 Formatting code..."
	@if command -v ruff >/dev/null 2>&1; then \
		ruff format . ; \
	else \
		echo "⚠️  ruff not installed - install with: pip install ruff"; \
	fi

# Application targets
check-env: ## Check environment setup
	@echo "🔧 Checking environment..."
	@if [ -z "$$ARCADE_API_KEY" ]; then \
		echo "❌ ARCADE_API_KEY environment variable not set"; \
		echo "   Please set it in .env file or export it"; \
		exit 1; \
	else \
		echo "✅ ARCADE_API_KEY is set"; \
	fi
	@echo "✅ Environment check passed"

run: check-env ## Run the domain monitor with full Arcade integration
	@echo "🚀 Running domain monitor (full version)..."
	@cd domain_name_monitor && python domain_monitor_app.py && cd ..

run-simple: ## Run simple domain monitoring test (no Arcade required)
	@echo "🚀 Running simple domain monitoring test..."
	cd domain_name_monitor && python test_simple_monitoring.py

run-config: ## Test configuration loading
	@echo "🔧 Testing configuration loading..."
	cd domain_name_monitor && python config_loader.py

# Development targets
clean: ## Clean up generated files
	@echo "🧹 Cleaning up..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage
	rm -f domain_check_results.json
	rm -f simple_test_results.json
	rm -f test_results.json
	@echo "✅ Cleanup complete"

validate-config: ## Validate YAML configuration file
	@echo "🔧 Validating configuration..."
	@if [ -f "domain_name_monitor/domain_monitor_config.yaml" ]; then \
		cd domain_name_monitor && python -c "from config_loader import load_config; config = load_config('domain_monitor_config.yaml'); print(f'✅ Config valid: {len(config.domains)} domains configured')"; \
	else \
		echo "❌ domain_name_monitor/domain_monitor_config.yaml not found"; \
		exit 1; \
	fi

# Toolkit development targets
install-toolkit: ## Install the domain toolkit in development mode
	@echo "📦 Installing domain toolkit..."
	cd domain_name_toolkit && pip install -e .
	@echo "✅ Domain toolkit installed"

test-toolkit: ## Test toolkit functions directly
	@echo "🧪 Testing domain toolkit functions..."
	python test_domain_toolkit.py

deploy-toolkit: ## Deploy toolkit to Arcade Cloud (requires authentication)
	@echo "🚀 Deploying toolkit to Arcade Cloud..."
	cd domain_name_toolkit && arcade deploy

# Docker targets (if you want to add Docker support later)
docker-build: ## Build Docker image
	@echo "🐳 Building Docker image..."
	docker build -t domain-monitor .

docker-run: ## Run in Docker container
	@echo "🐳 Running in Docker..."
	docker run --env-file .env domain-monitor

# CI/CD targets
ci-test: install-dev test lint ## Run CI tests (install, test, lint)
	@echo "✅ All CI checks passed"

# Development workflow
dev: install-dev validate-config test-quick ## Quick development setup and test
	@echo "🎯 Development environment ready!"
	@echo ""
	@echo "Quick commands:"
	@echo "  make test          - Run all tests"
	@echo "  make run-simple    - Test without Arcade"
	@echo "  make run           - Full monitoring run"
	@echo "  make lint          - Check code style"

# Information targets
info: ## Show project information
	@echo "📋 Domain Monitor Toolkit Information"
	@echo "======================================"
	@echo ""
	@echo "🏗️  Project Structure:"
	@echo "   domain_name_toolkit/     - Custom Arcade toolkit"
	@echo "   domain_monitor_app.py    - Main monitoring application"
	@echo "   config_loader.py         - YAML configuration loader"
	@echo "   domain_monitor_config.yaml - Configuration file"
	@echo "   tests/                   - Unit tests"
	@echo ""
	@echo "🔧 Key Commands:"
	@echo "   make setup         - Initial setup"
	@echo "   make test          - Run tests"
	@echo "   make run           - Run monitoring"
	@echo ""
	@echo "📁 Files in current directory:"
	@ls -la | grep -E '\.(py|yaml|md|txt)$$' | awk '{print "   " $$9}'

# Show current status
status: ## Show current project status
	@echo "📊 Project Status"
	@echo "================="
	@echo ""
	@echo "📦 Dependencies:"
	@if pip list | grep -q "arcade-ai"; then echo "   ✅ arcade-ai installed"; else echo "   ❌ arcade-ai not installed"; fi
	@if pip list | grep -q "pytest"; then echo "   ✅ pytest installed"; else echo "   ❌ pytest not installed"; fi
	@if pip list | grep -q "pyyaml"; then echo "   ✅ pyyaml installed"; else echo "   ❌ pyyaml not installed"; fi
	@echo ""
	@echo "🔧 Configuration:"
	@if [ -f "domain_name_monitor/domain_monitor_config.yaml" ]; then echo "   ✅ Configuration file exists"; else echo "   ❌ Configuration file missing"; fi
	@if [ -f ".env" ]; then echo "   ✅ Environment file exists"; else echo "   ❌ Environment file missing"; fi
	@echo ""
	@echo "🧪 Tests:"
	@if [ -d "domain_name_monitor/tests" ]; then echo "   ✅ Test directory exists ($(ls domain_name_monitor/tests/*.py 2>/dev/null | wc -l | tr -d ' ') test files)"; else echo "   ❌ Test directory missing"; fi
	@echo ""
	@echo "📁 Generated Files:"
	@if [ -f "domain_check_results.json" ]; then echo "   📄 domain_check_results.json ($(stat -f%z domain_check_results.json 2>/dev/null || stat -c%s domain_check_results.json 2>/dev/null || echo "unknown") bytes)"; fi
	@if [ -f "simple_test_results.json" ]; then echo "   📄 simple_test_results.json"; fi
	@if [ -d "htmlcov" ]; then echo "   📁 htmlcov/ (coverage report)"; fi
