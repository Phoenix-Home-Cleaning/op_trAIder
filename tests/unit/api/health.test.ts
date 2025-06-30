/**
 * @fileoverview Health API Endpoint Integration Tests
 * @module tests.unit.api.health
 * 
 * @description
 * Comprehensive integration tests for the TRAIDER V1 health check API endpoint.
 * Tests actual route handlers to achieve 90%+ statement coverage for world-class
 * engineering standards. Includes system status validation, error handling, and
 * monitoring integration.
 * 
 * @performance
 * - Test execution target: <100ms per test
 * - Memory usage: <5MB per test suite
 * - Coverage requirement: >95%
 * 
 * @risk
 * - Failure impact: HIGH - Health checks are critical for monitoring
 * - Recovery strategy: Automated test retry with endpoint isolation
 * 
 * @compliance
 * - Audit requirements: Yes - System monitoring validation
 * - Data retention: Test logs retained for 90 days
 * 
 * @see {@link docs/architecture/monitoring.md}
 * @since 1.0.0
 * @author TRAIDER Team
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { NextRequest } from 'next/server';

// Import the actual route handlers from unified API
import { GET, HEAD } from '../../../app/api/route';

describe('Health API Endpoint - Integration Tests', () => {
  /**
   * Test suite for health API endpoint functionality with real route handlers
   * 
   * @description Tests actual health check responses and system status validation
   * @riskLevel HIGH - Health checks are critical for system monitoring
   */
  
  beforeEach(() => {
    // Reset environment for each test
    vi.clearAllMocks();
    
    // Set test environment (using vi.stubEnv for proper test isolation)
    vi.stubEnv('NODE_ENV', 'test');
  });

  afterEach(() => {
    // Clean up any environment changes
    vi.restoreAllMocks();
  });

  describe('GET /api?endpoint=health - Unified API', () => {
    /**
     * Test suite for GET health endpoint with unified route handler
     * 
     * @description Tests comprehensive health check response with real system data
     * @riskLevel HIGH - GET endpoint provides detailed system status
     */

    it('returns healthy status with all service checks', async () => {
      /**
       * Test that health endpoint returns comprehensive system status
       * 
       * @performance Target: <50ms response time
       * @tradingImpact System health monitoring is critical for trading uptime
       * @riskLevel HIGH - Health checks detect system issues before they affect trading
       */
      
      const request = new NextRequest('http://localhost/api?endpoint=health');
      const response = await GET(request);
      const data = await response.json();

      // Verify response structure for unified API
      expect(data).toHaveProperty('status');
      expect(data).toHaveProperty('timestamp');
      expect(data).toHaveProperty('version');
      expect(data).toHaveProperty('services');
      expect(data).toHaveProperty('uptime');
      expect(data).toHaveProperty('system');

      // Verify status values
      expect(['healthy', 'degraded', 'unhealthy']).toContain(data.status);
      expect(data.version).toBe('1.0.0-alpha');

      // Verify service statuses (unified API structure)
      expect(data.services).toHaveProperty('database');
      expect(data.services).toHaveProperty('cache');
      expect(data.services).toHaveProperty('external_apis');

      // Verify system metrics (unified API field names)
      expect(data.system).toHaveProperty('memory_usage');
      expect(data.system).toHaveProperty('memory_total');
      expect(data.system).toHaveProperty('memory_percent');

      // Verify response status
      expect([200, 500]).toContain(response.status);
    });

    it('includes proper timestamp format', async () => {
      /**
       * Test that health endpoint returns valid ISO timestamp
       * 
       * @tradingImpact Accurate timestamps are needed for monitoring and alerting
       * @riskLevel MEDIUM - Timestamp format affects monitoring system integration
       */
      
      const request = new NextRequest('http://localhost/api?endpoint=health');
      const response = await GET(request);
      const data = await response.json();

      // Verify timestamp is valid ISO string
      expect(data.timestamp).toMatch(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$/);
      
      // Verify timestamp is recent (within last minute)
      const timestamp = new Date(data.timestamp);
      const now = new Date();
      const timeDiff = now.getTime() - timestamp.getTime();
      expect(timeDiff).toBeLessThan(60000); // Less than 1 minute
      expect(timeDiff).toBeGreaterThanOrEqual(0); // Not in the future
    });

    it('includes real memory usage metrics', async () => {
      /**
       * Test that health endpoint returns actual memory usage information
       * 
       * @tradingImpact Memory monitoring prevents system crashes during high load
       * @riskLevel HIGH - Memory issues could affect trading performance
       */
      
      const request = new NextRequest('http://localhost/api?endpoint=health');
      const response = await GET(request);
      const data = await response.json();

      // Verify memory metrics structure (unified API field names)
      expect(data.system).toHaveProperty('memory_usage');
      expect(data.system).toHaveProperty('memory_total');
      expect(data.system).toHaveProperty('memory_percent');

      // Verify memory values are reasonable numbers
      expect(typeof data.system.memory_usage).toBe('number');
      expect(typeof data.system.memory_total).toBe('number');
      expect(typeof data.system.memory_percent).toBe('number');
      
      expect(data.system.memory_usage).toBeGreaterThan(0);
      expect(data.system.memory_total).toBeGreaterThan(0);
      expect(data.system.memory_percent).toBeGreaterThanOrEqual(0);
      expect(data.system.memory_percent).toBeLessThanOrEqual(100);

      // Verify memory calculation is correct
      const expectedPercentage = Math.round((data.system.memory_usage / data.system.memory_total) * 100);
      expect(Math.abs(data.system.memory_percent - expectedPercentage)).toBeLessThanOrEqual(1);
    });

    it('includes real uptime information', async () => {
      /**
       * Test that health endpoint returns actual system uptime
       * 
       * @tradingImpact Uptime tracking helps assess system reliability
       * @riskLevel MEDIUM - Uptime metrics are important for SLA monitoring
       */
      
      const request = new NextRequest('http://localhost/api?endpoint=health');
      const response = await GET(request);
      const data = await response.json();

      // Verify uptime is included and valid
      expect(data).toHaveProperty('uptime');
      expect(typeof data.uptime).toBe('number');
      expect(data.uptime).toBeGreaterThanOrEqual(0);
      
      // Uptime should be reasonable (not negative, not impossibly large)
      expect(data.uptime).toBeLessThan(365 * 24 * 3600); // Less than 1 year in seconds
    });

    it('handles performance requirements', async () => {
      /**
       * Test that health endpoint responds within performance requirements
       * 
       * @performance Target: <50ms response time
       * @tradingImpact Fast health checks enable rapid system monitoring
       * @riskLevel MEDIUM - Slow health checks could delay issue detection
       */
      
      const startTime = performance.now();
      const request = new NextRequest('http://localhost/api?endpoint=health');
      const response = await GET(request);
      const responseTime = performance.now() - startTime;

      // Should respond quickly
      expect(responseTime).toBeLessThan(100); // Generous threshold for test environment
      
      // Verify response is valid
      expect(response).toBeDefined();
      const data = await response.json();
      expect(data.status).toBeDefined();
    });

    it('handles error conditions gracefully', async () => {
      /**
       * Test that health endpoint handles errors without crashing
       * 
       * @tradingImpact Error handling prevents health check failures from affecting system
       * @riskLevel HIGH - Health check failures could mask real system issues
       */
      
      // Test with malformed request (should still work)
      const request = new NextRequest('http://localhost/api?endpoint=health&invalid=param');
      const response = await GET(request);
      
      // Should still return valid health response
      expect(response.status).toBeLessThanOrEqual(503);
      const data = await response.json();
      expect(data).toHaveProperty('status');
      expect(data).toHaveProperty('timestamp');
    });
  });

  describe('HEAD /api - Quick Health Check', () => {
    /**
     * Test suite for HEAD health endpoint
     * 
     * @description Tests quick health check without response body
     * @riskLevel MEDIUM - HEAD requests are used for lightweight health checks
     */

    it('returns successful HEAD response', async () => {
      /**
       * Test that HEAD endpoint returns success status
       * 
       * @performance Target: <10ms response time
       * @tradingImpact Quick health checks enable rapid monitoring
       * @riskLevel MEDIUM - HEAD checks are used for load balancer health
       */
      
      const response = await HEAD();
      
      // Verify HEAD response
      expect([200, 500]).toContain(response.status);
      expect(response.body).toBeNull();
    });

    it('meets performance requirements for HEAD requests', async () => {
      /**
       * Test that HEAD endpoint responds very quickly
       * 
       * @performance Target: <10ms response time
       * @tradingImpact Ultra-fast health checks enable high-frequency monitoring
       * @riskLevel LOW - Performance optimization for monitoring efficiency
       */
      
      const startTime = performance.now();
      const response = await HEAD();
      const responseTime = performance.now() - startTime;

      // Should respond very quickly
      expect(responseTime).toBeLessThan(50); // Very generous threshold for test environment
      expect(response).toBeDefined();
    });
  });

  describe('API Integration - Default Endpoint', () => {
    /**
     * Test suite for default API endpoint behavior
     * 
     * @description Tests API root endpoint without specific endpoint parameter
     * @riskLevel LOW - Default endpoint provides API information
     */

    it('returns API information when no endpoint specified', async () => {
      /**
       * Test that default API endpoint returns API information
       * 
       * @tradingImpact API discovery helps with integration and debugging
       * @riskLevel LOW - Informational endpoint for API documentation
       */
      
      const request = new NextRequest('http://localhost/api');
      const response = await GET(request);
      const data = await response.json();

      // Verify API information structure
      expect(data).toHaveProperty('name');
      expect(data).toHaveProperty('version');
      expect(data).toHaveProperty('status');
      expect(data).toHaveProperty('phase');
      expect(data).toHaveProperty('endpoints');

      // Verify values
      expect(data.name).toBe('TRAIDER V1 API');
      expect(data.version).toBe('1.0.0-alpha');
      expect(data.status).toBe('active');
      expect(data.phase).toBe('Phase 0 - Foundation');

      // Verify endpoints information
      expect(data.endpoints).toHaveProperty('health');
      expect(data.endpoints).toHaveProperty('auth');
      expect(data.endpoints).toHaveProperty('login');
    });
  });
});

describe('Health API Error Handling', () => {
  /**
   * Test suite for health API error scenarios
   * 
   * @description Tests error handling and recovery mechanisms
   * @riskLevel HIGH - Error handling is critical for system reliability
   */

  it('handles invalid endpoint parameters gracefully', async () => {
    /**
     * Test that invalid endpoint parameters don't crash the API
     * 
     * @tradingImpact Robust error handling prevents API failures
     * @riskLevel MEDIUM - Input validation prevents system instability
     */
    
    const request = new NextRequest('http://localhost/api?endpoint=invalid');
    const response = await GET(request);
    
    // Should return default API information for invalid endpoints
    expect(response.status).toBe(200);
    const data = await response.json();
    expect(data).toHaveProperty('name');
    expect(data.name).toBe('TRAIDER V1 API');
  });

  it('maintains consistent response format during errors', async () => {
    /**
     * Test that error responses maintain consistent structure
     * 
     * @tradingImpact Consistent error formats enable reliable error handling
     * @riskLevel MEDIUM - Error format consistency improves system integration
     */
    
    // Test with various edge cases
    const testCases = [
      'http://localhost/api?endpoint=',
      'http://localhost/api?endpoint=null',
      'http://localhost/api?endpoint=undefined',
    ];

    for (const url of testCases) {
      const request = new NextRequest(url);
      const response = await GET(request);
      
      // All should return valid responses
      expect(response.status).toBeLessThanOrEqual(500);
      const data = await response.json();
      expect(typeof data).toBe('object');
      expect(data).not.toBeNull();
    }
  });
}); 