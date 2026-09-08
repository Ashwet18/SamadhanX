# SamadhanX Development Makefile

# Variables
DOCKER_COMPOSE = docker-compose
PROJECT_NAME = samadhanx
BACKEND_DIR = backend
FRONTEND_DIR = frontend

# Colors for output
RED = \033[0;31m
GREEN = \033[0;32m
YELLOW = \033[0;33m
BLUE = \033[0;34m
NC = \033[0m # No Color

.PHONY: help
help: ## Show this help message
	@echo "$(GREEN)SamadhanX Development Commands$(NC)"
	@echo "================================"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(BLUE)%-20s$(NC) %s\n", $$1, $$2}'

# ===================================
# DEVELOPMENT SETUP
# ===================================

.PHONY: setup
setup: ## Initial project setup
	@echo "$(GREEN)Setting up SamadhanX development environment...$(NC)"
	@cp .env.example .env
	@echo "$(YELLOW)Please update .env file with your configuration$(NC)"
	@$(MAKE) install

.PHONY: install
install: install-backend install-frontend ## Install all dependencies

.PHONY: install-backend
install-backend: ## Install backend dependencies
	@echo "$(GREEN)Installing backend dependencies...$(NC)"
	cd $(BACKEND_DIR) && pip install -r requirements.txt

.PHONY: install-frontend  
install-frontend: ## Install frontend dependencies
	@echo "$(GREEN)Installing frontend dependencies...$(NC)"
	cd $(FRONTEND_DIR) && npm install

# ===================================
# DOCKER COMMANDS
# ===================================

.PHONY: up
up: ## Start all services with Docker Compose
	@echo "$(GREEN)Starting SamadhanX services...$(NC)"
	$(DOCKER_COMPOSE) up -d

.PHONY: down
down: ## Stop all services
	@echo "$(YELLOW)Stopping SamadhanX services...$(NC)"
	$(DOCKER_COMPOSE) down

.PHONY: restart
restart: down up ## Restart all services

.PHONY: build
build: ## Build all Docker images
	@echo "$(GREEN)Building Docker images...$(NC)"
	$(DOCKER_COMPOSE) build

.PHONY: rebuild
rebuild: ## Rebuild all Docker images without cache
	@echo "$(GREEN)Rebuilding Docker images...$(NC)"
	$(DOCKER_COMPOSE) build --no-cache

.PHONY: logs
logs: ## View logs from all services
	$(DOCKER_COMPOSE) logs -f

.PHONY: logs-backend
logs-backend: ## View backend logs
	$(DOCKER_COMPOSE) logs -f backend

.PHONY: logs-frontend
logs-frontend: ## View frontend logs
	$(DOCKER_COMPOSE) logs -f frontend

# ===================================
# DEVELOPMENT COMMANDS
# ===================================

.PHONY: dev
dev: ## Start development environment
	@echo "$(GREEN)Starting development environment...$(NC)"
	$(DOCKER_COMPOSE) --profile development up -d
	@echo "$(GREEN)Services available at:$(NC)"
	@echo "Frontend: http://localhost:3000"
	@echo "Backend API: http://localhost:8000"
	@echo "API Docs: http://localhost:8000/docs"
	@echo "pgAdmin: http://localhost:5050"
	@echo "Redis Insight: http://localhost:8001"

.PHONY: dev-backend
dev-backend: ## Start only backend development
	@echo "$(GREEN)Starting backend development...$(NC)"
	cd $(BACKEND_DIR) && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

.PHONY: dev-frontend
dev-frontend: ## Start only frontend development
	@echo "$(GREEN)Starting frontend development...$(NC)"
	cd $(FRONTEND_DIR) && npm run dev

# ===================================
# DATABASE COMMANDS
# ===================================

.PHONY: db-up
db-up: ## Start only database services
	@echo "$(GREEN)Starting database services...$(NC)"
	$(DOCKER_COMPOSE) up -d postgres redis

.PHONY: db-reset
db-reset: ## Reset database (WARNING: destroys all data)
	@echo "$(RED)WARNING: This will destroy all database data!$(NC)"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		$(DOCKER_COMPOSE) down -v postgres; \
		$(DOCKER_COMPOSE) up -d postgres; \
		echo "$(GREEN)Database reset complete$(NC)"; \
	else \
		echo "$(YELLOW)Database reset cancelled$(NC)"; \
	fi

.PHONY: db-migrate
db-migrate: ## Run database migrations
	@echo "$(GREEN)Running database migrations...$(NC)"
	$(DOCKER_COMPOSE) exec backend alembic upgrade head

.PHONY: db-shell
db-shell: ## Connect to PostgreSQL shell
	$(DOCKER_COMPOSE) exec postgres psql -U samadhanx -d samadhanx

.PHONY: redis-shell
redis-shell: ## Connect to Redis CLI
	$(DOCKER_COMPOSE) exec redis redis-cli

# ===================================
# TESTING COMMANDS
# ===================================

.PHONY: test
test: test-backend test-frontend ## Run all tests

.PHONY: test-backend
test-backend: ## Run backend tests
	@echo "$(GREEN)Running backend tests...$(NC)"
	cd $(BACKEND_DIR) && python -m pytest

.PHONY: test-frontend
test-frontend: ## Run frontend tests
	@echo "$(GREEN)Running frontend tests...$(NC)"
	cd $(FRONTEND_DIR) && npm test

.PHONY: test-e2e
test-e2e: ## Run end-to-end tests
	@echo "$(GREEN)Running E2E tests...$(NC)"
	cd $(FRONTEND_DIR) && npm run test:e2e

.PHONY: test-coverage
test-coverage: ## Run tests with coverage
	@echo "$(GREEN)Running tests with coverage...$(NC)"
	cd $(BACKEND_DIR) && python -m pytest --cov=app --cov-report=html
	cd $(FRONTEND_DIR) && npm run test:coverage

# ===================================
# CODE QUALITY
# ===================================

.PHONY: lint
lint: lint-backend lint-frontend ## Run linting on all code

.PHONY: lint-backend
lint-backend: ## Run backend linting
	@echo "$(GREEN)Linting backend code...$(NC)"
	cd $(BACKEND_DIR) && black . && isort . && flake8 . && mypy .

.PHONY: lint-frontend
lint-frontend: ## Run frontend linting
	@echo "$(GREEN)Linting frontend code...$(NC)"
	cd $(FRONTEND_DIR) && npm run lint && npm run type-check

.PHONY: format
format: format-backend format-frontend ## Format all code

.PHONY: format-backend
format-backend: ## Format backend code
	@echo "$(GREEN)Formatting backend code...$(NC)"
	cd $(BACKEND_DIR) && black . && isort .

.PHONY: format-frontend
format-frontend: ## Format frontend code
	@echo "$(GREEN)Formatting frontend code...$(NC)"
	cd $(FRONTEND_DIR) && npm run format

# ===================================
# MONITORING COMMANDS
# ===================================

.PHONY: monitoring
monitoring: ## Start monitoring stack
	@echo "$(GREEN)Starting monitoring services...$(NC)"
	$(DOCKER_COMPOSE) --profile monitoring up -d
	@echo "$(GREEN)Monitoring services available at:$(NC)"
	@echo "Prometheus: http://localhost:9090"
	@echo "Grafana: http://localhost:3001 (admin/admin123)"
	@echo "Flower: http://localhost:5555"

.PHONY: logs-stack
logs-stack: ## Start logging stack
	@echo "$(GREEN)Starting logging services...$(NC)"
	$(DOCKER_COMPOSE) --profile logging up -d
	@echo "$(GREEN)Logging services available at:$(NC)"
	@echo "Kibana: http://localhost:5601"

# ===================================
# PRODUCTION COMMANDS
# ===================================

.PHONY: prod
prod: ## Start production environment
	@echo "$(GREEN)Starting production environment...$(NC)"
	$(DOCKER_COMPOSE) -f docker-compose.yml --profile production up -d

.PHONY: backup
backup: ## Create database backup
	@echo "$(GREEN)Creating database backup...$(NC)"
	mkdir -p backups
	$(DOCKER_COMPOSE) exec postgres pg_dump -U samadhanx samadhanx > backups/backup_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "$(GREEN)Backup created in backups/ directory$(NC)"

.PHONY: restore
restore: ## Restore database from backup (specify BACKUP_FILE)
	@if [ -z "$(BACKUP_FILE)" ]; then \
		echo "$(RED)Please specify BACKUP_FILE=path/to/backup.sql$(NC)"; \
		exit 1; \
	fi
	@echo "$(YELLOW)Restoring database from $(BACKUP_FILE)...$(NC)"
	$(DOCKER_COMPOSE) exec -T postgres psql -U samadhanx -d samadhanx < $(BACKUP_FILE)
	@echo "$(GREEN)Database restored$(NC)"

# ===================================
# MAINTENANCE COMMANDS
# ===================================

.PHONY: clean
clean: ## Clean up Docker resources
	@echo "$(YELLOW)Cleaning up Docker resources...$(NC)"
	$(DOCKER_COMPOSE) down -v --remove-orphans
	docker system prune -f
	docker volume prune -f

.PHONY: clean-all
clean-all: clean ## Clean up everything including images
	@echo "$(YELLOW)Cleaning up all Docker resources...$(NC)"
	docker image prune -a -f

.PHONY: ps
ps: ## Show running services
	$(DOCKER_COMPOSE) ps

.PHONY: stats
stats: ## Show resource usage statistics
	docker stats

.PHONY: shell-backend
shell-backend: ## Get shell access to backend container
	$(DOCKER_COMPOSE) exec backend /bin/bash

.PHONY: shell-frontend
shell-frontend: ## Get shell access to frontend container
	$(DOCKER_COMPOSE) exec frontend /bin/sh

# ===================================
# UTILITY COMMANDS
# ===================================

.PHONY: generate-secret
generate-secret: ## Generate a random secret key
	@python -c "import secrets; print('JWT_SECRET_KEY=' + secrets.token_urlsafe(32))"

.PHONY: check-env
check-env: ## Check if .env file exists and is properly configured
	@if [ ! -f .env ]; then \
		echo "$(RED).env file not found. Run 'make setup' first.$(NC)"; \
		exit 1; \
	else \
		echo "$(GREEN).env file found$(NC)"; \
	fi

.PHONY: update
update: ## Update all dependencies
	@echo "$(GREEN)Updating dependencies...$(NC)"
	cd $(BACKEND_DIR) && pip install -r requirements.txt --upgrade
	cd $(FRONTEND_DIR) && npm update
	$(DOCKER_COMPOSE) pull

.PHONY: docs
docs: ## Generate and serve documentation
	@echo "$(GREEN)Serving documentation...$(NC)"
	@echo "API Documentation: http://localhost:8000/docs"
	@echo "Database Documentation: ./docs/database.md"
	@echo "Architecture Documentation: ./docs/architecture.md"

# ===================================
# DEFAULT TARGET
# ===================================

.DEFAULT_GOAL := help