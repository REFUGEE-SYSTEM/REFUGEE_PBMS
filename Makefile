# ==============================================================================
# Makefile — Refugee Management Standalone Project
# ==============================================================================

SHELL := /bin/bash
.DEFAULT_GOAL := help

.PHONY: help check install start stop restart status backup restore verify logs

help: ## Display this help message
	@echo "Refugee Management — Standalone Control"
	@echo "Usage: make [target]"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'

check: ## Verify prerequisites, system dependencies, and available ports
	@./scripts/check_dependencies.sh

install: ## Install standalone dependencies and prepare runtime environment (Gate 4-6)
	@./scripts/install.sh

start: ## Start the standalone refugee_management services
	@./scripts/start.sh

stop: ## Stop standalone refugee_management services safely
	@./scripts/stop.sh

restart: ## Restart standalone refugee_management services
	@./scripts/restart.sh

status: ## Show health and status of standalone services
	@./scripts/status.sh

backup: ## Perform timestamped backup of database and filestore
	@./scripts/backup.sh

restore: ## Restore standalone environment from a verified backup
	@./scripts/restore.sh

verify: ## Run integrity and functional validation checks
	@./scripts/verify.sh

logs: ## Tail application logs
	@tail -f logs/*.log 2>/dev/null || echo "No active log files in logs/"
