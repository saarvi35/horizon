SHELL := /usr/bin/env bash

KIND_CLUSTER ?= beleva-cluster
KUBE_CONTEXT ?= kind-$(KIND_CLUSTER)
NAMESPACE ?= horizon
MONITORING_NAMESPACE ?= monitoring

.DEFAULT_GOAL := help

.PHONY: help cluster bootstrap deploy secret status app-status monitoring-status images build-local load-local local-up local-down logs app grafana prometheus argocd lint template

help: ## Show the available automation commands.
	@awk 'BEGIN {FS = ":.*##"}; /^[a-zA-Z0-9_-]+:.*##/ {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

cluster: ## Create the local kind cluster if it does not exist.
	@bash ./scripts/bootstrap-kind.sh $(KIND_CLUSTER)

bootstrap: cluster ## Install Argo CD, monitoring, the app secret, and the Argo CD application.
	@bash ./scripts/bootstrap-platform.sh $(KIND_CLUSTER)

deploy: ## Ask Argo CD to manage the Beleva Helm stack from GitHub.
	@kubectl --context $(KUBE_CONTEXT) apply -f argocd/application.yaml

secret: ## Create or update the Kubernetes app secret from .env (never commits it).
	@bash ./scripts/create-k8s-secret.sh $(KUBE_CONTEXT) $(NAMESPACE) .env

status: ## Show cluster, application, monitoring, Helm, and Argo CD status.
	@kubectl --context $(KUBE_CONTEXT) get nodes
	@kubectl --context $(KUBE_CONTEXT) get pods -n $(NAMESPACE)
	@kubectl --context $(KUBE_CONTEXT) get pods -n $(MONITORING_NAMESPACE)
	@kubectl --context $(KUBE_CONTEXT) get applications -n argocd
	@helm --kube-context $(KUBE_CONTEXT) list -A

app-status: ## Show all Beleva Kubernetes resources.
	@kubectl --context $(KUBE_CONTEXT) get all -n $(NAMESPACE)

monitoring-status: ## Show Prometheus and Grafana resources.
	@kubectl --context $(KUBE_CONTEXT) get all -n $(MONITORING_NAMESPACE)

images: ## List the Docker images used by the local Docker daemon.
	@docker image ls | head -n 20

build-local: ## Build local images for kind-only testing.
	@docker build -t beleva-django:dev ./beleva-website
	@docker build -t beleva-nginx:dev ./nginx

load-local: build-local ## Load local development images into kind.
	@kind load docker-image beleva-django:dev beleva-nginx:dev --name $(KIND_CLUSTER)

local-up: ## Run the local Docker Compose development stack.
	@docker compose up --build -d

local-down: ## Stop the local Docker Compose development stack.
	@docker compose down

logs: ## Stream Django application logs from Kubernetes.
	@kubectl --context $(KUBE_CONTEXT) logs -n $(NAMESPACE) deployment/beleva-django -f

app: ## Open a local port-forward for the Beleva Nginx service on :8081.
	@kubectl --context $(KUBE_CONTEXT) port-forward -n $(NAMESPACE) service/beleva-nginx 8081:80

grafana: ## Open a local Grafana port-forward on :3000.
	@kubectl --context $(KUBE_CONTEXT) port-forward -n $(MONITORING_NAMESPACE) service/monitoring-grafana 3000:80

prometheus: ## Open a local Prometheus port-forward on :9091.
	@kubectl --context $(KUBE_CONTEXT) port-forward -n $(MONITORING_NAMESPACE) service/monitoring-kube-prometheus-prometheus 9091:9090

argocd: ## Open a local Argo CD port-forward on :8082.
	@kubectl --context $(KUBE_CONTEXT) port-forward -n argocd service/argocd-server 8082:443

lint: ## Lint the final Helm stack.
	@helm lint ./helm/beleva-stack

template: ## Render the final Helm stack locally without deploying it.
	@helm template beleva ./helm/beleva-stack -n $(NAMESPACE)
