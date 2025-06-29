/**
 * @fileoverview Main dashboard page for TRAIDER V1
 * @module app/page
 *
 * @description
 * Main dashboard page that serves as the entry point for the TRAIDER platform.
 * Displays key trading metrics, portfolio overview, recent trades, and system status.
 * This is a placeholder implementation for Phase 0 - will be enhanced in Phase 1.
 *
 * @performance
 * - Latency target: <100ms initial render
 * - Throughput: N/A
 * - Memory usage: <5MB
 *
 * @risk
 * - Failure impact: HIGH (main user interface)
 * - Recovery strategy: Error boundary with fallback UI
 *
 * @compliance
 * - Audit requirements: Yes (user access logging)
 * - Data retention: N/A (display only)
 *
 * @see {@link docs/architecture/dashboard.md}
 * @since 1.0.0-alpha
 * @author TRAIDER Team
 */

import { Metadata } from 'next';

/**
 * Page metadata configuration
 */
export const metadata: Metadata = {
  title: 'Dashboard',
  description:
    'TRAIDER V1 main trading dashboard with portfolio overview, performance metrics, and system status.',
};

/**
 * Placeholder metric card component
 *
 * @description
 * Displays a key metric with title, value, and optional change indicator.
 * Used throughout the dashboard for consistent metric display.
 *
 * @param title - The metric title/label
 * @param value - The current metric value
 * @param change - Optional change indicator (positive/negative)
 * @param changeLabel - Optional label for the change value
 *
 * @returns JSX element representing a metric card
 *
 * @example
 * ```tsx
 * <MetricCard
 *   title="Portfolio Value"
 *   value="$10,000.00"
 *   change="+2.5%"
 *   changeLabel="24h"
 * />
 * ```
 */
function MetricCard({
  title,
  value,
  change,
  changeLabel,
}: {
  title: string;
  value: string;
  change?: string;
  changeLabel?: string;
}) {
  const isPositive = change?.startsWith('+');
  const isNegative = change?.startsWith('-');

  return (
    <div className="trading-card">
      <div className="trading-card-content">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-muted-foreground">{title}</p>
            <p className="text-2xl font-bold tabular-nums">{value}</p>
          </div>
          {change && (
            <div className="text-right">
              <p
                className={`text-sm font-medium tabular-nums ${
                  isPositive ? 'price-positive' : isNegative ? 'price-negative' : 'price-neutral'
                }`}
              >
                {change}
              </p>
              {changeLabel && <p className="text-xs text-muted-foreground">{changeLabel}</p>}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

/**
 * Status indicator component
 *
 * @description
 * Displays system status with colored indicator and label.
 * Used to show connection status, trading status, etc.
 *
 * @param status - The status type (online/offline/warning)
 * @param label - The status label text
 *
 * @returns JSX element representing a status indicator
 */
function StatusIndicator({
  status,
  label,
}: {
  status: 'online' | 'offline' | 'warning';
  label: string;
}) {
  const statusClasses = {
    online: 'status-online',
    offline: 'status-offline',
    warning: 'status-warning',
  };

  return (
    <div className="flex items-center space-x-2">
      <div className={`w-2 h-2 rounded-full ${statusClasses[status]}`} />
      <span className="text-sm font-medium">{label}</span>
    </div>
  );
}

/**
 * Main dashboard page component
 *
 * @description
 * Renders the main dashboard with portfolio overview, trading metrics,
 * recent activity, and system status. This is a placeholder implementation
 * that will be enhanced with real data in subsequent phases.
 *
 * @returns JSX element representing the dashboard page
 *
 * @performance
 * - Static rendering for optimal performance
 * - Lazy loading for non-critical components
 * - Efficient re-rendering with React keys
 *
 * @tradingImpact
 * - Provides real-time portfolio visibility
 * - Enables quick assessment of trading performance
 * - Shows critical system health information
 *
 * @riskLevel LOW - Display only, no trading operations
 *
 * @example
 * ```tsx
 * // Automatically rendered at root path
 * // http://localhost:3000/
 * ```
 *
 * @monitoring
 * - Metric: `dashboard.page_load_time`
 * - Alert threshold: > 2s
 */
export default function DashboardPage() {
  return (
    <div className="container-dashboard py-8">
      {/* Page Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
        <p className="text-muted-foreground">
          Welcome to TRAIDER V1 - Institutional Crypto Trading Platform
        </p>
      </div>

      {/* Key Metrics Grid */}
      <div className="trading-grid mb-8">
        <MetricCard title="Portfolio Value" value="$10,000.00" change="+2.5%" changeLabel="24h" />
        <MetricCard title="Total P&L" value="+$250.00" change="+2.5%" changeLabel="All time" />
        <MetricCard title="Active Positions" value="3" change="0" changeLabel="vs yesterday" />
        <MetricCard title="Win Rate" value="65.2%" change="+1.2%" changeLabel="30d avg" />
      </div>

      {/* Main Content Grid */}
      <div className="trading-grid-wide mb-8">
        {/* Portfolio Overview */}
        <div className="trading-card">
          <div className="trading-card-header">
            <h2 className="text-lg font-semibold">Portfolio Overview</h2>
          </div>
          <div className="trading-card-content">
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-sm font-medium">BTC-USD</span>
                <div className="text-right">
                  <div className="font-mono text-sm">0.15 BTC</div>
                  <div className="text-xs text-muted-foreground">~$6,750.00</div>
                </div>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm font-medium">ETH-USD</span>
                <div className="text-right">
                  <div className="font-mono text-sm">2.5 ETH</div>
                  <div className="text-xs text-muted-foreground">~$3,250.00</div>
                </div>
              </div>
              <div className="flex justify-between items-center border-t pt-4">
                <span className="text-sm font-semibold">Total Value</span>
                <div className="text-right">
                  <div className="font-mono text-sm font-semibold">$10,000.00</div>
                  <div className="text-xs price-positive">+$250.00 (2.5%)</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Recent Activity */}
        <div className="trading-card">
          <div className="trading-card-header">
            <h2 className="text-lg font-semibold">Recent Activity</h2>
          </div>
          <div className="trading-card-content">
            <div className="space-y-3">
              <div className="flex justify-between items-center text-sm">
                <div>
                  <div className="font-medium">BUY BTC-USD</div>
                  <div className="text-xs text-muted-foreground">2 hours ago</div>
                </div>
                <div className="text-right">
                  <div className="font-mono">0.05 BTC</div>
                  <div className="text-xs text-muted-foreground">@$45,000</div>
                </div>
              </div>
              <div className="flex justify-between items-center text-sm">
                <div>
                  <div className="font-medium">SELL ETH-USD</div>
                  <div className="text-xs text-muted-foreground">4 hours ago</div>
                </div>
                <div className="text-right">
                  <div className="font-mono">0.5 ETH</div>
                  <div className="text-xs text-muted-foreground">@$1,300</div>
                </div>
              </div>
              <div className="flex justify-between items-center text-sm">
                <div>
                  <div className="font-medium">BUY BTC-USD</div>
                  <div className="text-xs text-muted-foreground">1 day ago</div>
                </div>
                <div className="text-right">
                  <div className="font-mono">0.1 BTC</div>
                  <div className="text-xs text-muted-foreground">@$44,800</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* System Status */}
      <div className="trading-card">
        <div className="trading-card-header">
          <h2 className="text-lg font-semibold">System Status</h2>
        </div>
        <div className="trading-card-content">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <StatusIndicator status="online" label="Market Data Feed" />
            <StatusIndicator status="online" label="Trading Engine" />
            <StatusIndicator status="online" label="Risk Management" />
            <StatusIndicator status="warning" label="ML Signals (Phase 1)" />
          </div>
          <div className="mt-4 pt-4 border-t">
            <div className="flex justify-between items-center text-sm">
              <span className="text-muted-foreground">Last Updated</span>
              <span className="font-mono">{new Date().toLocaleTimeString()}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Phase 0 Notice */}
      <div className="mt-8 p-4 bg-warning/10 border border-warning/20 rounded-lg">
        <div className="flex items-start space-x-3">
          <div className="w-5 h-5 rounded-full bg-warning/20 flex items-center justify-center mt-0.5">
            <div className="w-2 h-2 rounded-full bg-warning" />
          </div>
          <div>
            <h3 className="text-sm font-semibold">Phase 0: Setup & Foundation</h3>
            <p className="text-sm text-muted-foreground mt-1">
              This is a placeholder dashboard. Real trading functionality, market data integration,
              and live portfolio tracking will be implemented in Phase 1.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
