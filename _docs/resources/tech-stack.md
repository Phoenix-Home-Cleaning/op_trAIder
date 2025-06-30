# 🛠️ TRAIDER V1 — Tech Stack Guide

### Best Practices, Limitations & Conventions *(June 28 2025)*

---

## 🌐 **Next.js + TypeScript**

### **Best Practices**
- **App Router**: Use the new App Router (not Pages Router) for better performance and DX
- **Server Components**: Default to Server Components, use Client Components only when needed
- **TypeScript Strict Mode**: Enable `"strict": true` in tsconfig.json for maximum type safety
- **File Organization**: Use feature-based folder structure in `/app` directory
```
app/
├── dashboard/
│   ├── page.tsx
│   ├── layout.tsx
│   └── components/
├── performance/
│   ├── page.tsx
│   └── components/
└── api/
    └── auth/
```

### **Common Pitfalls**
- **Hydration Mismatches**: Ensure server and client render identical content
- **Client Components Overuse**: Don't add `'use client'` unnecessarily
- **Bundle Size**: Monitor with `@next/bundle-analyzer` to prevent bloat
- **Memory Leaks**: Clean up intervals, subscriptions in useEffect cleanup

### **TRAIDER-Specific Conventions**
- **Real-time Data**: Use Server Components for initial data, Client Components for real-time updates
- **Type Definitions**: Create shared types in `/types/trading.ts` for positions, P&L, signals
- **Error Boundaries**: Wrap trading components to prevent dashboard crashes
- **Performance**: Use `next/dynamic` for heavy charting components

### **Configuration**
```typescript
// next.config.mjs
/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  experimental: {
    typedRoutes: true,
  },
  eslint: {
    // We run ESLint separately in CI
    ignoreDuringBuilds: true,
  },
};
export default nextConfig;
```

---

## 🎨 **Tailwind CSS**

### **Best Practices**
- **Design System**: Create custom utilities in `tailwind.config.js`
- **Component Classes**: Use `@apply` directive for reusable component styles
- **Responsive Design**: Mobile-first approach with `sm:`, `md:`, `lg:` prefixes
- **Performance**: Use JIT mode (default in v3+) and purge unused styles

### **TRAIDER-Specific Setup**
```javascript
// tailwind.config.js
/** @type {import('tailwindcss').Config} */
export default {
  content: ['./app/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#f0f9ff',
          500: '#3b82f6',
          900: '#1e3a8a',
        },
        success: '#10b981', // Green for profits
        danger: '#ef4444',  // Red for losses
        warning: '#f59e0b', // Yellow for warnings
      },
      fontFamily: {
        mono: ['"JetBrains Mono"', 'monospace'], // For trading data
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
  ],
}
```

### **Common Pitfalls**
- **Specificity Issues**: Avoid mixing Tailwind with custom CSS
- **Class Bloat**: Use component extraction for repeated patterns
- **Mobile Performance**: Test on actual devices, not just browser dev tools
- **Color Accessibility**: Ensure sufficient contrast ratios

### **Trading Dashboard Patterns**
```typescript
// Reusable trading card component
import { type ReactNode } from 'react';

const TradingCard = ({ children, variant = 'default' }: { children: ReactNode, variant?: 'default' | 'success' | 'danger' }) => {
  const baseClasses = 'rounded-lg border p-4 shadow-sm'
  const variants = {
    default: 'bg-white border-gray-200',
    success: 'bg-green-50 border-green-200',
    danger: 'bg-red-50 border-red-200',
  }
  
  return (
    <div className={`${baseClasses} ${variants[variant]}`}>
      {children}
    </div>
  )
}
```

---

## 📊 **Chart.js (→ TradingView)**

### **Best Practices**
- **Performance**: Use `react-chartjs-2` wrapper for React integration
- **Data Updates**: Implement efficient data updating without full re-renders
- **Responsive**: Configure responsive options for mobile compatibility
- **Memory Management**: Destroy chart instances properly

### **TRAIDER Implementation**
```typescript
// P&L Chart Component
import { Line } from 'react-chartjs-2'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  TimeScale,
} from 'chart.js'
import 'chartjs-adapter-date-fns'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  TimeScale
)

const PnLChart = ({ data }) => {
  const options = {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      x: {
        type: 'time',
        time: {
          unit: 'hour',
        },
      },
      y: {
        beginAtZero: false,
        ticks: {
          callback: (value) => `$${value.toLocaleString()}`,
        },
      },
    },
    plugins: {
      legend: {
        position: 'top',
      },
      tooltip: {
        mode: 'index',
        intersect: false,
        callbacks: {
          label: (context) => {
            return `P&L: $${context.parsed.y.toLocaleString()}`
          },
        },
      },
    },
  }

  return <Line data={data} options={options} height={400} />
}
```

### **Limitations**
- **Financial Features**: No built-in candlestick charts or technical indicators
- **Real-time Performance**: Can struggle with high-frequency updates
- **Advanced Interactions**: Limited compared to TradingView

### **Migration Path to TradingView**
1. **Phase 1**: Start with Chart.js for basic P&L and performance charts
2. **Phase 2**: Add TradingView for detailed price charts and technical analysis
3. **Phase 3**: Full migration when revenue justifies $3k/year cost

---

## 🔄 **Socket.IO**

### **Best Practices**
- **Connection Management**: Handle reconnections gracefully
- **Event Namespacing**: Use namespaces for different data types
- **Error Handling**: Implement comprehensive error handling
- **Authentication**: Secure WebSocket connections with JWT

### **TRAIDER Real-time Architecture**
```typescript
// Client-side Socket.IO setup
import { io, Socket } from 'socket.io-client'

class TradingSocketManager {
  private socket: Socket | null = null;
  private reconnectAttempts = 0;
  private readonly maxReconnectAttempts = 5;

  connect(token: string) {
    this.socket = io(process.env.NEXT_PUBLIC_WS_URL!, {
      auth: { token },
      transports: ['websocket'],
    })

    this.socket.on('connect', () => {
      console.log('Connected to trading feed');
      this.reconnectAttempts = 0;
    })

    this.socket.on('disconnect', (reason) => {
      console.log(`Disconnected from trading feed: ${reason}`);
    })

    this.socket.on('connect_error', (error) => {
      console.error('Connection error:', error.message);
      this.handleReconnect();
    })

    // Trading-specific events
    this.socket.on('pnl_update', (data) => {
      // Update P&L in real-time
    });

    this.socket.on('trade_executed', (data) => {
      // Show trade notification
    });
  }

  private handleReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      const delay = Math.pow(2, this.reconnectAttempts) * 1000;
      console.log(`Attempting to reconnect in ${delay / 1000}s...`);
      setTimeout(() => {
        this.socket?.connect();
      }, delay);
    } else {
      console.error('Max reconnection attempts reached.');
    }
  }

  disconnect() {
    this.socket?.disconnect();
  }
}
```

### **Common Pitfalls**
- **Memory Leaks**: Always clean up event listeners
- **Connection Storms**: Implement exponential backoff for reconnections
- **Data Flooding**: Throttle high-frequency updates to prevent UI freezing
- **Security**: Never trust client-side data; validate on server

### **Performance Considerations**
- **Batching**: Batch multiple updates into single emissions
- **Compression**: Enable compression for large payloads
- **Room Management**: Use rooms to limit data to relevant users only

---

## 🗄️ **Zustand + SWR**

### **Zustand Best Practices**
```typescript
// Trading store with Zustand
import { create } from 'zustand'
import { devtools, persist } from 'zustand/middleware'

interface TradingState {
  positions: Position[]
  pnl: number
  isTrading: boolean
  // Actions
  updatePositions: (positions: Position[]) => void
  updatePnL: (pnl: number) => void
  toggleTrading: () => void
}

export const useTradingStore = create<TradingState>()(
  devtools(
    persist(
      (set, get) => ({
        positions: [],
        pnl: 0,
        isTrading: false,
        updatePositions: (positions) => set({ positions }),
        updatePnL: (pnl) => set({ pnl }),
        toggleTrading: () => set((state) => ({ 
          isTrading: !state.isTrading 
        })),
      }),
      {
        name: 'trading-store',
        partialize: (state) => ({ 
          isTrading: state.isTrading 
        }), // Only persist essential state
      }
    ),
    { name: 'trading-store' }
  )
)
```

### **SWR Best Practices**
```typescript
// Custom hooks for trading data
import useSWR from 'swr'

const fetcher = (url: string) => fetch(url).then(res => res.json())

export const usePositions = () => {
  const { data, error, mutate } = useSWR('/api/positions', fetcher, {
    refreshInterval: 5000, // Refresh every 5 seconds
    revalidateOnFocus: true,
    revalidateOnReconnect: true,
    errorRetryCount: 3,
    errorRetryInterval: 1000,
  })

  return {
    positions: data,
    isLoading: !error && !data,
    error,
    mutate,
  }
}

export const usePnL = () => {
  const { data, error } = useSWR('/api/pnl', fetcher, {
    refreshInterval: 1000, // More frequent for P&L
    dedupingInterval: 500,
  })

  return {
    pnl: data,
    isLoading: !error && !data,
    error,
  }
}
```

### **Common Pitfalls**
- **Over-fetching**: Don't refresh data too frequently
- **State Duplication**: Keep Zustand for client state, SWR for server state
- **Memory Leaks**: Be careful with persistent state and subscriptions
- **Race Conditions**: Handle concurrent updates properly

---

## 🔐 **NextAuth.js (JWT)**

### **Setup for TRAIDER**
```typescript
// app/api/auth/[...nextauth]/route.ts
import NextAuth from 'next-auth'
import CredentialsProvider from 'next-auth/providers/credentials'
import { JWT } from 'next-auth/jwt'

const handler = NextAuth({
  providers: [
    CredentialsProvider({
      name: 'credentials',
      credentials: {
        password: { label: 'Password', type: 'password' }
      },
      async authorize(credentials) {
        // Simple password check for personal use
        if (credentials?.password === process.env.DASHBOARD_PASSWORD) {
          return {
            id: '1',
            name: 'Owner',
            email: 'owner@traider.local',
            role: 'owner'
          }
        }
        // Guest access
        if (credentials?.password === process.env.GUEST_PASSWORD) {
          return {
            id: '2',
            name: 'Guest',
            email: 'guest@traider.local',
            role: 'guest'
          }
        }
        return null
      }
    })
  ],
  session: {
    strategy: 'jwt',
    maxAge: 24 * 60 * 60, // 24 hours
  },
  jwt: {
    secret: process.env.NEXTAUTH_SECRET,
  },
  callbacks: {
    async jwt({ token, user }) {
      if (user) {
        token.role = user.role
      }
      return token
    },
    async session({ session, token }) {
      session.user.role = token.role
      return session
    },
  },
  pages: {
    signIn: '/login',
  },
})

export { handler as GET, handler as POST }
```

### **Security Best Practices**
- **Strong Secrets**: Use crypto.randomBytes(64).toString('hex') for NEXTAUTH_SECRET
- **HTTPS Only**: Set secure cookies in production
- **Role-based Access**: Implement proper role checking
- **Session Expiry**: Set appropriate session timeouts

### **Middleware Protection**
```typescript
// middleware.ts
import { withAuth } from 'next-auth/middleware'

export default withAuth(
  function middleware(req) {
    // Additional logic here
  },
  {
    callbacks: {
      authorized: ({ token, req }) => {
        // Protect admin routes
        if (req.nextUrl.pathname.startsWith('/settings')) {
          return token?.role === 'owner'
        }
        // Allow guest access to dashboard
        if (req.nextUrl.pathname.startsWith('/dashboard')) {
          return !!token
        }
        return true
      },
    },
  }
)

export const config = {
  matcher: ['/dashboard/:path*', '/settings/:path*']
}
```

---

## 🗄️ **PostgreSQL on DigitalOcean Managed**

### **Best Practices**
- **Connection Pooling**: Use connection pooling to handle concurrent requests
- **Indexing**: Create proper indexes for trading queries
- **Backup Strategy**: Enable automated backups and point-in-time recovery
- **Monitoring**: Set up alerts for connection limits and performance

### **TRAIDER Schema Design**
```sql
-- User sessions and preferences
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  role VARCHAR(50) NOT NULL DEFAULT 'guest',
  preferences JSONB DEFAULT '{}',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Trading configuration
CREATE TABLE trading_config (
  id SERIAL PRIMARY KEY,
  user_id INTEGER REFERENCES users(id),
  daily_loss_limit DECIMAL(15,2),
  max_position_size DECIMAL(15,2),
  risk_limits JSONB,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Audit log for critical actions
CREATE TABLE audit_log (
  id SERIAL PRIMARY KEY,
  user_id INTEGER REFERENCES users(id),
  action VARCHAR(100) NOT NULL,
  details JSONB,
  ip_address INET,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_audit_log_user_id ON audit_log(user_id);
CREATE INDEX idx_audit_log_created_at ON audit_log(created_at);
CREATE INDEX idx_trading_config_user_id ON trading_config(user_id);
```

### **Connection Management**
```typescript
// lib/db.ts
import { Pool } from 'pg'

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: process.env.NODE_ENV === 'production' ? { rejectUnauthorized: false } : false,
  max: 20, // Maximum connections
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 2000,
})

export default pool
```

### **Common Pitfalls**
- **Connection Leaks**: Always release connections back to pool
- **N+1 Queries**: Use JOIN queries instead of multiple round trips
- **Large Transactions**: Keep transactions small and fast
- **Missing Indexes**: Monitor slow queries and add appropriate indexes

---

## 🚀 **Deployment: Vercel + DigitalOcean**

### **Vercel Configuration**
```javascript
// vercel.json
{
  "framework": "nextjs",
  "regions": ["iad1"], // Close to your DO droplets
  "env": {
    "NEXTAUTH_URL": "https://thegambler.co",
    "NEXTAUTH_SECRET": "@nextauth-secret",
    "DATABASE_URL": "@database-url",
    "NEXT_PUBLIC_WS_URL": "wss://api.thegambler.co"
  },
  "functions": {
    "app/api/auth/[...nextauth]/route.ts": {
      "maxDuration": 30
    }
  }
}
```

### **Environment Variables**
```bash
# .env.local (development)
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your-secret-here
DATABASE_URL=postgresql://user:pass@localhost:5432/traider
DASHBOARD_PASSWORD=your-secure-password
GUEST_PASSWORD=guest-password
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

### **DigitalOcean Backend Setup**
- **Droplet Size**: Start with 2GB RAM, 2 vCPUs for backend services
- **Managed Database**: 1GB RAM PostgreSQL cluster with automated backups
- **Networking**: Use VPC for secure communication between services
- **Load Balancer**: Add load balancer when scaling beyond single droplet

### **Common Pitfalls**
- **CORS Issues**: Configure CORS properly between Vercel and DO
- **Environment Variables**: Keep production secrets secure
- **Cold Starts**: Vercel functions may have cold start delays
- **Regional Latency**: Deploy backend close to Vercel regions

---

## 📊 **Monitoring: GA4 + Sentry**

### **GA4 Setup**
```typescript
// lib/gtag.ts
export const GA_TRACKING_ID = process.env.NEXT_PUBLIC_GA_ID

export const pageview = (url: string) => {
  window.gtag('config', GA_TRACKING_ID, {
    page_path: url,
  })
}

export const event = ({ action, category, label, value }: {
  action: string
  category: string
  label?: string
  value?: number
}) => {
  window.gtag('event', action, {
    event_category: category,
    event_label: label,
    value: value,
  })
}
```

### **Sentry Configuration**
```typescript
// sentry.client.config.ts
import * as Sentry from '@sentry/nextjs'

Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
  environment: process.env.NODE_ENV,
  tracesSampleRate: 0.1,
  beforeSend(event) {
    // Filter out sensitive trading data
    if (event.request?.url?.includes('/api/positions')) {
      return null
    }
    return event
  },
})
```

### **Custom Trading Events**
```typescript
// Track trading-specific events
export const trackTradingEvent = (event: string, data: any) => {
  // GA4 event
  window.gtag('event', event, {
    event_category: 'trading',
    custom_parameters: {
      trading_mode: data.mode,
      asset_pair: data.pair,
    }
  })

  // Sentry breadcrumb
  Sentry.addBreadcrumb({
    category: 'trading',
    message: event,
    data,
    level: 'info',
  })
}
```

---

## 🔒 **Cloudflare**

### **Security Configuration**
- **SSL/TLS**: Full (strict) encryption mode
- **Security Level**: Medium for balance of security and usability
- **Bot Fight Mode**: Enable to prevent automated attacks
- **Rate Limiting**: Configure for API endpoints

### **Performance Optimization**
```javascript
// Cloudflare Page Rules for thegambler.co
{
  "url": "thegambler.co/dashboard*",
  "settings": {
    "cache_level": "bypass", // Don't cache dynamic trading data
    "security_level": "high"
  }
},
{
  "url": "thegambler.co/_next/static/*",
  "settings": {
    "cache_level": "cache_everything",
    "edge_cache_ttl": 31536000 // 1 year for static assets
  }
}
```

### **Common Pitfalls**
- **Caching Issues**: Don't cache dynamic trading data
- **SSL Loops**: Ensure proper SSL configuration
- **API Rate Limits**: Monitor API calls to avoid limits
- **Real-time Data**: WebSocket connections may need special handling

---

## 🧪 **Testing: Vitest + Playwright**

### **Vitest Configuration**
```typescript
// vitest.config.ts
import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    setupFiles: ['./test/setup.ts'],
    globals: true,
  },
  resolve: {
    alias: {
      '@': '/app',
    },
  },
})
```

### **Trading Component Tests**
```typescript
// __tests__/components/PnLChart.test.tsx
import { render, screen } from '@testing-library/react'
import { PnLChart } from '@/components/PnLChart'

describe('PnLChart', () => {
  const mockData = {
    labels: ['10:00', '11:00', '12:00'],
    datasets: [{
      label: 'P&L',
      data: [100, 150, 120],
    }]
  }

  it('renders P&L chart with correct data', () => {
    render(<PnLChart data={mockData} />)
    
    // Chart.js creates canvas element
    expect(screen.getByRole('img')).toBeInTheDocument()
  })

  it('formats currency values correctly', () => {
    render(<PnLChart data={mockData} />)
    
    // Test tooltip formatting logic
    // Implementation depends on your chart setup
  })
})
```

### **Playwright E2E Tests**
```typescript
// e2e/trading-dashboard.spec.ts
import { test, expect } from '@playwright/test'

test.describe('Trading Dashboard', () => {
  test.beforeEach(async ({ page }) => {
    // Login as owner
    await page.goto('/login')
    await page.fill('input[name="password"]', process.env.TEST_OWNER_PASSWORD!)
    await page.click('button[type="submit"]')
    await page.waitForURL('/dashboard')
  })

  test('displays real-time P&L updates', async ({ page }) => {
    // Check initial P&L display
    const pnlElement = page.locator('[data-testid="current-pnl"]')
    await expect(pnlElement).toBeVisible()
    
    // Simulate real-time update (you'll need to mock WebSocket)
    // This depends on your WebSocket implementation
  })

  test('emergency stop button works', async ({ page }) => {
    await page.click('[data-testid="emergency-stop"]')
    
    // Should show confirmation dialog
    await expect(page.locator('[role="dialog"]')).toBeVisible()
    
    // Confirm emergency stop
    await page.click('[data-testid="confirm-emergency-stop"]')
    
    // Should update trading status
    await expect(page.locator('[data-testid="trading-status"]')).toContainText('STOPPED')
  })
})
```

### **Testing Best Practices**
- **Mock External APIs**: Never hit real trading APIs in tests
- **Test Trading Logic**: Focus on critical trading calculations and risk checks
- **Visual Regression**: Use Playwright's screenshot comparison for charts
- **Performance Testing**: Test dashboard performance with large datasets

---

## 🔄 **GitHub Actions**

### **CI/CD Pipeline**
```yaml
# .github/workflows/ci.yml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'
          cache: 'npm'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Run type checking
        run: npm run type-check
      
      - name: Run linting
        run: npm run lint
      
      - name: Run unit tests
        run: npm run test
      
      - name: Run E2E tests
        run: npm run test:e2e
        env:
          TEST_OWNER_PASSWORD: ${{ secrets.TEST_OWNER_PASSWORD }}

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - name: Deploy to Vercel
        uses: amondnet/vercel-action@v25
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
          vercel-args: '--prod'
```

### **Security Considerations**
- **Secrets Management**: Store all sensitive data in GitHub Secrets
- **Branch Protection**: Require PR reviews and status checks
- **Dependency Scanning**: Enable Dependabot for security updates
- **OIDC**: Use OIDC tokens instead of long-lived secrets where possible

---

## 🚨 **Common Integration Pitfalls**

### **Real-time Data Flow Issues**
1. **WebSocket + SWR Conflicts**: Don't fetch the same data via both WebSocket and SWR
2. **State Synchronization**: Keep Zustand and SWR state in sync
3. **Memory Leaks**: Clean up WebSocket connections and intervals
4. **Race Conditions**: Handle concurrent updates to trading state

### **Authentication Edge Cases**
1. **Token Expiry**: Handle JWT expiration gracefully
2. **Role Changes**: Update UI immediately when user role changes
3. **Concurrent Sessions**: Decide policy for multiple browser sessions
4. **Password Changes**: Force re-authentication on password change

### **Performance Bottlenecks**
1. **Chart Rendering**: Optimize chart updates for real-time data
2. **Database Queries**: Use proper indexing and query optimization
3. **Bundle Size**: Monitor and optimize JavaScript bundle size
4. **API Rate Limits**: Implement proper rate limiting and caching

### **Security Vulnerabilities**
1. **XSS**: Sanitize all user inputs and trading data
2. **CSRF**: Use proper CSRF protection
3. **Data Exposure**: Never log sensitive trading information
4. **API Security**: Validate all API inputs and outputs

---

> **Remember**: This is a financial trading system. Prioritize reliability, security, and data integrity over fancy features. Test thoroughly, monitor everything, and always have rollback plans. 