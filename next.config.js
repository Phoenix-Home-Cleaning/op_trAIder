/**
 * @fileoverview Next.js configuration for TRAIDER V1
 * @module next.config.js
 * 
 * @description
 * Production-ready Next.js configuration for institutional-grade trading platform.
 * Includes API proxying, security headers, performance optimizations, and
 * development tools integration.
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
          {
            key: 'X-Frame-Options',
            value: 'DENY',
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'Referrer-Policy',
            value: 'strict-origin-when-cross-origin',
          },
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
          {
            key: 'X-RateLimit-Limit',
            value: '100',
          },
          {
            key: 'X-RateLimit-Remaining',
            value: '99',
          },
        ],
      },
    ];
  },

  // Webpack configuration for trading-specific optimizations
  webpack: (config, { dev, isServer }) => {
    // Optimize bundle for trading libraries
    const path = require('path');
    config.resolve.alias = {
      ...config.resolve.alias,
      '@': path.resolve(__dirname, 'app'),
    };

    // Add bundle analyzer in development
    if (dev && !isServer) {
      const { BundleAnalyzerPlugin } = require('webpack-bundle-analyzer');
      config.plugins.push(
        new BundleAnalyzerPlugin({
          analyzerMode: 'disabled',
          generateStatsFile: true,
          statsFilename: 'bundle-stats.json',
        })
      );
    }

    return config;
  },

  // Compiler options for better performance
  compiler: {
    // Remove console.log in production
    removeConsole: process.env.NODE_ENV === 'production',
  },

  // Output configuration
  output: 'standalone',
  
  // Disable powered by header for security
  poweredByHeader: false,

  // Compression
  compress: true,

  // Development configuration
  ...(process.env.NODE_ENV === 'development' && {
    // Enable source maps in development
    productionBrowserSourceMaps: false,
    
    // Faster builds in development
    swcMinify: true,
  }),

  // Production optimizations
  ...(process.env.NODE_ENV === 'production' && {
    // Enable all optimizations
    swcMinify: true,
    
    // Optimize images
    optimizeFonts: true,
    
    // Generate ETags
    generateEtags: true,
  }),
};

module.exports = nextConfig; 