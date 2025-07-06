[**TRAIDER V1 API Documentation v1.0.0-alpha**](../README.md)

***

[TRAIDER V1 API Documentation](../README.md) / authenticateWithBackend

# authenticateWithBackend()

> **authenticateWithBackend**(`username`, `password`, `fetchFn`): `Promise`\<`null` \| `User`\>

Defined in: [apps/frontend/lib/auth/backend-auth.ts:139](https://github.com/Phoenix-Home-Cleaning/op_trAIder/blob/3dfa0ac2b9c2853a3178461f245872609191f252/apps/frontend/lib/auth/backend-auth.ts#L139)

Authenticate user with FastAPI backend

## Parameters

### username

`string`

User's username

### password

`string`

User's password

### fetchFn

\{(`input`, `init?`): `Promise`\<`Response`\>; (`input`, `init?`): `Promise`\<`Response`\>; \}

Fetch function to use (allows for testing with mocks)

## Returns

`Promise`\<`null` \| `User`\>

User object with authentication data or null if failed

## Description

Validates credentials against FastAPI /auth/login endpoint.
Returns user data and JWT token for session management.

## Throws

Network or authentication error

## Performance

~100-200ms including network round-trip

## Side Effects

Makes HTTP request to backend API

## Trading Impact

CRITICAL - Gateway to trading platform access

## Risk Level

CRITICAL - Authentication security boundary

## Example

```typescript
const user = await authenticateWithBackend('admin', 'password');
// Returns: { id: '1', username: 'admin', role: 'ADMIN', ... }
```

## Monitoring

- Metric: `auth.backend.latency`
- Alert threshold: > 500ms
