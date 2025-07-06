[**TRAIDER V1 API Documentation v1.0.0-alpha**](../README.md)

***

[TRAIDER V1 API Documentation](../README.md) / mapBackendRole

# mapBackendRole()

> **mapBackendRole**(`backendRole`): `"ADMIN"` \| `"TRADER"` \| `"VIEWER"`

Defined in: [apps/frontend/lib/auth/backend-auth.ts:62](https://github.com/Phoenix-Home-Cleaning/op_trAIder/blob/3dfa0ac2b9c2853a3178461f245872609191f252/apps/frontend/lib/auth/backend-auth.ts#L62)

Map backend role to NextAuth role type

## Parameters

### backendRole

`string`

Role string from backend

## Returns

`"ADMIN"` \| `"TRADER"` \| `"VIEWER"`

Typed role for NextAuth

## Description

Converts backend role strings to typed role values for NextAuth.
Provides safe fallback to VIEWER for unknown roles.

## Performance

<1ms role mapping

## Side Effects

None - Pure function

## Trading Impact

Determines user access level to trading functions

## Risk Level

MEDIUM - Role assignment security
