#!/bin/bash

# 🚀 TRAIDER V1 - Docker Deployment Script
# Institutional-grade deployment with health checks and rollback
# 
# Usage:
#   ./scripts/docker-deploy.sh [environment] [action]
#   
# Examples:
#   ./scripts/docker-deploy.sh production deploy
#   ./scripts/docker-deploy.sh staging rollback
#   ./scripts/docker-deploy.sh development restart

set -euo pipefail

# =============================================================================
# CONFIGURATION
# =============================================================================

readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
readonly TIMESTAMP=$(date +%Y%m%d_%H%M%S)
readonly LOG_FILE="$PROJECT_ROOT/logs/deployment_$TIMESTAMP.log"

# Environment configuration
ENVIRONMENT="${1:-development}"
ACTION="${2:-deploy}"

# Docker configuration
readonly COMPOSE_FILE="docker-compose.yml"
readonly DEV_COMPOSE_FILE="docker-compose.dev.yml"
readonly NETWORK_NAME="traider-network"

# Health check configuration
readonly HEALTH_CHECK_TIMEOUT=300
readonly HEALTH_CHECK_INTERVAL=10
readonly MAX_RETRIES=30

# =============================================================================
# LOGGING & UTILITIES
# =============================================================================

# Create logs directory
mkdir -p "$PROJECT_ROOT/logs"

# Logging functions
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

log_info() {
    log "INFO: $*"
}

log_warn() {
    log "WARN: $*"
}

log_error() {
    log "ERROR: $*"
}

log_success() {
    log "SUCCESS: $*"
}

# Error handling
cleanup() {
    local exit_code=$?
    if [ $exit_code -ne 0 ]; then
        log_error "Deployment failed with exit code $exit_code"
        log_info "Check logs at: $LOG_FILE"
    fi
    exit $exit_code
}

trap cleanup EXIT

# =============================================================================
# VALIDATION FUNCTIONS
# =============================================================================

validate_environment() {
    log_info "Validating deployment environment..."
    
    # Check Docker is installed and running
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        log_error "Docker daemon is not running"
        exit 1
    fi
    
    # Check Docker Compose is available
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed"
        exit 1
    fi
    
    # Check environment file exists
    local env_file=".env"
    if [ "$ENVIRONMENT" = "development" ]; then
        env_file=".env.dev"
    fi
    
    if [ ! -f "$PROJECT_ROOT/$env_file" ]; then
        log_error "Environment file $env_file not found"
        log_info "Copy .env.docker to $env_file and configure it"
        exit 1
    fi
    
    log_success "Environment validation passed"
}

validate_secrets() {
    log_info "Validating secrets configuration..."
    
    local env_file=".env"
    if [ "$ENVIRONMENT" = "development" ]; then
        env_file=".env.dev"
    fi
    
    # Check for placeholder values
    if grep -q "CHANGE_ME_" "$PROJECT_ROOT/$env_file"; then
        log_error "Found placeholder values in $env_file"
        log_error "Please replace all CHANGE_ME_ values with secure secrets"
        exit 1
    fi
    
    # Validate critical secrets exist
    local required_vars=(
        "POSTGRES_PASSWORD"
        "JWT_SECRET"
        "NEXTAUTH_SECRET"
        "ENCRYPTION_KEY"
    )
    
    for var in "${required_vars[@]}"; do
        if ! grep -q "^$var=" "$PROJECT_ROOT/$env_file"; then
            log_error "Required environment variable $var not found"
            exit 1
        fi
    done
    
    log_success "Secrets validation passed"
}

validate_resources() {
    log_info "Validating system resources..."
    
    # Check available disk space (minimum 10GB)
    local available_space
    available_space=$(df "$PROJECT_ROOT" | awk 'NR==2 {print $4}')
    local min_space=10485760  # 10GB in KB
    
    if [ "$available_space" -lt "$min_space" ]; then
        log_error "Insufficient disk space. Available: ${available_space}KB, Required: ${min_space}KB"
        exit 1
    fi
    
    # Check available memory (minimum 4GB)
    local available_memory
    available_memory=$(free | awk 'NR==2{printf "%.0f", $7/1024/1024}')
    local min_memory=4
    
    if [ "$available_memory" -lt "$min_memory" ]; then
        log_warn "Low available memory: ${available_memory}GB (recommended: 8GB+)"
    fi
    
    log_success "Resource validation passed"
}

# =============================================================================
# NETWORK MANAGEMENT
# =============================================================================

setup_network() {
    log_info "Setting up Docker network..."
    
    if ! docker network ls | grep -q "$NETWORK_NAME"; then
        log_info "Creating network: $NETWORK_NAME"
        docker network create "$NETWORK_NAME" --driver bridge
    else
        log_info "Network $NETWORK_NAME already exists"
    fi
}

# =============================================================================
# DEPLOYMENT FUNCTIONS
# =============================================================================

build_images() {
    log_info "Building Docker images..."
    
    local compose_args=()
    if [ "$ENVIRONMENT" = "development" ]; then
        compose_args+=("-f" "$DEV_COMPOSE_FILE")
    else
        compose_args+=("-f" "$COMPOSE_FILE")
    fi
    
    # Build with no cache for production
    if [ "$ENVIRONMENT" = "production" ]; then
        compose_args+=("--no-cache")
    fi
    
    docker-compose "${compose_args[@]}" build
    
    log_success "Image build completed"
}

deploy_services() {
    log_info "Deploying services..."
    
    local compose_args=()
    if [ "$ENVIRONMENT" = "development" ]; then
        compose_args+=("-f" "$DEV_COMPOSE_FILE")
    else
        compose_args+=("-f" "$COMPOSE_FILE")
    fi
    
    # Start services in detached mode
    docker-compose "${compose_args[@]}" up -d
    
    log_success "Services deployed"
}

wait_for_health() {
    log_info "Waiting for services to become healthy..."
    
    local services=("postgres" "redis" "backend" "frontend")
    local healthy_services=0
    local attempts=0
    
    while [ $healthy_services -lt ${#services[@]} ] && [ $attempts -lt $MAX_RETRIES ]; do
        healthy_services=0
        
        for service in "${services[@]}"; do
            if docker-compose ps -q "$service" | xargs docker inspect --format="{{.State.Health.Status}}" 2>/dev/null | grep -q "healthy"; then
                ((healthy_services++))
            fi
        done
        
        log_info "Healthy services: $healthy_services/${#services[@]}"
        
        if [ $healthy_services -lt ${#services[@]} ]; then
            sleep $HEALTH_CHECK_INTERVAL
            ((attempts++))
        fi
    done
    
    if [ $healthy_services -eq ${#services[@]} ]; then
        log_success "All services are healthy"
    else
        log_error "Health check timeout. Only $healthy_services/${#services[@]} services are healthy"
        return 1
    fi
}

run_integration_tests() {
    log_info "Running integration tests..."
    
    # Test frontend accessibility
    if curl -f http://localhost:3000/api > /dev/null 2>&1; then
        log_success "Frontend health check passed"
    else
        log_error "Frontend health check failed"
        return 1
    fi
    
    # Test backend API
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        log_success "Backend health check passed"
    else
        log_error "Backend health check failed"
        return 1
    fi
    
    # Test database connectivity
    if docker-compose exec -T postgres pg_isready -U traider > /dev/null 2>&1; then
        log_success "Database health check passed"
    else
        log_error "Database health check failed"
        return 1
    fi
    
    log_success "Integration tests passed"
}

# =============================================================================
# BACKUP & ROLLBACK
# =============================================================================

create_backup() {
    log_info "Creating backup before deployment..."
    
    local backup_dir="$PROJECT_ROOT/backups/$TIMESTAMP"
    mkdir -p "$backup_dir"
    
    # Backup database
    if docker-compose ps postgres | grep -q "Up"; then
        log_info "Backing up database..."
        docker-compose exec -T postgres pg_dump -U traider traider > "$backup_dir/database.sql"
    fi
    
    # Backup volumes
    log_info "Backing up Docker volumes..."
    docker run --rm -v traider_postgres_data:/data -v "$backup_dir":/backup alpine tar czf /backup/postgres_data.tar.gz -C /data .
    docker run --rm -v traider_redis_data:/data -v "$backup_dir":/backup alpine tar czf /backup/redis_data.tar.gz -C /data .
    
    log_success "Backup created at: $backup_dir"
    echo "$backup_dir" > "$PROJECT_ROOT/.last_backup"
}

rollback_deployment() {
    log_warn "Initiating rollback..."
    
    if [ ! -f "$PROJECT_ROOT/.last_backup" ]; then
        log_error "No backup found for rollback"
        exit 1
    fi
    
    local backup_dir
    backup_dir=$(cat "$PROJECT_ROOT/.last_backup")
    
    if [ ! -d "$backup_dir" ]; then
        log_error "Backup directory not found: $backup_dir"
        exit 1
    fi
    
    # Stop current services
    docker-compose down
    
    # Restore database
    if [ -f "$backup_dir/database.sql" ]; then
        log_info "Restoring database..."
        docker-compose up -d postgres
        sleep 30
        docker-compose exec -T postgres psql -U traider -d traider < "$backup_dir/database.sql"
    fi
    
    # Restore volumes
    if [ -f "$backup_dir/postgres_data.tar.gz" ]; then
        log_info "Restoring PostgreSQL data..."
        docker run --rm -v traider_postgres_data:/data -v "$backup_dir":/backup alpine tar xzf /backup/postgres_data.tar.gz -C /data
    fi
    
    if [ -f "$backup_dir/redis_data.tar.gz" ]; then
        log_info "Restoring Redis data..."
        docker run --rm -v traider_redis_data:/data -v "$backup_dir":/backup alpine tar xzf /backup/redis_data.tar.gz -C /data
    fi
    
    log_success "Rollback completed"
}

# =============================================================================
# MONITORING & MAINTENANCE
# =============================================================================

show_status() {
    log_info "Service Status:"
    docker-compose ps
    
    log_info "Resource Usage:"
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}"
    
    log_info "Service Logs (last 20 lines):"
    docker-compose logs --tail=20
}

cleanup_old_images() {
    log_info "Cleaning up old Docker images..."
    
    # Remove dangling images
    docker image prune -f
    
    # Remove old images (keep last 3 versions)
    docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.ID}}\t{{.CreatedAt}}" | grep traider | tail -n +4 | awk '{print $3}' | xargs -r docker rmi -f
    
    log_success "Image cleanup completed"
}

# =============================================================================
# MAIN DEPLOYMENT LOGIC
# =============================================================================

main() {
    log_info "Starting TRAIDER V1 Docker deployment"
    log_info "Environment: $ENVIRONMENT"
    log_info "Action: $ACTION"
    log_info "Timestamp: $TIMESTAMP"
    
    cd "$PROJECT_ROOT"
    
    case "$ACTION" in
        "deploy")
            validate_environment
            validate_secrets
            validate_resources
            setup_network
            create_backup
            build_images
            deploy_services
            wait_for_health
            run_integration_tests
            cleanup_old_images
            show_status
            log_success "Deployment completed successfully!"
            ;;
        
        "rollback")
            rollback_deployment
            wait_for_health
            run_integration_tests
            show_status
            log_success "Rollback completed successfully!"
            ;;
        
        "restart")
            log_info "Restarting services..."
            docker-compose restart
            wait_for_health
            show_status
            log_success "Services restarted successfully!"
            ;;
        
        "stop")
            log_info "Stopping services..."
            docker-compose down
            log_success "Services stopped successfully!"
            ;;
        
        "status")
            show_status
            ;;
        
        "logs")
            docker-compose logs -f
            ;;
        
        *)
            log_error "Unknown action: $ACTION"
            log_info "Available actions: deploy, rollback, restart, stop, status, logs"
            exit 1
            ;;
    esac
}

# =============================================================================
# SCRIPT EXECUTION
# =============================================================================

# Verify script is run from project root or scripts directory
if [ ! -f "package.json" ] && [ ! -f "../package.json" ]; then
    log_error "This script must be run from the project root or scripts directory"
    exit 1
fi

# Change to project root if run from scripts directory
if [ -f "../package.json" ]; then
    cd ..
fi

# Execute main function
main "$@" 