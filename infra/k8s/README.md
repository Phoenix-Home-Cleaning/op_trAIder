# ☸️ TRAIDER Kubernetes Infrastructure Guide

### Local K3s Development & Production Helm Deployment

---

## 🎯 Overview

This guide provides comprehensive instructions for setting up TRAIDER's Kubernetes infrastructure, from local development with K3s to production deployment using Helm charts on managed Kubernetes clusters.

### Infrastructure Tiers

- **Local Development**: K3s single-node cluster for development and testing
- **Staging**: Lightweight K3s cluster for integration testing
- **Production**: Managed Kubernetes (DigitalOcean K8s) with Helm charts and service mesh

---

## 🚀 Local K3s Quick Start

### Prerequisites

```bash
# Install required tools
curl -sfL https://get.k3s.io | sh -
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
kubectl version --client
```

### K3s Installation

```bash
# Install K3s with Traefik disabled (we'll use our own ingress)
curl -sfL https://get.k3s.io | INSTALL_K3S_EXEC="--disable traefik" sh -

# Configure kubectl
sudo cp /etc/rancher/k3s/k3s.yaml ~/.kube/config
sudo chown $(id -u):$(id -g) ~/.kube/config

# Verify installation
kubectl get nodes
kubectl get pods -A
```

### Local Registry Setup

```bash
# Create local container registry for development
docker run -d -p 5000:5000 --name k3s-registry registry:2

# Configure K3s to use local registry
sudo mkdir -p /etc/rancher/k3s
cat <<EOF | sudo tee /etc/rancher/k3s/registries.yaml
mirrors:
  "localhost:5000":
    endpoint:
      - "http://localhost:5000"
EOF

# Restart K3s to apply registry configuration
sudo systemctl restart k3s
```

---

## 🏗️ Development Environment Setup

### Namespace Creation

```bash
# Create TRAIDER namespaces
kubectl create namespace traider-dev
kubectl create namespace traider-staging

# Set default namespace for development
kubectl config set-context --current --namespace=traider-dev
```

### Secret Management

```bash
# Create secrets for development - use actual values in production
# See docs/security/secrets-management.md for detailed instructions
kubectl create secret generic traider-secrets --namespace=traider-dev

# Verify secrets
kubectl get secrets -n traider-dev
```

### Basic Services Deployment

```bash
# Deploy development services
kubectl apply -f infrastructure/k8s/dev/

# Check deployment status
kubectl get pods -n traider-dev
kubectl get services -n traider-dev

# Access services via NodePort (for development)
# Frontend: http://localhost:30000
# Backend API: http://localhost:30001
# Grafana: http://localhost:30002

# Or via ingress (add to /etc/hosts):
# 127.0.0.1 traider.local api.traider.local grafana.traider.local prometheus.traider.local
# Frontend: http://traider.local
# Backend API: http://api.traider.local
# Grafana: http://grafana.traider.local
# Prometheus: http://prometheus.traider.local
```

---

## 📦 Core Services Architecture

### Service Structure

```
infrastructure/k8s/
├── dev/                    # Development manifests
│   ├── namespace.yaml
│   ├── database.yaml       # PostgreSQL for development
│   ├── redis.yaml         # Redis for caching
│   └── monitoring.yaml    # Basic monitoring stack
├── base/                  # Base configurations
│   ├── configmaps/
│   ├── secrets/
│   └── services/
├── overlays/             # Environment-specific overlays
│   ├── development/
│   ├── staging/
│   └── production/
└── helm/                 # Helm charts for production
    ├── traider-platform/
    ├── monitoring/
    └── ingress/
```

### Development Services

```yaml
# infrastructure/k8s/dev/database.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres-dev
  namespace: traider-dev
spec:
  replicas: 1
  selector:
    matchLabels:
      app: postgres-dev
  template:
    metadata:
      labels:
        app: postgres-dev
    spec:
      containers:
        - name: postgres
          image: timescale/timescaledb:latest-pg14
          ports:
            - containerPort: 5432
          env:
            - name: POSTGRES_DB
              value: traider
            - name: POSTGRES_USER
              value: traider
            - name: POSTGRES_PASSWORD
              value: REPLACE_WITH_DEV_PASSWORD
          volumeMounts:
            - name: postgres-storage
              mountPath: /var/lib/postgresql/data
      volumes:
        - name: postgres-storage
          emptyDir: {}
---
apiVersion: v1
kind: Service
metadata:
  name: postgres-dev
  namespace: traider-dev
spec:
  selector:
    app: postgres-dev
  ports:
    - port: 5432
      targetPort: 5432
```

---

_This guide is part of the TRAIDER institutional-grade infrastructure upgrade. See full documentation for complete setup instructions, production deployment, and troubleshooting._
