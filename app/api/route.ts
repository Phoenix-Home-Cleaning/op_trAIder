/**
 * @fileoverview Unified API route for TRAIDER V1 - Windows compatibility
 * @module app/api/route
 * 
 * @description
 * Single API route file to handle all endpoints and avoid Windows EISDIR issues.
 * This is a Phase 0 workaround for the Next.js 15 Windows filesystem problem.
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

// Authentication interfaces
interface LoginRequest {
  username: string;
  password: string;
}

interface LoginResponse {
  success: boolean;
  message: string;
  token?: string;
  user?: {
    id: string;
    username: string;
    role: string;
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
      case 'auth':
        return handleAuthInfo();
      default:
        return NextResponse.json({
          name: 'TRAIDER V1 API',
          version: '1.0.0-alpha',
          status: 'active',
          phase: 'Phase 0 - Foundation',
          endpoints: {
            health: '/api?endpoint=health',
            auth: '/api?endpoint=auth',
            login: 'POST /api (with credentials)',
          },
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
 * POST /api - Authentication and other POST operations
 */
export async function POST(request: NextRequest): Promise<NextResponse> {
  const url = new URL(request.url);
  const endpoint = url.searchParams.get('endpoint');
  
  try {
    // Handle authentication by default, or route based on endpoint parameter
    if (endpoint === 'auth' || !endpoint) {
      return handleLogin(request);
    }
    
    return NextResponse.json(
      { error: 'Endpoint not found', available_endpoints: ['auth'] },
      { status: 404 }
    );
  } catch (error) {
    return NextResponse.json(
      { error: 'Internal server error', message: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    );
  }
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
 * Handle authentication info requests
 */
async function handleAuthInfo(): Promise<NextResponse> {
  return NextResponse.json({
    endpoint: '/api?endpoint=auth',
    methods: ['GET', 'POST'],
    version: '1.0.0-alpha',
    description: 'Authentication endpoint for TRAIDER V1',
    phase: 'Phase 0 - Demo Implementation',
    demo_credentials: {
      admin: { username: 'admin', password: 'password', role: 'administrator' },
      demo: { username: 'demo', password: 'demo123', role: 'trader' },
    },
  });
}

/**
 * Handle login requests
 */
async function handleLogin(request: NextRequest): Promise<NextResponse<LoginResponse>> {
  try {
    const body: LoginRequest = await request.json();
    const { username, password } = body;

    if (!username || !password) {
      return NextResponse.json(
        {
          success: false,
          message: 'Username and password are required',
        },
        { status: 400 }
      );
    }

    // Phase 0 demo credentials
    const isValidCredentials =
      (username === 'admin' && password === 'password') ||
      (username === 'demo' && password === 'demo123');

    if (!isValidCredentials) {
      return NextResponse.json(
        {
          success: false,
          message: 'Invalid username or password',
        },
        { status: 401 }
      );
    }

    const token = `traider-jwt-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    
    const user = {
      id: username === 'admin' ? '1' : '2',
      username,
      role: username === 'admin' ? 'administrator' : 'trader',
    };

    return NextResponse.json({
      success: true,
      message: 'Authentication successful',
      token,
      user,
    });
  } catch {
    return NextResponse.json(
      {
        success: false,
        message: 'Internal server error',
      },
      { status: 500 }
    );
  }
} 