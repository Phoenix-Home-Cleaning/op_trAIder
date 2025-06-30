# Deployment Procedures

## Overview

This document outlines comprehensive deployment procedures for the TRAIDER V1 trading platform, ensuring safe, reliable, and automated deployments across all environments.

## Deployment Strategy

### Blue-Green Deployment
- **Zero Downtime**: Seamless switching between environments
- **Risk Mitigation**: Instant rollback capability
- **Testing**: Full production validation before switch
- **Monitoring**: Comprehensive health checks during deployment

### Environment Progression
```
Development → Testing → Staging → Production
     ↓           ↓        ↓          ↓
   Feature    Integration System   Live
   Testing     Testing   Testing   Trading
```

## Environment Configuration

### Development Environment
```yaml
# development.yml
environment: development
replicas: 1
resources:
  cpu: 500m
  memory: 512Mi
database:
  host: localhost
  name: traider_dev
features:
  live_trading: false
  debug_mode: true
```

### Staging Environment
```yaml
# staging.yml
environment: staging
replicas: 2
resources:
  cpu: 1000m
  memory: 1Gi
database:
  host: staging-db.traider.local
  name: traider_staging
features:
  live_trading: false
  debug_mode: false
```

### Production Environment
```yaml
# production.yml
environment: production
replicas: 3
resources:
  cpu: 2000m
  memory: 2Gi
database:
  host: prod-db.traider.com
  name: traider_prod
features:
  live_trading: true
  debug_mode: false
```

## Automated Deployment Pipeline

### CI/CD Workflow
```yaml
name: Deploy TRAIDER V1
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Tests
        run: |
          npm test
          npm run test:integration
          npm run test:e2e
          
  security:
    runs-on: ubuntu-latest
    steps:
      - name: Security Scan
        run: |
          npm audit
          npm run security:scan
          
  build:
    needs: [test, security]
    runs-on: ubuntu-latest
    steps:
      - name: Build Images
        run: |
          docker build -t traider-frontend .
          docker build -f Dockerfile.backend -t traider-backend .
          
  deploy-staging:
    needs: build
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to Staging
        run: |
          kubectl apply -f k8s/staging/
          kubectl rollout status deployment/traider-frontend
          kubectl rollout status deployment/traider-backend
          
  deploy-production:
    needs: deploy-staging
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    environment: production
    steps:
      - name: Deploy to Production
        run: |
          ./scripts/blue-green-deploy.sh
```

### Deployment Scripts

#### Blue-Green Deployment Script
```bash
#!/bin/bash
# scripts/blue-green-deploy.sh

set -e

NAMESPACE="traider-prod"
CURRENT_ENV=$(kubectl get service traider-frontend -o jsonpath='{.spec.selector.version}')
NEW_ENV=$([ "$CURRENT_ENV" = "blue" ] && echo "green" || echo "blue")

echo "🚀 Starting blue-green deployment..."
echo "Current environment: $CURRENT_ENV"
echo "Deploying to: $NEW_ENV"

# Deploy new version
echo "📦 Deploying new version to $NEW_ENV environment..."
kubectl apply -f k8s/production/frontend-$NEW_ENV.yaml
kubectl apply -f k8s/production/backend-$NEW_ENV.yaml

# Wait for deployment to be ready
echo "⏳ Waiting for deployment to be ready..."
kubectl rollout status deployment/traider-frontend-$NEW_ENV -n $NAMESPACE
kubectl rollout status deployment/traider-backend-$NEW_ENV -n $NAMESPACE

# Run health checks
echo "🏥 Running health checks..."
./scripts/health-check.sh $NEW_ENV

# Switch traffic
echo "🔄 Switching traffic to $NEW_ENV..."
kubectl patch service traider-frontend -p '{"spec":{"selector":{"version":"'$NEW_ENV'"}}}'
kubectl patch service traider-backend -p '{"spec":{"selector":{"version":"'$NEW_ENV'"}}}'

# Verify deployment
echo "✅ Verifying deployment..."
sleep 30
./scripts/health-check.sh production

# Cleanup old version
echo "🧹 Cleaning up $CURRENT_ENV environment..."
kubectl delete deployment traider-frontend-$CURRENT_ENV -n $NAMESPACE
kubectl delete deployment traider-backend-$CURRENT_ENV -n $NAMESPACE

echo "🎉 Blue-green deployment completed successfully!"
```

#### Health Check Script
```bash
#!/bin/bash
# scripts/health-check.sh

ENVIRONMENT=${1:-production}
BASE_URL="https://api.traider.com"

if [ "$ENVIRONMENT" = "staging" ]; then
    BASE_URL="https://staging-api.traider.com"
elif [ "$ENVIRONMENT" = "blue" ] || [ "$ENVIRONMENT" = "green" ]; then
    BASE_URL="https://$ENVIRONMENT-api.traider.com"
fi

echo "🏥 Running health checks for $ENVIRONMENT environment..."

# Basic health check
echo "Checking basic health..."
response=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/api/health")
if [ "$response" != "200" ]; then
    echo "❌ Health check failed: $response"
    exit 1
fi

# Detailed health check
echo "Checking detailed health..."
response=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/api/health/detailed")
if [ "$response" != "200" ]; then
    echo "❌ Detailed health check failed: $response"
    exit 1
fi

# Database connectivity
echo "Checking database connectivity..."
response=$(curl -s "$BASE_URL/api/health/detailed" | jq -r '.database.status')
if [ "$response" != "healthy" ]; then
    echo "❌ Database health check failed: $response"
    exit 1
fi

# Authentication system
echo "Checking authentication system..."
response=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/api/auth/csrf")
if [ "$response" != "200" ]; then
    echo "❌ Authentication health check failed: $response"
    exit 1
fi

echo "✅ All health checks passed!"
```

## Manual Deployment Procedures

### Emergency Deployment
```bash
# Emergency deployment procedure
echo "🚨 EMERGENCY DEPLOYMENT PROCEDURE"

# 1. Immediate rollback
kubectl rollout undo deployment/traider-frontend
kubectl rollout undo deployment/traider-backend

# 2. Verify rollback
kubectl rollout status deployment/traider-frontend
kubectl rollout status deployment/traider-backend

# 3. Run health checks
./scripts/health-check.sh production

# 4. Notify team
echo "Emergency rollback completed. Investigating issue..."
```

### Hotfix Deployment
```bash
# Hotfix deployment procedure
echo "🔥 HOTFIX DEPLOYMENT PROCEDURE"

# 1. Create hotfix branch
git checkout -b hotfix/critical-fix

# 2. Apply fix and test
npm test
npm run test:integration

# 3. Build and deploy
docker build -t traider-frontend:hotfix .
kubectl set image deployment/traider-frontend frontend=traider-frontend:hotfix

# 4. Monitor deployment
kubectl rollout status deployment/traider-frontend
./scripts/health-check.sh production
```

## Database Migrations

### Migration Strategy
```python
# Database migration procedure
class MigrationProcedure:
    def __init__(self):
        self.backup_created = False
        self.migration_applied = False
        
    def execute_migration(self, migration_file):
        try:
            # 1. Create backup
            self.create_backup()
            
            # 2. Apply migration
            self.apply_migration(migration_file)
            
            # 3. Verify migration
            self.verify_migration()
            
            # 4. Update application
            self.deploy_application()
            
        except Exception as e:
            self.rollback_migration()
            raise e
    
    def create_backup(self):
        """Create database backup before migration"""
        subprocess.run([
            'pg_dump', 
            '-h', 'prod-db.traider.com',
            '-U', 'traider_user',
            '-d', 'traider_prod',
            '-f', f'backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.sql'
        ])
        self.backup_created = True
    
    def apply_migration(self, migration_file):
        """Apply database migration"""
        subprocess.run(['alembic', 'upgrade', 'head'])
        self.migration_applied = True
    
    def verify_migration(self):
        """Verify migration was successful"""
        # Run migration verification tests
        subprocess.run(['python', '-m', 'pytest', 'tests/migration/'])
    
    def rollback_migration(self):
        """Rollback migration if something goes wrong"""
        if self.migration_applied:
            subprocess.run(['alembic', 'downgrade', '-1'])
        
        if self.backup_created:
            print("Database backup available for manual restore if needed")
```

### Migration Checklist
```markdown
## Pre-Migration Checklist
- [ ] Backup database
- [ ] Test migration on staging
- [ ] Verify rollback procedure
- [ ] Schedule maintenance window
- [ ] Notify stakeholders

## Migration Execution
- [ ] Stop application services
- [ ] Apply database migration
- [ ] Verify migration success
- [ ] Start application services
- [ ] Run health checks

## Post-Migration Checklist
- [ ] Verify application functionality
- [ ] Monitor system performance
- [ ] Confirm trading operations
- [ ] Update documentation
- [ ] Notify completion
```

## Rollback Procedures

### Automatic Rollback Triggers
```yaml
# Automatic rollback conditions
rollback_triggers:
  error_rate:
    threshold: 5%
    duration: 5m
    
  latency:
    p95_threshold: 1000ms
    duration: 3m
    
  health_check:
    consecutive_failures: 3
    
  manual:
    trigger: emergency_stop
```

### Rollback Script
```bash
#!/bin/bash
# scripts/rollback.sh

REASON=${1:-"Manual rollback"}
ENVIRONMENT=${2:-"production"}

echo "🔄 Starting rollback procedure..."
echo "Reason: $REASON"
echo "Environment: $ENVIRONMENT"

# 1. Stop current deployment
kubectl rollout pause deployment/traider-frontend
kubectl rollout pause deployment/traider-backend

# 2. Rollback to previous version
kubectl rollout undo deployment/traider-frontend
kubectl rollout undo deployment/traider-backend

# 3. Wait for rollback completion
kubectl rollout status deployment/traider-frontend
kubectl rollout status deployment/traider-backend

# 4. Verify rollback
./scripts/health-check.sh $ENVIRONMENT

# 5. Log rollback
echo "$(date): Rollback completed - $REASON" >> /var/log/traider/deployments.log

echo "✅ Rollback completed successfully!"
```

## Monitoring and Alerting

### Deployment Monitoring
```typescript
// Deployment monitoring configuration
const deploymentMonitoring = {
  metrics: {
    deployment_duration: 'histogram',
    deployment_success_rate: 'counter',
    rollback_frequency: 'counter',
    health_check_status: 'gauge'
  },
  
  alerts: {
    deployment_failure: {
      condition: 'deployment_success_rate < 0.95',
      severity: 'critical',
      notification: ['slack', 'email', 'pagerduty']
    },
    deployment_timeout: {
      condition: 'deployment_duration > 30m',
      severity: 'warning',
      notification: ['slack', 'email']
    },
    frequent_rollbacks: {
      condition: 'rollback_frequency > 3 per day',
      severity: 'warning',
      notification: ['slack', 'email']
    }
  }
};
```

### Post-Deployment Verification
```bash
#!/bin/bash
# scripts/post-deployment-verification.sh

echo "🔍 Running post-deployment verification..."

# 1. Health checks
./scripts/health-check.sh production

# 2. Performance verification
echo "Checking performance metrics..."
response_time=$(curl -s -w "%{time_total}" -o /dev/null https://api.traider.com/api/health)
if (( $(echo "$response_time > 1.0" | bc -l) )); then
    echo "⚠️  Warning: Response time is high: ${response_time}s"
fi

# 3. Trading system verification
echo "Verifying trading system functionality..."
# Add trading-specific verification tests

# 4. Security verification
echo "Running security checks..."
npm run security:verify

# 5. Generate deployment report
echo "Generating deployment report..."
./scripts/generate-deployment-report.sh

echo "✅ Post-deployment verification completed!"
```

## Security Considerations

### Deployment Security
```yaml
# Security measures during deployment
security:
  image_scanning:
    - vulnerability_scan
    - malware_scan
    - license_compliance
    
  secrets_management:
    - rotate_secrets
    - validate_encryption
    - audit_access
    
  access_control:
    - verify_permissions
    - audit_deployment_access
    - validate_signatures
```

### Secret Rotation
```bash
#!/bin/bash
# scripts/rotate-secrets.sh

echo "🔐 Rotating deployment secrets..."

# 1. Generate new secrets
NEW_JWT_SECRET=$(openssl rand -base64 32)
NEW_DB_PASSWORD=$(openssl rand -base64 16)

# 2. Update secrets in vault
kubectl create secret generic traider-secrets \
  --from-literal=jwt-secret=$NEW_JWT_SECRET \
  --from-literal=db-password=$NEW_DB_PASSWORD \
  --dry-run=client -o yaml | kubectl apply -f -

# 3. Restart deployments to pick up new secrets
kubectl rollout restart deployment/traider-frontend
kubectl rollout restart deployment/traider-backend

echo "✅ Secret rotation completed!"
```

## Disaster Recovery

### Backup and Restore
```bash
#!/bin/bash
# scripts/disaster-recovery.sh

RECOVERY_TYPE=${1:-"full"}

echo "🆘 Starting disaster recovery procedure..."
echo "Recovery type: $RECOVERY_TYPE"

case $RECOVERY_TYPE in
  "database")
    echo "Restoring database from backup..."
    ./scripts/restore-database.sh
    ;;
  "application")
    echo "Restoring application from last known good state..."
    ./scripts/restore-application.sh
    ;;
  "full")
    echo "Full system recovery..."
    ./scripts/restore-database.sh
    ./scripts/restore-application.sh
    ;;
esac

echo "✅ Disaster recovery completed!"
```

## Documentation and Compliance

### Deployment Documentation
- **Change Log**: Record of all deployments and changes
- **Rollback History**: History of rollbacks and reasons
- **Performance Impact**: Performance metrics before/after deployment
- **Security Audit**: Security verification results

### Compliance Requirements
- **Audit Trail**: Complete deployment audit trail
- **Change Approval**: Required approvals for production deployments
- **Testing Evidence**: Proof of testing completion
- **Risk Assessment**: Risk evaluation for each deployment

## See Also

- [Infrastructure Documentation](../infrastructure/)
- [Performance Benchmarks](../performance/benchmarks.md)
- [Security Guidelines](../security/security-guidelines.md)
- [Testing Strategy](../testing/testing-strategy.md) 