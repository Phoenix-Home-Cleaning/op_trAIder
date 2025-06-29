/**
 * @fileoverview Client-side providers for TRAIDER application
 * @module app/providers
 *
 * @description
 * Wraps the application with necessary client-side providers including
 * NextAuth SessionProvider for authentication state management.
 *
 * @since 1.0.0-alpha.1
 * @author TRAIDER Team
 */

'use client';

import { SessionProvider } from 'next-auth/react';

interface ProvidersProps {
  children: React.ReactNode;
}

/**
 * Application providers wrapper
 *
 * @description Provides authentication context and other client-side providers
 * to the entire application tree.
 *
 * @param {ProvidersProps} props - Component props
 * @param {React.ReactNode} props.children - Child components
 * @returns {JSX.Element} Wrapped children with providers
 */
export function Providers({ children }: ProvidersProps) {
  return <SessionProvider>{children}</SessionProvider>;
}
