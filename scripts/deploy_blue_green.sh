#!/bin/bash

# @fileoverview Zero-downtime blue-green deployment script for TRAIDER
# @module scripts/deploy_blue_green
# 
# @description
# Implements blue-green deployment strategy for TRAIDER trading platform:
# - Deploys to inactive environment (blue/green)
# - Performs comprehensive health checks and smoke tests
# - Switches traffic with validation
# - Provides automated rollback on failure
# 
# @performance
# - Deployment time: ~5-10 minutes
# - Zero-downtime switching: <5 seconds
# - Rollback time: <30 seconds
# 
# @risk
# - Failure impact: MEDIUM (automated rollback mitigates)
# - Recovery strategy: Automatic rollback to previous environment
# 
# @compliance
# - Audit requirements: Yes (all deployments logged)
# - Data retention: Deployment logs retained 1 year
# 
# @see infrastructure/k8s/README.md
# @since v2.0.0
# @author TRAIDER Team

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="/tmp/traider_deploy_${TIMESTAMP}.log"

# Default values
NAMESPACE_ACTIVE=${1:-traider-blue}
NAMESPACE_INACTIVE=${2:-traider-green}
IMAGE_TAG=${3:-latest}
HELM_CHART_PATH="${PROJECT_ROOT}/infrastructure/helm/traider-platform"
VALUES_FILE="${HELM_CHART_PATH}/values-production.yaml"
TIMEOUT=${TIMEOUT:-600}  # 10 minutes
HEALTH_CHECK_RETRIES=${HEALTH_CHECK_RETRIES:-30}
SMOKE_TEST_TIMEOUT=${SMOKE_TEST_TIMEOUT:-300}  # 5 minutes

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] ✅ $1${NC}" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] ⚠️  $1${NC}" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ❌ $1${NC}" | tee -a "$LOG_FILE"
}

# Error handling
cleanup() {
    local exit_code=$?
    if [ $exit_code -ne 0 ]; then
        log_error "Deployment failed with exit code $exit_code"
        log_error "Check logs at: $LOG_FILE"
        
        # Attempt rollback if we were in the middle of switching
        if [ "${TRAFFIC_SWITCHED:-false}" = "true" ]; then
            log_warning "Attempting automatic rollback..."
            rollback_traffic
        fi
    fi
    exit $exit_code
}

trap cleanup EXIT

# Validation functions
validate_prerequisites() {
    log "🔍 Validating prerequisites..."
    
    # Check required tools
    local required_tools=("kubectl" "helm" "curl" "jq")
    for tool in "${required_tools[@]}"; do
        if ! command -v "$tool" &> /dev/null; then
            log_error "Required tool '$tool' not found"
            exit 1
        fi
    done
    
    # Check kubectl connectivity
    if ! kubectl cluster-info &> /dev/null; then
        log_error "Cannot connect to Kubernetes cluster"
        exit 1
    fi
    
    # Check Helm chart exists
    if [ ! -f "$VALUES_FILE" ]; then
        log_error "Helm values file not found: $VALUES_FILE"
        exit 1
    fi
    
    # Validate namespaces
    if [ "$NAMESPACE_ACTIVE" = "$NAMESPACE_INACTIVE" ]; then
        log_error "Active and inactive namespaces cannot be the same"
        exit 1
    fi
    
    log_success "Prerequisites validated"
}

get_current_active_environment() {
    # Determine current active environment by checking ingress routing
    local current_service
    current_service=$(kubectl get ingress traider-traffic-switch -o jsonpath='{.spec.rules[0].http.paths[0].backend.service.name}' 2>/dev/null || echo "")
    
    if [[ "$current_service" == *"blue"* ]]; then
        echo "traider-blue"
    elif [[ "$current_service" == *"green"* ]]; then
        echo "traider-green"
    else
        # Default to blue if no ingress found
        echo "traider-blue"
    fi
}

# Deployment functions
deploy_to_inactive_environment() {
    log "📦 Deploying to inactive environment ($NAMESPACE_INACTIVE)..."
    
    # Extract environment name (blue/green) from namespace
    local env_name="${NAMESPACE_INACTIVE#traider-}"
    
    # Deploy using Helm
    helm upgrade --install "traider-${env_name}" \
        "$HELM_CHART_PATH" \
        --namespace "$NAMESPACE_INACTIVE" \
        --create-namespace \
        --values "$VALUES_FILE" \
        --set image.tag="$IMAGE_TAG" \
        --set environment="$env_name" \
        --set deployment.timestamp="$TIMESTAMP" \
        --wait \
        --timeout="${TIMEOUT}s" \
        --debug 2>&1 | tee -a "$LOG_FILE"
    
    if [ $? -ne 0 ]; then
        log_error "Helm deployment failed"
        exit 1
    fi
    
    log_success "Deployment completed successfully"
}

wait_for_pods_ready() {
    log "🏥 Waiting for pods to be ready..."
    
    # Wait for all pods to be ready
    if ! kubectl wait --for=condition=ready pod \
        -l app.kubernetes.io/name=traider-platform \
        -n "$NAMESPACE_INACTIVE" \
        --timeout="${TIMEOUT}s"; then
        log_error "Pods failed to become ready within timeout"
        return 1
    fi
    
    # Additional wait for application startup
    log "⏳ Waiting for application startup (30s)..."
    sleep 30
    
    log_success "All pods are ready"
}

perform_health_checks() {
    log "🩺 Performing comprehensive health checks..."
    
    local health_endpoint="http://traider-backend.${NAMESPACE_INACTIVE}.svc.cluster.local:8000/health"
    local retry_count=0
    
    while [ $retry_count -lt $HEALTH_CHECK_RETRIES ]; do
        log "Health check attempt $((retry_count + 1))/$HEALTH_CHECK_RETRIES"
        
        # Port forward for health check
        kubectl port-forward -n "$NAMESPACE_INACTIVE" \
            service/traider-backend 8080:8000 &
        local port_forward_pid=$!
        sleep 5
        
        # Perform health check
        if curl -s -f "http://localhost:8080/health" &> /dev/null; then
            kill $port_forward_pid 2>/dev/null || true
            log_success "Health check passed"
            return 0
        fi
        
        kill $port_forward_pid 2>/dev/null || true
        retry_count=$((retry_count + 1))
        sleep 10
    done
    
    log_error "Health checks failed after $HEALTH_CHECK_RETRIES attempts"
    return 1
}

run_smoke_tests() {
    log "💨 Running smoke tests..."
    
    # Create a temporary smoke test script
    local smoke_test_script="/tmp/smoke_tests_${TIMESTAMP}.sh"
    
    cat > "$smoke_test_script" << 'EOF'
#!/bin/bash
set -e

NAMESPACE=$1
BASE_URL="http://traider-backend.${NAMESPACE}.svc.cluster.local:8000"

echo "🧪 Testing API endpoints..."

# Test health endpoint
echo "Testing /health..."
kubectl exec -n "$NAMESPACE" deployment/traider-backend -- \
    curl -s -f "${BASE_URL}/health" > /dev/null

# Test metrics endpoint
echo "Testing /metrics..."
kubectl exec -n "$NAMESPACE" deployment/traider-backend -- \
    curl -s -f "${BASE_URL}/metrics" > /dev/null

# Test database connectivity
echo "Testing database connectivity..."
kubectl exec -n "$NAMESPACE" deployment/traider-backend -- \
    python -c "
import asyncio
import sys
sys.path.append('/app')
from backend.database import test_connection

async def test():
    result = await test_connection()
    if not result:
        sys.exit(1)
        
asyncio.run(test())
"

echo "✅ All smoke tests passed"
EOF

    chmod +x "$smoke_test_script"
    
    # Run smoke tests with timeout
    if timeout "$SMOKE_TEST_TIMEOUT" "$smoke_test_script" "$NAMESPACE_INACTIVE"; then
        log_success "Smoke tests passed"
        rm -f "$smoke_test_script"
        return 0
    else
        log_error "Smoke tests failed"
        rm -f "$smoke_test_script"
        return 1
    fi
}

switch_traffic() {
    log "🔄 Switching traffic to $NAMESPACE_INACTIVE..."
    
    local env_name="${NAMESPACE_INACTIVE#traider-}"
    local service_name="traider-${env_name}"
    
    # Create or update ingress to route traffic to new environment
    kubectl patch ingress traider-traffic-switch \
        --type='merge' \
        -p="{\"spec\":{\"rules\":[{\"host\":\"api.traider.io\",\"http\":{\"paths\":[{\"path\":\"/\",\"pathType\":\"Prefix\",\"backend\":{\"service\":{\"name\":\"${service_name}\",\"port\":{\"number\":8000}}}}]}}]}}" \
        2>&1 | tee -a "$LOG_FILE"
    
    if [ $? -ne 0 ]; then
        log_error "Failed to switch traffic"
        return 1
    fi
    
    # Mark that traffic has been switched (for rollback purposes)
    TRAFFIC_SWITCHED=true
    
    log_success "Traffic switched to $NAMESPACE_INACTIVE"
}

validate_traffic_switch() {
    log "✅ Validating traffic switch..."
    
    local validation_attempts=0
    local max_attempts=10
    
    while [ $validation_attempts -lt $max_attempts ]; do
        # Test that traffic is reaching the new environment
        local response
        response=$(curl -s -w "%{http_code}" -o /dev/null "https://api.traider.io/health" || echo "000")
        
        if [ "$response" = "200" ]; then
            log_success "Traffic validation successful"
            return 0
        fi
        
        validation_attempts=$((validation_attempts + 1))
        log "Validation attempt $validation_attempts/$max_attempts (HTTP $response)"
        sleep 5
    done
    
    log_error "Traffic validation failed after $max_attempts attempts"
    return 1
}

rollback_traffic() {
    log_warning "🔙 Rolling back traffic to $NAMESPACE_ACTIVE..."
    
    local active_env_name="${NAMESPACE_ACTIVE#traider-}"
    local active_service_name="traider-${active_env_name}"
    
    kubectl patch ingress traider-traffic-switch \
        --type='merge' \
        -p="{\"spec\":{\"rules\":[{\"host\":\"api.traider.io\",\"http\":{\"paths\":[{\"path\":\"/\",\"pathType\":\"Prefix\",\"backend\":{\"service\":{\"name\":\"${active_service_name}\",\"port\":{\"number\":8000}}}}]}}]}}" \
        2>&1 | tee -a "$LOG_FILE"
    
    if [ $? -eq 0 ]; then
        log_success "Traffic rolled back successfully"
        TRAFFIC_SWITCHED=false
    else
        log_error "Failed to rollback traffic - manual intervention required!"
    fi
}

cleanup_old_environment() {
    log "🗑️  Cleaning up old environment..."
    
    local should_cleanup
    read -p "Delete old environment ($NAMESPACE_ACTIVE)? [y/N] " -n 1 -r should_cleanup
    echo
    
    if [[ $should_cleanup =~ ^[Yy]$ ]]; then
        local active_env_name="${NAMESPACE_ACTIVE#traider-}"
        
        # Uninstall Helm release
        helm uninstall "traider-${active_env_name}" -n "$NAMESPACE_ACTIVE" 2>&1 | tee -a "$LOG_FILE"
        
        # Delete namespace
        kubectl delete namespace "$NAMESPACE_ACTIVE" 2>&1 | tee -a "$LOG_FILE"
        
        log_success "Old environment cleaned up"
    else
        log "Old environment preserved for manual cleanup"
    fi
}

generate_deployment_report() {
    log "📊 Generating deployment report..."
    
    local report_file="/tmp/traider_deployment_report_${TIMESTAMP}.md"
    
    cat > "$report_file" << EOF
# TRAIDER Blue-Green Deployment Report

**Deployment ID**: ${TIMESTAMP}
**Date**: $(date)
**Operator**: $(whoami)

## Deployment Details

- **Previous Active Environment**: ${NAMESPACE_ACTIVE}
- **New Active Environment**: ${NAMESPACE_INACTIVE}
- **Image Tag**: ${IMAGE_TAG}
- **Deployment Duration**: $((SECONDS / 60)) minutes

## Health Checks

- ✅ Pod Readiness: PASSED
- ✅ Application Health: PASSED
- ✅ Smoke Tests: PASSED
- ✅ Traffic Validation: PASSED

## Post-Deployment Status

\`\`\`bash
# Check current pods
kubectl get pods -n ${NAMESPACE_INACTIVE}

# Check services
kubectl get services -n ${NAMESPACE_INACTIVE}

# Check ingress
kubectl get ingress traider-traffic-switch
\`\`\`

## Rollback Instructions

If issues are detected, rollback using:

\`\`\`bash
# Quick rollback
./scripts/deploy_blue_green.sh ${NAMESPACE_INACTIVE} ${NAMESPACE_ACTIVE} ${IMAGE_TAG}

# Or manual traffic switch
kubectl patch ingress traider-traffic-switch --type='merge' \\
  -p='{"spec":{"rules":[{"host":"api.traider.io","http":{"paths":[{"path":"/","pathType":"Prefix","backend":{"service":{"name":"traider-${NAMESPACE_ACTIVE#traider-}","port":{"number":8000}}}}]}}]}}'
\`\`\`

## Logs

Full deployment logs available at: ${LOG_FILE}
EOF

    log_success "Deployment report generated: $report_file"
}

# Main deployment flow
main() {
    log "🚀 Starting TRAIDER blue-green deployment..."
    log "📋 Configuration:"
    log "   - Current Active: $NAMESPACE_ACTIVE"
    log "   - Deploy Target: $NAMESPACE_INACTIVE"
    log "   - Image Tag: $IMAGE_TAG"
    log "   - Timestamp: $TIMESTAMP"
    
    # Detect current active environment if not specified
    if [ "${1:-}" = "auto" ]; then
        NAMESPACE_ACTIVE=$(get_current_active_environment)
        NAMESPACE_INACTIVE=$([ "$NAMESPACE_ACTIVE" = "traider-blue" ] && echo "traider-green" || echo "traider-blue")
        log "🔍 Auto-detected environments: $NAMESPACE_ACTIVE -> $NAMESPACE_INACTIVE"
    fi
    
    # Execute deployment steps
    validate_prerequisites
    deploy_to_inactive_environment
    wait_for_pods_ready
    perform_health_checks
    run_smoke_tests
    switch_traffic
    
    # Wait for traffic switch to propagate
    log "⏳ Waiting for traffic switch to propagate (30s)..."
    sleep 30
    
    validate_traffic_switch
    
    log_success "🎉 Deployment completed successfully!"
    log_success "New active environment: $NAMESPACE_INACTIVE"
    
    # Optional cleanup
    cleanup_old_environment
    
    # Generate report
    generate_deployment_report
    
    log_success "✨ Blue-green deployment completed successfully!"
    log "📊 Deployment report and logs available for audit trail"
}

# Script usage
usage() {
    cat << EOF
TRAIDER Blue-Green Deployment Script

Usage: $0 [ACTIVE_NAMESPACE] [INACTIVE_NAMESPACE] [IMAGE_TAG]
   or: $0 auto [IMAGE_TAG]

Arguments:
  ACTIVE_NAMESPACE    Current active namespace (default: traider-blue)
  INACTIVE_NAMESPACE  Target deployment namespace (default: traider-green)
  IMAGE_TAG          Docker image tag to deploy (default: latest)
  auto               Auto-detect current active environment

Environment Variables:
  TIMEOUT                Deployment timeout in seconds (default: 600)
  HEALTH_CHECK_RETRIES   Number of health check attempts (default: 30)
  SMOKE_TEST_TIMEOUT     Smoke test timeout in seconds (default: 300)

Examples:
  $0                                    # Deploy latest to green (from blue)
  $0 traider-green traider-blue v1.2.3 # Deploy v1.2.3 to blue (from green)
  $0 auto v1.2.3                       # Auto-detect and deploy v1.2.3

For more information, see: infrastructure/k8s/README.md
EOF
}

# Handle help flag
if [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ]; then
    usage
    exit 0
fi

# Execute main function
main "$@" 