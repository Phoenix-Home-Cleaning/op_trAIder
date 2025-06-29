# TRAIDER V1 Health Monitoring API

## Overview

Health monitoring API providing comprehensive system health checks, service status monitoring, and performance metrics for the TRAIDER V1 trading platform.

## Endpoints

### GET /api/health
Comprehensive system health check returning detailed status information.

**Response:**
```typescript
{
  status: 'healthy' | 'degraded' | 'unhealthy';
  timestamp: string;
  version: string;
  uptime: number;
  system: {
    memory: { used: number; total: number; percentage: number; };
    cpu: { usage: number; };
  };
  services: {
    database: 'online' | 'offline' | 'degraded';
    redis: 'online' | 'offline' | 'degraded';
    backend: 'online' | 'offline' | 'degraded';
    marketData: 'online' | 'offline' | 'degraded';
  };
  phase: string;
  environment: string;
}
```

### HEAD /api/health
Lightweight health check returning only HTTP status code for load balancers.

## Health Status Levels

- **Healthy** (200): All systems operational
- **Degraded** (200): Some non-critical services offline
- **Unhealthy** (503): Critical services offline

## Performance Standards

- **GET Response Time**: < 50ms
- **HEAD Response Time**: < 10ms
- **Memory Usage**: < 500KB per request
- **Availability**: 99.99%

## Integration

- Load balancer health checks
- Kubernetes liveness/readiness probes
- Monitoring systems (Prometheus, Grafana)
- APM tools integration

## Monitoring Metrics

- Response time tracking
- Service availability monitoring
- System resource utilization
- Error rate tracking 