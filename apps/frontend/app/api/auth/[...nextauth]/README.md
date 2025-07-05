# NextAuth.js Route Handler

## Overview

This module contains the NextAuth.js route handler that manages all authentication endpoints for the TRAIDER trading platform. It provides a centralized authentication system with enterprise-grade security.

## File Structure

```
[...nextauth]/
├── route.ts      # NextAuth.js route handler
└── README.md     # This file
```

## Route Handler (`route.ts`)

### Purpose
- **Central Authentication**: Single point for all auth operations
- **Dynamic Routing**: Handles all `/api/auth/*` endpoints
- **Provider Integration**: Supports multiple authentication providers
- **Session Management**: Secure JWT-based session handling

### Configuration

#### Authentication Providers
```typescript
providers: [
  CredentialsProvider({
    name: "credentials",
    credentials: {
      email: { label: "Email", type: "email" },
      password: { label: "Password", type: "password" }
    },
    async authorize(credentials) {
      // Secure credential validation
    }
  })
]
```

#### JWT Configuration
```typescript
jwt: {
  secret: process.env.NEXTAUTH_JWT_SECRET,
  maxAge: 60 * 60 * 24 * 30, // 30 days
  encode: async ({ secret, token }) => {
    // Custom JWT encoding
  },
  decode: async ({ secret, token }) => {
    // Custom JWT decoding
  }
}
```

#### Session Configuration
```typescript
session: {
  strategy: "jwt",
  maxAge: 30 * 24 * 60 * 60, // 30 days
  updateAge: 24 * 60 * 60,    // 24 hours
  generateSessionToken: () => {
    // Custom session token generation
  }
}
```

## Handled Endpoints

### Authentication Endpoints
- `GET /api/auth/signin` - Display sign-in page
- `POST /api/auth/signin` - Process sign-in request
- `GET /api/auth/signout` - Display sign-out page
- `POST /api/auth/signout` - Process sign-out request
- `GET /api/auth/session` - Get current session
- `GET /api/auth/csrf` - Get CSRF token

### Provider Endpoints
- `GET /api/auth/providers` - List available providers
- `GET /api/auth/callback/[provider]` - Handle OAuth callbacks
- `POST /api/auth/callback/credentials` - Handle credential login

## Security Features

### Token Security
- **JWT Signing**: HMAC SHA-256 with secure secrets
- **Token Expiration**: Short-lived tokens with refresh capability
- **Secure Storage**: HttpOnly cookies with SameSite protection
- **Token Validation**: Comprehensive signature verification

### Session Security
- **Session Encryption**: AES-256 encryption for session data
- **CSRF Protection**: Double-submit cookie pattern
- **Session Fixation Prevention**: New session ID on login
- **Secure Cookies**: Secure, HttpOnly, SameSite attributes

### Authentication Security
- **Password Hashing**: bcrypt with salt rounds
- **Rate Limiting**: Login attempt throttling
- **Account Lockout**: Temporary lockout after failed attempts
- **Audit Logging**: Complete authentication event logging

## Callbacks & Events

### JWT Callback
```typescript
async jwt({ token, user, account, profile }) {
  // Customize JWT token content
  if (user) {
    token.role = user.role;
    token.permissions = user.permissions;
  }
  return token;
}
```

### Session Callback
```typescript
async session({ session, token }) {
  // Customize session object
  session.user.role = token.role;
  session.user.permissions = token.permissions;
  return session;
}
```

### SignIn Callback
```typescript
async signIn({ user, account, profile, email, credentials }) {
  // Custom sign-in validation
  return true; // Allow sign-in
}
```

## Error Handling

### Authentication Errors
- **CredentialsSignin**: Invalid username/password
- **OAuthSignin**: OAuth provider error
- **OAuthCallback**: OAuth callback error
- **OAuthCreateAccount**: Account creation error
- **EmailCreateAccount**: Email verification error
- **Callback**: General callback error
- **OAuthAccountNotLinked**: Account linking error
- **EmailSignin**: Email sign-in error
- **CredentialsSignin**: Credentials sign-in error
- **SessionRequired**: Session required error

### Error Responses
```typescript
{
  error: "CredentialsSignin",
  status: 401,
  message: "Invalid credentials",
  url: "/api/auth/error?error=CredentialsSignin"
}
```

## Performance Optimization

### Caching Strategy
- **Session Caching**: Redis-based session storage
- **JWT Caching**: In-memory JWT validation cache
- **Provider Metadata**: Cached provider configurations
- **Database Queries**: Optimized user lookup queries

### Performance Metrics
- **Authentication Latency**: < 100ms
- **Session Validation**: < 10ms
- **Token Generation**: < 50ms
- **Database Queries**: < 25ms

## Monitoring & Logging

### Authentication Events
- **Successful Logins**: User, timestamp, IP address
- **Failed Attempts**: Credentials, IP, user agent
- **Session Events**: Creation, renewal, destruction
- **Security Events**: Suspicious activity, rate limiting

### Performance Monitoring
- **Response Times**: P50, P95, P99 latencies
- **Error Rates**: Authentication failure percentages
- **Throughput**: Requests per second by endpoint
- **Resource Usage**: Memory and CPU utilization

## Testing

### Unit Tests
- JWT token generation and validation
- Session management functionality
- Provider configuration validation
- Error handling scenarios

### Integration Tests
- End-to-end authentication flow
- Provider integration testing
- Session persistence validation
- Security boundary testing

### Security Tests
- Authentication bypass attempts
- Session hijacking prevention
- CSRF protection validation
- Rate limiting effectiveness

## Configuration

### Environment Variables
```bash
# Required
NEXTAUTH_URL=https://traider.local
NEXTAUTH_SECRET=your-nextauth-secret

# JWT Configuration
NEXTAUTH_JWT_SECRET=your-jwt-secret

# Database (optional)
DATABASE_URL=postgresql://user:pass@localhost/traider

# OAuth Providers (optional)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
```

### Custom Configuration
```typescript
export const authOptions: NextAuthOptions = {
  providers: [...],
  callbacks: {...},
  session: {...},
  jwt: {...},
  pages: {
    signIn: '/login',
    error: '/auth/error',
  },
  debug: process.env.NODE_ENV === 'development',
};
```

## See Also

- [NextAuth.js Documentation](https://next-auth.js.org/)
- [Authentication Module](../README.md)
- [Security Guidelines](../../../../docs/security/)
- [Testing Guide](../../../../docs/testing/authentication-testing-guide.md) 