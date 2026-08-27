SHELL := /bin/bash

.PHONY: help install test eval lint run docker-build

help:
	@echo "Available commands:"
	@echo "  make install     Install dependencies"
	@echo "  make test        Run unit and integration tests"
	@echo "  make eval        Run 4-tier benchmark evaluation harness"
	@echo "  make run         Run local agent runtime"
	@echo "  make docker-build Build container image"

install:
	pip install -e ".[dev]"

test:
	python -m pytest tests/ -v

eval:
	python eval/run_evaluation.py

run:
	python app/main.py

docker-build:
	docker build -t altostrat-hr-agent:latest .
