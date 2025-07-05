/**
 * @fileoverview Main Dashboard Page - TRAIDER V1
 * @module app.page
 *
 * @description
 * This is the main entry point for the TRAIDER V1 dashboard.
 * It provides an overview of portfolio performance, recent activity, and system status.
 * The component is designed for high-performance, real-time updates and adheres to
 * institutional-grade UI/UX standards.
 *
 * @performance
 * - Initial load: <500ms
 * - Real-time updates: <100ms latency
 *
 * @risk
 * - Failure impact: HIGH - This is the primary user interface.
 * - Recovery strategy: Graceful degradation with cached data, error boundaries.
 *
 * @compliance
 * - Audit requirements: All user interactions on this page are logged.
 * - Data retention: Displayed data is ephemeral; historical data is archived.
 *
 * @see {@link docs/architecture/frontend.md}
 * @since 1.0.0
 * @author TRAIDER Team
 */
import React from 'react';
// import MetricCard from '@/components/dashboard/metric-card';
// import StatusIndicator from '@/components/dashboard/status-indicator';

import { Metadata } from 'next';

/**
 * Page metadata for SEO and browser information.
 * @type {Metadata}
 */
export const metadata: Metadata = {
  title: 'TRAIDER V1 - Dashboard',
  description: 'Institutional-grade autonomous crypto trading platform dashboard.',
};

/**
 * Main dashboard page component.
 * @returns {JSX.Element} The rendered dashboard page.
 */
export default function DashboardPage(): JSX.Element {
  return (
    <main data-testid="dashboard-main">
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
          {/* <MetricCard title="Portfolio Value" value="$10,000.00" change="+2.5%" changeLabel="24h" /> */}
          {/* <MetricCard title="Total P&L" value="+$250.00" change="+2.5%" changeLabel="All time" /> */}
          {/* <MetricCard title="Active Positions" value="3" change="0" changeLabel="vs yesterday" /> */}
          {/* <MetricCard title="Win Rate" value="65.2%" change="+1.2%" changeLabel="30d avg" /> */}
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
              {/* <StatusIndicator status="online" label="Market Data Feed" /> */}
              {/* <StatusIndicator status="online" label="Trading Engine" /> */}
              {/* <StatusIndicator status="online" label="Risk Management" /> */}
              {/* <StatusIndicator status="warning" label="ML Signals (Phase 1)" /> */}
            </div>
            <div className="mt-4 pt-4 border-t">
              <div className="flex justify-between items-center text-sm">
                <span className="text-muted-foreground">Last Updated</span>
                <span className="font-mono">
                  {new Date().toLocaleTimeString('en-US', { timeZone: 'UTC' })}
                </span>
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
                This is a placeholder dashboard. Real trading functionality, market data
                integration, and live portfolio tracking will be implemented in Phase 1.
              </p>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}
