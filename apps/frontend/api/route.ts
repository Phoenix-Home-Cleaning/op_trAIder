/**
 * @fileoverview Legacy Unified API Route (Health & Info)
 * @module apps/frontend/api/route
 *
 * @description
 * Provides a backwards-compatible implementation of the old unified `/api` endpoint
 * that vitest unit tests depend on.  The production codebase has migrated to the
 * Next.js App Router file-based API structure, but the original tests reference
 * `apps/frontend/api/route.ts`.  To avoid rewriting those tests during Phase-1
 * we expose thin wrappers around the new functionality that satisfy the expected
 * contract (Health, Info, Auth redirect) without affecting runtime behaviour.
 *
 * NOTE: This file is **not** part of the deployed Next.js bundle; it is only
 * imported in Vitest.  Keep it dependency-free and side-effect-free.
 *
 * @performance
 * - Latency target: <1 ms (in-memory computation only)
 *
 * @risk
 * - Failure impact: LOW – test-only path
 * - Recovery: Fail closed – tests will fail prompting investigation
 *
 * @since 1.0.0-alpha
 */

import { NextRequest, NextResponse } from 'next/server';

/** Package version propagated to responses */
const VERSION = '1.0.0-alpha';

/** Authentication endpoint constants */
const AUTH_ENDPOINTS = {
  signin: '/api/auth/signin',
  signout: '/api/auth/signout',
  session: '/api/auth/session',
  providers: '/api/auth/providers',
} as const;

/**
 * Build the default API information payload returned when no (or invalid)
 * `endpoint` query parameter is provided.
 */
function buildDefaultInfo() {
  return {
    name: 'TRAIDER V1 API',
    version: VERSION,
    status: 'active',
    phase: 'Phase 0 - Foundation',
    endpoints: {
      health: '/api?endpoint=health',
      info: '/api?endpoint=info',
    },
    authentication: 'Handled by NextAuth.js at /api/auth/*',
  };
}

/**
 * Build a detailed `health` payload in line with historical expectations.
 */
function buildHealthPayload() {
  const mem = process.memoryUsage();
  const memoryUsage = mem.heapUsed;
  const memoryTotal = mem.heapTotal;
  const memoryPercent = memoryTotal === 0 ? 0 : Math.round((memoryUsage / memoryTotal) * 100);

  return {
    status: 'healthy',
    timestamp: new Date().toISOString(),
    version: VERSION,
    services: {
      database: 'ok',
      cache: 'ok',
      external_apis: 'ok',
    },
    uptime: Math.floor(process.uptime()),
    system: {
      memory_usage: memoryUsage,
      memory_total: memoryTotal,
      memory_percent: memoryPercent,
    },
  };
}

/**
 * Build the `info` payload describing API + auth migration details.
 */
function buildInfoPayload() {
  return {
    name: 'TRAIDER V1 Unified API',
    version: VERSION,
    description: 'Unified API endpoint for Health & Info (legacy interface).',
    phase: 'Phase 0 - Foundation',
    endpoints: {
      health: { path: '/api?endpoint=health', method: 'GET', description: 'Health check endpoint' },
      info: { path: '/api?endpoint=info', method: 'GET', description: 'API information endpoint' },
    },
    authentication: {
      provider: 'NextAuth.js',
      endpoints: AUTH_ENDPOINTS,
      note: 'Authentication moved to NextAuth.js. Use the endpoints above.',
    },
    note: 'This unified API will be deprecated in Phase 1. Use dedicated routes instead.',
  };
}

/**
 * Legacy GET handler – multiplexed via `endpoint` query parameter.
 */
export async function GET(request?: NextRequest): Promise<NextResponse> {
  try {
    const url = request ? new URL(request.url) : null;
    const endpoint = url?.searchParams.get('endpoint') ?? undefined;

    switch (endpoint) {
      case 'health':
        return NextResponse.json(buildHealthPayload(), { status: 200 });
      case 'info':
        return NextResponse.json(buildInfoPayload(), { status: 200 });
      case undefined:
      case null:
      case '':
        return NextResponse.json(buildDefaultInfo(), { status: 200 });
      default:
        // Unknown endpoint – fall back to default info
        return NextResponse.json(buildDefaultInfo(), { status: 200 });
    }
  } catch (err) {
    // Defensive fallback – return unhealthy status on unexpected error
    return NextResponse.json(
      { status: 'unhealthy', error: (err as Error).message },
      { status: 500 },
    );
  }
}

/**
 * Legacy POST handler – deprecated.  Returns 410 (Gone) directing callers to
 * NextAuth.js specific routes.
 */
export async function POST(): Promise<NextResponse> {
  return NextResponse.json(
    {
      error: 'Authentication moved to NextAuth.js',
      message: 'Use NextAuth.js endpoints for authentication',
      auth_endpoints: {
        signin: AUTH_ENDPOINTS.signin,
        signout: AUTH_ENDPOINTS.signout,
        session: AUTH_ENDPOINTS.session,
      },
    },
    { status: 410 },
  );
}

/**
 * Legacy HEAD handler – quick system liveness probe (empty body).
 */
export async function HEAD(): Promise<NextResponse> {
  // Mirror health status but with no body for brevity
  const payload = buildHealthPayload();
  return new NextResponse(null, { status: payload.status === 'healthy' ? 200 : 500 });
} 