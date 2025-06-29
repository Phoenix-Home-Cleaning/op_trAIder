/**
 * @fileoverview Client-side providers for TRAIDER application
 * @module app/providers
 *
 * @description
 * Wraps the application with necessary client-side providers including
 * NextAuth SessionProvider for authentication state management.
 * Critical component for maintaining user session state across the trading platform.
 *
 * @performance
 * - Latency target: <1ms provider initialization
 * - Throughput: N/A (component wrapper)
 * - Memory usage: <1MB
 *
 * @risk
 * - Failure impact: CRITICAL - Breaks authentication across entire app
 * - Recovery strategy: Error boundary with login redirect
 *
 * @compliance
 * - Audit requirements: Yes - Session management
 * - Data retention: Session duration only
 *
 * @see {@link docs/architecture/authentication.md}
 * @since 1.0.0-alpha.1
 * @author TRAIDER Team
 */

'use client';

import { SessionProvider } from 'next-auth/react';

interface ProvidersProps {
  children: React.ReactNode;
}

/**
 * Application providers wrapper component
 *
 * @description 
 * Provides authentication context and other client-side providers
 * to the entire application tree. Essential for maintaining user
 * session state and enabling secure trading operations.
 *
 * @param {ProvidersProps} props - Component props
 * @param {React.ReactNode} props.children - Child components to wrap
 * @returns {JSX.Element} Wrapped children with authentication providers
 *
 * @throws {Error} If SessionProvider fails to initialize
 *
 * @performance O(1) time, minimal memory overhead
 * @sideEffects Establishes WebSocket connection for session updates
 *
 * @tradingImpact Enables secure access to all trading functionality
 * @riskLevel CRITICAL - Core authentication infrastructure
 *
 * @example
 * ```tsx
 * // Used in root layout to wrap entire application
 * <Providers>
 *   <App />
 * </Providers>
 * ```
 *
 * @monitoring
 * - Metric: `auth.provider.initialization_time`
 * - Alert threshold: > 100ms
 */
export function Providers({ children }: ProvidersProps) {
  return <SessionProvider>{children}</SessionProvider>;
}
