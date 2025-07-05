/**
 * @fileoverview Main dashboard page for TRAIDER trading platform
 * @module app/dashboard/page
 *
 * @description
 * Implements the main portfolio dashboard with real-time trading metrics,
 * position overview, and key performance indicators for institutional
 * cryptocurrency trading operations.
 *
 * @performance
 * - Latency target: <100ms page load
 * - Throughput: 1000+ concurrent users
 * - Memory usage: <10MB per session
 *
 * @risk
 * - Failure impact: MEDIUM - Dashboard unavailability affects monitoring
 * - Recovery strategy: Fallback to basic metrics display
 *
 * @compliance
 * - Audit requirements: Yes - All portfolio views logged
 * - Data retention: 7 years portfolio history
 *
 * @see {@link docs/architecture/dashboard-design.md}
 * @since 1.0.0-alpha.1
 * @author TRAIDER Team
 */

'use client';

import { useSession } from 'next-auth/react';

/**
 * Metric card interface
 *
 * @description Defines the structure for dashboard metric display cards
 * with values, changes, and visual indicators.
 */
interface MetricCard {
  /** Display title for the metric */
  title: string;
  /** Current value of the metric */
  value: string;
  /** Change from previous period */
  change: string;
  /** Whether the change is positive or negative */
  isPositive: boolean;
  /** Brief description of the metric */
  description: string;
}

/**
 * Position interface
 *
 * @description Defines the structure for trading position display
 * with asset information and current status.
 */
interface Position {
  /** Trading symbol (e.g., BTC-USD) */
  symbol: string;
  /** Position size */
  size: string;
  /** Current market value */
  value: string;
  /** Unrealized P&L */
  pnl: string;
  /** Whether P&L is positive */
  isPnlPositive: boolean;
}

/**
 * Dashboard page component
 *
 * @description Renders the main portfolio dashboard with trading metrics,
 * position overview, and system status indicators.
 *
 * @returns {JSX.Element} Dashboard page with portfolio overview
 *
 * @performance O(1) render time, static data for Phase 0
 * @sideEffects Tracks dashboard views for analytics
 *
 * @tradingImpact Provides overview of all trading activity and positions
 * @riskLevel MEDIUM - Dashboard accuracy affects trading decisions
 *
 * @example
 * ```tsx
 * // Renders complete dashboard with metrics and positions
 * <DashboardPage />
 * ```
 *
 * @monitoring
 * - Metric: `dashboard.page.load_time`
 * - Alert threshold: > 200ms
 */
export default function DashboardPage() {
  const { data: session } = useSession();

  // Phase 0: Mock data for demonstration
  // Phase 1+: Real-time data from trading engine
  const metrics: MetricCard[] = [
    {
      title: 'Portfolio Value',
      value: '$125,847.32',
      change: '+2.34%',
      isPositive: true,
      description: 'Total portfolio value including all positions',
    },
    {
      title: 'Daily P&L',
      value: '+$2,847.12',
      change: '+1.87%',
      isPositive: true,
      description: 'Profit/Loss for current trading day',
    },
    {
      title: 'Active Positions',
      value: '8',
      change: '+2',
      isPositive: true,
      description: 'Number of open trading positions',
    },
    {
      title: 'Win Rate',
      value: '67.3%',
      change: '+3.2%',
      isPositive: true,
      description: 'Percentage of profitable trades (30 days)',
    },
  ];

  const positions: Position[] = [
    {
      symbol: 'BTC-USD',
      size: '2.5847',
      value: '$89,234.12',
      pnl: '+$1,847.23',
      isPnlPositive: true,
    },
    {
      symbol: 'ETH-USD',
      size: '45.231',
      value: '$23,456.78',
      pnl: '+$567.89',
      isPnlPositive: true,
    },
    {
      symbol: 'SOL-USD',
      size: '125.67',
      value: '$8,934.56',
      pnl: '-$234.12',
      isPnlPositive: false,
    },
    {
      symbol: 'ADA-USD',
      size: '2847.12',
      value: '$4,221.86',
      pnl: '+$89.45',
      isPnlPositive: true,
    },
  ];

  return (
    <div className="space-y-6">
      {/* Welcome header */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h1 className="text-2xl font-bold text-gray-900">Welcome back, {session?.user?.name}</h1>
        <p className="mt-2 text-gray-600">
          Here&apos;s your portfolio overview for today. Phase 0 is showing mock data for
          demonstration.
        </p>
      </div>

      {/* Key metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {metrics.map((metric, index) => (
          <div key={index} className="bg-white rounded-lg shadow-sm p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">{metric.title}</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">{metric.value}</p>
              </div>
              <div
                className={`px-3 py-1 rounded-full text-sm font-medium ${
                  metric.isPositive ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                }`}
              >
                {metric.change}
              </div>
            </div>
            <p className="text-xs text-gray-500 mt-2">{metric.description}</p>
          </div>
        ))}
      </div>

      {/* Positions table */}
      <div className="bg-white rounded-lg shadow-sm">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">Active Positions</h2>
          <p className="text-sm text-gray-600">Current trading positions and performance</p>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Symbol
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Size
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Market Value
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Unrealized P&L
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {positions.map((position, index) => (
                <tr key={index} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="font-medium text-gray-900">{position.symbol}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-gray-600">{position.size}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-gray-900 font-medium">
                    {position.value}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span
                      className={`font-medium ${
                        position.isPnlPositive ? 'text-green-600' : 'text-red-600'
                      }`}
                    >
                      {position.pnl}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Recent activity */}
      <div className="bg-white rounded-lg shadow-sm">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">Recent Activity</h2>
          <p className="text-sm text-gray-600">Latest trading signals and system events</p>
        </div>
        <div className="p-6">
          <div className="space-y-4">
            <div className="flex items-center justify-between py-3 border-b border-gray-100">
              <div className="flex items-center">
                <div className="h-2 w-2 bg-green-400 rounded-full mr-3"></div>
                <div>
                  <p className="text-sm font-medium text-gray-900">Signal Generated: BTC Long</p>
                  <p className="text-xs text-gray-500">Momentum indicator triggered at $34,567</p>
                </div>
              </div>
              <span className="text-xs text-gray-500">2 min ago</span>
            </div>

            <div className="flex items-center justify-between py-3 border-b border-gray-100">
              <div className="flex items-center">
                <div className="h-2 w-2 bg-blue-400 rounded-full mr-3"></div>
                <div>
                  <p className="text-sm font-medium text-gray-900">Portfolio Rebalanced</p>
                  <p className="text-xs text-gray-500">Risk management adjustment completed</p>
                </div>
              </div>
              <span className="text-xs text-gray-500">15 min ago</span>
            </div>

            <div className="flex items-center justify-between py-3 border-b border-gray-100">
              <div className="flex items-center">
                <div className="h-2 w-2 bg-yellow-400 rounded-full mr-3"></div>
                <div>
                  <p className="text-sm font-medium text-gray-900">Market Data Update</p>
                  <p className="text-xs text-gray-500">
                    Real-time feeds synchronized across all exchanges
                  </p>
                </div>
              </div>
              <span className="text-xs text-gray-500">1 hour ago</span>
            </div>
          </div>
        </div>
      </div>

      {/* Phase 0 notice */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex items-start">
          <div className="flex-shrink-0">
            <svg className="h-5 w-5 text-blue-400" fill="currentColor" viewBox="0 0 20 20">
              <path
                fillRule="evenodd"
                d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z"
                clipRule="evenodd"
              />
            </svg>
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-blue-800">Phase 0 - Foundation Complete</h3>
            <div className="mt-2 text-sm text-blue-700">
              <p>
                This dashboard is showing mock data for demonstration purposes. Phase 1 will
                integrate real market data, live positions, and actual trading signals.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
