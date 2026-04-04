.PHONY: help build up down logs ps clean test deploy-k8s terraform-plan terraform-apply

DOCKER_COMPOSE = docker compose
KUBECTL = kubectl
NAMESPACE = finance-tracker

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

# Docker Compose commands
build: ## Build all Docker images
	$(DOCKER_COMPOSE) build --parallel

up: ## Start all services in detached mode
	$(DOCKER_COMPOSE) up -d

up-build: ## Build and start all services
	$(DOCKER_COMPOSE) up -d --build

down: ## Stop all services
	$(DOCKER_COMPOSE) down

down-v: ## Stop all services and remove volumes
	$(DOCKER_COMPOSE) down -v

logs: ## Show logs for all services
	$(DOCKER_COMPOSE) logs -f

logs-service: ## Show logs for a specific service (usage: make logs-service SERVICE=user-service)
	$(DOCKER_COMPOSE) logs -f $(SERVICE)

ps: ## Show running services
	$(DOCKER_COMPOSE) ps

clean: ## Remove all containers, images and volumes
	$(DOCKER_COMPOSE) down -v --rmi all --remove-orphans

restart: ## Restart all services
	$(DOCKER_COMPOSE) restart

# Health checks
health: ## Check health of all services
	@echo "Checking service health..."
	@curl -s http://localhost:3000/health | python3 -m json.tool || echo "API Gateway: DOWN"
	@curl -s http://localhost:8001/health | python3 -m json.tool || echo "User Service: DOWN"
	@curl -s http://localhost:8002/health | python3 -m json.tool || echo "Transaction Service: DOWN"
	@curl -s http://localhost:8003/health | python3 -m json.tool || echo "Budget Service: DOWN"
	@curl -s http://localhost:8004/health | python3 -m json.tool || echo "Notification Service: DOWN"

# Kubernetes commands
k8s-namespace: ## Create Kubernetes namespace
	$(KUBECTL) apply -f k8s/namespace.yaml

k8s-deploy: ## Deploy all services to Kubernetes
	$(KUBECTL) apply -f k8s/configmaps/
	$(KUBECTL) apply -f k8s/secrets/
	$(KUBECTL) apply -f k8s/postgres/
	$(KUBECTL) apply -f k8s/redis/
	$(KUBECTL) apply -f k8s/deployments/
	$(KUBECTL) apply -f k8s/ingress/
	$(KUBECTL) apply -f k8s/monitoring/

k8s-status: ## Check Kubernetes deployment status
	$(KUBECTL) get all -n $(NAMESPACE)

k8s-pods: ## Get pod status
	$(KUBECTL) get pods -n $(NAMESPACE) -o wide

k8s-logs: ## Get logs from a deployment (usage: make k8s-logs SERVICE=user-service)
	$(KUBECTL) logs -f deployment/$(SERVICE) -n $(NAMESPACE)

k8s-delete: ## Delete all Kubernetes resources
	$(KUBECTL) delete namespace $(NAMESPACE)

k8s-rollout: ## Check rollout status of all deployments
	@for service in api-gateway user-service transaction-service budget-service notification-service frontend; do \
		echo "Checking $$service..."; \
		$(KUBECTL) rollout status deployment/$$service -n $(NAMESPACE) --timeout=60s || true; \
	done

k8s-hpa: ## Show HPA status
	$(KUBECTL) get hpa -n $(NAMESPACE)

# Terraform commands
tf-init: ## Initialize Terraform
	cd terraform && terraform init

tf-plan: ## Run Terraform plan
	cd terraform && terraform plan -var-file=terraform.tfvars

tf-apply: ## Apply Terraform changes
	cd terraform && terraform apply -var-file=terraform.tfvars

tf-destroy: ## Destroy Terraform infrastructure
	cd terraform && terraform destroy -var-file=terraform.tfvars

tf-fmt: ## Format Terraform files
	cd terraform && terraform fmt -recursive

# Ansible commands
ansible-setup: ## Run Ansible setup playbook
	cd ansible && ansible-playbook playbooks/setup-nodes.yml

ansible-deploy: ## Run Ansible deploy playbook
	cd ansible && ansible-playbook playbooks/deploy-app.yml

ansible-health: ## Run Ansible health check
	cd ansible && ansible-playbook playbooks/health-check.yml

# Development helpers
dev-user: ## Run user service locally
	cd services/user-service && uvicorn app.main:app --reload --port 8001

dev-transaction: ## Run transaction service locally
	cd services/transaction-service && uvicorn app.main:app --reload --port 8002

dev-budget: ## Run budget service locally
	cd services/budget-service && uvicorn app.main:app --reload --port 8003

dev-notification: ## Run notification service locally
	cd services/notification-service && uvicorn app.main:app --reload --port 8004

dev-gateway: ## Run API gateway locally
	cd services/api-gateway && npm run dev

dev-frontend: ## Run frontend dev server
	cd services/frontend && npm run dev
