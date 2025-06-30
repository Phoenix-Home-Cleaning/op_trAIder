/**
 * @fileoverview Unified API route for TRAIDER V1 - Windows compatibility
 * @module app/api/route
 * 
 * @description
 * Single API route file to handle all endpoints and avoid Windows EISDIR issues.
 * This is a Phase 0 workaround for the Next.js 15 Windows filesystem problem.
 * Authentication is now handled by NextAuth.js routes.
 * 
 * @performance
 * - All endpoints: <200ms response time
 * - Memory efficient single route handler
 * 
 * @risk
 * - Failure impact: MEDIUM (consolidated API)
 * - Recovery strategy: Individual endpoint fallbacks
 * 
 * @since 1.0.0-alpha
 * @author TRAIDER Team
 */

import { NextRequest, NextResponse } from 'next/server';

// Health check response interface
interface HealthResponse {
  status: 'healthy' | 'degraded' | 'unhealthy';
  timestamp: string;
  uptime: number;
  version: string;
  services: {
    database: 'healthy' | 'degraded' | 'unhealthy';
    cache: 'healthy' | 'degraded' | 'unhealthy';
    external_apis: 'healthy' | 'degraded' | 'unhealthy';
  };
  system: {
    memory_usage: number;
    memory_total: number;
    memory_percent: number;
  };
}

/**
 * GET /api - API information and health check
 */
export async function GET(request: NextRequest): Promise<NextResponse> {
  const url = new URL(request.url);
  const endpoint = url.searchParams.get('endpoint');
  
  try {
    // Route to specific endpoint based on query parameter
    switch (endpoint) {
      case 'health':
        return handleHealthCheck();
      case 'info':
        return handleApiInfo();
      default:
        return NextResponse.json({
          name: 'TRAIDER V1 API',
          version: '1.0.0-alpha',
          status: 'active',
          phase: 'Phase 0 - Foundation',
          endpoints: {
            health: '/api?endpoint=health',
            info: '/api?endpoint=info',
          },
          authentication: 'Handled by NextAuth.js at /api/auth/*',
          note: 'Unified API endpoint for Windows compatibility',
        });
    }
  } catch (error) {
    return NextResponse.json(
      { error: 'Internal server error', message: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    );
  }
}

/**
 * POST /api - Future POST operations (authentication removed)
 */
export async function POST(): Promise<NextResponse> {
  return NextResponse.json(
    { 
      error: 'Authentication moved to NextAuth.js',
      auth_endpoints: {
        signin: '/api/auth/signin',
        signout: '/api/auth/signout',
        session: '/api/auth/session',
      },
      message: 'Use NextAuth.js endpoints for authentication'
    },
    { status: 410 } // Gone - resource permanently moved
  );
}

/**
 * HEAD /api - Quick health check
 */
export async function HEAD(): Promise<NextResponse> {
  try {
    return new NextResponse(null, { status: 200 });
  } catch {
    return new NextResponse(null, { status: 500 });
  }
}

/**
 * Handle health check requests
 */
async function handleHealthCheck(): Promise<NextResponse<HealthResponse>> {
  try {
    const memoryUsage = process.memoryUsage();
    const uptime = process.uptime();

    const healthResponse: HealthResponse = {
      status: 'healthy',
      timestamp: new Date().toISOString(),
      uptime: Math.floor(uptime),
      version: '1.0.0-alpha',
      services: {
        database: 'healthy', // Phase 0: Placeholder
        cache: 'healthy',    // Phase 0: Placeholder
        external_apis: 'healthy', // Phase 0: Placeholder
      },
      system: {
        memory_usage: Math.round(memoryUsage.heapUsed / 1024 / 1024), // MB
        memory_total: Math.round(memoryUsage.heapTotal / 1024 / 1024), // MB
        memory_percent: Math.round((memoryUsage.heapUsed / memoryUsage.heapTotal) * 100),
      },
    };

    return NextResponse.json(healthResponse);
  } catch (error) {
    return NextResponse.json(
      {
        status: 'unhealthy',
        timestamp: new Date().toISOString(),
        uptime: 0,
        version: '1.0.0-alpha',
        services: {
          database: 'unhealthy',
          cache: 'unhealthy',
          external_apis: 'unhealthy',
        },
        system: {
          memory_usage: 0,
          memory_total: 0,
          memory_percent: 0,
        },
        error: error instanceof Error ? error.message : 'Unknown error',
      } as HealthResponse & { error: string },
      { status: 500 }
    );
  }
}

/**
 * Handle API information requests
 */
async function handleApiInfo(): Promise<NextResponse> {
  return NextResponse.json({
    name: 'TRAIDER V1 Unified API',
    version: '1.0.0-alpha',
    description: 'Unified API endpoint for TRAIDER V1 - Windows compatibility workaround',
    phase: 'Phase 0 - Foundation',
    endpoints: {
      health: {
        path: '/api?endpoint=health',
        method: 'GET',
        description: 'System health check'
      },
      info: {
        path: '/api?endpoint=info',
        method: 'GET',
        description: 'API information'
      }
    },
    authentication: {
      provider: 'NextAuth.js',
      endpoints: {
        signin: '/api/auth/signin',
        signout: '/api/auth/signout',
        session: '/api/auth/session',
        providers: '/api/auth/providers'
      },
      note: 'Authentication handled by NextAuth.js with FastAPI backend integration'
    },
    note: 'This unified endpoint exists to work around Windows EISDIR issues in Next.js 15'
  });
} 