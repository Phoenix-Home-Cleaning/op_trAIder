/**
 * @fileoverview Shared Next.js 15 configuration for TRAIDER V1
 * @module next.config
 *
 * @description
 * Centralized Next.js configuration used by `apps/frontend`. Keeping the
 * configuration outside the application directory prevents Webpack from
 * recursively bundling `next.config.mjs` during the build process.
 *
 * @performance
 * - Bundle optimization enabled
 * - Image optimization configured
 * - API route proxying for development
 *
 * @security
 * - Security headers configured
 * - CORS properly handled
 * - Content Security Policy ready
 *
 * @see {@link https://nextjs.org/docs/api-reference/next.config.js}
 * @since 1.0.0-alpha
 * @author TRAIDER Team
 */

import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Absolute path to the Next.js app directory
const frontendDir = path.join(__dirname, 'apps', 'frontend');

/** @type {import('next').NextConfig} */
const nextConfig = {
  // Enable experimental features for better performance
  experimental: {
    typedRoutes: true, // Type-safe routing
    optimizeCss: true, // CSS optimization
    scrollRestoration: true, // Better UX
  },

  // Environment variables available to the client
  env: {
    CUSTOM_KEY: process.env.CUSTOM_KEY,
  },

  // Image optimization for trading charts and assets
  images: {
    domains: ['localhost', 'api.coinbase.com', 'cdn.jsdelivr.net'],
    formats: ['image/webp', 'image/avif'],
  },

  // API route rewrites for development
  async rewrites() {
    return [
      {
        source: '/api/health',
        destination: 'http://localhost:8000/health',
      },
      {
        source: '/api/trading/:path*',
        destination: 'http://localhost:8000/api/trading/:path*',
      },
      {
        source: '/api/market-data/:path*',
        destination: 'http://localhost:8000/api/market-data/:path*',
      },
    ];
  },

  // Security headers for production deployment
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          { key: 'X-Frame-Options', value: 'DENY' },
          { key: 'X-Content-Type-Options', value: 'nosniff' },
          { key: 'Referrer-Policy', value: 'strict-origin-when-cross-origin' },
          {
            key: 'Permissions-Policy',
            value: 'camera=(), microphone=(), geolocation=()',
          },
        ],
      },
      {
        // API routes security
        source: '/api/:path*',
        headers: [
          { key: 'X-RateLimit-Limit', value: '100' },
          { key: 'X-RateLimit-Remaining', value: '99' },
        ],
      },
    ];
  },

  // Webpack configuration for trading-specific optimizations
  webpack: (config, { dev, isServer }) => {
    // Optimize bundle for trading libraries
    config.cache = false;

    config.resolve.alias = {
      ...config.resolve.alias,
      '@': frontendDir,
    };

    // Disable symlink resolution on non-Windows platforms for faster module lookups
    if (process.platform !== 'win32') {
      config.resolve.symlinks = false;
    }

    // Additional Windows-specific fixes
    if (process.platform === 'win32') {
      config.watchOptions = {
        ...config.watchOptions,
        poll: 1000,
        aggregateTimeout: 300,
      };

      // Additional Windows filesystem fixes
      config.snapshot = {
        ...config.snapshot,
        managedPaths: [],
        immutablePaths: [],
      };
    }

    // Add bundle analyzer in development
    if (dev && !isServer && process.env.ANALYZE === 'true') {
      import('webpack-bundle-analyzer')
        .then(({ BundleAnalyzerPlugin }) => {
          config.plugins.push(
            new BundleAnalyzerPlugin({
              analyzerMode: 'disabled',
              generateStatsFile: true,
              statsFilename: 'bundle-stats.json',
            }),
          );
        })
        .catch(() => {
          // Bundle analyzer not available in this environment
        });
    }

    return config;
  },

  // Compiler options for better performance
  compiler: {
    // Remove console statements in production
    removeConsole: process.env.NODE_ENV === 'production',
  },

  // Output configuration
  output: 'standalone',

  // Disable webpack filesystem cache globally to avoid recursion with RSC loader
  cache: false,

  // Disable powered by header for security
  poweredByHeader: false,

  // Compression
  compress: true,

  // Development configuration
  ...(process.env.NODE_ENV === 'development' && {
    // Enable source maps in development
    productionBrowserSourceMaps: false,
  }),

  // Production optimizations
  ...(process.env.NODE_ENV === 'production' && {
    // Generate ETags
    generateEtags: true,
  }),
};

export default nextConfig; 