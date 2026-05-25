.PHONY: up down build logs test clean restart

up:
	docker-compose up -d

down:
	docker-compose down

build:
	docker-compose build --no-cache

logs:
	docker-compose logs -f musync

test:
	cd backend && pytest tests/ -v

clean:
	docker-compose down -v
	rm -rf backend/__pycache__ backend/*/__pycache__ .pytest_cache

restart:
	docker-compose down
	docker-compose up -d

help:
	@echo "MuSync 2.0 - Available commands:"
	@echo "  make up       - Start all services"
	@echo "  make down     - Stop all services"
	@echo "  make build    - Rebuild Docker images"
	@echo "  make logs     - View backend logs"
	@echo "  make test     - Run backend tests"
	@echo "  make clean    - Stop and remove all data"
	@echo "  make restart  - Restart all services"
