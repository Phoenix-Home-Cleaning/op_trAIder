# Authentication Architecture

## Overview

The TRAIDER V1 authentication architecture provides secure, scalable authentication and authorization for the trading platform using NextAuth.js with JWT tokens and role-based access control.

## Architecture Components

### Authentication Flow
```
User → Login Page → NextAuth.js → JWT Token → Protected Routes
  ↓
Backend API ← Token Validation ← Middleware ← Request
```

### Core Components

#### 1. NextAuth.js Configuration
- **Location**: `app/api/auth/[...nextauth]/route.ts`
- **Purpose**: Central authentication handler
- **Features**: JWT strategy, custom callbacks, session management

#### 2. Middleware Protection
- **Location**: `middleware.ts`
- **Purpose**: Route protection and token validation
- **Coverage**: All protected routes and API endpoints

#### 3. Backend Authentication
- **Location**: `app/lib/auth/backend-auth.ts`
- **Purpose**: Server-side authentication utilities
- **Features**: Token validation, user lookup, session management

## Security Model

### Token Security
- **Algorithm**: HMAC SHA-256
- **Expiration**: 1 hour access tokens, 7 day refresh tokens
- **Storage**: HttpOnly, Secure, SameSite cookies
- **Rotation**: Automatic token refresh on renewal

### Session Management
- **Strategy**: Stateless JWT tokens
- **Validation**: Real-time token verification
- **Cleanup**: Automatic session expiration
- **Multi-device**: Support for concurrent sessions

### Role-Based Access Control (RBAC)
- **Roles**: ADMIN, TRADER, VIEWER
- **Permissions**: Granular access control
- **Enforcement**: Middleware and API level checks
- **Audit**: Complete access logging

## Implementation Details

### JWT Token Structure
```typescript
interface JWTToken {
  sub: string;           // User ID
  email: string;         // User email
  role: 'ADMIN' | 'TRADER' | 'VIEWER';
  permissions: string[]; // Granular permissions
  iat: number;          // Issued at
  exp: number;          // Expires at
  jti: string;          // JWT ID for revocation
}
```

### Authentication Callbacks
```typescript
// JWT Callback - Customize token content
async jwt({ token, user, account }) {
  if (user) {
    token.role = user.role;
    token.permissions = user.permissions;
  }
  return token;
}

// Session Callback - Customize session object
async session({ session, token }) {
  session.user.role = token.role;
  session.user.permissions = token.permissions;
  return session;
}
```

### Route Protection
```typescript
// Middleware matcher configuration
export const config = {
  matcher: [
    '/((?!api/auth|api/health|_next/static|_next/image|favicon.ico|login|$).*)',
  ],
};
```

## Security Features

### Attack Prevention
- **Brute Force Protection**: Rate limiting and account lockout
- **Session Fixation**: New session ID on login
- **CSRF Protection**: Double-submit cookie pattern
- **XSS Prevention**: Secure cookie attributes
- **JWT Security**: Signature verification and expiration

### Compliance Features
- **Audit Logging**: All authentication events
- **Data Protection**: GDPR/CCPA compliance
- **Retention Policies**: Configurable data retention
- **Encryption**: Data encryption at rest and in transit

## Performance Characteristics

### Latency Targets
- **Login**: < 100ms
- **Token Validation**: < 10ms
- **Session Check**: < 5ms
- **Logout**: < 25ms

### Scalability
- **Stateless Design**: Horizontal scaling support
- **Token Caching**: In-memory validation cache
- **Session Storage**: Redis-backed for scale
- **Load Balancing**: No session affinity required

## Monitoring & Observability

### Metrics
- **Authentication Success Rate**: Target > 99%
- **Login Latency**: P95 < 100ms
- **Failed Attempts**: Security monitoring
- **Token Validation**: Performance tracking

### Alerts
- **High Failure Rate**: > 5% authentication failures
- **Brute Force Detection**: Multiple failed attempts
- **System Errors**: Authentication service issues
- **Security Events**: Suspicious activity patterns

## Error Handling

### Authentication Errors
- **Invalid Credentials**: Generic error for security
- **Account Locked**: Temporary lockout with recovery
- **Token Expired**: Automatic refresh attempt
- **Session Invalid**: Redirect to login

### Recovery Procedures
- **Password Reset**: Secure reset flow
- **Account Unlock**: Time-based or admin unlock
- **Token Refresh**: Automatic background refresh
- **Session Recovery**: Graceful re-authentication

## See Also

- [NextAuth.js Configuration](../../app/api/auth/[...nextauth]/README.md)
- [Authentication Testing](../testing/authentication-testing-guide.md)
- [Security Guidelines](../security/)
- [Backend Authentication](../../app/lib/auth/README.md) 