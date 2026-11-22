.PHONY: help install test lint eval run-backend run-frontend seed docker-up docker-down

help:
	@echo "SarkariSach Developer Commands:"
	@echo "  make install       Install backend & frontend dependencies"
	@echo "  make test          Run 48+ backend pytest test suite"
	@echo "  make eval          Run benchmark evaluation script across 25 samples"
	@echo "  make lint          Run ruff code linter"
	@echo "  make seed          Seed database with 120 realistic sample records"
	@echo "  make run-backend   Start FastAPI server (port 8000)"
	@echo "  make run-frontend  Start Vite development server (port 5173)"
	@echo "  make docker-up     Build and start Docker container"
	@echo "  make docker-down   Stop Docker container"

install:
	python -m pip install -r backend/requirements.txt
	cd frontend && npm install

test:
	pytest backend/tests -v

eval:
	python scripts/evaluate.py

lint:
	ruff check backend/ app/

seed:
	python scripts/seed_dashboard.py

run-backend:
	uvicorn app.main:app --app-dir backend --reload --port 8000

run-frontend:
	cd frontend && npm run dev

docker-up:
	docker compose up --build -d

docker-down:
	docker compose down

