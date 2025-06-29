# TRAIDER V1 Authentication API

## Overview

Authentication API module providing secure user authentication, session management, and authorization for the TRAIDER V1 trading platform. Implements JWT-based authentication with NextAuth.js integration.

## Endpoints

### POST /api/auth/login
User authentication with credentials validation and JWT token generation.

**Request:**
```typescript
{
  username: string;
  password: string;
}
```

**Response:**
```typescript
{
  success: boolean;
  message: string;
  token?: string;
  user?: {
    id: string;
    username: string;
    role: string;
  };
}
```

### GET /api/auth/login
API documentation and demo credentials for Phase 0 development.

### NextAuth.js Routes (/api/auth/[...nextauth])
Handles OAuth providers, session management, and authentication callbacks.

## Security Features

- **JWT Tokens** - Secure token-based authentication
- **Input Validation** - Comprehensive request validation
- **Rate Limiting** - Brute force protection
- **Audit Logging** - Complete authentication audit trail
- **Session Management** - Secure session handling

## Phase 0 Demo Credentials

- **Admin**: `admin` / `password`
- **Demo User**: `demo` / `demo123`

## Performance Standards

- **Response Time**: < 200ms
- **Throughput**: 100 requests/minute per user
- **Memory Usage**: < 1MB per request

## Monitoring

- Login attempts and success rates
- Authentication response times
- Failed login attempt tracking
- Security event logging 