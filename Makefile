# Flowcase Makefile

.PHONY: help install run clean test docker-up docker-down db-reset create-droplets

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	pip install -r requirements.txt

run: ## Run development server
	python3 start_dev.py

clean: ## Clean cache and temp files
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -delete
	find . -type d -name '.pytest_cache' -delete

test: ## Run tests
	pytest tests/ -v

docker-up: ## Start Docker containers
	docker-compose -f docker-compose.dev.yml up -d

docker-down: ## Stop Docker containers
	docker-compose -f docker-compose.dev.yml down

docker-build: ## Build Docker images
	docker-compose -f docker-compose.dev.yml build

db-reset: ## Reset database
	rm -rf data/.firstrun data/flowcase.db
	python3 start_dev.py

create-droplets: ## Create test droplets
	python3 create_test_droplets.py

create-workshops: ## Create test workshops
	python3 create_test_workshops.py

create-tenants: ## Create test tenants
	python3 create_test_tenants.py

create-all-test-data: create-droplets create-workshops create-tenants ## Create all test data

logs: ## Show application logs
	tail -f data/flowcase.log

kill-port: ## Kill process on port 5000
	lsof -ti:5000 | xargs kill -9 2>/dev/null || true

setup: install db-reset create-all-test-data ## Complete setup
	@echo "✅ Setup complete! Run 'make run' to start"
