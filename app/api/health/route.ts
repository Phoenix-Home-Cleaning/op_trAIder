/**
 * @fileoverview Health check API route for TRAIDER V1
 * @module app/api/health/route
 *
 * @description
 * Health check endpoint that provides system status information.
 * Used for monitoring, load balancing, and debugging purposes.
 * Returns comprehensive system health metrics and status indicators.
 *
 * @performance
 * - Latency target: <50ms response time
 * - Throughput: High (monitoring endpoint)
 * - Memory usage: <500KB per request
 *
 * @risk
 * - Failure impact: LOW (monitoring only)
 * - Recovery strategy: Static fallback response
 *
 * @compliance
 * - Audit requirements: No
 * - Data retention: N/A
 *
 * @see {@link docs/architecture/monitoring.md}
 * @since 1.0.0-alpha
 * @author TRAIDER Team
 */

import { NextResponse } from 'next/server';

/**
 * Health check response interface
 *
 * @description Defines the structure of health check response data
 */
interface HealthResponse {
  status: 'healthy' | 'degraded' | 'unhealthy';
  timestamp: string;
  version: string;
  uptime: number;
  system: {
    memory: {
      used: number;
      total: number;
      percentage: number;
    };
    cpu: {
      usage: number;
    };
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

/**
 * GET /api/health
 *
 * @description
 * Returns comprehensive system health information including service status,
 * resource utilization, and system metrics. Used by monitoring systems
 * and load balancers to determine system health.
 *
 * @returns JSON response with health status information
 *
 * @performance
 * - Fast response for monitoring systems
 * - Minimal resource usage
 * - Cached system metrics where possible
 *
 * @monitoring
 * - Used by external monitoring systems
 * - Load balancer health checks
 * - Application performance monitoring
 *
 * @example
 * ```typescript
 * // GET /api/health
 * // Response: { status: "healthy", timestamp: "...", services: {...} }
 * ```
 *
 * @monitoring
 * - Metric: `health.response_time`
 * - Alert threshold: > 100ms
 */
export async function GET(): Promise<NextResponse<HealthResponse>> {
  const startTime = Date.now();

  try {
    // Get system information (Node.js specific)
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const memoryUsage = (process as any).memoryUsage();
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const uptime = (process as any).uptime();

    // Calculate memory usage percentage
    const totalMemory = memoryUsage.heapTotal;
    const usedMemory = memoryUsage.heapUsed;
    const memoryPercentage = Math.round((usedMemory / totalMemory) * 100);

    // TODO: Replace with actual service health checks
    // This is a placeholder for Phase 0
    const services = {
      database: 'online' as 'online' | 'offline' | 'degraded',
      redis: 'online' as 'online' | 'offline' | 'degraded',
      backend: 'online' as 'online' | 'offline' | 'degraded',
      marketData: 'offline' as 'online' | 'offline' | 'degraded', // Not implemented in Phase 0
    };

    // Determine overall system status
    const serviceValues = Object.values(services);
    const hasOfflineServices = serviceValues.includes('offline');
    const hasDegradedServices = serviceValues.includes('degraded');

    let overallStatus: 'healthy' | 'degraded' | 'unhealthy';
    if (services.database === 'offline') {
      overallStatus = 'unhealthy';
    } else if (hasOfflineServices || hasDegradedServices) {
      overallStatus = 'degraded';
    } else {
      overallStatus = 'healthy';
    }

    // Build health response
    const healthResponse: HealthResponse = {
      status: overallStatus,
      timestamp: new Date().toISOString(),
      version: '1.0.0-alpha',
      uptime: Math.round(uptime),
      system: {
        memory: {
          used: Math.round(usedMemory / 1024 / 1024), // MB
          total: Math.round(totalMemory / 1024 / 1024), // MB
          percentage: memoryPercentage,
        },
        cpu: {
          usage: 0, // TODO: Implement CPU usage monitoring
        },
      },
      services,
      phase: 'Phase 0 - Setup & Foundation',
      environment: process.env.NODE_ENV || 'development',
    };

    // Log response time for monitoring
    const responseTime = Date.now() - startTime;
    if (responseTime > 100) {
      // In production: send to monitoring system
    }

    // Return appropriate HTTP status based on health
    const httpStatus = overallStatus === 'healthy' ? 200 : overallStatus === 'degraded' ? 200 : 503;

    return NextResponse.json(healthResponse, { status: httpStatus });
  } catch {
    // Log health check error for monitoring
    // In production: send to monitoring system

    // Return unhealthy status on error
    const errorResponse: HealthResponse = {
      status: 'unhealthy',
      timestamp: new Date().toISOString(),
      version: '1.0.0-alpha',
      uptime: 0,
      system: {
        memory: { used: 0, total: 0, percentage: 0 },
        cpu: { usage: 0 },
      },
      services: {
        database: 'offline',
        redis: 'offline',
        backend: 'offline',
        marketData: 'offline',
      },
      phase: 'Phase 0 - Setup & Foundation',
      environment: process.env.NODE_ENV || 'development',
    };

    return NextResponse.json(errorResponse, { status: 503 });
  }
}

/**
 * HEAD /api/health
 *
 * @description
 * Lightweight health check that returns only HTTP status code.
 * Used by load balancers and monitoring systems that only need
 * to know if the service is responsive.
 *
 * @returns HTTP status code only (no body)
 */
export async function HEAD(): Promise<NextResponse> {
  try {
    // Perform minimal health check
    const isHealthy = true; // TODO: Add actual health logic

    return new NextResponse(null, {
      status: isHealthy ? 200 : 503,
      headers: {
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'X-Health-Status': isHealthy ? 'healthy' : 'unhealthy',
        'X-Service-Version': '1.0.0-alpha',
      },
    });
  } catch {
    return new NextResponse(null, { status: 503 });
  }
}
