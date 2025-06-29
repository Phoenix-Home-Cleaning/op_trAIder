/**
 * @fileoverview NextAuth.js TypeScript declarations for TRAIDER
 * @module types/next-auth
 * 
 * @description
 * Extends NextAuth.js types with TRAIDER-specific user properties
 * and trading platform role definitions.
 * 
 * @since 1.0.0-alpha.1
 * @author TRAIDER Team
 */

import NextAuth from "next-auth"

declare module "next-auth" {
  /**
   * Extended User interface with trading platform properties
   * 
   * @description Adds role-based access control and trading permissions
   * to the standard NextAuth User interface.
   */
  interface User {
    /** User's role in the trading platform */
    role: "ADMIN" | "TRADER" | "VIEWER"
    /** User's email address */
    email: string
    /** User's display name */
    name: string
    /** User's unique identifier */
    id: string
  }

  /**
   * Extended Session interface with trading platform properties
   * 
   * @description Adds role information to the user session for
   * role-based access control throughout the application.
   */
  interface Session {
    user: {
      /** User's role in the trading platform */
      role: "ADMIN" | "TRADER" | "VIEWER"
      /** User's email address */
      email: string
      /** User's display name */
      name: string
      /** User's unique identifier */
      id: string
    }
  }
}

declare module "next-auth/jwt" {
  /**
   * Extended JWT interface with trading platform properties
   * 
   * @description Adds role information to JWT tokens for
   * secure role-based access control.
   */
  interface JWT {
    /** User's role in the trading platform */
    role: "ADMIN" | "TRADER" | "VIEWER"
    /** User's email address */
    email: string
  }
} 