# Makefile for Event-Driven Backtesting Engine Python Bindings

# Variables
PYTHON := python3
PIP := pip3
PYTEST := pytest
PROJECT_NAME := backtesting_engine

# Default target
.PHONY: all
all: clean install test

# Help target
.PHONY: help
help:
	@echo "Available targets:"
	@echo "  all          - Clean, install, and test"
	@echo "  install      - Install the package"
	@echo "  install-dev  - Install in development mode"
	@echo "  test         - Run all tests"
	@echo "  test-fast    - Run fast tests only"
	@echo "  benchmark    - Run benchmark tests"
	@echo "  clean        - Clean build artifacts"
	@echo "  deps         - Install dependencies"
	@echo "  examples     - Run example scripts"
	@echo "  lint         - Run code linting"
	@echo "  format       - Format code"
	@echo "  docs         - Build documentation"
	@echo "  wheel        - Build wheel distribution"
	@echo "  upload       - Upload to PyPI (test)"

# Installation targets
.PHONY: deps
deps:
	@echo "Installing dependencies..."
	$(PIP) install -r requirements.txt

.PHONY: install
install: deps
	@echo "Installing backtesting engine..."
	$(PIP) install .

.PHONY: install-dev
install-dev: deps
	@echo "Installing in development mode..."
	$(PIP) install -e .

# Testing targets
.PHONY: test
test:
	@echo "Running all tests..."
	$(PYTEST) tests/ -v --tb=short

.PHONY: test-fast
test-fast:
	@echo "Running fast tests..."
	$(PYTEST) tests/ -v -m "not slow and not benchmark"

.PHONY: test-integration
test-integration:
	@echo "Running integration tests..."
	$(PYTEST) tests/ -v -m "integration"

.PHONY: benchmark
benchmark:
	@echo "Running benchmark tests..."
	$(PYTEST) tests/ -v -m "benchmark" --benchmark-only

.PHONY: coverage
coverage:
	@echo "Running tests with coverage..."
	$(PYTEST) tests/ --cov=$(PROJECT_NAME) --cov-report=html --cov-report=term

# Code quality targets
.PHONY: lint
lint:
	@echo "Running linting..."
	flake8 examples/ tests/ --max-line-length=88 --exclude=build/
	@echo "Linting completed"

.PHONY: format
format:
	@echo "Formatting code..."
	black examples/ tests/ --line-length=88
	@echo "Formatting completed"

.PHONY: typecheck
typecheck:
	@echo "Running type checks..."
	mypy examples/ --ignore-missing-imports

# Example targets
.PHONY: examples
examples: install
	@echo "Running simple example..."
	$(PYTHON) examples/simple_backtest.py
	@echo "Running advanced example..."
	$(PYTHON) examples/advanced_example.py

.PHONY: example-simple
example-simple: install
	@echo "Running simple backtesting example..."
	$(PYTHON) examples/simple_backtest.py

.PHONY: example-advanced
example-advanced: install
	@echo "Running advanced backtesting example..."
	$(PYTHON) examples/advanced_example.py

# Build targets
.PHONY: wheel
wheel: clean
	@echo "Building wheel distribution..."
	$(PYTHON) setup.py bdist_wheel
	@echo "Wheel built in dist/"

.PHONY: sdist
sdist: clean
	@echo "Building source distribution..."
	$(PYTHON) setup.py sdist
	@echo "Source distribution built in dist/"

.PHONY: build
build: wheel sdist

# Documentation targets
.PHONY: docs
docs:
	@echo "Building documentation..."
	@if command -v sphinx-build >/dev/null 2>&1; then \
		sphinx-build -b html docs/ docs/_build/; \
		echo "Documentation built in docs/_build/"; \
	else \
		echo "Sphinx not installed. Install with: pip install sphinx sphinx-rtd-theme"; \
	fi

# Cleanup targets
.PHONY: clean
clean:
	@echo "Cleaning build artifacts..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf __pycache__/
	rm -rf tests/__pycache__/
	rm -rf examples/__pycache__/
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete
	find . -name "*~" -delete
	@echo "Clean completed"

.PHONY: clean-all
clean-all: clean
	@echo "Deep cleaning..."
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .mypy_cache/

# Development workflow targets
.PHONY: dev-setup
dev-setup:
	@echo "Setting up development environment..."
	$(PIP) install -r requirements.txt
	$(PIP) install -e .
	$(PIP) install pytest pytest-cov pytest-benchmark black flake8 mypy
	@echo "Development setup completed"

.PHONY: dev-test
dev-test: install-dev test-fast

.PHONY: ci
ci: clean deps install test lint
	@echo "CI pipeline completed successfully"

# Docker targets (optional)
.PHONY: docker-build
docker-build:
	@echo "Building Docker image..."
	docker build -t backtesting-engine-python .

.PHONY: docker-test
docker-test: docker-build
	@echo "Running tests in Docker..."
	docker run --rm backtesting-engine-python make test

# Profiling and debugging
.PHONY: profile
profile: install
	@echo "Running profiler on examples..."
	$(PYTHON) -m cProfile -s cumulative examples/simple_backtest.py

.PHONY: debug-test
debug-test:
	@echo "Running tests with debugging info..."
	$(PYTEST) tests/ -v -s --tb=long --capture=no

# Release targets
.PHONY: check-release
check-release: clean build
	@echo "Checking release build..."
	twine check dist/*

.PHONY: upload-test
upload-test: check-release
	@echo "Uploading to test PyPI..."
	twine upload --repository testpypi dist/*

.PHONY: upload
upload: check-release
	@echo "Uploading to PyPI..."
	twine upload dist/*

# Performance monitoring
.PHONY: perf-test
perf-test: install
	@echo "Running performance tests..."
	$(PYTHON) -m timeit -s "import backtesting_engine as bt; import numpy as np" \
		"engine = bt.BacktestingEngine(); strategy = bt.SMAStrategy(20); engine.add_strategy(strategy); [engine.add_market_data('TEST', 100+i, 1640995200+i*86400, 1000) for i in range(100)]; engine.run()"

# Status and info targets
.PHONY: info
info:
	@echo "Project Information:"
	@echo "  Python version: $$($(PYTHON) --version)"
	@echo "  Pip version: $$($(PIP) --version)"
	@echo "  Project: $(PROJECT_NAME)"
	@echo "  Current directory: $$(pwd)"

.PHONY: check-deps
check-deps:
	@echo "Checking dependencies..."
	$(PIP) check
	@echo "Dependencies OK"

# Quick development cycle
.PHONY: quick
quick: clean install-dev test-fast
	@echo "Quick development cycle completed"

# Pre-commit hooks simulation
.PHONY: pre-commit
pre-commit: format lint test-fast
	@echo "Pre-commit checks passed"