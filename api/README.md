**TRAIDER V1 API Documentation v1.0.0-alpha**

***

# TRAIDER V1 API Documentation

## Fileoverview

Backend authentication service for TRAIDER V1

## Description

Service for authenticating users with the FastAPI backend.
Provides a clean interface for credential validation and user data retrieval.

## Performance

- Authentication latency: <200ms
- Network timeout: 5000ms
- Memory usage: <1MB

## Risk

- Failure impact: CRITICAL (authentication gateway)
- Recovery strategy: Graceful error handling with null return

## Compliance

- Audit requirements: Yes (all auth attempts logged)
- Data retention: 90 days authentication logs

## See

docs/architecture/authentication.md

## Since

1.0.0-alpha

## Author

TRAIDER Team

## Variables

- [\_testHook\_forceAuthenticate](variables/testHook_forceAuthenticate.md)

## Functions

- [mapBackendRole](functions/mapBackendRole.md)
- [\_setTestHook\_forceAuthenticate](functions/setTestHook_forceAuthenticate.md)
- [authenticateWithBackend](functions/authenticateWithBackend.md)
