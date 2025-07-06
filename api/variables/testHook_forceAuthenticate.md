[**TRAIDER V1 API Documentation v1.0.0-alpha**](../README.md)

***

[TRAIDER V1 API Documentation](../README.md) / \_testHook\_forceAuthenticate

# \_testHook\_forceAuthenticate

> **\_testHook\_forceAuthenticate**: (`username`, `password`) => `Promise`\<`User` \| `null`\> \| `undefined`

Defined in: [apps/frontend/lib/auth/backend-auth.ts:89](https://github.com/Phoenix-Home-Cleaning/op_trAIder/blob/3dfa0ac2b9c2853a3178461f245872609191f252/apps/frontend/lib/auth/backend-auth.ts#L89)

**`Internal`**

Test hook for dependency injection in unit tests

## Description

Allows tests to override authentication behavior without brittle global mocks.
Production code path remains 100% intact.

 Use only in test environments
