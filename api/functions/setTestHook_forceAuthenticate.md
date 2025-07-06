[**TRAIDER V1 API Documentation v1.0.0-alpha**](../README.md)

***

[TRAIDER V1 API Documentation](../README.md) / \_setTestHook\_forceAuthenticate

# \_setTestHook\_forceAuthenticate()

> **\_setTestHook\_forceAuthenticate**(`hook`): `void`

Defined in: [apps/frontend/lib/auth/backend-auth.ts:103](https://github.com/Phoenix-Home-Cleaning/op_trAIder/blob/3dfa0ac2b9c2853a3178461f245872609191f252/apps/frontend/lib/auth/backend-auth.ts#L103)

**`Internal`**

Set test hook for authentication override

## Parameters

### hook

Authentication function or undefined to reset
 Use only in test environments

`undefined` | (`username`, `password`) => `Promise`\<`null` \| `User`\>

## Returns

`void`

## Description

Allows tests to inject custom authentication behavior.
Call with undefined to reset to production behavior.
