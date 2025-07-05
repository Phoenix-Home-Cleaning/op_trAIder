# 🚀 TRAIDER K8s Development Environment

## Overview

This directory contains Kubernetes manifests for running the TRAIDER V1 platform in a local K3s development environment. All services are configured with development-friendly settings and resource limits suitable for local development.

## Quick Start

### Prerequisites

1. **K3s installed and running**
   ```bash
   # Install K3s (Linux/macOS)
   curl -sfL https://get.k3s.io | sh -
   
   # Windows (WSL2)
   curl -sfL https://get.k3s.io | sh -s - --write-kubeconfig-mode 644
   ```

2. **kubectl configured**
   ```bash
   # Copy K3s config
   sudo cp /etc/rancher/k3s/k3s.yaml ~/.kube/config
   sudo chown $(id -u):$(id -g) ~/.kube/config
   ```

### Deploy Services

```bash
# Apply all manifests
kubectl apply -f infrastructure/k8s/dev/

# Check deployment status
kubectl get pods -n traider-dev
kubectl get services -n traider-dev
```

### Access Services

#### NodePort Access (Recommended for Development)
- **Frontend**: http://localhost:30000
- **Backend API**: http://localhost:30001  
- **Grafana**: http://localhost:30002 (admin/admin)
- **Prometheus**: `kubectl port-forward svc/prometheus-dev 9090:9090 -n traider-dev`

#### Ingress Access (Optional)
Add to `/etc/hosts` (Linux/macOS) or `C:\Windows\System32\drivers\etc\hosts` (Windows):
```
127.0.0.1 traider.local api.traider.local grafana.traider.local prometheus.traider.local
```

Then access:
- **Frontend**: http://traider.local
- **Backend API**: http://api.traider.local
- **Grafana**: http://grafana.traider.local
- **Prometheus**: http://prometheus.traider.local

## Service Architecture

### Core Services

1. **PostgreSQL with TimescaleDB** (`postgres-dev.yaml`)
   - Database: `traider`
   - User: `traider` / Password: `password`
   - Port: 5432
   - TimescaleDB extension auto-configured
   - Resource limits: 1Gi memory, 500m CPU

2. **Redis Cache** (`redis-dev.yaml`)
   - Port: 6379
   - Persistence enabled with AOF
   - LRU eviction policy
   - Resource limits: 256Mi memory, 200m CPU

3. **Backend API** (`backend-dev.yaml`)
   - FastAPI application
   - Port: 8000 (HTTP), 8001 (Metrics)
   - Environment variables from ConfigMap/Secret
   - Health checks configured
   - Resource limits: 512Mi memory, 500m CPU

4. **Frontend** (`frontend-dev.yaml`)
   - Next.js application
   - Port: 3000
   - Development build
   - Resource limits: 512Mi memory, 500m CPU

5. **Monitoring Stack** (`monitoring-dev.yaml`)
   - Prometheus: Metrics collection
   - Grafana: Dashboards and visualization
   - Pre-configured data sources
   - Resource limits: 512Mi memory each

## Configuration Details

### Environment Variables

All environment variables are managed through ConfigMaps and Secrets:

- **backend-config**: Non-sensitive configuration
- **backend-secrets**: JWT keys, API credentials
- **frontend-config**: Next.js configuration
- **frontend-secrets**: NextAuth secrets

### Resource Limits

All services have sensible resource limits for development:
- **Requests**: Minimum resources guaranteed
- **Limits**: Maximum resources allowed
- **Total cluster requirements**: ~3Gi memory, ~2.5 CPU cores

### Health Checks

All services include:
- **Liveness probes**: Restart unhealthy containers
- **Readiness probes**: Traffic routing control
- **Startup probes**: Allow slow container startup

## Helm Integration (Future)

### Placeholder Values

The current manifests use hardcoded values suitable for development. For production deployment with Helm, the following values will be templated:

```yaml
# Example Helm template patterns (not yet implemented)
image: "{{ .Values.backend.image.repository }}:{{ .Values.backend.image.tag }}"
replicas: {{ .Values.backend.replicas }}
resources:
  limits:
    memory: "{{ .Values.backend.resources.limits.memory }}"
    cpu: "{{ .Values.backend.resources.limits.cpu }}"
```

### Planned Helm Charts

Future Helm chart structure:
```
infrastructure/k8s/helm/
├── traider-platform/
│   ├── Chart.yaml
│   ├── values.yaml
│   ├── values-dev.yaml
│   ├── values-staging.yaml
│   ├── values-production.yaml
│   └── templates/
│       ├── backend/
│       ├── frontend/
│       ├── database/
│       └── monitoring/
```

## Ingress Configuration

### Development Domains

The ingress is configured with `.local` domains for development:
- `traider.local` - Frontend application
- `api.traider.local` - Backend API
- `grafana.traider.local` - Grafana dashboards
- `prometheus.traider.local` - Prometheus metrics

### CORS Configuration

Development CORS settings allow:
- Origin: `http://localhost:3000`
- Methods: `GET, POST, PUT, DELETE, OPTIONS`
- Headers: Standard + Authorization

### SSL/TLS

For development, SSL is disabled. Production deployment will include:
- Let's Encrypt certificates
- Automatic certificate renewal
- HTTPS redirects

## Troubleshooting

### Common Issues

1. **Pods stuck in Pending**
   ```bash
   kubectl describe pod <pod-name> -n traider-dev
   # Check resource availability and node capacity
   ```

2. **Database connection issues**
   ```bash
   kubectl logs deployment/postgres-dev -n traider-dev
   kubectl port-forward svc/postgres-dev 5432:5432 -n traider-dev
   ```

3. **Services not accessible**
   ```bash
   kubectl get svc -n traider-dev
   kubectl describe ingress traider-dev-ingress -n traider-dev
   ```

### Useful Commands

```bash
# View all resources
kubectl get all -n traider-dev

# Follow logs
kubectl logs -f deployment/backend-dev -n traider-dev

# Execute into containers
kubectl exec -it deployment/postgres-dev -n traider-dev -- psql -U traider -d traider

# Port forwarding
kubectl port-forward svc/backend-dev 8000:8000 -n traider-dev

# Delete and redeploy
kubectl delete -f infrastructure/k8s/dev/
kubectl apply -f infrastructure/k8s/dev/
```

## Security Considerations

### Development Security

- Default passwords (change in production)
- No network policies (add for production)
- Cluster admin access (restrict for production)
- Plain HTTP (use HTTPS for production)

### Production Preparation

When moving to production:
1. Enable network policies
2. Use proper secrets management (Vault, Sealed Secrets)
3. Implement RBAC
4. Enable Pod Security Standards
5. Use private container registry
6. Enable audit logging

## Monitoring & Observability

### Metrics Collection

Prometheus scrapes metrics from:
- Backend application (`/metrics` endpoint)
- Kubernetes cluster metrics
- Node metrics (future: node-exporter)

### Dashboards

Grafana includes:
- Pre-configured Prometheus data source
- Basic system monitoring dashboard
- Application-specific metrics (trading performance)

### Alerting (Future)

Planned alerting rules:
- High error rates
- Database connection failures
- Memory/CPU exhaustion
- Trading system anomalies

---

**Note**: This is a development environment. Production deployment requires additional security hardening, monitoring, and operational procedures. 